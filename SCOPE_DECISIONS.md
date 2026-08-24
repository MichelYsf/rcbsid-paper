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

7. **No ranking claim from a single seed.** For any method with a stochastic
   component, a ranking may be stated only if the seed distribution is reported
   explicitly alongside it; otherwise the claim is withheld. **Deterministic
   versus deterministic is the only comparison the paper may state flatly.**
   Forced by measurement, not caution: on the LITNET composite, HST across
   seeds 11/23/47 is 0.2388 / 0.1776 / 0.3678 (mean 0.2614, sd 0.0971) against
   a deterministic ECOD 0.2291 — the ordering flips with the seed, so the
   "composite ranking matches 1 of 3 streams" count was stable only by
   accident, while the stream it named changed. In this contrast the proposed
   detector and ECOD are deterministic and HST is not; every flat ranking
   statement must therefore be a proposed-versus-ECOD statement.

8. **The central claim, stated exactly as measured.** The paper's primary
   contribution is the construction contrast, and it is to be written in these
   terms and no stronger:

   > On CICIDS2017, holding the record multiset identical and changing only the
   > order, the held-out prevalence moves by 42.995 percentage points
   > (68.235% → 25.240%), the held-out slice becomes nearly disjoint from the
   > natural one (78,000 of 240,000 records shared, 32.5%), and the
   > deterministic ordering of ECOD against the proposed detector inverts
   > (ECOD 0.755 > proposed 0.728 natural; proposed 0.545 > ECOD 0.419
   > synthetic).

   Three things this is **not**, and may not be written as:
   - **not a full ranking reversal** — it is a rotation, Kendall tau -0.333,
     with 1 of 3 pairwise orderings preserved (proposed > HST holds in both);
   - **not a causal claim about prevalence in deployment** — the effect is
     measured under a fixed 70/15/15 tail split, no split-rule sensitivity
     check exists, and the mechanism is dilution by attack-free days rather
     than any redistribution of attacks;
   - **not a performance claim** — read against a chance floor equal to test
     prevalence, no method clears floor by more than 0.073 on the natural arm
     and HST sits 0.093 below it.

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

### CI-9 — manifests named the commit at write time, not the code that ran
`ProvenanceRun.to_dict()` called `git_commit()` when the manifest was written.
A run that takes hours outlives edits to its own repository, so three S4
contrast arms that started on `99805a9` and ran ~2.5 h were recorded as
`1fbc615` — a commit made two hours after they began, when the instance
checkout was updated mid-run. The manifests were internally consistent and
completely wrong about which code produced the numbers.

Corrected: the commit is captured at construction and recorded as
`git_commit`; the write-time commit is kept beside it as
`git_commit_at_write`, with `repo_changed_during_run` set when they differ, so
a repository edited mid-run is visible instead of silent. Two regression tests.

> **This section is corrected by CI-12.** The attribution table below is
> wrong in three places. It is left in place rather than edited, because
> corrections are recorded here, not silently applied.

**True attribution of the four S4 arms**, established from the diffs rather
than from the manifests:

| arm | manifest says | actually ran |
|---|---|---|
| `litnet_natural` | `db004dc` | `db004dc` (correct) |
| `litnet_synthetic` | `1fbc615` | `99805a9` |
| `cicids_synthetic` | `1fbc615` | `99805a9` |
| `cicids_natural` | `1fbc615` | `99805a9` |

`git diff 99805a9 HEAD -- scripts/run_construction_contrast.py src/` is empty,
so the last three arms ran harness code identical to the current tree. The one
real difference is `db004dc → 99805a9`, which `litnet_natural` predates: that
commit adds `import gc`, `del` statements, `gc.collect()` calls, makes a
`frames.append` conditional, and drops a redundant `.copy()` whose callee
returns a new frame regardless. Every change is memory management; none alters
a computed value, and most of it lies in the CICIDS synthetic path that
`litnet_natural` never executes.

`litnet_natural` has therefore **not** been re-run. Re-running it would cost
17.4 h to reproduce values the diff shows cannot change. That is a judgement,
and it is recorded here so a reviewer can disagree with it rather than
discover it.

