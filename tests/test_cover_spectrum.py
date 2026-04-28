from collatz_exp.cover import run_certificate_cover
from collatz_exp.cover_spectrum import cover_survival_spectrum


def test_cover_survival_spectrum_smoke():
    cover = run_certificate_cover(max_depth=8, max_nodes=200)
    report = cover_survival_spectrum(
        cover,
        sample_lift_power=2,
        max_states=1_000,
        top_n=3,
    )
    assert report.type == "cover_frontier_substochastic_spectrum"
    assert report.matrix_dimension == len(cover.frontier)
    assert report.row_denominator == 4
    assert 0 <= report.weighted_survival_num <= report.weighted_survival_den
    assert 0 <= report.max_row_survival_num <= report.max_row_survival_den
    assert len(report.top_survival_rows) <= 3
    if report.perron_eigenvalue is not None:
        assert 0 <= report.perron_eigenvalue <= 1


def test_cover_survival_spectrum_refuses_large_frontier():
    cover = run_certificate_cover(max_depth=12, max_nodes=4_000)
    report = cover_survival_spectrum(cover, max_states=1)
    assert report.status == "frontier_too_large_matrix_not_built"
    assert report.matrix_dimension == 0
    assert report.perron_eigenvalue is None
