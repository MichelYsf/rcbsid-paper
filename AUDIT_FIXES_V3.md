# V3 fixes after V2 audit

This release addresses the remaining issues identified in the V2 audit.

## Fixed

1. **Dependency conflict**
   - Changed `river==0.24.0` to `river==0.22.0` to preserve compatibility with the Python 3.11 / NumPy 1.26.4 stack targeted by the project.
   - Added `mmh3`, required by the native PySAD xStream path.
   - Added `setuptools`, because some environments require `pkg_resources` for legacy dependencies such as `rrcf`.
   - Added `pytest` so the test suite can be run from a clean environment.

2. **LODA score-before-learn bug**
   - Updated `src/baselines/loda.py` so PySAD LODA returns a neutral warm-up score before `fit_partial()` has initialized its internal projections.
   - This preserves the correct streaming order: score first, then learn.

3. **xStream first-score robustness**
   - Updated the native xStream wrapper so environments where `score_partial()` requires a first `fit_partial()` return a neutral warm-up score instead of crashing.

4. **Baseline smoke test**
   - Increased the synthetic baseline-smoke stream length so HS-Trees has enough observations to warm up beyond its default window.

## Validation performed

The target stack is Python 3.11. The execution environment used for this patch exposed Python 3.13 only, so the pinned Python 3.11 lockfile was not fully installable here because NumPy 1.26.4 does not provide Python 3.13 wheels.

To validate logic anyway, the test suite and smoke pipeline were executed under a Python 3.13 compatibility environment with current compatible wheels. Results:

- `python -m pytest -q` → 6 passed.
- `bash scripts/run_smoke_test.sh` → completed and produced `results_smoke/tables/main_metrics_summary.csv`.

These are smoke validations only. Final paper numbers must still be produced by running the full pipeline on Python 3.11 with UNSW-NB15, Engelen-corrected CICIDS2017, and LITNET-2020.
