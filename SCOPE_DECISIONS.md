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
     measured under a fixed 70/15/15 tail split, and the mechanism is dilution
     by attack-free days rather than any redistribution of attacks. *Amended
     2026-08-27:* this bullet previously read "no split-rule sensitivity check
     exists". One does now — A2 sweeps seven chronological cuts from 60% to
     90% and finds the measured ordering changes with the cut, so the fixed
     split is not neutral either. The bullet's conclusion is unchanged and
     strengthened; only its stated reason was stale;
   - **not a performance claim** — read against a chance floor equal to test
     prevalence, no method clears floor by more than 0.073 on the natural arm
     and HST sits 0.093 below it.

9. **Reported precision, and derivation from reported values.** Every metric is
   reported at six decimal places (`provenance.REPORT_DP`). A quantity derived
   from other reported quantities — a margin, a spread, a difference, a
   normalized lift — is computed from their **reported** values, not from the
   full-precision values behind them.

   The alternative rule (derive at full precision, round only for display)
   keeps each statistic exactly what the data says, and was rejected for two
   reasons. It makes the printed page fail to add up: a margin derived at full
   precision rounded to 0.061125 while the two AUC-PR values printed beside it
   differ by 0.061126, so a reader checking the arithmetic in a paper that
   invites exactly that check finds a mismatch. And it is not implementable
   downstream: manifests store values already rounded to six places, so the
   full-precision value is not recoverable by the display layer — the choice is
   between deriving from reported values and storing more digits everywhere.

   The cost is that a derived value may differ from its full-precision
   counterpart by a few units in the last reported place — under 1e-05 across
   this paper, orders of magnitude below any claimed effect. The benefit is an
   exact guarantee: **every derived number on the page equals the arithmetic a
   reader performs on the numbers printed beside it.**
   `scripts/check_decimals.py` enforces it and fails the build otherwise.

10. **Registrar-backed identifiers are verified against the registrar.** A DOI,
    arXiv ID, or ORCID is checked against the registrar's API (DataCite,
    Crossref, arXiv, ORCID) or the owning account --- never by whether a page
    fetch succeeds, and never by searching this repository's own files or
    history for the identifier. A failed or refused automated fetch is
    evidence about the fetch; an identifier absent from the repository is
    evidence about the repository. Both registrars this project has touched
    refuse automated page fetches while answering their APIs --- preprints.org
    was correctly handled through the Crossref API in the round-3 citation
    work, and Zenodo was not handled at all when the project's own DOI was
    declared unminted (CI-36).

11. **Plain register for outward and operator-facing prose.** Adopted
    2026-08-31. Any operator-facing or outward prose written or revised from
    that date on uses plain human register. No em dashes. No en dashes. No
    semicolons. No walls of bullet points. Short direct sentences. Facts and
    meaning never change under this rule. Wording changes only. Two texts are
    exempt: the canonical provenance limitation and the canonical DOI lineage
    sentence. The provenance limitation is stated word for word in the
    published Zenodo deposit description, and the editor note asserts that
    same-words fact to the DTRAP editors. Both canons are held byte-identical
    across all four venue texts by this repository's verification. Rewording
    them locally in a round that may not touch the published record would
    either falsify the same-words assertion or break the byte-identity that
    anchors it, so the canons keep their existing wording until a round is
    authorized to edit the published record. Historical records and retired
    texts are never rewritten.

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

### CI-20 — the fresh review's overlap finding is right; its identification is not
The 26 August 2026 adversarial review returned MAJOR REVISION with three
blocking findings. Verification-first triage confirmed most of its factual
claims and refuted one identification. Both directions are recorded, because a
review that is right about a defect and wrong about its cause will mislead the
response if it is accepted whole.

**Verified TRUE and acted on.**
- The arithmetic checks (T4, T17) reproduce exactly: 352,962/1,600,000 =
  22.060125%; 163,764/240,000 = 68.235%; 60,575/240,000 = 25.2396%; overlap
  78,000/240,000 = 32.5%; and (15.7747 + 3.544 + 0.176)/3 = 6.498233 against
  the emitted 6.4982.
- "AUC-ROC 0.50962 means constant" is false (T13): the repaired variant emits
  747 distinct values with standard deviation 0.159341. The manuscript now says
  **near-chance ranking**, never constant.
