#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STAMP="${STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_ROOT="${RUN_ROOT:-docs/runs/autonomous_sleep_frontiers_${STAMP}}"
LATEST_LINK="${LATEST_LINK:-docs/runs/latest_autonomous_sleep}"
CONTINUE_ON_FAILURE="${CONTINUE_ON_FAILURE:-0}"

mkdir -p "$RUN_ROOT" "$(dirname "$LATEST_LINK")"
ln -sfn "$ROOT/$RUN_ROOT" "$LATEST_LINK"

STATUS_TSV="$RUN_ROOT/status.tsv"
STATUS_MD="$RUN_ROOT/status.md"
CURRENT_ENV="$RUN_ROOT/current_job.env"
SUMMARY_MD="$RUN_ROOT/final_summary.md"

printf "job\tdescription\tstatus\tstarted_at\tfinished_at\texit_code\tlog\n" > "$STATUS_TSV"

write_status_md() {
  python3 - "$STATUS_TSV" "$STATUS_MD" "$RUN_ROOT" <<'PY'
import csv
import sys
from pathlib import Path

status_tsv = Path(sys.argv[1])
status_md = Path(sys.argv[2])
run_root = Path(sys.argv[3])
rows = list(csv.DictReader(status_tsv.open(), delimiter="\t"))

lines = [
    "# Autonomous Sleep Run Status",
    "",
    f"Run root: `{run_root}`",
    "",
    "| Job | Status | Exit | Started | Finished | Log |",
    "|---|---:|---:|---|---|---|",
]
for row in rows:
    log = row["log"]
    log_link = f"[log]({Path(log).name})" if log else ""
    lines.append(
        f"| {row['job']}<br>{row['description']} | {row['status']} | "
        f"{row['exit_code']} | {row['started_at']} | {row['finished_at']} | {log_link} |"
    )
status_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

append_status() {
  local job="$1"
  local description="$2"
  local status="$3"
  local started="$4"
  local finished="$5"
  local exit_code="$6"
  local log="$7"
  python3 - "$STATUS_TSV" "$job" "$description" "$status" "$started" "$finished" "$exit_code" "$log" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
new_row = {
    "job": sys.argv[2],
    "description": sys.argv[3],
    "status": sys.argv[4],
    "started_at": sys.argv[5],
    "finished_at": sys.argv[6],
    "exit_code": sys.argv[7],
    "log": sys.argv[8],
}
fields = ["job", "description", "status", "started_at", "finished_at", "exit_code", "log"]
rows = []
if path.exists():
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["job"] != new_row["job"]]
rows.append(new_row)
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)
PY
  write_status_md
}

mark_current() {
  local job="$1"
  local description="$2"
  local log="$3"
  {
    printf "JOB=%q\n" "$job"
    printf "DESCRIPTION=%q\n" "$description"
    printf "LOG=%q\n" "$log"
    printf "RUN_ROOT=%q\n" "$RUN_ROOT"
    printf "STARTED_AT=%q\n" "$(date --iso-8601=seconds)"
  } > "$CURRENT_ENV"
}

clear_current() {
  rm -f "$CURRENT_ENV"
}

run_job() {
  local job="$1"
  local description="$2"
  shift 2
  local job_dir="$RUN_ROOT/$job"
  local log="$job_dir/job.log"
  local started finished code
  mkdir -p "$job_dir"
  started="$(date --iso-8601=seconds)"
  mark_current "$job" "$description" "$log"
  append_status "$job" "$description" "running" "$started" "" "" "$log"

  {
    echo "job=$job"
    echo "description=$description"
    echo "started_at=$started"
    echo "root=$ROOT"
    echo "run_root=$RUN_ROOT"
    echo
    echo "== command =="
    printf "%q " "$@"
    echo
    echo
    echo "== git status =="
    git status --short
    echo
    echo "== gpu =="
    nvidia-smi || true
  ./scripts/gpu_power_snapshot.sh
    echo
  } | tee "$log"

  set +e
  "$@" 2>&1 | tee -a "$log"
  code="${PIPESTATUS[0]}"
  set -e

  finished="$(date --iso-8601=seconds)"
  append_status "$job" "$description" "finished" "$started" "$finished" "$code" "$log"
  clear_current
  echo "job=$job finished_at=$finished exit_code=$code" | tee -a "$log"

  if [[ "$code" != "0" && "$CONTINUE_ON_FAILURE" != "1" ]]; then
    echo "Stopping autonomous run because $job failed. Set CONTINUE_ON_FAILURE=1 to continue." | tee -a "$log"
    finalize_summary "$code"
    exit "$code"
  fi
}

finalize_summary() {
  local code="${1:-0}"
  {
    echo "# Autonomous Sleep Run Summary"
    echo
    echo "Finished: $(date --iso-8601=seconds)"
    echo "Exit code: $code"
    echo "Run root: \`$RUN_ROOT\`"
    echo
    echo "Status file: \`$STATUS_MD\`"
    echo
    echo "Artifacts:"
    find "$RUN_ROOT" -maxdepth 3 \( -name '*.json' -o -name '*.npz' -o -name '*.tsv' \) | sort | sed 's/^/- `/' | sed 's/$/`/'
  } > "$SUMMARY_MD"
  cp "$STATUS_MD" "$RUN_ROOT/status_final.md"
  touch "$RUN_ROOT/FINISHED"
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "Collatz sleep run finished" "Exit code $code: $RUN_ROOT" || true
  fi
}

