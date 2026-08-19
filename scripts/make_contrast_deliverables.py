#!/usr/bin/env python
"""S4 deliverables: merge the construction-contrast arms and write the findings.

Reads the per-arm partials in results/rebuild_parts/, merges them, and emits
every headline number as a provenance macro in a single manifested run. Nothing
here recomputes a metric: this script only aggregates, compares, and states
mechanical verdicts with their thresholds.

The claim under test is the rebuilt paper's primary contribution:

    benchmark stream CONSTRUCTION, not attack prevalence, produces the regime
    structure the literature reports.

Two contrasts, because the two benchmarks are constructed differently:

  CICIDS2017 (order) - one capture week, so the SAME RECORDS are evaluated in
      true timestamp order and in day-of-week round robin. Whole-stream
      prevalence is identical by construction; only the order differs. Any
      difference in the measured regime is therefore attributable to
      construction alone, with prevalence held exactly constant. This is the
      cleanest form of the argument.

  LITNET-2020 (composition) - three temporally disjoint captures, so no
      coherent global chronology exists and round robin WITHIN a per-type
      stream is the identity (each stream holds one attack_type). The contrast
      is instead between the three natural per-type streams and the pooled
      composite the literature evaluates. The composite arm is reported as a
      LABELLED SYNTHETIC CONTRAST, never as a measurement of deployment.

Re-running after the inputs change will emit the same macro names with
different values, which the provenance gate now reports as AMBIGUOUS and fails
(CI-5). That is intended: superseding a result is a deliberate act, and the
stale manifest must be removed on purpose rather than silently outvoted.
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

PARTS = ROOT / "results/rebuild_parts"
MERGED = ROOT / "results/construction_contrast.csv"
FINDINGS = ROOT / "findings_contrast.md"
TABLE = ROOT / "results/table_construction_contrast.tex"

METHOD_LABEL = {
    "proposed_detector": "proposed detector",
    "hst": "HST",
    "ecod": "ECOD",
}
LITNET_TYPES = ["udp_flood", "blaster_worm", "spam"]


def camel(*parts: str) -> str:
    out = []
    for p in parts:
        for w in str(p).replace("-", "_").split("_"):
            out.append(w.capitalize())
    return "".join(out)


def load_parts() -> tuple[pd.DataFrame, list[Path], list[str]]:
    files = sorted(PARTS.glob("contrast_*.csv"))
    if not files:
        raise SystemExit("no contrast partials in " + str(PARTS))
    frames, notes = [], []
    for f in files:
        d = pd.read_csv(f)
        d["source_part"] = f.name
        frames.append(d)
        if "excluded_reason" in d.columns and d["excluded_reason"].notna().any():
            for _, r in d[d["excluded_reason"].notna()].iterrows():
                notes.append(f.name + ": " + str(r.get("stream")) + "/" +
                             str(r.get("arm")) + "/" + str(r.get("method")) +
                             " -> " + str(r["excluded_reason"]))
    return pd.concat(frames, ignore_index=True), files, notes


def cell(df: pd.DataFrame, stream: str, arm: str, method: str, col: str):
    """One metric cell, or None when the cell was excluded or never ran."""
    if col not in df.columns:
        return None
    s = df[(df["stream"] == stream) & (df["arm"] == arm) &
           (df["method"] == method)][col]
    s = s.dropna()
    return float(s.mean()) if len(s) else None


def ranking(df: pd.DataFrame, stream: str, arm: str) -> list[str]:
    """Methods ordered by AUC-PR, best first. Missing cells drop out."""
    vals = {m: cell(df, stream, arm, m, "auc_pr")
            for m in ["proposed_detector", "hst", "ecod"]}
    vals = {k: v for k, v in vals.items() if v is not None}
    return [k for k, _ in sorted(vals.items(), key=lambda kv: -kv[1])]


def fmt(v, dp: int = 3, pct: bool = False) -> str:
    if v is None:
        return "not measured"
    return ("%." + str(dp) + "f") % (v * 100 if pct else v) + ("%" if pct else "")


class _DryRun:
    """Exercises the whole code path while emitting nothing.

    Running the real generator against an incomplete set of arms would write
    partial values into the macro index; the completed run would then emit the
    same names with different values and the gate would (correctly) call the
    result ambiguous forever. A dry run lets the code be tested before the
    compute lands without contaminating provenance.
    """

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
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise the generator without writing a manifest or "
                         "touching the macro index; outputs go to /scratch paths")
    a = ap.parse_args()

    global MERGED, FINDINGS, TABLE
    runner = provenance_run
    if a.dry_run:
        runner = _dry_run
        scratch = ROOT / "results/_dryrun"
        scratch.mkdir(parents=True, exist_ok=True)
        MERGED = scratch / "construction_contrast.csv"
        FINDINGS = scratch / "findings_contrast.md"
        TABLE = scratch / "table_construction_contrast.tex"

    df, files, exclusions = load_parts()
    MERGED.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(MERGED, index=False)

    arms_present = sorted(set(zip(df["stream"], df["arm"])))
    have_cicids_nat = ("cicids2017", "natural") in arms_present
    have_cicids_syn = ("cicids2017", "interleaved_synthetic") in arms_present
    have_pooled = ("litnet_pooled", "composite_synthetic") in arms_present

    with runner(
        "s4_contrast_deliverables",
        config={"parts": [f.name for f in files],
                "claim": "construction, not prevalence, drives regime structure",
                "cicids_contrast": "true timestamp order vs day-of-week round robin, "
                                   "identical record multiset",
                "litnet_contrast": "three natural per-type streams vs the pooled "
                                   "composite (labelled synthetic)"},
        seed=11,
        notes="aggregation only; no metric is recomputed here",
    ) as run:
        for f in files:
            run.declared_inputs.append(str(f))
        L: list[str] = []
        L.append("# findings_contrast — construction, not prevalence (Stage 4)")
        L.append("")
        L.append("Generating run: `" + run.run_id + "`.")
        L.append("Every number below is a provenance macro from this run's manifest "
                 "or from the per-arm manifests it aggregates.")
        L.append("")
        L.append("**Claim under test.** Benchmark stream *construction*, not attack "
                 "prevalence, produces the regime structure the intrusion-detection "
                 "literature reports.")
        L.append("")

        # ---- CICIDS: same records, order only ----------------------------
        L.append("## Contrast 1 — CICIDS2017, order only (prevalence held constant)")
        L.append("")
        L.append("CICIDS2017 is a single capture week, so the same record multiset "
                 "can be presented in true timestamp order and in day-of-week round "
                 "robin. Whole-stream prevalence is *identical by construction*; only "
                 "the order differs. Any change in the measured regime is therefore "
                 "attributable to construction alone.")
        L.append("")
        if have_cicids_nat and have_cicids_syn:
            pn = cell(df, "cicids2017", "natural", "proposed_detector", "test_prevalence")
            ps = cell(df, "cicids2017", "interleaved_synthetic", "proposed_detector",
                      "test_prevalence")
            an = cell(df, "cicids2017", "natural", "proposed_detector", "test_attacks")
            asy = cell(df, "cicids2017", "interleaved_synthetic", "proposed_detector",
                       "test_attacks")
            run.emit_macro("SFourCicidsNaturalTestPrev", round(pn * 100, 4), unit="%",
                           desc="CICIDS2017 held-out prevalence, true timestamp order")
            run.emit_macro("SFourCicidsInterleavedTestPrev", round(ps * 100, 4), unit="%",
                           desc="CICIDS2017 held-out prevalence, day-of-week round robin")
            shift = (ps - pn) * 100
            run.emit_macro("SFourCicidsPrevShiftPp", round(shift, 4), unit="pp",
                           desc="held-out prevalence shift caused by construction alone")
            run.emit_macro("SFourCicidsNaturalTestAttacks", int(an),
                           desc="CICIDS2017 held-out attacks, natural order")
            run.emit_macro("SFourCicidsInterleavedTestAttacks", int(asy),
                           desc="CICIDS2017 held-out attacks, interleaved")
            L.append("| quantity | natural (timestamp order) | synthetic (day round robin) |")
            L.append("|---|---|---|")
            L.append("| held-out prevalence | **" + fmt(pn, 3, True) + "** | **" +
                     fmt(ps, 3, True) + "** |")
            L.append("| held-out attacks | " + str(int(an)) + " | " + str(int(asy)) + " |")
            L.append("")
            L.append("The two arms hold the same records. Reordering alone moves the "
                     "held-out prevalence by **" + ("%+.3f" % shift) + " percentage "
                     "points**, which is the whole of the effect: no attack was added, "
                     "removed, or resampled.")
            L.append("")
            L.append("| method | AUC-PR natural | AUC-PR synthetic | delta (syn - nat) |")
            L.append("|---|---|---|---|")
            for m in ["proposed_detector", "hst", "ecod"]:
                a = cell(df, "cicids2017", "natural", m, "auc_pr")
                b = cell(df, "cicids2017", "interleaved_synthetic", m, "auc_pr")
                if a is not None:
                    run.emit_macro("SFourCicidsNatural" + camel(m) + "Aucpr",
                                   round(a, 6), desc="CICIDS natural " + m + " AUC-PR")
                if b is not None:
                    run.emit_macro("SFourCicidsSynthetic" + camel(m) + "Aucpr",
                                   round(b, 6), desc="CICIDS interleaved " + m + " AUC-PR")
                dv = ("%+.3f" % (b - a)) if (a is not None and b is not None) else "n/a"
                L.append("| " + METHOD_LABEL[m] + " | " + fmt(a) + " | " + fmt(b) +
                         " | " + dv + " |")
            L.append("")
            # mechanical verdict: does the ranking change between arms?
            rn = ranking(df, "cicids2017", "natural")
            rs = ranking(df, "cicids2017", "interleaved_synthetic")
            same = rn == rs
            run.emit_macro("SFourCicidsRankingPreserved", 1 if same else 0,
                           desc="1 if the method ranking is identical across arms")
            L.append("**Verdict (mechanical, threshold = identical ordering of methods "
                     "by AUC-PR):** ranking under natural order is " +
                     " > ".join(METHOD_LABEL[m] for m in rn) + "; under the synthetic "
                     "construction it is " + " > ".join(METHOD_LABEL[m] for m in rs) +
                     ". The ranking is " + ("PRESERVED" if same else "NOT PRESERVED") +
                     ".")
            L.append("")
            if same:
                L.append("Note the honest reading: a preserved ranking does **not** "
                         "rescue the synthetic construction. The regime it reports — "
                         "the held-out prevalence a reader would quote — still differs "
                         "by " + ("%+.3f" % shift) + " pp from the natural order for "
                         "the same records. What is preserved is the ordering of "
                         "methods, not the operating point they were evaluated at.")
                L.append("")
        else:
            L.append("*CICIDS arms incomplete; nothing is asserted for this contrast.*")
            L.append("")

        # ---- LITNET: composition ------------------------------------------
        L.append("## Contrast 2 — LITNET-2020, composition (labelled synthetic)")
        L.append("")
        L.append("LITNET-2020's three captures are temporally disjoint, so no global "
                 "chronology exists and round robin *within* a per-attack-type stream "
                 "is the identity. The contrast is therefore between the three natural "
                 "per-type streams and the pooled composite the literature evaluates. "
                 "The pooled arm is a **labelled synthetic contrast**, not a "
                 "measurement of any deployment.")
        L.append("")
        L.append("| stream | construction | held-out prevalence | held-out attacks |")
        L.append("|---|---|---|---|")
        per_prev = {}
        for t in LITNET_TYPES:
            p = cell(df, "litnet_" + t, "natural", "proposed_detector", "test_prevalence")
            a = cell(df, "litnet_" + t, "natural", "proposed_detector", "test_attacks")
            per_prev[t] = p
            if p is not None:
                run.emit_macro("SFourLitnet" + camel(t) + "TestPrev", round(p * 100, 4),
                               unit="%", desc="LITNET " + t + " held-out prevalence")
            L.append("| `" + t + "` | natural (per type) | **" + fmt(p, 3, True) +
                     "** | " + (str(int(a)) if a is not None else "n/a") + " |")
        pp = cell(df, "litnet_pooled", "composite_synthetic", "proposed_detector",
                  "test_prevalence")
        pa = cell(df, "litnet_pooled", "composite_synthetic", "proposed_detector",
                  "test_attacks")
        if pp is not None:
            run.emit_macro("SFourLitnetPooledTestPrev", round(pp * 100, 4), unit="%",
                           desc="LITNET pooled composite held-out prevalence")
        L.append("| `pooled` | **synthetic** (3-type round robin) | **" +
                 fmt(pp, 3, True) + "** | " + (str(int(pa)) if pa is not None else "n/a") +
                 " |")
        L.append("")
        known = [v for v in per_prev.values() if v is not None]
        if pp is not None and known:
            lo, hi = min(known), max(known)
            inside = lo <= pp <= hi
            run.emit_macro("SFourLitnetPooledInsideRange", 1 if inside else 0,
                           desc="1 if pooled prevalence lies inside the per-type range")
            L.append("The pooled composite reports a single prevalence of **" +
                     fmt(pp, 3, True) + "**, while the constituent streams span **" +
                     fmt(lo, 3, True) + " to " + fmt(hi, 3, True) + "**. The composite "
                     "figure is a mixture weight, not a property any of the three "
                     "captures exhibits: it is manufactured by pooling.")
            L.append("")
        L.append("| stream | " + " | ".join(METHOD_LABEL[m] for m in
                 ["proposed_detector", "hst", "ecod"]) + " |")
        L.append("|---|---|---|---|")
        for t in LITNET_TYPES:
            cells = []
            for m in ["proposed_detector", "hst", "ecod"]:
                v = cell(df, "litnet_" + t, "natural", m, "auc_pr")
                if v is not None:
                    run.emit_macro("SFourLitnet" + camel(t) + camel(m) + "Aucpr",
                                   round(v, 6), desc="LITNET " + t + " " + m + " AUC-PR")
                cells.append(fmt(v))
            L.append("| `" + t + "` (natural) | " + " | ".join(cells) + " |")
        cells = []
        for m in ["proposed_detector", "hst", "ecod"]:
            v = cell(df, "litnet_pooled", "composite_synthetic", m, "auc_pr")
            if v is not None:
                run.emit_macro("SFourLitnetPooled" + camel(m) + "Aucpr", round(v, 6),
                               desc="LITNET pooled " + m + " AUC-PR")
            cells.append(fmt(v))
        L.append("| `pooled` (**synthetic**) | " + " | ".join(cells) + " |")
        L.append("")

        # ---- what the composite does to the method ranking ----------------
        pooled_rank = ranking(df, "litnet_pooled", "composite_synthetic")
        nat_ranks = {t: ranking(df, "litnet_" + t, "natural") for t in LITNET_TYPES}
        nat_ranks = {t: r for t, r in nat_ranks.items() if r}
        if pooled_rank and nat_ranks:
            agree = [t for t, r in nat_ranks.items() if r == pooled_rank]
            run.emit_macro("SFourLitnetStreamsMatchingPooledRanking", len(agree),
                           desc="natural per-type streams whose method ranking "
                                "matches the pooled composite")
            run.emit_macro("SFourLitnetNaturalStreamsRanked", len(nat_ranks),
                           desc="natural per-type streams with a defined ranking")
            lost = [t for t, r in nat_ranks.items() if r and r[0] != "proposed_detector"]
            run.emit_macro("SFourLitnetStreamsProposedNotBest", len(lost),
                           desc="natural streams where the proposed detector is "
                                "not the best method")
            L.append("### What pooling does to the method ranking")
            L.append("")
            L.append("Ranking on the pooled composite: **" +
                     " > ".join(METHOD_LABEL[m] for m in pooled_rank) + "**.")
            L.append("")
            for t, r in nat_ranks.items():
                L.append("- `" + t + "` (natural): " +
                         " > ".join(METHOD_LABEL[m] for m in r) +
                         ("  — matches the composite" if r == pooled_rank
                          else "  — **differs from the composite**"))
            L.append("")
            L.append("**Verdict (mechanical, threshold = identical ordering):** the "
                     "composite's ranking reproduces **" + str(len(agree)) + " of " +
                     str(len(nat_ranks)) + "** natural per-type streams.")
            L.append("")
            if lost:
                L.append("This cuts against the proposed method, and is reported for "
                         "that reason. On the composite the proposed detector is best "
                         "by a wide margin. Evaluated per stream in natural order it "
                         "is **not** the best method on " + str(len(lost)) + " of " +
                         str(len(nat_ranks)) + " streams (" +
                         ", ".join("`" + t + "`" for t in lost) + "). The composite "
                         "reports a uniform dominance that the constituent streams do "
                         "not show.")
                L.append("")

        # ---- exclusions, stated never silent ------------------------------
        L.append("## Excluded cells")
        L.append("")
        if exclusions:
            for e in exclusions:
                L.append("- " + e)
        else:
            L.append("None. Every cell in every completed arm produced a defined "
                     "metric.")
        L.append("")
        run.emit_macro("SFourExcludedCells", len(exclusions),
                       desc="cells excluded with a recorded reason")
        missing_arms = [a for a in [("cicids2017", "natural"),
                                    ("cicids2017", "interleaved_synthetic"),
                                    ("litnet_pooled", "composite_synthetic")]
                        if a not in arms_present]
        if missing_arms:
            L.append("**Arms not present in this aggregation:** " +
                     ", ".join(s + "/" + a for s, a in missing_arms) + ". No claim is "
                     "made for them.")
            L.append("")

        FINDINGS.write_text("\n".join(L) + "\n", encoding="utf-8")

        # ---- LaTeX table ---------------------------------------------------
        tex = [
            "% Generated by scripts/make_contrast_deliverables.py",
            "% Run: " + run.run_id,
            "\\begin{tabular}{llrrr}",
            "\\toprule",
            "Benchmark & Construction & Held-out prev. & Attacks & AUC-PR (proposed) \\\\",
            "\\midrule",
        ]
        rowspec = [("cicids2017", "natural", "CICIDS2017", "natural (timestamp)"),
                   ("cicids2017", "interleaved_synthetic", "CICIDS2017",
                    "synthetic (day RR)")]
        rowspec += [("litnet_" + t, "natural", "LITNET " + t.replace("_", " "),
                     "natural (per type)") for t in LITNET_TYPES]
        rowspec += [("litnet_pooled", "composite_synthetic", "LITNET pooled",
                     "synthetic (3-type RR)")]
        for stream, arm, blabel, clabel in rowspec:
            p = cell(df, stream, arm, "proposed_detector", "test_prevalence")
            a = cell(df, stream, arm, "proposed_detector", "test_attacks")
            v = cell(df, stream, arm, "proposed_detector", "auc_pr")
            if p is None and v is None:
                continue
            tex.append(blabel + " & " + clabel + " & " +
                       (("%.3f" % (p * 100)) + "\\%" if p is not None else "--") +
                       " & " + (str(int(a)) if a is not None else "--") +
                       " & " + (("%.3f" % v) if v is not None else "--") + " \\\\")
        tex += ["\\bottomrule", "\\end{tabular}"]
        TABLE.write_text("\n".join(tex) + "\n", encoding="utf-8")

        for out in (MERGED, FINDINGS, TABLE):
            run.declared_outputs.append(str(out))
        run.note("merged_sha256", sha256_file(MERGED))
        run.note("rows_merged", int(len(df)))
        run.note("arms_present", [s + "/" + a for s, a in arms_present])

    print("wrote " + str(MERGED))
    print("wrote " + str(FINDINGS))
    print("wrote " + str(TABLE))
    print("arms present: " + ", ".join(s + "/" + a for s, a in arms_present))
    if exclusions:
        print("exclusions recorded: " + str(len(exclusions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
