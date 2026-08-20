# findings_contributions — every claim against the runs that exist (Stage 5)

Generating run: `s5_verified_contributions_20260820T085552_1ae23176`. Every count is a provenance macro.

The governing rule forbids a number without a manifest. Stage 5 applies the same test to the **claims**: for each contribution the paper asserts, is there an implementation, and is there a manifested run that exercised it on the data the paper reports?

| verdict | count |
|---|---|
| SUPPORTED | 1 |
| PARTIAL | 3 |
| UNSUPPORTED | 4 |
| WITHDRAWN | 3 |

**One** of 11 claims is fully supported, and it is the rebuilt paper's new primary contribution rather than any of the original ones. That is the honest summary of where this work stands.

## WITHDRAWN — ChangePoint

> Couples **Bayesian online change-point detection** with risk-calibrated alert thresholds.

**Evidence.** Stage 3 (`s3_score_threshold_verification`) measures `P(r=0)` at 0.001000 against a hazard of 0.001000 through the change-point window, deviating by at most 1.4e-15 between initialisation and truncation — the predictive term cancels algebraically, so the posterior is the hazard for any data. The auxiliary change-point term contributes a mean of 0.0025 on the records where it binds.

**Action.** The evaluated system is **prequential global-Gaussian tail scoring**. It may not be described as change-point detection unless Stage 6's corrected statistic changes the measurement.

## PARTIAL — SloThreshold

> Derives the alert threshold from false-positive cost, false-negative cost and incident base rate rather than treating it as a free hyperparameter.

**Evidence.** `src/bocpd/slo.py:posterior_threshold` implements the prior-inclusive Bayes rule and Stage 3 manifests its values (0.655172 at prior 0.05, 0.261745 at prior 0.22). But that is not the paper's Eq. (12) `C_FP/(C_FP+C_FN)` = 0.090909, and it varies per dataset through a prior the paper says is unused.

**Action.** Keep the claim, state the prior-inclusive rule explicitly, and drop any sentence saying the hazard carries the prior.

## UNSUPPORTED — BurnRate

> Multi-window **burn-rate alerting** against an SLO error budget.

**Evidence.** `MultiWindowBurnRateAlert` exists in `src/bocpd/slo.py` and the label-consuming defect (A10) was fixed in Stage 2. But no run in `results/manifests/` exercises it on the rebuilt natural-order streams, and binding scope rule 4 confines burn-rate work to CICIDS2017 because the LITNET captures span minutes.

**Action.** Either run it on natural-order CICIDS and manifest the result, or drop the claim from the contribution list.

## WITHDRAWN — ThreeDatasets

> Evaluated on **UNSW-NB15**, CICIDS2017 and LITNET-2020.

**Evidence.** No manifest in this rebuild declares a UNSW-NB15 input; the dataset was removed from scope by the acquisition addendum, and audit finding A5 showed its 'chronological' stream was a seeded permutation.

**Action.** Report two datasets. Do not cite UNSW-NB15 results.

## PARTIAL — Chronological

> Evaluated using **chronological streaming splits**.

**Evidence.** Stage 1 built genuine timestamp-ordered streams and the monotonicity gate passed for all four. But LITNET-2020 admits no coherent global chronology — its three captures are temporally disjoint — so it is evaluated as three per-attack-type streams, never one chronological stream.

**Action.** State the restriction: chronological within CICIDS2017 and within each LITNET capture, never across LITNET captures.

## UNSUPPORTED — StreamingBaselines

> Compared against KitNET, Half-Space Trees, LODA, xStream, RRCF and streaming Isolation Forest.

**Evidence.** All six wrappers exist in `src/baselines/registry.py`. In this rebuild only **HST** (construction contrast) and **LODA** (prevalence sweep) were run and manifested. KitNET, xStream, RRCF and streaming iForest have no manifested rebuild run.

**Action.** Name only the baselines that ran, or run the others and manifest them. A baseline present in the repository is not a baseline reported in the paper.

## PARTIAL — BatchReferences

> LOF, ECOD and COPOD retained as batch reference baselines.

**Evidence.** ECOD and LOF are manifested (prevalence sweep; ECOD also in the construction contrast). COPOD is implemented in `src/baselines/batch.py` but has no manifested rebuild run.

**Action.** Report LOF and ECOD. Drop COPOD or run it.

## UNSUPPORTED — StatisticalTests

> Wilcoxon signed-rank tests with Holm-Bonferroni correction.

**Evidence.** Implementations exist in `src/eval/metrics.py`. No manifested rebuild run emits a test statistic or a corrected p-value, and with a single seed per cell for the deterministic methods there is nothing to test over.

**Action.** Drop the claim, or design a comparison with enough paired observations to support it — which binding rule 7 now constrains.

## WITHDRAWN — Latency

> Reports **detection latency in milliseconds** and per-flow throughput.

**Evidence.** Stage 3 confirms `src/eval/latency.py` contains no wall-clock instrumentation; the quantity is `i - start`, a count of records between attack onset and first alert.

**Action.** Report it as detection delay in records. Per-flow compute cost is a different quantity this pipeline does not measure.

## SUPPORTED — Construction

> **Benchmark stream construction, not attack prevalence, produces the regime structure the literature reports** (the rebuilt paper's primary contribution).

**Evidence.** Manifested by seven `s4_construction_contrast` runs, the `s4_contrast_deliverables` aggregation, and the `cicids_heldout_composition` audit. On identical records with only the order changed, held-out prevalence moves 42.995 points, the held-out slices share 32.5% of their records, and the deterministic ECOD-versus-proposed ordering inverts.

**Action.** State it exactly as binding rule 8 fixes it: not a full ranking reversal, not a causal claim about deployment prevalence, not a performance claim.

## UNSUPPORTED — Artifacts

> Code, **Docker configuration**, fixed seeds, dataset scripts and reproduction commands released and **archived on Zenodo**.

**Evidence.** No Dockerfile and no Zenodo record exist in the repository. Fixed seeds and dataset scripts do exist.

**Action.** Stage 8 prepares the artifact. Nothing is published, and the DOI placeholder must not be filled with an invented identifier.

