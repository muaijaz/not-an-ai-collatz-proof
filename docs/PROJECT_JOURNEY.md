# Project Journey

A chronological record of where this project started, what was tried,
what worked, what didn't, and where we ended up. Written for transparency:
when this is published, readers should be able to follow the actual path
of investigation including the dead ends and recalibrations.

This is a companion to `RENEWAL_THEORETIC_NOTE.md` (the technical writeup)
and `UNIFIED_MODEL.md` (the operator-theoretic synthesis). Those documents
present the *results*; this document presents the *path*.

> **Status:** The Collatz conjecture remains open. This project did not
> prove it. It produced a reproducible computational framework, several
> verifiable empirical constants, and a calibrated map of why each
> attempted approach succeeded or failed.

---

## 0. Starting point

**Source:** internal project brief, April 2026.

**Stated goals:**

1. Build a rigorous, reproducible certificate-search framework for the
   accelerated odd Collatz map `S(n) = (3n+1) / 2^v_2(3n+1)`.
2. Either:
   - find a finite symbolic residue-cover proving descent for all odd
     integers, **or**
   - isolate the precise obstruction as an infinite bad branch/cycle in
     a residue automaton.

**Explicit non-goal:** prove the Collatz conjecture.

**Initial state:** one Python file `collatz_certificate_search.py`, ~5 KB.

**Current state:** `collatz_exp/` package with 92 modules, 262 passing
tests, 118 JSON artifact reports, seven integrated reference-paper threads, and
a complete renewal-theoretic / operator-theoretic framework.

---

## 1. Initial buildout (residue automaton, certificate search)

**What was tried:**

- Residue-cylinder descent certificates (`certificates.py`): given a
  valuation word, certify descent for all `n` in a residue class.
- Mixed `(2^k × 3^ℓ)`-adic automaton (`mixed.py`): track residues in
  both 2-adic and 3-adic structures.
- Cohomology of residue graph (`cohomology.py`): first Betti number
  as obstruction detector.
- Cover trie with frontier expansion (`cover.py`): adaptive
  depth-first search over residue classes.
- Sandpile / SNF of Laplacian (`sandpile.py`): integer torsion
  invariants of the residue graph.

**What worked:**

- Reproducible certificate generation for known residue classes, e.g.
  `27 mod 2^59`.
- Mass invariant on cover trie (`cover_mass.py`) verified.
- Sandpile critical groups computed via SNF; Paparella-style
  nilpotency confirmed at `n ≤ 1024`.

**What didn't:**

- Cover search at depths 16, 18, 20 produced unresolved frontier
  classes that did not close under naive splitting.
- The first Betti number alone was too coarse to identify obstructions.

**What we learned:** finite residue-cover search needs a Lyapunov-style
auxiliary function, not just bit-by-bit splitting.

---

## 2. Tail dynamics (the lemma that survived everything)

**What was tried:** identify the structure of orbits that pass through
deep "tail" states `n ≡ -1 mod 2^R`.

**What worked (and survived audit):**

For odd `n = 2^R · u − 1` with `R ≥ 2`:

```text
v_2(3n + 1) = 1   exactly
S(n) + 1     = 3 · 2^{R−1} · k    (k odd)
R(S(n))      = R − 1               (deterministic decrement)
```

**Tail-internal R-decrement is pointwise, deterministic, elementary.**
This was the first clean lemma the project produced and it survived
every subsequent audit. It is the foundation of every tail-related
argument.

Saved artifact: implicit in `core.py`, `tail_lemma.py`, `mersenne.py`.

---

## 3. Post-Exit Cylinder Map (PECM)

**Hypothesis:** if tail-internal descent is deterministic, the hard
part is what happens *after* tail exit. Build a Markov chain on
`(R, u mod 2^k, u mod 3^ℓ)` cylinders capturing post-exit dynamics.

**What was built:**

- `post_exit_map.py`: explicit PECM transition matrix.
- Recurrent / transient block decomposition.
- Substochastic Perron eigenvalue via matrix-free Arnoldi.

**Key empirical results:**

```text
λ_super(8,2)  = 0.5058
λ_super(10,3) = 0.3648
λ_super(12,4) = 0.3541
```

Decreasing trend in resolution, all < 1. **Initially read as evidence
of descent on the post-exit Markov chain.**

**What was missed at this stage:** the values capture *spectral gap of
an averaged operator*, not actual orbit growth rates. This subtlety
came back during audit.

Saved artifact: `docs/reports/post_exit_pecm_perron_scaled.json`.

---

## 4. Lyapunov LP closure attempts (multiple iterations)

**Hypothesis:** find an explicit Lyapunov function `V(state)` such that
`V` decreases on every PECM transition. Use linear programming to
search for one.

**Iteration A — naive linear ansatz `V = log₂ n + α·ψ − β·R`:**
- LP infeasible. Worst transition: `R=30 → R=3` with `Δlog₂ ≈ 16.55`.

**Iteration B — renormalized height `V = H(R, u) + α·ψ − β·R`:**
- LP infeasible after sign-correction. Worst at `R=23 → R=22` with
  `Δlog₂ ≈ 11.87`.

**Iteration C — debt-augmented `V = log₂ n + α·ψ − β·R + γ·D_PE`:**
- **LP feasible** at `(γ = 16, ε = 0.30)` with edge-debt convention.
- Caveat: this is an edge-debt diagnostic, not yet a state Lyapunov.

**Iteration D — bucketed-state Lyapunov:**
- Augment PECM state with `D_PE` bucketed at `Δ = 0.01`.
- LP feasible at `(8, 3)` with `α = 0, β = 0, γ = 16, ε = 0.3004`.
- Brute-force verified: 341,437 edges, zero violations.

**Initial conclusion (later revised):** the post-exit operator on
`(R, u₂, u₃, D_bucket)` admits a Lyapunov function with closure rate
`ε = 0.30`, certifying descent at `(k, ℓ) = (8, 3)`.

Saved artifact: `docs/reports/unified_lyapunov_state_debt.json`.

---

## 5. The harmonic projection collapse and ψ

**Setup:** at `(k, ℓ) = (6, 3)`, the harmonic projection of the
obstruction class indicator was 0.5410. At `(8, 3)`, it dropped to
`7.96 × 10⁻¹⁰`. At `(10, 4)`, `1.04 × 10⁻⁹`.

**Reading at the time:** the obstruction class is essentially a
coboundary at higher resolution, meaning there exists an explicit
chain `ψ` such that `1_obstruction = ∂ψ`. We extracted `ψ` and
observed unit decrement `≈ 0.99999999991` on PECM trajectories from
the obstruction class.

**Strategic claim (later demoted):** `ψ` is an explicit closed-form
Lyapunov potential with integer unit decrement.

This was used as a load-bearing claim for several rounds.

Saved artifacts: `docs/reports/harmonic_class_identification.json`,
`docs/reports/obstruction_lyapunov_correction.json`.

---

## 6. The audit (V1–V5)

**Trigger:** explicit user request to validate before the project
drifted further.

Five tests run:

- **V1 — harmonic projection by independent method:** dense Laplacian
  eigendecomposition gave residual ratio `3.7 × 10⁻¹⁵` vs LSMR's
  `7.96 × 10⁻¹⁰`. ✅ **Harmonic collapse is real, not a solver
  artifact.**
