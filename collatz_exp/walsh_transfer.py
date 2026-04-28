"""Walsh-Hadamard diagnostics for truncated 2-adic transfer operators."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class WalshTransferReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    dimension: int
    row_denominator: int
    max_nonconstant_coeff_num: int
    max_nonconstant_coeff_den: int
    mean_nonconstant_l1_num: int
    mean_nonconstant_l1_den: int
    sparsity_threshold_num: int
    sparsity_threshold_den: int
    coefficients_above_threshold: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def fwht(values: list[int]) -> None:
    """In-place unnormalized fast Walsh-Hadamard transform."""

    length = len(values)
    if length == 0 or length & (length - 1):
        raise ValueError("FWHT length must be a positive power of two")
    step = 1
    while step < length:
        for start in range(0, length, step * 2):
            for offset in range(step):
                left = values[start + offset]
                right = values[start + offset + step]
                values[start + offset] = left + right
                values[start + offset + step] = left - right
        step *= 2


def walsh_transfer_report(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
    threshold_denominator: int = 8,
) -> WalshTransferReport:
    """Summarize Walsh sparsity of transition rows modulo ``2^k``."""

    if threshold_denominator < 1:
        raise ValueError("threshold_denominator must be positive")
    artifact = transition_matrix_artifact(
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
    )
    dimension = len(artifact.residues)
    threshold = Fraction(1, threshold_denominator)
    max_coeff = Fraction(0, 1)
    total_l1 = Fraction(0, 1)
    above = 0
    for row in artifact.row_counts:
        transformed = list(row)
        fwht(transformed)
        normalized = [Fraction(abs(value), artifact.row_denominator) for value in transformed]
        nonconstant = normalized[1:]
        if nonconstant:
            max_coeff = max(max_coeff, max(nonconstant))
            total_l1 += sum(nonconstant, Fraction(0, 1))
            above += sum(1 for value in nonconstant if value >= threshold)
    mean_l1 = total_l1 / dimension if dimension else Fraction(0, 1)
    return WalshTransferReport(
        type="walsh_hadamard_transfer_diagnostic",
        status="finite_walsh_basis_artifact_not_diagonalization_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        dimension=dimension,
        row_denominator=artifact.row_denominator,
        max_nonconstant_coeff_num=max_coeff.numerator,
        max_nonconstant_coeff_den=max_coeff.denominator,
        mean_nonconstant_l1_num=mean_l1.numerator,
        mean_nonconstant_l1_den=mean_l1.denominator,
        sparsity_threshold_num=threshold.numerator,
        sparsity_threshold_den=threshold.denominator,
        coefficients_above_threshold=above,
    )
