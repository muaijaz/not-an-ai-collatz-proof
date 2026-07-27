# STATE

## Goal
Resolve the higher-`R` branch of the exact nested PECM exit grammar and
determine whether its induced returns admit a hierarchical Lyapunov function,
without confusing a complete source cover, Haar average, or contracting
subfamily with global Collatz descent.

## Now
The complete `R=2, u mod 2^8 odd, u mod 9=2` target fiber has an exact
symbolic outgoing cover: `96` states descend uniformly and `32` form a
countable reentry family. The family exactly refutes finite mixed
`2`-adic/`3`-adic state-only one-step corrections, but its nested same-`R`
loop contracts under
`K(n,u)=(n+5)(23/22)^v2(u+1)` by `11979/12167`. Maximal loop induction leaves
`S_exit in {1,2,3}`: the first two values descend and the third reenters at
`R_next>=3`. That higher-`R` family remains open.

## Next
1. Parametrize the `S_exit=3` family using
   `R_next=2+v2(9^(j+1)w-1)` and carry compatible target residues.
2. Trace its induced returns to `R=2` or descent and search for the next
   negative-fixed-point coordinate or a multi-return contraction.
3. Run the rational max-times solver only on an exact closed induced
   component; keep the countably infinite open family symbolic.
4. Test whether the nested coordinate can be combined with the outer
   `R`-cusp into one lexicographic or multiplicative potential across exits.
5. Retain chunked/streaming Galerkin and mixed-adic wavelet work as numerical
   support, not the primary theorem-facing lane.
6. Awaiting user: Chang/Siegel outreach emails and arXiv submission decision.

## Constraints
- NEVER git push without asking in this conversation (CLAUDE.md hard rule 5).
- Do not send Chang/Siegel outreach emails or submit to arXiv — outward-facing, needs explicit user go-ahead.
- Leave `.codex` (empty untracked file) uncommitted.

## Decisions
- DECISION: two commits (code vs run-harness) — experiments.py contains both PECM flags and dashboard wiring, so code lands as one commit.
- DECISION: skip outreach/arXiv items — outward-facing actions excluded from "do the things".
- DECISION: construct every comparison level from one finest sampled operator
  by exact sequential Galerkin coarsening; independently sampled levels are
  reported only as a non-compatible legacy diagnostic.
- DECISION: reject unresolved transition windows by default, label float64
  vectors as numerical rather than exact, and cap in-memory work at `250,000`
  states and `2,000,000` retained target entries.
- DECISION: use numerical PECM data only to rank a seed; require the extra
  `2`-adic bit for an exact valuation word and exact congruence coverage for
  every reported branch.
- DECISION: do not run or quote Karp on an open exact target frontier.
- DECISION: represent the outgoing `R=2` frontier as a countable parametric
  family. Its required source precision grows with target depth, so no finite
  adaptive cylinder enumeration can be complete.
- DECISION: demote the global outer-only class `n^alpha c^R`; an exact
  expanding `R=2 -> 2` branch refutes it for every `alpha>0`.
- DECISION: promote `S=v2(u+1)=v2(n+5)-2` as a nested cusp coordinate, but
  claim contraction only on consecutive same-`R` loops; the induced exit
  grammar is exact, but no contraction across its higher-`R` branch is yet
  claimed.

## Facts
- Tests: `uv run python -m pytest -q` -> 262 passed in 3.63s.
- Exact selected root: `(R,u mod 2^11,u mod 9)=(9,55,2)`.
- Full word `(1^8,3,2,4)` has `(m,A,B)=(11,17,186875)` and exact slope
  `177147/131072 > 1`; its one-word affine fixed point is the noninteger
  `-7475/1843`.
- Refinement to `u mod 2^18` produces exactly `128` verified children and all
  `128` odd target residues modulo `256` at `(R',u mod 9)=(2,2)`.
- Exact local cusp bound:
  `H(F(n),2)/H(n,9) <= 7164821035427968/7236312975589017 < 1`.
- Complete `R=2` mod-8 partition: `96/128` coarse states descend uniformly;
  `32/128` form a countable reentry family with
  `r=v2(9u+1)-1>=2`.
- At each fixed `r`, the live family has exactly `128` target-fixed source
  leaves and reaches every odd target residue modulo `256`.
- Outer-tail obstruction: `u=47`, `187 -> 211`, with `R=2 -> 2`; hence
  `n^alpha c^R` increases for every `alpha>0`, `c>0`.