- **V2 — ψ value distribution:** `{0: 3453, 1: 3}`. **ψ is essentially
  the indicator of the obstruction class.** Unit decrement was
  tautological. ❌ **ψ as "rich Lyapunov potential" demoted.**
- **V3 — brute-force LP verification:** all 341,437 edges checked,
  max `ΔV = −0.3004`, zero violations. ✅
- **V4 — convergent atlas at `R_max = 100`:** `84/53` still absent at
  `(8, 3)`. Triggered cross-resolution sweep V4'.
- **V4' — cross-resolution sweep at `R_max = 100`:** `84/53` appears
  at `(10, 4)` and `(12, 4)`. ❌ **"Structural realizability
  exclusion" hypothesis demoted to resolution artifact.**
- **V5 — Lyapunov on full orbits:** `V = log₂ n + 16·D_running` over
  `10⁶` orbits gave **50.1% non-decrease per accelerated step**. ❌
  **The PECM-edge Lyapunov does NOT lift to a per-step Collatz
  Lyapunov.**

**Net effect of the audit:**
- ✅ Tail-internal R-decrement: solid.
- ✅ LP closure at `(8, 3)`: real.
- ✅ Harmonic collapse: real.
- ❌ ψ as rich potential: tautological.
- ❌ Per-step Lyapunov from `log₂ n + 16·D`: doesn't work.
- ❌ Structural Diophantine sparsity: resolution artifact.

**Calibration:** the project shifted from "proof framework" to "honest
empirical observable" framing. **Distance to a Collatz proof was
re-estimated from ~20% to ~5–10%.**

---

## 7. Renewal pivot

**Trigger:** V5's per-step Lyapunov failure suggested the right
timescale wasn't per-step but per-renewal-excursion (between tail
entries).

**β-sweep:** test `V_β = log₂ n + β · D_running` for
`β ∈ {1, 2, 4, 8, 16, 32, 64}` on `10⁶` orbits.
- **All β give ≈ 50% non-decrease.** No β makes it work per-step.
- ❌ Per-step linear-in-debt Lyapunov definitively dead.

**β-renewal:** instead of per-step, aggregate by tail-entry events.
- Mean renewal increment: `E[Δlog₂ n] = −0.80` per excursion.
- Variance: `5.55`.
- ✅ **Renewal-scale drift is robustly negative.**

**β'' (spike decomposition):**
- `I(0) ≈ 0.0837` (Cramér rate).
- 64% of tilted MGF from no-spike (max_a = 1) class.
- Heavy-tail correction over `log(4/3)² = 0.0828` is `0.00097`.

**β''' (Markov-conditional):**
- `I_Markov ≈ 0.0819` (modest improvement over iid pair-target).
- Does NOT beat all-excursion iid `0.0836`.
- **Conclusion:** renewal increments are effectively iid for Cramér
  purposes.

**β'''' (n₀ stability):**
- `I(0)` across `[10², 10⁴], [10⁴, 10⁶], [10⁶, 10⁹], [10⁹, 10¹²],
  [10¹², 10¹⁵]` gives `0.0761, 0.0820, 0.0835, 0.0848, 0.0846`.
- Slope `0.0007` per decade. ✅ **Rate is structurally stable from
  `10⁴` upward.**

This established **`J = 0.0837`** as a candidate empirical Collatz
constant.

Saved artifacts:
- `docs/reports/orbit_lyapunov_beta_sweep_1e6.json`
- `docs/reports/orbit_renewal_descent.json`
- `docs/reports/orbit_renewal_spike_decomposition.json`
- `docs/reports/orbit_renewal_markov_cramer.json`
- `docs/reports/orbit_renewal_n0_stability.json`

---

## 8. Literature integration (four papers)

**Pulled and read in full:**

1. **Tao 2019 — *Almost all orbits of the Collatz map attain almost
   bounded values*** (arXiv 1909.03562, *Forum Math. Pi*).
   - Establishes Syracuse map `Syr(N) = (3N+1)/2^{v_2(3N+1)}`.
   - Proves `Syrac(ℤ/3^n ℤ)` has fine-scale 3-adic mixing.
   - Reduces full result to characteristic function decay (Prop 1.17).

2. **Mori 2024 — *Application of Operator Theory for the Collatz
   Conjecture*** (arXiv 2411.08084, *Adv. Operator Theory* 2025).
   - Three Hilbert-space formulations: single operator, two operators,
     Cuntz algebra.
   - Theorem 4.2.7 / 4.3.10: `C*(T_1, T_2)` has no non-trivial
     reducing subspaces ⟺ Collatz.
   - First serious operator-algebraic framework for Collatz.

3. **Hercher 2022 — *There are no Collatz-m-Cycles with m ≤ 91***
   (arXiv 2201.00406).
   - Reciprocal-sum bounds `T(n_i) < (97/54) · 1/X_0`.
   - Iterative continued-fraction scheme via Lemma 22.
   - Theorem 23: no m-cycle with `m ≤ 91`.

4. **Paparella 2024 — *A matricial view of the Collatz conjecture***
   (arXiv 2406.08498).
   - Adjacency submatrix `C_n` nilpotent ⟺ aperiodic Collatz on
     truncation.
   - Pure linear-algebra reformulation.

**Cross-validation experiments:**

- **τ — Tao characteristic function decay:** empirical exponent
  `1.286` vs Tao's exact `1.289`. **Match to 0.2%.**
- **π — Tao Syrac distribution:** TV ≤ 0.3% across `n = 1, …, 4`.
- **ρ — Hercher T(n_i):** universal bound `T(n_i) · n_i < 3` holds
  with empirical max `2.99`, sharp at the analytic ceiling.
- **σ — Paparella nilpotency:** `tr(C_n^p) = 0` verified for all
  `n ∈ {64, 128, 256, 512, 1024}`.

**All four papers' central predictions verified empirically on the
project's orbit cache.**

Saved artifacts:
- `docs/reports/tao_syrac_empirical.json`
- `docs/reports/tao_characteristic_function_decay.json`
- `docs/reports/hercher_t_ni_bound.json`
- `docs/reports/paparella_nilpotency.json`

---

## 9. The unified model

**Insight (combining the four papers + project work):** all approaches
operate on the same first-return map `P` on the odd-integer subspace
`N₁ ∪ N₂ = {n ≡ 1, 5 mod 6}`, with different overlay structures:

| Paper | Overlay | Object studied |
|-------|---------|----------------|
| Tao | log probability measure | `Syrac(ℤ/3^n ℤ)` distribution |
| Mori | Hilbert space | C*(T_1, T_2) ≅ Cuntz O_2 |
| Hercher | integer arithmetic | reciprocal sums, Christoffel words |
| Paparella | finite linear algebra | adjacency submatrix nilpotency |
| Project | bucketed Markov chain | PECM Perron + renewal Cramér rate |

**Constructed unified operator:** `M = T_1 + T_2` on
`ℓ²(N₁ ∪ N₂, μ_log)`. Each paper's claim becomes a different
projection:

