# V4 validation report

## What was checked

- `python -m pytest -q` was run after the V4 modifications.
- Result: `6 passed`.
- `bash scripts/run_smoke_test.sh` was run before cleaning the release package.
- Result: completed and produced the expected smoke summary tables.
- `python scripts/verify_native_baselines.py` was run in this execution environment.
- Result: it correctly failed because this environment does not have the full Python 3.11 publication dependency stack or native KitNET. This is expected and is exactly the safety behavior V4 adds.

## Why V4 exists

V3 fixed the V2 audit findings, but it still allowed full experiment runs to silently use smoke-test fallback implementations when native baseline dependencies were missing. V4 changes that policy:

- Smoke config: fallbacks allowed.
- Full publication config: fallbacks forbidden.

This prevents reviewer-facing tables from being populated with fallback baseline numbers by accident.

## Publication rule

Before the full real run, install the Python 3.11 requirements, put native KitNET on `PYTHONPATH`, then run:

```bash
python scripts/verify_native_baselines.py
```

Only proceed if all six streaming baselines report native availability.
