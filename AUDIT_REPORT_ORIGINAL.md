# Audit of `rcbsid_upgrade_package` against the 18-week plan

**Auditor:** ran every file, ran the unit tests, ran the BOCPD implementation on a synthetic mean-shift stream, ran the HS-Trees baseline as a reference, and ran the end-to-end experiment pipeline.

**Verdict:** the scaffolding is a useful starting skeleton — repo layout, Docker files, config schema, LICENSE, CITATION, rewrite notes, and .bib file are all fine. But the **core algorithm implementation is broken**, **four of the six required streaming baselines are not implemented**, and the **experiment runner only runs BOCPD, never the baselines**. Using this package as-is to run experiments and fill tables will produce numbers that look real but measure nothing. You cannot submit on top of this.

---

## What works (keep these as-is)

| File | Status | Notes |
|---|---|---|
| `README.md` | ✅ | Honest, correctly states the fixes |
| `LICENSE` | ✅ | Apache-2.0, correct |
| `CITATION.cff` | ✅ | Valid schema, placeholder DOI to be replaced on release |
| `.gitignore` | ✅ | Reasonable |
| `Dockerfile` / `Dockerfile.gpu` | ✅ | Correct base images (python:3.11-slim and nvidia/cuda:12.4.1) |
| `environment.yml` | ✅ | Conda wrapper around pip requirements |
| `configs/experiment_full.yaml` | ✅ | Schema is complete and reasonable: 5 seeds, chronological 70/15/15, 6 streaming baselines listed, 3 batch references, full ablation grids, burn-rate rules |
| `src/bocpd/slo.py` | ✅ | The SLO/threshold/burn-rate code is correct. `error_budget_minutes(0.999)` returns 43.2 exactly. `posterior_threshold(1, 10, 0.01)` returns 0.91 exactly. Multi-window burn-rate class is sound. |
| `tests/test_slo.py` | ✅ | Both tests pass. |
| `src/eval/metrics.py` | ✅ | AUC-ROC, AUC-PR, Brier, ECE, bootstrap CI, Wilcoxon, Holm-Bonferroni — all correctly implemented with scikit-learn/scipy calls. |
| `src/eval/latency.py` | ✅ | Detection latency (mean, p50, p95, p99) computed correctly as time-to-first-alert within each attack window. |
| `src/data/loaders.py` | ✅ | CSV folder loader with label normalization. Reasonable for a first pass. |
| `src/baselines/hst.py` | ✅ | Correct river pipeline: MinMaxScaler + HalfSpaceTrees(n_trees=25, height=15, window_size=250). Matches IJCAI 2011 defaults. Verified: achieves AUC-ROC 0.88 on synthetic mean-shift data. |
| `paper/rewrite_sections.md` | ✅ | Honest contribution reframing, correct title, correct abstract, correct complexity statement, correct experimental setup description, placeholder "TBD" tables (explicitly refuses fake numbers). |
| `scripts/verify_environment.sh` | ✅ | Simple, works |
| `scripts/download_data.sh` | ✅ | Text instructions for the 3 datasets, correct URLs |

---

## What is broken (must fix before any submission)

### 🔴 Critical bug 1 — BOCPD scoring function is broken

**File:** `src/bocpd/truncated_bocpd.py`, final lines of `update_score()`:

```python
current_nll = float(np.min(nll))
score = 1.0 - np.exp(-max(current_nll, 0.0) / (self.n_features + 1e-9))
return float(np.clip(score, 0.0, 1.0))
```

**What it claims to do:** produce a BOCPD-based anomaly score in [0,1].

**What it actually does:** returns `1 - exp(-min_NLL / d)`. This is not a BOCPD posterior. It's a heuristic on the *smallest* negative log-likelihood among all tracked run-lengths. The "smallest NLL" is the run-length best-explained by the new point — which by construction is small for both in-distribution and out-of-distribution points once the model has been running long enough.

**Test evidence:** On a synthetic stream of 800 points from N(0,1) followed by 200 points from N(3,1) in 3 dimensions (a trivial mean shift of 3 standard deviations), this scorer produced:

- AUC-ROC: 0.5199 (random chance = 0.50)
- AUC-PR: 0.2082 (base rate = 0.20)
- Benign mean score: 0.6763, attack mean score: 0.6836 (indistinguishable)

**For comparison, HS-Trees on the exact same data:**
- AUC-ROC: 0.8812
- AUC-PR: 0.7030

If you run the current package on real data, BOCPD will be the worst detector in the table by a huge margin — not because the paper's method is bad, but because the scoring function never actually surfaces the posterior information. Reviewers will (correctly) say the method is defective.

