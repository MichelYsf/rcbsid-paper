# Findings: prevalence sweep within CICIDS2017 (Stage 2)

The paper's regime-dependence claim confounds attack prevalence with dataset identity. This experiment holds the dataset fixed (the same interleaved corrected CICIDS2017 stream) and varies prevalence by stratified resampling: 5, 10, 22.06 (natural), 40, 64 percent, three resample seeds (11/23/47). CALIBURN is deterministic; the variance source is the resampling draw.

## Headline table (AUC-PR, mean over resample seeds)

| prevalence | CALIBURN (raw) | best streaming | best batch | chance floor |
|---|---|---|---|---|
| 5% | 0.367 | 0.208 (loda) | 0.538 (lof) | 0.050 |
| 10% | 0.447 | 0.300 (hst) | 0.697 (lof) | 0.100 |
| 22.06% | 0.545 | 0.433 (hst) | 0.863 (lof) | 0.221 |
| 22.0601% | 0.545 | nan (loda) | nan (lof) | 0.221 |
| 40% | 0.494 | 0.476 (hst) | 0.897 (lof) | 0.400 |
| 64% | 0.620 | 0.525 (loda) | 0.905 (lof) | 0.640 |

## Question 1: low-prevalence advantage

At 5% prevalence CALIBURN's AUC-PR is 0.367 vs 0.208 for the best streaming baseline (lead +0.160) and 0.538 for the best batch reference (lead -0.170). At natural prevalence the same leads are +0.112 (streaming) and -0.318 (batch).

**Verdict (mechanical, threshold = lead > 0):** the low-prevalence advantage REPRODUCES against the streaming group but NOT against the batch reference when prevalence is lowered inside CICIDS2017 alone.

## Question 2: high-prevalence collapse (CRC mechanism)

| prevalence | V1 F1 | V1 alert rate | V1 CRC tau | V3 FPR | V4 F1 | CALIBURN AUC-PR minus floor |
|---|---|---|---|---|---|---|
| 5% | 0.000 | 0.0000 | 0.235 | 0.150 | 0.406 | +0.317 |
| 10% | 0.000 | 0.0000 | 0.318 | 0.175 | 0.600 | +0.347 |
| 22.06% | nan | nan | nan | nan | nan | +0.324 |
| 22.0601% | 0.000 | 0.0000 | 0.485 | 0.999 | 0.695 | +0.324 |
| 40% | 0.000 | 0.0000 | 0.599 | 1.000 | 0.471 | +0.094 |
| 64% | 0.000 | 0.0000 | 0.705 | 1.000 | 0.229 | -0.020 |

**Verdict (mechanical):** V1 F1 < 0.05 at every level >= 40%: True. V1 F1 > 0.10 at some level <= 10%: False. CALIBURN AUC-PR within 0.05 of the prevalence floor at every level >= 40%: False. The high-prevalence collapse DOES NOT fully reproduce inside one dataset, and the ranking degeneracy near the floor does not accompany it.

## Interpretation constraint

Because the dataset, features, preprocessing, and stream construction are identical across levels, any pattern above is attributable to prevalence (and the resampling it requires), not to dataset identity. Where the within-dataset pattern matches the cross-dataset Figure 5 pattern, the regime-dependence reading survives this control; where it does not, the cross-dataset pattern was carrying dataset-identity effects.

Construction notes: stratified per-split resampling (see RUN_REPORT and commit d8d0796) was required because the interleaved stream has a structural attack-share gradient across splits; above-natural levels retain 97.3% of attacks. The natural column reuses the bit-exact Stage 1 rows for baselines (provenance column in the CSV) and recomputes CALIBURN through the sweep harness as the internal control.
