import math

from collatz_exp.furstenberg import furstenberg_lyapunov_report


def test_furstenberg_closed_form_smoke():
    report = furstenberg_lyapunov_report(monte_carlo_steps=1000, random_seed=0)
    assert report.type == "furstenberg_random_product_lyapunov"
    assert math.isclose(
        report.exact_log_growth_affine_coordinate_base2,
        math.log2(3.0 / 4.0),
    )
    assert report.exact_log_growth_homogeneous_coordinate_base2 == 0.0
    assert report.exact_typical_factor_affine_coordinate == 0.75
