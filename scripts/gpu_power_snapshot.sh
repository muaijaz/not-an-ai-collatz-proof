#!/usr/bin/env bash
set -euo pipefail

nvidia-smi -i "${GPU_INDEX:-0}" \
  --query-gpu=name,power.limit,power.draw,power.default_limit,power.max_limit,temperature.gpu \
  --format=csv || true
