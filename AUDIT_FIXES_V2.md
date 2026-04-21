# Audit Fixes Applied in v2

This package version responds directly to the independent audit findings against the first `rcbsid_upgrade_package` skeleton.

## Fixed critical issue 1: BOCPD scoring function

The previous `TruncatedGaussianBOCPD.update_score()` returned a minimum-NLL heuristic that was not a BOCPD posterior and failed on a trivial synthetic mean-shift stream.

v2 replaces it with a bounded-memory Gaussian BOCPD-style scorer that combines:

1. posterior mass on short run lengths, which captures changepoint posterior collapse; and
2. a posterior-predictive chi-square tail score from a prequential global Gaussian reference model.

New tests in `tests/test_bocpd_synthetic.py` require:

- AUC-ROC > 0.90 on a large mean-shift stream;
- AUC-ROC > 0.80 on a variance-shift stream;
- near-random behavior on an artificial no-change stream.

## Fixed critical issue 2: missing streaming baseline wrappers

The previous package listed six streaming baselines but only implemented HS-Trees, and KitNET was a stub.

v2 adds concrete wrappers for:

- `hst`
- `kitnet`
- `loda`
- `xstream`
- `rrcf`
- `iforest_asd`

Where optional native libraries are missing, wrappers fall back to deterministic smoke-test implementations and set `uses_fallback=True` in output metrics. Final paper numbers must use native implementations where available and report implementation commit hashes.

## Fixed critical issue 3: experiment runner ignored baselines and seeds

The previous runner only executed BOCPD once per dataset.

v2 rewrites `src/experiments/run_streaming_eval.py` to iterate over:

- datasets;
- fixed random seeds;
- the proposed BOCPD-SLO method;
- all configured streaming baselines;
- all configured batch-reference baselines.

It now writes:

- `results/tables/main_metrics_raw.csv`
- `results/tables/main_metrics_summary.csv`
- `results/tables/wilcoxon_tests.csv`
- `results/run_summary.json`

## Fixed dependency conflict

The previous `requirements.txt` pinned `river==0.24.0` and `scipy==1.13.1`, which conflicts with River's SciPy requirement.

v2 changes SciPy to:

```text
scipy>=1.16,<1.18
```

## Added missing utility scripts

v2 adds:

- `scripts/normalize_litnet.py`
- `scripts/convert_csv_folder_to_parquet.py`
- `scripts/create_synthetic_dataset.py`
- `scripts/run_smoke_test.sh`

## Validation performed

The package was tested with:

```bash
python -m pytest -q
bash scripts/run_smoke_test.sh
```

At the time of packaging, all tests pass and the smoke pipeline produces rows for BOCPD-SLO, all six streaming baselines, and all three batch-reference baselines.

## Still not a source of final paper numbers

This package is now a working research-code baseline, not a completed experimental study. Final submission still requires downloading the three real datasets, running the full pipeline, verifying native baseline implementations, manually inspecting outputs, generating figures, and replacing all TBD result placeholders with real numbers.
