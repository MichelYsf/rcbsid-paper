#!/usr/bin/env python
"""Stage 1 - natural-order evaluation streams, with hashes and gates.

Replaces the label-aware round-robin composites and the seeded UNSW
permutation as PRIMARY evaluation streams.

LITNET-2020: the three captures are temporally DISJOINT (udp_flood 2019-03-06
~4 min; spam 2019-12-09..2020-01-06; blaster_worm 2020-01-25 ~1.6 min), so no
coherent global chronology exists. Per the rebuild brief, we therefore build
PER-ATTACK-TYPE streams evaluated separately rather than manufacturing a
composite. This is a documented construction choice, not a workaround.

CICIDS2017: a single capture week, so a global timestamp sort IS coherent.

Emits per-stream: SHA-256, row count, per-split prevalence, attack run-length
distribution (median/p90/max), and a monotonic-timestamp gate that fails the
build on violation. Every number is emitted as a provenance macro.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from provenance import provenance_run, sha256_file          # noqa: E402

OUT = ROOT / "data/raw/natural"
OUT.mkdir(parents=True, exist_ok=True)
TRAIN, VAL = 0.70, 0.15


def run_lengths(y: np.ndarray) -> dict:
    runs, c = [], 0
    for v in y:
        if v == 1:
            c += 1
        elif c:
            runs.append(c); c = 0
    if c:
        runs.append(c)
    if not runs:
        return {"n_runs": 0, "median": 0.0, "p90": 0.0, "max": 0}
    a = np.array(runs)
    return {"n_runs": int(len(a)), "median": float(np.median(a)),
            "p90": float(np.percentile(a, 90)), "max": int(a.max())}


def splits(y: np.ndarray) -> dict:
    n = len(y); i = int(n * TRAIN); j = i + int(n * VAL)
    return {"train": float(y[:i].mean()), "val": float(y[i:j].mean()),
            "test": float(y[j:].mean()),
            "test_attacks": int(y[j:].sum()), "n": int(n)}


def emit(run, tag: str, df: pd.DataFrame, tcol: str, path: Path) -> None:
    ts = pd.to_datetime(df[tcol], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    if ts.isna().any():
        ts = pd.to_datetime(df[tcol], errors="coerce")
    # GATE: monotonic non-decreasing timestamps after construction
    if not ts.is_monotonic_increasing:
        raise SystemExit(f"MONOTONIC GATE FAILED for {tag}: timestamps not sorted")
    y = df["label"].to_numpy().astype(int)
    df.to_csv(path, index=False)
    sp, rl = splits(y), run_lengths(y)
    span_min = (ts.max() - ts.min()).total_seconds() / 60.0
    T = tag.title().replace("_", "")
    run.emit_macro(f"Stream{T}Rows", sp["n"], desc=f"{tag} rows")
    run.emit_macro(f"Stream{T}PrevalencePct", round(float(y.mean()) * 100, 4), unit=r"\%",
                   desc=f"{tag} overall attack prevalence")
    run.emit_macro(f"Stream{T}TestPrevalencePct", round(sp["test"] * 100, 4), unit=r"\%",
                   desc=f"{tag} test-split prevalence")
    run.emit_macro(f"Stream{T}TestAttacks", sp["test_attacks"], desc=f"{tag} test attacks")
    run.emit_macro(f"Stream{T}RunMedian", rl["median"], desc=f"{tag} attack run-length median")
    run.emit_macro(f"Stream{T}RunPninety", rl["p90"], desc=f"{tag} attack run-length p90")
    run.emit_macro(f"Stream{T}RunMax", rl["max"], desc=f"{tag} attack run-length max")
    run.emit_macro(f"Stream{T}SpanMinutes", round(span_min, 2), unit="min",
                   desc=f"{tag} capture span")
    run.declared_outputs.append(str(path))
    run.note(f"{tag}_sha256", sha256_file(path))
    run.note(f"{tag}_splits", sp)
    run.note(f"{tag}_run_lengths", rl)
    print(f"  {tag:<22} n={sp['n']:>9,} prev={y.mean()*100:6.3f}% "
          f"test={sp['test']*100:6.3f}% ({sp['test_attacks']:,} atk) "
          f"runs med/p90/max={rl['median']:.0f}/{rl['p90']:.0f}/{rl['max']} "
          f"span={span_min:,.1f}min")


def main() -> int:
    with provenance_run("stage1_natural_streams",
                        config={"train": TRAIN, "val": VAL,
                                "policy": "per-attack-type for LITNET (disjoint captures); "
                                          "global timestamp sort for CICIDS"},
                        seed=None,
                        notes="Stage 1: natural-order streams replace interleaved composites") as run:
        # ---- LITNET: per-attack-type, natural order within each capture ----
        src = ROOT / "data/raw/litnet2020/litnet2020_labeled.csv"
        run.declared_inputs.append(str(src))
        lit = pd.read_csv(src, low_memory=False)
        print("LITNET-2020 (per-attack-type; captures are temporally disjoint):")
        for at, g in lit.groupby("attack_type", sort=True):
            g = g.sort_values("timestamp", kind="mergesort").reset_index(drop=True)
            emit(run, f"litnet_{at}", g, "timestamp", OUT / f"litnet2020_{at}_natural.csv")

        # ---- CICIDS: single capture week, global chronological sort ----
        csrc = ROOT / "data/raw/cicids2017/cicids2017_labeled.csv"
        run.declared_inputs.append(str(csrc))
        cic = pd.read_csv(csrc, low_memory=False)
        cic = cic.sort_values("Timestamp", kind="mergesort").reset_index(drop=True)
        print("CICIDS2017 (global chronological sort):")
        emit(run, "cicids2017", cic, "Timestamp", OUT / "cicids2017_natural.csv")
        print("\nSTAGE 1 STREAMS BUILT — monotonic gate passed for every stream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
