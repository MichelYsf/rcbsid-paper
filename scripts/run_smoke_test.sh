#!/usr/bin/env bash
set -euo pipefail
python scripts/create_synthetic_dataset.py
python -m src.experiments.run_streaming_eval --config configs/smoke_synthetic.yaml --output results_smoke
cat results_smoke/tables/main_metrics_summary.csv
