# Confidential note to the DTRAP editors: prior appearance and correction status

Paste the plain-text render, `EDITOR_NOTE.txt`, into the ScholarOne
"Confidential Comments to the Editor" field, or send it to
dtrap-editors@acm.org referencing the submission ID. It sits outside the
manuscript on purpose, so the manuscript stays anonymous. DTRAP's author
guidelines (read 2026-09-18 at dl.acm.org/journal/dtrap/author-guidelines)
ask that any prior appearance be noted on the title page, and that the author
inform the Editors-in-Chief of any circumstances bearing on the
prior-publication policy. This note does the second. Its Anonymity paragraph
explains how the first is handled. The two prior submissions are disclosed
in this note, and in the portal form only if the form asks; the cover letter
carries none of them.

---

Dear Editors,

This submission has prior public appearance, and it is a correction of that
prior work. It also has two prior submissions, set out below; neither
received peer review. I would rather you have the full picture from me at
submission than discover it later.

**Prior versions.** This manuscript is the corrected version of the preprint
**arXiv:2605.24696**. Its first two versions were posted under the title
"CALIBURN: Operationally Calibrated Streaming Intrusion Detection with
Regime-Dependent Conformal Risk Control":

| version | date | status |
|---|---|---|
| v1 | posted 23 May 2026 | public preprint, superseded by v3 |
| v2 | posted 25 June 2026 | public preprint, superseded by v3 |
| v3 | posted 14 September 2026, announced 16 September 2026 | the corrected version, under the present title: this submission's text with the author named, the prior-version identifiers printed, and a per-result-group account in place of the pointer to this note; since then two cross-reference sentences have been corrected, and the layout and the generative-AI statement follow ACM's template and policy |

The corrected artifact is archived on Zenodo as version 2.2.0
(doi:10.5281/zenodo.22673735), in the same record lineage as version 2.1.0
(doi:10.5281/zenodo.22638195), version 2.0.0 (doi:10.5281/zenodo.22213264)
and version 1.0.0 (doi:10.5281/zenodo.20074590).

**Prior submissions.** This work has been submitted twice before. Neither
submission received peer review.

1. An earlier version of this work was submitted to KeAi *Cyber Security and
   Applications* in May 2026 and rejected within 48 hours without peer
   review. That version is the one the audit found defective, and this
   manuscript is the rebuild from it. The arXiv v1 Comments field and the
   description of Zenodo version 1.0.0 both name that submission. The v1
   comment, "Under review at Cyber Security and Applications", is out of
   date; the v2 Comments field does not repeat it.
2. The current version was submitted to *Transactions on Machine Learning
   Research* (TMLR) on 16 September 2026 and desk-rejected on 18 September
   2026 without review. The decision was signed by the venue. No action
   editor was assigned and no comment was given.

Neither manuscript has received peer review at any venue, and apart from
this submission nothing is under review anywhere. The archived artifact,
Zenodo version 2.2.0, carries the manuscript source in the TMLR LaTeX
template of that second submission; its analysis code, run manifests and
macro layer are identical to those behind this submission, whose anonymized
supplementary copy differs from them only by its anonymization rewrites; its
claim ledger differs only by corrected internal cross references, and the
camera-ready deposit will carry the final source.

**What was wrong, and what the correction covers.** An adversarial review and
a line-by-line audit of the archived artifacts established two defects that
affect interpretation rather than arithmetic:

1. The released code does not implement the anomaly score the papers describe.
   The evaluated score is a maximum of a chi-square tail term and a weighted
   short-run posterior mass, not the run-length-reset posterior of the text.
   The decision threshold is the prior-inclusive Bayes rule rather than the
   cost-only rule described. The quantity reported as "latency in
   milliseconds" is a count of records.
2. The headline results were produced on *assembled* evaluation streams
   (pooled captures, day-interleaved records). The prior versions interpreted
   the resulting operating points as dataset properties ("rare-attack regime",
   "moderate-prevalence regime"). The present submission shows that those
   operating points are properties of the assembly.

**Overlap with the prior versions, per result group.** This matrix is supplied
here rather than in the manuscript. A per-result-group account of what is
reused from named public preprints would identify the author to referees. The
anonymized body therefore carries only a short statement that prior versions
exist and that this note supplies the detail.

