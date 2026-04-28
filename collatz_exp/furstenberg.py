"""Furstenberg-style Lyapunov diagnostics for random Collatz matrix products."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FurstenbergLyapunovReport:
    type: str
    status: str
    matrix_family: str
    valuation_law: str
    valuation_cutoff: int
    monte_carlo_steps: int
    random_seed: int
    exact_log_growth_affine_coordinate_base2: float
    exact_log_growth_homogeneous_coordinate_base2: float
    exact_log_growth_affine_coordinate_natural: float
    exact_typical_factor_affine_coordinate: float
    monte_carlo_log_growth_base2: float
    monte_carlo_projective_mean: float
    monte_carlo_projective_p05: float
    monte_carlo_projective_p95: float
    closed_form_note: str
    caveat: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _geom2_sample(rng: random.Random, cutoff: int) -> int:
    """Sample P(a=k)=2^-k, with optional tail lumped at cutoff."""

    if cutoff < 1:
        raise ValueError("cutoff must be positive")
    value = 1
    while value < cutoff and rng.random() >= 0.5:
        value += 1
    return value


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def furstenberg_lyapunov_report(
    valuation_cutoff: int = 64,
    monte_carlo_steps: int = 1_000_000,
    random_seed: int = 0,
) -> FurstenbergLyapunovReport:
    """Compute the iid Geom(2) random-product Lyapunov diagnostic.

    For the accelerated affine map ``x -> (3x+1)/2^a``, the coefficient of
    ``x`` is ``3/2^a``.  With ``a ~ Geom(2)``, ``E[a]=2``, so the affine
    coordinate exponent is exactly ``log2(3)-2 = log2(3/4)``.  The
    homogeneous triangular matrix has a second diagonal entry equal to ``1``;
    its top exponent is therefore ``max(log2(3)-2, 0)=0`` unless one restricts
    to the affine coordinate.
    """

    if monte_carlo_steps < 1:
        raise ValueError("monte_carlo_steps must be positive")
    exact_affine_base2 = math.log2(3.0) - 2.0
    exact_homogeneous_base2 = max(exact_affine_base2, 0.0)
    rng = random.Random(random_seed)
    log_growth_sum = 0.0
    projective = 1.0
    projective_samples: list[float] = []
    sample_stride = max(1, monte_carlo_steps // 10_000)
    for step in range(1, monte_carlo_steps + 1):
        valuation = _geom2_sample(rng, valuation_cutoff)
        multiplier = 3.0 / float(1 << valuation)
        log_growth_sum += math.log2(multiplier)
        projective = multiplier * projective + 1.0 / float(1 << valuation)
        if step % sample_stride == 0:
            projective_samples.append(projective)

    return FurstenbergLyapunovReport(
        type="furstenberg_random_product_lyapunov",
        status="closed_form_random_model_confirmed_not_collatz_proof",
        matrix_family="affine accelerated Collatz matrices [[3/2^a, 1/2^a], [0, 1]]",
        valuation_law="iid Geom(2), P(a=k)=2^-k",
        valuation_cutoff=valuation_cutoff,
        monte_carlo_steps=monte_carlo_steps,
        random_seed=random_seed,
        exact_log_growth_affine_coordinate_base2=exact_affine_base2,
        exact_log_growth_homogeneous_coordinate_base2=exact_homogeneous_base2,
        exact_log_growth_affine_coordinate_natural=math.log(3.0 / 4.0),
        exact_typical_factor_affine_coordinate=2.0**exact_affine_base2,
        monte_carlo_log_growth_base2=log_growth_sum / monte_carlo_steps,
        monte_carlo_projective_mean=sum(projective_samples) / len(projective_samples),
        monte_carlo_projective_p05=_quantile(projective_samples, 0.05),
        monte_carlo_projective_p95=_quantile(projective_samples, 0.95),
        closed_form_note=(
            "The affine-coordinate exponent is E[log2(3/2^a)] = log2(3)-E[a]. "
            "For Geom(2), E[a]=2, giving log2(3/4)."
        ),
        caveat=(
            "This is an iid random-switching model. Collatz valuation sequences "
            "are residue-constrained and weakly dependent; the report is a "
            "calibration baseline, not a proof for actual orbits."
        ),
    )
