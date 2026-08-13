# DONE_ALL — 2026-08-13

Branch `exp/prevalence-and-tuning`. Stages 0–2 completed on the local Windows
machine; Stage 3 was migrated to AWS EC2 and completed **partially**; Stage 4
was never reached.

## How the run ended

The EC2 instance (`i-0a474922fd3f64d86`, c7i.2xlarge **spot**, eu-central-1a,
100 GB gp3 modified live to 6000 IOPS / 500 MB/s) was **reclaimed by AWS at
approximately 2026-08-13 11:03 UTC**:

> `instance-terminated-no-capacity` — "Your Spot instance was terminated
> because there is no Spot capacity available that matches your request."

This was not the cost guard and not the 12:35 UTC watchdog; both were still
holding. The root volume had `DeleteOnTermination=true` and no snapshot
existed, so it was deleted with the instance. The last successful artifact
pull was **09:27 UTC**, so roughly 1.5 hours of results — later grid points
and any finals that had begun — were lost with the volume.

**Instance runtime: 2026-08-12 09:16:08 UTC → ~2026-08-13 11:03 UTC =
~25.8 hours at $0.194/h spot = ~$5.00** (inside the $8 guard). Approximately
$3.90 of that was an idle window caused by an operator `pkill` self-kill,
documented in RUN_REPORT.md rather than glossed over.

## Stage 3 coverage actually achieved

- CICIDS2017 grid points evaluated: **18 of 24**
- LITNET-2020 grid points: 14 attempted, **abandoned as statistically void**
- Final (full-stream) runs completed: **0 of 8**

Because no finals completed, **`table4_litnet_tuned.tex` and
`table5_cicids_tuned.tex` contain default-configuration rows only**, and
`tuning_delta_summary.tex` has no tuned rows. `findings_tuning.md` reports
validation-stage selections for five CICIDS2017 baselines and explicitly
declines to draw any default-versus-tuned verdict, because that comparison
requires test-set numbers that do not exist.

Validation-stage selections (CICIDS2017, validation 21.70% / 52,085 attacks —
statistically sound):

| baseline | selected config | val AUC-PR |
|---|---|---|
| lof | `n_neighbors=50` | 0.8490 |
| loda | `n_bins=10, n_random_cuts=100` | 0.3574 |
| hst | `max_depth=10, num_trees=100, window_size=500` | 0.2650 |
| iforest_asd | `n_estimators=200, window_size=4096` | 0.2149 |
| kitnet | `max_size_ae=20` | 0.2082 |

Nine grid points were dropped and logged under the runbook's crash rule: all
eight HST `max_depth=20` configurations (genuinely infeasible — river
allocates ~2^21 nodes per tree, exceeding 6 GiB per worker) and one LODA point
lost to an over-tight 3 GiB address-space cap that was my error, since raised.

## LITNET-2020: why its tuning was abandoned

`configs/experiment_litnet_trial.yaml` sets `time_column: null`, so the stream
stays in file order and the chronological 70/15/15 split yields train 7.426% /
validation **0.003%** / test 0.059% attack prevalence. **The validation split
holds 6 attacks in 225,000 rows**, so validation-AUC-PR selection there is
noise, not tuning. The window was reallocated to CICIDS2017, which was in the
runbook's original two-dataset scope.

**This bears on the manuscript and is the most important finding of Stage 3.**
The published LITNET numbers are computed on that same 0.059% test slice
(~133 attacks in 225,000 rows) while the paper describes LITNET as the "5.2%
rare-attack regime" — 5.2% is the dataset-wide rate. The headline result
(AUC-PR 0.943, 2.21x the next-best method) therefore rests on ranking ~133
flows, Table 9's isotonic calibration is fit on the 6-positive validation
split, and the train→val→test prevalence swing violates the exchangeability
assumption the CRC section relies on. Nothing was changed: this is a
manuscript decision, not an agent decision. See `findings_tuning.md`.

## Deliverables

Produced:

- [x] `results/prevalence_sweep_cicids.csv` — Stage 2, 114 rows, internal control bit-exact vs Stage 1
- [x] `results/prevalence_sweep_table.tex` — Stage 2 LaTeX table (mean ± std over 3 resample seeds)
- [x] `figures/fig6_prevalence_sweep.pdf` — Stage 2 figure
- [x] `findings_prevalence.md` — Stage 2 findings
- [x] `results/baseline_tuning.csv` — Stage 3, 32 rows (23 usable grid points, 9 dropped)
- [x] `results/table4_litnet_tuned.tex` — defaults only (no finals)
- [x] `results/table5_cicids_tuned.tex` — defaults only (no finals)
- [x] `results/tuning_delta_summary.tex` — no tuned rows (no finals)
- [x] `results/appendix_a_replacement.tex` — Appendix A tuning-protocol block
- [x] `findings_tuning.md` — Stage 3 findings, incl. the LITNET split finding
- [x] `findings_burnrate.md` — Stage 4 scoping note (why it did not run)
- [x] `findings_paper_overlap.md` — sibling/CALIBURN overlap report
- [x] `RUN_REPORT.md` — full report: gates, reductions, migration, all incidents

Not produced:

- [ ] `results/burnrate_litnet.csv`, `results/burnrate_litnet_table.tex`,
      `figures/fig7_burnrate_litnet.pdf` — Stage 4 never ran. The harness is
      committed and ready (`scripts/run_burnrate_litnet.py`,
      `scripts/figures/fig7_burnrate_litnet.py`, `scripts/make_burnrate_table.py`).
- [ ] Stage 3 finals (0 of 8) — the remaining work is ~1.5–2 h of compute.

## Verification at close-out

`pytest -q`: **35 passed**. Smoke test: **green**. Branch pushed to origin.

## AWS resources

Instance and volume are gone (verified via API: instance record purged, volume
`InvalidVolume.NotFound`). No snapshots. Remaining free-of-charge artifacts:
key pair `caliburn-s3-key` and security group `sg-07aa8be9303e7cbb4`, kept in
case the finals are retried; delete them if not.

## Paste into the Claude chat for manuscript integration

- `findings_tuning.md` — **read this first**; it contains the LITNET split finding
- `findings_prevalence.md`
- `results/prevalence_sweep_table.tex`
- `results/appendix_a_replacement.tex`
- `RUN_REPORT.md` — the gates, reductions and migration sections
- `findings_paper_overlap.md`

Note that `table4/table5_tuned.tex` and `tuning_delta_summary.tex` are not
worth integrating until the finals are run; they currently carry defaults only.
