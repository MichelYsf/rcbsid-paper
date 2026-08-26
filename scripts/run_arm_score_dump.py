#!/usr/bin/env python
"""One full prequential pass over a CICIDS arm, dumping per-record scores.

This is the compute that answers three of the fresh review's demands at once,
because they all need the same thing the archived runs never saved: the
detector's score for EVERY record, tagged with that record's position in the
natural stream.

  A1  shared-record ranking  - restrict both arms to the records their held-out
      slices share, and recompute there.
  A2  split sensitivity      - the detector's score for record i depends only on
      records 0..i, never on where the split falls, so ONE pass supports every
      chronological cut point.
  A3  branch-wise discrimination - the tail and auxiliary components are dumped
      alongside the score, taken from the values update_score itself used.

Why a full pass and not a prefix: the detector is prequential, so a record's
score is a function of everything before it. There is no shortcut to the tail
of the stream, and the arms are different orderings of the same records, so
each arm needs its own pass.

Usage: run_arm_score_dump.py --arm natural|synthetic
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_construction_contrast import PROPOSED, interleave_by_day  # noqa: E402
from src.bocpd.truncated_bocpd import (  # noqa: E402
    TruncatedBOCPDConfig, TruncatedGaussianBOCPD,
)
from src.data.loaders import prepare_xy  # noqa: E402

SRC = ROOT / "data/raw/natural/cicids2017_natural.csv"
OUTDIR = ROOT / "results/score_dumps"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["natural", "synthetic"])
    ap.add_argument("--rows", type=int, default=0, help="0 = full stream")
    a = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    df = pd.read_csv(SRC, nrows=(a.rows or None), low_memory=False)
    df["_pos"] = np.arange(len(df))          # position in the natural stream

    if a.arm == "synthetic":
        df = interleave_by_day(df)

    pos = df["_pos"].to_numpy().astype(np.int64)
    X, y, _ = prepare_xy(df.drop(columns=["_pos"]), "label")
    del df

    # Same detector configuration as the contrast harness.
    cfg = TruncatedBOCPDConfig(
        hazard=float(PROPOSED["hazard_grid"][2]),
        max_run_length=int(PROPOSED["run_length_truncation"]),
        incident_prior=float(PROPOSED["default_incident_prior"]),
    )
    model = TruncatedGaussianBOCPD(cfg)

    n = len(X)
    score = np.empty(n, dtype=np.float64)
    tail = np.empty(n, dtype=np.float64)
    aux = np.empty(n, dtype=np.float64)
    for i, row in enumerate(X):
        s, t, u = model.update_score(row, return_components=True)
        score[i] = s
        tail[i] = t
        aux[i] = u

    out = OUTDIR / ("cicids_" + a.arm + "_scores.npz")
    np.savez_compressed(out, pos=pos, y=y.astype(np.int8), score=score,
                        tail=tail, aux=aux,
                        hazard=np.float64(cfg.hazard),
                        max_run_length=np.int64(cfg.max_run_length))
    el = time.time() - t0
    print("arm=%s rows=%d wrote %s in %.1f s (%.3f ms/row)"
          % (a.arm, n, out.name, el, 1000.0 * el / max(n, 1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
