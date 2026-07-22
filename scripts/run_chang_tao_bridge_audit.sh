#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/chang_tao_bridge_audit_${STAMP}}"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/run.log"
MSTEP_JSON="$RUN_DIR/m_step_foster_drift_k8.json"
CHANG_JSON="$RUN_DIR/chang_bit4_balance_audit.json"
POINTWISE_JSON="$RUN_DIR/pointwise_descent_audit.json"

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
      --m-step-foster-drift-k8 \
      --chang-bit4-audit \
      --pointwise-descent-audit \
      --orbit-range-samples "${ORBIT_RANGE_SAMPLES:-200000}" \
      --chang-bit4-samples "${CHANG_BIT4_SAMPLES:-200000}" \
      --pointwise-descent-samples "${POINTWISE_DESCENT_SAMPLES:-200000}" \
      --m-step-foster-drift-k8-output "$MSTEP_JSON" \
      --chang-bit4-audit-output "$CHANG_JSON" \
      --pointwise-descent-audit-output "$POINTWISE_JSON" \
      --max-hardness-power 12
  echo
  echo
} | tee "$LOG"

uv run python -m collatz_exp.experiments \
  --m-step-foster-drift-k8 \
  --chang-bit4-audit \
  --pointwise-descent-audit \
  --orbit-range-samples "${ORBIT_RANGE_SAMPLES:-200000}" \
  --chang-bit4-samples "${CHANG_BIT4_SAMPLES:-200000}" \
  --pointwise-descent-samples "${POINTWISE_DESCENT_SAMPLES:-200000}" \
  --m-step-foster-drift-k8-output "$MSTEP_JSON" \
  --chang-bit4-audit-output "$CHANG_JSON" \
  --pointwise-descent-audit-output "$POINTWISE_JSON" \
  --max-hardness-power 12 2>&1 | tee -a "$LOG"

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
  echo "m_step_foster=$MSTEP_JSON"
  echo "chang_bit4=$CHANG_JSON"
  echo "pointwise=$POINTWISE_JSON"
} | tee -a "$LOG"