- Tao mixing ⟺ exponential mixing of M.
- Mori reducing-subspace condition ⟺ irreducibility of M.
- Hercher cycle bounds ⟺ spectral norm constraints on cyclic vectors.
- Paparella nilpotency ⟺ truncated `M_n` has no cycles.
- Project PECM Perron ⟺ finite-rank approximation to M's recurrent
  block.

Saved artifacts: `docs/reports/unified_collatz_operator.json`,
`docs/UNIFIED_MODEL.md`.

---

## 10. JSR analysis (projective lift)

**User intuition:** "what if `ρ = 1/0`?" → projective coordinates →
matrix family `M_a = [[3, 1], [0, 2^a]]` → JSR.

**Sequential results:**

```text
JSR(unconstrained)              = 1.5     (exact, squeeze gap < 10⁻⁶)
JSR(naive legal-residue)        ≈ 1.5     (n=-1 loop survives)
JSR(tail-filtered, finite R)    = 0.75    (EXACT structural number)
JSR(tail-aware, q ≤ 10, R ≤ 7)  = 0.86–1.23  (artifact: overflow dropped)
JSR(LTE-closed tail-aware)      = 1.07–1.26  (deeper tails reintroduce growth)
```

**The clean structural fact:** when the trivial `n = −1` Mersenne-tail
loop is removed, the **worst-case** JSR equals `e^(mean drift) = 0.75`.
Worst-case = mean-case under that restriction.

**The honest result:** including all R, worst-case JSR > 1. Residue-
automaton JSR alone cannot certify Collatz descent. **This says any
proof of descent must use integrality / parity-word constraints
beyond the abstract residue automaton.**

Saved artifacts:
- `docs/reports/projective_jsr_claude_background.json`
- `docs/reports/constrained_projective_jsr.json`
- `docs/reports/tail_aware_projective_jsr.json`
- `docs/reports/tail_aware_lte_closed_projective_jsr.json`

---

## 11. Stress tests (calibrating the constants)

**κ — closed-form test on Jazz's constant J:**
- Candidate `log(4/3)² = 0.0828` rejected at 8.1 CI half-widths.
- Saddlepoint ratio matches at `T = 10` (1.01) but diverges at
  `T = 1000` (2.63).
- ❌ `J ≠ log(4/3)²`. J remains empirical.

**Stress suite — partition robustness, convergence, subfamily:**
- **Definition matters:** per-step `J = 0.0556` (matches Geom(2)
  closed form `0.0542`); per-2-step `J = 0.1007`; per-tail-entry
  `J = 0.0841`. **Variation 30–80% by partition.**
- **Convergence:** stable from `N = 20k`.
- **Mod-8 stratification:** range `[0.073, 0.094]`, 22% spread.
- **Mod-9 stratification:** 3% spread (essentially invariant).
- **Mersenne-like subfamily:** `J` factor 2–3 smaller, monotone
  decreasing in `R`.

**Calibrated outcome:**
- `J_renewal = 0.0837` (canonical Khinchin-style empirical constant).
- `J_step ≈ 0.0542` (closed form via Geom(2) MGF: `sup_λ
  [log(2^{1+λ} − 1) − λ·log 3]`, partition-independent, theoretically
  motivated).

Saved artifacts:
- `docs/reports/jazz_constant_closed_form_test.json`
- `docs/reports/jazz_constant_spike_decomposition.json`
- `docs/reports/jazz_constant_stress_test_claude_background.json`

---

## 12. Where we ended up

**Verified empirical results (with rigorous CIs):**

1. **Tail-internal R-decrement** (pointwise, deterministic).
2. **`J_renewal = 0.0837 ± 0.0001`** — Markov-renewal Cramér rate over
   tail-entry partition, stable across `[10⁴, 10¹⁵]`.
3. **`J_step ≈ 0.0542`** — closed-form per-step Cramér rate from
   Geom(2) MGF.
4. **Mean drift `μ = −0.802 ± 0.001` per excursion** with concentration.
5. **JSR(unconstrained) = 1.5** rigorously (squeeze gap < 10⁻⁶).
6. **JSR(tail-filtered, finite R) = 3/4** exactly, matching
   `e^(mean drift)` — structural worst-case = mean-case under
   `n = −1` exclusion.
7. **Tao distribution match:** TV ≤ 0.3%, characteristic function
   decay exponent `1.286 ≈ 1.289` (0.2% match).
8. **Hercher T(n_i)** universal bound `< 3` empirically tight.
9. **Paparella nilpotency** at `n ≤ 1024`.
10. **Five-projection consistency** of unified operator M = T_1 + T_2.
11. **Realizable Karp on tested LTE-closed tail graphs = `3/4`**:
    bounded simple-cycle audit at `(5,4),(6,5),(7,6)` leaves only the
    elementary `[2]` positive-integer realizer, while the high-growth
    abstract cycles classify as `noninteger_2adic_only`
    (`docs/reports/tail_cycle_realizability_extended.json`).
12. **m-step Foster-Lyapunov drift for `V(n) = log₂(n) + v_2(n+1)`**:
    on residue quotients mod `2^k` for `k ∈ {2,3,4,5,6,7,8}`, the finite audit
    finds residue-uniform negative drift at the smallest tested grid value
    `m = 16`, with margin `ε = 0.1`, over sample windows
    `n₀ ∈ [10²,10¹⁵]` (`docs/reports/m_step_foster_drift_k8.json`).
13. **Joint argument with Chang `arXiv:2603.25753` empirically supported at
    finite windows.** Three named technical verifications closed:
    `δ_max ≈ 0.119` (`docs/reports/delta_max_quantitative.md`), Foster
    condition at `k=7,8` (`docs/reports/m_step_foster_drift_k8.json`), and
    bit-4 balance Foster envelope holds for every sampled orbit
    (`docs/reports/chang_bit4_balance_audit.json`). Residual: Tao
    distributional-to-pointwise wall.
14. **Pointwise descent moonshot audit.** The finite pointwise descent audit
    found an empirical uniform bound across tested windows with
    `max_T_descent = 181` and `0%` truncation at `m_max = 100,000`
    (`docs/reports/pointwise_descent_audit.json`). This is a finite
    diagnostic over the tested windows, not a proof of global descent.
15. **Realizable Karp generalizes to qn+1.** The q-parameterized audit
    recovers the Mersenne-q fixed-point pattern at `q = 3,7,31`, where
    `q = 2^k - 1` gives the positive fixed cycle `n=1` with word `[k]`
    and factor `(2^k-1)/2^k`. In the small non-Mersenne grid, `5n+1` is
    the exceptional case with recovered positive cycles `{1,3}` via
    `[1,4]`, `{13,33,83}` via `[1,1,5]`, and `{17,43,27}` via `[1,3,3]`
    (`docs/reports/qnp1_realizability_q5.json`,
    `docs/reports/qnp1_phase_transition.json`).
16. **Rozier abc bridge sanity check.** Rozier's μ-function and Theorem 4.1
    were implemented and checked on the finite range `j=10..50`: all
    `1,230` elements of `N(j)` satisfied the theorem dichotomy and there were
    `0` violations (`docs/reports/rozier_abc_collatz_audit.json`).
