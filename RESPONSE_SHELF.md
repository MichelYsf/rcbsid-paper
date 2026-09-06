# RESPONSE_SHELF — analyses asked for by review and deliberately not run

Each entry records what was asked, why it is not in the paper, and what the
paper says instead. An entry leaves this file only when the analysis is run
and manifested, or when the reason below is shown to be wrong. Dates are
absolute. The referee report this round answers is
`REFEREE_TRIAGE.md`; the bounded analyses that were run are in
`findings_referee_analyses.md` (manifest
`referee_bounded_analyses_20260906T182158_de69afab`).

## 1. Crossed history-by-sample design (referee BLOCKING 1) — shelved 2026-09-06

**Asked.** Score each arm's detector state on the other arm's held-out
records, so that history and sample membership are crossed and the headline
attribution (the reversal follows test membership, not history) is identified
by design rather than assumed.

**Why it is not run.** The detector is prequential and updates its sufficient
statistics on every record it scores, including held-out ones (Table 2,
update-timing row). The records one arm holds out that the other does not
share are, in the other arm, training or validation records: of the 103,189
attacks that leave the held-out slice under day round robin, 77,670 sit in that
arm's training split and 25,519 in its validation split (analysis C). A
crossed cell therefore scores records the scoring arm's model state has
already absorbed, and reads training exposure as history. That is not the
quantity the design would need to isolate, and no post-hoc correction
recovers it from the archived per-record scores.

**What the paper says instead.** Section 6.1 and the abstract state the
attribution as *attributable to* test membership and state the assumption it
rests on: that history contributes no more on the records the arms do not
share than on those they do. The shared-record result is reported under both
ECOD batches (analysis A) with event-block bootstrap intervals (analysis B),
and the Threats section keeps the sentence that a factorial design would
decompose the remaining factors.

## 2. Event-based (range-aware) precision and recall (referee MAJOR 4) — future work, 2026-09-06

**Asked.** Report an event- or range-based sensitivity beside flow-wise
average precision, since a 2,522-record incident outweighs a one-record
incident 2,522:1 under flow-wise scoring; Tatbul et al. (NeurIPS 2018) is the
reference.

**Why it is not in this paper.** Flow-wise average precision is the convention
of every compared study on these benchmarks, and this paper's claims are about
what that convention measures under assembly. Range-based precision and recall
introduce a metric family with free parameters (positional bias, cardinality
weighting, overlap reward) that none of the compared work reports, so a value
under it could not be set beside the compared numbers. It is a separate
evaluation-protocol study, not a re-analysis of the archived scores under this
paper's protocol.

**What the paper says instead.** Table 2, metric row: Tatbul et al. is cited,
with the sentence that flow-wise AP is the convention of the compared work and
event-based evaluation is future work.

## 3. Ablation of the infinity and NaN mapping (referee MAJOR 10) — shelved 2026-09-06

**Asked.** An ablation showing what zero-imputing infinities and missing
values contributes to the detector and ECOD contrasts, since the mapping can
create point masses.

**Why it is not run.** Analysis D counted what the mapping touches, from the
archived streams: 4 of the 1,600,000 CICIDS2017 rows (8 infinite cells in 2 of
84 features, no NaN anywhere), and 0 rows in each of the three 500,000-row
LITNET streams (no infinite or missing cell at all). An ablation would rerun
both CICIDS arms' detectors and ECOD to measure the effect of eight cells in
four records; the count bounds what it could find, and detector reruns are
outside this round's bound (archived data only).

**What the paper says instead.** Table 2, missing/infinite row, carries the
counts as macros.

## Not shelved: the paired cut-by-assembly sweep (referee MAJOR 3)

Ran, from archived scores with ECOD refit at each cut for both arms, inside
the three-hour bound (the whole A–E run took 1,427 s). Result in
`findings_referee_analyses.md` § E and in Section 6.2: the arms' orderings
differ at 3 of the 7 cuts (75 %, 80 %, 85 %) and agree at the other 4, where
the detector leads in both arms; the detector leads in the day-round-robin arm
at every cut.

## Standing: rolling-origin resampling

The Threats section states that the reported intervals are moving-block
bootstrap intervals over the evaluated slice and that a rolling-origin
procedure is not applied. It is not shelved with a reason; it is stated as a
limit.
