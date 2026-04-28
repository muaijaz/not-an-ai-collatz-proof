"""Mass-transport view of certificate covers on the binary residue poset.

This is inspired by the sub-Markov/antichain proof pattern in the pasted
primitive-set note. In the odd residue prefix tree, the hitting probability of
``r mod 2^k`` under fair binary refinement is exactly ``2^(1-k)``. A finite
certificate cover plus its unresolved frontier should form an antichain whose
total mass is one.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .cover import CertificateCoverReport, CoverFrontierNode


@dataclass(frozen=True)
class CoverMassReport:
    type: str
    status: str
    certificate_classes: int
    frontier_classes: int
    certified_mass_num: int
    certified_mass_den: int
    frontier_mass_num: int
    frontier_mass_den: int
    total_mass_num: int
    total_mass_den: int
    antichain_valid: bool
    partition_valid: bool
    overlap_witnesses: tuple[tuple[str, str], ...]

    @property
    def certified_mass(self) -> Fraction:
        return Fraction(self.certified_mass_num, self.certified_mass_den)

    @property
    def frontier_mass(self) -> Fraction:
        return Fraction(self.frontier_mass_num, self.frontier_mass_den)

    @property
    def total_mass(self) -> Fraction:
        return Fraction(self.total_mass_num, self.total_mass_den)

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["overlap_witnesses"] = [list(item) for item in self.overlap_witnesses]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class _Cylinder:
    label: str
    residue: int
    modulus_power: int


def cylinder_mass(modulus_power: int) -> Fraction:
    """Return relative density among odd integers for one odd ``mod 2^k`` class."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    return Fraction(1, 1 << (modulus_power - 1))


def cylinder_contains(parent: _Cylinder, child: _Cylinder) -> bool:
    """Return whether the parent residue cylinder contains the child cylinder."""

    if parent.modulus_power > child.modulus_power:
        return False
    modulus = 1 << parent.modulus_power
    return child.residue % modulus == parent.residue % modulus


def _find_overlaps(cylinders: tuple[_Cylinder, ...], max_witnesses: int) -> tuple[tuple[str, str], ...]:
    witnesses: list[tuple[str, str]] = []
    for i, left in enumerate(cylinders):
        for right in cylinders[i + 1 :]:
            if cylinder_contains(left, right):
                witnesses.append((left.label, right.label))
            elif cylinder_contains(right, left):
                witnesses.append((right.label, left.label))
            if len(witnesses) >= max_witnesses:
                return tuple(witnesses)
    return tuple(witnesses)


def cover_mass_report(
    report: CertificateCoverReport,
    max_overlap_witnesses: int = 8,
) -> CoverMassReport:
    """Verify antichain mass accounting for a certificate-cover report."""

    certificate_cylinders = tuple(
        _Cylinder(
            label=f"cert:{certificate.residue}/2^{certificate.modulus_power}",
            residue=certificate.residue,
            modulus_power=certificate.modulus_power,
        )
        for certificate in report.certificates
    )
    frontier_cylinders = tuple(
        _Cylinder(
            label=f"frontier:{node.residue}/2^{node.modulus_power}",
            residue=node.residue,
            modulus_power=node.modulus_power,
        )
        for node in report.frontier
    )
    all_cylinders = certificate_cylinders + frontier_cylinders
    overlaps = _find_overlaps(all_cylinders, max_overlap_witnesses)

    certified_mass = sum(
        (cylinder_mass(cylinder.modulus_power) for cylinder in certificate_cylinders),
        Fraction(0, 1),
    )
    frontier_mass = sum(
        (cylinder_mass(cylinder.modulus_power) for cylinder in frontier_cylinders),
        Fraction(0, 1),
    )
    total_mass = certified_mass + frontier_mass

    return CoverMassReport(
        type="binary_prefix_antichain_mass_report",
        status="finite_cover_mass_identity_not_collatz_proof",
        certificate_classes=len(certificate_cylinders),
        frontier_classes=len(frontier_cylinders),
        certified_mass_num=certified_mass.numerator,
        certified_mass_den=certified_mass.denominator,
        frontier_mass_num=frontier_mass.numerator,
        frontier_mass_den=frontier_mass.denominator,
        total_mass_num=total_mass.numerator,
        total_mass_den=total_mass.denominator,
        antichain_valid=not overlaps,
        partition_valid=(not overlaps and total_mass == 1),
        overlap_witnesses=overlaps,
    )
