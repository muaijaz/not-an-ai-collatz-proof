# Collatz Renewal Diagnostics: Draft Note

## Status

This note describes finite diagnostics only. It makes no claim of resolving the
open Collatz problem. Every quantitative statement below is tied to a saved
JSON artifact under `docs/reports/`.

## 1. Tail-Aware Finite Operator

The finite operator uses odd states represented as `n = 2^R u - 1`, with state
coordinate `(R, u)` and a bounded unit precision. At the largest saved
LTE-closed level, `(q,Rmax)=(10,7)` has `3,584` states and `8,704` edges
(`docs/reports/tail_aware_lte_closed_projective_jsr.json`).

The worst-case finite switching value at that level is a JSR factor of
`1.2305030340113887`, with max cycle mean `0.29924821500679044` in log2 units
(`docs/reports/tail_aware_lte_closed_projective_jsr.json`). This is the
diagnostic split point: the closed finite graph still contains abstract
high-growth switching, so the operator data must be read together with the
typical-transition diagnostics.

## 2. LTE Closure

The LTE closure compresses deeper-tail overflow back to the tracked maximum
tail depth by following the forced valuation-one run. In the saved
`(q,Rmax)=(10,7)` level, the closed graph records `44` closed overflow edges
(`docs/reports/tail_aware_lte_closed_projective_jsr.json`).

This closure turns the tracked tail graph into a finite closed diagnostic while
preserving the distinction between visible tail coordinates and compressed
deeper-tail returns. The all-one self-loop is absent at the saved LTE-closed
level (`docs/reports/tail_aware_lte_closed_projective_jsr.json`).

## 3. Worst-Vs-Typical Markov Split

On the same `(q,Rmax)=(10,7)` finite graph, the lift-count Markov model has one
recurrent component with `1,113` states
(`docs/reports/tail_aware_markov_lyapunov.json`). Its average log2 growth per
accelerated step is `-0.4118668182695867`, giving typical factor
`0.7516501240662575` per accelerated step
(`docs/reports/tail_aware_markov_lyapunov.json`).

The paired worst-case and typical values are therefore sharply separated:
worst-case finite JSR factor `1.2305030340113887`, typical Markov factor
`0.7516501240662575` (`docs/reports/tail_aware_markov_lyapunov.json`). The
empirical interpretation is that adversarial switching and lift-count-natural
switching are measuring different regimes of the same finite tail graph.

## 4. Jazz Renewal Constant

The saved renewal calibration gives `J = 0.08372911906309355`, with bootstrap
interval `[0.08360260171293721, 0.08384169894885218]`
(`docs/reports/jazz_constant_closed_form_test.json`). The same values appear in
the spike-decomposition artifact
(`docs/reports/jazz_constant_spike_decomposition.json`).

The closed-form stress artifact tests `log(4/3)^2` and records it outside the
bootstrap interval (`docs/reports/jazz_constant_closed_form_test.json`). The
decomposition artifact also lists `1/12`, `log2(3)/19`, and
`(log2(3)-1)/7` outside the interval
(`docs/reports/jazz_constant_spike_decomposition.json`).

The tilted-MGF decomposition is dominated by the segment labeled `1`, which
contributes `64.00635058364243` percent of the total tilted MGF
(`docs/reports/jazz_constant_spike_decomposition.json`). This supports the
working renewal picture: high-spike excursions carry much of the negative
drift signal, while no-spike or low-spike excursions are the rate bottleneck.

## 5. Tao Syracuse Verification

The finite Syracuse comparison reports fixed-iterate total variation distance
at most `0.002783968493717706` for the saved small levels
`n=1,2,3,4` (`docs/reports/tao_syrac_empirical.json`). Each saved level uses
`1,000,000` nth-iterate samples (`docs/reports/tao_syrac_empirical.json`).

