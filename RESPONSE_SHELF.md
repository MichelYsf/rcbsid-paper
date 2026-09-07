# RESPONSE_SHELF — analyses asked for by review and deliberately not run

Each entry records what was asked, why it is not in the paper, and what the
paper says instead. An entry leaves this file only when the analysis is run
and manifested, or when the reason below is shown to be wrong. Dates are
absolute. The referee report this round answers is
`REFEREE_TRIAGE.md`; the bounded analyses that were run are in
`findings_referee_analyses.md` (manifest
`referee_bounded_analyses_20260906T182158_de69afab`).

## 1. Crossed history-by-sample design (first report BLOCKING 1; second report BLOCKING 1 and MAJOR 1) — shelved 2026-09-06, reaffirmed 2026-09-07

The second report adds that ECOD's benign-only training rows also differ
between the arms, so the shared-record comparison holds fixed the evaluated
sample and, in the shared-batch columns, ECOD's batch, but not the fitted
model. Table 6's caption and Section 6.1 now say exactly that, cite the two
movements the design does measure (the detector by 0.005242 AP between the
two prefixes, ECOD by 0.002788 AP between the two fitted models on the
identical shared batch), and the conclusion carries the assumption in a
clause. The reason the crossed design stays shelved is unchanged.

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

## 4. Table 9 diagnostics on the held-out slice (second report, MAJOR 3) — shelved 2026-09-07

**Asked.** Recompute the Section 9 diagnostics (posterior mass on short runs,
scores at the cap, distinct values, score standard deviation) on the 30,000
held-out records whose AP and AUC-ROC the section reports, rather than on the
first 15,000 records of the stream.

**Why it is not run.** The ablation run archived no per-record scores: its
manifests (`s6_bocpd_corrected_ablation_20260824T092655_a47acf51` and the
27 August re-derivation) declare a single output, the findings document, and
`results/s6_ablation_arms.json` holds per-arm metrics only. Recomputing the
diagnostics on the held-out slice would rerun both detector variants, which
this round's bound (archived data only) excludes.

**What the paper says instead.** Section 9 states that the prefix diagnostics
are consistent with, not proof of, the held-out ranking, names the two
populations and says the held-out scores were not archived.

## 5. Intervals for the LITNET rows (second report, MAJOR 5) — shelved 2026-09-07

**Asked.** Event-block bootstrap intervals for the four LITNET rows of Table 5.

**Why it is not run.** The archived per-record score dumps cover the two
CICIDS arms only (`results/score_dumps/`); no LITNET per-record scores were
archived, so a bootstrap over them would require rerunning every LITNET
method, outside the round's bound.

**What the paper says instead.** Section 12 names which results carry
intervals and which do not, and why.

## 6. A size-only ECOD manipulation at fixed batch composition (second report, MAJOR 2) — not possible by construction

**Asked (implicitly).** The complement of the composition-only experiment:
change the batch size while holding its content fixed.

**Why it is not run.** A batch's content is the set of records in it; a
larger batch contains records a smaller one does not, so size cannot vary
with content fixed. What can be held fixed is size while content varies,
which analysis E of this round did (`findings_ecod_composition.md`): at
identical size and model, content alone moves the shared records' AUC-PR by
0.007552. The paper states that both the size and the content of the batch
enter through the recomputed empirical CDFs, and keeps "in size or
composition".

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
