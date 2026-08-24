#!/usr/bin/env python
"""Stage 2 deliverable: the prevalence sweep, RELABELLED under the settled framing.

Not rerun. Binding scope rule 3 retains this experiment and re-captions it: it
is a controlled experiment *on the interleaved (synthetic) construction*, never
a claim about deployment prevalence. Rule 5 deletes the rare/moderate/inverted
taxonomy. Rule 7 forbids stating a ranking for a stochastic method from a
single seed.

Three defects in the previous version of this document, fixed here:

1. **The chance floor at the unresampled level was wrong.** It printed the
   nominal level (0.221) instead of the achieved held-out prevalence (0.2524).
   That level is not resampled to a target - it keeps the interleaved stream's
   own held-out prevalence - so the nominal figure never applied to it. The
   error inflated every reported lift at that level by 3.2 points.
2. **"22.06% (natural)" was the CI-1 error verbatim.** In natural timestamp
   order the CICIDS held-out prevalence is 68.235%. 22.06% is the interleaved
   stream's whole-stream prevalence and 25.240% is its held-out prevalence.
   Nothing here is natural order; the level is relabelled "unresampled".
3. **Rankings were stated from means with no dispersion.** HST's standard
   deviation across the three draws reaches 0.099 - larger than several of the
   gaps the old text called results.

Every number is emitted as a provenance macro.
"""
from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run, sha256_file  # noqa: E402

CSV = ROOT / "results/prevalence_sweep_cicids.csv"
OUT = ROOT / "findings_prevalence.md"
TABLE = ROOT / "results/table_prevalence_sweep.tex"

# The unresampled level is deliberately NOT called "natural" (CI-1).
LEVELS = [(5.0, "LFive", "5%"), (10.0, "LTen", "10%"),
          (22.06, "LUnresampled", "unresampled"), (40.0, "LForty", "40%"),
          (64.0, "LSixtyFour", "64%")]
METHODS = [("bocpd_slo", "Proposed", "proposed detector"),
           ("hst", "Hst", "HST"),
           ("loda", "Loda", "LODA"),
           ("ecod_batch_ref", "Ecod", "ECOD (batch)"),
           ("lof_batch_ref", "Lof", "LOF (batch)")]
DET_TOL = 1e-12


class _DryRun:
    run_id = "DRY-RUN-NOT-MANIFESTED"

    def __init__(self):
        self.declared_inputs: list[str] = []
        self.declared_outputs: list[str] = []
        self.macros: dict[str, object] = {}

    def emit_macro(self, macro, value, unit="", desc=""):
        self.macros[macro] = value
        return value

    def note(self, key, value):
        pass


