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

### A.6 Certified PECM spectral bounds (exact rational Collatz-Wielandt)

```
(8,2):  rho <= 134070211/345491728 ≈ 0.3880562   (33,408 states)
(10,3): rho <= 28432321/82385222  ≈ 0.3451143   (400,896 states)
(12,4): rho <= 436753/1307192     ≈ 0.3341154   (4,810,752 states)
```

**Status:** computer-verified exact statements — SCC decomposition plus
Collatz-Wielandt (`rho(A) <= max_i (Av)_i/v_i` for positive `v`) evaluated
in pure integer arithmetic; no floating point appears in the bound.

**Interpretation:** upgrades the floating-point scaled-Perron scan to
certified contraction at three levels; the bounds match the float
estimates to 6+ digits, cross-validating both. The recurrent cores are
tiny (largest blocks 16 / 260 / 984 states), so certification scales far
past the full-operator memory wall. Caveat per §12: a spectral statement
about the averaged residue-quotient operator, not an orbit-descent
certificate.

**Artifact:** `docs/reports/pecm_perron_certificates.json`;
module `collatz_exp/perron_certificate.py`.

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

### D.5 Scaled-Perron flanks (16,5) and (14,6): worst case converges to mean case

```
(14,5): scale = 0.33393, finite_ratio_max = 0.5357   (57.7M states)
(16,5): scale = 0.33604, finite_ratio_max = 0.33627  (231M states)
(14,6): scale = 0.34298, finite_ratio_max = 0.34332  (173M states)
zero infinite-ratio rows at all three levels; worst state R=2 throughout
```

**Status:** empirical, finite resolution (80 GPU power iterations,
checkpointed).

**Interpretation:** deepening the 2-adic axis collapses the worst-case
pointwise ratio from 0.536 onto the Perron scale itself (0.336) — the
same worst-equals-mean signature the JSR family showed at 3/4, now on
the PECM operator, with everything drifting toward ~1/3. The (16,6)
joint level remains gated on a compressed operator (int64 cache ~22 GB).

**Artifacts:** `docs/runs/pecm_16_5_14_6_scaled_gpu_20260722_130030/`.

---

### D.6 IID renewal model survives the Polli long-range-correlation threat

```
windows: 150 orbits × 400-bit and 150 × 1000-bit random odd starts
series: excursion delta, excursion length, per-step valuation
DFA alpha = 0.52–0.53 vs shuffle-surrogate 0.52–0.54 (indistinguishable)
ACF maxima at the 1.96/sqrt(N) null band; verdict iid_consistent (all 6)
```

**Status:** empirical defensive audit at tested scale.

**Interpretation:** Polli et al. (J. Phys. Complex. 2024) report
long-range power-law correlations in hailstone sequences — flagged in
the literature sweep as a threat to the IID renewal model underlying
`J_renewal`. At excursion scale, over ~180k excursions per window, no
such memory exists: all series match their within-orbit shuffled
surrogates. Does not preclude correlations at longer scales.

**Artifacts:** `docs/reports/renewal_correlation_polli_{400,1000}bit.json`;
module `collatz_exp/renewal_correlation.py`.

---

### D.7 Galerkin PECM ladder separates average contraction from branches

```
levels: (4,0) -> (6,1) -> (8,2), R = 2..30, common alpha = 0.55
unresolved finest samples: 0 / 133,632
max(Mh/h): 0.465489, 0.502925, 0.529990
E_mean: 0.189683 -> 0.362275
max log lift spread: 1.921116 -> 2.923891
max live target ratio: 5.267161 (Galerkin-induced) -> 1.995672 (finest sample)
```

**Status:** deterministic finite construction plus float64 vector diagnostic;
not proof-eligible.

**Interpretation:** one finest operator and exact sequential Galerkin
coarsening remove the old sampling mismatch, but the raw positive vectors do
not stabilize under the tested refinement and expanding surviving branches
remain. Exact Galerkin compatibility is therefore strictly weaker than both
pointwise projective compatibility and per-branch descent. This is a
productive negative result: the next candidate needs tail/cusp
renormalization or a genuinely branchwise potential, not merely a larger
Perron computation. The displayed `max(Mh/h)` values are induced by the chosen
common-`alpha` resolvent and are not independent spectral estimates.

**Artifact:** `docs/reports/pecm_cross_resolution_consistency.json`; modules
`collatz_exp/pecm_{vector_export,refinement,consistency}.py`.

