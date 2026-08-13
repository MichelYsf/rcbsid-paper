#!/usr/bin/env python
"""Stream-health gate: refuse to run experiments on an unshuffled stream.

Exists because both the EC2 bootstrap and the local Stage 0 build once ran
build_litnet_labeled.py without scripts/interleave_litnet.py. The stream was
left as three contiguous attack-type blocks, so the chronological 70/15/15
split put pure `spam` in validation and test (6 and 132 attacks). Every
LITNET number produced from it was garbage, and it took a full cloud run to
notice. This gate makes that failure loud and immediate instead.

Checks, per dataset that has an attack_type column:
  1. adjacent attack-type changes >= MIN_TYPE_CHANGES (1000)
     — a round-robin interleaved stream has ~n-1; a blocked one has ~k-1.
  2. validation-split prevalence >= MIN_VAL_PREVALENCE (1.0 percent)
     — the split the tuning layer selects on must contain enough positives
       for selection to mean anything.

Exit 0 = healthy. Exit 1 = refuse to proceed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MIN_TYPE_CHANGES = 1000
MIN_VAL_PREVALENCE = 0.01  # 1 percent
TRAIN, VAL = 0.70, 0.15

STREAMS = {
    "litnet2020": ROOT / "data/raw/litnet2020/litnet2020_labeled.csv",
    "cicids2017": ROOT / "data/raw/cicids2017/cicids2017_labeled.csv",
}


def split_prevalences(y) -> dict:
    n = len(y)
    i = int(n * TRAIN)
    j = i + int(n * VAL)
    return {"train": float(y[:i].mean()), "val": float(y[i:j].mean()),
            "test": float(y[j:].mean()), "n": n, "attacks": int(y.sum())}


def check(name: str, path: Path) -> list[str]:
    if not path.exists():
        print(f"[{name}] not present, skipping")
        return []
    cols = pd.read_csv(path, nrows=0).columns.tolist()
    usecols = [c for c in ("label", "attack_type") if c in cols]
    if "label" not in usecols:
        return [f"[{name}] no 'label' column in {path}"]
    d = pd.read_csv(path, usecols=usecols, low_memory=False)
    y = d["label"].to_numpy()
    p = split_prevalences(y)
    problems: list[str] = []

    if "attack_type" in d.columns:
        at = d["attack_type"].to_numpy()
        changes = int((at[1:] != at[:-1]).sum())
        n_types = d["attack_type"].nunique()
        status = "OK" if changes >= MIN_TYPE_CHANGES else "FAIL"
        print(f"[{name}] attack-type changes: {changes:,} across {p['n']:,} rows "
              f"({n_types} types) [{status}, need >= {MIN_TYPE_CHANGES:,}]")
        if changes < MIN_TYPE_CHANGES:
            problems.append(
                f"[{name}] stream is NOT interleaved: only {changes:,} adjacent "
                f"attack-type changes (blocked layout). Run the interleave step "
                f"(scripts/interleave_{name.replace('2020','').replace('2017','')}.py) "
                f"before any experiment.")

    status = "OK" if p["val"] >= MIN_VAL_PREVALENCE else "FAIL"
    print(f"[{name}] prevalence train={p['train']*100:.3f}% val={p['val']*100:.3f}% "
          f"test={p['test']*100:.3f}% [{status}, val needs >= {MIN_VAL_PREVALENCE*100:.1f}%]")
    if p["val"] < MIN_VAL_PREVALENCE:
        problems.append(
            f"[{name}] validation prevalence {p['val']*100:.3f}% is below "
            f"{MIN_VAL_PREVALENCE*100:.1f}%: validation-AUC-PR selection would be "
            f"noise. Refusing to proceed.")
    return problems


def main() -> int:
    problems: list[str] = []
    for name, path in STREAMS.items():
        problems += check(name, path)
    if problems:
        print("\nSTREAM HEALTH GATE FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nSTREAM HEALTH GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
