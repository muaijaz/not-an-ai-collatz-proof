"""Lift-realizability checks for symbolic quotient valuation cycles."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log2
from typing import Any

from .constrained_jsr import LegalResidueEdge, legal_residue_edges
from .core import apply_word, valuation_word
from .cycles import classify_cycle_word


@dataclass(frozen=True)
class LiftedCycleCheck:
    word: tuple[int, ...]
    period: int
    total_A: int
    total_debt: float
    quotient_start_residue: int
    cylinder_power: int
    closure_precision_power: int
    cylinder_residue_count: int
    closes_mod_power_count: int
    example_residue: int | None
    cycle_classification: str
    cycle_value: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["word"] = list(self.word)
        return data


@dataclass(frozen=True)
class LiftRealizabilityReport:
    type: str
    status: str
    modulus_power: int
    max_valuation: int
    max_period: int
    quotient_words_found: int
    checks: tuple[LiftedCycleCheck, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "modulus_power": self.modulus_power,
            "max_valuation": self.max_valuation,
            "max_period": self.max_period,
            "quotient_words_found": self.quotient_words_found,
            "checks": [check.to_json_dict() for check in self.checks],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def word_cylinder_residues(
    word: tuple[int, ...],
    precision_power: int | None = None,
    max_scan_power: int = 24,
) -> tuple[int, ...]:
    """Return residues modulo ``2^precision_power`` realizing an exact word."""

    if any(valuation < 1 for valuation in word):
        raise ValueError("valuation words must contain positive integers")
    if precision_power is None:
        precision_power = sum(word) + 1
    if precision_power < 1:
        raise ValueError("precision_power must be positive")
    if precision_power > max_scan_power:
        raise ValueError("precision_power exceeds max_scan_power")
    modulus = 1 << precision_power
    return tuple(
        residue
        for residue in range(1, modulus, 2)
        if valuation_word(residue, len(word)) == word
    )


def exact_word_closures_mod_power(
    word: tuple[int, ...],
    modulus_power: int,
    precision_power: int | None = None,
) -> tuple[int, ...]:
    """Return exact word-cylinder residues whose landing closes modulo ``2^k``."""

    if precision_power is None:
        precision_power = max(sum(word) + 1, modulus_power + sum(word) + 1)
    modulus = 1 << modulus_power
    closing: list[int] = []
    for residue in word_cylinder_residues(word, precision_power):
        landing = apply_word(residue, word)
        if landing % modulus == residue % modulus:
            closing.append(residue)
    return tuple(closing)


def _adjacency_by_source(
    edges: tuple[LegalResidueEdge, ...],
) -> dict[int, tuple[LegalResidueEdge, ...]]:
    buckets: dict[int, list[LegalResidueEdge]] = {}
    for edge in edges:
        buckets.setdefault(edge.source, []).append(edge)
    return {
        source: tuple(
            sorted(
                values,
                key=lambda edge: (edge.valuation, edge.target),
            )
        )
        for source, values in buckets.items()
    }


def quotient_closed_words(
    modulus_power: int,
    max_valuation: int,
    max_period: int,
    max_words: int = 200,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Enumerate closed valuation words in the finite legal residue quotient."""

    if max_period < 1:
        raise ValueError("max_period must be positive")
    edges = legal_residue_edges(modulus_power, max_valuation)
    adjacency = _adjacency_by_source(edges)
    found: dict[tuple[int, ...], int] = {}
    for edge in edges:
        if edge.source == edge.target:
            found.setdefault((edge.valuation,), edge.source)

    def walk(start: int, current: int, word: tuple[int, ...]) -> None:
        if len(found) >= max_words:
            return
        if word and current == start:
            found.setdefault(word, start)
        if len(word) >= max_period:
            return
        for edge in adjacency.get(current, ()):
            walk(start, edge.target, (*word, edge.valuation))

    for start in sorted(adjacency):
        walk(start, start, ())
        if len(found) >= max_words:
            break
    return tuple((start, word) for word, start in found.items())


def lift_realizability_report(
    modulus_power: int = 6,
    max_valuation: int = 6,
    max_period: int = 8,
    top_n: int = 12,
    max_words: int = 400,
) -> LiftRealizabilityReport:
    """Check whether high-debt quotient cycles survive exact word lifting."""

    closed = quotient_closed_words(
        modulus_power=modulus_power,
        max_valuation=max_valuation,
        max_period=max_period,
        max_words=max_words,
    )
    ranked = sorted(
        closed,
        key=lambda item: (len(item[1]) * log2(3) - sum(item[1]), -len(item[1])),
        reverse=True,
    )
    checks: list[LiftedCycleCheck] = []
    for start, word in ranked[:top_n]:
        total_A = sum(word)
        cylinder_power = total_A + 1
        closure_precision_power = max(cylinder_power, modulus_power + total_A + 1)
        residues = word_cylinder_residues(word, precision_power=cylinder_power)
        closings = exact_word_closures_mod_power(
            word,
            modulus_power=modulus_power,
            precision_power=closure_precision_power,
        )
        classification = classify_cycle_word(word)
        checks.append(
            LiftedCycleCheck(
                word=word,
                period=len(word),
                total_A=total_A,
                total_debt=len(word) * log2(3) - total_A,
                quotient_start_residue=start,
                cylinder_power=cylinder_power,
                closure_precision_power=closure_precision_power,
                cylinder_residue_count=len(residues),
                closes_mod_power_count=len(closings),
                example_residue=None if not closings else closings[0],
                cycle_classification=classification.kind,
                cycle_value=str(classification.value),
            )
        )
    return LiftRealizabilityReport(
        type="quotient_cycle_lift_realizability",
        status="finite_lift_realizability_not_collatz_proof",
        modulus_power=modulus_power,
        max_valuation=max_valuation,
        max_period=max_period,
        quotient_words_found=len(closed),
        checks=tuple(checks),
    )
