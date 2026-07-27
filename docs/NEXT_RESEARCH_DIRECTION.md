# Next Research Direction: Cross-Resolution Lyapunov Stability

## Purpose

The strongest current line in this repository is the Post-Exit Cylinder Map
(PECM) and its finite positive super-eigenvector certificates.

The next research objective should not be another larger finite computation by
itself. It should be to determine whether the finite Perron/Lyapunov vectors
converge toward a stable symbolic object that survives refinement and supports
exact pointwise inequalities.

The central gap is:

> Finite contraction on residue quotients does not yet imply uniform
> infinite-dimensional or per-orbit contraction.

The immediate program is therefore to test whether the finite certificates are
compatible across mixed `2`-adic/`3`-adic resolutions and whether they admit a
low-complexity symbolic representation.

## Implementation status: first Galerkin-compatible ladder

Phases A-C now have an in-memory, deterministic implementation:

- `collatz_exp/pecm_vector_export.py` exports common-`alpha` positive vectors,
  state-order hashes, `Mh/h`, graph roles, numerical residuals, and separate
  descent/reentry/unresolved counts.
- `collatz_exp/pecm_refinement.py` implements exact mixed-adic parent maps,
  legal fibers, prolongation, conditional averaging, sequential Galerkin
  coarsening, and three distinct exact rational operator diagnostics.
- `collatz_exp/pecm_consistency.py` builds one finest sampled operator,
  derives the coarser ladder, solves matched resolvents, computes minimax
  mean/min/max lift errors, and measures surviving-branch oscillation with the
  cemetery survival correction retained.
- `docs/reports/pecm_cross_resolution_consistency.json` records the first
  reproducible smoke ladder.

The first run uses `(4,0) -> (6,1) -> (8,2)`, `R = 2..30`, four CRT samples per
finest row, and common `alpha = 0.55`. All `133,632` finest transition samples
resolve. The result is mixed:

| Quantity | `(4,0) -> (6,1)` | `(6,1) -> (8,2)` |
|---|---:|---:|
| `E_mean` | `0.189683` | `0.362275` |
| `E_min` | `0.703883` | `0.787288` |
| `E_max` | `0.486959` | `0.940103` |
| maximum log lift spread | `1.921116` | `2.923891` |
| maximum live target ratio | `5.267161` (Galerkin-induced) | `1.995672` (concrete finest sample) |

The common-`alpha` resolvent gives numerical super-eigenvector ratios below
`0.55` at every level; these are resolvent bounds, not independent spectral
estimates. The raw cross-resolution errors grow and live target ratios still
exceed one.
This is therefore not evidence for raw pointwise stability at the tested
levels and triggers the stated stop condition. It does not rule out eventual
asymptotic stabilization. The negative finite signal pushes the next step
toward cusp/tail renormalization, wavelet detail analysis, and a branchwise
object.

The exact Galerkin defect is zero by construction. The pointwise projective
defect and the stronger full conditional-expectation defect are nonzero and
are reported separately. Independently sampled legacy operators are also
non-compatible at both adjacent pairs. None of these float64 results is marked
proof-eligible.

The production `(8,2) -> (10,3) -> (12,4)` ladder is intentionally not run by
this in-memory implementation: `(12,4)` has `4,810,752` states, and converting
its target array and fibers into Python objects would require multiple
gigabytes. A chunked arithmetic-parent-map implementation is now a concrete
prerequisite rather than an optional optimization.

## Implementation status: first exact branch cylinder

The worst concrete live-target ratio in the smoke ladder was used only to
*select* one adversarial seed. Its branch coverage was then rebuilt from exact
arithmetic. The selected root is

```text
(R, u mod 2^11, u mod 3^2) = (9, 55, 2).
```

Every member of this infinite cylinder follows the full valuation word

```text
(1,1,1,1,1,1,1,1,3,2,4)
```

until reentry at `R' = 2`. The exact macro is

```text
F(n) = (177147 n + 186875) / 131072,
```

