#!/usr/bin/env bash
set -euo pipefail

python --version
bash scripts/verify_environment.sh
python -m pytest -q
python scripts/verify_native_baselines.py
