"""Exact-rational Collatz-Wielandt certificates for finite PECM operators.

Upgrades the floating-point scaled-Perron scan at small levels to a certified
statement: for the exact finite substochastic PECM operator A at level
(mod2_power, mod3_power) — whose target array is built with exact integer
arithmetic — and ANY strictly positive vector v, the Collatz-Wielandt bound

    rho(A) <= max_i (A v)_i / v_i

holds. Taking v as a rationalized float Perron vector and evaluating the
right-hand side in pure integer arithmetic yields a certified rational upper
bound on the spectral radius, tight to the quality of v. A bound below 1 is a
rigorous finite spectral statement, free of floating-point error.

Caveat (PROJECT_JOURNEY §12): rho(A) < 1 for this averaged finite operator is
a spectral-gap statement about the residue-quotient operator. It is NOT an
orbit-descent certificate and does not bound deterministic per-orbit growth.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction

from .post_exit_map import (
    _build_post_exit_target_array,
    _decode_state_index,
)

_DEFAULT_R_VALUES = tuple(range(2, 31))


@dataclass
class PerronCertificateLevel:
    mod2_power: int
    mod3_power: int
    states: int
    row_denominator: int
    power_iterations: int
    float_scale_estimate: float
    rational_grid_digits: int
    scc_block_count: int
    certified_block_count: int
    largest_block_states: int
    certified_upper_numerator: str
    certified_upper_denominator: str
    certified_upper_float: float
    certified_contraction: bool
    worst_row_state: dict | None

    def to_json_dict(self) -> dict:
        return asdict(self)


@dataclass
class PerronCertificateReport:
    configurations: tuple[tuple[int, int], ...]
    sample_lift_power: int
    max_steps: int
    tail_reentry_min_R: int
    levels: tuple[PerronCertificateLevel, ...]
    note: str

    def to_json_dict(self) -> dict:
        return {
            "configurations": [list(pair) for pair in self.configurations],
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "tail_reentry_min_R": self.tail_reentry_min_R,
            "levels": [level.to_json_dict() for level in self.levels],
            "note": self.note,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _float_perron_vector(targets, denominator: int, iterations: int):
    import numpy as np

    n = targets.shape[0]
    vector = np.ones(n, dtype=np.float64)
    scale = 0.0
    for _ in range(iterations):
        image = np.zeros(n, dtype=np.float64)
        for col in range(targets.shape[1]):
            target = targets[:, col]
            mask = target >= 0
            image[mask] += vector[target[mask]]
        image /= denominator
        next_scale = float(image.max(initial=0.0))
        if next_scale == 0.0:
            return image, 0.0
        vector = image / next_scale
        scale = next_scale
    return vector, scale


def _scc_labels(targets):
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components

    mask = targets >= 0
    row_counts = mask.sum(axis=1).astype(np.int64)
    indptr = np.empty(targets.shape[0] + 1, dtype=np.int64)
    indptr[0] = 0
    np.cumsum(row_counts, out=indptr[1:])
    indices = targets[mask].astype(np.int64, copy=False)
    data = np.ones(indices.shape[0], dtype=np.int8)
    graph = csr_matrix(
        (data, indices, indptr), shape=(targets.shape[0], targets.shape[0])
    )
    _count, labels = connected_components(
        graph,
        directed=True,
        connection="strong",
        return_labels=True,
    )
    return labels


def _certify_block(
    block_rows,
    block_targets,
    denominator: int,
    power_iterations: int,
    grid: int,
):
    """Exact Collatz-Wielandt bound for one irreducible diagonal block.

    block_targets holds local indices (or -1) for edges inside the block.
    Returns (bound_numerator, bound_denominator, worst_local_row).
    """
    import numpy as np

    n = len(block_rows)
    vector = np.ones(n, dtype=np.float64)
    for _ in range(power_iterations):
        image = np.zeros(n, dtype=np.float64)
        for col in range(block_targets.shape[1]):
            target = block_targets[:, col]
            mask = target >= 0
            image[mask] += vector[target[mask]]
        image /= denominator
        peak = float(image.max(initial=0.0))
        if peak == 0.0:
            break
        # Smooth against imprimitivity: keep the iterate strictly positive.
        vector = 0.5 * (image / peak) + 0.5 * vector
        vector /= float(vector.max(initial=1.0))
    nums = [max(1, round(float(value) * grid)) for value in vector]
    best_num = 0
    best_den = 1
    worst_local = None
    for local_row, row_targets in enumerate(block_targets.tolist()):
        image_num = 0
        for target in row_targets:
            if target >= 0:
                image_num += nums[target]
        if image_num == 0:
            continue
        row_den = denominator * nums[local_row]
        if image_num * best_den > best_num * row_den:
            best_num = image_num
            best_den = row_den
            worst_local = local_row
    return best_num, best_den, worst_local


def certify_level(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...] = _DEFAULT_R_VALUES,
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    power_iterations: int = 200,
    rational_grid_digits: int = 9,
) -> PerronCertificateLevel:
    import numpy as np

    targets, _descended, _reentered, _out_of_range, _max_survival, _worst = (
        _build_post_exit_target_array(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
        )
    )
    denominator = 1 << sample_lift_power
    _vector, scale = _float_perron_vector(targets, denominator, power_iterations)

    # rho(A) = max over strongly connected diagonal blocks of rho(block):
    # the SCC condensation is block upper-triangular, so the spectrum is the
    # union of the diagonal-block spectra. Singleton blocks without self-loop
    # contribute rho = 0.
    labels = _scc_labels(targets)
    grid = 10**rational_grid_digits
    label_order = np.argsort(labels, kind="stable")
    boundaries = np.flatnonzero(np.diff(labels[label_order])) + 1
    groups = np.split(label_order, boundaries)

    bound = Fraction(0)
    worst_row = None
    scc_block_count = len(groups)
    certified_block_count = 0
    largest_block_states = 0
    for group in groups:
        rows = group
        if len(rows) == 1:
            row = int(rows[0])
            if not any(int(t) == row for t in targets[row]):
                continue
        largest_block_states = max(largest_block_states, len(rows))
        local_index = {int(row): i for i, row in enumerate(rows)}
        block_targets = np.full((len(rows), targets.shape[1]), -1, dtype=np.int64)
        for local_row, row in enumerate(rows):
            for col, target in enumerate(targets[int(row)]):
                target = int(target)
                if target >= 0 and target in local_index:
                    block_targets[local_row, col] = local_index[target]
        best_num, best_den, worst_local = _certify_block(
            rows,
            block_targets,
            denominator,
            power_iterations,
            grid,
        )
        certified_block_count += 1
        if worst_local is not None:
            block_bound = Fraction(best_num, best_den)
            if block_bound > bound:
                bound = block_bound
                worst_row = int(rows[worst_local])
    return PerronCertificateLevel(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        states=targets.shape[0],
        row_denominator=denominator,
        power_iterations=power_iterations,
        float_scale_estimate=scale,
        rational_grid_digits=rational_grid_digits,
        scc_block_count=scc_block_count,
        certified_block_count=certified_block_count,
        largest_block_states=largest_block_states,
        certified_upper_numerator=str(bound.numerator),
        certified_upper_denominator=str(bound.denominator),
        certified_upper_float=float(bound),
        certified_contraction=bound < 1,
        worst_row_state=None
        if worst_row is None
        else asdict(
            _decode_state_index(worst_row, mod2_power, mod3_power, R_values)
        ),
    )


def perron_certificate_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 2), (10, 3)),
    R_values: tuple[int, ...] = _DEFAULT_R_VALUES,
    sample_lift_power: int = 2,
    max_steps: int = 200,
    tail_reentry_min_R: int = 2,
    power_iterations: int = 200,
    rational_grid_digits: int = 9,
) -> PerronCertificateReport:
    levels = tuple(
        certify_level(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            tail_reentry_min_R=tail_reentry_min_R,
            power_iterations=power_iterations,
            rational_grid_digits=rational_grid_digits,
        )
        for mod2_power, mod3_power in configurations
    )
    note = (
        "Certified via SCC decomposition + Collatz-Wielandt: rho(A) equals the "
        "max of rho over strongly connected diagonal blocks; within each block "
        "rho <= max_i (Av)_i/v_i for any positive v, evaluated in exact "
        "integer arithmetic. Spectral statement about the averaged "
        "residue-quotient operator only; not an orbit-descent certificate "
        "(PROJECT_JOURNEY §12)."
    )
    return PerronCertificateReport(
        configurations=tuple(configurations),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=tail_reentry_min_R,
        levels=levels,
        note=note,
    )


def format_perron_certificate_report(report: PerronCertificateReport) -> str:
    lines = []
    for level in report.levels:
        lines.append(
            "  ({k},{l}): states={states} float_scale={scale:.6f} "
            "certified_upper={upper:.9f} (exact {num}/{den}) "
            "contraction={contraction} sccs={sccs} certified_blocks={blocks} "
            "largest_block={largest}".format(
                k=level.mod2_power,
                l=level.mod3_power,
                states=level.states,
                scale=level.float_scale_estimate,
                upper=level.certified_upper_float,
                num=level.certified_upper_numerator
                if len(level.certified_upper_numerator) <= 24
                else level.certified_upper_numerator[:21] + "...",
                den=level.certified_upper_denominator
                if len(level.certified_upper_denominator) <= 24
                else level.certified_upper_denominator[:21] + "...",
                contraction=level.certified_contraction,
                sccs=level.scc_block_count,
                blocks=level.certified_block_count,
                largest=level.largest_block_states,
            )
        )
    return "\n".join(lines)