so it is genuinely expanding in ordinary size: `3^11 > 2^17`. Fixing the
target modulo `2^8` requires source precision

```text
A_post + R' + 8 - 1 = 9 + 2 + 8 - 1 = 18.
```

The root therefore partitions into exactly `128` children modulo `2^18`.
Exact replay verifies every child, and their targets cover all `128` odd
classes modulo `2^8` at `(R', u mod 3^2) = (2,2)`.

The same computation produces a small symbolic success. On the entire
selected root,

```text
H(n,R) = n * (23/22)^R
```

satisfies

```text
H(F(n),2) / H(n,9)
    <= 7164821035427968 / 7236312975589017
    < 1.
```

This is an exact local cylinder inequality, not a global Lyapunov theorem. The
`128` target nodes have not yet been expanded, so the transition graph is open
and max-plus/Karp is correctly marked not applicable. The result identifies a
concrete candidate principal part—positive tail depth can pay for an expanding
size branch—and turns the next step into a sharp question: does one cusp base
survive exact expansion of the full target frontier?

Implementation and artifact:

- `collatz_exp/symbolic_branch_certificate.py`
- `docs/reports/pecm_exact_selected_cylinder_pilot.json`

## Implementation status: exact recursive `R=2` frontier

The `128` open targets from the selected-cylinder pilot have now been
expanded as a complete symbolic source cover. Writing `n=4u-1`, the odd
source units split exactly by `u mod 8`:

- `u=1 mod 8` descends at the first post-exit step;
- `u=5 mod 8` descends at the first post-exit step;
- `u=3 mod 8` expands once and descends at the second post-exit step;
- `u=7 mod 8` reenters through the full word `(1,2)`.

Thus `96` of the `128` coarse states descend uniformly. The final `32` do not
form a finite next layer. They are the exact countable family

```text
r = v2(9u+1)-1 >= 2,
v = (9u+1)/2^(r+1),
F(4u-1) = 2^r v - 1.
```

For every fixed `r` and every odd target `b mod 2^k`, the unique source
cylinder is

```text
u = (2^(r+1)b - 1) 9^(-1) mod 2^(r+k+1).
```

At `k=8`, each depth therefore has `128` target-fixed leaves and reaches all
odd target residues modulo `256`. Required source precision grows with `r`,
so no finite adaptive residue refinement can close this cover honestly.
There are no unresolved positive source integers; the *target grammar* is
what remains infinite and open.

This expansion exactly refutes the first outer-tail candidate class. The
`r=2` subfamily preserves `R=2` while increasing ordinary size; its least
current-domain witness is

```text
187 -> 211.
```

Consequently, `H(n,R)=n^alpha c^R` fails for every `alpha>0` and `c>0`.
Moreover, at every finite resolution `(k,ell)`, the coarse state
`(R,u mod 2^k,u mod 3^ell)=(2,-1,-1)` has a positive refined expanding
self-loop. This excludes strict one-step candidates
`n^alpha h(finite mixed 2-adic/3-adic state)` for `alpha>=0` and positive
`h`. The positive witnesses depend on `(k,ell)` and converge profinitely to
`u=-1`; they are not a single positive orbit or cycle.

The obstruction also identifies a secondary cusp. On an `R=2 -> 2` loop,

```text
T(u) = (9u+1)/8,
S = v2(u+1) = v2(n+5)-2,
S(T(u)) = S(u)-3,
F(n)+5 = 9(n+5)/8.
```

Therefore

```text
K(n,u) = (n+5) (23/22)^S
```

contracts on every such loop by the exact factor

```text
(9/8)(22/23)^3 = 11979/12167 < 1.
```

The maximal run now has an exact induced exit grammar as well. If

```text
j = floor((S-1)/3),
```

then

```text
u_j+1 = 9^j(u+1)/8^j,
S_exit = S-3j in {1,2,3}.
```

The residual coordinate completely determines the next event:

