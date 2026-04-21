#!/usr/bin/env bash
set -euo pipefail
bash scripts/verify_environment.sh
mkdir -p results/tables results/figures results/logs
python -m src.experiments.run_streaming_eval --config configs/experiment_full.yaml --output results
printf 'Reproduction completed. Verify all metrics before submission.
' > results/REPRODUCED.txt
