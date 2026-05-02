"""Phase-aware actual-orbit Lyapunov probes."""

from __future__ import annotations

import bisect
import heapq
import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .core import accelerated_step, v2

LOG2_3 = math.log2(3.0)
LOG2_3_OVER_2 = math.log2(1.5)

DEFAULT_ALPHA_GRID = (
    0.0,
    LOG2_3_OVER_2,
    2.0 * LOG2_3_OVER_2,
    0.5,
    1.0,
)
DEFAULT_BETA_GRID = (0.0, 1.0, 4.0, 8.0, 16.0, 32.0)
DEFAULT_GAMMA_DIFF_GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)


@dataclass(frozen=True)
class PhaseLyapunovParams:
    alpha: float
    beta: float
    gamma_diff: float
    gamma_R: float = 0.0
    gamma_PE: float | None = None

    def to_json_dict(self) -> dict[str, float]:
        gamma_pe = self.gamma_diff if self.gamma_PE is None else self.gamma_PE
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma_R": self.gamma_R,
            "gamma_PE": gamma_pe,
            "gamma_diff": gamma_pe - self.gamma_R,
        }


@dataclass(frozen=True)
class PhaseLyapunovStats:
    total_steps: int
    positive_steps: int
    nondecrease_steps: int
    fraction_positive: float | None
    fraction_nondecrease: float | None
    mean_delta: float | None
    max_delta: float | None
    conditional_mean_positive_delta: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseLyapunovEvaluation:
    params: PhaseLyapunovParams
    total: PhaseLyapunovStats
    phases: dict[str, PhaseLyapunovStats]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "params": self.params.to_json_dict(),
            "total": self.total.to_json_dict(),
            "phases": {
                phase: stats.to_json_dict() for phase, stats in self.phases.items()
            },
        }