{
  echo "# Autonomous Sleep Run"
  echo
  echo "Started: $(date --iso-8601=seconds)"
  echo "Run root: \`$RUN_ROOT\`"
  echo "Latest symlink: \`$LATEST_LINK\`"
  echo
  echo "Monitor:"
  echo
  echo "\`\`\`bash"
  echo "./scripts/monitor_autonomous_sleep_run.sh"
  echo "./scripts/monitor_autonomous_sleep_run.sh --watch"
  echo "\`\`\`"
} > "$RUN_ROOT/README.md"
write_status_md

echo "autonomous_sleep_run_started_at=$(date --iso-8601=seconds)"
echo "run_root=$RUN_ROOT"
echo "latest=$LATEST_LINK"

if [[ "${RUN_CANARY:-1}" == "1" ]]; then
  run_job "01_canary_gpu" "GPU canary with checkpoint/artifact" \
    env RUN_DIR="$RUN_ROOT/01_canary_gpu" \
      POST_EXIT_PERRON_ITERATIONS="${CANARY_ITERATIONS:-4}" \
      ./scripts/run_pecm_canary_gpu.sh
fi

if [[ "${RUN_STATE_DEBT_AND_DPE:-1}" == "1" ]]; then
  run_job "02_state_debt_dpe" "Original frontiers 2-3: state debt plus D_PE continued-fraction audits" \
    env RUN_DIR="$RUN_ROOT/02_state_debt_dpe" \
      POST_EXIT_CONFIGS="${DPE_POST_EXIT_CONFIGS:-8:3,10:4,12:4}" \
      POST_EXIT_K="${DPE_POST_EXIT_K:-8}" \
      POST_EXIT_ELL="${DPE_POST_EXIT_ELL:-3}" \
      DEBT_BUCKET_WIDTH="${DEBT_BUCKET_WIDTH:-0.01}" \
      ./scripts/run_post_exit_debt_cpu_audit.sh
fi

if [[ "${RUN_CHANG_TAO:-1}" == "1" ]]; then
  run_job "03_chang_tao_bridge" "Original frontier 4: Chang/Tao pointwise bridge audits" \
    env RUN_DIR="$RUN_ROOT/03_chang_tao_bridge" \
      ORBIT_RANGE_SAMPLES="${ORBIT_RANGE_SAMPLES:-200000}" \
      CHANG_BIT4_SAMPLES="${CHANG_BIT4_SAMPLES:-200000}" \
      POINTWISE_DESCENT_SAMPLES="${POINTWISE_DESCENT_SAMPLES:-200000}" \
      ./scripts/run_chang_tao_bridge_audit.sh
fi

if [[ "${RUN_CHRISTOFFEL_KARP:-1}" == "1" ]]; then
  run_job "04_christoffel_karp" "Original frontier 5: Christoffel/Karp scaling and realizability" \
    env RUN_DIR="$RUN_ROOT/04_christoffel_karp" \
      KARP_SLOPE_LEVELS="${KARP_SLOPE_LEVELS:-5:4,6:5,7:6}" \
      KARP_SLOPE_PERIODS="${KARP_SLOPE_PERIODS:-4,5,6}" \
      TAIL_CYCLE_LEVELS="${TAIL_CYCLE_LEVELS:-5:4,6:5,7:6}" \
      CHRISTOFFEL_MAX_CYCLE_EDGES="${CHRISTOFFEL_MAX_CYCLE_EDGES:-10}" \
      TAIL_CYCLE_MAX_CYCLES_SCANNED="${TAIL_CYCLE_MAX_CYCLES_SCANNED:-200000}" \
      ./scripts/run_christoffel_karp_scaling_audit.sh
fi

if [[ "${RUN_GPU_VALIDATION:-1}" == "1" ]]; then
  run_job "05_pecm_12_4_validation" "GPU validation: PECM (12,4) scaled Perron" \
    env RUN_DIR="$RUN_ROOT/05_pecm_12_4_validation" \
      POST_EXIT_PERRON_ITERATIONS="${VALIDATION_ITERATIONS:-20}" \
      ./scripts/run_pecm_12_4_scaled_gpu_validation.sh
fi

if [[ "${RUN_MAIN_GPU:-1}" == "1" ]]; then
  run_job "06_pecm_14_5_main" "Main GPU overnight: PECM (14,5) scaled Perron" \
    env RUN_DIR="$RUN_ROOT/06_pecm_14_5_main" \
      POST_EXIT_PERRON_ITERATIONS="${MAIN_ITERATIONS:-80}" \
      ./scripts/run_pecm_14_5_scaled_gpu.sh
fi

finalize_summary 0
echo "autonomous_sleep_run_finished_at=$(date --iso-8601=seconds)"
echo "summary=$SUMMARY_MD"
