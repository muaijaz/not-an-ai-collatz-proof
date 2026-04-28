"""Targeted analysis for Mersenne-tail cylinders ``n = 2^R*u - 1``."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log2
from typing import Any

from .certificates import certificate_from_residue
from .cover import CertificateCoverReport, CoverFrontierNode, frontier_density
from .core import accelerated_step, first_descent, v2
from .frontier_analysis import initial_ones
from .search import forced_trace_for_residue


@dataclass(frozen=True)
class TailPrefixFormula:
    """Closed form for the forced all-ones prefix of ``2^R*u - 1``."""

    R: int
    forced_steps: int
    input_expression: str
    output_expression: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailParameterSample:
    R: int
    u_residue: int
    u_mod_power: int
    canonical_R: int
    canonical_u_residue: int
    canonical_u_mod_power: int
    residue: int
    modulus_power: int
    forced_initial_ones: int
    m: int
    A: int
    debt: float
    certificate_found: bool
    certificate_m: int | None
    certificate_A: int | None
    certificate_threshold_num: int | None
    certificate_threshold_den: int | None
    representative_descent_m: int | None
    representative_descent_A: int | None
    representative_landing: int | None

    @property
    def density(self) -> Fraction:
        return Fraction(1, 1 << (self.modulus_power - 1))

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailFamilyReport:
    type: str
    status: str
    formula: TailPrefixFormula
    R: int
    u_mod_power: int
    samples: int
    certified_count: int
    certified_density_num: int
    certified_density_den: int
    unresolved_density_num: int
    unresolved_density_den: int
    top_dangerous: tuple[TailParameterSample, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "formula": self.formula.to_json_dict(),
            "R": self.R,
            "u_mod_power": self.u_mod_power,
            "samples": self.samples,
            "certified_count": self.certified_count,
            "certified_density_num": self.certified_density_num,
            "certified_density_den": self.certified_density_den,
            "unresolved_density_num": self.unresolved_density_num,
            "unresolved_density_den": self.unresolved_density_den,
            "top_dangerous": [
                sample.to_json_dict() for sample in self.top_dangerous
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class CoverTailReport:
    type: str
    status: str
    frontier_classes: int
    tail_classes: int
    tail_density_num: int
    tail_density_den: int
    top_tails: tuple[TailParameterSample, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "frontier_classes": self.frontier_classes,
            "tail_classes": self.tail_classes,
            "tail_density_num": self.tail_density_num,
            "tail_density_den": self.tail_density_den,
            "top_tails": [sample.to_json_dict() for sample in self.top_tails],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailRenormalizationStep:
    R: int
    u: int
    n: int
    c: int
    next_n: int
    next_R: int
    next_u: int
    block_m: int
    block_A: int
    block_debt: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailRenormalizationReport:
    type: str
    status: str
    R: int
    u_start: int
    steps: int
    path: tuple[TailRenormalizationStep, ...]
    total_m: int
    total_A: int
    total_debt: float
    descended: bool

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "R": self.R,
            "u_start": self.u_start,
            "steps": self.steps,
            "path": [item.to_json_dict() for item in self.path],
            "total_m": self.total_m,
            "total_A": self.total_A,
            "total_debt": self.total_debt,
            "descended": self.descended,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailRenormalizationFamilyReport:
    type: str
    status: str
    R: int
    u_mod_power: int
    samples: int
    max_blocks: int
    descended_count: int
    left_tail_count: int
    max_total_debt: float
    max_steps: int
    top_dangerous: tuple[TailRenormalizationReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "R": self.R,
            "u_mod_power": self.u_mod_power,
            "samples": self.samples,
            "max_blocks": self.max_blocks,
            "descended_count": self.descended_count,
            "left_tail_count": self.left_tail_count,
            "max_total_debt": self.max_total_debt,
            "max_steps": self.max_steps,
            "top_dangerous": [
                item.to_json_dict() for item in self.top_dangerous
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def tail_prefix_formula(R: int) -> TailPrefixFormula:
    """Return the closed form after the forced ``R-1`` single-divider steps."""

    if R < 2:
        raise ValueError("R must be at least two")
    return TailPrefixFormula(
        R=R,
        forced_steps=R - 1,
        input_expression=f"2^{R}*u - 1",
        output_expression=f"2*3^{R - 1}*u - 1",
    )


def tail_renormalization_step(R: int, u: int) -> TailRenormalizationStep:
    """Apply one forced tail block to ``n = 2^R*u - 1`` and recode the result."""

    if R < 2:
        raise ValueError("R must be at least two")
    if u < 1:
        raise ValueError("u must be positive")
    n = (1 << R) * u - 1
    c = v2((3**R) * u - 1)
    next_n = ((3**R) * u - 1) >> c

    direct_n = n
    direct_A = 0
    for _ in range(R):
        direct_n, direct_a = accelerated_step(direct_n)
        direct_A += direct_a
    if direct_n != next_n or direct_A != R + c:
        raise AssertionError("tail block formula disagrees with direct iteration")

    next_R = v2(next_n + 1)
    next_u = (next_n + 1) >> next_R
    block_m = R
    block_A = R + c
    return TailRenormalizationStep(
        R=R,
        u=u,
        n=n,
        c=c,
        next_n=next_n,
        next_R=next_R,
        next_u=next_u,
        block_m=block_m,
        block_A=block_A,
        block_debt=block_m * log2(3) - block_A,
    )


def tail_renormalization_report(
    R: int,
    u: int,
    max_blocks: int = 20,
) -> TailRenormalizationReport:
    """Iterate the tail renormalization map for one representative."""

    if max_blocks < 1:
        raise ValueError("max_blocks must be positive")
    start_n = (1 << R) * u - 1
    path: list[TailRenormalizationStep] = []
    total_m = 0
    total_A = 0
    current_R = R
    current_u = u
    descended = False
    for _ in range(max_blocks):
        step = tail_renormalization_step(current_R, current_u)
        path.append(step)
        total_m += step.block_m
        total_A += step.block_A
        if step.next_n < start_n:
            descended = True
            break
        current_R = step.next_R
        current_u = step.next_u
        if current_R < 2:
            descended = step.next_n < start_n
            break
    return TailRenormalizationReport(
        type="tail_renormalization_report",
        status="finite_tail_renormalization_not_collatz_proof",
        R=R,
        u_start=u,
        steps=len(path),
        path=tuple(path),
        total_m=total_m,
        total_A=total_A,
        total_debt=total_m * log2(3) - total_A,
        descended=descended,
    )


def tail_renormalization_family_report(
    R: int,
    u_mod_power: int,
    max_blocks: int = 20,
    top_n: int = 10,
    odd_u_only: bool = True,
) -> TailRenormalizationFamilyReport:
    """Rank a finite family of tail-renormalization representatives."""

    if u_mod_power < 0:
        raise ValueError("u_mod_power must be nonnegative")
    if top_n < 1:
        raise ValueError("top_n must be positive")
    u_values = range(1 << u_mod_power)
    if odd_u_only and u_mod_power > 0:
        u_values = range(1, 1 << u_mod_power, 2)
    reports = tuple(
        tail_renormalization_report(R=R, u=u, max_blocks=max_blocks)
        for u in u_values
    )
    left_tail_count = sum(
        1
        for report in reports
        if report.path and report.path[-1].next_R < 2 and not report.descended
    )
    top = tuple(
        sorted(
            reports,
            key=lambda report: (
                report.total_debt,
                report.steps,
                report.u_start,
            ),
            reverse=True,
        )[:top_n]
    )
    return TailRenormalizationFamilyReport(
        type="tail_renormalization_family_report",
        status="finite_tail_renormalization_family_not_collatz_proof",
        R=R,
        u_mod_power=u_mod_power,
        samples=len(reports),
        max_blocks=max_blocks,
        descended_count=sum(1 for report in reports if report.descended),
        left_tail_count=left_tail_count,
        max_total_debt=max((report.total_debt for report in reports), default=0.0),
        max_steps=max((report.steps for report in reports), default=0),
        top_dangerous=top,
    )


def tail_residue(R: int, u_residue: int, u_mod_power: int) -> tuple[int, int]:
    """Return ``(residue, modulus_power)`` for ``u == u_residue mod 2^ell``."""

    if R < 2:
        raise ValueError("R must be at least two")
    if u_mod_power < 0:
        raise ValueError("u_mod_power must be nonnegative")
    modulus_power = R + u_mod_power
    modulus = 1 << modulus_power
    residue = ((u_residue % (1 << u_mod_power)) << R) - 1
    return residue % modulus, modulus_power


def canonical_tail_coordinate(
    R: int,
    u_residue: int,
    u_mod_power: int,
) -> tuple[int, int, int]:
    """Move forced powers of two from ``u`` into the tail exponent ``R``."""

    if u_mod_power == 0:
        return R, 0, 0
    modulus = 1 << u_mod_power
    u = u_residue % modulus
    if u == 0:
        return R + u_mod_power, 0, 0
    shift = (u & -u).bit_length() - 1
    return R + shift, u >> shift, u_mod_power - shift


def analyze_tail_parameter_sample(
    R: int,
    u_residue: int,
    u_mod_power: int,
    max_certificate_steps: int = 1_000,
    bucket_scale: int = 100,
    representative_max_steps: int = 0,
) -> TailParameterSample:
    """Analyze one parameter cylinder in the Mersenne-tail family."""

    residue, modulus_power = tail_residue(R, u_residue, u_mod_power)
    canonical_R, canonical_u_residue, canonical_u_mod_power = canonical_tail_coordinate(
        R,
        u_residue,
        u_mod_power,
    )
    trace = forced_trace_for_residue(
        residue,
        modulus_power,
        max_steps=max_certificate_steps,
        bucket_scale=bucket_scale,
    )
    cert = certificate_from_residue(
        residue,
        modulus_power,
        max_steps=max_certificate_steps,
    )
    rep_m: int | None = None
    rep_A: int | None = None
    rep_landing: int | None = None
    if representative_max_steps > 0:
        representative = residue if residue > 1 else residue + (1 << modulus_power)
        descent = first_descent(representative, max_steps=representative_max_steps)
        if descent is not None:
            rep_m = descent.m
            rep_A = descent.A
            rep_landing = descent.landing
    return TailParameterSample(
        R=R,
        u_residue=u_residue % (1 << u_mod_power),
        u_mod_power=u_mod_power,
        canonical_R=canonical_R,
        canonical_u_residue=canonical_u_residue,
        canonical_u_mod_power=canonical_u_mod_power,
        residue=residue,
        modulus_power=modulus_power,
        forced_initial_ones=initial_ones(trace.word),
        m=trace.m,
        A=trace.A,
        debt=trace.m * log2(3) - trace.A,
        certificate_found=cert is not None,
        certificate_m=None if cert is None else cert.m,
        certificate_A=None if cert is None else cert.A,
        certificate_threshold_num=None if cert is None else cert.threshold_num,
        certificate_threshold_den=None if cert is None else cert.threshold_den,
        representative_descent_m=rep_m,
        representative_descent_A=rep_A,
        representative_landing=rep_landing,
    )


def analyze_tail_family(
    R: int = 20,
    u_mod_power: int = 6,
    max_certificate_steps: int = 1_000,
    top_n: int = 20,
    odd_u_only: bool = False,
    representative_max_steps: int = 0,
) -> TailFamilyReport:
    """Split ``n == -1 mod 2^R`` by ``u mod 2^ell`` and rank hard children."""

    if top_n < 1:
        raise ValueError("top_n must be positive")
    u_values = range(1 << u_mod_power)
    if odd_u_only and u_mod_power > 0:
        u_values = range(1, 1 << u_mod_power, 2)
    samples = tuple(
        analyze_tail_parameter_sample(
            R=R,
            u_residue=u,
            u_mod_power=u_mod_power,
            max_certificate_steps=max_certificate_steps,
            representative_max_steps=representative_max_steps,
        )
        for u in u_values
    )
    certified = tuple(sample for sample in samples if sample.certificate_found)
    certified_density = sum((sample.density for sample in certified), Fraction(0, 1))
    total_density = sum((sample.density for sample in samples), Fraction(0, 1))
    unresolved_density = total_density - certified_density
    dangerous = tuple(
        sorted(
            (sample for sample in samples if not sample.certificate_found),
            key=lambda sample: (
                sample.debt,
                sample.forced_initial_ones,
                sample.u_residue,
            ),
            reverse=True,
        )[:top_n]
    )
    return TailFamilyReport(
        type="mersenne_tail_parameter_family_report",
        status="finite_tail_family_split_not_collatz_proof",
        formula=tail_prefix_formula(R),
        R=R,
        u_mod_power=u_mod_power,
        samples=len(samples),
        certified_count=len(certified),
        certified_density_num=certified_density.numerator,
        certified_density_den=certified_density.denominator,
        unresolved_density_num=unresolved_density.numerator,
        unresolved_density_den=unresolved_density.denominator,
        top_dangerous=dangerous,
    )


def analyze_cover_tail_frontier(
    report: CertificateCoverReport,
    min_initial_ones: int = 12,
    top_n: int = 20,
    max_certificate_steps: int = 1_000,
    representative_max_steps: int = 0,
) -> CoverTailReport:
    """Rank unresolved cover nodes that look like high-odd-density tails."""

    if min_initial_ones < 1:
        raise ValueError("min_initial_ones must be positive")
    if top_n < 1:
        raise ValueError("top_n must be positive")
    samples: list[TailParameterSample] = []
    nodes: list[CoverFrontierNode] = []
    for node in report.frontier:
        trace = forced_trace_for_residue(
            node.residue,
            node.modulus_power,
            max_steps=max_certificate_steps,
        )
        run = initial_ones(trace.word)
        if run < min_initial_ones:
            continue
        R = run + 1
        if node.modulus_power < R:
            continue
        u_mod_power = node.modulus_power - R
        u_residue = ((node.residue + 1) >> R) % (1 << u_mod_power)
        samples.append(
            analyze_tail_parameter_sample(
                R=R,
                u_residue=u_residue,
                u_mod_power=u_mod_power,
                max_certificate_steps=max_certificate_steps,
                representative_max_steps=representative_max_steps,
            )
        )
        nodes.append(node)

    ranked = tuple(
        sorted(
            samples,
            key=lambda sample: (
                sample.debt,
                sample.forced_initial_ones,
                sample.modulus_power,
                sample.residue,
            ),
            reverse=True,
        )[:top_n]
    )
    density = frontier_density(tuple(nodes))
    return CoverTailReport(
        type="cover_tail_frontier_report",
        status="finite_tail_frontier_ranking_not_collatz_proof",
        frontier_classes=len(report.frontier),
        tail_classes=len(samples),
        tail_density_num=density.numerator,
        tail_density_den=density.denominator,
        top_tails=ranked,
    )