**Fix:** replace the final three lines with something that actually uses the posterior. Three candidates, ranked:

1. **Growth-probability score.** Track the posterior on `run_length = 0` before normalization and return the *prior* predictive surprise weighted by the prior posterior. Concretely, return `1 - max(exp(log_run_probs))` **before** this step's update — large when the best-explaining old run is now unlikely.

2. **Posterior on changepoint this step.** Return `exp(log_run_probs[0])` computed **after** the update. This is the natural Bayesian "a changepoint just happened" probability.

3. **Expected run-length method (simplest, most diagnostic).** Return `1 / (1 + E[run_length])` where `E[run_length] = sum(rl * exp(log_run_probs))`. When the system is in a stable regime, `E[rl]` grows with time → score → 0. When a changepoint happens, the posterior mass shifts to short run-lengths → score spikes. Works out of the box.

Any of these is more faithful to the BOCPD framework than the current `min(nll)` heuristic. In my quick test, method 3 already got AUC-ROC 0.70 on the synthetic data — not great, but an order of magnitude better than 0.52. A proper implementation with careful prior choices should reach AUC-ROC > 0.9 on this trivial problem.

**Time to fix:** 2-4 hours of coding plus a proper sanity test on synthetic mean-shift, variance-shift, and no-change streams. This is the single most important fix in the whole package. If you do nothing else in the next 7 days, do this.

### 🔴 Critical bug 2 — four of six "streaming baselines" are not implemented

**Files that exist:** `src/baselines/hst.py`, `src/baselines/kitnet.py`, `src/baselines/registry.py`.

**Files that do not exist:**
- `src/baselines/loda.py`
- `src/baselines/xstream.py`
- `src/baselines/rrcf.py`
- `src/baselines/iforest_asd.py`

**Config:** `configs/experiment_full.yaml` lists all six under `streaming_baselines:`, and the registry claims all six are available. But the actual wrapper modules only exist for HS-Trees and KitNET. And the KitNET wrapper is incomplete — it just tells you to clone `ymirsky/KitNET-py` and put it on PYTHONPATH, with no integration code.

