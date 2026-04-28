"""Finite LP tuning for the tail Lyapunov scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import floor, log2
from typing import Any

from .tail_spectral import TailSpectralLadderReport, tail_spectral_ladder


@dataclass(frozen=True)
class TailLyapunovLPReport:
    type: str
    status: str
    R0: int
    margin: float
    spectral_lambda_bound: float
    spectral_gap: float
    lte_drop_bound: int
    beta: float | None
    gamma: float | None
    objective: float | None
    spectral_ladder: TailSpectralLadderReport

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["spectral_ladder"] = self.spectral_ladder.to_json_dict()
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def lte_tail_depth_drop_bound(R0: int) -> int:
    """Lower bound for ``R - (2 + floor(log2 R))`` for ``R >= R0``."""

    if R0 < 3:
        raise ValueError("R0 must be at least three")
    return R0 - 2 - floor(log2(R0))


def tune_tail_lyapunov_lp(
    R0: int = 20,
    margin: float = 1e-3,
    k_values: tuple[int, ...] = (12, 14, 16, 18, 20),
    prefix_ones: int = 8,
    sample_lift_power: int = 6,
) -> TailLyapunovLPReport:
    """Tune ``V = log2(n) + beta*R + gamma*omega`` for finite tail checks.

    The sign on ``beta*R`` is intentionally positive: lowering the actual tail
    depth ``R=v2(n+1)`` must lower the monovariant. With the opposite sign, the
    LTE tail-depth collapse would increase the putative Lyapunov function.

    The spectral constraint is an expected-drift certificate for the sampled
    tail subkernel. The LTE constraint is a deterministic arithmetic scaffold.
    This is not a global Collatz proof.
    """

    ladder = tail_spectral_ladder(
        k_values=k_values,
        prefix_ones=prefix_ones,
        sample_lift_power=sample_lift_power,
    )
    lambda_bound = ladder.max_perron_eigenvalue
    if lambda_bound is None:
        return TailLyapunovLPReport(
            type="tail_lyapunov_two_variable_lp",
            status="spectral_ladder_empty_lp_not_solved",
            R0=R0,
            margin=margin,
            spectral_lambda_bound=0.0,
            spectral_gap=0.0,
            lte_drop_bound=0,
            beta=None,
            gamma=None,
            objective=None,
            spectral_ladder=ladder,
        )
    gap = 1.0 - lambda_bound
    drop = lte_tail_depth_drop_bound(R0)
    log_growth = log2(3 / 2)
    if gap <= 0 or drop <= 0:
        return TailLyapunovLPReport(
            type="tail_lyapunov_two_variable_lp",
            status="infeasible_nonpositive_gap_or_drop",
            R0=R0,
            margin=margin,
            spectral_lambda_bound=lambda_bound,
            spectral_gap=gap,
            lte_drop_bound=drop,
            beta=None,
            gamma=None,
            objective=None,
            spectral_ladder=ladder,
        )

    try:
        import numpy as np
        from scipy.optimize import linprog
    except ImportError:
        beta = (log_growth + margin) / drop
        gamma = (log_growth + margin) / gap
        return TailLyapunovLPReport(
            type="tail_lyapunov_two_variable_lp",
            status="scipy_unavailable_closed_form_bounds",
            R0=R0,
            margin=margin,
            spectral_lambda_bound=lambda_bound,
            spectral_gap=gap,
            lte_drop_bound=drop,
            beta=beta,
            gamma=gamma,
            objective=beta + gamma,
            spectral_ladder=ladder,
        )

    result = linprog(
        c=np.array([1.0, 1.0]),
        A_ub=np.array(
            [
                [-drop, 0.0],
                [0.0, -gap],
            ],
            dtype=float,
        ),
        b_ub=np.array(
            [
                -(log_growth + margin),
                -(log_growth + margin),
            ],
            dtype=float,
        ),
        bounds=[(0.0, None), (0.0, None)],
        method="highs",
    )
    if not result.success:
        return TailLyapunovLPReport(
            type="tail_lyapunov_two_variable_lp",
            status=f"linprog_failed_{result.status}",
            R0=R0,
            margin=margin,
            spectral_lambda_bound=lambda_bound,
            spectral_gap=gap,
            lte_drop_bound=drop,
            beta=None,
            gamma=None,
            objective=None,
            spectral_ladder=ladder,
        )
    return TailLyapunovLPReport(
        type="tail_lyapunov_two_variable_lp",
        status="finite_tail_lyapunov_lp_feasible_not_global_proof",
        R0=R0,
        margin=margin,
        spectral_lambda_bound=lambda_bound,
        spectral_gap=gap,
        lte_drop_bound=drop,
        beta=float(result.x[0]),
        gamma=float(result.x[1]),
        objective=float(result.fun),
        spectral_ladder=ladder,
    )