| `S_exit` | Exact event | Conditional Haar mass on odd `Z_2` |
|---:|---|---:|
| `1` | first-post descent | `4/7` |
| `2` | second-post descent | `2/7` |
| `3` | higher-`R` reentry | `1/7` |

For the reentry branch, writing `u+1=2^S w` with `w` odd gives

```text
R_next = 2 + v2(9^(j+1)w - 1) >= 3.
```

In the first two rows, descent is below the post-compression exit source, not
necessarily below the original pre-loop value. The `6/7` versus `1/7` split
is a normalized odd-unit Haar-average renewal diagnostic, not a pointwise
Lyapunov inequality.

This is evidence for a *hierarchy of unbounded cusp coordinates*, not a
global Lyapunov theorem. The next section records the exact resolution of
the `S_exit=3` handoff and the new obstruction exposed after it.

Implementation and artifact:

- `collatz_exp/symbolic_frontier_certificate.py`
- `docs/reports/pecm_r2_recursive_tail_cusp.json`

## Implementation status: higher-`R` phase and affine-ghost atlas

The `S_exit=3` handoff is now exact. Put `m>=1` and

```text
u+1=2^(3m)w,  w odd.
```

The full valuation word through the higher-tail exit is `(1,2)^m`, with

```text
n0=2^(3m+2)w-5,
n1=4*9^m*w-5,
R_next=2+v2(9^m*w-1).
```

For every `m>=1`, `R>=3`, odd target `b mod 2^k`, and source class
`a mod 3^ell`, an explicit mixed source cylinder lands in that target fiber.
Its source 2-adic precision is `3m+R+k-2`, and the target gains exactly `2m`
3-adic digits. The existing cusp satisfies the exact full-phase inequality

```text
EH(n1)/E2(n0)=(11979/12167)^m<1.
```

The first higher-`R` post stage is also exact. For `N=2^R v-1` and
`q=v2(3^R v-1)`,

```text
Z=(3^R v-1)/2^q,
Z<N iff (2^(R+q)-3^R)v>2^q-1.
```

Every tail-reentry or continuing target fiber has an explicit inverse
2-adic residue, and the stage gains `R` further 3-adic digits. Contracting
affine slopes require exact magnitude intervals in addition to residues.

The single `-5` cusp is nevertheless not global:

```text
1051 -> 1183 -> 4495
```

expands it by `125/33` for every cusp base. The replacement is a local
affine-ghost chart. For an expanding exact word

```text
T_W(n)=(3^M n+B)/2^A,
D_W=3^M-2^A,
L_W(n)=D_W n+B,
g_W=-B/D_W,
```

one has

```text
L_W(T_W(n))=(3^M/2^A)L_W(n),
v2(L_W(T_W(n)))=v2(L_W(n))-A.
```

Thus `L_W(n)c^v2(L_W(n))` contracts iff `c^A>3^M/2^A`. A fixed expanding
word can repeat only finitely often: `r` repetitions require
`rA<=v2(L_W(n))`.

The exact chart switch from word `W` to word `V` is

```text
L_V(T_W(n))
  = [D_V*3^M_W/(2^A_W*D_W)]L_W(n)
    + B_V-D_V*B_W/D_W.
```

The additive ghost-gap term is now the primary proof obstruction. The next
theorem-facing task is to build the induced ghost-atlas graph and prove
compatible edge inequalities, or identify a persistent chart-switch family
that prevents them.

Implementation and artifact:

- `collatz_exp/symbolic_higher_r_certificate.py`
- `docs/reports/pecm_higher_r_affine_ghost.json`

## 0. Mathematical preflight

Four issues must be handled before raw vector comparisons have proof-facing
meaning.

1. **Build a projectively compatible operator ladder.** The present PECM level
   samples a fixed number of CRT lifts. Refining `(k, ell)` changes both the
   cylinder partition and the representatives sampled, so the existing
   operators are not automatically restriction/prolongation levels of one
   infinite operator. Define restriction and prolongation maps first and
   measure the intertwining defect

   ```text
   D_{k,ell} =
       P_{k,ell} M_{k+2,ell+1}
       - M_{k,ell} P_{k,ell}.
   ```

   Vector stability is interpretable only if this defect is zero by
   construction or tends to zero with a proved bound.

