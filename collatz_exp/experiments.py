"""Command-line experiments for the Collatz certificate search package."""

from __future__ import annotations

import argparse

from .branch_table import branch_table_report
from .certificates import certificate_from_residue, verify_descent_certificate
from .champions import champion_report
from .cf_convergent_slope import cf_convergent_slope_hypothesis_report
from .cohomology import cohomology_report
from .cohomology_tower import cohomology_tower_report
from .cohn_elkies import cohn_elkies_walsh_bound
from .compact_trace import compact_trace_report
from .cover import load_cover_report, run_certificate_cover
from .cover_mass import cover_mass_report
from .cover_parity import analyze_cover_parity
from .cover_spectrum import cover_survival_spectrum
from .constrained_jsr import (
    christoffel_filtered_jsr_report,
    christoffel_slope_constrained_jsr_report,
    constrained_jsr_report,
    constrained_projective_jsr_report,
    tail_aware_markov_lyapunov_report,
    tail_aware_lte_closed_projective_jsr_report,
    tail_aware_projective_jsr_report,
)
from .constrained_karp import (
    constrained_karp_jsr_report,
    karp_slope_joint_sweep_report,
    tail_cycle_realizability_sweep_report,
)
from .core import hardest_first_descent_under_power
from .cycles import scan_near_balanced_cycles
from .cycle_tower import cycle_exclusion_tower_report
from .cycles_eliahou import cycle_length_screen
from .density_lp import density_bound
from .divider_patterns import divider_pattern_report
from .formal_artifacts import formal_artifact_report
from .foster_drift import (
    chang_bit4_balance_audit_report,
    foster_drift_report,
    m_step_foster_drift_k8_report,
    m_step_foster_drift_report,
    pointwise_descent_audit_report,
)
from .frontier_analysis import analyze_cover_frontier
from .frontier_dashboard import (
    format_frontier_dashboard_report,
    frontier_dashboard_report,
)
from .furstenberg import furstenberg_lyapunov_report
from .graph_curvature import ollivier_ricci_report
from .graph_tree import odd_tree_sibling_report
from .harmonic_class import harmonic_class_identification_report
from .hercher import hercher_t_ni_report
from .hodge import hodge_report
from .lll_cycles import cycle_lattice_report
from .jazz_constant import (
    jazz_constant_closed_form_report,
    jazz_constant_decomposition_report,
)
from .chang_phantom_gain import (
    chang_R_K_identity_report,
    jazz_constant_high_precision_from_identity_report,
)
from .lift_realizability import lift_realizability_report
from .magnitude import magnitude_report
from .mersenne import analyze_mersenne_tails, profile_mersenne
from .max_plus import max_plus_debt_report
from .mersenne_continuation import (
    analyze_mersenne_branches,
    analyze_mersenne_prefix_family,
    analyze_mersenne_progression,
    build_mersenne_continuation_graph,
    refine_mersenne_continuation_moduli,
)
from .mixed import explore_mixed_automaton
from .mixed_harmonic_class import (
    mixed_harmonic_class_report,
    obstruction_lyapunov_correction_report,
)
from .mixed_tensor import mixed_tensor_rank_report
from .newton_polygons import newton_polygon_report
from .orbit_lyapunov import orbit_lyapunov_beta_sweep_report
from .orbit_renewal import (
    orbit_renewal_descent_report,
    orbit_renewal_markov_cramer_report,
    orbit_renewal_n0_stability_report,
    orbit_renewal_per_k_mgf_report,
    orbit_renewal_spike_decomposition_report,
    renewal_drift_phase_decomposed_report,
    renewal_drift_phase_decomposed_n0_stability_report,
    renewal_drift_per_step_report,
)
from .orbit_renewal_tda import orbit_renewal_tda_report
from .phase_lyapunov import (
    DEFAULT_ALPHA_GRID,
    DEFAULT_BETA_GRID,
    DEFAULT_GAMMA_DIFF_GRID,
    phase_lyapunov_search_report,
)
from .perron_certificate import (
    format_perron_certificate_report,
    perron_certificate_report,
)
from .pecm_consistency import (
    format_pecm_cross_resolution_consistency_report,
    pecm_cross_resolution_consistency_report,
)
from .pecm_vector_export import post_exit_common_alpha_vector_exports
from .renewal_bootstrap import renewal_bootstrap_calibration_report
from .renewal_correlation import (
    format_renewal_correlation_report,
    renewal_correlation_report,
)
from .parity import parity_layer_report
from .paparella import paparella_nilpotency_report
from .post_exit_baker import (
    dpe_baker_certification_report,
    dpe_continued_fraction_certification_report,
    dpe_convergent_atlas_report,
)
from .post_exit_lasota_yorke import lasota_yorke_report
from .post_exit_lyapunov import (
    dpe_structural_bound_report,
    psi_symbolic_fit_report,
    state_debt_lyapunov_report,
    unified_lyapunov_lp_report,
)
from .post_exit_map import (
    post_exit_pointwise_ladder_report,
    post_exit_pointwise_report,
    post_exit_scaled_perron_report,
    post_exit_super_eigen_report,
)
from .power_ratio import power_ratio_report
from .qnp1_audit import qnp1_realizability_report
from .qnp1_phase_transition import Q_GRID, qnp1_phase_transition_report
from .rozier_abc_audit import rozier_abc_audit_report
from .stern_brocot_synthesis import (
    save_megasynthesis_executive_summary,
    stern_brocot_megasynthesis_report,
)
from .reports import (
    format_cohomology_report,
    format_compact_trace_report,
    format_baker_certification_report,
    format_certificate_cover_report,
    format_champion_report,
    format_christoffel_filtered_jsr_report,
    format_christoffel_slope_constrained_jsr_report,
    format_constrained_karp_jsr_report,
    format_cover_mass_report,
    format_cover_parity_report,
    format_cover_survival_spectrum,
    format_cohn_elkies_walsh_report,
    format_cohomology_tower_report,
    format_constrained_jsr_report,
    format_constrained_projective_jsr_report,
    format_tail_aware_projective_jsr_report,
    format_tail_aware_markov_lyapunov_report,
    format_tail_cycle_realizability_report,
    format_convergent_atlas_report,
    format_continued_fraction_certification_report,
    format_cycle_scan_summary,
    format_cycle_length_screen,
    format_cycle_lattice_report,
    format_cycle_exclusion_tower_report,
    format_certificate,
    format_cf_convergent_slope_hypothesis_report,
    format_cover_summary,
    format_density_bound,
    format_divider_pattern_report,
    format_dpe_structural_bound_report,
    format_formal_artifact_report,
    format_foster_drift_report,
    format_chang_bit4_balance_audit_report,
    format_m_step_foster_drift_k8_report,
    format_m_step_foster_drift_report,
    format_pointwise_descent_audit_report,
    format_frontier_analysis_report,
    format_furstenberg_lyapunov_report,
    format_first_descent,
    format_hodge_report,
    format_harmonic_class_identification_report,
    format_jazz_constant_closed_form_report,
    format_jazz_constant_decomposition_report,
    format_chang_R_K_identity_report,
    format_karp_slope_joint_sweep_report,
    format_hercher_t_ni_report,
    format_lasota_yorke_report,
    format_lift_realizability_report,
    format_mixed_harmonic_class_report,
    format_magnitude_report,
    format_mixed_summary,
    format_mixed_tensor_rank_report,
    format_max_plus_debt_report,
    format_mori_mixed_first_return_report,
    format_newton_polygon_report,
    format_ollivier_ricci_report,
    format_orbit_lyapunov_beta_sweep_report,
    format_orbit_renewal_markov_cramer_report,
    format_orbit_renewal_n0_stability_report,
    format_orbit_renewal_per_k_mgf_report,
    format_orbit_renewal_tda_report,
    format_phase_lyapunov_search_report,
    format_obstruction_lyapunov_correction_report,
    format_mersenne_tail_report,
    format_mersenne_continuation_graph,
    format_mersenne_branch_report,
    format_mersenne_prefix_family_report,
    format_mersenne_progression_report,
    format_mersenne_refinement_report,
    format_odd_tree_sibling_report,
    format_parity_layer_report,
    format_paparella_nilpotency_report,
    format_power_ratio_report,
    format_qnp1_phase_transition_report,
    format_qnp1_realizability_report,
    format_renewal_bootstrap_calibration_report,
    format_renewal_descent_report,
    format_renewal_drift_phase_decomposed_report,
    format_renewal_drift_phase_decomposed_n0_stability_report,
    format_renewal_drift_per_step_report,
    format_renewal_spike_decomposition_report,
    format_psi_symbolic_fit_report,
    format_post_exit_pointwise_ladder_report,
    format_post_exit_pointwise_report,
    format_post_exit_scaled_perron_report,
    format_post_exit_super_eigen_report,
    format_sensitivity_report,
    format_sandpile_report,
    format_snf_invariant_report,
    format_spike_correlation_report,
    format_state_debt_lyapunov_report,
    format_spectral_fingerprint_report,
    format_cover_tail_report,
    format_stern_brocot_megasynthesis_report,
    format_tail_family_report,
    format_tail_renormalization_family_report,
    format_tail_renormalization_report,
    format_tail_exit_lemma_report,
    format_tail_internal_step_report,
    format_tail_lte_report,
    format_tail_lyapunov_lp_report,
    format_tail_pointwise_ratio_report,
    format_tail_spectral_ladder_report,
    format_tail_subautomaton_spectrum_report,
    format_tao_characteristic_decay_report,
    format_tao_syrac_empirical_report,
    format_transfer_spectrum,
    format_pressure_report,
    format_walsh_transfer_report,
    format_lyapunov_artifact,
    format_reverse_frontier_report,
    format_rozier_abc_audit_report,
    format_rigorous_squeeze_report,
    format_tuple_merge_report,
    format_unified_collatz_operator_report,
    format_unified_lyapunov_lp_report,
    format_valuation_mi_lag_report,
)
from .reverse_frontier import reverse_frontier_probe
from .sandpile import sandpile_report
from .search import adaptive_cover
from .sensitivity import sensitivity_report
from .snf_invariants import snf_invariant_report
from .sos_lyapunov import lyapunov_template_artifact
from .spike_dpp import spike_correlation_report
from .spectral_fingerprint import spectral_fingerprint_report
from .squeeze_bounds import rigorous_squeeze_report
from .tail_family import (
    analyze_cover_tail_frontier,
    analyze_tail_family,
    tail_renormalization_family_report,
    tail_renormalization_report,
)
from .tail_lemma import prove_tail_exit_cylinders, tail_internal_step_report
from .tail_lte import tail_lte_report
from .tail_lyapunov import tune_tail_lyapunov_lp
from .tail_spectral import (
    tail_pointwise_ratio_scan,
    tail_spectral_ladder,
    tail_subautomaton_spectrum,
)
from .tao_syrac import tao_characteristic_decay_report, tao_syrac_empirical_report
from .transfer_op import transfer_spectrum
from .thermodynamic import pressure_report
from .tuple_merges import tuple_merge_report
from .unified_operator import mori_mixed_first_return_report, unified_collatz_operator_report
from .valuation_mi import valuation_mi_lag_report
from .walsh_transfer import walsh_transfer_report


def _parse_int_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def _parse_pair_tuple(value: str) -> tuple[tuple[int, int], ...]:
    pairs: list[tuple[int, int]] = []
    for item in value.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        left, sep, right = stripped.partition(":")
        if not sep:
            raise ValueError(f"expected pair like k:ell, got {stripped!r}")
        pairs.append((int(left), int(right)))
    return tuple(pairs)


def _parse_float_tuple(value: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in value.split(",") if item.strip())


