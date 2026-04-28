from collatz_exp.tail_lemma import (
    TailCylinder,
    prove_tail_exit_cylinders,
    split_tail_cylinder,
    tail_cylinder_transition,
    tail_internal_step_report,
)
from collatz_exp.tail_lte import lte_v2_3_power_minus_1, tail_lte_report
from collatz_exp.tail_lyapunov import (
    lte_tail_depth_drop_bound,
    tune_tail_lyapunov_lp,
)
from collatz_exp.tail_spectral import (
    is_tail_prefixed_residue,
    tail_pointwise_ratio_scan,
    tail_spectral_ladder,
    tail_subautomaton_spectrum,
)


def test_tail_cylinder_transition_for_known_class():
    transition = tail_cylinder_transition(TailCylinder(R=8, u_residue=1, u_mod_power=7))
    assert transition.status == "forced"
    assert transition.c == lte_v2_3_power_minus_1(8)
    assert transition.target is not None
    assert transition.target.blocks == 1


def test_tail_cylinder_split_smoke():
    left, right = split_tail_cylinder(TailCylinder(R=5, u_residue=1, u_mod_power=3))
    assert left.u_mod_power == 4
    assert right.u_mod_power == 4
    assert right.u_residue == 9


def test_tail_exit_lemma_smoke():
    report = prove_tail_exit_cylinders(
        R=8,
        initial_u_mod_power=4,
        max_u_mod_power=10,
        max_blocks=5,
        max_nodes=2_000,
    )
    assert report.type == "tail_exit_cylinder_lemma"
    assert report.nodes_processed > 0
    assert report.exited_count + report.unresolved_count >= 0


def test_tail_spectral_and_lte_smoke():
    assert is_tail_prefixed_residue(15, 3)
    assert not is_tail_prefixed_residue(1, 1)
    spectrum = tail_subautomaton_spectrum(
        modulus_power=6,
        prefix_ones=3,
        sample_lift_power=2,
    )
    assert spectrum.type == "tail_prefixed_subautomaton_spectrum"
    assert spectrum.tail_states >= 1
    lte = tail_lte_report(R_min=2, R_max=16)
    assert lte.all_match
    assert lte_v2_3_power_minus_1(8) == 5


def test_tail_internal_step_identity_and_pointwise_ratio_scan():
    internal = tail_internal_step_report(R_min=2, R_max=10, u_mod_power=4)
    assert internal.all_match
    ratio = tail_pointwise_ratio_scan(
        modulus_power=6,
        prefix_ones=3,
        sample_lift_power=2,
    )
    assert ratio.type == "tail_pointwise_ratio_scan"
    assert ratio.full_survival_rows > 0
    assert ratio.constant_weight_rho_max == 1.0


def test_tail_spectral_ladder_and_lyapunov_lp_smoke():
    ladder = tail_spectral_ladder(
        k_values=(6, 7),
        prefix_ones=3,
        sample_lift_power=2,
    )
    assert ladder.type == "tail_subautomaton_spectral_ladder"
    assert ladder.max_perron_eigenvalue is not None
    assert ladder.max_perron_eigenvalue <= 0.5
    assert lte_tail_depth_drop_bound(20) == 14
    tuned = tune_tail_lyapunov_lp(
        R0=20,
        k_values=(6, 7),
        prefix_ones=3,
        sample_lift_power=2,
    )
    assert tuned.type == "tail_lyapunov_two_variable_lp"
    assert tuned.beta is not None
    assert tuned.gamma is not None
