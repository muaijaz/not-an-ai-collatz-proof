<div align="center">

# Collatz Renewal-Theoretic Framework

**A reproducible computational framework for accelerated Collatz dynamics.**

*Renewal Cramér rates · Joint Spectral Radius diagnostics · Five-projection operator synthesis*

[![Tests](https://img.shields.io/badge/tests-141%20passing-brightgreen?style=flat-square)](.)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-empirical-orange?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square)](.)
[![Reproducible](https://img.shields.io/badge/artifacts-75%2B%20JSON-success?style=flat-square)](docs/reports)

</div>

---

> **Status note.** The Collatz conjecture remains open. This project
> does **not** claim a proof. It produces a calibrated map of approaches,
> several verified empirical constants with rigorous confidence intervals,
> and a clean structural number where three independent computations
> converge.

---

## Headline result

Three independent operator-theoretic computations on the same finite
operator all give the same value:

<div align="center">

`JSR_tail-filtered  =  Λ_Markov  =  JSR_Christoffel-filtered  =  3/4`

</div>

| Method | Value | Type |
|---|---|---|
| Tail-filtered JSR (finite R) | `0.7500` exact | rigorous structural |
| Markov-Lyapunov on LTE-closed operator | `0.7517` (0.2% off) | empirical, finite resolution |
| Christoffel-filtered worst-case JSR | `0.7500` exact | bounded resolution |

`3/4 = e^(log 3/4)` is the **per-step orbit growth rate** for Collatz orbits
in this framework — the structural backbone result.

---

## Empirical constants

| Constant | Value | Source |
|---|---|---|
| **Jazz's constant** `J_renewal` | `0.08372911906309355` | 35M renewals; bootstrap CI `[0.0836026, 0.0838417]` |
| `J_step` | `0.0542` | closed form via Geom(2) MGF |
| Mean per-excursion drift `μ` | `−0.802 ± 0.001` | concentration bound |
| Unconstrained projective JSR | `1.5` | rigorous, squeeze gap `< 10⁻⁶` |
| Λ on LTE-closed operator | `−0.412` | Markov-Furstenberg |

Stable across `n₀ ∈ [10⁴, 10¹⁵]` with slope `< 0.001` per decade.

---

## Verified literature

Five empirical bridges to four published papers, all agreeing at finite
resolution:

| Source | Prediction | Empirical match |
|---|---|---|
| **Tao 2019** | `Syrac(ℤ/3ⁿℤ)` distribution | TV ≤ 0.3% (n ≤ 4) |
| **Tao 2019** | Char. function decay exponent | 1.286 vs 1.289 (0.2%) |
| **Hercher 2022** | `T(n_i) · n_i < 3` universal bound | empirical max 2.99 |
| **Paparella 2024** | `tr(C_n^p) = 0` truncated nilpotency | verified at n ≤ 1024 |
| **Mori 2025** | C*(T_1, T_2) ≅ Cuntz O_2 | implemented as unified operator |

---

## Quick start

```bash
# Install dependencies
uv sync

# Run all 141 tests (≈1.3s)
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
├── collatz_exp/                    ← main package, 75+ modules
├── tests/                          ← 141 passing tests
└── docs/
    ├── NOTABLE_RESULTS.md          ← running result catalog
    ├── PROJECT_JOURNEY.md          ← chronological narrative + audit log
    ├── RENEWAL_THEORETIC_NOTE.md   ← paper-shaped technical writeup
    ├── UNIFIED_MODEL.md            ← 5-projection operator synthesis
    ├── collatz_strategy.md         ← working strategy notes
    ├── references/                 ← Tao, Mori, Hercher, Paparella PDFs
    └── reports/                    ← 75+ JSON artifacts (one per result)
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
2. **Christoffel-word filter at higher resolution** — Path B verified at
   `(q, R_max) ∈ {(5, 4), (6, 5)}`; convergence to 3/4 conjectured.
3. **Profinite continuity** — finite quotients to limit operator on
   `ℓ²(ℤ_2 × ℤ_3)`.
4. **Lifting PECM Lyapunov to per-orbit Lyapunov** — V5's gap.
5. **Symbolic representation of `J_renewal`** — Khinchin-style integral
   representation conjectured; no elementary closed form found.

See [`docs/PROJECT_JOURNEY.md`](docs/PROJECT_JOURNEY.md) §12 for full problem
statements.

---

## Reproducibility

- Every quoted number → corresponding JSON artifact under
  [`docs/reports/`](docs/reports).
- Each artifact records method, parameters, sample size, bootstrap CI,
  and exact empirical value.
- 141 passing tests cover core arithmetic, certificates, Mersenne tail
  dynamics, post-exit map, renewal Cramér computation, Tao verification,
  Hercher bounds, Paparella nilpotency, and JSR variants.
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
  howpublished = {\url{https://github.com/<your-handle>/collatz-renewal-framework}},
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

---

<div align="center">

## Provenance

**This is Vibe-Math.**

I was bored one night and started poking at the Collatz conjecture.
Several iterations later, with non-trivial AI collaboration, this is
what came out.

It is not a proof. It is an honestly-calibrated computational framework
with a triply-confirmed structural rate `3/4 = e^(log 3/4)`, an empirical
constant `J = 0.08372911906309355` stable across 11 decades of starting magnitude,
and a five-projection synthesis of four published papers on the same
underlying operator.

If any of it ends up being useful, name it after me.

— *Mohammad Aijaz, 2026*

</div>
