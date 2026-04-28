"""Empirical Lasota-Yorke diagnostics for the PECM operator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .post_exit_map import _apply_targets, _build_post_exit_target_array, _state_count


@dataclass(frozen=True)
class LasotaYorkeSampleFit:
    sample_index: int
    initial_bv: float
    initial_sup: float
    rho_fit: float
    bv_norms: tuple[float, ...]
    sup_norms: tuple[float, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bv_norms"] = list(self.bv_norms)
        data["sup_norms"] = list(self.sup_norms)
        return data


@dataclass(frozen=True)
class LasotaYorkeReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    states: int
    sample_lift_power: int
    row_denominator: int
    max_steps: int
    samples_requested: int
    samples_completed: int
    random_seed: int
    estimated_dense_vector_gib: float
    estimated_target_cache_gib: float
    rho_median: float
    rho_max: float
    sup_ratio_max: float
    C_estimate: float
    D_estimate: float
    sample_fits: tuple[LasotaYorkeSampleFit, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "states": self.states,
            "sample_lift_power": self.sample_lift_power,
            "row_denominator": self.row_denominator,
            "max_steps": self.max_steps,
            "samples_requested": self.samples_requested,
            "samples_completed": self.samples_completed,
            "random_seed": self.random_seed,
            "estimated_dense_vector_gib": self.estimated_dense_vector_gib,
            "estimated_target_cache_gib": self.estimated_target_cache_gib,
            "rho_median": self.rho_median,
            "rho_max": self.rho_max,
            "sup_ratio_max": self.sup_ratio_max,
            "C_estimate": self.C_estimate,
            "D_estimate": self.D_estimate,
            "sample_fits": [sample.to_json_dict() for sample in self.sample_fits],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _bv_norm(values, shape: tuple[int, int, int]) -> float:
    import numpy as np

    cube = values.reshape(shape)
    total = float(np.abs(np.diff(cube, axis=0)).sum())
    total += float(np.abs(np.diff(cube, axis=1)).sum())
    total += float(np.abs(np.diff(cube, axis=2)).sum())
    return total


def _random_box_function(rng, shape: tuple[int, int, int]):
    import numpy as np

    values = np.zeros(shape, dtype=np.float64)
    boxes = int(rng.integers(2, 7))
    for _ in range(boxes):
        starts = [int(rng.integers(0, dim)) for dim in shape]
        stops = [int(rng.integers(start + 1, dim + 1)) for start, dim in zip(starts, shape, strict=True)]
        amplitude = float(rng.choice([-1.0, 1.0]) * rng.uniform(0.25, 1.0))
        values[
            starts[0] : stops[0],
            starts[1] : stops[1],
            starts[2] : stops[2],
        ] += amplitude
    return values.reshape(-1)


def lasota_yorke_report(
    mod2_power: int = 12,
    mod3_power: int = 4,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    iterates: int = 10,
    sample_count: int = 32,
    random_seed: int = 0,
) -> LasotaYorkeReport:
    """Fit empirical BV contraction rates for random box-indicator functions."""

    import numpy as np

    states = _state_count(mod2_power, mod3_power, R_values)
    n2 = 1 << (mod2_power - 1)
    n3 = 3**mod3_power
    shape = (len(R_values), n2, n3)
    denominator = 1 << sample_lift_power
    (
        targets,
        _descended,
        _reentered,
        _out_of_range,
        _max_survival,
        _worst_index,
    ) = _build_post_exit_target_array(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        tail_reentry_min_R=2,
    )
    rng = np.random.default_rng(random_seed)
    fits: list[LasotaYorkeSampleFit] = []
    rho_values: list[float] = []
    sup_ratios: list[float] = []
    for sample_index in range(sample_count):
        vector = _random_box_function(rng, shape)
        bv_norms = [_bv_norm(vector, shape)]
        sup_norms = [float(np.max(np.abs(vector), initial=0.0))]
        for _ in range(iterates):
            vector = _apply_targets(targets, vector, denominator)
            bv_norms.append(_bv_norm(vector, shape))
            sup_norms.append(float(np.max(np.abs(vector), initial=0.0)))
        positive = [
            (n, value)
            for n, value in enumerate(bv_norms)
            if n > 0 and value > 0 and bv_norms[0] > 0
        ]
        if len(positive) >= 2:
            xs = np.array([n for n, _ in positive], dtype=float)
            ys = np.log(np.array([value / bv_norms[0] for _, value in positive], dtype=float))
            slope, _intercept = np.polyfit(xs, ys, deg=1)
            rho_fit = float(np.exp(slope))
        else:
            rho_fit = 0.0
        rho_values.append(rho_fit)
        if sup_norms[0] > 0:
            sup_ratios.extend(value / sup_norms[0] for value in sup_norms[1:])
        fits.append(
            LasotaYorkeSampleFit(
                sample_index=sample_index,
                initial_bv=bv_norms[0],
                initial_sup=sup_norms[0],
                rho_fit=rho_fit,
                bv_norms=tuple(float(value) for value in bv_norms),
                sup_norms=tuple(float(value) for value in sup_norms),
            )
        )
    rho_median = float(np.median(rho_values)) if rho_values else 0.0
    rho_max = max(rho_values, default=0.0)
    sup_ratio_max = max(sup_ratios, default=0.0)
    rho_for_bound = min(0.999999, max(rho_median, 1e-12))
    C_estimate = 0.0
    for fit in fits:
        if fit.initial_bv <= 0:
            continue
        for n, value in enumerate(fit.bv_norms):
            C_estimate = max(C_estimate, value / ((rho_for_bound**n) * fit.initial_bv))
    return LasotaYorkeReport(
        type="post_exit_pecm_lasota_yorke_empirical",
        status="empirical_BV_fit_not_lasota_yorke_proof",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        states=states,
        sample_lift_power=sample_lift_power,
        row_denominator=denominator,
        max_steps=max_steps,
        samples_requested=sample_count,
        samples_completed=len(fits),
        random_seed=random_seed,
        estimated_dense_vector_gib=states * 8 / (1024**3),
        estimated_target_cache_gib=states * denominator * 4 / (1024**3),
        rho_median=rho_median,
        rho_max=rho_max,
        sup_ratio_max=sup_ratio_max,
        C_estimate=C_estimate,
        D_estimate=sup_ratio_max,
        sample_fits=tuple(fits),
    )
