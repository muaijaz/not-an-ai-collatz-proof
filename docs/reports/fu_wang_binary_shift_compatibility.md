# Compatibility note: Fu-Wang `2412.08097` ↔ this framework

> **Date:** 2026-05-02
> **Source:** Weicheng Fu, Yisen Wang, *The Structure of the Route to the Period-three Orbit in the Collatz Map*, arXiv:2412.08097 (8 pages, nlin.CD), Mathematical and Computational Applications 31, 23 (2026).
> **Goal:** Verify the abstract's claim of "equivalence to a binary shift map" — is it (a) topological conjugacy, (b) measurable conjugacy, or (c) heuristic/symbolic correspondence? Determine whether this gives the Markov-chain → integer-orbit lifting our framework needs.

---

## 1. What the paper actually establishes

**Direction phases (Eq. 4).** `P_↑(n) = 1` if `X_{n+1} > X_n`, `P_↓(n) = −1` if `X_{n+1} < X_n`. `N_↑` = count of up-phases before reaching `{1,4,2}`; `N_↓` = count of down-phases.

**Recursive function family F_s (§III.A).** Parameterizes Collatz orbits by upward-phase count:
- Case `N_↑ = 1`: `X_0 = F_1(p) = (4^p − 1)/3`, with constraint `p ≥ 2`.
- Case `N_↑ = 2`: `X_0 = F_2(p, k_1) = (2^{k_1} F_1(p) − 1)/3`.
- General: `X_0 = F_s(p, k_{s−1}) = (2^{k_{s−1}} F_{s−1}(p, k_{s−2}) − 1)/3`.

The key open conjecture: `F = O ∪ {1}` — every odd integer `> 1` is expressible as `F_s(p, k_1, ..., k_{s-1})` for some choice of parameters.

**Logarithmic scaling law (Eq. 20).** For `X_0 ∈ F`:
```
N_s = N_↑ + N_↓ = s · log_2(3) + log_2(X_0) + s
    ≈ N_↑ · (1 + log_2 3) + log_2(X_0).
```
Total iterations grow logarithmically with `X_0` — consistent with conjectural Collatz convergence rate.

**"Equivalence to binary shift map" (§III.C).** Section III.C is INFORMAL / heuristic. Specifically:

- They write `X_0 = 2^{m-1} + Σ_{j=1}^{m-2} c_j 2^j + 2^0` (binary representation with leading + trailing 1).
- They observe that `2X_0 + 1` corresponds to "leftward binary shift with terminal 1 appended."
- They observe that `M²(X_0) = (3X_0+1)/2` "shifts `c_1` of `X_0` to the position of `c_0` of `X_2`, updating other coefficients via addition."
- Quote: "Statistically, a rightward shift occurs due to the equiprobability of `c_j ∈ {0,1}` — validating the Collatz conjecture."
- Quote: "The ergodicity of the binary shift map ensures that the state of `X^p` (Fig. 3) must eventually appear, further guaranteeing the validity of the Collatz conjecture."

**This is a heuristic statistical argument, not a topological or measurable conjugacy theorem.** No formal definition of the conjugacy is given; no theorem statement of the form "Φ: ({0,1}^ω, σ) → (ℕ, M²) is a topological conjugacy" appears.

The actual convergence proof in the paper (Eqs. 24-25) covers only `X_0 ∈ F` (the set in the image of the `F_s` family). Whether `F = O ∪ {1}` is itself unproven and remains the paper's primary open question.

**Empirical observations (§IV):** basins of attraction follow power-law (`N(p) ∝ 1/X^p` for `mod(p, 3) = 0`); odd numbers grouped by `N_↑` follow Gamma distributions (`A ≈ 1` constant; `K ∝ log_{10}(L)`).

---

## 2. Comparison to this framework

**Logarithmic scaling.** Their Eq. 20 says `N ≈ N_↑(1 + log_2 3) + log_2(X_0)`. Translating to this framework's accelerated odd-to-odd map: each accelerated step corresponds to one of their up-phases plus the consecutive halvings (down-phases). So `T = N_↑` accelerated steps and `N_↓ = T · ⟨a⟩` halvings where `⟨a⟩` is the mean valuation. This gives `N = T(1 + ⟨a⟩) ≈ T · 3` for `⟨a⟩ ≈ 2`, matching their `1 + log_2(3) ≈ 2.585` (off by ~16% — likely the difference between `log_2(3)` and the mean valuation; their formula treats up-phases as multiplying by 3 exactly, while ours treats accelerated steps as multiplying by `3/2^a`).

**Bottom line:** their logarithmic scaling and our renewal mean drift `log_2(3/4) ≈ −0.415` per accelerated step are **the same observation in different units**. No new structural insight; mutual confirmation only.

**`F_s` family vs our realizable Karp.** The two papers parameterize different objects:
- Fu-Wang: starting values `X_0` parameterized by `(p, k_1, ..., k_{s-1})` indexing upward-phase structure.
- This framework: cycles in the LTE-closed tail graph parameterized by `(q, R_max)` and bounded period.

