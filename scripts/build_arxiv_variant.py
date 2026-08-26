#!/usr/bin/env python
"""Derive the arXiv v3 source from the anonymous master and stage it.

The two builds differ on exactly four points, applied here so they can never
drift apart by hand-editing:
  1. document class: [manuscript,screen,nonacm] instead of review/anonymous;
  2. the author block is named (arXiv postings are not anonymous);
  3. the artifact-availability sentence points at the public repository;
  4. the arXiv IDs suppressed for double-anonymous review are reinstated in
     the origin paragraph and the companion disclosure.
Compilation of the result is the caller's job (pdflatex+bibtex x3); the
tarball must include main.bbl because arXiv does not run BibTeX.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "packages/arxiv_v3/src"


def main() -> int:
    SRC.mkdir(parents=True, exist_ok=True)
    for f in ("paper/numbers.tex", "paper/references.bib",
              "results/table_construction_contrast.tex",
              "results/table_prevalence_sweep.tex"):
        shutil.copy(ROOT / f, SRC / Path(f).name)

    s = (ROOT / "paper/main.tex").read_text(encoding="utf-8")
    edits = [
        ("\\documentclass[manuscript,anonymous,review]{acmart}",
         "\\documentclass[manuscript,screen,nonacm]{acmart}"),
        ("\\input{../results/table_construction_contrast}",
         "\\input{table_construction_contrast}"),
        ("\\input{../results/table_prevalence_sweep}",
         "\\input{table_prevalence_sweep}"),
        ("""\\author{Anonymous Author(s)}
\\affiliation{%
  \\institution{Anonymous Institution}
  \\city{}
  \\country{}}""",
         """\\author{Michel Youssef}
\\orcid{0009-0000-0664-8228}
\\affiliation{%
  \\institution{Independent Researcher}
  \\city{Beirut}
  \\country{Lebanon}}
\\email{michelyoussef@hotmail.com}"""),
        ("Earlier versions of this manuscript reported",
         "Earlier versions of this manuscript (arXiv:2605.24696, v1 and v2) reported"),
        ("A companion manuscript from the same research programme (reference suppressed\n"
         "for double-anonymous review) shares",
         "A companion manuscript from the same research programme "
         "(arXiv:2510.09619) shares"),
        ("identifiers are supplied to the editors confidentially.",
         "the earlier public versions are arXiv:2605.24696 v1 and v2."),
        ("During double-anonymous review, the artifact is available through the\n"
         "submission system's anonymous artifact channel.",
         "The repository is public at\n"
         "\\url{https://github.com/MichelYsf/rcbsid-paper} (branch "
         "\\texttt{rebuild/honest-v1}); the Zenodo deposit DOI will be added "
         "when minted."),
    ]
    for old, new in edits:
        if old not in s:
            print("ANCHOR MISSING for arXiv edit: " + old[:70])
            return 1
        s = s.replace(old, new, 1)
    (SRC / "main.tex").write_text(s, encoding="utf-8")
    print("arXiv variant staged in " + str(SRC))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
