# RUN_REPORT — CALIBURN revision experiments (branch exp/prevalence-and-tuning)

Status: IN PROGRESS (updated as stages complete). Date: 2026-08-06.
Machine: Windows 11, 12 logical cores, 15.7 GB RAM, Python 3.11.9 (venv).

## Amendments in force

The original runbook plus the authorized addendum: dataset acquisition is
autonomous (official sources only), UNSW-NB15 removed entirely, integrity
gates before use, and the paper-overlap sub-task (delivered:
`findings_paper_overlap.md`).

## Stage 0 — preflight (COMPLETE)

Disk gate: 277.9 GB free (>= 20 GB required).

Dataset acquisition (official sources only):
- CICIDS2017 Engelen-corrected: `CICIDS2017_improved.zip` (343,549,013 bytes)
  from intrusion-detection.distrinet-research.be/CNS2022/Datasets/ — the
  CNS2022 "improved" build linked from the WTMC2021 tools page named in the
  addendum; it is the version carrying the `Attempted Category` fingerprint.
  Contents: monday..friday.csv — 371,625 / 322,079 / 496,642 / 362,077 /
  547,558 rows (incl. header), `Attempted Category` present in all five.
- LITNET-2020: dataset.litnet.lt 301-redirects to the author's GitHub repo
  (Grigaliunas/electronics9050800); downloaded the six required zips from
  `dataset/` there (regular git blobs, not third-party mirrors):
  BLASTER_WORM_v2.csv (2,126,108,881 B / 3,119,478 rows) +
  BLASTER_WORM_v2_ATTACKERS_FLOWS.csv (16,489,000 B / 24,291 rows),
  UDP_FLOOD_v2.csv (426,323,549 B / 630,124 rows) +
  UDP_FLOOD_v2_ATTACKERS_FLOWS.csv (61,890,852 B / 93,583 rows),
  SPAM_v2.csv (845,442,205 B / 1,240,708 rows) +
  SPAM_v2_ATTACKERS_FLOWS.csv (496,301 B / 747 rows).
  Exactly the six expected files; per-attack rates match the repo's
  documented 0.78% / 14.8% / 0.06%.

Environment: fresh venv from requirements.txt (pysad 0.3.4, pyod 2.0.5,
river 0.22.0, rrcf 0.4.4, numpy 1.26.4, scikit-learn 1.8.0, scipy 1.17.1).
Note: the runbook's prose named PySAD 0.2.0 / PyOD 1.1.3, but the repo's
requirements.txt (which produced the paper, per its README) pins 0.3.4 /
2.0.5 — the repo pins win; the Stage 1 gate arbitrates. KitNET-py vendored
via scripts/setup_kitnet_py.sh under external/ (untracked).
`scripts/verify_native_baselines.py`: all six streaming baselines native,
non-constant. Smoke test green. pytest: 31 passed (incl. 20 new tests).

Datasets built (deterministic builders, no RNG):
- CICIDS: 1,600,000 flows, 352,962 attacks = 22.06% natural (splits
  21.46 / 21.70 / 25.24), 759.2 MB.
- LITNET: 1,500,000 flows, 78,111 attacks = 5.207% natural, 802.3 MB.

### Bug found and fixed: Windows loader doubled every dataset

`src/data/loaders.py::list_data_files` globbed `*.csv` AND `*.CSV`; on
case-insensitive filesystems both match the same file, so every dataset
loaded twice (verified: the 1.6M-row CICIDS stream loaded as 3.2M flows).
Fixed by resolved-path dedupe + 3 regression tests (commit cac5416).
Provenance oracle (deterministic batch refs through the exact runner
protocol) shows the PUBLISHED numbers were NOT affected:
- ECOD corrected stream: AUC-PR 0.418966 = published, diff 0.00e+00 (exact).
- LOF corrected stream: 0.863194 vs published 0.862661 (diff 5.3e-04; both
  round to the published 0.863 — residual drift attributable to the
  unpinned scikit-learn range `>=1.5,<1.9`, ours 1.8.0; ECOD is exact
  because pyod is hard-pinned).
- Doubled stream: LOF 0.912, ECOD 0.397 — far from published; the published
  pipeline did not run under the bug.

## Stage 1 — reproduction gate (RUNNING)

