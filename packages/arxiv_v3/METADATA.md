> **Historical.** This file describes the v3 package as staged for the posting
> of 14 September 2026: the named build in the TMLR template at commit 2bfb896
> (113,688 B). The listing's 108 KB source size does not match that tarball, so
> which exact file was uploaded is unverified. The tarball now in this
> directory is the acmart rebuild of 2026-09-18 (25 pages), which was not
> posted. The Comments field actually posted is recorded in
> `ARXIV_V3_SHEET.md`. The venue is now ACM DTRAP; TMLR desk-rejected the
> submission on 18 September 2026 without review.

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
either. The variant already carries the page count, **24 pages**; confirm it
still matches the compiled PDF before pasting.

**Categories:** cs.CR (primary); cross-list cs.LG unchanged from v2.

**Package contents** (`arxiv_v3_source.tar.gz`, compiles on arXiv's pipeline —
pdflatex, `.bbl` included because arXiv does not run BibTeX):
main.tex, numbers.tex, references.bib, main.bbl, the unmodified TMLR
template files tmlr.sty, tmlr.bst and fancyhdr.sty,
table_construction_contrast.tex, table_prevalence_sweep.tex, and the
figures/ directory with the four manuscript figures.
Verified locally: 3-pass compile, exit 0, zero undefined references,
24 pages (20 main body), author-named via the template's [preprint] option
(arXiv postings are not anonymous).