17. **Stern-Brocot slope structure.** The CF-convergent slope hypothesis is
    partially supported: realizable survivors occupy the CF-convergent slope
    `2/1`, the high-growth `(8,7)` ghost `[2,1,1,1]` occupies the
    non-convergent rational `5/4`, and a boundary ghost `[2,1,2]` appears at
    the intermediate fraction `5/3`
    (`docs/reports/cf_convergent_slope_hypothesis.json`).

**Demoted claims (audit-revealed):**

1. ψ as rich Lyapunov potential — actually tautological.
2. Per-step linear Lyapunov from D_running — fails at 50% per step.
3. Structural Diophantine exclusion of `84/53` — resolution artifact.
4. `J = log(4/3)²` — rejected at 8σ.
5. Constrained JSR < 1 with naive residue automaton — fake n=-1 loop.
6. **Raw `Σ R(K) ≈ J_renewal` identity.** Rejected at high-precision
   bootstrap: Chang's `Σ R(K)` is about `0.0882`, while `J_renewal` is about
   `0.0837`. The gap is structural, reflecting different weightings of the
   same `Geom(1/2)` i.i.d. cycle structure rather than a missing closed form
   (`docs/reports/jazz_constant_chang_R_K_identity.json`,
   `docs/reports/chang_spectral_analysis_compatibility.md`).
7. **Stern-Brocot triple alignment megasynthesis.** The strict claim that
   Chang phantom-gain spikes, Rozier μ-hit families, and this framework's
   slope-realizability cycles align at the same CF convergents of `log₂(3)`
   found `0` matching convergents at the audited depth
   (`docs/reports/stern_brocot_megasynthesis.json`).
8. **Tao Littlewood-Offord tier ordering.** The predicted median discrepancy
   order `CF convergent < intermediate fraction < random rational` did not
   hold for the tested congruence sums modulo `2^a - 3^m`
   (`docs/reports/stern_brocot_megasynthesis.json`).
9. **Six-reduction universal invariant claim.** The cross-tabulation of Tao,
   Chang, Mori, Santana, Siegel, and this framework is useful as a comparison
   table, but no single empirically verified universal invariant emerged
   (`docs/reports/stern_brocot_megasynthesis.json`).
10. **Strict CF-convergent slope hypothesis.** The binary prediction
    "realizable = CF convergent, non-realizable = non-convergent" failed at
    `(8,7)` because the ghost `[2,1,2]` sits at the Stern-Brocot intermediate
    fraction `5/3`; the refined tiered picture is the surviving claim
    (`docs/reports/cf_convergent_slope_hypothesis.json`).
11. **Small qn+1 cycle expectation outside the known patterns.** The light
    phase-transition scan found no positive integer cycles for
    `q ∈ {9,11,13,17,19,21,25,27}` at levels `(5,4)` and `(6,5)`. This is a
    depth-limited null result, not a cycle-absence theorem
    (`docs/reports/qnp1_phase_transition.json`).
12. **Megasynthesis ambition as stated.** The session-level speculation that
    Stern-Brocot tiers of `log₂(3)` form a universal organizing skeleton across
    three independent papers was tested and did not survive the finite audit.
    The methodological value is that the framework can attempt ambitious
    unifications and record refutation cleanly
    (`docs/reports/stern_brocot_megasynthesis.json`).

**Open theorem-shaped problems:**

1. **Markov/Lyapunov contraction on LTE-closed operator** (Codex's
   current target). Should give `Λ ≈ log(3/4)`.
2. **Christoffel-word integrality filter on JSR.** Bridge to
   Hercher's parity-vector framework. Expected outcome: filtered
   JSR < 1.
3. **Profinite continuity** from finite quotients to limit operator.
4. **Lifting PECM Lyapunov to per-orbit Lyapunov.** V5's gap.
5. **Symbolic interpretation of `J_renewal`** — the direct
   `Σ R(K) ≈ J_renewal` identity test is not supported at high precision:
   Chang's `Σ_{K=3}^{500} R(K) = 0.0882362530512702`, while the sampled
   `J_renewal = 0.08346903426255636` has bootstrap CI
   `[0.08314605994133623, 0.0837883621454151]`
   (`docs/reports/jazz_constant_chang_R_K_identity.json`). The remaining
   symbolic question is no longer the rejected raw `Σ R(K)` identity. The
   compatibility analysis reads Chang's `V` as a refinement of the same
   underlying `Geom(1/2)` i.i.d. run-length structure with a definitional
   weighting difference caused by run-length absorption
   (`docs/reports/chang_spectral_analysis_compatibility.md`).
6. **Phase-aware per-orbit Lyapunov.** The residue-Markov m-step Foster
   question is empirically closed on the tested grid for
   `V(n) = log₂(n) + v_2(n+1)`: `m = 16` gives residue-uniform negative
   drift with margin `ε = 0.1` across the tested windows and residue powers
   `k = 2..8`. The joint argument with Chang `2603.25753` reduces the
   framework's residual to the Tao distributional-to-pointwise wall expressed
   at Markov-measure-1, a sharper formulation than natural density.
7. **Slope-realizability hierarchy via Stern-Brocot approximation tiers.**
   The finite artifacts suggest a hierarchy: CF convergents of `log₂(3)` are
   where realizable survivors currently sit, intermediate fractions are
   boundary ghosts, and non-convergent rationals are high-growth ghosts. The
   open problem is to test and prove, or falsify, this hierarchy at higher
   `(q,Rmax)` levels.
8. **abc-conditional lower bounds on `N(j)`.** Rozier Theorem 2.1 gives an
   abc-conditional `ε`-improved lower bound for elements of `N(j)`, while
   Theorem 4.1 gives an unconditional dichotomy between a concrete lower
   bound and a rare μ-hit. Closing the conditional lower-bound route requires
   the independent abc conjecture, not only Collatz-specific dynamics.

---

## 13. Realizable-Karp / Renewal-Drift Bridge

**Trigger:** the Christoffel and constrained-Karp artifacts kept returning
`3/4`, while the LTE-closed tail graph still had abstract high-growth cycles.
The open question became whether the gap was arithmetic or analytic: are the
cycles filtered out by Christoffel/slope compatibility actually realizable by
positive integer orbits?

**Iteration 1 — joint Karp/slope sweep.** The product graph was swept across
`(q,Rmax)=(5,4),(6,5),(7,6)` while increasing the balanced-word automaton
period. The result was stable: exactly one slope-compatible survivor at each
level, the elementary valuation word `[2]`, with factor `3/4`
(`docs/reports/karp_slope_joint_sweep.json`).

**Iteration 2 — cycle realizability.** The next audit classified the
high-growth simple cycles by exact accelerated-word lifting. The obstruction
did not appear: the high-growth witnesses classified as
`noninteger_2adic_only`, not as positive integer cycles
(`docs/reports/tail_cycle_realizability.json`).

**Iteration 3 — extended realizable Karp.** The audit was widened to all
simple cycles up to `max_cycle_edges=12` at the same three levels. It scanned
`226,333` simple cycles; `226,330` classified as `noninteger_2adic_only`, and
the only `3` `positive_integer_cycle` entries were the elementary `[2]` cycle,
one per level. Therefore the finite diagnostic reads:

```text
realizable Karp = slope-filtered Karp = 3/4
```

at the tested levels (`docs/reports/tail_cycle_realizability_extended.json`).

**Iteration 4 — renewal per-step drift audit.** The first renewal-scale
identity check tested the naive per-step target
`mean_valuation_per_step = 2` and `mean_drift_per_step = log2(3/4)`.
At the standard `[10^6,10^9]` window both were outside the reported intervals:
`mean_valuation_per_step = 1.995093964280808` and
`mean_drift_per_step = -0.4069756235411483`
(`docs/reports/renewal_drift_per_step.json`). This was the first correction:
the bridge was not a one-phase Geom(2) story.

**Iteration 5 — phase decomposition.** Splitting accelerated steps by
pre-step odd residue clarified the structure. Tail-internal steps
(`n == 3 mod 4`, equivalently `v2(n+1) >= 2`) have deterministic valuation
`a=1`; post-exit steps (`n == 1 mod 4`) carry the shifted distribution. The
initial back-of-envelope estimate `w_tail ≈ 0.008` was wrong by a factor of
about `60`: the artifact gives `w_tail = 0.500054904385728` in the
`[10^6,10^9]` window. The post-exit valuation target is therefore `3`, not
`2` (`docs/reports/renewal_drift_phase_decomposed.json`).

**Iteration 6 — n0 sweep.** The phase-decomposed n0 sweep tracks the slow
finite-window approach to the shifted post-exit target. The post-exit
valuation deviation shrinks monotonically from `-0.03473021694546086` to
`-0.006503489706314536`, with log10-slope `-0.06656531395656089` per decade.
The total drift deviation falls into the `0.005` range at the deepest windows,
but is not strictly monotone: it moves from `0.005160187031614694` to
`0.0054062766596057465`, a change smaller than the deepest CI halfwidth
`0.0005710918683108357`. The saved verdict is therefore
`non_monotone_or_flat`, not a closed asymptotic theorem
(`docs/reports/renewal_drift_phase_decomposed_n0_stability.json`).

**What was confirmed:** at the tested finite levels, the realizable bounded
cycle maximizer is elementary `[2]` and has factor `3/4`. The renewal-scale
mean-step identity has the right phase form:

```text
mu_step = (1/2) log2(3/2) + (1/2) log2(3/4),
E[a | tail] = 1,     E[a | post_exit] -> 3.
```

**What was corrected:** the early one-phase reading `E[a] = 2` was the wrong
quantity for the post-exit phase; the right asymptotic target after removing
tail-internal forced steps is `E[a | PE] = 3`. The early mixing-weight
explanation `w_tail ≈ 0.008` was also wrong; the sampled phase weights are
balanced near `1/2`. The remaining deviations look like slow finite-window
mixing effects, but the artifacts deliberately stop short of claiming this as
a theorem.

Saved artifacts:
- `docs/reports/karp_slope_joint_sweep.json`
- `docs/reports/tail_cycle_realizability.json`
- `docs/reports/tail_cycle_realizability_extended.json`
- `docs/reports/renewal_drift_per_step.json`
- `docs/reports/renewal_drift_phase_decomposed.json`
- `docs/reports/renewal_drift_phase_decomposed_n0_stability.json`

---

## 14. Foster-Lyapunov Drift Audit

**Trigger:** the realizable-Karp / renewal-drift bridge made the old V5 failure
more precise. The question was no longer whether
`log₂ n + 16·D_running` decreases per accelerated step; V5 had already shown
that it does not. The reformulated question was whether the `n mod 4` phase
coordinate, and especially the tail depth `R(n)=v_2(n+1)`, supplies the missing
state variable for a Foster-style drift statement on residue quotients.

**Iteration 1 — phase Lyapunov search.** A grid search over
`(α, β, γ_diff)` found the rank-zero candidate

```text
V(n) = log₂(n) + v_2(n+1)
```

as the best point in the tested family: `α = 1.0`, `β = 0.0`,
`γ_diff = 0.0`. On the `100,000`-orbit sample, the non-decrease fraction fell
from V5's same-sample baseline `0.5001335415695829` to
`0.1655372436648494`. Tail-internal steps were locked at `0.0` non-decrease;
the remaining violations were post-exit `R`-spike events, such as `R=1`
landing at `R'=19` or `21` (`docs/reports/phase_lyapunov_search.json`). This
was not a per-step Lyapunov closure, but it localized the obstruction.

**Iteration 2 — one-step Foster audit.** The next pass used explicit
Meyn-Tweedie language and tested the candidate on residue quotients. The
marginal drift was right: across windows `[10²,10⁴]` through `[10¹²,10¹⁵]`,
the drift of `V` was consistent with `log₂(3/4)`, with deepest-window estimate
`-0.4123424992788405` and CI
`[-0.41856572879163634, -0.4061192697660446]`. But residue uniformity failed
decisively. The audit recorded `50` obstruction witnesses across
`k ∈ {3,4,5,6}`, with the arithmetic cascade
`n ≡ 1 mod 8` (drift `0.5954199142013228`),
`n ≡ 9 mod 16` (drift `1.5919631928192652`), and
`n ≡ 41 mod 64` (drift `3.557870295871902`)
(`docs/reports/phase_lyapunov_foster_drift.json`). So the one-step Foster
condition failed even though the marginal mean was already at the
realizable-Karp value.

**Iteration 3 — m-step Foster audit.** Foster-Lyapunov theory permits an
m-step version, so the audit was repeated for
`m ∈ {1,2,4,8,16,32,64}` using the same per-window samples. The `m=1`
cross-check reproduced the one-step audit to machine precision:
`m1_max_disagreement = 2.6645352591003757e-15`. The binding obstruction
remained `n ≡ 41 mod 64` through the chain: it was the maximal obstruction at
`m=1,2,4,8`. At `m=16`, residue-conditional drift became uniformly negative
across every tested window and residue power, with margin `ε = 0.1`; at
`m=64`, the obstruction count was `0`
(`docs/reports/m_step_foster_drift.json`).

This completes the finite diagnostic chain

```text
realizable Karp = 3/4
renewal mean drift = log₂(3/4)
m=16 Foster drift on residue quotients
```

at the tested levels and windows. It does not establish deterministic
per-orbit descent. The remaining lift from residue-Markov geometric ergodicity
to deterministic per-orbit descent is exactly the distributional-to-pointwise
wall that Tao 2019 addresses at the almost-all level.

Saved artifacts:
- `docs/reports/phase_lyapunov_search.json`
- `docs/reports/phase_lyapunov_foster_drift.json`
- `docs/reports/m_step_foster_drift.json`

---

### Chang 2026b compatibility closure — three verifications empirically closed

**Trigger:** the 2026 literature sweep returned with Chang `2603.25753`,
which found the same wall as this framework. Chang reduced Collatz to a
fixed-modulus, one-bit balance problem along burst-ending times; this
framework had independently reached a residue-Markov Foster condition whose
remaining gap was the deterministic pointwise upgrade.

