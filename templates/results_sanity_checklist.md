# Results Sanity Checklist

Complete this checklist after the UNSW trial and again after the full run.

## Files exist

- [ ] `tables/main_metrics_raw.csv` exists.
- [ ] `tables/main_metrics_summary.csv` exists.
- [ ] `tables/wilcoxon_tests.csv` exists.
- [ ] `run_summary.json` exists.

## Required methods exist

- [ ] `bocpd_slo`
- [ ] `hst`
- [ ] `kitnet`
- [ ] `loda`
- [ ] `xstream`
- [ ] `rrcf`
- [ ] `iforest_asd`
- [ ] `lof_batch_ref`
- [ ] `ecod_batch_ref`
- [ ] `copod_batch_ref`

## Publication-safety gates

- [ ] No row has `uses_fallback=True`.
- [ ] No row has a non-empty `error` value.
- [ ] No streaming method has constant-score behavior.
- [ ] No required method is missing from a dataset.
- [ ] All seeds are present for every dataset-method pair in the full run.

## Metric sanity

- [ ] AUC-PR is above the base rate for the serious streaming methods.
- [ ] AUC-ROC is not exactly 0.5 for LODA or xStream unless justified by the dataset.
- [ ] BOCPD-SLO has plausible calibration values, not perfect and not nonsensical.
- [ ] Batch references are clearly labeled as batch references.
- [ ] Detection latency is finite where attacks are detected.
- [ ] Throughput values are plausible and not zero.

## Paper-readiness gates

- [ ] The strongest baseline is identified honestly.
- [ ] BOCPD-SLO is not claimed to dominate if it does not dominate.
- [ ] The contribution is framed as SLO-aware thresholding and burn-rate alerting.
- [ ] Limitations mention cases where BOCPD-SLO underperforms.
- [ ] Raw CSVs, config files, commit hash, and environment files are archived.
