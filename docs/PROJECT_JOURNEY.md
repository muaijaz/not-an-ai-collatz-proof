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

**Final state:** `collatz_exp/` package with 75 modules, 150 passing
tests, 91 JSON artifact reports, five integrated reference papers, and
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
    on residue quotients mod `2^k` for `k ∈ {2,3,4,5,6}`, the finite audit
    finds residue-uniform negative drift at the smallest tested grid value
    `m = 16`, with margin `ε = 0.1`, over sample windows
    `n₀ ∈ [10²,10¹⁵]` (`docs/reports/m_step_foster_drift.json`).

**Demoted claims (audit-revealed):**

1. ψ as rich Lyapunov potential — actually tautological.
2. Per-step linear Lyapunov from D_running — fails at 50% per step.
3. Structural Diophantine exclusion of `84/53` — resolution artifact.
4. `J = log(4/3)²` — rejected at 8σ.
5. Constrained JSR < 1 with naive residue automaton — fake n=-1 loop.

**Open theorem-shaped problems:**

1. **Markov/Lyapunov contraction on LTE-closed operator** (Codex's
   current target). Should give `Λ ≈ log(3/4)`.
2. **Christoffel-word integrality filter on JSR.** Bridge to
   Hercher's parity-vector framework. Expected outcome: filtered
   JSR < 1.
3. **Profinite continuity** from finite quotients to limit operator.
4. **Lifting PECM Lyapunov to per-orbit Lyapunov.** V5's gap.
5. **Symbolic interpretation of `J_renewal`** — does it have a closed
   form via integral representation à la Khinchin?
6. **Phase-aware per-orbit Lyapunov.** The residue-Markov m-step Foster
   question is empirically closed on the tested grid for
   `V(n) = log₂(n) + v_2(n+1)`: `m = 16` gives residue-uniform negative
   drift with margin `ε = 0.1` across the tested windows and residue powers.
   The remaining theorem-shaped problem is the upgrade from residue-Markov
   geometric ergodicity to deterministic per-orbit descent, the same
   distributional-to-pointwise wall that Tao 2019 works around in an
   almost-all setting.

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

## 15. Lessons learned

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

## 16. Reproducibility

All results in this journey are reproducible:

```bash
# Run the full test suite (currently 160 tests passing in ~2s)
uv run python -m pytest -q

# Reproduce any artifact in docs/reports/ via the corresponding CLI:
uv run python -m collatz_exp.experiments --quick        # smoke test
uv run python -m collatz_exp.experiments --tao-syrac    # Tao verification
uv run python -m collatz_exp.experiments --jazz-spike   # spike decomposition
# ... see collatz_exp/experiments.py for the full flag list
```

Reference papers are saved in `docs/references/` for offline access.

---

## 17. Acknowledgments

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
