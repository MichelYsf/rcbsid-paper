# Findings: baseline tuning (Stage 3)

## CORRECTED INCIDENT — retraction of an earlier claim about LITNET-2020

An earlier version of this document, of DONE_ALL.md, of RUN_REPORT.md and of
results/tuning_parts/reductions.json asserted that the **paper's** LITNET-2020
evaluation was built on a degenerate split (validation holding 6 attacks, a
0.059% test slice) and that this undermined Table 9's calibration and the CRC
exchangeability assumption. **That claim was wrong and is fully retracted. The
paper's LITNET evaluation is sound.** The defect was in this harness.

What actually happened:

- Both the EC2 bootstrap (`scripts/ec2_bootstrap.sh`) and the local Stage 0
  build ran `scripts/build_litnet_labeled.py` and then went straight to the
  runner, **omitting `scripts/interleave_litnet.py`**. The CICIDS2017 path did
  run its equivalent (`interleave_cicids.py`), which is why only LITNET was
  affected.
- The resulting stream was **three contiguous attack-type blocks** (measured: 2
  adjacent `attack_type` changes across 1,500,000 rows, where round-robin gives
  ~1,499,999). Validation and test were therefore **100% `spam`**, whose native
  attack rate is 0.06% — hence 6 attacks in validation and 132 in test.
- **Every LITNET grid result from this run is an artifact of that broken stream
  and is void.** The partials are quarantined under
  `results/tuning_parts/void_litnet_uninterleaved/` and excluded from
  `baseline_tuning.csv`.
- The **published** LITNET evaluation uses a correctly interleaved stream: an
  in-memory reconstruction of the documented interleave gives train 4.928% /
  validation 5.218% / **test 6.498% (14,621 attacks in 225,000 rows)**. Two
  independent checks agree: the paper's Table 12 ablation row (alert rate 0.057,
  precision 0.976, recall 0.850) implies 6.54% prevalence and predicts FPR
  0.0015 against the 0.001 reported; and LOF's precision 0.0667 at recall 0.9605
  bounds test prevalence at <= 6.95%. A 0.059% slice would require an alert rate
  of 0.051% against the 5.7% reported — wrong by two orders of magnitude.
- **The reallocation of Stage 3 from LITNET-2020 to CICIDS2017 was therefore
  made on a false premise.** The CICIDS2017 tuning below is itself valid and
  its validation split is healthy, but LITNET tuning should not have been
  dropped and remains legitimate unfinished work.

## Coverage and completeness

- Grid points evaluated: 14 usable, 4 crashed and dropped (runbook rule: drop and log).
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 500}` — MemoryError: 
- **No final (full-stream) runs completed.** Selection results below are validation-only; no tuned test numbers exist yet, so no default-versus-tuned verdict can be drawn.

Selection criterion: validation AUC-PR only — the same chronological validation split CALIBURN's calibration layer uses. Test labels were never read during selection. Reductions applied are logged in results/tuning_parts/reductions.json and RUN_REPORT.md.

## litnet2020: not tuned (reduction rung; documented defaults carried)

## cicids2017: validation-stage selections only (no finals completed)

Validation split: 52,085 attacks in 240,000 rows (21.7% prevalence) — selection is statistically meaningful here.

| baseline | selected config (max validation AUC-PR) | val AUC-PR | grid points used |
|---|---|---|---|
| hst | `{"max_depth": 10, "num_trees": 100, "window_size": 500}` | 0.2650 | 4 |
| iforest_asd | `{"n_estimators": 200, "window_size": 4096}` | 0.2149 | 4 |
| kitnet | `{"max_size_ae": 20}` | 0.2082 | 2 |
| loda | `{"n_bins": 10, "n_random_cuts": 100}` | 0.3574 | 2 |
| lof | `{"n_neighbors": 50}` | 0.8490 | 2 |

**No verdict is drawn on whether CALIBURN still leads after tuning**: that comparison requires test-set numbers from the full-stream final runs, which did not complete in the available window. Selection above touched validation labels only.

Grid points that crashed and were dropped (logged): 4.
