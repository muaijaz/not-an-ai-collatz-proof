"""Finite spike-location correlation diagnostics."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import valuation_word


@dataclass(frozen=True)
class SpikeCorrelationReport:
    type: str
    status: str
    starts_checked: int
    steps: int
    spike_threshold: int
    spike_density: float
    adjacent_spike_density: float
    independent_adjacent_density: float
    negative_correlation_signal: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def spike_correlation_report(
    start_max: int = 999,
    steps: int = 64,
    spike_threshold: int = 3,
) -> SpikeCorrelationReport:
    if start_max < 3:
        raise ValueError("start_max must be at least three")
    total_positions = 0
    total_spikes = 0
    adjacent_positions = 0
    adjacent_spikes = 0
    starts = 0
    for n in range(3, start_max + 1, 2):
        word = valuation_word(n, steps)
        spikes = [value >= spike_threshold for value in word]
        starts += 1
        total_positions += len(spikes)
        total_spikes += sum(spikes)
        adjacent_positions += max(0, len(spikes) - 1)
        adjacent_spikes += sum(1 for left, right in zip(spikes, spikes[1:], strict=False) if left and right)
    density = total_spikes / total_positions if total_positions else 0.0
    adjacent_density = adjacent_spikes / adjacent_positions if adjacent_positions else 0.0
    independent = density * density
    return SpikeCorrelationReport(
        type="valuation_spike_correlation_diagnostic",
        status="finite_spike_correlation_not_dpp_proof",
        starts_checked=starts,
        steps=steps,
        spike_threshold=spike_threshold,
        spike_density=density,
        adjacent_spike_density=adjacent_density,
        independent_adjacent_density=independent,
        negative_correlation_signal=adjacent_density < independent,
    )
