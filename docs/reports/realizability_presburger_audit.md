# Realizability Presburger audit (Dhiman-Pandey 2601.12772 defensive check)

> **Date:** 2026-05-02
> **Trigger:** Dhiman-Pandey `arXiv:2601.12772` (Jan 2026) proves the divisibility predicate `D_y = {(x, C) ∈ ℕ² : (2^x − 3^y) ∣ C}` is NOT semilinear for any fixed `y ≥ 1`, hence NOT Presburger-definable. Implication: Presburger / finite-automaton characterizations cannot distinguish "ghost cycles" (2-adic integer solutions to the cycle equation that fail to be in ℤ) from genuine integer cycles. This audit verifies whether this framework's `lift_realizability.py` test is affected.
> **Verdict:** **NOT AFFECTED.** Our test computes the divisibility check via exact Python integer arithmetic, which is full Peano arithmetic, not the first-order theory of `(ℕ, +, <)` (Presburger). Existing realizable-Karp = 3/4 finding stands.

---

## 1. The Dhiman-Pandey obstruction (precise)

Cycle equation (Dhiman-Pandey Eq. 1, restated from Lagarias / Simons-de Weger):
```
n_0 · (2^x − 3^y) = Σ_{k=0}^{y-1} 3^{y-1-k} · 2^{σ_k}  =:  C(y, σ⃗)
```
where `(x, y, σ⃗)` is a parity pattern.

**Theorem 4.1 (Existence of Ghost Cycles).** For every cycle-admissible pattern `(x, y, σ⃗)`, there exists a unique `n_0 ∈ ℤ_2` solving the cycle equation: `n_0 = (2^x − 3^y)^{-1} · C(y, σ⃗)`. This 2-adic solution is termed a **ghost cycle**.

**Theorem 6.5.** Ghost cycles are genuine periodic points of the 2-adic Collatz map `T_2: ℤ_2^× → ℤ_2`.

**Integrality criterion (§5).** A ghost cycle `n_0 ∈ ℤ_2` is a genuine integer cycle iff `n_0 ∈ ℕ`, equivalently iff `(2^x − 3^y) ∣ C(y, σ⃗)` in `ℤ`.

**Theorem 7.2 (Unconditional Non-Semilinearity).** For any fixed `y ≥ 1`, the set
```
D_y = {(x, C) ∈ ℕ² : x > y log_2 3, C ≥ 1, (2^x − 3^y) ∣ C}
```
is NOT semilinear. Proof: the fiber `(D_y)_x = {k(2^x − 3^y) : k ∈ ℤ_>0}` has minimal period `2^x − 3^y` which grows unbounded as `x → ∞`. By Lemma 2.3 (unbounded-fiber-period obstruction), this rules out semilinearity.

**Corollary 7.3.** The predicate `P(x, C) ≡ [(2^x − 3^y) ∣ C]` is NOT definable in Presburger arithmetic.

**Heuristic Argument 1 (§8).** Since ghost cycles satisfy the cycle equation but fail integrality, and integrality is not Presburger-definable, **non-existence of integer cycles cannot be proven via algebraic manipulation of the cycle equation alone**. The "Integrality Gap" between `ℤ_2`-ghost-cycle and `ℤ` requires analytic methods.

---

## 2. Our test (in `collatz_exp/cycles.py:26 — classify_cycle_word`)

```python
def classify_cycle_word(word: tuple[int, ...]) -> CycleClassification:
    affine = affine_from_word(word)            # gets (A, m, B)
    denominator = (1 << affine.A) - 3**affine.m
    if denominator == 0:
        return CycleClassification(kind="impossible_power_balance", ...)
    value = Fraction(affine.B, denominator)
    if affine.B % abs(denominator) != 0:        # <<<< the integrality check
        return CycleClassification(kind="noninteger_2adic_only", ...)
    n = value.numerator
    if denominator < 0:
        return CycleClassification(kind="negative_integer_cycle", ...)
    if n > 0 and n % 2 == 1:
        realizes_word = apply_word(n, affine.word) == n   # <<<< direct verification
        return CycleClassification(kind="positive_integer_cycle" if realizes_word else "...nonrealizing_candidate", ...)
    return CycleClassification(kind="integer_but_not_positive_odd", ...)
```

**Variable correspondence:**

| Dhiman-Pandey | this framework | meaning |
|---|---|---|
| `x` | `affine.A` | total halvings (sum of valuations) |
| `y` | `affine.m` | number of odd steps (period) |
| `(2^x − 3^y)` | `denominator = (1 << affine.A) - 3**affine.m` | the cycle-equation coefficient |
| `C(y, σ⃗)` | `affine.B` | cycle-equation right-hand side |
| `(2^x − 3^y) ∣ C` | `affine.B % abs(denominator) == 0` | integrality of ghost cycle |
| Ghost cycle (non-integer) | `kind = "noninteger_2adic_only"` | divisibility fails |
| Genuine integer cycle | `kind = "positive_integer_cycle"` (with `realizes_word = True`) | divisibility succeeds + word verification |

**Exact correspondence** between this framework's `classify_cycle_word` and Dhiman-Pandey's algebraic framework. The two papers compute the same divisibility check with different terminology.

---

## 3. Why we are not affected by the Presburger obstruction

Dhiman-Pandey's Theorem 7.2 establishes that `[(2^x − 3^y) ∣ C]` is **not Presburger-definable**. This is a statement about which logical theory can express the predicate, not about whether the predicate can be computed.

