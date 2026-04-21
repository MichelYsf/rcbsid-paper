# V4 fixes

V4 is a hardening release after the V3 audit.

## Changes

1. Full experiments now set `allow_fallback_baselines: false`. Reviewer-facing results will fail loudly if a publication streaming baseline cannot run natively.
2. Smoke tests keep `allow_fallback_baselines: true` so the repo can still be tested on minimal systems.
3. Added `scripts/verify_native_baselines.py` to check HS-Trees, KitNET, LODA, xStream, RRCF, and iForestASD before the full run.
4. Cleaned the release package by removing `__pycache__`, `.pytest_cache`, embedded smoke data, and embedded smoke results.
5. `run_summary.json` now includes config metadata, baseline lists, fallback mode, dataset names, and row count.

## Important rule

Fallback baseline numbers are acceptable only for CI/smoke testing. They must never be copied into the paper tables.