`F_s` parameterizes pre-cycle trajectories (orbits reaching `{1,4,2}`); our realizable Karp characterizes potential cycle structures. **No direct overlap.** Their conjecture `F = O ∪ {1}` is essentially a re-statement of "every odd integer reaches 1" — i.e., the Collatz conjecture itself, in their parameterization.

**Binary shift "equivalence."** The §III.C observation is consistent with — but not stronger than — well-known Tao-style symbolic/measurable arguments on residues. Specifically:
- Mori 2024 establishes a rigorous operator-algebraic shift framework (`C*(T_1, T_2) ≅ Cuntz O_2`).
- Tao 2019 establishes rigorous distributional mixing on `Syrac(ℤ/3^n ℤ)`.
- This framework establishes Foster condition on residue Markov chain at `k ∈ {2..8}`.

Fu-Wang's heuristic shift argument is **informally adjacent** to all three but does not add a new tool. Their "ergodicity of the binary shift map ensures convergence" is the same Tao distributional-to-pointwise wall as everything else, expressed informally.

---

## 3. What is NOT in the paper (despite abstract suggesting otherwise)

- **No rigorous conjugacy theorem.** No statement of the form "Φ: ({0,1}^ω, σ) → (ℕ, M²) is a topological/measurable conjugacy."
- **No proof of Collatz.** Their Eq. 24-25 prove convergence only for `X_0 ∈ F`, where `F` is the image of `F_s`. The conjecture `F = O ∪ {1}` is explicitly named as remaining open (page 5: "providing a direct proof of this point is difficult, and efforts will continue in the future").
- **No new analytic technique.** The paper's contribution is empirical observations + recursive parameterization + heuristic shift argument. The substantive Collatz progress is implicit in their open conjecture `F = O ∪ {1}`.

---

## 4. Implications for this framework

**Negligible composition.** Fu-Wang's results are in the same general family as Tao distributional, Mori operator-algebraic, and our Markov Foster — all approaches to the same wall. Their specific contributions (`F_s` family, Gamma-distributed basins) are at a different level of the hierarchy than ours and don't compose directly.

**One concrete potential extension:** Fu-Wang observe that `N_↑` (upward-phase count) has a Gamma distribution with parameters `(A ≈ 1, K ∝ log_{10}(L), θ)`. This framework's renewal increment distribution under uniform-residue sampling is conjectured to be approximately Geom(1/2) on valuations (Chang Cor 9.62). The `N_↑` Gamma distribution should compose with the per-up-phase mean log-drift `log_2(3) − ⟨a⟩` to give Fu-Wang's Eq. 20 distributionally — testable on this framework's cache. **Effort:** 1 Codex prompt comparing empirical `N_↑` distribution per orbit on our cache to Fu-Wang's Gamma fit. **Output:** would either confirm Fu-Wang's distributional claim with much larger sample (1M orbits vs their `10^11` integers in `[3, 2L+1]` per `L`) or surface a deviation. Low priority.

**No defensive concerns.** Fu-Wang's claims are consistent with our framework. No revisions to existing artifacts needed.

---

## 5. Summary verdict

The abstract's "equivalence of the Collatz map to a binary shift map" is **not a rigorous conjugacy** but a heuristic/statistical argument. The paper's substantive contributions are:

1. The `F_s` recursive parameterization of orbits by upward-phase count.
2. The logarithmic scaling formula (consistent with our renewal mean drift `log_2(3/4)`).
3. Empirical Gamma distributions of `N_↑` and power-law basins.
4. Conjectural `F = O ∪ {1}` (essentially Collatz itself in their parameterization).

The **binary-shift-conjugacy expectation** that motivated putting this paper at the top of the literature-sweep priority list **is not realized** in the paper as written. The "ergodicity gives convergence" framing is heuristic, not theorem.

**Net contribution to this framework: confirmatory only.** Fu-Wang's logarithmic scaling and our renewal mean drift agree. No new tool, no new structural composition. **No follow-up tasks generated; remove from priority list.**

---

## 6. Caveats

- This compatibility analysis is based on the published 8-page paper. The authors may have follow-up work that formalizes the conjugacy claim.
- The Gamma distribution observation (their Fig. 8-9) is empirically tight (`R² > 0.999`); if there is a structural reason for the Gamma fit, it would be worth understanding. Currently treated as phenomenological.
- The paper is published in *Mathematical and Computational Applications*, a moderate venue; the methods are dynamical-systems style (heuristic + numerical), not rigorous-analytic. The `nlin.CD` arXiv classification is consistent with this.

---

## References

- Fu, W. & Wang, Y. (2026). *The Structure of the Route to the Period-three Orbit in the Collatz Map.* arXiv:2412.08097, Math. Comput. Appl. 31, 23.
- This framework's relevant artifacts: `renewal_drift_phase_decomposed.json`, `m_step_foster_drift.json`.
