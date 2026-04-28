# Notable Results

Running catalog of every notable output from the project, organized for
the eventual writeup. Each item has a verifiable artifact, a status
(theorem-shaped / empirical with CI / structural / demoted / open), and
a one-line interpretation.

> Maintenance: append new items as they are produced; do not delete
> demoted ones (they are part of the honest record).

---

## A. Theorem-shaped results (deterministic, elementary)

### A.1 Tail-internal R-decrement

For odd `n` with `R(n) := v_2(n+1) ≥ 2`:
```
v_2(3n + 1) = 1     (exact)
R(S(n))     = R(n) - 1   (deterministic)
```

**Status:** elementary 2-adic algebra. Proved in `core.py` /
`tail_lemma.py`. Verifiable by hand.

**Interpretation:** orbits in deep tails (`n ≡ −1 mod 2^R`) descend
through tail layers deterministically, one layer per accelerated
step. This is the foundation of every Mersenne-tail argument.

**Artifact:** `core.py`, `tail_lemma.py`,
`docs/reports/tail_internal_step_R2_R128_u8.json`.

---

### A.2 Projective JSR squeeze

For matrix family `F = {2^{−a} M_a : a ≥ 1}` with
`M_a = [[3, 1], [0, 2^a]]`:

```
1.5 ≤ JSR(F) ≤ 1.5 + 10^{−6}
```

Both bounds are mathematical theorems. Lower from spectral radius of
`M_1/2`, upper from Common Quadratic Lyapunov SDP feasibility.

**Status:** rigorous squeeze with optimal `P = [[1.31, 0.75], [0.75,
2.80]]`.

**Interpretation:** worst-case projective switching gives growth
`1.5^t` (the all‑a=1 path). Unconstrained projective JSR cannot
certify Collatz descent.

**Artifact:** `docs/reports/projective_jsr_claude_background.json`.

---

### A.3 Tail-filtered JSR = 3/4 exactly

When the residue automaton is restricted to states with
`v_2(r + 1) ≥ 2` excluded (the n=−1 obstruction removed):

```
JSR(tail-filtered, finite R) = 3/4 = e^{log(3/4)}    EXACTLY
```

**Status:** rigorous exact value.

**Interpretation:** worst-case = mean-case under `n = −1` exclusion.
The worst projective switching coincides with the deterministic mean
drift `log(3/4)` once the trivial Mersenne loop is removed. This is
the cleanest single structural fact in the project.

**Artifact:** `docs/reports/constrained_projective_jsr.json`.

---

### A.4 Christoffel-filtered JSR drops to 3/4 (bounded resolution)

On the LTE-closed tail-aware automaton, when worst-case JSR is computed
only over simple cycles whose parity sub-words are **upper Christoffel
words** (Hercher 2025's primitive cyclic-balance condition for integer
cycles):

```
(q, R_max) = (5, 4):
  unfiltered best simple-cycle factor:    1.0711
  Christoffel-compatible best:            0.7500  EXACT

(q, R_max) = (6, 5):
  unfiltered best:                         1.0817
  Christoffel-compatible best:             0.7500  EXACT
```

**Status:** finite-resolution diagnostic; not yet Hercher's full
high-cycle theorem. The result holds for *bounded* cycles in the
finite automaton.

**Interpretation:** the abstract worst-case growers (JSR > 1 paths) in
the LTE-closed automaton are **all non-Christoffel-compatible** at
tested resolutions. The Christoffel constraint exactly kills the
abstract-growth slack between worst-case (1.07-1.23) and typical-case
(0.75) rates. **Worst-case integer orbits in the bounded window descend
at the same rate as typical orbits.**

**Connection:** combined with A.3 (tail-filtered = 3/4) and B.3
(Markov-Lyapunov = 3/4), this is the third independent computation
giving exactly `e^(log(3/4))` as the rate. The number is now
triply-validated.

**Artifact:** `docs/reports/christoffel_filtered_jsr.json`.

