"""Profinite-style cohomology/sandpile towers across residue depths."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .cohomology import cohomology_report
from .hodge import hodge_report
from .sandpile import sandpile_report


@dataclass(frozen=True)
class CohomologyTowerLevel:
    modulus_power: int
    sample_lift_power: int
    vertices: int
    first_betti: int
    harmonic_dimension: int
    sandpile_components: int
    sandpile_forest_count: int
    sandpile_invariant_factors: tuple[tuple[int, ...], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["sandpile_invariant_factors"] = [
            list(factors) for factors in self.sandpile_invariant_factors
        ]
        return data


@dataclass(frozen=True)
class CohomologyTowerReport:
    type: str
    status: str
    k_min: int
    k_max: int
    levels: tuple[CohomologyTowerLevel, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "k_min": self.k_min,
            "k_max": self.k_max,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def cohomology_tower_report(
    k_min: int = 4,
    k_max: int = 6,
    sample_lift_power: int = 3,
) -> CohomologyTowerReport:
    """Compute rank and torsion-style invariants over a depth ladder."""

    if k_min < 2 or k_max < k_min:
        raise ValueError("require 2 <= k_min <= k_max")
    levels: list[CohomologyTowerLevel] = []
    for k in range(k_min, k_max + 1):
        cohom = cohomology_report(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
        hodge = hodge_report(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
        sand = sandpile_report(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
        levels.append(
            CohomologyTowerLevel(
                modulus_power=k,
                sample_lift_power=sample_lift_power,
                vertices=cohom.vertices,
                first_betti=cohom.first_betti,
                harmonic_dimension=hodge.harmonic_dimension,
                sandpile_components=sand.components,
                sandpile_forest_count=sand.total_spanning_forest_count,
                sandpile_invariant_factors=tuple(
                    component.invariant_factors for component in sand.components_data
                ),
            )
        )
    return CohomologyTowerReport(
        type="profinite_cohomology_sandpile_tower",
        status="finite_depth_tower_not_profinite_limit_proof",
        k_min=k_min,
        k_max=k_max,
        levels=tuple(levels),
    )