- The identification objection (T5, T6) is correct and is the round's most
  important finding. Held-out membership, prevalence and order all change
  together, so no claim may attribute the outcome to ordering alone. Every such
  claim is withdrawn, including from the title.
- The method-identity objection (T12) is correct: exact cancellation is proved
  only below the run-length cap, while the evaluations spend nearly all their
  length beyond it, and the scored quantity is a function of P(r<=5) rather
  than P(r=0). The manuscript now states the three facts separately.
- The mean-magnitude objection (T11) is correct: a branch's mean contribution
  says nothing about which branch *ranks*. The "tail term does the
  discriminative work" sentence was removed pending direct measurement.

**Verified TRUE, and materially more serious than the review could see.** The
review's T18 compares this submission against the public CALIBURN preprint
(arXiv:2605.24696) and finds the same rounded values. Checked directly against
that PDF: CALIBURN v2's Table 4 reports CALIBURN 0.943, HST 0.261 ± 0.097,
ECOD 0.229; its Table 5 reports LOF 0.863, CALIBURN 0.545, HST 0.433 ± 0.078,
ECOD 0.419, LODA 0.342. Those are our LITNET pooled and CICIDS unresampled
cells at lower precision — the deterministic values exactly, and the HST values
matching our three-draw means rather than our seed-11 cells. The overlap is
real, substantial, and was **not** disclosed per result group. It is now, in
the manuscript's own overlap matrix and correction-history table, plus a
confidential prior-appearance note to the editors.

**Verified FALSE — the identification.** The review infers that CALIBURN "is
the suppressed companion" and that the sentence "the two papers report disjoint
result sets" is therefore false. CALIBURN is not the companion: it is *this
manuscript's own earlier version*, which the manuscript already disclosed as
such in its origin paragraph. The suppressed companion is a different
manuscript, and this project's own archived overlap analysis
(`findings_paper_overlap.md`, 2026-08-06) records that it reports **no
quantitative results anywhere** — zero tables — so it has no numeric overlap to
disclose. The disjointness sentence was therefore accurate as written about the
paper it referred to.

That does not rescue the sentence, and it has been deleted on the operator's
instruction. The reason is better than the review's: a sentence whose truth
depends on which of two related papers the reader thinks is meant is a bad
sentence in a double-anonymous submission where the reference is suppressed.
What replaces it is not a denial but a table — reused, re-derived, corrected,
new, withdrawn — covering the versions that actually overlap.

**Recorded for the process, not the paper.** The review had no repository
access and said so, correctly flagging that manifests prove lineage rather than
correctness. Every one of its factual claims was checked against code,
manifests or the archived PDFs before being accepted; one identification did
not survive that check. This is the same discipline that produced CI-19, where
the failure ran the other way — our own ledger validated our own error.

### CI-21 — the headline reversal does not survive on the shared records
The fresh review's central objection was that the rank inversion is measured on
held-out slices sharing only 32.5% of their records. Analysis A1 tested it
directly: both arms restricted to exactly the 78,000 records
both held out, both deterministic methods recomputed there.

**The inversion does not survive.** On the shared records the detector leads
ECOD in *both* arms — 0.905613 against 0.844487 under timestamp order, and
0.900371 against 0.849842 under day round robin. The detector's own score moves
by only 0.005242 AUC-PR between the two histories. The reversal reported in the
manuscript is therefore produced by **which records the assembly places in the
test set**, not by the order in which the detector processed its history.

What is withdrawn: any reading of the contrast as evidence that ordering
changes detector behaviour, and the implicit suggestion that the reversal is a
property of the detectors rather than of the evaluation. What survives, and is
now the paper's claim: stream assembly is an uncontrolled treatment whose
membership component dominates the measured outcome — which is a sharper and
better-supported statement than the one it replaces.

Two further results from the same round change claims:

**A2 — the ordering depends on the split point.** Across seven chronological
cuts from 60% to 90% of the stream, ECOD exceeds the detector at three,
including the 85% cut the paper's fixed split uses; the detector leads at the
other four. The archived split is not adversarially chosen but it is not
neutral, and no ordering claim here is a stable property of CICIDS2017.

