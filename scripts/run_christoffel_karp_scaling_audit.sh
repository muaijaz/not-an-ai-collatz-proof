#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/christoffel_karp_scaling_${STAMP}}"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/run.log"
KARP_JSON="$RUN_DIR/karp_slope_joint_sweep.json"
REALIZABILITY_JSON="$RUN_DIR/tail_cycle_realizability.json"

{
  echo "started_at=$(date --iso-8601=seconds)"
  echo "root=$ROOT"
  echo "run_dir=$RUN_DIR"
  echo
  echo "== git status =="
  git status --short
  echo
  echo "== command =="
  printf '%q ' \
    uv run python -m collatz_exp.experiments \
      --karp-slope-joint-sweep \
      --tail-cycle-realizability \
      --karp-slope-levels "${KARP_SLOPE_LEVELS:-5:4,6:5,7:6}" \
      --karp-slope-periods "${KARP_SLOPE_PERIODS:-4,5,6}" \
      --karp-slope-tolerances "${KARP_SLOPE_TOLERANCES:-0.5}" \
      --tail-cycle-realizability-levels "${TAIL_CYCLE_LEVELS:-5:4,6:5,7:6}" \
      --karp-slope-joint-output "$KARP_JSON" \
      --tail-cycle-realizability-output "$REALIZABILITY_JSON" \
      --christoffel-max-cycle-edges "${CHRISTOFFEL_MAX_CYCLE_EDGES:-10}" \
      --christoffel-max-cycles-scanned "${CHRISTOFFEL_MAX_CYCLES_SCANNED:-50000}" \
      --tail-cycle-max-cycles-scanned "${TAIL_CYCLE_MAX_CYCLES_SCANNED:-200000}" \
      --tail-cycle-audit-all-cycles \
      --max-hardness-power 12
  echo
  echo
} | tee "$LOG"

uv run python -m collatz_exp.experiments \
  --karp-slope-joint-sweep \
  --tail-cycle-realizability \
  --karp-slope-levels "${KARP_SLOPE_LEVELS:-5:4,6:5,7:6}" \
  --karp-slope-periods "${KARP_SLOPE_PERIODS:-4,5,6}" \
  --karp-slope-tolerances "${KARP_SLOPE_TOLERANCES:-0.5}" \
  --tail-cycle-realizability-levels "${TAIL_CYCLE_LEVELS:-5:4,6:5,7:6}" \
  --karp-slope-joint-output "$KARP_JSON" \
  --tail-cycle-realizability-output "$REALIZABILITY_JSON" \
  --christoffel-max-cycle-edges "${CHRISTOFFEL_MAX_CYCLE_EDGES:-10}" \
  --christoffel-max-cycles-scanned "${CHRISTOFFEL_MAX_CYCLES_SCANNED:-50000}" \
  --tail-cycle-max-cycles-scanned "${TAIL_CYCLE_MAX_CYCLES_SCANNED:-200000}" \
  --tail-cycle-audit-all-cycles \
  --max-hardness-power 12 2>&1 | tee -a "$LOG"

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
  echo "karp=$KARP_JSON"
  echo "realizability=$REALIZABILITY_JSON"
} | tee -a "$LOG"