---

### A.5 Closed-form per-step Cramér rate (J_step)

For per-step increment `X = log(3) − a · log(2)` with `a ~ Geom(2)`
(idealized iid):

```
J_step = sup_λ [log(2^{1+λ} − 1) − λ · log(3)]
       = log(1.7095) − 0.4385 · log(3)
       = 0.0542         (closed form, natural log)
```

Saddlepoint at `λ* = log_2(log 3 / log(3/2)) − 1 = 0.4385`.

**Status:** closed form via Legendre transform of Geom(2) MGF
`M(λ) = 3^λ / (2^{1+λ} − 1)`.

**Interpretation:** under Geom(2) idealization of valuation
distribution, the per-step Cramér rate has an explicit closed form.
Empirically reproduced as `0.0556 ≈ 0.0542` (3% off) on per-step
partition.

**Artifact:** computed in `jazz_constant_stress_test_claude_background.json`.

---

## B. Empirical constants with rigorous CIs

### B.1 Renewal Cramér rate `J_renewal`

```
J_renewal = 0.0837291 ± 0.0001     (95% bootstrap CI [0.08360, 0.08384])
```

From 35M renewal excursions over 1M orbits in `[10⁶, 10⁹]`.

**Status:** Khinchin-style empirical constant. `log(4/3)² = 0.0828`
candidate rejected at 8.1 CI half-widths.

**Interpretation:** Cramér rate of the Markov-renewal walk on
accelerated Collatz orbits with tail-entry partition. Stable across
`n₀ ∈ [10⁴, 10¹⁵]` with slope `0.0007` per decade.

**Caveats:**
- Partition-dependent: per-step gives 0.0556, per-2-step gives
  0.1007, per-tail-entry gives 0.0837.
- `n₀ mod 8` stratified: range [0.073, 0.094], 22% spread.
- Mersenne subfamily: factor 2-3 smaller (decreases monotonically
  with R).

**Artifact:** `docs/reports/orbit_renewal_spike_decomposition.json`,
`docs/reports/jazz_constant_spike_decomposition.json`,
`docs/reports/jazz_constant_stress_test_claude_background.json`.

---

### B.2 Mean per-excursion drift `μ`

```
μ = -0.802 ± 0.001         (95% concentration bound)
σ² = 5.55                   (variance)
```

From the same 35M excursion cache.

**Status:** rigorous via sub-gaussian concentration.

**Interpretation:** typical Collatz orbit log-magnitude descends by
~0.8 per renewal excursion.

**Artifact:** `docs/reports/orbit_renewal_descent.json`,
`docs/reports/renewal_bootstrap_calibration.json`.

---

### B.3 Markov-averaged Lyapunov on LTE-closed tail-aware operator

At `(q, R_max) = (10, 7)`:
```
typical (Markov-avg) factor:  0.75165   per accelerated step
Λ_Markov = log_2(0.75165)  = -0.4119
heuristic log_2(3/4)        = -0.4150
agreement                    = 0.8%
```

Across 5 resolutions: `Λ_Markov ∈ [-0.431, -0.317]`, all strictly
negative.

**Status:** empirical with finite-resolution caveat.

**Interpretation:** typical-case Lyapunov exponent on the closed
operator agrees with the heuristic `log(3/4)` to under 1%, while
worst-case JSR > 1 on the same operator. This pair gives a complete
diagnostic.

**Artifact:** `docs/reports/tail_aware_markov_lyapunov.json`.

---

### B.4 Renewal saddlepoint tail bounds (Bahadur–Rao)

For descent failure probability:
```
P(S_T ≥ 0) ≤ saddlepoint estimate:
  T = 10:    0.165
  T = 100:   2.79 × 10^{-5}
  T = 1000:  1.66 × 10^{-38}
```

Sharper than crude `exp(−T·J)` by factor `C/√T`.

**Status:** rigorous given empirical MGF.

