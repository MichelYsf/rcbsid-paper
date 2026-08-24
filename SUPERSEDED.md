# SUPERSEDED — stale artifacts that must not be mistaken for current

Everything listed here predates the honest rebuild on `rebuild/honest-v1`
(Stages 0–8, 2026-08-17 → 2026-08-20) and reports numbers produced under the
withdrawn composite construction, describes a scoring rule the code did not
implement, or both. Nothing here is deleted — history is never deleted in this
project — but nothing here may be cited, packaged, or republished. The current
state of every claim is `SCOPE_DECISIONS.md` (18 corrected incidents),
`findings_*.md`, and the manuscript in `paper/`.

## In this repository

| artifact | why superseded |
|---|---|
| `figures/fig2_pr_comparison_litnet.pdf` … `fig6_prevalence_sweep.pdf` | Pre-rebuild figures: composite-construction results, and fig5 depicts a "BOCPD posterior" the implementation does not compute (the posterior is pinned to the hazard; Stage 3 / CI-17). The rebuilt manuscript references none of them. |
| `results/table4_litnet_tuned.tex`, `table5_cicids_tuned.tex`, `tuning_delta_summary.tex`, `appendix_a_replacement.tex`, `prevalence_sweep_table.tex` | Generated under the interleaved composite protocol before the re-scope. Retained as CI-4 evidence (tuning numbers remain valid *as measurements of the synthetic protocol*); not manuscript-bound. Current tables: `table_construction_contrast.tex`, `table_prevalence_sweep.tex`. |
| `findings_tuning.md`, `findings_burnrate.md`, `findings_paper_overlap.md` | Pre-re-scope findings; scoped by CI-3/CI-4. Kept as audit trail. |
| `AUDIT_FIXES_V2.md` … `V7.md`, `V4_VALIDATION_REPORT.md`, `V5_VALIDATION_REPORT.md`, `AUDIT_REPORT_ORIGINAL.md`, `CHANGELOG_FOR_REVIEWERS.md`, `README_EXECUTION_NOW.md`, `PIPELINE_STATUS*.md`, `DONE_ALL.md`, `RUN_REPORT.md` | Documents of earlier missions (v2–v7 fix cycles, the experiments/autopilot runs). Historical record only. |
| `paper/rewrite_sections.md` | The Aug 6 rewrite plan. Its abstract claims UNSW-NB15, KitNET/xStream/RRCF/iForest results, Wilcoxon tests, Docker, and Zenodo — none of which has a manifested run or exists (Stage 5: 1 of 11 claims supported). Superseded by `paper/main.tex`. |
| `results/manifests/superseded/` | Retired manifests, each with its reason in the README there. |
| branch `exp/prevalence-and-tuning` | The pre-rebuild experiment line (composite construction throughout). Its results are relabelled, not reused, per binding rule 3. |
| branch `main` | Last updated before the rebuild; carries the v7 code state whose defects A1–A13 document. The rebuild has **not** been merged to `main` — that is a deliberate post-review step. |

## On this machine, outside the repository (`C:\Users\CYBERWIZARD\Downloads\`)

| artifact | why superseded |
|---|---|
| `2605.24696v2.pdf`, `CALIBURN Operationally Calibrated Streaming.pdf` | The published v1/v2 manuscript line: composite-construction numbers, the unimplemented scoring rule, the "regime taxonomy" (withdrawn, CI-1/CI-2), "latency in ms" (withdrawn, A4). |
| `caliburn_pass1.zip`, `caliburn_pass1b.zip`, `caliburn_pass1b.pdf`, `CALIBURN_FINAL_pre_results.zip` | Overleaf-era source/PDF snapshots of the same line. |
| `CALIBURN_DTRAP_adversarial_review.md`, `CALIBURN_DTRAP_skeptical_review.md` | Referee reviews **of the superseded manuscript**. Their verified findings are incorporated (V1–V12 verification; `AUDIT_FINDINGS.md`); the reviews themselves address a paper that no longer exists in that form. |
| `caliburn_experiments_prompt.md`, `caliburn_autopilot.md` | Mission briefs for the pre-rebuild experiment campaign. |

## Never existed (do not go looking)

- `README_repo_final.md` — an Aug 8 draft that was **never committed**: absent
  from the working tree and from the full history of every branch (verified
  with `git log --all` on 2026-08-20). Its claims predate the method-identity
  findings and are void wherever a copy survives outside the repository.
- A Zenodo deposit — the only DOI ever recorded was the placeholder
  `10.5281/zenodo.XXXXXXX`. No deposit exists to supersede.
