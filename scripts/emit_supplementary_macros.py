#!/usr/bin/env python
"""Manifest the five numbers the contradiction sweep found typed as literals.

The F8 sweep (B6) found the manuscript asserting "every number traces to an
archived manifest" while five numbers were typed literals: the attack-free
held-out rows (162,000), the Friday held-out density (77.7%), the Stage-6
diagnostic window (15,000), and unsigned magnitudes used with directional
words ("below", "moves by") whose signed macros double-encode the sign.

None of these needs new compute. Each is a deterministic transcription or
arithmetic consequence of values ALREADY recorded in archived manifests, so
this run declares those manifests as inputs, re-derives each number from the
stored data, and emits it as a macro. The generating evidence remains the
original run; this run manifests the derivation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import MANIFEST_DIR, provenance_run, reported  # noqa: E402


def load(prefix: str) -> tuple[Path, dict]:
    hits = sorted(MANIFEST_DIR.glob(prefix + "*.json"))
    assert hits, "no manifest with prefix " + prefix
    assert len(hits) == 1, "ambiguous prefix " + prefix + ": " + str(hits)
    return hits[0], json.loads(hits[0].read_text(encoding="utf-8"))


def main() -> int:
    comp_path, comp = load("cicids_heldout_composition_")
    # Pinned rather than prefix-matched, for the reason recorded in
    # results/manifests/superseded/README.md: two deliverables runs can
    # coexist legitimately, and which one a number is attributed to must
    # be a decision, never whichever the glob happens to return.
    deliv_path, deliv = load("s4_contrast_deliverables_20260827T124050_")
    # Pinned, not prefix-matched: the 2026-08-27 ablation run regenerated the
    # findings document (to withdraw an unmanifested number) but reused the
    # cached arm metrics, so the run that actually MEASURED these values is the
    # 24 Aug one. Recency must not decide which run a number is attributed to.
    abl_path, abl = load("s6_bocpd_corrected_ablation_20260824T092655_")

    with provenance_run(
        "supplementary_macros",
        config={"reason": "F8 sweep item B6: replace typed literals with "
                          "manifested macros; derivations only, no new compute"},
        seed=0,
        notes="each value re-derived from the archived manifest named in inputs",
    ) as run:
        for p in (comp_path, deliv_path, abl_path):
            run.declared_inputs.append(str(p))

        # 1) attack-free held-out rows and Friday density, from the stored
        #    by-day composition of the synthetic held-out slice
        by_day = comp["extra"]["synthetic_heldout_by_day"]
        attack_free = sum(v["rows"] for v in by_day.values() if v["attacks"] == 0)
        fri = [v for v in by_day.values() if v["attacks"] > 0]
        assert len(fri) == 1, "expected exactly one attack-bearing day"
        density = 100.0 * fri[0]["attacks"] / fri[0]["rows"]
        run.emit_macro("CicidsHeldoutAttackFreeRows", int(attack_free),
                       desc="synthetic held-out rows from days contributing zero "
                            "attacks (Mon-Thu)")
        run.emit_macro("CicidsFridayHeldoutDensityPct", round(density, 3), unit="%",
                       desc="attack density of the synthetic arm's Friday held-out "
                            "sub-slice")

        # 2) unsigned magnitudes for use with directional words
        hst_lift = deliv["macros"]["SFourCicidsNaturalHstLift"]["value"]
        shift = deliv["macros"]["SFourCicidsPrevShiftPp"]["value"]
        run.emit_macro("SFourCicidsNaturalHstLiftAbs", round(abs(float(hst_lift)), 6),
                       desc="magnitude of HST's below-chance lift, natural arm")
        run.emit_macro("SFourCicidsPrevShiftAbsPp", round(abs(float(shift)), 4),
                       unit="pp", desc="magnitude of the held-out prevalence shift")

        # 3) the Stage-6 diagnostic window. Not in the ablation manifest's
        #    config (a defect of that run's recording, noted rather than
        #    hidden); the authoritative source is the default of
        #    saturation_diagnostic() in the script the manifest's git commit
        #    pins. Parsed from the source, and asserted to match.
        src = (ROOT / "scripts/run_bocpd_ablation.py").read_text(encoding="utf-8")
        m = re.search(r"def saturation_diagnostic\(X, rows: int = (\d[\d_]*)\)", src)
        assert m, "saturation_diagnostic default not found"
        window = int(m.group(1).replace("_", ""))
        run.note("window_source",
                 "saturation_diagnostic() default in scripts/run_bocpd_ablation.py "
                 "at the commit pinned by " + abl["run_id"] +
                 "; the ablation manifest did not record it (noted, not hidden)")
        run.emit_macro("SSixDiagWindowRows", window,
                       desc="records covered by the Stage-6 score-distribution "
                            "diagnostic")

        # 4) Amendment G: normalized lift (AP - p) / (1 - p). Additive lift has
        #    a prevalence-dependent ceiling of 1-p, so additive values are not
        #    comparable across arms whose prevalence differs by 43 points -
        #    which is exactly the comparison this paper makes.
        dm = deliv["macros"]
        am = abl["macros"]

        def nl(ap_v, p_v):
            # derived from REPORTED values (REPORT_DP): the printed lift
            # must equal the arithmetic on the printed AP and floor
            a, p = reported(ap_v), reported(p_v)
            return (a - p) / (1.0 - p)

        for arm, floor_key in (("Natural", "SFourCicidsNaturalChanceFloor"),
                               ("Synthetic", "SFourCicidsSyntheticChanceFloor")):
            floor = dm[floor_key]["value"]
            for meth in ("ProposedDetector", "Ecod", "Hst"):
                k = "SFourCicids" + arm + meth + "Aucpr"
                if k in dm:
                    run.emit_macro("SFourCicids" + arm + meth + "NormLift",
                                   round(nl(dm[k]["value"], floor), 6),
                                   desc="CICIDS " + arm + " " + meth +
                                        " normalized lift (AP-p)/(1-p)")
        s6floor = am["SSixChanceFloor"]["value"]
        for v in ("Original", "Corrected"):
            run.emit_macro("SSix" + v + "NormLift",
                           round(nl(am["SSix" + v + "Aucpr"]["value"], s6floor), 6),
                           desc="Stage 6 " + v.lower() +
                                " normalized lift (AP-p)/(1-p)")

        # 5) Round-3: the ECOD scoring batch behind every ECOD number in the
        #    paper. PyOD's ECOD.decision_function concatenates the stored
        #    training matrix with the batch it is given before recomputing the
        #    column ECDFs, so a score depends on which OTHER records shared the
        #    call. That makes "which batch was this scored in" part of the
        #    number's definition, and it therefore has to be manifested rather
        #    than asserted in prose. Every ECOD number in this paper comes from
        #    one of three code paths, each of which scores np.vstack([Xva,Xte]):
        #    run_construction_contrast.py (CICIDS and LITNET arms),
        #    run_prevalence_sweep.py (the sweep), and run_review_analyses.py
        #    (A1/A2/A4, which emit their own batch sizes in their own run).
        #    The sizes below are derived from archived row counts and the fixed
        #    70/15/15 split rule, and each derivation is asserted against a
        #    value the archive independently recorded.
        TRAIN_F, VAL_F = 0.70, 0.15

        def split_sizes(n: int) -> tuple[int, int]:
            i_tr = int(TRAIN_F * n)
            i_va = i_tr + int(VAL_F * n)
            return n - i_tr, n - i_va      # (scoring batch, test rows)

        cic_n = int(comp["macros"]["CicidsArmRows"]["value"])
        cic_batch, cic_test = split_sizes(cic_n)
        assert cic_test == int(comp["macros"]["CicidsHeldoutSize"]["value"]), \
            "derived CICIDS test size disagrees with the archived held-out size"
        run.emit_macro("CicidsEcodScoringBatch", cic_batch,
                       desc="records in the single decision_function call that "
                            "produced every CICIDS arm's ECOD scores "
                            "(validation+test, scored together)")

        # two stage1 manifests exist (a superseded 18 Aug run and the 19 Aug
        # one the macro index resolves); pin the one numbers.tex actually cites
        stream_path, stream = load("stage1_natural_streams_20260819T062728_")
        run.declared_inputs.append(str(stream_path))
        lit_n = int(stream["macros"]["StreamLitnetSpamRows"]["value"])
        lit_batch, lit_test = split_sizes(lit_n)
        assert lit_test * 3 == split_sizes(3 * lit_n)[1], \
            "pooled and per-capture test sizes are not consistent"
        run.emit_macro("LitnetCaptureEcodScoringBatch", lit_batch,
                       desc="records per decision_function call for each "
                            "per-capture LITNET ECOD score")
        run.emit_macro("LitnetPooledEcodScoringBatch", split_sizes(3 * lit_n)[0],
                       desc="records in the decision_function call that "
                            "produced the pooled LITNET ECOD score")

        # the sweep: batch derived per level from the archived CSV, and the
        # derivation checked against the n_test the CSV itself recorded.
        import csv as _csv
        sweep_csv = ROOT / "results" / "prevalence_sweep_cicids.csv"
        run.declared_inputs.append(str(sweep_csv))
        batches = set()
        with sweep_csv.open(encoding="utf-8", newline="") as fh:
            for row in _csv.DictReader(fh):
                if row.get("method") != "ecod_batch_ref":
                    continue
                nb, nt = split_sizes(int(row["n_flows"]))
                assert nt == int(row["n_test"]), (
                    "sweep batch derivation failed at level "
                    + str(row.get("level_target_pct")))
                batches.add(nb)
        assert batches, "no ECOD rows found in the prevalence sweep CSV"
        run.emit_macro("SweepEcodScoringBatchMin", min(batches),
                       desc="smallest ECOD scoring batch across the prevalence "
                            "sweep levels")
        run.emit_macro("SweepEcodScoringBatchMax", max(batches),
                       desc="largest ECOD scoring batch across the prevalence "
                            "sweep levels")
        run.note("ecod_batch_paths",
                 "every ECOD number in the paper is produced by a call of the "
                 "form run_batch_reference('ecod', Xfit, np.vstack([Xva, Xte])) "
                 "except the review analyses, which state their own batch")

        # 6) Round-3: the last derived values the literal scan found typed into
        #    ledger-cited findings files. Each is an exact arithmetic
        #    consequence of macros already archived; none needs new compute.
        for v in ("Original", "Corrected"):
            run.emit_macro("SSix" + v + "Lift",
                           round(reported(am["SSix" + v + "Aucpr"]["value"])
                                 - reported(s6floor), 6),
                           desc="Stage 6 " + v.lower() + " additive lift above "
                                "the chance floor")
        # LITNET pooling identity: the validation boundary of the pooled stream
        # and the per-capture held-out size whose triple it equals.
        pooled_rows = 3 * lit_n
        run.emit_macro("LitnetPooledValBoundary", int(TRAIN_F * pooled_rows)
                       + int(VAL_F * pooled_rows),
                       desc="row index where the pooled LITNET stream's held-out "
                            "slice begins")
        run.emit_macro("LitnetCaptureHeldoutRows", lit_test,
                       desc="held-out rows per LITNET capture; three of these "
                            "tile the pooled held-out slice exactly")
        run.emit_macro("LitnetCaptureValBoundary",
                       int(TRAIN_F * lit_n) + int(VAL_F * lit_n),
                       desc="row index where each LITNET capture's held-out "
                            "slice begins; three of these sum to the pooled "
                            "boundary")
        # A4's batch ladder pads. Constants in run_review_analyses.py, pinned by
        # the git commit its manifest records; parsed and asserted rather than
        # retyped, the same treatment SSixDiagWindowRows gets.
        a4src = (ROOT / "scripts/run_review_analyses.py").read_text(encoding="utf-8")
        m4 = re.search(r"pads = \[0, (\d+), (\d+), len\(Xva_n\)\]", a4src)
        assert m4, "A4 batch ladder pads not found in the analysis script"
        for i, pad in enumerate((int(m4.group(1)), int(m4.group(2))), start=1):
            run.emit_macro("RevEcodBatchLadder%d" % i, cic_test + pad,
                           desc="intermediate scoring batch %d of the ECOD "
                                "batch-size ladder" % i)
        assert 3 * lit_test == pooled_rows - (int(TRAIN_F * pooled_rows)
                                              + int(VAL_F * pooled_rows)), \
            "the pooling identity does not hold at these budgets"
        # the unresampled-level LOF/detector gap quoted in findings_prevalence
        with sweep_csv.open(encoding="utf-8", newline="") as fh:
            unres = {}
            for row in _csv.DictReader(fh):
                # 22.06 is the UNRESAMPLED level of the interleaved sweep; the
                # CSV's legacy "is_natural" column flags "not resampled", not
                # timestamp order, and is True only on these rows.
                if float(row["level_target_pct"]) != 22.06:
                    continue
                unres.setdefault(row["method"], []).append(float(row["auc_pr"]))
        if "lof_batch_ref" in unres and "bocpd_slo" in unres:
            lof_v = sum(unres["lof_batch_ref"]) / len(unres["lof_batch_ref"])
            det_v = sum(unres["bocpd_slo"]) / len(unres["bocpd_slo"])
            run.emit_macro("SweepUnresampledLofMinusDetector",
                           round(lof_v - det_v, 6),
                           desc="LOF minus proposed-detector AUC-PR at the "
                                "unresampled sweep level (both deterministic there)")

        print("emitted 5 supplementary macros")
        print("  CICIDS ECOD batch        :", cic_batch)
        print("  LITNET per-capture batch :", lit_batch)
        print("  LITNET pooled batch      :", split_sizes(3 * lit_n)[0])
        print("  sweep batch range        :", min(batches), "-", max(batches))
        print("  attack-free held-out rows:", attack_free)
        print("  Friday held-out density  : %.3f%%" % density)
        print("  |HST natural lift|       :", abs(float(hst_lift)))
        print("  |prevalence shift|       :", abs(float(shift)))
        print("  diag window rows         :", window)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
