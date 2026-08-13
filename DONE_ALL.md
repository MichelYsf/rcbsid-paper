# DONE_ALL — 2026-08-13 12:35:47 UTC

Branch `exp/prevalence-and-tuning`. Stage 3/4 ran on AWS EC2
`c7i.2xlarge` spot (`i-0a474922fd3f64d86`, eu-central-1a, gp3 100 GB upgraded live to
6000 IOPS / 500 MB/s). instance terminated (state=None), volume vol-094c20d2274329a3e: deleted (not found — DeleteOnTermination honoured).

**Instance runtime 27.33 h at $0.194/h spot = $5.30.**

## Stage 3 coverage actually achieved

- CICIDS2017 grid points evaluated: **18 / 24**
- LITNET-2020 grid points evaluated: 14 (abandoned — see below)
- Final (full-stream) runs completed: **0
0 / 8**

**LITNET-2020 tuning was abandoned as statistically void.** Its trial
config sets `time_column: null`, so the stream stays in file order and the
70/15/15 split yields train 7.426% / validation **0.003%** / test 0.059%
attack prevalence — the validation split holds **6 attacks in 225,000 rows**,
so validation-AUC-PR selection there is noise. The window was reallocated to
CICIDS2017 (validation 21.70%, 52,085 attacks), which was in the runbook's
original two-dataset scope. This also bears on the manuscript: the published
LITNET numbers are computed on that same 0.059% test slice while the paper
describes LITNET as the "5.2% rare-attack regime" — see findings_tuning.md.

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