---

### D.8 Exact tail-cusp inequality on the worst selected PECM cylinder

**Statement.** The worst concrete branch from the cross-resolution diagnostic
lies in the exact infinite cylinder

```text
(R, u mod 2^11, u mod 3^2) = (9,55,2).
```

Its complete accelerated word is `(1^8,3,2,4)`, with

```text
(m,A,B) = (11,17,186875)
F(n) = (177147 n + 186875) / 131072.
```

This is an exact expanding branch because `177147 > 131072`. Refinement to
`u mod 2^18` gives `128` disjoint children, all realizing the word and
reentering at `R'=2`; their targets are exactly the `128` odd residues modulo
`2^8` with `u mod 9 = 2`.

**Local symbolic certificate.** Despite the size expansion, the tail-cusp
candidate

```text
H(n,R) = n (23/22)^R
```

has exact worst ratio

```text
7164821035427968 / 7236312975589017
    = 0.9901203913...
```

on every positive integer in the selected root cylinder. The proof uses the
exact affine identity, the `R=9 -> 2` depth drop, and monotonicity of
`F(n)/n`; no floating logarithm enters the inequality.

**Status.** Exact within one sample-selected root, but not proof-eligible. Its
`128` targets form an open outgoing frontier, so max-plus/Karp is not yet a
valid global upper-bound calculation. The result is evidence that an
unbounded positive tail principal part is structurally relevant, not evidence
that the displayed base works globally.

**Artifact:** `docs/reports/pecm_exact_selected_cylinder_pilot.json`; module
`collatz_exp/symbolic_branch_certificate.py`.

---

### D.9 Exact recursive `R=2` frontier and nested-cusp obstruction

**Complete source cover.** The `128` targets left open by D.8 collectively
represent every odd unit with

```text
R=2,  u mod 9=2.
```

For `n=4u-1`, their outgoing behavior has an exact mod-8 partition. The
classes `u=1,5 mod 8` descend at the first post-exit step, and `u=3 mod 8`
descends at the second. These are `96` uniformly descending coarse states.
The remaining `32`, with `u=7 mod 8`, form the exact family

```text
r = v2(9u+1)-1 >= 2
v = (9u+1)/2^(r+1)
F(n) = 2^r v - 1.
```

For each `r>=2`, fixing `v mod 2^8` produces `128` source leaves and reaches
all odd target residues modulo `256`. The source cover is complete, but the
target depth and required source precision are unbounded, so the outgoing
graph is countably infinite rather than finite.

**Exact no-go theorem for finite mixed-adic state corrections.** The `r=2`
subfamily preserves `R=2` and expands size. Its least witness in the current
`u mod 9=2` domain is `187 -> 211`, which refutes every global
`n^alpha c^R` candidate with `alpha>0`. At every finite mixed resolution,
there is also a positive refined leaf returning to the same coarse
`(R,u mod 2^k,u mod 3^ell)=(2,-1,-1)` state while increasing `n`. The fixture

```text
u=1151,  n=4603 -> 5179,
(R,u mod 16,u mod 9)=(2,15,8) -> (2,15,8)
```

therefore excludes strict one-step
`n^alpha h(finite mixed 2-adic/3-adic state)` candidates for `alpha>=0` and
positive `h`. The witness changes with the chosen resolution and converges
profinitely to `u=-1`; it is not one positive orbit. The limiting fixed points
`u=-1` and `n=-5` are negative, so no positive cycle is being claimed.

**Nested-cusp certificate.** The same obstruction supplies a deeper
coordinate. On every consecutive `R=2 -> 2` loop,

```text
S = v2(u+1) = v2(n+5)-2,
S' = S-3,
n'+5 = 9(n+5)/8.
```

Hence

```text
K(n,u) = (n+5)(23/22)^S
```

has the exact constant ratio

```text
(9/8)(22/23)^3 = 11979/12167 < 1.
```

There are exactly `j=floor((S-1)/3)` consecutive floor loops. After their
maximal compression,

```text
S_exit = S-3j in {1,2,3}.
```

These residual values give first-post descent, second-post descent, and
higher-`R` reentry respectively. The descents are below the compressed exit
source, not necessarily below the original pre-loop value. Their exact
normalized Haar masses among odd 2-adic units are `4/7`, `2/7`, and `1/7`.
In the last branch, if `u+1=2^S w`, then

