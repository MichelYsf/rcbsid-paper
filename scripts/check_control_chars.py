#!/usr/bin/env python
"""Catch shell-heredoc escape damage in LaTeX sources.

A backslash-bearing edit passed through a shell heredoc has its escapes
interpreted before Python ever sees the string: `\\r` becomes a carriage
return, `\\t` a tab, `\\b` a backspace, `\\a` a bell, `\\f` a form feed, `\\v`
a vertical tab. The visible result is a LaTeX macro with its backslash eaten --
`\\ref{tab:x}` becomes CR + `ef{tab:x}`, which typesets as the literal text
"ef{tab:x}".

Nothing else in this repository can see it. The compiler does not error: a
`\\ref` without its backslash is not a reference, so the zero-undefined-
references check passes with the reference silently gone (CI-19, which shipped
"(Table eftab:litnet)" in a PDF). The provenance and literal gates read numbers,
not markup.

So this check looks for the damage directly: raw control characters in a text
source, and the orphaned macro-name fragments the common escapes leave behind.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "paper" / "main.tex",
    ROOT / "results" / "table_construction_contrast.tex",
    ROOT / "results" / "table_prevalence_sweep.tex",
    ROOT / "packages" / "arxiv_v3" / "src" / "main.tex",
    ROOT / "packages" / "dtrap" / "src" / "main.tex",
]

# Control characters that have no business in a .tex source. Tab is excluded:
# it is legal whitespace and appears in hand-formatted tables.
CONTROL = {
    "\r": "carriage return (from a mangled \\r, e.g. \\ref)",
    "\x07": "bell (from a mangled \\a, e.g. \\approx)",
    "\x08": "backspace (from a mangled \\b, e.g. \\bottomrule)",
    "\x0b": "vertical tab (from a mangled \\v)",
    "\x0c": "form feed (from a mangled \\f, e.g. \\frac)",
}

# Macro-name fragments left stranded when the leading backslash is eaten. Each
# is matched only where a backslash does NOT precede it, and only at a word
# boundary, so legitimate prose is not flagged.
ORPHANS = [
    (r"(?<!\\)(?<![A-Za-z])ef\{", "\\ref{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])abel\{", "\\label{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])egin\{", "\\begin{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])extbf\{", "\\textbf{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])extit\{", "\\textit{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])exttt\{", "\\texttt{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])ottomrule", "\\bottomrule with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])oprule", "\\toprule with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])pprox", "\\approx with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])rac\{", "\\frac{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])aption\{", "\\caption{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])ite\{", "\\cite{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])itep\{", "\\citep{ with its backslash eaten"),
    (r"(?<!\\)(?<![A-Za-z])mph\{", "\\emph{ with its backslash eaten"),
]


def main() -> int:
    findings = []
    scanned = 0
    for t in TARGETS:
        if not t.exists():
            continue
        scanned += 1
        raw = t.read_bytes().decode("utf-8", errors="replace")
        # These files are stored with CRLF, so every line legitimately ends in
        # a carriage return. Normalise the line terminator first: what we are
        # hunting is a control character INSIDE a line, which is what an eaten
        # backslash leaves behind.
        raw = raw.replace("\r\n", "\n")
        rel = str(t.relative_to(ROOT)).replace("\\", "/")
        for lineno, line in enumerate(raw.split("\n"), 1):
            for ch, why in CONTROL.items():
                if ch in line:
                    findings.append((rel, lineno, why,
                                     repr(line[:90])))
            for pat, why in ORPHANS:
                for m in re.finditer(pat, line):
                    findings.append((rel, lineno, why,
                                     line[max(0, m.start() - 34):m.start() + 26]))
    if not scanned:
        print("CONTROL-CHAR CHECK FAILED - no target could be read; the check "
              "must never pass vacuously.")
        return 1
    print("control-char check: %d LaTeX source(s) scanned" % scanned)
    if not findings:
        print("PASSED - no heredoc escape damage.")
        return 0
    for rel, lineno, why, ctx in findings:
        print("  DAMAGED  %s:%d  %s" % (rel, lineno, why))
        print("           ...%s..." % ctx.strip())
    print("")
    print("FAILED - a backslash was eaten before the file was written. Re-apply "
          "the edit from a script FILE, never a shell heredoc.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
