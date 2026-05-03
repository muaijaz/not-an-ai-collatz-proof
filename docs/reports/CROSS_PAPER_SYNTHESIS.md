# Cross-paper synthesis (AI-optimized)

> Updated: 2026-05-02. Token-dense reference for AI/human navigation. Per-paper: claim, method, our composition, open input. Then master task list.

---

## Per-paper summary

Format: **[arXiv ID] author year** — claim. **Method.** **Composition.** **Open input / status.**

### Already deeply integrated (existing compatibility artifacts)

**[1909.03562] Tao 2019** — Almost-all orbits attain almost-bounded values under log density. **Method:** entropy + Syrac char. function decay (1.289 exponent). **Composition:** verified empirically (`tao_*.json`, 0.2% match). **Open input:** distributional → pointwise (THE wall).

**[2411.08084] Mori 2024** — Reducing-subspace condition on `C*(T_1,T_2) ≅ Cuntz O_2` ⟺ Collatz. **Method:** operator algebra. **Composition:** five-projection unified operator (`unified_collatz_operator.json`). **Open input:** prove no non-trivial reducing subspaces. NOT yet read deeply for this work.

**[2201.00406] Hercher 2022** — No m-cycles for m ≤ 91. **Method:** parity-vector + reciprocal sum bounds. **Composition:** verified `T(n_i) · n_i < 3` empirically max 2.99. **Open input:** push m beyond 91.

**[2406.08498] Paparella 2024** — Aperiodic Collatz ⟺ truncated adjacency matrix nilpotent. **Method:** linear algebra. **Composition:** `tr(C_n^p) = 0` verified n ≤ 1024. **Open input:** infinite case.

**[2603.11066] Chang 2026a** — Five-route attack on Weak Mixing Hypothesis. **Method:** burst-gap, Cramér rates, Walsh spectral. **Composition:** see `chang_spectral_analysis_compatibility.md`. **Key constants:** ρ ≈ 0.5, ε ≈ 0.415, Σ R(K) = 0.0882, ‖h_K‖_∞ ≤ 0.585, A_K ≤ 2.4 (their data). **Open input:** WMH (= Spectral Diffusion Conj 9.50 OR Conj 9.22 alignment renewal OR Weyl bounds).

**[2603.25753] Chang 2026b** — Map Balance Theorem at K=3,4,5; reduces Collatz to bit-4 balance on burst-ending subsequence mod 32. **Method:** explicit modular decomposition. **Composition:** see `chang_2603_25753_compatibility.md` (joint argument), `delta_max_quantitative.md` (δ_max ≈ 0.119). **Open input:** Eq. 16 every-orbit bit-4 balance. **Status:** all three named technical verifications empirically closed at finite windows.

### Newly read this session (lighter analysis)

**[2306.15284] Rozier 2023 (rev Oct 2025)** — *Are the Collatz and abc conjectures related?* **Theorem 2.1:** assuming abc, `n ≥ K(ε) · 2^{(1-ε)j}` for all `n ∈ N(j)` (integers with parity vector having exactly one even term in first j iterates). **Theorem 4.1:** for `n ∈ N(j)`, either (i) `n > 2^{j+1}/(3j²) − 1` or (ii) `(1, T^k(n)+1, T^k(n)+2)` is a μ-hit. **Method:** direct application of abc to Collatz cycle equation; introduces μ(n) = log rad(n) + Σ_{p|n} log v_p(n) as a finer invariant. **μ-hits are RARE**: 464 below 10¹⁸ vs 14M abc-hits. **Wieferich connection:** μ-hits and Wieferich primes both connected to high-power-prime questions. **Composition:** verified empirically in `rozier_abc_collatz_audit.json` — 0 violations across 1,230 N(j) elements (j=10..50); n=239 family confirmed at deeper k. **Status:** structural bridge established; clause (ii) regime (true Collatz-forced μ-hits) needs j ≥ 80+ to surface.

