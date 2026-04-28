"""Rank unresolved cover frontier classes by exact forced-prefix features."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log2
from typing import Any

from .cover import CertificateCoverReport, CoverFrontierNode
from .cycles_eliahou import ConvergentWitness, log2_3_convergents
from .search import forced_trace_for_residue


@dataclass(frozen=True)
class FrontierClassAnalysis:
    residue: int
    modulus_power: int
    m: int
    A: int
    debt_bucket: int
    debt: float
    density_num: int
    density_den: int
    initial_ones: int
    suffix: tuple[int, ...]
    nearest_convergent: str
    nearest_convergent_error: float

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["suffix"] = list(self.suffix)
        return data


@dataclass(frozen=True)
class FrontierAnalysisReport:
    type: str
    status: str
    frontier_classes: int
    top: tuple[FrontierClassAnalysis, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "frontier_classes": self.frontier_classes,
            "top": [item.to_json_dict() for item in self.top],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def initial_ones(word: tuple[int, ...]) -> int:
    count = 0
    for value in word:
        if value != 1:
            break
        count += 1
    return count


def _nearest_convergent(A: int, m: int, witnesses: tuple[ConvergentWitness, ...]) -> tuple[str, float]:
    if m == 0 or not witnesses:
        return ("none", float("inf"))
    ratio = A / m
    best = min(witnesses, key=lambda witness: abs(ratio - witness.numerator_A / witness.denominator_m))
    return (best.approximation, abs(ratio - best.numerator_A / best.denominator_m))


def analyze_frontier_node(
    node: CoverFrontierNode,
    max_certificate_steps: int = 1_000,
    bucket_scale: int = 100,
    suffix_length: int = 12,
    convergents: tuple[ConvergentWitness, ...] | None = None,
) -> FrontierClassAnalysis:
    trace = forced_trace_for_residue(
        node.residue,
        node.modulus_power,
        max_steps=max_certificate_steps,
        bucket_scale=bucket_scale,
    )
    density = Fraction(1, 1 << (node.modulus_power - 1))
    witnesses = convergents or log2_3_convergents(max_denominator=max(2, trace.m + 1))
    nearest, nearest_error = _nearest_convergent(trace.A, trace.m, witnesses)
    return FrontierClassAnalysis(
        residue=node.residue,
        modulus_power=node.modulus_power,
        m=trace.m,
        A=trace.A,
        debt_bucket=trace.bucket,
        debt=trace.m * log2(3) - trace.A,
        density_num=density.numerator,
        density_den=density.denominator,
        initial_ones=initial_ones(trace.word),
        suffix=trace.word[-suffix_length:],
        nearest_convergent=nearest,
        nearest_convergent_error=nearest_error,
    )


def analyze_cover_frontier(
    report: CertificateCoverReport,
    top_n: int = 20,
    max_certificate_steps: int = 1_000,
    bucket_scale: int = 100,
) -> FrontierAnalysisReport:
    """Rank frontier nodes by largest debt, then longest initial run of ones."""

    if top_n < 1:
        raise ValueError("top_n must be positive")
    max_denominator = max((node.modulus_power for node in report.frontier), default=2)
    witnesses = log2_3_convergents(max_denominator=max_denominator)
    analyses = [
        analyze_frontier_node(
            node,
            max_certificate_steps=max_certificate_steps,
            bucket_scale=bucket_scale,
            convergents=witnesses,
        )
        for node in report.frontier
    ]
    analyses.sort(
        key=lambda item: (
            item.debt_bucket,
            item.initial_ones,
            item.modulus_power,
            -item.residue,
        ),
        reverse=True,
    )
    return FrontierAnalysisReport(
        type="cover_frontier_analysis",
        status="finite_frontier_ranking_not_collatz_proof",
        frontier_classes=len(report.frontier),
        top=tuple(analyses[:top_n]),
    )
