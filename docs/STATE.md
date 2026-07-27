# STATE

## Goal
Recursively close the four expanding exits of the exact exhausted
`(1,1,2)` partition and determine whether valuation resonances have bounded
complexity or admit one compatible Lyapunov inequality, without confusing an
infinite descent cylinder with a global Collatz proof.

## Now
Exact word membership and repeat counts are now controlled by one affine
linear form. An expanding word `W` is exact iff
`v2(L_W(n))>=A_W+1`, and it repeats exactly
`floor((v2(L_W(n))-1)/A_W)` times. At a maximal chart exit, every legal
nonresonant switch strictly lowers `A`; any chart cycle must contain a 2-adic
cancellation resonance. The `W=(1,1,2)` exit partition is complete and has
four expanding target charts. One resonant path gives first descent at step
13 for every `n=38119 mod 2^22`. No bound on successive resonances has been
derived, and the induced chart graph is still open.

## Next
1. Derive complete maximal-exit partitions for `(1,2)`, `(1,1,1,1)`,
   `(1,1,1,2)`, and `(1,1,1,3)`.
2. Store every integer ghost gap `G`, distinguish nonresonant strict
   `A`-decrease from valuation resonance, and look for a second
   well-founded quantity on resonance edges.
3. Determine whether repeated resonance depth is bounded, eventually
   periodic, or represented by an explicit infinite positive-integer family.
4. On any exact finite closed component, solve rational weighted
   chart-switch inequalities with explicit finite magnitude exceptions.
5. Use cusp-renormalized PECM vectors only to rank candidate charts and
   edges, not as pointwise proof.
6. Retain chunked/streaming Galerkin and mixed-adic wavelet work as numerical
   support, not the primary theorem-facing lane.
7. Awaiting user: Chang/Siegel outreach emails and arXiv submission decision.

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
  claim it only on consecutive same-`R` loops and their complete `(1,2)^m`
  higher-`R` handoff, with exact factor `(11979/12167)^m`; no contraction is
  claimed for the subsequent higher-`R` macro.
- DECISION: demote the single global `-5` cusp after the exact
  `1183 -> 4495` obstruction; retain it as the correct `R=2` phase chart.
- DECISION: represent each expanding exact valuation word by its own affine
  ghost `g_W=-B/(3^M-2^A)` and valuation coordinate
  `L_W=(3^M-2^A)n+B`.
- DECISION: treat the additive ghost-gap term at chart switches as the next
  proof obstruction. Wordwise factors cannot be multiplied globally until
  compatible edge inequalities are proved.
- DECISION: replace the old necessary repeat budget by the exact theorem
  `floor((v2(L_W)-1)/A_W)`; retain `v2(0)=infinity` for contracting fixed
  points.
- DECISION: call `G=0` a same-ghost/zero-gap switch and reserve
  "valuation resonance" for nonzero `G` with equal residual and gap
  valuations.
- DECISION: decompose induced paths into maximal expanding-word runs before
  applying the strict nonresonant `A`-decrease corollary.
- DECISION: treat `n=38119 mod 2^22` as a full binary first-descent cylinder;
  its earlier mixed 3-adic subfamily is provenance, not a restriction on the
  local theorem.

## Facts
- Tests: `uv run python -m pytest -q` -> 325 passed.
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
- Higher-`R` transfer: for `m>=1`,
  `2^(3m+2)w-5 --(1,2)^m--> 4*9^m*w-5`, with every `R>=3` and every odd
  target 2-adic residue represented.
- Transfer precision: fixing target `v mod 2^k` at depth `R` requires source
  `u mod 2^(3m+R+k-2)`; source precision `mod 3^ell` determines target
  precision `mod 3^(ell+2m)`.
- Full-phase cusp ratio:
  `EH(n1)/E2(n0)=(11979/12167)^m<1`.
- First higher-`R` stage:
  `Z=(3^R v-1)/2^q`, `q=v2(3^R v-1)`, and
  `Z<N iff (2^(R+q)-3^R)v>2^q-1`.
