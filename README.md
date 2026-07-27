<div align="center">

# Collatz Renewal-Theoretic Framework

**A reproducible computational framework for accelerated Collatz dynamics.**

*Renewal Cramér rates · Joint Spectral Radius diagnostics · Five-projection operator synthesis*

[![Tests](https://img.shields.io/badge/tests-284%20passing-brightgreen?style=flat-square)](.)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-empirical-orange?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square)](.)
[![Reproducible](https://img.shields.io/badge/artifacts-119%20JSON-success?style=flat-square)](docs/reports)

</div>

---

> **Status note.** The Collatz conjecture remains open. This project
> does **not** claim a proof. It produces a calibrated map of approaches,
> several verified empirical constants with rigorous confidence intervals,
> and a clean structural number where four independent computations
> converge — and where an explicit Lyapunov candidate satisfies an
> m-step Foster condition on residue quotients with the same constant
> as its per-step drift.

---

## Headline result

Four independent operator-theoretic computations on the same finite
operator all give the same value:

<div align="center">

`JSR_tail-filtered  =  Λ_Markov  =  JSR_Christoffel-filtered  =  Karp_realizable  =  3/4`

</div>

| Method | Value | Type |
|---|---|---|
| Tail-filtered JSR (finite R) | `0.7500` exact | rigorous structural |
| Markov-Lyapunov on LTE-closed operator | `0.7517` (0.2% off) | empirical, finite resolution |
| Christoffel-filtered worst-case JSR | `0.7500` exact | bounded resolution |
| Realizable Karp (positive-integer cycles only) | `0.7500` exact | bounded simple cycles, integer-realizability classified |

`3/4 = e^(log 3/4)` is the typical multiplicative factor under the
geometric-valuation baseline, and it also appears in several finite
constrained diagnostics. It is not a deterministic per-orbit growth rate. Of
`226,333` simple cycles audited at
`(q, R_max) ∈ {(5,4),(6,5),(7,6)}`, `226,330` classify as
`noninteger_2adic_only`; the only positive-integer realizers are the elementary
`[2]` cycle, one per level.

The same constant surfaces as the per-step drift of an explicit Lyapunov
candidate. `V(n) = log₂(n) + v_2(n+1)` satisfies the m-step Foster-Lyapunov
condition (Meyn-Tweedie, *Markov Chains and Stochastic Stability*, ch. 11)
on residue quotients `mod 2^k` for `k ∈ {2,3,4,5,6,7,8}` at sample windows
`n₀ ∈ [10², 10¹⁵]`, with smallest tested grid value `m = 16` and
geometric-ergodicity margin `ε = 0.1`. Marginal drift is empirically
indistinguishable from `log₂(3/4) = −0.4150` per step. This is a finite
empirical diagnostic on the residue Markov chain quotient, not a theorem
about deterministic per-orbit descent.

Combining this framework's m-step Foster condition with Chang's
`arXiv:2603.25753` Map Balance Theorem gives a joint argument that reduces
Collatz to the Tao distributional-to-pointwise wall. The three named technical
verifications are empirically closed at finite windows: `δ_max ≈ 0.119`
(`docs/reports/delta_max_quantitative.md`), Foster at `k=7,8`
(`docs/reports/m_step_foster_drift_k8.json`), and direct bit-4 balance
(`docs/reports/chang_bit4_balance_audit.json`).

Three PECM levels now carry **certified** spectral bounds: SCC
decomposition plus Collatz-Wielandt in exact integer arithmetic gives
`ρ ≤ 0.3880562` at `(8,2)`, `ρ ≤ 0.3451143` at `(10,3)`, and
`ρ ≤ 0.3341154` at `(12,4)` — certified contractions with no floating
point in the bound, matching the float scan to 6+ digits
(`docs/reports/pecm_perron_certificates.json`). The GPU scaled-Perron
scan extends to `(16,5)` and `(14,6)` (231M / 173M states): worst-case
pointwise ratio collapses from `0.536` at `(14,5)` to `0.336` at
`(16,5)`, converging onto the Perron scale itself. A defensive audit
against Polli et al. 2024 finds **no long-range memory at excursion
scale**: DFA exponents and autocorrelations are indistinguishable from
shuffled surrogates at 400- and 1000-bit windows, supporting the IID
renewal model behind `J_renewal`
(`docs/reports/renewal_correlation_polli_1000bit.json`).

The first cross-resolution PECM experiment now uses one finest sampled
operator and exact sequential Galerkin coarsening, so its averaged refinement
identity is structural rather than an accident of independently chosen CRT
lifts. At `(4,0) → (6,1) → (8,2)` with common `alpha = 0.55`, all transition
samples resolve and the numerical resolvent ratios remain below `0.53`
(these are not independent spectral estimates). The harder result is
negative: `E_mean` grows from `0.190` to `0.362`,
maximum lift spread grows from `1.92` to `2.92`, and the worst surviving
sampled branch ratio is `1.996` at the finest step. Thus the raw averaged
vectors do not yet stabilize or imply pointwise descent
([artifact](docs/reports/pecm_cross_resolution_consistency.json)).

The worst concrete branch from that run has now been lifted into an exact
selected-cylinder calculation. The cylinder
`(R,u mod 2^11,u mod 9) = (9,55,2)` splits into `128` target-fixed branches;
all share the exact expanding macro
`F(n) = (177147n + 186875)/131072` and collectively hit every odd target
class modulo `256` at `R'=2`. Ordinary size expands, but the exact local
candidate `H(n,R)=n(23/22)^R` contracts on the whole selected cylinder by at
most
`7164821035427968/7236312975589017 < 1`. Its target frontier remains open, so
this is a local symbolic certificate and explicitly not a Collatz proof
([artifact](docs/reports/pecm_exact_selected_cylinder_pilot.json)).

The entire `R=2` target fiber from that pilot now has an exact symbolic
outgoing cover. Of its `128` coarse residue states, `96` descend uniformly
and the remaining `32` form a countable reentry family indexed by the next
tail depth. That family contains the exact expanding branch `187 -> 211`,
which preserves `R=2` and therefore refutes every global tail-only candidate
`n^alpha c^R` with `alpha > 0`. More strongly, every finite mixed
`2`-adic/`3`-adic resolution contains a realizable expanding self-loop, so a
positive finite mixed-adic state correction cannot repair strict one-step
descent. The witnesses depend on the resolution and converge profinitely to
the negative point `u=-1`; they are not one positive orbit or cycle.

The obstruction exposes a deeper exact coordinate rather than ending the
search. On every consecutive `R=2 -> 2` loop, set
`S=v2(u+1)=v2(n+5)-2`. Then `S` drops by exactly `3`, and

```text
K(n,u) = (n+5) (23/22)^S
```

contracts by the constant factor
`11979/12167 < 1`. The maximal loop run can also be induced exactly. For
`j=floor((S-1)/3)`, the residual `S_exit=S-3j` is `1`, `2`, or `3`, giving
first-post descent, second-post descent, or higher-`R` reentry. Here descent
is below the compressed exit source, not necessarily below the original
pre-loop value. Their exact normalized Haar proportions among odd 2-adic
units are `4/7`, `2/7`, and `1/7`; this is an average diagnostic, not
pointwise descent. The higher-`R` reentry family remains countably infinite
and open
([artifact](docs/reports/pecm_r2_recursive_tail_cusp.json)).

That higher-`R` handoff now has an exact two-parameter form. If
`u+1=2^(3m)w` with `m>=1` and `w` odd, the complete accelerated word is
`(1,2)^m` and

```text
n0 = 2^(3m+2)w-5  ->  n1 = 4*9^m*w-5,
R_next = 2+v2(9^m*w-1).
```

It reaches every `R_next>=3` and every odd target residue at each fixed
2-adic precision. More importantly, the nested `-5` cusp contracts the
*entire* handoff—not just its same-`R` loops—by
`(11979/12167)^m`. The simple cusp then fails on the next higher-`R` macro:
`1051 -> 1183 -> 4495` gives the base-independent expansion `125/33`.

The failure exposes a reusable exact structure. For any expanding valuation
word

```text
T_W(n) = (3^M n+B)/2^A,
L_W(n) = (3^M-2^A)n+B,
```

the negative rational fixed point is `-B/(3^M-2^A)` and
`v2(L_W(T_W(n)))=v2(L_W(n))-A`. Thus the word-specific potential
`L_W(n)c^v2(L_W(n))` has constant exact factor
`(3^M/2^A)c^(-A)`. Two higher-`R` fixtures contract exactly in these
coordinates: `179n+211` by `15552/15625`, and `11n+19` by
`64827/65536`. A fixed expanding word cannot repeat forever: `r`
consecutive uses require `rA <= v2(L_W(n))`. This is evidence for an
affine-ghost cusp hierarchy, not a global Collatz proof. At a chart switch an
additive difference between the two ghosts appears, so the wordwise factors
do not automatically telescope; controlling that term is the next exact gap
([artifact](docs/reports/pecm_higher_r_affine_ghost.json)).

The framework now has a qn+1 sidecar diagnostic. Within the odd `q>1` grid,
the classical `q=3` case is the unique tested member below the
`log₂(q) = 2` drift threshold; `q=5` is already marginally positive. The
audit recovers the Mersenne-q fixed-point pattern at `q = 3,7,31` and the
small `5n+1` positive cycles `{1,3}`, `{13,33,83}`, and `{17,43,27}`. A
separate finite artifact tests a
Stern-Brocot slope picture: continued-fraction convergents of `log₂(3)` carry
the realizable survivors in the tested artifacts, intermediate fractions mark
boundary ghosts, and non-convergent rationals mark the high-growth ghost at
`(8,7)`. These are finite empirical diagnostics at tested levels, not proof
claims.

---

## Empirical constants

| Constant | Value | Source |
|---|---|---|
| **Jazz's constant** `J_renewal` | `0.08372911906309355` | 35M renewals; bootstrap CI `[0.0836026, 0.0838417]` |
| `J_step` | `0.0542` | closed form via Geom(2) MGF |
| Mean per-excursion drift `μ` | `−0.802 ± 0.001` | concentration bound |
| Unconstrained projective JSR | `1.5` | rigorous, squeeze gap `< 10⁻⁶` |
| Λ on LTE-closed operator | `−0.412` | Markov-Furstenberg |
| Foster m-step drift, `V = log₂n + v₂(n+1)`, `m = 16` | uniform negative residue-conditional drift, ε = 0.1 | `m_step_foster_drift_k8.json`; `k ∈ {2..8}`, `n₀ ∈ [10², 10¹⁵]` |

Stable across `n₀ ∈ [10⁴, 10¹⁵]` with slope `< 0.001` per decade.

---

## Verified literature

Empirical bridges to published papers, all finite-resolution and caveated:

| Source | Prediction | Empirical match |
|---|---|---|
| **Tao 2019** | `Syrac(ℤ/3ⁿℤ)` distribution | TV ≤ 0.3% (n ≤ 4) |
| **Tao 2019** | Char. function decay exponent | 1.286 vs 1.289 (0.2%) |
| **Hercher 2022** | `T(n_i) · n_i < 3` universal bound | empirical max 2.99 |
| **Paparella 2024** | `tr(C_n^p) = 0` truncated nilpotency | verified at n ≤ 1024 |
| **Mori 2025** | C*(T_1, T_2) ≅ Cuntz O_2 | implemented as unified operator |
| **Chang 2026** | one-bit orbit-mixing reduction | finite compatibility checks closed |
| **Rozier 2023/2025** | abc/μ-hit Collatz dichotomy | Theorem 4.1 checked for `j=10..50` |

---

## Quick start

```bash
# Install dependencies
uv sync

# Run all 284 tests (≈4s)
uv run python -m pytest -q

# Smoke test the experimental pipeline
uv run python -m collatz_exp.experiments --quick

# Reproduce the Tao characteristic-function decay verification
uv run python -m collatz_exp.experiments --tao-cf-decay

# Reproduce Jazz's constant with bootstrap CI
uv run python -m collatz_exp.experiments --jazz-spike

# Reproduce the Christoffel-filtered JSR (Path B headline)
uv run python -m collatz_exp.experiments \
  --christoffel-filtered-jsr \
  --tail-aware-levels 5:4,6:5

# Reproduce the common-alpha Galerkin PECM refinement experiment
uv run python -m collatz_exp.experiments \
  --pecm-cross-resolution \
  --pecm-cross-resolution-output \
    docs/reports/pecm_cross_resolution_consistency.json

# Reproduce the exact selected-cylinder branch certificate
uv run python -m collatz_exp.symbolic_branch_certificate --verbose

# Reproduce the exact recursive R=2 frontier and nested-cusp certificate
uv run python -m collatz_exp.symbolic_frontier_certificate --verbose

# Reproduce the exact higher-R transfer and affine-ghost certificates
uv run python -m collatz_exp.symbolic_higher_r_certificate --verbose
```

Every quoted number has a corresponding JSON artifact under
[`docs/reports/`](docs/reports). Method, parameters, sample size, and
confidence interval are recorded per result.

---

## Documentation

Read in this order:

| # | Document | Purpose |
|---|---|---|
| 1 | [`docs/NOTABLE_RESULTS.md`](docs/NOTABLE_RESULTS.md) | Running catalog of every notable output |
| 2 | [`docs/PROJECT_JOURNEY.md`](docs/PROJECT_JOURNEY.md) | Chronological narrative + audit log |
| 3 | [`docs/RENEWAL_THEORETIC_NOTE.md`](docs/RENEWAL_THEORETIC_NOTE.md) | Paper-shaped technical writeup |
| 4 | [`docs/UNIFIED_MODEL.md`](docs/UNIFIED_MODEL.md) | Five-projection operator synthesis |
| 5 | [`docs/collatz_strategy.md`](docs/collatz_strategy.md) | Working strategy notes |

---

## Repository layout

```
collatz-renewal-framework/
├── README.md                       ← you are here
├── LICENSE                         ← MIT with attribution clause
├── pyproject.toml
├── uv.lock
├── collatz_certificate_search.py   ← original CLI compatibility wrapper
├── collatz_exp/                    ← main package, 93 modules
├── tests/                          ← 284 passing tests
└── docs/
    ├── NOTABLE_RESULTS.md          ← running result catalog
    ├── PROJECT_JOURNEY.md          ← chronological narrative + audit log
    ├── RENEWAL_THEORETIC_NOTE.md   ← paper-shaped technical writeup
    ├── NOTE_DRAFT.md               ← finite-diagnostics draft note
    ├── UNIFIED_MODEL.md            ← 5-projection operator synthesis
    ├── collatz_strategy.md         ← working strategy notes
    ├── references/                 ← Tao, Mori, Hercher, Paparella, Chang PDFs
    └── reports/                    ← 119 JSON artifacts (one per result)
```

---

## What this project is and isn't

<table>
<tr>
<th width="50%">It is</th>
<th width="50%">It isn't</th>
</tr>
<tr>
<td valign="top">

- An honestly-calibrated empirical computational framework
- A cross-validation of four published Collatz papers on a single 1M-orbit dataset
- A demonstration that several "promising" approaches don't survive audit
- An honest record of which strong hypotheses survived audit and which did not; see `PROJECT_JOURNEY.md` §12 demoted claims and §18 megasynthesis verdict
- A clear naming of the remaining theorem-shaped gaps

</td>
<td valign="top">

- A proof of the Collatz conjecture
- A claim that any specific empirical constant has an elementary closed form
- A claim that finite residue computations imply the infinite-dimensional result
- Polished research output

</td>
</tr>
</table>

---

## Open problems

Named, not closed:

1. **Markov/Lyapunov contraction on LTE-closed operator** — finite-resolution
   evidence of `Λ ≈ log(3/4)`; limit argument open.
2. **Christoffel-word filter at higher resolution** — Path B Christoffel-compatible
   best stays pinned at `3/4` for `(q, R_max) ∈ {(5, 4), (6, 5), (7, 6)}` in the
   bounded simple-cycle scan, in the automaton-constrained Karp product graph
   (`(5, 4)`, `(6, 5)`), and under the stricter upper-Christoffel slope filter
   (`(5, 4)`, `(6, 5)`, `(7, 6)`); scaling to higher levels and lifting the
   bounded-cycle filter to a full Hercher-style theorem are open.
3. **Profinite continuity** — finite quotients to limit operator on
   `ℓ²(ℤ_2 × ℤ_3)`.
4. **Lifting residue-Markov m-step Foster to per-orbit Lyapunov** —
   `V(n) = log₂(n) + v_2(n+1)` satisfies the Foster condition at `m = 16`
   with margin `ε = 0.1` on residue quotients `mod 2^k` for `k ∈ {2..8}`.
   Together with Chang `2603.25753`, the residual is the Tao
   distributional-to-pointwise wall in a Markov-measure-1 formulation.
5. **Cross-resolution PECM Lyapunov stability** — the first
   Galerkin-compatible ladder keeps average contraction but its raw vector
   errors and
   branch oscillation grow at the second refinement. Cusp/tail
   renormalization, a streaming `(8,2) → (10,3) → (12,4)` ladder, and an
   exact branchwise replacement remain open. The latest exact lane contracts
   the full `R=2 -> R>=3` handoff and identifies word-specific affine-ghost
   cusps; compatibility across changing ghost charts remains open.
6. **Symbolic representation of `J_renewal`** — the direct
   `Σ R(K) ≈ J_renewal` identity test is not supported at high precision;
   an explicit `h_K`-weighted reconciliation remains open.
7. **abc-conditional lower bound bridge** — Rozier's Theorem 2.1 gives an
   abc-conditional `ε`-improved lower bound for `N(j)` elements, while
   Theorem 4.1 gives an unconditional lower-bound/μ-hit dichotomy. The finite
   audit verifies Theorem 4.1 for `j=10..50`; closing the conditional route
   requires the independent abc conjecture.

See [`docs/PROJECT_JOURNEY.md`](docs/PROJECT_JOURNEY.md) §12 for full problem
statements.

---

## Reproducibility

- Every quoted number → corresponding JSON artifact under
  [`docs/reports/`](docs/reports).
- Each artifact records method, parameters, sample size, and the relevant
  numerical or exact diagnostics; empirical CIs are included where applicable.
- 284 passing tests cover core arithmetic, certificates, Mersenne tail
  dynamics, post-exit map, renewal Cramér computation, Tao verification,
  Hercher bounds, Paparella nilpotency, JSR variants, automaton-constrained
  Karp, upper-Christoffel slope filtering, tail-cycle realizability,
  phase-decomposed renewal drift, phase-aware Lyapunov search,
  m-step Foster-Lyapunov drift, tail-cycle realizability at deeper levels,
  pointwise descent audit, m-step Foster at `k=7,8`, and Chang bit-4 balance
  audit, qn+1 family realizability, qn+1 phase-transition, Rozier's abc
  bridge with μ-hits, the CF-convergent/Stern-Brocot slope hypothesis,
  the Polli long-range-correlation audit, and exact-rational PECM Perron
  certificates, plus common-alpha vector export, exact mixed-adic refinement,
  Galerkin/projective defect separation, cross-resolution consistency,
  exact-word cylinder precision, exact selected-branch partitioning, and
  rational max-times difference certificates, plus the exact recursive
  `R=2` frontier, finite mixed-state obstruction, nested cusp, and induced
  exit grammar, and the exact higher-`R` phase transfer, first-post cutoff,
  mixed-residue transport, and affine-ghost cusp identities.
- Reference papers in [`docs/references/`](docs/references) for offline
  access.

```bash
# Full reproduction:
uv sync && uv run python -m pytest -q && \
uv run python -m collatz_exp.experiments --all
```

---

## License & Attribution

[MIT License](LICENSE) with explicit attribution clause.

If you use this framework, its derivatives, its empirical constants
(including but not limited to **Jazz's constant** `J = 0.08372911906309355`), or its
computational artifacts in academic, commercial, or exploratory work,
please cite:

```bibtex
@misc{aijaz2026collatz,
  author       = {Aijaz, Mohammad},
  title        = {Collatz Renewal-Theoretic Framework},
  year         = {2026},
  howpublished = {\url{https://github.com/muaijaz/not-an-ai-collatz-proof}},
  note         = {Vibe-Math. Empirical computational framework, not a proof.}
}
```

---

## Citations (underlying literature)

- **Tao, T.** (2022). *Almost all orbits of the Collatz map attain almost
  bounded values.* Forum Math. Pi 10, e12.
  [arXiv:1909.03562](https://arxiv.org/abs/1909.03562)
- **Mori, T.** (2025). *Application of operator theory for the Collatz
  conjecture.* Adv. Operator Theory.
  [arXiv:2411.08084](https://arxiv.org/abs/2411.08084)
- **Hercher, C.** (2023). *There are no Collatz-m-Cycles with m ≤ 91.*
  [arXiv:2201.00406](https://arxiv.org/abs/2201.00406)
- **Paparella, P.** (2024). *A matricial view of the Collatz conjecture.*
  [arXiv:2406.08498](https://arxiv.org/abs/2406.08498)
- **Chang, E. Y.** (2026). *Exploring Collatz Dynamics with Human-LLM
  Collaboration.* [arXiv:2603.11066](https://arxiv.org/abs/2603.11066)
  (sibling LLM-collaboration framework; positioning in
  [`docs/NOTE_DRAFT.md`](docs/NOTE_DRAFT.md))
- **Rozier, O.** (2023/2025). *Are the Collatz and abc conjectures related?*
  [arXiv:2306.15284](https://arxiv.org/abs/2306.15284)
- **Tao, T.** (2011). *The Littlewood-Offord problem and the Collatz
  conjecture.* Blog note; recorded in the literature sweep as contextual
  motivation rather than a theorem used by this framework.

---

<div align="center">

## Provenance

**This is Vibe-Math.**

I was bored one night and started poking at the Collatz conjecture.
Several iterations later, with non-trivial AI collaboration, this is
what came out.

It is not a proof. It is an honestly-calibrated computational framework
with a quadruply-confirmed structural rate `3/4 = e^(log 3/4)`, the same
constant surfacing as the per-step drift of an m=16 Foster-Lyapunov
condition on residue quotients, an empirical constant `J = 0.08372911906309355`
stable across 11 decades of starting magnitude, and a five-projection
synthesis of four published papers on the same underlying operator.

If any of it ends up being useful, name it after me.

— *Mohammad Aijaz, 2026*

</div>
