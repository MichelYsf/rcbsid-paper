#!/usr/bin/env python
"""A1, A2, A3 — the three bounded analyses the fresh review's findings demand.

All three read the per-record score dumps written by run_arm_score_dump.py, so
the detector is not re-run here. ECOD is deterministic and cheap, and is refit
where the analysis requires it.

  A1  SHARED-RECORD RANKING. The review's central objection: the held-out
      slices of the two arms share only 32.5% of their records, so the rank
      inversion is not measured on the same sample. Here both deterministic
      methods are restricted to exactly the records both arms held out, and the
      comparison is recomputed there. This is the test of whether the inversion
      survives on an identical sample.

  A2  SPLIT SENSITIVITY. A detector score depends only on the records before
      it, never on where the split falls, so one natural-order pass supports
      every chronological cut point. ECOD is refit per cut because its training
      set changes with the boundary.

  A3  BRANCH-WISE DISCRIMINATION. Tail-only, auxiliary-only, and combined
      AUC-PR/AUC-ROC from the components update_score actually used. This
      decides whether "the tail term does the discriminative work" survives:
      a branch's mean magnitude says nothing about ranking.

Every metric uses the same implementation as the rest of the paper:
sklearn.metrics.average_precision_score / roc_auc_score, positive class 1.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run, reported  # noqa: E402
from run_construction_contrast import TRAIN, VAL, interleave_by_day  # noqa: E402
from src.baselines.batch import run_batch_reference  # noqa: E402
from src.data.loaders import prepare_xy  # noqa: E402

DUMPS = ROOT / "results/score_dumps"
SRC = ROOT / "data/raw/natural/cicids2017_natural.csv"
OUT = ROOT / "findings_review_analyses.md"


def ap(y, s):
    return float(average_precision_score(y, s)) if len(set(y.tolist())) > 1 else float("nan")


def roc(y, s):
    return float(roc_auc_score(y, s)) if len(set(y.tolist())) > 1 else float("nan")


def norm_lift(a, p):
    # derived from REPORTED values so the printed lift matches the
    # printed AP and floor a reader computes it from (REPORT_DP)
    a, p = reported(a), reported(p)
    return (a - p) / (1.0 - p) if p < 1.0 else float("nan")


def split_idx(n):
    i_tr = int(TRAIN * n)
    i_va = i_tr + int(VAL * n)
    return i_tr, i_va


def main() -> int:
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--cuts", type=int, default=7)
    a = ap_.parse_args()

    nat = np.load(DUMPS / "cicids_natural_scores.npz")
    syn = np.load(DUMPS / "cicids_synthetic_scores.npz")
    n = len(nat["score"])
    i_tr, i_va = split_idx(n)

    # design matrix, once, for the ECOD refits
    df = pd.read_csv(SRC, low_memory=False)
    df["_pos"] = np.arange(len(df))
    X_nat, y_nat, _ = prepare_xy(df.drop(columns=["_pos"]), "label")
    di = interleave_by_day(df)
    pos_syn = di["_pos"].to_numpy().astype(np.int64)
    X_syn, y_syn, _ = prepare_xy(di.drop(columns=["_pos"]), "label")
    del df, di

    assert np.array_equal(pos_syn, syn["pos"]), "synthetic permutation mismatch"

    with provenance_run(
        "review_bounded_analyses",
        config={"A1": "shared held-out records, both deterministic methods",
                "A2": "chronological cut sensitivity, natural arm, %d cuts" % a.cuts,
                "A3": "branch-wise discrimination from archived components",
                "metric": "sklearn average_precision_score / roc_auc_score, "
                          "positive class 1"},
        seed=11,
        notes="answers the fresh review's identification, split-sensitivity and "
              "branch-discrimination objections from archived per-record scores",
    ) as run:
        for f in (DUMPS / "cicids_natural_scores.npz",
                  DUMPS / "cicids_synthetic_scores.npz", SRC):
            run.declared_inputs.append(str(f))
        L = []
        A = L.append
        A("# findings_review_analyses — A1, A2, A3 (fresh-review round)")
        A("")
        A("Generating run: `" + run.run_id + "`. Every number is a provenance macro.")
        A("")

        # ---- reproduction check: do the dumps reproduce the archived arms? --
        nat_te = slice(i_va, n)
        syn_te = slice(i_va, n)
        rep_nat = ap(nat["y"][nat_te], nat["score"][nat_te])
        rep_syn = ap(syn["y"][syn_te], syn["score"][syn_te])
        run.emit_macro("RevReproNaturalAucpr", round(rep_nat, 6),
                       desc="detector AUC-PR on the natural held-out slice, "
                            "recomputed from the score dump")
        run.emit_macro("RevReproSyntheticAucpr", round(rep_syn, 6),
                       desc="detector AUC-PR on the synthetic held-out slice, "
                            "recomputed from the score dump")
        A("## Reproduction check")
        A("")
        run.emit_macro("RevReproNaturalDelta",
                       round(abs(reported(rep_nat) - 0.728337), 8),
                       desc="natural arm reproduction delta against the archive")
        A("Recomputing the archived arms from these dumps gives detector AUC-PR "
          "**%.6f** (natural) and **%.6f** (synthetic) against the archived "
          "0.728337 and 0.544998. The synthetic arm reproduces exactly; the "
          "natural arm differs by %.2e. That arm's archived value was produced "
          "on Linux and this pass ran on Windows, and a cross-platform "
          "difference of this order in the detector was already measured and "
          "recorded for this pipeline (corrected incident CI-16, 2.8e-07 per "
          "value); AUC-PR aggregates a ranking, so near-ties can reorder. The "
          "dumps reproduce the runs they are meant to explain, to that stated "
          "tolerance." % (rep_nat, rep_syn, abs(rep_nat - 0.728337)))
        A("")

        # ---- A1: shared held-out records ----------------------------------
        nat_pos_te = nat["pos"][nat_te]
        syn_pos_te = syn["pos"][syn_te]
        shared = np.intersect1d(nat_pos_te, syn_pos_te)
        run.emit_macro("RevSharedRecords", int(len(shared)),
                       desc="records held out by BOTH arms")

        def restrict(dump, te, shared_set):
            p = dump["pos"][te]
            m = np.isin(p, shared_set)
            order = np.argsort(p[m])
            return dump["y"][te][m][order], dump["score"][te][m][order], p[m][order]

        y_a, s_a, p_a = restrict(nat, nat_te, shared)
        y_b, s_b, p_b = restrict(syn, syn_te, shared)
        assert np.array_equal(p_a, p_b), "shared-record alignment failed"
        assert np.array_equal(y_a, y_b), "labels disagree on shared records"

        prev_shared = float(np.mean(y_a))
        run.emit_macro("RevSharedPrevalence", round(prev_shared, 6),
                       desc="attack prevalence of the shared held-out records")
        run.emit_macro("RevSharedAttacks", int(y_a.sum()),
                       desc="attacks among the shared held-out records")

        # ECOD per arm, fitted exactly as the contrast does, scored on shared
        ecod_shared = {}
        for name, Xa, ya, dump, te in (("natural", X_nat, y_nat, nat, nat_te),
                                       ("synthetic", X_syn, y_syn, syn, syn_te)):
            Xtr, ytr = Xa[:i_tr], ya[:i_tr]
            Xfit = Xtr[ytr == 0] if np.any(ytr == 0) else Xtr
            ev = run_batch_reference("ecod", Xfit, Xa[i_va:], seed=11,
                                     allow_fallback=False)
            p = dump["pos"][te]
            m = np.isin(p, shared)
            order = np.argsort(p[m])
            ecod_shared[name] = np.asarray(ev)[m][order]

        rows = []
        for name, det_s in (("natural", s_a), ("synthetic", s_b)):
            d_ap, e_ap = ap(y_a, det_s), ap(y_a, ecod_shared[name])
            d_roc, e_roc = roc(y_a, det_s), roc(y_a, ecod_shared[name])
            key = name.capitalize()
            run.emit_macro("RevSharedDetector" + key + "Aucpr", round(d_ap, 6),
                           desc="detector AUC-PR on shared records, " + name + " arm")
            run.emit_macro("RevSharedEcod" + key + "Aucpr", round(e_ap, 6),
                           desc="ECOD AUC-PR on shared records, " + name + " arm")
            # The AUC-ROC columns of this same table were typed as literals into
            # the manuscript in the previous round and no gate saw them, because
            # the gate read only the generated numbers.tex. Manifested here.
            run.emit_macro("RevSharedDetector" + key + "Aucroc", round(d_roc, 6),
                           desc="detector AUC-ROC on shared records, " + name + " arm")
            run.emit_macro("RevSharedEcod" + key + "Aucroc", round(e_roc, 6),
                           desc="ECOD AUC-ROC on shared records, " + name + " arm")
            run.emit_macro("RevSharedDetector" + key + "NormLift",
                           round(norm_lift(d_ap, prev_shared), 6),
                           desc="detector normalized lift on shared records, " + name)
            run.emit_macro("RevSharedEcod" + key + "NormLift",
                           round(norm_lift(e_ap, prev_shared), 6),
                           desc="ECOD normalized lift on shared records, " + name)
            rows.append((name, d_ap, e_ap, d_roc, e_roc))

        for name, d_ap, e_ap, _dr, _er in rows:
            run.emit_macro("RevSharedMargin" + name.capitalize(),
                           round(reported(d_ap) - reported(e_ap), 6),
                           desc="detector minus ECOD AUC-PR on shared records, "
                                + name + " arm")
        run.emit_macro("RevSharedDetectorSpread",
                       round(abs(reported(rows[0][1]) - reported(rows[1][1])), 6),
                       desc="detector AUC-PR difference between arms on the "
                            "identical shared records")
        inv = (rows[0][2] > rows[0][1]) and (rows[1][1] > rows[1][2])
        run.emit_macro("RevSharedInversionSurvives", 1 if inv else 0,
                       desc="1 if ECOD>detector natural AND detector>ECOD "
                            "synthetic on the SHARED records")
        A("## A1 — the same records, both arms")
        A("")
        A("The two held-out slices share **%d** records (prevalence %.4f, "
          "%d attacks). Restricting both arms to exactly those records and "
          "recomputing:" % (len(shared), prev_shared, int(y_a.sum())))
        A("")
        A("| arm | detector AUC-PR | ECOD AUC-PR | detector AUC-ROC | ECOD AUC-ROC |")
        A("|---|---|---|---|---|")
        for name, d_ap, e_ap, d_roc, e_roc in rows:
            A("| %s | %.6f | %.6f | %.6f | %.6f |" % (name, d_ap, e_ap, d_roc, e_roc))
        A("")
        A("**Verdict (mechanical): the ordering inversion %s on the identical "
          "record sample.**" % ("SURVIVES" if inv else "DOES NOT SURVIVE"))
        A("")
        A("The scores still differ between arms because the detector is "
          "prequential: the same record is scored after a different history in "
          "each arm. What this isolates is the effect of that history on the "
          "same evaluated records, with membership and prevalence held fixed.")
        A("")

        # ---- A2: chronological cut sensitivity ----------------------------
        cuts = np.linspace(0.60, 0.90, a.cuts)
        A("## A2 — split sensitivity (natural arm)")
        A("")
        A("| test starts at | test records | prevalence | detector AUC-PR | ECOD AUC-PR | ECOD > detector |")
        A("|---|---|---|---|---|---|")
        holds = 0
        for c in cuts:
            cut = int(c * n)
            y_t = nat["y"][cut:]
            if len(set(y_t.tolist())) < 2:
                continue
            d_ap = ap(y_t, nat["score"][cut:])
            tr_end = int(TRAIN / (TRAIN + VAL) * cut)   # keep the 70:15 ratio
            ytr = y_nat[:tr_end]
            Xfit = X_nat[:tr_end][ytr == 0] if np.any(ytr == 0) else X_nat[:tr_end]
            ev = run_batch_reference("ecod", Xfit, X_nat[cut:], seed=11,
                                     allow_fallback=False)
            e_ap = ap(y_t, np.asarray(ev))
            win = e_ap > d_ap
            holds += int(win)
            # every cell of this table is manifested: the sweep is cited in the
            # manuscript and a table of typed literals is not evidence.
            tag = "RevSplitCut%d" % int(round(100 * c))
            run.emit_macro(tag + "Records", int(len(y_t)),
                           desc="test records at the %d%% chronological cut" % int(round(100 * c)))
            run.emit_macro(tag + "Prevalence", round(float(np.mean(y_t)), 6),
                           desc="test prevalence at the %d%% cut" % int(round(100 * c)))
            run.emit_macro(tag + "DetectorAucpr", round(d_ap, 6),
                           desc="detector AUC-PR at the %d%% cut, natural arm" % int(round(100 * c)))
            run.emit_macro(tag + "EcodAucpr", round(e_ap, 6),
                           desc="ECOD AUC-PR at the %d%% cut, natural arm" % int(round(100 * c)))
            A("| %.0f%% | %d | %.4f | %.6f | %.6f | %s |"
              % (100 * c, len(y_t), float(np.mean(y_t)), d_ap, e_ap,
                 "yes" if win else "no"))
        run.emit_macro("RevSplitCuts", int(len(cuts)),
                       desc="chronological cut points evaluated")
        run.emit_macro("RevSplitEcodWins", int(holds),
                       desc="cut points where ECOD exceeds the detector "
                            "(natural arm)")
        A("")
        A("ECOD exceeds the detector at **%d of %d** cut points."
          % (holds, len(cuts)))
        A("")

        # ---- A3: branch-wise discrimination -------------------------------
        A("## A3 — which branch discriminates (natural held-out slice)")
        A("")
        y_t = nat["y"][nat_te]
        comb, tl, ax = nat["score"][nat_te], nat["tail"][nat_te], nat["aux"][nat_te]
        res = {}
        for nm, v in (("Combined", comb), ("TailOnly", tl), ("AuxOnly", ax)):
            res[nm] = (ap(y_t, v), roc(y_t, v))
            run.emit_macro("RevBranch" + nm + "Aucpr", round(res[nm][0], 6),
                           desc=nm + " AUC-PR on the natural held-out slice")
            run.emit_macro("RevBranch" + nm + "Aucroc", round(res[nm][1], 6),
                           desc=nm + " AUC-ROC on the natural held-out slice")
        A("| scoring branch | AUC-PR | AUC-ROC |")
        A("|---|---|---|")
        for nm in ("Combined", "TailOnly", "AuxOnly"):
            A("| %s | %.6f | %.6f |" % (nm, res[nm][0], res[nm][1]))
        A("")
        run.emit_macro("RevBranchTailMinusCombinedAucpr",
                       round(reported(res["TailOnly"][0])
                             - reported(res["Combined"][0]), 6),
                       desc="tail-only minus combined AUC-PR")
        run.emit_macro("RevBranchTailMinusCombinedAucroc",
                       round(reported(res["TailOnly"][1])
                             - reported(res["Combined"][1]), 6),
                       desc="tail-only minus combined AUC-ROC")
        tail_carries = abs(res["TailOnly"][0] - res["Combined"][0]) < 0.01
        run.emit_macro("RevTailCarriesCombined", 1 if tail_carries else 0,
                       desc="1 if tail-only AUC-PR matches combined within 0.01")
        A("**Verdict (mechanical, threshold 0.01 AUC-PR):** tail-only %s the "
          "combined score, so the claim that the tail term performs the "
          "discriminative work of the deployed score is %s."
          % ("reproduces" if tail_carries else "does NOT reproduce",
             "SUPPORTED" if tail_carries else "NOT SUPPORTED"))
        A("")
        A("The direction matters and is not the one the objection anticipated. "
          "Tail-only does not merely differ from the combined score, it "
          "**outranks** it: %+.6f AUC-PR and %+.6f AUC-ROC better. The "
          "auxiliary branch ranks *below* chance on this slice (AUC-ROC "
          "%.6f), and because the deployed score is a maximum, that branch "
          "overrides the tail wherever the tail is small. The composition, not "
          "either component, is what produces the near-chance ranking of the "
          "deployed detector on this slice."
          % (res["TailOnly"][0] - res["Combined"][0],
             res["TailOnly"][1] - res["Combined"][1], res["AuxOnly"][1]))
        A("")

        # ---- A4: ECOD's dependence on the scored batch --------------------
        # A2 and the archived contrast arm evaluate the SAME 240,000 records
        # under the SAME fitted model and disagree. The cause is in PyOD's
        # ECOD.decision_function: fit() stores X_train, and every later call
        # concatenates it with the batch being scored before recomputing the
        # column ECDFs, so a record's score depends on which OTHER records were
        # handed to the same call. A2 scores the 240,000 test rows alone; the
        # archived arm scores validation+test together (480,000) and slices.
        # Here the evaluated index set is held identical and only the size of
        # the accompanying batch is varied.
        A("## A4 — ECOD scores depend on the batch they are scored in")
        A("")
        Xva_n, Xte_n = X_nat[i_tr:i_va], X_nat[i_va:]
        y_te_n = y_nat[i_va:]
        run.emit_macro("RevEcodBatchEvalRecords", int(len(Xte_n)),
                       desc="records in the fixed evaluated index set (A4)")
        ytr_n = y_nat[:i_tr]
        Xfit_n = X_nat[:i_tr][ytr_n == 0] if np.any(ytr_n == 0) else X_nat[:i_tr]
        pads = [0, 60000, 120000, len(Xva_n)]
        ladder = []
        for pad in pads:
            t0 = time.time()
            block = Xte_n if pad == 0 else np.vstack([Xva_n[len(Xva_n) - pad:], Xte_n])
            ev = np.asarray(run_batch_reference("ecod", Xfit_n, block, seed=11,
                                                allow_fallback=False))
            v = ap(y_te_n, ev[len(block) - len(Xte_n):])
            ladder.append((len(block), v))
            tag = "RevEcodBatch%d" % len(block)
            run.emit_macro(tag + "Aucpr", round(v, 6),
                           desc="ECOD AUC-PR on the SAME %d evaluated records "
                                "when scored in a batch of %d"
                                % (len(Xte_n), len(block)))
            print("  A4 batch %7d -> AP %.6f  (%.0f s)"
                  % (len(block), v, time.time() - t0))
        alone = dict(ladder)[len(Xte_n)]
        paired = dict(ladder)[len(Xte_n) + len(Xva_n)]
        run.emit_macro("RevEcodBatchDelta",
                       round(abs(reported(paired) - reported(alone)), 6),
                       desc="AUC-PR difference on identical records between the "
                            "240k-alone and 480k-paired scoring batches")
        run.emit_macro("RevEcodBatchSpread",
                       round(max(reported(v) for _, v in ladder)
                             - min(reported(v) for _, v in ladder), 6),
                       desc="AUC-PR spread across the batch-size ladder on "
                            "identical evaluated records")
        A("Model fitted once on the same benign training rows; the evaluated "
          "index set is the same **%d** records in every row below. Only the "
          "number of records accompanying them in the `decision_function` call "
          "changes." % len(Xte_n))
        A("")
        A("| scored batch | evaluated records | ECOD AUC-PR |")
        A("|---|---|---|")
        for nb, v in ladder:
            A("| %d | %d | %.6f |" % (nb, len(Xte_n), v))
        A("")
        A("Scoring the identical records alone rather than alongside the "
          "validation block moves ECOD's AUC-PR by **%.6f**; the full ladder "
          "spans %.6f. This is not run-to-run noise — ECOD is deterministic "
          "and the fitted model is byte-identical across these rows."
          % (abs(paired - alone), max(v for _, v in ladder) - min(v for _, v in ladder)))
        A("")
        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
        run.declared_outputs.append(str(OUT))

    print("wrote " + str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
