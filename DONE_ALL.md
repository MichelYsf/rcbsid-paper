# DONE_ALL — 2026-08-17 09:51:32 UTC

Branch `exp/prevalence-and-tuning`. Stage 3/4 finals run on AWS EC2
`c7i.2xlarge` **on-demand** (`i-01cdbf26eb6699d75`, eu-central-1a, gp3 100 GB at
6000 IOPS / 500 MB/s from launch). instance terminated (state=terminated), volume vol-049e26b01e2604a7c: deleted (not found — DeleteOnTermination honoured).

**Instance runtime 3.83 h at $0.4032/h on-demand = $1.54.**
Caps in force: 6 h wall and $4 spend, whichever first; neither extended.

## Stage 3 coverage actually achieved

- CICIDS2017 grid points: **20** on disk (of 20 after the rrcf reduction)
- LITNET-2020 grid points: **20** on disk (of 20 after the rrcf reduction)
- Final (full-stream) runs completed: **11**

**LITNET-2020 was rebuilt correctly for this run** with
`build_litnet_labeled.py` + `interleave_litnet.py`, and
`check_stream_health.py` passed: 1,499,999 adjacent attack-type changes and
splits 4.928% / 5.218% / 6.498% (14,621 test attacks). The earlier claim that
the PAPER's LITNET evaluation was degenerate has been **retracted** — that was
this harness omitting the interleave step. See the corrected incident in
RUN_REPORT.md and findings_tuning.md.

**Documented grid reduction:** all RRCF grid points were dropped on both
datasets under the runbook's grid rules (measured 2.5-5 h per point, never
completed inside a bounded window; ranked last of nine on LITNET in the
published Table 4). RRCF therefore carries its documented DEFAULT
configuration in all tables, as ECOD and COPOD do. Reason recorded in
results/tuning_parts/reductions.json.

## Deliverables

- [x] `results/prevalence_sweep_cicids.csv` — Stage 2: per-run sweep results (control-verified)
- [x] `results/prevalence_sweep_table.tex` — Stage 2: LaTeX table, mean/std over resample seeds
- [x] `figures/fig6_prevalence_sweep.pdf` — Stage 2: prevalence sweep figure
- [x] `findings_prevalence.md` — Stage 2: findings
- [x] `results/baseline_tuning.csv` — Stage 3: every grid point + finals
- [x] `results/table4_litnet_tuned.tex` — Stage 3: Table 4 with tuned rows
- [x] `results/table5_cicids_tuned.tex` — Stage 3: Table 5 with tuned rows
- [x] `results/tuning_delta_summary.tex` — Stage 3: default vs tuned delta summary
- [x] `results/appendix_a_replacement.tex` — Stage 3: Appendix A tuning-protocol block
- [x] `findings_tuning.md` — Stage 3: findings
- [ ] `results/burnrate_litnet.csv` — Stage 4: burn-rate results (NOT PRODUCED)
- [ ] `results/burnrate_litnet_table.tex` — Stage 4: burn-rate LaTeX table (NOT PRODUCED)
- [ ] `figures/fig7_burnrate_litnet.pdf` — Stage 4: burn-rate figure (NOT PRODUCED)
- [x] `findings_burnrate.md` — Stage 4: findings or scoping note
- [x] `findings_paper_overlap.md` — Sub-task: sibling/CALIBURN overlap report
- [x] `RUN_REPORT.md` — Full run report

## Paste into the Claude chat for manuscript integration

- findings_prevalence.md
- findings_tuning.md  (read the coverage section first)
- results/prevalence_sweep_table.tex
- results/table5_cicids_tuned.tex
- results/tuning_delta_summary.tex
- results/appendix_a_replacement.tex
- RUN_REPORT.md  (reductions, gates, migration note)