Our `affine.B % abs(denominator)` computation in Python uses arbitrary-precision integer arithmetic, which is full Peano arithmetic. Specifically:

- Multiplication is allowed (Presburger forbids it).
- Exponentiation `3**affine.m` is allowed (Presburger lacks it).
- Modular reduction `% abs(...)` is allowed (Presburger has +, <, but not /).

Our test is therefore **outside the scope of the Dhiman-Pandey obstruction**. The obstruction rules out Presburger / finite-automaton approaches; we are using neither.

Furthermore, the verification step `apply_word(n, affine.word) == n` is direct integer iteration of the Collatz map word, an explicit computation. If this passes, `n` is genuinely a fixed point of the word (an integer cycle).

**Our `noninteger_2adic_only` classification IS exactly the ghost-cycle case** in Dhiman-Pandey's terminology. We correctly identify ghost cycles as non-integer and exclude them from `positive_integer_cycle`. The realizable-Karp = 3/4 finding (`tail_cycle_realizability_extended.json`: 226,330 of 226,333 high-growth cycles are `noninteger_2adic_only`) is therefore **consistent with — and in fact a special case of — the Dhiman-Pandey ghost-cycle taxonomy**. They independently prove that ghost cycles exist for every cycle-admissible pattern; we independently exhibit specific ghost cycles in our finite scan.

---

## 4. The deeper Dhiman-Pandey concern: pure algebra cannot prove Collatz

Dhiman-Pandey's heuristic (§8) argues:
> If the cycle equation encapsulates all arithmetic constraints on a Collatz cycle, and ghost cycles satisfy this equation, then no algebraic contradiction can be derived from the equation alone. Non-existence of integer cycles must come from the "Integrality Gap" — an analytic phenomenon, not algebraic.

**Implication for this framework:** our finite empirical enumeration at tested `(q, R_max)` levels relies on **direct integer computation** rather than algebraic manipulation. We are not deriving a contradiction; we are **exhaustively checking** that no positive integer cycle exists in our finite enumeration window. This is consistent with Dhiman-Pandey's heuristic — we are not attempting an algebraic non-existence proof.

**Implication for our open problem 2** (`PROJECT_JOURNEY` §12: Christoffel-word integrality filter on JSR, Hercher bridge): a Hercher-style approach pushes the m-cycle bound from 91 toward larger m via parity-vector + reciprocal-sum analysis. Hercher's method uses **transcendence of `log_2 3`** (Baker's theorem) for some bounds — i.e., analytic, not pure algebra. **The Dhiman-Pandey obstruction does NOT rule out Hercher's approach** because Hercher uses analytic transcendence facts beyond pure first-order arithmetic.

Therefore: our open problem 2 (Christoffel/integrality filter via Hercher) remains viable. The Dhiman-Pandey obstruction rules out **only** pure-Presburger / pure-automaton routes, not analytic approaches.

---

## 5. Action items (none required)

The audit confirms:

- (A) Our `classify_cycle_word` test is sound: ghost cycles correctly classified as `noninteger_2adic_only`.
- (B) Our test uses Peano arithmetic (Python `int`), not Presburger; Dhiman-Pandey obstruction does not apply.
- (C) Existing realizable-Karp = 3/4 finding is unaffected. The 226,330 `noninteger_2adic_only` classifications are exactly Dhiman-Pandey ghost cycles, identified correctly.
- (D) Open problem 2 (Hercher/integrality bridge) remains viable since Hercher uses transcendence (analytic), not pure algebra.

**No code or documentation changes required.** The Dhiman-Pandey obstruction is consistent with this framework's empirical findings and provides additional theoretical grounding (every `noninteger_2adic_only` is a ghost cycle in their precise sense). One small update to PROJECT_JOURNEY §12 item 2 would acknowledge Dhiman-Pandey's structural support for the Hercher route's continued viability — optional, not load-bearing.

---

## 6. Caveats

- This audit verifies that our **algorithmic test** is not Presburger-bound. It does not address whether **the conclusions we draw** from finite enumeration are formally provable in Presburger or any specific logical theory. The conclusion "no positive integer cycle of bounded period exists at tested levels" is a finite empirical fact, not a theorem in any specific arithmetic theory.
- Dhiman-Pandey is a Jan 2026 preprint; not externally peer-reviewed. The obstruction proof (Theorem 7.2 + Lemma 2.3) is elementary and likely correct.
- Dhiman-Pandey explicitly note (Heuristic 1) that their conclusion is a heuristic, not a proof, that pure algebraic approaches fail. Combined with our finite-empirical methodology, this strengthens (rather than weakens) the framework's overall position: we are not making algebraic-non-existence claims.

---

## References

- Dhiman, M. & Pandey, R. (2026). *2-Adic Obstructions to Presburger-Definable Characterizations of Collatz Cycles.* arXiv:2601.12772.
- Ginsburg, S. & Spanier, E. (1966). *Semigroups, Presburger formulas, and languages.* Pacific J. Math 16(2):285–296. (Underlying semilinearity-Presburger equivalence.)
- This framework's source: `collatz_exp/cycles.py:26` (`classify_cycle_word`), `collatz_exp/lift_realizability.py:172` (`lift_realizability_report`).
- This framework's artifact: `tail_cycle_realizability_extended.json` (226,330 ghost cycles correctly classified).
