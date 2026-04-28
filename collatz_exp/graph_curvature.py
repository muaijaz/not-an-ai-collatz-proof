"""Ollivier-Ricci curvature artifacts for finite Collatz transition graphs."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class CurvatureEdge:
    source: int
    target: int
    wasserstein_1: float | None
    curvature: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OllivierRicciReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    vertices: int
    edges_checked: int
    min_curvature: float | None
    max_curvature: float | None
    most_negative_edges: tuple[CurvatureEdge, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["most_negative_edges"] = [
            edge.to_json_dict() for edge in self.most_negative_edges
        ]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def transition_probabilities(
    modulus_power: int,
    sample_lift_power: int,
) -> tuple[tuple[int, ...], dict[int, dict[int, Fraction]], dict[int, set[int]]]:
    artifact = transition_matrix_artifact(modulus_power, sample_lift_power)
    residues = artifact.residues
    probabilities: dict[int, dict[int, Fraction]] = {}
    adjacency: dict[int, set[int]] = {residue: set() for residue in residues}
    for i, row in enumerate(artifact.row_counts):
        source = residues[i]
        probabilities[source] = {}
        for j, count in enumerate(row):
            if count == 0:
                continue
            target = residues[j]
            probabilities[source][target] = Fraction(count, artifact.row_denominator)
            adjacency[source].add(target)
            adjacency[target].add(source)
    return residues, probabilities, adjacency


def graph_distances(
    residues: tuple[int, ...],
    adjacency: dict[int, set[int]],
) -> dict[tuple[int, int], int]:
    distances: dict[tuple[int, int], int] = {}
    for root in residues:
        seen = {root: 0}
        queue = deque([root])
        while queue:
            source = queue.popleft()
            for target in adjacency[source]:
                if target in seen:
                    continue
                seen[target] = seen[source] + 1
                queue.append(target)
        for target, distance in seen.items():
            distances[(root, target)] = distance
    return distances


def wasserstein_1_lp(
    mu: dict[int, Fraction],
    nu: dict[int, Fraction],
    distances: dict[tuple[int, int], int],
) -> float | None:
    """Compute W1 with scipy linprog when SciPy is installed."""

    if mu == nu:
        return 0.0
    try:
        import numpy as np
        from scipy.optimize import linprog
    except ImportError:
        return None

    sources = tuple(mu)
    targets = tuple(nu)
    costs = [distances[(source, target)] for source in sources for target in targets]
    A_eq = []
    b_eq = []
    for source_index, source in enumerate(sources):
        row = [0.0 for _ in costs]
        for target_index in range(len(targets)):
            row[source_index * len(targets) + target_index] = 1.0
        A_eq.append(row)
        b_eq.append(float(mu[source]))
    for target_index, target in enumerate(targets):
        row = [0.0 for _ in costs]
        for source_index in range(len(sources)):
            row[source_index * len(targets) + target_index] = 1.0
        A_eq.append(row)
        b_eq.append(float(nu[target]))
    result = linprog(
        c=np.array(costs, dtype=float),
        A_eq=np.array(A_eq, dtype=float),
        b_eq=np.array(b_eq, dtype=float),
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        return None
    return float(result.fun)


def ollivier_ricci_report(
    modulus_power: int = 4,
    sample_lift_power: int = 2,
    max_edges: int = 32,
) -> OllivierRicciReport:
    if max_edges < 1:
        raise ValueError("max_edges must be positive")
    residues, probabilities, adjacency = transition_probabilities(
        modulus_power,
        sample_lift_power,
    )
    distances = graph_distances(residues, adjacency)
    support_edges = sorted(
        {
            (source, target) if source <= target else (target, source)
            for source, neighbors in adjacency.items()
            for target in neighbors
            if source != target
        }
    )[:max_edges]
    edges: list[CurvatureEdge] = []
    solver_missing = False
    for source, target in support_edges:
        w1 = wasserstein_1_lp(probabilities[source], probabilities[target], distances)
        if w1 is None:
            solver_missing = True
            edges.append(CurvatureEdge(source, target, None, None))
            continue
        distance = distances[(source, target)]
        curvature = 1.0 - w1 / distance
        edges.append(CurvatureEdge(source, target, w1, curvature))
    curvatures = [edge.curvature for edge in edges if edge.curvature is not None]
    ranked = tuple(
        sorted(
            edges,
            key=lambda edge: float("inf") if edge.curvature is None else edge.curvature,
        )[: min(8, len(edges))]
    )
    return OllivierRicciReport(
        type="ollivier_ricci_transition_graph",
        status=(
            "scipy_unavailable_curvature_not_solved"
            if solver_missing and not curvatures
            else "finite_ollivier_ricci_quotient_not_collatz_proof"
        ),
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        vertices=len(residues),
        edges_checked=len(edges),
        min_curvature=None if not curvatures else min(curvatures),
        max_curvature=None if not curvatures else max(curvatures),
        most_negative_edges=ranked,
    )