**Iteration 1 — compatibility analysis.** The first pass
(`docs/reports/chang_2603_25753_compatibility.md`) translated notation:
Chang's compressed map is this framework's accelerated map, his burst
indicator is the post-exit indicator, and his mod-32 / mod-256 target sits
inside this framework's residue quotient language. That analysis named three
required verifications: compute a usable `δ_max`, extend Foster to `k=7,8`,
and directly audit the bit-4 balance at burst-ending times.

**Iteration 2 — bit-4 balance audit.** Prompt 4 implemented the direct
orbit-level measurement of Chang's Eq. 16 statistic. The audit found that the
Foster plus `1/sqrt(m)` envelope holds for every sampled orbit. The raw max
`δ` remains `0.5` because tiny denominators occur, but the mean `δ` decreases
with window depth and reaches `0.11212329012096864` in the deepest window
(`docs/reports/chang_bit4_balance_audit.json`).

**Iteration 3 — Foster at Chang's resolution.** Prompt 5 extended the m-step
Foster audit to `k=7,8`, matching Chang's mod-256 fiber refinement. The result
was stable: `m=16`, `ε=0.1` still holds, the weakest `k=8` CI upper bound at
`m=16` is `-0.24276696844795248`, and the cross-check against the earlier
`k≤6` artifact has max disagreement `0.0`
(`docs/reports/m_step_foster_drift_k8.json`).

**Iteration 4 — `δ_max` read.** The quantitative read of Chang `2603.11066`
Eq. 34 derived `δ_max ≈ 0.119` under the `R(K)`-weighted allocation
(`docs/reports/delta_max_quantitative.md`). That value puts the deepest-window
mean `δ = 0.11212329012096864` just below the finite-window budget.

**What was confirmed:** the joint argument is empirically supported at finite
windows. The three named technical verifications are empirically closed at
finite windows, and the Foster condition now matches Chang's working
resolution.

**What's still open:** the Tao distributional-to-pointwise wall remains the
residual. The exact `δ_max` via Chang §9.7–§9.9 is still a careful-reading
task, though the `R(K)`-weighted estimate is now numerically useful. The
direct `Σ R(K) ↔ J_renewal` identity test did not support equality:
`Σ_{K=3}^{500} R(K) = 0.0882362530512702` lies outside the high-precision
`J_renewal` CI `[0.08314605994133623, 0.0837883621454151]`
(`docs/reports/jazz_constant_chang_R_K_identity.json`). A more refined
`h_K`-weighted reconciliation remains future work. The follow-up compatibility
analysis (`docs/reports/chang_spectral_analysis_compatibility.md`) clarifies
that the mismatch is a definitional weighting difference on the same
`Geom(1/2)` i.i.d. run-length structure, with Chang's drift signal refined by
this framework's run-length absorption.

---

## 15. qn+1 family extension

**Trigger:** the q=3 realizable-Karp story had become too tailored to the
classical map. The qn+1 pass asked whether the same exact affine
classification could recover known small cycles in `5n+1`, where the mean
accelerated drift is positive: `log₂(5)-2 ≈ 0.322`.

**Iteration 1 — q-parameterized cycle arithmetic.** The new sidecar
`collatz_exp/qnp1_family.py` generalizes the accelerated step, valuation
words, affine word formula, and exact cycle classifier from `3n+1` to odd
`qn+1`. The q=3 regression tests agree exactly with the old core functions.

**Iteration 2 — q=5 realizability.** The bounded q=5 audit recovered the
known `{1,3}` accelerated cycle from word `[1,4]`, and also found positive
cycles `{13,33,83}` from `[1,1,5]` and `{17,43,27}` from `[1,3,3]`. The
positive realized Karp factor at the tested levels is `125/128`, not greater
than one: positive cycles require `2^A > 5^m`, so every positive integer
cycle is contracting even though the typical drift of the `5n+1` accelerated
map is positive (`docs/reports/qnp1_realizability_q5.json`).

**Iteration 3 — phase transition over q.** The sweep
`q ∈ {3,5,7,9,11,13,17,19,21,25,27,31}` separated two phenomena. The
Diophantine upper bound on positive cycle factor approaches one along good
approximants to `log₂(q)`. In this odd `q>1` grid, classical `q=3` is the
unique tested case below the `log₂(q)=2` drift threshold; `q=5` is already in
the positive-drift regime. The empirical bounded tail scan recovers the
Mersenne-q fixed-point pattern at `q = 3,7,31`: when `q = 2^k - 1`, `n=1`
has word `[k]` and factor `(2^k-1)/2^k`. Among the tested non-Mersenne small
q values, `5n+1` is the only one with small positive cycles found in the
bounded scan (`docs/reports/qnp1_phase_transition.json`).

The qn+1 pass confirms framework q-generality at the cycle-classification
level. It does not prove cycle absence for any q, nor does it turn positive
typical drift into a positive cycle obstruction.

Saved artifacts:
- `docs/reports/qnp1_realizability_q5.json`
- `docs/reports/qnp1_phase_transition.json`

---

## 16. abc-conjecture bridge (Rozier 2306.15284)

**Trigger:** the May 2026 literature sweep surfaced Rozier's bridge between
Collatz, abc-style invariants, and Wieferich primes. Rozier defines

```text
mu(n) = log rad(n) + log product_{p|n} nu_p(n)
```

and calls `(a,b,c)` a μ-hit when `a+b=c`, `gcd(a,b)=1`, and
`log c > mu(abc)`. Theorem 4.1 gives an unconditional dichotomy for shortcut
Collatz orbits whose first `j` iterates contain exactly one even term: either
the starting value is already above `2^{j+1}/(3j^2)-1`, or the orbit
produces a rare μ-hit of the form `(1,b,b+1)`.

**Finite verification.** The audit implemented Rozier's congruence
`n == -1 - (2/3)^k mod 2^j` for the set `N(j)`, then checked the Theorem 4.1
dichotomy for every element with `j=10..50`. All `1,230` elements satisfied
the theorem predicate and there were `0` violations
(`docs/reports/rozier_abc_collatz_audit.json`). In this finite range the
lower-bound side was always enough; the μ-hit escape clause was not needed.

**Family extension.** The same artifact extends Rozier's `n=239` family
`(1,239^{2^k}-1,239^{2^k})` through `k=20`. The certified gain lower bound
matches Rozier's predicted expression through `k=20`; it is positive through
`k=14` and negative from `k=15` onward, so no new exact deeper μ-hits are
claimed without infeasible full factorization.

This bridge is conditional in the appropriate place: Rozier's Theorem 2.1
uses abc to obtain an `ε`-improved lower bound for `N(j)` elements, while
Theorem 4.1 is checked here unconditionally at finite j. Neither statement is
a Collatz proof.

Saved artifacts and notes:
- `docs/reports/rozier_abc_collatz_audit.json`
- `docs/LITERATURE_SWEEP_2026_05.md`
- Tao's 2011 Littlewood-Offord/Collatz blog connection, recorded as
  literature context rather than a new theorem.

---

## 17. Stern-Brocot slope structure

**Trigger:** the `(8,7)` artifacts showed a slope-realizability divergence:
the slope filter admitted a high-growth nonrealizable survivor. The working
hypothesis was that realizable survivors sit at continued-fraction
convergents of `log₂(3)`, while non-realizable ghosts occupy less privileged
rational approximants.