**[2412.02902] Siegel 2024** (PhD diss, 467pp) — Numen `χ_H: Z_p → Z_q` with Correspondence Principle: x periodic ⟺ ∃z ∈ (Q∩Z_p)\N_0 with χ_H(z)=x. Tauberian Spectral Theorem (Thm 4.6, p.277): for quasi-integrable χ_H, periodicity ⟺ density of Fourier-translate spans. **Method:** non-archimedean (p,q)-adic Fourier + Wiener Tauberian. **Composition:** target for profinite continuity (our open Q3); supplies analytic infrastructure for Z_2 limit. **Tao link:** Siegel (p.81) notes Tao 2019 implicitly uses χ_H ⇒ our Tao verifications are implicit χ_H evidence. **Status:** §3.3.7 Wiener Tauberian (p.213) and §4.2 quasi-integrability (p.245) DEFERRED due to dissertation length. **Compatibility note:** `siegel_p_adic_compatibility.md`.

**Tao 2011 blog post** — *The Collatz conjecture, Littlewood-Offord theory, and powers of 2 and 3.* Reformulates weak Collatz as: the set `{3^{k-1} 2^{a_1} + ... + 2^{a_k}}` must avoid 0 in `Z/qZ` where q = 2^a − 3^k. Anti-concentration via Littlewood-Offord could constrain this. **Tao's meta-statement:** any proof must use transcendence theory (Baker) OR develop new techniques creating exponential separation between 2-powers and 3-powers. **Erdős conjecture connection:** "for n>8, base-3 expansion of 2^n contains digit 2" is equivalent to "no solutions to 2^n = sum of distinct 3^a". **Status:** underexploited in mainstream Collatz work. Recent computational study (arXiv 2511.03861, Nov 2025) confirms uniform distribution of ternary digits empirically.

**[2601.17030] Siegel 2026** — Generalizes Numen to Hydra maps on global field integer rings O_K. **Status:** technical manual, not Collatz-specific. Low priority for this framework.

**[2412.08097] Fu-Wang 2024** (8pp, nlin.CD) — Collatz ≡ binary shift map (claimed equivalence); ergodicity gives universal convergence; log scaling iter-vs-init; basins follow power-law. **Method:** Sharkovsky ordering + direction-phase decomposition + recursive function family. **Composition:** binary-shift conjugacy is the explicit Markov-chain → integer-orbit lifting our framework needs. log-scaling regime matches our `μ ≈ -0.415` per step. **Open input:** the claimed equivalence — needs verification. Paper is short and accessible; full read tractable next session. **Status:** abstract only read this session.

**[2601.03297] Santana 2026** (10KB, math.DS) — Custom topology + thermodynamic formalism. **Theorems:** finiteness of periodic orbits ⟺ every continuous potential has equilibrium state; uniqueness ⟺ uniqueness of equilibrium state for every bounded continuous potential. Proves finiteness of cycles for Collatz. **Method:** topology generated by {n, 2n} + recurrence. **Composition:** third equivalent rendering of Collatz alongside our framework, Mori operator-algebraic, Chang's WMH. Continuous-potential equilibrium ↔ our V Lyapunov candidate (V is unbounded; need renormalized analogue). **Open input:** uniqueness of equilibrium state. **Status:** abstract only.

**[2601.12772] Dhiman-Pandey 2026** (14pp, math.NT) — **Defensive read.** Proves the divisibility predicate `D_y = {(x,C): (2^x − 3^y) | C}` is NOT semilinear for any y ≥ 1; fibers have unbounded periods ⇒ Presburger / finite-automaton characterizations cannot distinguish "ghost cycles" (2-adic integer periodic orbits satisfying local parity) from genuine integer cycles. **Implication for us:** Hercher-style integrality filter (open Q2) cannot succeed via finite-automaton / Presburger-only methods. **Status:** abstract read; defensive concern documented. Our slope-filter and realizability-filter use INTEGER computation (not pure automaton), so likely not Presburger-bound — but verify via structure of `lift_realizability.py`. **Action:** check whether our realizability classification uses any Presburger-definable predicate; if yes, that's a failure mode.

