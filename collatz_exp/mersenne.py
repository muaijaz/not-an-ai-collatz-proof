"""Exact experiments for the Mersenne-family obstruction ``n = 2^R - 1``."""

from __future__ import annotations

from dataclasses import dataclass
import json
from math import log2
from typing import Any

from .certificates import certificate_from_residue
from .core import accelerated_step, first_descent, v2
from .cover import CertificateCoverReport, CoverFrontierNode
from .frontier_analysis import analyze_frontier_node


@dataclass(frozen=True)
class MersenneRun:
    R: int
    run_length: int
    post_run_value: int
    next_valuation: int


@dataclass(frozen=True)
class MersenneProfile:
    R: int
    post_run_steps: int
    post_run_valuation: int
    initial_debt: float
    max_debt: float
    landing_debt: float
    landing: int
    spikes: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class MersenneTailCylinder:
    residue: int
    modulus_power: int
    run_length: int
    defect: int
    m: int
    A: int
    debt: float

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "residue": self.residue,
            "modulus_power": self.modulus_power,
            "run_length": self.run_length,
            "defect": self.defect,
            "m": self.m,
            "A": self.A,
            "debt": self.debt,
        }


@dataclass(frozen=True)
class MersenneTailDischarge:
    residue: int
    modulus_power: int
    run_length: int
    representative_steps_to_descent: int | None
    representative_A_to_descent: int | None
    representative_landing: int | None
    subcylinders_checked: int
    subcylinders_certified: int
    best_extra_bits: int | None
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "residue": self.residue,
            "modulus_power": self.modulus_power,
            "run_length": self.run_length,
            "representative_steps_to_descent": self.representative_steps_to_descent,
            "representative_A_to_descent": self.representative_A_to_descent,
            "representative_landing": self.representative_landing,
            "subcylinders_checked": self.subcylinders_checked,
            "subcylinders_certified": self.subcylinders_certified,
            "best_extra_bits": self.best_extra_bits,
            "status": self.status,
        }


