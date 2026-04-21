# Manuscript Replacement Package

## New title

**SLO-Aware Streaming Intrusion Detection: Risk-Calibrated Bayesian Changepoint Alerting with Burn-Rate Budgets**

## Honest contribution framing

Do not sell the paper as a fundamental Bayesian ML breakthrough. The real contribution is operational:

> We do not propose a new machine-learning algorithm. We propose a principled bridge between Bayesian streaming detection and SRE operational contracts, showing how IDS thresholds can be derived from SLO error budgets and burn-rate policies, then evaluated against fair online streaming baselines.

## Abstract replacement

Network intrusion detection is commonly evaluated as a static classification problem, yet production security monitoring is an online operational process governed by alert fatigue, service-level objectives, and incident-response budgets. This paper presents an SLO-aware streaming intrusion-detection framework that couples Bayesian online changepoint detection with risk-calibrated alert thresholds derived from site-reliability-engineering error budgets. Rather than treating the anomaly threshold as a free hyperparameter, the method maps false-positive cost, false-negative cost, incident base rate, and SLO burn-rate windows into an explicit alerting policy. We evaluate the approach on UNSW-NB15, the Engelen-corrected CICIDS2017 release, and LITNET-2020 using chronological streaming splits. The proposed method is compared against online streaming baselines, including Kitsune/KitNET, Half-Space Trees, LODA, xStream, RRCF, and streaming Isolation Forest, while LOF, ECOD, and COPOD are retained only as batch reference baselines. Evaluation reports AUC-PR, AUC-ROC, calibration error, Brier score, detection latency, false-alarm rate, throughput, and Wilcoxon signed-rank tests with Holm-Bonferroni correction. Code, Docker configuration, fixed seeds, dataset scripts, and reproduction commands are released at a public GitHub repository and archived on Zenodo at DOI [TO BE INSERTED AFTER RELEASE].

## Method replacement: SLO threshold and burn-rate alerting

Define the decision actions as alert and no alert. Define the state as incident and non-incident. The expected loss of alerting is `C_FP * P(y=0 | x_1:t)`. The expected loss of not alerting is `C_FN * P(y=1 | x_1:t)`. Alert when the posterior incident probability exceeds the cost-derived threshold. If using the prior-sensitive odds form, state it explicitly:

```text
T = C_FP(1-rho) / [C_FP(1-rho) + C_FN rho]
```

For an SLO `S` over a period of `P` minutes, the error budget is:

```text
B = (1 - S)P
```

For a 30-day month and `S = 0.999`, `B = 43.2` minutes. False positive and false negative costs should be normalized against this budget.

Add multi-window burn-rate alerting:

```text
[b_1h > 14.4 AND b_5m > 14.4] OR [b_6h > 6 AND b_30m > 6]
```

Add ticket-level logic:

```text
b_3d > 1 AND b_6h > 1
```

## Complexity replacement

Remove the unqualified O(1) statement.

Use this statement instead:

> Unpruned BOCPD maintains a run-length posterior whose support grows with time and therefore has O(T) per-event update cost and O(T²) cumulative cost over a stream. We use explicit run-length truncation with cap k. With diagonal sufficient statistics over d features, the update cost is O(kd) per event and memory is O(kd). Since k is fixed before evaluation and varied in ablation experiments, the implementation is bounded-memory streaming, not mathematically O(1) in the untruncated BOCPD sense.

## Experimental setup replacement

Datasets:

1. UNSW-NB15.
2. Engelen-corrected CICIDS2017.
3. LITNET-2020.

Streaming baselines:

1. Kitsune/KitNET.
2. HS-Trees.
3. LODA.
4. xStream.
5. RRCF.
6. Streaming Isolation Forest ASD.

Batch reference baselines only:

1. LOF.
2. ECOD.
3. COPOD.

Use chronological 70/15/15 splits, five seeds, 95% confidence intervals, Wilcoxon signed-rank tests, and Holm-Bonferroni correction.

## Results table placeholders

Do not insert fake numbers. Replace only after running the package.

| Dataset | Method | AUC-PR | AUC-ROC | F1 | p-value |
|---|---:|---:|---:|---:|---:|
| UNSW-NB15 | BOCPD-SLO | TBD | TBD | TBD | ref |
| UNSW-NB15 | Kitsune/KitNET | TBD | TBD | TBD | TBD |
| UNSW-NB15 | HS-Trees | TBD | TBD | TBD | TBD |

## Code availability statement

All source code, experiment configuration files, Dockerfiles, and reproduction scripts are available at `https://github.com/myoussef/rcbsid-paper` and archived on Zenodo under DOI `10.5281/zenodo.XXXXXXX`. The repository uses fixed random seeds, chronological split definitions, and a one-command reproduction script.

## Data availability statement

The UNSW-NB15, Engelen-corrected CICIDS2017, and LITNET-2020 datasets are publicly available from their cited sources. Raw datasets are not redistributed in the GitHub repository. Preprocessed Parquet files, configuration files, checksums, and experiment outputs will be archived on Zenodo subject to the datasets' redistribution terms.
