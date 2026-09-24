# Contributing

## Checks

Every change passes these before it is merged:

```bash
.venv/bin/python -m pytest -q          # also on Python 3.9: python3 -m pytest -q -p no:cacheprovider tests
.venv/bin/ruff check .
```

A change to the kit, a builder, or a reference that the samples use also
rebuilds the samples and runs the QA gate on each:

```bash
python3 skills/premium-decks/samples/build_samples.py
cd skills/premium-decks/templates && node build-pitchbook.js pitchbook-pitch.sample.json
python3 ../scripts/qa-deck.py <deck>.pptx --register banking --facts ../samples/source/<name>/brief/facts.jsonl
```

## Versioning

Semantic, in `.claude-plugin/plugin.json` and `pyproject.toml`.

- **Patch:** wording fixes, a corrected value, a broken link.
- **Minor:** a new reference, script, rule, or sample.
- **Major:** the skill's routing or public workflow changes, or a reference
  that other files depend on is removed or renamed.

Every version bump adds a `CHANGELOG.md` entry naming what was added, what was
**rejected and why**, and any conflict resolved against the quality floor.

## Sources and licences

Only add material whose licence allows redistribution under MIT, and record it
in `PROVENANCE.md` and `NOTICE`. Never paste text from a proprietary skill, a
bank's legal disclaimer, or a copyrighted deck. The research corpus stays
outside the repository; commit only statistics, source URLs, and conventions
described in your own words.

## Evals

Cases live in `evals/cases/<name>/case.yaml`. Deck-building cases copy their
fixture folder with `setup.sh`; trigger cases (`--tag trigger`) check that the
skill fires on deck requests, picks the right register, and stays quiet
otherwise.

```bash
claude plugin eval . --tag trigger --trust-plugin --ablation none --no-publish --runs 3
claude plugin eval . --scaffold --trust-plugin --allow-tools Bash Write Edit --ablation none \
  --no-publish --keep-temp --json <out>          # deck cases: then evals/harvest.py and evals/objective.py
```

Raw eval output (`evals/results/`, `evals/reports/*.json`) holds absolute paths
and full transcripts, so it stays local; commit the Markdown summaries.

## Installing a local checkout

The repository is its own marketplace (`.claude-plugin/marketplace.json`). The
working tree also holds `.venv`, eval runs, and renders, so install from a
clean export of a tag rather than from the checkout itself:

```bash
git archive vX.Y.Z | tar -x -C <export dir>
claude plugin marketplace add <export dir>
claude plugin install deck-studio@deck-studio
```

Restart Claude Code afterwards to load the new version.
