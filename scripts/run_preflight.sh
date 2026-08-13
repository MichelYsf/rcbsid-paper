#!/usr/bin/env bash
set -euo pipefail

python --version
bash scripts/verify_environment.sh
python -m pytest -q
python scripts/verify_native_baselines.py
# Refuses to proceed on an un-interleaved stream or a validation split too
# sparse for AUC-PR selection to mean anything (2026-08-13 incident).
python scripts/check_stream_health.py