2. **Use a common positive extension.** The current positive resolvent
   super-eigenvector uses a level-dependent `alpha`. Raw vectors computed with
   different `alpha` values solve different equations. Cross-level comparison
   should use one common `alpha < 1`, or should explicitly continue the vectors
   in `alpha` and compare at matched values.

3. **Renormalize the Mersenne cusp.** The states
   `n = 2^R u - 1` approach the `2`-adic obstruction `-1` as `R -> infinity`.
   A bounded continuous residue-only pointwise Lyapunov function would extend
   to that obstruction and cannot strictly contract there. Fit and compare

   ```text
   log h(R, u) - kappa R
   ```

   (or another explicitly derived tail principal part), not only raw `log h`.
   The stable object may live on a renewal tower with an unbounded cusp weight,
   rather than on a compact profinite space with a bounded potential.

4. **Separate averaged from pointwise inequalities.** `M h <= lambda h` is an
   averaged killed-transfer inequality. A single expanding legal lift can be
   hidden by contracting siblings. The pointwise upgrade therefore needs
   either a max-plus/branchwise certificate or a uniform branch-oscillation
   theorem strong enough to convert the average bound into a worst-branch
   bound.

These are not reasons to abandon the direction. They specify the mathematical
object that the experiment must approximate.

## 1. Primary theorem-shaped target

For a mixed residue state

```text
(R, u mod 2^k, u mod 3^ell)
```

associated with

```text
n = 2^R u - 1,
```

seek positive functions `h_{k,ell}` and a constant `lambda < 1` such that

```text
M_{k,ell} h_{k,ell} <= lambda h_{k,ell}
```

holds on the full finite post-exit state space, with all of the following
properties:

- `lambda` is uniformly bounded away from `1` as `(k, ell)` increase.
- The vectors are strictly positive on recurrent and transient states.
- Their distortion under refinement remains controlled after cusp
  renormalization.
- Their values can be approximated by a fixed symbolic formula with finitely
  many residue corrections plus an explicit tail principal part.
- The resulting symbolic formula can be checked through exact branch
  inequalities rather than floating-point spectral estimates.

A successful result would not by itself prove Collatz, but it would convert the
current finite evidence into a substantially more theorem-like object.

## 2. Cross-resolution consistency experiment

Let `h_{k,ell}` be a normalized positive super-eigenvector at level `(k, ell)`
and let `h_{k+2,ell+1}` be the corresponding vector at the next refinement.

For each coarse state `x`, compare it with all legal refined lifts `y -> x`.
After subtracting the fitted cusp principal part, define

```text
mean_lift(x) = mean_y log h_{k+2,ell+1}(y)
min_lift(x)  = min_y  log h_{k+2,ell+1}(y)
max_lift(x)  = max_y  log h_{k+2,ell+1}(y).
```

After optimizing over an additive normalization constant `c`, compute

```text
E_mean(k,ell) =
    min_c max_x |log h_{k,ell}(x) - mean_lift(x) - c|

E_min(k,ell) =
    min_c max_x |log h_{k,ell}(x) - min_lift(x) - c|

E_max(k,ell) =
    min_c max_x |log h_{k,ell}(x) - max_lift(x) - c|.
```

Also compute the operator intertwining defect and the oscillation of the
one-step branch ratios, not only the spread of `h`.

### Interpretation

- If the operator defect and all three vector errors decrease, the finite
  vectors may approximate a limiting profinite/tower Lyapunov function.
- If the mean error decreases but the minimum and maximum errors do not, only
  an averaged object may be stabilizing.
- If vector errors shrink but branch-ratio oscillation does not, the limit may
  remain useless for deterministic pointwise descent.
- If errors remain large or grow, the finite Perron vectors are likely
  resolution-specific and should not be treated as approximations to one
  infinite object.

### Required artifact

Create a JSON report containing:

