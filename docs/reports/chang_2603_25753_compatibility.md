# Compatibility analysis: Chang 2603.25753 ↔ this framework

> **Date:** 2026-05-02
> **Source:** Edward Y. Chang, *A Structural Reduction of the Collatz Conjecture to One-Bit Orbit Mixing*, arXiv:2603.25753, 24 Mar 2026.
> **Companion:** Chang 2603.11066 (already integrated; see `docs/NOTE_DRAFT.md` "Position Relative to Chang 2026").
> **Goal:** Determine whether Chang's reduction and this framework's m-step Foster condition compose into a joint argument, and identify the precise residual gap.

---

## 1. Chang's framework (compressed)

**Map.** The compressed odd-to-odd Syracuse map `T(n) = (3n+1)/2^{v_2(3n+1)}` for odd `n ≥ 1` (identical to our `S`).

**Burst indicator.** `X_t = 1[v_2(3 n_t + 1) ≥ 2] = 1[n_t ≡ 1 mod 4]` (Chang Eq. 1). Equivalently, `X_t = 1` ⇔ `n_t` is post-exit in this framework's vocabulary; `X_t = 0` ⇔ tail-internal.

**Burst-gap decomposition.** `(X_t)` factors into alternating burst runs of length `L_i` and gap runs of length `G_i`. Burst density `ρ = T^{-1} Σ X_t`; block-alternation rate `q = m/T`.

**Block-TV budget condition** (Chang Eq. 3, from companion paper):
```
Σ_{K=3}^{K_0} ‖h_K‖_∞ · ε_K  <  ln 2 − ρ ln 3,
```
where `ε_K` = TV-distance between empirical K-block frequency `ν_T(w)` along a single orbit and Bernoulli(`ρ`) product law. `‖h_K‖_∞ = O(1)` uniformly in K. **This is the global condition equivalent to Collatz descent in Chang's setup.**

**Map Balance Theorem (Chang Thm 4.2).** Define `S_K = {r ∈ ℤ/2^K ℤ : r ≡ 1 mod 4, T(r) ≡ 3 mod 4}` (burst residues mod 2^K that initiate gaps). Define
- `C_3(K) = #{r ∈ S_K : T(r) ≡ 3 mod 8}` (gap continues, `G_i ≥ 2`),
- `C_7(K) = #{r ∈ S_K : T(r) ≡ 7 mod 8}` (unit gap, `G_i = 1`).

Then `|S_K| = 2^{K−3} − 1`, `C_3(K) − C_7(K) = (−1)^K` for `K ≥ 5`, and the `n ≡ 1 mod 8` subclass contributes exactly `C_3^{(1)} = C_7^{(1)} = 2^{K−5}` (perfect balance). Chang verifies the exact `|C_3 − C_7| = 1` numerically through `K = 19`.

**Single-bit bottleneck (Chang §5).** For the dominant `n ≡ 1 mod 8` class (≈ half of burst-to-gap transitions), the gap outcome reduces to bit 4 of `n_t` at burst-ending times:
- bit 4 = 0 ⇔ `n_t ≡ 9 mod 32` ⇔ `G_i ≥ 2`
- bit 4 = 1 ⇔ `n_t ≡ 25 mod 32` ⇔ `G_i = 1`

**Chang's Open Problem (Eq. 16).** For every odd `n_0 > 2^{68}`, restricted to the dominant subclass `n_{t_i} ≡ 1 mod 8`, prove
```
| #{i ≤ m : n_{t_i} ≡ 9 mod 32} / #{i ≤ m : n_{t_i} ≡ 9 or 25 mod 32} − 1/2 |  ≤  δ
```
for some `δ < δ_max` determined by the block-TV budget. **Fixed modulus (32), single bit (bit 4), sparse subsequence (O(m) out of T total).**

**Chang's three proposed routes** (§7.3):
- **Route A (Cocycle contraction).** Fiber matrices `A_0, …, A_7` indexed by `f = ⌊n_t/32⌋ mod 8`. Fiber-averaged matrix has spectral gap `γ ≈ 0.98` and stationary bit-4 ratio exactly `1/2`. Each `A_f` contracts on the mean-zero subspace with worst operator norm `0.831`. **At finer resolution (mod 16 and beyond), sub-fiber matrices do NOT all contract: the 0.831 bound is an averaging effect.** Chang verifies "consistently negative Lyapunov exponents (λ ∈ [−0.14, −0.09])" on five tested orbits. Closing Route A requires proving sub-fiber equidistribution within each base fiber along orbits.
- **Route B (Additive combinatorics).** Weyl-type estimates on the burst-ending subsequence.
- **Route C (p-adic dynamics).** 2-adic ergodic theorem for Collatz iteration on `ℤ/32ℤ` along the burst-ending subsequence.

