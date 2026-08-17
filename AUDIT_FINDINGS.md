# AUDIT_FINDINGS — verified defects in the pre-rebuild CALIBURN artifact

Status: **all twelve items below were verified directly against the code and
archived outputs on 2026-08-17**, read-only, at commit `6af616b` (branch
`exp/prevalence-and-tuning`), with the paper's cited repository state
`19be9b9` used for existence checks. This file is the paper's own correction
record. It is written so that a reader can re-verify every claim from the
quoted lines without trusting this document.

Terminology used below: "the paper" = arXiv:2605.24696 v1/v2; "the repo" =
this repository at the commit noted per item.

---

## A1 — The implemented score is not the score the paper defines

**Paper.** Eq. (6) and Algorithm 1 line 9 both define the anomaly score as
`s_t = P(r_t = 0 | x_1:t)`, the run-length-reset posterior.

**Code.** `src/bocpd/truncated_bocpd.py`, `update_score()`:

```python
score = float(np.clip(max(tail_score, 0.25 * short_run_score), 0.0, 1.0))
```

where `tail_score` is a chi-square CDF of the squared standardized residual
under a **global, slowly adapting diagonal Gaussian** (`_predictive_tail_score`):

```python
var = np.maximum(self.global_m2 / max(self.global_count - 1, 1), self.config.variance_floor)
stat = float(np.sum(((x - self.global_mean) ** 2) / var))
return float(np.clip(chi2.cdf(stat, df=int(self.n_features or x.shape[0])), 0.0, 1.0))
```

and `short_run_score` is `P(r_t <= 5)`, not `P(r_t = 0)`:

```python
short = min(len(probs), max(1, int(self.config.short_run_mass) + 1))
short_run_score = float(np.sum(probs[:short])) if self.n_seen >= self.config.warmup else 0.0
```

**What reached the metrics.** `src/experiments/run_streaming_eval.py:52`
`scores.append(float(model.update_score(row)))`, then l.84
`metrics = classification_metrics(y_test, scores_arr, threshold)`. So every
headline AUC-PR/AUC-ROC/F1 was computed on the composite above, never on
`P(r_t = 0)`.

**Verdict: CONFIRMED.** The evaluated detector is prequential global-Gaussian
tail scoring with a downweighted (0.25) change-point auxiliary term.

---

## A2 — The run-length posterior never responds to a change point

**Test (reproducible).** Repo BOCPD, `hazard=1e-3`, 3-D stream, 6σ mean shift
at t=300, 300 pre / 300 post:

```
P(r=0)  before shift (t 100-299): mean=0.001000 max=0.001000
P(r=0)  AT/after shift (t 300-310): [0.001 0.001 ... 0.001]
P(r=0)  peak anywhere t>=300: 0.0010
P(r<=5) peak anywhere t>=300: 0.0010
returned score peak t>=300: 1.0000
```

`P(r_t=0)` is pinned at the hazard rate and never spikes, because the growth
and change-point branches share the same predictive likelihood `nll`, which
cancels in the normalisation:

```python
nll = self._predictive_nll(x)
growth = self.log_run_probs + np.log1p(-self.config.hazard) - nll
cp = self._logsumexp(self.log_run_probs + np.log(self.config.hazard) - nll)
```

The reset branch must use a **prior-predictive** term, not the same
run-conditional `nll`, for the posterior to be data-responsive.

**Verdict: CONFIRMED.** All detection power in the published numbers comes
from the chi-square tail term. The BOCPD component contributes a constant.

---

## A3 — The threshold is prior-inclusive, contradicting the paper's Eq. (12)/(13)

**Paper.** `τ* = C_FP / (C_FP + C_FN) = 1/(1+C)`, described as derived from
costs alone, with the hazard said to carry the incident prior.

**Code.** `src/bocpd/slo.py`:

```python
numerator = false_positive_cost * (1.0 - incident_prior)
denominator = numerator + false_negative_cost * incident_prior
return numerator / denominator
```

That is the **prior-inclusive** Bayes rule (Elkan 2001), i.e. the sibling
paper's Eq. (2), not the paper's Eq. (12)/(13).

**Configs and archived thresholds.**
`configs/experiment_litnet_trial.yaml:26: default_incident_prior: 0.05` →
archived `threshold=0.655172`;
`configs/experiment_cicids_trial.yaml:26: default_incident_prior: 0.22` →
archived `threshold=0.261745`. Both match the prior-inclusive formula
exactly, and neither equals the paper's `0.091`. Archived F1 alongside:
`0.617291` (LITNET) and `0.639230` (CICIDS) — the paper's headline F1 values.

**Verdict: CONFIRMED.** The published F1 numbers were produced at a threshold
the paper does not describe, using a per-dataset prior the paper says is not
used.

---

## A4 — "Latency in milliseconds" is a detection delay in record counts

**Code.** `src/eval/latency.py` contains no clock:

```python
if in_attack and y_pred[i] == 1 and not detected:
    latencies.append(i - start)
```

