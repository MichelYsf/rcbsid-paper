# RCBSID Execution Add-On

This add-on is meant to be copied into the root of the `rcbsid_v6` repository. It does **not** change the core algorithm. It adds guarded execution scripts, a single-dataset trial config, and sanity-check templates so the next phase can move from code validation to real experimental results.

## Current status

The code infrastructure phase is complete enough to move forward. The latest audit verified that the V6 package has no critical bugs in the code controlled by the project. BOCPD, HS-Trees, LODA, xStream, RRCF, iForestASD, the experiment runner, statistical evaluation, and fallback guards are structurally ready. The only remaining blocker before real publication runs is native KitNET availability.

## Copy this add-on into the repository

From the folder containing this add-on and the extracted `rcbsid_v6` folder:

```bash
cp -r configs/* rcbsid_v6/configs/
cp -r scripts/* rcbsid_v6/scripts/
cp -r templates/* rcbsid_v6/templates/ 2>/dev/null || mkdir -p rcbsid_v6/templates && cp -r templates/* rcbsid_v6/templates/
cp README_EXECUTION_NOW.md rcbsid_v6/
chmod +x rcbsid_v6/scripts/*.sh
```

Then work from the repository root:

```bash
cd rcbsid_v6
```

## Environment setup

Use Python 3.11. Do not use Python 3.13 for the real run, because the pinned stack is designed for Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
bash scripts/verify_environment.sh
python -m pytest -q
```

Expected result:

```text
8 passed
```

## Native KitNET setup

The publication config does not allow fallback baselines. This is correct. You must install native KitNET before running the real experiment.

```bash
bash scripts/setup_kitnet_py.sh
source .venv/bin/activate
export PYTHONPATH="$PWD/external/KitNET-py:$PYTHONPATH"
python scripts/verify_native_baselines.py
```

Expected result: all six streaming baselines report native scoring with non-constant score vectors.

If KitNET fails because of deprecated NumPy aliases, the setup script attempts the common patches automatically.

## UNSW-NB15 trial run

Before running all datasets, run the single-dataset single-seed trial:

```bash
bash scripts/run_preflight.sh
bash scripts/run_unsw_trial.sh
```

Expected outputs:

```text
results_unsw_trial/tables/main_metrics_raw.csv
results_unsw_trial/tables/main_metrics_summary.csv
results_unsw_trial/tables/wilcoxon_tests.csv
results_unsw_trial/run_summary.json
```

Do not proceed to the full run until the UNSW trial passes the sanity checks in `templates/results_sanity_checklist.md`.

## Full experiment run

After the trial is valid and all three datasets are downloaded:

```bash
bash scripts/run_full_guarded.sh
```

Expected outputs:

```text
results_full_v1/tables/main_metrics_raw.csv
results_full_v1/tables/main_metrics_summary.csv
results_full_v1/tables/wilcoxon_tests.csv
results_full_v1/run_summary.json
```

## Dataset folders expected by the configs

```text
data/raw/unsw_nb15/
data/raw/cicids2017_engelen/
data/raw/litnet2020/
```

For LITNET-2020, run the normalizer first if the original files have inconsistent schemas:

```bash
python scripts/normalize_litnet.py --input data/raw/litnet2020_original --output data/raw/litnet2020
```

## Hard stop conditions

Stop immediately if any of the following occurs:

- `verify_native_baselines.py` fails.
- Any publication run reports `uses_fallback=True`.
- Any streaming baseline produces constant scores.
- LODA or xStream lands at exactly base-rate AUC-PR and AUC-ROC 0.5 on real data.
- The raw results contain error rows for required methods.
- The batch reference rows look better than every streaming method and are not clearly labeled as batch references.

## What goes into the paper after the full run

Use the real outputs only. Do not manually invent, smooth, or approximate values.

- Table 1: AUC-PR, AUC-ROC, F1, precision, recall.
- Table 2: latency mean, p50, p95, p99, throughput.
- Table 3: Brier score, ECE, burn-rate alerts.
- Statistical paragraph: Wilcoxon signed-rank p-values with Holm-Bonferroni correction.
- Reproducibility paragraph: GitHub URL, commit SHA, Zenodo DOI, Docker command, dataset sources.
