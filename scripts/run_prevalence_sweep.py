#!/usr/bin/env python
"""Stage 2: fixed-dataset prevalence sweep on CICIDS2017 (and optionally LITNET).

One invocation runs ONE (level, seed) cell and writes a partial CSV, so cells
can run as parallel OS processes; `--merge` combines partials into the final
deliverable. `--estimate` times every method on a stream prefix and prints an
extrapolated runtime estimate for the whole sweep on this machine.

The cell protocol reuses the existing experiment runner's private helpers so
that the natural-prevalence level (no resampling) reproduces the Stage 1
published pipeline bit-for-bit for deterministic methods (internal control).

Methods per cell (runbook):
- bocpd_slo         : exact Stage 1 configuration (raw scores, threshold =
                      posterior_threshold(C_FP=1, C_FN=10, prior from the trial
                      config) — kept fixed across levels as the control row)
- bocpd_v1_iso_crc  : CALIBURN V1 (isotonic + CRC at alpha=0.01)
- bocpd_v3_iso_elkan: V3 (isotonic + Elkan tau*=0.091)
- bocpd_v4_raw_elkan: V4 (raw + Elkan tau*=0.091)
- loda, hst         : streaming baselines (method seed = resample seed)
- lof, ecod         : deterministic batch references
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from src.experiments.run_streaming_eval import (  # noqa: E402
    _evaluate_row,
    _make_bocpd,
    _score_stream_with_warmup,
    _split_chronological,
    _threshold_from_validation,
)
from src.bocpd.slo import posterior_threshold  # noqa: E402
from src.baselines.registry import make_streaming_baseline, score_streaming_model  # noqa: E402
from src.baselines.batch import run_batch_reference  # noqa: E402
from src.data.loaders import load_dataset_folder, prepare_xy  # noqa: E402
from prevalence_lib import natural_rate, resample_to_prevalence, split_prevalences  # noqa: E402
from caliburn_variants import caliburn_variant_evaluations  # noqa: E402

NATURAL_SENTINEL = "natural"
STREAMING_METHODS = ["loda", "hst"]
BATCH_METHODS = ["lof", "ecod"]
CRC_ALPHA = 0.01
COST_RATIO = 10.0


def load_stream(cfg: dict, dataset_index: int = 0):
    ds = cfg["datasets"][dataset_index]
    df = load_dataset_folder(ds["path"], ds["label_column"])
    tcol = ds.get("time_column")
    if tcol and tcol in df.columns:
        df = df.sort_values(tcol, kind="mergesort").reset_index(drop=True)
    X, y, features = prepare_xy(df, ds["label_column"])
    return ds["name"], X, y


def run_cell(cfg: dict, dataset_name: str, X: np.ndarray, y: np.ndarray,
             level, seed: int, methods=None) -> list[dict]:
    """Run every method for one (level, seed) cell and return result rows."""
    methods = methods or (["bocpd"] + STREAMING_METHODS + BATCH_METHODS)
    nat = natural_rate(y)
    if level == NATURAL_SENTINEL:
        idx = np.arange(len(y))
        info = {
            "target_rate": nat, "seed": seed, "n_redraws": 0, "effective_seed": seed,
            "n_flows": int(len(y)), "achieved_overall": nat,
            **{f"achieved_{k}": v for k, v in split_prevalences(y).items()},
        }
        info = {k if k.startswith("achieved_") or k in ("target_rate", "seed", "n_redraws", "effective_seed", "n_flows") else k: v for k, v in info.items()}
        target_label = nat
    else:
        target = float(level) / 100.0
        idx, info = resample_to_prevalence(y, target, seed)
        info = {**info,
                **{f"achieved_{k}": v for k, v in
                   split_prevalences(y[idx]).items()}}
        target_label = target
    Xr, yr = X[idx], y[idx]

    meta = {
        "level_target_pct": round(float(target_label) * 100.0, 4),
        "is_natural": level == NATURAL_SENTINEL,
        "resample_seed": int(seed),
        "n_redraws": int(info["n_redraws"]),
        "n_flows": int(info["n_flows"]),
        "achieved_train_prev": info["achieved_train"],
        "achieved_val_prev": info["achieved_val"],
        "achieved_test_prev": info["achieved_test"],
    }

    (X_train, y_train), (X_val, y_val), (X_test, y_test) = _split_chronological(
        Xr, yr, float(cfg["splits"]["train"]), float(cfg["splits"]["validation"])
    )
    n_features = Xr.shape[1]
    pm = cfg["proposed_method"]
    default_threshold = posterior_threshold(
        pm["default_false_positive_cost"], pm["default_false_negative_cost"],
        pm["default_incident_prior"],
    )
    rows: list[dict] = []

    if "bocpd" in methods:
        model = _make_bocpd(pm, int(seed))
        scores_val = _score_stream_with_warmup(model, X_train, X_val)
        start = time.perf_counter()
        scores_test = _score_stream_with_warmup(model, np.empty((0, n_features)), X_test)
        elapsed = time.perf_counter() - start
        # Control row: byte-identical to the Stage 1 runner protocol.
        rows.append({**_evaluate_row(dataset_name, "bocpd_slo", int(seed), y_test,
                                     scores_test, default_threshold, elapsed, cfg), **meta})
        # Variant rows: V1 / V3 / V4 layered on the same scored stream.
        ev = caliburn_variant_evaluations(scores_val, y_val, scores_test, y_test,
                                          alpha=CRC_ALPHA, cost_ratio=COST_RATIO)
        for name, row in ev["rows"].items():
            scores = ev["p_test_iso"] if name != "bocpd_v4_raw_elkan" else scores_test
            base = _evaluate_row(dataset_name, name, int(seed), y_test, scores,
                                 row["threshold"] if np.isfinite(row["threshold"]) else np.inf,
                                 elapsed, cfg)
            rows.append({**base, **ev["shared"], **row, "method": name, **meta})

    for method in [m for m in STREAMING_METHODS if m in methods]:
        start = time.perf_counter()
        model = make_streaming_baseline(method, n_features=n_features, seed=int(seed),
                                        allow_fallback=bool(cfg.get("allow_fallback_baselines", False)))
        for r in X_train:
            model.learn_one(r)
        scores_val = []
        for r in X_val:
            scores_val.append(float(model.score_one(r)))
            model.learn_one(r)
        threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
        scores_test = np.asarray(score_streaming_model(model, X_test), dtype=float)
        elapsed = time.perf_counter() - start
        fallback = bool(getattr(model, "uses_fallback", False))
        rows.append({**_evaluate_row(dataset_name, method, int(seed), y_test, scores_test,
                                     threshold, elapsed, cfg, fallback=fallback), **meta})

    if any(m in methods for m in BATCH_METHODS):
        X_batch_train = X_train[y_train == 0] if np.any(y_train == 0) else X_train
        X_eval = np.vstack([X_val, X_test])
        for method in [m for m in BATCH_METHODS if m in methods]:
            start = time.perf_counter()
            scores_eval = run_batch_reference(method, X_batch_train, X_eval, seed=int(seed))
            scores_val = scores_eval[: len(X_val)]
            scores_test = scores_eval[len(X_val):]
            threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
            elapsed = time.perf_counter() - start
            rows.append({**_evaluate_row(dataset_name, f"{method}_batch_ref", int(seed),
                                         y_test, scores_test, threshold, elapsed, cfg), **meta})
    return rows


def estimate(cfg: dict, X: np.ndarray, y: np.ndarray, prefix: int, levels: list, seeds: list) -> None:
    """Time each method on a stream prefix, extrapolate to the full sweep."""
    nat = natural_rate(y)
    n_total = len(y)
    Xp, yp = X[:prefix], y[:prefix]
    per_flow: dict[str, float] = {}

    pm = cfg["proposed_method"]
    t0 = time.perf_counter()
    model = _make_bocpd(pm, 11)
    for r in Xp:
        model.update_score(r)
    per_flow["bocpd"] = (time.perf_counter() - t0) / prefix

    for method in STREAMING_METHODS:
        model = make_streaming_baseline(method, n_features=X.shape[1], seed=11,
                                        allow_fallback=False)
        t0 = time.perf_counter()
        for r in Xp:
            model.score_one(r)
            model.learn_one(r)
        per_flow[method] = (time.perf_counter() - t0) / prefix

    # Batch references scale superlinearly; time fit+score on the prefix and
    # extrapolate linearly as a lower bound (documented as such).
    for method in BATCH_METHODS:
        t0 = time.perf_counter()
        run_batch_reference(method, Xp[yp == 0] if np.any(yp == 0) else Xp, Xp, seed=11)
        per_flow[method] = (time.perf_counter() - t0) / prefix

    total_core_s = 0.0
    print(f"per-flow seconds (prefix n={prefix}): " +
          ", ".join(f"{k}={v * 1e6:.1f}us" for k, v in per_flow.items()))
    for level in levels:
        target = nat if level == NATURAL_SENTINEL else float(level) / 100.0
        attacks = int(np.sum(y)); benigns = n_total - attacks
        if target <= nat:
            n_lvl = benigns + int(round(target * benigns / (1 - target)))
        else:
            n_lvl = attacks + int(round(attacks * (1 - target) / target))
        cell_s = sum(per_flow.values()) * n_lvl
        total_core_s += cell_s * len(seeds)
        print(f"level {level}: ~{n_lvl:,} flows, ~{cell_s / 3600:.2f} core-h per seed")
    print(f"TOTAL sweep: ~{total_core_s / 3600:.1f} core-hours "
          f"({len(levels)}x{len(seeds)} cells); divide by parallel workers for wall-clock")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=str(ROOT / "configs/experiment_cicids_trial.yaml"))
    p.add_argument("--level", help="target prevalence percent, or 'natural'")
    p.add_argument("--seed", type=int)
    p.add_argument("--out", help="output CSV path for this cell (or merged file)")
    p.add_argument("--methods", nargs="*", default=None,
                   help="subset of: bocpd loda hst lof ecod (default all)")
    p.add_argument("--estimate", action="store_true", help="print runtime estimate and exit")
    p.add_argument("--prefix", type=int, default=20000)
    p.add_argument("--levels", nargs="*", default=["5", "10", "natural", "40", "64"])
    p.add_argument("--seeds", nargs="*", type=int, default=[11, 23, 47])
    p.add_argument("--merge", help="directory of partial CSVs to merge into --out")
    a = p.parse_args()

    if a.merge:
        parts = sorted(Path(a.merge).glob("*.csv"))
        if not parts:
            raise SystemExit(f"no partial CSVs found in {a.merge}")
        df = pd.concat([pd.read_csv(f) for f in parts], ignore_index=True)
        df = df.sort_values(["level_target_pct", "resample_seed", "method"]).reset_index(drop=True)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(a.out, index=False)
        print(f"merged {len(parts)} partials -> {a.out} ({len(df)} rows)")
        return

    cfg = yaml.safe_load(Path(a.config).read_text())
    dataset_name, X, y = load_stream(cfg)

    if a.estimate:
        estimate(cfg, X, y, a.prefix, a.levels, a.seeds)
        return

    if a.level is None or a.seed is None or a.out is None:
        raise SystemExit("--level, --seed and --out are required for a cell run")
    level = a.level if a.level == NATURAL_SENTINEL else a.level
    t0 = time.perf_counter()
    rows = run_cell(cfg, dataset_name, X, y, level, a.seed, methods=a.methods)
    wall = time.perf_counter() - t0
    for r in rows:
        r["cell_wall_s"] = round(wall, 1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)
    print(f"cell level={a.level} seed={a.seed}: {len(rows)} rows in {wall / 60:.1f} min -> {a.out}")


if __name__ == "__main__":
    main()