`i - start` is a count of records. `run_streaming_eval.py:86`
`metrics.update(latency_summary(detection_latencies(y_test, y_pred)))`.

**Archived values.** LITNET `latency_mean=0.005748`; CICIDS
`latency_mean=0.061029`.

**Paper.** Table 8 reports "5.75 ms" and "61.03 ms" as per-flow compute cost,
with the caption "Mean latency is the per-flow average… Per-flow updates
frequently complete in less than one timer tick."

**Verdict: CONFIRMED.** The numbers are the archived record-count means
multiplied by 1000 and relabelled as milliseconds of compute. Two distinct
quantities (detection delay; wall-clock cost) were conflated into one. Note
also archived `throughput_eps` 574.17 / 443.49 vs the paper's 561 / 435.

---

## A5 — UNSW-NB15's "chronological" stream is a seeded permutation

**Code.** `src/data/loaders.py`:

```python
path_str = str(path).lower()
if shuffle_within_files is None:
    shuffle_within_files = 'unsw' in path_str
...
if shuffle_within_files:
    idx = rng.permutation(len(frame))
    frame = frame.iloc[idx].reset_index(drop=True)
```

with `shuffle_seed=20260422`, and `configs/experiment_unsw_trial.yaml:15:
time_column: null` (so the runner never sorts).

**Verdict: CONFIRMED.** The UNSW stream is a fixed random permutation within
each file, concatenated in filename order. The paper's "chronological splits
only" does not hold for UNSW. No `results_unsw_trial/` exists in the repo, so
the paper's UNSW numbers have no archived generating output at all.

---

## A6 — The described preprocessing does not exist; ports are retained

**Paper.** Table 3 describes min–max scaling and one-hot encoding.

**Code.** `src/data/loaders.py::prepare_xy` in full:

```python
y_raw = df[label_column].astype(str).str.lower()
y = (~y_raw.isin(['benign', 'normal', '0', 'false'])).astype(int).to_numpy()
X = df.drop(columns=[label_column])
X = X.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
return X.to_numpy(dtype=float), y, list(X.columns)
```

No scaling, no encoding — numeric selection and zero-fill only. (River's HST
pipeline applies its own internal `MinMaxScaler`; that is one baseline's
internals, not the shared preprocessing.) Ports survive into the feature
matrix: LITNET `COLS[16]="src_port"`, `COLS[17]="dst_port"` are inside
`OUT_COLS`; CICIDS `DROP_COLS = ["id","Flow ID","Src IP","Dst IP","Attempted Category"]`
removes addresses but not ports.

**Verdict: CONFIRMED.** Retained ports are a known shortcut feature on both
benchmarks and are not disclosed as inputs.

---

## A7 — KitNET and RRCF score the previous observation (one-step lag)

**KitNET.** `src/baselines/kitnet.py` — the wrapper documents its own lag:

```python
# KitNET-py exposes a fused process(x) API rather than separate
# score/learn calls. learn_one() caches process(x)'s RMSE score;
# score_one() returns the most recently cached value. This creates
# a one-sample offset...
return float(self._last_native_score)
```

**RRCF.** `src/baselines/rrcf.py`:

```python
scores.append(float(tree.codisp(self.index - 1)))
```

`self.index - 1` is the previously inserted point.

**Verdict: CONFIRMED for both.** Both baselines are evaluated one record out
of alignment with their labels, which biases them downward on streams whose
attacks are short (see A12).

---

## A8 — RRCF's seed is accepted and never applied

**Code.** `RRCFWrapper.__init__(self, n_features, seed: int = 42, ...)` then:

```python
self.forest = [rrcf.RCTree() for _ in range(n_trees)]
```

No random state is passed or set. The `seed` parameter is dead.

**Verdict: CONFIRMED.** RRCF's reported seed-to-seed variation is not
seed-controlled; the paper's "random_state set per seed in {11,23,47}"
(Table A.14 preamble) is false for RRCF.

---

## A9 — Silent fallback for the batch references

**Code.** `src/baselines/batch.py`:

```python
except Exception:
    model = _EmpiricalTailDetector(mode=name).fit(X_train)
    return _minmax(model.decision_function(X_eval))
```

on both the ECOD/COPOD branch and the LOF branch. `_EmpiricalTailDetector` is
a hand-rolled substitute, not PyOD.

**Surfacing.** `run_streaming_eval.py` records `uses_fallback` only for
*streaming* baselines (l.204, `getattr(model, 'uses_fallback', False)`); the
batch-reference path never sets or reports it.

**Verdict: CONFIRMED.** If PyOD had failed to import or fit for any reason,
the run would have silently reported a different algorithm's numbers under
the names ECOD/COPOD/LOF, with no flag in the output. (In the archived runs
PyOD did work — verified by bit-exact reproduction of ECOD/COPOD — so this is
a latent integrity hazard, not a corruption of the published values.)

---

## A10 — Burn-rate alerting consumes ground-truth labels and counts false negatives

**Paper.** §3.5: "the system does not yet know whether a threshold-crossing
event is truly malicious or benign. It therefore meters threshold crossings
as budget-consuming events."

