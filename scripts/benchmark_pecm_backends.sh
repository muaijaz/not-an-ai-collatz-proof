#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="${RUN_DIR:-docs/runs/pecm_backend_benchmark_${STAMP}}"
mkdir -p "$RUN_DIR"

CONFIG="${POST_EXIT_CONFIGS:-8:2}"
R_VALUES="${POST_EXIT_R_VALUES:-2,3,4,5,6,7,8}"
ITERATIONS="${POST_EXIT_PERRON_ITERATIONS:-3}"
CHUNKS="${POST_EXIT_CHUNK_ROWS_LIST:-25000 50000 100000 250000}"
LOG="$RUN_DIR/benchmark.log"
SUMMARY="$RUN_DIR/summary.tsv"

{
  echo "started_at=$(date --iso-8601=seconds)"
  echo "root=$ROOT"
  echo "run_dir=$RUN_DIR"
  echo "config=$CONFIG"
  echo "R_values=$R_VALUES"
  echo "iterations=$ITERATIONS"
  echo "chunks=$CHUNKS"
  echo
  nvidia-smi || true
  ./scripts/gpu_power_snapshot.sh
  echo
} | tee "$LOG"

printf "mode\tchunk_rows\tseconds\tartifact\n" > "$SUMMARY"

run_case() {
  local mode="$1"
  local chunk_rows="$2"
  local label="$3"
  local artifact="$RUN_DIR/${label}.json"
  local checkpoint="$RUN_DIR/${label}.npz"
  local case_log="$RUN_DIR/${label}.log"
  local start end elapsed

  echo "== $label ==" | tee -a "$LOG"
  start="$(date +%s)"
  uv run python -m collatz_exp.experiments \
    --post-exit-scaled-perron \
    --post-exit-configs "$CONFIG" \
    --post-exit-R-values "$R_VALUES" \
    --post-exit-operator-mode "$mode" \
    --post-exit-chunk-rows "$chunk_rows" \
    --post-exit-perron-iterations "$ITERATIONS" \
    --post-exit-checkpoint "$checkpoint" \
    --post-exit-checkpoint-interval 0 \
    --post-exit-scaled-perron-output "$artifact" \
    --max-hardness-power 12 2>&1 | tee "$case_log" | tee -a "$LOG"
  end="$(date +%s)"
  elapsed="$((end - start))"
  printf "%s\t%s\t%s\t%s\n" "$mode" "$chunk_rows" "$elapsed" "$artifact" | tee -a "$SUMMARY"
}

for chunk in $CHUNKS; do
  run_case "streaming" "$chunk" "streaming_chunk_${chunk}"
done

run_case "gpu_target_cache" "0" "gpu_target_cache"

{
  echo
  echo "finished_at=$(date --iso-8601=seconds)"
  echo "summary=$SUMMARY"
} | tee -a "$LOG"