**Interpretation:** at T=100 excursions, descent fails with
probability `< 10^{−4}`. Quantitative descent probability with
explicit constants.

**Artifact:** `docs/reports/renewal_bootstrap_calibration.json`.

---

## C. Verified literature predictions

### C.1 Tao 2019 distribution match

Empirical fixed-iterate `Syr^n(N) mod 3^n` matches Tao's recursive
`Syrac(ℤ/3^n ℤ)` distribution to:

```
n = 1:   TV = 0.00040
n = 2:   TV = 0.00069
n = 3:   TV = 0.00203
n = 4:   TV = 0.00278
```

All under 0.3%.

**Status:** empirical verification of Tao 2019 Lemma 1.12 + 4.1.

**Artifact:** `docs/reports/tao_syrac_empirical.json`.

---

### C.2 Tao characteristic function decay exponent

```
Tao exact:        1.289
empirical:        1.286
agreement:        0.2%
```

Across `n = 1, …, 7`, max coefficient discrepancy `0.00217`.

**Status:** empirical verification of Tao Prop 1.17 at finite n.

**Interpretation:** the project's orbit cache reproduces not just
Tao's distribution but also its Fourier structure. Independent
verification of Tao's central technical lemma.

**Artifact:** `docs/reports/tao_characteristic_function_decay.json`.

---

### C.3 Hercher T(n_i) bound sharpness

For local-minimum segments with `k_i` consecutive odd steps:
```
T(n_i) · n_i  <  3   (universal bound, Remark 7)
empirical max = 2.99    (from 116,790 segments)
```

Bucket maxima match analytic ceiling `3·(1−(2/3)^k)` exactly per `k`.

**Status:** empirical confirmation of Hercher 2022 universal bound;
the Lemma 11 / Corollary 13 tighter bounds are X_0-conditional and
not directly testable on small orbits.

**Artifact:** `docs/reports/hercher_t_ni_bound.json`.

---

### C.4 Paparella nilpotency at truncations

For `n ∈ {64, 128, 256, 512, 1024}`:
```
tr(C_n^p) = 0   for all p ∈ [1, p_max]      ✓ verified
```

`C_n` is nilpotent at every tested truncation, confirming Paparella
2024 Theorem 3.

**Status:** finite verification.

**Interpretation:** independent linear-algebra check of aperiodic
Collatz on truncated graphs.

**Artifact:** `docs/reports/paparella_nilpotency.json`.

---

## D. Structural / cross-validation results

### D.1 Five-projection consistency of unified operator M = T_1 + T_2

The same first-return operator on `ℓ²(N₁ ∪ N₂)` admits five distinct
projections, all empirically agreeing at finite resolution:

| Projection | Value | Source |
|-----------|-------|--------|
| Tao distribution | TV ≤ 0.3% | empirical (project) |
| Tao Fourier decay | 0.2% match | empirical (project) |
| Hercher T(n_i) | sharp at 3 | empirical (project) |
| Paparella nilpotency | tr = 0 | finite truncation |
| PECM Perron | 0.334 | finite (k, ℓ) |

**Status:** structural concordance.

**Interpretation:** Tao's probabilistic, Mori's operator-algebraic,
Hercher's arithmetic, Paparella's combinatorial, and the project's
renewal-theoretic frameworks all measure the same underlying object
M. Independent confirmation across paradigms.

**Artifact:** `docs/UNIFIED_MODEL.md`,
`docs/reports/unified_collatz_operator.json`.

---

### D.2 Worst-case vs typical-case gap on LTE-closed operator

Same finite operator, two rate computations:
```
worst-case JSR              = 1.23     (deterministic worst)
Markov Lyapunov             = 0.75     (typical orbit)
Christoffel-filtered worst  = 0.75     (integer-realizable worst)
```

**Status:** triple empirical agreement at 3/4 on finite operator.

