#!/usr/bin/env python
"""Derive the arXiv v3 source from the anonymous master and stage it.

The two builds differ on exactly four points, applied here so they can never
drift apart by hand-editing:
  1. the TMLR style is loaded with its [preprint] option, which names the
     authors and removes the "Under review" running head, and is otherwise
     the same unmodified tmlr.sty;
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
              "paper/tmlr.sty", "paper/tmlr.bst", "paper/fancyhdr.sty",
              "results/table_construction_contrast.tex",
              "results/table_prevalence_sweep.tex"):
        shutil.copy(ROOT / f, SRC / Path(f).name)
    (SRC / "figures").mkdir(exist_ok=True)
    for f in sorted((ROOT / "paper/figures").glob("*.pdf")):
        shutil.copy(f, SRC / "figures" / f.name)

    s = (ROOT / "paper/main.tex").read_text(encoding="utf-8")
    edits = [
        ("\\usepackage{tmlr}\n",
         "\\usepackage[preprint]{tmlr}\n"),
        ("\\input{../results/table_construction_contrast}",
         "\\input{table_construction_contrast}"),
        ("\\input{../results/table_prevalence_sweep}",
         "\\input{table_prevalence_sweep}"),
        ("""\\author{\\name Anonymous authors \\email anonymous@example.org \\\\
      \\addr Paper under double-blind review}""",
         """\\author{\\name Michel Youssef \\email michelyoussef@hotmail.com \\\\
      \\addr Independent Researcher, Beirut, Lebanon \\\\
      ORCID 0009-0000-0664-8228}"""),
        ("Earlier versions of this manuscript reported",
         "Earlier versions of this manuscript (arXiv:2605.24696, v1 and v2) reported"),
        ("A companion manuscript from the same research programme (reference suppressed\n"
         "for double-blind review) shares",
         "A companion manuscript from the same research programme "
         "(arXiv:2510.09619) shares"),
        # the anonymous master withholds which measurements are shared because
        # naming them identifies the earlier versions; the named arXiv posting
        # has no such constraint and states them in full.
        ("is part of the account supplied to the action editor, because naming\n"
         "them here would identify the earlier versions.",
         "is as follows. The pooled LITNET composite and the assembled CICIDS arm\n"
         "are the same measurements as in v1 and v2, reported there under a regime\n"
         "interpretation that this paper replaces with an assembly interpretation;\n"
         "the timestamp-ordered CICIDS arm, the per-capture LITNET streams, the\n"
         "shared-record analysis and the method-identity audit have no counterpart\n"
         "in any earlier version; and results on a third dataset that appeared in\n"
         "the earlier versions are withdrawn and are not relied upon anywhere in\n"
         "this paper."),
        ("identifiers are supplied to the action editor confidentially.",
         "the earlier public versions are arXiv:2605.24696 v1 and v2."),
        ("During double-blind review, the artifact is available as the\n"
         "anonymized supplementary material accompanying this submission.",
         "The repository is public at\n"
         "\\url{https://github.com/MichelYsf/rcbsid-paper} (branch "
         "\\texttt{rebuild/honest-v1}); the artifact is archived as version 2.2.0 of the "
         "Zenodo record lineage, doi:10.5281/zenodo.22673735, which supersedes "
         "version 2.1.0 (doi:10.5281/zenodo.22638195), version 2.0.0 "
         "(doi:10.5281/zenodo.22213264) and version 1.0.0 "
         "(doi:10.5281/zenodo.20074590)."),
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
