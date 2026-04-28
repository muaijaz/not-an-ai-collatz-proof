"""Finite diagnostics inspired by Hercher's reciprocal-sum cycle bounds."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class HercherKBucketReport:
    bucket: str
    segments: int
    max_T_times_n: float
    analytic_ceiling: float | None
    ceiling_gap: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HercherTNiReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_shortcut_steps: int
    local_minimum_segments: int
    max_T_times_n: float | None
    mean_T_times_n: float | None
    p95_T_times_n: float | None
    p99_T_times_n: float | None
    universal_bound_3_passes: bool
    hercher_remark_7_note: str
    hercher_97_54_note: str
    buckets: tuple[HercherKBucketReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_shortcut_steps": self.total_shortcut_steps,
            "local_minimum_segments": self.local_minimum_segments,
            "max_T_times_n": self.max_T_times_n,
            "mean_T_times_n": self.mean_T_times_n,
            "p95_T_times_n": self.p95_T_times_n,
            "p99_T_times_n": self.p99_T_times_n,
            "universal_bound_3_passes": self.universal_bound_3_passes,
            "hercher_remark_7_note": self.hercher_remark_7_note,
            "hercher_97_54_note": self.hercher_97_54_note,
            "buckets": [bucket.to_json_dict() for bucket in self.buckets],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _shortcut_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def _quantile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    index = q * (len(sorted_values) - 1)
    lo = int(math.floor(index))
    hi = int(math.ceil(index))
    if lo == hi:
        return sorted_values[lo]
    weight = index - lo
    return sorted_values[lo] * (1.0 - weight) + sorted_values[hi] * weight


def _analytic_ceiling(k: int | None) -> float | None:
    if k is None:
        return 3.0
    return 3.0 * (1.0 - (2.0 / 3.0) ** k)


def hercher_t_ni_report(
    sample_count: int = 5_000,
    start_min: int = 10**5,
    start_max: int = 10**6,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    exact_bucket_max_k: int = 5,
) -> HercherTNiReport:
    """Sample local-minimum odd-run segments and compute Hercher's ``T(n_i)``."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")

    rng = random.Random(random_seed)
    completed = 0
    truncated = 0
    total_steps = 0
    values: list[float] = []
    bucket_values: dict[str, list[float]] = defaultdict(list)

    for _ in range(sample_count):
        n = rng.randrange(start_min, start_max)
        if n % 2 == 0:
            n += 1
            if n >= start_max:
                n -= 2
        steps = 0
        x = n
        while x != 1 and steps < max_steps_per_orbit:
            if x % 2 == 1:
                start = x
                T = Fraction(0, 1)
                k = 0
                while x % 2 == 1 and x != 1 and steps < max_steps_per_orbit:
                    T += Fraction(1, x)
                    x = _shortcut_step(x)
                    steps += 1
                    total_steps += 1
                    k += 1
                if k:
                    value = float(T * start)
                    values.append(value)
                    key = f"k={k}" if k <= exact_bucket_max_k else f"k>{exact_bucket_max_k}"
                    bucket_values[key].append(value)
            else:
                x = _shortcut_step(x)
                steps += 1
                total_steps += 1
        if x == 1:
            completed += 1
        else:
            truncated += 1

    sorted_values = sorted(values)
    buckets: list[HercherKBucketReport] = []
    def bucket_sort_key(key: str) -> int:
        return exact_bucket_max_k + 1 if key.startswith("k>") else int(key.split("=")[1])

    for key in sorted(bucket_values, key=bucket_sort_key):
        bucket = bucket_values[key]
        if key.startswith("k>"):
            ceiling = 3.0
        else:
            ceiling = _analytic_ceiling(int(key.split("=")[1]))
        max_value = max(bucket)
        buckets.append(
            HercherKBucketReport(
                bucket=key,
                segments=len(bucket),
                max_T_times_n=max_value,
                analytic_ceiling=ceiling,
                ceiling_gap=None if ceiling is None else ceiling - max_value,
            )
        )

    max_value = max(sorted_values) if sorted_values else None
    passes = max_value is not None and max_value < 3.0
    return HercherTNiReport(
        type="hercher_t_ni_reciprocal_sum_diagnostic",
        status=(
            "hercher_universal_Tn_bound_passes_sample"
            if passes
            else "hercher_universal_Tn_bound_failed_or_no_segments"
        ),
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_shortcut_steps=total_steps,
        local_minimum_segments=len(values),
        max_T_times_n=max_value,
        mean_T_times_n=sum(values) / len(values) if values else None,
        p95_T_times_n=_quantile(sorted_values, 0.95),
        p99_T_times_n=_quantile(sorted_values, 0.99),
        universal_bound_3_passes=passes,
        hercher_remark_7_note=(
            "Directly testable sampled form of Hercher Remark 7: "
            "T(n_i) < 3/n_i, equivalently T(n_i)*n_i < 3."
        ),
        hercher_97_54_note=(
            "Hercher's 97/54 bound applies to hypothetical cycle members with "
            "n_i >= X0 (currently X0=2^68 in the paper context); it is not "
            "directly testable on small sampled orbits."
        ),
        buckets=tuple(buckets),
    )