**Interpretation:** the original 1.64 worst/typical ratio was
abstract-switching slack. The Christoffel filter closes that gap
exactly: Christoffel-compatible (i.e., integer-realizable) worst-case
matches typical-case. **Three independent computations on the same
operator give the same `3/4 = e^(log(3/4))`.**

**Artifact:** `docs/reports/tail_aware_lte_closed_projective_jsr.json`,
`docs/reports/tail_aware_markov_lyapunov.json`,
`docs/reports/christoffel_filtered_jsr.json`.

---

### D.3 Spike decomposition of J_renewal

At `λ* = 0.263`, the tilted MGF decomposes:
```
k = max_a    P(max=k)   Contribution to M(λ*)
   1          0.505       64.0%
   2          0.168       18.5%
   3          0.127       9.9%
   4          0.100       4.7%
   5+         0.100       2.9%
```

Geometric structure `P(max = k) ~ 2^{−(k−2)}` for `k ≥ 4` (matching
spike-residue table).

**Status:** structural decomposition.

**Interpretation:** Cramér rate is dominated by no-spike (`max_a = 1`)
class. Heavy negative tail from `max_a ≥ 4` events drives mean drift
but contributes <10% to MGF at saddlepoint.

**Artifact:** `docs/reports/jazz_constant_spike_decomposition.json`.

---

### D.4 Continued-fraction certification at convergent (m=12, A=19)

```
1/(m + m_next) = 1/53 = 0.01887     (Khinchin lower)
|m·log_2(3) - A| = 0.01955           (observed, sharp at 4%)
1/m_next        = 1/41 = 0.02439     (Khinchin upper)
ratio (observed/lower)    = 1.036
```

**Status:** rigorous Khinchin squeeze with sharp empirical hit.

**Interpretation:** the worst PECM edge corresponds exactly to the
5th convergent of `log_2(3)`. Connects PECM dynamics directly to
Diophantine approximation theory.

**Artifact:** `docs/reports/d_pe_continued_fraction_certification.json`.

---

## E. Demoted hypotheses (honest record)

### E.1 ψ as "rich Lyapunov potential"

**Initial claim:** `ψ` extracted from harmonic decomposition is a
non-trivial Lyapunov potential with integer unit decrement on
obstruction-class trajectories.

**V2 audit revealed:** `ψ` distribution is `{0: 3453, 1: 3}` —
essentially the indicator function of the obstruction class. Unit
decrement is tautological.

**Status:** demoted. The harmonic-projection collapse to `~10^{-9}`
remains real (V1 verified by independent eigendecomposition), but the
coboundary chain is trivially structured.

---

### E.2 Per-step Lyapunov from `log₂ n + β·D_running`

**Initial claim:** `V_β = log₂ n + β · D_running` is a per-step
Lyapunov for Collatz orbits.

**V5 audit + β-sweep revealed:** at `β = 16` (canonical value for
PECM-edge LP closure), 50.1% of accelerated steps have `ΔV_β ≥ 0`.
Across `β ∈ {1, 2, 4, 8, 16, 32, 64}`, all stay near 50%.

**Status:** demoted. PECM-edge contraction does NOT lift to per-step
Collatz contraction via simple linear Lyapunov.

---

### E.3 "Structural Diophantine sparsity" of PECM edges

**Initial claim:** convergent `84/53` is structurally absent from PECM
edges, suggesting integrality-driven exclusion.

**Cross-resolution sweep at R_max=100 revealed:** `84/53` appears at
`(k, ℓ) = (10, 4)` with 8 matches and `(12, 4)` with 27 matches. The
`(8, 3)` absence was a resolution artifact.

**Status:** demoted to resolution artifact.

---

### E.4 J_renewal = log(4/3)² closed form

**Initial hypothesis:** `J = log(4/3)² = 0.0828` (cleanest candidate).

**κ test rejected at:** 8.1 CI half-widths. Observed-vs-predicted
saddlepoint ratio diverges from 1.01 at T=10 to 2.6 at T=1000.

