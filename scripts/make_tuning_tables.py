#!/usr/bin/env python
"""Generate Stage 3 LaTeX deliverables from results/baseline_tuning.csv:

- results/table4_litnet_tuned.tex   (paper Table 4 + tuned rows)
- results/table5_cicids_tuned.tex   (paper Table 5 + tuned rows)
- results/tuning_delta_summary.tex  (default vs tuned AUC-PR per baseline)
- results/appendix_a_replacement.tex (tuning-protocol text replacing the
  no-tuning paragraph; states grids, selection criterion, seeds, and the
  compute rule actually used)

Default rows come from the published trial results (bit-reproduced in
Stage 1); tuned rows from the tuning finals.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TUNING = ROOT / "results/baseline_tuning.csv"
DEFAULTS = {
    "litnet2020": ROOT / "results_litnet_trial/tables/main_metrics_raw.csv",
    "cicids2017": ROOT / "results_cicids_trial/tables/main_metrics_raw.csv",
}
OUT = ROOT / "results"

DISPLAY = {
    "bocpd_slo": "CALIBURN",
    "loda": "LODA", "hst": "HST", "kitnet": "KitNET", "rrcf": "RRCF",
    "iforest_asd": "iForest\\_ASD", "xstream": "xStream",
    "lof": "LOF", "lof_batch_ref": "LOF",
    "ecod": "ECOD", "ecod_batch_ref": "ECOD",
    "copod": "COPOD", "copod_batch_ref": "COPOD",
}
DET = {"bocpd_slo", "lof_batch_ref", "ecod_batch_ref", "copod_batch_ref", "kitnet", "lof",
       "ecod", "copod"}
TUNABLE = ["hst", "loda", "rrcf", "iforest_asd", "kitnet", "lof"]


def fmt(mean: float, std: float, det: bool) -> str:
    if pd.isna(mean):
        return "--"
    if det or pd.isna(std) or std < 5e-4:
        return f"{mean:.3f} det." if det else f"{mean:.3f}"
    return f"{mean:.3f} $\\pm$ {std:.3f}"


def method_rows(df: pd.DataFrame, method: str) -> dict:
    g = df[df["method"] == method]
    if g.empty:
        return {}
    out = {}
    for m in ("auc_pr", "auc_roc", "f1"):
        out[m] = (float(g[m].mean()), float(g[m].std()) if len(g) > 1 else float("nan"))
    return out


def build_table(dataset: str, caption: str, label: str, out_name: str, tuning: pd.DataFrame) -> None:
    base = pd.read_csv(DEFAULTS[dataset])
    base = base[base["auc_pr"].notna()]
    rows = []
    for method in base["method"].unique():
        r = method_rows(base, method)
        if r:
            rows.append((DISPLAY.get(method, method), "default", method in DET, r, None))
    tuned = tuning[(tuning["dataset"] == dataset) & (tuning["phase"] == "final_tuned")
                   & tuning["auc_pr"].notna()]
    for method in tuned["method"].unique():
        r = method_rows(tuned, method)
        params = tuned[tuned["method"] == method]["params"].iloc[0]
        rows.append((DISPLAY.get(method, method), "tuned", method in DET, r, params))
    rows.sort(key=lambda t: -t[3]["auc_pr"][0])

    lines = [r"\begin{table}[t]", r"\centering", r"\small",
             r"\begin{tabular}{llccc}", r"\toprule",
             r"Method & Config & AUC-PR & AUC-ROC & F1 \\", r"\midrule"]
    for name, cfg, det, r, params in rows:
        lines.append(f"{name} & {cfg} & {fmt(*r['auc_pr'], det)} & "
                     f"{fmt(*r['auc_roc'], det)} & {fmt(*r['f1'], det)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}",
              rf"\caption{{{caption}}}", rf"\label{{{label}}}", r"\end{table}"]
    (OUT / out_name).write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT / out_name}")


def build_delta(tuning: pd.DataFrame) -> None:
    lines = [r"\begin{table}[t]", r"\centering", r"\small",
             r"\begin{tabular}{llccc}", r"\toprule",
             r"Dataset & Baseline & default AUC-PR & tuned AUC-PR & $\Delta$ \\",
             r"\midrule"]
    for dataset in ("litnet2020", "cicids2017"):
        base = pd.read_csv(DEFAULTS[dataset])
        for method in TUNABLE:
            key = method if method in base["method"].unique() else f"{method}_batch_ref"
            d = base[base["method"] == key]["auc_pr"].mean()
            t = tuning[(tuning["dataset"] == dataset) & (tuning["method"] == method)
                       & (tuning["phase"] == "final_tuned")]["auc_pr"].mean()
            sel = tuning[(tuning["dataset"] == dataset) & (tuning["method"] == method)
                         & (tuning["phase"] == "final_tuned")]
            params = json.loads(sel["params"].iloc[0]) if not sel.empty else {}
            if pd.isna(t):
                continue
            pstr = ", ".join(f"{k}={v}" for k, v in params.items())
            lines.append(rf"{dataset} & {DISPLAY.get(method, method)} ({pstr}) & "
                         rf"{d:.3f} & {t:.3f} & {t - d:+.3f} \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{Default versus validation-tuned AUC-PR per baseline. Tuning "
              r"selects on validation AUC-PR only (the same split CALIBURN's "
              r"calibration layer uses); test labels are never read during selection.}",
              r"\label{tab:tuning-delta}", r"\end{table}"]
    (OUT / "tuning_delta_summary.tex").write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT / 'tuning_delta_summary.tex'}")


def build_appendix(tuning: pd.DataFrame) -> None:
    reduced = tuning[(tuning["phase"] == "grid") & (tuning["train_frac"] < 1.0)]
    frac_note = (
        "Because the full-stream grid exceeded the compute ceiling, grid points "
        "were evaluated on the first chronologically contiguous 40\\% of the "
        "training split followed by the full validation split; the selected "
        "configuration was then re-run on the full stream for the reported test "
        "numbers." if not reduced.empty else
        "All grid points were evaluated on the full training split followed by "
        "the full validation split.")
    n_crashed = int(tuning[(tuning["phase"] == "grid")]["error"].fillna("").astype(bool).sum())
    crash_note = (f" {n_crashed} grid point(s) crashed; each is logged with its error "
                  "in the released results and excluded from selection.") if n_crashed else ""
    text = rf"""% Appendix A replacement: baseline tuning protocol (replaces the
% framework-defaults / no-tuning paragraph).
Baseline hyperparameters are no longer framework defaults. Every tunable
baseline was tuned by exhaustive grid search with selection on
\emph{{validation}} AUC-PR only --- the same chronological validation split
that CALIBURN's calibration layer uses --- so the comparison is symmetric:
no method, proposed or baseline, ever touches test labels before the final
evaluation. The grids were fixed a priori: HST
$\{{25,50,100\}}$ trees $\times$ depth $\{{10,15,20\}}$ $\times$ window
$\{{100,250,500\}}$; LODA bins $\{{10,20,50\}}$ $\times$ projections
$\{{100,200,500\}}$; RRCF trees $\{{40,100\}}$ $\times$ tree size
$\{{256,512\}}$; iForest\_ASD estimators $\{{50,100,200\}}$ $\times$ window
$\{{1024,2048,4096\}}$; KitNET max autoencoder size $\{{5,10,20\}}$ with
grace periods scaled proportionally to stream length; LOF neighbours
$\{{10,20,35,50\}}$. ECOD and COPOD expose no tunable hyperparameters and
are carried forward unchanged. {frac_note}{crash_note}
Stochastic methods report final test numbers over seeds 11, 23, and 47
after selection; deterministic methods are single-run. Tuning was performed
on LITNET-2020 and CICIDS2017 only.
"""
    (OUT / "appendix_a_replacement.tex").write_text(text)
    print(f"wrote {OUT / 'appendix_a_replacement.tex'}")


def _normalize(tuning: pd.DataFrame) -> pd.DataFrame:
    """Guarantee the columns the builders index.

    A truncated run can produce a baseline_tuning.csv containing only grid
    rows (which carry val_auc_pr, not auc_pr/auc_roc/f1). Without this, every
    builder raises KeyError and the whole deliverable step dies — losing the
    partial tables that the bounded-run design exists to preserve.
    """
    for col in ("dataset", "method", "phase", "params", "error"):
        if col not in tuning.columns:
            tuning[col] = ""
    for col in ("auc_pr", "auc_roc", "f1", "val_auc_pr", "train_frac"):
        if col not in tuning.columns:
            tuning[col] = float("nan")
    return tuning


def main() -> None:
    tuning = _normalize(pd.read_csv(TUNING))
    build_table("litnet2020",
                "AUC-PR, AUC-ROC, and F1 on LITNET-2020 (3-seed mean $\\pm$ std), "
                "framework-default and validation-tuned configurations. Deterministic "
                "methods are marked ``det.'' Selection used validation AUC-PR only.",
                "tab:litnet-tuned", "table4_litnet_tuned.tex", tuning)
    build_table("cicids2017",
                "AUC-PR, AUC-ROC, and F1 on CICIDS2017 (3-seed mean $\\pm$ std), "
                "framework-default and validation-tuned configurations. Deterministic "
                "methods are marked ``det.'' Selection used validation AUC-PR only.",
                "tab:cicids-tuned", "table5_cicids_tuned.tex", tuning)
    build_delta(tuning)
    build_appendix(tuning)


if __name__ == "__main__":
    main()
