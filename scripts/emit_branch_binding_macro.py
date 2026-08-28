#!/usr/bin/env python
"""Manifest the auxiliary branch's binding share ON THE SLICE THAT IS SCORED.

The round-3 sweep found Section 6 supporting a statement about the held-out
slice (records 1.36M-1.6M) with \\SThreeChangePointBindingPct, which
verify_score_threshold.py measured on a 50,000-record PREFIX of the same
stream. The conclusion ("most records") survives either way, but citing a
measurement from a different sample to characterise this one is exactly the
class of slippage this project records rather than tolerates.

No new scoring is needed: run_arm_score_dump.py archived the tail and auxiliary
components per record, so the share is a count over values already stored.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run  # noqa: E402
from run_construction_contrast import TRAIN, VAL  # noqa: E402

DUMP = ROOT / "results/score_dumps/cicids_natural_scores.npz"


def main() -> int:
    d = np.load(DUMP)
    n = len(d["score"])
    i_va = int(TRAIN * n) + int(VAL * n)
    tail, aux = d["tail"][i_va:], d["aux"][i_va:]

    with provenance_run(
        "branch_binding_share",
        config={"slice": "natural-arm held-out slice (positional 70/15/15 tail)",
                "definition": "auxiliary binds when its value exceeds the tail "
                              "value, i.e. when it determines max(tail, aux)"},
        seed=0,
        notes="derived from archived per-record components; no re-scoring",
    ) as run:
        run.declared_inputs.append(str(DUMP))
        binds = float(np.mean(aux > tail)) * 100.0
        run.emit_macro("RevBranchAuxBindsHeldoutPct", round(binds, 3), unit="%",
                       desc="share of the natural held-out slice on which the "
                            "auxiliary branch exceeds the tail branch and so "
                            "determines the deployed score")
        run.emit_macro("RevBranchHeldoutRows", int(len(tail)),
                       desc="records in the natural held-out slice used for the "
                            "branch-binding share")
        print("held-out rows      :", len(tail))
        print("auxiliary binds on : %.3f%%" % binds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
