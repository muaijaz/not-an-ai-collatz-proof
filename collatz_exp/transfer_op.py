"""Truncated transfer-operator experiments on odd residues modulo ``2^k``."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class TransferSpectrumReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    dimension: int
    row_denominator: int
    second_eigenvalue_abs: float | None
    slowest_residue: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def transfer_spectrum(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
) -> TransferSpectrumReport:
    """Return spectrum summary if NumPy is installed, otherwise a fallback artifact."""

    artifact = transition_matrix_artifact(
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
    )
    dimension = len(artifact.residues)
    try:
        import numpy as np
    except ImportError:
        return TransferSpectrumReport(
            type="truncated_transfer_operator_spectrum",
            status="numpy_unavailable_matrix_artifact_only",
            modulus_power=modulus_power,
            sample_lift_power=sample_lift_power,
            dimension=dimension,
            row_denominator=artifact.row_denominator,
            second_eigenvalue_abs=None,
            slowest_residue=None,
        )

    matrix = np.array(artifact.row_counts, dtype=float) / artifact.row_denominator
    eigenvalues, eigenvectors = np.linalg.eig(matrix.T)
    order = np.argsort(-np.abs(eigenvalues))
    second_index = int(order[1]) if len(order) > 1 else int(order[0])
    vector = np.real(eigenvectors[:, second_index])
    slowest_index = int(np.argmax(np.abs(vector)))

    return TransferSpectrumReport(
        type="truncated_transfer_operator_spectrum",
        status="finite_truncated_heuristic_not_certificate",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        dimension=dimension,
        row_denominator=artifact.row_denominator,
        second_eigenvalue_abs=float(abs(eigenvalues[second_index])),
        slowest_residue=artifact.residues[slowest_index],
    )
