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


LATEX_COMMANDS = {"Description"}


def main() -> int:
    defined = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}",
                             (ROOT / "paper/numbers.tex").read_text(encoding="utf-8")))
    used: set[str] = set()
    for t in TEX_INPUTS:
        if t.exists():
            used |= set(re.findall(r"\\([A-Z][A-Za-z]+)", t.read_text(encoding="utf-8")))
    missing = sorted(u for u in used if u not in defined and u not in BUILTIN)
    # Capitalised LaTeX commands that are not numbers macros. acmart's
    # accessibility command entered with the figure round; without this
    # allow list the check reported it as an undefined macro.
    missing = sorted(set(missing) - LATEX_COMMANDS)
    print("manuscript macro check: %d used, %d defined in numbers.tex"
          % (len(used), len(defined)))
    rc = 0
    if missing:
        for m in missing:
            print("  UNDEFINED  \\" + m)
        print("FAILED - the manuscript references macros numbers.tex does not define.")
        rc = 1
    else:
        print("PASSED - every manuscript macro resolves.")

    # An undefined CITATION is the same defect class as an undefined macro: the
    # reader gets "[?]" where evidence should be. It is not caught by the
    # 0-undefined-references check, because natbib reports missing citations as
    # its own warning rather than as a LaTeX undefined reference -- which is how
    # two citations added in the previous round reached a "0 undefined" verdict
    # while resolving to nothing at all (CI-26).
    bib = (ROOT / "paper/references.bib")
    keys = set(re.findall(r"@\w+\{([^,\s]+)\s*,", bib.read_text(encoding="utf-8")))
    cited: set[str] = set()
    for t in TEX_INPUTS:
        if t.exists():
            for group in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}",
                                    t.read_text(encoding="utf-8")):
                cited |= {k.strip() for k in group.split(",") if k.strip()}
    dangling = sorted(cited - keys)
    print("citation check: %d key(s) cited, %d defined in references.bib"
          % (len(cited), len(keys)))
    if dangling:
        for d in dangling:
            print("  UNDEFINED CITATION  " + d)
        print("FAILED - a cited key has no bibliography entry; it renders as [?].")
        rc = 1
    else:
        print("PASSED - every cited key resolves.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