**Code.** `run_streaming_eval.py::_burn_rate_count`:

```python
budget_event = float((yp == 1 and yt == 0) or (yp == 0 and yt == 1))
```

This reads `y_true` and counts **false negatives** as budget events —
precisely what the paper says the online rule cannot and does not do.

**Windows.** `long_window=max(1, int(r['long_window_minutes']))` feeding
`deque(maxlen=self.max_window)` — the "60 / 360 / 4320 minute" windows of
Table 2 are implemented as **counts of records**, with no timestamps anywhere
in `src/bocpd/slo.py`.

**Verdict: CONFIRMED on both counts.** The alerting layer as implemented is
label-dependent and its window units are mislabelled.

---

## A11 — Baseline framework and hyperparameters diverge from Appendix A

Paper Table A.14 states all streaming baselines run through **PySAD 0.2.0**
"with their authors' default hyperparameters".

| Item | Paper (Table A.14) | Code | File |
|---|---|---|---|
| HST framework | PySAD 0.2.0 | **River** (`from river import anomaly`) | `baselines/hst.py` |
| LODA `n_bins` | 10 | **32** | `baselines/loda.py` |
| iForestASD `window_size` | 2048 | **1000** | `baselines/iforest_asd.py` |
| KitNET grace | `grace_feature_mapping=5000` | **`fm_grace=100, ad_grace=200`** | `baselines/kitnet.py` |
| LOF `n_neighbors` | 20 | **35** | `baselines/batch.py` |

LODA is additionally a **dependency-free reimplementation** in this repo
(documented in its docstring as replacing PySAD's LODA, which "can collapse to
a constant score vector"), not PySAD's implementation at all.

**Verdict: CONFIRMED.** Five documented divergences plus a framework
substitution. The reported margins are against differently-configured
baselines than the paper describes.

---

## A12 — Claimed analyses have no implementation at the cited commit

`git grep` at `19be9b9` (the commit the paper cites as its artifact) across
`src/` and `scripts/`:

| Claimed in paper | Implementation at 19be9b9 |
|---|---|
| Isotonic calibration (§3.4, Table 9) | **absent** |
| Platt scaling (Table 9) | **absent** |
| Conformal Risk Control (§3.4, Tables 10, 11) | **absent** |
| Prevalence/regime sweep (Fig. 5) | **absent** |
| UNSW TTL ablation (Table 13) | **absent** |
| Reliability diagrams | **absent** (never produced in either state) |

Every hit for these terms on the current branch is code written during the
2026-08 revision (`scripts/caliburn_variants.py`, `scripts/prevalence_lib.py`,
etc.), not code that could have produced the published tables.

**Verdict: CONFIRMED.** Sections 3.4 and 5.5 and Tables 9–13 have no
computational origin in the cited artifact.

---

## A13 (additional, from the same audit) — benchmark microstructure

Measured on the interleaved LITNET-2020 test slice (225,000 flows, 14,621
attacks), scoring the test stream with the repo detector at the archived
threshold 0.655172:

```
contiguous attack runs: 14,235   median length 1   p90 1   max 2
label (attack-window) boundaries: 28,470
TPs within 25 flows of a boundary: 100.0%   deep inside a window: 0.0%
```

**Verdict: CONFIRMED.** LITNET as constructed contains essentially **no
sustained attack episodes** — attacks are isolated single flows. Claims about
"sustained attack" behaviour, and the burn-rate layer's dual-window
"confirmation" rationale, have no support in this benchmark's structure.
(The reviewer's "interleave seam" framing is not the right instrument: the
round-robin construction puts a seam between essentially every adjacent pair
of flows — 224,999 seams in 225,000 flows — so "within 25 flows of a seam" is
trivially ~100% and carries no information. The run-length result above is the
substantive form of that concern.)

---

## Consequences adopted by the rebuild

1. The detector is renamed and described as what it is (A1, A2) — Stage 3.
2. The threshold is presented as the prior-inclusive Bayes rule with Elkan
   attribution, and every "prior-free" claim is removed (A3) — Stage 3.
3. Latency is split into two separately-named, separately-measured quantities
   (A4) — Stage 2.
4. Evaluation streams are rebuilt in natural timestamp order; the shuffled
   UNSW stream and the label-aware interleaved composites are demoted to an
   explicitly labelled synthetic stress protocol (A5, A13) — Stage 1.
5. Preprocessing is either implemented as described or documented exactly as
   it is, with feature dimensionality stated per dataset (A6) — Stage 3.
6. Alignment, seeding and fallback-surfacing are fixed with tests (A7, A8,
   A9) — Stage 2.
7. Burn-rate alerting is made label-free, and window units are made real or
   renamed (A10) — Stage 2.
8. Baseline configuration reporting is reconciled to what runs (A11) — Stage 2.
9. Nothing from A12 is claimed unless it is regenerated from a manifested run
   in this rebuild (A12) — Stages 4, 5, and the provenance gate.
