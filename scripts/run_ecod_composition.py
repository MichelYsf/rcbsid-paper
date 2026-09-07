#!/usr/bin/env python
"""ECOD batch composition, size held fixed (second referee report, MAJOR 2).

The batch-size ladder of the review round changed the number of records
accompanying the evaluated set and, with it, their content, so it could not
separate size from composition. This run holds the fitted model and the batch
SIZE fixed and changes only the batch CONTENT: the 78000 shared held-out
records are scored under the timestamp-arm fitted ECOD model (benign-only
training rows of that arm, PyOD defaults) inside two batches of identical
size, the timestamp-order held-out slice and the day-round-robin held-out
slice, each 240000 records, which share exactly those 78000 records and
differ in the other 162000. The AP and AUC-ROC of the shared records under
each batch, and their difference from reported values, are emitted. The
timestamp-slice value reproduces the Table 6 slice-batch value by
construction, and that reproduction is asserted.

Everything comes from data on disk: the archived per-record score dumps (for
positions and labels) and the archived stream file (for the design matrix).
The detector is not re-run. --dry-run uses random scores and writes no
manifest.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import MANIFEST_DIR, provenance_run, reported  # noqa: E402
from run_referee_analyses import DUMPS, SRC, ap, roc, split_idx, fit_score_ecod  # noqa: E402
from run_construction_contrast import TRAIN, VAL, interleave_by_day  # noqa: E402
from src.data.loaders import prepare_xy  # noqa: E402

REFEREE_RUN = "referee_bounded_analyses_20260906T182158_de69afab"
OUT = ROOT / "findings_ecod_composition.md"


class _DryRun:
    run_id = "DRY-RUN-NOT-MANIFESTED"

    def __init__(self):
        self.declared_inputs: list[str] = []
        self.macros: dict[str, object] = {}

    def emit_macro(self, macro, value, unit="", desc=""):
        self.macros[macro] = value
        return value


@contextlib.contextmanager
def _dry_run(*_a, **_kw):
    yield _DryRun()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    t0 = time.time()

    ref_path = MANIFEST_DIR / (REFEREE_RUN + ".json")
    ref = json.loads(ref_path.read_text(encoding="utf-8"))["macros"]
    archived_slice = float(ref["RefEcodShared240NaturalAucpr"]["value"])

    nat = np.load(DUMPS / "cicids_natural_scores.npz")
    syn = np.load(DUMPS / "cicids_synthetic_scores.npz")
    n = len(nat["score"])
    i_tr, i_va = split_idx(n)
    te = slice(i_va, n)
    nat_pos_te, syn_pos_te = nat["pos"][te], syn["pos"][te]
    shared = np.intersect1d(nat_pos_te, syn_pos_te)

    def restrict(dump):
        pp = dump["pos"][te]
        m = np.isin(pp, shared)
        order = np.argsort(pp[m])
        return dump["y"][te][m][order], pp[m][order], m, order

    y_sh, p_a, m_nat, o_nat = restrict(nat)
    y_b, p_b, m_syn, o_syn = restrict(syn)
    assert np.array_equal(p_a, p_b) and np.array_equal(y_sh, y_b)
    assert m_nat.sum() == m_syn.sum() == len(shared)

    if a.dry_run:
        rng = np.random.default_rng(0)
        s_nat_batch = rng.random(n - i_va)
        s_syn_batch = rng.random(n - i_va)
    else:
        print("loading design matrix", flush=True)
        df = pd.read_csv(SRC, low_memory=False)
        df["_pos"] = np.arange(len(df))
        X_nat, y_nat, _ = prepare_xy(df.drop(columns=["_pos"]), "label")
        di = interleave_by_day(df)
        pos_syn = di["_pos"].to_numpy().astype(np.int64)
        del df, di
        assert np.array_equal(pos_syn, syn["pos"]), "synthetic permutation mismatch"
        assert np.array_equal(y_nat, nat["y"])
        X_syn_te = X_nat[pos_syn][i_va:]           # the round-robin held-out slice
        # sanity: both batches contain exactly the shared records
        assert np.array_equal(np.sort(pos_syn[i_va:][m_syn]), shared)
        print("ECOD: timestamp-arm model, timestamp-slice batch", flush=True)
        s_nat_batch = fit_score_ecod(X_nat, y_nat, i_tr, X_nat[i_va:])
        print("ECOD: timestamp-arm model, round-robin-slice batch", flush=True)
        s_syn_batch = fit_score_ecod(X_nat, y_nat, i_tr, X_syn_te)
        del X_nat, X_syn_te

    sh_nat = s_nat_batch[m_nat][o_nat]      # shared records, natural-position order
    sh_syn = s_syn_batch[m_syn][o_syn]
    ap_nat, ap_syn = ap(y_sh, sh_nat), ap(y_sh, sh_syn)
    roc_nat, roc_syn = roc(y_sh, sh_nat), roc(y_sh, sh_syn)

    runner = _dry_run if a.dry_run else provenance_run
    with runner(
        "ecod_batch_composition",
        config={"model": "ECOD fitted on the timestamp arm's benign-only training rows, PyOD "
                         "defaults; the fit is repeated identically for each batch (ECOD is "
                         "deterministic, and the timestamp-slice value is asserted to reproduce "
                         "the archived slice value)",
                "batches": "timestamp-order held-out slice and day-round-robin held-out slice, "
                           "240000 records each, sharing the 78000 evaluated records",
                "evaluated": "the 78000 shared records, natural-position order",
                "metric": "sklearn average_precision_score / roc_auc_score, positive class 1",
                "train": TRAIN, "val": VAL, "referee_run": REFEREE_RUN},
        seed=11,
        notes="second referee report, MAJOR 2: batch content varied with size and model fixed; "
              "no detector rerun",
    ) as run:
        for f in (DUMPS / "cicids_natural_scores.npz", DUMPS / "cicids_synthetic_scores.npz",
                  SRC, ref_path):
            run.declared_inputs.append(str(f))
        if not a.dry_run:
            assert round(ap_nat, 6) == archived_slice, (ap_nat, archived_slice)
        run.emit_macro("RefEcodCompBatchRecords", int(n - i_va),
                       desc="records in each of the two scoring batches")
        run.emit_macro("RefEcodCompSharedRecords", int(len(shared)),
                       desc="evaluated records common to both batches")
        run.emit_macro("RefEcodCompDifferingRecords", int(n - i_va - len(shared)),
                       desc="records in which the two batches differ")
        run.emit_macro("RefEcodCompNaturalBatchAucpr", round(ap_nat, 6),
                       desc="ECOD AUC-PR on the shared records, timestamp-arm model, timestamp-slice batch (reproduces the Table 6 slice value)")
        run.emit_macro("RefEcodCompSyntheticBatchAucpr", round(ap_syn, 6),
                       desc="ECOD AUC-PR on the shared records, timestamp-arm model, round-robin-slice batch")
        run.emit_macro("RefEcodCompNaturalBatchAucroc", round(roc_nat, 6),
                       desc="ECOD AUC-ROC on the shared records, timestamp-arm model, timestamp-slice batch")
        run.emit_macro("RefEcodCompSyntheticBatchAucroc", round(roc_syn, 6),
                       desc="ECOD AUC-ROC on the shared records, timestamp-arm model, round-robin-slice batch")
        d_ap = abs(reported(ap_nat) - reported(ap_syn))
        d_roc = abs(reported(roc_nat) - reported(roc_syn))
        run.emit_macro("RefEcodCompDeltaAucpr", round(d_ap, 6),
                       desc="AUC-PR difference between the two batches, same model, same size, from reported values")
        run.emit_macro("RefEcodCompDeltaAucroc", round(d_roc, 6),
                       desc="AUC-ROC difference between the two batches, same model, same size, from reported values")
        run.emit_macro("RefEcodCompositionMovesAucpr", 1 if d_ap > 0 else 0,
                       desc="1 if batch content alone, at fixed size and model, changes the reported AUC-PR")
        run.emit_macro("RefEcodCompReproducesSlice", 1 if (round(ap_nat, 6) == archived_slice and not a.dry_run) else 0,
                       desc="1 if the timestamp-slice value reproduces the archived Table 6 slice-batch value")
        wall = int(time.time() - t0)
        run.emit_macro("RefEcodCompWallSeconds", wall, unit="s", desc="wall time of this run")

        L = []
        A = L.append
        A("# findings_ecod_composition — batch content at fixed size and fixed model")
        A("")
        A("Generating run: `" + run.run_id + "`. Every number is a provenance macro.")
        A("")
        A("Model: ECOD fitted on the timestamp arm's benign-only training rows, the same fit "
          "repeated identically for each batch. Evaluated: the "
          "%d records both arms hold out, in natural-position order. Batches: the timestamp-order "
          "held-out slice and the day-round-robin held-out slice, %d records each, differing in %d records."
          % (len(shared), n - i_va, n - i_va - len(shared)))
        A("")
        A("| batch (same model, same size) | AUC-PR | AUC-ROC |")
        A("|---|---|---|")
        A("| timestamp-order slice (Table 6 slice value) | %.6f | %.6f |" % (ap_nat, roc_nat))
        A("| day-round-robin slice | %.6f | %.6f |" % (ap_syn, roc_syn))
        A("")
        A("Difference from reported values: AUC-PR %.6f, AUC-ROC %.6f. Composition alone %s the AUC-PR."
          % (d_ap, d_roc, "moves" if d_ap > 0 else "does not move"))
        A("")
        A("Reproduction of the archived slice-batch value (%.6f): %s." % (archived_slice, "exact" if round(ap_nat, 6) == archived_slice else "NOT exact"))
        A("")
        A("Wall time: %d s." % wall)
        out = OUT if not a.dry_run else ROOT / "results" / "_dryrun" / OUT.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(L) + "\n", encoding="utf-8")
        if not a.dry_run:
            run.declared_outputs.append(str(out))
        print("wrote", out, flush=True)
    print("done in %ds" % int(time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
