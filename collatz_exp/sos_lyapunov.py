"""Solver-ready Lyapunov/SOS scaffold for finite residue quotients.

This module emits exact integer linear inequalities for a polynomial template
``V(r2, r3)`` on a finite ``2/3`` residue quotient. It does not solve an SDP or
claim a Lyapunov certificate; it creates a machine-readable artifact for tools
such as SumOfSquares.jl, Mosek, Z3, or a future neural-symbolic extractor.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class LyapunovConstraint:
    source2: int
    source3: int
    target2: int
    target3: int
    valuation: int
    delta_coefficients: tuple[int, ...]


@dataclass(frozen=True)
class LyapunovTemplateArtifact:
    type: str
    status: str
    proof_claim: bool
    modulus_power: int
    mod3_power: int
    degree: int
    basis: tuple[str, ...]
    normalization: str
    solver: str
    constraints: int
    sample_constraints: tuple[LyapunovConstraint, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["basis"] = list(self.basis)
        data["sample_constraints"] = [
            asdict(constraint) for constraint in self.sample_constraints
        ]
        for constraint in data["sample_constraints"]:
            constraint["delta_coefficients"] = list(constraint["delta_coefficients"])
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def monomial_features(degree: int) -> tuple[tuple[int, int], ...]:
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    return tuple(
        (i, j)
        for total in range(degree + 1)
        for i in range(total + 1)
        for j in (total - i,)
    )


def feature_names(degree: int) -> tuple[str, ...]:
    names: list[str] = []
    for i, j in monomial_features(degree):
        if i == 0 and j == 0:
            names.append("1")
        elif i == 0:
            names.append(f"y^{j}")
        elif j == 0:
            names.append(f"x^{i}")
        else:
            names.append(f"x^{i}*y^{j}")
    return tuple(names)


def feature_values(residue2: int, residue3: int, degree: int) -> tuple[int, ...]:
    return tuple((residue2**i) * (residue3**j) for i, j in monomial_features(degree))


def lyapunov_template_artifact(
    modulus_power: int = 5,
    mod3_power: int = 2,
    degree: int = 2,
    max_sample_constraints: int = 12,
) -> LyapunovTemplateArtifact:
    """Build finite inequalities ``V(source) - V(target) >= epsilon``."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")

    modulus2 = 1 << modulus_power
    modulus3 = 3**mod3_power
    constraints: list[LyapunovConstraint] = []
    total_constraints = 0

    for residue2 in range(1, modulus2, 2):
        representative = residue2
        target, valuation = accelerated_step(representative)
        target2 = target % modulus2
        for residue3 in range(modulus3):
            target3 = (
                ((3 * residue3 + 1) * pow(pow(2, valuation, modulus3), -1, modulus3))
                % modulus3
            )
            source_values = feature_values(residue2, residue3, degree)
            target_values = feature_values(target2, target3, degree)
            delta = tuple(a - b for a, b in zip(source_values, target_values))
            total_constraints += 1
            if len(constraints) < max_sample_constraints:
                constraints.append(
                    LyapunovConstraint(
                        source2=residue2,
                        source3=residue3,
                        target2=target2,
                        target3=target3,
                        valuation=valuation,
                        delta_coefficients=delta,
                    )
                )

    return LyapunovTemplateArtifact(
        type="finite_polynomial_lyapunov_template",
        status="solver_not_run_no_proof_claim",
        proof_claim=False,
        modulus_power=modulus_power,
        mod3_power=mod3_power,
        degree=degree,
        basis=feature_names(degree),
        normalization="fix one coefficient or mean(V)=0 before solving",
        solver="none",
        constraints=total_constraints,
        sample_constraints=tuple(constraints),
    )
