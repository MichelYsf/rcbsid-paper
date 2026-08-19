# findings_contrast — construction, not prevalence (Stage 4)

Generating run: `s4_contrast_deliverables_20260819T121304_c90469b2`.
Every number below is emitted as a provenance macro by this run (the manifest named above), by the per-arm runs it aggregates, or by the `cicids_heldout_composition` audit where cited.

> Adversarial review on 2026-08-19 refuted an earlier version of this sentence. Seven printed numbers had no `emit_macro` call, and one of them - the pooled attack count 14,621 - appeared in no manifest anywhere while being written into a manuscript-bound LaTeX table. That is exactly the orphan the governing rule forbids. Those macros are now emitted, and the sentence is asserted only because the generator emits a macro for every number it prints.

**Claim under test.** Benchmark stream *construction*, not attack prevalence, produces the regime structure the intrusion-detection literature reports.

## How to read these numbers - asymmetries that are real

These come from an adversarial review of this document and are stated up front rather than footnoted, because two of them materially condition the headline.

1. **The three methods do not get the same information.** ECOD is fitted on `Xtr[ytr == 0]`, benign-only training data, which *uses the labels*. HST trains on all of `Xtr` unlabelled and keeps adapting through validation and test. The proposed detector adapts online and sees no labels. ECOD is therefore label-privileged and HST is test-time-adaptive: where ECOD wins, label supervision is a live explanation and is not controlled for here.
2. **Thresholds are not comparable across methods.** The proposed detector uses a fixed untuned posterior threshold (0.655172) while HST and ECOD receive a validation F1-argmax threshold. AUC-PR is threshold-free so the comparisons below are unaffected, but every precision, recall, F1 and threshold column in `results/construction_contrast.csv` is non-comparable across methods and must not be quoted.
3. **AUC-PR is not comparable ACROSS arms.** Its chance floor is the test prevalence, which is precisely what the construction moves. Lift above floor is reported beside every raw value, and the raw cross-arm difference is deliberately not reported at all.
4. **Rankings rest on a single HST draw** unless a seed count above one is stated. The proposed detector and ECOD are deterministic here; HST is not, and its published standard deviation on the LITNET composite (`results/table4_litnet_tuned.tex`) is of the same order as some margins below. This is flagged where it bites.

## Contrast 1 — CICIDS2017, order only (prevalence held constant)

CICIDS2017 is a single capture week, so the same record multiset can be presented in true timestamp order and in day-of-week round robin. The reordering is verified mechanically to be an exact permutation, not asserted from reading the code: both arms hold `CicidsArmRows` records and `CicidsArmAttacks` attacks, a whole-stream prevalence of `CicidsArmPrevalencePct` in each (`cicids_heldout_composition` manifest). Order is the only manipulated variable.

What follows is a change in the measured regime **under reordering with the 70/15/15 tail split held fixed**. No split-rule sensitivity check has been run, so the effect is not attributed to construction in isolation.

| quantity | natural (timestamp order) | synthetic (day round robin) |
|---|---|---|
| held-out prevalence | **68.235%** | **25.240%** |
| held-out attacks | 163764 | 60575 |

Reordering alone moves the held-out prevalence by **-42.995 percentage points**.

**But the slices are not the same sample, and an earlier version of this document wrongly said no attack was resampled.** That is true of the stream and false of the evaluated slice, which is where the number lives. Measured by the `cicids_heldout_composition` audit:

- the two held-out slices share only **78000 of 240000 records (32.5%)**
- the synthetic arm's held-out attacks are a **strict subset** of the natural arm's
- **103189 attacks** are moved out of the held-out slice into training by the reordering
- every synthetic held-out attack comes from **1 capture day**; Monday-Thursday contribute 162,000 held-out rows and **zero** attacks
- the natural held-out slice is one **204.2-minute** Friday-evening window

So the mechanism is **dilution, not redistribution**. The synthetic arm's Friday sub-slice is *denser* in attacks (77.660%) than the natural arm's entire held-out slice (68.235%); the prevalence falls because four attack-free days are mixed in. This remains a real construction effect on the reported regime, but it is specific to CICIDS's per-day attack scheduling meeting a fixed fractional tail split, and it is narrower than 'construction changes the regime' on its own suggests.

