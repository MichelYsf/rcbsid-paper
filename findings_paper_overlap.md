# Paper overlap check: sibling manuscript vs CALIBURN

Sub-task 4 of the runbook addendum (2026-08-06). Both PDFs were located and
read end-to-end; extraction caveats are listed at the bottom.

- **Sibling manuscript**: `C:\Users\CYBERWIZARD\Downloads\Risk–Calibrated Bayesian Streaming Intrusion Detection with.pdf`
  — "Risk-Calibrated Bayesian Streaming Intrusion Detection with SRE-Aligned
  Decisions", Michel Youssef, arXiv:2510.09619v1 [cs.CR], 8 pages. (No PDF named
  literally "rcbsid" or "SLO-Aware" exists in Downloads/Documents/Desktop/projects;
  this is the only PDF matching the search terms, and "RCBSID" is the acronym of
  its title — it is also the namesake of this repo.)
- **CALIBURN**: `C:\Users\CYBERWIZARD\Downloads\2605.24696v2.pdf` — "CALIBURN:
  Operationally Calibrated Streaming Intrusion Detection with Regime-Dependent
  Conformal Risk Control", Michel A. Youssef, arXiv:2605.24696v2, 58 pages.
  Byte-identical (MD5 `0782c116a8fb6b612bf226c001b449e8`) to
  `Downloads\CALIBURN Operationally Calibrated Streaming.pdf`.

## 1. Figure and table captions — sibling (arXiv:2510.09619v1)

Figures (the paper contains **zero tables**):

1. "Figure 1: Precision–recall curve on the UNSW–NB15 stream. Our method maintains high precision across recall levels."
2. "Figure 2: Precision–recall curve on the CICIDS2017 stream. The risk–calibrated detector outperforms unsupervised baselines."
3. "Figure 3: ROC curve on the UNSW–NB15 stream. All detectors achieve high AUC but PR metrics reveal differences under imbalance."
4. "Figure 4: ROC curve on the CICIDS2017 stream."
5. "Figure 5: Reliability diagram for the UNSW–NB15 stream. The dashed line denotes perfect calibration and our probabilities lie close to this diagonal."
6. "Figure 6: Reliability diagram for the CICIDS2017 stream."
7. "Figure 7: Anomaly score timeline on a portion of the CICIDS2017 test stream. The shaded region indicates a true attack; the horizontal line marks the cost–derived threshold. Scores above the threshold trigger alerts."

Notable: the sibling reports **no quantitative results anywhere** (no AUC-PR/AUPRC
values, despite naming AUPRC its primary metric), and its figure legends read
"Ours (BOCPD+SLO)", "IF (tuned)", "OCSVM (tuned)" while the body text names
LOF/ECOD/COPOD as baselines — an internal text/figure inconsistency.

## 2. Figure and table captions — CALIBURN (arXiv:2605.24696v2)

Figures:

1. "Figure 1: CALIBURN architecture, organized into three responsibility layers. Streaming network flows enter the truncated Bayesian online change-point detector, which produces a probabilistic anomaly score st = P(rt = 0 | x1:t). The cost-sensitive threshold τ* = CFP/(CFP + CFN) is derived from operator-specified costs, not from a validation set. The SLO burn-rate alerting layer escalates the resulting events into ticket, slow page, or fast page actions using multi-window burn-rate logic. Each layer can be inspected and adjusted independently of the others."
2. "Figure 2: Truncated BOCPD posterior dynamics on a synthetic stream with one change-point at t=300. (a) Observation stream with mean shift. (b) Run-length posterior P(rt | x1:t) visualized as a heatmap; the bright diagonal ridge representing the dominant run length grows with time and resets at the change-point. (c) The anomaly mass concentrated at recent run lengths (here illustrated as P(rt ≤ 5 | x1:t) to make the discrete pulse visible) spikes sharply at the true change-point and crosses the cost-derived threshold τ* = 0.091 corresponding to cost ratio C=10."
3. "Figure 3: Multi-window burn-rate alerting on a synthetic event stream. (a) shows a transient noise burst at t=120 minutes and a sustained attack starting at t=300. (b) shows that the short-window burn rates spike with the noise burst, but the long windows do not cross threshold simultaneously, so no alert fires. The sustained attack drives both short and long windows above their thresholds. (c) shows the resulting alerts: the page-fast and page-slow levels both fire only during the sustained attack, demonstrating dual-window protection from transient noise."
4. "Figure 4: LITNET-2020 AUC-PR across all evaluated methods. Bars show the 3-seed mean. Error bars denote seed-to-seed standard deviation for stochastic methods (LODA, HST, iForest_ASD, RRCF); deterministic methods (CALIBURN, ECOD, COPOD, LOF, KitNET) produce identical results across seeds and have no error bars. CALIBURN's AUC-PR of 0.943 exceeds the next-best method (LODA, 0.425) by 2.21× and the best batch reference (ECOD, 0.229) by 4.12×."
5. "Figure 5: Regime sensitivity of AUC-PR across the three NIDS datasets, ordered by attack prevalence. CALIBURN dominates in the rare-attack regime (LITNET-2020, 5.2%), trails the LOF batch reference at moderate prevalence (CICIDS2017, 22.06%), and converges with the streaming-method cluster at high prevalence (UNSW-NB15, 64%). The orange line shows the strongest non-CALIBURN streaming baseline at each dataset (LODA on LITNET, HST on CICIDS, RRCF on UNSW); the green line shows the best batch reference (ECOD on LITNET, LOF on CICIDS and UNSW). The pattern supports the regime-sensitivity hypothesis: CALIBURN is most useful where streaming detection is operationally needed most."

