"""Small report helpers for command-line experiments."""

from __future__ import annotations

from .certificates import DescentCertificate
from .champions import ChampionReport
from .cohomology import CohomologyReport
from .compact_trace import CompactTraceReport
from .cohn_elkies import CohnElkiesWalshReport
from .cohomology_tower import CohomologyTowerReport
from .cover import CertificateCoverReport
from .cover_mass import CoverMassReport
from .cover_parity import CoverParityReport
from .cover_spectrum import CoverSurvivalSpectrumReport
from .constrained_jsr import (
    ChristoffelFilteredJSRReport,
    ConstrainedJSRReport,
    ConstrainedProjectiveJSRReport,
    TailAwareMarkovLyapunovReport,
    TailAwareProjectiveJSRReport,
)
from .constrained_karp import ConstrainedKarpReport
from .cycles import CycleScanReport
from .cycle_tower import CycleExclusionTowerReport
from .cycles_eliahou import CycleLengthScreen
from .core import FirstDescent
from .density_lp import DensityBound
from .divider_patterns import DividerPatternReport
from .formal_artifacts import FormalArtifactReport
from .frontier_analysis import FrontierAnalysisReport
from .furstenberg import FurstenbergLyapunovReport
from .graph_tree import OddTreeSiblingReport
from .graph_curvature import OllivierRicciReport
from .harmonic_class import HarmonicClassIdentificationReport
from .hodge import HodgeReport
from .hercher import HercherTNiReport
from .jazz_constant import (
    JazzConstantClosedFormReport,
    JazzConstantDecompositionReport,
)
from .lift_realizability import LiftRealizabilityReport
from .lll_cycles import CycleLatticeReport
from .magnitude import MagnitudeReport
from .max_plus import MaxPlusDebtReport
from .mersenne import MersenneTailReport
from .mersenne_continuation import (
    MersenneBranchReport,
    MersenneContinuationGraph,
    MersennePrefixFamilyReport,
    MersenneProgressionReport,
    MersenneRefinementReport,
)
from .mixed import MixedAutomatonReport
from .mixed_harmonic_class import (
    MixedHarmonicClassReport,
    ObstructionLyapunovCorrectionReport,
)
from .mixed_tensor import MixedTensorRankReport
from .newton_polygons import NewtonPolygonReport
from .parity import ParityLayerReport
from .paparella import PaparellaNilpotencyReport
from .orbit_lyapunov import OrbitLyapunovBetaSweepReport
from .orbit_renewal import (
    OrbitRenewalMarkovCramerReport,
    OrbitRenewalN0StabilityReport,
    OrbitRenewalPerKMGFReport,
    RenewalDescentReport,
    RenewalSpikeDecompositionReport,
)
from .orbit_renewal_tda import OrbitRenewalTDAReport
from .post_exit_lasota_yorke import LasotaYorkeReport
from .post_exit_baker import (
    BakerCertificationReport,
    ContinuedFractionCertificationReport,
    ConvergentAtlasReport,
)
from .post_exit_lyapunov import (
    DPEStructuralBoundReport,
    PsiSymbolicFitReport,
    StateDebtLyapunovReport,
    UnifiedLyapunovLPReport,
)
from .post_exit_map import (
    PostExitPointwiseLadderReport,
    PostExitPointwiseReport,
    PostExitScaledPerronReport,
    PostExitSuperEigenReport,
)
from .power_ratio import PowerRatioReport
from .reverse_frontier import ReverseFrontierReport
from .renewal_bootstrap import RenewalBootstrapCalibrationReport
from .sandpile import SandpileReport
from .search import CoverSearchResult
from .sensitivity import SensitivityReport
from .snf_invariants import SNFInvariantReport
from .sos_lyapunov import LyapunovTemplateArtifact
from .spike_dpp import SpikeCorrelationReport
from .spectral_fingerprint import SpectralFingerprintReport
from .squeeze_bounds import RigorousSqueezeReport
from .tail_family import (
    CoverTailReport,
    TailFamilyReport,
    TailRenormalizationFamilyReport,
    TailRenormalizationReport,
)
from .tail_lemma import TailExitLemmaReport, TailInternalStepReport
from .tail_lte import TailLTEReport
from .tail_lyapunov import TailLyapunovLPReport
from .tail_spectral import (
    TailPointwiseRatioReport,
    TailSpectralLadderReport,
    TailSubautomatonSpectrumReport,
)
from .tao_syrac import TaoCharacteristicDecayReport, TaoSyracEmpiricalReport
from .transfer_op import TransferSpectrumReport
from .thermodynamic import PressureReport
from .tuple_merges import TupleMergeReport
from .unified_operator import MoriMixedFirstReturnReport, UnifiedCollatzOperatorReport
from .valuation_mi import ValuationMILagScanReport


def format_first_descent(result: FirstDescent) -> str:
    return (
        f"n={result.n}, first descent m={result.m}, A={result.A}, "
        f"lands at {result.landing}, first 20 valuations={result.word[:20]}"
    )


def format_furstenberg_lyapunov_report(
    result: FurstenbergLyapunovReport,
) -> str:
    return (
        f"status={result.status}, exact_base2="
        f"{result.exact_log_growth_affine_coordinate_base2}, "
        f"mc_base2={result.monte_carlo_log_growth_base2}, "
        f"typical_factor={result.exact_typical_factor_affine_coordinate}"
    )


def format_certificate(certificate: DescentCertificate) -> str:
    return certificate.summary()


def format_cover_summary(result: CoverSearchResult) -> str:
    return (
        f"strategy={result.strategy}, "
        f"nodes={result.nodes_processed}, "
        f"certificates={len(result.certificates)}, "
        f"unresolved={len(result.unresolved)}, "
        f"dominated_pruned={result.dominated_pruned}, "
        f"depth_counts={result.depth_counts}"
    )


def format_certificate_cover_report(result: CertificateCoverReport) -> str:
    return (
        f"status={result.status}, complete={result.complete}, "
        f"nodes={result.nodes_processed}, certificates={len(result.certificates)}, "
        f"frontier={len(result.frontier)}, covered_pruned={result.covered_pruned}, "
        f"duplicates={result.duplicate_certificates}, "
        f"unresolved_odd_density="
        f"{result.unresolved_odd_density_num}/{result.unresolved_odd_density_den}"
    )


