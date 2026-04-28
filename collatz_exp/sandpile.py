"""Sandpile / critical-group artifacts for finite residue support graphs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class SandpileComponent:
    sink: int
    vertices: tuple[int, ...]
    undirected_edges: int
    spanning_tree_count: int
    invariant_factors: tuple[int, ...]
    smith_normal_form_available: bool

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["vertices"] = list(self.vertices)
        return data


@dataclass(frozen=True)
class SandpileReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    vertices: int
    undirected_edges: int
    components: int
    total_spanning_forest_count: int
    components_data: tuple[SandpileComponent, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "modulus_power": self.modulus_power,
            "sample_lift_power": self.sample_lift_power,
            "vertices": self.vertices,
            "undirected_edges": self.undirected_edges,
            "components": self.components,
            "total_spanning_forest_count": self.total_spanning_forest_count,
            "components_data": [
                component.to_json_dict() for component in self.components_data
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def support_edges(modulus_power: int, sample_lift_power: int) -> tuple[tuple[int, int], ...]:
    artifact = transition_matrix_artifact(modulus_power, sample_lift_power)
    edges = set()
    for i, source in enumerate(artifact.residues):
        for j, count in enumerate(artifact.row_counts[i]):
            if count == 0:
                continue
            target = artifact.residues[j]
            if source == target:
                continue
            edges.add((source, target) if source < target else (target, source))
    return tuple(sorted(edges))


def connected_components(
    vertices: tuple[int, ...],
    edges: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, ...], ...]:
    adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[int] = set()
    components: list[tuple[int, ...]] = []
    for root in vertices:
        if root in seen:
            continue
        stack = [root]
        seen.add(root)
        component: list[int] = []
        while stack:
            vertex = stack.pop()
            component.append(vertex)
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(tuple(sorted(component)))
    return tuple(components)


def laplacian_matrix(
    vertices: tuple[int, ...],
    edges: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, ...], ...]:
    index = {vertex: i for i, vertex in enumerate(vertices)}
    matrix = [[0 for _ in vertices] for _ in vertices]
    for left, right in edges:
        i = index[left]
        j = index[right]
        matrix[i][i] += 1
        matrix[j][j] += 1
        matrix[i][j] -= 1
        matrix[j][i] -= 1
    return tuple(tuple(row) for row in matrix)


def bareiss_det(matrix: tuple[tuple[int, ...], ...]) -> int:
    """Exact determinant by the fraction-free Bareiss algorithm."""

    n = len(matrix)
    if n == 0:
        return 1
    rows = [list(row) for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        if rows[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if rows[i][k] != 0), None)
            if swap is None:
                return 0
            rows[k], rows[swap] = rows[swap], rows[k]
            sign *= -1
        pivot = rows[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                rows[i][j] = (rows[i][j] * pivot - rows[i][k] * rows[k][j]) // previous
        previous = pivot
        for i in range(k + 1, n):
            rows[i][k] = 0
    return sign * rows[n - 1][n - 1]


def reduced_laplacian(laplacian: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row[1:]) for row in laplacian[1:])


def _sympy_invariant_factors(matrix: tuple[tuple[int, ...], ...]) -> tuple[int, ...] | None:
    try:
        from sympy import Matrix
        from sympy.matrices.normalforms import smith_normal_form
    except ImportError:
        return None
    snf = smith_normal_form(Matrix(matrix))
    factors = []
    for i in range(min(snf.rows, snf.cols)):
        value = abs(int(snf[i, i]))
        if value > 1:
            factors.append(value)
    return tuple(factors)


def sandpile_report(
    modulus_power: int = 5,
    sample_lift_power: int = 3,
) -> SandpileReport:
    artifact = transition_matrix_artifact(modulus_power, sample_lift_power)
    vertices = artifact.residues
    edges = support_edges(modulus_power, sample_lift_power)
    components = connected_components(vertices, edges)
    component_data: list[SandpileComponent] = []
    total_forest_count = 1
    any_snf = False
    for component in components:
        component_edges = tuple(
            edge for edge in edges if edge[0] in component and edge[1] in component
        )
        if len(component) == 1:
            tree_count = 1
            factors: tuple[int, ...] | None = ()
        else:
            laplacian = laplacian_matrix(component, component_edges)
            reduced = reduced_laplacian(laplacian)
            tree_count = abs(bareiss_det(reduced))
            factors = _sympy_invariant_factors(reduced)
        total_forest_count *= tree_count
        any_snf = any_snf or factors is not None
        component_data.append(
            SandpileComponent(
                sink=component[0],
                vertices=component,
                undirected_edges=len(component_edges),
                spanning_tree_count=tree_count,
                invariant_factors=() if factors is None else factors,
                smith_normal_form_available=factors is not None,
            )
        )
    return SandpileReport(
        type="residue_graph_sandpile_group",
        status=(
            "finite_residue_support_sandpile_not_collatz_proof"
            if any_snf
            else "finite_residue_support_sandpile_snf_unavailable_not_collatz_proof"
        ),
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        vertices=len(vertices),
        undirected_edges=len(edges),
        components=len(components),
        total_spanning_forest_count=total_forest_count,
        components_data=tuple(component_data),
    )
