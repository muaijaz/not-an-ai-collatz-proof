# Collatz Proof-Search Strategy Notes

This project is a reproducible experimental certificate-search framework. It
does not claim a proof of the Collatz conjecture.

## Ideas To Reuse

- Stopping time is the right local target: proving every odd `n > 1` has an
  accelerated iterate below `n` implies the conjecture by infinite descent.
- Parity vectors identify residue classes modulo powers of two. In the
  accelerated odd map, valuation words play the same role with coarser
  symbolic steps.
- The inverse graph suggests a complementary search: instead of only splitting
  forward residue cylinders, grow certified-predecessor structure backward and
  compare it against unresolved forward frontier classes.
- The 2-adic extension is useful as a warning label. Every infinite parity
  sequence can describe a 2-adic point, but not every such point is a positive
  integer obstruction.
- Cycle searches should report exact affine data. A cycle candidate must solve
  `(2^A - 3^m)n = B`; if the resulting `n` is not a positive integer matching
  the word, it is not an ordinary Collatz cycle.

## Near-Term Creative Hooks

- Use base 2 for exact proof gates: every descent certificate ultimately
  depends on the integer comparison `2^A > 3^m`, not on floating-point debt.
- Do not reduce the whole search to base 2. Binary residue cylinders determine
  valuation words, but mod `3^ell` state helps preserve information about the
  arithmetic shape of future spike opportunities.
- In the mixed automaton, `2`-adic precision decays by the forced valuation
  while `3`-adic precision grows by one step. The implementation caps the
  `3`-adic precision for a finite exploratory graph and reports truncations.
- The residue cover and mixed automaton have different jobs: the cover emits
  descent certificates; the automaton emits suspicious abstract cycles/frontier
  states for exact classification.
- Academic-inspired modules now emit finite artifacts:
  `cycles_eliahou.py` for continued-fraction cycle screens, `density_lp.py` for
  exact unresolved finite-cover density and transition-count scaffolds, and
  `transfer_op.py` for truncated transfer-operator spectra when NumPy is
  installed. These are not yet encodings of the full published theorems.
- Cross-disciplinary probes include finite transition-graph cohomology
  (`cohomology.py`), a solver-ready polynomial Lyapunov/SOS scaffold
  (`sos_lyapunov.py`), a bounded reverse-frontier probe (`reverse_frontier.py`),
  and locally verifiable JSON certificate artifacts (`formal_artifacts.py`).
- Linear-algebra probes now include a substochastic frontier-survival spectrum
  (`cover_spectrum.py`) and a max-plus debt cycle-mean diagnostic
  (`max_plus.py`). The survival spectrum is the more proof-facing artifact:
  on `docs/reports/cover_depth16.json` with `2^6` sampled lifts, its finite
  frontier Perron value is `0.5`; after sparse power iteration, the
  `docs/reports/cover_depth20_resumed.json` frontier also has Perron value
  `0.5` with top survivor `1048575 mod 2^20`. The max-plus quotient currently
  finds positive mean-debt symbolic cycles, which should be treated as coarse
  quotient obstructions to refine, not as integer orbit witnesses.
- Broader "try the weird tools" artifacts are wired behind `--all-things`:
  LLL near-relations (`lll_cycles.py`), constrained legal-residue JSR
  (`constrained_jsr.py`), Walsh-Hadamard transfer diagnostics
  (`walsh_transfer.py`), mixed tensor flattening ranks (`mixed_tensor.py`),
  graph Hodge dimensions (`hodge.py`), Ollivier-Ricci curvature
  (`graph_curvature.py`), integer/Bowen-Franks-style invariants
  (`snf_invariants.py`), toy thermodynamic pressure (`thermodynamic.py`),
  auxiliary-prime valuation scans (`newton_polygons.py`), spike correlations
  (`spike_dpp.py`), and cover-trie magnitude (`magnitude.py`).
- Second-wave finite linear-algebra artifacts include a Cohn-Elkies/Delsarte
  Walsh LP (`cohn_elkies.py`) and a residue support sandpile group
  (`sandpile.py`). The Walsh LP is explicitly over the XOR group of odd-residue
  bit indices, not cyclic `Z/2^k`. At `k=8` it reports unresolved density
  `13/64` and a finite XOR-packing density bound `1/32`. The sandpile artifact
  computes exact Matrix-Tree orders by Bareiss determinant; full critical-group
  invariant factors are filled in when optional SymPy is installed.
- Quotient-cycle lift checks (`lift_realizability.py`) now separate finite
  residue graph cycles from exact valuation-word cylinders and exact cycle
  classifications. At `k=6`, the leading positive-debt quotient loop has word
  `(1,)`; it does lift to exact quotient-closing tail residues, but its exact
  cycle classification is the negative cycle `n=-1`, not a positive integer
  cycle. This points the proof search back to tail-renormalization rather than
  ordinary cycle exclusion.
- Round-three fusion artifacts compose existing modules instead of adding
  side-by-side diagnostics: `cycle_tower.py` fuses continued fractions, LLL,
  exact cycle classification, and lift-realizability; `cohomology_tower.py`
  tracks Betti/Hodge ranks and sandpile critical groups across depths; and
  `spectral_fingerprint.py` combines transfer spectrum, max-plus debt,
  Hodge rank, sandpile order, Walsh sparsity, and mixed tensor ranks into one
  per-depth obstruction fingerprint.
- Tail-exclusion work has four independent witnesses now. `tail_lemma.py`
  attempts exact cylinder-level exit certification under the renormalized
  `(R,u)` map and reports unresolved cylinders when more precision/invariants
  are needed. `tail_spectral.py` restricts the transfer operator to
  all-ones-prefixed residues; at `k=12`, prefix length `8`, sampled lift
  `2^6`, the finite subblock Perron value is `0.5`. The spectral ladder in
  `docs/reports/tail_spectral_ladder_k12_20_prefix8.json` repeats this at
  `k=12,14,16,18,20`; the top survivor stays the Mersenne-tail residue
  `511`, and the average survival probability remains exactly `1/2`.
  `tail_lte.py` verifies the LTE identity `v2(3^R-1)=1` for odd `R` and
  `2+v2(R)` for even `R` through `R=128`; this is a checked arithmetic input
  for the eventual closed tail-exclusion lemma.
