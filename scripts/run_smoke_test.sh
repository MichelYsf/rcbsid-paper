#!/usr/bin/env bash
set -euo pipefail
${PY:-python3} scripts/create_synthetic_dataset.py
${PY:-python3} -m src.experiments.run_streaming_eval --config configs/smoke_synthetic.yaml --output results_smoke
cat results_smoke/tables/main_metrics_summary.csv
