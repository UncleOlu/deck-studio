#!/usr/bin/env python3
"""Check that an HTML deck keeps its design decisions in the token layer.

Slides must reference `var(--token)` only. A raw hex, a raw font-family, or a
hard-coded font-size outside the `:root` token block is a defect: it means one
slide can drift away from the deck's system.

What it flags, outside `:root`:
  - raw hex colours and rgb()/rgba()/hsl()/oklch()/lab() literals in CSS rules
  - font-family declarations naming a face instead of a var()
  - font-size declarations with any literal length instead of a var()
  - raw hex or font-family inside a `style="…"` attribute
  - named CSS colours (white, black, red …) in a declaration value
  - SVG presentation attributes carrying a literal: fill=, stroke=,
    stop-color=, font-family=, font-size=. Browser support for var() there is
    uneven, so an inline chart must take its colours from CSS classes.

What it allows:
  - everything inside the `:root { … }` block (that is the token layer)
  - `@media print` rules (print overrides are allowed literal values)
  - inline `style="…"` that only sets layout data: grid-column, grid-row,
    grid-template-columns, width, height, left, right, top, bottom, inset,
    transform, translate, order, flex, text-align, margin/padding, and custom
    properties. Any other inline declaration must use a var().
  - the `<meta name="theme-color">` attribute (HTML, not CSS)

Usage: python3 slide-token-validator.py deck.html [more.html …]
Exit code 1 if any defect is found.
"""
import re
import sys
from pathlib import Path

HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
COLOR_FN = re.compile(r"\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\s*\(")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}]+)")
FONT_SIZE = re.compile(r"font-size\s*:\s*([^;}]+)")
STYLE_ATTR = re.compile(r"""style\s*=\s*["']([^"']*)["']""")
# SVG presentation attributes: they never resolve var(), so any literal is a defect
PRES_ATTR = re.compile(
    r"""\b(fill|stroke|stop-color|flood-color|lighting-color|font-family|font-size)"""
    r"""\s*=\s*["']([^"']*)["']"""
)
PRES_OK = {"none", "currentcolor", "inherit", "transparent", "context-fill",
           "context-stroke", "freeze", "remove", "auto"}   # incl. SMIL fill=
LENGTH = re.compile(r"\d\s*(px|pt|rem|em|ch|vw|vh|%)?\b")
DATA_PROPS = re.compile(
    r"^\s*(grid-column|grid-row|grid-template-columns|grid-template-rows|"
    r"grid-area|width|height|min-width|max-width|min-height|max-height|"
    r"left|right|top|bottom|inset|transform|translate|rotate|scale|order|flex|"
    r"flex-basis|text-align|align-self|justify-self|margin|margin-top|"
    r"margin-bottom|margin-left|margin-right|padding|aspect-ratio|"
    r"--[\w-]+)\s*:", re.I
)
# a value is fine if it comes from the token layer
NAMED_COLORS = {
    "white", "black", "red", "green", "blue", "yellow", "orange", "purple",
    "gray", "grey", "silver", "navy", "teal", "olive", "maroon", "lime",
    "aqua", "fuchsia", "pink", "brown", "cyan", "magenta", "gold", "beige",
    "ivory", "tan", "coral", "salmon", "khaki", "indigo", "violet", "crimson",
    "rebeccapurple", "darkgray", "darkgrey", "lightgray", "lightgrey",
}
COLOR_PROPS = re.compile(
    r"^(color|background|background-color|border(-\w+)?-?color|border|outline|"
    r"outline-color|fill|stroke|stop-color|box-shadow|text-shadow|"
    r"text-decoration-color|caret-color|accent-color|column-rule-color)$", re.I
)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)


class Decl:
    __slots__ = ("prop", "val", "line")

    def __init__(self, prop, val, line):
        self.prop, self.val, self.line = prop, val, line


def split_decls(body: str):
    """Yield the `prop: value` declarations in one rule body, with line offsets."""
    out, pos = [], 0
    for piece in body.split(";"):
        if ":" in piece:
            prop, _, val = piece.partition(":")
            out.append(Decl(prop.strip().lower(), val.strip(),
                            body.count("\n", 0, pos + piece.index(":"))))
        pos += len(piece) + 1
    return out


