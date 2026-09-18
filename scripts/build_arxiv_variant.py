#!/usr/bin/env python
"""Derive the arXiv v3 source from the anonymous master and stage it.

The two builds differ on exactly four points, applied here so they can never
drift apart by hand-editing:
  1. document class: [manuscript,screen,nonacm] instead of review/anonymous;
  2. the author block is named (arXiv postings are not anonymous);
  3. the artifact-availability sentence points at the public repository;
  4. the arXiv IDs suppressed for double-anonymous review are reinstated in
     the origin paragraph and the companion disclosure, and the account of
     prior versions that the anonymous build supplies to the editors is
     printed in full.
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
    (SRC / "figures").mkdir(exist_ok=True)
    for f in sorted((ROOT / "paper/figures").glob("*.pdf")):
        shutil.copy(f, SRC / "figures" / f.name)

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
        # the anonymous master withholds which measurements are shared because
        # naming them identifies the earlier versions; the named arXiv posting
        # has no such constraint and states them in full.
        ("Section~\\ref{sec:disclosure} states that some measurements in this paper also\n"
         "appear in those versions, under an interpretation this paper withdraws; which\n"
         "measurements those are, which results are new and which are withdrawn are\n"
         "supplied to the editors confidentially, because naming them here would defeat\n"
         "anonymization. The dated correction history is the corrected-incident log that\n"
         "ships with the artifact.",
         "Section~\\ref{sec:disclosure} states which measurements this paper shares with\n"
         "those versions and which are new, and gives the per-result-group account; the\n"
         "dated correction history is the corrected-incident log in the artifact."),
        ("Earlier versions of this manuscript were publicly posted and are superseded by\n"
         "this one. Because a per-result-group account of what is reused, re-derived,\n"
         "corrected, withdrawn or new would identify those versions --- and they are not\n"
         "anonymous --- that account is supplied to the editors confidentially rather\n"
         "than printed here, together with the dated version history and the list of\n"
         "claims each correction invalidates.",
         "Earlier versions of this manuscript (arXiv:2605.24696 v1, posted 23 May 2026,\n"
         "and v2, posted 25 June 2026) were publicly posted and are superseded by this\n"
         "one. The per-result-group account of what is reused, re-derived, corrected,\n"
         "withdrawn or new follows; the dated version history and the list of claims\n"
         "each correction invalidates are the corrected-incident log in the artifact."),
        ("is part of the account supplied to the editors, because naming them\n"
         "here would identify the earlier versions.",
         "is as follows. The pooled LITNET composite and the assembled CICIDS arm\n"
         "are the same measurements as in v1 and v2, reported there under a regime\n"
         "interpretation that this paper replaces with an assembly interpretation;\n"
         "the timestamp-ordered CICIDS arm, the per-capture LITNET streams, the\n"
         "shared-record analysis and the method-identity audit have no counterpart\n"
         "in any earlier version; and results on a third dataset that appeared in\n"
         "the earlier versions are withdrawn and are not relied upon anywhere in\n"
         "this paper."),
        ("the identifiers of the\n"
         "companion and of those versions are supplied to the editors confidentially.",
         "those versions\n"
         "are arXiv:2605.24696 v1 and v2."),
        ("During double-anonymous review, the artifact is available through the\n"
         "submission system's anonymous artifact channel.",
         "The repository is public at\n"
         "\\url{https://github.com/MichelYsf/rcbsid-paper} (branch "
         "\\texttt{rebuild/honest-v1}); the artifact is archived as version 2.2.0 of the "
         "Zenodo record lineage, doi:10.5281/zenodo.22673735, which supersedes "
         "version 2.1.0 (doi:10.5281/zenodo.22638195), version 2.0.0 "
         "(doi:10.5281/zenodo.22213264) and version 1.0.0 "
         "(doi:10.5281/zenodo.20074590)."),
    ]
    for old, new in edits:
        if s.count(old) != 1:
            print("ANCHOR for arXiv edit matches %d times: %s" % (s.count(old), old[:70]))
            return 1
        s = s.replace(old, new, 1)
    (SRC / "main.tex").write_text(s, encoding="utf-8")
    print("arXiv variant staged in " + str(SRC))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