def _parse_qnp1_param(value: str | None) -> int:
    if value is None:
        return 5
    stripped = value.strip()
    if not stripped:
        return 5
    if "=" in stripped:
        name, raw = stripped.split("=", 1)
        if name.strip() != "q":
            raise ValueError(f"expected q=<odd integer>, got {value!r}")
        stripped = raw.strip()
    return int(stripped)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="run a short deterministic smoke experiment",
    )
    parser.add_argument(
        "--frontier-dashboard",
        action="store_true",
        help="rank next proof-search attack surfaces from saved reports",
    )
    parser.add_argument(
        "--frontier-dashboard-dir",
        default="docs/reports",
        help="directory containing saved JSON reports for --frontier-dashboard",
    )
    parser.add_argument(
        "--renewal-correlation",
        action="store_true",
        help="long-range correlation audit of renewal series (Polli check)",
    )
    parser.add_argument(
        "--renewal-correlation-orbits",
        type=int,
        default=150,
        help="orbit count for --renewal-correlation",
    )
    parser.add_argument(
        "--renewal-correlation-bits",
        type=int,
        default=1000,
        help="bit length of random odd starts for --renewal-correlation",
    )
    parser.add_argument(
        "--renewal-correlation-max-lag",
        type=int,
        default=50,
        help="maximum autocorrelation lag for --renewal-correlation",
    )
    parser.add_argument(
        "--renewal-correlation-seed",
        type=int,
        default=0,
        help="random seed for --renewal-correlation",
    )
    parser.add_argument(
        "--renewal-correlation-output",
        type=str,
        default=None,
        help="write --renewal-correlation JSON report to this path",
    )
    parser.add_argument(
        "--perron-certificate",
        action="store_true",
        help="exact-rational Collatz-Wielandt PECM spectral certificates",
    )
    parser.add_argument(
        "--perron-certificate-configs",
        type=str,
        default="8:2,10:3",
        help="k:ell levels for --perron-certificate",
    )
    parser.add_argument(
        "--perron-certificate-iterations",
        type=int,
        default=200,
        help="float power iterations for --perron-certificate",
    )
    parser.add_argument(
        "--perron-certificate-output",
        type=str,
        default=None,
        help="write --perron-certificate JSON report to this path",
    )
    parser.add_argument(
        "--pecm-vector-export",
        action="store_true",
        help="export common-alpha positive PECM resolvent vectors",
    )
    parser.add_argument(
        "--pecm-vector-export-configs",
        type=str,
        default="4:0,6:1,8:2",
        help="k:ell levels for --pecm-vector-export",
    )
    parser.add_argument(
        "--pecm-common-alpha",
        type=float,
        default=0.55,
        help="shared resolvent alpha for PECM vector/refinement reports",
    )
    parser.add_argument(
        "--pecm-vector-export-output",
        type=str,
        default=None,
        help="write --pecm-vector-export JSON report to this path",
    )
    parser.add_argument(
        "--pecm-cross-resolution",
        action="store_true",
        help="compare a common-alpha exact-Galerkin PECM refinement ladder",
    )
    parser.add_argument(
        "--pecm-cross-resolution-configs",
        type=str,
        default="4:0,6:1,8:2",
        help="coarse-to-fine k:ell levels for --pecm-cross-resolution",
    )
    parser.add_argument(
        "--pecm-cross-resolution-output",
        type=str,
        default=None,
        help="write --pecm-cross-resolution JSON report to this path",
    )
    parser.add_argument(
        "--pecm-max-materialized-states",
        type=int,
        default=250_000,
        help=(
            "safety limit for in-memory PECM vector/refinement diagnostics; "
            "larger levels require a future streaming path"
        ),
    )
    parser.add_argument(
        "--pecm-max-materialized-transitions",
        type=int,
        default=2_000_000,
        help=(
            "target-entry budget for in-memory PECM vector/refinement "
            "diagnostics"
        ),
    )
    parser.add_argument(
        "--max-hardness-power",
        type=int,
        default=16,
        help="largest K for hardest first-descent search",
    )
    parser.add_argument(
        "--cover-depth",
        type=int,
        default=18,
        help="adaptive cover depth",
    )
    parser.add_argument(
        "--cover-nodes",
        type=int,
        default=100_000,
        help="adaptive cover node limit",
    )
    parser.add_argument(
        "--mersenne",
        action="store_true",
        help="print Mersenne obstruction profiles",
    )
    parser.add_argument(
        "--mixed",
        action="store_true",
        help="run the experimental mixed 2/3-residue automaton",
    )
    parser.add_argument(
        "--cycles",
        action="store_true",
        help="run a bounded exact cycle-word scan",
    )
    parser.add_argument(
        "--academic",
        action="store_true",
        help="run academic-inspired finite artifacts",
    )
    parser.add_argument(
        "--all-things",
        action="store_true",
        help="run the broader experimental artifact suite from recent ideas",
    )
    parser.add_argument(
        "--cohomology",
        action="store_true",
        help="run finite transition-graph cohomology artifact",
    )
    parser.add_argument(
        "--max-plus",
        action="store_true",
        help="run max-plus cycle-mean debt diagnostic on a truncated residue graph",
    )
    parser.add_argument("--max-plus-power", type=int, default=6)
    parser.add_argument("--max-plus-lift-power", type=int, default=4)
    parser.add_argument("--jsr-power", type=int, default=6)
    parser.add_argument("--jsr-max-valuation", type=int, default=10)
    parser.add_argument(
        "--constrained-projective-jsr",
        action="store_true",
        help="compute exact scalar/projective JSR on finite legal-residue quotients",
    )
    parser.add_argument(
        "--constrained-projective-powers",
        type=str,
        default="4,6,8,10",
    )
    parser.add_argument(
        "--tail-aware-projective-jsr",
        action="store_true",
        help="compute bounded tail-aware projective JSR in (R,u mod 2^q) coordinates",
    )
    parser.add_argument(
        "--tail-aware-lte-closed-jsr",
        action="store_true",
        help="compute tail-aware projective JSR with deeper-tail overflow compressed back by LTE/forced-run closure",
    )
    parser.add_argument(
        "--tail-aware-markov-lyapunov",
        action="store_true",
        help="compute stationary Markov-average growth on the LTE-closed tail-aware graph",
    )
    parser.add_argument(
        "--christoffel-filtered-jsr",
        action="store_true",
        help="scan bounded LTE-closed tail cycles through a Christoffel-compatible parity filter",
    )
    parser.add_argument(
        "--christoffel-slope-constrained-jsr",
        action="store_true",
        help="scan bounded LTE-closed tail cycles through an upper-Christoffel slope window",
    )
    parser.add_argument(
        "--constrained-karp-jsr",
        action="store_true",
        help="run Karp on the LTE-closed tail graph crossed with a finite balanced-word automaton",
    )
    parser.add_argument(
        "--karp-slope-joint-sweep",
        action="store_true",
        help="jointly sweep constrained Karp period caps and upper-Christoffel slope precision",
    )
    parser.add_argument(
        "--tail-cycle-realizability",
        action="store_true",
        help="audit high-growth LTE-closed tail cycles against exact word lifting",
    )
    parser.add_argument(
        "--karp-slope-joint-output",
        type=str,
        default="docs/reports/karp_slope_joint_sweep.json",
        help="path for the joint Karp/slope sweep JSON artifact",
    )
    parser.add_argument(
        "--karp-slope-levels",
        type=str,
        default="5:4,6:5,7:6",
        help="comma-separated q:Rmax levels for the joint Karp/slope sweep",
    )
    parser.add_argument(
        "--tail-cycle-realizability-output",
        type=str,
        default="docs/reports/tail_cycle_realizability.json",
        help="path for the tail-cycle realizability JSON artifact",
    )
    parser.add_argument(
        "--tail-cycle-realizability-levels",
        type=str,
        default="5:4,6:5,7:6",
        help="comma-separated q:Rmax levels for the tail-cycle realizability audit",
    )
    parser.add_argument(
        "--tail-cycle-factor-threshold",
        type=float,
        default=1.0,
        help="minimum edge factor for cycles included in the realizability audit",
    )
    parser.add_argument(
        "--tail-cycle-max-cycles-scanned",
        type=int,
        default=200_000,
        help="maximum simple cycles scanned per level for tail-cycle realizability",
    )
    parser.add_argument(
        "--tail-cycle-lift-max-scan-power",
        type=int,
        default=32,
        help="maximum precision power allowed for tail-cycle cylinder closure checks",
    )
    parser.add_argument(
        "--tail-cycle-audit-all-cycles",
        action="store_true",
        help="classify every scanned tail cycle, while recording high-growth and positive-integer witnesses",
    )
    parser.add_argument(
        "--qnp1-realizability",
        nargs="?",
        const="q=5",
        default=None,
        help="run the qn+1 realizability audit, e.g. --qnp1-realizability q=5",
    )
    parser.add_argument(
        "--qnp1-realizability-output",
        type=str,
        default="docs/reports/qnp1_realizability_q5.json",
        help="path for the qn+1 realizability JSON artifact",
    )
    parser.add_argument(
        "--qnp1-realizability-levels",
        type=str,
        default="5:4,6:5,7:6",
        help="comma-separated tail_unit_power:Rmax levels for the qn+1 audit",
    )
    parser.add_argument(
        "--qnp1-phase-transition",
        action="store_true",
        help="compare qn+1 Diophantine cycle-factor bounds with bounded empirical scans",
    )
    parser.add_argument(
        "--qnp1-phase-transition-output",
        type=str,
        default="docs/reports/qnp1_phase_transition.json",
        help="path for the qn+1 phase-transition JSON artifact",
    )
    parser.add_argument(
        "--qnp1-phase-q-grid",
        type=str,
        default=",".join(str(q) for q in Q_GRID),
        help="comma-separated odd q values for --qnp1-phase-transition",
    )
    parser.add_argument(
        "--qnp1-phase-levels",
        type=str,
        default="5:4,6:5",
        help="comma-separated tail_unit_power:Rmax levels for --qnp1-phase-transition",
    )
    parser.add_argument("--qnp1-phase-m-max", type=int, default=100)
    parser.add_argument(
        "--rozier-abc-audit",
        action="store_true",
        help="run Rozier mu-hit and Collatz Theorem 4.1 finite diagnostics",
    )
    parser.add_argument(
        "--rozier-abc-output",
        type=str,
        default="docs/reports/rozier_abc_collatz_audit.json",
        help="path for the Rozier abc/Collatz JSON artifact",
    )
    parser.add_argument("--rozier-j-min", type=int, default=10)
    parser.add_argument("--rozier-j-max", type=int, default=50)
    parser.add_argument("--rozier-orbit-samples", type=int, default=10_000)
    parser.add_argument("--rozier-orbit-time-budget", type=float, default=300.0)
    parser.add_argument(
        "--cf-convergent-slope-hypothesis",
        action="store_true",
        help="analyze existing slope-realizability artifacts against CF convergents of log2(3)",
    )
    parser.add_argument(
        "--cf-convergent-slope-output",
        type=str,
        default="docs/reports/cf_convergent_slope_hypothesis.json",
        help="path for the CF-convergent slope hypothesis JSON artifact",
    )
    parser.add_argument(
        "--stern-brocot-megasynthesis",
        action="store_true",
        help="build the Stern-Brocot megasynthesis finite synthesis artifact",
    )
    parser.add_argument(
        "--stern-brocot-megasynthesis-output",
        type=str,
        default="docs/reports/stern_brocot_megasynthesis.json",
        help="path for the Stern-Brocot megasynthesis JSON artifact",
    )
    parser.add_argument(
        "--stern-brocot-megasynthesis-summary-output",
        type=str,
        default="docs/reports/megasynthesis_executive_summary.md",
        help="path for the human-readable megasynthesis summary",
    )
    parser.add_argument("--stern-brocot-cf-depth", type=int, default=20)
    parser.add_argument("--stern-brocot-tao-max-m", type=int, default=20)
    parser.add_argument("--stern-brocot-tao-random-count", type=int, default=100)
    parser.add_argument("--stern-brocot-tao-bootstrap-samples", type=int, default=1000)
    parser.add_argument("--stern-brocot-rozier-n-max", type=int, default=500)
    parser.add_argument("--stern-brocot-chang-max-K", type=int, default=80)
    parser.add_argument(
        "--tail-aware-levels",
        type=str,
        default="5:4,6:5,7:6,8:6,10:7",
        help="comma-separated q:Rmax levels for tail-aware projective JSR",
    )
    parser.add_argument("--christoffel-max-cycle-edges", type=int, default=10)
    parser.add_argument("--christoffel-max-cycles-scanned", type=int, default=50000)
    parser.add_argument("--christoffel-slope-tolerance", type=float, default=0.5)
    parser.add_argument("--constrained-karp-max-imbalance", type=int, default=1)
    parser.add_argument("--constrained-karp-max-period", type=int, default=4)
    parser.add_argument(
        "--karp-slope-periods",
        type=str,
        default="4,5,6",
        help="comma-separated automaton period caps for the joint sweep",
    )
    parser.add_argument(
        "--karp-slope-tolerances",
        type=str,
        default="0.5",
        help="comma-separated slope windows for the joint sweep",
    )
    parser.add_argument("--lift-realizability-power", type=int, default=6)
    parser.add_argument("--lift-realizability-max-valuation", type=int, default=6)
    parser.add_argument("--lift-realizability-max-period", type=int, default=8)
    parser.add_argument("--walsh-power", type=int, default=6)
    parser.add_argument("--walsh-lift-power", type=int, default=4)
    parser.add_argument("--ce-walsh-power", type=int, default=8)
    parser.add_argument("--sandpile-power", type=int, default=5)
    parser.add_argument("--sandpile-lift-power", type=int, default=3)
    parser.add_argument("--mixed-tensor-power", type=int, default=5)
    parser.add_argument("--mixed-tensor-mod3-power", type=int, default=2)
    parser.add_argument("--fusion-k-min", type=int, default=4)
    parser.add_argument("--fusion-k-max", type=int, default=6)
    parser.add_argument("--fusion-lift-power", type=int, default=3)
    parser.add_argument(
        "--lyapunov-artifact",
        action="store_true",
        help="emit finite polynomial Lyapunov/SOS scaffold summary",
    )
    parser.add_argument(
        "--reverse-frontier",
        action="store_true",
        help="probe unresolved cover classes against bounded inverse tree of 1",
    )
    parser.add_argument(
        "--formal-artifacts",
        action="store_true",
        help="export and locally verify certificate artifacts",
    )
    parser.add_argument(
        "--certificate-cover",
        action="store_true",
        help="run proof-facing certificate cover database search",
    )
    parser.add_argument(
        "--certificate-cover-depth",
        type=int,
        default=16,
        help="maximum depth for certificate cover database search",
    )
    parser.add_argument(
        "--certificate-cover-nodes",
        type=int,
        default=20_000,
        help="node budget for certificate cover database search",
    )
    parser.add_argument(
        "--cover-report-path",
        type=str,
        default=None,
        help="optional path to save certificate cover JSON report",
    )
    parser.add_argument(
        "--resume-cover-report",
        type=str,
        default=None,
        help="optional certificate cover JSON report to resume",
    )
    parser.add_argument(
        "--analyze-cover-report",
        type=str,
        default=None,
        help="analyze a saved certificate cover report",
    )
    parser.add_argument(
        "--frontier-top",
        type=int,
        default=10,
        help="number of dangerous frontier classes to include in analysis",
    )
    parser.add_argument(
        "--mersenne-tail-analysis",
        type=str,
        default=None,
        help="analyze Mersenne-tail cylinders in a saved cover report",
    )
    parser.add_argument(
        "--tail-extra-bits",
        type=int,
        default=6,
        help="extra bits to try when discharging Mersenne-tail cylinders",
    )
    parser.add_argument(
        "--mersenne-continuation",
        action="store_true",
        help="build a finite R mod M graph for Mersenne post-run continuations",
    )
    parser.add_argument(
        "--mersenne-R-max",
        type=int,
        default=128,
        help="largest R for Mersenne continuation profiling",
    )
    parser.add_argument(
        "--mersenne-modulus",
        type=int,
        default=16,
        help="modulus for grouping Mersenne continuation graph by R mod M",
    )
    parser.add_argument(
        "--mersenne-refinement",
        action="store_true",
        help="compare Mersenne continuation worst classes across nested moduli",
    )
    parser.add_argument(
        "--mersenne-moduli",
        type=str,
        default="16,32,64,128",
        help="comma-separated modulus ladder for Mersenne refinement",
    )
    parser.add_argument(
        "--mersenne-progression",
        action="store_true",
        help="analyze exact post-run words for R = base + modulus*t",
    )
    parser.add_argument("--progression-base", type=int, default=134)
    parser.add_argument("--progression-modulus", type=int, default=256)
    parser.add_argument("--progression-t-max", type=int, default=8)
    parser.add_argument("--progression-prefix", type=int, default=80)
    parser.add_argument(
        "--progression-max-steps",
        type=int,
        default=10_000,
        help="maximum accelerated steps when reconstructing Mersenne words",
    )
    parser.add_argument(
        "--mersenne-branches",
        action="store_true",
        help="build a valuation-prefix branch tree for the hard Mersenne progression",
    )
    parser.add_argument("--branch-depth", type=int, default=4)
    parser.add_argument(
        "--mersenne-prefix-family",
        action="store_true",
        help="test recurrence of a target valuation prefix in a Mersenne progression",
    )
    parser.add_argument(
        "--progression-target-prefix",
        type=str,
        default="4,1,2,1,1,1,6",
        help="comma-separated valuation prefix for --mersenne-prefix-family",
    )
    parser.add_argument(
        "--tuple-merges",
        action="store_true",
        help="check finite local tuple-merge families from graph observations",
    )
    parser.add_argument("--tuple-merge-samples", type=int, default=16)
    parser.add_argument(
        "--power-ratio",
        action="store_true",
        help="compute proportional-power-ratio graph diagnostics for one orbit",
    )
    parser.add_argument("--power-ratio-start", type=int, default=27)
    parser.add_argument("--power-ratio-max-steps", type=int, default=10_000)
    parser.add_argument(
        "--branch-table",
        action="store_true",
        help="print a finite jump/division branch-table diagnostic",
    )
    parser.add_argument("--branch-table-start", type=int, default=27)
    parser.add_argument(
        "--compact-trace",
        action="store_true",
        help="verify compact trace affine invariants for one odd start",
    )
    parser.add_argument("--compact-trace-start", type=int, default=19)
    parser.add_argument("--compact-trace-max-steps", type=int, default=10_000)
    parser.add_argument(
        "--champions",
        action="store_true",
        help="scan an interval for max-height and longest-stopping champions",
    )
    parser.add_argument("--champion-stop", type=int, default=10_000)
    parser.add_argument(
        "--odd-tree-siblings",
        action="store_true",
        help="check exact inverse odd-tree sibling formulas",
    )
    parser.add_argument("--odd-tree-parent", type=int, default=1)
    parser.add_argument("--odd-tree-count", type=int, default=8)
    parser.add_argument(
        "--sensitivity",
        action="store_true",
        help="measure finite bit-flip sensitivity of Collatz iterates",
    )
    parser.add_argument("--sensitivity-count", type=int, default=128)
    parser.add_argument("--sensitivity-bit", type=int, default=0)
    parser.add_argument("--sensitivity-steps", type=int, default=32)
    parser.add_argument(
        "--parity-layer",
        action="store_true",
        help="summarize Terras parity-vector cylinders at fixed base-2 depth",
    )
    parser.add_argument("--parity-length", type=int, default=16)
    parser.add_argument(
        "--divider-patterns",
        action="store_true",
        help="count finite transitions between single and multiple divider odd steps",
    )
    parser.add_argument("--divider-modulus-power", type=int, default=12)
    parser.add_argument("--divider-lookahead", type=int, default=16)
    parser.add_argument(
        "--cover-parity-overlay",
        type=str,
        default=None,
        help="overlay Terras parity cylinders on a saved certificate cover report",
    )
    parser.add_argument(
        "--cover-parity-output",
        type=str,
        default=None,
        help="optional path to save the cover parity overlay JSON artifact",
    )
    parser.add_argument(
        "--cover-survival-spectrum",
        type=str,
        default=None,
        help="build a substochastic survival spectrum for a saved cover report",
    )
    parser.add_argument(
        "--survival-sample-lift-power",
        type=int,
        default=4,
        help="binary lift depth for --cover-survival-spectrum",
    )
    parser.add_argument(
        "--survival-max-states",
        type=int,
        default=2048,
        help="largest frontier matrix to build for --cover-survival-spectrum",
    )
    parser.add_argument(
        "--cover-survival-output",
        type=str,
        default=None,
        help="optional path to save the survival spectrum JSON artifact",
    )
    parser.add_argument(
        "--tail-family",
        action="store_true",
        help="split and rank the Mersenne-tail family n = 2^R*u - 1",
    )
    parser.add_argument("--tail-R", type=int, default=20)
    parser.add_argument("--tail-u-mod-power", type=int, default=6)
    parser.add_argument(
        "--tail-odd-u-only",
        action="store_true",
        help="analyze only odd u residues to avoid recursively deeper pure tails",
    )
    parser.add_argument(
        "--tail-representative-max-steps",
        type=int,
        default=0,
        help="optional first-descent step cap for representative tail samples",
    )
    parser.add_argument(
        "--tail-renormalization",
        action="store_true",
        help="iterate the compressed Mersenne-tail block map for one representative",
    )
    parser.add_argument(
        "--tail-renormalization-family",
        action="store_true",
        help="rank compressed tail dynamics across u residues",
    )
    parser.add_argument(
        "--tail-u",
        type=int,
        default=1,
        help="u representative for --tail-renormalization",
    )
    parser.add_argument(
        "--tail-renorm-blocks",
        type=int,
        default=20,
        help="maximum compressed blocks for --tail-renormalization",
    )
    parser.add_argument(
        "--tail-renormalization-output",
        type=str,
        default=None,
        help="optional path to save tail-renormalization JSON artifact",
    )
    parser.add_argument(
        "--tail-exit-lemma",
        action="store_true",
        help="try to certify exact tail-cylinder exit under renormalization",
    )
    parser.add_argument("--tail-lemma-max-u-power", type=int, default=24)
    parser.add_argument("--tail-lemma-max-nodes", type=int, default=100_000)
    parser.add_argument(
        "--tail-internal-step",
        action="store_true",
        help="check the exact deterministic tail-depth decrement identity",
    )
    parser.add_argument(
        "--tail-subautomaton-spectrum",
        action="store_true",
        help="compute spectrum of tail-prefixed transition subblock",
    )
    parser.add_argument("--tail-spectrum-power", type=int, default=12)
    parser.add_argument("--tail-spectrum-prefix-ones", type=int, default=8)
    parser.add_argument("--tail-spectrum-lift-power", type=int, default=4)
    parser.add_argument(
        "--tail-spectral-ladder",
        action="store_true",
        help="check tail-subblock Perron values across multiple depths",
    )
    parser.add_argument("--tail-spectral-k-values", type=str, default="12,14,16,18,20")
    parser.add_argument(
        "--tail-pointwise-ratio",
        action="store_true",
        help="scan per-cylinder tail-subblock ratios for a pointwise certificate",
    )
    parser.add_argument(
        "--tail-lte",
        action="store_true",
        help="check LTE formula for pure Mersenne tail blocks",
    )
    parser.add_argument("--tail-lte-R-max", type=int, default=128)
    parser.add_argument(
        "--tail-lyapunov-lp",
        action="store_true",
        help="tune beta/gamma for the finite tail Lyapunov scaffold",
    )
    parser.add_argument("--tail-lyapunov-R0", type=int, default=20)
    parser.add_argument(
        "--post-exit-pointwise",
        action="store_true",
        help="scan the post-exit cylinder map for pointwise contraction",
    )
    parser.add_argument(
        "--post-exit-ladder",
        action="store_true",
        help="run post-exit pointwise scans over several (k,ell) pairs",
    )
    parser.add_argument(
        "--post-exit-scaled-perron",
        action="store_true",
        help="run the scaled target-cache PECM Perron/rate scan",
    )
    parser.add_argument(
        "--post-exit-scaled-perron-output",
        default=None,
        help="optional path for the scaled PECM Perron JSON artifact",
    )
    parser.add_argument(
        "--post-exit-super-eigen",
        action="store_true",
        help="build a positive resolvent super-eigenvector for PECM",
    )
    parser.add_argument(
        "--harmonic-class-identification",
        action="store_true",
        help="project the visible obstruction-class shadow onto finite H^1",
    )
    parser.add_argument(
        "--mixed-harmonic-class",
        action="store_true",
        help="project the mixed obstruction class onto finite mixed H^1",
    )
    parser.add_argument(
        "--obstruction-lyapunov-correction",
        action="store_true",
        help="extract the finite Hodge potential correcting the obstruction class",
    )
    parser.add_argument(
        "--post-exit-lasota-yorke",
        action="store_true",
        help="run empirical BV/Lasota-Yorke diagnostics for PECM",
    )
    parser.add_argument(
        "--psi-symbolic-fit",
        action="store_true",
        help="fit the obstruction Hodge potential against mixed-adic features",
    )
    parser.add_argument(
        "--unified-lyapunov-lp",
        action="store_true",
        help="solve the finite unified post-exit Lyapunov LP",
    )
    parser.add_argument(
        "--state-debt-lyapunov",
        action="store_true",
        help="solve the finite bucketed-state debt Lyapunov LP",
    )
    parser.add_argument(
        "--state-debt-lyapunov-output",
        default=None,
        help="optional path for the bucketed state-debt Lyapunov JSON artifact",
    )
    parser.add_argument(
        "--dpe-structural-bound",
        action="store_true",
        help="enumerate PECM edge D_PE values and fit a finite debt envelope",
    )
    parser.add_argument(
        "--dpe-structural-bound-output",
        default=None,
        help="optional path for the D_PE structural-bound JSON artifact",
    )
    parser.add_argument(
        "--dpe-baker-certification",
        action="store_true",
        help="compare PECM edge gaps with a configurable Baker-style floor",
    )
    parser.add_argument(
        "--dpe-continued-fraction-certification",
        action="store_true",
        help="compare PECM edge gaps with continued-fraction lower bounds",
    )
    parser.add_argument(
        "--dpe-continued-fraction-output",
        default=None,
        help="optional path for the D_PE continued-fraction JSON artifact",
    )
    parser.add_argument(
        "--dpe-convergent-atlas",
        action="store_true",
        help="check which log2(3) convergents occur as PECM reentry edges",
    )
    parser.add_argument(
        "--dpe-convergent-atlas-output",
        default=None,
        help="optional path for the D_PE convergent-atlas JSON artifact",
    )
    parser.add_argument(
        "--orbit-lyapunov-beta-sweep",
        action="store_true",
        help="sweep beta for running-debt Lyapunov candidates on actual orbits",
    )
    parser.add_argument(
        "--phase-lyapunov-search",
        action="store_true",
        help="search phase-aware per-step Lyapunov candidates on actual orbits",
    )
    parser.add_argument(
        "--foster-drift",
        action="store_true",
        help="audit Foster-style drift for V(n)=log2(n)+v2(n+1) on sampled windows",
    )
    parser.add_argument(
        "--m-step-foster-drift",
        action="store_true",
        help="audit m-step Foster-style drift for V(n)=log2(n)+v2(n+1)",
    )
    parser.add_argument(
        "--m-step-foster-drift-k8",
        action="store_true",
        help="audit m-step Foster drift through residue power k=8 for Chang resolution",
    )
    parser.add_argument(
        "--pointwise-descent-audit",
        action="store_true",
        help="search sampled pointwise hitting-time bounds for V(n)=log2(n)+v2(n+1)",
    )
    parser.add_argument(
        "--chang-bit4-audit",
        action="store_true",
        help="audit Chang 2603.25753 bit-4 balance at burst-ending times",
    )
    parser.add_argument(
        "--orbit-renewal-descent",
        action="store_true",
        help="aggregate actual orbits into tail-entry renewal excursions",
    )
    parser.add_argument(
        "--renewal-drift-per-step",
        action="store_true",
        help="bootstrap the per-step renewal drift identity on sampled excursions",
    )
    parser.add_argument(
        "--renewal-drift-phase-decomposed",
        action="store_true",
        help="bootstrap tail-internal vs post-exit renewal drift phases",
    )
    parser.add_argument(
        "--renewal-drift-phase-decomposed-n0",
        action="store_true",
        help="run phase-decomposed renewal drift across n0 windows",
    )
    parser.add_argument(
        "--orbit-renewal-spike-decomposition",
        action="store_true",
        help="decompose renewal increments by maximum valuation spike and estimate Cramer rate",
    )
    parser.add_argument(
        "--orbit-renewal-per-k-mgf",
        action="store_true",
        help="report per-spike-level conditional MGFs on a fixed lambda grid",
    )
    parser.add_argument(
        "--orbit-renewal-markov-cramer",
        action="store_true",
        help="estimate the tilted Markov-additive Cramer rate by spike class",
    )
    parser.add_argument(
        "--orbit-renewal-n0-stability",
        action="store_true",
        help="run renewal Cramer diagnostics across starting-magnitude ranges",
    )
    parser.add_argument(
        "--orbit-renewal-tda",
        action="store_true",
        help="sample renewal events and run H1 persistence diagnostics",
    )
    parser.add_argument(
        "--renewal-bootstrap-calibration",
        action="store_true",
        help="bootstrap renewal Cramer/drift estimates and compute saddlepoint tails",
    )
    parser.add_argument(
        "--valuation-mi-lags",
        action="store_true",
        help="compute accelerated-valuation mutual information for lags 1..20",
    )
    parser.add_argument(
        "--tao-syrac-empirical",
        action="store_true",
        help="compare empirical Syracuse residues with Tao's Syrac random variables",
    )
    parser.add_argument(
        "--tao-characteristic-decay",
        action="store_true",
        help="compare exact and empirical Tao Syracuse characteristic coefficients",
    )
    parser.add_argument(
        "--unified-collatz-operator",
        action="store_true",
        help="assemble finite projections of the unified Collatz operator model",
    )
    parser.add_argument(
        "--mori-mixed-first-return",
        action="store_true",
        help=(
            "build the mixed 2^k x 3^ell first-return quotient for "
            "Mori's N1 union N2"
        ),
    )
    parser.add_argument(
        "--mori-mixed-configs",
        type=str,
        default="6:2,8:3,10:3",
        help="comma-separated k:ell pairs for --mori-mixed-first-return",
    )
    parser.add_argument(
        "--rigorous-squeeze",
        action="store_true",
        help="assemble upper/lower-bound squeeze intervals from saved artifacts",
    )
    parser.add_argument(
        "--furstenberg-lyapunov",
        action="store_true",
        help="compute iid Geom(2) random-product Lyapunov baseline",
    )
    parser.add_argument("--furstenberg-steps", type=int, default=1_000_000)
    parser.add_argument(
        "--jazz-constant-test",
        action="store_true",
        help="stress-test I(0)=log(4/3)^2 against the renewal bootstrap artifact",
    )
    parser.add_argument(
        "--jazz-constant-decomposition",
        action="store_true",
        help="summarize spike-stratified decomposition of the renewal Cramer constant",
    )
    parser.add_argument(
        "--chang-R-K-identity",
        action="store_true",
        help="compare Chang's R(K) necklace sum with this framework's J_renewal",
    )
    parser.add_argument(
        "--hercher-t-ni",
        action="store_true",
        help="sample Hercher reciprocal-sum T(n_i) local-minimum segments",
    )
    parser.add_argument(
        "--paparella-nilpotency",
        action="store_true",
        help="check Paparella C_n trace nilpotency on finite truncations",
    )
    parser.add_argument("--post-exit-configs", type=str, default="8:2,10:3,12:4")
    parser.add_argument("--post-exit-k", type=int, default=8)
    parser.add_argument("--post-exit-ell", type=int, default=2)
    parser.add_argument(
        "--post-exit-R-values",
        type=str,
        default=",".join(str(value) for value in range(2, 31)),
    )
    parser.add_argument("--post-exit-sample-lift-power", type=int, default=2)
    parser.add_argument("--post-exit-max-steps", type=int, default=200)
    parser.add_argument("--post-exit-tail-reentry-min-R", type=int, default=2)
    parser.add_argument("--post-exit-perron-iterations", type=int, default=80)
    parser.add_argument("--post-exit-extension-iterations", type=int, default=400)
    parser.add_argument("--post-exit-alpha-margin", type=float, default=0.02)
    parser.add_argument(
        "--post-exit-operator-mode",
        choices=("dense_target_cache", "streaming", "gpu_target_cache", "auto"),
        default="dense_target_cache",
        help="PECM operator backend for Perron/super-eigen scans",
    )
    parser.add_argument(
        "--post-exit-chunk-rows",
        type=int,
        default=100_000,
        help="row chunk size for streaming PECM operator mode",
    )
    parser.add_argument(
        "--post-exit-dense-entry-limit",
        type=int,
        default=50_000_000,
        help="auto mode switches to streaming above this target-cache entry count",
    )
    parser.add_argument(
        "--post-exit-checkpoint",
        default=None,
        help="path to save/resume scaled Perron vector checkpoints",
    )
    parser.add_argument(
        "--post-exit-checkpoint-interval",
        type=int,
        default=1,
        help="save scaled Perron checkpoint every N iterations; 0 saves only final",
    )
    parser.add_argument("--lasota-samples", type=int, default=32)
    parser.add_argument("--lasota-iterates", type=int, default=10)
    parser.add_argument("--lasota-seed", type=int, default=0)
    parser.add_argument("--lyapunov-trajectory-samples", type=int, default=1000)
    parser.add_argument(
        "--lyapunov-height-mode",
        type=str,
        default="raw_log2",
        choices=(
            "raw_log2",
            "renormalized_3_over_2",
            "renormalized_plus_3_over_2",
            "renormalized_plus_log2_3",
        ),
    )
    parser.add_argument(
        "--lyapunov-debt-term",
        action="store_true",
        help="include the post-exit edge debt term gamma*D_PE in the finite LP",
    )
    parser.add_argument("--debt-bucket-width", type=float, default=0.1)
    parser.add_argument("--baker-C", type=float, default=1e-9)
    parser.add_argument("--baker-kappa", type=float, default=13.3)
    parser.add_argument("--convergent-max-denominator", type=int, default=1000)
    parser.add_argument("--orbit-samples", type=int, default=1_000_000)
    parser.add_argument("--phase-lyapunov-samples", type=int, default=100_000)
    parser.add_argument("--phase-lyapunov-max-steps-per-orbit", type=int, default=10_000)
    parser.add_argument(
        "--phase-lyapunov-alpha-grid",
        type=str,
        default="",
        help="optional comma-separated alpha grid; default is the phase Lyapunov anchor grid",
    )
    parser.add_argument(
        "--phase-lyapunov-beta-grid",
        type=str,
        default="",
        help="optional comma-separated beta grid; default is 0,1,4,8,16,32",
    )
    parser.add_argument(
        "--phase-lyapunov-gamma-diff-grid",
        type=str,
        default="",
        help="optional comma-separated gamma_PE-gamma_R grid",
    )
    parser.add_argument(
        "--phase-lyapunov-output",
        type=str,
        default="docs/reports/phase_lyapunov_search.json",
        help="path for the phase-aware Lyapunov search JSON artifact",
    )
    parser.add_argument(
        "--foster-drift-output",
        type=str,
        default="docs/reports/phase_lyapunov_foster_drift.json",
        help="path for the Foster-drift JSON artifact",
    )
    parser.add_argument(
        "--foster-drift-ranges",
        type=str,
        default="100:10000,10000:1000000,1000000:1000000000,1000000000:1000000000000,1000000000000:1000000000000000",
        help="comma-separated n_min:n_max ranges for --foster-drift",
    )
    parser.add_argument(
        "--foster-drift-residue-powers",
        type=str,
        default="2,3,4,5,6",
        help="comma-separated residue powers for --foster-drift",
    )
    parser.add_argument(
        "--foster-drift-tail-thresholds",
        type=str,
        default="0.5,1.0,2.0,4.0,8.0,16.0",
        help="comma-separated upper-tail thresholds for --foster-drift",
    )
    parser.add_argument("--foster-drift-hitting-max-steps", type=int, default=1000)
    parser.add_argument("--foster-drift-hitting-threshold", type=float, default=1.0)
    parser.add_argument(
        "--m-step-foster-drift-output",
        type=str,
        default="docs/reports/m_step_foster_drift.json",
        help="path for the m-step Foster-drift JSON artifact",
    )
    parser.add_argument(
        "--m-step-foster-drift-k8-output",
        type=str,
        default="docs/reports/m_step_foster_drift_k8.json",
        help="path for the k<=8 m-step Foster-drift JSON artifact",
    )
    parser.add_argument(
        "--pointwise-descent-audit-output",
        type=str,
        default="docs/reports/pointwise_descent_audit.json",
        help="path for the pointwise descent audit JSON artifact",
    )
    parser.add_argument(
        "--pointwise-descent-samples",
        type=int,
        default=1_000_000,
        help="odd samples per n0 window for --pointwise-descent-audit",
    )
    parser.add_argument(
        "--pointwise-descent-m-max-values",
        type=str,
        default="100,1000,10000,100000",
        help="comma-separated staged m_max values for --pointwise-descent-audit",
    )
    parser.add_argument(
        "--chang-bit4-audit-output",
        type=str,
        default="docs/reports/chang_bit4_balance_audit.json",
        help="path for the Chang bit-4 balance audit JSON artifact",
    )
    parser.add_argument(
        "--chang-bit4-samples",
        type=int,
        default=1_000_000,
        help="odd samples per n0 window for --chang-bit4-audit",
    )
    parser.add_argument(
        "--chang-bit4-bootstrap-resamples",
        type=int,
        default=200,
        help="bootstrap resamples for --chang-bit4-audit delta summaries",
    )
    parser.add_argument(
        "--chang-bit4-max-steps-per-orbit",
        type=int,
        default=10_000,
        help="accelerated steps per orbit for --chang-bit4-audit",
    )
    parser.add_argument(
        "--m-step-foster-drift-grid",
        type=str,
        default="1,2,4,8,16,32,64",
        help="comma-separated m values for --m-step-foster-drift",
    )
    parser.add_argument("--m-step-foster-epsilon", type=float, default=0.1)
    parser.add_argument("--orbit-range-samples", type=int, default=200_000)
    parser.add_argument("--orbit-seed", type=int, default=0)
    parser.add_argument("--orbit-start-min", type=int, default=10**6)
    parser.add_argument("--orbit-start-max", type=int, default=10**9)
    parser.add_argument("--orbit-renewal-histogram-bin-width", type=float, default=0.005)
    parser.add_argument("--renewal-bootstrap-repetitions", type=int, default=500)
    parser.add_argument("--chang-R-K-K-max", type=int, default=200)
    parser.add_argument("--chang-R-K-comparison-K-max", type=int, default=500)
    parser.add_argument("--chang-R-K-target-excursions", type=int, default=5_000_000)
    parser.add_argument("--chang-R-K-bootstrap-resamples", type=int, default=500)
    parser.add_argument(
        "--chang-R-K-identity-output",
        type=str,
        default="docs/reports/jazz_constant_chang_R_K_identity.json",
        help="path for the Chang R(K) identity JSON artifact",
    )
    parser.add_argument(
        "--jazz-constant-high-precision-output",
        type=str,
        default="docs/reports/jazz_constant_high_precision.json",
        help="path for the high-precision J_renewal JSON artifact",
    )
    parser.add_argument("--renewal-drift-bootstrap-resamples", type=int, default=1000)
    parser.add_argument(
        "--renewal-drift-output",
        type=str,
        default="docs/reports/renewal_drift_per_step.json",
        help="path for the renewal per-step drift JSON artifact",
    )
    parser.add_argument(
        "--renewal-drift-phase-output",
        type=str,
        default="docs/reports/renewal_drift_phase_decomposed.json",
        help="path for the phase-decomposed renewal drift JSON artifact",
    )
    parser.add_argument(
        "--renewal-drift-phase-n0-output",
        type=str,
        default="docs/reports/renewal_drift_phase_decomposed_n0_stability.json",
        help="path for the phase-decomposed n0-stability JSON artifact",
    )
    parser.add_argument("--orbit-renewal-tda-points", type=int, default=5000)
    parser.add_argument("--orbit-renewal-tda-null-replicates", type=int, default=8)
    parser.add_argument(
        "--cover-tail-frontier",
        type=str,
        default=None,
        help="rank high-initial-ones frontier nodes in a saved cover report",
    )
    parser.add_argument("--tail-min-ones", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    powers = [12, 14]
    if not args.quick and args.max_hardness_power >= 16:
        powers.append(16)
    if not args.quick and args.max_hardness_power >= 20:
        powers.append(20)

    if args.frontier_dashboard:
        print("\nProof-search frontier dashboard:")
        print(
            format_frontier_dashboard_report(
                frontier_dashboard_report(args.frontier_dashboard_dir)
            )
        )

    print("Hardest first-descent cases under powers of 2:")
    for K in powers:
        print(f"K={K:>2}: {format_first_descent(hardest_first_descent_under_power(K))}")

    print("\nKnown residue certificate for n == 27 mod 2^59:")
    certificate = certificate_from_residue(27, 59)
    if certificate is None:
        print("No certificate found")
    else:
        print(format_certificate(certificate))
        print(f"verified={verify_descent_certificate(certificate)}")

    depth = min(args.cover_depth, 16) if args.quick else args.cover_depth
    nodes = min(args.cover_nodes, 20_000) if args.quick else args.cover_nodes
    cover = adaptive_cover(max_depth=depth, max_nodes=nodes)
    print(f"\nAdaptive cover summary to depth {depth}:")
    print(format_cover_summary(cover))

    if args.mersenne or args.quick:
        print("\nMersenne obstruction profiles:")
        for R in ([32, 40] if args.quick else [32, 40, 56, 64, 72, 80, 88, 90]):
            profile = profile_mersenne(R)
            print(
                f"R={R}: post_steps={profile.post_run_steps}, "
                f"post_A={profile.post_run_valuation}, "
                f"initial_debt={profile.initial_debt:.2f}, "
                f"landing_debt={profile.landing_debt:.2f}, "
                f"spikes={len(profile.spikes)}"
            )

    if args.mixed or args.quick:
        print("\nMixed 2/3-residue automaton:")
        report = explore_mixed_automaton(
            initial_mod2_power=4 if args.quick else 5,
            mod3_power=0 if args.quick else 1,
            max_states=5_000 if args.quick else 20_000,
            max_mod3_power=5 if args.quick else 8,
            cycle_mod3_power=3 if args.quick else 4,
        )
        print(format_mixed_summary(report))

    if args.cycles or args.quick:
        print("\nBounded exact cycle scan:")
        scan = scan_near_balanced_cycles(
            m_max=8 if args.quick else 10,
            valuation_max=5,
            slack=1,
        )
        print(format_cycle_scan_summary(scan))

    if args.academic or args.all_things or args.quick:
        print("\nContinued-fraction cycle screen:")
        screen = cycle_length_screen(max_m=90 if args.quick else 200)
        print(format_cycle_length_screen(screen))

        print("\nFinite density bound:")
        density = density_bound(
            max_depth=12 if args.quick else 16,
            max_nodes=10_000 if args.quick else 20_000,
        )
        print(format_density_bound(density))

        print("\nTruncated transfer operator:")
        spectrum = transfer_spectrum(
            modulus_power=5 if args.quick else 6,
            sample_lift_power=3 if args.quick else 4,
        )
        print(format_transfer_spectrum(spectrum))

    if args.all_things:
        print("\nCycle exclusion tower:")
        print(
            format_cycle_exclusion_tower_report(
                cycle_exclusion_tower_report(
                    max_m=10,
                    valuation_max=6,
                    lift_modulus_power=args.lift_realizability_power,
                    lift_max_period=args.lift_realizability_max_period,
                )
            )
        )

        print("\nCycle lattice LLL near-relations:")
        print(format_cycle_lattice_report(cycle_lattice_report()))

        print("\nWalsh-Hadamard transfer diagnostic:")
        print(
            format_walsh_transfer_report(
                walsh_transfer_report(
                    modulus_power=args.walsh_power,
                    sample_lift_power=args.walsh_lift_power,
                )
            )
        )

        print("\nCohn-Elkies/Walsh finite LP:")
        print(
            format_cohn_elkies_walsh_report(
                cohn_elkies_walsh_bound(modulus_power=args.ce_walsh_power)
            )
        )

        print("\nMixed tensor rank diagnostic:")
        print(
            format_mixed_tensor_rank_report(
                mixed_tensor_rank_report(
                    mod2_power=args.mixed_tensor_power,
                    mod3_power=args.mixed_tensor_mod3_power,
                )
            )
        )

        print("\nProfinite cohomology/sandpile tower:")
        print(
            format_cohomology_tower_report(
                cohomology_tower_report(
                    k_min=args.fusion_k_min,
                    k_max=args.fusion_k_max,
                    sample_lift_power=args.fusion_lift_power,
                )
            )
        )

        print("\nMixed spectral fingerprint:")
        print(
            format_spectral_fingerprint_report(
                spectral_fingerprint_report(
                    k_min=args.fusion_k_min,
                    k_max=args.fusion_k_max,
                    sample_lift_power=args.fusion_lift_power,
                )
            )
        )

    if args.cohomology or args.academic or args.all_things or args.quick:
        print("\nFinite graph cohomology:")
        cohomology = cohomology_report(
            modulus_power=5 if args.quick else 6,
            sample_lift_power=2 if args.quick else 4,
        )
        print(format_cohomology_report(cohomology))

    if args.all_things:
        print("\nHodge graph dimensions:")
        print(format_hodge_report(hodge_report()))

        print("\nOllivier-Ricci graph curvature:")
        print(format_ollivier_ricci_report(ollivier_ricci_report()))

        print("\nInteger/SNF-style invariants:")
        print(format_snf_invariant_report(snf_invariant_report()))

        print("\nSandpile critical-group artifact:")
        print(
            format_sandpile_report(
                sandpile_report(
                    modulus_power=args.sandpile_power,
                    sample_lift_power=args.sandpile_lift_power,
                )
            )
        )

    if args.max_plus or args.academic or args.all_things or args.quick:
        print("\nMax-plus debt cycle mean:")
        max_plus = max_plus_debt_report(
            modulus_power=5 if args.quick else args.max_plus_power,
            sample_lift_power=2 if args.quick else args.max_plus_lift_power,
        )
        print(format_max_plus_debt_report(max_plus))

    if args.all_things:
        print("\nConstrained legal-residue JSR diagnostic:")
        print(
            format_constrained_jsr_report(
                constrained_jsr_report(
                    modulus_power=args.jsr_power,
                    max_valuation=args.jsr_max_valuation,
                )
            )
        )

    if args.constrained_projective_jsr:
        print("\nConstrained projective JSR diagnostic:")
        print(
            format_constrained_projective_jsr_report(
                constrained_projective_jsr_report(
                    modulus_powers=_parse_int_tuple(args.constrained_projective_powers),
                    max_valuation=args.jsr_max_valuation,
                )
            )
        )

    if args.tail_aware_projective_jsr:
        print("\nTail-aware projective JSR diagnostic:")
        print(
            format_tail_aware_projective_jsr_report(
                tail_aware_projective_jsr_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                )
            )
        )

    if args.tail_aware_lte_closed_jsr:
        print("\nTail-aware LTE-closed projective JSR diagnostic:")
        print(
            format_tail_aware_projective_jsr_report(
                tail_aware_lte_closed_projective_jsr_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                )
            )
        )

    if args.tail_aware_markov_lyapunov:
        print("\nTail-aware Markov Lyapunov diagnostic:")
        print(
            format_tail_aware_markov_lyapunov_report(
                tail_aware_markov_lyapunov_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                )
            )
        )

    if args.christoffel_filtered_jsr:
        print("\nChristoffel-filtered tail JSR diagnostic:")
        print(
            format_christoffel_filtered_jsr_report(
                christoffel_filtered_jsr_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                    max_cycle_edges=args.christoffel_max_cycle_edges,
                    max_cycles_scanned=args.christoffel_max_cycles_scanned,
                )
            )
        )

    if args.christoffel_slope_constrained_jsr:
        print("\nChristoffel slope-constrained tail JSR diagnostic:")
        print(
            format_christoffel_slope_constrained_jsr_report(
                christoffel_slope_constrained_jsr_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                    max_cycle_edges=args.christoffel_max_cycle_edges,
                    max_cycles_scanned=args.christoffel_max_cycles_scanned,
                    tolerance=args.christoffel_slope_tolerance,
                )
            )
        )

    if args.constrained_karp_jsr:
        print("\nAutomaton-constrained Karp tail JSR diagnostic:")
        print(
            format_constrained_karp_jsr_report(
                constrained_karp_jsr_report(
                    levels=_parse_pair_tuple(args.tail_aware_levels),
                    max_valuation=args.jsr_max_valuation,
                    max_imbalance=args.constrained_karp_max_imbalance,
                    max_period=args.constrained_karp_max_period,
                )
            )
        )

    if args.karp_slope_joint_sweep:
        from pathlib import Path

        print("\nKarp/slope joint sweep diagnostic:")
        joint_sweep = karp_slope_joint_sweep_report(
            levels=_parse_pair_tuple(args.karp_slope_levels),
            max_valuation=args.jsr_max_valuation,
            max_imbalance=args.constrained_karp_max_imbalance,
            automaton_max_periods=_parse_int_tuple(args.karp_slope_periods),
            slope_tolerances=_parse_float_tuple(args.karp_slope_tolerances),
            max_cycle_edges=args.christoffel_max_cycle_edges,
            max_cycles_scanned=args.christoffel_max_cycles_scanned,
        )
        print(format_karp_slope_joint_sweep_report(joint_sweep))
        output_path = Path(args.karp_slope_joint_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(joint_sweep.to_json() + "\n")
        print(f"saved={output_path}")

    if args.tail_cycle_realizability:
        from pathlib import Path

        print("\nTail-cycle realizability audit:")
        realizability = tail_cycle_realizability_sweep_report(
            levels=_parse_pair_tuple(args.tail_cycle_realizability_levels),
            max_valuation=args.jsr_max_valuation,
            max_cycle_edges=args.christoffel_max_cycle_edges,
            max_cycles_scanned=args.tail_cycle_max_cycles_scanned,
            factor_threshold=args.tail_cycle_factor_threshold,
            slope_tolerance=args.christoffel_slope_tolerance,
            lift_max_scan_power=args.tail_cycle_lift_max_scan_power,
            audit_all_cycles=args.tail_cycle_audit_all_cycles,
        )
        print(format_tail_cycle_realizability_report(realizability))
        output_path = Path(args.tail_cycle_realizability_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(realizability.to_json() + "\n")
        print(f"saved={output_path}")

    if args.qnp1_realizability is not None:
        from pathlib import Path

        q_param = _parse_qnp1_param(args.qnp1_realizability)
        print(f"\nqn+1 realizability audit (q={q_param}):")
        realizability = qnp1_realizability_report(
            q_param=q_param,
            levels=_parse_pair_tuple(args.qnp1_realizability_levels),
            max_valuation=args.jsr_max_valuation,
            max_cycle_edges=args.christoffel_max_cycle_edges,
            max_cycles_scanned=args.tail_cycle_max_cycles_scanned,
        )
        print(format_qnp1_realizability_report(realizability))
        output_path = Path(args.qnp1_realizability_output)
        if output_path == Path("docs/reports/qnp1_realizability_q5.json") and q_param != 5:
            output_path = Path(f"docs/reports/qnp1_realizability_q{q_param}.json")
        realizability.save(output_path)
        print(f"saved={output_path}")

    if args.qnp1_phase_transition:
        from pathlib import Path

        print("\nqn+1 phase-transition audit:")
        phase = qnp1_phase_transition_report(
            q_grid=_parse_int_tuple(args.qnp1_phase_q_grid),
            m_max=args.qnp1_phase_m_max,
            levels=_parse_pair_tuple(args.qnp1_phase_levels),
            max_valuation=args.jsr_max_valuation,
            max_cycle_edges=args.christoffel_max_cycle_edges,
            max_cycles_scanned=args.tail_cycle_max_cycles_scanned,
        )
        print(format_qnp1_phase_transition_report(phase))
        output_path = Path(args.qnp1_phase_transition_output)
        phase.save(output_path)
        print(f"saved={output_path}")

    if args.rozier_abc_audit:
        from pathlib import Path

        print("\nRozier abc/Collatz mu-hit audit:")
        audit = rozier_abc_audit_report(
            j_min=args.rozier_j_min,
            j_max=args.rozier_j_max,
            orbit_sample_count=args.rozier_orbit_samples,
            orbit_time_budget_seconds=args.rozier_orbit_time_budget,
        )
        print(format_rozier_abc_audit_report(audit))
        output_path = Path(args.rozier_abc_output)
        audit.save(output_path)
        print(f"saved={output_path}")

    if args.cf_convergent_slope_hypothesis:
        from pathlib import Path

        print("\nCF-convergent slope hypothesis audit:")
        audit = cf_convergent_slope_hypothesis_report()
        print(format_cf_convergent_slope_hypothesis_report(audit))
        output_path = Path(args.cf_convergent_slope_output)
        audit.save(output_path)
        print(f"saved={output_path}")

    if args.stern_brocot_megasynthesis:
        from pathlib import Path

        print("\nStern-Brocot megasynthesis audit:")
        audit = stern_brocot_megasynthesis_report(
            cf_depth=args.stern_brocot_cf_depth,
            tao_max_m=args.stern_brocot_tao_max_m,
            tao_random_count=args.stern_brocot_tao_random_count,
            tao_bootstrap_samples=args.stern_brocot_tao_bootstrap_samples,
            rozier_n_max=args.stern_brocot_rozier_n_max,
            chang_max_K=args.stern_brocot_chang_max_K,
        )
        print(format_stern_brocot_megasynthesis_report(audit))
        output_path = Path(args.stern_brocot_megasynthesis_output)
        audit.save(output_path)
        summary_path = Path(args.stern_brocot_megasynthesis_summary_output)
        save_megasynthesis_executive_summary(audit, summary_path)
        print(f"saved={output_path}")
        print(f"saved_summary={summary_path}")

    if args.all_things:
        print("\nQuotient-cycle lift realizability:")
        print(
            format_lift_realizability_report(
                lift_realizability_report(
                    modulus_power=args.lift_realizability_power,
                    max_valuation=args.lift_realizability_max_valuation,
                    max_period=args.lift_realizability_max_period,
                )
            )
        )

        print("\nToy thermodynamic pressure:")
        print(format_pressure_report(pressure_report()))

        print("\nAuxiliary-prime Newton polygon scan:")
        print(format_newton_polygon_report(newton_polygon_report()))

        print("\nSpike-location correlation:")
        print(format_spike_correlation_report(spike_correlation_report()))

        print("\nCover trie magnitude:")
        print(format_magnitude_report(magnitude_report(run_certificate_cover(max_depth=8, max_nodes=300))))

    if args.lyapunov_artifact or args.academic or args.all_things or args.quick:
        print("\nPolynomial Lyapunov/SOS artifact:")
        lyapunov = lyapunov_template_artifact(
            modulus_power=4 if args.quick else 5,
            mod3_power=1 if args.quick else 2,
            degree=2,
        )
        print(format_lyapunov_artifact(lyapunov))

    if args.reverse_frontier or args.academic or args.all_things or args.quick:
        print("\nReverse frontier probe:")
        reverse = reverse_frontier_probe(
            cover.unresolved,
            reverse_depth=3 if args.quick else 4,
            max_nodes=5_000 if args.quick else 20_000,
        )
        print(format_reverse_frontier_report(reverse))

    if args.formal_artifacts or args.academic or args.all_things or args.quick:
        print("\nFormal proof artifacts:")
        if certificate is None:
            print("status=no_certificate_exported, exported=0, verified=False")
        else:
            print(format_formal_artifact_report(formal_artifact_report(certificate)))

    if args.certificate_cover or args.quick:
        print("\nCertificate cover database:")
        initial = (
            load_cover_report(args.resume_cover_report)
            if args.resume_cover_report is not None
            else None
        )
        cover_report = run_certificate_cover(
            max_depth=min(args.certificate_cover_depth, 12)
            if args.quick
            else args.certificate_cover_depth,
            max_nodes=min(args.certificate_cover_nodes, 10_000)
            if args.quick
            else args.certificate_cover_nodes,
            initial_report=initial,
        )
        print(format_certificate_cover_report(cover_report))
        if args.cover_report_path is not None:
            cover_report.save(args.cover_report_path)
            print(f"saved={args.cover_report_path}")

    if args.analyze_cover_report is not None:
        analyzed = load_cover_report(args.analyze_cover_report)
        print("\nCover mass transport:")
        print(format_cover_mass_report(cover_mass_report(analyzed)))
        print("\nCover frontier analysis:")
        print(
            format_frontier_analysis_report(
                analyze_cover_frontier(analyzed, top_n=args.frontier_top)
            )
        )

    if args.cover_parity_overlay is not None:
        analyzed = load_cover_report(args.cover_parity_overlay)
        print("\nCover parity overlay:")
        parity_overlay = analyze_cover_parity(analyzed, top_n=args.frontier_top)
        print(format_cover_parity_report(parity_overlay))
        if args.cover_parity_output is not None:
            from pathlib import Path

            Path(args.cover_parity_output).write_text(
                parity_overlay.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={args.cover_parity_output}")

    if args.cover_survival_spectrum is not None:
        analyzed = load_cover_report(args.cover_survival_spectrum)
        print("\nCover survival spectrum:")
        survival = cover_survival_spectrum(
            analyzed,
            sample_lift_power=args.survival_sample_lift_power,
            max_states=args.survival_max_states,
            top_n=args.frontier_top,
        )
        print(format_cover_survival_spectrum(survival))
        if args.cover_survival_output is not None:
            from pathlib import Path

            Path(args.cover_survival_output).write_text(
                survival.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={args.cover_survival_output}")

    if args.tail_family:
        print("\nMersenne-tail parameter family:")
        print(
            format_tail_family_report(
                analyze_tail_family(
                    R=args.tail_R,
                    u_mod_power=args.tail_u_mod_power,
                    odd_u_only=args.tail_odd_u_only,
                    representative_max_steps=args.tail_representative_max_steps,
                )
            )
        )

    if args.tail_renormalization:
        print("\nMersenne-tail renormalization:")
        renorm = tail_renormalization_report(
            R=args.tail_R,
            u=args.tail_u,
            max_blocks=args.tail_renorm_blocks,
        )
        print(format_tail_renormalization_report(renorm))
        if args.tail_renormalization_output is not None:
            from pathlib import Path

            Path(args.tail_renormalization_output).write_text(
                renorm.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={args.tail_renormalization_output}")

    if args.tail_renormalization_family:
        print("\nMersenne-tail renormalization family:")
        renorm_family = tail_renormalization_family_report(
            R=args.tail_R,
            u_mod_power=args.tail_u_mod_power,
            max_blocks=args.tail_renorm_blocks,
            top_n=args.frontier_top,
            odd_u_only=args.tail_odd_u_only,
        )
        print(format_tail_renormalization_family_report(renorm_family))
        if args.tail_renormalization_output is not None:
            from pathlib import Path

            Path(args.tail_renormalization_output).write_text(
                renorm_family.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={args.tail_renormalization_output}")

    if args.tail_exit_lemma:
        print("\nMersenne-tail exit cylinder lemma:")
        lemma = prove_tail_exit_cylinders(
            R=args.tail_R,
            initial_u_mod_power=args.tail_u_mod_power,
            max_u_mod_power=args.tail_lemma_max_u_power,
            max_blocks=args.tail_renorm_blocks,
            max_nodes=args.tail_lemma_max_nodes,
        )
        print(format_tail_exit_lemma_report(lemma))
        if args.tail_renormalization_output is not None:
            from pathlib import Path

            Path(args.tail_renormalization_output).write_text(
                lemma.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={args.tail_renormalization_output}")

    if args.tail_subautomaton_spectrum:
        print("\nTail-prefixed subautomaton spectrum:")
        print(
            format_tail_subautomaton_spectrum_report(
                tail_subautomaton_spectrum(
                    modulus_power=args.tail_spectrum_power,
                    prefix_ones=args.tail_spectrum_prefix_ones,
                    sample_lift_power=args.tail_spectrum_lift_power,
                )
            )
        )

    if args.tail_internal_step:
        print("\nTail-internal deterministic step:")
        print(format_tail_internal_step_report(tail_internal_step_report()))

    if args.tail_spectral_ladder:
        print("\nTail-prefixed spectral ladder:")
        print(
            format_tail_spectral_ladder_report(
                tail_spectral_ladder(
                    k_values=_parse_int_tuple(args.tail_spectral_k_values),
                    prefix_ones=args.tail_spectrum_prefix_ones,
                    sample_lift_power=args.tail_spectrum_lift_power,
                )
            )
        )

    if args.tail_pointwise_ratio:
        print("\nTail pointwise ratio scan:")
        print(
            format_tail_pointwise_ratio_report(
                tail_pointwise_ratio_scan(
                    modulus_power=args.tail_spectrum_power,
                    prefix_ones=args.tail_spectrum_prefix_ones,
                    sample_lift_power=args.tail_spectrum_lift_power,
                )
            )
        )

    if args.tail_lte:
        print("\nPure Mersenne-tail LTE blocks:")
        print(format_tail_lte_report(tail_lte_report(R_max=args.tail_lte_R_max)))

    if args.tail_lyapunov_lp:
        print("\nTail Lyapunov two-variable LP:")
        print(
            format_tail_lyapunov_lp_report(
                tune_tail_lyapunov_lp(
                    R0=args.tail_lyapunov_R0,
                    k_values=_parse_int_tuple(args.tail_spectral_k_values),
                    prefix_ones=args.tail_spectrum_prefix_ones,
                    sample_lift_power=args.tail_spectrum_lift_power,
                )
            )
        )

    if args.post_exit_pointwise:
        print("\nPost-exit pointwise scan:")
        print(
            format_post_exit_pointwise_report(
                post_exit_pointwise_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
                )
            )
        )

    if args.post_exit_ladder:
        print("\nPost-exit pointwise ladder:")
        print(
            format_post_exit_pointwise_ladder_report(
                post_exit_pointwise_ladder_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
                )
            )
        )

    if args.renewal_correlation:
        print("\nRenewal long-range correlation audit (Polli check):")
        correlation = renewal_correlation_report(
            orbit_count=args.renewal_correlation_orbits,
            start_bits=args.renewal_correlation_bits,
            random_seed=args.renewal_correlation_seed,
            max_lag=args.renewal_correlation_max_lag,
        )
        print(format_renewal_correlation_report(correlation))
        if args.renewal_correlation_output:
            from pathlib import Path

            output_path = Path(args.renewal_correlation_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(correlation.to_json() + "\n", encoding="utf-8")
            print(f"saved={output_path}")

    if args.perron_certificate:
        print("\nExact-rational PECM Perron certificates:")
        certificate_report = perron_certificate_report(
            configurations=_parse_pair_tuple(args.perron_certificate_configs),
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
            power_iterations=args.perron_certificate_iterations,
        )
        print(format_perron_certificate_report(certificate_report))
        if args.perron_certificate_output:
            from pathlib import Path

            output_path = Path(args.perron_certificate_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                certificate_report.to_json() + "\n", encoding="utf-8"
            )
            print(f"saved={output_path}")

    if args.pecm_vector_export:
        print("\nCommon-alpha PECM positive-vector export:")
        vector_exports = post_exit_common_alpha_vector_exports(
            _parse_pair_tuple(args.pecm_vector_export_configs),
            alpha=args.pecm_common_alpha,
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
            extension_iterations=args.post_exit_extension_iterations,
            max_materialized_states=args.pecm_max_materialized_states,
            max_materialized_transitions=(
                args.pecm_max_materialized_transitions
            ),
        )
        for export in vector_exports:
            print(
                f"(k={export.mod2_power}, ell={export.mod3_power}, "
                f"states={export.states}, alpha={export.alpha:.6f}, "
                f"lambda={export.lambda_super:.6f}, "
                f"converged={export.converged}, "
                f"unresolved={export.unresolved_or_out_of_window_samples}, "
                f"state_hash={export.state_order_hash[:12]})"
            )
        if args.pecm_vector_export_output:
            import json
            from pathlib import Path

            output_path = Path(args.pecm_vector_export_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(
                    {
                        "type": "post_exit_common_alpha_vector_export",
                        "alpha": args.pecm_common_alpha,
                        "configurations": [
                            list(configuration)
                            for configuration in _parse_pair_tuple(
                                args.pecm_vector_export_configs
                            )
                        ],
                        "levels": [
                            export.to_json_dict() for export in vector_exports
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.pecm_cross_resolution:
        print("\nCross-resolution PECM Lyapunov consistency:")
        consistency = pecm_cross_resolution_consistency_report(
            configurations=_parse_pair_tuple(
                args.pecm_cross_resolution_configs
            ),
            alpha=args.pecm_common_alpha,
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
            extension_iterations=args.post_exit_extension_iterations,
            max_materialized_states=args.pecm_max_materialized_states,
            max_materialized_transitions=(
                args.pecm_max_materialized_transitions
            ),
        )
        print(format_pecm_cross_resolution_consistency_report(consistency))
        if args.pecm_cross_resolution_output:
            from pathlib import Path

            output_path = Path(args.pecm_cross_resolution_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                consistency.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.post_exit_scaled_perron:
        print("\nPost-exit scaled Perron scan:")
        scaled_perron = post_exit_scaled_perron_report(
            configurations=_parse_pair_tuple(args.post_exit_configs),
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
            iterations=args.post_exit_perron_iterations,
            operator_mode=args.post_exit_operator_mode,
            chunk_rows=args.post_exit_chunk_rows,
            dense_entry_limit=args.post_exit_dense_entry_limit,
            checkpoint_path=args.post_exit_checkpoint,
            checkpoint_interval=args.post_exit_checkpoint_interval,
        )
        print(format_post_exit_scaled_perron_report(scaled_perron))
        if args.post_exit_scaled_perron_output:
            from pathlib import Path

            output_path = Path(args.post_exit_scaled_perron_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                scaled_perron.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.post_exit_super_eigen:
        print("\nPost-exit positive super-eigenvector:")
        print(
            format_post_exit_super_eigen_report(
                post_exit_super_eigen_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
                    power_iterations=args.post_exit_perron_iterations,
                    extension_iterations=args.post_exit_extension_iterations,
                    alpha_margin=args.post_exit_alpha_margin,
                    operator_mode=args.post_exit_operator_mode,
                    chunk_rows=args.post_exit_chunk_rows,
                    dense_entry_limit=args.post_exit_dense_entry_limit,
                )
            )
        )

    if args.harmonic_class_identification:
        print("\nHarmonic class identification:")
        print(
            format_harmonic_class_identification_report(
                harmonic_class_identification_report()
            )
        )

    if args.mixed_harmonic_class:
        print("\nMixed harmonic class identification:")
        print(format_mixed_harmonic_class_report(mixed_harmonic_class_report()))

    if args.obstruction_lyapunov_correction:
        print("\nObstruction Lyapunov correction:")
        print(
            format_obstruction_lyapunov_correction_report(
                obstruction_lyapunov_correction_report()
            )
        )

    if args.post_exit_lasota_yorke:
        print("\nPost-exit Lasota-Yorke empirical fit:")
        print(
            format_lasota_yorke_report(
                lasota_yorke_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    iterates=args.lasota_iterates,
                    sample_count=args.lasota_samples,
                    random_seed=args.lasota_seed,
                )
            )
        )

    if args.psi_symbolic_fit:
        print("\nPsi symbolic fit:")
        print(
            format_psi_symbolic_fit_report(
                psi_symbolic_fit_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    sample_lift_power=args.post_exit_sample_lift_power,
                )
            )
        )

    if args.unified_lyapunov_lp:
        print("\nUnified post-exit Lyapunov LP:")
        print(
            format_unified_lyapunov_lp_report(
                unified_lyapunov_lp_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    trajectory_samples=args.lyapunov_trajectory_samples,
                    height_mode=args.lyapunov_height_mode,
                    include_debt_term=args.lyapunov_debt_term,
                )
            )
        )

    if args.state_debt_lyapunov:
        from pathlib import Path

        print("\nBucketed state-debt Lyapunov LP:")
        state_debt = state_debt_lyapunov_report(
            mod2_power=args.post_exit_k,
            mod3_power=args.post_exit_ell,
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            bucket_width=args.debt_bucket_width,
        )
        print(format_state_debt_lyapunov_report(state_debt))
        if args.state_debt_lyapunov_output:
            output_path = Path(args.state_debt_lyapunov_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                state_debt.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.dpe_structural_bound:
        from pathlib import Path

        print("\nD_PE structural bound scan:")
        dpe_structural = dpe_structural_bound_report(
            configurations=_parse_pair_tuple(args.post_exit_configs),
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            histogram_bin_width=args.debt_bucket_width,
        )
        print(format_dpe_structural_bound_report(dpe_structural))
        if args.dpe_structural_bound_output:
            output_path = Path(args.dpe_structural_bound_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                dpe_structural.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.dpe_baker_certification:
        print("\nD_PE Baker certification scan:")
        print(
            format_baker_certification_report(
                dpe_baker_certification_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    baker_C=args.baker_C,
                    baker_kappa=args.baker_kappa,
                )
            )
        )

    if args.dpe_continued_fraction_certification:
        from pathlib import Path

        print("\nD_PE continued-fraction certification scan:")
        dpe_cf = dpe_continued_fraction_certification_report(
            configurations=_parse_pair_tuple(args.post_exit_configs),
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            max_denominator=args.convergent_max_denominator,
        )
        print(format_continued_fraction_certification_report(dpe_cf))
        if args.dpe_continued_fraction_output:
            output_path = Path(args.dpe_continued_fraction_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                dpe_cf.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.dpe_convergent_atlas:
        from pathlib import Path

        print("\nD_PE convergent atlas:")
        dpe_atlas = dpe_convergent_atlas_report(
            mod2_power=args.post_exit_k,
            mod3_power=args.post_exit_ell,
            R_values=_parse_int_tuple(args.post_exit_R_values),
            sample_lift_power=args.post_exit_sample_lift_power,
            max_steps=args.post_exit_max_steps,
            max_denominator=args.convergent_max_denominator,
        )
        print(format_convergent_atlas_report(dpe_atlas))
        if args.dpe_convergent_atlas_output:
            output_path = Path(args.dpe_convergent_atlas_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                dpe_atlas.to_json() + "\n",
                encoding="utf-8",
            )
            print(f"saved={output_path}")

    if args.orbit_lyapunov_beta_sweep:
        print("\nActual-orbit Lyapunov beta sweep:")
        print(
            format_orbit_lyapunov_beta_sweep_report(
                orbit_lyapunov_beta_sweep_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.phase_lyapunov_search:
        from pathlib import Path

        alpha_grid = (
            _parse_float_tuple(args.phase_lyapunov_alpha_grid)
            if args.phase_lyapunov_alpha_grid
            else DEFAULT_ALPHA_GRID
        )
        beta_grid = (
            _parse_float_tuple(args.phase_lyapunov_beta_grid)
            if args.phase_lyapunov_beta_grid
            else DEFAULT_BETA_GRID
        )
        gamma_diff_grid = (
            _parse_float_tuple(args.phase_lyapunov_gamma_diff_grid)
            if args.phase_lyapunov_gamma_diff_grid
            else DEFAULT_GAMMA_DIFF_GRID
        )
        print("\nPhase-aware actual-orbit Lyapunov search:")
        phase_lyapunov = phase_lyapunov_search_report(
            sample_count=args.phase_lyapunov_samples,
            start_min=args.orbit_start_min,
            start_max=args.orbit_start_max,
            random_seed=args.orbit_seed,
            max_steps_per_orbit=args.phase_lyapunov_max_steps_per_orbit,
            alpha_grid=alpha_grid,
            beta_grid=beta_grid,
            gamma_diff_grid=gamma_diff_grid,
        )
        print(format_phase_lyapunov_search_report(phase_lyapunov))
        output_path = Path(args.phase_lyapunov_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(phase_lyapunov.to_json() + "\n")
        print(f"saved={output_path}")

    if args.foster_drift:
        from pathlib import Path
        import json

        print("\nPhase-aware Foster-drift diagnostic:")
        foster = foster_drift_report(
            ranges=_parse_pair_tuple(args.foster_drift_ranges),
            sample_count_per_range=args.orbit_range_samples,
            residue_powers=_parse_int_tuple(args.foster_drift_residue_powers),
            tail_thresholds=_parse_float_tuple(args.foster_drift_tail_thresholds),
            hitting_time_max_steps=args.foster_drift_hitting_max_steps,
            hitting_time_threshold=args.foster_drift_hitting_threshold,
            bootstrap_resamples=args.renewal_drift_bootstrap_resamples,
            random_seed=args.orbit_seed,
        )
        print(format_foster_drift_report(foster))
        output_path = Path(args.foster_drift_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(foster, indent=2, sort_keys=True) + "\n")
        print(f"saved={output_path}")

    if args.m_step_foster_drift:
        from pathlib import Path
        import json

        print("\nPhase-aware m-step Foster-drift diagnostic:")
        m_step_foster = m_step_foster_drift_report(
            ranges=_parse_pair_tuple(args.foster_drift_ranges),
            sample_count_per_range=args.orbit_range_samples,
            residue_powers=_parse_int_tuple(args.foster_drift_residue_powers),
            m_steps_grid=_parse_int_tuple(args.m_step_foster_drift_grid),
            foster_epsilon=args.m_step_foster_epsilon,
            random_seed=args.orbit_seed,
        )
        print(format_m_step_foster_drift_report(m_step_foster))
        output_path = Path(args.m_step_foster_drift_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(m_step_foster, indent=2, sort_keys=True) + "\n"
        )
        print(f"saved={output_path}")

    if args.m_step_foster_drift_k8:
        from pathlib import Path
        import json

        print("\nPhase-aware m-step Foster-drift diagnostic through k=8:")
        m_step_foster_k8 = m_step_foster_drift_k8_report(
            ranges=_parse_pair_tuple(args.foster_drift_ranges),
            sample_count_per_range=args.orbit_range_samples,
            residue_powers=(2, 3, 4, 5, 6, 7, 8),
            m_steps_grid=_parse_int_tuple(args.m_step_foster_drift_grid),
            foster_epsilon=args.m_step_foster_epsilon,
            random_seed=args.orbit_seed,
        )
        print(format_m_step_foster_drift_k8_report(m_step_foster_k8))
        output_path = Path(args.m_step_foster_drift_k8_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(m_step_foster_k8, indent=2, sort_keys=True) + "\n"
        )
        print(f"saved={output_path}")

    if args.pointwise_descent_audit:
        from pathlib import Path
        import json

        print("\nPointwise descent hitting-time audit:")
        pointwise = pointwise_descent_audit_report(
            ranges=_parse_pair_tuple(args.foster_drift_ranges),
            sample_count_per_range=args.pointwise_descent_samples,
            m_max_values=_parse_int_tuple(args.pointwise_descent_m_max_values),
            random_seed=args.orbit_seed,
        )
        print(format_pointwise_descent_audit_report(pointwise))
        output_path = Path(args.pointwise_descent_audit_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(pointwise, indent=2, sort_keys=True) + "\n")
        print(f"saved={output_path}")

    if args.chang_bit4_audit:
        from pathlib import Path
        import json

        print("\nChang bit-4 balance audit:")
        chang_bit4 = chang_bit4_balance_audit_report(
            ranges=_parse_pair_tuple(args.foster_drift_ranges),
            sample_count_per_range=args.chang_bit4_samples,
            random_seed=args.orbit_seed,
            bootstrap_resamples=args.chang_bit4_bootstrap_resamples,
            max_steps_per_orbit=args.chang_bit4_max_steps_per_orbit,
        )
        print(format_chang_bit4_balance_audit_report(chang_bit4))
        output_path = Path(args.chang_bit4_audit_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(chang_bit4, indent=2, sort_keys=True) + "\n")
        print(f"saved={output_path}")

    if args.orbit_renewal_descent:
        print("\nActual-orbit renewal descent:")
        print(
            format_renewal_descent_report(
                orbit_renewal_descent_report(
                    sample_count=args.orbit_samples,
                    start_min=args.orbit_start_min,
                    start_max=args.orbit_start_max,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.renewal_drift_per_step:
        from pathlib import Path

        print("\nRenewal per-step drift identity audit:")
        drift_report = renewal_drift_per_step_report(
            sample_count=args.orbit_samples,
            start_min=args.orbit_start_min,
            start_max=args.orbit_start_max,
            random_seed=args.orbit_seed,
            bootstrap_resamples=args.renewal_drift_bootstrap_resamples,
        )
        print(format_renewal_drift_per_step_report(drift_report))
        output_path = Path(args.renewal_drift_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(drift_report.to_json() + "\n")
        print(f"saved={output_path}")

    if args.renewal_drift_phase_decomposed:
        from pathlib import Path

        print("\nPhase-decomposed renewal drift audit:")
        phase_report = renewal_drift_phase_decomposed_report(
            sample_count=args.orbit_samples,
            start_min=args.orbit_start_min,
            start_max=args.orbit_start_max,
            random_seed=args.orbit_seed,
            bootstrap_resamples=args.renewal_drift_bootstrap_resamples,
        )
        print(format_renewal_drift_phase_decomposed_report(phase_report))
        output_path = Path(args.renewal_drift_phase_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(phase_report.to_json() + "\n")
        print(f"saved={output_path}")

    if args.renewal_drift_phase_decomposed_n0:
        from pathlib import Path

        print("\nPhase-decomposed renewal drift n0 stability:")
        phase_n0 = renewal_drift_phase_decomposed_n0_stability_report(
            sample_count_per_range=args.orbit_range_samples,
            random_seed=args.orbit_seed,
            bootstrap_resamples=args.renewal_drift_bootstrap_resamples,
        )
        print(format_renewal_drift_phase_decomposed_n0_stability_report(phase_n0))
        output_path = Path(args.renewal_drift_phase_n0_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(phase_n0.to_json() + "\n")
        print(f"saved={output_path}")

    if args.orbit_renewal_spike_decomposition:
        print("\nActual-orbit renewal spike decomposition:")
        print(
            format_renewal_spike_decomposition_report(
                orbit_renewal_spike_decomposition_report(
                    sample_count=args.orbit_samples,
                    start_min=args.orbit_start_min,
                    start_max=args.orbit_start_max,
                    random_seed=args.orbit_seed,
                    histogram_bin_width=args.orbit_renewal_histogram_bin_width,
                )
            )
        )

    if args.renewal_bootstrap_calibration:
        print("\nActual-orbit renewal bootstrap calibration:")
        print(
            format_renewal_bootstrap_calibration_report(
                renewal_bootstrap_calibration_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                    bootstrap_repetitions=args.renewal_bootstrap_repetitions,
                    histogram_bin_width=args.orbit_renewal_histogram_bin_width,
                )
            )
        )

    if args.orbit_renewal_per_k_mgf:
        print("\nActual-orbit renewal per-k MGF:")
        print(
            format_orbit_renewal_per_k_mgf_report(
                orbit_renewal_per_k_mgf_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.orbit_renewal_markov_cramer:
        print("\nActual-orbit renewal Markov Cramer:")
        print(
            format_orbit_renewal_markov_cramer_report(
                orbit_renewal_markov_cramer_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.orbit_renewal_n0_stability:
        print("\nActual-orbit renewal n0 stability:")
        print(
            format_orbit_renewal_n0_stability_report(
                orbit_renewal_n0_stability_report(
                    sample_count_per_range=args.orbit_range_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.orbit_renewal_tda:
        print("\nActual-orbit renewal TDA:")
        print(
            format_orbit_renewal_tda_report(
                orbit_renewal_tda_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                    max_points=args.orbit_renewal_tda_points,
                    null_replicates=args.orbit_renewal_tda_null_replicates,
                )
            )
        )

    if args.valuation_mi_lags:
        print("\nValuation MI lag scan:")
        print(
            format_valuation_mi_lag_report(
                valuation_mi_lag_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.tao_syrac_empirical:
        print("\nTao Syrac empirical comparison:")
        print(
            format_tao_syrac_empirical_report(
                tao_syrac_empirical_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.tao_characteristic_decay:
        print("\nTao characteristic function decay:")
        print(
            format_tao_characteristic_decay_report(
                tao_characteristic_decay_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.unified_collatz_operator:
        print("\nUnified Collatz operator projection:")
        print(format_unified_collatz_operator_report(unified_collatz_operator_report()))

    if args.mori_mixed_first_return:
        print("\nMori mixed first-return projection:")
        print(
            format_mori_mixed_first_return_report(
                mori_mixed_first_return_report(
                    levels=_parse_pair_tuple(args.mori_mixed_configs)
                )
            )
        )

    if args.rigorous_squeeze:
        print("\nRigorous/finite/empirical squeeze bounds:")
        print(format_rigorous_squeeze_report(rigorous_squeeze_report()))

    if args.furstenberg_lyapunov:
        print("\nFurstenberg random-product Lyapunov baseline:")
        print(
            format_furstenberg_lyapunov_report(
                furstenberg_lyapunov_report(
                    monte_carlo_steps=args.furstenberg_steps,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.jazz_constant_test:
        print("\nJazz constant closed-form stress test:")
        print(format_jazz_constant_closed_form_report(jazz_constant_closed_form_report()))

    if args.jazz_constant_decomposition:
        print("\nJazz constant spike decomposition:")
        print(format_jazz_constant_decomposition_report(jazz_constant_decomposition_report()))

    if args.chang_R_K_identity:
        from pathlib import Path
        import json

        print("\nChang R(K) / Jazz constant identity diagnostic:")
        identity = chang_R_K_identity_report(
            K_max=args.chang_R_K_K_max,
            comparison_K_max=args.chang_R_K_comparison_K_max,
            target_renewal_excursions=args.chang_R_K_target_excursions,
            start_min=args.orbit_start_min,
            start_max=args.orbit_start_max,
            random_seed=args.orbit_seed,
            bootstrap_resamples=args.chang_R_K_bootstrap_resamples,
            histogram_bin_width=args.orbit_renewal_histogram_bin_width,
        )
        print(format_chang_R_K_identity_report(identity))
        identity_path = Path(args.chang_R_K_identity_output)
        identity_path.parent.mkdir(parents=True, exist_ok=True)
        identity_path.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n")
        high_precision_path = Path(args.jazz_constant_high_precision_output)
        high_precision_path.parent.mkdir(parents=True, exist_ok=True)
        high_precision_path.write_text(
            json.dumps(
                jazz_constant_high_precision_from_identity_report(identity),
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        print(f"saved={identity_path}")
        print(f"saved={high_precision_path}")

    if args.hercher_t_ni:
        print("\nHercher T(n_i) reciprocal-sum diagnostic:")
        print(format_hercher_t_ni_report(hercher_t_ni_report()))

    if args.paparella_nilpotency:
        print("\nPaparella nilpotency diagnostic:")
        print(format_paparella_nilpotency_report(paparella_nilpotency_report()))

    if args.cover_tail_frontier is not None:
        analyzed = load_cover_report(args.cover_tail_frontier)
        print("\nCover tail frontier:")
        print(
            format_cover_tail_report(
                analyze_cover_tail_frontier(
                    analyzed,
                    min_initial_ones=args.tail_min_ones,
                    top_n=args.frontier_top,
                    representative_max_steps=args.tail_representative_max_steps,
                )
            )
        )

    if args.mersenne_tail_analysis is not None:
        analyzed = load_cover_report(args.mersenne_tail_analysis)
        print("\nMersenne-tail frontier analysis:")
        print(
            format_mersenne_tail_report(
                analyze_mersenne_tails(
                    analyzed,
                    top_n=args.frontier_top,
                    max_extra_bits=args.tail_extra_bits,
                )
            )
        )

    if args.mersenne_continuation or args.quick:
        print("\nMersenne continuation graph:")
        graph = build_mersenne_continuation_graph(
            R_min=2,
            R_max=min(args.mersenne_R_max, 64) if args.quick else args.mersenne_R_max,
            modulus=args.mersenne_modulus,
        )
        print(format_mersenne_continuation_graph(graph))

    if args.mersenne_refinement:
        moduli = tuple(int(item) for item in args.mersenne_moduli.split(",") if item)
        print("\nMersenne continuation refinement:")
        refinement = refine_mersenne_continuation_moduli(
            R_min=2,
            R_max=args.mersenne_R_max,
            moduli=moduli,
        )
        print(format_mersenne_refinement_report(refinement))

    if args.mersenne_progression:
        print("\nMersenne progression word analysis:")
        progression = analyze_mersenne_progression(
            base_R=args.progression_base,
            modulus=args.progression_modulus,
            t_max=args.progression_t_max,
            prefix_length=args.progression_prefix,
            max_steps=args.progression_max_steps,
        )
        print(format_mersenne_progression_report(progression))

    if args.mersenne_branches:
        print("\nMersenne progression branch tree:")
        branches = analyze_mersenne_branches(
            base_R=args.progression_base,
            modulus=args.progression_modulus,
            t_max=args.progression_t_max,
            prefix_length=args.progression_prefix,
            max_depth=args.branch_depth,
            max_steps=args.progression_max_steps,
        )
        print(format_mersenne_branch_report(branches))

    if args.mersenne_prefix_family:
        print("\nMersenne target-prefix family:")
        family = analyze_mersenne_prefix_family(
            base_R=args.progression_base,
            modulus=args.progression_modulus,
            target_prefix=_parse_int_tuple(args.progression_target_prefix),
            t_max=args.progression_t_max,
            prefix_length=args.progression_prefix,
            max_steps=args.progression_max_steps,
        )
        print(format_mersenne_prefix_family_report(family))

    if args.tuple_merges:
        print("\nLocal tuple-merge checks:")
        print(format_tuple_merge_report(tuple_merge_report(samples=args.tuple_merge_samples)))

    if args.power_ratio:
        print("\nProportional-power-ratio diagnostics:")
        print(
            format_power_ratio_report(
                power_ratio_report(
                    start=args.power_ratio_start,
                    max_steps=args.power_ratio_max_steps,
                )
            )
        )

    if args.branch_table:
        print("\nBranch-table diagnostic:")
        table = branch_table_report(args.branch_table_start)
        terminal = table.terminal_power_exponent
        print(
            f"status={table.status}, start={table.start}, rows={len(table.rows)}, "
            f"reached_one={table.reached_one}, ordinary_steps={table.ordinary_steps}, "
            f"total_divisions={table.total_divisions}, terminal_power={terminal}"
        )

    if args.compact_trace:
        print("\nCompact trace invariant:")
        print(
            format_compact_trace_report(
                compact_trace_report(
                    args.compact_trace_start,
                    max_steps=args.compact_trace_max_steps,
                )
            )
        )

    if args.champions:
        print("\nInterval champions:")
        print(format_champion_report(champion_report(stop=args.champion_stop)))

    if args.odd_tree_siblings:
        print("\nOdd inverse-tree siblings:")
        print(
            format_odd_tree_sibling_report(
                odd_tree_sibling_report(
                    parent=args.odd_tree_parent,
                    count=args.odd_tree_count,
                )
            )
        )

    if args.sensitivity:
        print("\nCollatz sensitivity diagnostic:")
        print(
            format_sensitivity_report(
                sensitivity_report(
                    count=args.sensitivity_count,
                    bit=args.sensitivity_bit,
                    steps=args.sensitivity_steps,
                )
            )
        )

    if args.parity_layer:
        print("\nTerras parity-vector layer:")
        print(format_parity_layer_report(parity_layer_report(length=args.parity_length)))

    if args.divider_patterns:
        print("\nSingle/multiple divider transition census:")
        print(
            format_divider_pattern_report(
                divider_pattern_report(
                    modulus_power=args.divider_modulus_power,
                    lookahead=args.divider_lookahead,
                )
            )
        )


if __name__ == "__main__":
    main()
