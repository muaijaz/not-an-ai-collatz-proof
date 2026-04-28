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

## Current Reading

The strongest finite picture is consistent across three views: LTE-closed
worst-case switching can grow, lift-count Markov switching contracts near
`3/4`, and bounded Christoffel-compatible filters remove the high-growth simple
cycle witnesses in the tested windows (`docs/reports/tail_aware_markov_lyapunov.json`,
`docs/reports/christoffel_filtered_jsr_7_6.json`,
`docs/reports/constrained_karp_jsr.json`,
`docs/reports/christoffel_slope_constrained_jsr.json`).