| result group | status | note |
|---|---|---|
| LITNET pooled composite, all methods | **reused measurement, corrected interpretation** | The same measurements appear in v1/v2's LITNET table (v2 Table 4). Reported there as a "rare-attack regime" property. Reported now as an artifact of pooling three temporally disjoint captures, with the equal-weight identity made explicit. |
| CICIDS assembled arm, all methods | **reused measurement, corrected interpretation** | Same measurements as v1/v2's CICIDS table (v2 Table 5), there labelled a "moderate-prevalence regime". Relabelled as one assembled construction, with the budgeted-subsample and dilution mechanisms quantified. |
| Prevalence sweep | **re-derived, re-scoped** | Re-derived from the archived pre-audit runs. Re-captioned as an experiment on the assembled construction, with corrected chance floors and normalized lift added. |
| Timestamp-ordered CICIDS arm | **new** | No counterpart in any earlier version. |
| Per-capture LITNET streams | **new** | No counterpart. Earlier versions reported only the pooled composite. |
| Held-out overlap, relocation, dilution | **new** | |
| Shared-record analysis | **new** | Establishes that the ordering reversal does not survive on the records both arms hold out. |
| Method-identity audit (score, posterior, threshold, delay) | **new, and corrective** | Invalidates v1/v2's description of the scoring rule and of the threshold derivation. |
| One untuned alternative reset formulation (Appendix A) | **new** | |
| UNSW-NB15 results | **withdrawn** | Reported in v1/v2. Not reproduced and not relied upon. Its stream was a seeded permutation, not a chronology. |

**Correction history, with the claims each version invalidates.**

| version | date | public status | claims invalidated |
|---|---|---|---|
| v1 | posted 23 May 2026 | public preprint, superseded | Scoring-rule description (code computes a different score). Threshold derivation (prior-inclusive, not cost-only). The "regime" taxonomy resting on assembled constructions. Detection latency reported in milliseconds when the quantity is a count of records. Tables for which no archived computational origin exists. Label-aware round-robin interleaved streams described as chronological. |
| v2 | posted 25 June 2026 | public preprint, superseded | All of v1's, plus the reframed contribution statement, which retained the regime framing. |
| v3 | posted 14 September 2026, announced 16 September 2026 | public preprint, the corrected version | Supersedes both. Retains the measurements marked "reused" above with corrected interpretation, withdraws the UNSW-NB15 results and the regime taxonomy, and adds the timestamp-ordered arm, the per-capture streams, the shared-record analysis and the method-identity audit. Every number carries an archived generating-run manifest, enforced by a build gate. |

v3 carries a public correction note in its arXiv Comments field. It states
that v1 and v2 reported results on assembled evaluation streams, described a
scoring rule the code did not implement, and included tables with no archived
origin. The corrected-incident log in the artifact records each numbered
incident with its evidence and closure status. The count is a record of the
process, not a quality claim, so none is quoted here.

**The artifact DOI.** Earlier manuscript versions cite doi:10.5281/zenodo.20074590, which resolves to version 1.0.0 of the artifact record, deposited 2026-05-07 and containing the pre-audit codebase; this corrected rebuild is published in the same record lineage, first as version 2.0.0 (doi:10.5281/zenodo.22213264) and then, with the manifests of the pre-submission review rounds added, as version 2.1.0 (doi:10.5281/zenodo.22638195), each superseding the one before it. The version accompanying this manuscript is 2.2.0 (doi:10.5281/zenodo.22673735), which adds the revisions of the final pre-submission review round and supersedes 2.1.0, and Zenodo displays a newer-version notice on each superseded record. An earlier draft of the correction texts accompanying this submission said that DOI was never minted. That was false. The check behind it searched the repository's own history instead of the registrar. The error is recorded as corrected incident CI-36 in the log that ships with the artifact.

