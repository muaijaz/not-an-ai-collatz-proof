from collatz_exp.post_exit_lasota_yorke import lasota_yorke_report


def test_lasota_yorke_smoke():
    report = lasota_yorke_report(
        mod2_power=4,
        mod3_power=1,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        iterates=3,
        sample_count=2,
    )
    assert report.type == "post_exit_pecm_lasota_yorke_empirical"
    assert report.samples_completed == 2
    assert report.rho_max >= 0.0
    assert report.C_estimate >= 0.0