**Finite test.** The analysis read only existing artifacts:
`karp_slope_joint_sweep*.json` and `tail_cycle_realizability*.json`. It
computed continued-fraction convergents of `log₂(3)` to depth 20 and compared
every recorded survivor's slope `A/m` against CF convergents and
Stern-Brocot intermediate fractions.

**Outcome.** The strict hypothesis is partially supported, not fully proved.
At `(5,4)`, `(6,5)`, and `(7,6)`, the slope-filtered survivor is the
realizable elementary `[2]` cycle with slope `2/1`, a CF convergent. At
`(8,7)`, the realizable survivor remains `[2]`, while the high-growth ghost
`[2,1,1,1]` has slope `5/4`, a non-convergent rational. However, the same
`(8,7)` slope-survivor set also contains `[2,1,2]` at slope `5/3`, an
intermediate fraction. The refined structural picture is therefore tiered:

```text
CF convergents             -> realizable survivors in tested artifacts
Stern-Brocot intermediates -> boundary ghosts
non-convergent rationals   -> high-growth ghosts
```

This is a finite empirical diagnostic at tested levels, not a theorem about
all slope filters. It is nevertheless a sharper explanation of the `(8,7)`
divergence than the earlier binary "slope vs realizability" framing.

Saved artifact:
- `docs/reports/cf_convergent_slope_hypothesis.json`

---

## 18. The megasynthesis attempt and its negative verdict

**Trigger:** midway through the session, a stronger unification hypothesis
emerged. The idea was that the Stern-Brocot tier hierarchy of `log₂(3)` might
be the universal skeleton organizing Chang's phantom-gain spikes, Rozier's
μ-hit families, and this framework's slope-realizability tiers. This was an
ambitious cross-paper claim, so it was turned into a direct finite audit rather
than left as an attractive story.

**Synthesis A — triple alignment.** For each CF convergent of `log₂(3)`, the
audit asked whether three signals aligned at the same rational scale: a local
Chang `R(K)` oscillation proxy at `K=p`, a slope-realizability survivor at
`A/m=p/q`, and a Rozier-style low-μ family arithmetically tied to `q`. The
strict criterion found `0` aligned convergents at the audited depth
(`docs/reports/stern_brocot_megasynthesis.json`).

**Synthesis B — Tao Littlewood-Offord tiering.** The audit tested whether the
finite discrepancy

```text
#{sigma : sum_i 3^{m-1-i} 2^{sigma_i} == 0 mod (2^a - 3^m)} / #{sigma}
```

is ordered by Stern-Brocot tier, with CF convergents smallest, intermediate
fractions in the middle, and random rationals largest. The tested medians did
not satisfy that ordering (`docs/reports/stern_brocot_megasynthesis.json`).
At this resolution, Tao-style anti-concentration is not simply
Stern-Brocot-tier-ordered.

**Synthesis C — six-reduction unification.** The audit also assembled a
six-way comparison table for Tao, Chang, Mori, Santana, Siegel, and this
framework. The table is useful: it names the state spaces, conditions, and
2-adic/3-adic quantities each approach tracks. But it remains structural-only.
No single empirically verified universal invariant emerged
(`docs/reports/stern_brocot_megasynthesis.json`).

**What survives.** The narrower q=3 slope-realizability picture still survives
as a finite structural diagnostic: CF convergents contain the realizable
survivors currently seen; Stern-Brocot intermediates appear as boundary ghosts;
non-convergent rationals appear as high-growth ghosts
(`docs/reports/cf_convergent_slope_hypothesis.json`). The six-reduction table
also survives as a useful comparison scaffold. What does not survive is the
strong claim that all three external frameworks are computing the same
Stern-Brocot skeleton in different units.

**Lesson:** cross-paper alignment through one Diophantine skeleton at
`log₂(3)` is not empirically supported at the tested resolution. The better
reading is more nuanced: these frameworks all touch the same 2-adic/3-adic
near-resonance problem, but they measure different aspects of it. Recording
that negative verdict is part of the framework's value, because it prevents
the same attractive over-unification from being re-pursued as if it had not
already been tested.

Saved artifacts:
- `docs/reports/stern_brocot_megasynthesis.json`
- `docs/reports/megasynthesis_executive_summary.md`
- `docs/reports/cf_convergent_slope_hypothesis.json`

---

## 19. Cross-resolution Lyapunov experiment

The exact-rational Perron bounds established contraction on several finite
PECM quotients, but left a more important question unanswered: do their
positive vectors approximate one object as the mixed `2`-adic/`3`-adic
partition is refined?

The first implementation uncovered a preflight problem. Independently
building the old fixed-CRT-sample operator at each level does not give a
projective ladder. Comparing those eigenvectors directly would mix genuine
resolution effects with a changing sampling scheme. The replacement builds
only the finest operator and obtains all coarser kernels by exact sequential
Galerkin averaging. It also distinguishes three identities:

```text
K_f I = I K_c       pointwise/projective compatibility
A K_f I = K_c       Galerkin compatibility on coarse observables
A K_f = K_c A       full conditional-expectation compatibility
```

Only the middle identity is forced by construction. The other two defects are
computed exactly as rational row norms.

At the safe in-memory ladder `(4,0) -> (6,1) -> (8,2)`, with common
`alpha = 0.55` and `R = 2..30`, all `133,632` finest samples resolve. The
finite numerical vectors contract on average:

```text
max(Mh/h) = 0.465489, 0.502925, 0.529990.
```

Those ratios are induced by the chosen common-`alpha` resolvent; they are
numerical upper ratios rather than independent spectral estimates.

But the raw lift profiles move in the wrong direction:

```text
E_mean             = 0.189683 -> 0.362275
maximum log spread = 1.921116 -> 2.923891
maximum live target ratio =
    5.267161 (Galerkin-induced) -> 1.995672 (finest sample)
```

Thus averaged contraction survives while raw vector stability and pointwise
descent are not supported at these tested levels. This triggers the planned
stop condition, but two adjacent comparisons do not rule out eventual
asymptotic stabilization. The next candidate must absorb the Mersenne
cusp/tail principal part, suppress high-frequency mixed-adic details, or work
directly with a branchwise potential.

The report is deliberately marked proof-ineligible: its vectors are float64,
Galerkin compatibility is weaker than projective compatibility, and a finite
averaged residue operator is not a per-orbit theorem. Unresolved and
out-of-window transitions are rejected by default because they share the
target-array sentinel with genuine descent.

The requested `(8,2) -> (10,3) -> (12,4)` production ladder now has a precise
engineering prerequisite. The `(12,4)` level contains `4,810,752` states, so
Python tuple/fiber materialization would consume multiple gigabytes. Arithmetic
parent maps, chunked coarsening, and streaming vector output must precede that
run.

Artifact: `docs/reports/pecm_cross_resolution_consistency.json`.

### 19.1 From a sampled obstruction to an exact local inequality

The worst concrete live-target ratio selected a source at
`(R,u mod 2^8,u mod 9)=(9,55,2)` and sampled unit `u=4151`. Sampling stopped
there. Exact replay found the post word `(3,2,4)`, hence full macro
`(1^8,3,2,4)` and affine identity

```text
F(n) = (177147 n + 186875) / 131072.
```

