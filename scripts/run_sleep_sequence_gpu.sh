#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_ROOT="${RUN_ROOT:-docs/runs/sleep_sequence_gpu_${STAMP}}"
mkdir -p "$RUN_ROOT"

echo "sleep_sequence_started_at=$(date --iso-8601=seconds)" | tee "$RUN_ROOT/sequence.log"
echo "run_root=$RUN_ROOT" | tee -a "$RUN_ROOT/sequence.log"

echo "== canary ==" | tee -a "$RUN_ROOT/sequence.log"
RUN_DIR="$RUN_ROOT/01_canary" \
  POST_EXIT_PERRON_ITERATIONS="${CANARY_ITERATIONS:-4}" \
  ./scripts/run_pecm_canary_gpu.sh 2>&1 | tee -a "$RUN_ROOT/sequence.log"

echo "== 12:4 validation ==" | tee -a "$RUN_ROOT/sequence.log"
RUN_DIR="$RUN_ROOT/02_12_4_validation" \
  POST_EXIT_PERRON_ITERATIONS="${VALIDATION_ITERATIONS:-20}" \
  ./scripts/run_pecm_12_4_scaled_gpu_validation.sh 2>&1 | tee -a "$RUN_ROOT/sequence.log"

echo "== 14:5 main ==" | tee -a "$RUN_ROOT/sequence.log"
RUN_DIR="$RUN_ROOT/03_14_5_main" \
  POST_EXIT_PERRON_ITERATIONS="${MAIN_ITERATIONS:-80}" \
  ./scripts/run_pecm_14_5_scaled_gpu.sh 2>&1 | tee -a "$RUN_ROOT/sequence.log"

echo "sleep_sequence_finished_at=$(date --iso-8601=seconds)" | tee -a "$RUN_ROOT/sequence.log"
