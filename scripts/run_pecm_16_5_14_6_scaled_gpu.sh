#!/usr/bin/env bash
set -euo pipefail

# (16,6) is infeasible with current backends (int64 target cache ~22 GB > GPU;
# streaming apply recomputes ~2.77B pure-Python transitions per iteration).
# Run the two feasible flanks instead: (16,5) pushes the 2-adic axis,
# (14,6) pushes the 3-adic axis, both past the completed (14,5) level.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/pecm_16_5_14_6_scaled_gpu_${STAMP}}"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/run.log"

run_level() {
  local config="$1"
  local tag="$2"
  local artifact="$RUN_DIR/post_exit_pecm_scaled_${tag}_gpu.json"
  local checkpoint="$RUN_DIR/scaled_perron_checkpoint_${tag}.npz"
  {
    echo
    echo "== level ${config} started_at=$(date --iso-8601=seconds) =="
    nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader || true
  } | tee -a "$LOG"
  uv run python -m collatz_exp.experiments \
    --post-exit-scaled-perron \
    --post-exit-configs "$config" \
    --post-exit-operator-mode gpu_target_cache \
    --post-exit-perron-iterations "${POST_EXIT_PERRON_ITERATIONS:-80}" \
    --post-exit-checkpoint "$checkpoint" \
    --post-exit-checkpoint-interval "${POST_EXIT_CHECKPOINT_INTERVAL:-1}" \
    --post-exit-scaled-perron-output "$artifact" \
    --max-hardness-power 12 2>&1 | tee -a "$LOG"
  {
    echo "== level ${config} finished_at=$(date --iso-8601=seconds) artifact=$artifact =="
  } | tee -a "$LOG"
}

{
  echo "started_at=$(date --iso-8601=seconds)"
  echo "root=$ROOT"
  echo "run_dir=$RUN_DIR"
  echo
  echo "== git head =="
  git log --oneline -1
  git status --short
} | tee "$LOG"

run_level 16:5 16_5
run_level 14:6 14_6

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
} | tee -a "$LOG"