- `tail_lyapunov.py` now tunes the proposed tail monovariant scaffold
  `V(n)=log2(n)+beta*v2(n+1)+gamma*omega(n mod 2^k)`. The positive sign on
  `beta*v2(n+1)` is forced by the algebra: a collapse in tail depth must lower
  the monovariant. With `R0=20`,
  prefix length `8`, sampled lift `2^6`, and the spectral ladder
  `k=12..20`, the two-variable LP is feasible:
  `beta=0.04185446433722544`, `gamma=1.1719250014423124`, spectral gap
  `1/2`, and LTE tail-depth drop bound `14`
  (`docs/reports/tail_lyapunov_lp_R20_prefix8.json`). This is a finite
  expected-drift / arithmetic scaffold, not yet a pointwise proof for all
  positive integers. The next proof-facing step is to replace naive tail
  cylinder splitting with symbolic verification of `Delta V < 0` on the
  renormalized tail cylinders, then export the successful inequalities as
  exact rational artifacts.
- The Livsic/pointwise gap is now explicit. `tail_internal_step_report`
  records the elementary identity: for every odd `u` and `R>=2`, if
  `n=2^R*u-1`, then `v2(3n+1)=1`, `S(n)=3*2^(R-1)*u-1`, and
  `v2(S(n)+1)=R-1`. Thus the all-ones tail phase is deterministic and does
  not need the Perron argument. Conversely, `tail_pointwise_ratio_scan`
  confirms that the current all-ones-prefix subblock cannot itself provide a
  pointwise contraction: at `k=12,14,16,18,20`, exactly half the rows have
  zero survival and half have full survival (`64/64` sampled lifts), even
  though average survival is `1/2`
  (`docs/reports/tail_pointwise_ratio_k12_20_prefix8.json`). The pointwise
  proof gate must therefore move to the post-exit renormalized cylinder map.
- `post_exit_map.py` implements that next gate. A PECM state is
  `(R, u mod 2^k, u mod 3^ell)`: from
  `m_post=2*3^(R-1)*u-1`, the exact accelerated orbit is run until it either
  drops below the original `n0=2^R*u-1` or re-enters a tail cylinder
  `v2(x+1)>=2`. The saved PECM ladder over `(k,ell)=(8,2),(10,3),(12,4)`,
  `R=2..30`, and one representative per mixed residue has no out-of-range
  reentries, but has full-survival rows at all three resolutions
  (`docs/reports/post_exit_pecm_pointwise.json`). With four CRT lifts per
  cylinder, the same worst class persists:
  `R=2`, `u == 7 mod 2^k`, `u == 0 mod 3^ell`
  (`docs/reports/post_exit_pecm_pointwise_lifts4.json`). At `(k,ell)=(8,2)`,
  the constant-weight pointwise bound is blocked (`rho_max=1`), while the
  Perron-weighted finite ratio scan gives `finite_ratio_max=0.5` with no
  infinite-ratio rows. This is the first genuinely post-exit Livsic-style
  object; the next refinement is to lift the weighted scan to `(10,3)` and
  `(12,4)` without materializing the full matrix, or isolate the full-survival
  class as a closed symbolic subproblem.
- The scaled PECM Perron scan now does that lift by caching target indices
  rather than materializing a sparse matrix
  (`docs/reports/post_exit_pecm_perron_scaled.json`). With `R=2..30`, four
  CRT lifts per cylinder, and 120 right-power iterations, the constant-weight
  obstruction remains (`rho_max=1`) but the Perron-weighted ratio improves:
  `(8,2)` has `finite_ratio_max=0.5`, `(10,3)` has about `0.34511437`, and
  `(12,4)` has about `0.33411513`, with no infinite-ratio rows and no
  out-of-window tail reentries. Many zero-weight rows remain, so this is a
  recurrent-support contraction artifact rather than a globally positive
  Lyapunov certificate. The next proof-facing step is to turn this
  Perron-weighted recurrent-support vector into a strictly positive
  super-eigenvector, for example by epsilon-lifting transient rows or solving
  the finite Collatz-Wielandt inequalities directly.
- The positive super-eigenvector extension has been tested as a finite
  resolvent certificate (`docs/reports/post_exit_pecm_super_eigenvector.json`).
  For each level, the construction chooses `alpha` just above the recurrent
  ratio, iterates `h = 1 + M h / alpha`, and reports the actual
  `lambda_super = max_i (M h)(i)/h(i)` over the full finite PECM state space.
  With `R=2..30`, four CRT lifts, and margin `0.02`, the results are:
  `(8,2)` has `lambda_super ~= 0.5058`, `(10,3)` has
  `lambda_super ~= 0.3648`, and `(12,4)` has `lambda_super ~= 0.3541`.
  The vector is strictly positive (`positive_min=1.0`) at all three levels,
  so this closes the finite support-extension gate for the sampled PECM
  windows. It is still a finite-window certificate, not a proof for all
  moduli or all `R`.
- The obstruction class also has a finite cohomology shadow. At `k=6`, the
  mixed condition `u == 0 mod 9` is invisible to the binary transition graph,
  but the binary shadow is `n == 27 mod 64`. Projecting the incident-edge
  indicator of this vertex onto the finite graph cycle space gives projection
  norm about `1.7018`, ratio about `0.6948`
  (`docs/reports/harmonic_class_identification.json`). This is not a mixed
  harmonic identification yet; it says the named obstruction has a substantial
  visible component in the binary H^1 artifact.
