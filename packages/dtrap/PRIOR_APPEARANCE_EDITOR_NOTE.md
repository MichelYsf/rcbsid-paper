# Confidential note to the DTRAP editors — prior appearance and correction status

Paste into the ScholarOne "Confidential Comments to the Editor" field, or send
to dtrap-editors@acm.org referencing the submission ID. It is deliberately
outside the manuscript so the manuscript stays anonymous; DTRAP's guidance asks
authors to disclose prior appearance to the editors.

---

Dear Editors,

This submission has prior public appearance, and it is a correction of that
prior work. I would rather you have the full picture from me at submission than
discover it later.

**Prior versions.** The manuscript supersedes a preprint posted as
**arXiv:2605.24696**, "CALIBURN: Operationally Calibrated Streaming Intrusion
Detection with Regime-Dependent Conformal Risk Control":

| version | date | status |
|---|---|---|
| v1 | 23 May 2026 | public preprint, never submitted to a journal |
| v2 | 25 June 2026 | public preprint, never submitted to a journal |

Neither version was accepted anywhere. A corrected v3, matching this
submission, will be posted; I will hold it until the editors advise if you
prefer.

**What was wrong, and what the correction covers.** An adversarial review and a
line-by-line audit of the archived artifacts established two defects that
affect interpretation rather than arithmetic:

1. The released code does not implement the anomaly score the papers describe.
   The evaluated score is a maximum of a chi-square tail term and a weighted
   short-run posterior mass, not the run-length-reset posterior of the text;
   the decision threshold is the prior-inclusive Bayes rule rather than the
   cost-only rule described; and the quantity reported as "latency in
   milliseconds" is a count of records.
2. The headline results were produced on *assembled* evaluation streams
   (pooled captures, day-interleaved records). The prior versions interpreted
   the resulting operating points as dataset properties ("rare-attack regime",
   "moderate-prevalence regime"). The present submission shows that those
   operating points are properties of the assembly.

**Overlap with the prior versions, per result group.** This matrix is supplied
here rather than in the manuscript: a per-result-group account of what is
reused from named public preprints would identify the authors to referees, so
the anonymized body carries only a short statement that prior versions exist
and that this note supplies the detail.

| result group | status | note |
|---|---|---|
| LITNET pooled composite, all methods | **reused measurement, corrected interpretation** | The same measurements appear in v1/v2's LITNET table (v2 Table 4). Reported there as a "rare-attack regime" property; reported now as an artifact of pooling three temporally disjoint captures, with the equal-weight identity made explicit. |
| CICIDS assembled arm, all methods | **reused measurement, corrected interpretation** | Same measurements as v1/v2's CICIDS table (v2 Table 5), there labelled a "moderate-prevalence regime". Relabelled as one assembled construction, with the budgeted-subsample and dilution mechanisms quantified. |
| Prevalence sweep | **re-derived, re-scoped** | Re-derived from the archived pre-audit runs; re-captioned as an experiment on the assembled construction, with corrected chance floors and normalized lift added. |
| Timestamp-ordered CICIDS arm | **new** | No counterpart in any earlier version. |
| Per-capture LITNET streams | **new** | No counterpart; earlier versions reported only the pooled composite. |
| Held-out overlap, relocation, dilution | **new** | |
| Shared-record analysis | **new** | Establishes that the ordering reversal does not survive on the records both arms hold out. |
| Method-identity audit (score, posterior, threshold, delay) | **new, and corrective** | Invalidates v1/v2's description of the scoring rule and of the threshold derivation. |
| Untuned change-point repair | **new** | |
| UNSW-NB15 results | **withdrawn** | Reported in v1/v2; not reproduced and not relied upon. Its stream was a seeded permutation, not a chronology. |

**Correction history, with the claims each version invalidates.**

| version | date | public status | claims invalidated |
|---|---|---|---|
| v1 | 23 May 2026 | public preprint, never submitted to a journal | Scoring-rule description (code computes a different score); threshold derivation (prior-inclusive, not cost-only); the "regime" taxonomy resting on assembled constructions; detection latency reported in milliseconds when the quantity is a count of records; tables for which no archived computational origin exists; label-aware round-robin interleaved streams described as chronological. |
| v2 | 25 June 2026 | public preprint, never submitted to a journal | All of v1's, plus the reframed contribution statement, which retained the regime framing. |
| v3 / this submission | pending | not yet posted | Supersedes both. Retains the measurements marked "reused" above with corrected interpretation, withdraws the UNSW-NB15 results and the regime taxonomy, and adds the timestamp-ordered arm, the per-capture streams, the shared-record analysis and the method-identity audit. Every number carries an archived generating-run manifest, enforced by a build gate. |