### CI-10 — every ranking in Stage 4 rests on a single HST draw
`--seeds` defaults to `[11]`, and the proposed detector is hardcoded to seed 11
and runs once. The proposed detector and ECOD are deterministic on this data,
so **one HST sample decides each reported ranking**. The LITNET composite's
second/third place turns on a margin of 0.0097 (HST 0.2388 against ECOD
0.2291) while HST's own published standard deviation on that identical
225,000-row composite is 0.097 to 0.253 (`results/table4_litnet_tuned.tex`,
raw seeds 0.259 / 0.530 / 0.765). The margin is roughly a tenth of a standard
deviation: the "composite ranking matches 1 of 3 streams" count is not
established.

Partially addressed rather than fixed. Extra HST seeds were bought within the
run's wall cap for the LITNET composite (seeds 23 and 47) and for both CICIDS
arms (seed 23); the three LITNET per-type natural streams could not be covered
before the cap. Until every cell has at least three seeds, no ranking COUNT and
no per-stream ranking attribution may enter the manuscript.

What does survive seeding, and is stated in `findings_contrast.md` for that
reason: the proposed detector and ECOD are both deterministic here, so
**ECOD > proposed under natural order and proposed > ECOD under the synthetic
construction** is a seed-free result. HST's placement is not.

### CI-11 — the Stage 4 findings document printed orphan numbers
Adversarial review REFUTED the sentence "every number below is a provenance
macro". Seven of thirty-three printed numbers had no `emit_macro` call: the
three AUC-PR delta values and the four LITNET held-out attack counts. One of
them, the pooled count **14,621**, appeared in no manifest anywhere in the
repository while being written as a bare literal into
`results/table_construction_contrast.tex`, which is manuscript-bound. That is
precisely the orphan the governing rule forbids, produced by the machinery
built to prevent it.

Two things also became clear about the gate's reach. It targets
`paper/numbers.tex` only and parses `\newcommand` definitions only, so it never
read the findings document or the LaTeX table at all; and because
`numbers.tex` is generated *from* the macro index it is checked against, a pass
immediately after generation demonstrates faithful transcription and nothing
stronger. `emit_numbers_tex.py` said so in its header, but the gate's own PASS
message did not, and this file had not logged it.

Corrected: every number the generator prints is now emitted as a macro, and the
LaTeX table carries **macro references only** — no data literal survives in it,
so a number cannot again sit in a manuscript-bound file outside the gate's
view. The cross-arm delta column was removed outright (see CI-13).

### CI-12 — CI-9's own attribution table was wrong
The correction written to fix commit attribution was itself misattributed, in
three places. Commit timestamps are `+03:00`; converting to UTC:
`db004dc` 06:06:29Z, `99805a9` 06:37:44Z, `1fbc615` 06:59:44Z.

| arm | started (UTC) | manifest records | actually ran |
|---|---|---|---|
| `litnet_natural` | 2026-08-18 12:45:10 | `db004dc` | an **uncommitted working tree** — the harness was committed 100 s later as `4edfeb0` |
| `litnet_synthetic` | 2026-08-19 06:40:27 | `1fbc615` | `99805a9` |
| `cicids_synthetic` | 2026-08-19 06:40:27 | `1fbc615` | `99805a9` |
| `cicids_natural` | 2026-08-19 09:08:13 | `1fbc615` | `1fbc615` — **the manifest was right** |

So: (1) CI-9 filed `cicids_natural` under `99805a9`, but that arm is the
*re-run* after the OOM, started two hours after `1fbc615` was committed — its
manifest was correct and my correction was not. (2) CI-9 said the repository
moved "two hours after they began"; the real gap is **19 minutes**. (3) CI-9
called `litnet_natural`'s `db004dc` "correct", but that arm started 17.4 hours
before `db004dc` existed, from a tree where `run_construction_contrast.py` was
not yet committed to anything. Its recorded commit is a write-time artefact
like the others.