def format_mixed_summary(result: MixedAutomatonReport) -> str:
    cycle_kinds: dict[str, int] = {}
    for candidate in result.cycle_candidates:
        kind = candidate.classification.kind
        cycle_kinds[kind] = cycle_kinds.get(kind, 0) + 1

    return (
        f"states={result.states_explored}, "
        f"transitions={result.transitions}, "
        f"certified={result.terminal_certified}, "
        f"low_debt={result.terminal_low_debt}, "
        f"dominated_pruned={result.dominated_pruned}, "
        f"mod3_truncations={result.mod3_truncations}, "
        f"cycles={len(result.cycle_candidates)} {cycle_kinds}, "
        f"unresolved={len(result.unresolved_states)}"
    )


def format_cycle_scan_summary(result: CycleScanReport) -> str:
    return (
        f"words={result.words_scanned}, "
        f"kinds={result.by_kind}, "
        f"positive_cycles={len(result.positive_integer_cycles)}, "
        f"nontrivial_positive_cycles={len(result.nontrivial_positive_integer_cycles)}, "
        f"no_nontrivial_positive_cycles={not result.nontrivial_positive_integer_cycles}, "
        f"nonrealizing_positive_candidates={len(result.positive_integer_nonrealizing)}"
    )


def format_cycle_length_screen(result: CycleLengthScreen) -> str:
    witness = result.best_witness
    return (
        f"status={result.status}, max_m={result.max_m}, "
        f"best={witness.approximation}, relation={witness.relation}, "
        f"abs_error={witness.abs_error:.3g}"
    )


def format_cycle_lattice_report(result: CycleLatticeReport) -> str:
    relation = result.relations[0] if result.relations else None
    return (
        f"status={result.status}, words={result.words_scanned}, "
        f"best=(m={result.best_m}, A={result.best_A}, "
        f"gap={result.best_power_gap_abs}), "
        f"best_relation={None if relation is None else relation.coefficients}, "
        f"residual={None if relation is None else f'{relation.residual:.3g}'}"
    )


def format_cycle_exclusion_tower_report(result: CycleExclusionTowerReport) -> str:
    lift = result.lift_realizability.checks[0] if result.lift_realizability.checks else None
    return (
        f"status={result.status}, max_m={result.max_m}, "
        f"words={result.words_scanned}, kinds={result.cycle_kinds}, "
        f"nontrivial_positive={result.nontrivial_positive_cycles}, "
        f"top_lift={None if lift is None else lift.word}, "
        f"top_lift_kind={None if lift is None else lift.cycle_classification}"
    )


def format_density_bound(result: DensityBound) -> str:
    return (
        f"status={result.status}, max_depth={result.max_depth}, "
        f"unresolved={result.unresolved_classes}, "
        f"unresolved_odd_density="
        f"{result.unresolved_odd_density_num}/{result.unresolved_odd_density_den}"
    )


def format_transfer_spectrum(result: TransferSpectrumReport) -> str:
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"dim={result.dimension}, second_abs={result.second_eigenvalue_abs}, "
        f"slowest_residue={result.slowest_residue}"
    )


def format_cover_survival_spectrum(result: CoverSurvivalSpectrumReport) -> str:
    if result.perron_eigenvalue is None:
        perron = "n/a"
    else:
        perron = f"{result.perron_eigenvalue:.6f}"
    if result.top_survival_rows:
        leader = result.top_survival_rows[0]
        leader_text = (
            f"top={leader.residue} mod 2^{leader.modulus_power}, "
            f"survival={leader.survival_count}/{leader.row_denominator}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, frontier={result.frontier_classes}, "
        f"dim={result.matrix_dimension}, sample_lifts=2^{result.sample_lift_power}, "
        f"weighted_survival="
        f"{result.weighted_survival_num}/{result.weighted_survival_den}, "
        f"max_row_survival="
        f"{result.max_row_survival_num}/{result.max_row_survival_den}, "
        f"perron={perron}, slowest={result.slowest_state_residue} "
        f"mod 2^{result.slowest_state_modulus_power}, {leader_text}"
    )


def format_cohn_elkies_walsh_report(result: CohnElkiesWalshReport) -> str:
    bound = "n/a" if result.density_bound is None else f"{result.density_bound:.6f}"
    objective = "n/a" if result.objective_sum is None else f"{result.objective_sum:.6f}"
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"model={result.group_model}, dim={result.dimension}, "
        f"unresolved={result.unresolved_points}, "
        f"allowed_differences={result.allowed_differences}, "
        f"sum_f={objective}, density_bound={bound}, "
        f"unresolved_density="
        f"{result.unresolved_density_num}/{result.unresolved_density_den}"
    )


def format_max_plus_debt_report(result: MaxPlusDebtReport) -> str:
    mean = (
        "n/a"
        if result.max_cycle_mean_debt is None
        else f"{result.max_cycle_mean_debt:.6f}"
    )
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"sample_lifts=2^{result.sample_lift_power}, states={result.states}, "
        f"edges={result.edges}, max_cycle_mean_debt={mean}, "
        f"positive_mean={result.positive_mean_detected}, "
        f"witness_residue={result.witness_residue}"
    )


def format_constrained_jsr_report(result: ConstrainedJSRReport) -> str:
    mean = (
        "n/a"
        if result.max_cycle_mean_log2_slope is None
        else f"{result.max_cycle_mean_log2_slope:.6f}"
    )
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"max_a={result.max_valuation}, states={result.states}, "
        f"edges={result.edges}, max_cycle_mean={mean}, "
        f"witness={result.witness_residue}, "
        f"all_one_self_loop={result.all_one_self_loop_detected}"
    )


def format_constrained_projective_jsr_report(
    result: ConstrainedProjectiveJSRReport,
) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_k={None if last is None else last.modulus_power}, "
        f"last_affine_jsr={None if last is None else last.affine_quotient_jsr_upper}, "
        f"obstruction={None if last is None else last.obstruction_kind}"
    )


def format_tail_aware_projective_jsr_report(
    result: TailAwareProjectiveJSRReport,
) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_q={None if last is None else last.tail_unit_power}, "
        f"last_Rmax={None if last is None else last.max_tail_depth}, "
        f"last_jsr={None if last is None else last.affine_quotient_jsr}, "
        f"overflow={None if last is None else last.overflow_edges}, "
        f"all_one_loop={None if last is None else last.all_one_self_loop_detected}"
    )


