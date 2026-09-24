import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools" / "corpus"


def load_from(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(name: str) -> ModuleType:
    return load_from(TOOLS / f"{name}.py", name)


edgar = load("edgar_fetch")
render = load("render")
agreement = load("agreement")


def test_edgar_refuses_non_sec_hosts() -> None:
    with pytest.raises(ValueError):
        edgar.fetch("https://example.com/x", "ua test@example.com")


def test_edgar_safe_dir_blocks_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        edgar.safe_dir(tmp_path, "..")
    with pytest.raises(ValueError):
        edgar.safe_dir(tmp_path, "a/b")
    assert edgar.safe_dir(tmp_path, "0001-ab_c.d").parent == tmp_path.resolve()


def test_edgar_requires_contact_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(SystemExit):
        edgar.user_agent()


def test_render_sampling_keeps_head_and_spreads_tail() -> None:
    assert render.sample_pages(3, 12) == [1, 2, 3]
    pages = render.sample_pages(100, 12)
    assert pages[:4] == [1, 2, 3, 4] and len(pages) == 12 and pages[-1] <= 100


def test_render_contained_blocks_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        render.contained(tmp_path, "../etc")


def test_kappa() -> None:
    assert agreement.kappa([("a", "a"), ("b", "b")]) == 1.0
    assert round(agreement.kappa([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]), 2) == 0.0


@pytest.mark.parametrize(
    "url",
    [
        "http://www.sec.gov/x",
        "file:///etc/passwd",
        "https://www.sec.gov:8443/x",
        "https://www.sec.gov.evil.com/x",
        "ftp://efts.sec.gov/x",
    ],
)
def test_edgar_refuses_non_https_or_non_sec_urls(url: str) -> None:
    with pytest.raises(ValueError):
        edgar.fetch(url, "ua test@example.com")


def test_edgar_rechecks_every_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resp:
        status_code = 302
        headers = {"Location": "https://evil.example.com/steal"}
        content = b""

    seen: list[str] = []

    def fake_get(url: str, **kw: object) -> Resp:
        seen.append(url)
        assert kw["allow_redirects"] is False
        return Resp()

    monkeypatch.setattr(edgar.requests, "get", fake_get)
    monkeypatch.setattr(edgar, "MIN_INTERVAL_S", 0)
    with pytest.raises(ValueError):
        edgar.fetch("https://www.sec.gov/Archives/x", "ua test@example.com")
    assert seen == ["https://www.sec.gov/Archives/x"]


def test_harvest_only_opens_own_run_dirs_in_a_sticky_temp_dir(tmp_path: Path) -> None:
    harvest = load_from(Path(__file__).resolve().parents[1] / "evals" / "harvest.py", "harvest")
    assert harvest.is_shared_temp(0o41777) and not harvest.is_shared_temp(0o40755)
    assert not harvest.is_shared_temp(0o40777)  # no sticky bit

    def sticky(mode: int) -> bool:
        return True  # stands in for a system temp dir without making one world-writable

    tmp = tmp_path / "tmp"
    run = tmp / "e-abc123" / "home"
    run.mkdir(parents=True)
    assert harvest.owned_run_dir(str(run / "trace.jsonl"), sticky) == tmp / "e-abc123"
    assert harvest.owned_run_dir(str(run / "trace.jsonl")) is None  # parent not sticky
    assert harvest.owned_run_dir(str(tmp / "e-abc123" / ".." / "x" / "t"), sticky) is None  # traversal
    assert harvest.owned_run_dir("relative/e-1/home/trace.jsonl", sticky) is None
    (tmp / "other" / "home").mkdir(parents=True)
    assert harvest.owned_run_dir(str(tmp / "other" / "home" / "t"), sticky) is None  # not e-*
    (tmp / "e-link").symlink_to(tmp / "e-abc123")
    assert harvest.owned_run_dir(str(tmp / "e-link" / "home" / "t"), sticky) is None  # symlinked run dir
