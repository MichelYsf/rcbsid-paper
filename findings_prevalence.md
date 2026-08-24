# findings_prevalence — prevalence *within the synthetic construction* (Stage 2)

Generating run: `s2_prevalence_relabelled_20260824T094843_2ef126ae`. Every number below is a provenance macro.

## What this experiment is, and is not

It holds the dataset fixed — **the interleaved (synthetic) CICIDS2017 stream** — and varies attack prevalence by stratified resampling. Under binding scope rule 3 it is retained and relabelled: a controlled experiment *on a synthetic construction*, **not** evidence about prevalence in deployment. It has not been rerun.

Under rule 5 the rare/moderate/inverted regime taxonomy is deleted. Under CI-1 the level previously captioned "22.06% (natural)" is relabelled **unresampled**: in true timestamp order the CICIDS held-out prevalence is 68.235%, and nothing in this experiment is natural order. 22.06% is the interleaved stream's whole-stream prevalence; its held-out prevalence is 25.240%.

## AUC-PR by prevalence level

Mean over three resampling draws (seeds 11/23/47), with standard deviation and the per-draw values. **Lift is measured against the achieved held-out prevalence**, which is the AUC-PR chance floor.

| level | chance floor | proposed detector | HST | LODA | ECOD (batch) | LOF (batch) |
|---|---|---|---|---|---|---|
| 5% | 0.0495 | 0.3672 ±0.0005 | 0.1993 ±0.0810 | 0.2076 ±0.0069 | 0.1662 ±0.0008 | 0.5376 ±0.0008 |
| 10% | 0.0990 | 0.4472 ±0.0024 | 0.2997 ±0.0989 | 0.2474 ±0.0055 | 0.2522 ±0.0003 | 0.6970 ±0.0010 |
| unresampled | 0.2524 | 0.5450 ±0.0000 *det* | 0.4330 ±0.0777 | 0.3417 ±0.0047 | 0.4190 ±0.0000 *det* | 0.8632 ±0.0000 *det* |
| 40% | 0.4000 | 0.4942 ±0.0017 | 0.4760 ±0.0561 | 0.3994 ±0.0050 | 0.5274 ±0.0007 | 0.8970 ±0.0060 |
| 64% | 0.6400 | 0.6195 ±0.0011 | 0.4993 ±0.0316 | 0.5247 ±0.0049 | 0.6784 ±0.0005 | 0.9049 ±0.0100 |

`*det*` marks a cell identical across all three draws. At the unresampled level no resampling occurs, so every draw sees the same records and the deterministic methods return identical values; at the resampled levels their small spread is the draw, not the model.

## Lift above chance

| level | proposed detector | HST | LODA | ECOD (batch) | LOF (batch) |
|---|---|---|---|---|---|
| 5% | +0.3176 | +0.1497 | +0.1581 | +0.1167 | +0.4881 |
| 10% | +0.3482 | +0.2007 | +0.1484 | +0.1532 | +0.5980 |
| unresampled | +0.2926 | +0.1806 | +0.0893 | +0.1666 | +0.6108 |
| 40% | +0.0942 | +0.0760 | -0.0006 | +0.1274 | +0.4970 |
| 64% | -0.0204 | -0.1406 | -0.1153 | +0.0384 | +0.2649 |

## Findings

**1. A batch reference dominates at every level.** LOF's mean AUC-PR exceeds the proposed detector's at **5 of 5** levels, by 0.19 to 0.44. At the unresampled level both are identical across draws, so this comparison is **deterministic versus deterministic** and rule 7 permits it flatly: LOF 0.8632 against the proposed detector 0.5450, a gap of 0.3182 on the same held-out slice.

**2. The proposed detector's lift falls as prevalence rises, and goes negative.** Lift above chance runs +0.3176 at 5%, +0.3482 at 10%, +0.2926 unresampled, +0.0942 at 40%, and **-0.0204 at 64%** — below the floor a constant predictor achieves. This is the honest form of the 'low-prevalence advantage': it is a lift-versus-prevalence gradient inside one synthetic construction, and it does not survive to high prevalence.

**3. Rankings involving HST are withheld (rule 7).** HST's standard deviation across three draws reaches 0.0989 at the 10% level and 0.0810 at 5% — larger than several gaps the previous version of this document reported as findings. Its per-draw values are printed above; no ranking claim involving HST is stated here.

**4. What this cannot show.** Every row is the interleaved construction. Stage 4 measures the same detector and baselines on the *natural-order* stream and finds a different ordering, so nothing in this table transfers to natural order or to deployment.

