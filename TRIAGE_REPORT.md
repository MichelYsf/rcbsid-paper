# TRIAGE_REPORT — the binding round, 26–27 August 2026

One round, closed. Covers the pre-submission review triage, seven operator
amendments, three bounded analyses, four submission-side amendments, and the
a void IEEE TIFS withdrawal preparation (T4). Nothing was published, submitted, or sent.

## T0. Review artifacts on this machine

Searched the whole user profile (Downloads, Documents, Desktop, OneDrive) and
the repository for review documents from the last 45 days, by filename and by
content.

| path | date | size | what it is |
|---|---|---|---|
| `Downloads/Fresh_Adversarial_Review_and_Triage.pdf` | 2026-08-26 | 66,867 B | **The pre-submission review of the current manuscript.** "ACM DTRAP PRE-SUBMISSION REVIEW… MAJOR REVISION – DO NOT SUBMIT THIS VERSION". Copied to `REVIEWER_KIT/review_fresh_1.pdf`. |
| `Downloads/CALIBURN_DTRAP_adversarial_review.md` | 2026-08-17 | 38,223 B | Referee report on the **superseded** pre-rebuild manuscript (66 pp. elsarticle build). Recommendation: Major Revision. Already processed: verified item-by-item as V1–V12 and folded into `AUDIT_FINDINGS.md`. |
| `Downloads/CALIBURN_DTRAP_skeptical_review.md` | 2026-08-17 | 45,373 B | Second referee report on the same superseded manuscript. Recommendation: **Reject, confidence high**. Same disposition. |

Other hits (`AutoGreet-Eval-Fixtures-Review.md`, the ITIG-CRM prompts) belong to
unrelated projects.

**The round is single-reviewer for the current manuscript.** Only one review
targets the version under submission. That weakens convergence evidence: where
two independent reviewers agree, a finding is likely real; a single reviewer's
*judgment* calls carry no such support. Accordingly, single-review judgment
items were shelved rather than acted on unless independently verified — and the
three that were acted on (identification, method-identity scope, mean-magnitude)
were each verified by running the analysis, not by accepting the argument. No
further reviews were commissioned and none were waited for.

## T1/T2. The triage and the bounded analyses

Executed in full. **The analyses changed the paper's central claim.**

**A1 (shared-record ranking) — FIX, and decisive.** Both arms restricted to the
**78,000 records both held out**:

| arm | detector $AP$ | ECOD $AP$ |
|---|---|---|
| timestamp order | 0.905613 | 0.844487 |
| day round robin | 0.900371 | 0.849842 |

The ordering reversal **does not survive**. The detector leads in both arms; its
own score moves 0.005242 $AP$ between the two histories. The reversal is
produced by *which records the assembly places in the test set*, not by the
order the detector processed. Title, abstract, contributions, outcome section
and conclusion all rewritten. **CI-21.**

**A2 (split sensitivity) — FIX.** Seven chronological cuts, 60%–90%: ECOD
exceeds the detector at **3 of 7**, including the 85% cut this paper's split
uses. No ordering claim is a stable property of CICIDS2017.

**A3 (branch-wise discrimination) — FIX.** Tail-only $AP$ 0.831832 / AUC-ROC
0.829281 against the deployed composition's 0.728355 / 0.526623 — the tail term
**outranks the deployed detector** (+0.103477 $AP$, +0.302658 AUC-ROC) and the
auxiliary branch ranks **below chance** (AUC-ROC 0.281890). Because the score is
a maximum, the auxiliary overrides the tail wherever the tail is small. The
near-chance ranking is a property of the **composition**, not either component.
This refutes the withdrawn "tail term does the work" sentence — in the opposite
direction from the one the review anticipated.

All three fit because a prequential score depends only on prior records: one
instrumented pass per arm (7,775 s and 7,768 s at 4.86 ms/record, in parallel)
serves every split point and subset. The hook returns values `update_score`
already computes; the default path was verified bit-identical first. **≈2.2 h
against the 3 h cap.** Dumps reproduce the archived arms exactly on the
assembled arm and to 1.8e-05 $AP$ on the timestamp-ordered arm (Linux-vs-Windows,
the CI-16 class, stated in the findings).

