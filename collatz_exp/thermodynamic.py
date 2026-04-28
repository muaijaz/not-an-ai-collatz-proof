"""Thermodynamic-pressure toy bounds for valuation-symbol models."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log
from typing import Any


@dataclass(frozen=True)
class PressureReport:
    type: str
    status: str
    valuation_cutoff: int
    root_s: float
    pressure_at_one: float
    contraction_dimension_signal: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def pressure(s: float, valuation_cutoff: int) -> float:
    """Toy pressure for independent valuation weights ``2^-a``."""

    total = 0.0
    for valuation in range(1, valuation_cutoff + 1):
        total += (2.0 ** -valuation) * (3.0 / (2.0 ** valuation)) ** s
    return log(total)


def pressure_report(valuation_cutoff: int = 32) -> PressureReport:
    if valuation_cutoff < 1:
        raise ValueError("valuation_cutoff must be positive")
    lo, hi = 0.0, 4.0
    if pressure(lo, valuation_cutoff) * pressure(hi, valuation_cutoff) > 0:
        root = 1.0
    else:
        for _ in range(80):
            mid = (lo + hi) / 2
            if pressure(mid, valuation_cutoff) > 0:
                hi = mid
            else:
                lo = mid
        root = (lo + hi) / 2
    p1 = pressure(1.0, valuation_cutoff)
    return PressureReport(
        type="toy_valuation_pressure_report",
        status="independent_symbol_pressure_not_ruelle_proof",
        valuation_cutoff=valuation_cutoff,
        root_s=root,
        pressure_at_one=p1,
        contraction_dimension_signal=root < 1.0,
    )