def format_tail_aware_markov_lyapunov_report(
    result: TailAwareMarkovLyapunovReport,
) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_q={None if last is None else last.tail_unit_power}, "
        f"last_Rmax={None if last is None else last.max_tail_depth}, "
        f"last_jsr={None if last is None else last.worst_case_jsr_factor}, "
        f"last_avg_per_step="
        f"{None if last is None else last.largest_component_average_log2_growth_per_accelerated_step}, "
        f"last_typical_factor="
        f"{None if last is None else last.largest_component_typical_factor_per_accelerated_step}"
    )


def format_christoffel_filtered_jsr_report(
    result: ChristoffelFilteredJSRReport,
) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_q={None if last is None else last.tail_unit_power}, "
        f"last_Rmax={None if last is None else last.max_tail_depth}, "
        f"cycles={None if last is None else last.cycles_scanned}, "
        f"compatible={None if last is None else last.christoffel_compatible_cycles}, "
        f"exact_karp={None if last is None else last.exact_karp_factor}, "
        f"filtered_best={None if last is None else last.christoffel_filtered_best_factor}"
    )


def format_constrained_karp_jsr_report(result: ConstrainedKarpReport) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_q={None if last is None else last.tail_unit_power}, "
        f"last_Rmax={None if last is None else last.max_tail_depth}, "
        f"last_product_states={None if last is None else last.product_states}, "
        f"last_product_edges={None if last is None else last.product_edges}, "
        f"last_factor={None if last is None else last.constrained_karp_factor}, "
        f"within_cycle_filter_bound="
        f"{None if last is None else last.within_cycle_filter_bound}"
    )


def format_lift_realizability_report(result: LiftRealizabilityReport) -> str:
    if result.checks:
        leader = result.checks[0]
        leader_text = (
            f"top_word={leader.word}, debt={leader.total_debt:.3f}, "
            f"cylinder={leader.cylinder_residue_count}, "
            f"closes={leader.closes_mod_power_count}, "
            f"cycle_kind={leader.cycle_classification}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"max_a={result.max_valuation}, max_period={result.max_period}, "
        f"quotient_words={result.quotient_words_found}, {leader_text}"
    )


def format_walsh_transfer_report(result) -> str:
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"dim={result.dimension}, max_coeff="
        f"{result.max_nonconstant_coeff_num}/{result.max_nonconstant_coeff_den}, "
        f"above_threshold={result.coefficients_above_threshold}"
    )


def format_mixed_tensor_rank_report(result: MixedTensorRankReport) -> str:
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"nonzero={result.nonzero_entries}/{result.tensor_entries}, "
        f"ranks=({result.flatten_rank_2_vs_rest},"
        f"{result.flatten_rank_23_vs_rest},{result.flatten_rank_232_vs_3})"
    )


def format_hodge_report(result: HodgeReport) -> str:
    return (
        f"status={result.status}, V={result.vertices}, E={result.undirected_edges}, "
        f"components={result.components}, gradient={result.gradient_dimension}, "
        f"harmonic={result.harmonic_dimension}"
    )


def format_harmonic_class_identification_report(
    result: HarmonicClassIdentificationReport,
) -> str:
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"projected_residue={result.projected_residue}, "
        f"mod3_visible={result.mod3_visible}, "
        f"harmonic_dim={result.harmonic_dimension}, "
        f"indicator_edges={result.indicator_edges}, "
        f"projection_norm={result.harmonic_projection_norm:.6f}, "
        f"projection_ratio={result.harmonic_projection_ratio}"
    )


def format_mixed_harmonic_class_report(result: MixedHarmonicClassReport) -> str:
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"V={result.vertices}, E={result.undirected_edges}, "
        f"b1={result.first_betti}, harmonic={result.harmonic_dimension}, "
        f"obstruction_vertices={len(result.obstruction_vertices)}, "
        f"projection_norm={result.harmonic_projection_norm:.6f}, "
        f"projection_ratio={result.harmonic_projection_ratio}"
    )


def format_obstruction_lyapunov_correction_report(
    result: ObstructionLyapunovCorrectionReport,
) -> str:
    check = result.trajectory_check
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"residual_ratio={result.residual_ratio}, "
        f"potential_entries={len(result.potential_entries)}, "
        f"edge_entries={len(result.edge_correction_entries)}, "
        f"trajectory_reentered={check.reentered}/{check.samples}, "
        f"min_delta={check.min_delta}, mean_delta={check.mean_delta}"
    )


def format_lasota_yorke_report(result: LasotaYorkeReport) -> str:
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"samples={result.samples_completed}, steps={result.max_steps}, "
        f"rho_median={result.rho_median:.6f}, rho_max={result.rho_max:.6f}, "
        f"C={result.C_estimate:.6f}, D={result.D_estimate:.6f}"
    )


def format_psi_symbolic_fit_report(result: PsiSymbolicFitReport) -> str:
    best = max(result.fits, key=lambda fit: fit.r_squared) if result.fits else None
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"entries={result.entries}, "
        f"centered_integer_fraction={result.centered_integer_fraction_1e8:.6f}, "
        f"offset={result.best_integer_offset:.6g}, "
        f"best_fit={None if best is None else best.name}, "
        f"best_R2={None if best is None else f'{best.r_squared:.6f}'}"
    )


def format_unified_lyapunov_lp_report(result: UnifiedLyapunovLPReport) -> str:
    return (
        f"status={result.status}, mode={result.height_mode}, "
        f"k={result.mod2_power}, ell={result.mod3_power}, "
        f"constraints={result.reentry_constraints}, descended={result.descended_samples}, "
        f"lp_success={result.lp_success}, "
        f"alpha={result.alpha}, beta={result.beta}, gamma={result.gamma}, "
        f"epsilon={result.epsilon}, debt={result.include_debt_term}, "
        f"relaxed_alpha={result.relaxed_alpha}, "
        f"relaxed_beta={result.relaxed_beta}, "
        f"relaxed_max_delta={result.relaxed_max_delta}"
    )


def format_state_debt_lyapunov_report(result: StateDebtLyapunovReport) -> str:
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"bucket={result.bucket_width}, buckets={result.bucket_min}..{result.bucket_max}, "
        f"augmented_bound={result.augmented_state_upper_bound}, "
        f"constraints={result.reentry_constraints}, lp_success={result.lp_success}, "
        f"alpha={result.alpha}, beta={result.beta}, gamma={result.gamma}, "
        f"epsilon={result.epsilon}"
    )