This is the source for the informal `TV <= 0.3%` summary on small levels. The
time-pooled orbit marginal is larger in the same artifact, reaching
`0.06846164509274151`, so the relevant comparison here is specifically the
fixed-iterate distribution (`docs/reports/tao_syrac_empirical.json`).

## 6. Hercher / Christoffel Bounded Filter

The bounded Christoffel-compatible scan at `(q,Rmax)=(7,6)` scans `37,168`
cycles, finds `9` primitive-balanced compatible cycles, and keeps the
compatible best at `0.75`
(`docs/reports/christoffel_filtered_jsr_7_6.json`). At the same level, the
exact Karp factor is `1.1905507889761504`, while the bounded unfiltered best is
`1.0606601717798212`
(`docs/reports/christoffel_filtered_jsr_7_6.json`).

The automaton-constrained Karp product graph gives factor `3/4` at `(5,4)` and
`3/4` at `(6,5)`, with product sizes `1,024` states and `509` edges at `(5,4)`
and `2,560` states and `1,275` edges at `(6,5)`
(`docs/reports/constrained_karp_jsr.json`).

The upper-Christoffel slope-constrained scan reports primitive-balanced best
`0.75` and slope-constrained best `0.75` at `(5,4)`, `(6,5)`, and `(7,6)`
(`docs/reports/christoffel_slope_constrained_jsr.json`). The stricter
slope-window filter leaves `1` survivor per saved level
(`docs/reports/christoffel_slope_constrained_jsr.json`).

## Position Relative to Chang 2026

Reference: Edward Y. Chang, "Exploring Collatz Dynamics with Human-LLM
Collaboration," arXiv:2603.11066v6 [math.DS], April 22, 2026
(`docs/references/chang_2026_human_llm_collatz_arxiv_2603.11066v6.pdf`).
This is best read as a sibling LLM-collaboration artifact, not as evidence for
this framework and not as a competing artifact.

The two appearances of `3/4` are different objects. Chang's Theorem 3.1 is a
`1/4` Persistent-Transition Law: among admissible mod-8 lifts of a persistent
state, `1/4` have Syracuse successor again persistent, so `3/4` exit that
class in that transition model
(`docs/references/chang_2026_human_llm_collatz_arxiv_2603.11066v6.pdf`). This
framework's `3/4` is a Christoffel-compatible bounded JSR factor and an
automaton-constrained Karp product-graph factor on the LTE-closed tail graph
(`docs/reports/christoffel_filtered_jsr_7_6.json`,
`docs/reports/constrained_karp_jsr.json`). In plain language: Chang's number is
a modular transition probability; this framework's number is a cycle-mean
factor. They happen to evaluate to the same rational value, but no deeper
equivalence is asserted here. The dominant compatible cycle in this framework
is the elementary `valuation_word=[2]`, with edge factor `3/(2^2)=3/4`
(`docs/reports/christoffel_slope_constrained_jsr.json`).

