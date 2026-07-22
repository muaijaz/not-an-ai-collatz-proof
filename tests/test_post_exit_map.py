import pytest

from collatz_exp.post_exit_map import (
    PostExitState,
    post_exit_landing,
    post_exit_pointwise_ladder_report,
    post_exit_pointwise_report,
    post_exit_scaled_perron_level,
    post_exit_scaled_perron_report,
    post_exit_states,
    post_exit_super_eigen_level,
    post_exit_super_eigen_report,
    post_exit_transition_sample,
)
from collatz_exp.core import accelerated_step


def test_post_exit_states_are_crt_indexed():
    states = post_exit_states(mod2_power=3, mod3_power=1, R_values=(4, 6))
    assert len(states) == 2 * 4 * 3
    assert states[0].R == 4
    assert states[0].u_mod2 % 2 == 1


def test_post_exit_landing_matches_direct_forced_steps():
    R = 8
    u = 5
    x = (1 << R) * u - 1
    total_A = 0
    for _ in range(R - 1):
        x, a = accelerated_step(x)
        total_A += a
    assert total_A == R - 1
    assert x == post_exit_landing(R, u)


def test_post_exit_transition_sample_reaches_terminal_status():
    state = PostExitState(R=8, u_mod2=1, u_mod2_power=4, u_mod3=1, u_mod3_power=1)
    transition = post_exit_transition_sample(state, u=1, max_steps=50)
    assert transition.status in {
        "descended",
        "reentered_tail",
        "reentered_tail_out_of_range",
        "max_steps_exceeded",
    }
    assert transition.post_start == 2 * (3 ** (state.R - 1)) - 1


def test_post_exit_pointwise_report_smoke():
    report = post_exit_pointwise_report(
        mod2_power=4,
        mod3_power=1,
        R_values=(4, 6),
        sample_lift_power=1,
        max_steps=80,
    )
    assert report.type == "post_exit_pointwise_report"
    assert report.states == 2 * 8 * 3
    assert report.row_denominator == 2
    assert report.descended_samples + report.reentry_samples + report.out_of_range_reentry_samples == (
        report.states * report.row_denominator
    )
    assert 0.0 <= report.constant_weight_rho_max <= 1.0


def test_post_exit_pointwise_ladder_smoke():
    ladder = post_exit_pointwise_ladder_report(
        configurations=((4, 1), (5, 1)),
        R_values=(4,),
        sample_lift_power=0,
        max_steps=50,
    )
    assert ladder.type == "post_exit_pointwise_ladder_report"
    assert len(ladder.levels) == 2


def test_post_exit_scaled_perron_report_smoke():
    report = post_exit_scaled_perron_report(
        configurations=((4, 1),),
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=4,
    )
    assert report.type == "post_exit_scaled_perron_report"
    assert len(report.levels) == 1
    level = report.levels[0]
    assert level.states == 3 * 8 * 3
    assert level.row_denominator == 2
    assert level.finite_ratio_max is None or level.finite_ratio_max >= 0.0


def test_post_exit_scaled_perron_streaming_matches_dense():
    dense = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=4,
        operator_mode="dense_target_cache",
    )
    streaming = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=4,
        operator_mode="streaming",
        chunk_rows=7,
    )
    assert streaming.operator_mode == "streaming"
    assert streaming.states == dense.states
    assert streaming.descended_samples == dense.descended_samples
    assert streaming.reentry_samples == dense.reentry_samples
    assert streaming.out_of_range_reentry_samples == dense.out_of_range_reentry_samples
    assert streaming.constant_weight_rho_max_num == dense.constant_weight_rho_max_num
    assert streaming.constant_weight_rho_max_den == dense.constant_weight_rho_max_den
    assert streaming.finite_ratio_max == dense.finite_ratio_max


def test_post_exit_scaled_perron_checkpoint_resume(tmp_path):
    checkpoint = tmp_path / "scaled_perron.npz"
    first = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=1,
        checkpoint_path=checkpoint,
    )
    resumed = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=2,
        checkpoint_path=checkpoint,
    )
    full = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=2,
    )
    assert first.checkpoint_saved_iteration == 1
    assert resumed.checkpoint_loaded_iteration == 1
    assert resumed.checkpoint_saved_iteration == 2
    assert resumed.power_scale_estimate == full.power_scale_estimate
    assert resumed.finite_ratio_max == full.finite_ratio_max


def test_post_exit_scaled_perron_gpu_matches_dense_when_available():
    pytest.importorskip("cupy")
    dense = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=4,
        operator_mode="dense_target_cache",
    )
    gpu = post_exit_scaled_perron_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterations=4,
        operator_mode="gpu_target_cache",
    )
    assert gpu.operator_mode == "gpu_target_cache"
    assert gpu.descended_samples == dense.descended_samples
    assert gpu.reentry_samples == dense.reentry_samples
    assert gpu.out_of_range_reentry_samples == dense.out_of_range_reentry_samples
    assert gpu.finite_ratio_max == dense.finite_ratio_max


def test_post_exit_super_eigen_report_smoke():
    report = post_exit_super_eigen_report(
        configurations=((4, 1),),
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        power_iterations=4,
        extension_iterations=8,
        alpha_margin=0.2,
        scc_state_limit=1_000,
    )
    assert report.type == "post_exit_super_eigenvector_report"
    level = report.levels[0]
    assert level.states == 3 * 8 * 3
    assert level.positive_min > 0.0
    assert level.lambda_super <= level.alpha


def test_post_exit_super_eigen_streaming_matches_dense():
    dense = post_exit_super_eigen_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        power_iterations=4,
        extension_iterations=8,
        alpha_margin=0.2,
        scc_state_limit=1_000,
        operator_mode="dense_target_cache",
    )
    streaming = post_exit_super_eigen_level(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        power_iterations=4,
        extension_iterations=8,
        alpha_margin=0.2,
        scc_state_limit=1_000,
        operator_mode="streaming",
        chunk_rows=7,
    )
    assert streaming.operator_mode == "streaming"
    assert streaming.descended_samples == dense.descended_samples
    assert streaming.reentry_samples == dense.reentry_samples
    assert streaming.lambda_super == dense.lambda_super
    assert streaming.positive_min == dense.positive_min