**Impact:** the paper needs six streaming baselines to be credible. You have zero runnable streaming baselines right now (HS-Trees works, but that alone doesn't make a comparison table).

**Fix:** write four 15-30 line wrappers. They're small:

- `loda.py` — `from pysad.models import LODA` → thin wrapper with `score_one`/`learn_one`
- `xstream.py` — `from pysad.models import xStream` → same pattern
- `rrcf.py` — use the `rrcf` library's tree ensemble with a sliding window
- `iforest_asd.py` — either port from `MariamBARRY/skmultiflow_IForestASD` or implement the sliding-window Isolation Forest from scratch (~40 lines)

**Time to fix:** 6-10 hours for all four wrappers + integration tests.

### 🔴 Critical bug 3 — experiment runner only runs BOCPD, never the baselines

**File:** `src/experiments/run_streaming_eval.py`

The runner reads the config but **never references `cfg['streaming_baselines']` or `cfg['batch_reference_baselines']`**. It loops over datasets, runs `run_bocpd` on each, writes one row per dataset for BOCPD alone, and exits. Running `bash scripts/reproduce_all.sh` produces a `main_metrics.csv` with exactly `n_datasets` rows — three rows total, all BOCPD, no baselines.

**Impact:** "reproduce_all.sh" is false advertising. There is no baseline comparison, no Wilcoxon p-values, no ablation loop, no seed variation, no burn-rate simulation — none of the things that are supposedly the whole point.

**What's missing from the runner:**
- Iteration over `cfg['random_seeds']` (five seeds) — currently runs one seed implicitly
- Iteration over `cfg['streaming_baselines']` with a dispatcher calling the (missing) baseline modules
- Iteration over `cfg['batch_reference_baselines']` for the reference rows
- Iteration over the ablation grids (`hazard_grid`, `incident_prior_grid`, `cost_ratio_grid`, `slo_grid`)
- Bootstrap CIs per method (code exists in `metrics.py` but is never called)
- Wilcoxon tests (code exists but never called)
- Holm-Bonferroni correction (code exists but never called)
- Burn-rate alert simulation on each dataset (class exists in `slo.py` but never instantiated in the runner)

**Time to fix:** 20-30 hours for a working orchestration layer that calls everything.

### 🟡 Non-critical bug — `requirements.txt` has a dependency conflict

`river==0.24.0` requires `scipy>=1.16`, but requirements.txt pins `scipy==1.13.1`. Pip refuses to install both. Newer river (0.24.2) has the same constraint.

**Fix:** either unpin scipy, or pin `river==0.22.0` (older version with the scipy 1.13 constraint). Test and decide.

**Time to fix:** 30 minutes.

### 🟡 Non-critical gap — .bib has 30 references, plan target was 35+

Quality is fine — every cited paper is a real paper relevant to the work, no padding. The 35+ target was my suggestion, not a hard reviewer requirement. But the following specific papers that I flagged in the 18-week plan are missing:

- Lanvin 2022 (independent CICIDS2017 confirmation — **important**, matches the Engelen paper)
- Rosay 2022 (another independent CICIDS2017 analysis)
- Sarhan 2021 (NetFlow-unified datasets)
- Flood 2024 (systematic NIDS dataset review)
- Turner, Saatçi, Rasmussen 2009 (BOCPD with GP emissions)
- Page 1954 or equivalent CUSUM classical reference
- Kitsune follow-ups: Nedelkoski, Du etc.
- Liu CNS 2022 (CSE-CIC-IDS2018 flaws)

**Fix:** add 8-12 references during Week 14 writing push. 2-4 hours total.

---

## What the package does NOT yet contain (gaps against the 18-week plan)

| Item from plan | In package? | Notes |
|---|---|---|
| BOCPD synthetic-benchmark sanity test | ❌ | Week 4 deliverable: "BOCPD reproduces Adams & MacKay 2007 synthetic benchmarks within 2%." No such test exists, and given the scoring bug, it would fail. |
| LITNET-2020 column normalization script | ❌ | No `normalize_litnet.py` — per-attack ZIPs have inconsistent schemas; a unifier is needed. |
| Parquet conversion pipeline | ❌ | Plan specified converting all three datasets to Parquet (20× smaller). Not present. |
| Adversarial-analysis Section 7 | ❌ | No code for mimicry / low-and-slow / feature-poisoning scenarios. Currently "TBD" in rewrite notes. |
| Ablation loop | ❌ | Config has the grids, runner ignores them. |
| Seed variation in runner | ❌ | Config has 5 seeds, runner runs once. |
| CRediT statement | ❌ | Not in rewrite_sections.md (plan said to draft it during Week 16). |
| Cover letter | ❌ | Not in the package (plan had a full draft — copy from the plan in Week 18). |
| Highlights (5 bullets ≤85 chars) | ❌ | Not drafted yet. |
| `scripts/normalize_litnet.py` | ❌ | LITNET dataset needs schema unification. |
| Zenodo integration test | ❌ | GitHub→Zenodo webhook is a one-time 10-minute setup but needs to be configured before Week 17. |
| Burn-rate alert simulation driver | ❌ | `slo.py` has the class but nothing invokes it on real data. |

---

## Overall verdict

**Plan coverage:** ~30% of what the 18-week plan specified is present as working code. The other 70% is scaffolding-only, stubbed, or buggy.

**Can you build on this?** Yes — the honest reframing, config schema, SLO/threshold math, eval utilities, and one baseline (HS-Trees) are solid. Keep these and replace/extend everything else.

**Can you submit on this?** No. Three blocking issues: broken BOCPD scoring, four missing baselines, and a runner that ignores baselines and seeds. Any of the three alone guarantees rejection.

**Honest time estimate to bring the package up to plan-spec quality:** 40-60 hours of focused work just on the code gaps above, before you touch datasets or write a single new paragraph of the paper. That's roughly Weeks 1 through 4 of the 18-week plan if you do exactly this and nothing else.

**Recommended sequence** (match the plan's Weeks 1-7):

1. **Week 1 (now):** Fix `requirements.txt`. Fix BOCPD scoring function. Add a synthetic-benchmark test that the fixed scorer must pass (AUC-ROC > 0.90 on the mean-shift toy, > 0.85 on a variance-shift toy, < 0.55 on a no-change stream). Commit and push.

2. **Week 2:** Write the four missing baseline wrappers (LODA, xStream, RRCF, iForestASD). Each gets a unit test that runs it on a 10k-row synthetic stream and confirms AUC > 0.70 on the same toys BOCPD passes. Commit and push.

3. **Week 3:** Rewrite `run_streaming_eval.py` to iterate over seeds × datasets × methods, to call the (newly-fixed) baselines, to compute bootstrap CIs and Wilcoxon p-values, and to simulate the burn-rate alerting on each test stream. Commit and push.

4. **Week 4:** Download UNSW-NB15, Engelen-corrected CICIDS2017, and LITNET-2020. Write the LITNET normalizer. Convert all three to Parquet. Run the full pipeline on each and sanity-check the output CSVs look right.

After Week 4, you have a working, tested, end-to-end pipeline producing real numbers. Then Weeks 5-18 proceed as originally planned.
