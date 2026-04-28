from collatz_exp.post_exit_lyapunov import (
    dpe_structural_bound_report,
    psi_symbolic_fit_report,
    state_debt_lyapunov_report,
    unified_lyapunov_lp_report,
)


def test_psi_symbolic_fit_smoke():
    report = psi_symbolic_fit_report(
        mod2_power=4,
        mod3_power=2,
        sample_lift_power=1,
    )
    assert report.type == "psi_symbolic_fit"
    assert report.entries == 8 * 9
    assert report.raw_integer_fraction_1e8 >= 0.0
    assert report.fits


def test_unified_lyapunov_lp_smoke():
    report = unified_lyapunov_lp_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        trajectory_samples=4,
    )
    assert report.type == "unified_lyapunov_lp"
    assert report.height_mode == "raw_log2"
    assert report.transitions_checked > 0
    assert report.reentry_constraints >= 0
    assert report.lp_status >= -1


def test_unified_lyapunov_renormalized_smoke():
    report = unified_lyapunov_lp_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        trajectory_samples=4,
        height_mode="renormalized_3_over_2",
    )
    assert report.height_mode == "renormalized_3_over_2"
    assert report.drift_coefficient > 0.0
    assert report.transitions_checked > 0


def test_unified_lyapunov_plus_renormalized_smoke():
    report = unified_lyapunov_lp_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        trajectory_samples=4,
        height_mode="renormalized_plus_3_over_2",
    )
    assert report.height_mode == "renormalized_plus_3_over_2"
    assert report.drift_coefficient < 0.0
    assert report.transitions_checked > 0


def test_unified_lyapunov_debt_smoke():
    report = unified_lyapunov_lp_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        trajectory_samples=4,
        include_debt_term=True,
    )
    assert report.include_debt_term
    assert report.gamma_bound > 0.0
    assert report.transitions_checked > 0


def test_state_debt_lyapunov_smoke():
    report = state_debt_lyapunov_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        bucket_width=0.1,
    )
    assert report.type == "unified_lyapunov_state_debt"
    assert report.transitions_checked > 0
    assert report.augmented_state_upper_bound >= report.base_states


def test_dpe_structural_bound_smoke():
    report = dpe_structural_bound_report(
        configurations=((4, 2),),
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
    )
    assert report.type == "d_pe_structural_bound"
    assert len(report.levels) == 1
    assert report.levels[0].transitions_checked > 0
