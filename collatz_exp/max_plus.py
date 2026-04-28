"""Max-plus cycle-mean diagnostics for truncated accelerated Collatz graphs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import inf, log2
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class MaxPlusDebtReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    states: int
    edges: int
    max_cycle_mean_debt: float | None
    witness_residue: int | None
    positive_mean_detected: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _karp_max_cycle_mean(
    states: int,
    edges: tuple[tuple[int, int, float], ...],
) -> tuple[float, int] | None:
    if states == 0 or not edges:
        return None
    dp = [[-inf for _ in range(states)] for _ in range(states + 1)]
    for state in range(states):
        dp[0][state] = 0.0
    incoming: list[list[tuple[int, float]]] = [[] for _ in range(states)]
    for source, target, weight in edges:
        incoming[target].append((source, weight))
    for length in range(1, states + 1):
        for target in range(states):
            best = -inf
            for source, weight in incoming[target]:
                value = dp[length - 1][source] + weight
                if value > best:
                    best = value
            dp[length][target] = best

    best_mean = -inf
    best_state = 0
    for state in range(states):
        if dp[states][state] == -inf:
            continue
        worst_prefix = inf
        for length in range(states):
            if dp[length][state] == -inf:
                continue
            mean = (dp[states][state] - dp[length][state]) / (states - length)
            if mean < worst_prefix:
                worst_prefix = mean
        if worst_prefix > best_mean:
            best_mean = worst_prefix
            best_state = state
    if best_mean == -inf:
        return None
    return best_mean, best_state


def max_plus_debt_report(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
) -> MaxPlusDebtReport:
    """Compute a finite max-plus cycle mean for debt ``log2(3) - a``.

    The graph vertices are odd residues modulo ``2^modulus_power``. Each
    sampled binary lift contributes one accelerated transition edge weighted by
    the one-step debt contribution. Parallel edges are collapsed by keeping the
    largest weight, as max-plus paths only care about the most dangerous edge.
    """

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")

    residues = tuple(range(1, 1 << modulus_power, 2))
    index = {residue: i for i, residue in enumerate(residues)}
    edge_weights: dict[tuple[int, int], float] = {}
    lift_count = 1 << sample_lift_power
    for residue in residues:
        source = index[residue]
        for lift in range(lift_count):
            n = residue + (lift << modulus_power)
            landing, valuation = accelerated_step(n)
            target = index[landing % (1 << modulus_power)]
            weight = log2(3) - valuation
            key = (source, target)
            if weight > edge_weights.get(key, -inf):
                edge_weights[key] = weight

    edges = tuple(
        (source, target, weight)
        for (source, target), weight in edge_weights.items()
    )
    result = _karp_max_cycle_mean(len(residues), edges)
    if result is None:
        mean = None
        witness = None
    else:
        mean, state = result
        witness = residues[state]
    return MaxPlusDebtReport(
        type="truncated_max_plus_debt_cycle_mean",
        status="finite_max_plus_quotient_not_collatz_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        states=len(residues),
        edges=len(edges),
        max_cycle_mean_debt=mean,
        witness_residue=witness,
        positive_mean_detected=False if mean is None else mean > 0,
    )