def format_dpe_structural_bound_report(result: DPEStructuralBoundReport) -> str:
    if not result.levels:
        return f"status={result.status}, levels=0"
    parts = []
    for level in result.levels:
        parts.append(
            f"({level.mod2_power},{level.mod3_power}): "
            f"max_D={level.max_D_PE}, min_D={level.min_D_PE}, "
            f"c={level.conjecture_c}, alpha={level.conjecture_alpha}"
        )
    return f"status={result.status}, " + "; ".join(parts)


def format_baker_certification_report(result: BakerCertificationReport) -> str:
    parts = []
    for level in result.levels:
        parts.append(
            f"({level.mod2_power},{level.mod3_power}): "
            f"min_gap={level.min_observed_gap}, "
            f"min_ratio={level.min_observed_to_baker_ratio}, "
            f"signed_ratio={level.max_signed_D_over_baker_ratio}"
        )
    return f"status={result.status}, " + "; ".join(parts)


def format_convergent_atlas_report(result: ConvergentAtlasReport) -> str:
    hits = sum(1 for entry in result.entries if entry.appears_as_reentry_edge)
    best = min(result.entries, key=lambda entry: entry.abs_gap) if result.entries else None
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"entries={len(result.entries)}, hits={hits}, "
        f"best={None if best is None else f'{best.A}/{best.m}'}, "
        f"best_gap={None if best is None else best.abs_gap}"
    )


def format_continued_fraction_certification_report(
    result: ContinuedFractionCertificationReport,
) -> str:
    parts = []
    for level in result.levels:
        parts.append(
            f"({level.mod2_power},{level.mod3_power}): "
            f"min_gap={level.min_observed_gap}, "
            f"min_ratio={level.min_observed_to_cf_ratio}, "
            f"conv_edges={level.convergent_edge_count}"
        )
    return f"status={result.status}, " + "; ".join(parts)


def format_orbit_lyapunov_beta_sweep_report(
    result: OrbitLyapunovBetaSweepReport,
) -> str:
    best = min(result.results, key=lambda item: item.fraction_nonnegative)
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"completed={result.completed_orbits}, truncated={result.truncated_orbits}, "
        f"steps={result.total_accelerated_steps}, "
        f"best=({best.convention}, beta={best.beta}, "
        f"frac_nonneg={best.fraction_nonnegative:.6f})"
    )


def format_renewal_descent_report(result: RenewalDescentReport) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"orbits={result.completed_orbits}/{result.sample_count}, "
        f"excursions={result.total_excursions}, "
        f"mean_delta={result.mean_delta_log2}, "
        f"frac_nonneg={result.fraction_nonnegative_delta_log2}"
    )


def format_renewal_bootstrap_calibration_report(
    result: RenewalBootstrapCalibrationReport,
) -> str:
    rate_interval = next(
        (
            interval
            for interval in result.bootstrap_intervals
            if interval.quantity == "cramer_rate_I0"
        ),
        None,
    )
    return (
        f"status={result.status}, excursions={result.total_excursions}, "
        f"I0={result.cramer_rate_I0}, lambda={result.cramer_lambda}, "
        f"I0_CI={None if rate_interval is None else (rate_interval.q025, rate_interval.q975)}"
    )


def format_renewal_spike_decomposition_report(
    result: RenewalSpikeDecompositionReport,
) -> str:
    top = min(result.segments, key=lambda item: item.drift_contribution)
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"excursions={result.total_excursions}, "
        f"mean_delta={result.mean_delta_log2}, "
        f"I0={result.cramer_rate_I0_grid}, lambda={result.cramer_rate_lambda}, "
        f"top_drift_segment=max_a={top.segment}"
    )


def format_orbit_renewal_per_k_mgf_report(
    result: OrbitRenewalPerKMGFReport,
) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"excursions={result.total_excursions}, "
        f"grid_I0={result.implied_cramer_rate_grid}, "
        f"lambda={result.implied_cramer_lambda_grid}, "
        f"bottleneck=max_a={result.bottleneck_segment_at_best_lambda}"
    )


def format_orbit_renewal_markov_cramer_report(
    result: OrbitRenewalMarkovCramerReport,
) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"pairs={result.markov_pairs}, "
        f"markov_I0={result.best_markov_rate}, "
        f"lambda={result.best_markov_lambda}, "
        f"iid_pair_I0={result.best_iid_pair_target_rate}, "
        f"lift_pair={result.markov_rate_lift_over_iid_at_best}, "
        f"iid_all_I0={result.best_iid_all_excursion_rate}, "
        f"lift_all={result.markov_rate_lift_over_iid_all_grid}"
    )


def format_orbit_renewal_n0_stability_report(
    result: OrbitRenewalN0StabilityReport,
) -> str:
    return (
        f"status={result.status}, ranges={len(result.range_reports)}, "
        f"samples_per_range={result.sample_count_per_range}, "
        f"rate_width={result.cramer_rate_range_width}, "
        f"rate_slope={result.cramer_rate_slope_per_log10}"
    )


def format_orbit_renewal_tda_report(result: OrbitRenewalTDAReport) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"excursions={result.total_excursions}, "
        f"R_H1={result.r_drop_h1.h1_features}, "
        f"mag_delta_top_H1={result.magnitude_delta_h1.top_h1_persistence}, "
        f"null_top_H1_mean={result.magnitude_delta_null_top_h1_mean}"
    )


def format_valuation_mi_lag_report(result: ValuationMILagScanReport) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"steps={result.total_accelerated_steps}, "
        f"entropy={result.marginal_entropy_bits}, "
        f"best_lag={result.best_lag}, "
        f"best_MI={result.best_debiased_mutual_information_bits}, "
        f"lag4_MI={result.lag4_debiased_mutual_information_bits}"
    )


def format_tao_syrac_empirical_report(result: TaoSyracEmpiricalReport) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"steps={result.total_accelerated_steps}, "
        f"max_TV_nth={result.max_tv_nth_iterate_to_tao}, "
        f"max_TV_all={result.max_tv_all_iterates_to_tao}"
    )


def format_tao_characteristic_decay_report(
    result: TaoCharacteristicDecayReport,
) -> str:
    last = result.level_reports[-1] if result.level_reports else None
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"max_n={result.max_n}, "
        f"empirical_exponent={result.fitted_empirical_power_exponent}, "
        f"tao_exponent={result.fitted_tao_power_exponent}, "
        f"last_max_emp={None if last is None else last.empirical_max_abs}"
    )


