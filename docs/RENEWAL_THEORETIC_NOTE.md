# A Renewal-Theoretic Framework for Accelerated Collatz Orbits

Status: working draft scaffold. This note is not a proof of the Collatz
conjecture. It consolidates finite computations and theorem-shaped statements
that the project has made reproducible.

## Abstract

We study accelerated Collatz dynamics through renewal excursions between
Mersenne-tail states, finite residue quotients, and probabilistic projections
of Tao's `3`-adic Syracuse model. The computational evidence isolates three
stable quantities:

- a renewal Cramer rate `J = 0.083729...`, stable across starting ranges from
  `10^6` through `10^15`;
- an exact affine drift factor `3/4` after removing Mersenne-tail states from
  the projective quotient;
- a worst-case projective growth obstruction `3/2`, caused first by the
  negative `2`-adic cycle `n=-1`, and then by positive-tail reentry paths after
  tail coordinates are made explicit.

The framework does not prove global descent. It gives a reproducible finite
operator picture in which the remaining gaps are named: closed tail
renormalization, Markov/Lyapunov contraction on the closed operator, and a
limit argument from finite quotients to the full system.

## 1. Accelerated Map And Renewal Scale

For odd `n`, write

```text
S(n) = (3n+1) / 2^a,    a = v2(3n+1).
```

The renewal scale used in the experiments partitions an orbit into excursions
between tail states `v2(n+1) >= 2`. This is the scale at which a simple
per-step Lyapunov failed, but a stable negative drift appeared.

Saved artifacts:

- `docs/reports/orbit_renewal_spike_decomposition.json`
- `docs/reports/orbit_renewal_n0_stability.json`
- `docs/reports/renewal_bootstrap_calibration.json`

Main empirical facts:

- mean renewal increment `E[Delta log2 n] ~= -0.8024`;
- Cramer rate `J ~= 0.083729`;
- bootstrap interval for `J`: `[0.083603, 0.083842]`;
- range stability: `I(0)` is approximately `0.084` from starts `10^6` upward.

## 2. Jazz's Constant

Define the empirical renewal constant

```text
J = sup_{lambda >= 0} -log E[exp(lambda X)],
```

where `X` is the renewal increment `Delta log2 n` under the sampled Collatz
renewal law.

The project tested the attractive closed form `log(4/3)^2`; it is close but
outside the tight bootstrap interval by about `8.1` CI half-widths. The current
best interpretation is Khinchin-style: `J` is a dynamical constant defined by a
renewal law, not presently an elementary expression.

The spike-stratified MGF decomposition is the useful structure:

```text
E[exp(lambda X)] = sum_k P(max a = k) E[exp(lambda X) | max a = k].
```

At `lambda* ~= 0.263`, the no-spike class `max a = 1` contributes about `64%`
of the tilted MGF. The difference

```text
J - log(4/3)^2 ~= 0.000968
```

is the measured heavy-tail correction.

Saved artifact:

- `docs/reports/jazz_constant_spike_decomposition.json`

## 3. Projective JSR Diagnostics

The projective affine-size quotient gives an exact scalar edge weight

```text
log2(3) - a.
```

Therefore finite constrained JSR computations reduce to max-plus cycle mean.

Findings:

- Unconstrained projective family has `JSR = 3/2`.
- Naive legal-residue constrained quotient still has `JSR = 3/2`, dominated by
  the all-`a=1` word, classified as the negative integer cycle `n=-1`.
- Removing states with `v2(r+1) >= 2` gives exact factor `3/4`.
- Tail-aware coordinates `(R,u mod 2^q)` remove the fake all-`a=1` self-loop,
  but worst-case products still grow.
- LTE-closed tail-aware graphs route deeper-tail overflows back to `Rmax` and
  still show worst-case growth above `1`.
- The same LTE-closed graph, weighted by enumerated lift counts, has negative
  stationary average growth. At the largest saved level `(q,Rmax)=(10,7)`, the
  worst-case factor is about `1.2305`, while the Markov typical factor per
  accelerated step is about `0.75165`.
- A bounded Christoffel-compatible cycle filter gives the first Hercher-style
  bridge on the same tail graph. Expanding each accelerated valuation `a` to
  parity block `1 0^(a-1)`, the high-growth simple cycles found at
  `(q,Rmax)=(5,4)` and `(6,5)` fail the primitive cyclic-balance test. The best
  compatible survivor has factor `3/4` at both levels.

Interpretation: a proof cannot be a plain worst-case JSR `<1` certificate. The
operator needs either a Markov/Lyapunov weighting or a stronger realizability
filter.

Saved artifacts:

- `docs/reports/projective_jsr_claude_background.json`
- `docs/reports/constrained_projective_jsr.json`
- `docs/reports/tail_aware_projective_jsr.json`
- `docs/reports/tail_aware_lte_closed_projective_jsr.json`
- `docs/reports/tail_aware_markov_lyapunov.json`
- `docs/reports/christoffel_filtered_jsr.json`

## 4. Tao Projection

Tao's finite `3`-adic Syracuse random variable is reproduced by the orbit
sampler:

- fixed-iterate distributions match Tao's recursive law to under `0.3%` total
  variation through `n=4`;
- empirical characteristic-function decay matches the exact finite recursive
  distribution through `n=7`.

Saved artifacts:

- `docs/reports/tao_syrac_empirical.json`
- `docs/reports/tao_characteristic_function_decay.json`

The interpretation is limited but valuable: the sampler reproduces Tao's
finite probabilistic mechanism, and the renewal constant `J` is compatible with
that probabilistic picture.

## 5. Cycle And Finite-Matrix Projections

Hercher's reciprocal-sum shape appears sharply in ordinary orbit segments:

```text
T(n_i) n_i < 3,
```

with bucket maxima matching the geometric ceiling
`3(1-(2/3)^k)`.

Paparella's finite adjacency criterion is also verified at tested truncations:
all checked traces vanish, and no non-trivial finite truncated cycle appears.

Saved artifacts:

- `docs/reports/hercher_t_ni_bound.json`
- `docs/reports/paparella_nilpotency.json`

## 6. What Would Become A Theorem

The strongest theorem-shaped path is now:

1. Work on the LTE-closed tail-aware operator.
2. Prove a Markov/Lyapunov contraction for the closed operator, not a worst-case
   JSR bound.
3. Show the finite quotients converge to a well-defined renewal operator.
4. Transfer the contraction to a density/descent statement.

The Christoffel-word filter from Hercher's high-cycle work is the natural next
realizability constraint for worst-case products. It may remove abstract
growing words that no integer orbit can realize.

## 7. Claims To Avoid

Do not claim:

- a proof of Collatz;
- an infinite-dimensional spectral gap;
- that `J` is an exact closed form;
- that finite JSR growth implies integer orbit divergence.

Do claim, carefully:

- the finite computations are reproducible;
- the renewal rate is stable in the sampled ranges;
- the projective obstructions are now explicitly classified;
- the remaining gaps are named and technically localized.