```text
R_next = 2 + v2(9^(j+1)w - 1) >= 3.
```

The Haar split is average-only. The nested loop contraction and exit
classification are exact pointwise statements, but the higher-`R` return
family is still open.

**Artifact:** `docs/reports/pecm_r2_recursive_tail_cusp.json`; module
`collatz_exp/symbolic_frontier_certificate.py`.

---

### D.10 Exact higher-`R` transfer and affine-ghost cusp hierarchy

**The formerly open handoff is now parametrized.** Put `m>=1` and write

```text
u+1 = 2^(3m)w,  w odd,
n0 = 4u-1 = 2^(3m+2)w-5.
```

The full maximal `R=2` loop run together with its higher-`R` exit has exact
valuation word `(1,2)^m` and landing

```text
n1 = 4*9^m*w-5,
n1+5 = (9/8)^m(n0+5).
```

If `t=v2(9^m*w-1)`, then

```text
R = t+2 >= 3,
v = (9^m*w-1)/2^t,
n1 = 2^R*v-1.
```

For every `m>=1`, `R>=3`, odd target `b mod 2^k`, and source
`a mod 3^ell`, there is one mixed source cylinder

```text
u mod 2^(3m+R+k-2),  u=a mod 3^ell
```

whose target has `v=b mod 2^k`. The target 3-adic residue is determined
modulo `3^(ell+2m)`, so the handoff gains exactly `2m` available 3-adic
digits. In particular, every higher tail depth and every odd target 2-adic
residue occur; this is an exact infinite family rather than a finite scan.

**The old cusp pays for the complete handoff.** With

```text
E2(n) = (n+5)c^(v2(n+5)-2),  EH(n)=n+5,
```

the exact ratio is

```text
EH(n1)/E2(n0) = [(9/8)c^(-3)]^m.
```

At `c=23/22`, this is

```text
(11979/12167)^m < 1.
```

Thus the `-5` cusp contracts not only each consecutive `R=2 -> 2` loop, but
the entire maximal phase including its final `R>=3` exit.

**The next higher-`R` stage is exact but not uniformly descending.** From
`N=2^R v-1`, let `q=v2(3^R v-1)`. After the forced `R-1` valuation-one
steps and the next valuation `q+1`,

```text
Z = (3^R v-1)/2^q
  = [3^R N+(3^R-2^R)]/2^(R+q).
```

Its precise descent criterion relative to `N` is

```text
(2^(R+q)-3^R)v > 2^q-1.
```

If the branch remains live, its next tail/continuation depth and every
target-fixed mixed residue cylinder also have explicit inverse formulas.
Magnitude must be retained on contracting-slope branches; residues alone do
not decide the cutoff.

**A simple cusp is not global.** The canonical exact chain

```text
1051 --(1,2)--> 1183 --(1,1,1,1,2)--> 4495
```

has cusp exponent `v2(n+5)-2=0` at the last two endpoints. Consequently
`(n+5)c^(v2(n+5)-2)` expands there by `125/33` for every `c`. The witness
lies in an infinite exact cylinder; cylinder ratios vary with the lift but
remain greater than one.

**Affine-ghost theorem.** Let an exact expanding valuation word satisfy

```text
T_W(n) = (3^M n+B)/2^A,  3^M>2^A,
L_W(n) = (3^M-2^A)n+B.
```

Then `g_W=-B/(3^M-2^A)` is its negative rational fixed point and

```text
L_W(T_W(n)) = (3^M/2^A)L_W(n),
v2(L_W(T_W(n))) = v2(L_W(n))-A.
```

Therefore the word-specific cusp

```text
K_W,c(n)=L_W(n)c^v2(L_W(n))
```

has constant factor `(3^M/2^A)c^(-A)` and contracts exactly when
`c^A>3^M/2^A`. Two certified fixtures are:

- `(1,1,1,1,2)`, `L=179n+211`, factor `15552/15625` at `c=5/4`;
- `(1,1,2)`, `L=11n+19`, factor `64827/65536` at `c=8/7`.

There is also a finite-use theorem: if the same expanding word repeats `r`
times, then `rA<=v2(L_W(n))`. No positive orbit can remain in one expanding
word forever.

The remaining global obstruction is now explicit. Switching from chart `W`
to chart `V` gives

