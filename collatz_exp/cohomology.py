"""Finite graph cohomology artifacts for truncated Collatz dynamics.

The report computes the first Betti number of the undirected support graph of a
finite transition quotient. A nonzero value means the quotient has graph cycles,
so any globally exact potential on this quotient has nontrivial consistency
conditions around those loops. This is an obstruction detector for simple
Lyapunov-on-quotient ansatzes, not a Collatz proof.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class CohomologyReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    vertices: int
    directed_edges: int
    undirected_edges: int
    components: int
    first_betti: int
    cycle_witnesses: tuple[tuple[int, ...], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cycle_witnesses"] = [list(cycle) for cycle in self.cycle_witnesses]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _path_in_tree(parent: dict[int, int | None], start: int, end: int) -> tuple[int, ...]:
    ancestors: dict[int, int] = {}
    node: int | None = start
    distance = 0
    while node is not None:
        ancestors[node] = distance
        node = parent[node]
        distance += 1

    end_path: list[int] = []
    node = end
    while node not in ancestors:
        end_path.append(node)
        parent_node = parent[node]
        if parent_node is None:
            return ()
        node = parent_node

    lca = node
    start_path: list[int] = []
    node = start
    while node != lca:
        start_path.append(node)
        parent_node = parent[node]
        if parent_node is None:
            return ()
        node = parent_node
    start_path.append(lca)
    return tuple(start_path + list(reversed(end_path)))


def first_betti_number(vertices: int, undirected_edges: int, components: int) -> int:
    if vertices < 0 or undirected_edges < 0 or components < 0:
        raise ValueError("graph counts must be nonnegative")
    return undirected_edges - vertices + components


def cohomology_report(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
    max_cycle_witnesses: int = 8,
) -> CohomologyReport:
    """Compute graph ``H^1`` rank for a truncated transition support graph."""

    artifact = transition_matrix_artifact(
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
    )
    residues = artifact.residues
    directed: set[tuple[int, int]] = set()
    undirected: set[tuple[int, int]] = set()
    adjacency: dict[int, set[int]] = {residue: set() for residue in residues}

    for i, row in enumerate(artifact.row_counts):
        source = residues[i]
        for j, count in enumerate(row):
            if count == 0:
                continue
            target = residues[j]
            directed.add((source, target))
            edge = (source, target) if source <= target else (target, source)
            undirected.add(edge)
            adjacency[source].add(target)
            adjacency[target].add(source)

    parent: dict[int, int | None] = {}
    tree_edges: set[tuple[int, int]] = set()
    components = 0
    cycle_witnesses: list[tuple[int, ...]] = []

    for root in residues:
        if root in parent:
            continue
        components += 1
        parent[root] = None
        queue = deque([root])
        while queue:
            source = queue.popleft()
            for target in sorted(adjacency[source]):
                edge = (source, target) if source <= target else (target, source)
                if target not in parent:
                    parent[target] = source
                    tree_edges.add(edge)
                    queue.append(target)
                elif parent[source] != target and edge not in tree_edges:
                    if len(cycle_witnesses) < max_cycle_witnesses:
                        path = _path_in_tree(parent, source, target)
                        if path:
                            cycle_witnesses.append(path)
                    tree_edges.add(edge)

    first_betti = first_betti_number(len(residues), len(undirected), components)
    return CohomologyReport(
        type="truncated_residue_graph_cohomology",
        status="finite_graph_obstruction_artifact_not_global_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        vertices=len(residues),
        directed_edges=len(directed),
        undirected_edges=len(undirected),
        components=components,
        first_betti=first_betti,
        cycle_witnesses=tuple(cycle_witnesses),
    )