- The mixed harmonic projection is now explicit at `(k,ell)=(6,3)`
  (`docs/reports/harmonic_class_identification_mixed.json`). The mixed graph
  has `864` vertices, `2589` undirected support edges, and `b1=1726`. The
  obstruction class `R=2`, `u == 7 mod 2^8`, `u == 0 mod 9` appears as three
  mixed vertices `(27,26)`, `(27,8)`, `(27,17)` modulo
  `2^6 x 3^3`. Its incident-edge indicator projects onto the mixed cycle
  space with norm about `2.4193`, ratio about `0.5410`. This is lower than the
  binary shadow ratio, so the first mixed graph does not identify the
  obstruction as a single pure harmonic class; it says the obstruction remains
  partly coboundary even after adding the visible `3`-adic coordinate.
- Extending the mixed harmonic projection changes the picture sharply
  (`docs/reports/harmonic_class_identification_mixed_extended.json`). With the
  sparse Hodge projection, `(8,3)` has projection ratio about `8e-10`, and
  `(10,4)` has ratio about `1e-9`. In these finite mixed graphs the named
  obstruction is essentially entirely a coboundary/gradient artifact, not a
  stable harmonic class. This strongly supports the idea that adding enough
  `2/3`-adic resolution kills the cohomological obstruction.
- Attempting the next PECM super-eigen levels exposes the current scaling
  boundary (`docs/reports/post_exit_pecm_perron_extended.json`). At
  `(14,5)`, the exact four-lift target-cache operator would have about
  `57.7M` states and `230.9M` exact post-exit transition evaluations; at
  `(16,6)` it would have about `692.7M` states and `2.77B` exact transition
  evaluations, plus roughly `10.3 GiB` just for the int32 target cache and
  `5.16 GiB` per float64 vector. The existing matrix-free cache is adequate
  through `(12,4)` but needs a compressed/distributed operator, symmetry
  quotient, or stochastic validated estimator before `(14,5)` and `(16,6)` are
  routine exact artifacts.
- The Hodge solve now emits an explicit finite correction potential for the
  named obstruction (`docs/reports/obstruction_lyapunov_correction.json`). At
  `(k,ell)=(8,3)`, the residual ratio is about `8e-10`; after choosing the
  sign for Lyapunov decrement, 100 sampled PECM trajectories from
  `R=2`, `u==7 mod 2^8`, `u==0 mod 9` all re-entered tail cylinders with
  `psi(source)-psi(target)` essentially equal to `1.0`. This is a concrete
  finite mixed-adic correction term for the constant-weight failure mode.
- A first empirical Lasota-Yorke diagnostic is saved at
  `docs/reports/post_exit_pecm_lasota_yorke.json`. On `(k,ell)=(12,4)`,
  `R=2..30`, four lifts, 8 random box-BV samples, and 10 iterates, the fitted
  BV contraction has median `rho ~= 0.214` and max `rho ~= 0.351`. This is
  encouraging and below the observed super-eigenvalue scale, but it is an
  empirical fit, not a Lasota-Yorke proof. The code supports larger sample
  counts; the requested 1000-sample run should be treated as a longer batch
  job rather than a quick interactive artifact.
- The symbolic fit for the Hodge correction is now sharp at `(8,3)`
  (`docs/reports/psi_symbolic_fit.json`). The 3456 finite potential values are
  all integers after subtracting the graph-component offset
  `-0.000868055555...`. A two-feature mixed obstruction model with the
  resolved indicator `R=2`, `u == 7 mod 2^8`, `u == 0 mod 9` fits with
  `R^2=1.0` up to numerical noise. In this finite graph, the correction is not
  a mysterious smooth potential; it is essentially the obstruction-class
  indicator/coboundary.
- The proposed unified Lyapunov
  `V(n)=log2(n)+alpha*psi(cyl(n))-beta*R(n)` does **not** close the full
  `(8,3)` PECM window (`docs/reports/unified_lyapunov_lp.json`). The strict LP
  is infeasible on 341437 in-window reentry constraints. The minimax relaxation
  chooses `alpha=0`, `beta=0`, with worst remaining `Delta V ~= 16.55` at a
  transition from `R=30` to `R=3`. This names the next missing term: a
  post-exit height/debt correction that handles high-`R` growth before tail
  reentry. The finite psi correction kills the named `R=2` mixed obstruction,
  but it is not by itself a global PECM Lyapunov.
- Testing the proposed renormalized height
  `log2(n)-R*log2(3/2)` at `(8,3)` made the high-`R` obstruction worse under
  the `target-source` LP convention (`docs/reports/unified_lyapunov_renormalized.json`):
  the worst transition remained high-depth, now `R=30 -> R=2` with
  renormalized height delta about `32.93`. The sign-corrected variant
  `log2(n)+R*log2(3/2)` improved that specific failure but still did not close
  (`docs/reports/unified_lyapunov_plus_3_over_2.json`); the new worst was
  `R=23 -> R=22` with height delta about `11.87` and essentially zero psi
  movement. This confirms that deterministic tail-depth renormalization alone
  is insufficient.
- Adding the post-exit edge debt term
  `gamma*(A_PE - m_PE*log2(3))` closes the finite `(8,3)` LP as a diagnostic
  (`docs/reports/unified_lyapunov_debt.json`). With raw height and
  `gamma_bound=16`, the LP finds `alpha=0`, `beta=0`, `gamma=16`, and
  margin `epsilon ~= 0.2932` over all 341437 in-window reentry constraints;
  1000 random trajectory checks had no violations. A gamma-bound scan
  (`docs/reports/unified_lyapunov_debt_gamma_scan.json`) shows infeasibility at
  `gamma_bound=1`, feasibility by `gamma_bound=2`, and the objective saturates
  the supplied gamma cap. This is not yet a formal state Lyapunov, because
  debt is edge-local here; the next formal step is to bucket/accumulate
  `D_PE` as a PECM state coordinate.
