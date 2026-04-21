# RCBSID Paper Reproducibility Package v5

GitHub-ready package for the revised paper:

**SLO-Aware Streaming Intrusion Detection: Risk-Calibrated Bayesian Changepoint Alerting with Burn-Rate Budgets**

## Core fixes implemented

1. Main comparison now uses online streaming baselines: Kitsune/KitNET, HS-Trees, LODA, xStream, RRCF, and streaming Isolation Forest.
2. LOF, ECOD, and COPOD are kept only as batch-reference rows.
3. A third dataset, LITNET-2020, is added.
4. CICIDS2017 is specified as the Engelen-corrected version.
5. Chronological splits only, with fixed seeds.
6. Wilcoxon signed-rank tests and Holm-Bonferroni correction are specified.
7. Detection latency, calibration, false-alarm rate, and throughput are added.
8. The unsupported O(1) complexity claim is removed.
9. The corrected complexity is O(kd) per event with run-length truncation k and feature dimension d.
10. The contribution is reframed as SLO-aware IDS thresholding and burn-rate alerting.


## Audit fixes

This package addresses the blocking issues identified across the audit reports:

- fixed the BOCPD scoring function and added synthetic sanity tests;
- added concrete wrappers for all six streaming baselines;
- rewrote the experiment runner so it actually iterates over datasets, seeds, streaming baselines, and batch references;
- fixed the River/SciPy and PySAD/PyOD dependency conflicts;
- added LITNET normalization, CSV-to-Parquet conversion, and smoke-test scripts;
- hardened native-baseline verification so publication runs cannot silently use fallback or constant-zero baselines;
- replaced upstream-broken PySAD LODA with a dependency-free native LODA implementation; xStream still uses `scalar_score` for PySAD output conversion.

Run local validation with:

```bash
python -m pytest -q
bash scripts/run_smoke_test.sh
```

Final publication numbers must still be generated from the real datasets, not from the synthetic smoke test.

## One-command reproduction

After downloading datasets into `data/raw`, run:

```bash
bash scripts/reproduce_all.sh
```

## Dataset folders

```text
data/raw/unsw_nb15/
data/raw/cicids2017_engelen/
data/raw/litnet2020/
```

Do not commit raw datasets. Use DVC for checksums and Zenodo for final archived artifacts.

## Zenodo release

After final results are produced, create a GitHub release and archive it on Zenodo. Replace `10.5281/zenodo.XXXXXXX` in `CITATION.cff`, the paper, and README with the issued DOI.


## Publication baseline safety

`configs/experiment_full.yaml` sets `allow_fallback_baselines: false`. This is intentional: full paper experiments must fail if HS-Trees, KitNET, LODA, xStream, RRCF, or iForestASD cannot run natively. Smoke tests may use fallbacks, but reviewer-facing tables must not.

Before launching the full run, execute:

```bash
python scripts/verify_native_baselines.py
```

If this fails, install the missing dependency or native implementation first. In particular, native KitNET requires the `ymirsky/KitNET-py` implementation, or a compatible `KitNET` module, on `PYTHONPATH`.