Amendments **A–G** all applied and verified in the compiled PDF (twelve
mechanical checks: near-chance not constant; "can mask temporal dependence" not
"manufactures"; timestamp-sorted budgeted subsample with 76.628% at first use;
`sklearn.metrics.average_precision_score` named with version, tie convention and
positive class; "orthogonal" replaced; normalized lift present;
"label-privileged" present; "Not Attack Prevalence" gone from the title).
Amendment **G changed a finding**: in normalized $(AP-p)/(1-p)$ terms the
detector's lift peaks at the *unresampled* level, not at 10% as the additive
form implied.

**Verification refuted part of the review (CI-20).** Its overlap finding is true
and worse than it could see — CALIBURN v2's Tables 4–5 are our LITNET pooled and
CICIDS unresampled cells at lower precision. But its identification is false:
CALIBURN is *this manuscript's own earlier version*, not the suppressed
companion, and the archived overlap analysis records that the companion reports
no quantitative results at all. The disjointness sentence was accurate about the
paper it named — and is deleted anyway, because a sentence whose truth depends
on which related paper the reader assumes is a bad sentence in a blinded
submission.

## E3. The disclosure tables left the manuscript — an anonymity fix

The previous round put the overlap matrix and the dated correction history **in
the manuscript body**. That deanonymizes: a per-result-group account of what is
reused from named public preprints, plus a dated version history, identifies the
paper as a specific preprint's third version. Both tables now live only in
`packages/dtrap/PRIOR_APPEARANCE_EDITOR_NOTE.md`, expanded there with the
claims each version invalidates. The body keeps a short third-person statement:
prior versions exist, some measurements are shared with corrected
interpretation, several results are new, one dataset's results are withdrawn,
and the detail is with the editors. Verified: **zero identity tokens** in the
anonymized PDF (Youssef, Michel, arXiv IDs, CALIBURN, github.com, institution,
dated version history — all absent), no dangling references to the removed
tables. Manuscript went 13 pp → 12 pp on the move, then back to 13 pp with the
T3 additions.

## T3. Submission-side amendments

1. **ACM authorship policy** — verified against the current policy (retrieved
   2026-08-27; ACM's own page returns 403 to automated fetches, so the operative
   wording was taken from ACM policy summaries and SIG venue restatements). Two
   operative requirements: generative-AI use must be **fully disclosed in the
   Work**, with the **Acknowledgements section** the recommended location; and
   **AI tools may not be listed as authors**. The statement is now titled
   *Acknowledgements: Generative AI Usage*, cites the policy by name, states
   that no AI tool is an author, that no reported number was produced by one,
   and that the authors take full responsibility. Anonymity-preserving.
2. **2026 concurrent work cited and distinguished** — all three verified to
   resolve before citing: **FIRCE** (Barrett, Li, Dorai, Rajaganapathy,
   arXiv:2605.01962, cs.CR, May 2026); **FADES** (Barrett, Dorai, Li,
   Rajaganapathy, *Electronics* 15(10):2114, doi 10.3390/electronics15102114 —
   verified via Crossref); **Gurjar and Camp**, *Predicting Tail-Risk Escalation
   in IDS Alert Time Series* (arXiv:2601.14299, Jan 2026, 251 M Suricata
   alerts). Distinguished explicitly: the first two propose and evaluate
   detection machinery, the third forecasts operational alert volume; none
   examines how capture files are assembled into an evaluation stream.
3. **Category and metadata** — submission type is **full research paper**
   (recorded in `HUMAN_ACTIONS.md` step 6.2). CCS concepts now cover Security
   and privacy → Intrusion detection systems (500), Computing methodologies →
   Machine learning (300), and General and reference → Evaluation (300).
   Keywords now: streaming network intrusion detection, benchmark stream
   construction, evaluation methodology, experimental design, conformal risk
   control, reproducibility, provenance.
4. **Artifact availability** — the Data and Artifact Availability section is
   labelled and states the Apache-2.0 artifact, the provenance rule, the run
   manifests, the automated gate and the claim ledger, in anonymized form
   (submission-system channel during review).