**A3 — the composition, not the tail term, is the defect.** Scoring the
timestamp-ordered held-out slice with each branch alone: the tail term alone
reaches AUC-PR 0.831832 / AUC-ROC 0.829281, while the deployed composition
reaches 0.728355 / 0.526623 — the tail term **outranks the deployed detector**
by 0.103477 AUC-PR and 0.302658 AUC-ROC. The auxiliary branch ranks *below*
chance (AUC-ROC 0.281890) and, because the score is a maximum, overrides the
tail wherever the tail is small. The near-chance ranking of the deployed
detector is a property of how the two signals are combined, not of either
signal.

This corrects the removed Stage 3 sentence in the opposite direction from the
review's expectation. The review argued that a small mean contribution cannot
establish that the tail term does the discriminative work; correct. The
measurement shows the tail term does *more* than the deployed score, and that
the auxiliary branch is actively harmful to ranking. Neither the original claim
nor the reviewer's suspected alternative was right.

**Method note.** These analyses were affordable only because the detector's
score for a record depends solely on the records before it: one instrumented
prequential pass per arm (7,775 s and 7,768 s, 4.86 ms/record, run in parallel
within the round's three-hour cap) yields per-record scores and branch
components for every split point and every subset. The instrumentation hook
returns values `update_score` already computes and was verified bit-identical
on the default path before use. The dumps reproduce the archived arms exactly
on the assembled arm and to 1.8e-05 AUC-PR on the timestamp-ordered arm, whose
archived value was produced on Linux against this pass on Windows — the
cross-platform class recorded in CI-16.

### CI-22 — the provenance gate certified a file it generated itself
`check_provenance.py` scans one target: `paper/numbers.tex`. That file is
generated *from* the manifests, so it cannot contain an unmanifested number,
and the gate has been printing "every number in the manuscript traces to a run
manifest" while never opening the manuscript. Three defects of the same class
shipped past a green gate: CI-11 (the pooled attack count in a manuscript-bound
table), CI-19 (caught only by an independent auditor), and the four
shared-record AUC-ROC values typed into Table 4 in the previous round. The
pattern is stable — the gate certifies the generated file, the defect lives in
the hand-written one.

**Fix (structural, not four numbers).** `scripts/check_literals.py` now scans
the manuscript, every `.tex` it `\input`s, and every file the claim ledger
cites, for measurement-shaped numbers with no corresponding value in the macro
index; `check_provenance.py` runs it and fails on it. Files whose purpose is to
record numbers — this file, `AUDIT_FINDINGS.md`, `SUPERSEDED.md`, and the gate's
own fake-number fixtures — are scanned and reported but not failed on, because
forcing a withdrawn value through the macro layer would manifest an error as a
measurement. Genuine non-measurements in enforced files (ACM CCS concept
identifiers, the cited 60/360/4320-minute SRE window) sit in a named allowlist
with a stated reason, so an exclusion is a recorded decision rather than a
silent hole. The gate's success message no longer claims more than it checked.

**First run over the repository: 88 findings.** Four were the known Table 4
literals; 28 more were in `findings_review_analyses.md`, whose A2 sweep table
and A1 AUC-ROC columns were printed without ever being emitted as macros —
the same defect as CI-11, in the file the ledger cites as the evidence for the
round's new claims. The rest were a sign-handling false-positive class (a
`-0.3333` macro read as the literal `0.333`, now fixed), record-only files, and
six derived values in generated findings files that were arithmetic
consequences of archived macros and are now emitted as such. One value —
the `P(r=0)` peak of a *discarded* first attempt at the BOCPD repair — had no
manifest because that attempt was never archived; it was deleted from the
findings generator rather than back-filled, per the project's own rule.

### CI-23 — a background launch reported failure while its process kept running
The first launch of the round-3 analysis was issued as a backgrounded shell
command whose stdout redirect failed. The tool reported exit code 1, and that
was read as "the run did not start". It had started. Fifty minutes later a
process listing showed **two** concurrent copies of `run_review_analyses.py`,
each holding several GB and each due to write the same manifest directory and
overwrite the same findings file — the collision class that produced the OOM
recorded in CI-8, plus a manifest race that could have archived one run's
numbers under the other's inputs. The duplicate was identified by command line,
killed by PID, and verified gone; no partial manifest was written, because
manifests are committed at run completion and the kill left no handler to run.

