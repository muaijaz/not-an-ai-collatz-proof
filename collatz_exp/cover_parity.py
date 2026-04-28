"""Overlay Terras parity-cylinder data onto certificate-cover frontiers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .cover import CertificateCoverReport, CoverFrontierNode, frontier_density
from .parity import ParityAffine, parity_affine, parity_vector, terras_step


@dataclass(frozen=True)
class FrontierParityAnalysis:
    residue: int
    modulus_power: int
    bits: tuple[int, ...]
    odd_steps: int
    coefficient_num: int
    coefficient_den: int
    descent_threshold: int | None
    exception_count: int
    failing_exceptions: tuple[int, ...]
    terminal_one_exception: bool
    parity_certified: bool
    density_num: int
    density_den: int

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bits"] = list(self.bits)
        data["failing_exceptions"] = list(self.failing_exceptions)
        return data


@dataclass(frozen=True)
class CoverParityReport:
    type: str
    status: str
    frontier_classes: int
    parity_certified_classes: int
    parity_certified_density_num: int
    parity_certified_density_den: int
    remaining_density_num: int
    remaining_density_den: int
    parity_certified_frontier: tuple[CoverFrontierNode, ...]
    remaining_frontier: tuple[CoverFrontierNode, ...]
    top: tuple[FrontierParityAnalysis, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "frontier_classes": self.frontier_classes,
            "parity_certified_classes": self.parity_certified_classes,
            "parity_certified_density_num": self.parity_certified_density_num,
            "parity_certified_density_den": self.parity_certified_density_den,
            "remaining_density_num": self.remaining_density_num,
            "remaining_density_den": self.remaining_density_den,
            "parity_certified_frontier": [
                item.to_json_dict() for item in self.parity_certified_frontier
            ],
            "remaining_frontier": [
                item.to_json_dict() for item in self.remaining_frontier
            ],
            "top": [item.to_json_dict() for item in self.top],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _terras_iterate(n: int, steps: int) -> int:
    x = n
    for _ in range(steps):
        x = terras_step(x)
    return x


def _positive_exceptions_below_threshold(
    residue: int,
    modulus_power: int,
    threshold: int,
) -> tuple[int, ...]:
    modulus = 1 << modulus_power
    n = residue % modulus
    if n == 0:
        n = modulus
    values: list[int] = []
    while n < threshold:
        values.append(n)
        n += modulus
    return tuple(values)


def analyze_frontier_parity_node(node: CoverFrontierNode) -> FrontierParityAnalysis:
    """Analyze one frontier cylinder as a Terras parity cylinder."""

    bits = parity_vector(node.residue, node.modulus_power)
    affine = parity_affine(bits)
    if affine.residue != node.residue % (1 << node.modulus_power):
        raise RuntimeError("parity residue does not match frontier node")

    failing: list[int] = []
    terminal_one_exception = False
    exceptions: tuple[int, ...] = ()
    if affine.descent_threshold is not None:
        exceptions = _positive_exceptions_below_threshold(
            node.residue,
            node.modulus_power,
            affine.descent_threshold,
        )
        for value in exceptions:
            if value == 1:
                terminal_one_exception = True
                continue
            if _terras_iterate(value, node.modulus_power) >= value:
                failing.append(value)

    density = Fraction(1, 1 << (node.modulus_power - 1))
    parity_certified = (
        affine.descent_threshold is not None
        and not failing
    )
    return FrontierParityAnalysis(
        residue=node.residue,
        modulus_power=node.modulus_power,
        bits=bits,
        odd_steps=affine.odd_steps,
        coefficient_num=affine.coefficient_num,
        coefficient_den=affine.coefficient_den,
        descent_threshold=affine.descent_threshold,
        exception_count=len(exceptions),
        failing_exceptions=tuple(failing),
        terminal_one_exception=terminal_one_exception,
        parity_certified=parity_certified,
        density_num=density.numerator,
        density_den=density.denominator,
    )


def analyze_cover_parity(
    report: CertificateCoverReport,
    top_n: int = 20,
) -> CoverParityReport:
    """Overlay Terras parity certificates on unresolved cover frontier nodes."""

    if top_n < 1:
        raise ValueError("top_n must be positive")
    analyses = tuple(analyze_frontier_parity_node(node) for node in report.frontier)
    certified_nodes = tuple(item for item in analyses if item.parity_certified)
    parity_certified_frontier = tuple(
        CoverFrontierNode(item.residue, item.modulus_power)
        for item in certified_nodes
    )
    remaining_frontier = tuple(
        CoverFrontierNode(item.residue, item.modulus_power)
        for item in analyses
        if not item.parity_certified
    )
    certified_density = frontier_density(
        parity_certified_frontier
    )
    remaining_density = report.unresolved_odd_density - certified_density
    ranked = tuple(
        sorted(
            analyses,
            key=lambda item: (
                item.parity_certified,
                item.descent_threshold or -1,
                item.odd_steps,
                -item.residue,
            ),
            reverse=True,
        )[:top_n]
    )
    return CoverParityReport(
        type="cover_parity_overlay_report",
        status="finite_parity_overlay_not_collatz_proof",
        frontier_classes=len(report.frontier),
        parity_certified_classes=len(certified_nodes),
        parity_certified_density_num=certified_density.numerator,
        parity_certified_density_den=certified_density.denominator,
        remaining_density_num=remaining_density.numerator,
        remaining_density_den=remaining_density.denominator,
        parity_certified_frontier=parity_certified_frontier,
        remaining_frontier=remaining_frontier,
        top=ranked,
    )
