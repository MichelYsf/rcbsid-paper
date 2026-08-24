# arXiv v3 replacement — metadata to paste

**Replaces:** arXiv:2605.24696 v2.

**New title** (title-change note for the replacement form):
> Benchmark Stream Construction, Not Attack Prevalence, Produces the Regime
> Structure of Streaming Intrusion Detection

Previous title, for the record: "CALIBURN: Operationally Calibrated Streaming
Intrusion Detection with Regime-Dependent Conformal Risk Control". The title
change is part of the correction: the prior title names capabilities
(operational calibration, regime-dependent conformal risk control) that the
audit found unimplemented or withdrawn.

**Comments field:** use ONE of the two variants in
`../sibling/ARXIV_V3_COMMENT_COEXIST.txt` according to the sibling decision
(`../../SIBLING_DECISION.md`). Update the page count in the chosen variant to
**10 pages** (the compiled count of this package) before pasting.

**Categories:** cs.CR (primary); cross-list cs.LG unchanged from v2.

**Package contents** (`arxiv_v3_source.tar.gz`, compiles on arXiv's pipeline —
pdflatex, `.bbl` included because arXiv does not run BibTeX):
main.tex, numbers.tex, references.bib, main.bbl,
table_construction_contrast.tex, table_prevalence_sweep.tex.
Verified locally: 3-pass compile, exit 0, zero undefined references,
10 pages, author-named (arXiv postings are not anonymous).
