# V6 audit fixes

V6 addresses the V5 audit finding that `pysad==0.3.4`'s LODA implementation can return an effectively constant score vector even when the wrapper is converting scores correctly.

## Changes

1. **Replaced PySAD LODA with native project implementation**
   - `src/baselines/loda.py` now implements LODA directly using random one-dimensional projections and sliding-window histogram-density scoring.
   - The implementation has `uses_fallback = False` and is safe for publication runs.
   - It preserves the score-before-learn streaming protocol.

2. **Kept V5 scalar-score hardening for xStream**
   - PySAD xStream still uses `scalar_score()` to safely convert one-element NumPy outputs.

3. **Publication verifier now catches constant-score failures**
   - `scripts/verify_native_baselines.py` still exercises each baseline on synthetic data and fails if a native scorer returns a constant vector.
   - This is the guard that exposed the upstream PySAD LODA issue.

## Validation commands

The package should be validated with:

```bash
python -m pytest -q
bash scripts/run_smoke_test.sh
python scripts/verify_native_baselines.py
```

The verifier may still fail until native KitNET is installed and available on `PYTHONPATH`; that is expected for environments without `ymirsky/KitNET-py`.
