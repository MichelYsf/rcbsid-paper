# SCOPE_DECISIONS — binding framing for the honest rebuild

Authorized 2026-08-18, after Stage 1's natural-order results.

## New primary contribution

**Benchmark stream construction, not attack prevalence, produces the regime
structure the literature reports.** Detector characterization and the conformal
degeneracy are supporting findings, not the headline.

## Binding scope rules

1. **Per-stream, never composite.** The four natural-order streams
   (`litnet2020/{udp_flood,blaster_worm,spam}`, `cicids2017`) are reported
   separately, each with its own prevalence, run-length distribution, capture
   span, and results.
2. **The interleaved construction is a first-class experiment**, retained as an
   explicitly labelled *synthetic* protocol and run head-to-head against natural
   order on the same detector and baselines. This contrast is the paper's central
   evidence and carries its own manifests.
3. **The prevalence sweep is retained but relabelled**: a controlled experiment
   *on the interleaved construction*, not a claim about deployment prevalence.
   Not rerun; re-captioned with the limitation stated.
4. **Burn-rate work is confined to CICIDS2017.** LITNET captures span minutes
   (udp_flood ~4.0, blaster_worm ~1.6) and cannot host 60/360/4320-minute
   windows. The span check is reported as a finding.
5. **The rare/moderate/inverted regime taxonomy is deleted.** Measured per-stream
   prevalence is reported instead, with the explicit statement that **in natural
   order no moderate-prevalence regime exists among these datasets**.
6. **The tuning study is re-scoped** to whichever streams remain valid under 1-5;
   only what fits the caps is run, and exclusions are documented.

## Corrected incidents created by this re-scope

Recorded here rather than silently changing prior text.

### CI-1 — "moderate prevalence regime (22.06%)" withdrawn
Prior artifacts (RUN_REPORT, findings_prevalence, DONE_ALL) describe CICIDS2017
as a moderate-prevalence regime at 22.06% (test slice 25.240%). Under natural
chronological order the CICIDS2017 test slice is **68.235%** attacks
(manifest `stage1_natural_streams_20260818T114117_285582fc`). The 22.06% figure
describes the *interleaved synthetic* construction only. The regime label is
withdrawn; the number survives solely as a property of the synthetic protocol.

### CI-2 — "LITNET = 5.2% rare-attack regime" withdrawn as a stream property
LITNET's 5.207% is a pooled rate across three temporally disjoint captures.
Per-stream natural-order test prevalence is 15.775% (udp_flood), 3.544%
(blaster_worm), 0.176% (spam). No single LITNET prevalence exists; the pooled
figure is an artifact of composition.

### CI-3 — sustained-attack and burn-rate claims restricted
LITNET attack runs are near-isolated single flows (median 1; max 2-20).
Sustained-detection, dwell-time and burn-rate-escalation claims are untestable
on LITNET and are confined to CICIDS2017 (median 2, p90 70, max 2522).

### CI-4 — prior tuning results are scoped to the synthetic protocol
The Stage 3 tuning study (11/14 finals, branch `exp/prevalence-and-tuning`) ran
entirely on interleaved composites. Those numbers remain valid *as measurements
of the synthetic protocol* and are relabelled accordingly; they are not
evidence about natural-order behaviour.

### CI-5 — the provenance gate's soundness was overstated a second time
On 2026-08-17 the gate was found to pass vacuously on an absent or empty target
set; that hole was closed and the gate was then treated as proven. On
2026-08-19 a second hole was found in the same function: a macro was resolved
as `index[name][-1]`, the manifest written *last*. Manifests are appended, and
parallel experiment arms legitimately re-emit shared macros (feature
dimensionality, for one), so two arms disagreeing about a symbol would have
been resolved silently in favour of whichever finished second — while the
manuscript number still reported as "traces to a run manifest".

Corrected: a macro claimed by two manifests with different values is now a
failure in its own right (`AMBIGUOUS`), independent of whether the manuscript
agrees with one of them, with three regression tests. What is withdrawn is not
a number but a claim about the gate: any statement that the gate was *proven*
sound before 2026-08-19 should be read as "passed the tests written for it at
the time". No published number is affected — no macro in the current index has
conflicting values — but the assurance the gate provided was weaker than
recorded, and that is the kind of thing this file exists to say out loud.

