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

## Current Reading

The strongest finite picture is consistent across three views: LTE-closed
worst-case switching can grow, lift-count Markov switching contracts near
`3/4`, and bounded Christoffel-compatible filters remove the high-growth simple
cycle witnesses in the tested windows (`docs/reports/tail_aware_markov_lyapunov.json`,
`docs/reports/christoffel_filtered_jsr_7_6.json`,
`docs/reports/constrained_karp_jsr.json`,
`docs/reports/christoffel_slope_constrained_jsr.json`).
