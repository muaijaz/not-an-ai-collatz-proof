"""Composite cycle-exclusion tower artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .cycles import scan_near_balanced_cycles
from .cycles_eliahou import CycleLengthScreen, cycle_length_screen
from .lift_realizability import LiftRealizabilityReport, lift_realizability_report
from .lll_cycles import CycleLatticeReport, cycle_lattice_report


@dataclass(frozen=True)
class CycleExclusionTowerReport:
    type: str
    status: str
    max_m: int
    valuation_max: int
    slack: int
    continued_fraction: CycleLengthScreen
    lattice: CycleLatticeReport
    words_scanned: int
    cycle_kinds: dict[str, int]
    nontrivial_positive_cycles: int
    nonrealizing_positive_candidates: int
    lift_realizability: LiftRealizabilityReport

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["continued_fraction"] = self.continued_fraction.to_json_dict()
        data["lattice"] = self.lattice.to_json_dict()
        data["lift_realizability"] = self.lift_realizability.to_json_dict()
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def cycle_exclusion_tower_report(
    max_m: int = 12,
    valuation_max: int = 6,
    slack: int = 1,
    lift_modulus_power: int = 6,
    lift_max_period: int = 8,
) -> CycleExclusionTowerReport:
    """Fuse continued fractions, LLL, exact cycle checks, and lift checks."""

    screen = cycle_length_screen(max_m=max_m)
    lattice = cycle_lattice_report(
        m_max=min(max_m, 8),
        valuation_max=valuation_max,
        slack=slack,
    )
    scan = scan_near_balanced_cycles(
        m_max=max_m,
        valuation_max=valuation_max,
        slack=slack,
    )
    lift = lift_realizability_report(
        modulus_power=lift_modulus_power,
        max_valuation=valuation_max,
        max_period=lift_max_period,
    )
    return CycleExclusionTowerReport(
        type="cycle_exclusion_tower",
        status="finite_baker_lll_pila_style_tower_not_cycle_proof",
        max_m=max_m,
        valuation_max=valuation_max,
        slack=slack,
        continued_fraction=screen,
        lattice=lattice,
        words_scanned=scan.words_scanned,
        cycle_kinds=dict(scan.by_kind),
        nontrivial_positive_cycles=len(scan.nontrivial_positive_integer_cycles),
        nonrealizing_positive_candidates=len(scan.positive_integer_nonrealizing),
        lift_realizability=lift,
    )