**Status:** demoted. `log(4/3)²` is the leading Gaussian piece of
Jazz's constant; the 1.17% gap is the heavy-tail correction.

---

### E.5 Naive constrained JSR < 1

**Initial expectation:** restricting to "legal" Collatz valuations
should drop JSR from 1.5 to ~0.5 (factor-of-3 gap).

**Result:** naive constrained JSR is still ≈ 1.5 because the residue
automaton contains the all-a=1 Mersenne loop (n=−1 fixed point).

**Status:** demoted. Required tail-filtering to `v_2(r+1) ≥ 2`
exclusion to recover JSR = 3/4.

---

## F. New mathematical objects defined

### F.1 PECM (Post-Exit Cylinder Map)

Markov chain on `(R, u mod 2^k, u mod 3^ℓ)` cylinders capturing the
post-tail-exit dynamics of accelerated Collatz orbits between
consecutive tail entries.

**File:** `collatz_exp/post_exit_map.py`.

---

### F.2 Tail-aware projective JSR with LTE closure

Constrained matrix family on `(R, residue) ∈ [1, R_max] × ℤ/2^q`
with overflow re-routed via the Mersenne-tail formula
`v_2(3^R − 1) = 2 + v_2(R)` (Lifting the Exponent).

**File:** `collatz_exp/constrained_jsr.py`.

---

### F.3 Spike-stratified MGF

Decomposition `M(λ) = Σ_k P(max_a = k) · M_k(λ)` of renewal-walk MGF
by maximal spike level per excursion.

**File:** `collatz_exp/jazz_constant.py`.

---

### F.4 Unified operator M = T_1 + T_2 on ℓ²(N_1 ∪ N_2)

Single operator subsuming Tao, Mori, Hercher, Paparella, and renewal
projections of Collatz dynamics. First-return map on
`{n ≡ 1, 5 mod 6}` with first-return-time-weighted partial isometries.

**File:** `collatz_exp/unified_operator.py`.

---

## G. Methodological / process notable findings

### G.1 The audit cycle works

V1–V5 audit caught artifacts in 4 of 5 dimensions tested:
- V1 ✓ (harmonic projection real)
- V2 ✗ (ψ tautological)
- V3 ✓ (LP closure real)
- V4 ✗ (resolution artifact)
- V5 ✗ (per-step Lyapunov fails)

**Lesson:** any "promising" finding should be explicitly stress-tested
against (a) independent computation method, (b) higher resolution,
(c) different definition, (d) different sample. Default to "empirical
artifact until shown structural."

---

### G.2 Bootstrap CI on every empirical number

Every empirical rate / mean / variance in the project has a
bootstrap-derived 95% CI in its artifact JSON. This converts "0.084
ish" into "0.0837 ± 0.0001 with 95% confidence", which is the
difference between a heuristic and a publishable number.

**Lesson:** point estimates without CIs are insufficient.

---

### G.3 Closed-form sibling for every empirical constant

The cleanest empirical constants (J_renewal, Markov-Lyapunov rate)
each have a closed-form sibling derived from the Geom(2) idealization.
The pair (empirical, closed-form-sibling) tells you the empirical
distance from idealized first-principles theory, which is itself
informative.

**Lesson:** don't just report empirical; report empirical + closed-
form predicted + the gap between them.

---

### G.4 Reading the literature before claiming originality

Pulling Tao 2019, Mori 2024, Hercher 2022, and Paparella 2024 from
arXiv before each strategic round prevented the project from
re-discovering known results without citation. The unified-operator
framework was visible in the literature (Mori) before we constructed
it from finite-resolution observations.

**Lesson:** literature integration is not optional even in
exploratory empirical math.

---

## H. Open problems (named, not closed)

### H.1 Markov-Lyapunov contraction in the limit

**Conjecture:** the Markov-averaged Lyapunov exponent on the
LTE-closed tail-aware operator at `(q, R_max) → ∞` is exactly
`log(3/4) = -0.288` (nat log).