def format_unified_collatz_operator_report(
    result: UnifiedCollatzOperatorReport,
) -> str:
    last = result.dyadic_levels[-1] if result.dyadic_levels else None
    return (
        f"status={result.status}, dyadic_levels={len(result.dyadic_levels)}, "
        f"paparella_levels={len(result.paparella_levels)}, "
        f"last_k={None if last is None else last.modulus_power}, "
        f"last_second_abs={None if last is None else last.second_eigenvalue_abs}, "
        f"saved={sum(1 for item in result.saved_projections if item.available)}"
    )


def format_mori_mixed_first_return_report(
    result: MoriMixedFirstReturnReport,
) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last=({None if last is None else last.modulus_power2},"
        f"{None if last is None else last.modulus_power3}), "
        f"last_dim={None if last is None else last.dimension}, "
        f"last_second_abs={None if last is None else last.second_eigenvalue_abs}, "
        f"unresolved={None if last is None else last.unresolved_lifts}"
    )


def format_rigorous_squeeze_report(result: RigorousSqueezeReport) -> str:
    return (
        f"status={result.status}, entries={len(result.entries)}, "
        f"theorem_or_finite={result.theorem_or_finite_entries}, "
        f"high_confidence={result.high_confidence_entries}, "
        f"empirical_envelopes={result.empirical_envelope_entries}"
    )


def format_jazz_constant_closed_form_report(
    result: JazzConstantClosedFormReport,
) -> str:
    return (
        f"status={result.status}, candidate={result.candidate_value}, "
        f"empirical={result.empirical_cramer_rate}, "
        f"inside_ci={result.candidate_inside_bootstrap_ci}, "
        f"verdict={result.verdict}"
    )


def format_jazz_constant_decomposition_report(
    result: JazzConstantDecompositionReport,
) -> str:
    return (
        f"status={result.status}, J={result.empirical_cramer_rate}, "
        f"dominant_segment={result.dominant_segment}, "
        f"dominant_pct={result.dominant_segment_percent_of_mgf:.2f}, "
        f"heavy_tail_correction={result.heavy_tail_correction}"
    )


def format_hercher_t_ni_report(result: HercherTNiReport) -> str:
    return (
        f"status={result.status}, samples={result.sample_count}, "
        f"segments={result.local_minimum_segments}, "
        f"max_Tn={result.max_T_times_n}, "
        f"p99={result.p99_T_times_n}"
    )


def format_paparella_nilpotency_report(result: PaparellaNilpotencyReport) -> str:
    last = result.levels[-1] if result.levels else None
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"last_n={None if last is None else last.n}, "
        f"last_traces_zero={None if last is None else last.all_traces_zero}, "
        f"last_max_escape={None if last is None else last.max_escape_depth}"
    )


def format_ollivier_ricci_report(result: OllivierRicciReport) -> str:
    return (
        f"status={result.status}, vertices={result.vertices}, "
        f"edges_checked={result.edges_checked}, min_kappa={result.min_curvature}, "
        f"max_kappa={result.max_curvature}"
    )


def format_snf_invariant_report(result: SNFInvariantReport) -> str:
    return (
        f"status={result.status}, vertices={result.vertices}, "
        f"edges={result.support_edges}, rank={result.integer_rank_i_minus_a_t}, "
        f"free_rank={result.cokernel_free_rank}, entry_gcd={result.entry_gcd}"
    )


def format_sandpile_report(result: SandpileReport) -> str:
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"V={result.vertices}, E={result.undirected_edges}, "
        f"components={result.components}, "
        f"forest_count={result.total_spanning_forest_count}"
    )


def format_cohomology_tower_report(result: CohomologyTowerReport) -> str:
    if result.levels:
        last = result.levels[-1]
        last_text = (
            f"last_k={last.modulus_power}, b1={last.first_betti}, "
            f"forest={last.sandpile_forest_count}"
        )
    else:
        last_text = "last=none"
    return f"status={result.status}, levels={len(result.levels)}, {last_text}"


def format_spectral_fingerprint_report(result: SpectralFingerprintReport) -> str:
    if result.levels:
        last = result.levels[-1]
        last_text = (
            f"last_k={last.modulus_power}, second={last.transfer_second_abs}, "
            f"maxplus={last.max_plus_mean_debt}, "
            f"harmonic={last.harmonic_dimension}"
        )
    else:
        last_text = "last=none"
    return f"status={result.status}, levels={len(result.levels)}, {last_text}"


def format_pressure_report(result: PressureReport) -> str:
    return (
        f"status={result.status}, cutoff={result.valuation_cutoff}, "
        f"root_s={result.root_s:.6f}, P(1)={result.pressure_at_one:.6f}, "
        f"signal={result.contraction_dimension_signal}"
    )


def format_newton_polygon_report(result: NewtonPolygonReport) -> str:
    parts = ", ".join(
        f"p={item.prime}:vB={item.max_vp_B},vgap={item.max_vp_power_gap}"
        for item in result.summaries
    )
    return f"status={result.status}, words={result.words_scanned}, {parts}"


def format_spike_correlation_report(result: SpikeCorrelationReport) -> str:
    return (
        f"status={result.status}, starts={result.starts_checked}, "
        f"density={result.spike_density:.4f}, "
        f"adjacent={result.adjacent_spike_density:.4f}, "
        f"independent={result.independent_adjacent_density:.4f}, "
        f"negative_signal={result.negative_correlation_signal}"
    )


def format_magnitude_report(result: MagnitudeReport) -> str:
    magnitude = "n/a" if result.magnitude is None else f"{result.magnitude:.6f}"
    return (
        f"status={result.status}, points={result.sampled_points}, "
        f"scale={result.scale}, magnitude={magnitude}"
    )


def format_cohomology_report(result: CohomologyReport) -> str:
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"V={result.vertices}, E={result.undirected_edges}, "
        f"components={result.components}, b1={result.first_betti}, "
        f"witnesses={len(result.cycle_witnesses)}"
    )


def format_lyapunov_artifact(result: LyapunovTemplateArtifact) -> str:
    return (
        f"status={result.status}, proof_claim={result.proof_claim}, "
        f"k={result.modulus_power}, ell={result.mod3_power}, "
        f"degree={result.degree}, basis={len(result.basis)}, "
        f"constraints={result.constraints}, solver={result.solver}"
    )


