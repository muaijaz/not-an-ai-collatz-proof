"""LTE checks for pure Mersenne tail-renormalization blocks."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log2
from typing import Any

from .core import v2
from .tail_family import tail_renormalization_step


@dataclass(frozen=True)
class LTEBlock:
    R: int
    c_actual: int
    c_lte: int
    matches_lte: bool
    block_A: int
    block_debt: float
    next_R: int
    next_u: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailLTEReport:
    type: str
    status: str
    R_min: int
    R_max: int
    all_match: bool
    worst_debt_R: int | None
    worst_block_debt: float | None
    blocks: tuple[LTEBlock, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "all_match": self.all_match,
            "worst_debt_R": self.worst_debt_R,
            "worst_block_debt": self.worst_block_debt,
            "blocks": [block.to_json_dict() for block in self.blocks],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def lte_v2_3_power_minus_1(R: int) -> int:
    """LTE formula for ``v2(3^R - 1)``."""

    if R < 1:
        raise ValueError("R must be positive")
    if R % 2 == 1:
        return 1
    return 2 + v2(R)


def tail_lte_report(R_min: int = 2, R_max: int = 128) -> TailLTEReport:
    """Compare exact pure-tail block valuations with the LTE formula."""

    if R_min < 2 or R_max < R_min:
        raise ValueError("require 2 <= R_min <= R_max")
    blocks: list[LTEBlock] = []
    for R in range(R_min, R_max + 1):
        step = tail_renormalization_step(R, 1)
        lte = lte_v2_3_power_minus_1(R)
        blocks.append(
            LTEBlock(
                R=R,
                c_actual=step.c,
                c_lte=lte,
                matches_lte=step.c == lte,
                block_A=step.block_A,
                block_debt=R * log2(3) - step.block_A,
                next_R=step.next_R,
                next_u=step.next_u,
            )
        )
    worst = max(blocks, key=lambda block: block.block_debt, default=None)
    return TailLTEReport(
        type="pure_mersenne_tail_lte_blocks",
        status="finite_lte_identity_check_not_tail_exclusion_proof",
        R_min=R_min,
        R_max=R_max,
        all_match=all(block.matches_lte for block in blocks),
        worst_debt_R=None if worst is None else worst.R,
        worst_block_debt=None if worst is None else worst.block_debt,
        blocks=tuple(blocks),
    )
