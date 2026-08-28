#!/usr/bin/env python
"""Fail the build when typeset text runs off the page.

TeX reports an overfull \\hbox and carries on; the compile exits 0 with zero
undefined references, and the PDF ships with the overflowing material simply
not visible. Every other check in this repository reads sources -- numbers,
citations, markup -- and none of them looks at the log, so nothing saw the
protocol table overflow its measure by 1639pt and lose the readable half of
five rows, including the ECOD label-access disclosure and the operative half of
the reporting-precision rule (CI-30).

Threshold: anything over 2pt. TeX routinely reports sub-point overfulls that
are invisible in print; 1639pt, 78pt and 16pt were not.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOGS = [
    ROOT / "paper" / "main.log",
    ROOT / "packages" / "arxiv_v3" / "src" / "main.log",
]

OVERFULL = re.compile(
    r"Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\)[^\n]*", re.M)

TOLERANCE_PT = 2.0


def main() -> int:
    findings = []
    scanned = 0
    for log in LOGS:
        if not log.exists():
            continue
        scanned += 1
        rel = str(log.relative_to(ROOT)).replace("\\", "/")
        text = log.read_text(encoding="utf-8", errors="replace")
        for m in OVERFULL.finditer(text):
            pt = float(m.group(1))
            if pt >= TOLERANCE_PT:
                findings.append((rel, pt, m.group(0).strip()[:110]))
    if not scanned:
        print("OVERFULL CHECK FAILED - no LaTeX log found; compile first. "
              "The check must never pass vacuously.")
        return 1
    print("overfull check: %d LaTeX log(s), tolerance %.1fpt"
          % (scanned, TOLERANCE_PT))
    if not findings:
        print("PASSED - nothing typeset past the page measure.")
        return 0
    for rel, pt, line in sorted(findings, key=lambda x: -x[1]):
        print("  OVERFULL  %s  %.2fpt" % (rel, pt))
        print("            %s" % line)
    print("")
    print("FAILED - text runs off the page. The compile exits 0 and reports no "
          "undefined references while doing it, so this is the only check that "
          "sees it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
