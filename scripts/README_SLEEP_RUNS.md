# Sleep Run Menu

Run these from the repository root.

## Preflight Canary

Fast end-to-end GPU path check with checkpoint and JSON output:

```bash
./scripts/run_pecm_canary_gpu.sh
```

## Benchmark Backends

Compares streaming chunk sizes and the CuPy target-cache backend on a small
PECM level. Use this before the long run if you want a local timing table.

```bash
./scripts/benchmark_pecm_backends.sh
```

Useful overrides:

```bash
POST_EXIT_CONFIGS=10:3 \
POST_EXIT_R_VALUES=2,3,4,5,6,7,8,9,10 \
POST_EXIT_PERRON_ITERATIONS=3 \
POST_EXIT_CHUNK_ROWS_LIST="25000 50000 100000 250000" \
./scripts/benchmark_pecm_backends.sh
```

## Validation Run

Runs the known `(12,4)` PECM scaled Perron level on the GPU. Good before the
full `(14,5)` job.

```bash
POST_EXIT_PERRON_ITERATIONS=20 ./scripts/run_pecm_12_4_scaled_gpu_validation.sh
```

## Main Overnight Run

The full `(14,5)` GPU target-cache scaled Perron run, with checkpointing every
iteration:

```bash
./scripts/run_pecm_14_5_scaled_gpu.sh
```

Shorter probe:

```bash
POST_EXIT_PERRON_ITERATIONS=20 ./scripts/run_pecm_14_5_scaled_gpu.sh
```

## One-Command Sleep Sequence

Runs canary, then `(12,4)` validation, then `(14,5)` main.

```bash
./scripts/run_sleep_sequence_gpu.sh
```

Useful overrides:

```bash
CANARY_ITERATIONS=4 \
VALIDATION_ITERATIONS=20 \
MAIN_ITERATIONS=80 \
./scripts/run_sleep_sequence_gpu.sh
```

## Original Frontier 2: State-Debt Certificate

Runs the bucketed state-debt LP and saves JSON. This is the path for turning
the finite PECM debt certificate into a sharper artifact.

```bash
./scripts/run_post_exit_debt_cpu_audit.sh
```

## Original Frontier 3: D_PE Continued-Fraction Theorem

The same debt audit script also runs structural debt, continued-fraction
certification, and the convergent atlas. Tighter/larger run:

```bash
POST_EXIT_CONFIGS=8:3,10:4,12:4 \
POST_EXIT_K=8 \
POST_EXIT_ELL=3 \
DEBT_BUCKET_WIDTH=0.01 \
./scripts/run_post_exit_debt_cpu_audit.sh
```

## Original Frontier 4: Chang/Tao Pointwise Bridge

Runs the k<=8 m-step Foster audit, Chang bit-4 balance audit, and pointwise
descent audit with JSON outputs:

```bash
./scripts/run_chang_tao_bridge_audit.sh
```

Shorter probe:

```bash
ORBIT_RANGE_SAMPLES=20000 \
CHANG_BIT4_SAMPLES=20000 \
POINTWISE_DESCENT_SAMPLES=20000 \
./scripts/run_chang_tao_bridge_audit.sh
```

## Original Frontier 5: Christoffel/Karp Scaling

Runs the Karp/slope joint sweep plus exact tail-cycle realizability audit:

```bash
./scripts/run_christoffel_karp_scaling_audit.sh
```

Deeper but heavier:

```bash
KARP_SLOPE_LEVELS=5:4,6:5,7:6,8:7 \
TAIL_CYCLE_LEVELS=5:4,6:5,7:6,8:7 \
CHRISTOFFEL_MAX_CYCLE_EDGES=12 \
TAIL_CYCLE_MAX_CYCLES_SCANNED=300000 \
./scripts/run_christoffel_karp_scaling_audit.sh
```