Tables:

1. "Table 1: Cost ratio C = CFN/CFP and the resulting cost-sensitive posterior threshold τ*."
2. "Table 2: Multi-window burn-rate alerting configuration used in CALIBURN, following Beyer et al. (2018)."
3. "Table 3: Main experimental configuration used for CALIBURN and the evaluated baselines."
4. "Table 4: AUC-PR, AUC-ROC, and F1 on LITNET-2020 (3-seed mean ± std). Deterministic methods are marked \"det.\" because repeated seeds produce identical results."
5. "Table 5: AUC-PR, AUC-ROC, and F1 on CICIDS2017 (3-seed mean ± std). CALIBURN remains the best streaming method but trails the LOF batch reference."
6. "Table 6: AUC-PR and AUC-ROC on UNSW-NB15 (single seed; test set = 38,652 records, attack prevalence ≈ 64%, prevalence floor 0.6764). Methods are ordered by AUC-PR. AUC-PR values close to the prevalence floor indicate near-trivial ranking performance."
7. "Table 7: Cross-dataset ranking summary. CALIBURN's rank is its position in the AUC-PR ordering on each dataset. \"Best method\" is the highest AUC-PR overall; \"best streaming baseline\" is the highest AUC-PR among the streaming methods, excluding CALIBURN itself."
8. "Table 8: CALIBURN operational latency and throughput per dataset. Values are computed over the evaluated test stream. Mean latency is the per-flow average; throughput is the streaming rate in events per second. Per-flow updates frequently complete in less than one timer tick (the mean reflects the small fraction of computationally expensive updates)."
9. "Table 9: Calibration metrics on the test set for raw, Platt-scaled, and isotonic-regression-calibrated BOCPD scores. Calibrators are fit on the validation split. Lower is better. Best result per dataset and metric is shown in bold."
10. "Table 10: Conformal Risk Control: nominal alert budget α, fitted threshold τ̂, and empirical test-set FPR on isotonic-calibrated scores. CRC validity requires the empirical FPR to be at or below α."
11. "Table 11: Comparison of the cost-sensitive threshold τ* = 0.091 (Section 3.3, C = 10) and the CRC-derived threshold τ̂α=0.01 (Section 3.4) on isotonic-calibrated BOCPD scores. Alert rate is the fraction of test flows above the threshold. Recall is the fraction of true attacks above the threshold. Both thresholds operate on calibrated scores."
12. "Table 12: Ablation of the calibration and Conformal Risk Control layers. All variants share the same BOCPD scoring stage. V1 is the recommended pipeline; V4 omits both calibration and CRC. The variants reveal regime-dependent contributions of each layer. Threshold τ denotes the operating threshold applied to the appropriate score (calibrated or raw, depending on variant). NaN in the threshold column indicates that CRC at α = 0.01 was infeasible on raw scores for that dataset because no τ ∈ [0, 1] produced an upper-bounded FPR below α."
13. "Table 13: UNSW-NB15 TTL ablation. We re-run the full pipeline with sttl, dttl, and ct_state_ttl removed from the feature vector and compare against the full-feature baseline. The artifact hypothesis predicts a substantial drop in detection metrics when the TTL features are removed. Empirically, we observe small improvements across all metrics, indicating that CALIBURN's collapse on UNSW-NB15 is intrinsic to the streaming setting at 64 percent attack prevalence rather than caused by removable feature leakage."
14. "Table A.14: Baseline implementations and hyperparameter configurations. PySAD baselines are streaming detectors; PyOD baselines are batch references included for context. All settings reflect framework defaults at the time of evaluation. CALIBURN's run_length_truncation (L = 500) and hazard (H = 10^-3) are documented in the main text."

## 3. Overlap between the two papers

**Captions**: no caption pair overlaps in wording, and no caption pair describes
the same figure/table content. Closest conceptual parallels only:
- Sibling Fig. 7 (anomaly-score timeline crossing a cost-derived threshold on
  real CICIDS2017 data, threshold ≈ 0.91) vs CALIBURN Fig. 2 (synthetic stream,
  threshold τ* = 0.091) — same visual idea, different data and different numbers.