- The debt coordinate has now been promoted to a finite bucketed state
  diagnostic (`docs/reports/unified_lyapunov_state_debt.json`). With cumulative
  debt buckets and `Delta=0.01`, the `(8,3)` LP closes with `alpha=0`,
  `beta=0`, `gamma=16`, and `epsilon ~= 0.3004`. The bucket range is
  `-1655..-2`, giving an augmented-state upper bound of about `165.8M`
  states, but the LP is generated from the 341437 exact reentry constraints
  without materializing that state space. A bucket-width scan
  (`docs/reports/unified_lyapunov_state_debt_bucket_scan.json`) shows
  `Delta=0.1` and `0.05` fail because they round the worst debt
  `D_PE ~= -0.01955` to zero; `Delta=0.02` and `0.01` both close.
- The structural `D_PE` scan is saved at
  `docs/reports/d_pe_structural_bound.json`. On both `(8,3)` and `(10,4)`, all
  in-window reentry edges have negative post-exit debt. The worst reentry edge
  is stable across both resolutions with `D_PE ~= -0.01955000865`, `m_PE=12`,
  and total valuation `A=19`. Terminal descent edges are recorded separately
  and may have positive debt because they already cross below the starting
  value. The finite reentry-envelope fit supports
  `D_PE <= -c*m_PE^alpha` with roughly `c=0.014`, `alpha=0.13`.
- Baker/continued-fraction diagnostics now explain the debt gap
  (`docs/reports/d_pe_baker_certification.json`,
  `docs/reports/d_pe_convergent_atlas.json`). A configurable Baker-style floor
  `C/max(m,A)^kappa` with `C=1e-9`, `kappa=13.3` is respected by every reentry
  edge at `(8,3)` and `(10,4)`, but it is far too weak numerically: for the
  worst `(m,A)=(12,19)` edge, the observed gap is `0.01955000865` while the
  configured Baker floor is about `9.8e-27`. The useful finite structure is
  continued-fraction: `19/12` is a convergent of `log2(3)` and appears as a
  PECM reentry edge 613 times at `(8,3)`. Better negative convergents such as
  `84/53` and `1054/665` do not appear in the `(8,3)` reentry edge set, so the
  structural theorem must combine Diophantine separation with PECM
  realizability constraints.
- The sharp continued-fraction replacement is now explicit
  (`docs/reports/d_pe_continued_fraction_certification.json`). For both
  `(8,3)` and `(10,4)`, the worst edge is again `(m,A)=(12,19)` with
  continued-fraction lower bound `1/(12+41)=0.0188679`; the observed gap
  `0.0195500` is only a factor `1.036` above this bound. This is the right
  finite-resolution certificate; Baker remains only an asymptotic/citation
  fallback.
- The first R-truncation test
  (`docs/reports/d_pe_convergent_atlas_R100.json`) showed that at `(8,3)` and
  `R<=100`, `84/53` was absent. A cross-resolution sweep reverses the
  structural-exclusion interpretation
  (`docs/reports/d_pe_convergent_atlas_resolution_sweep.json`): `84/53`
  appears 8 times at `(10,4)` and 27 times at `(12,4)`, while `(14,5)` is an
  exact-enumeration capacity boundary at about `788M` transitions. Therefore
  the `(8,3)` absence of `84/53` is a resolution artifact, not evidence for a
  genuine structural exclusion. The wrong-A forensic report
  (`docs/reports/wrong_A_distribution.json`) explains the mechanism: at
  `(8,3)`, candidates reentering exactly at `m=53` have `A` values from `54`
  through `83`; at `(10,4)` and `(12,4)`, the same distribution extends to
  `A=84`, with 8 and 27 realized `84/53` edges respectively.
- The calibrated validation audit V1--V5 is saved at
  `docs/reports/validation_v1_v5.json`. The independent dense Laplacian
  eigensolve confirms the mixed harmonic collapse at `(8,3)` with residual
  ratio about `3.7e-15` (LSMR was about `8e-10`), so that part is not an LSMR
  artifact. The psi potential is also confirmed to be trivial/integer at this
  resolution: after subtracting the component offset, the distribution is
  `3453` zeros and `3` ones, so psi is essentially the finite obstruction
  indicator rather than a rich Lyapunov potential. Direct evaluation of the
  bucketed debt LP over all 341437 `(8,3)` reentry edges gives max
  `Delta V=-0.3004087`, with zero violations of the `-0.30` margin and zero
  nonnegative deltas. The R<=100 atlas again shows `84/53` absent. However, the
  naive actual-orbit probe using a running debt reset convention has about
  `50.1%` nonnegative accelerated-step deltas, so `log2(n)+16D` should not be
  described as an ordinary per-step Collatz Lyapunov; it is a PECM
  reentry-edge certificate under a specific debt-state convention.
- The full actual-orbit beta sweep is saved at
  `docs/reports/orbit_lyapunov_beta_sweep_1e6.json`. It ran `1,000,000` random
  odd starts in `[10^6,10^9]`, completed all orbits, and checked `69,939,768`
  accelerated steps. For the `reset_at_source` convention, every `beta>=2`
  gives fraction nonnegative `0.499945`, essentially a coin flip and only
  barely below `1/2`; max and mean deltas are positive and grow with beta. For
  the cleaner `reset_at_target` state convention, all tested beta values have
  fraction nonnegative at least `0.5838`. Conclusion: this sweep does not
  produce an ordinary per-step Lyapunov for full Collatz orbits; the debt
  coordinate remains useful as a PECM renewal/reentry certificate, not as a
  global accelerated-step monovariant.
- The renewal-scale orbit diagnostic is saved at
  `docs/reports/orbit_renewal_descent.json`. On the same `1,000,000` random
  starts, all orbits completed, with `69,939,768` accelerated steps grouped into
  `35,473,285` tail-entry renewal excursions. The mean renewal increment is
  strongly negative, `E[Delta log2 n] ~= -0.8024`, with variance about `5.55`.
  However, `63.3%` of individual excursions have nonnegative increment; the
  negative drift is carried by a heavy left tail (`min ~= -33.68`, max
  `~= 0.652`). Hoeffding bounds are correspondingly weak because the bounded
  range is large (`T=1000` gives only about `0.335`). This supports a
  renewal/probabilistic drift direction, not a per-excursion majority descent
  or simple Hoeffding proof.