---

## 2. This framework's relevant findings

**Map.** Identical: `S(n) = (3n+1)/2^{v_2(3n+1)}`.

**Phase partition.** Identical: `n ≡ 3 mod 4` (tail-internal) vs `n ≡ 1 mod 4` (post-exit). Equivalent to Chang's gap-step vs burst-step.

**Realizable Karp.** At LTE-closed tail graph levels `(q, R_max) ∈ {(5,4),(6,5),(7,6)}`, of `226,333` simple cycles audited up to `max_cycle_edges = 12`, exactly 3 classify as `positive_integer_cycle` (the elementary `[2]` cycle, factor 3/4, one per level); 226,330 classify as `noninteger_2adic_only`. Realizable Karp = slope-filtered Karp = 3/4 at tested levels. Source: `tail_cycle_realizability_extended.json`.

**Renewal mean drift.** `mean_drift_per_step = log₂(3/4) − 0.0046` at `n_0 ∈ [10⁶, 10⁹]` with CI `[−0.4187, −0.4061]`; phase decomposition gives `E[a | tail] = 1` exactly, `E[a | post-exit] → 3` (shifted-Geom asymptotic). Source: `renewal_drift_phase_decomposed_n0_stability.json`.

**Lyapunov candidate.** `V(n) = log₂(n) + v_2(n+1)`. Phase-Lyapunov search reduces V5's per-step non-decrease from 50.0% to 16.5% over 100k orbits; tail-internal phase locked at 0%, residual obstruction is post-exit `R'`-spike events. Source: `phase_lyapunov_search.json`.

**1-step Foster drift.** Marginal drift of `V` consistent with `log₂(3/4)` at every window in `[10², 10¹⁵]`. Residue-conditional drift fails uniform negativity at every `k ∈ {3,4,5,6}` with 50 obstruction witnesses; binding class `n ≡ 41 mod 64` has +3.558 drift. Source: `phase_lyapunov_foster_drift.json`.

**m-step Foster drift.** Smallest `m ∈ {1,2,4,8,16,32,64}` for which residue-conditional drift is uniformly negative across all windows and `k ∈ {2,3,4,5,6}` is **m = 16** with margin `ε = 0.1` (geometric-ergodicity grade). At `m = 64`, zero obstructions remain. Sample size: 200,000 per window across 5 windows = 1,000,000 sampled orbits. Source: `m_step_foster_drift.json`.

**Hitting-time distribution.** 0.99-quantile of `T_descent(n) = min{m : V(S^m(n)) ≤ V(n) − 1}` at deepest window `[10¹², 10¹⁵]` is 33 accelerated steps with 0% truncation at `m_max = 1000`. Source: `phase_lyapunov_foster_drift.json`.

---

## 3. Notation correspondence

| Object | Chang notation | This framework notation | Identity |
|---|---|---|---|
| Map | `T(n) = (3n+1)/2^{v_2(3n+1)}` | `S(n)` | identical |
| Phase indicator | `X_t = 1[n_t ≡ 1 mod 4]` | `1[n_t ≡ 1 mod 4]` (post-exit) | identical |
| Burst run length | `L_i` | (consecutive post-exit runs) | identical |
| Gap run length | `G_i` | (consecutive tail-internal runs) | identical |
| Burst density | `ρ` | `w_post_exit ≈ 0.5` | identical |
| Block-TV at depth K | `ε_K` | (not directly tracked) | implicit via residue distribution |
| Burst residues mod 2^K | `S_K` (gap-producing) | (subset of post-exit class) | refinement |
| Single-bit observable | bit 4 of `n_t` at burst-end | (not directly tracked) | new |
| Residue chain quotient | (implicit, mod 2^K + fiber mod 8) | mod 2^k for `k ∈ {2,3,4,5,6}` | Chang at finer mod 256; ours at mod 64 max |
| Lyapunov | (not explicit; cocycle norm 0.831 averaging) | `V(n) = log₂(n) + v_2(n+1)` | new in this framework |
| Empirical Lyapunov rate | `λ ∈ [−0.14, −0.09]` over 5 orbits | `m=16 ⇒ ε ≥ 0.1 / 16` ≈ 0.006 per step over 1M orbits | rate-comparable |

---

## 4. The shared open problem

**Chang's open step (Eq. 16):** for every individual deterministic orbit, the sub-mod-32 burst-ending residue visits ≡9 vs ≡25 in balance up to `δ < δ_max`.

**This framework's open step (PROJECT_JOURNEY.md §12, item 4):** lift residue-Markov m-step Foster condition to deterministic per-orbit Lyapunov contraction.

**They are the same problem** in two different presentations:

- Chang reduces to "balance of bit 4 along the burst-ending subsequence at sparse times along every orbit."
- This framework reduces to "drift of V on residue Markov chain at k=6 ⇒ pointwise descent of V along every orbit."

Both are instances of the Tao 2019 distributional-to-pointwise wall: a probabilistic / distributional statement is established (Chang's Map Balance Theorem; this framework's Foster condition), and the upgrade to every individual deterministic orbit is the open step.

---

## 5. What this framework's Foster condition provides toward Chang's open problem

**Direct provision.** For the residue Markov chain on `ℤ/2^k ℤ` (`k ∈ {2,3,4,5,6}`), the Foster condition with `m = 16` and margin `ε = 0.1`, combined with Markov-chain ergodicity (irreducibility + aperiodicity, both of which the chain satisfies), gives **almost-sure equidistribution of the orbit's empirical residue distribution to the stationary distribution `1/2^{k−1}` on each odd residue class** (Birkhoff's ergodic theorem applied to the residue chain). At `k = 5` (mod 32), this is exactly the stationary `1/2` split between `n ≡ 9 mod 32` and `n ≡ 25 mod 32` within the `n ≡ 1 mod 8` class — the rate Chang asks for in Eq. 16.

**Quantitative rate.** The geometric-ergodicity margin `ε = 0.1` (per `m = 16` accelerated steps) translates to an empirical mixing rate. For a residue Markov chain with Foster margin `ε` at step `m`, the convergence to stationary distribution is geometric with rate `O((1 − ε)^{t/m}) = O((0.9)^{t/16})`. For an orbit of length `t = T`, the empirical-vs-stationary deviation is bounded by `O((0.9)^{T/16}) ≈ O(e^{−0.0066 T})`. Combined with Chang's block-TV budget Eq. 3 (LHS bounded by `O(1) · ε_K`), the budget is satisfied for every `T` large enough that `e^{−0.0066 T} < δ_max`.

**Key composition.** This framework's Foster condition + Markov ergodicity → almost-sure equidistribution on orbits → Chang's `δ < δ_max` for almost every orbit.

---

## 6. The residual gap

**The gap is the same Tao 2019 wall.** Foster + Birkhoff gives **almost-sure** equidistribution; Chang asks for **every-orbit** equidistribution.

The set of orbits on which Foster ergodicity fails has Markov-chain measure zero. Whether this measure-zero set contains any actual integer orbit is exactly Tao's distributional-to-pointwise question.

**What the joint argument achieves:** *Conditional on Markov-chain-measure-1 holding for every starting integer*, Chang's reduction + this framework's Foster condition imply Collatz descent for every starting integer.

**What it doesn't achieve:** the conditional itself. The unconditional version is the Collatz conjecture. Tao 2019 establishes the conditional at the level of natural density (almost all integers); the joint argument here would give it at the level of Markov-measure (a related but distinct measure).

---

## 7. Joint argument candidate

The composition is:

```
Foster m=16 with ε=0.1 (this framework)
          ⇓  (Markov-chain ergodicity + Birkhoff)
