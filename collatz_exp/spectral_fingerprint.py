"""Mixed spectral fingerprints from several finite Collatz artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .cohomology import cohomology_report
from .hodge import hodge_report
from .max_plus import max_plus_debt_report
from .mixed_tensor import mixed_tensor_rank_report
from .sandpile import sandpile_report
from .transfer_op import transfer_spectrum
from .walsh_transfer import walsh_transfer_report


@dataclass(frozen=True)
class SpectralFingerprintLevel:
    modulus_power: int
    sample_lift_power: int
    transfer_second_abs: float | None
    max_plus_mean_debt: float | None
    harmonic_dimension: int
    first_betti: int
    sandpile_forest_count: int
    walsh_above_threshold: int
    mixed_rank_2_vs_rest: int | None
    mixed_rank_23_vs_rest: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpectralFingerprintReport:
    type: str
    status: str
    k_min: int
    k_max: int
    levels: tuple[SpectralFingerprintLevel, ...]

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


def spectral_fingerprint_report(
    k_min: int = 4,
    k_max: int = 6,
    sample_lift_power: int = 3,
    mixed_mod3_power: int = 1,
) -> SpectralFingerprintReport:
    """Combine spectral, Hodge, sandpile, Walsh, and tensor signatures."""

    if k_min < 2 or k_max < k_min:
        raise ValueError("require 2 <= k_min <= k_max")
    levels: list[SpectralFingerprintLevel] = []
    for k in range(k_min, k_max + 1):
        transfer = transfer_spectrum(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
        max_plus = max_plus_debt_report(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
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
        walsh = walsh_transfer_report(
            modulus_power=k,
            sample_lift_power=sample_lift_power,
        )
        mixed_rank_2 = None
        mixed_rank_23 = None
        if k <= 5:
            mixed = mixed_tensor_rank_report(
                mod2_power=k,
                mod3_power=mixed_mod3_power,
            )
            mixed_rank_2 = mixed.flatten_rank_2_vs_rest
            mixed_rank_23 = mixed.flatten_rank_23_vs_rest
        levels.append(
            SpectralFingerprintLevel(
                modulus_power=k,
                sample_lift_power=sample_lift_power,
                transfer_second_abs=transfer.second_eigenvalue_abs,
                max_plus_mean_debt=max_plus.max_cycle_mean_debt,
                harmonic_dimension=hodge.harmonic_dimension,
                first_betti=cohom.first_betti,
                sandpile_forest_count=sand.total_spanning_forest_count,
                walsh_above_threshold=walsh.coefficients_above_threshold,
                mixed_rank_2_vs_rest=mixed_rank_2,
                mixed_rank_23_vs_rest=mixed_rank_23,
            )
        )
    return SpectralFingerprintReport(
        type="mixed_spectral_fingerprint",
        status="finite_fingerprint_not_collatz_proof",
        k_min=k_min,
        k_max=k_max,
        levels=tuple(levels),
    )