**Companion manuscript.** A companion preprint, **arXiv:2510.09619**
("Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
Decisions"), shares part of the same codebase and predates the audit. The
method-identity findings apply to its shared lineage. It reports no
quantitative result tables, so it has no numeric overlap with this submission.
Its v2, posted 14 September 2026 and announced 16 September 2026, adds a
correction note on its title page and in its abstract. Its arXiv Comments
field states that an audit of the shared codebase found the score, threshold
and latency descriptions unsupported by the implementation and the evaluation
streams to be assembled constructions, and points to arXiv:2605.24696 v3 and
the Zenodo 2.2.0 record.

**The companion is a public preprint and is not under review at any
journal.** I state this plainly because an earlier draft of this note said
that "the relevant journal has been or is being informed", and that was
false. The same implication stood in the manuscript's Companion Manuscript
Disclosure and is now corrected there too. No submission of the companion to
IEEE Transactions on Information Forensics and Security (TIFS), the journal
that sentence presumed, existed. I verified this in the IEEE Author Portal on
2026-08-27, with the filters set to All Publications and All Submission
Statuses. The account returned one closed record, `TDSC-2025-10-1842`, and no
other. That record is the companion's: arXiv:2510.09619 was submitted to IEEE
Transactions on Dependable and Secure Computing and desk-rejected on 22 October
2025 on scope grounds, without peer review. The error was mine and was caught
before submission rather than by you. It is recorded as corrected incident
CI-25, together with the rule it produced. The rule says that a venue
relationship asserted in any artifact must be verified against the venue's
own system before the artifact is prepared, and that researching a venue's
procedures is not verification of a submission's existence. There is
consequently no concurrent-submission or dual-consideration question for you
to weigh. This manuscript is under consideration at DTRAP and nowhere else,
and nothing else of mine is under review anywhere.

**On the provenance mechanism, and two failures of it.** The manuscript's
Provenance Discipline section (Section 9) and its Appendix B state what the
checks cover as a scope rather than by name. The reason it is written that way
belongs with you rather than with the referees, so I set it out here.

The gate was written to enforce a rule: no number in the manuscript without an
archived generating run. For its first ten days, from 18 to 28 August 2026, it
reported that the rule held. It was reading one file, the generated macro
file, which is produced from the manifests and therefore cannot contain an
unmanifested number. It never opened the manuscript. Values typed directly
into manuscript-bound tables passed a green gate on three occasions and were
found by independent audit passes instead (corrected incidents CI-11 and
CI-19, and four AUC-ROC values in the shared-record table).
The scan now covers the manuscript, everything it includes, and every file the
claim ledger cites. Its first run over the repository returned 88 findings:
the four known values, 28 unmanifested values in the findings file behind the
analyses added at that time, six derived values in generated findings files,
a class of false positives from a sign-handling bug that was then fixed, and
entries in files that exist to record numbers. Every real finding is now
emitted as a macro or deleted.

A second check failed the same way. A three-pass compile reported zero
undefined references while two citations resolved to nothing. The bibliography
entries were absent, and natbib reports that condition as a citation warning
rather than an undefined reference (CI-26). A citation check now runs beside
the macro check.

I record these because the alternative, presenting the mechanism at the
strength its name implies, is the failure this paper is about. The corrected
incident log in the artifact carries both in full, with the reasoning and the
closure state. My judgement is that a referee needs the scope statement and
not the history. If you would prefer the history in the body as well, I will
add it.

**Provenance limitation.** The artifact accompanying this submission carries a
limitation I would rather you hear from me. It is stated in the same words in
the description of the Zenodo 2.2.0 record.

Provenance limitation, stated precisely. Twenty-seven of the thirty-three live
run manifests in this record executed on a working tree that carried
uncommitted edits, so the exact source state for those runs is not
recoverable. Every base commit they name resolves and is an ancestor of the
published branch, so the generating code is reachable at commit granularity;
what is missing is the uncommitted delta at run time. Two of the twenty-seven
are irreducible: the CICIDS construction-contrast arms, run ids
s4_construction_contrast_20260819T064027_20f44694 and
s4_construction_contrast_20260819T090813_46e9bd32, ran on an EC2 Linux
instance that has since been decommissioned, and re-running them on the
author's Windows machine would change published numbers -- the cross-platform
difference this project records as corrected incident CI-16. They were
therefore not re-run, and the other twenty-five were deliberately left as they
are rather than regenerate a subset that would not change this disclosure.

**Anonymity.** The manuscript suppresses these identifiers for double-anonymous
review and points to this note. DTRAP's guidelines ask that prior appearance
be noted on the title page. An anonymized title page cannot name the preprint,
so the manuscript states, without identifiers, that earlier public versions
exist, in its Introduction and in Section 10, and this note supplies the
identifiers. If you judge that the correction history makes effective
anonymity impossible and would prefer a different handling, I will follow
your instruction.

The full artifact accompanies the submission as anonymized supplementary
material. It holds the code, every run manifest, the claim ledger, and the
numbered corrected-incident log. The figure renderer postdates the Zenodo
2.0.0 deposit, draws only measured values already archived in the manifests
(its one typed constant is the chance level of AUC-ROC), and is included from
version 2.1.0 onward, together with the manifests of the pre-submission
review rounds.

Sincerely,
[Author, identified to the editorial system]
