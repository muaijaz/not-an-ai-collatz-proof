"""Cross-resolution stability diagnostics for PECM Lyapunov vectors.

The primary report in this module deliberately constructs one operator at the
finest requested mixed-adic level and derives every coarser operator by exact
Galerkin coarsening.  This makes the averaged identity

``A K_f I = K_c``

true by construction.  Independently sampled PECM levels are retained only as
an explicitly labeled legacy diagnostic, because their fixed CRT lift windows
do not form a projective operator ladder.

All operator-intertwining defects are exact rational quantities.  Resolvent
vectors and their cross-resolution log profiles remain ``float64`` numerical
diagnostics; this module does not claim an exact Lyapunov certificate or a
proof of Collatz.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .pecm_refinement import (
    MixedAdicLevel,
    MixedAdicRefinement,
    UniformTargetOperator,
    decode_state_index,
    diagnose_conditional_expectation_intertwining,
    diagnose_operator_intertwining,
    galerkin_coarsen,
)
from .pecm_vector_export import (
    pecm_state_order_hash,
    positive_resolvent_vector,
)
from .post_exit_map import _build_post_exit_target_array


_DEFAULT_LEVELS = ((4, 0), (6, 1), (8, 2))
_DEFAULT_R_VALUES = tuple(range(2, 31))
_DEFAULT_QUANTILES = (0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0)
_DEFAULT_MAX_MATERIALIZED_STATES = 250_000
_DEFAULT_MAX_MATERIALIZED_TRANSITIONS = 2_000_000


def _level_pair(level: MixedAdicLevel) -> list[int]:
    return [level.mod2_power, level.mod3_power]


def _pair_key(coarse: MixedAdicLevel, fine: MixedAdicLevel) -> str:
    return (
        f"{coarse.mod2_power}:{coarse.mod3_power}"
        f"->{fine.mod2_power}:{fine.mod3_power}"
    )


def _quantile_key(value: float) -> str:
    return f"{value:g}"


def _quantiles(
    values: Sequence[float],
    quantile_levels: tuple[float, ...] = _DEFAULT_QUANTILES,
) -> dict[str, float] | None:
    """Return deterministic linear quantiles, or ``None`` for an empty set."""

    if not values:
        return None
    import numpy as np

    array = np.asarray(values, dtype=np.float64)
    if not bool(np.isfinite(array).all()):
        raise ValueError("quantile values must be finite")
    result = np.quantile(array, quantile_levels, method="linear")
    return {
        _quantile_key(level): float(value)
        for level, value in zip(quantile_levels, result, strict=True)
    }


def _validate_positive_vector(
    values: Sequence[float],
    expected_length: int,
    label: str,
):
    import numpy as np

    array = np.asarray(values, dtype=np.float64)
    if array.shape != (expected_length,):
        raise ValueError(
            f"{label} has shape {array.shape}, expected ({expected_length},)"
        )
    if not bool(np.isfinite(array).all()) or bool((array <= 0.0).any()):
        raise ValueError(f"{label} must contain only finite positive values")
    return array


@dataclass(frozen=True)
class LiftConsistencyProfile:
    """Chebyshev-aligned log-vector comparison across one refinement."""

    coarse_level: MixedAdicLevel
    fine_level: MixedAdicLevel
    fiber_size: int
    errors: dict[str, float]
    optimal_additive_constants: dict[str, float]
    lift_spread_quantiles: dict[str, float]
    worst_coarse_states: tuple[dict[str, Any], ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "coarse_level": self.coarse_level.to_json_dict(),
            "fine_level": self.fine_level.to_json_dict(),
            "fiber_size": self.fiber_size,
            "errors": dict(self.errors),
            "optimal_additive_constants": dict(
                self.optimal_additive_constants
            ),
            "lift_spread_quantiles": dict(self.lift_spread_quantiles),
            "worst_coarse_states": [
                dict(record) for record in self.worst_coarse_states
            ],
        }


def lift_consistency_profile(
    refinement: MixedAdicRefinement,
    coarse_values: Sequence[float],
    fine_values: Sequence[float],
    *,
    worst_per_metric: int = 3,
) -> LiftConsistencyProfile:
    """Compare log weights using the exact minimax additive alignment.

    If ``d_x`` is the coarse log weight minus a chosen statistic of the fine
    lifts, then

    ``min_c max_x |d_x-c| = (max d_x-min d_x)/2``

    with optimizer ``c=(max d_x+min d_x)/2``.  Consequently the errors are
    invariant under independent positive rescaling of either input vector.
    """

    import numpy as np

    if worst_per_metric <= 0:
        raise ValueError("worst_per_metric must be positive")
    coarse = _validate_positive_vector(
        coarse_values,
        refinement.coarse.state_count,
        "coarse_values",
    )
    fine = _validate_positive_vector(
        fine_values,
        refinement.fine.state_count,
        "fine_values",
    )
    coarse_log = np.log(coarse)
    fine_log = np.log(fine)

    means = np.empty(refinement.coarse.state_count, dtype=np.float64)
    minima = np.empty_like(means)
    maxima = np.empty_like(means)
    spreads = np.empty_like(means)
    for coarse_index, children in enumerate(refinement.fibers()):
        lifted = fine_log[list(children)]
        means[coarse_index] = float(lifted.mean())
        minima[coarse_index] = float(lifted.min())
        maxima[coarse_index] = float(lifted.max())
        spreads[coarse_index] = maxima[coarse_index] - minima[coarse_index]

    errors: dict[str, float] = {}
    constants: dict[str, float] = {}
    worst: list[dict[str, Any]] = []
    for metric, aggregate in (
        ("mean", means),
        ("min", minima),
        ("max", maxima),
    ):
        differences = coarse_log - aggregate
        constant = 0.5 * (
            float(differences.max()) + float(differences.min())
        )
        residuals = differences - constant
        absolute = np.abs(residuals)
        errors[metric] = float(absolute.max())
        constants[metric] = constant
        worst_indices = sorted(
            range(refinement.coarse.state_count),
            key=lambda index: (-float(absolute[index]), index),
        )[:worst_per_metric]
        for coarse_index in worst_indices:
            state = decode_state_index(refinement.coarse, coarse_index)
            worst.append(
                {
                    "metric": metric,
                    "coarse_state_id": coarse_index,
                    "R": state.R,
                    "u_mod_2k": state.u_mod2,
                    "u_mod_3ell": state.u_mod3,
                    "signed_aligned_residual": float(residuals[coarse_index]),
                    "absolute_aligned_residual": float(absolute[coarse_index]),
                    "lift_log_spread": float(spreads[coarse_index]),
                }
            )

    spread_quantiles = _quantiles(spreads.tolist())
    assert spread_quantiles is not None
    return LiftConsistencyProfile(
        coarse_level=refinement.coarse,
        fine_level=refinement.fine,
        fiber_size=refinement.fiber_size,
        errors=errors,
        optimal_additive_constants=constants,
        lift_spread_quantiles=spread_quantiles,
        worst_coarse_states=tuple(worst),
    )


def sampled_branch_ratio_profile(
    refinement: MixedAdicRefinement,
    fine_operator: UniformTargetOperator,
    fine_values: Sequence[float],
    *,
    lambda_super: float,
) -> dict[str, Any]:
    """Measure live target-weight ratios on one finite operator.

    On the finest sampled operator these are concrete sampled Collatz branch
    ratios.  On a coarsened operator they are Galerkin-induced target ratios
    and are labeled as such in the result. Cemetery/descent samples have ratio
    zero and are counted separately. For every source with survival
    probability ``p > 0`` and live log-ratio spread ``delta``, the averaged
    row ratio ``q`` gives

    ``max_live_target_ratio <= q * exp(delta) / p``.

    The division by ``p`` is essential: killed siblings may otherwise make an
    averaged contraction look like a branchwise contraction.
    """

    import numpy as np

    fine = _validate_positive_vector(
        fine_values,
        refinement.fine.state_count,
        "fine_values",
    )
    if fine_operator.state_count != refinement.fine.state_count:
        raise ValueError("fine operator does not match the refinement")
    if not math.isfinite(lambda_super) or lambda_super < 0.0:
        raise ValueError("lambda_super must be finite and nonnegative")

    sample_count = fine_operator.sample_count
    within_source_spreads: list[float] = []
    coarse_fiber_logs: list[list[float]] = [
        [] for _ in range(refinement.coarse.state_count)
    ]
    live_target_samples = 0
    cemetery_samples = 0
    fully_killed_rows = 0
    actual_max_ratio: float | None = None
    derived_bound_max: float | None = None
    lambda_bound_max: float | None = None
    minimum_positive_survival: float | None = None
    maximum_averaged_row_ratio = 0.0

    for fine_source, row in enumerate(fine_operator.rows):
        ratios = [
            float(fine[target] / fine[fine_source])
            for target in row
            if target is not None
        ]
        cemetery_samples += sample_count - len(ratios)
        if not ratios:
            fully_killed_rows += 1
            continue
        if any(not math.isfinite(ratio) or ratio <= 0.0 for ratio in ratios):
            raise ValueError("surviving branch ratios must be finite and positive")
        live_target_samples += len(ratios)
        logs = [math.log(ratio) for ratio in ratios]
        spread = max(logs) - min(logs)
        within_source_spreads.append(spread)
        coarse_source = refinement.restrict_index(fine_source)
        coarse_fiber_logs[coarse_source].extend(logs)

        survival = len(ratios) / sample_count
        averaged_ratio = sum(ratios) / sample_count
        maximum_averaged_row_ratio = max(
            maximum_averaged_row_ratio,
            averaged_ratio,
        )
        derived_bound = averaged_ratio * math.exp(spread) / survival
        lambda_bound = lambda_super * math.exp(spread) / survival
        local_max = max(ratios)
        actual_max_ratio = (
            local_max
            if actual_max_ratio is None
            else max(actual_max_ratio, local_max)
        )
        derived_bound_max = (
            derived_bound
            if derived_bound_max is None
            else max(derived_bound_max, derived_bound)
        )
        lambda_bound_max = (
            lambda_bound
            if lambda_bound_max is None
            else max(lambda_bound_max, lambda_bound)
        )
        minimum_positive_survival = (
            survival
            if minimum_positive_survival is None
            else min(minimum_positive_survival, survival)
        )

    within_fiber_spreads = [
        max(logs) - min(logs)
        for logs in coarse_fiber_logs
        if logs
    ]
    numerical_tolerance = 1e-10 * max(1.0, lambda_super)
    if maximum_averaged_row_ratio > lambda_super + numerical_tolerance:
        raise ValueError(
            "lambda_super does not bound the computed averaged row ratios"
        )
    ratio_kind = (
        "concrete_finest_sample_branch_ratio"
        if fine_operator.label == "finest_independently_sampled_operator"
        else "galerkin_induced_target_ratio"
    )
    if live_target_samples:
        status = "finite_live_target_ratios_measured"
    else:
        status = "no_live_targets"
    return {
        "coarse_level": _level_pair(refinement.coarse),
        "fine_level": _level_pair(refinement.fine),
        "fine_operator_label": fine_operator.label,
        "ratio_kind": ratio_kind,
        "status": status,
        "live_target_samples": live_target_samples,
        "cemetery_or_descent_samples": cemetery_samples,
        "fully_killed_source_rows": fully_killed_rows,
        "minimum_positive_row_survival_probability": minimum_positive_survival,
        "max_live_target_ratio": actual_max_ratio,
        "live_targets_contract_pointwise": (
            None if actual_max_ratio is None else actual_max_ratio < 1.0
        ),
        "maximum_averaged_row_ratio": maximum_averaged_row_ratio,
        "rowwise_q_to_live_target_upper_bound": derived_bound_max,
        "rowwise_q_bound_margin_to_one": (
            None if derived_bound_max is None else 1.0 - derived_bound_max
        ),
        "rowwise_q_bound_below_one": (
            None if derived_bound_max is None else derived_bound_max < 1.0
        ),
        "global_lambda_to_live_target_upper_bound": lambda_bound_max,
        "global_lambda_bound_margin_to_one": (
            None if lambda_bound_max is None else 1.0 - lambda_bound_max
        ),
        "global_lambda_bound_below_one": (
            None if lambda_bound_max is None else lambda_bound_max < 1.0
        ),
        "fine_lambda_super": lambda_super,
        "within_source_log_ratio_spread_quantiles": _quantiles(
            within_source_spreads
        ),
        "within_coarse_fiber_log_ratio_spread_quantiles": _quantiles(
            within_fiber_spreads
        ),
        "interpretation": (
            "Finite target samples only; ratio_kind distinguishes concrete "
            "finest sampled Collatz branches from Galerkin-induced targets. "
            "Cemetery entries are zero-valued descent branches when the "
            "primary transition window is complete. The average-to-branch "
            "bounds use either each actual row average q or the global "
            "lambda_super, and both divide by each row's survival probability. "
            "They are numerical, not infinite-orbit certificates."
        ),
    }


@dataclass(frozen=True)
class PECMCrossResolutionReport:
    """Machine-readable output of the Galerkin-ladder experiment."""

    type: str
    status: str
    levels: tuple[tuple[int, int], ...]
    normalization: str
    common_alpha: float
    parameters: dict[str, Any]
    operator_ladder_construction: str
    certificate_kind: str
    exact_lyapunov_inequality_verified: bool
    primary_transition_window_complete: bool
    legacy_transition_windows_complete: bool
    proof_facing_input_complete: bool
    proof_eligible: bool
    proof_ineligibility_reasons: tuple[str, ...]
    global_collatz_proof: bool
    finest_sample_outcomes: dict[str, Any]
    level_summaries: tuple[dict[str, Any], ...]
    operator_intertwining_defect: tuple[dict[str, Any], ...]
    legacy_independently_sampled_operator_defects: tuple[dict[str, Any], ...]
    errors: dict[str, tuple[float, ...]]
    adjacent_profiles: tuple[LiftConsistencyProfile, ...]
    branch_ratio_oscillation: tuple[dict[str, Any], ...]
    lift_spread_quantiles: dict[str, dict[str, float]]
    worst_coarse_states: tuple[dict[str, Any], ...]
    interpretation: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["levels"] = [list(level) for level in self.levels]
        data["errors"] = {
            metric: list(values) for metric, values in self.errors.items()
        }
        data["adjacent_profiles"] = [
            profile.to_json_dict() for profile in self.adjacent_profiles
        ]
        data["operator_intertwining_defect"] = [
            dict(record) for record in self.operator_intertwining_defect
        ]
        data["legacy_independently_sampled_operator_defects"] = [
            dict(record)
            for record in self.legacy_independently_sampled_operator_defects
        ]
        data["branch_ratio_oscillation"] = [
            dict(record) for record in self.branch_ratio_oscillation
        ]
        data["worst_coarse_states"] = [
            dict(record) for record in self.worst_coarse_states
        ]
        data["interpretation"] = list(self.interpretation)
        return data

    def to_json(self) -> str:
        return json.dumps(
            self.to_json_dict(),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )


def _validate_configurations(
    configurations: tuple[tuple[int, int], ...],
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_materialized_states: int | None,
    max_materialized_transitions: int | None,
) -> tuple[tuple[MixedAdicLevel, ...], int]:
    if len(configurations) < 2:
        raise ValueError("at least two refinement levels are required")
    levels = tuple(
        MixedAdicLevel(mod2_power, mod3_power, R_values)
        for mod2_power, mod3_power in configurations
    )
    for coarse, fine in zip(levels, levels[1:]):
        MixedAdicRefinement(coarse, fine)
        if (
            coarse.mod2_power == fine.mod2_power
            and coarse.mod3_power == fine.mod3_power
        ):
            raise ValueError("adjacent refinement levels must be distinct")
    if max_materialized_states is not None:
        if max_materialized_states <= 0:
            raise ValueError("max_materialized_states must be positive or None")
        if levels[-1].state_count > max_materialized_states:
            raise ValueError(
                f"finest level has {levels[-1].state_count} states, above "
                f"max_materialized_states={max_materialized_states}; use the "
                "future chunked/streaming consistency path"
            )
    finest_transition_count = levels[-1].state_count * (
        1 << sample_lift_power
    )
    primary_ladder_entries = finest_transition_count * len(levels)
    independent_legacy_entries = sum(
        level.state_count * (1 << sample_lift_power)
        for level in levels[:-1]
    )
    retained_transition_entries = (
        primary_ladder_entries + independent_legacy_entries
    )
    if max_materialized_transitions is not None:
        if max_materialized_transitions <= 0:
            raise ValueError(
                "max_materialized_transitions must be positive or None"
            )
        if retained_transition_entries > max_materialized_transitions:
            raise ValueError(
                "cross-resolution report would retain approximately "
                f"{retained_transition_entries} target entries, above "
                "max_materialized_transitions="
                f"{max_materialized_transitions}; reduce levels or "
                "sample_lift_power, or use the future streaming path"
            )
    return levels, retained_transition_entries


def _build_sampled_operator(
    level: MixedAdicLevel,
    *,
    sample_lift_power: int,
    max_steps: int,
    tail_reentry_min_R: int,
    label: str,
) -> tuple[UniformTargetOperator, dict[str, int]]:
    (
        targets,
        descended,
        reentered,
        unresolved,
        max_survival,
        worst_index,
    ) = _build_post_exit_target_array(
        mod2_power=level.mod2_power,
        mod3_power=level.mod3_power,
        R_values=level.R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
    )
    return (
        UniformTargetOperator.from_target_array(targets, label=label),
        {
            "descended_samples": descended,
            "reentry_samples": reentered,
            "unresolved_or_out_of_window_samples": unresolved,
            "max_row_survival_samples": max_survival,
            "worst_survival_state_id": worst_index,
        },
    )


def pecm_cross_resolution_consistency_report(
    configurations: tuple[tuple[int, int], ...] = _DEFAULT_LEVELS,
    *,
    alpha: float = 0.55,
    R_values: tuple[int, ...] = _DEFAULT_R_VALUES,
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    extension_iterations: int = 400,
    tolerance: float = 1e-10,
    require_resolved: bool = True,
    max_materialized_states: int | None = _DEFAULT_MAX_MATERIALIZED_STATES,
    max_materialized_transitions: int | None = (
        _DEFAULT_MAX_MATERIALIZED_TRANSITIONS
    ),
) -> PECMCrossResolutionReport:
    """Build and compare a common-alpha, exact-Galerkin PECM ladder."""

    import numpy as np

    configurations = tuple(tuple(pair) for pair in configurations)
    R_values = tuple(R_values)
    if not math.isfinite(alpha) or alpha <= 0.0 or alpha >= 1.0:
        raise ValueError("alpha must be finite and strictly between zero and one")
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")
    if max_steps <= 0:
        raise ValueError("max_steps must be positive")
    if tail_reentry_min_R < 1:
        raise ValueError("tail_reentry_min_R must be positive")
    if extension_iterations <= 0:
        raise ValueError("extension_iterations must be positive")
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    levels, retained_transition_entries = _validate_configurations(
        configurations,
        R_values,
        sample_lift_power,
        max_materialized_states,
        max_materialized_transitions,
    )
    finest_operator, finest_outcomes = _build_sampled_operator(
        levels[-1],
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
        label="finest_independently_sampled_operator",
    )
    unresolved = finest_outcomes["unresolved_or_out_of_window_samples"]
    if require_resolved and unresolved:
        raise ValueError(
            "finest transition window is incomplete: "
            f"{unresolved} samples are unresolved or out of the R window"
        )

    operators: list[UniformTargetOperator | None] = [None] * len(levels)
    operators[-1] = finest_operator
    refinements: list[MixedAdicRefinement | None] = [None] * (len(levels) - 1)
    for index in range(len(levels) - 2, -1, -1):
        refinement = MixedAdicRefinement(levels[index], levels[index + 1])
        refinements[index] = refinement
        fine_operator = operators[index + 1]
        assert fine_operator is not None
        operators[index] = galerkin_coarsen(
            refinement,
            fine_operator,
            label=(
                "exact_galerkin_from_finest_"
                f"{levels[index].mod2_power}_{levels[index].mod3_power}"
            ),
        )
    resolved_operators = tuple(operator for operator in operators if operator)
    resolved_refinements = tuple(
        refinement for refinement in refinements if refinement
    )
    if len(resolved_operators) != len(levels):
        raise AssertionError("internal operator ladder construction failed")

    solutions = []
    normalized_vectors = []
    level_summaries = []
    for level, operator in zip(levels, resolved_operators, strict=True):
        solution = positive_resolvent_vector(
            operator,
            alpha=alpha,
            iterations=extension_iterations,
            tolerance=tolerance,
        )
        if not solution.converged:
            raise ValueError(
                f"common-alpha resolvent did not converge at "
                f"({level.mod2_power},{level.mod3_power})"
            )
        if not solution.lambda_super < alpha:
            raise ValueError(
                "common-alpha vector does not numerically contract at "
                f"({level.mod2_power},{level.mod3_power})"
            )
        log_vector = np.log(solution.vector)
        normalized = np.exp(log_vector - float(log_vector.mean()))
        solutions.append(solution)
        normalized_vectors.append(normalized)
        worst_state = decode_state_index(level, solution.worst_state_id)
        level_summaries.append(
            {
                "level": _level_pair(level),
                "states": level.state_count,
                "row_sample_count": operator.sample_count,
                "alpha": alpha,
                "lambda_super": solution.lambda_super,
                "alpha_minus_lambda": alpha - solution.lambda_super,
                "iterations_used": solution.iterations,
                "converged": solution.converged,
                "relative_fixed_point_residual": (
                    solution.relative_fixed_point_residual
                ),
                "normalized_h_min": float(normalized.min()),
                "normalized_h_max": float(normalized.max()),
                "worst_state": {
                    "state_id": solution.worst_state_id,
                    "R": worst_state.R,
                    "u_mod_2k": worst_state.u_mod2,
                    "u_mod_3ell": worst_state.u_mod3,
                },
                "state_order_hash": pecm_state_order_hash(
                    level.mod2_power,
                    level.mod3_power,
                    level.R_values,
                ),
                "state_order_hash_algorithm": "sha256:pecm-state-order-v1",
                "certificate_kind": (
                    "floating_point_super_eigenvector_diagnostic"
                ),
                "exact_inequality_verified": False,
            }
        )

    profiles: list[LiftConsistencyProfile] = []
    operator_defects: list[dict[str, Any]] = []
    branch_profiles: list[dict[str, Any]] = []
    for index, refinement in enumerate(resolved_refinements):
        coarse_operator = resolved_operators[index]
        fine_operator = resolved_operators[index + 1]
        profile = lift_consistency_profile(
            refinement,
            normalized_vectors[index],
            normalized_vectors[index + 1],
        )
        profiles.append(profile)
        pointwise_and_galerkin = diagnose_operator_intertwining(
            refinement,
            coarse_operator,
            fine_operator,
        )
        full_conditional = diagnose_conditional_expectation_intertwining(
            refinement,
            coarse_operator,
            fine_operator,
        )
        operator_defects.append(
            {
                "pair": _pair_key(refinement.coarse, refinement.fine),
                "pointwise_and_galerkin": (
                    pointwise_and_galerkin.to_json_dict()
                ),
                "full_conditional_expectation": (
                    full_conditional.to_json_dict()
                ),
            }
        )
        branch_profiles.append(
            sampled_branch_ratio_profile(
                refinement,
                fine_operator,
                normalized_vectors[index + 1],
                lambda_super=solutions[index + 1].lambda_super,
            )
        )

    legacy_operators: list[UniformTargetOperator] = []
    legacy_outcomes: list[dict[str, int]] = []
    for index, level in enumerate(levels):
        if index == len(levels) - 1:
            operator = finest_operator
            outcomes = finest_outcomes
        else:
            operator, outcomes = _build_sampled_operator(
                level,
                sample_lift_power=sample_lift_power,
                max_steps=max_steps,
                tail_reentry_min_R=tail_reentry_min_R,
                label=(
                    "legacy_independently_sampled_"
                    f"{level.mod2_power}_{level.mod3_power}"
                ),
            )
        legacy_operators.append(operator)
        legacy_outcomes.append(outcomes)

    legacy_defects: list[dict[str, Any]] = []
    for index, refinement in enumerate(resolved_refinements):
        diagnostic = diagnose_operator_intertwining(
            refinement,
            legacy_operators[index],
            legacy_operators[index + 1],
        )
        full_conditional = diagnose_conditional_expectation_intertwining(
            refinement,
            legacy_operators[index],
            legacy_operators[index + 1],
        )
        legacy_defects.append(
            {
                "pair": _pair_key(refinement.coarse, refinement.fine),
                "coarse_sample_outcomes": legacy_outcomes[index],
                "fine_sample_outcomes": legacy_outcomes[index + 1],
                "pointwise_and_galerkin": diagnostic.to_json_dict(),
                "full_conditional_expectation": (
                    full_conditional.to_json_dict()
                ),
                "interpretation": (
                    "This compares independently sampled fixed-CRT-lift "
                    "operators and is not the primary Galerkin ladder."
                ),
            }
        )

    errors = {
        metric: tuple(profile.errors[metric] for profile in profiles)
        for metric in ("mean", "min", "max")
    }
    lift_spreads = {
        _pair_key(profile.coarse_level, profile.fine_level): (
            profile.lift_spread_quantiles
        )
        for profile in profiles
    }
    worst_states = tuple(
        {
            "pair": _pair_key(profile.coarse_level, profile.fine_level),
            **record,
        }
        for profile in profiles
        for record in profile.worst_coarse_states
    )
    complete_window = unresolved == 0
    legacy_windows_complete = all(
        outcomes["unresolved_or_out_of_window_samples"] == 0
        for outcomes in legacy_outcomes
    )
    status = (
        "finite_galerkin_ladder_diagnostic_not_global_proof"
        if complete_window
        else "finite_galerkin_ladder_has_unresolved_primary_transitions"
    )
    return PECMCrossResolutionReport(
        type="pecm_cross_resolution_consistency_report",
        status=status,
        levels=configurations,
        normalization="geometric_mean_1",
        common_alpha=alpha,
        parameters={
            "R_values": list(R_values),
            "sample_lift_power": sample_lift_power,
            "max_steps": max_steps,
            "tail_reentry_min_R": tail_reentry_min_R,
            "extension_iterations": extension_iterations,
            "tolerance": tolerance,
            "max_materialized_states": max_materialized_states,
            "max_materialized_transitions": max_materialized_transitions,
            "estimated_retained_transition_entries": (
                retained_transition_entries
            ),
        },
        operator_ladder_construction=(
            "one finest sampled operator followed by exact sequential "
            "Galerkin coarsening"
        ),
        certificate_kind="floating_point_common_alpha_diagnostic",
        exact_lyapunov_inequality_verified=False,
        primary_transition_window_complete=complete_window,
        legacy_transition_windows_complete=legacy_windows_complete,
        proof_facing_input_complete=complete_window,
        proof_eligible=False,
        proof_ineligibility_reasons=(
            (
                "unresolved_or_out_of_window_samples_share_the_cemetery_sentinel",
            )
            if not complete_window
            else ()
        )
        + (
            "float64_lyapunov_inequalities_not_exactly_verified",
            "galerkin_compatibility_is_not_pointwise_projective_compatibility",
            "finite_averaged_residue_operator_is_not_a_per_orbit_theorem",
        ),
        global_collatz_proof=False,
        finest_sample_outcomes=finest_outcomes,
        level_summaries=tuple(level_summaries),
        operator_intertwining_defect=tuple(operator_defects),
        legacy_independently_sampled_operator_defects=tuple(legacy_defects),
        errors=errors,
        adjacent_profiles=tuple(profiles),
        branch_ratio_oscillation=tuple(branch_profiles),
        lift_spread_quantiles=lift_spreads,
        worst_coarse_states=worst_states,
        interpretation=(
            "The primary coarse kernels are Galerkin projections of one finest "
            "finite sampled operator; their Galerkin defect is zero by "
            "construction and must not be called full compatibility.",
            "Pointwise projective and full conditional-expectation defects are "
            "reported separately in exact rational arithmetic.",
            "All h vectors, log errors, and branch ratios use float64 and are "
            "numerical diagnostics awaiting exact branch verification.",
            "The reported lambda_super values come from the chosen common-alpha "
            "resolvent and are numerical upper ratios, not independent "
            "spectral-radius estimates.",
            "The same ordered R grid is used at every residue level, so a "
            "common fixed cusp term kappa*R cancels in adjacent lift "
            "comparisons; tail-grid refinement remains future work.",
            "Independently sampled legacy PECM levels are isolated because "
            "fixed CRT lift windows change under refinement.",
            "The in-memory implementation intentionally stops before the "
            "(12,4) production level; arithmetic parent maps, chunked "
            "coarsening, and streaming vector output are required there.",
        ),
    )


def format_pecm_cross_resolution_consistency_report(
    report: PECMCrossResolutionReport,
) -> str:
    """Format a compact human-readable summary."""

    lines = [
        f"status={report.status}",
        f"levels={report.levels}",
        f"common_alpha={report.common_alpha:.8f}",
        "primary_transition_window_complete="
        f"{report.primary_transition_window_complete}",
        "legacy_transition_windows_complete="
        f"{report.legacy_transition_windows_complete}",
    ]
    for summary in report.level_summaries:
        level = tuple(summary["level"])
        lines.append(
            f"level={level} states={summary['states']} "
            f"samples={summary['row_sample_count']} "
            f"lambda={summary['lambda_super']:.8f} "
            f"residual={summary['relative_fixed_point_residual']:.3e}"
        )
    for index, profile in enumerate(report.adjacent_profiles):
        lines.append(
            f"pair={_pair_key(profile.coarse_level, profile.fine_level)} "
            f"E_mean={report.errors['mean'][index]:.6g} "
            f"E_min={report.errors['min'][index]:.6g} "
            f"E_max={report.errors['max'][index]:.6g}"
        )
    return "\n".join(lines)