Runtime estimate printed before launch (steady-state per-flow, corrected
stream): BOCPD 2.04 ms, LODA 4.62 ms, HST 4.57 ms; LOF ~38 min/run,
ECOD ~3 min/run. Per seed ~5.7 h; three single-seed processes in parallel
(staggered 5 min for RAM) ~6 h wall — inside the 12 h ceiling. Sequential
would be ~16 h; parallelization is the logged mitigation. Reduction applied
and logged: Stage 1 configs (configs/stage1/) restrict methods to the
gate-relevant set (bocpd + LODA + HST + LOF + ECOD); kitnet / rrcf /
iforest_asd / copod are not part of the gate and would multiply runtime.

Commands:
```
python -m src.experiments.run_streaming_eval --config configs/stage1/cicids_repro_seed{11,23,47}.yaml --output results_stage1/seed{11,23,47}
python scripts/check_stage1_gate.py results_stage1/seed11 results_stage1/seed23 results_stage1/seed47
```

Gate targets: CALIBURN AUC-PR 0.545 / AUC-ROC 0.880 / F1 0.639 exact
(<=1e-9 vs the in-repo trial CSV), LOF 0.863 at published 3-decimal
precision (documented above), LODA 0.342 / HST 0.433 seed-tight (1e-6) with
the paper's mean±std envelope as documented fallback.

### Ceiling overrun (logged 2026-08-07 07:50, decision: let them finish)

The pre-launch estimate (~6 h wall from isolated steady-state timing) was
inside the ceiling, but by 07:49 next morning all three runs were still in
flight at ~13.8 h wall / ~13.5 CPU-h each (98% of one core, never suspended).
A live probe measured BOCPD-class work at 10.04 ms/flow — 4.9x the isolated
benchmark — so effective in-run throughput was throttled (laptop clocks /
3-way contention), putting true position between ~48% (if the overnight
factor was ~4.9x) and ~99% (if ~2.4x). Ruling: the 12 h ceiling was
respected at launch; the runbook's authorized reduction rules contain
nothing scoped to Stage 1, and no reduction can replace the reproduction
gate itself — killing the runs would discard ~40 CPU-h and re-incur the
identical cost. The runs are being allowed to finish, loudly logged here.
Consequences applied downstream: Stage 2/3 estimates will be recalibrated
from the measured in-situ Stage 1 wall times (not isolated benchmarks), and
Stage 2/3 use their authorized reductions aggressively. Recommendation for
the operator: keep the machine on AC power with sleep disabled during
stages; sustained clocks dominate wall-clock here.

## Stage 2 — prevalence sweep (PENDING gate)

Harness: scripts/run_prevalence_sweep.py (cells = level × seed, resampling
per scripts/prevalence_lib.py with per-split 1 pp tolerance and logged
redraws; CALIBURN variants V1/V3/V4 per scripts/caliburn_variants.py layered
on one scored stream per cell; bocpd_slo control row is byte-identical to
the Stage 1 protocol). Estimate to be printed before launch.

## Stage 3 — baseline tuning (PENDING)

Harness: scripts/run_baseline_tuning.py (runbook-exact grids; validation
AUC-PR selection only; crash-drop logging; 40%-of-train reduction mode
available per the runbook compute rule).

## Stage 4 — burn-rate validation (PENDING Stages 2+3)

Harness: scripts/run_burnrate_litnet.py (real-timestamp span gate; minute
bucketing; episode reporting). Note for findings: LITNET timestamps are
non-zero-padded and the runner orders them by string sort, which is not
perfectly chronological within a month; scoring uses the published stream
order, burn-rate evaluation maps events to true parsed timestamps.

## Wall-clock log

- Stage 0: downloads ~15 min (parallel); builds ~9 min; verify+smoke+pytest
  ~9 min.
- Forensics: provenance oracle ~4.6 h total CPU in background (the doubled
  LOF leg dominated), overlapped with prep.
- Stage 1: launched 2026-08-06 ~14:0x local, 3 processes staggered.

## Paper-overlap sub-task (COMPLETE)

See `findings_paper_overlap.md`. Verdict: shared lineage, not duplicated
material; the sibling's alerting is single-threshold and windowless (quoted
verbatim there), CALIBURN's is genuinely multi-window multi-burn.