```json
{
  "levels": [[8, 2], [10, 3], [12, 4]],
  "normalization": "geometric_mean_1_after_cusp_subtraction",
  "common_alpha": null,
  "operator_intertwining_defect": [],
  "errors": {
    "mean": [],
    "min": [],
    "max": []
  },
  "branch_ratio_oscillation": [],
  "lift_spread_quantiles": {},
  "worst_coarse_states": []
}
```

Suggested filename:

```text
docs/reports/pecm_cross_resolution_consistency.json
```

## 3. Martingale and wavelet representation

The mean over refined lifts is the natural conditional expectation on nested
mixed-adic cylinder sigma-algebras. Treat the renormalized potentials

```text
V_{k,ell} = log h_{k,ell} - kappa R
```

as a candidate martingale and decompose every refinement into coarse and detail
parts.

Track the mixed-adic Haar/Walsh detail norms:

```text
||Delta_{k,ell} V||_2
||Delta_{k,ell} V||_infinity.
```

Square-summable `L2` details would support an averaged or almost-everywhere
limit. A pointwise program needs the stronger summability

```text
sum_{k,ell} ||Delta_{k,ell} V||_infinity < infinity,
```

or another uniform Hölder/bounded-distortion estimate. This distinction gives
the consistency experiment a direct functional-analytic interpretation.

## 4. Symbolic representation target

Do not use unconstrained black-box regression as the final object. Use it only
to identify a small candidate basis.

Fit `log h(R, a, b)` against arithmetic features such as:

```text
1
R
log(R + 1)
v2(a + 1)
v2(3^R a - 1)
indicator[a mod 2^j = c]
indicator[b mod 3^j = d]
canonical start-residue height
canonical endpoint-residue height
```

The preferred candidate class is

```text
H(n) = n^alpha * exp(kappa R) * A_R * B_{u mod 2^s} * C_{u mod 3^t}
```

or equivalently

```text
V(n) = alpha log n
     + kappa R
     + rho_bounded(R)
     + phi_2(u mod 2^s)
     + phi_3(u mod 3^t).
```

The goal is not the best numerical fit. The goal is the smallest interpretable
model that preserves the contraction inequality.

### Model-selection order

1. `alpha log n + kappa R + rho_bounded(R)`
2. Add a `2`-adic residue correction.
3. Add a `3`-adic residue correction.
4. Add a canonical representative/carry-height term.
5. Add one interaction term only if necessary.
6. Reject models whose unexplained residue complexity grows rapidly with
   resolution.

### Success criterion

A candidate is interesting only if all of the following hold:

- Fit error decreases or remains stable across held-out levels.
- The inferred coefficients and cusp slope stabilize.
- Exact branch verification succeeds with a uniform negative margin, or the
  average-to-pointwise oscillation criterion succeeds.
- The model controls both recurrent and transient states.

## 5. Exact pointwise verification

For a symbolic candidate `V`, evaluate every branch of the compressed post-exit
map and attempt to prove

```text
V(F(n)) - V(n) <= -epsilon
```

outside an explicitly listed finite exceptional set.

The verification should avoid floating-point logarithmic comparisons whenever
possible. For example, if

```text
H(n) = n^alpha * exp(kappa R) * A_R * B_a * C_b,
```

then compare

```text
H(F(n)) / H(n) <= lambda
```

by clearing denominators and converting all residue-dependent factors into
exact rational or algebraic quantities. Where irrational exponents are
unavoidable, use interval arithmetic with a formally recorded precision and
margin.

### Required outputs

For every branch class, store:

- source cylinder;
- exact transition rule;
- target cylinder;
- symbolic ratio;
- verified upper bound;
- margin to `1`;
- exception status;
- integer-realizability status.

Suggested artifact:

```text
docs/reports/symbolic_lyapunov_branch_certificate.json
```

### Least-lift domination

There is a promising exact shortcut once a refined cylinder fixes a complete
post-exit macro word `w` and its target cylinder. On that cylinder,

