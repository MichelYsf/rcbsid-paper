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

- Grid points evaluated: 28 usable, 12 crashed and dropped (runbook rule: drop and log).
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 500}` — MemoryError: 
  - DROPPED `loda` `{"n_bins": 10, "n_random_cuts": 500}` — NOT EVALUATED: n_random_cuts=500 point abandoned at the deadline on 2026-08-13 (~4 h per p
  - DROPPED `loda` `{"n_bins": 50, "n_random_cuts": 500}` — NOT EVALUATED: n_random_cuts=500 point abandoned at the deadline on 2026-08-13 (~4 h per p
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 500}` — MemoryError: 
  - DROPPED `loda` `{"n_bins": 10, "n_random_cuts": 500}` — NOT EVALUATED: n_random_cuts=500 point abandoned at the deadline on 2026-08-13 (~4 h per p
  - DROPPED `loda` `{"n_bins": 50, "n_random_cuts": 500}` — NOT EVALUATED: n_random_cuts=500 point abandoned at the deadline on 2026-08-13 (~4 h per p
- Final runs completed for: copod, ecod, hst, iforest_asd, kitnet, lof.

Selection criterion: validation AUC-PR only — the same chronological validation split CALIBURN's calibration layer uses. Test labels were never read during selection. Reductions applied are logged in results/tuning_parts/reductions.json and RUN_REPORT.md.

## litnet2020

| baseline | default AUC-PR | tuned AUC-PR | delta | selected config |
|---|---|---|---|---|
| hst | 0.261 | 0.518 | +0.257 | `{"max_depth": 10, "num_trees": 25, "window_size": 500}` |
| iforest_asd | 0.130 | 0.144 | +0.014 | `{"n_estimators": 50, "window_size": 4096}` |
| kitnet | 0.086 | 0.066 | -0.020 | `{"max_size_ae": 5}` |
| lof | 0.099 | 0.099 | -0.000 | `{"n_neighbors": 50}` |

CALIBURN (untuned, deterministic) AUC-PR: **0.943**. Best streaming baseline in this comparison: **hst 0.518**. Lead: **+0.425** (1.82x).

**Verdict withheld — the comparison is NOT yet symmetric.** Every tunable method must carry a tuned test number before a symmetric-tuning verdict is earned. Tuned finals exist for hst, iforest_asd, kitnet, lof; **loda still carry DEFAULT configurations** because their final runs did not complete. (rrcf carries its default by DOCUMENTED reduction and is not counted against symmetry.) CALIBURN's apparent lead of +0.425 is therefore a tuned-vs-partially-default comparison and must not be quoted as evidence that CALIBURN survives symmetric tuning.

For the baselines that WERE finalised, tuning helped some baselines and not others: hst 0.261 -> 0.518 (better); iforest_asd 0.130 -> 0.144 (better); kitnet 0.086 -> 0.066 (worse); lof 0.099 -> 0.099 (no change).

## cicids2017

| baseline | default AUC-PR | tuned AUC-PR | delta | selected config |
|---|---|---|---|---|
| hst | 0.433 | 0.444 | +0.010 | `{"max_depth": 10, "num_trees": 100, "window_size": 500}` |
| kitnet | 0.191 | 0.186 | -0.006 | `{"max_size_ae": 20}` |
| lof | 0.863 | 0.851 | -0.012 | `{"n_neighbors": 50}` |

CALIBURN (untuned, deterministic) AUC-PR: **0.545**. Best streaming baseline in this comparison: **hst 0.444**. Lead: **+0.101** (1.23x).

**Verdict withheld — the comparison is NOT yet symmetric.** Every tunable method must carry a tuned test number before a symmetric-tuning verdict is earned. Tuned finals exist for hst, kitnet, lof; **loda, iforest_asd still carry DEFAULT configurations** because their final runs did not complete. (rrcf carries its default by DOCUMENTED reduction and is not counted against symmetry.) CALIBURN's apparent lead of +0.101 is therefore a tuned-vs-partially-default comparison and must not be quoted as evidence that CALIBURN survives symmetric tuning.

For the baselines that WERE finalised, tuning helped some baselines and not others: hst 0.433 -> 0.444 (better); kitnet 0.191 -> 0.186 (worse); lof 0.863 -> 0.851 (worse).

Grid points that crashed and were dropped (logged): 12.
