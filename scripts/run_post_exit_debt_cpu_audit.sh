#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/post_exit_debt_cpu_audit_${STAMP}}"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/run.log"
STATE_DEBT_JSON="$RUN_DIR/state_debt_lyapunov.json"
DPE_STRUCTURAL_JSON="$RUN_DIR/d_pe_structural_bound.json"
DPE_CF_JSON="$RUN_DIR/d_pe_continued_fraction.json"
DPE_ATLAS_JSON="$RUN_DIR/d_pe_convergent_atlas.json"

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
      --dpe-structural-bound \
      --dpe-continued-fraction-certification \
      --dpe-convergent-atlas \
      --state-debt-lyapunov \
      --post-exit-configs "${POST_EXIT_CONFIGS:-8:3,10:4,12:4}" \
      --post-exit-k "${POST_EXIT_K:-8}" \
      --post-exit-ell "${POST_EXIT_ELL:-3}" \
      --debt-bucket-width "${DEBT_BUCKET_WIDTH:-0.01}" \
      --state-debt-lyapunov-output "$STATE_DEBT_JSON" \
      --dpe-structural-bound-output "$DPE_STRUCTURAL_JSON" \
      --dpe-continued-fraction-output "$DPE_CF_JSON" \
      --dpe-convergent-atlas-output "$DPE_ATLAS_JSON" \
      --max-hardness-power 12
  echo
  echo
} | tee "$LOG"

uv run python -m collatz_exp.experiments \
  --dpe-structural-bound \
  --dpe-continued-fraction-certification \
  --dpe-convergent-atlas \
  --state-debt-lyapunov \
  --post-exit-configs "${POST_EXIT_CONFIGS:-8:3,10:4,12:4}" \
  --post-exit-k "${POST_EXIT_K:-8}" \
  --post-exit-ell "${POST_EXIT_ELL:-3}" \
  --debt-bucket-width "${DEBT_BUCKET_WIDTH:-0.01}" \
  --state-debt-lyapunov-output "$STATE_DEBT_JSON" \
  --dpe-structural-bound-output "$DPE_STRUCTURAL_JSON" \
  --dpe-continued-fraction-output "$DPE_CF_JSON" \
  --dpe-convergent-atlas-output "$DPE_ATLAS_JSON" \
  --max-hardness-power 12 2>&1 | tee -a "$LOG"

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
  echo "log=$LOG"
  echo "state_debt=$STATE_DEBT_JSON"
  echo "dpe_structural=$DPE_STRUCTURAL_JSON"
  echo "dpe_cf=$DPE_CF_JSON"
  echo "dpe_atlas=$DPE_ATLAS_JSON"
} | tee -a "$LOG"
