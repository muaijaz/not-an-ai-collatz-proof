"""Finite harmonic projection diagnostics for named obstruction classes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .cohomology import cohomology_report
from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class HarmonicClassIdentificationReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    obstruction_R: int
    obstruction_u_mod2: int
    obstruction_u_mod2_power: int
    obstruction_u_mod3: int
    obstruction_u_mod3_power: int
    projected_residue: int
    mod3_visible: bool
    vertices: int
    undirected_edges: int
    first_betti: int
    harmonic_dimension: int
    indicator_edges: int
    indicator_norm: float
    harmonic_projection_norm: float
    harmonic_projection_ratio: float | None
    caveat: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def harmonic_class_identification_report(
    modulus_power: int = 6,
    sample_lift_power: int = 3,
    obstruction_R: int = 2,
    obstruction_u_mod2: int = 7,
    obstruction_u_mod2_power: int = 8,
    obstruction_u_mod3: int = 0,
    obstruction_u_mod3_power: int = 2,
) -> HarmonicClassIdentificationReport:
    """Project the visible binary shadow of the PECM obstruction onto H^1."""

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    if obstruction_R < 1:
        raise ValueError("obstruction_R must be positive")
    if obstruction_u_mod2 % 2 == 0:
        raise ValueError("obstruction_u_mod2 must be odd")

    artifact = transition_matrix_artifact(
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
    )
    residues = artifact.residues
    vertex_index = {residue: i for i, residue in enumerate(residues)}
    projected_residue = ((obstruction_u_mod2 << obstruction_R) - 1) % (
        1 << modulus_power
    )
    undirected_edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for i, row in enumerate(artifact.row_counts):
        source = residues[i]
        for j, count in enumerate(row):
            if count == 0:
                continue
            target = residues[j]
            edge = (source, target) if source <= target else (target, source)
            if edge not in seen:
                seen.add(edge)
                undirected_edges.append(edge)

    import numpy as np

    incidence = np.zeros((len(residues), len(undirected_edges)), dtype=float)
    indicator = np.zeros(len(undirected_edges), dtype=float)
    for col, (left, right) in enumerate(undirected_edges):
        if left != right:
            incidence[vertex_index[left], col] = -1.0
            incidence[vertex_index[right], col] = 1.0
        if left == projected_residue or right == projected_residue:
            indicator[col] = 1.0

    # Harmonic 1-forms on a graph are the cycle-space vectors, i.e. ker(B).
    _, singular_values, vh = np.linalg.svd(incidence, full_matrices=True)
    rank = int((singular_values > 1e-10).sum())
    null_basis = vh[rank:, :]
    if null_basis.size:
        projection = null_basis.T @ (null_basis @ indicator)
        projection_norm = float(np.linalg.norm(projection))
    else:
        projection_norm = 0.0
    indicator_norm = float(np.linalg.norm(indicator))
    cohom = cohomology_report(
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
    )
    ratio = None if indicator_norm == 0.0 else projection_norm / indicator_norm
    mod3_visible = False
    return HarmonicClassIdentificationReport(
        type="harmonic_class_identification",
        status="finite_binary_shadow_projection_not_mixed_harmonic_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        obstruction_R=obstruction_R,
        obstruction_u_mod2=obstruction_u_mod2,
        obstruction_u_mod2_power=obstruction_u_mod2_power,
        obstruction_u_mod3=obstruction_u_mod3,
        obstruction_u_mod3_power=obstruction_u_mod3_power,
        projected_residue=projected_residue,
        mod3_visible=mod3_visible,
        vertices=len(residues),
        undirected_edges=len(undirected_edges),
        first_betti=cohom.first_betti,
        harmonic_dimension=len(undirected_edges) - rank,
        indicator_edges=int(indicator.sum()),
        indicator_norm=indicator_norm,
        harmonic_projection_norm=projection_norm,
        harmonic_projection_ratio=ratio,
        caveat=(
            "The k=6 transition graph is binary only. The obstruction's "
            "u == 0 mod 9 condition is invisible here; this projects only "
            "the binary shadow n == 27 mod 64 onto the finite cycle space."
        ),
    )
