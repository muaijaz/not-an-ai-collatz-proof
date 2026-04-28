"""Paparella-style nilpotency diagnostics for finite Collatz submatrices."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PaparellaTraceLevelReport:
    n: int
    matrix_size: int
    nonzero_edges_inside: int
    p_max_tested: int
    all_traces_zero: bool
    first_nonzero_trace_p: int | None
    nilpotent_by_escape_depth: bool
    max_escape_depth: int
    verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PaparellaNilpotencyReport:
    type: str
    status: str
    n_values: tuple[int, ...]
    levels: tuple[PaparellaTraceLevelReport, ...]
    theorem_note: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "n_values": list(self.n_values),
            "levels": [level.to_json_dict() for level in self.levels],
            "theorem_note": self.theorem_note,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _collatz_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def _level_report(n: int, p_max: int | None) -> PaparellaTraceLevelReport:
    if n < 3:
        raise ValueError("n must be at least 3")
    vertices = set(range(3, n + 1))
    image = {
        source: _collatz_step(source)
        for source in vertices
    }
    nonzero = sum(1 for target in image.values() if target in vertices)
    max_power = n if p_max is None else min(p_max, n)
    first_nonzero = None
    for p in range(1, max_power + 1):
        trace = 0
        for source in vertices:
            x = source
            alive = True
            for _ in range(p):
                x = image[x] if x in vertices else _collatz_step(x)
                if x not in vertices:
                    alive = False
                    break
            if alive and x == source:
                trace += 1
        if trace:
            first_nonzero = p
            break

    max_escape = 0
    cycle_found = False
    for source in vertices:
        seen: set[int] = set()
        x = source
        depth = 0
        while x in vertices:
            if x in seen:
                cycle_found = True
                break
            seen.add(x)
            x = image[x]
            depth += 1
            if depth > len(vertices):
                cycle_found = True
                break
        max_escape = max(max_escape, depth)
    nilpotent = (not cycle_found) and max_escape <= len(vertices)
    all_zero = first_nonzero is None
    return PaparellaTraceLevelReport(
        n=n,
        matrix_size=n - 2,
        nonzero_edges_inside=nonzero,
        p_max_tested=max_power,
        all_traces_zero=all_zero,
        first_nonzero_trace_p=first_nonzero,
        nilpotent_by_escape_depth=nilpotent,
        max_escape_depth=max_escape,
        verdict=(
            "C_n_nilpotent_on_tested_truncation"
            if all_zero and nilpotent
            else "nonzero_trace_or_escape_cycle_detected"
        ),
    )


def paparella_nilpotency_report(
    n_values: tuple[int, ...] = (64, 128, 256, 512, 1024),
    p_max: int = 200,
) -> PaparellaNilpotencyReport:
    """Check traces and escape-depth nilpotency for Paparella's ``C_n``."""

    levels = tuple(_level_report(n, p_max if n > p_max else None) for n in n_values)
    ok = all(level.all_traces_zero and level.nilpotent_by_escape_depth for level in levels)
    return PaparellaNilpotencyReport(
        type="paparella_nilpotency_trace_diagnostic",
        status=(
            "paparella_traces_zero_and_escape_nilpotent"
            if ok
            else "paparella_nonzero_trace_or_cycle_detected"
        ),
        n_values=n_values,
        levels=levels,
        theorem_note=(
            "Paparella Theorem 3 states that the aperiodic Collatz conjecture "
            "is equivalent to nilpotency of every finite C_n. This report is a "
            "finite diagnostic only."
        ),
    )
