"""Unified finite operator diagnostics for the Collatz project.

This module intentionally keeps the claims finite.  The dyadic operator below
is a lift-averaged quotient of Mori's ``T_1 + T_2`` picture on residues modulo
``2^k``; division by two is not well-defined on ``Z/2^k`` without this lift
average.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UnifiedDyadicLevelReport:
    modulus_power: int
    dimension: int
    nonzero_entries: int
    row_sum_min: float
    row_sum_max: float
    spectral_radius: float | None
    second_eigenvalue_abs: float | None
    operator_norm_l2: float | None
    strongly_connected_components: int | None
    recurrent_components: int | None
    recurrent_states: int | None
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MoriMixedFirstReturnLevelReport:
    modulus_power2: int
    modulus_power3: int
    modulus: int
    dimension: int
    n1_residues: int
    n2_residues: int
    nonzero_entries: int
    lift_count_per_row: int
    max_return_steps: int
    mean_return_steps: float
    unresolved_lifts: int
    row_sum_min: float
    row_sum_max: float
    spectral_radius: float | None
    second_eigenvalue_abs: float | None
    operator_norm_l2: float | None
    strongly_connected_components: int | None
    recurrent_components: int | None
    recurrent_states: int | None
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MoriMixedFirstReturnReport:
    type: str
    status: str
    map_convention: str
    finite_model_caveat: str
    levels: tuple[MoriMixedFirstReturnLevelReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "map_convention": self.map_convention,
            "finite_model_caveat": self.finite_model_caveat,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PaparellaNilpotencyLevelReport:
    n: int
    dimension: int
    nonzero_edges_inside: int
    nilpotent_by_escape_depth: bool
    max_escape_depth: int
    nontrivial_cycle_found: bool
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UnifiedSavedProjectionReport:
    name: str
    path: str
    available: bool
    summary: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UnifiedCollatzOperatorReport:
    type: str
    status: str
    model_name: str
    finite_model_caveat: str
    dyadic_levels: tuple[UnifiedDyadicLevelReport, ...]
    paparella_levels: tuple[PaparellaNilpotencyLevelReport, ...]
    saved_projections: tuple[UnifiedSavedProjectionReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "model_name": self.model_name,
            "finite_model_caveat": self.finite_model_caveat,
            "dyadic_levels": [item.to_json_dict() for item in self.dyadic_levels],
            "paparella_levels": [
                item.to_json_dict() for item in self.paparella_levels
            ],
            "saved_projections": [
                item.to_json_dict() for item in self.saved_projections
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _dyadic_lift_averaged_rows(modulus_power: int) -> tuple[list[list[tuple[int, float]]], int]:
    if modulus_power < 2:
        raise ValueError("modulus_power must be at least 2")
    modulus = 1 << modulus_power
    rows: list[list[tuple[int, float]]] = []
    nonzero = 0
    half = 1 << (modulus_power - 1)
    for residue in range(modulus):
        if residue % 2:
            rows.append([((3 * residue + 1) % modulus, 1.0)])
            nonzero += 1
        else:
            first = residue // 2
            second = first + half
            rows.append([(first, 0.5), (second, 0.5)])
            nonzero += 2
    return rows, nonzero


def _dyadic_level_report(modulus_power: int) -> UnifiedDyadicLevelReport:
    rows, nonzero = _dyadic_lift_averaged_rows(modulus_power)
    dimension = len(rows)
    row_sums = [sum(weight for _target, weight in row) for row in rows]
    try:
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        from scipy.sparse.linalg import ArpackNoConvergence, eigs, svds
    except Exception:
        return UnifiedDyadicLevelReport(
            modulus_power=modulus_power,
            dimension=dimension,
            nonzero_entries=nonzero,
            row_sum_min=min(row_sums),
            row_sum_max=max(row_sums),
            spectral_radius=None,
            second_eigenvalue_abs=None,
            operator_norm_l2=None,
            strongly_connected_components=None,
            recurrent_components=None,
            recurrent_states=None,
            status="scipy_unavailable_support_only",
        )

    indptr = [0]
    indices: list[int] = []
    data: list[float] = []
    for row in rows:
        for target, weight in row:
            indices.append(target)
            data.append(weight)
        indptr.append(len(indices))
    matrix = csr_matrix((data, indices, indptr), shape=(dimension, dimension))
    spectral_radius = 1.0
    second = None
    eig_status = "spectrum_partial"
    eig_count = min(4, dimension - 1)
    if eig_count >= 2:
        try:
            eigenvalues = eigs(
                matrix.T,
                k=eig_count,
                which="LM",
                return_eigenvectors=False,
                maxiter=50_000,
            )
        except ArpackNoConvergence as error:
            eigenvalues = error.eigenvalues
            eig_status = "spectrum_arpack_partial_no_convergence"
        ordered = sorted((abs(complex(value)) for value in eigenvalues), reverse=True)
        below_top = [value for value in ordered if value < 1.0 - 1e-8]
        if below_top:
            second = float(below_top[0])
        elif len(ordered) >= 2:
            second = float(ordered[1])
        if eig_status == "spectrum_partial":
            eig_status = "spectrum_converged"
    operator_norm = float(svds(matrix, k=1, return_singular_vectors=False)[0])

    support = matrix.copy()
    support.data = np.ones_like(support.data)
    components, labels = connected_components(
        support,
        directed=True,
        connection="strong",
        return_labels=True,
    )
    outgoing = [False for _ in range(components)]
    component_sizes = [0 for _ in range(components)]
    for source, row in enumerate(rows):
        source_component = int(labels[source])
        component_sizes[source_component] += 1
        for target, _weight in row:
            if int(labels[target]) != source_component:
                outgoing[source_component] = True
    recurrent = [
        component
        for component in range(components)
        if not outgoing[component]
    ]
    return UnifiedDyadicLevelReport(
        modulus_power=modulus_power,
        dimension=dimension,
        nonzero_entries=nonzero,
        row_sum_min=float(min(row_sums)),
        row_sum_max=float(max(row_sums)),
        spectral_radius=spectral_radius,
        second_eigenvalue_abs=second,
        operator_norm_l2=operator_norm,
        strongly_connected_components=int(components),
        recurrent_components=len(recurrent),
        recurrent_states=sum(component_sizes[component] for component in recurrent),
        status=f"lift_averaged_dyadic_mori_projection_not_theorem_{eig_status}",
    )


def _collatz_full_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def _mori_original_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else 3 * n + 1


def _is_mori_n1(n: int) -> bool:
    return n % 6 in (1, 5)


def _is_mori_n2(n: int) -> bool:
    return (n - 1) % 3 == 0 and _is_mori_n1((n - 1) // 3)


def _is_mori_first_return_state(n: int) -> bool:
    return _is_mori_n1(n) or _is_mori_n2(n)


def _mori_mixed_domain_residues(modulus: int) -> tuple[list[int], set[int], set[int]]:
    if modulus % 18 != 0:
        raise ValueError("mixed Mori modulus must be divisible by 18")
    n1 = {residue for residue in range(modulus) if residue % 6 in (1, 5)}
    n2 = {residue for residue in range(modulus) if residue % 18 in (4, 16)}
    return sorted(n1 | n2), n1, n2


def _mori_first_return_target(
    n: int,
    max_return_steps: int,
) -> tuple[int | None, int]:
    x = n
    for steps in range(1, max_return_steps + 1):
        x = _mori_original_step(x)
        if _is_mori_first_return_state(x):
            return x, steps
    return None, max_return_steps


def _mori_mixed_first_return_level_report(
    modulus_power2: int,
    modulus_power3: int,
    lift_power: int,
    max_return_steps: int,
) -> MoriMixedFirstReturnLevelReport:
    if modulus_power2 < 1:
        raise ValueError("modulus_power2 must be at least 1")
    if modulus_power3 < 2:
        raise ValueError("modulus_power3 must be at least 2")
    if lift_power < 0:
        raise ValueError("lift_power must be non-negative")
    modulus = (1 << modulus_power2) * (3**modulus_power3)
    residues, n1_residues, n2_residues = _mori_mixed_domain_residues(modulus)
    index = {residue: i for i, residue in enumerate(residues)}
    lift_count = 1 << lift_power
    rows: list[list[tuple[int, float]]] = []
    unresolved_lifts = 0
    return_step_sum = 0
    return_step_count = 0
    return_step_max = 0

    for residue in residues:
        counts: dict[int, int] = {}
        for lift in range(lift_count):
            n = residue + lift * modulus
            target, steps = _mori_first_return_target(n, max_return_steps)
            if target is None:
                unresolved_lifts += 1
                continue
            target_residue = target % modulus
            target_index = index[target_residue]
            counts[target_index] = counts.get(target_index, 0) + 1
            return_step_sum += steps
            return_step_count += 1
            return_step_max = max(return_step_max, steps)
        if counts:
            denominator = sum(counts.values())
            rows.append(
                [
                    (target, count / denominator)
                    for target, count in sorted(counts.items())
                ]
            )
        else:
            rows.append([])

    dimension = len(rows)
    row_sums = [sum(weight for _target, weight in row) for row in rows]
    nonzero = sum(len(row) for row in rows)
    mean_steps = return_step_sum / return_step_count if return_step_count else 0.0

    try:
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        from scipy.sparse.linalg import ArpackNoConvergence, eigs, svds
    except Exception:
        return MoriMixedFirstReturnLevelReport(
            modulus_power2=modulus_power2,
            modulus_power3=modulus_power3,
            modulus=modulus,
            dimension=dimension,
            n1_residues=len(n1_residues),
            n2_residues=len(n2_residues),
            nonzero_entries=nonzero,
            lift_count_per_row=lift_count,
            max_return_steps=return_step_max,
            mean_return_steps=float(mean_steps),
            unresolved_lifts=unresolved_lifts,
            row_sum_min=float(min(row_sums)) if row_sums else 0.0,
            row_sum_max=float(max(row_sums)) if row_sums else 0.0,
            spectral_radius=None,
            second_eigenvalue_abs=None,
            operator_norm_l2=None,
            strongly_connected_components=None,
            recurrent_components=None,
            recurrent_states=None,
            status="scipy_unavailable_support_only",
        )

    indptr = [0]
    indices: list[int] = []
    data: list[float] = []
    for row in rows:
        for target, weight in row:
            indices.append(target)
            data.append(weight)
        indptr.append(len(indices))
    matrix = csr_matrix((data, indices, indptr), shape=(dimension, dimension))

    spectral_radius = None
    second = None
    eig_status = "spectrum_partial"
    eig_count = min(6, dimension - 1)
    if eig_count >= 2 and nonzero:
        try:
            eigenvalues = eigs(
                matrix.T,
                k=eig_count,
                which="LM",
                return_eigenvectors=False,
                maxiter=50_000,
            )
        except ArpackNoConvergence as error:
            eigenvalues = error.eigenvalues
            eig_status = "spectrum_arpack_partial_no_convergence"
        ordered = sorted((abs(complex(value)) for value in eigenvalues), reverse=True)
        if ordered:
            spectral_radius = float(ordered[0])
        below_top = [
            value for value in ordered if spectral_radius is not None and value < spectral_radius - 1e-8
        ]
        if below_top:
            second = float(below_top[0])
        elif len(ordered) >= 2:
            second = float(ordered[1])
        if eig_status == "spectrum_partial":
            eig_status = "spectrum_converged"
    operator_norm = float(svds(matrix, k=1, return_singular_vectors=False)[0])

    support = matrix.copy()
    support.data = np.ones_like(support.data)
    components, labels = connected_components(
        support,
        directed=True,
        connection="strong",
        return_labels=True,
    )
    outgoing = [False for _ in range(components)]
    component_sizes = [0 for _ in range(components)]
    for source, row in enumerate(rows):
        source_component = int(labels[source])
        component_sizes[source_component] += 1
        for target, _weight in row:
            if int(labels[target]) != source_component:
                outgoing[source_component] = True
    recurrent = [
        component
        for component in range(components)
        if not outgoing[component]
    ]
    return MoriMixedFirstReturnLevelReport(
        modulus_power2=modulus_power2,
        modulus_power3=modulus_power3,
        modulus=modulus,
        dimension=dimension,
        n1_residues=len(n1_residues),
        n2_residues=len(n2_residues),
        nonzero_entries=nonzero,
        lift_count_per_row=lift_count,
        max_return_steps=return_step_max,
        mean_return_steps=float(mean_steps),
        unresolved_lifts=unresolved_lifts,
        row_sum_min=float(min(row_sums)) if row_sums else 0.0,
        row_sum_max=float(max(row_sums)) if row_sums else 0.0,
        spectral_radius=spectral_radius,
        second_eigenvalue_abs=second,
        operator_norm_l2=operator_norm,
        strongly_connected_components=int(components),
        recurrent_components=len(recurrent),
        recurrent_states=sum(component_sizes[component] for component in recurrent),
        status=f"mixed_2_3_mori_first_return_finite_lift_average_{eig_status}",
    )


def mori_mixed_first_return_report(
    levels: tuple[tuple[int, int], ...] = ((6, 2), (8, 3), (10, 3)),
    lift_power: int = 3,
    max_return_steps: int = 200,
) -> MoriMixedFirstReturnReport:
    """Finite lift-averaged first-return model for Mori's N1 union N2 set."""

    return MoriMixedFirstReturnReport(
        type="mori_mixed_first_return_operator",
        status="finite_lift_averaged_projection_not_collatz_proof",
        map_convention=(
            "Original Collatz branch operator: odd n -> 3n+1, even n -> n/2. "
            "First-return set is N1={n mod 6 in {1,5}} union "
            "N2={3n+1: n in N1}."
        ),
        finite_model_caveat=(
            "Rows average over finitely many integer lifts of each residue. "
            "This resolves some division-by-two ambiguity but remains a finite "
            "quotient diagnostic, not an infinite-dimensional Mori theorem."
        ),
        levels=tuple(
            _mori_mixed_first_return_level_report(
                modulus_power2=k,
                modulus_power3=ell,
                lift_power=lift_power,
                max_return_steps=max_return_steps,
            )
            for k, ell in levels
        ),
    )


