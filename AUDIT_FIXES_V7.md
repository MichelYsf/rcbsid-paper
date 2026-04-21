# AUDIT_FIXES_V7

V7 applies the execution-add-on audit fixes.

## Fixed

1. `scripts/run_preflight.sh` now runs `verify_environment.sh` with `bash`, not `python`.
2. `README_EXECUTION_NOW.md` has the same corrected command.
3. Native KitNET no longer returns constant `0.0` scores. The wrapper now caches the return value of `KitNET.process(x)` in `learn_one()` and returns the cached value in `score_one()`.
4. KitNET native default grace periods were reduced to `fm_grace=100` and `ad_grace=200` so the native verifier can exercise real scoring behavior in a short preflight stream.
5. The experiment runner now records score diagnostics: `score_std`, `score_min`, `score_max`, and `score_finite_frac`.
6. Added `scripts/guard_results.py`, which fails runs with fallback baselines, error rows, missing streaming methods, constant score vectors, non-finite scores, invalid throughput, or near-random/base-rate collapse.
7. `scripts/run_unsw_trial.sh` and `scripts/run_full_guarded.sh` now call `guard_results.py` before printing summaries.

## Still required before publication runs

- Install under Python 3.11.
- Run `bash scripts/setup_kitnet_py.sh`.
- Export `PYTHONPATH="$PWD/external/KitNET-py:$PYTHONPATH"`.
- Run `bash scripts/run_preflight.sh` and proceed only if all six streaming baselines verify as native and non-constant.