| Chang route | Diagnostically aligned saved reports | Alignment |
| --- | --- | --- |
| (A) WMH / burst-gap | `docs/reports/orbit_renewal_spike_decomposition.json`, `docs/reports/orbit_renewal_markov_cramer.json`, `docs/reports/tail_aware_markov_lyapunov.json`, `docs/reports/tao_syrac_empirical.json` | Substantive for renewal/typical-drift observables; shallow for Chang's WMH machinery itself. |
| (B) CIC / Carry Contamination | `docs/reports/christoffel_filtered_jsr_7_6.json`, `docs/reports/christoffel_slope_constrained_jsr.json`, `docs/reports/constrained_karp_jsr.json`, `docs/reports/lift_realizability_k6_a6_p8.json` | Substantive at the level of valuation/parity-word compatibility; not a check of Chang's CIC. |
| (C) I2 spectral | `docs/reports/tail_spectral_ladder_k12_20_prefix8.json`, `docs/reports/tail_subautomaton_k12_prefix8.json`, `docs/reports/cohn_elkies_walsh_k8.json` | Mostly shallow: both use finite spectral diagnostics, but the state spaces and target observables differ. |
| (D) C-2adic auxiliary | `docs/reports/tail_aware_lte_closed_projective_jsr.json`, `docs/reports/tail_lte_R2_R128.json`, `docs/reports/tail_internal_step_R2_R128_u8.json`, `docs/reports/tail_exit_lemma_R20_u8.json` | Substantive for 2-adic tail memory and LTE closure; not the same auxiliary-memory route. |
| (E) cascade algebra | `docs/reports/valuation_mi_lags.json`, `docs/reports/obstruction_lyapunov_correction.json`, `docs/reports/unified_lyapunov_state_debt.json`, `docs/reports/post_exit_pecm_pointwise.json` | Mostly shallow: shared carry/post-exit vocabulary, unrelated algebraic organization. |
| (F) cycle exclusion via discrete-log obstruction | `docs/reports/cycle_exclusion_tower_m10.json`, `docs/reports/d_pe_continued_fraction_certification.json`, `docs/reports/d_pe_baker_certification.json`, `docs/reports/realizability_structural_exclusion.json` | Substantive for cycle-exclusion diagnostics, shallow for the discrete-log target set. |

The shared open problem is the same wall in different language. Chang calls it
the distributional-to-pointwise upgrade; this framework calls it the upgrade
from finite diagnostics to infinite arithmetic. These are not independent
walls. They are two descriptions of the same missing bridge between ensemble or
bounded finite behavior and every individual positive integer.

There is also a Mersenne overlap. Chang's Section 13.1 says the family
`2^L - 1` survives the running divergent-compatibility condition at every
finite depth
(`docs/references/chang_2026_human_llm_collatz_arxiv_2603.11066v6.pdf`). This
framework has `collatz_exp/mersenne.py` and
`collatz_exp/mersenne_continuation.py`, which profile the same all-one tail
family after the initial run. The saved tail reports operate at a different
level: finite LTE-closed tail-graph dynamics and tail subautomata
(`docs/reports/tail_aware_lte_closed_projective_jsr.json`,
`docs/reports/tail_spectral_ladder_k12_20_prefix8.json`). From the saved JSON
artifacts alone, I do not read this as contradicting or confirming Chang's
Mersenne bypass. The qualitative reconciliation is that Chang's bypass concerns
survival of a finite-depth sieve condition, while this framework's Mersenne
code studies post-run descent and tail closure after the all-one branch has
been followed. Those can both be true because they ask different questions.

Finally, the methodology is kin. Chang's Section 12 documents a three-party
human/LLM workflow with error-correction logs and false-lemma case studies
(`docs/references/chang_2026_human_llm_collatz_arxiv_2603.11066v6.pdf`). This
framework's `docs/CODEX_HANDOFF_*.md` chain serves a similar continuity and
correction role. The relationship is methodological kinship, not a priority
claim.

## Bridge Candidate Audit

The next bridge candidate is now recorded as an explicit finite obstruction
ledger: every infinite compatible tail schedule over the LTE-closed graph would
need to force either a visible high-valuation exit at some finite level or a
Mersenne-style post-run descent event
(`docs/reports/finite_to_infinite_bridge_audit.json`). This is a target
statement, not a completed upgrade.

The ledger separates three signals. First, the largest saved LTE-closed tail
graph has worst-case factor `1.2305030340113887` and lift-count typical factor
`0.7516501240662575`
(`docs/reports/finite_to_infinite_bridge_audit.json`). Second, the constrained
Karp product graph reports exact rational `3/4` at the largest saved product
level, while the slope-constrained bounded scan has `1` survivor at its largest
saved level (`docs/reports/finite_to_infinite_bridge_audit.json`). Third, the
new Mersenne post-run table reaches descent below the start for sampled
Mersenne exponents up to `90`, with maximum measured post-run length `155`
(`docs/reports/mersenne_post_run_descent.json`,
`docs/reports/finite_to_infinite_bridge_audit.json`).

