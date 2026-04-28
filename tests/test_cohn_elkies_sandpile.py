from math import prod

from collatz_exp.cohn_elkies import (
    cohn_elkies_walsh_bound,
    difference_closure,
    unresolved_indices,
    walsh_matrix,
    walsh_spectrum,
)
from collatz_exp.sandpile import (
    bareiss_det,
    connected_components,
    laplacian_matrix,
    reduced_laplacian,
    sandpile_report,
)


def test_walsh_helpers_and_difference_closure():
    assert walsh_spectrum((1, 0, 0, 0)) == (1, 1, 1, 1)
    assert walsh_matrix(2) == [[1, 1], [1, -1]]
    assert difference_closure((0, 2, 3)) == (0, 1, 2, 3)


def test_cohn_elkies_walsh_bound_smoke():
    unresolved = unresolved_indices(4)
    report = cohn_elkies_walsh_bound(modulus_power=4)
    assert report.type == "cohn_elkies_walsh_residue_lp"
    assert report.dimension == 8
    assert report.unresolved_points == len(unresolved)
    if report.density_bound is not None:
        assert report.density_bound >= 0


def test_bareiss_and_hand_graph_matrix_tree():
    assert bareiss_det(()) == 1
    assert bareiss_det(((3,),)) == 3
    assert bareiss_det(((2, -1), (-1, 2))) == 3
    triangle_vertices = (1, 3, 5)
    triangle_edges = ((1, 3), (1, 5), (3, 5))
    laplacian = laplacian_matrix(triangle_vertices, triangle_edges)
    assert bareiss_det(reduced_laplacian(laplacian)) == 3
    path_edges = ((1, 3), (3, 5))
    assert connected_components(triangle_vertices, path_edges) == ((1, 3, 5),)
    assert bareiss_det(reduced_laplacian(laplacian_matrix(triangle_vertices, path_edges))) == 1


def test_sandpile_report_smoke():
    report = sandpile_report(modulus_power=4, sample_lift_power=2)
    assert report.type == "residue_graph_sandpile_group"
    assert report.components >= 1
    assert report.total_spanning_forest_count == prod(
        component.spanning_tree_count for component in report.components_data
    )
    assert report.to_json_dict()["components_data"]
