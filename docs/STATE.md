# STATE

## Goal
"Do the things" — execute the recommended next steps from the repo survey: commit pending work, launch (16,6) streaming PECM run, Polli long-range-correlation audit, exact-rational Perron certification slice.

## Now
Committing pending working-tree changes in two logical commits (code, then run-harness/artifacts).

## Next
1. Commit code chunk (post_exit_map/experiments/reports/tests/pyproject/uv.lock + frontier_dashboard + its test).
2. Commit scripts/ + docs/runs/ chunk.
3. Launch (16,6) PECM scaled-Perron run in background (streaming or gpu mode per memory estimate), copying scripts/run_pecm_14_5_scaled_gpu.sh structure.
4. New module: renewal-increment long-range-correlation audit (Polli defensive check) + CLI flag + formatter + test; run it; write docs/reports artifact.
5. New module: exact-rational Collatz-Wielandt Perron certification at small PECM level + test; run; write artifact.

## Constraints
- NEVER git push without asking in this conversation (CLAUDE.md hard rule 5).
- Do not send Chang/Siegel outreach emails or submit to arXiv — outward-facing, needs explicit user go-ahead.
- Leave `.codex` (empty untracked file) uncommitted.

## Decisions
- DECISION: two commits (code vs run-harness) — experiments.py contains both PECM flags and dashboard wiring, so code lands as one commit.
- DECISION: skip outreach/arXiv items — outward-facing actions excluded from "do the things".

## Facts
- Tests: `uv run python -m pytest -q` → 191 passed (baseline, this session).
- GPU: RTX 3090 Ti 24564 MiB (~21.5 GB free), CuPy 14.0.1 OK.
- (14,5) run completed 2026-06-18: 57.7M states, finite_ratio_max=0.5357, artifact docs/runs/pecm_14_5_scaled_gpu_20260618_015521/.
- (16,6) estimate: ~692.7M states, ~2.77B transitions (docs/collatz_strategy.md).
- CLI: `python -m collatz_exp.experiments --post-exit-scaled-perron --post-exit-configs K:L --post-exit-operator-mode {dense_target_cache,streaming,gpu_target_cache,auto} --post-exit-checkpoint <npz> --post-exit-scaled-perron-output <json>`.

## Done
- Repo survey (2 Explore agents) — RESULT: full state + roadmap synthesis delivered to user; frontier = PECM (16,6) wall, Polli check open threat, paper v0.5 unsubmitted.

## Open items
- Chang/Siegel outreach emails (drafted in docs, unsent) — awaiting user decision.
- arXiv submission decision — awaiting user.
- (16,6) run results → update frontier dashboard artifact once complete.

## Failed attempts
(none yet)
