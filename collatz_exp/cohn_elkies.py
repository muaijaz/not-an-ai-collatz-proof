"""Cohn-Elkies/Delsarte-style Walsh LP bounds on finite residue sets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .certificates import certificate_from_residue
from .walsh_transfer import fwht


@dataclass(frozen=True)
class CohnElkiesWalshReport:
    type: str
    status: str
    modulus_power: int
    dimension: int
    group_model: str
    solver: str
    success: bool
    unresolved_points: int
    allowed_differences: int
    objective_sum: float | None
    density_bound: float | None
    unresolved_density_num: int
    unresolved_density_den: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def walsh_matrix(dimension: int) -> list[list[int]]:
    """Return the unnormalized Walsh character matrix on ``(Z/2)^d``."""

    if dimension < 1 or dimension & (dimension - 1):
        raise ValueError("dimension must be a positive power of two")
    rows: list[list[int]] = []
    for character in range(dimension):
        values = [1 if ((character & x).bit_count() % 2 == 0) else -1 for x in range(dimension)]
        rows.append(values)
    return rows


def unresolved_indices(modulus_power: int) -> tuple[int, ...]:
    """Return odd-residue indices not discharged by a local descent certificate."""

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    indices: list[int] = []
    for index, residue in enumerate(range(1, 1 << modulus_power, 2)):
        if certificate_from_residue(residue, modulus_power) is None:
            indices.append(index)
    return tuple(indices)


def difference_closure(indices: tuple[int, ...]) -> tuple[int, ...]:
    values = {0}
    for left in indices:
        for right in indices:
            values.add(left ^ right)
    return tuple(sorted(values))


def cohn_elkies_walsh_bound(
    modulus_power: int = 8,
) -> CohnElkiesWalshReport:
    """Solve a finite Walsh-positive LP for unresolved odd residues.

    This is a Delsarte packing bound on the XOR group indexing odd residues.
    It is rigorous for this finite model, but the model is only a quotient
    artifact and does not by itself prove a Collatz density theorem.
    """

    dimension = 1 << (modulus_power - 1)
    unresolved = unresolved_indices(modulus_power)
    allowed = set(difference_closure(unresolved))
    unresolved_density = Fraction(len(unresolved), dimension)

    try:
        import numpy as np
        from scipy.optimize import linprog
    except ImportError:
        return CohnElkiesWalshReport(
            type="cohn_elkies_walsh_residue_lp",
            status="scipy_unavailable_lp_not_solved",
            modulus_power=modulus_power,
            dimension=dimension,
            group_model="xor_odd_index_bits",
            solver="scipy.optimize.linprog/highs",
            success=False,
            unresolved_points=len(unresolved),
            allowed_differences=len(allowed),
            objective_sum=None,
            density_bound=None,
            unresolved_density_num=unresolved_density.numerator,
            unresolved_density_den=unresolved_density.denominator,
        )

    W = walsh_matrix(dimension)
    c = np.array([-1.0 for _ in range(dimension)])
    A_ub: list[list[float]] = []
    b_ub: list[float] = []
    for row in W:
        A_ub.append([-float(value) for value in row])
        b_ub.append(0.0)
    for x in range(dimension):
        if x not in allowed:
            row = [0.0 for _ in range(dimension)]
            row[x] = 1.0
            A_ub.append(row)
            b_ub.append(0.0)
    A_eq = [[0.0 for _ in range(dimension)]]
    A_eq[0][0] = 1.0
    b_eq = [1.0]
    result = linprog(
        c=c,
        A_ub=np.array(A_ub, dtype=float),
        b_ub=np.array(b_ub, dtype=float),
        A_eq=np.array(A_eq, dtype=float),
        b_eq=np.array(b_eq, dtype=float),
        bounds=[(None, None) for _ in range(dimension)],
        method="highs",
    )
    if not result.success:
        return CohnElkiesWalshReport(
            type="cohn_elkies_walsh_residue_lp",
            status=f"linprog_failed_{result.status}",
            modulus_power=modulus_power,
            dimension=dimension,
            group_model="xor_odd_index_bits",
            solver="scipy.optimize.linprog/highs",
            success=False,
            unresolved_points=len(unresolved),
            allowed_differences=len(allowed),
            objective_sum=None,
            density_bound=None,
            unresolved_density_num=unresolved_density.numerator,
            unresolved_density_den=unresolved_density.denominator,
        )
    objective_sum = float(sum(result.x))
    density_bound = None if objective_sum <= 0 else 1.0 / objective_sum
    return CohnElkiesWalshReport(
        type="cohn_elkies_walsh_residue_lp",
        status="finite_walsh_positive_lp_not_collatz_proof",
        modulus_power=modulus_power,
        dimension=dimension,
        group_model="xor_odd_index_bits",
        solver="scipy.optimize.linprog/highs",
        success=True,
        unresolved_points=len(unresolved),
        allowed_differences=len(allowed),
        objective_sum=objective_sum,
        density_bound=density_bound,
        unresolved_density_num=unresolved_density.numerator,
        unresolved_density_den=unresolved_density.denominator,
    )


def walsh_spectrum(values: tuple[int, ...]) -> tuple[int, ...]:
    """Small helper for tests and artifacts."""

    transformed = list(values)
    fwht(transformed)
    return tuple(transformed)