The audit's falsifiable next step is to search for compatible product paths
whose finite prefixes avoid both high-valuation exits and the Mersenne post-run
descent marker (`docs/reports/finite_to_infinite_bridge_audit.json`). A
persistent family there would refocus the obstruction; failure to find one
would make the bridge candidate sharper but still finite.

## Realizable Karp on the LTE-Closed Tail Graph

The bounded-cycle audit now separates abstract tail-graph cycles from
integer-realizable cycle words. In the joint Karp/slope sweep at
`(q,Rmax)=(5,4),(6,5),(7,6)`, with automaton period widened across the levels,
the only slope-compatible survivor at each tested level is the elementary
valuation word `[2]`, with factor `3/4`
(`docs/reports/karp_slope_joint_sweep.json`). The realizability extension then
audits all simple cycles up to `max_cycle_edges=12` at the same three levels:
`226,333` simple cycles are classified, `226,330` are
`noninteger_2adic_only`, and the only `3` `positive_integer_cycle` entries are
the elementary `[2]` cycle, one per level
(`docs/reports/tail_cycle_realizability.json`,
`docs/reports/tail_cycle_realizability_extended.json`). Thus the saved finite
diagnostic has

```text
realizable Karp factor = slope-filtered Karp factor = 3/4
```

on these levels. This should be read as a finite bounded-cycle fact, not as a
global statement about arbitrary infinite products.

The renewal-scale drift data now has a compatible phase interpretation. Split
accelerated steps by the pre-step odd integer modulo `4`: `n == 3 mod 4`
(`v2(n+1) >= 2`) is tail-internal and has forced valuation `a=1`; `n == 1 mod
4` is the post-exit phase (`docs/reports/renewal_drift_phase_decomposed.json`).
The asymptotic post-exit valuation target in this convention is **`3`**, not
`2`: it is the shifted-Geometric value seen after removing the deterministic
tail-internal valuation-one steps. The symbolic mean-step identity suggested by
the artifacts is therefore

```text
mu_step = (1/2) log2(3/2) + (1/2) log2(3/4) = log2(3/4),
```

with `E[a | tail] = 1` and asymptotic `E[a | post_exit] = 3`
(`docs/reports/renewal_drift_per_step.json`,
`docs/reports/renewal_drift_phase_decomposed.json`,
`docs/reports/renewal_drift_phase_decomposed_n0_stability.json`).

The finite-window n0 sweep is consistent with slow approach to this phase
picture, but not yet with a completed asymptotic identification. Across
`[10^2,10^4]` through `[10^12,10^15]`, the post-exit valuation deviation
shrinks from `-0.03473021694546086` to `-0.006503489706314536`, with monotone
absolute decrease and log10-slope `-0.06656531395656089` per decade
(`docs/reports/renewal_drift_phase_decomposed_n0_stability.json`). From the
`[10^6,10^9]` window onward the total drift deviation is below `0.01`, ending
in the `0.005` range; it is not strictly monotone at the deepest window, moving
from `0.005160187031614694` to `0.0054062766596057465`, a change smaller than
the reported deepest-window CI halfwidth `0.0005710918683108357`
(`docs/reports/renewal_drift_phase_decomposed_n0_stability.json`). Thus the
saved verdict is `non_monotone_or_flat`, while the deepest-window deviations
remain small finite-sample quantities rather than theorem-level residuals.

The caveat is essential. These artifacts combine a finite audit of bounded
simple cycles on finite LTE-closed tail graphs with finite-window empirical
renewal drift estimates. They do not prove a global per-orbit Lyapunov
function, do not control arbitrary infinite switching paths, and do not imply a
Collatz descent theorem.

## Foster-Lyapunov Drift Audit on V(n) = log₂(n) + v_2(n+1)

