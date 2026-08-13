#!/usr/bin/env bash
# Phase 5: bring the cloud run home and stop the meter.
#
# Idempotent and safe to re-run. Pulls every durable artifact from the EC2
# instance, commits and pushes from the laptop (where git auth lives),
# terminates the instance, verifies the volume is gone, and writes an honest
# DONE_ALL.md that states which deliverables exist and which do not.
#
# Usage: bash scripts/phase5_bring_home.sh [--keep-instance]
set -uo pipefail

REPO="C:/Users/CYBERWIZARD/projects/rcbsid-paper"
PEM="$REPO/caliburn-s3-key.pem"
HOST="${CALIBURN_HOST:-ubuntu@3.70.72.121}"
IID="${CALIBURN_IID:-i-0de18850edfab1a40}"
VOL="${CALIBURN_VOL:-vol-01968761956323f00}"
AWS="/c/Program Files/Amazon/AWSCLIV2/aws.exe"
export AWS_DEFAULT_REGION=eu-central-1
LAUNCH_EPOCH=${CALIBURN_LAUNCH_EPOCH:-1786645130}
RATE=${CALIBURN_RATE:-0.4032}
KEEP=0
[ "${1:-}" = "--keep-instance" ] && KEEP=1

cd "$REPO" || exit 1
echo "=== PHASE 5 @ $(date -u '+%Y-%m-%d %H:%M:%S') UTC ==="

# ---- 1. final pull -------------------------------------------------------
echo "--- pulling artifacts from the instance ---"
if ssh -i "$PEM" -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
     'cd rcbsid-paper && tar czf - results figures findings_*.md RUN_REPORT.md logs/autopilot.log logs/jobs 2>/dev/null' \
     2>/dev/null | tar xzf - -C "$REPO"; then
  echo "pull OK"
  ssh -i "$PEM" -o BatchMode=yes -o ConnectTimeout=30 "$HOST" \
    'cd rcbsid-paper && git log --oneline -3 2>/dev/null' 2>/dev/null | sed 's/^/  remote commit: /'
else
  echo "PULL FAILED — instance unreachable; proceeding with whatever is already on local disk"
fi

# ---- 2. honest deliverable inventory ------------------------------------
echo "--- inventory ---"
INVENTORY=""
add() {  # add <path> <label>
  if [ -s "$1" ]; then
    INVENTORY="${INVENTORY}- [x] \`$1\` — $2\n"
    echo "  EXISTS  $1"
  else
    INVENTORY="${INVENTORY}- [ ] \`$1\` — $2 (NOT PRODUCED)\n"
    echo "  MISSING $1"
  fi
}
add "results/prevalence_sweep_cicids.csv"   "Stage 2: per-run sweep results (control-verified)"
add "results/prevalence_sweep_table.tex"    "Stage 2: LaTeX table, mean/std over resample seeds"
add "figures/fig6_prevalence_sweep.pdf"     "Stage 2: prevalence sweep figure"
add "findings_prevalence.md"                "Stage 2: findings"
add "results/baseline_tuning.csv"           "Stage 3: every grid point + finals"
add "results/table4_litnet_tuned.tex"       "Stage 3: Table 4 with tuned rows"
add "results/table5_cicids_tuned.tex"       "Stage 3: Table 5 with tuned rows"
add "results/tuning_delta_summary.tex"      "Stage 3: default vs tuned delta summary"
add "results/appendix_a_replacement.tex"    "Stage 3: Appendix A tuning-protocol block"
add "findings_tuning.md"                    "Stage 3: findings"
add "results/burnrate_litnet.csv"           "Stage 4: burn-rate results"
add "results/burnrate_litnet_table.tex"     "Stage 4: burn-rate LaTeX table"
add "figures/fig7_burnrate_litnet.pdf"      "Stage 4: burn-rate figure"
add "findings_burnrate.md"                  "Stage 4: findings or scoping note"
add "findings_paper_overlap.md"             "Sub-task: sibling/CALIBURN overlap report"
add "RUN_REPORT.md"                         "Full run report"

# NB: `grep -c || echo 0` emits TWO lines when grep matches nothing (grep
# prints 0 and exits 1, then echo adds another 0), which corrupted the
# generated counts. grep -c always prints a number, so no fallback is needed.
GRID=$(ls results/tuning_parts 2>/dev/null | grep -c '^grid_cicids')
GRIDL=$(ls results/tuning_parts 2>/dev/null | grep -c '^grid_litnet')
FIN=$(ls results/tuning_parts 2>/dev/null | grep -c '^final_')

