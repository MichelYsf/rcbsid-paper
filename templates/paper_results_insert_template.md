# Paper Results Insert Template

Use this after the full run only.

## Experimental environment

All experiments were executed with Python 3.11 using the pinned dependency set in `requirements.txt`. The streaming baselines were verified using `scripts/verify_native_baselines.py`; fallback baselines were disabled for publication runs. The full experiment used chronological 70/15/15 train-validation-test splits and five fixed random seeds: 11, 23, 37, 41, and 53.

## Datasets

The evaluation used three datasets: UNSW-NB15, Engelen-corrected CICIDS2017, and LITNET-2020. Each dataset was processed as a chronological stream. LITNET-2020 schemas were normalized before evaluation.

## Baselines

The online streaming baselines were HS-Trees, KitNET/Kitsune, LODA, xStream, RRCF, and iForestASD. LOF, ECOD, and COPOD were retained only as batch reference baselines and are not treated as fair online comparators.

## Statistical testing

For each dataset, we compared BOCPD-SLO against each baseline using Wilcoxon signed-rank tests over the fixed seed runs. P-values were corrected using Holm-Bonferroni correction.

## Required replacement placeholders

Replace these only with values from `results_full_v1/tables/main_metrics_summary.csv` and `results_full_v1/tables/wilcoxon_tests.csv`.

- BOCPD-SLO AUC-PR on UNSW-NB15: `[VALUE]`
- BOCPD-SLO AUC-PR on Engelen-corrected CICIDS2017: `[VALUE]`
- BOCPD-SLO AUC-PR on LITNET-2020: `[VALUE]`
- Strongest online baseline per dataset: `[VALUE]`
- Detection latency p95 per dataset: `[VALUE]`
- Calibration ECE per dataset: `[VALUE]`
- Wilcoxon/Holm corrected significance claims: `[VALUE]`
