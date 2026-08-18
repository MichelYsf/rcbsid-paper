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
