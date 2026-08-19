#!/usr/bin/env python
"""Manifest what the CICIDS2017 'whole week' actually is.

Stage 1 describes `cicids2017_natural.csv` as the whole capture week, 1,600,000
rows. That row count is exactly round because it is a BUDGET, not a census:
scripts/build_cicids_labeled.py applies a fixed per-day budget
(300k/300k/350k/300k/350k) and proportionally stride-subsamples each day to fit.

The subsample preserves prevalence WITHIN each day. It does not preserve the
mix BETWEEN days, because the budgets are fixed rather than a common factor, so
days that are larger in the original are cut harder. The attack-heavy days
(Wednesday, Friday) are the largest, so they are cut hardest, and the resulting
overall prevalence is lower than the true week's.

This does not affect the S4 construction contrast, where both arms hold the
identical record multiset and only the order differs. It does affect how the
absolute prevalence figures may be described in the manuscript, so the numbers
are measured and manifested here rather than asserted.

Run time is a few minutes: it reads the label column of all five original
per-day CSVs (about 1.1 GB).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run  # noqa: E402

SRC = ROOT / "data/raw/cicids2017_original"
LABELED = ROOT / "data/raw/cicids2017/cicids2017_labeled.csv"
DAYS = [("monday", 300_000), ("tuesday", 300_000), ("wednesday", 350_000),
        ("thursday", 300_000), ("friday", 350_000)]
ATTEMPTED = " - Attempted"


def main() -> int:
    if not SRC.exists():
        print("original per-day CSVs absent at " + str(SRC) + "; cannot audit")
        return 1

    with provenance_run(
        "cicids_subsample_audit",
        config={"per_day_budgets": {d: b for d, b in DAYS},
                "source": str(SRC), "labeled": str(LABELED),
                "question": "is the 1.6M-row 'whole week' a census or a budget?"},
        seed=0,
        notes="measures what fraction of the capture week the labeled dataset "
              "retains, and the prevalence bias the fixed per-day budgets induce",
    ) as run:
        run.declared_inputs.append(str(LABELED))
        per_day = {}
        raw_tot = post_tot = used_tot = atk_post_tot = 0
        for day, budget in DAYS:
            f = SRC / (day + ".csv")
            run.declared_inputs.append(str(f))
            lab = pd.read_csv(f, usecols=["Label"], low_memory=False)["Label"].astype(str)
            raw = len(lab)
            att_mask = lab.str.contains(ATTEMPTED, na=False)
            post = int(raw - att_mask.sum())
            atk = int((lab[~att_mask] != "BENIGN").sum())
            used = min(budget, post)
            per_day[day] = {"raw": raw, "attempted_dropped": int(att_mask.sum()),
                            "eligible": post, "budget": budget, "used": used,
                            "retention_pct": round(100.0 * used / post, 3),
                            "attacks_eligible": atk,
                            "day_prevalence_pct": round(100.0 * atk / post, 4)}
            raw_tot += raw
            post_tot += post
            used_tot += used
            atk_post_tot += atk

        run.note("per_day", per_day)

        # Measured, not inferred: read the labeled file's actual prevalence.
        lab_used = pd.read_csv(LABELED, usecols=["label"], low_memory=False)["label"]
        used_rows = int(len(lab_used))
        used_atk = int(lab_used.sum())
        used_prev = 100.0 * used_atk / used_rows
        true_prev = 100.0 * atk_post_tot / post_tot

        run.emit_macro("CicidsWeekRawRows", raw_tot,
                       desc="rows in the improved CICIDS2017 per-day CSVs")
        run.emit_macro("CicidsWeekAttemptedDropped", raw_tot - post_tot,
                       desc="rows dropped for a ' - Attempted' label")
        run.emit_macro("CicidsWeekEligibleRows", post_tot,
                       desc="capture-week rows eligible after the Attempted drop")
        run.emit_macro("CicidsWeekUsedRows", used_rows,
                       desc="rows actually used by the labeled dataset")
        run.emit_macro("CicidsWeekRetentionPct", round(100.0 * used_rows / post_tot, 3),
                       unit="%", desc="fraction of the eligible capture week retained")
        run.emit_macro("CicidsWeekTruePrevalencePct", round(true_prev, 4), unit="%",
                       desc="attack prevalence of the full eligible capture week")
        run.emit_macro("CicidsWeekUsedPrevalencePct", round(used_prev, 4), unit="%",
                       desc="attack prevalence of the subsampled labeled dataset")
        run.emit_macro("CicidsWeekPrevalenceBiasPp", round(used_prev - true_prev, 4),
                       unit="pp",
                       desc="prevalence bias induced by the fixed per-day budgets")
        run.emit_macro("CicidsWeekMinDayRetentionPct",
                       round(min(v["retention_pct"] for v in per_day.values()), 3),
                       unit="%", desc="least-retained capture day")
        run.emit_macro("CicidsWeekMaxDayRetentionPct",
                       round(max(v["retention_pct"] for v in per_day.values()), 3),
                       unit="%", desc="most-retained capture day")

        print("CICIDS2017 capture week")
        print("  raw rows                : %d" % raw_tot)
        print("  dropped ' - Attempted'  : %d" % (raw_tot - post_tot))
        print("  eligible rows           : %d" % post_tot)
        print("  used by labeled dataset : %d  (%.2f%% retained)"
              % (used_rows, 100.0 * used_rows / post_tot))
        print("")
        print("  true week prevalence    : %.4f%%" % true_prev)
        print("  subsampled prevalence   : %.4f%%" % used_prev)
        print("  bias from fixed budgets : %+.4f pp" % (used_prev - true_prev))
        print("")
        for day, v in per_day.items():
            print("  %-10s eligible %7d  used %6d  (%5.1f%%)  day prev %6.2f%%"
                  % (day, v["eligible"], v["used"], v["retention_pct"],
                     v["day_prevalence_pct"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
