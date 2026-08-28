# ARXIV_V3_SHEET — replacement of arXiv:2605.24696, nothing submitted

Assembled 2026-08-27 against commit **`45229a57fbf3cef9ce7f2dbe66b9e34263c96ff1`**.
Do this **after** the Zenodo deposit, so the DOI can go in.

> **Immutable on submission:** an arXiv version is permanent. v3 will sit
> publicly beside v1 and v2 forever; you cannot delete a version, only add v4.
> The **Comments** field is part of the permanent record. Title, abstract,
> categories and comments can be corrected only by submitting a further version.

---

## Step 1 — Files in the tarball

Upload `packages/arxiv_v3/arxiv_v3_source.tar.gz` (43,833 B). It contains
exactly six files and compiles standalone:

| file | why |
|---|---|
| `main.tex` | named-author variant (not the anonymous DTRAP build) |
| `numbers.tex` | the generated macro layer every number resolves through |
| `references.bib` | 51 entries |
| `main.bbl` | **required** — arXiv does not run BibTeX |
| `table_construction_contrast.tex` | `\input` by main.tex |
| `table_prevalence_sweep.tex` | `\input` by main.tex |

Verified locally: 3-pass pdflatex+bibtex, **exit 0, 0 undefined references, 0
overfull boxes, 17 pages**, author named on page 1.

## Step 2 — Title (replaces the v1/v2 title)

```
Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks
```

Previous title, for the "title changed" note: *CALIBURN: Operationally
Calibrated Streaming Intrusion Detection with Regime-Dependent Conformal Risk
Control*.

## Step 3 — Abstract (paste verbatim)

```
Public network captures are rarely usable as evaluation streams as they stand,
so streaming intrusion-detection studies assemble them: interleaving capture
days, pooling temporally disjoint captures, or replaying records round robin. We
show on two benchmarks that this assembly step is not neutral plumbing but an
uncontrolled experimental treatment. On CICIDS2017, holding the full record
multiset identical and changing only the ordering, a fixed positional 70/15/15
chronological split then produces held-out samples that share only 32.5% of
their records, at held-out prevalences of 68.235% and 25.2396% -- a
42.9954-point difference -- and the measured ordering of the two deterministic
scorers reverses. Restricting both arms to the 78000 records they both held out
removes that reversal: the same scorer leads in both arms there. The reversal is
therefore a consequence of which records the assembly hands to the test set, not
of the order in which the detector saw its history, and we locate it
accordingly. On LITNET-2020, pooling three temporally disjoint captures reports
a single 6.4982% operating point that is the equal-weight mean of per-capture
held-out prevalences spanning 0.176% to 15.7747%; we present that identity as an
audit check rather than a discovery. We also audit the evaluated detector
against its description: its reset and growth branches share a predictive term
that cancels, so the run-length posterior equals the hazard rate exactly below
the run-length cap, while the evaluations spend nearly all their length at or
beyond that cap, where the posterior instead wanders; and the score the
evaluation consumes is a function of P(r<=5), not of P(r=0). Scoring that
detector one branch at a time yields a separate result: its deployed max
composition ranks worse than its own tail term alone (0.103477 AP, 0.302658
AUC-ROC), because the auxiliary branch is inverted rather than uninformative
(AUC-ROC 0.281890) and a maximum lets it govern the rank wherever the tail is
small -- a defect no metric computed on the assembled score can attribute.
Finally, we quantify a batch dependence in the ECOD reference implementation,
whose empirical CDFs are recomputed over the training matrix concatenated with
the scored batch: holding the evaluated records and the fitted model fixed and
changing only the accompanying batch moves its AUC-PR by 0.003063, so published
ECOD numbers are not comparable across studies that score different batch sizes.
Every measured value traces to an archived, hash-verified run manifest, and the
sentence-level claim ledger ships with the artifact.
```

## Step 4 — Comments field (paste verbatim; permanent and public)

Source of truth: the **NO VENUE CLAIM VARIANT** at the top of
`packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt`. The two variants below it in
that file are **retired and false** — both asserted a journal status for the
companion preprint that does not exist. Do not paste either.

```
v3: substantial correction and rebuild. v1/v2 reported results produced on
assembled evaluation streams (pooled captures, day-interleaved records) and
interpreted the resulting operating points as dataset properties; they also
described a scoring rule the released code did not implement, reported a
detection-delay record count as a latency in milliseconds, derived the decision
threshold by a rule other than the one stated, and included tables for which no
archived computational origin exists. An adversarial review and a line-by-line
audit of the archived artifacts established all of these. v3 rebuilds the
study: the assembled constructions are retained as explicitly labelled
protocols and contrasted against least-transformed alternatives; the detector
is characterised as the code implements it; every reported number is generated
by a script that writes an archived run manifest in the same execution, with a
build gate that fails on any number lacking one; and a sentence-level claim
ledger ships with the artifact. v1 and v2 also cited a Zenodo DOI that was
never minted -- no such deposit existed; the artifact is being deposited for
the first time with v3, and the placeholder is withdrawn. Title changed
accordingly (previously "CALIBURN: Operationally Calibrated Streaming Intrusion
Detection with Regime-Dependent Conformal Risk Control"). A companion preprint
sharing parts of the same codebase (arXiv:2510.09619) predates this audit; the
method-identity findings reported here apply to that shared lineage, and it is
being corrected separately. Provenance limitation, stated precisely. Nineteen of the twenty-five live run manifests in this record executed on a working tree that carried uncommitted edits, so the exact source state for those runs is not recoverable. Every base commit they name resolves and is an ancestor of the published branch, so the generating code is reachable at commit granularity; what is missing is the uncommitted delta at run time. Two of the nineteen are irreducible: the CICIDS construction-contrast arms, run ids s4_construction_contrast_20260819T064027_20f44694 and s4_construction_contrast_20260819T090813_46e9bd32, ran on an EC2 Linux instance that has since been decommissioned, and re-running them on the author's Windows machine would change published numbers -- the cross-platform difference this project records as corrected incident CI-16. They were therefore not re-run, and the other seventeen were deliberately left as they are rather than regenerate a subset that would not change this disclosure. 17 pages.
```

**[decide]** If the Zenodo deposit is published first, append one sentence:
`Artifact deposited at doi:10.5281/zenodo.XXXXXXX.` — using the **version DOI**.

**The Comments text now carries the provenance disclosure** in the same words
as the Zenodo description and the DTRAP editor note — 19 of 25 live run
manifests ran on an uncommitted tree, two irreducibly. Decided 2026-08-27:
accepted, not re-run.

**Page count is 17.** Verify against the arXiv build preview before submitting;
a stale count in this permanent field is the class of error this version exists
to correct.

## Step 5 — Categories and license

| field | value |
|---|---|
| Primary | **cs.CR** (Cryptography and Security) |
| Cross-list | cs.LG — unchanged from v2 |
| License | keep the v1/v2 licence selection unless you intend a change; arXiv does not allow relicensing an earlier version, only the new one |

## Step 6 — Before pressing submit

1. Preview arXiv's own build. Confirm **17 pages** and **your name on page 1**
   (this is the named variant; the anonymous build is for DTRAP only).
2. Confirm the Comments field is the NO VENUE CLAIM variant.
3. Confirm the abstract has no LaTeX macros left in it (the text above is
   already expanded).