### CI-6 — two smoke-test manifests were live in the provenance store
The CI-5 ambiguity check, run for the first time on 2026-08-19, immediately
found three manifests named `s4_construction_contrast` claiming the same macros
with different values. Two were smoke tests taken while the S4 harness was
being designed — `budget` 9,000 and 30,000 records against a prefix of the
LITNET streams, 193 s and 287 s of wall time, writing `_smoke_litnet.csv` and
`_smoke2.csv`. The third, `…T124510_2b2d27b1`, is the real full-stream run
(62,609 s) whose values are the ones in the committed CSV.

They have been moved to `results/manifests/superseded/` with the reason
recorded there. Nothing was deleted; the directory is outside the non-recursive
glob that builds the macro index, so the manifests survive in git history
without contributing numbers.

What is withdrawn is a piece of confidence, not a number. The manuscript would
in fact have carried the correct values, because the index is built from
`sorted(glob(...))` and the canonical run's timestamped filename happens to
sort last. That is an accident of when the smoke tests were taken. Had either
been run an hour later, a 9,000-row prefix measurement would have entered the
manuscript under the full run's macro names, and every check in place at the
time would have reported green. Smoke tests must not write into the same
provenance store as results; until the harness enforces that, the ambiguity
check is what stands between a trial run and the manuscript.

### CI-7 — the CICIDS2017 "whole week" is a 76.63% budgeted subsample
Stage 1 describes `cicids2017_natural.csv` as the whole capture week at
1,600,000 rows. That figure is exactly round because it is a **budget, not a
census**: `scripts/build_cicids_labeled.py` assigns each day a fixed quota
(300k/300k/350k/300k/350k) and proportionally stride-subsamples the day to fit.
Measured and manifested by `scripts/audit_cicids_subsample.py`:

| quantity | value |
|---|---|
| raw rows in the improved per-day CSVs | 2,099,976 |
| dropped for a ` - Attempted` label | 11,979 |
| eligible rows | 2,087,997 |
| rows actually used | 1,600,000 (**76.63%**) |
| true eligible-week prevalence | **24.2065%** |
| subsampled prevalence | **22.0601%** |
| bias from the fixed budgets | **-2.1464 pp** |

The subsample preserves prevalence *within* each day but not the mix *between*
days, because a fixed quota cuts a larger day harder and the attack-heavy days
are the largest. Retention runs from 64.4% (Friday, 46.91% attacks) to 93.2%
(Tuesday, 2.15% attacks) — that is, retention is anti-correlated with attack
density, which is precisely the direction that lowers measured prevalence.

**What this does and does not touch.** It does *not* affect the S4 construction
contrast: both arms hold the identical record multiset and differ only in
order, so the order-only comparison stands exactly as measured. What it
qualifies is the *absolute* prevalence figures. The "22.06% moderate regime"
was therefore doubly constructed — first by a subsampling budget that removed
2.15 pp of prevalence, then by an interleaving that redistributed what was
left. Neither step is a property of network traffic. The natural-order
68.235% held-out figure is likewise conditioned on this subsample; the
qualitative finding (chronological order concentrates attacks in the tail)
does not depend on it, but the exact number does and must be stated with it.

No prior number is withdrawn. What is corrected is the description: "whole
week" should read "76.63% proportional subsample of the capture week, with a
-2.15 pp prevalence bias from fixed per-day budgets".

### CI-8 — a crashed job was recorded as a timeout
On 2026-08-19 the CICIDS natural contrast arm was killed by the Linux OOM
killer at 8,680 s (anon-RSS 10,450,436 kB; `dmesg` confirms `oom-kill` on pid
6043). The runner's failure recorder hardcoded one sentence for every failure
mode, so the durable exclusion it wrote read:

> TIMEOUT: job exceeded the 8680s per-job ceiling and was terminated

Both halves are false. The ceiling is 43,200 s, not 8,680 s, and the cause was
memory exhaustion, not elapsed time. A reviewer reading that exclusion would
have concluded the arm was too slow and that the fix was a longer ceiling —
the opposite of the truth, which is that two arms peaked in ECOD at the same
moment on a 16 GB box.

Corrected: failures now record their real cause, with signal decoding
(`SIGKILL` is reported as probable OOM), the elapsed time and the true ceiling
in separate columns, and four regression tests including an end-to-end one
asserting an OOM record never mentions a ceiling. The arm itself was re-run to
completion rather than left excluded, so no result rests on this.

The general rule this incident argues for: an excluded cell that states the
wrong reason is worse than a missing file, because a missing file invites
investigation while a confident wrong reason closes it.
