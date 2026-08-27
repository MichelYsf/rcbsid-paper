# TRIAGE_REPORT — the binding round, 26–27 August 2026

One round, closed. Covers the pre-submission review triage, seven operator
amendments, three bounded analyses, four submission-side amendments, and the
IEEE TIFS withdrawal preparation. Nothing was published, submitted, or sent.

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

## T4. IEEE TIFS withdrawal, prepared to the last click

Fetched fresh 2026-08-27 and cited in the letter:

- **The portal has migrated.** TIFS now uses the IEEE Author Portal at
  `https://ieee.atyponrex.com/journal/tifs-ieee`, not ScholarOne (IEEE Signal
  Processing Society TIFS page). The brief's warning was correct, and any
  previously recorded address is stale — the letter tells the operator to check
  which system holds *his* submission, since a pre-migration submission may
  still live in the old one.
- **Withdrawal is not self-service.** IEEE guidance is that authors cannot
  withdraw from within the submission account and must contact the editorial
  office. The letter is therefore the mechanism; a portal *Withdraw* action, if
  present, is confirmation and not a substitute.
- **Addressee**: Editor-in-Chief **Prof. Luisa Verdoliva** (University of Naples
  Federico II), `verdoliv@unina.it`, cc the editorial-office address from the
  submission confirmation.
- **Resubmission**: IEEE does not prohibit later submission of a corrected
  manuscript; a voluntary withdrawal is not a retraction, and IEEE's
  post-publication policies govern published articles, which this is not. The
  letter flags that the operator should confirm this against his own submission
  terms rather than rely on the general policy.
- **Manuscript ID: NOT ON THIS MACHINE.** Searched the whole profile, the
  repository, and every prior session transcript for `TIFS-#####` patterns and
  "manuscript ID" near TIFS. Zero hits. It is the single field the operator must
  supply, marked `[[MANUSCRIPT ID]]` in two places.
- **arXiv v3 comment** is now unambiguously the **withdrawal variant**, and
  states in one clause that v1/v2 cited a Zenodo DOI that was never minted. The
  coexistence variant is retained only, and labelled, as the branch not taken.

## T5. Verification state at exit

| check | result |
|---|---|
| `pytest -q` | 72 passed |
| provenance gate | 510 macros, 0 orphans, 0 mismatches, 0 ambiguous, index verified |
| claim ledger | 25 rows, every reference resolves |
| manuscript macro check | all used macros defined |
| anonymous compile | 3-pass, exit 0, **0 undefined references**, 13 pp |
| arXiv named variant | 3-pass, exit 0, 0 undefined, 13 pp, `.bbl` shipped, identifiers restored |
| DTRAP artifact | 174 files, identity scan clean |
| anonymity scan of the PDF | zero identity tokens |
| corrected incidents | 21 |

## What remains unresolved, and why

- **The factorial decomposition.** A1 removes the membership difference *post
  hoc*; it does not decompose order from prevalence prospectively. Shelved with
  a ≈13 h estimate (S8). The paper says a factorial design is the natural next
  experiment and does not pretend otherwise.
- **Uncertainty quantification.** Determinism removes seed variance only. With
  attack runs of median/p90/max 2/70/2522, an IID bootstrap is inappropriate;
  event-block or rolling-origin is the right instrument and is not applied (S7).
- **Single-reviewer round.** No convergence evidence. Recorded above.
- **Two operator-only items**: the TIFS manuscript ID and the ACM waiver PDF,
  both in email, both flagged in `HUMAN_ACTIONS.md`.
- **The sibling's threshold-derivation tension** flagged by an earlier auditor
  needs a human read of the companion manuscript; it does not affect this
  paper's packages.

One round. Not looped.