- The spike-decomposed renewal diagnostic is saved at
  `docs/reports/orbit_renewal_spike_decomposition.json`. It uses the same
  `1,000,000` starts and `35,473,285` renewal excursions, grouped by the maximum
  accelerated valuation in each excursion. With the corrected upper-tail MGF
  `M(lambda)=E[exp(lambda*Delta)]`, the empirical Cramer rate is
  `I(0) ~= 0.08373` at `lambda ~= 0.263`. The reported opposite-sign MGF is
  retained only as an audit guard against the earlier sign error. The one-sided
  Bernstein rate using the bounded upper deviation is `~= 0.05416`, so the
  binned empirical Cramer exponent is about `1.5x` sharper. Drift is
  mechanically explained by valuation spikes: max valuation `1` and `2`
  excursions contribute positive drift (`+0.2961` and `+0.00657` to the total
  mean), while max valuation `3`, `4`, and `5` already contribute about
  `-0.1711`, `-0.3500`, and `-0.2468`. Higher spikes are rarer but extend the
  negative tail. This is a strong empirical renewal-rate artifact, still not a
  proof: iid/exchangeability, finite sampling, and the passage from sampled
  excursions to all orbits remain open.
- The per-spike-level MGF grid is saved at
  `docs/reports/orbit_renewal_per_k_mgf.json`. On the fixed audit grid
  `lambda in {0.05,0.1,0.2,0.3,0.5}`, the aggregate positive-tail MGF is
  minimized at `lambda=0.3`, giving grid `I(0) ~= 0.08270`, consistent with the
  continuous/histogram estimate `0.08373` from the spike-decomposition report.
  The bottleneck at the best aggregate lambda is max valuation `1`, with
  weighted MGF contribution about `0.602`; the spike levels `>=3` are the
  negative-drift mechanism, but the common no-spike class is the mass that the
  rate function must overcome. Conditional grid optima are `lambda*=0` for
  max-a `1` and `2`, and `lambda*=0.5` for all resolved negative-drift classes
  `3..10` on this coarse grid, so the conditional shapes are not uniform:
  positive/no-spike renewals and spike renewals are qualitatively different.
  For `k>=4`, empirical probabilities mostly follow the geometric halving
  shape when normalized at `k=4`: ratios are about `1.05, 0.94, 0.96, 0.90,
  0.88` for `k=5..9`, with a bump at `k=10` due to finite-window/residue
  effects.
- The sampled renewal TDA artifact is saved at
  `docs/reports/orbit_renewal_tda.json`. The first attempt included initial
  non-tail starts and terminal landings and produced nonzero H1 in the
  `(R_source,R_target)` cloud, so that interpretation was rejected. With the
  corrected tail-to-tail filter `R_source>=2` and `R_target>=2`, the full
  million-start run had `33,973,770` eligible tail-depth transitions; a
  5000-point reservoir sample has zero finite H1 features in the
  `(R_t,R_{t+1})` embedding. This supports the tree-like tail-depth observation
  at sampled scale. The `(log2 n_source, Delta log2 n)` embedding has many H1
  features, but top persistence `~=0.345` is below the permutation-null mean
  `~=0.385`, so this run does not support a robust magnitude-conditioned loop
  signal.
- The Markov-conditional Cramer artifact is saved at
  `docs/reports/orbit_renewal_markov_cramer.json`. States are max-valuation
  classes `1..10, >10`; for each consecutive renewal pair `i -> j`, the tilted
  matrix uses the next excursion's increment:
  `D_ij(lambda)=P(j|i) E[exp(lambda*Delta_next) | i->j]`. On the grid
  `lambda=0.05..0.60`, the best Markov rate is `0.08189` at `lambda=0.25`.
  This is a small improvement over the iid baseline on pair-target increments
  (`0.07829`, lift `0.00360`), but it is slightly below the all-excursion iid
  grid rate (`0.08358`, lift `-0.00169`). Therefore the Markov dependence does
  not currently improve the headline beta'' Cramer exponent; the iid aggregate
  remains the stronger sampled rate. The transition matrix still exposes useful
  structure: `1->1` is the dominant transition with probability about `0.486`
  and positive mean increment `0.585`, while transitions from low spike states
  into spike classes `>=3` carry the negative renewals.
- The starting-magnitude stability sweep is saved at
  `docs/reports/orbit_renewal_n0_stability.json`. It uses `200,000` random odd
  starts per range across `[10^2,10^4]`, `[10^4,10^6]`, `[10^6,10^9]`,
  `[10^9,10^12]`, and `[10^12,10^15]`. The empirical Cramer rate rises from
  `0.0761` in the smallest range to `0.0820`, `0.0835`, `0.0848`, and
  `0.0846`; total width is `0.00869`, with fitted slope only `0.000713` per
  log10 midpoint. The small range has short-orbit bias (`16.0` renewal
  excursions/orbit, mean drift `-0.744`), while ranges from `10^6` upward are
  stable around the original `I(0) ~= 0.084` and mean drift near `-0.81`.
  Spike mass also stabilizes: max-a `1` probability moves from `0.515` in the
  smallest range to about `0.503` at high ranges, and its positive drift
  contribution settles near `0.295`. This supports a rate-uniform empirical
  statement for medium/large starts, not for tiny starts without caveats.
- The valuation mutual-information lag scan is saved at
  `docs/reports/valuation_mi_lags.json`. On the full `1,000,000`-orbit
  baseline (`69,939,768` accelerated valuation symbols), the marginal entropy
  is `1.9903` bits. The lag-4 bump persists and is the global peak:
  debiased `I(a_t;a_{t+4}) ~= 0.02837` bits versus lag-1
  `~=0.01578` bits; the Miller-Madow bias floor is only about `1e-6` bits. The
  dependence is weak in absolute terms but real. The lag-4 structure is now a
  separate residue-dynamics question, not a sampling artifact from the smaller
  probe.