@dataclass(frozen=True)
class PhaseLyapunovWorstEvent:
    n: int
    target: int
    R: int
    R_next: int
    valuation: int
    phase: str
    target_phase: str
    delta_V: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseLyapunovSearchReport:
    type: str
    status: str
    caveat: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_steps_per_orbit: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    alpha_grid: tuple[float, ...]
    beta_grid: tuple[float, ...]
    gamma_diff_grid: tuple[float, ...]
    grid_candidates_evaluated: int
    gamma_parametrization: str
    running_debt_convention: str
    V5_baseline: PhaseLyapunovEvaluation
    anchor_candidate_V0: PhaseLyapunovEvaluation
    best_grid_candidate: PhaseLyapunovEvaluation
    improvement_over_baseline: float | None
    worst_positive_events: tuple[PhaseLyapunovWorstEvent, ...]
    sample_orbits: tuple[dict[str, Any], ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "max_steps_per_orbit": self.max_steps_per_orbit,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "alpha_grid": list(self.alpha_grid),
            "beta_grid": list(self.beta_grid),
            "gamma_diff_grid": list(self.gamma_diff_grid),
            "grid_candidates_evaluated": self.grid_candidates_evaluated,
            "gamma_parametrization": self.gamma_parametrization,
            "running_debt_convention": self.running_debt_convention,
            "V5_baseline": self.V5_baseline.to_json_dict(),
            "V5_baseline_nondecrease_fraction": (
                self.V5_baseline.total.fraction_nondecrease
            ),
            "anchor_candidate_V0": self.anchor_candidate_V0.to_json_dict(),
            "best_grid_candidate": self.best_grid_candidate.to_json_dict(),
            "best_candidate_nondecrease_fraction": (
                self.best_grid_candidate.total.fraction_nondecrease
            ),
            "improvement_over_baseline": self.improvement_over_baseline,
            "worst_positive_events": [
                event.to_json_dict() for event in self.worst_positive_events
            ],
            "sample_orbits": [dict(item) for item in self.sample_orbits],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass
class _StepGroup:
    phase: str
    valuation: int
    delta_R: int
    delta_indicator_PE: int
    epsilons: list[float]


@dataclass(frozen=True)
class _PreparedStepGroup:
    phase: str
    valuation: int
    delta_R: int
    delta_indicator_PE: int
    count: int
    sum_epsilon: float
    max_epsilon: float
    sorted_epsilons: tuple[float, ...]
    prefix_sums: tuple[float, ...]


@dataclass(frozen=True)
class PhaseLyapunovOrbitSample:
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_steps_per_orbit: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    groups: tuple[_PreparedStepGroup, ...]
    sample_orbits: tuple[dict[str, Any], ...]


def _as_odd_start(rng: random.Random, start_min: int, start_max: int) -> int:
    x = rng.randrange(start_min, start_max)
    if x % 2 == 0:
        x += 1
        if x >= start_max:
            x -= 2
    return x


def _phase_from_R(R: int) -> str:
    return "tail_internal" if R >= 2 else "post_exit"


def _post_exit_indicator(R: int) -> int:
    return 0 if R >= 2 else 1


def _step_components(
    n: int,
    target: int,
    valuation: int,
) -> tuple[int, int, str, str, int, float]:
    R = v2(n + 1)
    R_next = v2(target + 1)
    phase = _phase_from_R(R)
    target_phase = _phase_from_R(R_next)
    delta_R = R_next - R
    delta_indicator = _post_exit_indicator(R_next) - _post_exit_indicator(R)
    epsilon = math.log2(1.0 + 1.0 / (3.0 * n))
    return R, R_next, phase, target_phase, delta_R, delta_indicator, epsilon


def collect_phase_lyapunov_orbits(
    *,
    sample_count: int = 100_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
) -> PhaseLyapunovOrbitSample:
    """Collect grouped accelerated-step features from sampled actual orbits."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")
    if max_steps_per_orbit < 1:
        raise ValueError("max_steps_per_orbit must be positive")

    rng = random.Random(random_seed)
    groups: dict[tuple[str, int, int, int], _StepGroup] = {}
    completed = 0
    truncated = 0
    total_steps = 0
    sample_orbits: list[dict[str, Any]] = []

    for orbit_index in range(sample_count):
        x = _as_odd_start(rng, start_min, start_max)
        start = x
        steps = 0
        local_tail_steps = 0
        local_post_exit_steps = 0
        while x != 1 and steps < max_steps_per_orbit:
            y, valuation = accelerated_step(x)
            (
                R,
                R_next,
                phase,
                _target_phase,
                delta_R,
                delta_indicator,
                epsilon,
            ) = _step_components(x, y, valuation)
            key = (phase, valuation, delta_R, delta_indicator)
            group = groups.get(key)
            if group is None:
                group = _StepGroup(
                    phase=phase,
                    valuation=valuation,
                    delta_R=delta_R,
                    delta_indicator_PE=delta_indicator,
                    epsilons=[],
                )
                groups[key] = group
            group.epsilons.append(epsilon)
            if phase == "tail_internal":
                local_tail_steps += 1
            else:
                local_post_exit_steps += 1
            x = y
            steps += 1
            total_steps += 1
            # Keep R/R_next in scope for linters and future debug probes.
            _ = (R, R_next)

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
                    "tail_internal_steps": local_tail_steps,
                    "post_exit_steps": local_post_exit_steps,
                }
            )

    prepared: list[_PreparedStepGroup] = []
    for group in groups.values():
        eps = sorted(group.epsilons)
        prefix = [0.0]
        for value in eps:
            prefix.append(prefix[-1] + value)
        prepared.append(
            _PreparedStepGroup(
                phase=group.phase,
                valuation=group.valuation,
                delta_R=group.delta_R,
                delta_indicator_PE=group.delta_indicator_PE,
                count=len(eps),
                sum_epsilon=prefix[-1],
                max_epsilon=eps[-1],
                sorted_epsilons=tuple(eps),
                prefix_sums=tuple(prefix),
            )
        )

    prepared.sort(
        key=lambda item: (
            item.phase,
            item.valuation,
            item.delta_R,
            item.delta_indicator_PE,
        )
    )
    return PhaseLyapunovOrbitSample(
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        max_steps_per_orbit=max_steps_per_orbit,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        groups=tuple(prepared),
        sample_orbits=tuple(sample_orbits),
    )


def _empty_stats() -> dict[str, float | int]:
    return {
        "total_steps": 0,
        "positive_steps": 0,
        "nondecrease_steps": 0,
        "sum_delta": 0.0,
        "max_delta": float("-inf"),
        "sum_positive_delta": 0.0,
    }


def _finalize_stats(raw: dict[str, float | int]) -> PhaseLyapunovStats:
    total_steps = int(raw["total_steps"])
    positive_steps = int(raw["positive_steps"])
    nondecrease_steps = int(raw["nondecrease_steps"])
    if total_steps == 0:
        return PhaseLyapunovStats(
            total_steps=0,
            positive_steps=0,
            nondecrease_steps=0,
            fraction_positive=None,
            fraction_nondecrease=None,
            mean_delta=None,
            max_delta=None,
            conditional_mean_positive_delta=None,
        )
    return PhaseLyapunovStats(
        total_steps=total_steps,
        positive_steps=positive_steps,
        nondecrease_steps=nondecrease_steps,
        fraction_positive=positive_steps / total_steps,
        fraction_nondecrease=nondecrease_steps / total_steps,
        mean_delta=float(raw["sum_delta"]) / total_steps,
        max_delta=float(raw["max_delta"]),
        conditional_mean_positive_delta=(
            float(raw["sum_positive_delta"]) / positive_steps
            if positive_steps
            else None
        ),
    )


def _evaluate_prepared_sample(
    sample: PhaseLyapunovOrbitSample,
    params: PhaseLyapunovParams,
) -> PhaseLyapunovEvaluation:
    by_phase = {
        "tail_internal": _empty_stats(),
        "post_exit": _empty_stats(),
    }
    total_raw = _empty_stats()
    gamma_diff = (
        params.gamma_diff
        if params.gamma_PE is None
        else params.gamma_PE - params.gamma_R
    )

    for group in sample.groups:
        base = (
            (1.0 - params.beta) * (LOG2_3 - group.valuation)
            + params.alpha * group.delta_R
            + gamma_diff * group.delta_indicator_PE
        )
        sum_delta = group.count * base + group.sum_epsilon
        max_delta = base + group.max_epsilon
        threshold = -base
        positive_index = bisect.bisect_right(group.sorted_epsilons, threshold)
        nondecrease_index = bisect.bisect_left(group.sorted_epsilons, threshold)
        positive_steps = group.count - positive_index
        nondecrease_steps = group.count - nondecrease_index
        positive_epsilon_sum = (
            group.prefix_sums[-1] - group.prefix_sums[positive_index]
        )
        positive_delta_sum = positive_steps * base + positive_epsilon_sum

        for raw in (total_raw, by_phase[group.phase]):
            raw["total_steps"] = int(raw["total_steps"]) + group.count
            raw["positive_steps"] = int(raw["positive_steps"]) + positive_steps
            raw["nondecrease_steps"] = (
                int(raw["nondecrease_steps"]) + nondecrease_steps
            )
            raw["sum_delta"] = float(raw["sum_delta"]) + sum_delta
            raw["max_delta"] = max(float(raw["max_delta"]), max_delta)
            raw["sum_positive_delta"] = (
                float(raw["sum_positive_delta"]) + positive_delta_sum
            )

    return PhaseLyapunovEvaluation(
        params=params,
        total=_finalize_stats(total_raw),
        phases={phase: _finalize_stats(raw) for phase, raw in by_phase.items()},
    )


def evaluate_phase_lyapunov(
    orbits: PhaseLyapunovOrbitSample,
    params: PhaseLyapunovParams | dict[str, float],
) -> dict[str, Any]:
    """Evaluate one phase-aware Lyapunov parameter set on collected orbits."""

    if isinstance(params, dict):
        params = PhaseLyapunovParams(
            alpha=float(params.get("alpha", 0.0)),
            beta=float(params.get("beta", 0.0)),
            gamma_diff=float(params.get("gamma_diff", 0.0)),
        )
    return _evaluate_prepared_sample(orbits, params).to_json_dict()


def search_phase_lyapunov(
    orbits: PhaseLyapunovOrbitSample,
    *,
    alpha_grid: Iterable[float] = DEFAULT_ALPHA_GRID,
    beta_grid: Iterable[float] = DEFAULT_BETA_GRID,
    gamma_diff_grid: Iterable[float] = DEFAULT_GAMMA_DIFF_GRID,
) -> dict[str, Any]:
    """Return the grid point minimizing non-decrease, then mean delta."""

    best: PhaseLyapunovEvaluation | None = None
    candidates = 0
    for alpha in alpha_grid:
        for beta in beta_grid:
            for gamma_diff in gamma_diff_grid:
                candidates += 1
                evaluation = _evaluate_prepared_sample(
                    orbits,
                    PhaseLyapunovParams(
                        alpha=float(alpha),
                        beta=float(beta),
                        gamma_diff=float(gamma_diff),
                    ),
                )
                if best is None:
                    best = evaluation
                    continue
                best_key = (
                    best.total.fraction_nondecrease
                    if best.total.fraction_nondecrease is not None
                    else float("inf"),
                    best.total.mean_delta
                    if best.total.mean_delta is not None
                    else float("inf"),
                    best.total.max_delta
                    if best.total.max_delta is not None
                    else float("inf"),
                )
                candidate_key = (
                    evaluation.total.fraction_nondecrease
                    if evaluation.total.fraction_nondecrease is not None
                    else float("inf"),
                    evaluation.total.mean_delta
                    if evaluation.total.mean_delta is not None
                    else float("inf"),
                    evaluation.total.max_delta
                    if evaluation.total.max_delta is not None
                    else float("inf"),
                )
                if candidate_key < best_key:
                    best = evaluation
    if best is None:
        raise ValueError("search grids must contain at least one candidate")
    return {
        "grid_candidates_evaluated": candidates,
        "best": best.to_json_dict(),
    }


def _delta_for_step(
    n: int,
    target: int,
    valuation: int,
    params: PhaseLyapunovParams,
) -> tuple[float, int, int, str, str]:
    R, R_next, phase, target_phase, delta_R, delta_indicator, epsilon = (
        _step_components(n, target, valuation)
    )
    gamma_diff = (
        params.gamma_diff
        if params.gamma_PE is None
        else params.gamma_PE - params.gamma_R
    )
    delta = (
        (1.0 - params.beta) * (LOG2_3 - valuation)
        + epsilon
        + params.alpha * delta_R
        + gamma_diff * delta_indicator
    )
    return delta, R, R_next, phase, target_phase


def _worst_positive_events(
    params: PhaseLyapunovParams,
    *,
    sample_count: int,
    start_min: int,
    start_max: int,
    random_seed: int,
    max_steps_per_orbit: int,
    limit: int = 5,
) -> tuple[PhaseLyapunovWorstEvent, ...]:
    rng = random.Random(random_seed)
    heap: list[tuple[float, int, PhaseLyapunovWorstEvent]] = []
    seen: set[tuple[int, int, int, int, int]] = set()
    order = 0
    for _ in range(sample_count):
        x = _as_odd_start(rng, start_min, start_max)
        steps = 0
        while x != 1 and steps < max_steps_per_orbit:
            y, valuation = accelerated_step(x)
            delta, R, R_next, phase, target_phase = _delta_for_step(
                x,
                y,
                valuation,
                params,
            )
            if delta > 0.0:
                key = (x, y, R, R_next, valuation)
                if key in seen:
                    x = y
                    steps += 1
                    continue
                seen.add(key)
                event = PhaseLyapunovWorstEvent(
                    n=x,
                    target=y,
                    R=R,
                    R_next=R_next,
                    valuation=valuation,
                    phase=phase,
                    target_phase=target_phase,
                    delta_V=delta,
                )
                item = (delta, order, event)
                if len(heap) < limit:
                    heapq.heappush(heap, item)
                elif delta > heap[0][0]:
                    heapq.heapreplace(heap, item)
                order += 1
            x = y
            steps += 1
    return tuple(
        item[2] for item in sorted(heap, key=lambda item: item[0], reverse=True)
    )


def _status_from_best(
    baseline: PhaseLyapunovEvaluation,
    best: PhaseLyapunovEvaluation,
) -> str:
    baseline_fraction = baseline.total.fraction_nondecrease
    best_fraction = best.total.fraction_nondecrease
    if best_fraction is None:
        return "phase_lyapunov_search_no_steps"
    if best_fraction == 0.0:
        return "phase_lyapunov_search_zero_nondecrease_on_sample"
    if best_fraction > 0.5:
        return "phase_lyapunov_search_best_above_half_investigate"
    if baseline_fraction is not None and best_fraction < baseline_fraction:
        return "phase_lyapunov_search_grid_improves_v5_baseline"
    return "phase_lyapunov_search_no_grid_improvement_over_v5_baseline"


def phase_lyapunov_search_report(
    *,
    sample_count: int = 100_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    alpha_grid: Iterable[float] = DEFAULT_ALPHA_GRID,
    beta_grid: Iterable[float] = DEFAULT_BETA_GRID,
    gamma_diff_grid: Iterable[float] = DEFAULT_GAMMA_DIFF_GRID,
) -> PhaseLyapunovSearchReport:
    """Search a small phase-aware Lyapunov family on sampled actual orbits."""

    alpha_values = tuple(float(value) for value in alpha_grid)
    beta_values = tuple(float(value) for value in beta_grid)
    gamma_values = tuple(float(value) for value in gamma_diff_grid)
    if not alpha_values or not beta_values or not gamma_values:
        raise ValueError("all search grids must be nonempty")

    sample = collect_phase_lyapunov_orbits(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
    )
    baseline = _evaluate_prepared_sample(
        sample,
        PhaseLyapunovParams(alpha=0.0, beta=16.0, gamma_diff=0.0),
    )
    anchor = _evaluate_prepared_sample(
        sample,
        PhaseLyapunovParams(alpha=LOG2_3_OVER_2, beta=0.0, gamma_diff=0.0),
    )
    search = search_phase_lyapunov(
        sample,
        alpha_grid=alpha_values,
        beta_grid=beta_values,
        gamma_diff_grid=gamma_values,
    )
    best = _evaluate_prepared_sample(
        sample,
        PhaseLyapunovParams(
            alpha=search["best"]["params"]["alpha"],
            beta=search["best"]["params"]["beta"],
            gamma_diff=search["best"]["params"]["gamma_diff"],
        ),
    )
    baseline_fraction = baseline.total.fraction_nondecrease
    best_fraction = best.total.fraction_nondecrease
    improvement = (
        baseline_fraction - best_fraction
        if baseline_fraction is not None and best_fraction is not None
        else None
    )
    worst_events = _worst_positive_events(
        best.params,
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
        limit=5,
    )
    return PhaseLyapunovSearchReport(
        type="phase_lyapunov_search",
        status=_status_from_best(baseline, best),
        caveat=(
            "Empirical search on a finite sampled orbit set and a modest "
            "parameter grid. A zero non-decrease fraction here would still "
            "require larger confirmation runs before any structural claim."
        ),
        sample_count=sample.sample_count,
        random_seed=sample.random_seed,
        start_min=sample.start_min,
        start_max=sample.start_max,
        max_steps_per_orbit=sample.max_steps_per_orbit,
        completed_orbits=sample.completed_orbits,
        truncated_orbits=sample.truncated_orbits,
        total_accelerated_steps=sample.total_accelerated_steps,
        alpha_grid=alpha_values,
        beta_grid=beta_values,
        gamma_diff_grid=gamma_values,
        grid_candidates_evaluated=int(search["grid_candidates_evaluated"]),
        gamma_parametrization=(
            "gamma_R fixed to 0; gamma_PE=gamma_diff, since adding a common "
            "constant to gamma_R and gamma_PE is degenerate with V's additive "
            "constant."
        ),
        running_debt_convention=(
            "V5 reset_at_source convention: D_running is reset before steps "
            "whose source has v2(n+1)>=2, and each step contributes "
            "a-log2(3) to the next state."
        ),
        V5_baseline=baseline,
        anchor_candidate_V0=anchor,
        best_grid_candidate=best,
        improvement_over_baseline=improvement,
        worst_positive_events=worst_events,
        sample_orbits=sample.sample_orbits,
    )
