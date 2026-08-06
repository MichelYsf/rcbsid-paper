#!/usr/bin/env python
"""Stage 4: real-data burn-rate validation on the LITNET-2020 test stream.

Protocol:
1. Load LITNET-2020 exactly as the experiment runner does (string mergesort on
   the timestamp column), so CALIBURN scores the identical stream.
2. Report the REAL time span of the test slice (proper datetime parse) and
   which alert levels are honestly evaluable (page-fast needs a 60 min span,
   page-slow 360 min, ticket 4320 min).
3. Score CALIBURN V1: BOCPD scores warm-forward, isotonic calibration fit on
   the validation split, CRC threshold at alpha=0.01. Threshold-crossing
   events are p_hat >= tau_hat on the test slice.
4. Bucket crossings into real 1-minute bins and feed each alert level's
   long/short window pair (paper Table 2) through the repo's burn-rate logic.
   A minute is a budget event iff it contains at least one crossing.
5. Report alerts fired per level with timestamps and whether they coincide
   with labeled attack windows (minutes containing >= 1 labeled attack flow).

Note (documented honestly): the runner orders LITNET by *string* timestamp
sort; LITNET timestamps have non-zero-padded day fields, so string order is
not perfectly chronological within a month. Scoring uses the published stream
order; the burn-rate evaluation maps every event to its true parsed timestamp.
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
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.bocpd.slo import BurnRateWindow, MultiWindowBurnRateAlert  # noqa: E402
from src.experiments.run_streaming_eval import (  # noqa: E402
    _make_bocpd,
    _score_stream_with_warmup,
    _split_chronological,
)
from src.data.loaders import load_dataset_folder, prepare_xy  # noqa: E402
from caliburn_variants import crc_threshold, fit_isotonic  # noqa: E402

LEVELS = {  # paper Table 2
    "page_fast": {"long": 60, "short": 5, "beta": 14.4},
    "page_slow": {"long": 360, "short": 30, "beta": 6.0},
    "ticket": {"long": 4320, "short": 360, "beta": 1.0},
}
SLO = 0.999
CRC_ALPHA = 0.01


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs/experiment_litnet_trial.yaml"))
    ap.add_argument("--out", default=str(ROOT / "results/burnrate_litnet.csv"))
    ap.add_argument("--scores-cache", default=str(ROOT / "results/burnrate_litnet_scores.npz"))
    a = ap.parse_args()

    cfg = yaml.safe_load(Path(a.config).read_text())
    ds = cfg["datasets"][0]
    df = load_dataset_folder(ds["path"], ds["label_column"])
    tcol = ds.get("time_column")
    df = df.sort_values(tcol, kind="mergesort").reset_index(drop=True)
    X, y, _ = prepare_xy(df, ds["label_column"])
    n = len(y)
    i_train = int(n * float(cfg["splits"]["train"]))
    i_val = i_train + int(n * float(cfg["splits"]["validation"]))

    ts = pd.to_datetime(df[tcol], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    ts_test = ts.iloc[i_val:].reset_index(drop=True)
    n_bad = int(ts_test.isna().sum())
    t_min, t_max = ts_test.min(), ts_test.max()
    span_min = (t_max - t_min).total_seconds() / 60.0
    print(f"test slice: {n - i_val:,} flows, {n_bad} unparseable timestamps")
    print(f"real span: {t_min} .. {t_max}  = {span_min:,.1f} minutes ({span_min / 1440:.1f} days)")
    evaluable = {k: span_min >= v["long"] for k, v in LEVELS.items()}
    for k, v in LEVELS.items():
        print(f"  {k}: long window {v['long']} min -> {'EVALUABLE' if evaluable[k] else 'NOT EVALUABLE (span too short)'}")

    (X_train, y_train), (X_val, y_val), (X_test, y_test) = _split_chronological(
        X, y, float(cfg["splits"]["train"]), float(cfg["splits"]["validation"]))

    cache = Path(a.scores_cache)
    if cache.exists():
        z = np.load(cache)
        scores_val, scores_test = z["scores_val"], z["scores_test"]
        print(f"loaded cached BOCPD scores from {cache}")
    else:
        model = _make_bocpd(cfg["proposed_method"], 11)  # deterministic
        t0 = time.perf_counter()
        scores_val = _score_stream_with_warmup(model, X_train, X_val)
        scores_test = _score_stream_with_warmup(model, np.empty((0, X.shape[1])), X_test)
        print(f"BOCPD scoring took {(time.perf_counter() - t0) / 60:.1f} min")
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache, scores_val=scores_val, scores_test=scores_test)

    iso = fit_isotonic(scores_val, y_val)
    p_val = iso.predict(scores_val)
    p_test = iso.predict(scores_test)
    tau = crc_threshold(p_val[np.asarray(y_val) == 0], CRC_ALPHA)
    print(f"CRC tau_hat (alpha={CRC_ALPHA}) = {tau}")
    if not np.isfinite(tau):
        print("CRC infeasible on isotonic scores -> zero crossing events by construction")
        crossing = np.zeros(len(p_test), dtype=int)
    else:
        crossing = (p_test >= tau).astype(int)
    print(f"threshold crossings on test: {int(crossing.sum()):,} of {len(crossing):,} "
          f"({crossing.mean() * 100:.2f}%)")

    # Real-time minute bucketing.
    valid = ts_test.notna().to_numpy()
    minutes = ts_test[valid].dt.floor("min")
    minute_index = pd.date_range(t_min.floor("min"), t_max.floor("min"), freq="min")
    cross_by_min = pd.Series(crossing[valid]).groupby(minutes.values).max()
    attack_by_min = pd.Series(np.asarray(y_test)[valid]).groupby(minutes.values).max()
    budget = cross_by_min.reindex(minute_index, fill_value=0).to_numpy()
    attackmin = attack_by_min.reindex(minute_index, fill_value=0).to_numpy()
    print(f"minutes with >=1 crossing: {int(budget.sum()):,} of {len(budget):,}; "
          f"minutes with >=1 labeled attack flow: {int(attackmin.sum()):,}")

    rows = []
    for level, v in LEVELS.items():
        if not evaluable[level]:
            rows.append({"level": level, "evaluable": False, "long_min": v["long"],
                         "short_min": v["short"], "beta": v["beta"], "span_min": round(span_min, 1),
                         "n_alerts": 0, "alert_timestamps": "", "n_coinciding": 0})
            continue
        alert = MultiWindowBurnRateAlert(
            slo=SLO, rules=[BurnRateWindow(long_window=v["long"], short_window=v["short"],
                                           threshold=v["beta"])])
        fired = []
        for i, b in enumerate(budget):
            if alert.update(float(b)):
                fired.append(i)
        coinciding = [i for i in fired if attackmin[max(0, i - v["long"] + 1): i + 1].any()]
        # Compress runs of consecutive alert-minutes into episodes for reporting.
        episodes = []
        for i in fired:
            if episodes and i == episodes[-1][1] + 1:
                episodes[-1] = (episodes[-1][0], i)
            else:
                episodes.append((i, i))
        ep_str = "; ".join(
            f"{minute_index[s].isoformat()}..{minute_index[e].isoformat()}" for s, e in episodes)
        rows.append({"level": level, "evaluable": True, "long_min": v["long"],
                     "short_min": v["short"], "beta": v["beta"], "span_min": round(span_min, 1),
                     "n_alert_minutes": len(fired), "n_episodes": len(episodes),
                     "n_coinciding_minutes": len(coinciding),
                     "alert_episodes": ep_str})
        print(f"{level}: {len(fired)} alert-minutes in {len(episodes)} episodes, "
              f"{len(coinciding)} coincide with an attack window")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    # Per-minute trace for the figure.
    trace = pd.DataFrame({"minute": minute_index, "crossing": budget, "attack": attackmin})
    trace.to_csv(out.with_name("burnrate_litnet_trace.csv"), index=False)
    print(f"wrote {out} and per-minute trace")


if __name__ == "__main__":
    main()
