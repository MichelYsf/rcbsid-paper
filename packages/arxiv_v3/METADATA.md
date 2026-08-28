# arXiv v3 replacement — metadata to paste

**Replaces:** arXiv:2605.24696 v2.

**New title** (title-change note for the replacement form):
> Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
>
> *Corrected 2026-08-27:* this field previously carried "Benchmark Stream
> Construction, Not Attack Prevalence, Produces the Regime Structure of
> Streaming Intrusion Detection" — a title analysis A1 refuted and CI-21
> withdrew. Following it would have put the withdrawn claim on arXiv.

Previous title, for the record: "CALIBURN: Operationally Calibrated Streaming
Intrusion Detection with Regime-Dependent Conformal Risk Control". The title
change is part of the correction: the prior title names capabilities
(operational calibration, regime-dependent conformal risk control) that the
audit found unimplemented or withdrawn.

**Comments field:** use the **NO VENUE CLAIM VARIANT** at the top of
`../sibling/ARXIV_V3_COMMENT.txt`. The two variants below it are
retired and false — both asserted a journal status for the companion preprint
that does not exist (see `../../SIBLING_DECISION.md`, CI-25) — so do not paste
either. The variant already carries the page count, **17 pages**; confirm it
still matches the compiled PDF before pasting.

**Categories:** cs.CR (primary); cross-list cs.LG unchanged from v2.

**Package contents** (`arxiv_v3_source.tar.gz`, compiles on arXiv's pipeline —
pdflatex, `.bbl` included because arXiv does not run BibTeX):
main.tex, numbers.tex, references.bib, main.bbl,
table_construction_contrast.tex, table_prevalence_sweep.tex.
Verified locally: 3-pass compile, exit 0, zero undefined references,
17 pages, author-named (arXiv postings are not anonymous).
