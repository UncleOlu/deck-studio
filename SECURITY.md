# Security

## Reporting a vulnerability

Please report security issues privately through GitHub's **Report a
vulnerability** button on this repository (Security tab → Advisories), which
is enabled when the repository is public. Until then, contact the maintainer
through their GitHub profile. Do not open a public issue. Include the affected
script, the input that triggers the problem, and what happens. You should get a first response within a week.

## Scope

The scripts read files a user points them at, so the areas that matter most:

- `scripts/ingest.py`: path handling (symlink escapes, paths outside the input
  folder), zip and XML parsing of Office files (size caps, defusedxml), and
  malformed PDFs.
- `scripts/pptx2pdf.py`: file paths passed to LibreOffice and AppleScript.
- `tools/corpus/edgar_fetch.py`: outbound requests (HTTPS to sec.gov only).
- The vendored JavaScript in `templates/lib/vendor/`.

Decks and fact bases are built from the user's own documents. The plugin sends
nothing over the network except the SEC fetcher in `tools/`, which is a
development tool and not part of the skill.
