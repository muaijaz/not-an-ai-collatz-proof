# Collatz Renewal-Theoretic Framework

A reproducible computational framework for accelerated Collatz dynamics
through renewal excursions, finite residue quotients, and probabilistic
projections of Tao's 3-adic Syracuse model.

> **Status:** The Collatz conjecture remains open. This project does not
> claim a proof. It produces a calibrated map of approaches, several
> verified empirical constants with rigorous confidence intervals, and a
> clean structural number `JSR_tail-filtered = 3/4 = e^(log(3/4))`.

## Quick start

```bash
# Run all 141 tests (~1.3s)
uv run python -m pytest -q

# Smoke test the experimental pipeline
uv run python -m collatz_exp.experiments --quick

# Reproduce the Tao characteristic-function decay verification
uv run python -m collatz_exp.experiments --tao-cf-decay

# Reproduce Jazz's constant with bootstrap CI
uv run python -m collatz_exp.experiments --jazz-spike
```

## Documentation

Read in this order:

1. **[`docs/NOTABLE_RESULTS.md`](docs/NOTABLE_RESULTS.md)** — running
   catalog of every notable output (theorems, empirical constants with
   CIs, verified literature predictions, demoted hypotheses, open
   problems). The structured reference for any future writeup.

2. **[`docs/PROJECT_JOURNEY.md`](docs/PROJECT_JOURNEY.md)** — chronological
   narrative of where the project started, what was tried, what was
   audited and demoted, and where we ended up. Honest record of dead
   ends and recalibrations.

3. **[`docs/RENEWAL_THEORETIC_NOTE.md`](docs/RENEWAL_THEORETIC_NOTE.md)** —
   paper-shaped technical writeup. Renewal Cramér rate `J = 0.0837`,
   projective JSR diagnostics, Tao verification, what's a theorem and
   what's empirical.

4. **[`docs/UNIFIED_MODEL.md`](docs/UNIFIED_MODEL.md)** — operator-theoretic
   synthesis combining Tao 2019, Mori 2024, Hercher 2022, Paparella 2024
   with the project's renewal framework into one operator
   `M = T_1 + T_2`.

5. **[`docs/collatz_strategy.md`](docs/collatz_strategy.md)** — working
   strategy notes, accumulated as the project iterated.

## Headline results

**Empirical constants with rigorous bootstrap CIs:**

| Constant | Value | CI | Interpretation |
|----------|-------|-----|----------------|
| `J_renewal` | 0.0837 | ±0.0001 | Markov-renewal Cramér rate (tail-entry partition) |
| `J_step` | 0.0542 | closed form | Per-step Cramér rate via Geom(2) MGF |
| `μ` | -0.802 | ±0.001 | Mean per-excursion log-drift |
| `JSR(unconstr.)` | 1.5 | gap < 10⁻⁶ | Worst-case projective JSR |
| `JSR(tail-filt.)` | 3/4 | exact | Worst-case = mean-case after `n=-1` exclusion |

**Verified literature predictions:**

- Tao 2019 distribution match: TV ≤ 0.3% across `n = 1, …, 4`.
- Tao characteristic function decay exponent: empirical 1.286 vs Tao's
  exact 1.289 (0.2% agreement).
- Hercher T(n_i) bound: `T(n_i) · n_i < 3` with empirical max 2.99,
  matches analytic ceiling.
- Paparella nilpotency: `tr(C_n^p) = 0` verified at `n ≤ 1024`.

## Repository layout

```
collatz-renewal-framework/
├── README.md                      ← you are here
├── collatz_certificate_search.py  ← compatibility wrapper for original CLI
├── collatz_exp/                   ← main package (~40 modules)
├── tests/                         ← 141 tests
└── docs/
    ├── NOTABLE_RESULTS.md         ← running catalog (theorems, CIs, demoted, open)
    ├── PROJECT_JOURNEY.md         ← chronological narrative + audit log
    ├── RENEWAL_THEORETIC_NOTE.md  ← paper-shaped technical writeup
    ├── UNIFIED_MODEL.md           ← five-projection operator synthesis
    ├── collatz_strategy.md        ← working strategy notes
    ├── references/                ← Tao, Mori, Hercher, Paparella PDFs
    └── reports/                   ← ~30 JSON artifacts (one per result)
```

## Reproducibility

Every quoted number in the technical documents has a corresponding JSON
artifact under `docs/reports/`. Each artifact records the method,
parameters, sample size, bootstrap CI where applicable, and the precise
empirical value. The 141-test suite covers core arithmetic, certificates,
Mersenne tail dynamics, post-exit map, renewal Cramér computation, Tao
verification, Hercher bounds, Paparella nilpotency, and JSR variants.

## What this project is and isn't

**It is:**
- An honestly-calibrated empirical computational framework.
- A cross-validation of four published Collatz papers (Tao, Mori,
  Hercher, Paparella) on a single 1M-orbit dataset.
- A demonstration that several "promising" approaches don't survive
  audit (PECM Lyapunov, structural Diophantine sparsity, ψ as rich
  potential, `log(4/3)²` as closed form for `J`).
- A clear naming of the remaining theorem-shaped gaps.

**It isn't:**
- A proof of the Collatz conjecture.
- A claim that any specific empirical constant has a closed form.
- A claim that finite residue computations imply the infinite-dimensional
  result.

## Open problems (named, not closed)

1. **Markov/Lyapunov contraction on LTE-closed operator** (in progress).
2. **Christoffel-word integrality filter on JSR** (Hercher 2025 bridge).
3. **Profinite continuity** from finite quotients to limit operator.
4. **Lifting PECM Lyapunov to per-orbit Lyapunov** (V5's gap).
5. **Symbolic representation of `J_renewal`** (Khinchin-style integral
   representation).

See `docs/PROJECT_JOURNEY.md` §12 for full problem statements.

## License & Attribution

MIT License (see [`LICENSE`](LICENSE)).

**Attribution required.** If you use this framework, its derivatives, its
empirical constants (including but not limited to **Jazz's constant** `J ≈
0.0837`), or its computational artifacts in academic, commercial, or
exploratory work, please cite the original author and this repository.

Standard MIT attribution format:

> Aijaz, M. (2026). *Collatz Renewal-Theoretic Framework.* GitHub repository.

## Citation

If you use this framework or its empirical constants, please cite this
repository and the underlying research papers in `docs/references/`:

- Tao, T. (2022). *Almost all orbits of the Collatz map attain almost
  bounded values.* Forum Math. Pi 10, e12.
- Mori, T. (2025). *Application of operator theory for the Collatz
  conjecture.* Adv. Operator Theory.
- Hercher, C. (2023). *There are no Collatz-m-Cycles with m ≤ 91.*
  arXiv:2201.00406.
- Paparella, P. (2024). *A matricial view of the Collatz conjecture.*
  arXiv:2406.08498.

---

## Provenance

This is **Vibe-Math.** I was bored one night and started poking at the
Collatz conjecture. Several iterations later, with non-trivial AI
collaboration, this is what came out.

It is not a proof. It is an honestly-calibrated computational framework
with a triply-confirmed structural rate `3/4 = e^(log(3/4))`, an empirical
constant `J ≈ 0.0837` stable across 11 decades of starting magnitude, and
a complete five-projection synthesis of four published papers on the
same underlying operator.

If any of it ends up being useful, name it after me.
