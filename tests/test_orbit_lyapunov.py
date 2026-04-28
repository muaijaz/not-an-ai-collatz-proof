from collatz_exp.orbit_lyapunov import orbit_lyapunov_beta_sweep_report


def test_orbit_lyapunov_beta_sweep_smoke():
    report = orbit_lyapunov_beta_sweep_report(
        sample_count=10,
        beta_values=(1.0, 2.0),
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "actual_orbit_lyapunov_beta_sweep"
    assert report.completed_orbits == 10
    assert report.total_accelerated_steps > 0
    assert len(report.results) == 4