def format_reverse_frontier_report(result: ReverseFrontierReport) -> str:
    return (
        f"status={result.status}, checked={result.unresolved_checked}, "
        f"depth={result.reverse_depth}, nodes={result.nodes_generated}, "
        f"hits={len(result.hits)}, misses={len(result.misses)}"
    )


def format_formal_artifact_report(result: FormalArtifactReport) -> str:
    return (
        f"status={result.status}, exported={result.exported}, "
        f"verified={result.verified}, lean={result.lean_skeleton_status}"
    )


def format_cover_mass_report(result: CoverMassReport) -> str:
    return (
        f"status={result.status}, antichain={result.antichain_valid}, "
        f"partition={result.partition_valid}, "
        f"certified_mass={result.certified_mass_num}/{result.certified_mass_den}, "
        f"frontier_mass={result.frontier_mass_num}/{result.frontier_mass_den}, "
        f"total={result.total_mass_num}/{result.total_mass_den}, "
        f"overlaps={len(result.overlap_witnesses)}"
    )


def format_frontier_analysis_report(result: FrontierAnalysisReport) -> str:
    if not result.top:
        return f"status={result.status}, frontier=0"
    leader = result.top[0]
    return (
        f"status={result.status}, frontier={result.frontier_classes}, "
        f"top_residue={leader.residue} mod 2^{leader.modulus_power}, "
        f"m={leader.m}, A={leader.A}, debt={leader.debt:.3f}, "
        f"initial_ones={leader.initial_ones}, nearest={leader.nearest_convergent}"
    )


def format_mersenne_tail_report(result: MersenneTailReport) -> str:
    if not result.top_tails:
        return f"status={result.status}, tails=0/{result.frontier_classes}"
    leader = result.top_tails[0]
    discharged = sum(
        1
        for item in result.discharges
        if item.status == "all_subcylinders_certified_at_extra_precision"
    )
    return (
        f"status={result.status}, tails={result.tail_classes}/{result.frontier_classes}, "
        f"top={leader.residue} mod 2^{leader.modulus_power}, "
        f"run={leader.run_length}, defect={leader.defect}, "
        f"discharged={discharged}/{len(result.discharges)}"
    )


def format_mersenne_continuation_graph(result: MersenneContinuationGraph) -> str:
    if not result.worst_samples:
        return f"status={result.status}, samples=0"
    worst = result.worst_samples[0]
    return (
        f"status={result.status}, modulus={result.modulus}, "
        f"samples={result.samples}, classes={len(result.classes)}, "
        f"edges={len(result.edges)}, worst_R={worst.R}, "
        f"worst_landing_debt={worst.landing_debt:.3f}, "
        f"worst_steps={worst.post_run_steps}"
    )


def format_mersenne_refinement_report(result: MersenneRefinementReport) -> str:
    if not result.worst_by_modulus:
        return f"status={result.status}, moduli=0"
    chain = " -> ".join(
        f"{item.worst_class} mod {item.modulus}"
        for item in result.worst_by_modulus
    )
    worst = max(result.worst_by_modulus, key=lambda item: item.max_landing_debt)
    return (
        f"status={result.status}, R=[{result.R_min},{result.R_max}], "
        f"moduli={result.moduli}, worst_chain={chain}, "
        f"global_worst_R={worst.worst_R}, "
        f"global_worst_debt={worst.max_landing_debt:.6f}"
    )


def format_mersenne_progression_report(result: MersenneProgressionReport) -> str:
    return (
        f"status={result.status}, R={result.base_R}+{result.modulus}t, "
        f"t=[{result.t_min},{result.t_max}], samples={len(result.samples)}, "
        f"common_prefix_len={len(result.common_prefix)}, "
        f"distinct_prefixes={result.distinct_prefixes}, "
        f"worst_R={result.worst_R}, "
        f"worst_debt={result.worst_landing_debt:.6f}"
    )


def format_mersenne_branch_report(result: MersenneBranchReport) -> str:
    root = result.root
    child_bits = ", ".join(
        f"{child.prefix[:len(root.prefix)+1]}:{child.count}/{child.worst_landing_debt:.3f}"
        for child in root.children[:6]
    )
    return (
        f"status={result.status}, R={result.base_R}+{result.modulus}t, "
        f"t=[{result.t_min},{result.t_max}], root_prefix_len={len(root.prefix)}, "
        f"count={root.count}, worst_R={root.worst_R}, "
        f"worst_debt={root.worst_landing_debt:.6f}, children=[{child_bits}]"
    )


def format_mersenne_prefix_family_report(result: MersennePrefixFamilyReport) -> str:
    if result.hits:
        leader = max(result.hits, key=lambda sample: sample.landing_debt)
        leader_text = (
            f"best_hit_t={leader.t}, best_hit_R={leader.R}, "
            f"best_hit_debt={leader.landing_debt:.6f}"
        )
    else:
        leader_text = "best_hit_t=none"
    return (
        f"status={result.status}, R={result.base_R}+{result.modulus}t, "
        f"t=[{result.t_min},{result.t_max}], target={result.target_prefix}, "
        f"hits={result.hit_count}, misses={result.miss_count}, "
        f"gcd_gap={result.gcd_hit_gap}, {leader_text}"
    )


def format_tuple_merge_report(result: TupleMergeReport) -> str:
    passed = sum(1 for item in result.families if item.passed)
    parts = [
        f"{item.family.name}:{'ok' if item.passed else 'fail'}"
        f"({item.samples_checked - len(item.failures)}/{item.samples_checked})"
        for item in result.families
    ]
    return (
        f"status={result.status}, passed={passed}/{len(result.families)}, "
        f"families=[{', '.join(parts)}]"
    )


def format_power_ratio_report(result: PowerRatioReport) -> str:
    parts = []
    for summary in result.summaries:
        if summary.period44_mean_abs_delta is None:
            delta = "n/a"
        else:
            delta = f"{summary.period44_mean_abs_delta:.3f}"
        parts.append(f"base={summary.base:g}:mean={summary.mean_ratio:.3f},d44={delta}")
    return (
        f"status={result.status}, start={result.start}, "
        f"orbit_length={result.orbit_length}, reached_one={result.reached_one}, "
        f"summaries=[{', '.join(parts)}]"
    )


def format_compact_trace_report(result: CompactTraceReport) -> str:
    last = result.rows[-1]
    return (
        f"status={result.status}, start={result.start}, "
        f"rows={len(result.rows)}, reached_one={result.reached_one}, "
        f"invariant_valid={result.invariant_valid}, "
        f"last=(m={last.m}, x={last.x}, y={last.y}, z={last.z})"
    )