- Simple-cusp obstruction: `1051 -> 1183 -> 4495`; the last transition has
  shifted ratio `125/33>1` for every base.
- Affine-ghost theorem:
  `L_W(T_W(n))=(3^M/2^A)L_W(n)` and
  `v2(L_W(T_W(n)))=v2(L_W(n))-A`.
- Certified affine ghosts: `179n+211` with factor `15552/15625`, and
  `11n+19` with factor `64827/65536`.
- Universal exact-word theorem: `W` is exact at odd `n` iff
  `v2(|L_W(n)|)>=A+1`, taking `v2(0)=infinity`.
- Exact repeat count for expanding `W`:
  `floor((v2(L_W(n))-1)/A)`.
- Chart-switch identity has the additive term
  `B_V-D_V*B_W/D_W`; its integer numerator is
  `G_VW=B_V D_W-D_V B_W`.
- Maximal-exit resonance theorem: if residual depth and `v2(|G_VW|)` differ,
  target depth is their minimum. Every legal nonresonant edge strictly lowers
  `A`, so every maximal-chart cycle contains a resonance.
- `W=(1,1,2)` exit residuals `e=1..4` have exact normalized masses
  `8/15,4/15,2/15,1/15`; its expanding targets are exactly `(1,2)`,
  `(1,1,1,1)`, `(1,1,1,2)`, and `(1,1,1,3)`.
- Exact maximal-word fixture path:
  `38119 --(1,1,2)^2--> 108553 --(2,1,1,2)--> 137389
  --(3,2,2)--> 28981`.
- The full 13-step word has `(M,A,B)=(13,21,3563675)` and is exact for
  every `n=38119+2^22*t`. Its first descent is
  `28981+2*3^13*t`, with gap `9138+1005658*t`.
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
- Exact higher-`R`/affine-ghost artifact:
  `docs/reports/pecm_higher_r_affine_ghost.json`.
- Exact repeat/resonance atlas artifact:
  `docs/reports/pecm_affine_ghost_atlas.json`.
- GPU: RTX 3090 Ti 24564 MiB (~21.5 GB free), CuPy 14.0.1 OK.
- (14,5) run completed 2026-06-18: 57.7M states, finite_ratio_max=0.5357, artifact docs/runs/pecm_14_5_scaled_gpu_20260618_015521/.
- (16,6) estimate: ~692.7M states, ~2.77B transitions (docs/collatz_strategy.md).
- CLI: `python -m collatz_exp.experiments --post-exit-scaled-perron --post-exit-configs K:L --post-exit-operator-mode {dense_target_cache,streaming,gpu_target_cache,auto} --post-exit-checkpoint <npz> --post-exit-scaled-perron-output <json>`.

## Done
- Exact affine-ghost repeat/resonance atlas
  (`collatz_exp/affine_ghost_atlas.py`) — RESULT: universal exact-word
  cylinder theorem, exact maximal repeats, conditional Haar exit law,
  integer-gap resonance lemma, strict nonresonant maximal-edge `A` decrease,
  complete `(1,1,2)` residual partition, canonical resonant path, full
  `38119 mod 2^22` first-descent cylinder, deterministic report, and explicit
  open global atlas status.
- Exact higher-`R` phase and affine-ghost certificate
  (`collatz_exp/symbolic_higher_r_certificate.py`) — RESULT: complete
  `(m,R)` transfer parametrization, target-fixed mixed-residue transport,
  full-phase cusp contraction, exact first-post cutoff and reentry transport,
  simple-cusp obstruction, general affine-ghost theorem, finite repeat
  budget, exact chart-switch identity, deterministic report, and explicit
  open cross-chart status.
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
- The single shifted cusp `(n+5)c^(v2(n+5)-2)` cannot survive all higher-`R`
  phases: the exact `1183 -> 4495` word preserves its cusp exponent and
  expands its shifted size by `125/33`. Word-specific affine ghosts replace
  it locally, but their chart-switch compatibility is not yet proved.