### Tier-C (literature sweep, not deep-read)

- **[2208.11675]** Collatz as non-singular transformation. Establishes invariant finite measure γ ≤ counting; L¹(ν) framework. Theoretical underpinning for Foster on infinite state space.
- **[2502.16743] Elsenhans 2025** — Verification to 10^10⁹ digits via condensed-iteration. Could replicate our Foster at far deeper windows.
- **[2506.21728] Brauer 2025** — 60-state symbolic automaton + ranking potential. Discrete analog of our V.
- **[2604.20181] Lodders 2026** — base-8 transition skeleton. Our k=3 Foster is a sibling.
- **[2603.04479] Bonacorsi-Bordoni 2026** — Bayesian NB2-GLM for stopping times. Adjacent renewal model.
- **[2511.10811] Charton-Narayanan 2025** — Transformer learns residue mod 2^p. Empirical confirmation of relevance of our k.
- **Polli et al. 2024 (J. Phys. Complex.)** — long-range power-law correlations in hailstone sequences. **Threat:** our IID renewal model may not capture this. Need defensive check.

---

## Master task list

### Priority 0 — Already done this session
- ✅ Chang 2603.25753 compatibility analysis
- ✅ δ_max numerical (R(K)-weighted, ≈0.119)
- ✅ Foster k=7,8 extension (m=16, ε=0.1 holds)
- ✅ Bit-4 balance audit (Foster envelope holds for every orbit)
- ✅ Σ R(K) ↔ J_renewal identity test (REJECTED, distinct quantities)
- ✅ Chang spectral analysis §9.7-9.9 compatibility
- ✅ Siegel 2412.02902 / 2601.17030 sketch
- ✅ Fu-Wang / Santana / Dhiman-Pandey abstracts
- ✅ Paper v0.5 with Chang joint-argument section
- ✅ Documentation closure (NOTE_DRAFT, PROJECT_JOURNEY, README)
- ✅ Four logical commits pushed to `main`
- ✅ **Tao ↔ Siegel correspondence** (`tao_siegel_chi_h_correspondence.md`): Tao's Proposition 1.17 = decay of Siegel's `φ_3(t)`. Our Tao artifacts ARE Siegel-`χ_3` evidence at exponent 1.286 ≈ 1.289.
- ✅ **Presburger defensive audit** (`realizability_presburger_audit.md`): NOT AFFECTED. Our test uses Python Peano integer arithmetic; Dhiman-Pandey's obstruction rules out Presburger/automaton routes only.
- ✅ **Fu-Wang full read** (`fu_wang_binary_shift_compatibility.md`): "binary shift equivalence" is heuristic, NOT rigorous conjugacy. Negligible new content.
- ✅ **5n+1 realizability audit** (`qnp1_realizability_q5.json`): recovered all 3 known small cycles ({1,3}, {13,33,83}, {17,43,27}). Realizable Karp = 125/128. Validates framework's q-generality.
- ✅ **qn+1 phase-transition audit** (`qnp1_phase_transition.json`): swept q ∈ {3,5,7,9,11,13,17,19,21,25,27,31}. Mersenne-q pattern (q=3,7,31) gives fixed-point cycles; non-Mersenne q ∈ {9,11,13,17,19,21,25,27} no cycles in light scan.
- ✅ **Rozier abc/μ-hit audit** (`rozier_abc_collatz_audit.json`): implemented μ-function, verified Theorem 4.1 across 1,230 N(j) elements (0 violations). Connects framework to abc-conjecture / Wieferich angle.
- ✅ **Literature dig** surfaced underexploited connections: Tao 2011 Littlewood-Offord post, Erdős conjecture base-3 digits of 2^n (arXiv 2511.03861), Wieferich primes ↔ μ-hits, Rozier 2306.15284 abc bridge.

