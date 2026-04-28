"""Finite Hodge-dimension artifacts for transition support graphs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .cohomology import cohomology_report


@dataclass(frozen=True)
class HodgeReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    vertices: int
    undirected_edges: int
    components: int
    gradient_dimension: int
    harmonic_dimension: int
    coexact_dimension: int
    cycle_witnesses: tuple[tuple[int, ...], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cycle_witnesses"] = [list(cycle) for cycle in self.cycle_witnesses]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def hodge_report(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
) -> HodgeReport:
    """Return graph-Hodge dimensions for the truncated transition support."""

    base = cohomology_report(modulus_power, sample_lift_power)
    gradient_dimension = base.vertices - base.components
    harmonic_dimension = base.first_betti
    return HodgeReport(
        type="transition_graph_hodge_dimensions",
        status="finite_graph_hodge_obstruction_not_lyapunov_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        vertices=base.vertices,
        undirected_edges=base.undirected_edges,
        components=base.components,
        gradient_dimension=gradient_dimension,
        harmonic_dimension=harmonic_dimension,
        coexact_dimension=0,
        cycle_witnesses=base.cycle_witnesses,
    )