```text
F_w(n) = (3^m n + B_w) / 2^A
```

with `B_w > 0`. If the symbolic source and target corrections are fixed and
the Archimedean exponent in `H` is positive, then

```text
H(F_w(n)) / H(n)
  = exp(Delta residue potential)
    * (3^m / 2^A + B_w / (2^A n))^alpha
```

is strictly decreasing in `n`. The least positive integer in the CRT cylinder
is therefore the worst lift. One exact rational or interval check at that least
lift certifies every larger integer in the cylinder.

This suggests an adaptive exact verifier:

1. Refine until the macro word and target cylinder are fixed.
2. Compute the least positive CRT representative.
3. Certify that representative exactly.
4. Split only cylinders whose least lift fails or whose macro word is not yet
   fixed.

This route bypasses the sampled-lift average instead of trying to infer a
pointwise theorem from it.

## 6. Average-to-pointwise collapse target

For a coarse cylinder `C` with `D` sampled lifts, let

```text
r(z) = H(F(z)) / H(z)
```

on every surviving legal lift `z`, and assign ratio zero to every killed
descent lift. Let `p_C` be the fraction of surviving lifts. The killed transfer
operator controls the unconditional row average

```text
q_C = (1/D) sum_{z survives} r(z) <= lambda,
```

not the conditional live mean `q_C / p_C`. Suppose a uniform distortion
estimate also proves

```text
max_C log r - min_C log r <= omega.
```

For `p_C > 0`, the correct bound is

```text
max_C r <= exp(omega) * (q_C / p_C)
        <= exp(omega) * (lambda / p_C).
```

Rows with `p_C = 0` have no surviving branch and are vacuous. If
`p_C >= p_min > 0` uniformly on all other rows, the averaged certificate
becomes pointwise as soon as

```text
lambda * exp(omega) / p_min < 1.
```

The survival factor is essential: contracting killed siblings can hide an
expanding live branch. If a future operator instead controls the conditional
live mean directly, the `p_min` denominator disappears. This corrected
inequality is the cleanest possible bridge from the existing PECM contraction
to deterministic descent. The cross-resolution experiment should prioritize
both `omega` and `p_min`, because convergence of the vector alone controls
neither.

If `omega` fails to shrink globally, partition the states into a regular class
where the inequality closes and a persistent exceptional-cylinder tree to be
handled arithmetically.

The Doob transform induced by a positive finite eigenvector is also useful
here: it describes the finite process conditioned on avoiding descent. Its
stationary mass is a microscope for the exceptional rays, not evidence that
those rays represent positive integers.

## 7. Persistent exceptional cylinders and the residue-rate gap

Every finite accelerated valuation word determines:

- its real drift;
- a canonical starting residue modulo a power of `2`;
- a canonical endpoint residue modulo a power of `3`.

For an exponent-code prefix `w`, write these least nonnegative
representatives as `r_2(w)` and `r_3(w)`. A code generated forever by one fixed
positive integer eventually has no new high start bits, so its normalized
start-residue height tends to zero. The same kind of vanishing condition holds
for its endpoint representatives.

This suggests a deterministic alternative to orbit equidistribution.

### Residue-rate gap target

Prove that every infinite non-descending, near-critical exponent code outside
the trivial cycle satisfies

```text
liminf_k max(
    log(1 + r_2(w_k)) / A_k,
    log(1 + r_3(w_k)) / k
) >= c
```

for some explicit `c > 0`, where `A_k` is total `2`-adic valuation.

A fixed positive-integer orbit would require the left side to vanish, giving a
contradiction. This is a “no immortal cylinder” theorem: locally legal bad
paths may survive in the `2`-adic completion, but they are forced away from
eventually-zero binary expansions and therefore cannot come from a fixed
positive integer.

The PECM exceptional states, Christoffel/slope filters, and mixed-adic
representatives make this repository well suited to search for the inequality.
It also avoids pretending that density-one or Markov-typical behavior controls
every orbit.