- The Tao Syracuse empirical check is saved at
  `docs/reports/tao_syrac_empirical.json`. Tao's recursive distribution
  `Syrac(Z/3^n Z)` was computed exactly from Lemma 1.12 through `n=4`, and the
  empirical analogue `Syr^n(N) mod 3^n` was sampled from the same
  `1,000,000` starting values. The direct Tao comparison is excellent:
  total-variation distances are `0.00040`, `0.00069`, `0.00203`, and
  `0.00278` for `n=1..4`, all below `0.3%`. The all-iterate time marginal over
  the full `69,939,768` accelerated steps is intentionally reported separately
  and deviates more (`0.0039`, `0.0280`, `0.0491`, `0.0685`), so it should not
  be conflated with Tao's fixed-iterate random variable. The oscillations from
  Tao Eq. 1.24 also match closely for fixed iterates: e.g. `(m,n)=(2,4)` gives
  Tao `0.53503` versus empirical `0.53482`. This is an independent empirical
  confirmation that our orbit sampler is seeing Tao's 3-adic Syracuse random
  variable at small levels.
- The Tao characteristic-function decay check is saved at
  `docs/reports/tao_characteristic_function_decay.json`. Exact recursive
  `Syrac(Z/3^n Z)` distributions and empirical fixed iterates were compared
  for `n=1..7` over all frequencies `xi` not divisible by `3`. The empirical
  maxima match Tao's exact maxima closely and at the same frequencies:
  `0.5777`, `0.3787`, `0.2523`, `0.1762`, `0.1290`, `0.0958`, `0.0768`,
  versus Tao exact `0.5774`, `0.3779`, `0.2522`, `0.1770`, `0.1293`,
  `0.0961`, `0.0759`. Maximum coefficient discrepancy remains about
  `0.0022` by `n=7`. A log-log fit over `n=2..7` gives power-decay exponent
  `~1.29` for both exact Tao and empirical data. This is finite-scale evidence
  for the direction of Tao Prop. 1.17, not an empirical verification of the
  asymptotic superpolynomial theorem; nevertheless it confirms that the orbit
  sampler reproduces Tao's small-level Fourier structure, not just the marginal
  residue probabilities.
- The unified finite-operator synthesis is saved at
  `docs/reports/unified_collatz_operator.json`, with the narrative scaffold in
  `docs/UNIFIED_MODEL.md`. The dyadic component is a lift-averaged quotient of
  Mori's `T_1 + T_2`, because division by two is not well-defined on `Z/2^k`
  without averaging over lifts modulo `2^(k+1)`. At `k=8,10,12`, the quotient
  has spectral radius `1`, second eigenvalue magnitude `~0.5`, and L2 operator
  norm `sqrt(3/2) ~= 1.2247`; the `k=12` ARPACK solve is partial but still
  recovers the same second-eigenvalue signal. Paparella-style finite
  non-trivial truncations are nilpotent by escape depth for
  `n=64,128,256,512`; after switching to Paparella's shortcut map convention,
  the escape depths are `17,22,24,32`. The same artifact summarizes the saved
  Tao TV, Tao Fourier, renewal stability, Markov-Cramer, valuation-MI,
  Hercher, and Paparella projections. This is a finite synthesis artifact, not
  an infinite operator theorem; the next faithful approximation should be a
  mixed `2^k x 3^ell` first-return operator aligned with Mori's `N_1 union N_2`
  structure.
- The Hercher reciprocal-sum diagnostic is saved at
  `docs/reports/hercher_t_ni_bound.json`. Using Hercher's shortcut map
  convention `C(n)=n/2` for even `n` and `(3n+1)/2` for odd `n`, the sample of
  `5000` orbits in `[10^5,10^6]` produced `116790` local-minimum segments. The
  universal sampled check from Remark 7 passes: max `T(n_i)n_i ~= 2.99695 < 3`.
  Bucket maxima match the analytic ceilings `3(1-(2/3)^k)` to about `1e-8` for
  `k=1..5`; the `k>5` bucket comes within `0.00305` of the asymptotic ceiling
  `3`. Hercher's `97/54` bound is recorded as a hypothetical-cycle bound at
  `X0=2^68`, not directly testable on small ordinary orbits.
- The standalone Paparella trace diagnostic is saved at
  `docs/reports/paparella_nilpotency.json`. For shortcut-map `C_n` on
  `{3,...,n}`, traces are zero for all tested powers at
  `n=64,128,256,512,1024`; escape-depth nilpotency also holds, with no
  nontrivial truncated cycle found. This complements the escape-depth summary
  in the unified operator report.
- The mixed Mori first-return quotient is now saved at
  `docs/reports/mori_mixed_first_return_operator.json` and summarized inside
  the unified operator artifact. It uses the original branch convention
  `odd n -> 3n+1`, `even n -> n/2`, with first-return set
  `N_1={n mod 6 in {1,5}}` and `N_2={3n+1: n in N_1}`. Finite rows average
  over `8` integer lifts of each residue. At `(k,ell)=(6,2),(8,3),(10,3)`,
  dimensions are `256,3072,12288`; row sums are exactly `1`, unresolved lifts
  are `0`, and the second eigenvalue magnitudes are approximately
  `0.7715,0.7723,0.7790`. The recurrent block is a single component at each
  level, but this remains a finite lift-averaged projection, not a verification
  of Mori's infinite reducing-subspace condition.
- The bound-squeeze layer is saved at
  `docs/reports/rigorous_bound_squeeze.json`. It separates deterministic
  theorems, exact finite computations, high-confidence empirical intervals,
  and empirical envelopes. Current examples: the convergent squeeze
  `1/53 < |12 log2(3)-19| < 1/41`, the Hercher `m<=91` cycle squeeze recorded
  from the reference notes, empirical-Bernstein confidence interval
  `[-0.80548,-0.79932]` for sampled renewal mean drift, Bernstein lower bound
  `I(0)>=0.05416` for the sampled renewal upper-tail rate, Wilson intervals for
  spike probabilities, finite Paparella trace nilpotency, and the mixed Mori
  finite spectral squeeze. The artifact is intentionally not a proof of
  Collatz; it is a calibration layer that tells us which numbers are theorem
  bounds, which are finite computations, and which are statistical.