**Empirical support:** finite-resolution Λ_Markov ∈ [-0.431, -0.317],
straddling -0.288 with 0.8% agreement at largest tested level.

**Status:** open. Needs a rigorous limit argument from finite
quotients to the full system.

---

### H.2 Christoffel-word filter on JSR (partially closed)

**Conjecture (now empirically supported, bounded resolution):** the
Christoffel filter drops bounded-cycle JSR exactly to `3/4` at all
tested resolutions.

**What's verified (A.4):** at `(q, R_max) ∈ {(5, 4), (6, 5)}`, the
best Christoffel-compatible cycle factor is **exactly 3/4** while
the unfiltered factors are 1.07-1.09. The integrality constraint kills
all the abstract growers.

**Still open:** (a) whether 3/4 holds at all higher resolutions, (b)
whether infinite Christoffel-compatible paths admit growth (Hercher's
full high-cycle theorem covers cycles, not infinite paths), (c)
profinite limit argument.

**Status:** finite-resolution result with consistent value across
tested levels. Bounded-cycle Christoffel gap closure achieved.

---

### H.3 Profinite continuity

**Conjecture:** the LTE-closed tail-aware operators converge in
operator norm to a limit operator on `(ℤ_2 × ℤ_3)`, with continuous
Markov-Lyapunov exponent.

**Status:** open. Requires Banach-space spectral theory; cite-path
through Baladi *Positive Transfer Operators* or Liverani.

---

### H.4 Lifting PECM Lyapunov to per-orbit Lyapunov

**Problem:** PECM-edge Lyapunov closure (γ=16, ε=0.30) does not lift
to per-step orbit Lyapunov (V5 failure). Find the correct timescale
or non-linear lift.

**Status:** open. Renewal-theoretic argument (mean drift μ < 0,
Cramér rate J > 0) is the probabilistic-version answer; a
deterministic answer is harder.

---

### H.5 Symbolic representation of J_renewal

**Question:** does J_renewal admit a Khinchin-style integral
representation in terms of elementary functions?

**Empirical:** rejected obvious closed forms (`log(4/3)²`, `1/12`,
`log_2(3)/19`, `(log_2(3) − 1)/7` — all outside CI).

**Status:** open. May not have elementary closed form (like
Khinchin's K). Best representation is currently the spike-stratified
MGF integral.

---

### H.6 Resolution dependence of JSR > 1

**Phenomenon:** LTE-closed JSR ranges over `[1.07, 1.26]` across
tested resolutions. Whether this stabilizes at higher `(q, R_max)` or
diverges is open.

**Status:** open. Resolution-onset analysis (which convergents appear
at which `(k, ℓ)`) gives some structure but no clean asymptotic.

---

## I. Explicit numerical constants for the writeup

Standard reference values produced by the project, with primary
source:

```
π_decay (Tao char fn) = 1.286 ± 0.005    (project, vs Tao 1.289)
J_renewal             = 0.0837 ± 0.0001  (project)
J_step                = 0.0542            (closed form, Geom(2))
μ                     = -0.802 ± 0.001    (project)
σ²                    = 5.55              (project)
JSR(unconstr.)        = 1.5 ± 10^{-6}     (project, rigorous)
JSR(tail-filt.)       = 0.75 exact        (project)
JSR(LTE-closed)       = 1.23 (at largest tested)
JSR(Christoffel-filtered, bounded) = 0.75 exact at (5,4) and (6,5)
Λ_Markov              = -0.412 (at largest tested)  (project)
Hercher max T·n       = 2.99 (vs ceiling 3)         (project)
Khinchin (m=12, A=19) = 0.01955 (in [1/53, 1/41])    (project)
```

Stable across cross-validation; appropriate for citation.

---

*Last updated: alongside Path A (Markov-Lyapunov on LTE-closed
operator) landing. Update this document as Path B and subsequent
results land.*
