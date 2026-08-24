#!/usr/bin/env python
"""Every CamelCase macro used by the manuscript must be defined in numbers.tex.

An undefined macro is a compile error, so LaTeX would catch it eventually --
but catching it before a compile costs seconds instead of a toolchain trip,
and this check also runs where no TeX engine exists. It complements
check_provenance.py: that gate proves defined numbers trace to manifests;
this one proves the manuscript uses no number that is not defined.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# LaTeX/acmart commands that legitimately start with a capital letter.
BUILTIN = {"LaTeX", "TeX", "CCSXML", "ACM", "Large", "Huge", "Big", "Bigg"}

TEX_INPUTS = [
    ROOT / "paper/main.tex",
    ROOT / "results/table_construction_contrast.tex",
    ROOT / "results/table_prevalence_sweep.tex",
]


def main() -> int:
    defined = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}",
                             (ROOT / "paper/numbers.tex").read_text(encoding="utf-8")))
    used: set[str] = set()
    for t in TEX_INPUTS:
        if t.exists():
            used |= set(re.findall(r"\\([A-Z][A-Za-z]+)", t.read_text(encoding="utf-8")))
    missing = sorted(u for u in used if u not in defined and u not in BUILTIN)
    print("manuscript macro check: %d used, %d defined in numbers.tex"
          % (len(used), len(defined)))
    if missing:
        for m in missing:
            print("  UNDEFINED  \\" + m)
        print("FAILED - the manuscript references macros numbers.tex does not define.")
        return 1
    print("PASSED - every manuscript macro resolves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
