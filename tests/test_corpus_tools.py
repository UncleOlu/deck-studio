import importlib.util
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools" / "corpus"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


edgar = load("edgar_fetch")
render = load("render")
agreement = load("agreement")


def test_edgar_refuses_non_sec_hosts():
    with pytest.raises(ValueError):
        edgar.fetch("https://example.com/x", "ua test@example.com")


def test_edgar_safe_dir_blocks_traversal(tmp_path):
    with pytest.raises(ValueError):
        edgar.safe_dir(tmp_path, "..")
    with pytest.raises(ValueError):
        edgar.safe_dir(tmp_path, "a/b")
    assert edgar.safe_dir(tmp_path, "0001-ab_c.d").parent == tmp_path.resolve()


def test_edgar_requires_contact_user_agent(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(SystemExit):
        edgar.user_agent()


def test_render_sampling_keeps_head_and_spreads_tail():
    assert render.sample_pages(3, 12) == [1, 2, 3]
    pages = render.sample_pages(100, 12)
    assert pages[:4] == [1, 2, 3, 4] and len(pages) == 12 and pages[-1] <= 100


def test_render_contained_blocks_escape(tmp_path):
    with pytest.raises(ValueError):
        render.contained(tmp_path, "../etc")


def test_kappa():
    assert agreement.kappa([("a", "a"), ("b", "b")]) == 1.0
    assert round(agreement.kappa([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]), 2) == 0.0
