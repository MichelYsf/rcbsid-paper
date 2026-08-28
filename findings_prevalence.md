# findings_prevalence — prevalence *within the synthetic construction* (Stage 2)

Generating run: `s2_prevalence_relabelled_20260827T140708_90bc36cd`. Every number below is a provenance macro.

## What this experiment is, and is not

It holds the dataset fixed — **the interleaved (synthetic) CICIDS2017 stream** — and varies attack prevalence by stratified resampling. Under binding scope rule 3 it is retained and relabelled: a controlled experiment *on a synthetic construction*, **not** evidence about prevalence in deployment. It has not been rerun.

Under rule 5 the rare/moderate/inverted regime taxonomy is deleted. Under CI-1 the level previously captioned "22.06% (natural)" is relabelled **unresampled**: in true timestamp order the CICIDS held-out prevalence is 68.235%, and nothing in this experiment is natural order. 22.06% is the interleaved stream's whole-stream prevalence; its held-out prevalence is 25.240%.

## AUC-PR by prevalence level

Mean over three resampling draws (seeds 11/23/47), with standard deviation and the per-draw values. **Lift is measured against the achieved held-out prevalence**, which is the AUC-PR chance floor.

| level | chance floor | proposed detector | HST | LODA | ECOD (batch) | LOF (batch) |
|---|---|---|---|---|---|---|
| 5% | 0.0495 | 0.3672 ±0.0005<br><sub>0.3670, 0.3668, 0.3677</sub> | 0.1993 ±0.0810<br><sub>0.2806, 0.1986, 0.1186</sub> | 0.2076 ±0.0069<br><sub>0.2008, 0.2146, 0.2074</sub> | 0.1662 ±0.0008<br><sub>0.1671, 0.1661, 0.1656</sub> | 0.5376 ±0.0008<br><sub>0.5381, 0.5380, 0.5367</sub> |
| 10% | 0.0990 | 0.4472 ±0.0024<br><sub>0.4499, 0.4465, 0.4452</sub> | 0.2997 ±0.0989<br><sub>0.4002, 0.2964, 0.2025</sub> | 0.2474 ±0.0055<br><sub>0.2411, 0.2501, 0.2511</sub> | 0.2522 ±0.0003<br><sub>0.2520, 0.2520, 0.2526</sub> | 0.6970 ±0.0010<br><sub>0.6981, 0.6960, 0.6969</sub> |
| unresampled | 0.2524 | 0.5450 ±0.0000 *det*<br><sub>0.5450, 0.5450, 0.5450</sub> | 0.4330 ±0.0777<br><sub>0.5136, 0.4270, 0.3585</sub> | 0.3417 ±0.0047<br><sub>0.3389, 0.3391, 0.3472</sub> | 0.4190 ±0.0000 *det*<br><sub>0.4190, 0.4190, 0.4190</sub> | 0.8632 ±0.0000 *det*<br><sub>0.8632, 0.8632, 0.8632</sub> |
| 40% | 0.4000 | 0.4942 ±0.0017<br><sub>0.4962, 0.4932, 0.4933</sub> | 0.4760 ±0.0561<br><sub>0.5407, 0.4456, 0.4417</sub> | 0.3994 ±0.0050<br><sub>0.4025, 0.3937, 0.4021</sub> | 0.5274 ±0.0007<br><sub>0.5281, 0.5271, 0.5268</sub> | 0.8970 ±0.0060<br><sub>0.8934, 0.8936, 0.9039</sub> |
| 64% | 0.6400 | 0.6195 ±0.0011<br><sub>0.6184, 0.6197, 0.6206</sub> | 0.4993 ±0.0316<br><sub>0.5180, 0.4629, 0.5171</sub> | 0.5247 ±0.0049<br><sub>0.5297, 0.5198, 0.5246</sub> | 0.6784 ±0.0005<br><sub>0.6784, 0.6789, 0.6779</sub> | 0.9049 ±0.0100<br><sub>0.9141, 0.9061, 0.8943</sub> |

`*det*` marks a cell identical across all three draws. At the unresampled level no resampling occurs, so every draw sees the same records and the deterministic methods return identical values; at the resampled levels their small spread is the draw, not the model.

## Lift above chance

Additive lift `AP-p` has a ceiling of `1-p`, so it is not comparable across levels; the normalized form `(AP-p)/(1-p)` is given beneath each additive value.

| level | proposed detector | HST | LODA | ECOD (batch) | LOF (batch) |
|---|---|---|---|---|---|
| 5% | +0.3176<br><sub>norm +0.3342</sub> | +0.1497<br><sub>norm +0.1575</sub> | +0.1581<br><sub>norm +0.1663</sub> | +0.1167<br><sub>norm +0.1228</sub> | +0.4881<br><sub>norm +0.5135</sub> |
| 10% | +0.3482<br><sub>norm +0.3865</sub> | +0.2007<br><sub>norm +0.2228</sub> | +0.1484<br><sub>norm +0.1647</sub> | +0.1532<br><sub>norm +0.1700</sub> | +0.5980<br><sub>norm +0.6637</sub> |
| unresampled | +0.2926<br><sub>norm +0.3914</sub> | +0.1806<br><sub>norm +0.2416</sub> | +0.0893<br><sub>norm +0.1195</sub> | +0.1666<br><sub>norm +0.2228</sub> | +0.6108<br><sub>norm +0.8170</sub> |
| 40% | +0.0942<br><sub>norm +0.1570</sub> | +0.0760<br><sub>norm +0.1267</sub> | -0.0006<br><sub>norm -0.0010</sub> | +0.1274<br><sub>norm +0.2123</sub> | +0.4970<br><sub>norm +0.8283</sub> |
| 64% | -0.0204<br><sub>norm -0.0568</sub> | -0.1406<br><sub>norm -0.3907</sub> | -0.1153<br><sub>norm -0.3203</sub> | +0.0384<br><sub>norm +0.1067</sub> | +0.2649<br><sub>norm +0.7357</sub> |

## Findings

**1. A batch reference dominates at every level.** LOF's mean AUC-PR exceeds the proposed detector's at **5 of 5** levels, by 0.19 to 0.44. At the unresampled level both are identical across draws, so this comparison is **deterministic versus deterministic** and rule 7 permits it flatly: LOF 0.8632 against the proposed detector 0.5450, a gap of 0.3182 on the same held-out slice.

**2. The proposed detector's lift falls as prevalence rises, and goes negative.** Lift above chance runs +0.3176 at 5%, +0.3482 at 10%, +0.2926 unresampled, +0.0942 at 40%, and **-0.0204 at 64%** — below the floor a constant predictor achieves. This is the honest form of the 'low-prevalence advantage': it is a lift-versus-prevalence gradient inside one synthetic construction, and it does not survive to high prevalence.

**3. Rankings involving HST are withheld (rule 7).** HST's standard deviation across three draws reaches 0.0989 at the 10% level and 0.0810 at 5% — larger than several gaps the previous version of this document reported as findings. Its per-draw values are printed above; no ranking claim involving HST is stated here.

**4. What this cannot show.** Every row is the interleaved construction. Stage 4 measures the same detector and baselines on the *natural-order* stream and finds a different ordering, so nothing in this table transfers to natural order or to deployment.

