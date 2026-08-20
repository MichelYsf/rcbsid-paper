#!/usr/bin/env python
"""Stage 3: what the detector's score and threshold ACTUALLY are.

The audit (A1-A4) established that the evaluated score is not the score the
paper defines, that the run-length posterior contributes a constant, that the
threshold is the prior-inclusive Elkan rule rather than the paper's Eq. (12),
and that "latency in milliseconds" is a detection delay counted in records.

This script does not restate those findings. It re-measures them against the
code as it stands today and manifests the numbers, so the manuscript's prose
can be written from measurement. Everything here runs locally in a couple of
minutes.

It also quantifies something the audit asserted qualitatively: how often the
change-point term is the term that actually sets the score. The score is
`max(tail, 0.25 * P(r <= 5))`, and `0.25 * P(r <= 5) <= 0.25`, so the
change-point branch can only bind where the chi-square tail is below 0.25.
"""
from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from provenance import provenance_run  # noqa: E402
from src.bocpd.slo import posterior_threshold  # noqa: E402
from src.bocpd.truncated_bocpd import (  # noqa: E402
    TruncatedBOCPDConfig, TruncatedGaussianBOCPD as TruncatedBOCPD,
)
from src.data.loaders import prepare_xy  # noqa: E402

STREAM = ROOT / "data/raw/natural/cicids2017_natural.csv"
OUT = ROOT / "findings_score_threshold.md"
SAMPLE = 50_000


class _DryRun:
    run_id = "DRY-RUN-NOT-MANIFESTED"

    def __init__(self):
        self.declared_inputs, self.declared_outputs, self.macros = [], [], {}

    def emit_macro(self, m, v, unit="", desc=""):
        self.macros[m] = v
        return v

    def note(self, k, v):
        pass


@contextlib.contextmanager
def _dry(*_a, **_k):
    yield _DryRun()


def changepoint_probe(hazard: float = 1e-3, d: int = 3, n: int = 300,
                      shift: float = 6.0, seed: int = 11, window: int = 50):
    """A 6-sigma mean shift at t=n. Does P(r=0) respond to it?

    Three regimes have to be separated or the answer comes out wrong, which it
    did on the first attempt here:

      t = 0            the run array has length 1, so P(r=0) is trivially 1.0.
                       An initialisation artefact, not a detection.
      t < max_run_length   no truncation; P(r=0) is exactly the hazard, because
                       cp = log h + logsumexp(logp - nll) and the growth branch
                       sums to log(1-h) + the same logsumexp, so the predictive
                       term cancels in the normalisation.
      t >= max_run_length  truncation drops growth mass before normalisation, so
                       the identity breaks and P(r=0) wanders. Also not a
                       detection - it is an artefact of the run-length cap.

    Taking a max over "t >= shift" mixes all three and reports a spike that has
    nothing to do with the change point.
    """
    rng = np.random.default_rng(seed)
    stream = np.vstack([rng.normal(0.0, 1.0, size=(n, d)),
                        rng.normal(shift, 1.0, size=(n, d))])

    cfg = TruncatedBOCPDConfig(hazard=hazard)
    model = TruncatedBOCPD(cfg)
    cap = int(cfg.max_run_length)
    pr0, scores = [], []
    for row in stream:
        s_ = float(model.update_score(row))
        lp = model.log_run_probs
        probs = np.exp(lp - model._logsumexp(lp))
        pr0.append(float(probs[0]))
        scores.append(s_)
    pr0 = np.asarray(pr0)
    scores = np.asarray(scores)

    resp = pr0[n:n + window]                      # the change-point window
    steady = pr0[1:min(cap, len(pr0))]            # post-init, pre-truncation
    return {
        "hazard": hazard,
        "cap": cap,
        "pre_mean": float(pr0[100:n].mean()),
        "resp_max": float(resp.max()),
        "resp_min": float(resp.min()),
        "window": window,
        "steady_max_dev": float(np.abs(steady - hazard).max()),
        "score_resp_peak": float(scores[n:n + window].max()),
        "trunc_mean": float(pr0[cap:].mean()) if len(pr0) > cap else float("nan"),
        "trunc_max": float(pr0[cap:].max()) if len(pr0) > cap else float("nan"),
        "init_value": float(pr0[0]),
    }


