#!/usr/bin/env python
"""Stage 3: symmetric baseline tuning on the validation split.

Selection criterion is validation AUC-PR ONLY; test labels are never read
during selection. Grids are fixed by the runbook. A grid point that crashes is
logged with its error and dropped.

Modes:
  --phase grid  --dataset D --method M [--point N] : run grid point(s), write
        one CSV per point under results/tuning_parts/ (parallelizable).
  --phase final --dataset D --method M --params-json J --seeds 11 23 47 :
        rerun the selected configuration on the full stream, full test metrics.
  --select      --dataset D --method M : read grid partials, print the argmax.
  --estimate    : per-method per-flow timing on a prefix, extrapolated grid cost.
  --merge DIR --out CSV : combine partials into results/baseline_tuning.csv.

Compute rule (runbook): if the full-stream grid breaks the 12h ceiling, tune on
the first chronologically contiguous 40 percent of train plus the (unchanged)
validation split via --train-frac 0.4, then rerun only the selected
configuration on the full stream for the final number.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import time
import traceback
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)
KITNET_DIR = ROOT / "external" / "KitNET-py"
if KITNET_DIR.exists() and str(KITNET_DIR) not in sys.path:
    sys.path.insert(0, str(KITNET_DIR))

from sklearn.metrics import average_precision_score  # noqa: E402

from src.experiments.run_streaming_eval import (  # noqa: E402
    _evaluate_row,
    _split_chronological,
    _threshold_from_validation,
)
from src.bocpd.slo import posterior_threshold  # noqa: E402
from src.baselines.registry import make_streaming_baseline, score_streaming_model  # noqa: E402
from src.baselines.batch import run_batch_reference  # noqa: E402
from src.data.loaders import load_dataset_folder, prepare_xy  # noqa: E402

# Runbook grids. Keys are runbook names; VALUES map to wrapper kwargs below.
GRIDS: dict[str, dict[str, list]] = {
    "hst": {"num_trees": [25, 50, 100], "max_depth": [10, 15, 20], "window_size": [100, 250, 500]},
    "loda": {"n_bins": [10, 20, 50], "n_random_cuts": [100, 200, 500]},
    "rrcf": {"num_trees": [40, 100], "tree_size": [256, 512]},
    "iforest_asd": {"n_estimators": [50, 100, 200], "window_size": [1024, 2048, 4096]},
    "kitnet": {"max_size_ae": [5, 10, 20]},
    "lof": {"n_neighbors": [10, 20, 35, 50]},
}
# runbook param name -> wrapper kwarg
PARAM_MAP = {
    "hst": {"num_trees": "n_trees", "max_depth": "height", "window_size": "window_size"},
    "loda": {"n_bins": "n_bins", "n_random_cuts": "n_projections"},
    "rrcf": {"num_trees": "n_trees", "tree_size": "tree_size"},
    "iforest_asd": {"n_estimators": "n_estimators", "window_size": "window_size"},
    "kitnet": {"max_size_ae": "max_ae"},
    "lof": {"n_neighbors": "n_neighbors"},
}
GRID_SEED = 11  # selection runs use one fixed seed; finals use 11/23/47
STREAM_METHODS = {"hst", "loda", "rrcf", "iforest_asd", "kitnet"}

DATASET_CONFIGS = {
    "cicids2017": ROOT / "configs/experiment_cicids_trial.yaml",
    "litnet2020": ROOT / "configs/experiment_litnet_trial.yaml",
}


def grid_points(method: str) -> list[dict]:
    grid = GRIDS[method]
    keys = list(grid)
    return [dict(zip(keys, combo)) for combo in itertools.product(*(grid[k] for k in keys))]


def to_wrapper_params(method: str, point: dict, stream_len: int | None = None) -> dict:
    params = {PARAM_MAP[method][k]: v for k, v in point.items()}
    if method == "kitnet" and stream_len is not None:
        # Runbook: grace periods scaled proportionally to stream length.
        # Published defaults fm_grace=100, ad_grace=200 correspond to the full
        # ~1.5M-flow streams; scale linearly with the actual learn-stream length
        # (the wrapper caps ad_grace at 1000).
        scale = stream_len / 1_500_000
        params["fm_grace"] = max(10, int(round(100 * scale * 10)))
        params["ad_grace"] = max(20, int(round(200 * scale * 10)))
    return params


def load_stream(dataset: str):
    """Load the stream with an .npy cache: parallel grid workers memory-map
    the shared feature matrix instead of each parsing the CSV (six concurrent
    pandas parses OOM-killed workers on the 15 GB EC2 box)."""
    cfg = yaml.safe_load(DATASET_CONFIGS[dataset].read_text())
    ds = cfg["datasets"][0]
    folder = Path(ds["path"])
    cache_x, cache_y = folder / "cache_X.npy", folder / "cache_y.npy"
    sources = list(folder.glob("*.csv"))
    if cache_x.exists() and cache_y.exists() and sources and \
            cache_x.stat().st_mtime > max(f.stat().st_mtime for f in sources):
        return cfg, np.load(cache_x, mmap_mode="r"), np.load(cache_y)
    df = load_dataset_folder(ds["path"], ds["label_column"])
    tcol = ds.get("time_column")
    if tcol and tcol in df.columns:
        df = df.sort_values(tcol, kind="mergesort").reset_index(drop=True)
    X, y, _ = prepare_xy(df, ds["label_column"])
    np.save(cache_x, X)
    np.save(cache_y, y)
    return cfg, X, y


def run_grid_point(dataset: str, method: str, point: dict, X, y, cfg, train_frac: float) -> dict:
    (X_train, y_train), (X_val, y_val), _ = _split_chronological(
        X, y, float(cfg["splits"]["train"]), float(cfg["splits"]["validation"])
    )
    if train_frac < 1.0:
        keep = int(len(X_train) * train_frac)
        X_train, y_train = X_train[:keep], y_train[:keep]
    n_features = X.shape[1]
    row = {
        "dataset": dataset, "method": method, "phase": "grid",
        "params": json.dumps(point, sort_keys=True), "seed": GRID_SEED,
        "train_frac": train_frac, "n_train": len(X_train), "n_val": len(X_val),
    }
    t0 = time.perf_counter()
    try:
        if method in STREAM_METHODS:
            params = to_wrapper_params(method, point, stream_len=len(X_train) + len(X_val))
            model = make_streaming_baseline(method, n_features=n_features, seed=GRID_SEED,
                                            allow_fallback=False, **params)
            for r in X_train:
                model.learn_one(r)
            scores_val = []
            for r in X_val:
                scores_val.append(float(model.score_one(r)))
                model.learn_one(r)
        elif method == "lof":
            X_fit = X_train[y_train == 0] if np.any(y_train == 0) else X_train
            scores_val = run_batch_reference("lof", X_fit, X_val, seed=GRID_SEED,
                                             **to_wrapper_params(method, point))
        else:
            raise KeyError(method)
        scores_val = np.asarray(scores_val, dtype=float)
        row["val_auc_pr"] = float(average_precision_score(y_val, scores_val)) \
            if len(set(y_val.tolist())) > 1 else float("nan")
        row["val_auc_roc"] = float("nan")
        row["error"] = ""
    except Exception as exc:
        row["val_auc_pr"] = float("nan")
        row["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    row["wall_s"] = round(time.perf_counter() - t0, 1)
    return row


def run_final(dataset: str, method: str, point: dict, X, y, cfg, seeds: list[int],
              tuned: bool) -> list[dict]:
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = _split_chronological(
        X, y, float(cfg["splits"]["train"]), float(cfg["splits"]["validation"])
    )
    n_features = X.shape[1]
    pm = cfg["proposed_method"]
    default_threshold = posterior_threshold(
        pm["default_false_positive_cost"], pm["default_false_negative_cost"],
        pm["default_incident_prior"])
    rows = []
    for seed in seeds:
        t0 = time.perf_counter()
        try:
            if method in STREAM_METHODS:
                params = to_wrapper_params(method, point, stream_len=len(X)) if point else {}
                model = make_streaming_baseline(method, n_features=n_features, seed=int(seed),
                                                allow_fallback=False, **params)
                for r in X_train:
                    model.learn_one(r)
                scores_val = []
                for r in X_val:
                    scores_val.append(float(model.score_one(r)))
                    model.learn_one(r)
                threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
                scores_test = np.asarray(score_streaming_model(model, X_test), dtype=float)
            else:  # batch references: lof (tunable), ecod/copod (carried forward)
                X_fit = X_train[y_train == 0] if np.any(y_train == 0) else X_train
                X_eval = np.vstack([X_val, X_test])
                kwargs = to_wrapper_params(method, point) if (point and method == "lof") else {}
                scores_eval = run_batch_reference(method, X_fit, X_eval, seed=int(seed), **kwargs)
                scores_val = scores_eval[: len(X_val)]
                scores_test = scores_eval[len(X_val):]
                threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
            elapsed = time.perf_counter() - t0
            row = _evaluate_row(dataset, method, int(seed), y_test, scores_test,
                                threshold, elapsed, cfg)
            row.update({
                "phase": "final_tuned" if tuned else "final_default",
                "params": json.dumps(point, sort_keys=True) if point else "{}",
                "val_auc_pr": float(average_precision_score(y_val, np.asarray(scores_val, dtype=float)))
                if len(set(y_val.tolist())) > 1 else float("nan"),
                "error": "",
            })
        except Exception as exc:
            row = {"dataset": dataset, "method": method, "seed": int(seed),
                   "phase": "final_tuned" if tuned else "final_default",
                   "params": json.dumps(point, sort_keys=True) if point else "{}",
                   "error": f"{type(exc).__name__}: {exc}"}
            traceback.print_exc()
        rows.append(row)
    return rows


def select_best(parts_dir: Path, dataset: str, method: str) -> tuple[dict, pd.DataFrame]:
    files = sorted(parts_dir.glob(f"grid_{dataset}_{method}_*.csv"))
    if not files:
        raise SystemExit(f"no grid partials for {dataset}/{method} in {parts_dir}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    ok = df[df["val_auc_pr"].notna()].copy()
    if ok.empty:
        raise SystemExit(f"every grid point failed for {dataset}/{method}")
    best = ok.sort_values(["val_auc_pr", "params"], ascending=[False, True]).iloc[0]
    return json.loads(best["params"]), df


def _cap_address_space(gib: float = 3.0) -> None:
    """Fail fast instead of dragging the whole box down.

    HST at 100 trees x depth 20 allocates ~2^21 nodes per tree (multiple GiB
    in one grid point). Without a cap, such a point exhausts RAM, the kernel
    OOM-kills workers mid-job, and the machine thrashes so hard that nothing
    else completes either (observed 2026-08-13: 45 min at 6 workers, zero
    jobs finished). With a per-worker cap the offending point raises
    MemoryError, is logged and dropped per the runbook's crash rule, and the
    remaining grid keeps making progress.
    """
    if os.name == "nt":
        return
    try:
        import resource
        limit = int(gib * (1 << 30))
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        if hard != resource.RLIM_INFINITY:
            limit = min(limit, hard)
        resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
    except Exception:
        pass  # capping is best-effort; never block a run over it


def main() -> None:
    _cap_address_space(float(os.environ.get("CALIBURN_WORKER_MEM_GIB", "3.0")))
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=["grid", "final"])
    p.add_argument("--dataset", choices=list(DATASET_CONFIGS))
    p.add_argument("--method")
    p.add_argument("--point", type=int, help="grid point index (omit = all points sequentially)")
    p.add_argument("--train-frac", type=float, default=1.0)
    p.add_argument("--params-json", help="explicit params for --phase final ('{}' = defaults)")
    p.add_argument("--seeds", nargs="*", type=int, default=[11, 23, 47])
    p.add_argument("--parts", default=str(ROOT / "results/tuning_parts"))
    p.add_argument("--select", action="store_true")
    p.add_argument("--estimate", action="store_true")
    p.add_argument("--prefix", type=int, default=20000)
    p.add_argument("--merge", help="partials dir to merge")
    p.add_argument("--out")
    a = p.parse_args()
    parts_dir = Path(a.parts)
    parts_dir.mkdir(parents=True, exist_ok=True)

    if a.merge:
        files = sorted(Path(a.merge).glob("*.csv"))
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(a.out, index=False)
        print(f"merged {len(files)} partials -> {a.out} ({len(df)} rows)")
        return

    if a.select:
        best, df = select_best(parts_dir, a.dataset, a.method)
        n_fail = int(df["error"].fillna("").astype(bool).sum())
        print(json.dumps({"dataset": a.dataset, "method": a.method, "best": best,
                          "n_points": len(df), "n_failed": n_fail,
                          "best_val_auc_pr": float(df[df['params'] == json.dumps(best, sort_keys=True)]['val_auc_pr'].max())}))
        return

    if a.estimate:
        for dataset in DATASET_CONFIGS:
            try:
                cfg, X, y = load_stream(dataset)
            except Exception as exc:
                print(f"{dataset}: unavailable ({exc})")
                continue
            n = len(y)
            Xp = X[: a.prefix]
            print(f"--- {dataset}: {n:,} flows ---")
            for method in GRIDS:
                if method == "lof":
                    continue  # batch; timed separately below
                try:
                    model = make_streaming_baseline(
                        method, n_features=X.shape[1], seed=GRID_SEED, allow_fallback=False,
                        **to_wrapper_params(method, grid_points(method)[0], stream_len=n))
                    t0 = time.perf_counter()
                    for r in Xp:
                        model.score_one(r)
                        model.learn_one(r)
                    us = (time.perf_counter() - t0) / len(Xp) * 1e6
                    grid_h = us * 1e-6 * n * 0.55 * len(grid_points(method)) / 3600
                    print(f"  {method}: {us:.0f} us/flow -> full-stream grid "
                          f"({len(grid_points(method))} pts, 55% stream) ~{grid_h:.1f} core-h")
                except Exception as exc:
                    print(f"  {method}: estimate failed: {exc}")
        return

    cfg, X, y = load_stream(a.dataset)

    if a.phase == "grid":
        pts = grid_points(a.method)
        indices = [a.point] if a.point is not None else range(len(pts))
        for i in indices:
            row = run_grid_point(a.dataset, a.method, pts[i], X, y, cfg, a.train_frac)
            out = parts_dir / f"grid_{a.dataset}_{a.method}_{i:03d}.csv"
            pd.DataFrame([row]).to_csv(out, index=False)
            print(f"[{a.dataset}/{a.method} {i + 1}/{len(pts)}] {row['params']} "
                  f"val_auc_pr={row.get('val_auc_pr')} wall={row['wall_s']}s"
                  + (f" ERROR={row['error']}" if row.get("error") else ""))
    elif a.phase == "final":
        point = json.loads(a.params_json) if a.params_json else select_best(parts_dir, a.dataset, a.method)[0]
        tuned = bool(point)
        rows = run_final(a.dataset, a.method, point, X, y, cfg, a.seeds, tuned)
        tag = "tuned" if tuned else "default"
        out = parts_dir / f"final_{a.dataset}_{a.method}_{tag}.csv"
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"final {a.dataset}/{a.method} ({tag}) -> {out}")
    else:
        raise SystemExit("choose --phase grid|final, --select, --estimate or --merge")


if __name__ == "__main__":
    main()
