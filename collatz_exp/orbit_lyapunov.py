"""Actual-orbit probes for running-debt Lyapunov candidates."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class BetaSweepConventionResult:
    convention: str
    beta: float
    total_steps: int
    nonnegative_steps: int
    fraction_nonnegative: float
    min_delta: float
    max_delta: float
    mean_delta: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrbitLyapunovBetaSweepReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_steps_per_orbit: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    beta_values: tuple[float, ...]
    conventions: tuple[str, ...]
    results: tuple[BetaSweepConventionResult, ...]
    sample_orbits: tuple[dict[str, Any], ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "max_steps_per_orbit": self.max_steps_per_orbit,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "beta_values": list(self.beta_values),
            "conventions": list(self.conventions),
            "results": [result.to_json_dict() for result in self.results],
            "sample_orbits": [dict(item) for item in self.sample_orbits],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def orbit_lyapunov_beta_sweep_report(
    sample_count: int = 1_000_000,
    beta_values: tuple[float, ...] = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0),
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
) -> OrbitLyapunovBetaSweepReport:
    """Sweep ``V_beta = log2(n) + beta*D_running`` on actual orbits.

    Two debt conventions are reported:
    - ``reset_at_source`` resets debt before stepping out of a tail state.
    - ``reset_at_target`` treats arrival at a tail state as a renewal and sets
      target debt to zero, making the convention closer to a state function.
    """

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")
    if max_steps_per_orbit < 1:
        raise ValueError("max_steps_per_orbit must be positive")
    betas = tuple(float(beta) for beta in beta_values)
    if not betas or any(beta <= 0.0 for beta in betas):
        raise ValueError("beta_values must be positive")

    conventions = ("reset_at_source", "reset_at_target")
    nonnegative = {(name, beta): 0 for name in conventions for beta in betas}
    sum_delta = {(name, beta): 0.0 for name in conventions for beta in betas}
    min_delta = {(name, beta): float("inf") for name in conventions for beta in betas}
    max_delta = {(name, beta): float("-inf") for name in conventions for beta in betas}
    log2_3 = math.log2(3.0)
    rng = random.Random(random_seed)
    completed = 0
    truncated = 0
    total_steps = 0
    sample_orbits: list[dict[str, Any]] = []

    for orbit_index in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        start = x
        debt_source = 0.0
        debt_target = 0.0
        steps = 0
        local_nonnegative = {name: 0 for name in conventions}
        local_max_delta = {name: float("-inf") for name in conventions}
        while x != 1 and steps < max_steps_per_orbit:
            source_is_tail = v2(x + 1) >= 2
            if source_is_tail:
                debt_source = 0.0
                debt_target = 0.0
            y, valuation = accelerated_step(x)
            # log2(y/x) = log2(3 + 1/x) - valuation.
            log_delta = math.log2(3.0 + 1.0 / x) - valuation
            debt_increment = valuation - log2_3

            next_debt_source = debt_source + debt_increment
            target_candidate = debt_target + debt_increment
            next_debt_target = 0.0 if v2(y + 1) >= 2 else target_candidate

            for beta in betas:
                delta_source = log_delta + beta * (next_debt_source - debt_source)
                key_source = ("reset_at_source", beta)
                sum_delta[key_source] += delta_source
                min_delta[key_source] = min(min_delta[key_source], delta_source)
                max_delta[key_source] = max(max_delta[key_source], delta_source)
                if delta_source >= 0.0:
                    nonnegative[key_source] += 1
                    local_nonnegative["reset_at_source"] += 1
                local_max_delta["reset_at_source"] = max(
                    local_max_delta["reset_at_source"],
                    delta_source,
                )

                delta_target = log_delta + beta * (next_debt_target - debt_target)
                key_target = ("reset_at_target", beta)
                sum_delta[key_target] += delta_target
                min_delta[key_target] = min(min_delta[key_target], delta_target)
                max_delta[key_target] = max(max_delta[key_target], delta_target)
                if delta_target >= 0.0:
                    nonnegative[key_target] += 1
                    local_nonnegative["reset_at_target"] += 1
                local_max_delta["reset_at_target"] = max(
                    local_max_delta["reset_at_target"],
                    delta_target,
                )

            debt_source = next_debt_source
            debt_target = next_debt_target
            x = y
            steps += 1
            total_steps += 1

        if x == 1:
            completed += 1
        else:
            truncated += 1
        if len(sample_orbits) < 20:
            sample_orbits.append(
                {
                    "index": orbit_index,
                    "start": start,
                    "steps": steps,
                    "ended_at": x,
                    "completed": x == 1,
                    "nonnegative_step_counts_all_betas": local_nonnegative,
                    "max_delta_all_betas": local_max_delta,
                }
            )

    results: list[BetaSweepConventionResult] = []
    for convention in conventions:
        for beta in betas:
            key = (convention, beta)
            results.append(
                BetaSweepConventionResult(
                    convention=convention,
                    beta=beta,
                    total_steps=total_steps,
                    nonnegative_steps=nonnegative[key],
                    fraction_nonnegative=nonnegative[key] / total_steps
                    if total_steps
                    else 0.0,
                    min_delta=min_delta[key],
                    max_delta=max_delta[key],
                    mean_delta=sum_delta[key] / total_steps if total_steps else 0.0,
                )
            )
    best_fraction = min(result.fraction_nonnegative for result in results)
    status = (
        "actual_orbit_beta_sweep_strong_beta_below_half_nonnegative"
        if best_fraction < 0.49
        else "actual_orbit_beta_sweep_near_coin_flip_no_per_step_lyapunov"
    )
    return OrbitLyapunovBetaSweepReport(
        type="actual_orbit_lyapunov_beta_sweep",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        max_steps_per_orbit=max_steps_per_orbit,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        beta_values=betas,
        conventions=conventions,
        results=tuple(results),
        sample_orbits=tuple(sample_orbits),
    )