def _paparella_level_report(n: int) -> PaparellaNilpotencyLevelReport:
    if n < 4:
        raise ValueError("n must be at least 4")
    vertices = set(range(3, n + 1))
    max_escape = 0
    edges_inside = 0
    cycle_found = False
    for start in vertices:
        seen: dict[int, int] = {}
        x = start
        depth = 0
        while x in vertices:
            if x in seen:
                cycle_found = True
                break
            seen[x] = depth
            y = _collatz_full_step(x)
            if y in vertices:
                edges_inside += 1 if x == start else 0
            x = y
            depth += 1
            if depth > len(vertices):
                cycle_found = True
                break
        max_escape = max(max_escape, depth)
    nilpotent = (not cycle_found) and max_escape <= len(vertices)
    return PaparellaNilpotencyLevelReport(
        n=n,
        dimension=len(vertices),
        nonzero_edges_inside=sum(
            1 for source in vertices if _collatz_full_step(source) in vertices
        ),
        nilpotent_by_escape_depth=nilpotent,
        max_escape_depth=max_escape,
        nontrivial_cycle_found=cycle_found,
        status=(
            "truncated_nontrivial_submatrix_nilpotent"
            if nilpotent
            else "truncated_nontrivial_cycle_or_escape_depth_failure"
        ),
    )


