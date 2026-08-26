# TRIAGE_REPORT — one round, executed 26–27 August 2026

Input: `Fresh_Adversarial_Review_and_Triage.pdf` (15 pp, MAJOR REVISION — DO NOT
SUBMIT THIS VERSION), plus seven binding operator amendments (A–G) and three
bounded analyses (A1–A3) under a hard three-hour local compute cap.

**Round status: closed.** One round, no loop. The manuscript is materially
different: its central claim is narrower, better supported, and now survives the
test that would have broken it.

## The headline: verification changed the paper's claim

Analysis **A1** restricted both arms to the **78,000 records both held out** and
recomputed the two deterministic methods there.

| arm | detector $AP$ | ECOD $AP$ |
|---|---|---|
| timestamp order | 0.905613 | 0.844487 |
| day round robin | 0.900371 | 0.849842 |

**The ordering reversal does not survive.** The detector leads in *both* arms
once membership and prevalence are held fixed, and its own score moves by only
0.005242 $AP$ between the two histories. The reversal reported in the previous
version is produced by *which records the assembly places in the test set*, not
by the order the detector saw. The paper now says exactly that, in the title,
the abstract, the contributions and the conclusion. Recorded as **CI-21**.

Two further analyses changed claims:

- **A2 (split sensitivity).** Across seven chronological cuts (60%–90%), ECOD
  exceeds the detector at **3 of 7**, including the 85% cut this paper's split
  uses. No ordering claim is a stable property of CICIDS2017.
- **A3 (branch-wise discrimination).** Tail-only reaches $AP$ 0.831832 /
  AUC-ROC 0.829281; the deployed composition reaches 0.728355 / 0.526623. The
  tail term **outranks the deployed detector** by 0.103477 $AP$ and 0.302658
  AUC-ROC, and the auxiliary branch ranks *below* chance (AUC-ROC 0.281890).
  The near-chance ranking is a property of the `max` composition, not of either
  component. This refutes the removed "tail term does the discriminative work"
  sentence — and refutes it in the opposite direction from the one the review
  anticipated.

All three were affordable only because a detector score depends solely on the
records before it: one instrumented pass per arm (7,775 s and 7,768 s at
4.86 ms/record, run in parallel) yields every split point and every subset. The
instrumentation hook returns values `update_score` already computes and was
verified bit-identical on the default path first. Total analysis compute:
**≈2.2 h against the 3 h cap.**

## Verification-first: where the review was right, and where it was not

The reviewer had no repository access and said so. Every factual claim was
checked against code, manifests or archived PDFs before acceptance.

**VERIFIED-TRUE and acted on:** the identification objection (T5, T6) — the
round's most important finding; the method-identity scope objection (T12); the
mean-magnitude objection (T11); "AUC-ROC 0.50962 means constant" is false (T13,
747 distinct values, sd 0.159341); the exchangeability objection (T14); the
missing-protocol objection (T10); the unsupported frequency claims (T2); the
prior-art positioning (T3); the additive-lift headroom objection (T16); and all
the arithmetic checks (T4, T17) reproduce exactly.

**VERIFIED-TRUE, and worse than the review could see (T18):** checked directly
against the public CALIBURN PDF, its Table 4 (0.943 / 0.261 ± 0.097 / 0.229)
and Table 5 (0.863 / 0.545 / 0.433 ± 0.078 / 0.419 / 0.342) are our LITNET
pooled and CICIDS unresampled cells at lower precision — deterministic values
exactly, HST values matching our three-draw means. Real, substantial, and
previously undisclosed per result group.

**VERIFIED-FALSE — the identification (T18).** The review infers CALIBURN "is
the suppressed companion" and that "the two papers report disjoint result sets"
is therefore false. CALIBURN is **this manuscript's own earlier version**, which
the manuscript already disclosed as such. The suppressed companion is a
different paper, and this project's archived overlap analysis records that it
reports *no quantitative results anywhere*. The disjointness sentence was
accurate about the paper it referred to. It is deleted regardless — a sentence
whose truth depends on which related paper the reader assumes is a bad sentence
in a double-anonymous submission. Recorded as **CI-20**.