The phase-aware Lyapunov search turns V5's failed running-debt ansatz into a
more structured candidate. Over `100,000` sampled orbits in
`[10^6,10^9]`, the best grid point in

```text
V(n; alpha, beta, gamma_diff)
  = log2(n) + alpha R(n) + beta D_running(n) + phase offset
```

is `alpha = 1.0`, `beta = 0.0`, `gamma_diff = 0.0`, i.e.

```text
V(n) = log2(n) + v2(n+1).
```

This reduces the same-sample V5 non-decrease fraction from
`0.5001335415695829` to `0.1655372436648494`; the tail-internal phase has
`0.0` non-decrease, and the remaining positive jumps are post-exit steps with
large `R' = v2(S(n)+1)` spikes (`docs/reports/phase_lyapunov_search.json`).

The one-step Foster audit confirms the marginal drift but rejects uniform
one-step residue negativity. Across the five windows
`[10^2,10^4]` through `[10^12,10^15]`, the marginal drift of `V` is
empirically consistent with `log2(3/4)`: the deepest-window estimate is
`-0.4123424992788405` with CI
`[-0.41856572879163634, -0.4061192697660446]`, and the saved one-step verdict
is `drift_residue_obstruction`
(`docs/reports/phase_lyapunov_foster_drift.json`). The m-step artifact
cross-checks the `m=1` slice against this one-step audit with maximum
disagreement `2.6645352591003757e-15`
(`docs/reports/m_step_foster_drift.json`).

The obstruction is arithmetic rather than marginal. At one step, residue
conditional drift fails uniform negativity for every tested
`k in {3,4,5,6}`, with `50` obstruction witnesses
(`docs/reports/phase_lyapunov_foster_drift.json`). The visible cascade is

```text
n == 1  mod 8   : drift 0.5954199142013228,
                  CI [0.5830610092394827, 0.6077788191631629]
n == 9  mod 16  : drift 1.5919631928192652,
                  CI [1.5747431836625472, 1.6091832019759833]
n == 41 mod 64  : drift 3.557870295871902,
                  CI [3.5249778818408877, 3.5907627099029162]
```

all in the first window `[10^2,10^4]`; the same `41 mod 64` class remains the
largest obstruction across later windows
(`docs/reports/phase_lyapunov_foster_drift.json`).

The m-step audit closes this finite residue-Markov version of the question on
the tested grid. For `m in {1,2,4,8,16,32,64}`, the smallest value with
residue-conditional drift uniformly negative across all tested windows and
residue powers is `m = 16`, and the same `m = 16` also clears the
`epsilon = 0.1` margin. At `m = 64`, the obstruction count is `0`. The binding
class before clearance is still `n == 41 mod 64`: it is the maximal
obstruction at `m = 1,2,4,8`, then disappears at `m = 16`
(`docs/reports/m_step_foster_drift.json`).

The candidate Lyapunov satisfies the m-step Foster-Lyapunov drift condition (Meyn-Tweedie, Markov Chains and Stochastic Stability, ch. 11) on residue quotients mod 2^k for k ∈ {2,3,4,5,6} at sample windows n_0 ∈ [10², 10¹⁵], with smallest tested grid value m = 16 and geometric-ergodicity margin ε = 0.1. The Collatz orbit is deterministic, not a Markov chain; this is a finite empirical diagnostic on the residue Markov chain quotient, not a theorem about deterministic per-orbit descent.

## Current Reading

The strongest finite picture is consistent across three views: LTE-closed
worst-case switching can grow, lift-count Markov switching contracts near
`3/4`, and bounded Christoffel-compatible filters remove the high-growth simple
cycle witnesses in the tested windows (`docs/reports/tail_aware_markov_lyapunov.json`,
`docs/reports/christoffel_filtered_jsr_7_6.json`,
`docs/reports/constrained_karp_jsr.json`,
`docs/reports/christoffel_slope_constrained_jsr.json`).