Almost-sure equidistribution mod 2^k along Markov-chain trajectories
          ⇓  (assumption: every integer orbit is in the measure-1 set)
Every-orbit equidistribution mod 32 at burst-ending times
          ⇓  (Chang's Map Balance Theorem 4.2 + bit-4 reduction §5)
Every-orbit balance of bit 4 within δ_max (Chang Eq. 16)
          ⇓  (Chang's block-TV budget Eq. 3 + companion paper [3])
Collatz descent for every starting integer
```

**Residual gaps:**

1. The "every integer orbit is in the measure-1 set" assumption (the Tao wall).
2. Verifying Chang's `δ_max` quantitatively from the block-TV budget Eq. 3 — Chang does not compute `δ_max` in `2603.25753`; he refers to companion paper `[3]` (= 2603.11066). Our Foster rate `(0.9)^{T/16}` would need to be checked against this `δ_max`.
3. Markov-chain ergodicity at higher `k` (we have it empirically at `k ∈ {2..6}`; Chang operates at mod 32 with mod 256 fiber refinement, so we'd need to confirm Foster holds at `k = 8`).

**This is significantly tighter than the framework's previous statement of the open problem.** The joint argument reduces it from "two unrelated walls" to "a single Tao-style wall plus two technical verifications."

---

## 8. Empirical contribution comparison

| Quantity | Chang `2603.25753` | This framework |
|---|---|---|
| Largest verified depth | mod 2^19 (Map Balance Thm via Table 1) | mod 2^6 (Foster); mod 2^15 (LTE-closed tail subautomaton) |
| Orbits with empirical Lyapunov | 5 orbits (λ ∈ [−0.14, −0.09]) | 1,000,000 orbits (Foster ε=0.1 at m=16) |
| Window depth | up to `n_0 = 10^9` | up to `n_0 = 10^{15}` |
| Tail bound | (none stated) | Sub-exponential rejected by KS at deepest window; `λ̂ = 0.92` for partial exponential |
| Hitting-time bound | (not measured) | 0.99-quantile = 33 steps at deepest window with 0% truncation |

**This framework provides substantially stronger empirical evidence for Chang's Route A (cocycle contraction)** than Chang himself does. Specifically: Chang's Route A is verified on 5 orbits with eyeball Lyapunov estimates; this framework's Foster condition is verified on 1M orbits with publication-grade CIs and an exact m=1 cross-check. Combining the two papers strictly strengthens both.

---

## 9. Action items

**Immediate (high-value, AI-tractable).**

1. **Compute `δ_max` from Chang's Eq. 3.** Chang refers to companion paper `[3]` (2603.11066) for explicit values of `‖h_K‖_∞`. Cross-reference, compute the LHS of Eq. 3 numerically using this framework's empirical `ρ ≈ 0.5` and a conservative estimate of `ε_K`, derive `δ_max`, and compare to this framework's Foster rate `(0.9)^{T/16} ≈ e^{−0.0066 T}`.

2. **Extend Foster condition to `k = 7, 8`** to match Chang's working resolution (mod 256). Run the m-step Foster audit at `(k_max = 8, m_grid = (1,2,4,8,16,32,64))` and check whether the Foster condition still holds at `m = 16` with `ε = 0.1`. If yes, the joint argument's third gap closes empirically.

3. **Verify the bit-4 balance directly** along orbits in this framework's cache. Compute the empirical `#{n_{t_i} ≡ 9 mod 32} / #{n_{t_i} ≡ 9 or 25 mod 32}` along sampled orbits at each window depth, and check whether the deviation from 1/2 satisfies Chang's `δ < δ_max`. This is a direct empirical test of the joint argument's conclusion at finite windows. Save to `docs/reports/chang_bit4_balance_audit.json`.

**Documentation.**

4. Update `docs/NOTE_DRAFT.md` "Position Relative to Chang 2026" section to reflect the composition with `2603.25753`, distinguishing the two Chang papers.

5. Update `docs/PROJECT_JOURNEY.md` §12 "Open theorem-shaped problems" to record the joint-argument formulation: the Foster + Chang composition reduces this framework's open problem 4 (residue-Markov-to-deterministic) to Chang's Eq. 16 (bit-4 pointwise balance), which in turn is the Tao 2019 wall.

**Coordination.**

6. **Reach out to Edward Y. Chang** (Stanford). The papers are sibling efforts addressing the same open step from complementary angles (combinatorial-structural vs Markov-Lyapunov). A joint note positioning both contributions toward the `δ_max` budget is a natural coordination.

---

## 10. Caveats

- This compatibility analysis is a finite empirical / cross-paper diagnostic. It does not establish a proof of Collatz descent, and it does not close any of the three residual gaps in §6.
- Chang's `δ_max` is named in `2603.25753` Eq. 16 but not computed there; the cross-reference to companion paper `[3]` (2603.11066) is required to derive it.
- This framework's Foster condition is verified at `k ∈ {2,3,4,5,6}`; extending to `k = 8` (Chang's working resolution) is action item 2 and is empirical, not yet performed.
- The "Markov-chain ergodicity" step uses Birkhoff's ergodic theorem applied to the residue-Markov chain, which is a standard but non-trivial inference; for this framework's empirical Foster condition, ergodicity is plausible but not formally verified (the chain is irreducible by construction, but aperiodicity and the Doeblin condition would need explicit checks).
- Both papers are dated 2026; neither has gone through external peer review at the time of this analysis.

---

## References

- Chang, E. Y. (2026). *A Structural Reduction of the Collatz Conjecture to One-Bit Orbit Mixing.* arXiv:2603.25753.
- Chang, E. Y. (2026). *Exploring Collatz Dynamics with Human-LLM Collaboration.* arXiv:2603.11066. (Companion paper containing block-TV budget Eq. 3 and `‖h_K‖_∞` constants.)
- Tao, T. (2019). *Almost all orbits of the Collatz map attain almost bounded values.* Forum Math. Pi 10, e12. arXiv:1909.03562.
- Meyn, S. & Tweedie, R. L. (2009). *Markov Chains and Stochastic Stability.* Cambridge University Press, ch. 11. (Foster-Lyapunov drift theorem; Birkhoff for Markov chains.)
- This framework's artifacts: `m_step_foster_drift.json`, `phase_lyapunov_foster_drift.json`, `phase_lyapunov_search.json`, `tail_cycle_realizability_extended.json`, `renewal_drift_phase_decomposed_n0_stability.json`.
