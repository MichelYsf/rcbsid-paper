# findings_score_threshold — what the detector actually computes (Stage 3)

Generating run: `s3_score_threshold_verification_20260820T084659_1e2b01b8`. Every number is a provenance macro.

This re-measures audit findings A1-A4 against the code as it stands, rather than restating them, so the manuscript's prose can be written from measurement.

## The score is not the score the paper defines

The paper's Eq. (6) defines the anomaly score as `P(r_t = 0 | x_1:t)`. `TruncatedBOCPD.update_score` returns

```python
score = float(np.clip(max(tail_score, 0.25 * short_run_score), 0.0, 1.0))
```

where `tail_score` is a chi-square CDF of the squared standardised residual under a **global, slowly adapting diagonal Gaussian**, and `short_run_score` is `P(r_t <= 5)`, not `P(r_t = 0)`.

Because `0.25 * P(r <= 5) <= 0.25`, the change-point branch can only set the score where the chi-square tail is below 0.25. Measured over **49970** post-warm-up records of the natural-order CICIDS stream, it sets the score in **37497** of them (**75.04%**), at a mean value of 0.0025.

**That majority is not evidence the change-point term matters.** Where it binds it contributes a mean score of only 0.0025 — so on those records *both* terms are essentially zero, and the change-point branch wins a comparison between two near-zero numbers. It is supplying a floor, not signal. On the remaining 24.96% the chi-square tail exceeds it and does all of the discriminative work. Reading 75% as "the change-point component is doing most of the work" would invert the finding.

## The run-length posterior does not respond to a change point

A 6-sigma mean shift in a 3-D Gaussian stream at t=300, hazard 1e-03:

| quantity | value |
|---|---|
| mean `P(r=0)` before the shift | 0.001000 |
| peak `P(r=0)` in the 50-record window after the shift | 0.001000 |
| hazard rate | 0.001000 |
| max deviation from hazard, post-init and pre-truncation | 1.40e-15 |
| peak returned score in that window | 1.0000 |

`P(r=0)` is **pinned to the hazard rate** through the change point. The reason is algebraic, not empirical: the change-point branch is `log h + logsumexp(log p - nll)` and the growth branch sums to `log(1-h) +` the same `logsumexp`, so the predictive term cancels in the normalisation and `P(r=0)` is exactly the hazard for any data whatsoever. The score still peaks at 1.0000 in that window — entirely from the chi-square tail term.

Two regimes where `P(r=0)` is *not* the hazard, neither of which is a detection, and both of which will mislead anyone who takes a maximum over the whole stream (this cost me a wrong number on the first attempt):

- **t = 0**: the run array has length one, so `P(r=0)` is trivially 1.0. Initialisation, not detection.
- **t >= 500** (`max_run_length`): truncation drops growth mass *before* normalisation, so the cancellation breaks and `P(r=0)` wanders — mean 0.0110, max 1.0000. This is an artefact of the run-length cap and carries no information about change points either.

**Consequence for the manuscript.** The detector may not be described as change-point detection. What was evaluated is prequential global-Gaussian tail scoring, with an auxiliary term that is algebraically pinned to the hazard rate in the probe and, on real data, contributes a mean of 0.0025 on the records where it binds at all. Stage 6 implements the corrected statistic and measures whether it changes anything.

## The threshold is the prior-inclusive rule, not Eq. (12)

| quantity | value |
|---|---|
| implemented, incident prior 0.05 (LITNET) | 0.655172 |
| implemented, incident prior 0.22 (CICIDS) | 0.261745 |
| the paper's Eq. (12), `C_FP/(C_FP+C_FN)` | 0.090909 |

The implemented threshold is the prior-inclusive Bayes rule (Elkan 2001). It **does not match** the paper's Eq. (12), and it varies per dataset through a prior the paper states is not used. Every published F1 was produced at one of these two thresholds.

## "Latency" is a detection delay in records, not milliseconds

`src/eval/latency.py` contains no wall-clock instrumentation; the reported quantity is `i - start`, a count of records between attack onset and first alert. It cannot be reported in milliseconds, and per-flow compute cost is a different quantity that this pipeline does not measure.