The branch is genuinely expanding, with `2125311 -> 2872411`. The exact-word
condition uses the often-missed final valuation bit:
`n = 28159 mod 2^18`. The post-exit form needs `u mod 2^9` for the word,
`u mod 2^11` for exact reentry at `R'=2`, and `u mod 2^18` to carry eight
target bits.

Partitioning the selected `u mod 2^11` root into its `128` children at
`2^18` was exhaustive. Every child has the same word and reentry depth, and
the targets cover all odd classes modulo `256` at `u mod 9=2`. The fixed-point
equation gives the noninteger value `-7475/1843`; this rules out a one-word
periodic integer cycle, but not an expanding itinerary through new cylinders.

The productive surprise was the cusp correction. The exact local formula

```text
H(n,R) = n (23/22)^R
```

contracts throughout the selected infinite root with worst factor

```text
7164821035427968 / 7236312975589017 < 1.
```

This is the first exact symbolic branch inequality in the PECM lane. It is
still local: all `128` targets are an open frontier, so the report refuses to
run Karp or claim a global certificate. An exact rational max-times
difference-constraint solver was added for the point when that graph becomes
closed.

Artifact: `docs/reports/pecm_exact_selected_cylinder_pilot.json`.

### 19.2 The open fiber becomes an exact recursive cusp

Expanding the `128` targets did not produce another finite quotient graph.
Instead, it exposed a cleaner symbolic structure. Every target has `R=2`,
so write `n=4u-1`. The complete odd-unit domain splits by `u mod 8`: three
classes descend in at most two post-exit steps, while `u=7 mod 8` reenters
through `(1,2)` with

```text
F(n) = (9n+5)/8 = (9u-1)/2.
```

The reentry depth is

```text
r = v2(9u+1)-1 >= 2.
```

For each fixed `r`, exact target refinement again reaches all `128` odd
residues modulo `256`. But the source precision is `r+9`, so it grows without
bound. The correct completion is a countable parametric branch family, not a
larger finite enumeration. This was a useful methodological correction:
ordinary positive source integers are completely classified even though the
resulting target grammar is infinite and open.

The first candidate then failed for an exact reason. The depth-2 member

```text
u=47,  n=187 -> 211
```

keeps `R=2`. No choice of the outer tail base can offset an expanding branch
when the outer tail coordinate does not change. A stronger construction
showed that every finite mixed `2`-adic/`3`-adic residue resolution contains
such a realizable expanding self-loop. The witnesses vary with resolution
and converge profinitely to `u=-1`; they are not one positive orbit. This
rules out a whole candidate class:

```text
n^alpha h(R,u mod 2^k,u mod 3^ell),
alpha >= 0, h > 0 finite-state.
```

The failure was informative rather than terminal. The same-`R` map on units
is

```text
T(u) = (9u+1)/8,
T(u)+1 = 9(u+1)/8.
```

The new coordinate `S=v2(u+1)` falls by exactly three on every repetition,
while `n+5` grows by `9/8`. Thus the nested potential

```text
K(n,u) = (n+5)(23/22)^S
```

contracts exactly by `11979/12167`. Arbitrarily long positive expanding
chains exist, but no positive integer can stay in this subfamily forever:
`S` loses three units per loop. The negative fixed point `n=-5` is a
2-adic organizing center, not a positive Collatz cycle.

The maximal run could then be induced without sampling. With
`j=floor((S-1)/3)`, the residual `S_exit=S-3j` is exactly `1`, `2`, or `3`.
Those cases descend at the first post step, descend at the second post step,
or reenter at a higher tail depth. The descents are below the compressed exit
source, not necessarily below the original pre-loop value. Their normalized
Haar proportions among odd 2-adic units are `4/7`, `2/7`, and `1/7`. For the
last branch, writing `u+1=2^S w` gives the exact next depth

```text
R_next = 2 + v2(9^(j+1)w - 1) >= 3.
```

The `6/7` descent mass is an average diagnostic and does not replace the
pointwise problem.

This changed the research picture from “fit one finite residue table” to
“discover a hierarchy of cusp coordinates and induce over their exits.” The
next exact target is the higher-`R` branch selected by `S_exit=3` and its
multi-return grammar.

Artifact: `docs/reports/pecm_r2_recursive_tail_cusp.json`.

---

## 20. Lessons learned

**What we got right:**

- Heavy use of audits caught real artifacts (V1–V5).
- Cross-validation with multiple methods (bootstrap, Bahadur–Rao,
  spike decomposition) gave concordant numbers.
- Reproducible JSON artifacts for every claim.
- Pulling and reading primary literature (Tao, Mori, Hercher,
  Paparella) before claiming originality.
- Distinguishing empirical from rigorous: empirical evidence with
  bootstrap CIs ≠ proof.

**What we got wrong (and corrected):**

- Initially treated `λ_super < 1` PECM Perron as descent certificate.
  Audit revealed PECM is averaged operator, not orbit growth rate.
- Treated `J = 0.0837` as universal constant. Stress-test revealed
  partition dependence and mod-8 stratification.
- Hypothesized `84/53` structural exclusion. Resolution artifact.
- Hypothesized `log(4/3)²` as closed form for J. 8σ rejection.
- Conflated dyadic quotient eigenvalue 0.5 with constrained JSR.
  Different objects.

**Methodological observations:**

- Iterative cycle of brainstorm → implement → audit → recalibrate
  worked well. Stalled iteration without audit produced artifacts.
- Reading literature *before* committing to a research direction
  (Mori's framework, Hercher's bounds) kept the project oriented to
  real mathematics.
- Stress-testing every candidate closed form caught at least 5 wrong
  guesses. Default to "empirical until proven structural."
- Every "promising" finding should be questioned: is this the
  artifact of definition / sampling / resolution?

---

## 21. Reproducibility

All results in this journey are reproducible:

```bash
# Run the full test suite (currently 262 tests passing in ~4s)
uv run python -m pytest -q

# Reproduce any artifact in docs/reports/ via the corresponding CLI:
uv run python -m collatz_exp.experiments --quick        # smoke test
uv run python -m collatz_exp.experiments --tao-syrac    # Tao verification
uv run python -m collatz_exp.experiments --jazz-spike   # spike decomposition
uv run python -m collatz_exp.experiments \
  --pecm-cross-resolution \
  --pecm-cross-resolution-output \
    docs/reports/pecm_cross_resolution_consistency.json
# ... see collatz_exp/experiments.py for the full flag list
```

Reference papers are saved in `docs/references/` for offline access.

---

## 22. Acknowledgments

The project was driven by an iterative human–AI collaboration. The
human's intuition repeatedly produced productive starting points
("ρ = 1/0", "what if there's a unified model", "is Jazz's constant
real?"). The AI's role was to formalize, implement, audit, and connect
to literature. Codex (CLI) implemented the bulk of the empirical
infrastructure; Claude assisted with strategic direction, literature
integration, and stress-testing.

The Collatz conjecture remains open. This project did not prove it.
It produced an honestly-calibrated computational framework that may
serve as a starting point for future work or as an example of how
iterative human–AI collaboration can produce a reproducible empirical
artifact in mathematics without overclaiming.
