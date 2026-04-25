#!/usr/bin/env python
"""Build a labeled LITNET-2020 dataset, streaming and memory-bounded.

Per attack type:
1. Load ATTACKERS_ONLY row hashes into a set (small, few MB)
2. Stream FLOWS CSV in chunks, label each row, keep only the first N rows
   (which preserves temporal clustering of attacks at the file front)
3. Append labeled rows directly to the combined output CSV

Never holds full FLOWS files in memory.
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import pandas as pd

SRC = Path("/tmp/litnet_unzipped")
OUT_DIR = Path("data/raw/litnet2020")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "litnet2020_labeled.csv"

COLS = [f"f{i}" for i in range(85)]
COLS[0] = "seq"
COLS[1:7] = ["start_year","start_mon","start_day","start_hr","start_min","start_sec"]
COLS[7:13] = ["end_year","end_mon","end_day","end_hr","end_min","end_sec"]
COLS[13] = "duration"
COLS[14] = "src_ip"
COLS[15] = "dst_ip"
COLS[16] = "src_port"
COLS[17] = "dst_port"
COLS[18] = "proto"

# (name, flows, attackers, row_budget). Attack rates from our earlier analysis:
# blaster_worm 0.78%, udp_flood 14.8%, spam 0.06%.
PAIRS = [
    ("blaster_worm", "BLASTER_WORM_v2.csv", "BLASTER_WORM_v2_ATTACKERS_FLOWS.csv", 500_000),
    ("udp_flood",    "UDP_FLOOD_v2.csv",    "UDP_FLOOD_v2_ATTACKERS_FLOWS.csv",    500_000),
    ("spam",         "SPAM_v2.csv",         "SPAM_v2_ATTACKERS_FLOWS.csv",         500_000),
]

# Output column list: drop seq, add label, attack_type, timestamp
OUT_COLS = COLS[1:] + ["label", "attack_type", "timestamp"]


def load_attacker_hashes(path: Path) -> set[bytes]:
    hashes: set[bytes] = set()
    with open(path, "rt") as fh:
        for line in fh:
            fields = [f.strip().strip('"') for f in line.rstrip("\n").split(",")]
            if len(fields) != 85:
                continue
            # Hash all fields except seq (column 0)
            payload = "|".join(fields[1:]).encode()
            hashes.add(hashlib.md5(payload).digest())
    return hashes


def process_attack(name: str, flows_name: str, attackers_name: str, budget: int, writer, write_header: bool) -> tuple[int, int]:
    print(f"\n=== {name} ===", flush=True)
    attacker_set = load_attacker_hashes(SRC / attackers_name)
    print(f"  {len(attacker_set):,} attacker signatures loaded", flush=True)

    n_written = 0
    n_attack_written = 0
    chunksize = 100_000

    reader = pd.read_csv(SRC / flows_name, names=COLS, header=None,
                         chunksize=chunksize, dtype=str, na_filter=False,
                         low_memory=False, quoting=csv.QUOTE_ALL)

    for chunk_idx, chunk in enumerate(reader):
        if n_written >= budget:
            break

        # Compute signatures for this chunk
        sig_series = chunk[COLS[1:]].agg("|".join, axis=1).apply(
            lambda s: hashlib.md5(s.encode()).digest()
        )
        chunk["label"] = sig_series.isin(attacker_set).astype(int)
        chunk["attack_type"] = name
        chunk["timestamp"] = (
            chunk["start_year"] + "-" + chunk["start_mon"] + "-" + chunk["start_day"] +
            "T" + chunk["start_hr"] + ":" + chunk["start_min"] + ":" + chunk["start_sec"]
        )

        # Cap this chunk's rows to the remaining budget
        remaining = budget - n_written
        if len(chunk) > remaining:
            chunk = chunk.iloc[:remaining]

        # Keep only OUT_COLS
        out_chunk = chunk[OUT_COLS]
        out_chunk.to_csv(writer, header=write_header and n_written == 0, index=False, mode="a")

        n_written += len(out_chunk)
        n_attack_written += int(out_chunk["label"].sum())

        if chunk_idx % 5 == 0 or n_written >= budget:
            print(f"  wrote {n_written:,} rows, {n_attack_written:,} attacks so far", flush=True)

    print(f"  {name} done: {n_written:,} rows, {n_attack_written:,} attacks "
          f"({n_attack_written/max(1,n_written)*100:.2f}% attack rate)", flush=True)
    return n_written, n_attack_written


def main():
    if OUT_CSV.exists():
        OUT_CSV.unlink()

    total_rows = 0
    total_attacks = 0

    with open(OUT_CSV, "at") as writer:
        for i, (name, flows_name, attackers_name, budget) in enumerate(PAIRS):
            write_header = (i == 0)
            n, a = process_attack(name, flows_name, attackers_name, budget, writer, write_header)
            total_rows += n
            total_attacks += a

    print(f"\n=== COMBINED ===", flush=True)
    print(f"total rows: {total_rows:,}", flush=True)
    print(f"total attacks: {total_attacks:,}", flush=True)
    print(f"overall attack rate: {total_attacks/max(1,total_rows)*100:.3f}%", flush=True)
    size_mb = OUT_CSV.stat().st_size / 1e6
    print(f"wrote {OUT_CSV} ({size_mb:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