def _read_projection(path: Path, name: str) -> UnifiedSavedProjectionReport:
    if not path.exists():
        return UnifiedSavedProjectionReport(
            name=name,
            path=str(path),
            available=False,
            summary={},
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    summary_keys = (
        "type",
        "status",
        "max_tv_nth_iterate_to_tao",
        "max_tv_all_iterates_to_tao",
        "fitted_empirical_power_exponent",
        "best_markov_rate",
        "best_iid_all_excursion_rate",
        "cramer_rate_range_width",
        "cramer_rate_slope_per_log10",
        "best_debiased_mutual_information_bits",
        "lag4_debiased_mutual_information_bits",
        "max_T_times_n",
        "universal_bound_3_passes",
        "map_convention",
        "finite_model_caveat",
        "theorem_or_finite_entries",
        "high_confidence_entries",
        "empirical_envelope_entries",
        "cramer_rate_I0",
        "cramer_lambda",
        "tilted_variance_at_lambda",
        "bootstrap_repetitions",
        "headline_finding",
        "key_caveat",
        "exact_log_growth_affine_coordinate_base2",
        "exact_typical_factor_affine_coordinate",
        "monte_carlo_log_growth_base2",
        "candidate_value",
        "empirical_cramer_rate",
        "candidate_inside_bootstrap_ci",
        "verdict",
        "dominant_segment",
        "dominant_segment_percent_of_mgf",
        "heavy_tail_correction",
        "heavy_tail_relative_multiplier",
        "interpolated_decomposition_rate",
        "scalar_certificate_note",
        "homogeneous_caveat",
        "next_step",
        "coordinate_model",
    )
    if "levels" in data and isinstance(data["levels"], list):
        summary: dict[str, Any] = {
            key: data[key] for key in summary_keys if key in data
        }
        summary["levels"] = len(data["levels"])
        if data["levels"]:
            last = data["levels"][-1]
            for key in (
                "modulus_power2",
                "modulus_power3",
                "dimension",
                "second_eigenvalue_abs",
                "recurrent_components",
                "recurrent_states",
                "unresolved_lifts",
                "modulus_power",
                "affine_quotient_jsr_lower",
                "affine_quotient_jsr_upper",
                "homogeneous_jsr_lower",
                "homogeneous_jsr_upper",
                "obstruction_kind",
                "obstruction_word",
                "tail_unit_power",
                "max_tail_depth",
                "affine_quotient_jsr",
                "overflow_edges",
                "all_one_self_loop_detected",
                "worst_case_jsr_factor",
                "largest_component_average_log2_growth_per_accelerated_step",
                "largest_component_typical_factor_per_accelerated_step",
                "recurrent_components",
                "largest_recurrent_component_states",
            ):
                if key in last:
                    summary[f"last_{key}"] = last[key]
            if "tail_filtered" in last:
                cutoff_two = [
                    item
                    for item in last["tail_filtered"]
                    if int(item.get("tail_depth_cutoff", -1)) == 2
                ]
                if cutoff_two:
                    summary["last_tail_cutoff_2_affine_jsr"] = cutoff_two[0][
                        "affine_quotient_jsr"
                    ]
        return UnifiedSavedProjectionReport(
            name=name,
            path=str(path),
            available=True,
            summary=summary,
        )
    return UnifiedSavedProjectionReport(
        name=name,
        path=str(path),
        available=True,
        summary={key: data[key] for key in summary_keys if key in data},
    )


def unified_collatz_operator_report(
    dyadic_powers: tuple[int, ...] = (8, 10, 12),
    paparella_n_values: tuple[int, ...] = (64, 128, 256, 512),
    reports_dir: str | Path = "docs/reports",
) -> UnifiedCollatzOperatorReport:
    """Assemble finite projections of the shared Collatz operator picture."""

    reports_path = Path(reports_dir)
    dyadic = tuple(_dyadic_level_report(power) for power in dyadic_powers)
    paparella = tuple(_paparella_level_report(n) for n in paparella_n_values)
    saved = (
        _read_projection(reports_path / "tao_syrac_empirical.json", "tao_tv"),
        _read_projection(
            reports_path / "tao_characteristic_function_decay.json",
            "tao_characteristic_decay",
        ),
        _read_projection(
            reports_path / "orbit_renewal_n0_stability.json",
            "renewal_n0_stability",
        ),
        _read_projection(
            reports_path / "orbit_renewal_markov_cramer.json",
            "renewal_markov_cramer",
        ),
        _read_projection(
            reports_path / "valuation_mi_lags.json",
            "valuation_mi_lags",
        ),
        _read_projection(
            reports_path / "hercher_t_ni_bound.json",
            "hercher_reciprocal_sum",
        ),
        _read_projection(
            reports_path / "paparella_nilpotency.json",
            "paparella_nilpotency",
        ),
        _read_projection(
            reports_path / "mori_mixed_first_return_operator.json",
            "mori_mixed_first_return",
        ),
        _read_projection(
            reports_path / "rigorous_bound_squeeze.json",
            "rigorous_bound_squeeze",
        ),
        _read_projection(
            reports_path / "renewal_bootstrap_calibration.json",
            "renewal_bootstrap_calibration",
        ),
        _read_projection(
            reports_path / "projective_jsr_claude_background.json",
            "projective_jsr_background",
        ),
        _read_projection(
            reports_path / "constrained_projective_jsr.json",
            "constrained_projective_jsr",
        ),
        _read_projection(
            reports_path / "tail_aware_projective_jsr.json",
            "tail_aware_projective_jsr",
        ),
        _read_projection(
            reports_path / "tail_aware_lte_closed_projective_jsr.json",
            "tail_aware_lte_closed_projective_jsr",
        ),
        _read_projection(
            reports_path / "tail_aware_markov_lyapunov.json",
            "tail_aware_markov_lyapunov",
        ),
        _read_projection(
            reports_path / "christoffel_filtered_jsr.json",
            "christoffel_filtered_tail_jsr",
        ),
        _read_projection(
            reports_path / "lyapunov_furstenberg.json",
            "furstenberg_lyapunov",
        ),
        _read_projection(
            reports_path / "jazz_constant_closed_form_test.json",
            "jazz_constant_closed_form_test",
        ),
        _read_projection(
            reports_path / "jazz_constant_spike_decomposition.json",
            "jazz_constant_spike_decomposition",
        ),
    )
    return UnifiedCollatzOperatorReport(
        type="unified_collatz_operator_finite_projection",
        status="finite_synthesis_not_collatz_proof",
        model_name="lift_averaged_Mori_T1_plus_T2_with_Tao_Hercher_Paparella_PECM_projections",
        finite_model_caveat=(
            "Division by two is not well-defined on Z/2^k; dyadic levels use "
            "a lift-averaged transfer quotient. Saved projections summarize "
            "separate finite experiments rather than proving an infinite "
            "operator theorem."
        ),
        dyadic_levels=dyadic,
        paparella_levels=paparella,
        saved_projections=saved,
    )