**Rule.** A nonzero exit from a launcher is evidence about the launcher, not
about the process it launched. Before treating a background job as dead, list
processes and match on the command line. Never infer liveness from the log
file, which is exactly what failed here.

### CI-24 — a document-only re-run claimed compute it did not perform
Re-running the Stage 6 ablation to regenerate its findings document took the
cached path, reusing arm metrics from the 24 Aug run as designed — and then
emitted `SSixTotalWallS` for its own 128 s elapsed time, against the measuring
run's 155.3 s. The gate refused to render `numbers.tex`: two runs claiming one
macro with different values. Both numbers were true of their own run, which is
what made the macro name wrong. Fixed by having the cached path emit no stage
wall-time macro and record a note instead; the over-claiming manifest was
deleted and the run repeated. **Rule:** a run may only claim a macro for work
it actually did, and "reused from cache" is not "performed".

### CI-25 — a withdrawal was prepared for a submission that never existed
The previous round prepared, to the last click, an author-initiated withdrawal
of the companion manuscript (`arXiv:2510.09619`) from IEEE TIFS: a finalized
letter, an addressee, a portal-migration note, an execution order that put the
withdrawal *first*, an arXiv correction note announcing the withdrawal
publicly, a manuscript sentence and a confidential editor-note sentence both
stating that the relevant editors had been informed.

**There was no TIFS submission.** Verified by the author in the IEEE Author
Portal on 2026-08-27: filters set to *All Publications* and *All Submission
Statuses* return exactly one record, `TDSC-2025-10-1842`, rejected 22 October
2025, and no TIFS record of any kind. The companion is a public preprint and is
not under review anywhere.

**How it happened.** The venue was researched and the submission was not. The
round fetched the editor-in-chief, the ScholarOne-to-Author-Portal migration,
and IEEE's non-self-service withdrawal procedure — all accurate about TIFS, and
none of it capable of establishing that a manuscript had been submitted there.
The one signal pointing at the truth was logged and misread: the manuscript ID
was recorded as "not on this machine" after an exhaustive search, and treated
as *the operator must retrieve it* when it was equally consistent with *there
is nothing to retrieve*. A thorough search returning nothing is evidence about
the thing, not only about the search.