A particularly strong finite pattern would be: after some refinement depth,
every bad cylinder has at most one bad child, and those forced child digits
converge to one of finitely many mixed-adic ghosts disjoint from the diagonal
embedding of the positive integers. That would reduce the infinite exceptional
set to a finite substitution grammar and an exact non-integrality proof.

## 8. Risk-sensitive continuation

Interpolate between the averaged Perron operator and the worst-case max-plus
operator with a tilted family

```text
L_theta f(x) =
    sum_b p(b | x) * exp(theta * Delta(b)) * f(F_b x).
```

- `theta = 0` recovers the averaged survival operator.
- Moderate `theta` probes renewal large deviations.
- `theta -> infinity` isolates the worst legal branch and the max-plus
  calibrated subaction.

Track the leading eigenvalue, eigenvector, and dominant occupation measure as
`theta` increases. A phase transition identifies exactly which cylinder family
separates typical contraction from pointwise failure. Feed that family into
the residue-rate and integer-realizability analysis rather than fitting the
whole state space blindly.

## 9. Distinguish average from pointwise contraction

The repository should continue to separate:

- IID geometric-valuation drift;
- stationary Markov average drift;
- finite Perron contraction;
- finite max-plus contraction;
- pointwise symbolic descent.

The repeated factor `3/4` is best described as:

> The typical multiplicative factor under the geometric-valuation baseline,
> which also appears in several finite constrained diagnostics.

It should not be described without qualification as a deterministic per-orbit
growth rate.

## 10. Immediate implementation plan

### Phase A: Compatible vector export

Add a machine-readable export for each positive super-eigenvector:

```text
state_id
R
u_mod_2k
u_mod_3ell
h
Mh_over_h
recurrent_or_transient
alpha
state_order_hash
```

Use a common `alpha` across compared levels.

### Phase B: Refinement and operator maps

Implement explicit refined-to-coarse maps, enumerate all legal children, and
define compatible conditional lift weights. Test the operator intertwining
identity or record its defect.

### Phase C: Consistency and detail report

Compute:

- `E_mean`, `E_min`, and `E_max`;
- lift-spread quantiles;
- mixed-adic Haar/Walsh detail norms;
- branch-ratio oscillation;
- worst inconsistent states;
- cusp-slope estimates.

### Phase D: Structured fitting

Fit the candidate basis in increasing complexity and hold out one resolution
level from training.

### Phase E: Exact certificate attempt

Translate the best stable model into branchwise exact inequalities. Split any
surviving exceptions into a nested exceptional-cylinder tree and measure their
`2`-adic/`3`-adic representative rates.

## 11. Suggested implementation modules

Implemented modules:

```text
collatz_exp/pecm_vector_export.py
collatz_exp/pecm_refinement.py
collatz_exp/pecm_consistency.py
collatz_exp/symbolic_branch_certificate.py
collatz_exp/symbolic_frontier_certificate.py
```

Planned modules:

```text
collatz_exp/symbolic_lyapunov_fit.py
collatz_exp/exceptional_cylinder_tree.py
```

Implemented tests:

```text
tests/test_pecm_vector_export.py
tests/test_pecm_refinement.py
tests/test_pecm_consistency.py
tests/test_symbolic_branch_certificate.py
tests/test_symbolic_frontier_certificate.py
```

Planned tests:

```text
tests/test_symbolic_lyapunov_fit.py
tests/test_exceptional_cylinder_tree.py
```

The consistency module should be deterministic and should support small
fixture graphs so that refinement logic can be tested independently from the
large PECM computation.

## 12. Adversarial classes to retain

The analysis should not fit only dominant or recurrent states. Explicitly
retain:

- states with the largest `Mh/h` ratio;
- deep tail reentries;
- states near the current obstruction class;
- transient states added by the positive resolvent extension;
- states whose refined lifts have unusually large weight spread;
- cylinders whose behavior changes sharply after adding one `3`-adic digit;
- classes that remain exceptional at multiple consecutive resolutions;
- branches with small canonical start and endpoint representatives;
- branches selected by the high-`theta` risk-sensitive operator.

