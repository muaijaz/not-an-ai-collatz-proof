"""Post-exit cylinder map for Mersenne-tail proof search."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import log2
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class PostExitState:
    R: int
    u_mod2: int
    u_mod2_power: int
    u_mod3: int
    u_mod3_power: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PostExitTransitionSample:
    source: PostExitState
    u: int
    n0: int
    post_start: int
    status: str
    steps: int
    total_A: int
    landing: int
    landing_tail_depth: int
    target: PostExitState | None
    debt_against_start: float

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.to_json_dict(),
            "u": self.u,
            "n0": self.n0,
            "post_start": self.post_start,
            "status": self.status,
            "steps": self.steps,
            "total_A": self.total_A,
            "landing": self.landing,
            "landing_tail_depth": self.landing_tail_depth,
            "target": None if self.target is None else self.target.to_json_dict(),
            "debt_against_start": self.debt_against_start,
        }


@dataclass(frozen=True)
class PostExitPointwiseReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    R_values: tuple[int, ...]
    sample_lift_power: int
    max_steps: int
    tail_reentry_min_R: int
    states: int
    row_denominator: int
    descended_samples: int
    reentry_samples: int
    out_of_range_reentry_samples: int
    max_row_survival_num: int
    max_row_survival_den: int
    constant_weight_rho_max: float
    perron_eigenvalue_estimate: float | None
    finite_ratio_max: float | None
    zero_weight_rows: int
    infinite_ratio_rows: int
    worst_state: PostExitState | None
    worst_row_descended: int
    worst_row_reentered: int
    sample_transitions: tuple[PostExitTransitionSample, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_values": list(self.R_values),
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "tail_reentry_min_R": self.tail_reentry_min_R,
            "states": self.states,
            "row_denominator": self.row_denominator,
            "descended_samples": self.descended_samples,
            "reentry_samples": self.reentry_samples,
            "out_of_range_reentry_samples": self.out_of_range_reentry_samples,
            "max_row_survival_num": self.max_row_survival_num,
            "max_row_survival_den": self.max_row_survival_den,
            "constant_weight_rho_max": self.constant_weight_rho_max,
            "perron_eigenvalue_estimate": self.perron_eigenvalue_estimate,
            "finite_ratio_max": self.finite_ratio_max,
            "zero_weight_rows": self.zero_weight_rows,
            "infinite_ratio_rows": self.infinite_ratio_rows,
            "worst_state": None if self.worst_state is None else self.worst_state.to_json_dict(),
            "worst_row_descended": self.worst_row_descended,
            "worst_row_reentered": self.worst_row_reentered,
            "sample_transitions": [
                sample.to_json_dict() for sample in self.sample_transitions
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PostExitPointwiseLadderReport:
    type: str
    status: str
    levels: tuple[PostExitPointwiseReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PostExitScaledPerronLevel:
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    states: int
    row_denominator: int
    iterations: int
    converged: bool
    power_scale_estimate: float
    finite_ratio_max: float | None
    finite_ratio_min: float | None
    zero_weight_rows: int
    infinite_ratio_rows: int
    descended_samples: int
    reentry_samples: int
    out_of_range_reentry_samples: int
    constant_weight_rho_max_num: int
    constant_weight_rho_max_den: int
    worst_state: PostExitState | None
    worst_ratio_state: PostExitState | None

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["worst_state"] = (
            None if self.worst_state is None else self.worst_state.to_json_dict()
        )
        data["worst_ratio_state"] = (
            None
            if self.worst_ratio_state is None
            else self.worst_ratio_state.to_json_dict()
        )
        return data


@dataclass(frozen=True)
class PostExitScaledPerronReport:
    type: str
    status: str
    levels: tuple[PostExitScaledPerronLevel, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PostExitSuperEigenLevel:
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    states: int
    row_denominator: int
    recurrent_ratio_estimate: float
    alpha: float
    alpha_margin: float
    iterations: int
    converged: bool
    residual: float
    lambda_super: float
    finite_ratio_min: float
    finite_ratio_max: float
    positive_min: float
    positive_max: float
    recurrent_sccs: int | None
    closed_sccs: int | None
    sccs_skipped: bool
    descended_samples: int
    reentry_samples: int
    out_of_range_reentry_samples: int
    constant_weight_rho_max_num: int
    constant_weight_rho_max_den: int
    worst_state: PostExitState | None
    worst_transient_state: PostExitState | None

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["worst_state"] = (
            None if self.worst_state is None else self.worst_state.to_json_dict()
        )
        data["worst_transient_state"] = (
            None
            if self.worst_transient_state is None
            else self.worst_transient_state.to_json_dict()
        )
        return data


@dataclass(frozen=True)
class PostExitSuperEigenReport:
    type: str
    status: str
    levels: tuple[PostExitSuperEigenLevel, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _crt_mod_2_3(residue2: int, power2: int, residue3: int, power3: int) -> int:
    modulus2 = 1 << power2
    modulus3 = 3**power3
    if modulus3 == 1:
        return residue2 % modulus2
    inverse = pow(modulus2, -1, modulus3)
    t = ((residue3 - residue2) * inverse) % modulus3
    return residue2 + modulus2 * t


def post_exit_states(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
) -> tuple[PostExitState, ...]:
    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    if not R_values:
        raise ValueError("R_values must be nonempty")
    if any(R < 2 for R in R_values):
        raise ValueError("all R_values must be at least two")
    residues2 = range(1, 1 << mod2_power, 2)
    residues3 = range(3**mod3_power)
    return tuple(
        PostExitState(
            R=R,
            u_mod2=u2,
            u_mod2_power=mod2_power,
            u_mod3=u3,
            u_mod3_power=mod3_power,
        )
        for R in R_values
        for u2 in residues2
        for u3 in residues3
    )


def _state_count(mod2_power: int, mod3_power: int, R_values: tuple[int, ...]) -> int:
    return len(R_values) * (1 << (mod2_power - 1)) * (3**mod3_power)


def _decode_state_index(
    index: int,
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
) -> PostExitState:
    n2 = 1 << (mod2_power - 1)
    n3 = 3**mod3_power
    per_R = n2 * n3
    r_index, rem = divmod(index, per_R)
    u2_index, u3 = divmod(rem, n3)
    return PostExitState(
        R=R_values[r_index],
        u_mod2=2 * u2_index + 1,
        u_mod2_power=mod2_power,
        u_mod3=u3,
        u_mod3_power=mod3_power,
    )


def _target_index(
    state: PostExitState,
    R_index: dict[int, int],
    mod2_power: int,
    mod3_power: int,
) -> int | None:
    if state.R not in R_index:
        return None
    n2 = 1 << (mod2_power - 1)
    n3 = 3**mod3_power
    return (
        R_index[state.R] * n2 * n3
        + ((state.u_mod2 % (1 << mod2_power)) // 2) * n3
        + state.u_mod3
    )


def _iter_post_exit_states(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
):
    residues2 = range(1, 1 << mod2_power, 2)
    residues3 = range(3**mod3_power)
    for R in R_values:
        for u2 in residues2:
            for u3 in residues3:
                yield PostExitState(
                    R=R,
                    u_mod2=u2,
                    u_mod2_power=mod2_power,
                    u_mod3=u3,
                    u_mod3_power=mod3_power,
                )


def _sample_u_values(state: PostExitState, sample_lift_power: int) -> tuple[int, ...]:
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")
    modulus = (1 << state.u_mod2_power) * (3**state.u_mod3_power)
    base = _crt_mod_2_3(
        state.u_mod2,
        state.u_mod2_power,
        state.u_mod3,
        state.u_mod3_power,
    )
    return tuple(base + lift * modulus for lift in range(1 << sample_lift_power))


def post_exit_landing(R: int, u: int) -> int:
    """Return the landing after the forced ``R-1`` valuation-one tail steps."""

    if R < 2:
        raise ValueError("R must be at least two")
    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be positive and odd")
    return 2 * (3 ** (R - 1)) * u - 1


def post_exit_transition_sample(
    state: PostExitState,
    u: int,
    state_index: dict[tuple[int, int, int], int] | None = None,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
) -> PostExitTransitionSample:
    """Run the exact post-exit phase for one representative ``u``."""

    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    if tail_reentry_min_R < 1:
        raise ValueError("tail_reentry_min_R must be positive")
    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be positive and odd")
    n0 = (1 << state.R) * u - 1
    post_start = post_exit_landing(state.R, u)
    x = post_start
    total_A = state.R - 1
    if x < n0:
        return PostExitTransitionSample(
            source=state,
            u=u,
            n0=n0,
            post_start=post_start,
            status="descended_at_post_start",
            steps=0,
            total_A=total_A,
            landing=x,
            landing_tail_depth=v2(x + 1),
            target=None,
            debt_against_start=total_A - 0.0,
        )

    for steps in range(1, max_steps + 1):
        x, a = accelerated_step(x)
        total_A += a
        tail_depth = v2(x + 1)
        if x < n0:
            return PostExitTransitionSample(
                source=state,
                u=u,
                n0=n0,
                post_start=post_start,
                status="descended",
                steps=steps,
                total_A=total_A,
                landing=x,
                landing_tail_depth=tail_depth,
                target=None,
                debt_against_start=(state.R - 1 + steps) * log2(3) - total_A,
            )
        if tail_depth >= tail_reentry_min_R:
            next_u = (x + 1) >> tail_depth
            target = PostExitState(
                R=tail_depth,
                u_mod2=next_u % (1 << state.u_mod2_power),
                u_mod2_power=state.u_mod2_power,
                u_mod3=next_u % (3**state.u_mod3_power)
                if state.u_mod3_power
                else 0,
                u_mod3_power=state.u_mod3_power,
            )
            status = (
                "reentered_tail"
                if state_index is None
                or (target.R, target.u_mod2, target.u_mod3) in state_index
                else "reentered_tail_out_of_range"
            )
            return PostExitTransitionSample(
                source=state,
                u=u,
                n0=n0,
                post_start=post_start,
                status=status,
                steps=steps,
                total_A=total_A,
                landing=x,
                landing_tail_depth=tail_depth,
                target=target,
                debt_against_start=(state.R - 1 + steps) * log2(3) - total_A,
            )

    return PostExitTransitionSample(
        source=state,
        u=u,
        n0=n0,
        post_start=post_start,
        status="max_steps_exceeded",
        steps=max_steps,
        total_A=total_A,
        landing=x,
        landing_tail_depth=v2(x + 1),
        target=None,
        debt_against_start=(state.R - 1 + max_steps) * log2(3) - total_A,
    )


def _sparse_left_perron(
    rows: tuple[dict[int, int], ...],
    denominator: int,
    iterations: int = 200,
) -> tuple[float, int] | None:
    n = len(rows)
    if n == 0:
        return None
    vector = [1.0 / n for _ in range(n)]
    eigenvalue = 0.0
    for _ in range(iterations):
        nxt = [0.0 for _ in range(n)]
        for i, value in enumerate(vector):
            for j, count in rows[i].items():
                nxt[j] += value * count / denominator
        mass = sum(nxt)
        if mass == 0.0:
            return 0.0, 0
        eigenvalue = mass / sum(vector)
        vector = [value / mass for value in nxt]
    return eigenvalue, max(range(n), key=lambda i: vector[i])


def _right_perron_vector(
    rows: tuple[dict[int, int], ...],
    denominator: int,
    iterations: int = 200,
) -> tuple[float, tuple[float, ...]]:
    n = len(rows)
    if n == 0:
        return 0.0, ()
    vector = [1.0 for _ in range(n)]
    eigenvalue = 0.0
    for _ in range(iterations):
        nxt = [
            sum(count * vector[j] / denominator for j, count in row.items())
            for row in rows
        ]
        scale = max(nxt, default=0.0)
        if scale == 0.0:
            return 0.0, tuple(nxt)
        eigenvalue = scale
        vector = [value / scale for value in nxt]
    return eigenvalue, tuple(vector)


def post_exit_pointwise_report(
    mod2_power: int = 8,
    mod3_power: int = 2,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    sample_transitions: int = 12,
    perron_state_limit: int = 200_000,
) -> PostExitPointwiseReport:
    """Build the finite post-exit transition matrix and scan pointwise ratios."""

    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    if not R_values:
        raise ValueError("R_values must be nonempty")
    if any(R < 2 for R in R_values):
        raise ValueError("all R_values must be at least two")
    R_set = set(R_values)
    total_states = _state_count(mod2_power, mod3_power, R_values)
    build_matrix = total_states <= perron_state_limit
    states = (
        post_exit_states(mod2_power, mod3_power, R_values)
        if build_matrix
        else ()
    )
    index = (
        {(state.R, state.u_mod2, state.u_mod3): i for i, state in enumerate(states)}
        if build_matrix
        else {}
    )
    denominator = 1 << sample_lift_power
    rows: list[dict[int, int]] = []
    row_descents: list[int] = []
    row_reentries: list[int] = []
    descended_samples = 0
    reentry_samples = 0
    out_of_range_samples = 0
    samples: list[PostExitTransitionSample] = []
    max_survival = 0
    worst_state: PostExitState | None = None
    worst_descents = 0
    worst_reentries = 0

    state_iter = states if build_matrix else _iter_post_exit_states(mod2_power, mod3_power, R_values)
    for state in state_iter:
        row: dict[int, int] = {}
        descents = 0
        reentries = 0
        for u in _sample_u_values(state, sample_lift_power):
            transition = post_exit_transition_sample(
                state,
                u,
                state_index=index if build_matrix else None,
                max_steps=max_steps,
                tail_reentry_min_R=tail_reentry_min_R,
            )
            if len(samples) < sample_transitions:
                samples.append(transition)
            if transition.status.startswith("descended"):
                descents += 1
                descended_samples += 1
            elif transition.status == "reentered_tail" and transition.target is not None:
                if transition.target.R in R_set:
                    if build_matrix:
                        target_key = (
                            transition.target.R,
                            transition.target.u_mod2,
                            transition.target.u_mod3,
                        )
                        target_index = index[target_key]
                        row[target_index] = row.get(target_index, 0) + 1
                    reentries += 1
                    reentry_samples += 1
                else:
                    out_of_range_samples += 1
            else:
                out_of_range_samples += 1
        if reentries > max_survival:
            max_survival = reentries
            worst_state = state
            worst_descents = descents
            worst_reentries = reentries
        if build_matrix:
            rows.append(row)
            row_descents.append(descents)
            row_reentries.append(reentries)

    left: tuple[float, int] | None = None
    finite_ratio_max: float | None = None
    zero_weight_rows = 0
    infinite_ratio_rows = 0
    if build_matrix:
        left = _sparse_left_perron(tuple(rows), denominator)
        _, omega = _right_perron_vector(tuple(rows), denominator)
        ratios: list[float] = []
        for i, row in enumerate(rows):
            image = sum(count * omega[j] / denominator for j, count in row.items())
            if omega[i] == 0.0:
                zero_weight_rows += 1
                if image > 0.0:
                    infinite_ratio_rows += 1
                continue
            ratios.append(image / omega[i])
        finite_ratio_max = max(ratios, default=None)
    rho = Fraction(max_survival, denominator)
    if out_of_range_samples:
        status = "finite_post_exit_scan_has_out_of_range_reentries"
    elif max_survival < denominator:
        status = "finite_post_exit_pointwise_contraction_candidate_not_global_proof"
    elif max_survival == denominator:
        status = "finite_post_exit_full_survival_row_obstruction"
    else:
        status = "finite_post_exit_scan_inconclusive_not_global_proof"
    return PostExitPointwiseReport(
        type="post_exit_pointwise_report",
        status=status,
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
        states=total_states,
        row_denominator=denominator,
        descended_samples=descended_samples,
        reentry_samples=reentry_samples,
        out_of_range_reentry_samples=out_of_range_samples,
        max_row_survival_num=rho.numerator,
        max_row_survival_den=rho.denominator,
        constant_weight_rho_max=float(rho),
        perron_eigenvalue_estimate=None if left is None else left[0],
        finite_ratio_max=finite_ratio_max,
        zero_weight_rows=zero_weight_rows,
        infinite_ratio_rows=infinite_ratio_rows,
        worst_state=worst_state,
        worst_row_descended=worst_descents,
        worst_row_reentered=worst_reentries,
        sample_transitions=tuple(samples),
    )


def post_exit_pointwise_ladder_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 2), (10, 3), (12, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
) -> PostExitPointwiseLadderReport:
    levels = tuple(
        post_exit_pointwise_report(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
        )
        for mod2_power, mod3_power in configurations
    )
    if all(
        level.status == "finite_post_exit_pointwise_contraction_candidate_not_global_proof"
        for level in levels
    ):
        status = "finite_post_exit_ladder_pointwise_contraction_candidates"
    else:
        status = "finite_post_exit_ladder_has_obstructions_or_truncations"
    return PostExitPointwiseLadderReport(
        type="post_exit_pointwise_ladder_report",
        status=status,
        levels=levels,
    )


def _post_exit_transition_target_index(
    R: int,
    u: int,
    R_index: dict[int, int],
    mod2_power: int,
    mod3_power: int,
    max_steps: int,
    tail_reentry_min_R: int,
) -> tuple[int, int]:
    """Return ``(status_code, target_index)`` for a concrete post-exit sample.

    Status codes: ``0`` descended, ``1`` in-window tail reentry, ``2``
    out-of-window reentry or unresolved.
    """

    n0 = (1 << R) * u - 1
    x = post_exit_landing(R, u)
    if x < n0:
        return 0, -1
    for _ in range(1, max_steps + 1):
        x, _ = accelerated_step(x)
        if x < n0:
            return 0, -1
        tail_depth = v2(x + 1)
        if tail_depth >= tail_reentry_min_R:
            if tail_depth not in R_index:
                return 2, -1
            next_u = (x + 1) >> tail_depth
            u2 = next_u % (1 << mod2_power)
            if u2 % 2 == 0:
                return 2, -1
            u3 = next_u % (3**mod3_power) if mod3_power else 0
            n2 = 1 << (mod2_power - 1)
            n3 = 3**mod3_power
            return 1, R_index[tail_depth] * n2 * n3 + (u2 // 2) * n3 + u3
    return 2, -1


def _build_post_exit_target_array(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
    tail_reentry_min_R: int,
):
    import numpy as np

    denominator = 1 << sample_lift_power
    total_states = _state_count(mod2_power, mod3_power, R_values)
    if total_states >= (1 << 31):
        raise ValueError("state count is too large for int32 target cache")
    targets = np.full((total_states, denominator), -1, dtype=np.int32)
    modulus = (1 << mod2_power) * (3**mod3_power)
    residues3 = 3**mod3_power
    R_index = {R: i for i, R in enumerate(R_values)}
    descended = 0
    reentered = 0
    out_of_range = 0
    max_survival = 0
    worst_index: int | None = None
    row = 0
    for R in R_values:
        for u2 in range(1, 1 << mod2_power, 2):
            for u3 in range(residues3):
                base = _crt_mod_2_3(u2, mod2_power, u3, mod3_power)
                row_survival = 0
                for lift in range(denominator):
                    status, target = _post_exit_transition_target_index(
                        R=R,
                        u=base + lift * modulus,
                        R_index=R_index,
                        mod2_power=mod2_power,
                        mod3_power=mod3_power,
                        max_steps=max_steps,
                        tail_reentry_min_R=tail_reentry_min_R,
                    )
                    if status == 0:
                        descended += 1
                    elif status == 1:
                        targets[row, lift] = target
                        row_survival += 1
                        reentered += 1
                    else:
                        out_of_range += 1
                if row_survival > max_survival:
                    max_survival = row_survival
                    worst_index = row
                row += 1
    return targets, descended, reentered, out_of_range, max_survival, worst_index


def _right_power_scaled_ratios(
    targets,
    denominator: int,
    iterations: int,
    tolerance: float,
) -> tuple[bool, float, float | None, float | None, int, int, int | None]:
    import numpy as np

    n = targets.shape[0]
    vector = np.ones(n, dtype=np.float64)
    scale = 0.0
    converged = False
    previous_vector = vector
    for _ in range(iterations):
        image = np.zeros(n, dtype=np.float64)
        for col in range(targets.shape[1]):
            target = targets[:, col]
            mask = target >= 0
            image[mask] += vector[target[mask]]
        image /= denominator
        next_scale = float(image.max(initial=0.0))
        if next_scale == 0.0:
            vector = image
            scale = 0.0
            converged = True
            break
        image /= next_scale
        vector_delta = float(np.max(np.abs(image - previous_vector), initial=0.0))
        if (
            scale
            and abs(next_scale - scale) <= tolerance * max(1.0, abs(scale))
            and vector_delta <= tolerance
        ):
            converged = True
        vector = image
        previous_vector = image.copy()
        scale = next_scale
        if converged:
            break

    image = np.zeros(n, dtype=np.float64)
    for col in range(targets.shape[1]):
        target = targets[:, col]
        mask = target >= 0
        image[mask] += vector[target[mask]]
    image /= denominator
    nonzero = vector > 0.0
    zero_weight_rows = int((~nonzero).sum())
    infinite_ratio_rows = int(((~nonzero) & (image > 0.0)).sum())
    if bool(nonzero.any()):
        ratios = image[nonzero] / vector[nonzero]
        finite_ratio_max = float(ratios.max(initial=0.0))
        finite_ratio_min = float(ratios.min(initial=0.0))
        nonzero_indices = np.flatnonzero(nonzero)
        worst_ratio_index = int(nonzero_indices[int(ratios.argmax())])
    else:
        finite_ratio_max = None
        finite_ratio_min = None
        worst_ratio_index = None
    return (
        converged,
        scale,
        finite_ratio_max,
        finite_ratio_min,
        zero_weight_rows,
        infinite_ratio_rows,
        worst_ratio_index,
    )


def _apply_targets(targets, vector, denominator: int):
    import numpy as np

    image = np.zeros(targets.shape[0], dtype=np.float64)
    for col in range(targets.shape[1]):
        target = targets[:, col]
        mask = target >= 0
        image[mask] += vector[target[mask]]
    image /= denominator
    return image


def _scc_counts(targets, state_limit: int):
    if targets.shape[0] > state_limit:
        return None, None, True
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components

    mask = targets >= 0
    row_counts = mask.sum(axis=1).astype(np.int64)
    indptr = np.empty(targets.shape[0] + 1, dtype=np.int64)
    indptr[0] = 0
    np.cumsum(row_counts, out=indptr[1:])
    indices = targets[mask].astype(np.int32, copy=False)
    data = np.ones(indices.shape[0], dtype=np.int8)
    graph = csr_matrix((data, indices, indptr), shape=(targets.shape[0], targets.shape[0]))
    component_count, labels = connected_components(
        graph,
        directed=True,
        connection="strong",
        return_labels=True,
    )
    closed = np.ones(component_count, dtype=bool)
    for source in range(targets.shape[0]):
        source_component = labels[source]
        for target in targets[source]:
            if target >= 0 and labels[target] != source_component:
                closed[source_component] = False
                break
    nonempty_closed = int(closed.sum())
    return component_count, nonempty_closed, False


def _positive_resolvent_super_vector(
    targets,
    denominator: int,
    alpha: float,
    iterations: int,
    tolerance: float,
):
    import numpy as np

    vector = np.ones(targets.shape[0], dtype=np.float64)
    residual = float("inf")
    converged = False
    for iteration in range(1, iterations + 1):
        image = _apply_targets(targets, vector, denominator)
        nxt = 1.0 + image / alpha
        residual = float(np.max(np.abs(nxt - vector), initial=0.0))
        vector = nxt
        if residual <= tolerance * max(1.0, float(np.max(vector, initial=1.0))):
            converged = True
            break
    image = _apply_targets(targets, vector, denominator)
    ratios = image / vector
    worst_index = int(np.argmax(ratios))
    # Transient rows are exactly the rows outside the zero-free recurrent
    # support of the unlifted vector; after lifting every row is positive.
    return (
        vector,
        ratios,
        iteration,
        converged,
        residual,
        worst_index,
    )


def post_exit_scaled_perron_level(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    iterations: int = 80,
    tolerance: float = 1e-10,
) -> PostExitScaledPerronLevel:
    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    if not R_values:
        raise ValueError("R_values must be nonempty")
    if any(R < 2 for R in R_values):
        raise ValueError("all R_values must be at least two")
    denominator = 1 << sample_lift_power
    (
        targets,
        descended,
        reentered,
        out_of_range,
        max_survival,
        worst_index,
    ) = _build_post_exit_target_array(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
    )
    (
        converged,
        scale,
        finite_ratio_max,
        finite_ratio_min,
        zero_weight_rows,
        infinite_ratio_rows,
        worst_ratio_index,
    ) = _right_power_scaled_ratios(
        targets=targets,
        denominator=denominator,
        iterations=iterations,
        tolerance=tolerance,
    )
    rho = Fraction(max_survival, denominator)
    return PostExitScaledPerronLevel(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        states=targets.shape[0],
        row_denominator=denominator,
        iterations=iterations,
        converged=converged,
        power_scale_estimate=scale,
        finite_ratio_max=finite_ratio_max,
        finite_ratio_min=finite_ratio_min,
        zero_weight_rows=zero_weight_rows,
        infinite_ratio_rows=infinite_ratio_rows,
        descended_samples=descended,
        reentry_samples=reentered,
        out_of_range_reentry_samples=out_of_range,
        constant_weight_rho_max_num=rho.numerator,
        constant_weight_rho_max_den=rho.denominator,
        worst_state=None
        if worst_index is None
        else _decode_state_index(worst_index, mod2_power, mod3_power, R_values),
        worst_ratio_state=None
        if worst_ratio_index is None
        else _decode_state_index(
            worst_ratio_index,
            mod2_power,
            mod3_power,
            R_values,
        ),
    )


def post_exit_scaled_perron_report(
    configurations: tuple[tuple[int, int], ...] = ((10, 3), (12, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    iterations: int = 80,
    tolerance: float = 1e-10,
) -> PostExitScaledPerronReport:
    levels = tuple(
        post_exit_scaled_perron_level(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
            iterations=iterations,
            tolerance=tolerance,
        )
        for mod2_power, mod3_power in configurations
    )
    if all(
        level.infinite_ratio_rows == 0
        and level.finite_ratio_max is not None
        and level.finite_ratio_max < 1.0
        for level in levels
    ):
        status = "finite_scaled_perron_pointwise_contraction_candidates"
    else:
        status = "finite_scaled_perron_has_obstructions_or_zero_weight_edges"
    return PostExitScaledPerronReport(
        type="post_exit_scaled_perron_report",
        status=status,
        levels=levels,
    )


def post_exit_super_eigen_level(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    power_iterations: int = 120,
    extension_iterations: int = 400,
    alpha_margin: float = 0.02,
    tolerance: float = 1e-10,
    scc_state_limit: int = 1_000_000,
) -> PostExitSuperEigenLevel:
    denominator = 1 << sample_lift_power
    (
        targets,
        descended,
        reentered,
        out_of_range,
        max_survival,
        worst_index,
    ) = _build_post_exit_target_array(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
    )
    (
        _,
        scale,
        finite_ratio_max,
        _,
        zero_weight_rows,
        _,
        _,
    ) = _right_power_scaled_ratios(
        targets=targets,
        denominator=denominator,
        iterations=power_iterations,
        tolerance=tolerance,
    )
    recurrent_ratio = max(scale, finite_ratio_max or 0.0)
    alpha = min(0.999999, recurrent_ratio + alpha_margin)
    (
        vector,
        ratios,
        iterations_used,
        converged,
        residual,
        worst_ratio_index,
    ) = _positive_resolvent_super_vector(
        targets=targets,
        denominator=denominator,
        alpha=alpha,
        iterations=extension_iterations,
        tolerance=tolerance,
    )
    recurrent_sccs, closed_sccs, sccs_skipped = _scc_counts(
        targets,
        state_limit=scc_state_limit,
    )
    rho = Fraction(max_survival, denominator)
    return PostExitSuperEigenLevel(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        states=targets.shape[0],
        row_denominator=denominator,
        recurrent_ratio_estimate=recurrent_ratio,
        alpha=alpha,
        alpha_margin=alpha_margin,
        iterations=iterations_used,
        converged=converged,
        residual=residual,
        lambda_super=float(ratios.max(initial=0.0)),
        finite_ratio_min=float(ratios.min()) if ratios.size else 0.0,
        finite_ratio_max=float(ratios.max()) if ratios.size else 0.0,
        positive_min=float(vector.min()) if vector.size else 0.0,
        positive_max=float(vector.max()) if vector.size else 0.0,
        recurrent_sccs=recurrent_sccs,
        closed_sccs=closed_sccs,
        sccs_skipped=sccs_skipped,
        descended_samples=descended,
        reentry_samples=reentered,
        out_of_range_reentry_samples=out_of_range,
        constant_weight_rho_max_num=rho.numerator,
        constant_weight_rho_max_den=rho.denominator,
        worst_state=None
        if worst_index is None
        else _decode_state_index(worst_index, mod2_power, mod3_power, R_values),
        worst_transient_state=_decode_state_index(
            worst_ratio_index,
            mod2_power,
            mod3_power,
            R_values,
        )
        if zero_weight_rows
        else None,
    )


def post_exit_super_eigen_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 2), (10, 3), (12, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    power_iterations: int = 120,
    extension_iterations: int = 400,
    alpha_margin: float = 0.02,
    tolerance: float = 1e-10,
    scc_state_limit: int = 1_000_000,
) -> PostExitSuperEigenReport:
    levels = tuple(
        post_exit_super_eigen_level(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
            power_iterations=power_iterations,
            extension_iterations=extension_iterations,
            alpha_margin=alpha_margin,
            tolerance=tolerance,
            scc_state_limit=scc_state_limit,
        )
        for mod2_power, mod3_power in configurations
    )
    if all(level.lambda_super < 1.0 and level.positive_min > 0.0 for level in levels):
        status = "finite_positive_super_eigenvector_candidates"
    else:
        status = "finite_super_eigenvector_has_obstructions"
    return PostExitSuperEigenReport(
        type="post_exit_super_eigenvector_report",
        status=status,
        levels=levels,
    )
