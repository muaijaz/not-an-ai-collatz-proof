#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RUN_ROOT="${RUN_ROOT:-docs/runs/latest_autonomous_sleep}"
TAIL_LINES="${TAIL_LINES:-50}"
WATCH_INTERVAL="${WATCH_INTERVAL:-30}"

print_once() {
  if [[ ! -e "$RUN_ROOT" ]]; then
    echo "No autonomous run found at $RUN_ROOT"
    return 1
  fi

  echo "== autonomous run =="
  echo "run_root=$RUN_ROOT"
  echo

  if [[ -f "$RUN_ROOT/status.md" ]]; then
    sed -n '1,220p' "$RUN_ROOT/status.md"
  else
    echo "status.md not written yet"
  fi

  echo
  if [[ -f "$RUN_ROOT/current_job.env" ]]; then
    # shellcheck disable=SC1090
    source "$RUN_ROOT/current_job.env"
    echo "== current job =="
    echo "job=${JOB:-unknown}"
    echo "description=${DESCRIPTION:-unknown}"
    echo "started_at=${STARTED_AT:-unknown}"
    echo "log=${LOG:-unknown}"
    echo
    if [[ -f "${LOG:-}" ]]; then
      echo "== tail -n $TAIL_LINES =="
      tail -n "$TAIL_LINES" "$LOG"
    fi
  elif [[ -f "$RUN_ROOT/FINISHED" ]]; then
    echo "Run is finished."
    if [[ -f "$RUN_ROOT/final_summary.md" ]]; then
      echo
      sed -n '1,220p' "$RUN_ROOT/final_summary.md"
    fi
  else
    echo "No current job recorded."
  fi
}

if [[ "${1:-}" == "--watch" ]]; then
  while true; do
    clear
    print_once || true
    sleep "$WATCH_INTERVAL"
  done
else
  print_once
fi
