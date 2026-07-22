#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/pecm_14_5_scaled_gpu_${STAMP}}"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/run.log"
ARTIFACT="$RUN_DIR/post_exit_pecm_scaled_14_5_gpu.json"
CHECKPOINT="$RUN_DIR/scaled_perron_checkpoint.npz"

{
  echo "started_at=$(date --iso-8601=seconds)"
  echo "root=$ROOT"
  echo "run_dir=$RUN_DIR"
  echo
  echo "== git status =="
  git status --short
  echo
  echo "== git diff stat =="
  git diff --stat
  echo
  echo "== gpu =="
  nvidia-smi || true
  ./scripts/gpu_power_snapshot.sh
  echo
  echo "== command =="
  printf '%q ' \
    uv run python -m collatz_exp.experiments \
      --post-exit-scaled-perron \
      --post-exit-configs 14:5 \
      --post-exit-operator-mode gpu_target_cache \
      --post-exit-perron-iterations "${POST_EXIT_PERRON_ITERATIONS:-80}" \
      --post-exit-checkpoint "$CHECKPOINT" \
      --post-exit-checkpoint-interval "${POST_EXIT_CHECKPOINT_INTERVAL:-1}" \
      --post-exit-scaled-perron-output "$ARTIFACT" \
      --max-hardness-power 12
  echo
  echo
} | tee "$LOG"

uv run python -m collatz_exp.experiments \
  --post-exit-scaled-perron \
  --post-exit-configs 14:5 \
  --post-exit-operator-mode gpu_target_cache \
  --post-exit-perron-iterations "${POST_EXIT_PERRON_ITERATIONS:-80}" \
  --post-exit-checkpoint "$CHECKPOINT" \
  --post-exit-checkpoint-interval "${POST_EXIT_CHECKPOINT_INTERVAL:-1}" \
  --post-exit-scaled-perron-output "$ARTIFACT" \
  --max-hardness-power 12 2>&1 | tee -a "$LOG"

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
  echo "artifact=$ARTIFACT"
  echo "checkpoint=$CHECKPOINT"
} | tee -a "$LOG"
