"""Finite post-exit Lyapunov artifacts built from the mixed Hodge potential."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from .mixed_harmonic_class import obstruction_lyapunov_correction_report
from .post_exit_map import (
    PostExitState,
    _iter_post_exit_states,
    _sample_u_values,
    post_exit_transition_sample,
)


@dataclass(frozen=True)
class PsiLinearFit:
    name: str
    samples: int
    features: tuple[str, ...]
    coefficients: tuple[float, ...]
    r_squared: float
    max_abs_residual: float
    rms_residual: float

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["features"] = list(self.features)
        data["coefficients"] = list(self.coefficients)
        return data


@dataclass(frozen=True)
class PsiSymbolicFitReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    sample_lift_power: int
    entries: int
    raw_integer_fraction_1e8: float
    centered_integer_fraction_1e8: float
    best_integer_offset: float
    value_min: float
    value_max: float
    rounded_value_histogram: tuple[tuple[int, int], ...]
    fits: tuple[PsiLinearFit, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "sample_lift_power": self.sample_lift_power,
            "entries": self.entries,
            "raw_integer_fraction_1e8": self.raw_integer_fraction_1e8,
            "centered_integer_fraction_1e8": self.centered_integer_fraction_1e8,
            "best_integer_offset": self.best_integer_offset,
            "value_min": self.value_min,
            "value_max": self.value_max,
            "rounded_value_histogram": [
                list(item) for item in self.rounded_value_histogram
            ],
            "fits": [fit.to_json_dict() for fit in self.fits],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class UnifiedLyapunovTrajectoryCheck:
    samples: int
    descended: int
    reentered: int
    out_of_window: int
    violations: int
    min_decrement: float | None
    mean_decrement: float | None
    worst_delta: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UnifiedLyapunovLPReport:
    type: str
    status: str
    height_mode: str
    drift_coefficient: float
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    states: int
    transitions_checked: int
    descended_samples: int
    reentry_constraints: int
    out_of_window_samples: int
    lp_success: bool
    lp_status: int
    lp_message: str
    alpha_bound: float
    beta_bound: float
    gamma_bound: float
    include_debt_term: bool
    alpha: float | None
    beta: float | None
    gamma: float | None
    epsilon: float | None
    relaxed_alpha: float | None
    relaxed_beta: float | None
    relaxed_max_delta: float | None
    max_delta_on_constraints: float | None
    worst_constraint_state: dict[str, Any] | None
    trajectory_check: UnifiedLyapunovTrajectoryCheck | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "height_mode": self.height_mode,
            "drift_coefficient": self.drift_coefficient,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "states": self.states,
            "transitions_checked": self.transitions_checked,
            "descended_samples": self.descended_samples,
            "reentry_constraints": self.reentry_constraints,
            "out_of_window_samples": self.out_of_window_samples,
            "lp_success": self.lp_success,
            "lp_status": self.lp_status,
            "lp_message": self.lp_message,
            "alpha_bound": self.alpha_bound,
            "beta_bound": self.beta_bound,
            "gamma_bound": self.gamma_bound,
            "include_debt_term": self.include_debt_term,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "relaxed_alpha": self.relaxed_alpha,
            "relaxed_beta": self.relaxed_beta,
            "relaxed_max_delta": self.relaxed_max_delta,
            "max_delta_on_constraints": self.max_delta_on_constraints,
            "worst_constraint_state": self.worst_constraint_state,
            "trajectory_check": None
            if self.trajectory_check is None
            else self.trajectory_check.to_json_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class DPELevelReport:
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    transitions_checked: int
    descended_samples: int
    reentry_samples: int
    out_of_window_samples: int
    min_D_PE: float | None
    max_D_PE: float | None
    mean_D_PE: float | None
    terminal_min_D_PE: float | None
    terminal_max_D_PE: float | None
    terminal_mean_D_PE: float | None
    min_m_PE: int | None
    max_m_PE: int | None
    worst_edge_by_max_D_PE: dict[str, Any] | None
    histogram_bin_width: float
    histogram: tuple[tuple[float, int], ...]
    envelope_points: tuple[tuple[int, float], ...]
    conjecture_alpha: float | None
    conjecture_c: float | None
    conjecture_holds_on_envelope: bool | None
    conjecture_max_violation: float | None

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["histogram"] = [list(item) for item in self.histogram]
        data["envelope_points"] = [list(item) for item in self.envelope_points]
        return data


@dataclass(frozen=True)
class DPEStructuralBoundReport:
    type: str
    status: str
    levels: tuple[DPELevelReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class StateDebtLyapunovReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    bucket_width: float
    bucket_min: int | None
    bucket_max: int | None
    base_states: int
    augmented_state_upper_bound: int
    transitions_checked: int
    descended_samples: int
    reentry_constraints: int
    out_of_window_samples: int
    lp_success: bool
    lp_status: int
    lp_message: str
    alpha: float | None
    beta: float | None
    gamma: float | None
    epsilon: float | None
    max_delta_on_constraints: float | None
    worst_constraint_state: dict[str, Any] | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _v2_capped(value: int, cap: int) -> int:
    if value == 0:
        return cap
    exponent = 0
    while exponent < cap and value % (1 << (exponent + 1)) == 0:
        exponent += 1
    return exponent


def _v3_capped(value: int, cap: int) -> int:
    if value == 0:
        return cap
    exponent = 0
    divisor = 3
    while exponent < cap and value % divisor == 0:
        exponent += 1
        divisor *= 3
    return exponent


def _tail_vertex_from_state(
    state: PostExitState,
    mod2_power: int,
    mod3_power: int,
) -> tuple[int, int]:
    return (
        ((state.u_mod2 << state.R) - 1) % (1 << mod2_power),
        ((1 << state.R) * state.u_mod3 - 1) % (3**mod3_power),
    )


def _potential_map(
    mod2_power: int,
    mod3_power: int,
    sample_lift_power: int,
) -> dict[tuple[int, int], float]:
    report = obstruction_lyapunov_correction_report(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        trajectory_samples=32,
    )
    return {
        (int(r2), int(r3)): float(value)
        for r2, r3, value in report.potential_entries
    }


def _linear_fit(name: str, features: tuple[str, ...], rows, values) -> PsiLinearFit:
    import numpy as np

    matrix = np.asarray(rows, dtype=float)
    y = np.asarray(values, dtype=float)
    coefficients, *_ = np.linalg.lstsq(matrix, y, rcond=None)
    fitted = matrix @ coefficients
    residual = y - fitted
    ss_res = float(np.dot(residual, residual))
    centered = y - float(np.mean(y))
    ss_tot = float(np.dot(centered, centered))
    r_squared = 1.0 if ss_tot == 0.0 else 1.0 - ss_res / ss_tot
    return PsiLinearFit(
        name=name,
        samples=len(values),
        features=features,
        coefficients=tuple(float(value) for value in coefficients),
        r_squared=float(r_squared),
        max_abs_residual=float(np.max(np.abs(residual), initial=0.0)),
        rms_residual=float(math.sqrt(ss_res / len(values))) if len(values) else 0.0,
    )


def psi_symbolic_fit_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    sample_lift_power: int = 2,
) -> PsiSymbolicFitReport:
    """Fit the finite Hodge potential against simple mixed-adic features."""

    import numpy as np

    potential = _potential_map(mod2_power, mod3_power, sample_lift_power)
    values = np.asarray(list(potential.values()), dtype=float)
    raw_close = np.abs(values - np.rint(values)) <= 1e-8
    fractional_offsets = values - np.rint(values)
    best_offset = float(np.median(fractional_offsets)) if values.size else 0.0
    centered = values - best_offset
    centered_close = np.abs(centered - np.rint(centered)) <= 1e-8
    rounded = np.rint(centered).astype(int)
    histogram_counts: dict[int, int] = {}
    for value in rounded:
        histogram_counts[int(value)] = histogram_counts.get(int(value), 0) + 1
    histogram = tuple(sorted(histogram_counts.items()))

    rows_basic: list[list[float]] = []
    rows_obstruction: list[list[float]] = []
    fit_values: list[float] = []
    modulus2 = 1 << mod2_power
    modulus3 = 3**mod3_power
    for (r2, r3), value in potential.items():
        tail_raw = (r2 + 1) % modulus2
        R = _v2_capped(tail_raw, mod2_power)
        if R < mod2_power:
            u2_width = mod2_power - R
            u2 = ((r2 + 1) >> R) % (1 << u2_width)
            v2_u_minus_7 = _v2_capped((u2 - 7) % (1 << u2_width), u2_width)
        else:
            v2_u_minus_7 = 0
        inverse = pow(pow(2, R, modulus3), -1, modulus3)
        u3 = ((r3 + 1) * inverse) % modulus3
        v3_u = _v3_capped(u3, mod3_power)
        obstruction = 1.0 if R == 2 and v2_u_minus_7 >= min(6, mod2_power - 2) and v3_u >= 2 else 0.0
        rows_basic.append([1.0, float(R), float(v3_u), float(v2_u_minus_7)])
        rows_obstruction.append(
            [1.0, float(R), float(v3_u), float(v2_u_minus_7), obstruction]
        )
        fit_values.append(value)

    fits = (
        _linear_fit(
            name="intercept_plus_tail_depth_v3u_v2u_minus_7",
            features=("1", "R_cap", "v3(u)", "v2(u2_minus_7)"),
            rows=rows_basic,
            values=fit_values,
        ),
        _linear_fit(
            name="basic_plus_obstruction_indicator",
            features=("1", "R_cap", "v3(u)", "v2(u2_minus_7)", "obstruction"),
            rows=rows_obstruction,
            values=fit_values,
        ),
    )
    return PsiSymbolicFitReport(
        type="psi_symbolic_fit",
        status="finite_hodge_potential_fit_not_closed_form_proof",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        sample_lift_power=sample_lift_power,
        entries=len(potential),
        raw_integer_fraction_1e8=float(np.mean(raw_close)) if values.size else 0.0,
        centered_integer_fraction_1e8=float(np.mean(centered_close))
        if values.size
        else 0.0,
        best_integer_offset=best_offset,
        value_min=float(np.min(values, initial=0.0)),
        value_max=float(np.max(values, initial=0.0)),
        rounded_value_histogram=histogram,
        fits=fits,
    )


def unified_lyapunov_lp_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    alpha_bound: float = 16.0,
    beta_bound: float = 16.0,
    gamma_bound: float = 16.0,
    trajectory_samples: int = 1000,
    random_seed: int = 0,
    height_mode: str = "raw_log2",
    include_debt_term: bool = False,
) -> UnifiedLyapunovLPReport:
    """Solve a finite LP for post-exit Lyapunov candidates.

    ``height_mode="renormalized_3_over_2"`` is the literal proposed
    ``log2(n) - R*log2(3/2)`` convention. The ``plus_*`` modes use the same
    drift with the opposite sign, which is the decreasing convention for
    target-minus-source LP inequalities when tail depth drops.

    If ``include_debt_term`` is true, the LP adds ``gamma*D_PE`` per edge,
    where ``D_PE = A_PE - m_PE*log2(3)`` is the exact post-exit debt for that
    transition. This is an edge-debt diagnostic; the fully formal version
    should bucket ``D_PE`` into the PECM state.
    """

    import numpy as np
    from scipy.optimize import linprog

    potential = _potential_map(mod2_power, mod3_power, sample_lift_power)
    if height_mode == "raw_log2":
        drift = 0.0
    elif height_mode == "renormalized_3_over_2":
        drift = math.log2(1.5)
    elif height_mode == "renormalized_plus_3_over_2":
        drift = -math.log2(1.5)
    elif height_mode == "renormalized_plus_log2_3":
        drift = -math.log2(3.0)
    else:
        raise ValueError(
            "height_mode must be 'raw_log2', 'renormalized_3_over_2', "
            "'renormalized_plus_3_over_2', or 'renormalized_plus_log2_3'"
        )
    R_set = set(R_values)
    states = 0
    transitions_checked = 0
    descended = 0
    out_of_window = 0
    rows: list[list[float]] = []
    rhs: list[float] = []
    metadata: list[dict[str, Any]] = []
    for state in _iter_post_exit_states(mod2_power, mod3_power, R_values):
        states += 1
        source_psi = potential.get(
            _tail_vertex_from_state(state, mod2_power, mod3_power),
            0.0,
        )
        for u in _sample_u_values(state, sample_lift_power):
            transitions_checked += 1
            transition = post_exit_transition_sample(state, u, max_steps=max_steps)
            if transition.status.startswith("descended"):
                descended += 1
                continue
            if (
                transition.target is None
                or transition.target.R not in R_set
                or not transition.status.startswith("reentered_tail")
            ):
                out_of_window += 1
                continue
            target = transition.target
            target_psi = potential.get(
                _tail_vertex_from_state(target, mod2_power, mod3_power),
                0.0,
            )
            psi_delta = target_psi - source_psi
            R_delta = target.R - state.R
            log_delta = math.log2(transition.landing) - math.log2(transition.n0)
            height_delta = log_delta - drift * R_delta
            debt = -transition.debt_against_start
            if include_debt_term:
                rows.append([psi_delta, -float(R_delta), debt, 1.0])
            else:
                rows.append([psi_delta, -float(R_delta), 1.0])
            rhs.append(-height_delta)
            metadata.append(
                {
                    "source": state.to_json_dict(),
                    "target": target.to_json_dict(),
                    "u": u,
                    "landing": transition.landing,
                    "n0": transition.n0,
                    "log_delta": log_delta,
                    "height_delta": height_delta,
                    "psi_delta": psi_delta,
                    "R_delta": R_delta,
                    "post_exit_debt": debt,
                    "steps": transition.steps,
                    "total_A": transition.total_A,
                }
            )

    if not rows:
        return UnifiedLyapunovLPReport(
            type="unified_lyapunov_lp",
            status="no_reentry_constraints",
            height_mode=height_mode,
            drift_coefficient=drift,
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_min=min(R_values),
            R_max=max(R_values),
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            states=states,
            transitions_checked=transitions_checked,
            descended_samples=descended,
            reentry_constraints=0,
            out_of_window_samples=out_of_window,
            lp_success=False,
            lp_status=-1,
            lp_message="no in-window reentry constraints were generated",
            alpha_bound=alpha_bound,
            beta_bound=beta_bound,
            gamma_bound=gamma_bound,
            include_debt_term=include_debt_term,
            alpha=None,
            beta=None,
            gamma=None,
            epsilon=None,
            relaxed_alpha=None,
            relaxed_beta=None,
            relaxed_max_delta=None,
            max_delta_on_constraints=None,
            worst_constraint_state=None,
            trajectory_check=None,
        )

    A_ub = np.asarray(rows, dtype=float)
    b_ub = np.asarray(rhs, dtype=float)
    if include_debt_term:
        objective = np.array([0.0, 0.0, 0.0, -1.0])
        bounds = (
            (0.0, alpha_bound),
            (0.0, beta_bound),
            (0.0, gamma_bound),
            (0.0, None),
        )
        relaxed_A = np.column_stack(
            (
                A_ub[:, 0],
                A_ub[:, 1],
                A_ub[:, 2],
                -np.ones(A_ub.shape[0]),
            )
        )
        relaxed_objective = np.array([0.0, 0.0, 0.0, 1.0])
        relaxed_bounds = (
            (0.0, alpha_bound),
            (0.0, beta_bound),
            (0.0, gamma_bound),
            (None, None),
        )
    else:
        objective = np.array([0.0, 0.0, -1.0])
        bounds = ((0.0, alpha_bound), (0.0, beta_bound), (0.0, None))
        relaxed_A = np.column_stack(
            (A_ub[:, 0], A_ub[:, 1], -np.ones(A_ub.shape[0]))
        )
        relaxed_objective = np.array([0.0, 0.0, 1.0])
        relaxed_bounds = ((0.0, alpha_bound), (0.0, beta_bound), (None, None))
    result = linprog(
        c=objective,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method="highs",
    )
    alpha = beta = gamma = epsilon = None
    relaxed_alpha = relaxed_beta = relaxed_max_delta = None
    max_delta = None
    worst_state = None
    trajectory_check = None
    relaxed = linprog(
        c=relaxed_objective,
        A_ub=relaxed_A,
        b_ub=b_ub,
        bounds=relaxed_bounds,
        method="highs",
    )
    if relaxed.success:
        relaxed_alpha = float(relaxed.x[0])
        relaxed_beta = float(relaxed.x[1])
        relaxed_max_delta = float(relaxed.x[-1])
        relaxed_deltas = A_ub[:, :-1] @ relaxed.x[:-1] - b_ub
        relaxed_worst_index = int(np.argmax(relaxed_deltas))
        worst_state = metadata[relaxed_worst_index]
    if result.success:
        alpha = float(result.x[0])
        beta = float(result.x[1])
        if include_debt_term:
            gamma = float(result.x[2])
        epsilon = float(result.x[-1])
        deltas = A_ub[:, :-1] @ result.x[:-1] - b_ub
        worst_index = int(np.argmax(deltas))
        max_delta = float(deltas[worst_index])
        worst_state = metadata[worst_index]
        rng = random.Random(random_seed)
        state_list = tuple(_iter_post_exit_states(mod2_power, mod3_power, R_values))
        checks: list[float] = []
        check_descended = 0
        check_reentered = 0
        check_out = 0
        violations = 0
        attempts = 0
        while len(checks) + check_descended + check_out < trajectory_samples and attempts < trajectory_samples * 20:
            attempts += 1
            state = rng.choice(state_list)
            if state.R == 2 and state.u_mod2 % (1 << mod2_power) == 7 and state.u_mod3 % 9 == 0:
                continue
            u = rng.choice(_sample_u_values(state, sample_lift_power))
            transition = post_exit_transition_sample(state, u, max_steps=max_steps)
            if transition.status.startswith("descended"):
                check_descended += 1
                continue
            if (
                transition.target is None
                or transition.target.R not in R_set
                or not transition.status.startswith("reentered_tail")
            ):
                check_out += 1
                continue
            source_psi = potential.get(
                _tail_vertex_from_state(state, mod2_power, mod3_power),
                0.0,
            )
            target_psi = potential.get(
                _tail_vertex_from_state(transition.target, mod2_power, mod3_power),
                0.0,
            )
            delta = (
                math.log2(transition.landing)
                - math.log2(transition.n0)
                - drift * (transition.target.R - state.R)
                + alpha * (target_psi - source_psi)
                - beta * (transition.target.R - state.R)
                + (0.0 if gamma is None else gamma * (-transition.debt_against_start))
            )
            check_reentered += 1
            checks.append(-delta)
            if delta > 1e-9:
                violations += 1
        trajectory_check = UnifiedLyapunovTrajectoryCheck(
            samples=trajectory_samples,
            descended=check_descended,
            reentered=check_reentered,
            out_of_window=check_out,
            violations=violations,
            min_decrement=None if not checks else min(checks),
            mean_decrement=None if not checks else sum(checks) / len(checks),
            worst_delta=None if not checks else -min(checks),
        )

    status = (
        "finite_unified_lyapunov_lp_feasible_not_global_proof"
        if result.success and epsilon is not None and epsilon > 1e-9
        else "finite_unified_lyapunov_lp_infeasible_or_zero_margin"
    )
    return UnifiedLyapunovLPReport(
        type="unified_lyapunov_lp",
        status=status,
        height_mode=height_mode,
        drift_coefficient=drift,
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        states=states,
        transitions_checked=transitions_checked,
        descended_samples=descended,
        reentry_constraints=len(rows),
        out_of_window_samples=out_of_window,
        lp_success=bool(result.success),
        lp_status=int(result.status),
        lp_message=str(result.message),
        alpha_bound=alpha_bound,
        beta_bound=beta_bound,
        gamma_bound=gamma_bound,
        include_debt_term=include_debt_term,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        epsilon=epsilon,
        relaxed_alpha=relaxed_alpha,
        relaxed_beta=relaxed_beta,
        relaxed_max_delta=relaxed_max_delta,
        max_delta_on_constraints=max_delta,
        worst_constraint_state=worst_state,
        trajectory_check=trajectory_check,
    )


def _dpe_level_report(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
    histogram_bin_width: float,
) -> DPELevelReport:
    import numpy as np

    if histogram_bin_width <= 0.0:
        raise ValueError("histogram_bin_width must be positive")
    R_set = set(R_values)
    transitions_checked = 0
    descended = 0
    reentered = 0
    out_of_window = 0
    debts: list[float] = []
    terminal_debts: list[float] = []
    m_values: list[int] = []
    histogram_counts: dict[float, int] = {}
    envelope: dict[int, float] = {}
    min_debt: float | None = None
    max_debt: float | None = None
    worst: dict[str, Any] | None = None
    for state in _iter_post_exit_states(mod2_power, mod3_power, R_values):
        for u in _sample_u_values(state, sample_lift_power):
            transitions_checked += 1
            transition = post_exit_transition_sample(state, u, max_steps=max_steps)
            debt = -transition.debt_against_start
            m_pe = state.R - 1 + transition.steps
            if transition.status.startswith("descended"):
                descended += 1
                terminal_debts.append(debt)
                continue
            elif (
                transition.target is not None
                and transition.target.R in R_set
                and transition.status.startswith("reentered_tail")
            ):
                reentered += 1
            else:
                out_of_window += 1
                continue
            debts.append(debt)
            m_values.append(m_pe)
            bin_center = round(
                math.floor(debt / histogram_bin_width) * histogram_bin_width,
                10,
            )
            histogram_counts[bin_center] = histogram_counts.get(bin_center, 0) + 1
            if m_pe not in envelope or debt > envelope[m_pe]:
                envelope[m_pe] = debt
            if min_debt is None or debt < min_debt:
                min_debt = debt
            if max_debt is None or debt > max_debt:
                max_debt = debt
                worst = {
                    "source": state.to_json_dict(),
                    "target": None
                    if transition.target is None
                    else transition.target.to_json_dict(),
                    "status": transition.status,
                    "u": u,
                    "n0": transition.n0,
                    "landing": transition.landing,
                    "D_PE": debt,
                    "m_PE": m_pe,
                    "steps": transition.steps,
                    "total_A": transition.total_A,
                    "log_delta": math.log2(transition.landing)
                    - math.log2(transition.n0),
                }

    envelope_points = tuple(sorted(envelope.items()))
    alpha = c = max_violation = None
    holds = None
    positive_points = [(m, -debt) for m, debt in envelope_points if debt < 0.0]
    if len(positive_points) >= 2:
        xs = np.log(np.asarray([m for m, _ in positive_points], dtype=float))
        ys = np.log(np.asarray([surplus for _, surplus in positive_points], dtype=float))
        slope, intercept = np.polyfit(xs, ys, deg=1)
        alpha = max(0.0, float(slope))
        raw_c = float(math.exp(intercept))
        # Use the largest c that is actually certified by the finite envelope.
        c = min(surplus / (m**alpha) for m, surplus in positive_points)
        violations = [
            debt + c * (m**alpha)
            for m, debt in envelope_points
        ]
        max_violation = max(violations, default=0.0)
        holds = max_violation <= 1e-10 and raw_c > 0.0
    histogram = tuple(sorted(histogram_counts.items()))
    return DPELevelReport(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        transitions_checked=transitions_checked,
        descended_samples=descended,
        reentry_samples=reentered,
        out_of_window_samples=out_of_window,
        min_D_PE=min_debt,
        max_D_PE=max_debt,
        mean_D_PE=None if not debts else float(sum(debts) / len(debts)),
        terminal_min_D_PE=None if not terminal_debts else min(terminal_debts),
        terminal_max_D_PE=None if not terminal_debts else max(terminal_debts),
        terminal_mean_D_PE=None
        if not terminal_debts
        else float(sum(terminal_debts) / len(terminal_debts)),
        min_m_PE=None if not m_values else min(m_values),
        max_m_PE=None if not m_values else max(m_values),
        worst_edge_by_max_D_PE=worst,
        histogram_bin_width=histogram_bin_width,
        histogram=histogram,
        envelope_points=tuple((int(m), float(debt)) for m, debt in envelope_points),
        conjecture_alpha=alpha,
        conjecture_c=c,
        conjecture_holds_on_envelope=holds,
        conjecture_max_violation=max_violation,
    )


def dpe_structural_bound_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 3), (10, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    histogram_bin_width: float = 0.1,
) -> DPEStructuralBoundReport:
    """Enumerate finite PECM edge debts and fit a structural debt envelope."""

    levels = tuple(
        _dpe_level_report(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            histogram_bin_width=histogram_bin_width,
        )
        for mod2_power, mod3_power in configurations
    )
    if all(
        level.max_D_PE is not None
        and level.max_D_PE < 0.0
        and not level.out_of_window_samples
        for level in levels
    ):
        status = "finite_all_pecm_edges_have_negative_D_PE_not_global_proof"
    else:
        status = "finite_D_PE_scan_has_nonnegative_or_unresolved_edges"
    return DPEStructuralBoundReport(
        type="d_pe_structural_bound",
        status=status,
        levels=levels,
    )


def state_debt_lyapunov_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    bucket_width: float = 0.1,
    alpha_bound: float = 16.0,
    beta_bound: float = 16.0,
    gamma_bound: float = 16.0,
) -> StateDebtLyapunovReport:
    """Solve the finite LP after promoting post-exit debt to a bucketed state.

    This uses a cumulative bucket convention: the target debt bucket changes by
    ``round(D_PE / bucket_width)`` across an edge. Therefore the Lyapunov
    difference contains the state term ``gamma * bucket_delta * bucket_width``.
    """

    import numpy as np
    from scipy.optimize import linprog

    if bucket_width <= 0.0:
        raise ValueError("bucket_width must be positive")
    potential = _potential_map(mod2_power, mod3_power, sample_lift_power)
    R_set = set(R_values)
    transitions_checked = 0
    descended = 0
    out_of_window = 0
    rows: list[list[float]] = []
    rhs: list[float] = []
    metadata: list[dict[str, Any]] = []
    bucket_min: int | None = None
    bucket_max: int | None = None
    base_states = 0
    for state in _iter_post_exit_states(mod2_power, mod3_power, R_values):
        base_states += 1
        source_psi = potential.get(
            _tail_vertex_from_state(state, mod2_power, mod3_power),
            0.0,
        )
        for u in _sample_u_values(state, sample_lift_power):
            transitions_checked += 1
            transition = post_exit_transition_sample(state, u, max_steps=max_steps)
            if transition.status.startswith("descended"):
                descended += 1
                continue
            if (
                transition.target is None
                or transition.target.R not in R_set
                or not transition.status.startswith("reentered_tail")
            ):
                out_of_window += 1
                continue
            target = transition.target
            target_psi = potential.get(
                _tail_vertex_from_state(target, mod2_power, mod3_power),
                0.0,
            )
            debt = -transition.debt_against_start
            bucket_delta = int(round(debt / bucket_width))
            bucket_value = bucket_delta * bucket_width
            bucket_min = bucket_delta if bucket_min is None else min(bucket_min, bucket_delta)
            bucket_max = bucket_delta if bucket_max is None else max(bucket_max, bucket_delta)
            R_delta = target.R - state.R
            log_delta = math.log2(transition.landing) - math.log2(transition.n0)
            rows.append(
                [
                    target_psi - source_psi,
                    -float(R_delta),
                    bucket_value,
                    1.0,
                ]
            )
            rhs.append(-log_delta)
            metadata.append(
                {
                    "source": state.to_json_dict(),
                    "target": target.to_json_dict(),
                    "u": u,
                    "n0": transition.n0,
                    "landing": transition.landing,
                    "log_delta": log_delta,
                    "D_PE": debt,
                    "D_bucket": bucket_delta,
                    "D_bucket_value": bucket_value,
                    "R_delta": R_delta,
                    "steps": transition.steps,
                    "total_A": transition.total_A,
                }
            )
    bucket_count = 0 if bucket_min is None or bucket_max is None else bucket_max - bucket_min + 1
    augmented_bound = base_states * max(1, bucket_count)
    if not rows:
        return StateDebtLyapunovReport(
            type="unified_lyapunov_state_debt",
            status="no_reentry_constraints",
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_min=min(R_values),
            R_max=max(R_values),
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            bucket_width=bucket_width,
            bucket_min=bucket_min,
            bucket_max=bucket_max,
            base_states=base_states,
            augmented_state_upper_bound=augmented_bound,
            transitions_checked=transitions_checked,
            descended_samples=descended,
            reentry_constraints=0,
            out_of_window_samples=out_of_window,
            lp_success=False,
            lp_status=-1,
            lp_message="no in-window reentry constraints were generated",
            alpha=None,
            beta=None,
            gamma=None,
            epsilon=None,
            max_delta_on_constraints=None,
            worst_constraint_state=None,
        )
    A_ub = np.asarray(rows, dtype=float)
    b_ub = np.asarray(rhs, dtype=float)
    result = linprog(
        c=np.array([0.0, 0.0, 0.0, -1.0]),
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=(
            (0.0, alpha_bound),
            (0.0, beta_bound),
            (0.0, gamma_bound),
            (0.0, None),
        ),
        method="highs",
    )
    alpha = beta = gamma = epsilon = max_delta = None
    worst_state = None
    if result.success:
        alpha = float(result.x[0])
        beta = float(result.x[1])
        gamma = float(result.x[2])
        epsilon = float(result.x[3])
        deltas = A_ub[:, :-1] @ result.x[:-1] - b_ub
        worst_index = int(np.argmax(deltas))
        max_delta = float(deltas[worst_index])
        worst_state = metadata[worst_index]
    status = (
        "finite_bucketed_state_debt_lyapunov_feasible_not_global_proof"
        if result.success and epsilon is not None and epsilon > 1e-9
        else "finite_bucketed_state_debt_lyapunov_infeasible_or_zero_margin"
    )
    return StateDebtLyapunovReport(
        type="unified_lyapunov_state_debt",
        status=status,
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        bucket_width=bucket_width,
        bucket_min=bucket_min,
        bucket_max=bucket_max,
        base_states=base_states,
        augmented_state_upper_bound=augmented_bound,
        transitions_checked=transitions_checked,
        descended_samples=descended,
        reentry_constraints=len(rows),
        out_of_window_samples=out_of_window,
        lp_success=bool(result.success),
        lp_status=int(result.status),
        lp_message=str(result.message),
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        epsilon=epsilon,
        max_delta_on_constraints=max_delta,
        worst_constraint_state=worst_state,
    )
