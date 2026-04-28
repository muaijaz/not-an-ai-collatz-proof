"""Empirical checks for Tao's Syracuse random variables."""

from __future__ import annotations

import json
import math
import cmath
import random
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class TaoSyracLevelReport:
    n: int
    modulus: int
    theoretical_support: int
    nth_iterate_samples: int
    all_iterate_samples: int
    tv_nth_iterate_to_tao: float
    tv_all_iterates_to_tao: float
    tao_distribution: dict[str, float]
    empirical_nth_iterate_distribution: dict[str, float]
    empirical_all_iterates_distribution: dict[str, float]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaoSyracOscillationReport:
    m: int
    n: int
    tao_oscillation: float
    empirical_nth_iterate_oscillation: float
    empirical_all_iterates_oscillation: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaoSyracEmpiricalReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_n: int
    max_steps_per_orbit: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    max_tv_nth_iterate_to_tao: float | None
    max_tv_all_iterates_to_tao: float | None
    level_reports: tuple[TaoSyracLevelReport, ...]
    oscillation_reports: tuple[TaoSyracOscillationReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "max_n": self.max_n,
            "max_steps_per_orbit": self.max_steps_per_orbit,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "max_tv_nth_iterate_to_tao": self.max_tv_nth_iterate_to_tao,
            "max_tv_all_iterates_to_tao": self.max_tv_all_iterates_to_tao,
            "level_reports": [item.to_json_dict() for item in self.level_reports],
            "oscillation_reports": [
                item.to_json_dict() for item in self.oscillation_reports
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TaoCharacteristicTopFrequency:
    xi: int
    tao_abs: float
    empirical_abs: float
    abs_difference: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaoCharacteristicLevelReport:
    n: int
    modulus: int
    frequencies_checked: int
    empirical_samples: int
    tao_max_abs: float
    tao_max_xi: int
    empirical_max_abs: float
    empirical_max_xi: int
    max_abs_difference: float
    mean_abs_difference: float
    top_frequencies_by_tao_abs: tuple[TaoCharacteristicTopFrequency, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "modulus": self.modulus,
            "frequencies_checked": self.frequencies_checked,
            "empirical_samples": self.empirical_samples,
            "tao_max_abs": self.tao_max_abs,
            "tao_max_xi": self.tao_max_xi,
            "empirical_max_abs": self.empirical_max_abs,
            "empirical_max_xi": self.empirical_max_xi,
            "max_abs_difference": self.max_abs_difference,
            "mean_abs_difference": self.mean_abs_difference,
            "top_frequencies_by_tao_abs": [
                item.to_json_dict() for item in self.top_frequencies_by_tao_abs
            ],
        }


@dataclass(frozen=True)
class TaoCharacteristicDecayReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_n: int
    completed_orbits: int
    truncated_orbits: int
    empirical_steps_used: int
    fitted_tao_power_exponent: float | None
    fitted_empirical_power_exponent: float | None
    level_reports: tuple[TaoCharacteristicLevelReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "max_n": self.max_n,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "empirical_steps_used": self.empirical_steps_used,
            "fitted_tao_power_exponent": self.fitted_tao_power_exponent,
            "fitted_empirical_power_exponent": self.fitted_empirical_power_exponent,
            "level_reports": [item.to_json_dict() for item in self.level_reports],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def tao_syrac_distributions(max_n: int) -> list[list[Fraction]]:
    """Return Tao's Syrac(Z/3^n Z) distributions for ``0 <= n <= max_n``."""

    if max_n < 0:
        raise ValueError("max_n must be nonnegative")
    distributions: list[list[Fraction]] = [[Fraction(1, 1)]]
    for level in range(max_n):
        previous = distributions[-1]
        previous_modulus = 3**level
        modulus = 3 ** (level + 1)
        period = 2 * previous_modulus
        denominator = Fraction(1, 1) - Fraction(1, 2**period)
        current = [Fraction(0, 1) for _ in range(modulus)]
        powers = [(a, 1 << a, pow(2, a, 3)) for a in range(1, period + 1)]
        for x in range(modulus):
            mass = Fraction(0, 1)
            for a, power2, power2_mod3 in powers:
                if (power2_mod3 * (x % 3)) % 3 != 1:
                    continue
                previous_x = ((power2 * x - 1) // 3) % previous_modulus
                mass += Fraction(1, 2**a) * previous[previous_x]
            current[x] = mass / denominator
        distributions.append(current)
    return distributions


def _distribution_from_counts(counts: list[int]) -> list[float]:
    total = sum(counts)
    if total == 0:
        return [0.0 for _ in counts]
    return [count / total for count in counts]


def _tv_distance(left: list[float], right: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(left, right))


def _oscillation(distribution: list[float], m: int, n: int) -> float:
    if not 1 <= m <= n:
        raise ValueError("expected 1 <= m <= n")
    modulus = 3**n
    coarse_modulus = 3**m
    if len(distribution) != modulus:
        raise ValueError("distribution length must be 3^n")
    class_masses = [0.0 for _ in range(coarse_modulus)]
    for y, value in enumerate(distribution):
        class_masses[y % coarse_modulus] += value
    expected_factor = 1.0 / (3 ** (n - m))
    return sum(
        abs(value - expected_factor * class_masses[y % coarse_modulus])
        for y, value in enumerate(distribution)
    )


def _sparse_distribution(distribution: list[float]) -> dict[str, float]:
    return {
        str(index): value
        for index, value in enumerate(distribution)
        if value != 0.0
    }


def _characteristic_abs_by_frequency(
    distribution: list[float],
    modulus: int,
) -> dict[int, float]:
    result: dict[int, float] = {}
    for xi in range(1, modulus):
        if xi % 3 == 0:
            continue
        total = 0.0j
        for y, probability in enumerate(distribution):
            if probability:
                total += probability * cmath.exp(-2j * math.pi * xi * y / modulus)
        result[xi] = abs(total)
    return result


def _fit_power_decay(levels: list[tuple[int, float]]) -> float | None:
    points = [(math.log(n), math.log(value)) for n, value in levels if n > 1 and value > 0]
    if len(points) < 2:
        return None
    mean_x = sum(point[0] for point in points) / len(points)
    mean_y = sum(point[1] for point in points) / len(points)
    denominator = sum((x - mean_x) ** 2 for x, _y in points)
    if denominator == 0.0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator
    return -slope


def tao_syrac_empirical_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_n: int = 4,
    max_steps_per_orbit: int = 10_000,
    oscillation_pairs: tuple[tuple[int, int], ...] = ((1, 2), (1, 3), (2, 3), (2, 4)),
) -> TaoSyracEmpiricalReport:
    """Compare empirical Syracuse residues with Tao's recursive random variables."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if max_n < 1:
        raise ValueError("max_n must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")

    theoretical_fraction = tao_syrac_distributions(max_n)
    theoretical = [
        [float(value) for value in distribution]
        for distribution in theoretical_fraction
    ]
    nth_counts = [[0 for _ in range(3**n)] for n in range(max_n + 1)]
    all_counts = [[0 for _ in range(3**n)] for n in range(max_n + 1)]

    rng = random.Random(random_seed)
    completed = 0
    truncated = 0
    total_steps = 0
    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        while x != 1 and steps < max_steps_per_orbit:
            x, _valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            for n in range(1, max_n + 1):
                all_counts[n][x % (3**n)] += 1
            if steps <= max_n:
                nth_counts[steps][x % (3**steps)] += 1
        if x == 1:
            completed += 1
        else:
            truncated += 1

    level_reports: list[TaoSyracLevelReport] = []
    tv_nth_values: list[float] = []
    tv_all_values: list[float] = []
    empirical_nth_by_level: dict[int, list[float]] = {}
    empirical_all_by_level: dict[int, list[float]] = {}
    for n in range(1, max_n + 1):
        empirical_nth = _distribution_from_counts(nth_counts[n])
        empirical_all = _distribution_from_counts(all_counts[n])
        empirical_nth_by_level[n] = empirical_nth
        empirical_all_by_level[n] = empirical_all
        tao = theoretical[n]
        tv_nth = _tv_distance(empirical_nth, tao)
        tv_all = _tv_distance(empirical_all, tao)
        tv_nth_values.append(tv_nth)
        tv_all_values.append(tv_all)
        level_reports.append(
            TaoSyracLevelReport(
                n=n,
                modulus=3**n,
                theoretical_support=sum(1 for value in tao if value != 0.0),
                nth_iterate_samples=sum(nth_counts[n]),
                all_iterate_samples=sum(all_counts[n]),
                tv_nth_iterate_to_tao=tv_nth,
                tv_all_iterates_to_tao=tv_all,
                tao_distribution=_sparse_distribution(tao),
                empirical_nth_iterate_distribution=_sparse_distribution(empirical_nth),
                empirical_all_iterates_distribution=_sparse_distribution(empirical_all),
            )
        )

    oscillations: list[TaoSyracOscillationReport] = []
    for m, n in oscillation_pairs:
        if n > max_n:
            continue
        oscillations.append(
            TaoSyracOscillationReport(
                m=m,
                n=n,
                tao_oscillation=_oscillation(theoretical[n], m, n),
                empirical_nth_iterate_oscillation=_oscillation(
                    empirical_nth_by_level[n], m, n
                ),
                empirical_all_iterates_oscillation=_oscillation(
                    empirical_all_by_level[n], m, n
                ),
            )
        )

    max_tv_nth = max(tv_nth_values) if tv_nth_values else None
    max_tv_all = max(tv_all_values) if tv_all_values else None
    status = (
        "tao_nth_iterate_tv_within_1_percent"
        if max_tv_nth is not None and max_tv_nth <= 0.01
        else "tao_nth_iterate_tv_exceeds_1_percent"
        if max_tv_nth is not None
        else "tao_no_empirical_samples"
    )
    return TaoSyracEmpiricalReport(
        type="tao_syrac_empirical",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        max_n=max_n,
        max_steps_per_orbit=max_steps_per_orbit,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        max_tv_nth_iterate_to_tao=max_tv_nth,
        max_tv_all_iterates_to_tao=max_tv_all,
        level_reports=tuple(level_reports),
        oscillation_reports=tuple(oscillations),
    )


def tao_characteristic_decay_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_n: int = 7,
    top_frequencies: int = 10,
) -> TaoCharacteristicDecayReport:
    """Compare Tao and empirical characteristic coefficients through ``max_n``."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if max_n < 1:
        raise ValueError("max_n must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")

    theoretical_fraction = tao_syrac_distributions(max_n)
    theoretical = [
        [float(value) for value in distribution]
        for distribution in theoretical_fraction
    ]
    nth_counts = [[0 for _ in range(3**n)] for n in range(max_n + 1)]

    rng = random.Random(random_seed)
    completed = 0
    truncated = 0
    empirical_steps_used = 0
    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        while x != 1 and steps < max_n:
            x, _valuation = accelerated_step(x)
            steps += 1
            empirical_steps_used += 1
            nth_counts[steps][x % (3**steps)] += 1
        if x == 1:
            completed += 1
        else:
            # Only means the orbit did not hit 1 before max_n fixed iterates.
            truncated += 1

    level_reports: list[TaoCharacteristicLevelReport] = []
    tao_decay_points: list[tuple[int, float]] = []
    empirical_decay_points: list[tuple[int, float]] = []
    for n in range(1, max_n + 1):
        modulus = 3**n
        empirical = _distribution_from_counts(nth_counts[n])
        tao_abs = _characteristic_abs_by_frequency(theoretical[n], modulus)
        empirical_abs = _characteristic_abs_by_frequency(empirical, modulus)
        frequencies = sorted(tao_abs)
        differences = [
            abs(tao_abs[xi] - empirical_abs[xi])
            for xi in frequencies
        ]
        tao_max_xi = max(frequencies, key=lambda xi: tao_abs[xi])
        empirical_max_xi = max(frequencies, key=lambda xi: empirical_abs[xi])
        tao_max = tao_abs[tao_max_xi]
        empirical_max = empirical_abs[empirical_max_xi]
        tao_decay_points.append((n, tao_max))
        empirical_decay_points.append((n, empirical_max))
        top = sorted(frequencies, key=lambda xi: tao_abs[xi], reverse=True)[
            :top_frequencies
        ]
        level_reports.append(
            TaoCharacteristicLevelReport(
                n=n,
                modulus=modulus,
                frequencies_checked=len(frequencies),
                empirical_samples=sum(nth_counts[n]),
                tao_max_abs=tao_max,
                tao_max_xi=tao_max_xi,
                empirical_max_abs=empirical_max,
                empirical_max_xi=empirical_max_xi,
                max_abs_difference=max(differences) if differences else 0.0,
                mean_abs_difference=(
                    sum(differences) / len(differences) if differences else 0.0
                ),
                top_frequencies_by_tao_abs=tuple(
                    TaoCharacteristicTopFrequency(
                        xi=xi,
                        tao_abs=tao_abs[xi],
                        empirical_abs=empirical_abs[xi],
                        abs_difference=abs(tao_abs[xi] - empirical_abs[xi]),
                    )
                    for xi in top
                ),
            )
        )

    empirical_exponent = _fit_power_decay(empirical_decay_points)
    status = (
        "tao_empirical_characteristic_decay_exponent_at_least_1"
        if empirical_exponent is not None and empirical_exponent >= 1.0
        else "tao_empirical_characteristic_decay_exponent_below_1"
        if empirical_exponent is not None
        else "tao_empirical_characteristic_decay_no_fit"
    )
    return TaoCharacteristicDecayReport(
        type="tao_characteristic_function_decay",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        max_n=max_n,
        completed_orbits=completed,
        truncated_orbits=truncated,
        empirical_steps_used=empirical_steps_used,
        fitted_tao_power_exponent=_fit_power_decay(tao_decay_points),
        fitted_empirical_power_exponent=empirical_exponent,
        level_reports=tuple(level_reports),
    )