def declaration_defects(prop: str, val: str):
    """Every reason this declaration is not sourced from the token layer."""
    if not val or "var(" in val:
        return
    for m in HEX.finditer(val):
        yield f"raw hex {m.group(0)} in {prop} — use a var(--token)"
    for m in COLOR_FN.finditer(val):
        yield f"raw {m.group(0)[:-1].strip()}() colour in {prop} — declare it in :root"
    if COLOR_PROPS.match(prop):
        for word in re.findall(r"[A-Za-z]+", val):
            if word.lower() in NAMED_COLORS:
                yield f"named colour '{word}' in {prop} — use a var(--token)"
    if prop == "font-family":
        yield f"font-family:{val} — use var(--font-*)"
    if prop == "font-size" and LENGTH.search(val):
        yield f"font-size:{val} — declare it once as var(--size-*)"


def blank(chunk: str) -> str:
    """Replace a chunk with its newlines, so reported line numbers stay true."""
    return "\n" * chunk.count("\n")


def strip_root_and_print(css: str):
    """Return CSS with comments, the :root token block, and @media print gone.

    Comments go first: a comment that merely mentions `:root` used to make the
    block matcher swallow the next real rule, silently skipping every check in
    it.
    """
    css = CSS_COMMENT.sub(lambda m: blank(m.group(0)), css)
    out, i, n = [], 0, len(css)
    while i < n:
        m = re.compile(r"(^|[\s}])(:root[^{;]*|@media\s+print[^{;]*)\{",
                       re.M).search(css, i)
        if not m:
            out.append(css[i:])
            break
        out.append(css[i:m.start()])
        depth, j = 1, m.end()
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        out.append(blank(css[m.start():j]))
        i = j
    return "".join(out)


def check(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []

    for block in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S | re.I):
        offset = text.count("\n", 0, block.start(1))
        css = strip_root_and_print(block.group(1))
        # scan declarations inside rule bodies only, so a selector such as
        # `#faded { … }` is never mistaken for a raw hex colour
        for body in re.finditer(r"\{([^{}]*)\}", css):
            base = offset + css.count("\n", 0, body.start(1))
            for decl in split_decls(body.group(1)):
                line = base + decl.line + 1
                for msg in declaration_defects(decl.prop, decl.val):
                    findings.append((line, msg))

    # inline styles: layout data is fine, anything else must come from a token
    for m in STYLE_ATTR.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        for d in m.group(1).split(";"):
            if not d.strip() or DATA_PROPS.match(d) or "var(" in d:
                continue
            prop, _, val = d.partition(":")
            if not val.strip():
                continue
            findings.append((line, f"inline style '{d.strip()}' — "
                                   f"{prop.strip()} is not layout data; use a var(--token)"))

    # SVG presentation attributes live in the markup, outside any <style> block
    for m in PRES_ATTR.finditer(text):
        name, val = m.group(1), m.group(2).strip()
        if val.lower() in PRES_OK or val.startswith("url("):
            continue
        if name == "font-size":
            bad = bool(LENGTH.search(val))
        else:
            bad = bool(HEX.search(val) or COLOR_FN.search(val)
                       or re.match(r"^[A-Za-z][\w \-,\'\"]*$", val))
        if bad:
            findings.append((text.count("\n", 0, m.start()) + 1,
                             f'{name}="{val}" — var() support in SVG presentation '
                             f"attributes is uneven; move it to a CSS class"))

    findings.sort()
    if findings:
        print(f"{path}: {len(findings)} token defect(s)")
        for line, msg in findings:
            print(f"  {path}:{line} - {msg}")
    else:
        print(f"{path}: clean — every slide value comes from the token layer.")
    return len(findings)


def main():
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("-")]
    if not paths:
        print(__doc__)
        return 2
    return 1 if sum(check(p) for p in paths) else 0


if __name__ == "__main__":
    sys.exit(main())