- Sibling Figs. 5–6 (reliability diagrams) vs CALIBURN Table 9 (calibration
  metrics) — both address calibration, no shared artifact.
- Sibling has zero tables; CALIBURN has 14. Sibling's PR/ROC curve figures have
  no CALIBURN counterpart; CALIBURN's architecture/burn-rate/regime figures have
  no sibling counterpart.

**Numbers**: exactly one genuinely shared value — the cost pair C_FP = 1,
C_FN = 10 (cost ratio C = 10). Two near-misses that are *not* the same number:
- Threshold **0.91 (sibling) vs 0.091 (CALIBURN)**: same costs, different
  formulas. The sibling includes the prior: T = C_FP(1−ρ)/(C_FP(1−ρ)+C_FN·ρ) ≈
  0.91 at ρ = 0.01. CALIBURN drops the prior: τ* = C_FP/(C_FP+C_FN) = 1/11 ≈
  0.091. A ~10× different operating point despite the visual similarity.
- **0.01** appears in both as different quantities (sibling: incident prior ρ;
  CALIBURN: CRC alert budget α).
- No shared performance numbers can exist: the sibling reports none at all.

**Verdict**: shared lineage, not duplicated material. Same author, same
BOCPD + cost-threshold + SRE framing, same two datasets (CALIBURN adds
LITNET-2020), same PyOD batch baseline family — and CALIBURN's artifact repo is
literally named `rcbsid-paper` after the sibling's title acronym. CALIBURN is
the substantially expanded successor: it adds multi-window burn-rate alerting,
a third dataset, Platt/isotonic calibration, Conformal Risk Control, ablations,
and actual quantitative results. No verbatim caption reuse, no shared table, no
shared reported result. The papers should cite each other given the shared
framework, but nothing suggests duplicated content.

## 4. Sibling paper's alerting section: one window or many?

**Answer: single threshold, windowless — definitively NOT multi-window
multi-burn.** The sibling uses exactly one cost-derived threshold (T ≈ 0.91) on
the per-event posterior incident probability, evaluated event-by-event. There
are no lookback windows and no burn-rate computation; the SRE error budget is
used once, offline, to motivate the single static threshold. The phrase "burn
rate" never appears in the paper. (CALIBURN, by contrast, uses three paired
long/short windows — 60/5, 360/30, 4320/360 minutes with burn thresholds
14.4/6.0/1.0 and an AND condition over both windows — following Beyer et al.'s
SRE Workbook. The multi-window logic is a CALIBURN addition.)

The sibling's alerting passage, verbatim:

> 3.1 Cost–Sensitive Decision Rule
> Let C_FP and C_FN denote the relative costs of false positives and false
> negatives, and let ρ be the prior probability of an incident. Under Bayesian
> decision theory, the optimal threshold on the posterior incident probability
> P(y_t = 1 | x_1:t) is
>
> T = C_FP(1 − ρ) / (C_FP(1 − ρ) + C_FN ρ).   (2)
>
> An alert is issued whenever P(y_t = 1 | x_1:t) > T. In a setting where a
> false alarm costs one minute of analyst time and a missed intrusion costs ten
> minutes of downtime, with ρ = 0.01, the threshold evaluates to T ≈ 0.91. Thus
> only events with predicted malicious probability above 0.91 trigger an alert,
> reflecting the stringent SRE error budget.
>
> 3.2 SRE Error–Budget Example
> Consider an SRE team with a 99.9% availability SLO, corresponding to a
> monthly error budget of 43.2 minutes. If responding to a false alert consumes
> approximately one minute, while an undetected intrusion causes ten minutes of
> downtime, then C_FP = 1 and C_FN = 10. Assuming an incident base rate of
> ρ = 0.01, the probability threshold becomes
>
> T = (1 · 0.99) / (1 · 0.99 + 10 · 0.01) ≈ 0.91.
>
> Burning the entire error budget solely through false alarms would require
> about 43 spurious alerts, whereas four missed attacks (4 × 10 min) would
> exhaust the budget. Selecting T = 0.91 therefore trades a few additional
> false positives against the risk of missing serious incidents.

And from its Section 4 online detection procedure, step 2(d): "If
P(y_t = 1 | x_1:t) > T then raise an alert."

## Extraction caveats

Both PDFs were converted to text (pdf-parse / pdftotext-layout); inter-word
spacing from justified text was normalized, and true math subscripts/glyphs
(C_FP, y_t, τ, τ̂, α, β) are flattened to linear notation. Wording is otherwise
exactly as printed; nothing was paraphrased inside quotes. Two-line fraction
layouts in CALIBURN's Eqs. 18–20 were reconstructed inline.