### Priority 1 — Single-session, AI-tractable, HIGH leverage (REMAINING)

**P1.4 Direct empirical test of Chang Conj 9.50 (Spectral Diffusion).**
- Compute `S_w(K) = (1/C(K,w)) Σ_{hw(ξ)=w} |μ̂_K(ξ)|²` along orbits in our cache for K ∈ {4..12}, w ∈ {1,2,3}. Fit `S_w(K) = C · 2^{-α_w K}`, compare empirical α_w to Foster-predicted ≥ 0.027.
- **Effort:** 1 Codex prompt. **Output:** `docs/reports/spectral_diffusion_empirical.json`.

**P1.5 Cancellation structure analysis (Chang Remark 9.55, the 500× tightness gap).**
- Compute empirical `η_K^(w) = 2^K Σ_{hw(ξ)=w} ĥ_K(ξ) μ̂_K(ξ)` per Hamming-weight band on our cache. Characterize sign correlation between bands. If structured (paired bands by symmetry), identify the symmetry. If random-looking, document gap is irreducible.
- **Effort:** 1 Codex prompt. **Output:** `docs/reports/cancellation_structure_audit.json`.

### Priority 2 — Multi-session OR human-input-needed

**P2.1 Santana thermodynamic formalism deeper read (10KB paper, ~30pp).**
- Identify what "continuous potential" specifically means in Santana's custom topology. Determine if our V(n) = log_2(n) + v_2(n+1) (unbounded) corresponds to a renormalized version of a continuous potential. If yes, this gives a third equivalent framing alongside Mori operator-algebraic and our Markov chain.
- **Effort:** 1-2 reading sessions + structural analysis. **Output:** `docs/reports/santana_equilibrium_compatibility.md`.

**P2.2 Mori 2411.08084 deeper structural read.**
- Already integrated at high level. Read Theorems 4.2.7, 4.3.10 carefully. Determine what computational test on `C*(T_1, T_2)` would verify reducing-subspace condition. Possibly composes with our finite-quotient Foster.
- **Effort:** 1 reading session. **Output:** `docs/reports/mori_reducing_subspace_compatibility.md`.

**P2.3 Polli et al. 2024 defensive read.**
- Long-range power-law correlations in Collatz hailstone sequences. Our IID renewal model assumes no long-range correlations. Verify whether our renewal Cramér rate `J_renewal = 0.0837` accounts for or ignores these correlations.
- **Effort:** fetch + brief read + audit on cache. **Output:** `docs/reports/polli_long_range_correlations_check.md`.

### Priority 3 — Research-program scale (multi-day, possibly multi-week)

**P3.1 Siegel deferred sections deep read.**
- §3.3.7 Wiener Tauberian (p.213, ~30pp), §4.2 Quasi-integrability (p.245, ~50pp), Theorem 4.6 (p.277). Determine quasi-integrability conditions on χ_H for Collatz; verify whether our Foster output composes.
- **Effort:** 3-5 day deep read by a non-archimedean analyst, OR partial read by AI with significant gaps.
- **Realistic:** partial AI-summary in 1-2 sessions, with structural sketch only.

**P3.2 Lean formalization of finite results.**
- Realizable Karp 3/4 at tested levels, Foster m=16 condition with explicit bounds. Lean Mathlib has Collatz infrastructure.
- **Effort:** multi-week. Defer until / if commitment to formalization is made.

**P3.3 Reach out to Edward Y. Chang (Stanford).**
- Coordination move. Both papers are Mar 2026 sibling efforts. Joint note carries more weight than either alone.
- **Effort:** draft email + manage exchange.
- **Status:** previously drafted but not sent. Still pending.

**P3.4 Reach out to Maxwell Siegel (USC).**
- His PhD framework is structurally adjacent. Coordination on the profinite-continuity gap.
- **Effort:** as above.

