#!/usr/bin/env bash
# Local results puller — runs DETACHED on the laptop, not as a session watcher.
#
# The 2026-08-13 spot reclaim destroyed ~1.5 h of results because the only
# puller was a session-bound watcher that had died. This process is launched
# via WMI so its parent is WmiPrvSE, survives the agent session entirely, and
# keeps a complete local copy from which deliverable generation and Phase 5
# can run even if the instance is never reachable again.
#
# Usage: local_puller.sh <host> <interval_seconds>
set -uo pipefail
REPO="C:/Users/CYBERWIZARD/projects/rcbsid-paper"
PEM="$REPO/caliburn-s3-key.pem"
HOST="${1:?host required}"
INTERVAL="${2:-900}"
LOG="$REPO/logs/local_puller.log"
mkdir -p "$REPO/logs"

say() { echo "[$(date -u '+%Y-%m-%d %H:%M:%S')Z] $*" >> "$LOG"; }
say "puller started (host=$HOST interval=${INTERVAL}s pid=$$)"

fails=0
while true; do
  if ssh -i "$PEM" -o BatchMode=yes -o ConnectTimeout=45 -o StrictHostKeyChecking=accept-new \
       "$HOST" 'cd rcbsid-paper && tar czf - results figures findings_*.md RUN_REPORT.md logs/autopilot.log 2>/dev/null' \
       2>/dev/null | tar xzf - -C "$REPO" 2>/dev/null; then
    fails=0
    G=$(ls "$REPO/results/tuning_parts" 2>/dev/null | grep -c '^grid_')
    F=$(ls "$REPO/results/tuning_parts" 2>/dev/null | grep -c '^final_')
    say "pull OK — grid=$G finals=$F"
    {
      echo "# CALIBURN status (local copy, pulled by detached puller)"
      echo
      echo "- Last successful pull: $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
      echo "- Grid partials: $G | Finals: $F"
      echo "- Host: $HOST"
      echo "- Deliverables can be generated entirely from this local copy."
    } > "$REPO/PIPELINE_STATUS.md" 2>/dev/null
    if [ -f "$REPO/DONE_ALL.md" ] && grep -q "FINALS RUN" "$REPO/DONE_ALL.md" 2>/dev/null; then
      say "DONE_ALL from the finals run is present; puller exiting"
      break
    fi
  else
    fails=$((fails+1))
    say "pull FAILED (consecutive=$fails)"
    if [ "$fails" -ge 40 ]; then say "giving up after $fails failures"; break; fi
  fi
  sleep "$INTERVAL"
done
say "puller stopped"