def format_odd_tree_sibling_report(result: OddTreeSiblingReport) -> str:
    children = ", ".join(
        f"{child.child}(a={child.exponent})"
        for child in result.children[:8]
    )
    verified = all(child.verified for child in result.children)
    return (
        f"status={result.status}, parent={result.parent}, "
        f"count={len(result.children)}, verified={verified}, "
        f"children=[{children}]"
    )


def format_champion_report(result: ChampionReport) -> str:
    height = result.max_height_champion
    stopping = result.longest_stopping_champion
    return (
        f"status={result.status}, interval=[{result.start},{result.stop}], "
        f"checked={result.checked}, "
        f"max_height=n{height.start}:{height.max_value}, "
        f"longest=n{stopping.start}:{stopping.steps_to_one}"
    )


def format_sensitivity_report(result: SensitivityReport) -> str:
    return (
        f"status={result.status}, start={result.start}, count={result.count}, "
        f"bit={result.bit}, steps={result.steps}, width={result.width}, "
        f"mean_hamming={result.mean_hamming_distance:.3f}, "
        f"max_hamming={result.max_hamming_distance}"
    )


def format_parity_layer_report(result: ParityLayerReport) -> str:
    leader = result.top_thresholds[0] if result.top_thresholds else None
    leader_text = (
        "none"
        if leader is None
        else (
            f"residue={leader.residue} mod 2^{result.length}, "
            f"q={leader.odd_steps}, threshold={leader.descent_threshold}"
        )
    )
    return (
        f"status={result.status}, length={result.length}, "
        f"favorable={result.favorable_vectors}/{result.vectors}, "
        f"worst_threshold={result.worst_threshold}, top={leader_text}"
    )


def format_divider_pattern_report(result: DividerPatternReport) -> str:
    counts = result.counts
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"odd_residues={result.odd_residues}, "
        f"S->S={counts.single_to_single}, S->M={counts.single_to_multiple}, "
        f"M->S={counts.multiple_to_single}, M->M={counts.multiple_to_multiple}, "
        f"longest_S={result.longest_single_run}, "
        f"longest_M={result.longest_multiple_run}"
    )


def format_cover_parity_report(result: CoverParityReport) -> str:
    if result.top:
        leader = result.top[0]
        leader_text = (
            f"top={leader.residue} mod 2^{leader.modulus_power}, "
            f"q={leader.odd_steps}, threshold={leader.descent_threshold}, "
            f"certified={leader.parity_certified}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, frontier={result.frontier_classes}, "
        f"parity_certified={result.parity_certified_classes}, "
        f"certified_density="
        f"{result.parity_certified_density_num}/{result.parity_certified_density_den}, "
        f"remaining_density={result.remaining_density_num}/{result.remaining_density_den}, "
        f"{leader_text}"
    )


def format_post_exit_pointwise_report(result: PostExitPointwiseReport) -> str:
    if result.worst_state is None:
        worst = "none"
    else:
        worst = (
            f"R={result.worst_state.R}, "
            f"u2={result.worst_state.u_mod2} mod 2^{result.worst_state.u_mod2_power}, "
            f"u3={result.worst_state.u_mod3} mod 3^{result.worst_state.u_mod3_power}"
        )
    return (
        f"status={result.status}, k={result.mod2_power}, ell={result.mod3_power}, "
        f"R_values={result.R_values}, states={result.states}, "
        f"sample_lifts=2^{result.sample_lift_power}, "
        f"descended={result.descended_samples}, reentered={result.reentry_samples}, "
        f"out_of_range={result.out_of_range_reentry_samples}, "
        f"rho_max={result.max_row_survival_num}/{result.max_row_survival_den}, "
        f"perron={result.perron_eigenvalue_estimate}, "
        f"finite_ratio_max={result.finite_ratio_max}, worst=({worst})"
    )


def format_post_exit_pointwise_ladder_report(
    result: PostExitPointwiseLadderReport,
) -> str:
    pieces = [
        f"(k={level.mod2_power}, ell={level.mod3_power}, "
        f"rho={level.max_row_survival_num}/{level.max_row_survival_den}, "
        f"status={level.status})"
        for level in result.levels
    ]
    return f"status={result.status}, levels={len(result.levels)}, " + "; ".join(pieces)


def format_post_exit_scaled_perron_report(result: PostExitScaledPerronReport) -> str:
    pieces = []
    for level in result.levels:
        worst = (
            "none"
            if level.worst_ratio_state is None
            else (
                f"R={level.worst_ratio_state.R}, "
                f"u2={level.worst_ratio_state.u_mod2}, "
                f"u3={level.worst_ratio_state.u_mod3}"
            )
        )
        pieces.append(
            f"(k={level.mod2_power}, ell={level.mod3_power}, "
            f"scale={level.power_scale_estimate:.6f}, "
            f"ratio_max={level.finite_ratio_max}, "
            f"inf={level.infinite_ratio_rows}, "
            f"rho={level.constant_weight_rho_max_num}/"
            f"{level.constant_weight_rho_max_den}, worst_ratio={worst})"
        )
    return f"status={result.status}, levels={len(result.levels)}, " + "; ".join(pieces)


def format_post_exit_super_eigen_report(result: PostExitSuperEigenReport) -> str:
    pieces = []
    for level in result.levels:
        worst = (
            "none"
            if level.worst_transient_state is None
            else (
                f"R={level.worst_transient_state.R}, "
                f"u2={level.worst_transient_state.u_mod2}, "
                f"u3={level.worst_transient_state.u_mod3}"
            )
        )
        pieces.append(
            f"(k={level.mod2_power}, ell={level.mod3_power}, "
            f"lambda_super={level.lambda_super:.6f}, "
            f"alpha={level.alpha:.6f}, "
            f"closed_sccs={level.closed_sccs}, "
            f"sccs_skipped={level.sccs_skipped}, "
            f"worst={worst})"
        )
    return f"status={result.status}, levels={len(result.levels)}, " + "; ".join(pieces)


