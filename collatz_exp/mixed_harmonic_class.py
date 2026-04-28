"""Mixed 2/3-adic harmonic projection for named obstruction classes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class MixedHarmonicClassReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    sample_lift_power: int
    vertices: int
    undirected_edges: int
    components: int
    first_betti: int
    harmonic_dimension: int
    projection_method: str
    obstruction_R: int
    obstruction_u_mod2: int
    obstruction_u_mod3_modulus: int
    obstruction_vertices: tuple[tuple[int, int], ...]
    indicator_edges: int
    indicator_norm: float
    harmonic_projection_norm: float
    harmonic_projection_ratio: float | None

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["obstruction_vertices"] = [list(item) for item in self.obstruction_vertices]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ObstructionTrajectoryCheck:
    samples: int
    reentered: int
    descended: int
    min_delta: float | None
    max_delta: float | None
    mean_delta: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObstructionLyapunovCorrectionReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    sample_lift_power: int
    vertices: int
    undirected_edges: int
    obstruction_vertices: tuple[tuple[int, int], ...]
    residual_norm: float
    residual_ratio: float | None
    potential_entries: tuple[tuple[int, int, float], ...]
    edge_correction_entries: tuple[tuple[int, int, float], ...]
    trajectory_check: ObstructionTrajectoryCheck

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "sample_lift_power": self.sample_lift_power,
            "vertices": self.vertices,
            "undirected_edges": self.undirected_edges,
            "obstruction_vertices": [list(item) for item in self.obstruction_vertices],
            "residual_norm": self.residual_norm,
            "residual_ratio": self.residual_ratio,
            "potential_entries": [list(item) for item in self.potential_entries],
            "edge_correction_entries": [
                list(item) for item in self.edge_correction_entries
            ],
            "trajectory_check": self.trajectory_check.to_json_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _crt_mod_2_3(residue2: int, power2: int, residue3: int, power3: int) -> int:
    modulus2 = 1 << power2
    modulus3 = 3**power3
    inverse = pow(modulus2, -1, modulus3)
    t = ((residue3 - residue2) * inverse) % modulus3
    return residue2 + modulus2 * t


def _mixed_hodge_components(
    mod2_power: int,
    mod3_power: int,
    sample_lift_power: int,
    obstruction_R: int,
    obstruction_u_mod2: int,
    obstruction_u_mod3_modulus: int,
):
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse.linalg import lsmr

    residues2 = tuple(range(1, 1 << mod2_power, 2))
    residues3 = tuple(range(3**mod3_power))
    vertices = tuple((r2, r3) for r2 in residues2 for r3 in residues3)
    index = {vertex: i for i, vertex in enumerate(vertices)}
    modulus = (1 << mod2_power) * (3**mod3_power)
    edges: set[tuple[int, int]] = set()
    for r2, r3 in vertices:
        source = index[(r2, r3)]
        base = _crt_mod_2_3(r2, mod2_power, r3, mod3_power)
        for lift in range(1 << sample_lift_power):
            n = base + lift * modulus
            if n == 1:
                n += modulus * (1 << sample_lift_power)
            landing, _ = accelerated_step(n)
            target = index[(landing % (1 << mod2_power), landing % (3**mod3_power))]
            edge = (source, target) if source <= target else (target, source)
            edges.add(edge)
    edge_list = sorted(edges)

    row_indices: list[int] = []
    col_indices: list[int] = []
    values: list[float] = []
    obstruction_u3_values = tuple(
        value
        for value in residues3
        if value % obstruction_u_mod3_modulus == 0
    )
    obstruction_vertices = tuple(
        (
            ((obstruction_u_mod2 << obstruction_R) - 1) % (1 << mod2_power),
            ((1 << obstruction_R) * u3 - 1) % (3**mod3_power),
        )
        for u3 in obstruction_u3_values
    )
    obstruction_indices = {index[vertex] for vertex in obstruction_vertices}
    indicator = np.zeros(len(edge_list), dtype=float)
    adjacency_rows: list[int] = []
    adjacency_cols: list[int] = []
    for col, (left, right) in enumerate(edge_list):
        if left != right:
            row_indices.extend([left, right])
            col_indices.extend([col, col])
            values.extend([-1.0, 1.0])
            adjacency_rows.extend([left, right])
            adjacency_cols.extend([right, left])
        if left in obstruction_indices or right in obstruction_indices:
            indicator[col] = 1.0
    incidence = csr_matrix(
        (values, (row_indices, col_indices)),
        shape=(len(vertices), len(edge_list)),
        dtype=float,
    )
    graph = csr_matrix(
        (
            np.ones(len(adjacency_rows), dtype=np.int8),
            (adjacency_rows, adjacency_cols),
        ),
        shape=(len(vertices), len(vertices)),
    )
    components, _ = connected_components(graph, directed=False, return_labels=True)
    gradient_solution = lsmr(
        incidence.transpose(),
        indicator,
        atol=1e-10,
        btol=1e-10,
        maxiter=max(200, 2 * len(vertices)),
    )[0]
    gradient_projection = incidence.transpose() @ gradient_solution
    harmonic_residual = indicator - gradient_projection
    return {
        "vertices": vertices,
        "index": index,
        "edge_list": edge_list,
        "incidence": incidence,
        "components": components,
        "obstruction_vertices": obstruction_vertices,
        "indicator": indicator,
        "potential": gradient_solution,
        "gradient_projection": gradient_projection,
        "harmonic_residual": harmonic_residual,
    }


def mixed_harmonic_class_report(
    mod2_power: int = 6,
    mod3_power: int = 3,
    sample_lift_power: int = 2,
    obstruction_R: int = 2,
    obstruction_u_mod2: int = 7,
    obstruction_u_mod3_modulus: int = 9,
) -> MixedHarmonicClassReport:
    """Project the full mixed obstruction indicator onto finite cycle space."""

    if mod2_power < 2:
        raise ValueError("mod2_power must be at least two")
    if mod3_power < 1:
        raise ValueError("mod3_power must be positive")
    if obstruction_R < 1:
        raise ValueError("obstruction_R must be positive")
    import numpy as np

    pieces = _mixed_hodge_components(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        obstruction_R=obstruction_R,
        obstruction_u_mod2=obstruction_u_mod2,
        obstruction_u_mod3_modulus=obstruction_u_mod3_modulus,
    )
    vertices = pieces["vertices"]
    edge_list = pieces["edge_list"]
    components = pieces["components"]
    obstruction_vertices = pieces["obstruction_vertices"]
    indicator = pieces["indicator"]
    harmonic_residual = pieces["harmonic_residual"]
    projection_norm = float(np.linalg.norm(harmonic_residual))
    indicator_norm = float(np.linalg.norm(indicator))
    ratio = None if indicator_norm == 0.0 else projection_norm / indicator_norm
    first_betti = len(edge_list) - len(vertices) + components
    return MixedHarmonicClassReport(
        type="mixed_harmonic_class_identification",
        status="finite_mixed_graph_projection_not_global_hodge_proof",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        vertices=len(vertices),
        undirected_edges=len(edge_list),
        components=components,
        first_betti=first_betti,
        harmonic_dimension=first_betti,
        projection_method="sparse_lsmr_gradient_residual",
        obstruction_R=obstruction_R,
        obstruction_u_mod2=obstruction_u_mod2,
        obstruction_u_mod3_modulus=obstruction_u_mod3_modulus,
        obstruction_vertices=obstruction_vertices,
        indicator_edges=int(indicator.sum()),
        indicator_norm=indicator_norm,
        harmonic_projection_norm=projection_norm,
        harmonic_projection_ratio=ratio,
    )


def obstruction_lyapunov_correction_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    sample_lift_power: int = 2,
    trajectory_samples: int = 100,
    obstruction_R: int = 2,
    obstruction_u_mod2: int = 7,
    obstruction_u_mod3_modulus: int = 9,
) -> ObstructionLyapunovCorrectionReport:
    """Extract the finite potential whose gradient explains the obstruction."""

    import random
    import numpy as np

    from .post_exit_map import (
        PostExitState,
        _sample_u_values,
        post_exit_transition_sample,
    )

    pieces = _mixed_hodge_components(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        obstruction_R=obstruction_R,
        obstruction_u_mod2=obstruction_u_mod2,
        obstruction_u_mod3_modulus=obstruction_u_mod3_modulus,
    )
    vertices = pieces["vertices"]
    index = pieces["index"]
    edge_list = pieces["edge_list"]
    # Choose the sign so psi(source)-psi(target) is positive on the PECM
    # obstruction trajectories. The Hodge residual norm is sign-invariant.
    potential = -pieces["potential"]
    gradient_projection = -pieces["gradient_projection"]
    harmonic_residual = pieces["harmonic_residual"]
    indicator = pieces["indicator"]
    indicator_norm = float(np.linalg.norm(indicator))
    residual_norm = float(np.linalg.norm(harmonic_residual))
    residual_ratio = None if indicator_norm == 0.0 else residual_norm / indicator_norm
    potential_entries = tuple(
        (r2, r3, float(value))
        for (r2, r3), value in zip(vertices, potential, strict=True)
        if abs(value) > 1e-10
    )
    edge_entries = tuple(
        (vertices[left][0] * (3**mod3_power) + vertices[left][1],
         vertices[right][0] * (3**mod3_power) + vertices[right][1],
         float(value))
        for (left, right), value in zip(edge_list, gradient_projection, strict=True)
        if abs(value) > 1e-10
    )

    rng = random.Random(0)
    deltas: list[float] = []
    reentered = 0
    descended = 0
    u3_choices = [
        value
        for value in range(3**mod3_power)
        if value % obstruction_u_mod3_modulus == 0
    ]
    for _ in range(trajectory_samples):
        u3 = rng.choice(u3_choices)
        state = PostExitState(
            R=obstruction_R,
            u_mod2=obstruction_u_mod2 % (1 << mod2_power),
            u_mod2_power=mod2_power,
            u_mod3=u3,
            u_mod3_power=mod3_power,
        )
        lifts = _sample_u_values(state, 2)
        u = rng.choice(lifts)
        transition = post_exit_transition_sample(state, u, max_steps=200)
        if transition.target is None:
            descended += 1
            continue
        reentered += 1
        source_vertex = (
            ((state.u_mod2 << state.R) - 1) % (1 << mod2_power),
            ((1 << state.R) * state.u_mod3 - 1) % (3**mod3_power),
        )
        target = transition.target
        target_vertex = (
            ((target.u_mod2 << target.R) - 1) % (1 << mod2_power),
            ((1 << target.R) * target.u_mod3 - 1) % (3**mod3_power),
        )
        if source_vertex in index and target_vertex in index:
            deltas.append(float(potential[index[source_vertex]] - potential[index[target_vertex]]))
    check = ObstructionTrajectoryCheck(
        samples=trajectory_samples,
        reentered=reentered,
        descended=descended,
        min_delta=None if not deltas else min(deltas),
        max_delta=None if not deltas else max(deltas),
        mean_delta=None if not deltas else sum(deltas) / len(deltas),
    )
    return ObstructionLyapunovCorrectionReport(
        type="obstruction_lyapunov_correction",
        status="finite_hodge_potential_not_global_lyapunov_proof",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        vertices=len(vertices),
        undirected_edges=len(edge_list),
        obstruction_vertices=pieces["obstruction_vertices"],
        residual_norm=residual_norm,
        residual_ratio=residual_ratio,
        potential_entries=potential_entries,
        edge_correction_entries=edge_entries,
        trajectory_check=check,
    )