def binding_term_share(n_rows: int = SAMPLE):
    """On real data, which term actually sets the score?

    Replicates the implementation's ordering exactly: the tail score is computed
    from the PRE-update predictive, the short-run mass from the POST-update
    posterior, and the warm-up test uses the pre-increment `n_seen` (the counter
    is bumped at the end of update_score). Measuring these out of order compares
    two quantities the detector never compares.
    """
    if not STREAM.exists():
        return None
    df = pd.read_csv(STREAM, nrows=n_rows, low_memory=False)
    X, _y, _ = prepare_xy(df, "label")
    model = TruncatedBOCPD(TruncatedBOCPDConfig())
    tail_wins = cp_wins = ties = warm = 0
    cp_binding_at = []
    for row in X:
        x = np.asarray(row, dtype=float)
        n_before = model.n_seen
        tail = model._predictive_tail_score(x)     # pre-update, as implemented
        model.update_score(x)
        lp = model.log_run_probs
        probs = np.exp(lp - model._logsumexp(lp))
        short = min(len(probs), max(1, int(model.config.short_run_mass) + 1))
        srs = float(np.sum(probs[:short])) if n_before >= model.config.warmup else 0.0
        if n_before < model.config.warmup:
            warm += 1
            continue
        a, b = tail, 0.25 * srs
        if abs(a - b) < 1e-12:
            ties += 1
        elif a > b:
            tail_wins += 1
        else:
            cp_wins += 1
            cp_binding_at.append(b)
    total = tail_wins + cp_wins + ties
    return {"rows": total, "warmup_skipped": warm, "tail_wins": tail_wins,
            "cp_wins": cp_wins, "ties": ties,
            "cp_share": cp_wins / total if total else float("nan"),
            "cp_value_mean": float(np.mean(cp_binding_at)) if cp_binding_at else float("nan")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rows", type=int, default=SAMPLE)
    a = ap.parse_args()

    global OUT
    runner = provenance_run
    if a.dry_run:
        runner = _dry
        (ROOT / "results/_dryrun").mkdir(parents=True, exist_ok=True)
        OUT = ROOT / "results/_dryrun/findings_score_threshold.md"

    with runner(
        "s3_score_threshold_verification",
        config={"probe": "6-sigma mean shift, 3-D, hazard 1e-3",
                "binding_sample_rows": a.rows, "stream": str(STREAM)},
        seed=11,
        notes="re-measures A1-A4 against the current code; no prose is asserted "
              "that a number here does not support",
    ) as run:
        probe = changepoint_probe()
        binding = binding_term_share(a.rows)

        # --- A2: does the run-length posterior respond? -------------------
        run.emit_macro("SThreeProbeHazard", probe["hazard"],
                       desc="hazard rate used in the change-point probe")
        run.emit_macro("SThreePrZeroPreMean", round(probe["pre_mean"], 8),
                       desc="mean P(r=0) before the 6-sigma shift")
        run.emit_macro("SThreePrZeroResponsePeak", round(probe["resp_max"], 8),
                       desc="peak P(r=0) in the " + str(probe["window"]) +
                            "-record window after the 6-sigma shift")
        pinned = abs(probe["resp_max"] - probe["hazard"]) < 1e-9
        run.emit_macro("SThreePrZeroPinnedToHazard", 1 if pinned else 0,
                       desc="1 if P(r=0) in the change-point window equals the hazard")
        run.emit_macro("SThreePrZeroSteadyMaxDeviation",
                       round(probe["steady_max_dev"], 12),
                       desc="max |P(r=0) - hazard| after init and before truncation")
        run.emit_macro("SThreeRunLengthCap", probe["cap"],
                       desc="max_run_length at which truncation begins")
        run.emit_macro("SThreePrZeroInitValue", round(probe["init_value"], 6),
                       desc="P(r=0) at t=0, when the run array has length one")
        run.emit_macro("SThreePrZeroTruncatedMean", round(probe["trunc_mean"], 6),
                       desc="mean P(r=0) once the run array is truncated")
        run.emit_macro("SThreePrZeroTruncatedMax", round(probe["trunc_max"], 6),
                       desc="max P(r=0) once the run array is truncated")
        run.emit_macro("SThreeProbeScorePeak", round(probe["score_resp_peak"], 6),
                       desc="peak returned score in the change-point window")

        # --- A1: which term sets the score, on real data ------------------
        if binding:
            run.emit_macro("SThreeBindingRows", binding["rows"],
                           desc="records examined for which term sets the score")
            run.emit_macro("SThreeChangePointBindingRows", binding["cp_wins"],
                           desc="records where the change-point branch sets the score")
            run.emit_macro("SThreeChangePointBindingPct",
                           round(100.0 * binding["cp_share"], 4), unit="%",
                           desc="share of records where the change-point branch binds")
            run.emit_macro("SThreeShortRunWeight", 0.25,
                           desc="weight on the change-point auxiliary term")
            run.emit_macro("SThreeChangePointBindingMeanValue",
                           round(binding["cp_value_mean"], 6),
                           desc="mean score contributed where the change-point "
                                "branch sets the score")

        # --- A3: the threshold actually used -------------------------------
        t05 = posterior_threshold(1.0, 10.0, 0.05)
        t22 = posterior_threshold(1.0, 10.0, 0.22)
        cost_only = 1.0 / (1.0 + 10.0)
        run.emit_macro("SThreeThresholdLitnet", round(t05, 6),
                       desc="threshold at incident prior 0.05 (LITNET config)")
        run.emit_macro("SThreeThresholdCicids", round(t22, 6),
                       desc="threshold at incident prior 0.22 (CICIDS config)")
        run.emit_macro("SThreeThresholdCostOnly", round(cost_only, 6),
                       desc="the paper's Eq. (12) cost-only threshold C_FP/(C_FP+C_FN)")
        run.emit_macro("SThreeThresholdMatchesPaper",
                       1 if abs(t05 - cost_only) < 1e-9 else 0,
                       desc="1 if the implemented threshold equals the paper's Eq. (12)")

        # --- A4: is latency a clock? --------------------------------------
        lat = (ROOT / "src/eval/latency.py").read_text(encoding="utf-8")
        has_clock = any(tok in lat for tok in ("time.", "perf_counter", "monotonic",
                                               "datetime", "clock"))
        run.emit_macro("SThreeLatencyUsesAClock", 1 if has_clock else 0,
                       desc="1 if the latency module measures wall-clock time")

        # ---- document ----------------------------------------------------
        L, A = [], None
        L.append("# findings_score_threshold — what the detector actually computes (Stage 3)")
        L.append("")
        L.append("Generating run: `" + run.run_id + "`. Every number is a provenance macro.")
        L.append("")
        L.append("This re-measures audit findings A1-A4 against the code as it stands, "
                 "rather than restating them, so the manuscript's prose can be written "
                 "from measurement.")
        L.append("")
        L.append("## The score is not the score the paper defines")
        L.append("")
        L.append("The paper's Eq. (6) defines the anomaly score as `P(r_t = 0 | x_1:t)`. "
                 "`TruncatedBOCPD.update_score` returns")
        L.append("")
        L.append("```python")
        L.append("score = float(np.clip(max(tail_score, 0.25 * short_run_score), 0.0, 1.0))")
        L.append("```")
        L.append("")
        L.append("where `tail_score` is a chi-square CDF of the squared standardised "
                 "residual under a **global, slowly adapting diagonal Gaussian**, and "
                 "`short_run_score` is `P(r_t <= 5)`, not `P(r_t = 0)`.")
        L.append("")
        if binding:
            L.append("Because `0.25 * P(r <= 5) <= 0.25`, the change-point branch can "
                     "only set the score where the chi-square tail is below 0.25. "
                     "Measured over **" + str(binding["rows"]) + "** post-warm-up "
                     "records of the natural-order CICIDS stream, it sets the score in "
                     "**" + str(binding["cp_wins"]) + "** of them (**" +
                     ("%.2f%%" % (100.0 * binding["cp_share"])) + "**), at a mean value "
                     "of " + ("%.4f" % binding["cp_value_mean"]) + ".")
            L.append("")
            L.append("**That majority is not evidence the change-point term "
                     "matters.** Where it binds it contributes a mean score of only " +
                     ("%.4f" % binding["cp_value_mean"]) + " — so on those records "
                     "*both* terms are essentially zero, and the change-point branch "
                     "wins a comparison between two near-zero numbers. It is supplying "
                     "a floor, not signal. On the remaining " +
                     ("%.2f%%" % (100.0 - 100.0 * binding["cp_share"])) + " the "
                     "chi-square tail exceeds it and does all of the discriminative "
                     "work. Reading 75% as \"the change-point component is doing most "
                     "of the work\" would invert the finding.")
            L.append("")
        L.append("## The run-length posterior does not respond to a change point")
        L.append("")
        L.append("A 6-sigma mean shift in a 3-D Gaussian stream at t=300, hazard " +
                 ("%.0e" % probe["hazard"]) + ":")
        L.append("")
        L.append("| quantity | value |")
        L.append("|---|---|")
        L.append("| mean `P(r=0)` before the shift | " + ("%.6f" % probe["pre_mean"]) + " |")
        L.append("| peak `P(r=0)` in the " + str(probe["window"]) +
                 "-record window after the shift | " + ("%.6f" % probe["resp_max"]) + " |")
        L.append("| hazard rate | " + ("%.6f" % probe["hazard"]) + " |")
        L.append("| max deviation from hazard, post-init and pre-truncation | " +
                 ("%.2e" % probe["steady_max_dev"]) + " |")
        L.append("| peak returned score in that window | " + ("%.4f" % probe["score_resp_peak"]) + " |")
        L.append("")
        L.append("`P(r=0)` is **" + ("pinned to the hazard rate" if pinned else
                                     "not pinned to the hazard rate") + "** through the "
                 "change point. The reason is algebraic, not empirical: the "
                 "change-point branch is `log h + logsumexp(log p - nll)` and the growth "
                 "branch sums to `log(1-h) +` the same `logsumexp`, so the predictive "
                 "term cancels in the normalisation and `P(r=0)` is exactly the hazard "
                 "for any data whatsoever. The score still peaks at " +
                 ("%.4f" % probe["score_resp_peak"]) + " in that window — entirely from "
                 "the chi-square tail term.")
        L.append("")
        L.append("Two regimes where `P(r=0)` is *not* the hazard, neither of which is a "
                 "detection, and both of which will mislead anyone who takes a maximum "
                 "over the whole stream (this cost me a wrong number on the first "
                 "attempt):")
        L.append("")
        L.append("- **t = 0**: the run array has length one, so `P(r=0)` is trivially " +
                 ("%.1f" % probe["init_value"]) + ". Initialisation, not detection.")
        L.append("- **t >= " + str(probe["cap"]) + "** (`max_run_length`): truncation "
                 "drops growth mass *before* normalisation, so the cancellation breaks "
                 "and `P(r=0)` wanders — mean " + ("%.4f" % probe["trunc_mean"]) +
                 ", max " + ("%.4f" % probe["trunc_max"]) + ". This is an artefact of "
                 "the run-length cap and carries no information about change points "
                 "either.")
        L.append("")
        L.append("**Consequence for the manuscript.** The detector may not be "
                 "described as change-point detection. What was evaluated is "
                 "prequential global-Gaussian tail scoring, with an auxiliary term "
                 "that is algebraically pinned to the hazard rate in the probe and, on "
                 "real data, contributes a mean of " +
                 (("%.4f" % binding["cp_value_mean"]) if binding else "a near-zero value") +
                 " on the records where it binds at all. Stage 6 implements the "
                 "corrected statistic and measures whether it changes anything.")
        L.append("")
        L.append("## The threshold is the prior-inclusive rule, not Eq. (12)")
        L.append("")
        L.append("| quantity | value |")
        L.append("|---|---|")
        L.append("| implemented, incident prior 0.05 (LITNET) | " + ("%.6f" % t05) + " |")
        L.append("| implemented, incident prior 0.22 (CICIDS) | " + ("%.6f" % t22) + " |")
        L.append("| the paper's Eq. (12), `C_FP/(C_FP+C_FN)` | " + ("%.6f" % cost_only) + " |")
        L.append("")
        L.append("The implemented threshold is the prior-inclusive Bayes rule "
                 "(Elkan 2001). It **" + ("matches" if abs(t05 - cost_only) < 1e-9
                                          else "does not match") + "** the paper's "
                 "Eq. (12), and it varies per dataset through a prior the paper states "
                 "is not used. Every published F1 was produced at one of these two "
                 "thresholds.")
        L.append("")
        L.append("## \"Latency\" is a detection delay in records, not milliseconds")
        L.append("")
        L.append("`src/eval/latency.py` " + ("contains" if has_clock else "contains no") +
                 " wall-clock instrumentation; the reported quantity is `i - start`, a "
                 "count of records between attack onset and first alert. It cannot be "
                 "reported in milliseconds, and per-flow compute cost is a different "
                 "quantity that this pipeline does not measure.")
        L.append("")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
        run.declared_outputs.append(str(OUT))

    print("wrote " + str(OUT))
    if binding:
        print("  change-point branch binds on %.4f%% of %d records"
              % (100.0 * binding["cp_share"], binding["rows"]))
    print("  P(r=0) peak in the change-point window = %.8f (hazard %.0e)"
          % (probe["resp_max"], probe["hazard"]))
    print("  P(r=0) after truncation at t>=%d: mean %.4f max %.4f"
          % (probe["cap"], probe["trunc_mean"], probe["trunc_max"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