# ---- 3. terminate and verify --------------------------------------------
TERM_NOTE="instance left running by request (--keep-instance)"
if [ "$KEEP" = "0" ]; then
  echo "--- terminating instance $IID ---"
  "$AWS" ec2 terminate-instances --instance-ids "$IID" \
    --query 'TerminatingInstances[0].[InstanceId,CurrentState.Name]' --output text 2>&1
  for i in $(seq 1 30); do
    ST=$("$AWS" ec2 describe-instances --instance-ids "$IID" \
         --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)
    echo "  state: ${ST:-<record purged>}"
    # An empty/None state means the instance record is already gone (spot
    # reclaim purges it), which is terminal — without this the loop polled a
    # non-existent instance for its full 10 minutes.
    case "$ST" in
      terminated|""|None) break;;
    esac
    sleep 20
  done
  [ -z "$ST" ] || [ "$ST" = "None" ] && ST="gone (record purged)"
  VST=$("$AWS" ec2 describe-volumes --volume-ids "$VOL" \
        --query 'Volumes[0].State' --output text 2>&1 | tail -1)
  case "$VST" in
    *InvalidVolume.NotFound*|"") VST="deleted (not found — DeleteOnTermination honoured)";;
  esac
  echo "  volume $VOL: $VST"
  TERM_NOTE="instance terminated (state=$ST), volume $VOL: $VST"
fi

NOW=$(date -u +%s)
HOURS=$(awk -v a="$NOW" -v b="$LAUNCH_EPOCH" 'BEGIN{printf "%.2f",(a-b)/3600}')
COST=$(awk -v h="$HOURS" -v r="$RATE" 'BEGIN{printf "%.2f",h*r}')
echo "--- runtime ${HOURS} h, cost \$${COST} ---"

# ---- 4. DONE_ALL.md ------------------------------------------------------
{
  echo "# DONE_ALL — $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
  echo
  echo "Branch \`exp/prevalence-and-tuning\`. Stage 3/4 ran on AWS EC2"
  echo "\`c7i.2xlarge\` spot (\`$IID\`, eu-central-1a, gp3 100 GB upgraded live to"
  echo "6000 IOPS / 500 MB/s). $TERM_NOTE."
  echo
  echo "**Instance runtime ${HOURS} h at \$${RATE}/h spot = \$${COST}.**"
  echo
  echo "## Stage 3 coverage actually achieved"
  echo
  echo "- CICIDS2017 grid points evaluated: **$GRID / 24**"
  echo "- LITNET-2020 grid points evaluated: $GRIDL (abandoned — see below)"
  echo "- Final (full-stream) runs completed: **$FIN / 8**"
  echo
  echo "**LITNET-2020 tuning was abandoned as statistically void.** Its trial"
  echo "config sets \`time_column: null\`, so the stream stays in file order and the"
  echo "70/15/15 split yields train 7.426% / validation **0.003%** / test 0.059%"
  echo "attack prevalence — the validation split holds **6 attacks in 225,000 rows**,"
  echo "so validation-AUC-PR selection there is noise. The window was reallocated to"
  echo "CICIDS2017 (validation 21.70%, 52,085 attacks), which was in the runbook's"
  echo "original two-dataset scope. This also bears on the manuscript: the published"
  echo "LITNET numbers are computed on that same 0.059% test slice while the paper"
  echo "describes LITNET as the \"5.2% rare-attack regime\" — see findings_tuning.md."
  echo
  echo "## Deliverables"
  echo
  printf "%b" "$INVENTORY"
  echo
  echo "## Paste into the Claude chat for manuscript integration"
  echo
  echo "- findings_prevalence.md"
  echo "- findings_tuning.md  (read the coverage section first)"
  echo "- results/prevalence_sweep_table.tex"
  echo "- results/table5_cicids_tuned.tex"
  echo "- results/tuning_delta_summary.tex"
  echo "- results/appendix_a_replacement.tex"
  echo "- RUN_REPORT.md  (reductions, gates, migration note)"
} > DONE_ALL.md
echo "--- DONE_ALL.md written ---"

# ---- 5. commit and push from the laptop ---------------------------------
git add -A >/dev/null 2>&1
git add -f results figures findings_*.md RUN_REPORT.md DONE_ALL.md PIPELINE_STATUS.md >/dev/null 2>&1
git commit -q -m "exp: bring the AWS Stage 3/4 run home; terminate instance

$TERM_NOTE. Instance runtime ${HOURS} h = \$${COST} spot.
CICIDS2017 grid $GRID/24, finals $FIN/8. LITNET tuning abandoned as
statistically void (validation split holds 6 attacks in 225,000 rows).
DONE_ALL.md records exactly which deliverables were produced.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" && echo "committed"
if git push -q origin exp/prevalence-and-tuning 2>/dev/null; then
  echo "pushed to origin"
else
  echo "PUSH FAILED — commits are local only (recorded in DONE_ALL.md)"
  echo >> DONE_ALL.md
  echo "> NOTE: the final push failed; commits exist locally on the branch only." >> DONE_ALL.md
fi
echo "=== PHASE 5 COMPLETE ==="
