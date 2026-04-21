#!/usr/bin/env python3
"""Guard result folders against silent baseline failures.

This script is intentionally stricter than a normal results summarizer. It is
meant to run immediately after trial/full experiments and fail fast if the
output contains any reviewer-poisoning condition: fallback baselines, error
rows, missing streaming methods, constant score vectors, non-finite scores, or
near-random AUC collapse for a streaming method.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

STREAMING_METHODS = {
    "bocpd_slo",
    "hst",
    "kitnet",
    "loda",
    "xstream",
    "rrcf",
    "iforest_asd",
}


def _bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.fillna(False).astype(str).str.lower().isin({"true", "1", "yes"})


def guard(output: Path, require_all_methods: bool = True) -> None:
    raw_path = output / "tables" / "main_metrics_raw.csv"
    summary_path = output / "tables" / "main_metrics_summary.csv"
    if not raw_path.exists():
        raise SystemExit(f"ERROR: missing raw metrics file: {raw_path}")
    if not summary_path.exists():
        raise SystemExit(f"ERROR: missing summary metrics file: {summary_path}")

    raw = pd.read_csv(raw_path)
    summary = pd.read_csv(summary_path)
    errors = []

    if "uses_fallback" in raw.columns:
        fb = raw[_bool_series(raw["uses_fallback"])]
        if len(fb):
            errors.append("Fallback baselines were used:\n" + fb[["dataset", "method", "seed", "uses_fallback"]].to_string(index=False))

    if "error" in raw.columns:
        err = raw[raw["error"].notna() & (raw["error"].astype(str).str.len() > 0)]
        if len(err):
            cols = [c for c in ["dataset", "method", "seed", "error"] if c in err.columns]
            errors.append("Experiment rows contain errors:\n" + err[cols].to_string(index=False))

    if require_all_methods and {"dataset", "method"}.issubset(raw.columns):
        for dataset, g in raw.groupby("dataset"):
            if str(dataset).upper() == "SKIPPED":
                continue
            present = set(g["method"].dropna().astype(str))
            missing = sorted(STREAMING_METHODS - present)
            if missing:
                errors.append(f"Dataset {dataset!r} is missing streaming methods: {missing}")

    # These fields are produced by the v7 runner. If absent, fail because the
    # package cannot detect silent-zero scorers in reviewer-facing output.
    required_diag = {"score_std", "score_finite_frac"}
    missing_diag = sorted(required_diag - set(raw.columns))
    if missing_diag:
        errors.append(f"Missing score diagnostic columns in raw output: {missing_diag}. Re-run with the v7 runner.")
    else:
        streaming_raw = raw[raw["method"].isin(STREAMING_METHODS)].copy()
        bad_finite = streaming_raw[pd.to_numeric(streaming_raw["score_finite_frac"], errors="coerce") < 0.999]
        if len(bad_finite):
            errors.append("Streaming method produced non-finite scores:\n" + bad_finite[["dataset", "method", "seed", "score_finite_frac"]].to_string(index=False))
        constant = streaming_raw[pd.to_numeric(streaming_raw["score_std"], errors="coerce") <= 1e-12]
        if len(constant):
            errors.append("Streaming method produced a constant score vector:\n" + constant[["dataset", "method", "seed", "score_std", "auc_pr", "auc_roc"]].to_string(index=False))

    if {"method", "auc_roc_mean", "auc_pr_mean"}.issubset(summary.columns):
        streaming_summary = summary[summary["method"].isin(STREAMING_METHODS)].copy()
        roc = pd.to_numeric(streaming_summary["auc_roc_mean"], errors="coerce")
        pr = pd.to_numeric(streaming_summary["auc_pr_mean"], errors="coerce")
        suspicious = streaming_summary[(roc.between(0.49, 0.51)) & (pr < 0.50)]
        if len(suspicious):
            errors.append("Streaming method collapsed to near-random/base-rate summary performance:\n" + suspicious[["dataset", "method", "auc_pr_mean", "auc_roc_mean"]].to_string(index=False))

    if {"throughput_eps"}.issubset(raw.columns):
        thr = pd.to_numeric(raw["throughput_eps"], errors="coerce")
        bad_thr = raw[raw["method"].isin(STREAMING_METHODS) & (~np.isfinite(thr) | (thr <= 0))]
        if len(bad_thr):
            errors.append("Streaming method has invalid throughput:\n" + bad_thr[["dataset", "method", "seed", "throughput_eps"]].to_string(index=False))

    if errors:
        print("\n\n".join(errors), file=sys.stderr)
        raise SystemExit("ERROR: Result guard failed. Do not use these numbers in the paper.")
    print(f"OK: result guard passed for {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-missing-methods", action="store_true")
    args = parser.parse_args()
    guard(args.output, require_all_methods=not args.allow_missing_methods)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