- Next calibration moves, in priority order: bootstrap confidence intervals for
  `I(0)`, drift, spike probabilities, and Tao Fourier exponents; Bahadur-Rao or
  saddlepoint anticoncentration to get an upper/lower Cramer-rate sandwich;
  held-out cross-validation for LP Lyapunov certificates; coupling experiments
  for renewal mixing; and surrogate-data nulls for every structural signal such
  as lag-4 mutual information or harmonic projection collapse.
- The first renewal bootstrap/saddlepoint calibration is saved at
  `docs/reports/renewal_bootstrap_calibration.json`. It reruns the
  `1,000,000`-orbit renewal sample, stores the binned increment histogram, and
  performs `500` multinomial bootstrap resamples of the binned law. Bootstrap
  95% intervals: mean drift `[-0.80317,-0.80166]`, variance
  `[5.54849,5.55978]`, Cramer rate `I(0)` `[0.08360,0.08384]`, and optimizer
  `lambda` `[0.26286,0.26324]`. The empirical Cramer tilt has variance
  `1.57455`; Bahadur-Rao-style saddlepoint calibration gives
  `P(S_10>=0) ~= 0.165`, `P(S_100>=0) ~= 2.79e-5`, and
  `P(S_1000>=0) ~= 1.66e-38` for the empirical renewal law. These are
  calibration numbers, not all-orbit probability theorems.
- Claude's projective JSR background artifact is integrated into
  `docs/reports/rigorous_bound_squeeze.json` and summarized in the unified
  report. For the unconstrained projective family
  `F_a = 2^-a [[3,1],[0,2^a]]`, the lower bound from `a=1` gives `JSR>=1.5`,
  while the reported common-quadratic SDP gives `JSR<=1.500001` for
  `a<=12`. This is a clean negative result for unconstrained matrix-product
  descent: arbitrary switching grows. The comparison with the dyadic quotient's
  `~0.5` second eigenvalue gives a factor-`3` structural diagnostic, but we
  should phrase it as a finite projection comparison, not as a theorem that the
  dyadic eigenvalue is literally the constrained JSR.
- The iid random-switching Furstenberg baseline is saved at
  `docs/reports/lyapunov_furstenberg.json`. For the affine accelerated matrices
  `[[3/2^a,1/2^a],[0,1]]` with iid `a~Geom(2)`, the affine-coordinate Lyapunov
  exponent is exactly `E[log2(3/2^a)] = log2(3)-2 = log2(3/4) ~= -0.415037`,
  giving typical factor `3/4`. A `1,000,000`-step Monte Carlo gives
  `-0.41433`, confirming the baseline. Important caveat: the homogeneous
  triangular matrix has top exponent `0` because of the constant coordinate;
  the negative exponent is the affine-size drift, not the top exponent of the
  full homogeneous operator.
- The "Jazz's constant" closed-form stress test is saved at
  `docs/reports/jazz_constant_closed_form_test.json`. Candidate
  `log(4/3)^2 ~= 0.082761` is pretty but rejected by the renewal bootstrap
  interval `[0.083603,0.083842]` for the measured empirical renewal law; the
  gap is about `0.000968`, or `8.10` CI half-widths. It nevertheless matches
  saddlepoint tails surprisingly well at short horizons: closed-form
  saddlepoint tail / empirical saddlepoint tail is `1.01` at `T=10`, `1.10` at
  `T=100`, but grows to `2.63` at `T=1000` and about `1.6e4` at `T=10000`.
  Verdict: `log(4/3)^2` is a useful idealized-model comparison, not the
  measured renewal Cramer rate. The empirical constant remains
  `I(0) ~= 0.083729`.
- The spike-stratified Jazz decomposition is saved at
  `docs/reports/jazz_constant_spike_decomposition.json`. It uses the
  `1,000,000`-orbit per-`max a` MGF table and interpolates to the bootstrap
  optimizer `lambda* ~= 0.263`. The high-precision scalar still comes from the
  bootstrap histogram; the decomposition is structural. At `lambda*`, the
  no-spike class `max a=1` contributes about `64.0%` of the tilted MGF, `max a=2`
  contributes `18.6%`, `max a=3` contributes `9.9%`, and `max a>=4` supplies the
  heavy-tail correction. The measured difference
  `I(0)-log(4/3)^2 ~= 0.000968` is about a `1.17%` multiplier over the Gaussian
  candidate. Tested elementary candidates `log(4/3)^2`, `1/12`, `log2(3)/19`,
  and `(log2(3)-1)/7` all sit below the tight bootstrap interval. Current
  framing: Jazz's constant is a Khinchin-style renewal constant with a useful
  spike-decomposition formula, not an elementary closed form.
- The constrained projective JSR diagnostic is saved at
  `docs/reports/constrained_projective_jsr.json` and now feeds the squeeze and
  unified summaries. On the affine-size/projective quotient, every edge carries
  scalar weight `log2(3)-a`, so Karp max-cycle-mean gives an exact finite
  lower/upper bound. The naive legal-residue quotient through `k=12` still has
  exact JSR `~=1.5`, dominated by the all-`a=1` word `(1)`, classified as the
  negative integer cycle `n=-1`. This is not a bug: the quotient is correctly
  seeing the true Mersenne `2`-adic obstruction. Tail-filtering states with
  `v2(r+1)>=2` recovers exact factor `0.75` (`log2(3/4)`), but admitting deeper
  tail states raises the JSR above `1`. Next theorem-shaped target: replace the
  naive residue quotient by a tail-aware constrained product system that tracks
  `R=v2(n+1)` and proves the positive-integer tail exits instead of letting the
  `-1` loop masquerade as an admissible positive orbit cycle.
