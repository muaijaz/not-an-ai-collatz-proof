"""Mutual-information diagnostics for accelerated valuation sequences."""

from __future__ import annotations

import json
import math
import random
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class ValuationMILagReport:
    lag: int
    pairs: int
    mutual_information_bits: float
    miller_madow_bias_bits: float
    debiased_mutual_information_bits: float
    nonzero_source_symbols: int
    nonzero_target_symbols: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValuationMILagScanReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    max_steps_per_orbit: int
    max_lag: int
    max_exact_valuation: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    marginal_entropy_bits: float
    best_lag: int | None
    best_debiased_mutual_information_bits: float | None
    lag4_debiased_mutual_information_bits: float | None
    lag_reports: tuple[ValuationMILagReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "max_steps_per_orbit": self.max_steps_per_orbit,
            "max_lag": self.max_lag,
            "max_exact_valuation": self.max_exact_valuation,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "marginal_entropy_bits": self.marginal_entropy_bits,
            "best_lag": self.best_lag,
            "best_debiased_mutual_information_bits": (
                self.best_debiased_mutual_information_bits
            ),
            "lag4_debiased_mutual_information_bits": (
                self.lag4_debiased_mutual_information_bits
            ),
            "lag_reports": [item.to_json_dict() for item in self.lag_reports],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _bucket_valuation(valuation: int, max_exact: int) -> int:
    return valuation if valuation <= max_exact else max_exact + 1


def _entropy_bits(counts: list[int]) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def _mutual_information_report(
    lag: int,
    matrix: list[list[int]],
) -> ValuationMILagReport:
    total = sum(sum(row) for row in matrix)
    if total == 0:
        return ValuationMILagReport(
            lag=lag,
            pairs=0,
            mutual_information_bits=0.0,
            miller_madow_bias_bits=0.0,
            debiased_mutual_information_bits=0.0,
            nonzero_source_symbols=0,
            nonzero_target_symbols=0,
        )
    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(len(matrix))) for j in range(len(matrix))]
    mi = 0.0
    for i, row in enumerate(matrix):
        for j, count in enumerate(row):
            if count:
                mi += (count / total) * math.log2((count * total) / (row_sums[i] * col_sums[j]))
    nonzero_rows = sum(1 for value in row_sums if value)
    nonzero_cols = sum(1 for value in col_sums if value)
    # Leading finite-sample plug-in bias for MI under independence.
    bias = ((nonzero_rows - 1) * (nonzero_cols - 1)) / (2.0 * total * math.log(2.0))
    return ValuationMILagReport(
        lag=lag,
        pairs=total,
        mutual_information_bits=mi,
        miller_madow_bias_bits=bias,
        debiased_mutual_information_bits=max(0.0, mi - bias),
        nonzero_source_symbols=nonzero_rows,
        nonzero_target_symbols=nonzero_cols,
    )


def valuation_mi_lag_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    max_lag: int = 20,
    max_exact_valuation: int = 10,
) -> ValuationMILagScanReport:
    """Compute valuation-symbol mutual information for lags ``1..max_lag``."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if max_lag < 1:
        raise ValueError("max_lag must be positive")
    if max_exact_valuation < 1:
        raise ValueError("max_exact_valuation must be positive")
    if start_min < 1 or start_max <= start_min:
        raise ValueError("expected 1 <= start_min < start_max")

    symbols = max_exact_valuation + 1
    matrices = [
        [[0 for _ in range(symbols)] for _ in range(symbols)]
        for _ in range(max_lag + 1)
    ]
    marginal = [0 for _ in range(symbols)]
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
        history: deque[int] = deque(maxlen=max_lag)
        steps = 0
        while x != 1 and steps < max_steps_per_orbit:
            x, valuation = accelerated_step(x)
            symbol = _bucket_valuation(valuation, max_exact_valuation) - 1
            marginal[symbol] += 1
            for lag, previous in enumerate(reversed(history), start=1):
                matrices[lag][previous][symbol] += 1
            history.append(symbol)
            steps += 1
            total_steps += 1
        if x == 1:
            completed += 1
        else:
            truncated += 1

    lag_reports = tuple(
        _mutual_information_report(lag, matrices[lag])
        for lag in range(1, max_lag + 1)
    )
    best = max(
        lag_reports,
        key=lambda item: item.debiased_mutual_information_bits,
        default=None,
    )
    lag4 = next((item for item in lag_reports if item.lag == 4), None)
    status = (
        "valuation_mi_lag4_is_global_peak"
        if best is not None and best.lag == 4
        else "valuation_mi_lag4_not_global_peak"
        if best is not None
        else "valuation_mi_no_pairs"
    )
    return ValuationMILagScanReport(
        type="valuation_mi_lags",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        max_steps_per_orbit=max_steps_per_orbit,
        max_lag=max_lag,
        max_exact_valuation=max_exact_valuation,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        marginal_entropy_bits=_entropy_bits(marginal),
        best_lag=None if best is None else best.lag,
        best_debiased_mutual_information_bits=(
            None if best is None else best.debiased_mutual_information_bits
        ),
        lag4_debiased_mutual_information_bits=(
            None if lag4 is None else lag4.debiased_mutual_information_bits
        ),
        lag_reports=lag_reports,
    )