A public correction note accompanies the v3 replacement, stating the same
defects in the arXiv Comments field. The corrected-incident log in the artifact
records each numbered incident with its evidence and closure status; the count
is a record of the process, not a quality claim, so none is quoted here.

**The artifact DOI.** Earlier manuscript versions cite doi:10.5281/zenodo.20074590, which resolves to version 1.0.0 of the artifact record, deposited 2026-05-07 and containing the pre-audit codebase; this corrected rebuild is published as version 2.0.0 in the same record lineage and supersedes it, and Zenodo displays a newer-version notice on the superseded record. An earlier draft of the correction texts accompanying this submission said that DOI was never minted; that was false --- the check behind it searched the repository's own history instead of the registrar --- and it is recorded as corrected incident CI-36 in the log that ships with the artifact.

**Companion manuscript.** A companion preprint, **arXiv:2510.09619**
("Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
Decisions"), shares part of the same codebase and predates the audit. The
method-identity findings apply to its shared lineage. It reports no
quantitative result tables, so it has no numeric overlap with this submission,
and its correction is being handled separately.

**It is a public preprint and is not under review at any journal.** I state
this plainly because an earlier draft of this note told you that "the relevant
journal has been or is being informed", and that was false — as was the same
implication in the manuscript's Companion Manuscript Disclosure, now corrected.
No submission of the companion existed. I verified this in the IEEE Author
Portal on 2026-08-27 (filters: All Publications, All Submission Statuses; the
account returns one closed record, `TDSC-2025-10-1842`, rejected 22 October
2025, and no other). The error was mine and was caught before submission
rather than by you; it is recorded as corrected incident CI-25, together with
the rule it produced — that a venue relationship asserted in any artifact must
be verified against the venue's own system before the artifact is prepared, and
that researching a venue's procedures is not verification of a submission's
existence. There is consequently no concurrent-submission or dual-consideration
question for you to weigh: this manuscript is under consideration at DTRAP and
nowhere else, and so is nothing else of mine.

**On the provenance mechanism, and two failures of it.** The manuscript's
Provenance Discipline section states what the checks cover as a scope rather
than by name. The reason it is written that way belongs with you rather than
with the referees, so I set it out here.

The gate was written to enforce a rule -- no number in the manuscript without
an archived generating run -- and for several months it reported that the rule
held. It was reading one file: the generated macro file, which is produced
*from* the manifests and therefore cannot contain an unmanifested number. It
never opened the manuscript. Three numbers typed directly into manuscript-bound
tables passed a green gate and were found by human auditors instead (corrected
incidents CI-11, CI-19, and four AUC-ROC values in the shared-record table).
The scan now covers the manuscript, everything it includes, and every file the
claim ledger cites; widening it surfaced 88 further findings on its first run,
including unmanifested values in the findings file backing this round's new
analyses, all now emitted as macros or deleted.

A second check failed the same way: a three-pass compile reported zero
undefined references while two citations resolved to nothing, because the
bibliography entries were absent and that condition is reported by natbib as a
citation warning rather than an undefined reference (CI-26). A citation check
now runs beside the macro check.

I record these because the alternative -- presenting the mechanism at the
strength its name implies -- is the failure this paper is about. The corrected
incident log in the artifact carries both in full, with the reasoning and the
closure state. My judgement is that a referee needs the scope statement and not
the history; if you would prefer the history in the body as well, I will add
it.

**Provenance limitation.** The artifact accompanying this submission carries a
limitation I would rather you hear from me. It is stated in the same words in
the Zenodo deposit description and the arXiv v3 correction note.

Provenance limitation, stated precisely. Nineteen of the twenty-five live run
manifests in this record executed on a working tree that carried uncommitted
edits, so the exact source state for those runs is not recoverable. Every base
commit they name resolves and is an ancestor of the published branch, so the
generating code is reachable at commit granularity; what is missing is the
uncommitted delta at run time. Two of the nineteen are irreducible: the CICIDS
construction-contrast arms, run ids
s4_construction_contrast_20260819T064027_20f44694 and
s4_construction_contrast_20260819T090813_46e9bd32, ran on an EC2 Linux instance
that has since been decommissioned, and re-running them on the author's Windows
machine would change published numbers -- the cross-platform difference this
project records as corrected incident CI-16. They were therefore not re-run, and
the other seventeen were deliberately left as they are rather than regenerate a
subset that would not change this disclosure.

**Anonymity.** The manuscript suppresses these identifiers for double-anonymous
review and points to this note. If you judge that the correction history makes
effective anonymity impossible and would prefer a different handling, I will
follow your instruction.

The full artifact — code, every run manifest, the claim ledger, and the
numbered corrected-incident log — accompanies the submission as anonymized
supplementary material.

Sincerely,
[Author, identified to the editorial system]
