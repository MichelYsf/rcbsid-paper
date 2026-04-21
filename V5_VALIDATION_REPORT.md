# V5 validation report

## Validation performed in this environment

The package was patched from V4 to V5 and validated with the available Python 3.13 runtime.

Executed:

```bash
python -m pytest -q
```

Result:

```text
8 passed
```

Executed:

```bash
bash scripts/run_smoke_test.sh
```

Result: completed successfully and produced synthetic smoke-test summary tables under `results_smoke/` before release cleanup.

Executed:

```bash
python scripts/verify_native_baselines.py
```

Result: intentionally failed in this environment because native publication dependencies such as `river`, `pysad`, `rrcf`, and native KitNET are not installed here. This is expected and confirms that publication mode does not silently fall back.

## Main V5-specific checks

- `pyod==2.0.5` is now pinned to match `pysad==0.3.4`.
- LODA and xStream use `scalar_score()` instead of `float(np.array([score]))`.
- The broad `except Exception: return 0.0` path was removed from native LODA and xStream scoring.
- The native-baseline verifier now exercises each baseline on synthetic data and rejects constant score vectors.
- A unit test covers `scalar_score()` behavior for Python scalars, zero-dimensional arrays, one-element arrays, and multi-value arrays.

## Final publication gate

Before running full experiments, use Python 3.11 and execute:

```bash
pip install -r requirements.txt
python -m pytest -q
python scripts/verify_native_baselines.py
```

Only proceed to full dataset experiments if all six streaming baselines are native and produce non-constant scores.