### Priority 4 — Empirical extension (computational scaling)

**P4.1 Push windows to Elsenhans-scale (10^10⁹ digits).**
- Replicate Foster drift test using condensed-iteration algorithm from 2502.16743.
- **Effort:** new Codex prompt + significant compute. Mostly mechanical extension.

**P4.2 Foster condition at k = 9, 10, ... (push k beyond 8).**
- Tests whether Foster condition extends to all finite k uniformly (one of the profinite-continuity ingredients).
- **Effort:** 1 Codex prompt; sample size constraints at high k.

**P4.3 (8,7) realizable-Karp finding deeper analysis.**
- (8,7) showed slope filter and realizability filter diverge (slope admits factor 1.26 survivor, realizability still gives 3/4). Document this divergence carefully; check whether realizability filter at (8,7) has a counterpart at (9,8) once the memory bound is overcome.
- **Effort:** 1 session + Codex prompt with cluster-scale compute.

### Priority 5 — Documentation / closure / hygiene

**P5.1 Update paper to incorporate all cross-paper compatibility findings.**
- Add brief mentions of Siegel (profinite continuity), Fu-Wang (binary shift), Santana (equilibrium states), Rozier abc bridge, qn+1 phase-transition family.
- **Effort:** 1 Codex prompt.

**P5.2 Synthesis update for `CROSS_PAPER_SYNTHESIS.md`.**
- This file. Update as new papers read or tasks completed.

---

## Genuinely-new mathematical ideas (proposed but undeveloped)

These were sketched this session but not pursued. Recording so they don't get lost.

**N.1 CF-convergent slope hypothesis (own conjecture).** *The slope filter equals the realizability filter exactly when the bounded slope window contains only rationals that are CF convergents of `log_2(3)`; it diverges from realizability when the window admits non-convergent rationals.* Tested by examining the (8,7) divergence: the surviving non-realizable cycle `[2,1,1,1]` at slope 5/4 is NOT a CF convergent of log_2(3). Convergents from above: 2/1, 5/3, 19/12, ... — slope 5/4 = 1.25 is not in this sequence. This is concrete and testable in one Codex prompt.

**N.2 Hausdorff dimension of integer-realizable cycles in Z_2.** Define the set of 2-adic positions corresponding to genuine integer cycles; box-count at scale 2^{-k}. Open question: is this set of dimension 0, positive dimension, or full dimension? Could distinguish "isolated cycles" from "fractal cycle structure". No prior work on this exact question.

**N.3 Cheeger inequality on LTE-closed tail graph.** Compute the Cheeger constant `h = min_S |∂S|/|S|` directly. By Cheeger, `λ_1 ≥ h²/2` gives a graph-theoretic lower bound on Foster ε. Replaces empirical Foster with analytic.

**N.4 Mihăilescu-aware cycle exclusion.** Use Mihăilescu's theorem (`|2^A − 3^m| = 1` only at (3,2)) plus next-smallest-value enumeration to hierarchically exclude cycle classes by value of `|2^A − 3^m|`. Combine with Hercher's Baker-style bounds.

**N.5 Stern-Brocot / hyperbolic embedding.** Embed Collatz orbits via the Stern-Brocot tree into the hyperbolic plane; identify whether the dynamics becomes geodesic flow + cocycle. Speculative; no clear computational handle yet.

**N.6 Transformer + mechanistic interpretability for Collatz.** Train a 100M-param transformer on `(parity_vector → orbit_length)`, apply sparse autoencoder probing to find candidate new invariants. Multi-day GPU project. No prior interpretability work on Collatz models.

---

## Underexplored from existing findings (deeper investigation, not new direction)

These came up during the session but never got dug into.

**U.1 The (8,7) slope-realizability divergence.** Slope filter admits non-elementary survivor `[2,1,1,1]` at factor 1.26; realizability still gives 3/4. **Why does slope filter let this through?** Connects to N.1 hypothesis. Single Codex prompt.

