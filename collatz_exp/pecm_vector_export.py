"""Deterministic, common-alpha exports of finite PECM resolvent vectors.

The exported ``recurrent_or_transient`` field is retained for compatibility
with the research plan.  Here ``recurrent`` has its finite substochastic
Markov-chain meaning: the state belongs to a closed, non-leaky cyclic strongly
connected component.  ``graph_role`` carries the more useful three-way
classification:

``cyclic_core``
    The state itself lies on a directed cycle of sampled legal reentries.
``cyclic_basin``
    The state can reach such a cycle but does not itself lie on one.
``transient_off_support``
    The state cannot reach any directed cycle.

Thus a leaky cyclic component is truthfully identified as ``cyclic_core`` but
is not mislabeled recurrent.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from .post_exit_map import (
    _apply_targets,
    _build_post_exit_target_array,
    _decode_state_index,
)

_DEFAULT_R_VALUES = tuple(range(2, 31))
_STATE_ORDER_HASH_ALGORITHM = "sha256:pecm-state-order-v1"
_DEFAULT_MAX_MATERIALIZED_STATES = 250_000
_DEFAULT_MAX_MATERIALIZED_TRANSITIONS = 2_000_000
_GRAPH_ROLES = (
    "transient_off_support",
    "cyclic_basin",
    "cyclic_core",
)


@dataclass(frozen=True)
class PositiveResolventSolution:
    """Numerical solution of ``h = 1 + M h / alpha`` on a finite operator."""

    vector: Any = field(repr=False, compare=False)
    ratios: Any = field(repr=False, compare=False)
    iterations: int
    converged: bool
    fixed_point_residual: float
    relative_fixed_point_residual: float
    lambda_super: float
    worst_state_id: int


@dataclass(frozen=True)
class PostExitVectorRecord:
    state_id: int
    R: int
    u_mod_2k: int
    u_mod_3ell: int
    h: float
    Mh_over_h: float
    graph_role: str
    recurrent_or_transient: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PostExitVectorExport:
    type: str
    mod2_power: int
    mod3_power: int
    R_values: tuple[int, ...]
    sample_lift_power: int
    max_steps: int
    tail_reentry_min_R: int
    states: int
    row_denominator: int
    materialized_transition_count: int
    alpha: float
    extension_iterations: int
    iterations_used: int
    converged: bool
    raw_fixed_point_residual: float
    raw_relative_fixed_point_residual: float
    lambda_super: float
    alpha_minus_lambda: float
    certificate_kind: str
    exact_inequality_verified: bool
    complete_transition_window: bool
    proof_facing_input_complete: bool
    proof_eligible: bool
    proof_ineligibility_reasons: tuple[str, ...]
    global_collatz_proof: bool
    normalization: str
    normalization_scale: float
    raw_geometric_mean: float
    state_order_hash: str
    state_order_hash_algorithm: str
    descended_samples: int
    reentry_samples: int
    unresolved_or_out_of_window_samples: int
    cyclic_core_states: int
    cyclic_basin_states: int
    transient_off_support_states: int
    recurrent_states: int
    transient_states: int
    classification_note: str
    records: tuple[PostExitVectorRecord, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_values": list(self.R_values),
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "tail_reentry_min_R": self.tail_reentry_min_R,
            "states": self.states,
            "row_denominator": self.row_denominator,
            "materialized_transition_count": self.materialized_transition_count,
            "alpha": self.alpha,
            "extension_iterations": self.extension_iterations,
            "iterations_used": self.iterations_used,
            "converged": self.converged,
            "raw_fixed_point_residual": self.raw_fixed_point_residual,
            "raw_relative_fixed_point_residual": (
                self.raw_relative_fixed_point_residual
            ),
            "lambda_super": self.lambda_super,
            "alpha_minus_lambda": self.alpha_minus_lambda,
            "certificate_kind": self.certificate_kind,
            "exact_inequality_verified": self.exact_inequality_verified,
            "complete_transition_window": self.complete_transition_window,
            "proof_facing_input_complete": self.proof_facing_input_complete,
            "proof_eligible": self.proof_eligible,
            "proof_ineligibility_reasons": list(
                self.proof_ineligibility_reasons
            ),
            "global_collatz_proof": self.global_collatz_proof,
            "normalization": self.normalization,
            "normalization_scale": self.normalization_scale,
            "raw_geometric_mean": self.raw_geometric_mean,
            "state_order_hash": self.state_order_hash,
            "state_order_hash_algorithm": self.state_order_hash_algorithm,
            "descended_samples": self.descended_samples,
            "reentry_samples": self.reentry_samples,
            "unresolved_or_out_of_window_samples": (
                self.unresolved_or_out_of_window_samples
            ),
            "cyclic_core_states": self.cyclic_core_states,
            "cyclic_basin_states": self.cyclic_basin_states,
            "transient_off_support_states": self.transient_off_support_states,
            "recurrent_states": self.recurrent_states,
            "transient_states": self.transient_states,
            "classification_note": self.classification_note,
            "records": [record.to_json_dict() for record in self.records],
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_json_dict(),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )


def _validate_solver_parameters(
    alpha: float,
    iterations: int,
    tolerance: float,
) -> None:
    if not math.isfinite(alpha) or alpha <= 0.0:
        raise ValueError("alpha must be finite and positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive")


def _operator_application(operator_or_targets: Any, denominator: int | None):
    import numpy as np

    if isinstance(operator_or_targets, np.ndarray):
        targets = operator_or_targets
        if targets.ndim != 2:
            raise ValueError("target array must be two-dimensional")
        if denominator is None or denominator <= 0:
            raise ValueError("a positive denominator is required for target arrays")
        states = int(targets.shape[0])

        def apply(vector):
            return _apply_targets(targets, vector, denominator)

        return states, apply

    apply = getattr(operator_or_targets, "apply", None)
    states = getattr(
        operator_or_targets,
        "states",
        getattr(operator_or_targets, "state_count", None),
    )
    if not callable(apply) or not isinstance(states, int) or states <= 0:
        raise TypeError(
            "operator must expose .states or .state_count as a positive integer "
            "and .apply(vector)"
        )
    return states, apply


def positive_resolvent_vector(
    operator_or_targets: Any,
    denominator: int | None = None,
    *,
    alpha: float,
    iterations: int = 400,
    tolerance: float = 1e-10,
) -> PositiveResolventSolution:
    """Solve a positive resolvent for a target array or matrix-free operator.

    A target array must be accompanied by its positive row ``denominator``.
    A matrix-free operator must expose ``states: int`` (or ``state_count``)
    and ``apply(vector)``; its ``apply`` method is responsible for all row
    normalization.
    """

    import numpy as np

    _validate_solver_parameters(alpha, iterations, tolerance)
    states, apply = _operator_application(operator_or_targets, denominator)
    vector = np.ones(states, dtype=np.float64)

    iterations_used = 0
    for iterations_used in range(1, iterations + 1):
        image = np.asarray(apply(vector), dtype=np.float64)
        if image.shape != vector.shape:
            raise ValueError("operator.apply returned a vector with the wrong shape")
        if not bool(np.isfinite(image).all()) or bool((image < 0.0).any()):
            raise ValueError("operator.apply must return finite nonnegative values")
        nxt = 1.0 + image / alpha
        step_residual = float(np.max(np.abs(nxt - vector), initial=0.0))
        vector = nxt
        relative_step_residual = step_residual / max(
            1.0, float(np.max(np.abs(vector), initial=1.0))
        )
        if relative_step_residual <= tolerance:
            break

    image = np.asarray(apply(vector), dtype=np.float64)
    if image.shape != vector.shape:
        raise ValueError("operator.apply returned a vector with the wrong shape")
    if not bool(np.isfinite(image).all()) or bool((image < 0.0).any()):
        raise ValueError("operator.apply must return finite nonnegative values")
    fixed_point_image = 1.0 + image / alpha
    fixed_point_residual = float(
        np.max(np.abs(fixed_point_image - vector), initial=0.0)
    )
    relative_fixed_point_residual = fixed_point_residual / max(
        1.0, float(np.max(np.abs(vector), initial=1.0))
    )
    converged = relative_fixed_point_residual <= tolerance
    if not bool(np.isfinite(vector).all()) or bool((vector <= 0.0).any()):
        raise ValueError("resolvent iteration did not produce a finite positive vector")
    ratios = image / vector
    worst_state_id = int(np.argmax(ratios))
    return PositiveResolventSolution(
        vector=vector,
        ratios=ratios,
        iterations=iterations_used,
        converged=converged,
        fixed_point_residual=fixed_point_residual,
        relative_fixed_point_residual=relative_fixed_point_residual,
        lambda_super=float(ratios[worst_state_id]),
        worst_state_id=worst_state_id,
    )


def _graph_roles(targets):
    """Return three-way graph roles and strict recurrent-state membership."""

    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components

    states = int(targets.shape[0])
    valid = targets >= 0
    row_counts = valid.sum(axis=1, dtype=np.int64)
    indptr = np.empty(states + 1, dtype=np.int64)
    indptr[0] = 0
    np.cumsum(row_counts, out=indptr[1:])
    indices = targets[valid].astype(np.int64, copy=False)
    graph = csr_matrix(
        (np.ones(indices.size, dtype=np.int8), indices, indptr),
        shape=(states, states),
    )
    component_count, labels = connected_components(
        graph,
        directed=True,
        connection="strong",
        return_labels=True,
    )
    component_sizes = np.bincount(labels, minlength=component_count)
    cyclic_components = component_sizes > 1
    rows = np.arange(states)
    self_loop_rows = np.zeros(states, dtype=bool)
    for column in range(targets.shape[1]):
        self_loop_rows |= targets[:, column] == rows
    cyclic_components[labels[self_loop_rows]] = True
    cyclic_core = cyclic_components[labels]

    reverse = graph.transpose().tocsr()
    reaches_cycle = cyclic_core.copy()
    queue = deque(int(row) for row in np.flatnonzero(cyclic_core))
    while queue:
        target = queue.popleft()
        start, stop = reverse.indptr[target : target + 2]
        for source in reverse.indices[start:stop]:
            if not reaches_cycle[source]:
                reaches_cycle[source] = True
                queue.append(int(source))

    role_codes = np.zeros(states, dtype=np.uint8)
    role_codes[reaches_cycle] = 1
    role_codes[cyclic_core] = 2

    closed_components = np.ones(component_count, dtype=bool)
    bad_rows = np.zeros(states, dtype=bool)
    for column in range(targets.shape[1]):
        target = targets[:, column]
        same_component = np.zeros(states, dtype=bool)
        present = target >= 0
        same_component[present] = (
            labels[target[present]] == labels[present]
        )
        bad_rows |= ~same_component
    closed_components[labels[bad_rows]] = False
    recurrent = cyclic_core & closed_components[labels]
    return role_codes, recurrent


def _state_order_digest(
    mod2_power: int,
    mod3_power: int,
    states: Iterable[Any],
) -> str:
    digest = hashlib.sha256()
    digest.update(b"pecm-state-order-v1\n")
    digest.update(f"k={mod2_power};ell={mod3_power}\n".encode("ascii"))
    for state_id, state in enumerate(states):
        digest.update(
            f"{state_id},{state.R},{state.u_mod2},{state.u_mod3}\n".encode("ascii")
        )
    return digest.hexdigest()


def pecm_state_order_hash(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
) -> str:
    """Hash the canonical PECM row order without retaining state records."""

    R_values = tuple(R_values)
    state_count = (
        len(R_values)
        * (1 << (mod2_power - 1))
        * (3**mod3_power)
    )
    states = (
        _decode_state_index(
            state_id,
            mod2_power,
            mod3_power,
            R_values,
        )
        for state_id in range(state_count)
    )
    return _state_order_digest(mod2_power, mod3_power, states)


def _validate_export_parameters(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
    tail_reentry_min_R: int,
    alpha: float,
    normalization: str,
) -> None:
    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    if not R_values or any(R < 2 for R in R_values):
        raise ValueError("R_values must be nonempty and contain only R >= 2")
    if len(set(R_values)) != len(R_values):
        raise ValueError("R_values must not contain duplicates")
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")
    if max_steps <= 0:
        raise ValueError("max_steps must be positive")
    if tail_reentry_min_R < 1:
        raise ValueError("tail_reentry_min_R must be positive")
    if alpha >= 1.0:
        raise ValueError("alpha must be strictly below one")
    if normalization not in {"none", "geometric_mean_1"}:
        raise ValueError("normalization must be none or geometric_mean_1")


def post_exit_vector_export(
    mod2_power: int,
    mod3_power: int,
    *,
    alpha: float,
    R_values: tuple[int, ...] = _DEFAULT_R_VALUES,
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    extension_iterations: int = 400,
    tolerance: float = 1e-10,
    normalization: str = "geometric_mean_1",
    require_convergence: bool = True,
    require_resolved: bool = True,
    max_materialized_states: int | None = _DEFAULT_MAX_MATERIALIZED_STATES,
    max_materialized_transitions: int | None = (
        _DEFAULT_MAX_MATERIALIZED_TRANSITIONS
    ),
) -> PostExitVectorExport:
    """Build a deterministic numerical PECM vector export at a supplied alpha.

    This in-memory exporter is intended for small and medium research levels.
    It uses ``float64`` resolvent iteration, so its inequality is a numerical
    diagnostic rather than an exact certificate.  By default it rejects any
    transition window containing unresolved or out-of-window samples, because
    those samples share the target-array cemetery sentinel with true descent.
    """

    import numpy as np

    R_values = tuple(R_values)
    _validate_solver_parameters(alpha, extension_iterations, tolerance)
    _validate_export_parameters(
        mod2_power,
        mod3_power,
        R_values,
        sample_lift_power,
        max_steps,
        tail_reentry_min_R,
        alpha,
        normalization,
    )
    state_count = (
        len(R_values)
        * (1 << (mod2_power - 1))
        * (3**mod3_power)
    )
    if max_materialized_states is not None:
        if max_materialized_states <= 0:
            raise ValueError("max_materialized_states must be positive or None")
        if state_count > max_materialized_states:
            raise ValueError(
                f"vector export would materialize {state_count} states, above "
                f"max_materialized_states={max_materialized_states}; use a "
                "chunked/streaming vector export for this level"
            )
    transition_count = state_count * (1 << sample_lift_power)
    if max_materialized_transitions is not None:
        if max_materialized_transitions <= 0:
            raise ValueError(
                "max_materialized_transitions must be positive or None"
            )
        if transition_count > max_materialized_transitions:
            raise ValueError(
                f"vector export would materialize {transition_count} target "
                "entries, above max_materialized_transitions="
                f"{max_materialized_transitions}; reduce sample_lift_power or "
                "use a chunked/streaming vector export"
            )
    (
        targets,
        descended,
        reentered,
        unresolved,
        _max_survival,
        _worst_index,
    ) = _build_post_exit_target_array(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
    )
    if require_resolved and unresolved:
        raise ValueError(
            "post-exit transition window is incomplete: "
            f"{unresolved} samples are unresolved or reenter outside R_values; "
            "increase max_steps/R_values or set require_resolved=False for an "
            "explicitly non-proof-facing diagnostic"
        )
    denominator = 1 << sample_lift_power
    solution = positive_resolvent_vector(
        targets,
        denominator,
        alpha=alpha,
        iterations=extension_iterations,
        tolerance=tolerance,
    )
    if require_convergence and not solution.converged:
        raise ValueError(
            "positive resolvent did not converge; alpha may not exceed the "
            "operator spectral radius"
        )
    if require_convergence and not solution.lambda_super < alpha:
        raise ValueError(
            "positive vector does not numerically witness rho < alpha: "
            f"max(Mh/h)={solution.lambda_super!r}, alpha={alpha!r}"
        )

    log_values = np.log(solution.vector)
    raw_geometric_mean = float(math.exp(float(log_values.mean())))
    normalization_scale = (
        raw_geometric_mean if normalization == "geometric_mean_1" else 1.0
    )
    normalized = solution.vector / normalization_scale
    state_count = int(targets.shape[0])
    states = tuple(
        _decode_state_index(
            state_id,
            mod2_power,
            mod3_power,
            R_values,
        )
        for state_id in range(state_count)
    )
    role_codes, recurrent = _graph_roles(targets)
    records = tuple(
        PostExitVectorRecord(
            state_id=state_id,
            R=state.R,
            u_mod_2k=state.u_mod2,
            u_mod_3ell=state.u_mod3,
            h=float(normalized[state_id]),
            Mh_over_h=float(solution.ratios[state_id]),
            graph_role=_GRAPH_ROLES[int(role_codes[state_id])],
            recurrent_or_transient=(
                "recurrent" if bool(recurrent[state_id]) else "transient"
            ),
        )
        for state_id, state in enumerate(states)
    )
    recurrent_states = int(recurrent.sum())
    cyclic_core_states = int((role_codes == 2).sum())
    cyclic_basin_states = int((role_codes == 1).sum())
    transient_off_support_states = int((role_codes == 0).sum())
    return PostExitVectorExport(
        type="post_exit_vector_export",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
        states=state_count,
        row_denominator=denominator,
        materialized_transition_count=transition_count,
        alpha=alpha,
        extension_iterations=extension_iterations,
        iterations_used=solution.iterations,
        converged=solution.converged,
        raw_fixed_point_residual=solution.fixed_point_residual,
        raw_relative_fixed_point_residual=(
            solution.relative_fixed_point_residual
        ),
        lambda_super=solution.lambda_super,
        alpha_minus_lambda=alpha - solution.lambda_super,
        certificate_kind="floating_point_super_eigenvector_diagnostic",
        exact_inequality_verified=False,
        complete_transition_window=unresolved == 0,
        proof_facing_input_complete=unresolved == 0,
        proof_eligible=False,
        proof_ineligibility_reasons=(
            (
                "unresolved_or_out_of_window_samples_share_the_cemetery_sentinel",
            )
            if unresolved
            else ()
        )
        + (
            "float64_inequality_not_exactly_verified",
            "finite_averaged_residue_operator_not_a_per_orbit_theorem",
        ),
        global_collatz_proof=False,
        normalization=normalization,
        normalization_scale=normalization_scale,
        raw_geometric_mean=raw_geometric_mean,
        state_order_hash=_state_order_digest(
            mod2_power, mod3_power, states
        ),
        state_order_hash_algorithm=_STATE_ORDER_HASH_ALGORITHM,
        descended_samples=descended,
        reentry_samples=reentered,
        unresolved_or_out_of_window_samples=unresolved,
        cyclic_core_states=cyclic_core_states,
        cyclic_basin_states=cyclic_basin_states,
        transient_off_support_states=transient_off_support_states,
        recurrent_states=recurrent_states,
        transient_states=state_count - recurrent_states,
        classification_note=(
            "recurrent means membership in a closed non-leaky cyclic SCC; "
            "graph_role separately records cyclic core, basin, and off-support "
            "states"
            + (
                "; because unresolved samples share the cemetery sentinel, "
                "all graph roles are provisional for this incomplete window"
                if unresolved
                else ""
            )
        ),
        records=records,
    )


def post_exit_common_alpha_vector_exports(
    configurations: tuple[tuple[int, int], ...],
    *,
    alpha: float,
    R_values: tuple[int, ...] = _DEFAULT_R_VALUES,
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    extension_iterations: int = 400,
    tolerance: float = 1e-10,
    normalization: str = "geometric_mean_1",
    require_convergence: bool = True,
    require_resolved: bool = True,
    max_materialized_states: int | None = _DEFAULT_MAX_MATERIALIZED_STATES,
    max_materialized_transitions: int | None = (
        _DEFAULT_MAX_MATERIALIZED_TRANSITIONS
    ),
) -> tuple[PostExitVectorExport, ...]:
    """Export several PECM levels using exactly one supplied alpha."""

    if not configurations:
        raise ValueError("configurations must be nonempty")
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")
    if any(
        mod2_power < 1 or mod3_power < 0
        for mod2_power, mod3_power in configurations
    ):
        raise ValueError(
            "all configurations require mod2_power >= 1 and mod3_power >= 0"
        )
    if max_materialized_states is not None and max_materialized_states <= 0:
        raise ValueError("max_materialized_states must be positive or None")
    if (
        max_materialized_transitions is not None
        and max_materialized_transitions <= 0
    ):
        raise ValueError(
            "max_materialized_transitions must be positive or None"
        )
    R_values = tuple(R_values)
    total_states = sum(
        len(R_values) * (1 << (mod2_power - 1)) * (3**mod3_power)
        for mod2_power, mod3_power in configurations
    )
    total_transitions = total_states * (1 << sample_lift_power)
    if (
        max_materialized_states is not None
        and total_states > max_materialized_states
    ):
        raise ValueError(
            f"common-alpha export would retain {total_states} states, above "
            f"max_materialized_states={max_materialized_states}"
        )
    if (
        max_materialized_transitions is not None
        and total_transitions > max_materialized_transitions
    ):
        raise ValueError(
            "common-alpha export would retain "
            f"{total_transitions} target entries, above "
            "max_materialized_transitions="
            f"{max_materialized_transitions}"
        )
    return tuple(
        post_exit_vector_export(
            mod2_power,
            mod3_power,
            alpha=alpha,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
            extension_iterations=extension_iterations,
            tolerance=tolerance,
            normalization=normalization,
            require_convergence=require_convergence,
            require_resolved=require_resolved,
            max_materialized_states=max_materialized_states,
            max_materialized_transitions=max_materialized_transitions,
        )
        for mod2_power, mod3_power in configurations
    )
