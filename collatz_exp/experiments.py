"""Command-line experiments for the Collatz certificate search package."""

from __future__ import annotations

import argparse

from .branch_table import branch_table_report
from .certificates import certificate_from_residue, verify_descent_certificate
from .champions import champion_report
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
    constrained_jsr_report,
    constrained_projective_jsr_report,
    tail_aware_markov_lyapunov_report,
    tail_aware_lte_closed_projective_jsr_report,
    tail_aware_projective_jsr_report,
)
from .core import hardest_first_descent_under_power
from .cycles import scan_near_balanced_cycles
from .cycle_tower import cycle_exclusion_tower_report
from .cycles_eliahou import cycle_length_screen
from .density_lp import density_bound
from .divider_patterns import divider_pattern_report
from .formal_artifacts import formal_artifact_report
from .frontier_analysis import analyze_cover_frontier
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
)
from .orbit_renewal_tda import orbit_renewal_tda_report
from .renewal_bootstrap import renewal_bootstrap_calibration_report
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
from .reports import (
    format_cohomology_report,
    format_compact_trace_report,
    format_baker_certification_report,
    format_certificate_cover_report,
    format_champion_report,
    format_christoffel_filtered_jsr_report,
    format_cover_mass_report,
    format_cover_parity_report,
    format_cover_survival_spectrum,
    format_cohn_elkies_walsh_report,
    format_cohomology_tower_report,
    format_constrained_jsr_report,
    format_constrained_projective_jsr_report,
    format_tail_aware_projective_jsr_report,
    format_tail_aware_markov_lyapunov_report,
    format_convergent_atlas_report,
    format_continued_fraction_certification_report,
    format_cycle_scan_summary,
    format_cycle_length_screen,
    format_cycle_lattice_report,
    format_cycle_exclusion_tower_report,
    format_certificate,
    format_cover_summary,
    format_density_bound,
    format_divider_pattern_report,
    format_dpe_structural_bound_report,
    format_formal_artifact_report,
    format_frontier_analysis_report,
    format_furstenberg_lyapunov_report,
    format_first_descent,
    format_hodge_report,
    format_harmonic_class_identification_report,
    format_jazz_constant_closed_form_report,
    format_jazz_constant_decomposition_report,
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
    format_renewal_bootstrap_calibration_report,
    format_renewal_descent_report,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="run a short deterministic smoke experiment",
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
        "--tail-aware-levels",
        type=str,
        default="5:4,6:5,7:6,8:6,10:7",
        help="comma-separated q:Rmax levels for tail-aware projective JSR",
    )
    parser.add_argument("--christoffel-max-cycle-edges", type=int, default=10)
    parser.add_argument("--christoffel-max-cycles-scanned", type=int, default=50000)
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
        "--dpe-structural-bound",
        action="store_true",
        help="enumerate PECM edge D_PE values and fit a finite debt envelope",
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
        "--dpe-convergent-atlas",
        action="store_true",
        help="check which log2(3) convergents occur as PECM reentry edges",
    )
    parser.add_argument(
        "--orbit-lyapunov-beta-sweep",
        action="store_true",
        help="sweep beta for running-debt Lyapunov candidates on actual orbits",
    )
    parser.add_argument(
        "--orbit-renewal-descent",
        action="store_true",
        help="aggregate actual orbits into tail-entry renewal excursions",
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
    parser.add_argument("--orbit-range-samples", type=int, default=200_000)
    parser.add_argument("--orbit-seed", type=int, default=0)
    parser.add_argument("--orbit-renewal-histogram-bin-width", type=float, default=0.005)
    parser.add_argument("--renewal-bootstrap-repetitions", type=int, default=500)
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

    if args.post_exit_scaled_perron:
        print("\nPost-exit scaled Perron scan:")
        print(
            format_post_exit_scaled_perron_report(
                post_exit_scaled_perron_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    tail_reentry_min_R=args.post_exit_tail_reentry_min_R,
                    iterations=args.post_exit_perron_iterations,
                )
            )
        )

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
        print("\nBucketed state-debt Lyapunov LP:")
        print(
            format_state_debt_lyapunov_report(
                state_debt_lyapunov_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    bucket_width=args.debt_bucket_width,
                )
            )
        )

    if args.dpe_structural_bound:
        print("\nD_PE structural bound scan:")
        print(
            format_dpe_structural_bound_report(
                dpe_structural_bound_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    histogram_bin_width=args.debt_bucket_width,
                )
            )
        )

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
        print("\nD_PE continued-fraction certification scan:")
        print(
            format_continued_fraction_certification_report(
                dpe_continued_fraction_certification_report(
                    configurations=_parse_pair_tuple(args.post_exit_configs),
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    max_denominator=args.convergent_max_denominator,
                )
            )
        )

    if args.dpe_convergent_atlas:
        print("\nD_PE convergent atlas:")
        print(
            format_convergent_atlas_report(
                dpe_convergent_atlas_report(
                    mod2_power=args.post_exit_k,
                    mod3_power=args.post_exit_ell,
                    R_values=_parse_int_tuple(args.post_exit_R_values),
                    sample_lift_power=args.post_exit_sample_lift_power,
                    max_steps=args.post_exit_max_steps,
                    max_denominator=args.convergent_max_denominator,
                )
            )
        )

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

    if args.orbit_renewal_descent:
        print("\nActual-orbit renewal descent:")
        print(
            format_renewal_descent_report(
                orbit_renewal_descent_report(
                    sample_count=args.orbit_samples,
                    random_seed=args.orbit_seed,
                )
            )
        )

    if args.orbit_renewal_spike_decomposition:
        print("\nActual-orbit renewal spike decomposition:")
        print(
            format_renewal_spike_decomposition_report(
                orbit_renewal_spike_decomposition_report(
                    sample_count=args.orbit_samples,
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
