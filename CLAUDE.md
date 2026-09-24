# Project Security Notes

Global security and verification standards apply (see `~/.claude/CLAUDE.md`).
This file covers only what is specific to this repo.

## Testing Requirements

Write tests that try to BREAK the code:
- Null/None, empty strings, negative numbers, overflow-scale numbers
- Unicode edge cases (emoji, RTL, zero-width)
- Collections with 0, 1, and 100k+ items
- Deeply nested objects, concurrent access, timeouts

For every endpoint or function handling user input, test:
- SQL injection: `'; DROP TABLE users; --`
- XSS: `<script>alert('xss')</script>`
- Path traversal: `../../../etc/passwd`
- Command injection: `; rm -rf /`
- Oversized payloads, missing/expired/invalid tokens, another user's resources (IDOR)

## When Writing New Features

1. Start with the threat model: what could go wrong?
2. Define allowed inputs before writing logic.
3. Least privilege: minimal permissions, minimal scope.
4. Fail secure — errors deny access, never grant it.
5. Log security events: auth failures, permission denials, validation failures.

## Repo-specific

- **Trust boundary:** every file under a user-supplied input folder is
  untrusted. `scripts/ingest.py` canonicalises paths, refuses symlink escapes,
  caps file count, per-part and per-file decompressed size, and parses Office
  XML with defusedxml. Keep those guards when changing ingest.
- **Subprocesses:** fixed argv lists only; file paths reach AppleScript as
  argv, never inside script text (`pptx2pdf.py`).
- **Network:** the skill makes no network calls. `tools/corpus/edgar_fetch.py`
  (dev only) allows HTTPS to sec.gov hosts only.
- **Licensing is a release gate:** never commit proprietary skill material
  (the Anthropic pptx scripts live only on the local branch
  `private/anthropic-pptx-scripts`, never pushed), copyrighted deck files, or
  the research corpus. Record every third-party source in `PROVENANCE.md`.
- **Personal data:** no home-directory paths, email addresses, or raw eval
  transcripts in tracked files.
