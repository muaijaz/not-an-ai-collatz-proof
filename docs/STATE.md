# STATE

## Goal
"Do the things" — execute the recommended next steps from the repo survey: commit pending work, launch (16,6) streaming PECM run, Polli long-range-correlation audit, exact-rational Perron certification slice.

## Now
Waiting on two background jobs: (a) GPU scaled-Perron at (16,5) then (14,6) via scripts/run_pecm_16_5_14_6_scaled_gpu.sh; (b) perron-certificate run at 8:2,10:3,12:4 writing docs/reports/pecm_perron_certificates.json.

## Next
1. When certification finishes: review artifact, then commit renewal_correlation + perron_certificate modules/tests/wiring + Polli artifacts + runner script.
2. When GPU run finishes: review (16,5)/(14,6) artifacts, report results, commit docs/runs additions.
3. Final summary to user (incl. Polli verdict + certified bounds + open outward-facing decisions).

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
- Exact-rational Perron certification (collatz_exp/perron_certificate.py, 4 tests) — RESULT: SCC-decomposed Collatz-Wielandt bounds; (8,2) certified rho <= 0.388056211 exact rational, contraction True, only 6 nontrivial blocks (largest 16 states) of 33408. Full suite 201 passed.

## Open items
- Chang/Siegel outreach emails (drafted in docs, unsent) — awaiting user decision.
- arXiv submission decision — awaiting user.
- (16,6) run results → update frontier dashboard artifact once complete.

## Failed attempts
(none yet)
