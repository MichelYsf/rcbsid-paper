# Superseded manifests — retired from the index, preserved as history

Files here are real run manifests that must NOT contribute numbers to the
manuscript. `provenance._reindex_macros()` globs `results/manifests/*.json`
non-recursively, so anything in this directory is outside the macro index while
remaining on disk and in git history. Nothing is ever deleted.

A manifest is moved here only for a stated reason, recorded below.

## s4_construction_contrast_20260818T123509_281ee7ae.json
## s4_construction_contrast_20260818T123941_7b00764c.json
Smoke tests taken while the S4 harness was being designed: `budget` 9,000 and
30,000 records against a prefix of the LITNET streams, wall times 193 s and
287 s, writing `_smoke_litnet.csv` and `_smoke2.csv`. They emit the same macro
names as the real experiment (`ContrastLitnetUdpFloodNaturalProposedDetectorAucpr`
and siblings) with values measured on a few thousand rows.

The canonical run is `s4_construction_contrast_20260818T124510_2b2d27b1`:
`budget` 0 (full streams), 62,609 s of wall time, output
`results/rebuild_parts/contrast_litnet_natural.csv`. Its values are the ones in
the committed CSV (udp_flood proposed 0.394428, HST 0.552675, ECOD 0.321185).

Why this matters more than the tidy-up suggests: before the CI-5 fix the gate
resolved each macro to `index[name][-1]`, and the index is built from
`sorted(glob(...))`, i.e. filename order. The canonical run happens to sort
last, so the correct value would have been chosen — by accident of the
timestamp in the filename. Had either smoke test been taken an hour later, a
9,000-row prefix measurement would have entered the manuscript wearing the full
run's name, and every check in place at the time would have reported green.

## s4_contrast_deliverables_20260819T113331_a7a5eadd.json
The first S4 deliverables run, superseded on 2026-08-19 after adversarial
review. Its macros are not wrong, but the document it generated was: seven
printed numbers had no `emit_macro` call (the three AUC-PR deltas and four
LITNET attack counts, one of which — 14,621 — appeared in no manifest at all
while being written into a manuscript-bound LaTeX table), the cross-arm delta
column subtracted across a chance floor that moves with the construction, and
the prose asserted "no attack was added, removed, or resampled", which is true
of the stream and false of the evaluated slice. Superseded by the run that
emits a macro for every number it prints. Retired rather than deleted so the
withdrawn version stays inspectable.

## s4_contrast_deliverables_20260819T121003_2a215fc8.json
Intermediate same-session iteration of the corrected deliverables run, retired
immediately: it still wrote the LaTeX table as bare literals. Superseded by the
run whose table carries only macro references, so that no number in a
manuscript-bound file can sit outside the provenance gate's view.

## s4_contrast_deliverables_20260819T121304_c90469b2.json
Superseded by the run that adds the seed-sensitivity section, after three
extra-seed HST runs were recovered from the stopped instance. Its macros are
unchanged and correct; it simply predates the evidence that the HST/ECOD
ordering on the LITNET composite flips with the seed.

## s4_contrast_deliverables_20260820T081139_a5bf9183.json
Superseded when the Stage 2 sweep was found to hold a third HST seed for the
CICIDS interleaved cell (CI-16). Its seed-sensitivity section reported 1 of 2
cells flipping; the correct figure is 2 of 2.

## s3_score_threshold_verification_20260820T084128_ce4545b5.json
First Stage 3 run, superseded within the hour. Its numbers were right but two
sentences in the document it generated contradicted them - written from an
expectation formed before the measurement rather than from the measurement.

## s6_bocpd_corrected_ablation_20260820T094323_d28cfa65.json
The Stage 6 ablation as first run (22.3 min of local compute). Its measured
values are correct and are carried forward unchanged - the arm metrics in
`results/s6_ablation_arms.json` come from this run and cite its id. It is
retired because the document it generated read the result as "repairing the
change-point statistic degrades detection", which the saturation diagnostic
shows is the wrong reading: the corrected variant emits a constant 0.25 on 93%
of records and cannot rank at all. Superseded rather than recomputed, because
re-paying 22 minutes to reword a document would breach the 30-minute cap.

## s5_verified_contributions_20260820T085552_1ae23176.json
Superseded when Stage 6 completed: the ChangePoint entry said the verdict held
"unless Stage 6 changes the measurement". Stage 6 ran and did not change it.
Counts and macro values are identical; only the action text is updated.

## s6_bocpd_corrected_ablation_20260820T101012_e216266e.json
Superseded same-day: its cached-arms path failed to re-emit the arm AUC-PR
macros, leaving the findings table orphaned - the CI-11 class again. The
replacement emits them from the cache, which cites the originating run.

## s2_prevalence_relabelled_20260820T082620_005ffef6.json
Superseded same-day by a regeneration: the LaTeX table it wrote carried
unescaped percent signs in the level labels, which LaTeX reads as comments -
the row terminators vanished and the manuscript could not compile. Macro
values are identical in the replacement.

## s2_prevalence_relabelled_20260824T094843_2ef126ae.json
Superseded by the review-round regeneration: amendment G requires normalized
lift (AP-p)/(1-p) beside every additive lift, and the individual per-draw
values wherever spread is claimed. Macro values for the previously emitted
names are unchanged.

## supplementary_macros_20260824T102403_89c8967a.json
Superseded by the review round: amendment G adds normalized lift (AP-p)/(1-p)
for the contrast arms and the Stage 6 ablation. Previously emitted values are
unchanged.

## s4_contrast_deliverables_20260820T082833_05219839.json
Superseded by the review round: amendment G requires the individual seed
values to be printed wherever spread is claimed, so the deliverables run now
emits per-draw macros. All previously emitted values are unchanged.

## review_bounded_analyses_20260826T223442_cfe47f09.json
Superseded within the same round: the first analyses run claimed exact
reproduction of the natural arm when it differs by 1.8e-05 (a cross-platform
difference of the class recorded in CI-16), and did not emit the composition
and margin macros the corrected conclusions need. All measured values are
unchanged in the replacement.
