"""TDA diagnostics for renewal-scale Collatz orbit data."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class H1PersistenceSummary:
    embedding: str
    points: int
    h1_features: int | None
    top_h1_persistence: float | None
    finite_h1_features: int | None
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrbitRenewalTDAReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    tda_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    reservoir_points: int
    r_drop_events_seen: int
    r_drop_filter: str
    null_replicates: int
    standardize_embeddings: bool
    mean_delta_log2: float | None
    variance_delta_log2: float | None
    fraction_nonnegative_delta_log2: float | None
    fraction_delta_le_minus_10: float | None
    min_delta_log2: float | None
    max_delta_log2: float | None
    r_drop_h1: H1PersistenceSummary
    magnitude_delta_h1: H1PersistenceSummary
    magnitude_delta_null_h1: tuple[H1PersistenceSummary, ...]
    magnitude_delta_null_top_h1_mean: float | None
    magnitude_delta_null_top_h1_max: float | None
    tda_backend: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "tda_seed": self.tda_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "reservoir_points": self.reservoir_points,
            "r_drop_events_seen": self.r_drop_events_seen,
            "r_drop_filter": self.r_drop_filter,
            "null_replicates": self.null_replicates,
            "standardize_embeddings": self.standardize_embeddings,
            "mean_delta_log2": self.mean_delta_log2,
            "variance_delta_log2": self.variance_delta_log2,
            "fraction_nonnegative_delta_log2": self.fraction_nonnegative_delta_log2,
            "fraction_delta_le_minus_10": self.fraction_delta_le_minus_10,
            "min_delta_log2": self.min_delta_log2,
            "max_delta_log2": self.max_delta_log2,
            "r_drop_h1": self.r_drop_h1.to_json_dict(),
            "magnitude_delta_h1": self.magnitude_delta_h1.to_json_dict(),
            "magnitude_delta_null_h1": [
                item.to_json_dict() for item in self.magnitude_delta_null_h1
            ],
            "magnitude_delta_null_top_h1_mean": (
                self.magnitude_delta_null_top_h1_mean
            ),
            "magnitude_delta_null_top_h1_max": self.magnitude_delta_null_top_h1_max,
            "tda_backend": self.tda_backend,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _reservoir_add(
    reservoir: list[tuple[float, float]],
    item: tuple[float, float],
    seen: int,
    max_points: int,
    rng: random.Random,
) -> None:
    if len(reservoir) < max_points:
        reservoir.append(item)
        return
    index = rng.randrange(seen)
    if index < max_points:
        reservoir[index] = item


def _standardized_points(
    points: list[tuple[float, float]],
    standardize: bool,
) -> list[tuple[float, float]]:
    if not standardize or not points:
        return points
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    var_x = sum((value - mean_x) ** 2 for value in xs) / len(xs)
    var_y = sum((value - mean_y) ** 2 for value in ys) / len(ys)
    scale_x = math.sqrt(var_x) if var_x > 0.0 else 1.0
    scale_y = math.sqrt(var_y) if var_y > 0.0 else 1.0
    return [
        ((x - mean_x) / scale_x, (y - mean_y) / scale_y)
        for x, y in points
    ]


def _h1_summary(
    points: list[tuple[float, float]],
    embedding: str,
    *,
    standardize: bool,
    run_tda: bool,
    persistence_threshold: float,
) -> H1PersistenceSummary:
    if not run_tda:
        return H1PersistenceSummary(
            embedding=embedding,
            points=len(points),
            h1_features=None,
            top_h1_persistence=None,
            finite_h1_features=None,
            status="tda_not_requested",
        )
    if len(points) < 4:
        return H1PersistenceSummary(
            embedding=embedding,
            points=len(points),
            h1_features=0,
            top_h1_persistence=0.0,
            finite_h1_features=0,
            status="too_few_points",
        )
    try:
        import numpy as np
        from ripser import ripser
    except Exception:
        return H1PersistenceSummary(
            embedding=embedding,
            points=len(points),
            h1_features=None,
            top_h1_persistence=None,
            finite_h1_features=None,
            status="ripser_unavailable",
        )

    array = np.asarray(_standardized_points(points, standardize), dtype=float)
    result = ripser(array, maxdim=1)
    h1 = result["dgms"][1]
    finite = [
        (float(birth), float(death))
        for birth, death in h1
        if math.isfinite(float(death))
    ]
    persistences = [
        death - birth
        for birth, death in finite
        if death - birth > persistence_threshold
    ]
    return H1PersistenceSummary(
        embedding=embedding,
        points=len(points),
        h1_features=len(persistences),
        top_h1_persistence=max(persistences) if persistences else 0.0,
        finite_h1_features=len(finite),
        status="ok",
    )


def orbit_renewal_tda_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    tda_seed: int = 1,
    max_steps_per_orbit: int = 10_000,
    max_points: int = 5_000,
    null_replicates: int = 8,
    standardize_embeddings: bool = True,
    run_tda: bool = True,
    persistence_threshold: float = 1e-9,
) -> OrbitRenewalTDAReport:
    """Sample renewal events and compute H1 persistence for two embeddings."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if max_points < 1:
        raise ValueError("max_points must be positive")
    if null_replicates < 0:
        raise ValueError("null_replicates must be nonnegative")

    orbit_rng = random.Random(random_seed)
    reservoir_rng = random.Random(tda_seed)
    null_rng = random.Random(tda_seed + 1)
    r_drop_points: list[tuple[float, float]] = []
    magnitude_delta_points: list[tuple[float, float]] = []

    completed = 0
    truncated = 0
    total_steps = 0
    total_excursions = 0
    r_drop_events_seen = 0
    sum_delta = 0.0
    sum_delta_sq = 0.0
    nonnegative = 0
    le_minus_10 = 0
    min_delta = float("inf")
    max_delta = float("-inf")

    for _ in range(sample_count):
        x = orbit_rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        source_tail_depth = v2(excursion_start + 1)
        while x != 1 and steps < max_steps_per_orbit:
            x, _valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            if x == 1 or v2(x + 1) >= 2:
                target_tail_depth = v2(x + 1) if x > 0 else 0
                delta = math.log2(x) - math.log2(excursion_start)
                total_excursions += 1
                sum_delta += delta
                sum_delta_sq += delta * delta
                min_delta = min(min_delta, delta)
                max_delta = max(max_delta, delta)
                if delta >= 0.0:
                    nonnegative += 1
                if delta <= -10.0:
                    le_minus_10 += 1

                md_item = (math.log2(excursion_start), delta)
                if source_tail_depth >= 2 and target_tail_depth >= 2:
                    r_drop_events_seen += 1
                    r_item = (float(source_tail_depth), float(target_tail_depth))
                    _reservoir_add(
                        r_drop_points,
                        r_item,
                        r_drop_events_seen,
                        max_points,
                        reservoir_rng,
                    )
                _reservoir_add(
                    magnitude_delta_points,
                    md_item,
                    total_excursions,
                    max_points,
                    reservoir_rng,
                )
                excursion_start = x
                source_tail_depth = target_tail_depth
        if x == 1:
            completed += 1
        else:
            truncated += 1

    if total_excursions:
        mean_delta = sum_delta / total_excursions
        variance_delta = max(0.0, sum_delta_sq / total_excursions - mean_delta**2)
        fraction_nonnegative = nonnegative / total_excursions
        fraction_le_minus_10 = le_minus_10 / total_excursions
        min_delta_value = min_delta
        max_delta_value = max_delta
    else:
        mean_delta = None
        variance_delta = None
        fraction_nonnegative = None
        fraction_le_minus_10 = None
        min_delta_value = None
        max_delta_value = None

    r_drop_h1 = _h1_summary(
        r_drop_points,
        "tail_depth_pair",
        standardize=standardize_embeddings,
        run_tda=run_tda,
        persistence_threshold=persistence_threshold,
    )
    magnitude_delta_h1 = _h1_summary(
        magnitude_delta_points,
        "log_source_delta",
        standardize=standardize_embeddings,
        run_tda=run_tda,
        persistence_threshold=persistence_threshold,
    )

    null_summaries: list[H1PersistenceSummary] = []
    if magnitude_delta_points:
        magnitudes = [point[0] for point in magnitude_delta_points]
        deltas = [point[1] for point in magnitude_delta_points]
        for index in range(null_replicates):
            shuffled = list(deltas)
            null_rng.shuffle(shuffled)
            null_points = list(zip(magnitudes, shuffled))
            null_summaries.append(
                _h1_summary(
                    null_points,
                    f"log_source_delta_permutation_null_{index}",
                    standardize=standardize_embeddings,
                    run_tda=run_tda,
                    persistence_threshold=persistence_threshold,
                )
            )

    null_top_values = [
        item.top_h1_persistence
        for item in null_summaries
        if item.top_h1_persistence is not None
    ]
    status = (
        "r_drop_has_no_sampled_h1_features"
        if r_drop_h1.h1_features == 0
        else "r_drop_has_sampled_h1_features"
        if r_drop_h1.h1_features is not None
        else r_drop_h1.status
    )
    return OrbitRenewalTDAReport(
        type="orbit_renewal_tda",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        tda_seed=tda_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        total_excursions=total_excursions,
        reservoir_points=len(r_drop_points),
        r_drop_events_seen=r_drop_events_seen,
        r_drop_filter="source_tail_depth>=2_and_target_tail_depth>=2",
        null_replicates=null_replicates,
        standardize_embeddings=standardize_embeddings,
        mean_delta_log2=mean_delta,
        variance_delta_log2=variance_delta,
        fraction_nonnegative_delta_log2=fraction_nonnegative,
        fraction_delta_le_minus_10=fraction_le_minus_10,
        min_delta_log2=min_delta_value,
        max_delta_log2=max_delta_value,
        r_drop_h1=r_drop_h1,
        magnitude_delta_h1=magnitude_delta_h1,
        magnitude_delta_null_h1=tuple(null_summaries),
        magnitude_delta_null_top_h1_mean=(
            sum(null_top_values) / len(null_top_values) if null_top_values else None
        ),
        magnitude_delta_null_top_h1_max=(
            max(null_top_values) if null_top_values else None
        ),
        tda_backend="ripser" if run_tda else "not_requested",
    )