The strongest candidate is not the one with the best average fit. It is the one
that survives the worst legal, positive-integer-realizable branch.

## 13. Stop conditions

Demote the raw cross-resolution Perron line if any of the following occurs:

- contraction factors trend upward toward `1`;
- operator intertwining defects do not shrink;
- refinement errors grow materially after common-alpha and cusp normalization;
- the weight vectors require exponentially increasing unexplained residue
  complexity;
- symbolic coefficients or the cusp slope fail to stabilize;
- exact branch margins collapse as resolution increases;
- exceptional classes reproduce indefinitely with vanishing representative
  rates;
- the fitted formula performs well only on recurrent states but fails on
  transient or lifted states.

A negative result would still be valuable because it would show that the
present finite Perron certificates do not encode a stable infinite Lyapunov
function.

## 14. Research priority

Recommended allocation within the Collatz project:

```text
40% exact affine-ghost chart-switch inequalities
25% higher-R induced grammar with magnitude intervals
20% cusp-renormalized PECM ranking of candidate charts
10% exceptional-cylinder residue-rate search
 5% unrelated diagnostics
```

The next meaningful milestone is:

> Construct a nontrivial exact induced grammar of affine-ghost charts and
> either prove compatible contraction across every chart-switch edge or isolate
> a persistent positive-integer-realizable switch family that obstructs it.

The cross-resolution vector lane remains useful for prioritizing charts and
guessing edge weights, but exact branch identities and finite magnitude
cutoffs remain the proof-facing acceptance test.

## 15. Definition of a publishable result

A worthwhile computational research result would be any one of the following:

- a stable sequence of compatible finite Lyapunov vectors with quantified
  cross-resolution and operator-intertwining error;
- a compact cusp-renormalized mixed-residue approximation whose coefficients
  stabilize across levels;
- a uniform branch-oscillation estimate that upgrades an averaged contraction
  to a pointwise contraction;
- an exact finite branch certificate with a contraction factor uniformly below
  `1` over a nontrivial family of resolutions;
- a rigorous counterexample showing that the finite Perron vectors cannot
  converge to a bounded-distortion profinite function;
- identification of one persistent exceptional-cylinder family together with
  an exact reduced dynamical system governing it;
- an exact affine-ghost atlas on a nontrivial induced family, with certified
  chart-switch inequalities and a well-founded repeat budget;
- a residue-rate gap theorem excluding every persistent exceptional path from
  the positive integers.

Any of these would sharpen the current proof landscape, even without resolving
the Collatz conjecture.

## 16. Literature touchpoints

- Terence Tao, [*Almost all orbits of the Collatz map attain almost bounded
  values*](https://arxiv.org/abs/1909.03562): the strongest current
  distributional/renewal comparison and the source of the almost-all versus
  every-orbit wall.
- Olivier Rozier and Claude Terracol, [*Paradoxical behavior in Collatz
  sequences*](https://arxiv.org/abs/2502.00948): a false Collatz orbit would
  generate infinitely many paradoxical sequences, making finite stopping
  certificates a direct proof-facing target.
- Oliver Kramer, [*Adaptive Search in Collatz Exponent-Code Space via 2-adic
  and 3-adic Constraints*](https://arxiv.org/abs/2607.10041): introduces the
  `2`-`3`-infinity diagnostic and proves the necessary vanishing of normalized
  residue rates for codes generated by a fixed positive integer.
- Tristan Stérin and Damien Woods, [*The Collatz process embeds a base
  conversion algorithm*](https://arxiv.org/abs/2007.06979): motivates treating
  persistent exceptional cylinders as an exact mixed-base carry grammar rather
  than only a finite residue automaton.
- Takehiko Mori, [*Application of Operator Theory for the Collatz
  Conjecture*](https://arxiv.org/abs/2411.08084): supplies the broader operator
  perspective in which irreducibility/orbit equivalence, rather than a finite
  eigenvalue alone, is the proof-facing property.
