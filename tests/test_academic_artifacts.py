from fractions import Fraction

from collatz_exp.cycles_eliahou import cycle_length_screen, log2_3_convergents
from collatz_exp.density_lp import (
    density_bound,
    transition_matrix_artifact,
    unresolved_odd_density,
)
from collatz_exp.transfer_op import transfer_spectrum


def test_continued_fraction_cycle_screen_is_machine_readable():
    convergents = log2_3_convergents(max_denominator=50)
    assert any((w.numerator_A, w.denominator_m) == (65, 41) for w in convergents)

    screen = cycle_length_screen(max_m=50)
    data = screen.to_json_dict()
    assert data["type"] == "continued_fraction_cycle_screen"
    assert "not_eliahou_hercher_theorem" in data["status"]
    assert screen.best_witness.denominator_m <= 50


def test_unresolved_odd_density_is_exact():
    assert unresolved_odd_density(((1, 1),)) == Fraction(1, 1)
    assert unresolved_odd_density(((1, 3), (5, 3))) == Fraction(1, 2)


def test_density_bound_and_transition_matrix_artifact():
    bound = density_bound(max_depth=8, max_nodes=200)
    assert bound.unresolved_odd_density_num >= 0
    assert bound.unresolved_odd_density_den > 0

    artifact = transition_matrix_artifact(modulus_power=4, sample_lift_power=2)
    assert artifact.row_denominator == 4
    assert len(artifact.residues) == 8
    assert all(sum(row) == artifact.row_denominator for row in artifact.row_counts)


def test_transfer_spectrum_has_fallback_or_spectrum():
    report = transfer_spectrum(modulus_power=4, sample_lift_power=2)
    assert report.dimension == 8
    if report.second_eigenvalue_abs is not None:
        assert report.second_eigenvalue_abs >= 0