def format_tail_family_report(result: TailFamilyReport) -> str:
    if result.top_dangerous:
        leader = result.top_dangerous[0]
        leader_text = (
            f"top_u={leader.u_residue} mod 2^{leader.u_mod_power}, "
            f"canonical_R={leader.canonical_R}, "
            f"residue={leader.residue} mod 2^{leader.modulus_power}, "
            f"ones={leader.forced_initial_ones}, debt={leader.debt:.3f}, "
            f"rep_m={leader.representative_descent_m}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, R={result.R}, u_mod_power={result.u_mod_power}, "
        f"certified={result.certified_count}/{result.samples}, "
        f"certified_density={result.certified_density_num}/{result.certified_density_den}, "
        f"unresolved_density={result.unresolved_density_num}/{result.unresolved_density_den}, "
        f"{leader_text}"
    )


def format_tail_renormalization_report(result: TailRenormalizationReport) -> str:
    if result.path:
        first = result.path[0]
        last = result.path[-1]
        path_text = (
            f"first=(R={first.R}, u={first.u}, c={first.c}, "
            f"next_R={first.next_R}, next_u={first.next_u}), "
            f"last=(R={last.R}, u={last.u}, c={last.c}, "
            f"next_R={last.next_R}, next_u={last.next_u})"
        )
    else:
        path_text = "path=empty"
    return (
        f"status={result.status}, R={result.R}, u={result.u_start}, "
        f"steps={result.steps}, total_m={result.total_m}, "
        f"total_A={result.total_A}, total_debt={result.total_debt:.3f}, "
        f"descended={result.descended}, {path_text}"
    )


def format_tail_renormalization_family_report(
    result: TailRenormalizationFamilyReport,
) -> str:
    if result.top_dangerous:
        leader = result.top_dangerous[0]
        last = leader.path[-1] if leader.path else None
        leader_text = (
            f"top_u={leader.u_start}, top_debt={leader.total_debt:.3f}, "
            f"top_steps={leader.steps}, "
            f"top_last_R={last.next_R if last is not None else 'none'}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, R={result.R}, "
        f"u_mod_power={result.u_mod_power}, samples={result.samples}, "
        f"descended={result.descended_count}, "
        f"left_tail={result.left_tail_count}, max_steps={result.max_steps}, "
        f"max_total_debt={result.max_total_debt:.3f}, {leader_text}"
    )


def format_tail_exit_lemma_report(result: TailExitLemmaReport) -> str:
    if result.unresolved:
        leader = result.unresolved[0]
        unresolved_text = (
            f"top_unresolved=(R={leader.R}, u={leader.u_residue} "
            f"mod 2^{leader.u_mod_power}, blocks={leader.blocks})"
        )
    else:
        unresolved_text = "top_unresolved=none"
    return (
        f"status={result.status}, R={result.initial_R}, "
        f"u_mod=2^{result.initial_u_mod_power}, "
        f"nodes={result.nodes_processed}, splits={result.split_count}, "
        f"transitions={result.transition_count}, exited={result.exited_count}, "
        f"unresolved={result.unresolved_count}, "
        f"max_terminal_debt={result.max_terminal_debt:.3f}, {unresolved_text}"
    )


def format_tail_internal_step_report(result: TailInternalStepReport) -> str:
    return (
        f"status={result.status}, R=[{result.R_min},{result.R_max}], "
        f"u_mod=2^{result.u_mod_power}, cases={result.cases_checked}, "
        f"all_match={result.all_match}"
    )


def format_tail_subautomaton_spectrum_report(
    result: TailSubautomatonSpectrumReport,
) -> str:
    perron = (
        "n/a"
        if result.perron_eigenvalue is None
        else f"{result.perron_eigenvalue:.6f}"
    )
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"prefix_ones={result.prefix_ones}, states={result.tail_states}, "
        f"survival={result.survival_mass_num}/{result.survival_mass_den}, "
        f"perron={perron}, top={result.top_tail_residue}"
    )


def format_tail_pointwise_ratio_report(result: TailPointwiseRatioReport) -> str:
    ratio = (
        "inf"
        if result.infinite_ratio_rows
        else (
            "n/a"
            if result.finite_ratio_max is None
            else f"{result.finite_ratio_max:.6f}"
        )
    )
    return (
        f"status={result.status}, k={result.modulus_power}, "
        f"prefix_ones={result.prefix_ones}, states={result.tail_states}, "
        f"zero_rows={result.zero_survival_rows}, "
        f"full_rows={result.full_survival_rows}, "
        f"max_row_survival="
        f"{result.max_row_survival_num}/{result.max_row_survival_den}, "
        f"constant_rho_max={result.constant_weight_rho_max}, "
        f"perron_right_est={result.perron_eigenvalue_estimate}, "
        f"rho_max={ratio}, worst={result.worst_residue}"
    )


def format_tail_spectral_ladder_report(result: TailSpectralLadderReport) -> str:
    return (
        f"status={result.status}, levels={len(result.levels)}, "
        f"prefix_ones={result.prefix_ones}, "
        f"max_perron={result.max_perron_eigenvalue}, "
        f"max_survival={result.max_survival_mass_num}/{result.max_survival_mass_den}"
    )


def format_tail_lte_report(result: TailLTEReport) -> str:
    return (
        f"status={result.status}, R=[{result.R_min},{result.R_max}], "
        f"all_match={result.all_match}, worst_R={result.worst_debt_R}, "
        f"worst_debt={result.worst_block_debt}"
    )


def format_tail_lyapunov_lp_report(result: TailLyapunovLPReport) -> str:
    return (
        f"status={result.status}, R0={result.R0}, "
        f"lambda={result.spectral_lambda_bound:.6f}, "
        f"gap={result.spectral_gap:.6f}, drop={result.lte_drop_bound}, "
        f"beta={result.beta}, gamma={result.gamma}, objective={result.objective}"
    )


def format_cover_tail_report(result: CoverTailReport) -> str:
    if result.top_tails:
        leader = result.top_tails[0]
        leader_text = (
            f"top={leader.residue} mod 2^{leader.modulus_power}, "
            f"R={leader.R}, u={leader.u_residue} mod 2^{leader.u_mod_power}, "
            f"canonical_R={leader.canonical_R}, "
            f"ones={leader.forced_initial_ones}, debt={leader.debt:.3f}, "
            f"rep_m={leader.representative_descent_m}"
        )
    else:
        leader_text = "top=none"
    return (
        f"status={result.status}, frontier={result.frontier_classes}, "
        f"tails={result.tail_classes}, "
        f"tail_density={result.tail_density_num}/{result.tail_density_den}, "
        f"{leader_text}"
    )