- The first tail-aware constrained product diagnostic is saved at
  `docs/reports/tail_aware_projective_jsr.json`. It uses coordinates
  `n=2^R*u-1` with finite state `(R, u mod 2^q)`, so tail-internal steps have
  deterministic valuation `1` and `R -> R-1`. This removes the all-`a=1`
  self-loop at every saved level. Results through
  `(q,Rmax)=(5,4),(6,5),(7,6),(8,6),(10,7)` show tracked-subgraph affine JSR
  values `1.0607, 1.0893, 1.1906, 1.2613, 1.2305`; the largest saved level has
  witness state `(R,u)=(2,81)` and `44` overflow exits to deeper tail depth.
  Calibration: this is not a global upper bound, because overflow exits are
  currently dropped rather than renormalized. Interpretation: the fake
  negative `-1` obstruction has been removed; the next obstruction is genuine
  post-exit reentry into deeper positive-tail coordinates. Next move: replace
  overflow exits by the renormalized block transition so the quotient is closed.
- The LTE-closed tail-aware constrained product diagnostic is saved at
  `docs/reports/tail_aware_lte_closed_projective_jsr.json`. For a post-exit
  edge landing at depth `R'>Rmax`, it computes the exact lifted `R'` and folds
  the forced valuation-one run back down to `Rmax` using
  `S^d(2^R*u-1)=2^{R-d}3^d*u-1`. This closes the bounded graph instead of
  dropping overflows. Results through the same levels give affine JSR values
  `1.0711, 1.0893, 1.1906, 1.2613, 1.2305`; the largest level closes `44`
  overflow edges and still has witness `(R,u)=(2,81)`. Interpretation:
  worst-case constrained products still grow after the fake `-1` loop is gone;
  the expected proof path is therefore Markov/Lyapunov contraction on the closed
  operator, not worst-case JSR `<1`.
- The Markov-weighted Lyapunov diagnostic on the LTE-closed tail graph is saved
  at `docs/reports/tail_aware_markov_lyapunov.json`. It uses the same closed
  graph, weights outgoing edges by enumerated lift counts, normalizes each row,
  identifies recurrent components, and computes the stationary average growth
  on the largest recurrent component. Through
  `(q,Rmax)=(5,4),(6,5),(7,6),(8,6),(10,7)`, average log2 growth per accelerated
  step is `-0.4310, -0.4265, -0.3556, -0.3169, -0.4119`. The largest saved
  level therefore has worst-case factor `1.2305` but typical factor `0.75165`,
  close to the baseline `3/4`. This is the desired typical-vs-worst-case split
  on a single finite operator.
- The bounded Christoffel-filtered JSR diagnostic is saved at
  `docs/reports/christoffel_filtered_jsr.json`. It expands each accelerated
  valuation word to Terras parity bits by `a -> 1 0^(a-1)` and retains only
  primitive cyclically balanced words as a finite Christoffel/Sturmian
  compatibility proxy. At `(q,Rmax)=(5,4)`, exact Karp factor and bounded
  unfiltered best are both `1.0711`, but the compatible best is `0.75`.
  At `(q,Rmax)=(6,5)`, exact Karp factor is `1.0893` and bounded unfiltered
  best is `1.0817`, while the compatible best remains `0.75`. This is the
  first Path-B result: the bounded high-growth witnesses are not
  Christoffel-compatible, but this is a finite diagnostic rather than
  Hercher's full high-cycle theorem.
- A larger empirical Lasota-Yorke batch is saved at
  `docs/reports/post_exit_pecm_lasota_yorke_full.json`. Completed partial
  levels: `(8,3)` with 64 samples gives median `rho ~= 0.250`, max
  `rho ~= 0.385`; `(10,4)` with 32 samples gives median `rho ~= 0.327`, max
  `rho ~= 0.417`; `(12,4)` with 16 samples gives median `rho ~= 0.330`, max
  `rho ~= 0.362`. This remains empirical. The full 1000-sample `(12,4)` run is
  a batch-compute job, not an interactive proof artifact.
- Treat dangerous valuation words as "debt instruments": a branch is dangerous
  while `m*log2(3) - A` is near or above zero, and certified when exact affine
  descent beats the initial value.
- Compress Mersenne-tail cylinders with the renormalized block map. For
  `n = 2^R*u - 1`, the first `R - 1` accelerated valuations are `1`, and the
  closed `R`-step block lands at `(3^R*u - 1)/2^c`, where
  `c = v2(3^R*u - 1)` and total valuation is `R + c`. Recoding the landing as
  `2^R'*u' - 1` gives a finite diagnostic for whether the high-initial-ones
  obstruction is dynamically stable.
- Current tail-renormalization target: for `R=20` and odd `u mod 2^8`, all 128
  representatives leave the tail regime (`R' < 2`) within at most 9 compressed
  blocks. The worst sampled cumulative tail debt is about `14.889` at `u=111`.
  The theorem-shaped goal is to prove that no infinite tail-renormalization
  orbit can keep cumulative block debt nonnegative forever.
- Add a reverse-frontier experiment for unresolved cylinders: ask whether the
  inverse graph already reaches a known certified cylinder before the forward
  splitter has to deepen.
- Keep 2-adic cycle candidates instead of discarding them. Classify them as
  positive integer, negative integer, nonordinary 2-adic, or already-descending.
- The exact `S_exit=3` handoff is now
  `2^(3m+2)w-5 --(1,2)^m--> 4*9^m*w-5`, and the nested cusp contracts the
  full phase by `(11979/12167)^m`. The subsequent simple-cusp obstruction
  leads to word-specific affine ghosts
  `L_W(n)=(3^M-2^A)n+B`, whose valuation loses exactly `A` under word `W`.
  Prioritize an induced ghost-atlas graph. Its exact edge relation has an
  additive ghost-gap term, so retain signed rational offsets and finite
  magnitude intervals rather than multiplying local contraction factors as if
  they telescoped.

## Sources

- Wikipedia, "Collatz conjecture":
  https://en.wikipedia.org/wiki/Collatz_conjecture
