#!/usr/bin/env python
"""Fail when a staged package is older than what it is supposed to contain.

Packages are built from the tree and then sit in `packages/` until someone
uploads them. Nothing connected the two, so a package could silently fall
behind: the Zenodo code zip was found three days and one correction round
stale, still carrying values a binding rule had removed and a sentence a
corrected incident had withdrawn, and the DTRAP artifact was rebuilt 37
seconds before the last source edit and so shipped a weaker gate than the
repository's (CI-31).

The rule is simple enough to enforce mechanically: a package artifact must be
at least as new as every source file it is built from. This does not verify
CONTENT -- a package can be newer and still wrong -- but the failure it catches
is the one that actually happened, twice, and it costs nothing to run.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (package artifact, [source roots it is built from])
PACKAGES = [
    (ROOT / "packages/zenodo/rcbsid_rebuild_code.zip",
     ["src", "scripts", "tests", "paper/main.tex", "paper/numbers.tex",
      "SCOPE_DECISIONS.md", "CLAIM_LEDGER.md", "findings_contrast.md",
      "findings_review_analyses.md", "findings_prevalence.md"]),
    (ROOT / "packages/dtrap/artifact_anonymous.zip",
     ["src", "scripts", "tests", "paper/main.tex", "paper/numbers.tex",
      "SCOPE_DECISIONS.md", "CLAIM_LEDGER.md", "results/manifests",
      "findings_contrast.md", "findings_review_analyses.md"]),
    (ROOT / "packages/dtrap/source_anonymous.tar.gz",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
    (ROOT / "packages/dtrap/manuscript_anonymous.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
    (ROOT / "packages/arxiv_v3/arxiv_v3_source.tar.gz",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
    # Built PDFs. paper/main.pdf is the source of every shipped copy, so a
    # stale one silently makes all of them stale; packages/arxiv_v3/src/main.pdf
    # is what the arXiv page count is read from; and the reviewer-kit copy was
    # found four pages and a whole correction round behind (CI-31), pointed at
    # by a step no longer in the operator's sequence.
    (ROOT / "paper/main.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
    (ROOT / "packages/arxiv_v3/src/main.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
    (ROOT / "REVIEWER_KIT/manuscript_review.pdf",
     ["paper/main.tex", "paper/numbers.tex", "paper/references.bib"]),
]

SKIP_SUFFIX = {".pyc", ".aux", ".log", ".out", ".bbl", ".blg", ".pdf",
               ".sha256"}
SLACK_S = 2.0     # filesystem timestamp granularity, not a grace period


def newest(paths: list[str]) -> tuple[float, Path | None]:
    best, who = 0.0, None
    for rel in paths:
        p = ROOT / rel
        if not p.exists():
            continue
        it = [p] if p.is_file() else [q for q in p.rglob("*") if q.is_file()]
        for q in it:
            if q.suffix in SKIP_SUFFIX or "__pycache__" in q.parts:
                continue
            m = q.stat().st_mtime
            if m > best:
                best, who = m, q
    return best, who


def main() -> int:
    stale, checked, absent = [], 0, []
    for pkg, sources in PACKAGES:
        if not pkg.exists():
            absent.append(pkg)
            continue
        checked += 1
        src_m, who = newest(sources)
        if src_m - pkg.stat().st_mtime > SLACK_S:
            stale.append((pkg, who, src_m - pkg.stat().st_mtime))
    print("package freshness: %d staged artifact(s) checked" % checked)
    for p in absent:
        print("  ABSENT    %s" % p.relative_to(ROOT).as_posix())
    for pkg, who, delta in stale:
        print("  STALE     %s" % pkg.relative_to(ROOT).as_posix())
        print("            %.0fs older than %s"
              % (delta, who.relative_to(ROOT).as_posix() if who else "?"))
    if not checked:
        print("FAILED - no staged package found; the check must never pass "
              "vacuously.")
        return 1
    if stale:
        print("")
        print("FAILED - a staged package predates its sources. Rebuild it "
              "before any upload; an uploaded Zenodo deposit is immutable.")
        return 1
    print("PASSED - every staged package is at least as new as its sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
