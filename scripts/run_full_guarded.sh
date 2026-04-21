#!/usr/bin/env bash
set -euo pipefail

for d in data/raw/unsw_nb15 data/raw/cicids2017_engelen data/raw/litnet2020; do
  if [ ! -d "$d" ]; then
    echo "Missing dataset folder: $d"
    exit 1
  fi
done

bash scripts/run_preflight.sh

python -m src.experiments.run_streaming_eval \
  --config configs/experiment_full.yaml \
  --output results_full_v1

python scripts/guard_results.py --output results_full_v1

python - <<'PY'
from pathlib import Path
import pandas as pd
out = Path('results_full_v1')
raw = pd.read_csv(out / 'tables/main_metrics_raw.csv')
summary = pd.read_csv(out / 'tables/main_metrics_summary.csv')
tests = pd.read_csv(out / 'tables/wilcoxon_tests.csv')
print('\nRaw rows:', len(raw))
print('Datasets:', sorted(raw['dataset'].dropna().unique()))
print('Methods:', sorted(raw['method'].dropna().unique()))
if 'uses_fallback' in raw.columns and raw['uses_fallback'].fillna(False).astype(bool).any():
    raise SystemExit('ERROR: Full run used fallback baselines. Results are not publication-safe.')
if 'error' in raw.columns and raw['error'].notna().any():
    print(raw[raw['error'].notna()][['dataset','method','seed','error']])
    raise SystemExit('ERROR: Full run has error rows. Stop.')
print('\nSummary written to:', out / 'tables/main_metrics_summary.csv')
print('Wilcoxon tests written to:', out / 'tables/wilcoxon_tests.csv')
print('\nFull run completed. Do not insert results into the paper until you complete templates/results_sanity_checklist.md.')
PY
