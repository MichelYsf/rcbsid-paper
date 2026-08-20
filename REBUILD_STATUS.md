# CALIBURN honest rebuild — status

- **State**: S4 COMPLETE. Cloud compute finished and torn down.
- **Last update**: 2026-08-20 08:25 UTC
- **Branch**: `rebuild/honest-v1`
- **Framing**: `SCOPE_DECISIONS.md` (per-stream, never composite; the construction
  contrast is the headline; 14 corrected incidents recorded)
- **Gate**: green — 165 manifested macros, 0 orphans, 0 mismatches, 0 ambiguous,
  macro index verified against its manifests. 72 tests pass.

## Cloud state — nothing is running, nothing is billing

`i-0a8e79006a8f2c143` **terminated**; `vol-036c8ec7a9d442f29` **verified deleted**
(confirmed by `InvalidVolume.NotFound`, not by trusting `DeleteOnTermination`);
`snap-0aa6eab53f0e59c31` deleted. No instances and no volumes remain in
eu-central-1.

**Measured cost, this run: $4.86** (list prices; Cost Explorer lags ~24 h and is
the authority) — 8.07 h compute at $0.4032/h = $3.25, plus 25.79 h of gp3 at
$0.0624/h = $1.61. The volume kept billing through the ~18 h the instance sat
stopped, which is most of the EBS line.

Caps: the 8 h wall cap was enforced by the watchdog at 14:22:03Z on 2026-08-19
and the experiment consumed 7.97 h of it. A further ~0.1 h was spent the next
day starting the instance to retrieve results before destroying the volume;
that is compute outside the experiment's 8 h and is recorded here rather than
folded in. The $6 spend cap was not reached.

**Still billing, NOT from this run:** three 100 GiB snapshots from the earlier
finals missions (`snap-0c3f130db41ed7586` 2026-08-17, `snap-09be952951db9af1e`
and `snap-008f2633123c89f4f` 2026-08-13). Roughly $2–3/month depending on used
blocks. Left in place — they are prior-mission data and deleting them is the
operator's call.

## What S4 established

Four primary arms, full streams, no excluded cells. Both synthetic arms
reproduce the published evaluations exactly (CICIDS 25.2396% / 60,575 attacks;
LITNET 6.498% / 14,621), so neither is a strawman.

**The seed-free result the argument rests on.** The proposed detector and ECOD
are deterministic here, so this cannot move with a seed:

> ECOD > proposed under true chronological order (0.755 vs 0.728), and
> proposed > ECOD under the day-of-week interleaving (0.545 vs 0.419).

A plain batch reference is best under natural order and worst under the
synthetic construction, on the identical record multiset.

**Read with its floor.** AUC-PR's chance floor is the test prevalence — 0.682
natural, 0.252 synthetic. Against floor no method clears 0.073 on the natural
arm and HST sits 0.093 *below* chance. The natural triple is not a performance
claim. Cross-arm raw deltas are not reported at all.

**The −42.995 pp prevalence shift is dilution, not redistribution.** The two
held-out slices share 78,000 of 240,000 records (32.5%); the synthetic
held-out attacks are a strict subset of the natural ones; 103,189 attacks move
into training; every synthetic held-out attack is a Friday record; and the
natural held-out slice is one 204.2-minute Friday-evening window.

## Open, and blocking for the manuscript

1. **Rankings are seed-fragile (CI-10).** On the LITNET composite, HST across
   seeds 11/23/47 is 0.2388 / 0.1776 / 0.3678 (mean 0.2614, sd 0.0971) against a
   deterministic ECOD 0.2291 — **the ordering flips**. No ranking count and no
   per-stream ranking attribution may enter the manuscript. Needs ≥3 seeds on
   the three LITNET per-type natural streams and the CICIDS natural arm; the
   latter's seed-23 run was killed mid-job by the cost cap.
2. **Method asymmetries are disclosed but not controlled.** ECOD is fitted on
   benign-only training data (it uses labels); HST adapts through test; the
   proposed detector uses a fixed untuned threshold while the baselines get
   validation F1-argmax. Every precision/recall/F1/threshold column in
   `results/construction_contrast.csv` is non-comparable across methods.
3. **No split-rule sensitivity check.** Every construction effect is measured
   under a fixed 70/15/15 tail split.

## Stages remaining

S3, S5, S6, S7, S8 and WRAP are unstarted: score/threshold prose honesty,
verified contributions, the corrected-BOCPD ablation (≤90 min), the ACM
manuscript rebuild, missing related work, the GenAI usage statement, the
companion-paper disclosure, and `PUBLISH_INSTRUCTIONS.md`. Nothing is published
or submitted anywhere.
