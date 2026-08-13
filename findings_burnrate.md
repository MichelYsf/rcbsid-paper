# Burn-rate validation (Stage 4): not run

Stage 4 was never reached. Under the runbook's priority order the Stage 3
tuning deliverables come first, and the bounded cloud window was consumed by
the Stage 3 grid. The EC2 instance was then reclaimed by AWS at approximately
11:03 UTC on 2026-08-13 (spot capacity withdrawal, not a failure of the
pipeline or the cost guard), roughly ten minutes into the finals phase.

No burn-rate numbers are reported rather than rushed or partial ones.

The harness is complete, committed, and ready to run when hardware time is
available:

- `scripts/run_burnrate_litnet.py` — real-timestamp span check (reports which
  alert levels the test slice honestly supports: page-fast needs 60 min of
  span, page-slow 360, ticket 4320), CALIBURN V1 threshold-crossing events
  bucketed into real minutes, multi-window burn-rate logic with the paper's
  Table 2 configuration, and coincidence with labeled attack windows.
- `scripts/figures/fig7_burnrate_litnet.py` — the three-panel figure.
- `scripts/make_burnrate_table.py` — the LaTeX table.

**Before running it, read `findings_tuning.md` first.** The LITNET-2020 test
slice carries roughly 133 attacks in 225,000 rows (0.059% prevalence), so a
burn-rate evaluation on it will be extremely thin. The span check in the
script is what should decide whether the result is reportable at all.
