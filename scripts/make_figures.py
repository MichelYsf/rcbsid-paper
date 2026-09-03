#!/usr/bin/env python
"""Render the manuscript figures from archived run manifests, deterministically.

Rules this script enforces on itself (SCOPE_DECISIONS rule 12):
  * every plotted value is read from an archived manifest under
    results/manifests/; nothing is typed here, and protocol constants (split
    fractions, per-day budgets) are read from the manifests' config blocks;
  * the style is fixed, the random state is fixed although nothing here is
    stochastic, and no timestamp is written anywhere;
  * PDF metadata carries the paper title only: Author, Creator, Producer,
    Subject, Keywords, CreationDate and ModDate are all removed;
  * no file path, username or handle is written into any figure;
  * tick locators and formatters are library defaults on every numeric axis;
    categorical axes carry their category names, which is the library's own
    behaviour for categorical bars;
  * paper/figures/figure_manifest.json records the generator's own hash, every
    input file with its SHA-256, every output figure with its SHA-256, and
    every value plotted keyed by the macro name it carries in its manifest, so
    that scripts/check_figures.py can prove the figures show the macro layer
    and nothing else.

Run after the manifests are final and before the LaTeX build:
    python scripts/make_figures.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "results" / "manifests"
OUT = ROOT / "paper" / "figures"
MANIFEST = OUT / "figure_manifest.json"

PAPER_TITLE = ("Stream Assembly Is an Uncontrolled Treatment in Streaming "
               "Intrusion-Detection Benchmarks")

INPUTS = {
    "subsample":    MAN / "cicids_subsample_audit_20260819T085704_3ed9b901.json",
    "composition":  MAN / "cicids_heldout_composition_20260819T120420_ebb7c281.json",
    "natural":      MAN / "s4_construction_contrast_20260819T090813_46e9bd32.json",
    "synthetic":    MAN / "s4_construction_contrast_20260819T064027_20f44694.json",
    "deliverables": MAN / "s4_contrast_deliverables_20260827T124050_ec876714.json",
    "review":       MAN / "review_bounded_analyses_20260827T131839_87899899.json",
}

# Okabe-Ito, colourblind-safe.
C = {"orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
     "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00",
     "purple": "#CC79A7", "black": "#000000", "grey": "#7F7F7F"}
DAY_COLOURS = [C["blue"], C["sky"], C["green"], C["yellow"], C["orange"]]

WIDTH_IN = 3.33          # ACM column width
META = {"Title": PAPER_TITLE, "Author": None, "Creator": None,
        "Producer": None, "Subject": None, "Keywords": None,
        "CreationDate": None, "ModDate": None}

# The only constant not read from a manifest: the AUC-ROC of an uninformative
# ranking. It is a definition, not a measurement, and it is recorded in the
# figure manifest under "constants" so the exception is visible.
AUC_ROC_CHANCE = 0.5


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def style() -> None:
    np.random.seed(0)
    plt.rcdefaults()
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8,
        "axes.labelsize": 8, "axes.titlesize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.linewidth": 0.6, "lines.linewidth": 1.0, "lines.markersize": 4,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "pdf.fonttype": 42, "pdf.compression": 6,
        "figure.dpi": 100, "savefig.dpi": 300,
    })


def load(key: str) -> dict:
    return json.loads(INPUTS[key].read_text(encoding="utf-8"))


def macro(man: dict, name: str, used: dict) -> float:
    v = man["macros"][name]["value"]
    used[name] = v
    return v


def save(fig, name: str) -> Path:
    p = OUT / name
    fig.savefig(p, metadata=META)
    plt.close(fig)
    return p


# ---------------------------------------------------------------------------
def fig_assembly(used: dict, protocol: dict) -> Path:
    """Schematic: the same records in timestamp order and in day round robin,
    under one positional split. Protocol constants only."""
    sub = load("subsample")
    comp = load("composition")
    budgets = sub["config"]["per_day_budgets"]           # ordered Mon..Fri
    days = list(budgets.keys())
    sizes = np.array([budgets[d] for d in days], dtype=float)
    n = sizes.sum()
    train = float(comp["config"]["train"])
    val = float(comp["config"]["val"])
    protocol.update({"per_day_budgets": budgets, "train": train, "val": val,
                     "source": [INPUTS["subsample"].name,
                                INPUTS["composition"].name]})

    fig, ax = plt.subplots(figsize=(WIDTH_IN, 1.9))
    bar_h = 0.32
    # top bar: timestamp order is the days concatenated
    x = 0.0
    for i, d in enumerate(days):
        w = sizes[i] / n
        ax.add_patch(plt.Rectangle((x, 1.0), w, bar_h, color=DAY_COLOURS[i],
                                   linewidth=0))
        x += w
    # bottom bar: round robin is lanes of every day still supplying records
    pos, k = 0.0, 0
    for b in sorted(set(sizes.tolist())):
        active = [i for i in range(len(days)) if sizes[i] > k]
        seg = (b - k) * len(active) / n
        lane = bar_h / len(active)
        for j, i in enumerate(active):
            ax.add_patch(plt.Rectangle((pos, j * lane), seg, lane,
                                       color=DAY_COLOURS[i], linewidth=0))
        pos += seg
        k = b
    # the fixed positional split, identical for both arms
    for xc in (train, train + val):
        ax.axvline(xc, color=C["black"], linewidth=0.8, linestyle="--")
    ax.axvspan(train + val, 1.0, color=C["grey"], alpha=0.18, linewidth=0)
    ax.text(train / 2, 1.42, "train", ha="center", va="bottom", fontsize=7)
    ax.text(train + val / 2, 1.42, "val", ha="center", va="bottom", fontsize=7)
    ax.text(1.0, 1.42, "held-out", ha="right", va="bottom", fontsize=7)
    ax.text(-0.01, 1.0 + bar_h / 2, "timestamp\norder", ha="right",
            va="center", fontsize=7)
    ax.text(-0.01, bar_h / 2, "day\nround robin", ha="right", va="center",
            fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 1.75)
    ax.set_xlabel("position in the assembled stream (fraction)")
    ax.get_yaxis().set_visible(False)
    ax.spines["left"].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=DAY_COLOURS[i])
               for i in range(len(days))]
    ax.legend(handles, [d.capitalize()[:3] for d in days], ncol=5,
              loc="lower center", bbox_to_anchor=(0.5, -0.66),
              handlelength=1.0, columnspacing=1.2, fontsize=7)
    fig.subplots_adjust(left=0.21, right=0.97, top=0.97, bottom=0.44)
    return save(fig, "fig_assembly.pdf")


def fig_decomposition(used: dict) -> Path:
    """Detector and ECOD AUC-PR per arm, full held-out slice beside the shared
    records, each group with its chance floor (held-out prevalence)."""
    nat, syn = load("natural"), load("synthetic")
    dl, rv = load("deliverables"), load("review")
    full = [
        ("timestamp\norder",
         macro(nat, "ContrastCicids2017NaturalProposedDetectorAucpr", used),
         macro(nat, "ContrastCicids2017NaturalEcodAucpr", used),
         macro(dl, "SFourCicidsNaturalChanceFloor", used)),
        ("day\nround robin",
         macro(syn, "ContrastCicids2017InterleavedSyntheticProposedDetectorAucpr", used),
         macro(syn, "ContrastCicids2017InterleavedSyntheticEcodAucpr", used),
         macro(dl, "SFourCicidsSyntheticChanceFloor", used)),
    ]
    p_shared = macro(rv, "RevSharedPrevalence", used)
    shared = [
        ("timestamp\norder",
         macro(rv, "RevSharedDetectorNaturalAucpr", used),
         macro(rv, "RevSharedEcodNaturalAucpr", used), p_shared),
        ("day\nround robin",
         macro(rv, "RevSharedDetectorSyntheticAucpr", used),
         macro(rv, "RevSharedEcodSyntheticAucpr", used), p_shared),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 2.2), sharey=True)
    w = 0.36
    for ax, groups, title in zip(axes, (full, shared),
                                 ("full held-out slice", "shared records")):
        xs = np.arange(len(groups))
        det = [g[1] for g in groups]
        eco = [g[2] for g in groups]
        ax.bar(xs - w / 2, det, w, color=C["blue"], label="detector")
        ax.bar(xs + w / 2, eco, w, color=C["vermillion"], label="ECOD")
        for xi, g in zip(xs, groups):
            ax.hlines(g[3], xi - w, xi + w, colors=C["black"], linestyles=":",
                      linewidth=1.0,
                      label="chance floor" if xi == 0 else None)
        ax.set_xticks(xs, [g[0] for g in groups])
        ax.set_title(title)
    axes[0].set_ylabel("AUC-PR")
    axes[0].legend(loc="lower left", bbox_to_anchor=(0.0, 1.12), ncol=3,
                   handlelength=1.2, columnspacing=1.0)
    fig.subplots_adjust(left=0.15, right=0.99, top=0.78, bottom=0.22,
                        wspace=0.12)
    return save(fig, "fig_decomposition.pdf")


def fig_split(used: dict, protocol: dict) -> Path:
    """Both deterministic scorers' AUC-PR across the seven chronological cuts,
    with the held-out prevalence (the AUC-PR chance floor) on the same axis."""
    rv = load("review")
    comp = load("composition")
    cuts = sorted(int(k[len("RevSplitCut"):-len("Records")])
                  for k in rv["macros"]
                  if k.startswith("RevSplitCut") and k.endswith("Records"))
    x = np.array(cuts, dtype=float) / 100.0
    det = np.array([macro(rv, "RevSplitCut%dDetectorAucpr" % c, used) for c in cuts])
    eco = np.array([macro(rv, "RevSplitCut%dEcodAucpr" % c, used) for c in cuts])
    prev = np.array([macro(rv, "RevSplitCut%dPrevalence" % c, used) for c in cuts])
    macro(rv, "RevSplitCuts", used)
    macro(rv, "RevSplitEcodWins", used)
    fixed_cut = float(comp["config"]["train"]) + float(comp["config"]["val"])
    protocol["fixed_cut"] = fixed_cut

    fig, ax = plt.subplots(figsize=(WIDTH_IN, 2.5))
    lead = eco > det
    for j, xi in enumerate(x[lead]):
        ax.axvspan(xi - 0.012, xi + 0.012, color=C["vermillion"], alpha=0.15,
                   linewidth=0, label="ECOD leads" if j == 0 else None)
    ax.axvline(fixed_cut, color=C["black"], linewidth=0.7, linestyle="--",
               label="this paper's split")
    ax.plot(x, prev, color=C["grey"], linestyle=":", marker="^",
            label="held-out prevalence (chance floor)")
    ax.plot(x, det, color=C["blue"], marker="o", label="detector")
    ax.plot(x, eco, color=C["vermillion"], marker="s", label="ECOD")
    ax.set_xlabel("chronological cut\n(fraction of the stream before the held-out slice)")
    ax.set_ylabel("AUC-PR")
    ax.legend(loc="upper left", handlelength=1.6, fontsize=6.5)
    fig.subplots_adjust(left=0.15, right=0.98, top=0.97, bottom=0.27)
    return save(fig, "fig_split.pdf")


def fig_branch(used: dict) -> Path:
    """Combined, tail-only and auxiliary-only AUC-PR and AUC-ROC on the
    timestamp-ordered held-out slice, with the chance level drawn."""
    rv, dl = load("review"), load("deliverables")
    names = ["deployed", "tail\nonly", "auxiliary\nonly"]
    pr = [macro(rv, "RevBranchCombinedAucpr", used),
          macro(rv, "RevBranchTailOnlyAucpr", used),
          macro(rv, "RevBranchAuxOnlyAucpr", used)]
    roc = [macro(rv, "RevBranchCombinedAucroc", used),
           macro(rv, "RevBranchTailOnlyAucroc", used),
           macro(rv, "RevBranchAuxOnlyAucroc", used)]
    p_nat = macro(dl, "SFourCicidsNaturalChanceFloor", used)
    cols = [C["purple"], C["green"], C["orange"]]

    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 2.2))
    for ax, vals, chance, lab in zip(axes, (pr, roc), (p_nat, AUC_ROC_CHANCE),
                                     ("AUC-PR", "AUC-ROC")):
        ax.bar(names, vals, color=cols, width=0.6)
        ax.axhline(chance, color=C["black"], linestyle=":", linewidth=1.0,
                   label="chance")
        ax.set_ylabel(lab)
    axes[0].legend(loc="upper left", bbox_to_anchor=(0.0, 1.14),
                   handlelength=1.4)
    fig.subplots_adjust(left=0.15, right=0.98, top=0.86, bottom=0.24,
                        wspace=0.55)
    return save(fig, "fig_branch.pdf")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    style()
    used: dict = {}
    protocol: dict = {}
    outputs = [fig_assembly(used, protocol), fig_decomposition(used),
               fig_split(used, protocol), fig_branch(used)]
    manifest = {
        "generator": "scripts/make_figures.py",
        "generator_sha256": sha256(Path(__file__).resolve()),
        "paper_title": PAPER_TITLE,
        "environment": {"matplotlib": matplotlib.__version__,
                        "numpy": np.__version__,
                        "python": ".".join(map(str, sys.version_info[:3]))},
        "inputs": {p.relative_to(ROOT).as_posix(): sha256(p)
                   for p in sorted(INPUTS.values())},
        "figures": {p.relative_to(ROOT).as_posix(): sha256(p) for p in outputs},
        "values": dict(sorted(used.items())),
        "protocol": protocol,
        "constants": {"auc_roc_chance": AUC_ROC_CHANCE,
                      "note": "AUC-ROC of an uninformative ranking, by definition"},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("rendered %d figure(s) into %s"
          % (len(outputs), OUT.relative_to(ROOT).as_posix()))
    for p in outputs:
        rel = p.relative_to(ROOT).as_posix()
        print("  %-22s %7d B  %s" % (p.name, p.stat().st_size,
                                     manifest["figures"][rel][:16]))
    print("  figure_manifest.json: %d input(s), %d value(s)"
          % (len(INPUTS), len(used)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