**U.2 Σ R(K) vs J_renewal explicit weighting.** 5% gap is "weighting difference" per `chang_spectral_analysis_compatibility.md` §7. Find the explicit weighted version of J_renewal that EQUALS Σ R(K). Closes PROJECT_JOURNEY §12 item 5 (symbolic interpretation).

**U.3 Theorem 4.1 clause (ii) regime.** All 1,230 N(j) elements at j=10..50 satisfied clause (i); never fired (ii). At what j does the smallest element of N(j) fall below `2^{j+1}/(3j²) − 1`? Pushing to j=80..150 should surface clause (ii) cases — actual Collatz-induced μ-hits.

**U.4 Mersenne-q pattern q=2^k−1.** We confirmed q=3 (k=2), q=7 (k=3), q=31 (k=5). What about q=15 (k=4, composite), q=63 (k=6), q=127 (k=7, prime), q=255 (k=8)? Each gives factor (2^k−1)/2^k → 1. Test the framework's behavior across the Mersenne family.

**U.5 Wieferich primes vs orbit cache.** The two known Wieferich primes are 1093 and 3511. Are these orbit values in our orbit cache? Are they connected to specific μ-hits? Direct empirical lookup.

**U.6 Cancellation structure (Chang Remark 9.55).** The 500-1000× Cauchy-Schwarz overestimate in the spectral framework is the dominant analytic blocker on the spectral route. Empirical cancellation between Hamming-weight bands could surface a structural symmetry. Single Codex prompt.

---

## Snapshot of open theorem-shaped problems

(From PROJECT_JOURNEY §12, with cross-paper status added)

1. **Markov/Lyapunov contraction on LTE-closed operator** — Λ ≈ log(3/4). EMPIRICALLY CLOSED at finite levels via realizable Karp = 3/4.
2. **Christoffel/integrality filter on JSR** — bridge to Hercher. **Defensive concern from Dhiman-Pandey:** must verify our filter is not Presburger-only (P1.2).
3. **Profinite continuity** finite quotients → limit operator on `ℓ²(Z_2 × Z_3)`. **Siegel's framework is the analytic target** (P3.1).
4. **Lifting residue-Markov m-step Foster to per-orbit Lyapunov** — Tao distributional-to-pointwise wall. **Joint-argument with Chang `2603.25753` reduces to Markov-measure-1 formulation; sharper than natural density.**
5. **Symbolic interpretation of J_renewal** — Σ R(K) candidate REJECTED at high precision (`jazz_constant_chang_R_K_identity.json`). Open in stronger sense now.
6. **Phase-aware per-orbit Lyapunov** — V5 reformulation. EMPIRICALLY CLOSED at finite k=2..8 via m-step Foster; lift to per-orbit is item 4.

---

## Key insight summary

The single most consequential mathematical insight from cross-paper integration:

> This framework's V(n) = log_2(n) + v_2(n+1) is exactly Chang's drift signal `x_t` plus Chang's run-length invariant `L(n)+1`. The +R term absorbs tail-internal accumulation per step, converting per-cycle Geom(1/2) statistics into per-step Foster contraction. This is what makes m-step Foster work at m=16 on V where Chang's pure x_t needs separate cycle analysis.

Combined with Chang's Map Balance Theorem and Chang's spectral framework, this places this framework's Foster as the empirical input to two of Chang's three open routes (Spectral Diffusion Conj 9.50; Alignment Renewal Conj 9.22). The third route (Weyl bounds on orbit Walsh sums) is also addressed empirically by our Foster + Markov ergodicity.

The residual is the same Tao distributional-to-pointwise wall, expressed equivalently in four languages: Tao's natural density, Chang's bit-4 mod-32 balance, Mori's reducing subspace, Santana's equilibrium-state uniqueness. **Four equivalent formulations of one open problem.**