5. **Length** — 13 pages, inside DTRAP's 10–25. Growth came from the
   shared-record section, the protocol table and the concurrent-work
   distinctions: material that strengthens external validity and the protocol
   description. Nothing was padded.

## T4. The IEEE TIFS withdrawal — VOID, the submission does not exist

**Superseding everything this section previously said.** On 2026-08-27 the
author checked the IEEE Author Portal directly. With filters set to *All
Publications* and *All Submission Statuses* the account returns exactly one
record — `TDSC-2025-10-1842`, **rejected 22 October 2025** — and no TIFS record
of any kind. The companion manuscript `arXiv:2510.09619` is a public preprint
and is not under review at any journal.

This section had reported a withdrawal "prepared to the last click": addressee,
portal migration, non-self-service procedure, resubmission policy, and an
execution order that put the withdrawal first. Every one of those findings was
accurate about IEEE TIFS as a journal, and none of them was the thing that
needed checking. The single signal pointing at the truth was recorded here and
misread — the manuscript ID was "NOT ON THIS MACHINE" after an exhaustive
search, which was treated as a retrieval task for the operator rather than as
evidence that there was nothing to retrieve.

**What was corrected, and where it had reached.** Two false statements were in
artifacts bound for publication and one was queued for a permanent public
record:

| artifact | false statement | now |
|---|---|---|
| `paper/main.tex`, Companion Manuscript Disclosure | "a correction process ... has been disclosed to the relevant editors" | states the companion is a preprint, not under review, no other editor to inform, and names the earlier error |
| `packages/dtrap/PRIOR_APPEARANCE_EDITOR_NOTE.md` | "the relevant journal has been or is being informed" | states the verified status, how it was verified, and that the error was the author's |
| `packages/sibling/ARXIV_V3_COMMENT_COEXIST.txt` (withdrawal variant) | "has been withdrawn from journal consideration by the author" | retired; a third **no venue claim** variant is now the one to paste |
| `packages/dtrap/COVER_LETTER.md` | pointed at the disclosure for "its status" | states the verified status directly |
| `HUMAN_ACTIONS.md` | withdrawal-first ordering, two void steps | steps removed; order is Zenodo → DOI → arXiv v3 → DTRAP |
| `SIBLING_DECISION.md` | two branches, both premised on the submission | replaced by the verified state and the rule it produced |
| `packages/sibling/WITHDRAWAL_LETTER_TIFS.md` | the letter itself | retired in place with a notice; not deleted |
| `PUBLISH_INSTRUCTIONS.md`, `FINALIZE_DONE.md`, `FINALIZE_REPORT.md` | ordering constraint and standing recommendation | marked void with the verification |

Recorded as **CI-25**, with the rule: a venue relationship asserted in any
artifact must be verified against the venue's own system before the artifact is
prepared; researching a venue's procedures is not verification of a
submission's existence; and a hedge like "has been or is being" in a factual
disclosure is a signal that the fact was never checked.

Nothing was ever sent. That is the only reason this reached no editor, and it
is not a control — the control is the verification, which is now recorded.

## T5. Verification state after T4

*(Superseded by T6 below, which reports the state after the round-3 sweep.)*