The value-neutrality conclusion is unaffected: `db004dc` does not touch the
harness, so the only harness difference between `litnet_natural` and the rest
remains the `4edfeb0 → 99805a9` memory-management commit, verified by diff to
change no computed value. What was wrong was the labelling, twice over — first
in the manifests, then in the correction of the manifests. That is the argument
for capturing the commit at run start in code, which is now done, rather than
reconstructing it by hand afterwards.

### CI-13 — the macro index drifted silently, and AUC-PR was compared across moving floors
Two further findings from the same review.

**The index.** `results/manifests/macro_index.json` was found in the working
tree carrying 78 macros where the manifests on disk supported 121 — every
Stage 4 number the manuscript cites had vanished from it, while the manifests
that produced them sat untouched beside it. The index is a *derived* artefact
that any process running the reindexer against a different manifest directory
can rewrite, and the gate read it without checking it. A gate that trusts a
derived artefact will report that a vanished number still traces to a manifest.
Corrected: the gate now rebuilds the index from the manifests and FAILS on any
drift — macros missing, macros with no manifest behind them, or values that
disagree — with four regression tests.

**The floor.** AUC-PR's chance floor equals the test prevalence, which is
exactly the quantity the construction moves (0.682 natural against 0.252
synthetic). The published "delta (syn − nat)" column therefore subtracted
across a floor that had shifted 43 points. Read against their floors, *every*
method scores higher on the synthetic arm, and in the natural arm HST sits
**0.093 below chance** while nothing clears the floor by more than 0.073 — so
the natural triple must not be read as a performance claim at all. The delta
column is withdrawn; lift above floor is reported beside every raw value.

### CI-14 — the cost watchdog stopped the box on a stale completion marker
The instance watchdog stopped when it saw
`results/rebuild_parts/contrast_done.json`, on the assumption that the marker
meant the machine was idle. When the re-run of the CICIDS natural arm finished
at 11:32Z the runner rewrote that marker; the watchdog read it, slept its
30-minute grace and shut the instance down at 12:02Z — three minutes after a
new set of seed jobs had been launched on it. Those jobs were lost.

Nothing else was: stopping preserves the volume by design, all four primary
arms were already committed and pushed, and the instance was restarted and the
jobs relaunched inside the same wall cap. The watchdog is now **deadline-only**.
A completion marker written by one job is not evidence that a machine is idle,
and a cost guard that infers idleness from a file another process controls will
eventually kill live work.

### CI-15 — the prevalence sweep's chance floor was wrong at the unresampled level
`findings_prevalence.md` printed a chance floor of 0.221 for the level it
captioned "22.06% (natural)". That level is **not** resampled to a target — it
keeps the interleaved stream's own held-out slice, whose achieved prevalence is
**0.252396**. AUC-PR's floor is the test prevalence, so the floor was
understated by 3.2 points and every lift reported at that level was inflated by
the same amount. The proposed detector's lift there is **+0.2926**, not the
+0.324 the old floor implied.

The four resampled levels were unaffected — their achieved prevalence lands on
the target (0.0495, 0.0990, 0.4000, 0.6400) — which is precisely why the error
survived: four rows of five were right, so the column looked consistent.

Corrected in the relabelled Stage 2 deliverable, which now takes every floor
from `achieved_test_prev` rather than from the nominal level, and prints the
floor beside every value. The caption "22.06% (natural)" was the CI-1 error
verbatim and is replaced by "unresampled".

### CI-16 — cloud time was spent re-deriving a seed the repository already held
The Stage 2 sweep's unresampled cell is not merely comparable to the Stage 4
CICIDS interleaved arm — **it is the same cell**: the same 240,000-row held-out
slice at the same achieved prevalence 0.252396. It already contained HST at
three seeds. On 2026-08-19 an EC2 instance was started to buy a *second* HST
seed for that cell, at 5,732 s of compute, re-deriving 0.4270 — a value already
sitting in `results/prevalence_sweep_cicids.csv`. Check the archived artifacts
before buying compute; the cost here was small but the mistake was avoidable
and entirely mine.