@dataclass(frozen=True)
class MersenneTailReport:
    type: str
    status: str
    frontier_classes: int
    tail_classes: int
    top_tails: tuple[MersenneTailCylinder, ...]
    discharges: tuple[MersenneTailDischarge, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "frontier_classes": self.frontier_classes,
            "tail_classes": self.tail_classes,
            "top_tails": [tail.to_json_dict() for tail in self.top_tails],
            "discharges": [discharge.to_json_dict() for discharge in self.discharges],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def mersenne_value(R: int) -> int:
    if R < 1:
        raise ValueError("R must be positive")
    return (1 << R) - 1


def initial_mersenne_run(R: int) -> MersenneRun:
    """Return the exact initial all-ones run for ``2^R - 1``."""

    if R < 2:
        raise ValueError("R must be at least 2")

    post_run_value = 2 * 3 ** (R - 1) - 1
    if R % 2 == 1:
        next_valuation = 2
    else:
        next_valuation = 3 + v2(R)

    return MersenneRun(
        R=R,
        run_length=R - 1,
        post_run_value=post_run_value,
        next_valuation=next_valuation,
    )


def verify_initial_mersenne_run(R: int) -> bool:
    """Check the closed-form initial run against direct iteration."""

    run = initial_mersenne_run(R)
    x = mersenne_value(R)
    valuations: list[int] = []

    for _ in range(run.run_length):
        x, a = accelerated_step(x)
        valuations.append(a)

    return (
        all(a == 1 for a in valuations)
        and x == run.post_run_value
        and v2(3 * x + 1) == run.next_valuation
    )


def profile_mersenne(R: int, spike_threshold: int = 4) -> MersenneProfile:
    """Profile descent after the initial Mersenne all-ones run."""

    run = initial_mersenne_run(R)
    original = mersenne_value(R)
    x = run.post_run_value
    post_A = 0
    post_steps = 0
    total_m = run.run_length
    total_A = run.run_length
    log2_3 = log2(3)
    initial_debt = total_m * log2_3 - total_A
    max_debt = initial_debt
    spikes: list[tuple[int, int, int]] = []

    while x >= original:
        x, a = accelerated_step(x)
        post_steps += 1
        post_A += a
        total_m += 1
        total_A += a
        debt = total_m * log2_3 - total_A
        max_debt = max(max_debt, debt)
        if a >= spike_threshold:
            spikes.append((post_steps, a, x))

    return MersenneProfile(
        R=R,
        post_run_steps=post_steps,
        post_run_valuation=post_A,
        initial_debt=initial_debt,
        max_debt=max_debt,
        landing_debt=total_m * log2_3 - total_A,
        landing=x,
        spikes=tuple(spikes),
    )


def mersenne_tail_defect(residue: int, modulus_power: int) -> int:
    """Return distance from the pure Mersenne residue ``-1 mod 2^k``."""

    modulus = 1 << modulus_power
    return ((modulus - 1) - (residue % modulus)) % modulus


def is_mersenne_tail_cylinder(
    node: CoverFrontierNode,
    min_run_length: int = 8,
) -> bool:
    analysis = analyze_frontier_node(node)
    return analysis.initial_ones >= min_run_length


def classify_mersenne_tail_cylinder(node: CoverFrontierNode) -> MersenneTailCylinder:
    analysis = analyze_frontier_node(node)
    return MersenneTailCylinder(
        residue=node.residue,
        modulus_power=node.modulus_power,
        run_length=analysis.initial_ones,
        defect=mersenne_tail_defect(node.residue, node.modulus_power),
        m=analysis.m,
        A=analysis.A,
        debt=analysis.debt,
    )


def representative_descent_from_cylinder(
    residue: int,
    modulus_power: int,
    max_steps: int = 10_000,
) -> tuple[int, int, int] | None:
    representative = residue % (1 << modulus_power)
    if representative <= 1:
        representative += 1 << modulus_power
    descent = first_descent(representative, max_steps=max_steps)
    if descent is None:
        return None
    return (descent.m, descent.A, descent.landing)


def discharge_mersenne_tail_cylinder(
    node: CoverFrontierNode,
    max_extra_bits: int = 6,
    max_certificate_steps: int = 1_000,
) -> MersenneTailDischarge:
    """Try to certify all immediate subcylinders after adding extra bits."""

    if max_extra_bits < 0:
        raise ValueError("max_extra_bits must be nonnegative")

    tail = classify_mersenne_tail_cylinder(node)
    representative = representative_descent_from_cylinder(
        node.residue,
        node.modulus_power,
    )
    rep_m: int | None
    rep_A: int | None
    rep_landing: int | None
    if representative is None:
        rep_m, rep_A, rep_landing = None, None, None
    else:
        rep_m, rep_A, rep_landing = representative

    total_checked = 0
    best_extra_bits: int | None = None
    best_certified = 0
    for extra_bits in range(max_extra_bits + 1):
        certified = 0
        checked = 1 << extra_bits
        for lift in range(checked):
            residue = node.residue + (lift << node.modulus_power)
            certificate = certificate_from_residue(
                residue,
                node.modulus_power + extra_bits,
                max_steps=max_certificate_steps,
            )
            if certificate is not None:
                certified += 1
        total_checked += checked
        if certified > best_certified:
            best_certified = certified
            best_extra_bits = extra_bits
        if certified == checked:
            return MersenneTailDischarge(
                residue=node.residue,
                modulus_power=node.modulus_power,
                run_length=tail.run_length,
                representative_steps_to_descent=rep_m,
                representative_A_to_descent=rep_A,
                representative_landing=rep_landing,
                subcylinders_checked=checked,
                subcylinders_certified=certified,
                best_extra_bits=extra_bits,
                status="all_subcylinders_certified_at_extra_precision",
            )

    return MersenneTailDischarge(
        residue=node.residue,
        modulus_power=node.modulus_power,
        run_length=tail.run_length,
        representative_steps_to_descent=rep_m,
        representative_A_to_descent=rep_A,
        representative_landing=rep_landing,
        subcylinders_checked=total_checked,
        subcylinders_certified=best_certified,
        best_extra_bits=best_extra_bits,
        status="not_discharged_within_extra_precision",
    )


def analyze_mersenne_tails(
    report: CertificateCoverReport,
    min_run_length: int = 8,
    top_n: int = 10,
    discharge_top_n: int = 3,
    max_extra_bits: int = 6,
) -> MersenneTailReport:
    tails = [
        classify_mersenne_tail_cylinder(node)
        for node in report.frontier
        if is_mersenne_tail_cylinder(node, min_run_length=min_run_length)
    ]
    tails.sort(key=lambda tail: (tail.run_length, tail.debt, -tail.defect), reverse=True)
    discharges = tuple(
        discharge_mersenne_tail_cylinder(
            CoverFrontierNode(tail.residue, tail.modulus_power),
            max_extra_bits=max_extra_bits,
        )
        for tail in tails[:discharge_top_n]
    )
    return MersenneTailReport(
        type="mersenne_tail_frontier_report",
        status="finite_tail_analysis_not_collatz_proof",
        frontier_classes=len(report.frontier),
        tail_classes=len(tails),
        top_tails=tuple(tails[:top_n]),
        discharges=discharges,
    )


def verify_mersenne_descent(Rmax: int) -> dict[int, MersenneProfile]:
    """Verify first descent for all Mersenne starts ``2^R - 1`` up to ``Rmax``."""

    if Rmax < 2:
        raise ValueError("Rmax must be at least 2")

    profiles: dict[int, MersenneProfile] = {}
    for R in range(2, Rmax + 1):
        profile = profile_mersenne(R)
        direct = first_descent(mersenne_value(R))
        if direct is None:
            raise RuntimeError(f"no first descent found for R={R}")
        if direct.m != (R - 1) + profile.post_run_steps:
            raise RuntimeError(f"profile mismatch for R={R}")
        profiles[R] = profile
    return profiles