- Every finite mixed `2`-adic/`3`-adic resolution has a positive expanding
  coarse self-loop.
  Fixture `(k,ell)=(4,2)`: `u=1151`, `4603 -> 5179`, coarse state
  `(R,u mod16,u mod9)=(2,15,8)` at both ends.
- Nested cusp: `S=v2(u+1)` drops by `3`, `n+5` grows by `9/8`, and
  `(n+5)(23/22)^S` contracts exactly by `11979/12167`.
- Consecutive same-`R` loop count is exactly `floor((S-1)/3)`.
- Maximal-loop exit grammar: `S_exit=1,2,3` gives first-post descent,
  second-post descent, or higher-`R` reentry. Descent is relative to the
  compressed exit source. Exact normalized Haar masses among odd 2-adic
  units are `4/7`, `2/7`, and `1/7`; the last branch has
  `R_next=2+v2(9^(j+1)w-1)>=3`.
- Galerkin smoke ladder: `(4,0) -> (6,1) -> (8,2)`,
  `R = 2..30`, common `alpha = 0.55`, 0 unresolved samples.
- Numerical `max(Mh/h)`: `0.465489`, `0.502925`, `0.529990`.
- Minimax `E_mean`: `0.189683`, then `0.362275`; maximum log lift
  spread: `1.921116`, then `2.923891`.
- Maximum live target ratio: `5.267161` on the Galerkin-induced middle
  kernel, then `1.995672` on the concrete finest samples; averaged
  contraction does not collapse to pointwise contraction.
- Primary ladder has exact Galerkin identity only; pointwise projective and
  full conditional-expectation defects remain nonzero. Both independently
  sampled adjacent pairs are non-compatible.
- Artifact:
  `docs/reports/pecm_cross_resolution_consistency.json`.
- Exact branch artifact:
  `docs/reports/pecm_exact_selected_cylinder_pilot.json`.
- Exact recursive-frontier artifact:
  `docs/reports/pecm_r2_recursive_tail_cusp.json`.
- GPU: RTX 3090 Ti 24564 MiB (~21.5 GB free), CuPy 14.0.1 OK.
- (14,5) run completed 2026-06-18: 57.7M states, finite_ratio_max=0.5357, artifact docs/runs/pecm_14_5_scaled_gpu_20260618_015521/.
- (16,6) estimate: ~692.7M states, ~2.77B transitions (docs/collatz_strategy.md).
- CLI: `python -m collatz_exp.experiments --post-exit-scaled-perron --post-exit-configs K:L --post-exit-operator-mode {dense_target_cache,streaming,gpu_target_cache,auto} --post-exit-checkpoint <npz> --post-exit-scaled-perron-output <json>`.

## Done
- Exact recursive `R=2` frontier
  (`collatz_exp/symbolic_frontier_certificate.py`) — RESULT: exhaustive mod-8
  source partition, exact countable target-depth parametrization, all odd
  target residues at every fixed depth, realizable finite-state no-go
  witnesses, exact nested-cusp contraction, exact maximal-loop exit grammar,
  deterministic report, and explicit open higher-`R` status.
- Exact selected-cylinder branch pilot
  (`collatz_exp/symbolic_branch_certificate.py`) — RESULT: correct
  `2^(A+1)` exact-word cylinders, exact post-exit precision carry, exhaustive
  `128`-leaf partition, exact affine/cycle audit, local rational tail-cusp
  certificate, explicit open-frontier status, and a reusable exact rational
  max-times feasibility/obstruction solver.
- Common-alpha PECM vector export (`collatz_exp/pecm_vector_export.py`) —
  RESULT: deterministic state hashes and full per-state `h`, `Mh/h`, and graph
  role records; unresolved windows rejected by default; float output explicitly
  proof-ineligible; oversized materialized exports guarded.
- Exact mixed-adic refinement (`collatz_exp/pecm_refinement.py`) — RESULT:
  canonical parent/fiber maps, exact prolongation/averaging, associative
  Galerkin coarsening, and separately named Galerkin, pointwise-projective, and
  full conditional-expectation defects.
- Cross-resolution consistency (`collatz_exp/pecm_consistency.py`) — RESULT:
  common-alpha Galerkin ladder, exact minimax lift alignment, spread
  quantiles, worst states, survival-corrected branch bounds, legacy sampling
  comparison, deterministic JSON artifact.
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
- A single outer-tail potential `n^alpha c^R` cannot be global: the exact
  `187 -> 211` branch expands while preserving `R=2`.
- Positive corrections on any fixed finite mixed `2`-adic/`3`-adic residue
  quotient cannot provide strict one-step descent: every such quotient
  contains a realizable expanding coarse self-loop.
