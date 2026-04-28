"""Proof-facing cylinder lemmas for Mersenne-tail renormalization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log2
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class TailCylinder:
    R: int
    u_residue: int
    u_mod_power: int
    blocks: int = 0
    total_m: int = 0
    total_A: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailCylinderTransition:
    status: str
    source: TailCylinder
    c: int | None
    next_R: int | None
    next_u_residue: int | None
    next_u_mod_power: int | None
    target: TailCylinder | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source": self.source.to_json_dict(),
            "c": self.c,
            "next_R": self.next_R,
            "next_u_residue": self.next_u_residue,
            "next_u_mod_power": self.next_u_mod_power,
            "target": None if self.target is None else self.target.to_json_dict(),
        }


@dataclass(frozen=True)
class TailExitLemmaReport:
    type: str
    status: str
    initial_R: int
    initial_u_mod_power: int
    max_u_mod_power: int
    max_blocks: int
    nodes_processed: int
    split_count: int
    transition_count: int
    exited_count: int
    unresolved_count: int
    max_terminal_debt: float
    unresolved: tuple[TailCylinder, ...]
    sample_transitions: tuple[TailCylinderTransition, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "initial_R": self.initial_R,
            "initial_u_mod_power": self.initial_u_mod_power,
            "max_u_mod_power": self.max_u_mod_power,
            "max_blocks": self.max_blocks,
            "nodes_processed": self.nodes_processed,
            "split_count": self.split_count,
            "transition_count": self.transition_count,
            "exited_count": self.exited_count,
            "unresolved_count": self.unresolved_count,
            "max_terminal_debt": self.max_terminal_debt,
            "unresolved": [item.to_json_dict() for item in self.unresolved],
            "sample_transitions": [
                item.to_json_dict() for item in self.sample_transitions
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailInternalStepReport:
    type: str
    status: str
    R_min: int
    R_max: int
    u_mod_power: int
    cases_checked: int
    all_match: bool
    first_failure: dict[str, int] | None
    theorem_statement: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def tail_internal_step_report(
    R_min: int = 2,
    R_max: int = 64,
    u_mod_power: int = 8,
) -> TailInternalStepReport:
    """Check and state the exact tail-internal step identity.

    For odd ``u`` and ``R >= 2``, ``n=2^R*u-1`` has accelerated valuation
    exactly one, and the next tail depth is exactly ``R-1``:

    ``S(n)=3*2^(R-1)*u-1`` and ``v2(S(n)+1)=R-1``.
    """

    if R_min < 2:
        raise ValueError("R_min must be at least two")
    if R_max < R_min:
        raise ValueError("R_max must be at least R_min")
    if u_mod_power < 1:
        raise ValueError("u_mod_power must be positive")
    cases = 0
    first_failure: dict[str, int] | None = None
    for R in range(R_min, R_max + 1):
        for u in range(1, 1 << u_mod_power, 2):
            n = (1 << R) * u - 1
            landing, a = accelerated_step(n)
            expected = 3 * (1 << (R - 1)) * u - 1
            cases += 1
            if a != 1 or landing != expected or v2(landing + 1) != R - 1:
                first_failure = {
                    "R": R,
                    "u": u,
                    "n": n,
                    "valuation": a,
                    "landing": landing,
                    "expected_landing": expected,
                    "next_R": v2(landing + 1),
                }
                break
        if first_failure is not None:
            break
    return TailInternalStepReport(
        type="tail_internal_step_identity",
        status=(
            "exact_tail_internal_identity_checked"
            if first_failure is None
            else "tail_internal_identity_failed"
        ),
        R_min=R_min,
        R_max=R_max,
        u_mod_power=u_mod_power,
        cases_checked=cases,
        all_match=first_failure is None,
        first_failure=first_failure,
        theorem_statement=(
            "For every odd u and every R>=2, if n=2^R*u-1 then "
            "v2(3n+1)=1, S(n)=3*2^(R-1)*u-1, and v2(S(n)+1)=R-1."
        ),
    )


def tail_cylinder_transition(cylinder: TailCylinder) -> TailCylinderTransition:
    """Compute one exact forced transition for a tail cylinder, if determined."""

    if cylinder.R < 2:
        return TailCylinderTransition(
            status="already_exited_tail",
            source=cylinder,
            c=None,
            next_R=None,
            next_u_residue=None,
            next_u_mod_power=None,
            target=None,
        )
    if cylinder.u_mod_power < 1:
        raise ValueError("u_mod_power must be at least one for odd-u cylinders")
    modulus = 1 << cylinder.u_mod_power
    u0 = cylinder.u_residue % modulus
    if u0 % 2 == 0:
        raise ValueError("tail cylinder representative must be odd")

    c = v2((3**cylinder.R) * u0 - 1)
    if c >= cylinder.u_mod_power:
        return TailCylinderTransition(
            status="needs_split_for_c",
            source=cylinder,
            c=None,
            next_R=None,
            next_u_residue=None,
            next_u_mod_power=None,
            target=None,
        )

    base_next_n = ((3**cylinder.R) * u0 - 1) >> c
    carried_power = cylinder.u_mod_power - c
    next_R = v2(base_next_n + 1)
    if next_R >= carried_power:
        return TailCylinderTransition(
            status="needs_split_for_next_R",
            source=cylinder,
            c=c,
            next_R=None,
            next_u_residue=None,
            next_u_mod_power=None,
            target=None,
        )

    next_u_mod_power = carried_power - next_R
    next_u_residue = ((base_next_n + 1) >> next_R) % (1 << next_u_mod_power)
    target = TailCylinder(
        R=next_R,
        u_residue=next_u_residue,
        u_mod_power=next_u_mod_power,
        blocks=cylinder.blocks + 1,
        total_m=cylinder.total_m + cylinder.R,
        total_A=cylinder.total_A + cylinder.R + c,
    )
    return TailCylinderTransition(
        status="forced",
        source=cylinder,
        c=c,
        next_R=next_R,
        next_u_residue=next_u_residue,
        next_u_mod_power=next_u_mod_power,
        target=target,
    )


def split_tail_cylinder(cylinder: TailCylinder) -> tuple[TailCylinder, TailCylinder]:
    """Split ``u mod 2^ell`` into its two children."""

    next_power = cylinder.u_mod_power + 1
    return (
        TailCylinder(
            R=cylinder.R,
            u_residue=cylinder.u_residue,
            u_mod_power=next_power,
            blocks=cylinder.blocks,
            total_m=cylinder.total_m,
            total_A=cylinder.total_A,
        ),
        TailCylinder(
            R=cylinder.R,
            u_residue=cylinder.u_residue + (1 << cylinder.u_mod_power),
            u_mod_power=next_power,
            blocks=cylinder.blocks,
            total_m=cylinder.total_m,
            total_A=cylinder.total_A,
        ),
    )


def prove_tail_exit_cylinders(
    R: int = 20,
    initial_u_mod_power: int = 8,
    max_u_mod_power: int = 24,
    max_blocks: int = 12,
    max_nodes: int = 100_000,
    sample_transitions: int = 12,
) -> TailExitLemmaReport:
    """Try to certify that all odd ``u`` cylinders exit ``R >= 2`` tails."""

    if R < 2:
        raise ValueError("R must be at least two")
    if initial_u_mod_power < 1:
        raise ValueError("initial_u_mod_power must be at least one")
    if max_u_mod_power < initial_u_mod_power:
        raise ValueError("max_u_mod_power must be at least initial_u_mod_power")
    queue = [
        TailCylinder(R=R, u_residue=u, u_mod_power=initial_u_mod_power)
        for u in range(1, 1 << initial_u_mod_power, 2)
    ]
    nodes_processed = 0
    split_count = 0
    transition_count = 0
    exited: list[TailCylinder] = []
    unresolved: list[TailCylinder] = []
    samples: list[TailCylinderTransition] = []

    while queue and nodes_processed < max_nodes:
        cylinder = queue.pop()
        nodes_processed += 1
        if cylinder.R < 2:
            exited.append(cylinder)
            continue
        if cylinder.blocks >= max_blocks:
            unresolved.append(cylinder)
            continue
        transition = tail_cylinder_transition(cylinder)
        if len(samples) < sample_transitions:
            samples.append(transition)
        if transition.status == "forced" and transition.target is not None:
            transition_count += 1
            queue.append(transition.target)
            continue
        if cylinder.u_mod_power >= max_u_mod_power:
            unresolved.append(cylinder)
            continue
        split_count += 1
        queue.extend(split_tail_cylinder(cylinder))

    unresolved.extend(queue)
    max_terminal_debt = max(
        (
            item.total_m * log2(3) - item.total_A
            for item in (*exited, *unresolved)
        ),
        default=0.0,
    )
    return TailExitLemmaReport(
        type="tail_exit_cylinder_lemma",
        status=(
            "finite_tail_exit_certificate_not_collatz_proof"
            if not unresolved
            else "finite_tail_exit_search_incomplete_not_collatz_proof"
        ),
        initial_R=R,
        initial_u_mod_power=initial_u_mod_power,
        max_u_mod_power=max_u_mod_power,
        max_blocks=max_blocks,
        nodes_processed=nodes_processed,
        split_count=split_count,
        transition_count=transition_count,
        exited_count=len(exited),
        unresolved_count=len(unresolved),
        max_terminal_debt=max_terminal_debt,
        unresolved=tuple(
            sorted(
                unresolved,
                key=lambda item: (
                    item.R,
                    item.u_mod_power,
                    item.u_residue,
                    item.blocks,
                ),
                reverse=True,
            )[:sample_transitions]
        ),
        sample_transitions=tuple(samples),
    )