## Operator amendments A–G: all applied

| # | amendment | disposition |
|---|---|---|
| A | Assembly as uncontrolled treatment; "Not Attack Prevalence" leaves the title | **DONE.** New title *Stream Assembly Is an Uncontrolled Treatment…*; three ledger-checked candidates in `TITLE_ABSTRACT_OPTIONS.md`; no claim attributes the outcome to ordering alone or excludes prevalence |
| B | ECOD a label-privileged diagnostic reference; no superiority language | **DONE.** Every comparison reframed; the reversal is stated as a pipeline-level evaluation outcome |
| C | Method identity scoped; tail-term sentence removed unless A3 verifies | **DONE.** Three facts stated separately; A3 did *not* verify the sentence, and replaced it with the composition finding |
| D | Mandatory wording | **DONE.** near-chance not constant; "can mask temporal dependence" not "manufactures"; "timestamp-sorted budgeted subsample" with 76.628% at first use; metric named (`sklearn.metrics.average_precision_score`, 1.8.0, step-wise, positive class 1, no weighting); frequency claims narrowed; "orthogonal" replaced by case-study-and-mechanism-audit; LITNET identity presented as an audit check |
| E | Disclosure rebuilt | **DONE.** Disjointness sentence deleted; overlap matrix (reused / re-derived / corrected / new / withdrawn) and correction-history table (v1 23 May 2026, v2 25 Jun 2026, both public preprints, neither accepted) in the manuscript; `packages/dtrap/PRIOR_APPEARANCE_EDITOR_NOTE.md` drafted, anonymity-compliant |
| F | Protocol table + stream-assembly pseudocode | **DONE.** Table 2 covers features, scaling, missing/infinite, eligibility, budgets, stride, warm-up, hazard, cap, update timing, label access, baselines, metric; pseudocode for all three assemblies and the split |
| G | Normalized lift and per-draw values | **DONE.** $(AP-p)/(1-p)$ beside raw $AP$ and $p$ throughout; every per-draw value printed. **This changed a finding**: the detector's lift peaks at the *unresampled* level (+0.3914) in normalized terms, not at 10% (+0.3865) as the additive form suggested |

## SHELF (7 items, each with measured or estimated cost)

In `REVIEWER_KIT/RESPONSE_SHELF.md` §"From the fresh round": event-block/
rolling-origin uncertainty (S7); the factorial decomposition (S8, ≈13 h);
protocol-aligned ECOD (S9); truncated-regime characterization (S10);
tuned-repair validation (S11, 8–20 h); the systematic literature survey (S12,
weeks); artifact audit (S13, resolved by shipping the artifact). Nothing was
shelved that the analyses could have settled inside the cap.

## Verification state after the round

| check | result |
|---|---|
| `pytest -q` | 72 passed |
| provenance gate | 510 manifested macros, 0 orphans, 0 mismatches, 0 ambiguous, index verified |
| claim ledger | 25 rows (A5b, A7b added for the new findings), every reference resolves |
| manuscript macro check | 184 used, all defined |
| anonymous compile | 3-pass, exit 0, **0 undefined references**, 13 pp |
| arXiv named variant | 3-pass, exit 0, 0 undefined, 13 pp, `.bbl` shipped, identifiers reinstated |
| DTRAP artifact | 172 files, anonymity scan clean |
| corrected incidents | 21 |

## What a referee should now be told

The paper's claim is smaller than the version reviewed, and it is the claim the
evidence supports: **stream assembly is an uncontrolled treatment whose
membership component dominates the measured outcome.** The reversal that
motivated the previous framing is real as an evaluation-level fact and is *not*
an ordering effect — we established that ourselves, by running the analysis that
could have refuted us, and it did.
