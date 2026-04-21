#!/usr/bin/env bash
set -euo pipefail

if [ ! -d data/raw/unsw_nb15 ]; then
  echo "Missing data/raw/unsw_nb15. Download UNSW-NB15 CSVs first."
  exit 1
fi

python -m src.experiments.run_streaming_eval \
  --config configs/experiment_unsw_trial.yaml \
  --output results_unsw_trial

python scripts/guard_results.py --output results_unsw_trial

python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out = Path('results_unsw_trial')
raw = pd.read_csv(out / 'tables/main_metrics_raw.csv')
summary = pd.read_csv(out / 'tables/main_metrics_summary.csv')
print('\nRaw rows:', len(raw))
print('Methods:', sorted(raw['method'].dropna().unique()))
if 'uses_fallback' in raw.columns and raw['uses_fallback'].fillna(False).astype(bool).any():
    raise SystemExit('ERROR: Trial used fallback baselines. Stop.')
if 'error' in raw.columns and raw['error'].notna().any():
    print(raw[raw['error'].notna()][['dataset','method','seed','error']])
    raise SystemExit('ERROR: Trial has error rows. Stop.')
print('\nSummary preview:')
cols = [c for c in ['dataset','method','auc_pr_mean','auc_roc_mean','f1_mean','latency_mean_mean','throughput_eps_mean'] if c in summary.columns]
print(summary[cols].to_string(index=False))
print('\nUNSW trial finished. Review templates/results_sanity_checklist.md before full run.')
PY
