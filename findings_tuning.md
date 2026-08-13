# Findings: baseline tuning (Stage 3)

## Coverage and completeness

- Grid points evaluated: 23 usable, 9 crashed and dropped (runbook rule: drop and log).
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 25, "window_size": 500}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 100}` — MemoryError: 
  - DROPPED `hst` `{"max_depth": 20, "num_trees": 100, "window_size": 500}` — MemoryError: 
  - DROPPED `loda` `{"n_bins": 10, "n_random_cuts": 500}` — MemoryError: Unable to allocate 1.95 MiB for an array with shape (512, 500) and data type 
- **No final (full-stream) runs completed.** Selection results below are validation-only; no tuned test numbers exist yet, so no default-versus-tuned verdict can be drawn.

Selection criterion: validation AUC-PR only — the same chronological validation split CALIBURN's calibration layer uses. Test labels were never read during selection. Reductions applied are logged in results/tuning_parts/reductions.json and RUN_REPORT.md.

## litnet2020: validation-stage selections only (no finals completed) — **SELECTIONS VOID**

> **Do not use these configurations.** litnet2020's validation split holds **6 attacks in 225,000 rows** (0.003% prevalence), because the trial config sets `time_column: null` and the stream stays in file order. Selecting by validation AUC-PR on that many positives is noise, not tuning — which is why the values below sit far below the 5.2% chance line. They are listed only to document what the grid produced. Tuning was reallocated to CICIDS2017.

| baseline | selected config (max validation AUC-PR) | val AUC-PR | grid points used |
|---|---|---|---|
| hst | `{"max_depth": 10, "num_trees": 25, "window_size": 100}` | 0.0004 | 4 |
| loda | `{"n_bins": 10, "n_random_cuts": 100}` | 0.0235 | 2 |
| rrcf | `{"num_trees": 100, "tree_size": 256}` | 0.0000 | 3 |

**No verdict is drawn on whether CALIBURN still leads after tuning**: that comparison requires test-set numbers from the full-stream final runs, which did not complete in the available window. Selection above touched validation labels only.

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

Grid points that crashed and were dropped (logged): 9.
