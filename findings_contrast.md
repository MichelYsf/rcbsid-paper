# findings_contrast — construction, not prevalence (Stage 4)

Generating run: `s4_contrast_deliverables_20260819T113331_a7a5eadd`.
Every number below is a provenance macro from this run's manifest or from the per-arm manifests it aggregates.

**Claim under test.** Benchmark stream *construction*, not attack prevalence, produces the regime structure the intrusion-detection literature reports.

## Contrast 1 — CICIDS2017, order only (prevalence held constant)

CICIDS2017 is a single capture week, so the same record multiset can be presented in true timestamp order and in day-of-week round robin. Whole-stream prevalence is *identical by construction*; only the order differs. Any change in the measured regime is therefore attributable to construction alone.

| quantity | natural (timestamp order) | synthetic (day round robin) |
|---|---|---|
| held-out prevalence | **68.235%** | **25.240%** |
| held-out attacks | 163764 | 60575 |

The two arms hold the same records. Reordering alone moves the held-out prevalence by **-42.995 percentage points**, which is the whole of the effect: no attack was added, removed, or resampled.

| method | AUC-PR natural | AUC-PR synthetic | delta (syn - nat) |
|---|---|---|---|
| proposed detector | 0.728 | 0.545 | -0.183 |
| HST | 0.589 | 0.514 | -0.075 |
| ECOD | 0.755 | 0.419 | -0.336 |

**Verdict (mechanical, threshold = identical ordering of methods by AUC-PR):** ranking under natural order is ECOD > proposed detector > HST; under the synthetic construction it is proposed detector > HST > ECOD. The ranking is NOT PRESERVED.

## Contrast 2 — LITNET-2020, composition (labelled synthetic)

LITNET-2020's three captures are temporally disjoint, so no global chronology exists and round robin *within* a per-attack-type stream is the identity. The contrast is therefore between the three natural per-type streams and the pooled composite the literature evaluates. The pooled arm is a **labelled synthetic contrast**, not a measurement of any deployment.

| stream | construction | held-out prevalence | held-out attacks |
|---|---|---|---|
| `udp_flood` | natural (per type) | **15.775%** | 11831 |
| `blaster_worm` | natural (per type) | **3.544%** | 2658 |
| `spam` | natural (per type) | **0.176%** | 132 |
| `pooled` | **synthetic** (3-type round robin) | **6.498%** | 14621 |

The pooled composite reports a single prevalence of **6.498%**, while the constituent streams span **0.176% to 15.775%**. The composite figure is a mixture weight, not a property any of the three captures exhibits: it is manufactured by pooling.

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