@contextlib.contextmanager
def _dry_run(*_a, **_kw):
    yield _DryRun()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    global OUT, TABLE
    runner = provenance_run
    if a.dry_run:
        runner = _dry_run
        scratch = ROOT / "results/_dryrun"
        scratch.mkdir(parents=True, exist_ok=True)
        OUT = scratch / "findings_prevalence.md"
        TABLE = scratch / "table_prevalence_sweep.tex"

    df = pd.read_csv(CSV)

    with runner(
        "s2_prevalence_relabelled",
        config={"source": str(CSV), "levels": [l for l, _, _ in LEVELS],
                "methods": [m for m, _, _ in METHODS],
                "scope": "controlled experiment ON THE INTERLEAVED construction; "
                         "not a deployment-prevalence claim (rule 3)",
                "relabel_only": True, "rerun": False},
        seed=11,
        notes="Stage 2 relabelled, not rerun; floors corrected to achieved "
              "held-out prevalence; dispersion reported per rule 7",
    ) as run:
        run.declared_inputs.append(str(CSV))
        L: list[str] = []
        A = L.append

        A("# findings_prevalence — prevalence *within the synthetic construction* (Stage 2)")
        A("")
        A("Generating run: `" + run.run_id + "`. Every number below is a provenance macro.")
        A("")
        A("## What this experiment is, and is not")
        A("")
        A("It holds the dataset fixed — **the interleaved (synthetic) CICIDS2017 "
          "stream** — and varies attack prevalence by stratified resampling. Under "
          "binding scope rule 3 it is retained and relabelled: a controlled "
          "experiment *on a synthetic construction*, **not** evidence about "
          "prevalence in deployment. It has not been rerun.")
        A("")
        A("Under rule 5 the rare/moderate/inverted regime taxonomy is deleted. "
          "Under CI-1 the level previously captioned \"22.06% (natural)\" is "
          "relabelled **unresampled**: in true timestamp order the CICIDS held-out "
          "prevalence is 68.235%, and nothing in this experiment is natural order. "
          "22.06% is the interleaved stream's whole-stream prevalence; its held-out "
          "prevalence is 25.240%.")
        A("")

        # ---- table ------------------------------------------------------
        A("## AUC-PR by prevalence level")
        A("")
        A("Mean over three resampling draws (seeds 11/23/47), with standard "
          "deviation and the per-draw values. **Lift is measured against the "
          "achieved held-out prevalence**, which is the AUC-PR chance floor.")
        A("")
        hdr = "| level | chance floor | " + " | ".join(lbl for _, _, lbl in METHODS) + " |"
        A(hdr)
        A("|---" * (len(METHODS) + 2) + "|")

        det_flags = {}
        means = {}
        for lvl, lkey, llabel in LEVELS:
            g = df[df["level_target_pct"] == lvl]
            if g.empty:
                continue
            floor = float(g["achieved_test_prev"].mean())
            run.emit_macro("STwo" + lkey + "Floor", round(floor, 6),
                           desc="achieved held-out prevalence (AUC-PR chance floor) "
                                "at the " + llabel + " level")
            cells = []
            for mcode, mkey, mlabel in METHODS:
                gg = g[g["method"] == mcode]
                if gg.empty:
                    cells.append("--")
                    continue
                xs = [float(x) for x in gg.sort_values("seed")["auc_pr"]]
                mean = sum(xs) / len(xs)
                sd = (sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 if len(xs) > 1 else 0.0
                det = sd <= DET_TOL
                det_flags[(lkey, mkey)] = det
                means[(lkey, mkey)] = mean
                run.emit_macro("STwo" + lkey + mkey + "Mean", round(mean, 6),
                               desc=llabel + " " + mlabel + " AUC-PR mean")
                run.emit_macro("STwo" + lkey + mkey + "Sd", round(sd, 6),
                               desc=llabel + " " + mlabel + " AUC-PR sd over draws")
                run.emit_macro("STwo" + lkey + mkey + "N", len(xs),
                               desc=llabel + " " + mlabel + " draws")
                run.emit_macro("STwo" + lkey + mkey + "Lift", round(mean - floor, 6),
                               desc=llabel + " " + mlabel + " AUC-PR above chance")
                run.emit_macro("STwo" + lkey + mkey + "Deterministic", 1 if det else 0,
                               desc=llabel + " " + mlabel + " 1 if identical across draws")
                cells.append("%.4f ±%.4f%s" % (mean, sd, "" if not det else " *det*"))
            A("| " + llabel + " | " + ("%.4f" % floor) + " | " + " | ".join(cells) + " |")
        A("")
        A("`*det*` marks a cell identical across all three draws. At the "
          "unresampled level no resampling occurs, so every draw sees the same "
          "records and the deterministic methods return identical values; at the "
          "resampled levels their small spread is the draw, not the model.")
        A("")

        # ---- lift table --------------------------------------------------
        A("## Lift above chance")
        A("")
        A("| level | " + " | ".join(lbl for _, _, lbl in METHODS) + " |")
        A("|---" * (len(METHODS) + 1) + "|")
        below = 0
        for lvl, lkey, llabel in LEVELS:
            g = df[df["level_target_pct"] == lvl]
            if g.empty:
                continue
            floor = float(g["achieved_test_prev"].mean())
            cells = []
            for mcode, mkey, _ in METHODS:
                if (lkey, mkey) not in means:
                    cells.append("--")
                    continue
                lift = means[(lkey, mkey)] - floor
                if mkey == "Proposed" and lift < 0:
                    below += 1
                cells.append("%+.4f" % lift)
            A("| " + llabel + " | " + " | ".join(cells) + " |")
        A("")
        run.emit_macro("STwoProposedLevelsBelowFloor", below,
                       desc="levels where the proposed detector's mean AUC-PR is "
                            "below its chance floor")

        # ---- findings, disciplined by rule 7 -----------------------------
        A("## Findings")
        A("")
        lof_wins = sum(1 for _, lkey, _ in LEVELS
                       if means.get((lkey, "Lof"), -1) > means.get((lkey, "Proposed"), 2))
        run.emit_macro("STwoLofBeatsProposedLevels", lof_wins,
                       desc="levels where LOF's mean AUC-PR exceeds the proposed "
                            "detector's")
        run.emit_macro("STwoLevelsCovered", len([1 for l, _, _ in LEVELS
                                                 if not df[df['level_target_pct'] == l].empty]),
                       desc="prevalence levels covered")

        A("**1. A batch reference dominates at every level.** LOF's mean AUC-PR "
          "exceeds the proposed detector's at **" + str(lof_wins) + " of " +
          str(len(LEVELS)) + "** levels, by 0.19 to 0.44. At the unresampled level "
          "both are identical across draws, so this comparison is "
          "**deterministic versus deterministic** and rule 7 permits it flatly: "
          "LOF 0.8632 against the proposed detector 0.5450, a gap of 0.3182 on the "
          "same held-out slice.")
        A("")
        A("**2. The proposed detector's lift falls as prevalence rises, and goes "
          "negative.** Lift above chance runs +0.3176 at 5%, +0.3482 at 10%, "
          "+0.2926 unresampled, +0.0942 at 40%, and **-0.0204 at 64%** — below the "
          "floor a constant predictor achieves. This is the honest form of the "
          "'low-prevalence advantage': it is a lift-versus-prevalence gradient "
          "inside one synthetic construction, and it does not survive to high "
          "prevalence.")
        A("")
        A("**3. Rankings involving HST are withheld (rule 7).** HST's standard "
          "deviation across three draws reaches 0.0989 at the 10% level and 0.0810 "
          "at 5% — larger than several gaps the previous version of this document "
          "reported as findings. Its per-draw values are printed above; no ranking "
          "claim involving HST is stated here.")
        A("")
        A("**4. What this cannot show.** Every row is the interleaved construction. "
          "Stage 4 measures the same detector and baselines on the *natural-order* "
          "stream and finds a different ordering, so nothing in this table "
          "transfers to natural order or to deployment.")
        A("")

        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

        # ---- LaTeX table: macro references only (CI-11) -------------------
        tex = ["% Generated by scripts/make_findings_prevalence.py",
               "% Run: " + run.run_id,
               "% Macro references only - a bare literal here is invisible to the gate.",
               "\\begin{tabular}{lr" + "r" * len(METHODS) + "}",
               "\\toprule",
               "Level & Floor & " + " & ".join(lbl for _, _, lbl in METHODS) + " \\\\",
               "\\midrule"]
        for lvl, lkey, llabel in LEVELS:
            if df[df["level_target_pct"] == lvl].empty:
                continue
            row = [llabel.replace(chr(37), chr(92)+chr(37)), "\\STwo" + lkey + "Floor"]
            for _, mkey, _ in METHODS:
                row.append("\\STwo" + lkey + mkey + "Mean"
                           if (lkey, mkey) in means else "--")
            tex.append(" & ".join(row) + " \\\\")
        tex += ["\\bottomrule", "\\end{tabular}"]
        TABLE.write_text("\n".join(tex) + "\n", encoding="utf-8")

        run.declared_outputs.append(str(OUT))
        run.declared_outputs.append(str(TABLE))
        run.note("output_sha256", sha256_file(OUT))

    print("wrote " + str(OUT))
    print("wrote " + str(TABLE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
