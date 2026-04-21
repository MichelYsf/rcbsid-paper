# V5 fixes

V5 addresses the audit finding that V4's native LODA and xStream wrappers silently returned constant zero scores.

## Changes

1. `requirements.txt`
   - Changed `pyod==2.0.3` to `pyod==2.0.5`, matching `pysad==0.3.4` metadata.

2. `src/baselines/score_utils.py`
   - Added `scalar_score(value)` to safely convert Python scalars, 0-D arrays, and one-element arrays to a Python float.
   - This avoids the modern NumPy failure mode where `float(np.array([x]))` raises a `TypeError`.
   - The helper intentionally raises on multi-valued or empty outputs so real wrapper bugs are not hidden.

3. `src/baselines/loda.py`
   - Replaced `float(self.model.score_partial(x))` with `scalar_score(self.model.score_partial(x))`.
   - Removed the broad `except Exception` that previously swallowed runtime conversion failures and returned 0 forever.
   - Kept only the true warm-up `AttributeError` path.

4. `src/baselines/xstream.py`
   - Same scalar conversion fix as LODA.
   - Same removal of the broad exception swallow.

5. `scripts/verify_native_baselines.py`
   - Hardened the verifier so it no longer checks imports only.
   - It now constructs each baseline with `allow_fallback=False`, runs score-then-learn over a small synthetic stream, and fails if the score vector is non-finite or constant.
   - This is the guard that prevents publication tables from being generated with silent-zero native baselines.

## Validation expectation

In a Python 3.11 environment with native dependencies installed, run:

```bash
pip install -r requirements.txt
python -m pytest -q
bash scripts/run_smoke_test.sh
python scripts/verify_native_baselines.py
```

The native verifier is expected to fail only if a publication dependency is missing, such as native KitNET not being on `PYTHONPATH`. It should not pass a baseline that returns a constant score vector.