| check | result |
|---|---|
| `pytest -q` | 72 passed |
| provenance gate (orphans) | 564 macros, 0 orphans, 0 mismatches, 0 ambiguous, index verified |
| **typed-literal scan (new)** | 14 files scanned; **0 unmanifested literals in enforced files**; 31 reported in record-only files |
| claim ledger | 31 rows, every reference resolves |
| manuscript macro check | 198 used, all defined |
| **citation check (new)** | 40 cited keys, all resolve |
| anonymous compile | 3-pass, exit 0, **0 undefined**, 17 pp |
| arXiv named variant | 3-pass, exit 0, 0 undefined, 17 pp, `.bbl` shipped, identifiers restored |
| DTRAP artifact | 181 files, identity scan clean |
| anonymity scan of the PDF | zero identity tokens (the one `github.com` is a third-party citation to PyOD's issue tracker, not an author identifier) |
| DTRAP source package | rebuilt, identity scan clean |

## Round 3 (27 Aug 2026) — what changed and why

Seven operator items, all executed. No new review cycle was opened.

**1. The provenance gate was fixed structurally, not four numbers at a time.**
The gate scanned only `paper/numbers.tex`, a file generated *from* the
manifests, and therefore certified transcription while never reading the
manuscript. Three defects of that class had already shipped past it. The scan
now covers the manuscript, everything it `\input`s, and every file the claim
ledger cites, with a tiered policy: files whose purpose is to record withdrawn
numbers are reported, not failed, and genuine non-measurements sit in a
reasoned allowlist. **First honest run: 88 findings.** Four were the known
table literals; 28 were in the findings file backing this round's own new
claims; the remainder were a sign-handling false-positive class, record-only
files, and six derived values now emitted as macros. One value had no manifest
because the run that produced it was discarded rather than archived, and was
deleted rather than back-filled. Final state: **0**. Recorded as CI-22, with
the general lesson — a check that validates a generated artifact against its
own generator proves transcription, not provenance.

**2. ECOD's batch dependence is now a numbered subsection with a measurement.**
The A2/archived discrepancy was traced to PyOD's `decision_function`, which
concatenates the stored training matrix with the scored batch before
recomputing the column ECDFs. Holding the evaluated records and the fitted
model identical and varying only the accompanying batch: AP 0.758205 (240,000
alone), 0.760029, 0.762108, **0.755142** (480,000 = validation+test). The last
value **reproduces the archived arm exactly**, which is what turned a
suspected mechanism into a demonstrated one. Delta 0.003063, spread 0.006966,
and the relationship is not monotone. Prior awareness is credited (PyOD issue
#401, 2022, still open; ADBench holds the batch constant; the ECOD paper gives
no out-of-sample rule) and the novelty claim is confined to the measurement and
its cross-study consequence. Every ECOD number in the paper now states the
batch it was scored in — including the prevalence sweep, whose batch varies
from 160,917 to 480,000 records across levels.

**3. A3 was promoted from support to a primary finding.** It has its own
section, its own contribution entry and a sentence in the abstract. The
numbers justify it: the deployed `max` composition ranks worse than its own
tail term by 0.103477 AP and 0.302658 AUC-ROC, and the auxiliary branch is
*inverted* (AUC-ROC 0.281890) rather than uninformative, so a working ranking
is overridden by a broken one wherever the tail is small.

**4. The conformal-vacuity result was demoted to corroboration.** It appears in
the superseded public versions and cannot be presented as new. It is stated in
third person in the disclosure section, explicitly not as a contribution, and
"conformal risk control" was dropped from the keyword list so it does not steer
reviewer assignment toward a topic this paper does not advance.

**5. Thirteen references added and distinguished**, each resolved against
Crossref, the publisher record or the arXiv listing *before* being cited.
Biswas (doi:10.20944/preprints202606.0903.v1) required Crossref because
preprints.org refuses automated fetches; it is the nearest neighbour to this
work and is distinguished explicitly — it isolates unseen-attack coverage from
drift across different datasets and never intersects held-out sets, whereas
this work isolates composition from history order within one fixed multiset via
the common-records restriction.

**6. Prevalence-changes-AUC-PR is credited, not claimed.** Davis and Goadrich
and Saito and Rehmsmeier own the metric result, with Axelsson for the IDS
base-rate consequence. Our narrower point is that this benchmark's prevalence
regime is doubly constructed: by a retention budget anti-correlated with attack
density, then by the assembly step.

**7. Two further defects were found by doing the above**, both of the same
family as CI-22 — a check that reads as comprehensive while the defect sits
outside what it inspects. CI-24: a document-only re-run claimed a compute-time
macro for work it reused from cache, and the gate refused to render on the
disagreement. CI-26: two citations added in the previous round were never in
the bibliography and rendered `[?]` under a truthful "0 undefined references"
verdict, because natbib reports a missing entry as a citation warning rather
than an undefined reference. A citation check now runs beside the macro check.

## T6. Three-auditor adversarial sweep (27 Aug 2026)

Three independent auditor lenses over the manuscript and every artifact —
claim-versus-evidence, cross-artifact consistency, and a hostile DTRAP referee —
with **every finding independently verified by a separate agent instructed to
refute it** before it was acted on. 57 findings raised, **41 survived**
verification, consolidating to 14 distinct defects. All were fixed.

The verification step earned its cost: 16 findings were refuted, mostly quotes
that did not appear in the file as filed or severities inflated above what the
text supported.

**What it caught that the gates could not.** The most serious finding was a
process defect no automated check in this repository could see: two withdrawn
claims had been corrected in `scripts/make_contrast_deliverables.py` and the
script was never re-run, so `findings_contrast.md` — cited by the claim ledger
and shipped inside both the DTRAP artifact and the Zenodo bundle — still
carried the heading "order only (prevalence held constant)", the sentence
"Order is the only manipulated variable", and "No split-rule sensitivity check
has been run". Every number in that stale file still resolved to a manifest, so
the provenance layer passed it; the defect was in prose. Recorded as **CI-27**
with the rule: editing a generator is not a fix, running it is.

The same withdrawn split-rule claim survived independently in `README.md`,
`REBUILD_STATUS.md` and `REVIEWER_KIT/RESPONSE_SHELF.md`. Alongside it: a
corrected-incident count of 18 in six places against a log of 27; stale gate
statistics (356 and 362 macros against 564); a stale page count reaching an
instruction to type "10 pages" into the permanent public arXiv Comments field;
and five self-descriptive universals in the manuscript that its own tables
falsify — "every number in this paper is a macro" (protocol constants and cited
third-party values are typed), "every AUC-PR is reported with normalized lift"
(four tables print none), "every ECOD number is scored validation-plus-test"
(two analyses score test-only), an unsourced comparison against "most of the
differences this literature reports as method contributions", and a branch
binding share quoted from a 50,000-record prefix to characterise a
240,000-record slice.

That last one was fixed by measurement rather than by hedging: the share is now
computed on the slice it describes, from components already archived, and
emitted as a macro (\RevBranchAuxBindsHeldoutPct, 58.452%, via
`scripts/emit_branch_binding_macro.py`). Two numbers taken from Biswas via
Crossref metadata were dropped, and the universal negative about that work was
softened to the hedge the paper uses elsewhere, because metadata is not a
full-text read.

**Verification state after the sweep:** 72 tests; gate 564 macros / 0 orphans /
0 ambiguous; literal scan clean; macro and citation checks
clean; ledger 31 rows; both builds 3-pass, exit 0, **0 undefined**, **17 pp**, **no overfull boxes**; DTRAP artifact
186 files, identity scan clean; anonymized PDF and source package carry zero
identity tokens.

## What remains unresolved, and why

- **The factorial decomposition.** A1 removes the membership difference *post
  hoc*; it does not decompose order from prevalence prospectively. Shelved with
  a ≈13 h estimate (S8). The paper says a factorial design is the natural next
  experiment and does not pretend otherwise.
- **Uncertainty quantification.** Determinism removes seed variance only. With
  attack runs of median/p90/max 2/70/2522, an IID bootstrap is inappropriate;
  event-block or rolling-origin is the right instrument and is not applied (S7).
- **Single-reviewer round.** No convergence evidence. Recorded above.
- **One operator-only item**: the ACM waiver PDF, in email, flagged in
  `HUMAN_ACTIONS.md`. The TIFS manuscript ID is no longer needed — there is no
  such submission (T4, CI-25).
- **The sibling's threshold-derivation tension** flagged by an earlier auditor
  needs a human read of the companion manuscript; it does not affect this
  paper's packages.
- **The companion preprint itself.** It shares the audited codebase and the
  method-identity findings reach it, so it needs correcting or replacing. That
  is separate work on a separate manuscript, and it is *not* a venue question:
  it is not under review anywhere (T4, CI-25).
- **Priority on the ECOD batch measurement.** We assert only that we are aware
  of no prior published quantification, on the basis of a literature and
  issue-tracker search recorded in the section. A reader may know otherwise;
  the measurement stands either way.

One round. Not looped.