**A claim is corrected by this.** With only seeds 11 and 23 the Stage 4 seed
section reported that on CICIDS interleaved "HST stays ahead of ECOD but the
margin collapses from 0.0946 to 0.0080", and counted the HST/ECOD ordering as
flipping in 1 of 2 covered cells. The third draw, seed 47, gives HST **0.3585**
against a deterministic ECOD 0.4190. HST does not stay ahead. The ordering
flips in **2 of 2** covered cells, and the count and the surrounding sentence
are corrected accordingly. This strengthens binding rule 7 rather than
qualifying it: two of two stochastic-versus-deterministic orderings in this
experiment reverse under a seed change.

**One result of this comparison is positive and worth recording.** The two runs
were produced on different machines, operating systems and interpreter builds —
the sweep on Windows / Python 3.11.9, the Stage 4 arm on Linux / Python 3.11.15
with a different resolved wheel set. HST and ECOD agree **bit-for-bit**, and
the proposed detector agrees to **2.8e-07**. That is an unplanned
cross-platform reproduction of the interleaved cell, and it is stronger
evidence for the pipeline's determinism than anything designed for the purpose.

### CI-17 — the run-length posterior is degenerate in two regimes A2 did not cover
Audit finding A2 established that `P(r_t = 0)` is pinned to the hazard rate and
never responds to a change point. Stage 3 reproduces that exactly: through the
50-record window after a 6-sigma shift, `P(r=0)` is 0.001000 against a hazard of
0.001000, with a maximum deviation of 1.4e-15 anywhere between initialisation
and truncation. The reason is algebraic rather than empirical — the
change-point branch is `log h + logsumexp(log p - nll)` and the growth branch
sums to `log(1-h) +` the same `logsumexp`, so the predictive term cancels in the
normalisation and `P(r=0)` equals the hazard **for any data whatsoever**.

Two regimes A2 did not report, found while re-measuring it:

- **t = 0**: the run array has length one, so `P(r=0)` is trivially 1.0.
- **t >= `max_run_length` (500)**: truncation drops growth mass *before*
  normalisation, so the cancellation breaks and `P(r=0)` wanders — mean 0.0110,
  maximum 1.0000. Every stream in this paper is far longer than 500 records, so
  **the published runs spent nearly all of their length in this regime**, where
  the run-length posterior is neither the hazard nor a change-point signal but
  an artefact of the cap.

Neither regime is a detection, and both will mislead anyone who summarises the
posterior with a maximum over the whole stream. My first Stage 3 probe did
exactly that and reported a peak of 1.0, which reads as "the posterior responds
strongly" and would have contradicted a correct audit finding. The measurement
was not wrong; the summary statistic mixed three regimes. Recorded because the
error is the interesting part: an aggregate over a window that spans a regime
change is not a measurement of either regime.

