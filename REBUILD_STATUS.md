# CALIBURN honest rebuild — status

- **State**: S0-S8 complete; superseded as a live status file by `REBUILD_DONE.md` and `TRIAGE_REPORT.md`. Retained as a dated snapshot. No cloud in use; nothing billing.
- **Last update**: 2026-08-27 (counts and stage status reconciled; the narrative below is the 2026-08-20 snapshot) (Stage 6 closed out)
- **Branch**: `rebuild/honest-v1`
- **Framing**: `SCOPE_DECISIONS.md` (per-stream, never composite; the construction
  contrast is the headline; every corrected incident recorded, count not quoted)
- **Gate**: green — 564 manifested macros, 0 orphans, 0 mismatches, 0 ambiguous,
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

**Region is empty.** On 2026-08-20 the three remaining 100 GiB snapshots from
the earlier finals missions were deleted on the operator's instruction:
`snap-09be952951db9af1e` and `snap-008f2633123c89f4f` (2026-08-13, both of
`vol-01968761956323f00`, an incremental chain) and `snap-0c3f130db41ed7586`
(2026-08-17, of `vol-049e26b01e2604a7c`). Each is individually confirmed gone
by `InvalidSnapshot.NotFound`, and eu-central-1 now holds **0 snapshots,
0 volumes and 0 non-terminated instances**. Estimated recurring storage cost
avoided: **~$1.30-2.20/month** (an estimate: the account lacks
ebs:ListSnapshotBlocks, so actual stored blocks could not be measured).
No AWS resource from this project is billing.

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
3. **The construction effects are measured under one split rule** (a fixed
   70/15/15 tail split). A2 later swept seven chronological cuts from 60% to
   90% and found the measured ordering changes with the cut, so the fixed
   split is not neutral either; the contrast itself was not re-run per cut.

## Stages remaining

**S7 and S8 are complete** (`REBUILD_DONE.md` is the terminal record); what follows is kept as the plan they were run against:
the ACM manuscript rebuild, missing related work, the GenAI usage statement, the
companion-paper disclosure, `PUBLISH_INSTRUCTIONS.md`, and WRAP. Nothing is
published or submitted anywhere.

S6 ran inside a 30-minute local cap (22.3 min ablation + 2.0 min diagnostic) and
established a **failure mode, not a working correction**: the corrected reset
branch makes P(r=0) respond (1000x) but saturates the composed score, 92.7% of
values at exactly 0.25, AUC-ROC 0.5096. Both variants are degenerate in opposite
directions. Stage 5's ChangePoint verdict stays WITHDRAWN.