The AUC-PR chance floor is the test prevalence: **0.682** natural against **0.252** synthetic. A raw difference across arms straddles a floor that moved 43 points, so lift above floor is given and the raw cross-arm delta is not reported.

| method | natural AUC-PR (lift) | synthetic AUC-PR (lift) |
|---|---|---|
| proposed detector | 0.728 (+0.046) | 0.545 (+0.293) |
| HST | 0.589 (-0.093) | 0.514 (+0.261) |
| ECOD | 0.755 (+0.073) | 0.419 (+0.167) |

Against that floor the natural arm is far less impressive than the raw values suggest. HST scores BELOW chance. No method clears the floor by more than **+0.073**. A high-prevalence held-out slice makes every AUC-PR look large, which is why the raw triple must not be read as a performance claim.

**Verdict (mechanical, threshold = identical ordering of methods by AUC-PR):** ranking under natural order is ECOD > proposed detector > HST; under the synthetic construction it is proposed detector > HST > ECOD. The ranking is NOT PRESERVED, but it is a **rotation, not a full reversal**: Kendall tau = -0.333, with 1 of 3 pairwise orderings preserved.

The part that does not depend on a random seed is the part worth keeping. The proposed detector and ECOD are both deterministic here, so **ECOD > proposed under natural order and proposed > ECOD under the synthetic construction is a seed-free result**. HST's placement is a single draw and is not.

## Contrast 2 — LITNET-2020, composition (labelled synthetic)

LITNET-2020's three captures are temporally disjoint, so no global chronology exists and round robin *within* a per-attack-type stream is the identity. The contrast is therefore between the three natural per-type streams and the pooled composite the literature evaluates. The pooled arm is a **labelled synthetic contrast**, not a measurement of any deployment.

| stream | construction | held-out prevalence | held-out attacks |
|---|---|---|---|
| `udp_flood` | natural (per type) | **15.775%** | 11831 |
| `blaster_worm` | natural (per type) | **3.544%** | 2658 |
| `spam` | natural (per type) | **0.176%** | 132 |
| `pooled` | **synthetic** (3-type round robin) | **6.498%** | 14621 |

The pooled composite reports a single prevalence of **6.498%**, while the constituent streams span **0.176% to 15.775%**. The composite figure is a mixture weight, not a property any of the three captures exhibits: it is manufactured by pooling.

This is an **identity, not a measurement**, and saying otherwise would dress a tautology as a finding. Equal 500,000-row budgets, a perfect three-cycle round robin, and a validation boundary at 1,275,000 = 3 x 425,000 make the pooled held-out slice exactly the union of the three natural held-out slices - the same records. Its prevalence is therefore the equal-weight mean of the three by construction. What that demonstrates is narrower than it first appears: pooling reports one number for three populations that share no prevalence, and the equal weighting is an artefact of equal budgets rather than anything about network traffic.

| stream | proposed detector | HST | ECOD |
|---|---|---|---|
| `udp_flood` (natural) | 0.394 | 0.553 | 0.321 |
| `blaster_worm` (natural) | 0.964 | 0.148 | 0.036 |
| `spam` (natural) | 0.846 | 0.008 | 0.107 |
| `pooled` (**synthetic**) | 0.943 | 0.239 | 0.229 |

### What pooling does to the method ranking

Ranking on the pooled composite: **proposed detector > HST > ECOD**.

- `udp_flood` (natural): HST > proposed detector > ECOD  — **differs from the composite**
- `blaster_worm` (natural): proposed detector > HST > ECOD  — matches the composite
- `spam` (natural): proposed detector > ECOD > HST  — **differs from the composite**

**Verdict (mechanical, threshold = identical ordering):** the composite's ranking reproduces **1 of 3** natural per-type streams.

This cuts against the proposed method, and is reported for that reason. On the composite the proposed detector is best by a wide margin. Evaluated per stream in natural order it is **not** the best method on 1 of 3 streams (`udp_flood`). The composite reports a uniform dominance that the constituent streams do not show.

## Excluded cells

None. Every cell in every completed arm produced a defined metric.