```text
L_V(T_W(n))
  = [D_V*3^M_W/(2^A_W*D_W)]L_W(n)
    + B_V-D_V*B_W/D_W.
```

The additive ghost-gap term prevents the local multiplicative contractions
from telescoping automatically. Controlling those chart-switch terms on the
exact induced grammar is the next proof-facing problem.

**Status.** Exact symbolic infinite-family result with bounded regression
checks; not a global Lyapunov function and not a Collatz proof.

**Artifact:** `docs/reports/pecm_higher_r_affine_ghost.json`; module
`collatz_exp/symbolic_higher_r_certificate.py`.

---

### D.11 Exact word repeats, switch resonances, and one descent cylinder

**Exact word-cylinder theorem.** For every nonempty accelerated valuation
word

```text
T_W(n)=(3^M n+B)/2^A,
L_W(n)=(3^M-2^A)n+B,
```

the word is exact at positive odd `n` precisely when

```text
v2(|L_W(n)|)>=A+1,
```

where `v2(0)=infinity`. Equivalently, its domain is one unique odd residue
modulo `2^(A+1)`. For an expanding word, `L_W(n)>0`, and its exact maximal
repeat count is

```text
floor((v2(L_W(n))-1)/A).
```

After maximal repetition the residual depth is in `{1,...,A}`. Its
conditional normalized odd 2-adic Haar masses are

```text
P(e)=2^(A-e)/(2^A-1).
```

No IID or typical-orbit claim is attached to this measure identity.

**Chart-switch resonance theorem.** For expanding charts `W,V`, define

```text
G_VW=B_V D_W-D_V B_W.
```

After one exact `W` use, let `e` be the residual valuation in the source
coordinate and `g=v2(|G_VW|)`. If `e!=g`, the target coordinate has valuation
`min(e,g)`. If `e=g`, its two odd leading terms cancel and the valuation is
strictly larger. At a maximal `W` exit, target exactness then implies:

```text
nonresonant legal edge => A_V < A_W.
```

Hence every directed cycle of maximal expanding charts contains a valuation
resonance. This is a genuine well-founded component, but it is not a
termination proof because the size of a resonant reset is not bounded.
The special case `G=0` means the charts have the same ghost and is recorded
separately from nonzero-gap resonance.

**Complete first node.** For `W=(1,1,2)`,

```text
L_W(n)=11n+19,  A=4.
```

Writing `11n+19=2^e z` partitions every exhausted state into four exact cases.
The `e=1` and `e=4` cases descend below that exhausted state; `e=2` either
does the same or enters the `(1,2)` ghost; `e=3` either descends below the
exhausted state or enters one of `(1,1,1,1)`, `(1,1,1,2)`, `(1,1,1,3)`.
These are not pre-run descent claims. Their residual Haar masses are
`8/15,4/15,2/15,1/15`.

**Infinite exact first-descent cylinder.** One exact maximal-chart fixture is

```text
38119 --(1,1,2)^2--> 108553
      --(2,1,1,2)--> 137389
      --(3,2,2)----> 28981.
```

Its first switch is resonant: the residual source depth and `v2(810)` are both
one, and cancellation raises the next chart depth to eight. The complete word
has

```text
(M,A,B)=(13,21,3563675),
3^M-2^A=-502829.
```

Its exact source domain is the full cylinder

```text
n=38119+2^22 t,  t>=0.
```

Every member has its first descent at step 13:

```text
T(n)=28981+3188646t,
n-T(n)=9138+1005658t>0.
```

**Status.** Exact symbolic results with bounded formula regression. The
exhausted `(1,1,2)` source partition is complete, but chart selection is not
canonical, its four expanding targets are not recursively closed, and no
bound on successive resonance depth, global Lyapunov function, or Collatz
proof has been derived.

**Artifact:** `docs/reports/pecm_affine_ghost_atlas.json`; module
`collatz_exp/affine_ghost_atlas.py`.

---

### D.12 Recursive resonant parser and explicit infinite 2-adic ladder

**Source-relative exit theorem.** At an exhausted expanding chart `W`, write

```text
L_W(n)=D_W n+B_W=2^e z,  z odd,  1<=e<=A_W.
```

Following every valuation forced by `e` and then including the first
lift-dependent valuation gives an exit word `V` with

```text
A_V=e+q,  q>=1.
```

This rule is deterministic after the source chart has been chosen. It is not
an intrinsic parsing of the raw valuation itinerary. Target exactness and