**What was false, and where.** Two of the statements had reached artifacts
bound for publication: the manuscript's Companion Manuscript Disclosure
("a correction process ... has been disclosed to the relevant editors") and the
confidential editor note ("the relevant journal has been or is being
informed" — whose "has been or is being" hedge concealed that nobody knew
which). A third was queued for a public, permanent arXiv Comments field ("has
been withdrawn from journal consideration by the author"). All three are
corrected; the letter is retired in place with a notice; `SIBLING_DECISION.md`
is replaced by the verified state; the withdrawal-first ordering is removed
from `HUMAN_ACTIONS.md`; and a third arXiv comment variant that makes no venue
claim at all is now the one to paste.

**Rule.** Before preparing any artifact that asserts a venue relationship — a
withdrawal, a disclosure, a correction note, a cover-letter sentence — verify
that the relationship exists against the venue's own system, and record the
verification with its date and source. Researching a venue's *procedures* is
not verification of a submission's *existence*. A hedge like "has been or is
being" in a factual disclosure is a signal that the fact was never checked.

### CI-26 — two citations resolved to nothing under a "0 undefined" verdict
The previous round added three concurrent-work citations to the manuscript and
recorded the compile as "3-pass, exit 0, **0 undefined references**, 13 pp".
Two of the three — `barrett2026firce` and `gurjar2026tailrisk` — were never
added to `references.bib`, so both rendered as `[?]` in the shipped PDF. The
verdict was not wrong, it was answering a different question: natbib reports a
missing bibliography entry as a *citation* warning, not as a LaTeX *undefined
reference*, so a document can carry dangling citations and report zero
undefined references truthfully.

This is the CI-22 pattern in a second mechanism: a check that reads as
comprehensive because of what it is named, while the defect sits just outside
what it actually inspects. Fixed by extending `check_manuscript_macros.py` to
parse every `\\cite*` key out of the manuscript and its inputs and fail on any
key with no entry in the bibliography — the citation analogue of the macro
check it already performed. Both missing works were then verified against their
arXiv listings before their entries were written: FIRCE (Barrett, Li, Dorai,
Rajaganapathy, arXiv:2605.01962, 3 May 2026) and Gurjar and Camp
(arXiv:2601.14299, 16 January 2026).

### CI-27 — a generated artifact was fixed in its generator and never regenerated
Two withdrawn claims were corrected in `scripts/make_contrast_deliverables.py`
and the script was never re-run, so `findings_contrast.md` continued to ship
the heading "Contrast 1 --- CICIDS2017, order only (prevalence held constant)",
the sentence "Order is the only manipulated variable", and the assertion "No
split-rule sensitivity check has been run" --- the first two withdrawn by CI-21
(A1), the third falsified by A2's seven-cut sweep, which the manuscript carries
as a live subsection. The file is cited by the claim ledger and ships inside
both `artifact_anonymous.zip` and the Zenodo bundle, so a referee opening the
artifact would have found it contradicting the paper it accompanies.

Editing a generator is not a fix; running it is. The gates could not catch this
because every number in the stale file still resolved to a manifest --- the
defect was in prose, and prose is exactly what the provenance layer does not
check. **Rule:** after editing any script that writes a tracked artifact,
re-run it in the same change and diff the output; treat an artifact whose
generator is newer than itself as stale by definition.

The same sweep found the withdrawn split-rule claim surviving independently in
`README.md`, `REBUILD_STATUS.md` and `REVIEWER_KIT/RESPONSE_SHELF.md`; a
corrected-incident count of 18 in six places against a log of 26; stale gate
statistics (356 and 362 macros against 564) and a stale page count (9 pp, then
10 pp in the arXiv metadata, against 17); and five self-descriptive universals
in the manuscript that its own tables falsify --- "every number in this paper
is a macro" (protocol constants and cited third-party values are typed),
"every AUC-PR is reported with normalized lift" (four tables print none),
"every ECOD number is scored validation-plus-test" (two analyses score
test-only), an unsourced comparison against "most of the differences this
literature reports", and a binding share quoted from a 50,000-record prefix to
characterise a 240,000-record slice. All are corrected; the binding share is
now measured on the slice it describes (\RevBranchAuxBindsHeldoutPct,
58.452%, emitted by `scripts/emit_branch_binding_macro.py` from the archived
components).

### CI-28 — the printed page did not add up, and nothing checked whether it did
The three-auditor sweep found the natural-arm margin printed as 0.061125 beside
two AUC-PR values whose difference is 0.061126. It was filed as a NIT and first
answered with a caption clause explaining that margins are rounded
independently of the cells — a hedge, and the wrong repair: it documented the
inconsistency instead of removing it.

Sweeping every derived quantity against its printed operands found **four**
such disagreements out of 21 (the natural-arm margin and three normalized
lifts), each one or two units in the sixth decimal. The seventeen that agreed
are why the four were invisible: a background of agreement reads as a rule
being followed.

A second, independent defect surfaced in the same sweep: display width. Because
the renderer used `repr()`, trailing zeros vanished, so an AUC-ROC of 0.799910
printed as `0.79991` five wide beside six-wide neighbours in the same table,
and unrounded floats reached `numbers.tex` at fifteen and sixteen decimals.
Metric families now render at a fixed width.

Both are closed by binding rule 9 and by `scripts/check_decimals.py`, which
fails the build if any derived value disagrees with its printed operands or if
a metric family renders at more than one width. Neither check can be satisfied
by editing the manuscript: both read the generated macro file and the archived
index, so the only way to pass is to fix the emitting run — which is why the
four values were corrected by re-running the analysis under the new rule rather
than by patching the file.

### CI-29 — the heredoc ate a backslash again, and only a new check saw it
The tab:branch caption added during the round-3 sweep was written through a
shell heredoc. Its `\ref` became a carriage return plus `ef`, so the caption
read "differ from Table~" / "ef{tab:contrast}" -- and the same damage was
copied into both staged package trees. This is the CI-19 defect exactly,
in a project that had already recorded the rule it violates ("backslash-bearing
edits go through script files only"), which is worth stating plainly: the rule
was written down, and written down was not enough.

Nothing in the existing gate could see it. The compile reported **zero
undefined references** and was right to: a `\ref` without its backslash is not
a reference, so it is not an undefined one -- it is prose that typesets as the
literal string `ef{tab:contrast}`. The provenance, literal and decimal checks
all read numbers, and this is markup.

`scripts/check_control_chars.py` now scans the manuscript and both package
copies for raw control characters and for the orphaned macro fragments the
common escapes leave behind (`ef{`, `abel{`, `egin{`, `pprox`, `ottomrule`,
and the rest), and the gate runs it. Its first honest run found both sites in
all three trees; it now passes. Note the check itself had to be corrected
before it was trustworthy: its first version flagged every line of every file,
because these sources are stored CRLF and it was treating the line terminator
as damage.

### CI-30 — half of the protocol table was off the page in three shipped PDFs
`tab:protocol` used an unwrapped `ll` column spec, so its settings column ran
past the measure by **1639pt**. Five rows were clipped mid-sentence in
`paper/main.pdf`, `packages/arxiv_v3/src/main.pdf` and
`packages/dtrap/manuscript_anonymous.pdf`. What was unreadable: the operative
half of the reporting-precision rule adopted the same round (the exactness
guarantee and the 1e-05 bound), the **bolded ECOD label-access disclosure** —
a load-bearing honesty caveat about this paper's own comparisons — the
average-precision definition with its scikit-learn version, the feature
encoding note, and the update-timing rule.

TeX reports an overfull \hbox and continues. The compile exited 0 with **zero
undefined references** and the round's own report counted the protocol table
among the material that strengthens the protocol description, while half of it
could not be read. Every check in this repository reads sources — numbers,
citations, markup — and none read the log.

Fixed by a wrapping column spec; two further overfulls found in the same pass
(78pt and 16pt, both long unbreakable `\texttt` runs) were fixed by giving
them break opportunities and by setting the ECOD call on its own line.
`scripts/check_overfull.py` now parses the LaTeX logs and fails the build on
anything over 2pt; the gate runs it. Both builds are now clean.

### CI-31 — the packages went stale, including the one with an immutable DOI
Two staged artifacts had fallen behind the tree they claim to archive.

The **Zenodo code zip** was three days and one full correction round old: 510
macros against 564, a corrected-incident log stopping at CI-21, the sentence
CI-21 withdrew ("Order is the only manipulated variable") still in
`findings_contrast.md`, and the four full-precision derived values that binding
rule 9 exists to remove. Its manifest bundle was 20 manifests short and carried
two **retired** manifests at top level as though live, and its
`superseded/README.md` documented 11 retirements against the repository's 18 —
while the deposit description promises every retirement reason. This is the
first artifact `HUMAN_ACTIONS.md` publishes, under a DOI that cannot be
withdrawn. It was stale because it was the one package with no build script:
every other package was rebuilt that round by running its builder.

The **DTRAP artifact** was rebuilt 37 seconds before the last source edit, so
it shipped a `check_provenance.py` that never called `check_control_chars` —
a referee running the artifact's own gate would have run a weaker one than the
repository's.

Two content defects surfaced with them. `findings_review_analyses.md` was
absent from the artifact's include list although the `CLAIM_LEDGER.md` inside
the same zip cites it in five rows: extracting the zip and running the ledger
check failed immediately, on the artifact's own missing evidence — and the
missing file is the one carrying A1, the analysis that refutes this paper's
own earlier headline, denied to the one audience that cannot ask for it. And
`results/manifests/superseded/README.md` never shipped at all, because the
manifest glob takes `*.json` and the retirement reasons live in a README.

Fixed: `scripts/build_zenodo_package.py` rebuilds the deposit deterministically
from the tree; the artifact builder now derives its findings set from the
`file:` references in the claim ledger, so the two cannot disagree again, and
includes the superseded README; `scripts/check_package_freshness.py` fails the
build when any staged artifact predates its sources, and the gate runs it. It
does not verify content — a package can be newer and still wrong — but it
catches the failure that actually happened, twice.

### CI-32 — the exclusion guard missed the escaped unit, and fabricated digits
Binding rule 9 excludes percentage-scaled values from the six-decimal metric
family precisely because six decimals on a value emitted with four would
fabricate digits. The guard tested `unit in {"%", "pp", ...}` and, as a
fallback, `"[%]" in desc`. Eight prevalence macros are emitted by
`build_natural_streams.py` with `unit=r"\%"` -- LaTeX-escaped, unlike every
other percent macro in the project -- and their generated comment tag is
therefore `[\%]`. Neither guard matched. The desc keyword "prevalence" then
matched, `is_metric` returned true, and the renderer forced `%.6f`.

The result reached the compiled manuscript: Table 1 printed the CICIDS
whole-stream prevalence as **22.060100%** and its held-out prevalence as
**68.235000%**, both padded from four decimals, while the contributions list and
Section 5 print **22.060125%** for the same quantity and the abstract prints
**68.235%**. Two renderings of one number, one of them carrying two digits that
are not measurements. `352962/1600000 = 22.060125` exactly, so the padded form
was also the less accurate one.

The width check could not see it: none of the eight ends in a listed suffix, so
all eight landed in the catch-all family together, at a uniform six decimals,
and read as compliant. **A uniform width is not evidence of a correct width.**

Fixed by normalising escaped units and comment tags in `is_metric`, and by
emitting a bare `%` from the stream builder. The eight now render at the four
decimals they were measured to, and Table 1 agrees with the abstract.

### CI-33 — an invariant written for a human to check, that nobody executed
`PUBLISH_INSTRUCTIONS.md` lists five invariants that must hold "before any of
them leaves this machine". Invariant 5 is "git status clean, branch pushed".
At the close of the final content round it was false: 120 uncommitted paths,
the branch with no upstream at all, and **61 of 65 live run manifests recording
a `-dirty` commit** -- a sha that is not resolvable from the public repository,
so a reader cannot reach the code behind those numbers. `zenodo_metadata.md`
names the GitHub repository and branch as an *is derived from* identifier on a
deposit that cannot be withdrawn.

Every other invariant was green and the round was declared closed. The
difference between invariant 5 and the rest is that the rest are commands and
invariant 5 was a sentence. This is the project's own thesis turned on its own
release procedure: an assertion nobody executes enforces nothing.

`scripts/check_publish_ready.py` now executes it -- clean tree, published HEAD,
and no live manifest citing a dirty commit -- exposed as
`check_provenance.py --publish-ready`. It is deliberately **not** in the default
gate: the build gate asks whether the tree is internally consistent, this asks
whether it is publishable, and running the second on every build would make
every working state red and train the operator to ignore it. It is named in
`PUBLISH_INSTRUCTIONS.md` invariant 5 and as a step in `HUMAN_ACTIONS.md` before
the Zenodo deposit. **It does not pass as of 2026-08-27, by design: the round is
uncommitted.** Committing and pushing is the operator's decision, not the
build's.

### CI-34 — the gate's self-test was polluting the store it tests
`check_provenance.py --selftest` proves the gate resolves a manifested number
by writing a manifest holding a deliberately fake value
(`SelfTestManifested = 0.4242`) and then checking that the gate finds it. It
never removed the fixture. Forty accumulated: **61% of the live provenance
store**, every one recording an uncommitted tree, and one of them putting a
fake number into `paper/numbers.tex` — the generated file the manuscript reads
from. Nothing ever cited them, and no manuscript sentence used the macro, so
nothing published was wrong; but a self-test that contaminates the thing it
tests is not a self-test, and the store's own comment already identified this
risk for a neighbouring case while leaving this one open.

Fixed: the selftest deletes its fixture and reindexes before returning, so the
store is exactly as it was. The forty are retired to `superseded/`, and
`numbers.tex` dropped from 564 macros to 563 with the fixture gone.

### CI-35 — I overstated the "-dirty" problem, and the overstatement drove a decision
The previous round's `check_publish_ready` said a `-dirty` stamp is "not
resolvable from the public repository", and that wording propagated into
`HUMAN_ACTIONS.md`, `PUBLISH_INSTRUCTIONS.md` and the operator's next action.
**It is false.** A `-dirty` stamp is `<sha>-dirty`: the base sha resolves
normally. Checked explicitly after the push — all twelve distinct base commits
recorded across every live manifest resolve **and are ancestors of the pushed
branch**. A reader reaches the generating code to commit granularity.

What `-dirty` actually records is narrower: the working tree carried
uncommitted edits when the run executed, so the *exact* source state is not
recoverable. That is a real limitation, and for a deposit that cannot be
withdrawn it is worth failing on — but it is not the thing I said it was, and
the operator was being asked to make a publication decision on the strength of
the stronger claim.

Corrected in all four places. **The check's verdict is unchanged** — it still
exits 1 — because correcting a false rationale is not the same as relaxing a
threshold, and relaxing it to reach green is exactly what this project forbids.

### CI-36 — a published DOI was declared "never minted", on a repo-history search
The belief, carried into three publication-bound texts: the Zenodo DOI cited
by the v1/v2 manuscripts was never minted, no deposit existed, and the rebuild
would be "the first deposit of this artifact."

**Verified false on 2026-08-31, in the owning Zenodo account.** DOI
**10.5281/zenodo.20074590** exists, is published and public: created
2026-05-07T19:11Z; title "SLO-Aware Streaming Intrusion Detection:
Reproducibility Package"; version 1.0.0; type Software; licence Apache-2.0;
one file, a source archive of this repository at tag `v1.0.0` (2,028,268 B,
md5 f67dfa9c0203490a4de1648f6d6ce8c6); description "Initial release for
CALIBURN paper submission to KeAi Cyber Security and Applications"; concept
DOI 10.5281/zenodo.20074589; related identifier *is-supplement-to* the
repository tree at tag `v1.0.0` (the tag exists on the remote and resolves);
35 views and 7 downloads at verification. The v1/v2 citation therefore
resolves --- to the pre-audit codebase this rebuild corrects.

**Where the belief entered, and what check produced it.** `SUPERSEDED.md`
(2026-08-20) records the actual check verbatim: the only DOI ever recorded was
the placeholder `10.5281/zenodo.XXXXXXX` --- *verified with `git log --all`*.
A search of the repository's own history was substituted for a registrar
query. The repository's CITATION.cff had always carried a literal placeholder,
and the leap from "no real DOI anywhere in the repo history" to "the DOI cited
by the published manuscripts was never minted" was made without asking
DataCite, Zenodo's API, or the owning account. The FINALIZE round (2026-08-24)
then propagated the conclusion into `CITATION.cff`, the arXiv v3 Comments
text, the deposit metadata, and `README.md` --- and the deposit metadata file
shows the round explicitly **overriding the operator's own "new version"
wording** on the strength of the wrong check ("despite F-scope wording 'new
version', this is the FIRST deposit"). Whether an automated fetch of the DOI
was also attempted and refused is not recorded; the recorded evidence chain is
repo-history-only.

This is CI-25's failure shape, third occurrence: a thorough search returning
nothing, read as evidence about the thing rather than about the search. Worse,
the correct instrument was already in this project's toolkit --- when
preprints.org refused automated fetches during the round-3 citation work, the
Crossref API was used instead, and that handling was recorded as the pattern
to follow. The rule existed and was not applied to the project's own
identifier. Binding rule 10 now states it.

**Consequence.** The rebuild is not a first deposit. It publishes as **version
2.0.0** of the existing record lineage via Zenodo's New-version flow,
superseding v1.0.0, which stays public with a newer-version notice. All three
publication-bound texts were corrected before anything was published, and the
canonical DOI-correction sentence is byte-identical across the deposit
description, the DTRAP editor note, and the arXiv v3 note.

### Dated fact — the corrected artifact is published (2026-08-31)
The rebuild is live on Zenodo as **version 2.0.0** of the existing record
lineage. Version DOI **10.5281/zenodo.22213264**; concept DOI
10.5281/zenodo.20074589; superseded v1.0.0 at 10.5281/zenodo.20074590.
Published version string: "2.0.0". Verified against the Zenodo API on
2026-08-31 (title, creator with ORCID, and all five files at their staged
byte sizes). This closes the deposit step of the publish sequence; the
remaining outward actions are the DTRAP submission, the arXiv v3 replacement
within 48 hours of it, and the companion's v2 replacement.

**The pattern across CI-22, CI-24, CI-26 and CI-27 is one pattern:** a check or
a claim that reads as universal while covering less than its wording implies.
The provenance gate said "every number in the manuscript" and read one
generated file; the compile check said "0 undefined references" and did not
look at citations; the manuscript said "every number is a macro" while typing
protocol constants. The discipline that catches these is not another gate --- it
is reading the sentence and asking what it would take for it to be false.
