# STATE

## Goal
"Do the things" — execute the recommended next steps from the repo survey: commit pending work, launch (16,6) streaming PECM run, Polli long-range-correlation audit, exact-rational Perron certification slice.

## Now
"Do the things" batch complete; all results committed locally (nothing pushed).

## Next
1. Candidate next step (not started): streaming SCC pass to extend exact Perron certificates to (14,5)/(16,5)/(16,6) — recurrent cores are tiny (<=984 states at (12,4)) so only block extraction needs to scale.
2. Awaiting user: Chang/Siegel outreach emails, arXiv submission decision.

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
- Commits 4ba7a91 (PECM streaming/GPU/checkpoint + frontier dashboard) and a66644d (scripts/ + docs/runs/ + STATE.md) — RESULT: working tree clean except .codex; 191 tests green before commit.
- (16,6) feasibility check — RESULT: infeasible with current backends (streaming = ~2.77B pure-Python transitions/iteration at post_exit_map.py:930-967; gpu/dense cache = int64 ~22GB > 21.5GB free GPU / 34GB avail RAM). Running (16,5)+(14,6) flanks instead.
- Polli long-range-correlation audit (collatz_exp/renewal_correlation.py, 6 tests) — RESULT: iid_consistent on all three series at 400-bit and 1000-bit windows; DFA alpha 0.52-0.53 vs surrogate 0.52-0.54; ACF maxima at null band. IID renewal model survives. Artifacts: docs/reports/renewal_correlation_polli_{400,1000}bit.json.
- Exact-rational Perron certification (collatz_exp/perron_certificate.py, 4 tests) — RESULT: SCC-decomposed Collatz-Wielandt bounds; certified rho <= 0.3880562 (8,2), 0.3451143 (10,3), 0.3341154 (12,4), all contractions; recurrent cores tiny (<=984 of 4.81M states). Full suite 201 passed. Committed a75dcd0.
- GPU scaled-Perron flanks (docs/runs/pecm_16_5_14_6_scaled_gpu_20260722_130030) — RESULT: (16,5) scale=0.336040 ratio_max=0.33627 inf=0; (14,6) scale=0.342979 ratio_max=0.34332 inf=0; both 80 iters, worst state R=2. Pointwise contraction candidates hold on both axes past (14,5).

## Open items
- Chang/Siegel outreach emails (drafted in docs, unsent) — awaiting user decision.
- arXiv submission decision — awaiting user.
- (16,6) run results → update frontier dashboard artifact once complete.

## Failed attempts
(none yet)