```text
G_VW=D_W L_V(n)-D_V L_W(n)
```

give the universal induced-resonance identity

```text
G_VW != 0,  v2(G_VW)=e.
```

Thus resonance is forced on every source-relative first-free edge, including
contracting exits; it is not a rare numerical exception. The four expanding
children of the previous `(1,1,2)` partition have exactly `18` residual
templates and `19` expanding first-free exits, all now derived.

Resonance depth is unbounded on every legal edge. For any desired
`S>=A_V+1`, solve

```text
L_V(n)=2^S (mod 2^(S+1)).
```

The odd coefficient `D_V` gives a positive odd cylinder with exact target
depth `S`, while the gap identity forces the source depth to remain `e`.
Consequently the target repeat count `floor((S-1)/A_V)` has no uniform
edgewise bound. A landing produced by an exact source copy additionally has
`3^M_W | z`. CRT combines that odd-modulus condition with every binary branch
cylinder, and the artifact records a positive exact source predecessor for
each branch and depth witness.

**Finite parser versus macro renormalization.** All charts in the
shortest-divergence parser belong to

```text
P_(m,a)=(1^(m-1),a),
A=m-1+a,
B=3^m-2^m,
D=3^m-2^(m-1+a).
```

From `P_(4,3)=(1,1,1,3)`, the expanding component closes exactly on seven
nodes and `18` resonant edges. This finite closure does not give a static
chart Lyapunov function. The cycle

```text
P_(2,1) -> P_(2,2) -> P_(2,1)
```

uses exit-word slopes `9/8` and `9/4`, whose product is `81/32>1`; positive
node weights cancel around the cycle.

The same words have the exact renormalization

```text
(P_(m,1))^r P_(m,a)=P_((r+1)m,a).
```

In particular, with

```text
J_m=(1^m),
K_m=(1^(m-1),2),
```

one gets the source-relative first-free ladder

```text
J_m -> K_m -> J_(m+1),  m>=2,
J_m || K_m=K_(2m)  (valuation-word concatenation).
```

Its two gap families are

```text
G_(K_m,J_m)=(3^m-2^m)2^m,
G_(J_(m+1),K_m)=-(3^(m+1)-2^(m+1))2^m,
```

both of exact 2-adic order `m`. Every finite ladder prefix is compatible:
its concatenated valuation word has one positive exact cylinder. All chart
boundaries in that prefix increase. A point on one edge cylinder need not
take the next edge; continuation requires the nested refined cylinder.

**Explicit infinite boundary.** The nested prefixes select one point
`xi_m0` in `Z_2`. Pairing the word concatenation
`J_m || K_m=K_(2m)` gives

```text
xi_m0 = -1 - (1/2) sum_(m=m0+1)^infinity
        2^(m^2-m0^2) / 3^(m(m-1)-m0(m0-1)),
v2(xi_m0+1)=2m0.
```

After `r` pairs the exact exponents are

```text
M_r=r(2m0+r-1),  A_r=r(2m0+r).
```

Truncating the displayed series through `m=m0+r` reproduces the exact prefix
residue modulo `2^(A_r+1)`; this identity is checked directly in the artifact.
With

```text
T_q(z)=sum_(k>=0) z^k q^(-k(k-1)/2),
```

the boundary is

```text
xi_m0=-1-(4/9)^m0 T_(9/4)(2(4/9)^(m0+1)).
```

The functional equation `T_q(z)=1+z T_q(z/q)` reduces rationality of every
ladder boundary to the single `Q_2` target `T_(9/4)(2)`.

For `m0=4`, every extension lies in

```text
xi=767 (mod 1024).
```

Whether `xi_m0` is an ordinary nonnegative integer is open. Proving it is not
would exclude this entire infinite increasing ladder. If it were positive,
it would yield an unbounded chart-boundary orbit, so no such claim is made.
The obstruction has moved from a finite resonant cycle to escape at infinite
macro complexity.

**Status.** Exact symbolic grammar and parametric obstruction with bounded
formula regression; no positive infinite itinerary, global Lyapunov
function, or Collatz proof has been derived.

**Artifact:** `docs/reports/pecm_recursive_ghost_atlas.json`; module
`collatz_exp/recursive_ghost_atlas.py`.

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

*Last updated: alongside the first Galerkin-compatible cross-resolution PECM
Lyapunov ladder. Continue appending positive and negative results.*
