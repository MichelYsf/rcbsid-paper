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
- LITNET-2020 grid points: 14 attempted, **VOID** (broken un-interleaved stream built by this harness — see corrected incident below)
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

## CORRECTED INCIDENT — the LITNET-2020 claim is retracted

An earlier version of this file asserted that the **paper's** LITNET-2020
evaluation used a 0.059% test slice (~133 attacks), that Table 9's calibration
was fit on 6 positives, and that the CRC exchangeability assumption was
violated. **That claim was wrong and is fully retracted. The paper's LITNET
evaluation is sound.** The defect was in this harness.

- **Root cause:** `scripts/ec2_bootstrap.sh` and the by-hand local Stage 0
  build ran `build_litnet_labeled.py` but **omitted
  `scripts/interleave_litnet.py`**. The CICIDS2017 path did run its equivalent,
  so only LITNET was affected.
- **Effect:** the stream was three contiguous attack-type blocks (2 adjacent
  `attack_type` changes across 1,500,000 rows; round-robin gives ~1,499,999),
  so validation and test were **100% `spam`** (native rate 0.06%) — 6 and 132
  attacks.
- **All 14 LITNET grid partials from this run are void** — artifacts of the
  broken stream. They are quarantined under
  `results/tuning_parts/void_litnet_uninterleaved/`, each row marked
  `VOID=True` with a reason, and excluded from `baseline_tuning.csv`.
- **The published evaluation uses a ~6.5% test slice: 14,621 attacks in
  225,000 rows.** In-memory reconstruction of the documented interleave gives
  train 4.928% / val 5.218% / test 6.498%. Independently confirmed by the
  Table 12 ablation row (alert 0.057, precision 0.976, recall 0.850 ⇒ 6.54%,
  predicting FPR 0.0015 vs the 0.001 reported) and by LOF's precision 0.0667
  at recall 0.9605 (prevalence ≤ 6.95%). A 0.059% slice would require a 0.051%
  alert rate against the 5.7% reported — wrong by two orders of magnitude.
- **The reallocation of Stage 3 to CICIDS2017 was made on a false premise.**
  The CICIDS2017 tuning is itself valid (validation: 52,085 attacks in 240,000
  rows), but LITNET tuning should not have been dropped and remains legitimate
  unfinished work.
- **Nothing in the manuscript needs changing on account of this run.**

Root-cause fixes shipped: interleave added to `ec2_bootstrap.sh`; new
`scripts/build_datasets_local.sh` (canonical local build); new
`scripts/check_stream_health.py` gate refusing <1,000 attack-type changes or
<1% validation prevalence, wired into bootstrap and preflight; and
`tests/test_stream_health.py` (5 regression tests).

## Deliverables

Produced:

- [x] `results/prevalence_sweep_cicids.csv` — Stage 2, 114 rows, internal control bit-exact vs Stage 1
- [x] `results/prevalence_sweep_table.tex` — Stage 2 LaTeX table (mean ± std over 3 resample seeds)
- [x] `figures/fig6_prevalence_sweep.pdf` — Stage 2 figure
- [x] `findings_prevalence.md` — Stage 2 findings
- [x] `results/baseline_tuning.csv` — Stage 3, 18 rows, CICIDS2017 only (void LITNET partials excluded)
- [x] `results/table4_litnet_tuned.tex` — defaults only (no finals)
- [x] `results/table5_cicids_tuned.tex` — defaults only (no finals)
- [x] `results/tuning_delta_summary.tex` — no tuned rows (no finals)
- [x] `results/appendix_a_replacement.tex` — Appendix A tuning-protocol block
- [x] `findings_tuning.md` — Stage 3 findings, incl. the corrected-incident retraction
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

- `findings_tuning.md` — **read this first**; it opens with the corrected-incident retraction
- `findings_prevalence.md`
- `results/prevalence_sweep_table.tex`
- `results/appendix_a_replacement.tex`
- `RUN_REPORT.md` — the gates, reductions and migration sections
- `findings_paper_overlap.md`

Note that `table4/table5_tuned.tex` and `tuning_delta_summary.tex` are not
worth integrating until the finals are run; they currently carry defaults only.