**A second correction, to my own prose rather than to a number.** The Stage 3
document initially said the change-point branch "binds on a small minority of
real records". It binds on **75.04%** — but at a mean contributed score of
**0.0025**, meaning both terms are essentially zero there and the branch wins a
comparison between two near-zero numbers. Both the original sentence and the
naive reading of the corrected figure ("the change-point term does most of the
work") are wrong in opposite directions. The document now states the share and
the contributed magnitude together, because either alone misleads.

### CI-18 — Stage 6 reduced to a 30-minute cap, and its first reading was wrong
**Scope reduction (operator constraint, 2026-08-20).** Stage 6 was capped at 30
minutes of local compute, down from 90, with no cloud. Scope was cut to fit and
the cuts are limitations of the result: one stream
(`litnet2020_udp_flood_natural`, d=36) rather than four, with CICIDS2017
excluded because at d=84 a two-arm full-stream run is about 3.3 hours; a fixed
200,000-record prefix rather than the full 500,000; `blaster_worm` and `spam`
excluded independently because their attacks sit at the end of the stream so no
prefix holds test attacks; and one seed, which binding rule 7 permits because
both variants are deterministic. Measured cost: 22.3 minutes for the ablation
plus 2.0 minutes to add the diagnostic, against the 30-minute cap.

**The finding.** The correction audit finding A2 prescribes — a prior-predictive
term on the reset branch — was implemented and does make `P(r=0)` respond: peak
1.000000 after a 6-sigma shift against 0.001000 for the evaluated detector, a
1000x change. On real data it collapses detection: AUC-PR 0.1699 against
0.3975, and an AUC-ROC of 0.5096, which is chance.

**The first reading of that was wrong and nearly shipped.** The obvious
conclusion — "repairing the change-point statistic degrades detection" — is not
what the data shows. A saturation diagnostic measured why: under the corrected
statistic the run-length posterior sits on short runs at *every* step (mean
`P(r<=5)` = 1.0000), so the `0.25 * P(r<=5)` branch saturates and **92.7% of its
scores are exactly 0.25**. It emits 747 distinct score values where the original
emits 3,899. A score that is constant on most records cannot rank, and that is
all an AUC-ROC of 0.5096 means.

So both variants are degenerate in opposite directions: the evaluated detector
**never** resets, because `P(r=0)` is algebraically pinned to the hazard; this
correction **always** resets, because a nu=2 Student-t prior predictive prefers
a fresh run to any fitted run for nearly every point. Neither is change-point
detection, and the comparison between them says nothing about whether a correct
change-point statistic would help.

**An earlier correction attempt also failed, differently.** Using the global
slowly-adapting Gaussian as the prior predictive changed nothing (`P(r=0)` peak
0.001001 against a hazard of 0.001000): immediately after a change the global
model is as stale as the run-conditional ones, so both branches take the same
penalty. A reset branch is informative only if a surprising point is *better*
explained by starting over, which requires a vague predictive — and a vague
enough predictive resets always. The working scale lies between, and locating
it is a hyperparameter search that the cap excludes and the no-selecting-on-test
rule constrains.

**Stage 6 therefore establishes a failure mode, not a working correction**, and
the manuscript may claim no more than that. The Stage 5 verdict on the
change-point contribution stays WITHDRAWN: Stage 6 did not rescue it.

### CI-19 — the manuscript reintroduced the CI-1 class error, and the ledger inherited it
The F8 contradiction sweep (three independent auditors over the compiled
manuscript, 2026-08-24) returned 7 BLOCKING, 10 WORDING and 6 NIT findings.
All were fixed before FINALIZE_DONE. Three deserve permanent record:

**The worst: "natural-order" applied to the interleaved slice — CI-1's error,
reintroduced by the author of the correction.** The introduction stated the
LOF-versus-detector result (0.8632 vs 0.5450) "on the identical natural-order
held-out slice". That slice is the *interleaved unresampled* stream's held-out
slice (floor 0.2524); the detector's natural-order value is 0.7283. The claim
ledger's row I15 carried the same words, so the ledger — built to catch
exactly this — validated the defect instead: **a ledger written by the same
hand as the manuscript shares the manuscript's blind spots.** The gate checks
that ledger references *exist*, not that their gists are *true*; the sweep's
independence is what caught it. Both fixed; ledger gists for A5, A6, A8, I11,
I15, I16 tightened in the same pass.

**"Monotonically" falsified by its own macros.** The Section 6 sentence
claimed lift "falls monotonically from +0.3176 at 5% ... to −0.020 at 64%"
while its own second value (+0.3482 at 10%) rises from the first. Replaced
with the peak-then-fall form the findings file always used.

**The heredoc \r class, completed.** Prior incidents recorded `\b`→backspace
and `\t`→tab damage from shell-mangled Python heredocs; this sweep found the
third member: `\ref` became a literal carriage return + "ef{...}", which a
later universal-newlines read/write cycle converted into a mid-token line
break — rendering "(Table eftab:litnet)" in the shipped PDF while the
0-undefined-references check passed vacuously (a `\ref` that has lost its
backslash is not a reference). The general rule, now enforced by practice:
**backslash-bearing text never goes through the shell heredoc; it goes
through Write-tool script files.** Also fixed en route: five typed literals
manifested (`supplementary_macros` run), single-seed HST placements removed
from flat rankings (rule 7), arXiv IDs stripped from the anonymous build and
reinstated only in the named arXiv variant by `build_arxiv_variant.py`.
