"""Exact higher-tail phase transfer and affine-ghost cusp certificates.

The recursive ``R=2`` frontier leaves one exact live branch after maximal
floor-loop compression.  If ``v2(u+1)=3m``, that branch follows
``(1,2)^m`` and lands at an arbitrary tail depth ``R >= 3``.  This module
parametrizes that transfer, carries mixed residues at proof-facing precision,
and records the exact phase-energy contraction.

The simple ``n+5`` cusp is not global after the transfer.  Its first exact
obstruction reveals a general replacement: every expanding affine valuation
word has a negative rational fixed point and a word-specific valuation cusp.
Those cusps contract while one word repeats; compatibility when the word
changes remains the open global problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .core import affine_from_word, apply_word, v2
from .symbolic_branch_certificate import (
    ExactMixedCylinder,
    least_positive_mixed_representative,
)
from .symbolic_frontier_certificate import (
    DEFAULT_NESTED_CUSP_BASE,
    nested_cusp_factor,
)


LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("docs/reports/pecm_r2_recursive_tail_cusp.json")
DEFAULT_INPUT_SHA256 = (
    "5ec3952845b37cea83dc20f3bdb3cafb5fa0b6e57e70abf9c274a562ffab9f13"
)
DEFAULT_OUTPUT_PATH = Path("docs/reports/pecm_higher_r_affine_ghost.json")
DEFAULT_TARGET_MOD2_POWER = 8
DEFAULT_SOURCE_U_MOD3 = 2
DEFAULT_SOURCE_MOD3_POWER = 2


@dataclass(frozen=True)
class R2HigherRTransferInstance:
    """One target-fixed member of the exact ``R=2`` to higher-``R`` family."""

    block_count: int
    target_R: int
    target_u_mod2: int
    target_mod2_power: int
    source: ExactMixedCylinder
    least_positive_u: int
    source_lift_modulus: int
    source_w: int
    source_n: int
    valuation_word: tuple[int, ...]
    intermediate_tail_depths: tuple[int, ...]
    target_n: int
    target_unit: int
    target: ExactMixedCylinder
    phase_base: Fraction
    phase_ratio: Fraction

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "block_count": self.block_count,
            "target_R": self.target_R,
            "target_u_mod2": self.target_u_mod2,
            "target_mod2_power": self.target_mod2_power,
            "source": self.source.to_json_dict(),
            "least_positive_u": str(self.least_positive_u),
            "source_lift_modulus": str(self.source_lift_modulus),
            "source_w": str(self.source_w),
            "source_n": str(self.source_n),
            "valuation_word": list(self.valuation_word),
            "intermediate_tail_depths": list(self.intermediate_tail_depths),
            "target_n": str(self.target_n),
            "target_unit": str(self.target_unit),
            "target": self.target.to_json_dict(),
            "phase_base": _fraction_json(self.phase_base),
            "phase_ratio": _fraction_json(self.phase_ratio),
        }


@dataclass(frozen=True)
class HigherRFirstPostStage:
    """The first post-tail step from one exact higher-``R`` state."""

    source_R: int
    source_unit: int
    source_n: int
    post_q: int
    valuation_word: tuple[int, ...]
    landing: int
    landing_tail_depth: int
    classification: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_R": self.source_R,
            "source_unit": str(self.source_unit),
            "source_n": str(self.source_n),
            "post_q": self.post_q,
            "valuation_word": list(self.valuation_word),
            "landing": str(self.landing),
            "landing_tail_depth": self.landing_tail_depth,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class AffineGhostCertificate:
    """One exact word-specific negative-fixed-point cusp certificate."""

    valuation_word: tuple[int, ...]
    M: int
    A: int
    B: int
    slope: Fraction
    linear_D: int
    ghost: Fraction
    source_n: int
    target_n: int
    source_linear_value: int
    target_linear_value: int
    source_linear_v2: int
    target_linear_v2: int
    base: Fraction
    potential_factor: Fraction
    contracts: bool

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "valuation_word": list(self.valuation_word),
            "affine": {
                "M": self.M,
                "A": self.A,
                "B": str(self.B),
                "map": (f"T(n) = (3^{self.M}*n + {self.B}) / 2^{self.A}"),
                "slope": _fraction_json(self.slope),
            },
            "linear_form": {
                "D": str(self.linear_D),
                "expression": f"{self.linear_D}*n + {self.B}",
                "ghost": _fraction_json(self.ghost),
            },
            "witness": {
                "source_n": str(self.source_n),
                "target_n": str(self.target_n),
                "source_linear_value": str(self.source_linear_value),
                "target_linear_value": str(self.target_linear_value),
                "source_linear_v2": self.source_linear_v2,
                "target_linear_v2": self.target_linear_v2,
                "valuation_drop": (self.source_linear_v2 - self.target_linear_v2),
                "repeat_budget": {
                    "initial_valuation_units": self.source_linear_v2,
                    "cost_per_exact_word": self.A,
                    "maximum_possible_consecutive_uses": (
                        self.source_linear_v2 // self.A
                    ),
                    "necessary_not_sufficient": True,
                },
            },
            "base": _fraction_json(self.base),
            "potential_factor": _fraction_json(self.potential_factor),
            "contracts": self.contracts,
        }


@dataclass(frozen=True)
class AffineGhostChartTransition:
    """Exact change of coordinates between two expanding affine ghosts."""

    source_word: tuple[int, ...]
    target_word: tuple[int, ...]
    source_D: int
    source_B: int
    target_D: int
    target_B: int
    linear_multiplier: Fraction
    additive_ghost_gap: Fraction

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.source_word),
            "target_word": list(self.target_word),
            "source_linear_form": (f"{self.source_D}*n + {self.source_B}"),
            "target_linear_form": (f"{self.target_D}*n + {self.target_B}"),
            "linear_multiplier": _fraction_json(self.linear_multiplier),
            "additive_ghost_gap": _fraction_json(self.additive_ghost_gap),
            "identity": (
                "L_target(T_source(n)) = "
                "linear_multiplier*L_source(n) + additive_ghost_gap"
            ),
        }


@dataclass(frozen=True)
class HigherRAffineGhostReport:
    """Machine-readable higher-tail phase and affine-ghost result."""

    type: str
    status: str
    provenance: dict[str, Any]
    higher_r_transfer: dict[str, Any]
    mixed_residue_transport: dict[str, Any]
    phase_energy: dict[str, Any]
    first_higher_r_stage: dict[str, Any]
    simple_cusp_obstruction: dict[str, Any]
    affine_ghost_theorem: dict[str, Any]
    finite_verification: dict[str, Any]
    frontier: dict[str, Any]
    max_plus: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "provenance": dict(self.provenance),
            "higher_r_transfer": dict(self.higher_r_transfer),
            "mixed_residue_transport": dict(self.mixed_residue_transport),
            "phase_energy": dict(self.phase_energy),
            "first_higher_r_stage": dict(self.first_higher_r_stage),
            "simple_cusp_obstruction": dict(self.simple_cusp_obstruction),
            "affine_ghost_theorem": dict(self.affine_ghost_theorem),
            "finite_verification": dict(self.finite_verification),
            "frontier": dict(self.frontier),
            "max_plus": dict(self.max_plus),
            "proof": dict(self.proof),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _fraction_json(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_input_artifact(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "json_parsed": False,
        "type_matches": False,
        "exit_grammar_present": False,
        "bounded_regression_passed": False,
        "global_proof_disclaimed": False,
        "fully_verified": False,
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("input artifact does not exist")
        return result
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        result["errors"].append(
            f"input artifact could not be parsed: {type(exc).__name__}"
        )
        return result
    if not isinstance(payload, dict):
        result["errors"].append("input artifact root is not an object")
        return result

    result["json_parsed"] = True
    result["type_matches"] = payload.get("type") == "pecm_r2_exact_recursive_tail_cusp"
    grammar = payload.get("induced_exit_grammar")
    branches = grammar.get("branches") if isinstance(grammar, dict) else None
    result["exit_grammar_present"] = bool(
        isinstance(grammar, dict)
        and grammar.get("status") == "exact_maximal_floor_loop_exit_partition"
        and isinstance(branches, list)
        and any(
            isinstance(branch, dict)
            and branch.get("S_exit") == 3
            and branch.get("outcome") == "higher_R_tail_reentry"
            for branch in branches
        )
    )
    proof = payload.get("proof")
    result["bounded_regression_passed"] = bool(
        isinstance(proof, dict)
        and proof.get("bounded_machine_regression_passed") is True
    )
    result["global_proof_disclaimed"] = bool(
        isinstance(proof, dict)
        and proof.get("global_collatz_proof") is False
        and proof.get("global_recursive_lyapunov_derived") is False
    )
    required = (
        "type_matches",
        "exit_grammar_present",
        "bounded_regression_passed",
        "global_proof_disclaimed",
    )
    result["fully_verified"] = all(result[key] is True for key in required)
    if not result["fully_verified"]:
        result["errors"].append(
            "artifact content does not certify the prior exit grammar"
        )
    return result


def higher_r_source_residue(
    block_count: int,
    target_R: int,
    target_u_mod2: int,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
) -> tuple[int, int]:
    """Return the source-unit residue fixing one higher-``R`` target."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    if target_R < 3:
        raise ValueError("target_R must be at least three")
    if target_mod2_power < 1:
        raise ValueError("target_mod2_power must be positive")
    target_modulus = 1 << target_mod2_power
    if not 0 <= target_u_mod2 < target_modulus or target_u_mod2 % 2 == 0:
        raise ValueError("target_u_mod2 must be an odd canonical residue")

    tail_q = target_R - 2
    w_power = tail_q + target_mod2_power
    w_modulus = 1 << w_power
    inverse_9m = pow(pow(9, block_count, w_modulus), -1, w_modulus)
    w_residue = ((1 + (target_u_mod2 << tail_q)) * inverse_9m) % w_modulus
    if w_residue % 2 == 0:
        raise AssertionError("target-fixed w residue is not odd")

    source_power = 3 * block_count + w_power
    source_modulus = 1 << source_power
    source_residue = ((w_residue << (3 * block_count)) - 1) % source_modulus
    return source_residue, source_power


def higher_r_event_residue(
    block_count: int,
    target_R: int,
) -> tuple[int, int]:
    """Return the source-unit residue fixing only the next tail depth."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    if target_R < 3:
        raise ValueError("target_R must be at least three")
    tail_q = target_R - 2
    w_power = tail_q + 1
    w_modulus = 1 << w_power
    w_residue = (
        (1 + (1 << tail_q)) * pow(pow(9, block_count, w_modulus), -1, w_modulus)
    ) % w_modulus
    source_power = 3 * block_count + w_power
    source_residue = ((w_residue << (3 * block_count)) - 1) % (1 << source_power)
    return source_residue, source_power


def higher_r_target_mod3(
    block_count: int,
    target_R: int,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
) -> tuple[int, int]:
    """Carry the source cylinder through its exact ``2m`` digit gain."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    if target_R < 3:
        raise ValueError("target_R must be at least three")
    if source_mod3_power < 0:
        raise ValueError("source_mod3_power must be nonnegative")
    source_modulus = 3**source_mod3_power
    if not 0 <= source_u_mod3 < source_modulus:
        raise ValueError("source_u_mod3 must be a canonical residue")

    target_power = source_mod3_power + 2 * block_count
    target_modulus = 3**target_power
    if source_modulus == 1:
        w_mod3 = 0
    else:
        w_mod3 = (
            (source_u_mod3 + 1)
            * pow(pow(2, 3 * block_count, source_modulus), -1, source_modulus)
        ) % source_modulus
    numerator = (pow(9, block_count, target_modulus) * w_mod3 - 1) % target_modulus
    tail_q = target_R - 2
    target_residue = (
        numerator * pow(pow(2, tail_q, target_modulus), -1, target_modulus)
    ) % target_modulus
    return target_residue, target_power


def higher_r_reentry_source_residue(
    source_R: int,
    post_q: int,
    reentry_depth: int,
    target_u_mod2: int,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
) -> tuple[int, int]:
    """Fix one target unit after the first higher-``R`` post stage.

    ``reentry_depth >= 2`` describes an actual tail reentry.  The same
    formula also accepts ``reentry_depth == 1`` so the continuing post-exit
    branch can be represented without a separate convention.
    """

    if source_R < 3:
        raise ValueError("source_R must be at least three")
    if post_q < 1:
        raise ValueError("post_q must be positive")
    if reentry_depth < 1:
        raise ValueError("reentry_depth must be positive")
    if target_mod2_power < 1:
        raise ValueError("target_mod2_power must be positive")
    target_modulus = 1 << target_mod2_power
    if not 0 <= target_u_mod2 < target_modulus or target_u_mod2 % 2 == 0:
        raise ValueError("target_u_mod2 must be an odd canonical residue")

    source_power = post_q + reentry_depth + target_mod2_power
    source_modulus = 1 << source_power
    numerator = (target_u_mod2 << (post_q + reentry_depth)) - ((1 << post_q) - 1)
    source_residue = (
        numerator * pow(pow(3, source_R, source_modulus), -1, source_modulus)
    ) % source_modulus
    if source_residue % 2 == 0:
        raise AssertionError("target-fixed higher-R source unit is not odd")
    return source_residue, source_power


def higher_r_reentry_target_mod3(
    source_R: int,
    post_q: int,
    reentry_depth: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> tuple[int, int]:
    """Carry source 3-adic precision through the first post-stage landing."""

    if source_R < 3:
        raise ValueError("source_R must be at least three")
    if post_q < 1:
        raise ValueError("post_q must be positive")
    if reentry_depth < 1:
        raise ValueError("reentry_depth must be positive")
    if source_mod3_power < 0:
        raise ValueError("source_mod3_power must be nonnegative")
    source_modulus = 3**source_mod3_power
    if not 0 <= source_u_mod3 < source_modulus:
        raise ValueError("source_u_mod3 must be a canonical residue")

    target_power = source_mod3_power + source_R
    target_modulus = 3**target_power
    numerator = (
        pow(3, source_R, target_modulus) * source_u_mod3 + (1 << post_q) - 1
    ) % target_modulus
    target_residue = (
        numerator
        * pow(
            pow(2, post_q + reentry_depth, target_modulus),
            -1,
            target_modulus,
        )
    ) % target_modulus
    return target_residue, target_power


def higher_r_phase_factor(
    block_count: int,
    base: Fraction = DEFAULT_NESTED_CUSP_BASE,
) -> Fraction:
    """Return the exact full-transfer phase-energy ratio."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    return nested_cusp_factor(base) ** block_count


def higher_r_transfer_instance(
    block_count: int,
    target_R: int,
    target_u_mod2: int,
    *,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
    phase_base: Fraction = DEFAULT_NESTED_CUSP_BASE,
) -> R2HigherRTransferInstance:
    """Construct and replay one exact higher-tail phase transfer."""

    if phase_base <= 1:
        raise ValueError("phase_base must be greater than one")
    source_residue, source_power = higher_r_source_residue(
        block_count,
        target_R,
        target_u_mod2,
        target_mod2_power,
    )
    source = ExactMixedCylinder(
        R=2,
        u_mod2=source_residue,
        mod2_power=source_power,
        u_mod3=source_u_mod3,
        mod3_power=source_mod3_power,
    )
    source_u, lift_modulus = least_positive_mixed_representative(source)
    source_shift = v2(source_u + 1)
    if source_shift != 3 * block_count:
        raise AssertionError("source does not have the required cusp depth")
    source_w = (source_u + 1) >> source_shift
    source_n = 4 * source_u - 1
    valuation_word = (1, 2) * block_count

    x = source_n
    intermediate_depths: list[int] = []
    for _ in range(block_count):
        x = apply_word(x, (1, 2))
        intermediate_depths.append(v2(x + 1))
    target_n = x
    expected_depths = [2] * (block_count - 1) + [target_R]
    if intermediate_depths != expected_depths:
        raise AssertionError("higher-tail intermediate depths changed")

    tail_q = target_R - 2
    target_unit = (target_n + 1) >> target_R
    if target_unit != (pow(9, block_count) * source_w - 1) >> tail_q:
        raise AssertionError("higher-tail target unit identity failed")
    target_mod3, target_mod3_power = higher_r_target_mod3(
        block_count,
        target_R,
        source_u_mod3,
        source_mod3_power,
    )
    target = ExactMixedCylinder(
        R=target_R,
        u_mod2=target_unit % (1 << target_mod2_power),
        mod2_power=target_mod2_power,
        u_mod3=target_unit % (3**target_mod3_power),
        mod3_power=target_mod3_power,
    )
    if target.u_mod2 != target_u_mod2 or target.u_mod3 != target_mod3:
        raise AssertionError("higher-tail target residue transport failed")

    phase_ratio = Fraction(target_n + 5, source_n + 5) / (
        phase_base ** (3 * block_count)
    )
    expected_ratio = higher_r_phase_factor(block_count, phase_base)
    if phase_ratio != expected_ratio:
        raise AssertionError("higher-tail phase-energy identity failed")

    return R2HigherRTransferInstance(
        block_count=block_count,
        target_R=target_R,
        target_u_mod2=target_u_mod2,
        target_mod2_power=target_mod2_power,
        source=source,
        least_positive_u=source_u,
        source_lift_modulus=lift_modulus,
        source_w=source_w,
        source_n=source_n,
        valuation_word=valuation_word,
        intermediate_tail_depths=tuple(intermediate_depths),
        target_n=target_n,
        target_unit=target_unit,
        target=target,
        phase_base=phase_base,
        phase_ratio=phase_ratio,
    )


def verify_higher_r_transfer_instance(
    instance: R2HigherRTransferInstance,
) -> bool:
    """Independently verify a stored higher-tail transfer."""

    try:
        if instance.phase_base <= 1:
            return False
        expected_residue, expected_power = higher_r_source_residue(
            instance.block_count,
            instance.target_R,
            instance.target_u_mod2,
            instance.target_mod2_power,
        )
        if (
            instance.source.R != 2
            or instance.source.u_mod2 != expected_residue
            or instance.source.mod2_power != expected_power
        ):
            return False
        source_u, lift_modulus = least_positive_mixed_representative(instance.source)
        if (
            source_u != instance.least_positive_u
            or lift_modulus != instance.source_lift_modulus
            or v2(source_u + 1) != 3 * instance.block_count
        ):
            return False
        source_w = (source_u + 1) >> (3 * instance.block_count)
        source_n = 4 * source_u - 1
        word = (1, 2) * instance.block_count
        x = source_n
        intermediate_depths: list[int] = []
        for _ in range(instance.block_count):
            x = apply_word(x, (1, 2))
            intermediate_depths.append(v2(x + 1))
        target_n = x
        target_unit = (target_n + 1) >> instance.target_R
        expected_mod3, expected_mod3_power = higher_r_target_mod3(
            instance.block_count,
            instance.target_R,
            instance.source.u_mod3,
            instance.source.mod3_power,
        )
        phase_ratio = Fraction(target_n + 5, source_n + 5) / (
            instance.phase_base ** (3 * instance.block_count)
        )
        return (
            source_w == instance.source_w
            and source_n == instance.source_n
            and word == instance.valuation_word
            and tuple(intermediate_depths) == instance.intermediate_tail_depths
            and intermediate_depths
            == [2] * (instance.block_count - 1) + [instance.target_R]
            and target_n == instance.target_n
            and target_unit == instance.target_unit
            and v2(target_n + 1) == instance.target_R
            and target_unit % (1 << instance.target_mod2_power)
            == instance.target_u_mod2
            and instance.target.R == instance.target_R
            and instance.target.u_mod2 == instance.target_u_mod2
            and instance.target.mod2_power == instance.target_mod2_power
            and instance.target.mod3_power == expected_mod3_power
            and instance.target.u_mod3 == expected_mod3
            and target_unit % (3**expected_mod3_power) == expected_mod3
            and phase_ratio == instance.phase_ratio
            and phase_ratio
            == higher_r_phase_factor(
                instance.block_count,
                instance.phase_base,
            )
        )
    except (AssertionError, ValueError):
        return False


def higher_r_first_post_stage(
    source_R: int,
    source_unit: int,
) -> HigherRFirstPostStage:
    """Evaluate the first post-tail step and its exact descent cutoff."""

    if source_R < 3:
        raise ValueError("source_R must be at least three")
    if source_unit <= 0 or source_unit % 2 == 0:
        raise ValueError("source_unit must be a positive odd integer")
    source_n = (1 << source_R) * source_unit - 1
    post_q = v2(pow(3, source_R) * source_unit - 1)
    word = (1,) * (source_R - 1) + (post_q + 1,)
    landing = apply_word(source_n, word)
    formula_landing = (pow(3, source_R) * source_unit - 1) >> post_q
    if landing != formula_landing:
        raise AssertionError("first higher-tail post formula failed")
    landing_tail_depth = v2(landing + 1)
    if landing < source_n:
        classification = "descent_below_higher_R_source"
    elif landing_tail_depth >= 2:
        classification = "tail_reentry"
    else:
        classification = "continuing_post_exit_branch"
    return HigherRFirstPostStage(
        source_R=source_R,
        source_unit=source_unit,
        source_n=source_n,
        post_q=post_q,
        valuation_word=word,
        landing=landing,
        landing_tail_depth=landing_tail_depth,
        classification=classification,
    )


def affine_ghost_certificate(
    valuation_word: tuple[int, ...],
    source_n: int,
    base: Fraction,
) -> AffineGhostCertificate:
    """Construct one exact expanding-word affine-cusp certificate."""

    if not valuation_word:
        raise ValueError("valuation_word must be nonempty")
    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    if base <= 1:
        raise ValueError("base must be greater than one")
    affine = affine_from_word(valuation_word)
    numerator = pow(3, affine.m)
    denominator = 1 << affine.A
    linear_D = numerator - denominator
    if linear_D <= 0:
        raise ValueError("affine ghost certificate requires an expanding word")

    target_n = apply_word(source_n, valuation_word)
    source_linear = linear_D * source_n + affine.B
    target_linear = linear_D * target_n + affine.B
    if target_linear * denominator != numerator * source_linear:
        raise AssertionError("affine-ghost conjugacy identity failed")
    source_linear_v2 = v2(source_linear)
    target_linear_v2 = v2(target_linear)
    if source_linear_v2 - target_linear_v2 != affine.A:
        raise AssertionError("affine-ghost valuation did not drop by A")

    factor = Fraction(numerator, denominator) / base**affine.A
    source_potential = Fraction(source_linear) * base**source_linear_v2
    target_potential = Fraction(target_linear) * base**target_linear_v2
    if target_potential / source_potential != factor:
        raise AssertionError("affine-ghost potential ratio failed")
    return AffineGhostCertificate(
        valuation_word=valuation_word,
        M=affine.m,
        A=affine.A,
        B=affine.B,
        slope=Fraction(numerator, denominator),
        linear_D=linear_D,
        ghost=Fraction(-affine.B, linear_D),
        source_n=source_n,
        target_n=target_n,
        source_linear_value=source_linear,
        target_linear_value=target_linear,
        source_linear_v2=source_linear_v2,
        target_linear_v2=target_linear_v2,
        base=base,
        potential_factor=factor,
        contracts=factor < 1,
    )


def affine_ghost_chart_transition(
    source_word: tuple[int, ...],
    target_word: tuple[int, ...],
) -> AffineGhostChartTransition:
    """Return the exact affine relation between two ghost coordinates."""

    if not source_word or not target_word:
        raise ValueError("source_word and target_word must be nonempty")
    source = affine_from_word(source_word)
    target = affine_from_word(target_word)
    source_numerator = 3**source.m
    source_denominator = 1 << source.A
    source_D = source_numerator - source_denominator
    target_D = 3**target.m - (1 << target.A)
    if source_D <= 0 or target_D <= 0:
        raise ValueError("both ghost charts must be expanding words")

    multiplier = Fraction(
        target_D * source_numerator,
        source_denominator * source_D,
    )
    ghost_gap = Fraction(
        target.B * source_D - target_D * source.B,
        source_D,
    )
    return AffineGhostChartTransition(
        source_word=source_word,
        target_word=target_word,
        source_D=source_D,
        source_B=source.B,
        target_D=target_D,
        target_B=target.B,
        linear_multiplier=multiplier,
        additive_ghost_gap=ghost_gap,
    )


def _verify_transfer_family(
    block_count_max: int,
    target_R_max: int,
    target_mod2_power: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> tuple[int, str]:
    if block_count_max < 1:
        raise ValueError("block_count_max must be positive")
    if target_R_max < 3:
        raise ValueError("target_R_max must be at least three")
    digest = hashlib.sha256()
    verified = 0
    expected_targets = tuple(range(1, 1 << target_mod2_power, 2))
    expected_target_set = set(expected_targets)
    for block_count in range(1, block_count_max + 1):
        for target_R in range(3, target_R_max + 1):
            targets: set[int] = set()
            for target_u_mod2 in expected_targets:
                instance = higher_r_transfer_instance(
                    block_count,
                    target_R,
                    target_u_mod2,
                    target_mod2_power=target_mod2_power,
                    source_u_mod3=source_u_mod3,
                    source_mod3_power=source_mod3_power,
                )
                if not verify_higher_r_transfer_instance(instance):
                    raise AssertionError("higher-tail family instance failed")
                targets.add(instance.target.u_mod2)

                lifted_u = instance.least_positive_u + instance.source_lift_modulus
                lifted_n = 4 * lifted_u - 1
                lifted_target = apply_word(
                    lifted_n,
                    instance.valuation_word,
                )
                lifted_unit = (lifted_target + 1) >> target_R
                if (
                    lifted_unit % (1 << target_mod2_power) != target_u_mod2
                    or lifted_unit % (3**instance.target.mod3_power)
                    != instance.target.u_mod3
                ):
                    raise AssertionError("higher-tail lift transport failed")
                digest.update(
                    (
                        f"{block_count}:{target_R}:{target_u_mod2}:"
                        f"{instance.source.u_mod2}:"
                        f"{instance.least_positive_u}:"
                        f"{instance.target.u_mod3}\n"
                    ).encode()
                )
                verified += 1
            if targets != expected_target_set:
                raise AssertionError("higher-tail depth missed target residues")
    return verified, digest.hexdigest()


def _verify_first_post_partition(
    target_R_max: int,
    unit_mod2_power: int,
) -> tuple[dict[str, int], str]:
    if target_R_max < 3:
        raise ValueError("target_R_max must be at least three")
    if unit_mod2_power < 1:
        raise ValueError("unit_mod2_power must be positive")
    counts = {
        "descent_below_higher_R_source": 0,
        "tail_reentry": 0,
        "continuing_post_exit_branch": 0,
    }
    digest = hashlib.sha256()
    for source_R in range(3, target_R_max + 1):
        for source_unit in range(1, 1 << unit_mod2_power, 2):
            stage = higher_r_first_post_stage(source_R, source_unit)
            coefficient = (1 << (source_R + stage.post_q)) - pow(3, source_R)
            descent_inequality = coefficient * source_unit > (1 << stage.post_q) - 1
            if descent_inequality != (
                stage.classification == "descent_below_higher_R_source"
            ):
                raise AssertionError("higher-tail descent cutoff failed")
            counts[stage.classification] += 1
            digest.update(
                (
                    f"{source_R}:{source_unit}:{stage.post_q}:"
                    f"{stage.landing}:{stage.landing_tail_depth}:"
                    f"{stage.classification}\n"
                ).encode()
            )
    return counts, digest.hexdigest()


def higher_r_affine_ghost_report(
    *,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
    verification_block_count_max: int = 4,
    verification_target_R_max: int = 10,
    verification_first_post_unit_power: int = 8,
    input_path: str | Path = DEFAULT_INPUT_PATH,
) -> HigherRAffineGhostReport:
    """Build the exact higher-tail transfer and affine-ghost report."""

    if target_mod2_power < 1:
        raise ValueError("target_mod2_power must be positive")
    if source_mod3_power < 0:
        raise ValueError("source_mod3_power must be nonnegative")
    source_modulus3 = 3**source_mod3_power
    if not 0 <= source_u_mod3 < source_modulus3:
        raise ValueError("source_u_mod3 must be a canonical residue")

    input_artifact = Path(input_path)
    input_hash = _sha256(input_artifact)
    input_validation = _validate_input_artifact(input_artifact)
    default_scope = (
        target_mod2_power == DEFAULT_TARGET_MOD2_POWER
        and source_u_mod3 == DEFAULT_SOURCE_U_MOD3
        and source_mod3_power == DEFAULT_SOURCE_MOD3_POWER
    )
    canonical_provenance = bool(
        default_scope
        and input_hash == DEFAULT_INPUT_SHA256
        and input_validation["fully_verified"]
    )

    family_count, family_hash = _verify_transfer_family(
        verification_block_count_max,
        verification_target_R_max,
        target_mod2_power,
        source_u_mod3,
        source_mod3_power,
    )
    post_counts, post_hash = _verify_first_post_partition(
        verification_target_R_max,
        verification_first_post_unit_power,
    )

    phase_fixture_1 = higher_r_transfer_instance(
        1,
        3,
        67 % (1 << target_mod2_power),
        target_mod2_power=target_mod2_power,
        source_u_mod3=source_u_mod3,
        source_mod3_power=source_mod3_power,
    )
    phase_fixture_2 = higher_r_transfer_instance(
        2,
        3,
        121 % (1 << target_mod2_power),
        target_mod2_power=target_mod2_power,
        source_u_mod3=source_u_mod3,
        source_mod3_power=source_mod3_power,
    )

    canonical_obstruction_phase = higher_r_transfer_instance(
        1,
        5,
        37,
        target_mod2_power=DEFAULT_TARGET_MOD2_POWER,
        source_u_mod3=DEFAULT_SOURCE_U_MOD3,
        source_mod3_power=DEFAULT_SOURCE_MOD3_POWER,
    )
    obstruction_source = canonical_obstruction_phase.target_n
    obstruction_word = (1, 1, 1, 1, 2)
    obstruction_target = apply_word(obstruction_source, obstruction_word)
    if (
        canonical_obstruction_phase.source_n != 1051
        or obstruction_source != 1183
        or obstruction_target != 4495
    ):
        raise AssertionError("canonical higher-tail obstruction changed")
    simple_source_depth = v2(obstruction_source + 5) - 2
    simple_target_depth = v2(obstruction_target + 5) - 2
    if simple_source_depth != 0 or simple_target_depth != 0:
        raise AssertionError("simple n+5 cusp obstruction lost its seam")

    ghost_1183 = affine_ghost_certificate(
        obstruction_word,
        obstruction_source,
        Fraction(5, 4),
    )
    if (
        ghost_1183.linear_D != 179
        or ghost_1183.B != 211
        or ghost_1183.potential_factor != Fraction(15552, 15625)
    ):
        raise AssertionError("canonical 179*n+211 ghost changed")

    canonical_r3_phase = higher_r_transfer_instance(
        1,
        3,
        4765 % (1 << DEFAULT_TARGET_MOD2_POWER),
        target_mod2_power=DEFAULT_TARGET_MOD2_POWER,
        source_u_mod3=DEFAULT_SOURCE_U_MOD3,
        source_mod3_power=DEFAULT_SOURCE_MOD3_POWER,
    )
    ghost_r3 = affine_ghost_certificate(
        (1, 1, 2),
        canonical_r3_phase.target_n,
        Fraction(8, 7),
    )
    if (
        canonical_r3_phase.source_n != 33883
        or canonical_r3_phase.target_n != 38119
        or ghost_r3.target_n != 64327
        or ghost_r3.linear_D != 11
        or ghost_r3.B != 19
        or ghost_r3.potential_factor != Fraction(64827, 65536)
    ):
        raise AssertionError("canonical 11*n+19 ghost changed")
    canonical_chart_switch = affine_ghost_chart_transition(
        obstruction_word,
        (1, 1, 2),
    )
    if canonical_chart_switch.linear_multiplier != Fraction(
        2673, 11456
    ) or canonical_chart_switch.additive_ghost_gap != Fraction(1080, 179):
        raise AssertionError("canonical affine-ghost chart relation changed")

    phase_lambda = nested_cusp_factor(DEFAULT_NESTED_CUSP_BASE)
    target_count = 1 << (target_mod2_power - 1)
    return HigherRAffineGhostReport(
        type="pecm_higher_r_affine_ghost_phase_transfer",
        status=(
            "exact_higher_r_phase_transfer_and_affine_ghost_hierarchy_open_cross_chart"
        ),
        provenance={
            "artifact": str(input_artifact),
            "artifact_sha256": input_hash,
            "expected_artifact_sha256": DEFAULT_INPUT_SHA256,
            "artifact_snapshot_match": input_hash == DEFAULT_INPUT_SHA256,
            "artifact_content_validation": input_validation,
            "canonical_prior_frontier_verified": canonical_provenance,
            "scope_relation": (
                "canonical_prior_frontier_verified"
                if canonical_provenance
                else (
                    "requested_scope_differs_from_canonical"
                    if not default_scope
                    else (
                        "canonical_artifact_snapshot_mismatch"
                        if input_validation["fully_verified"]
                        else "canonical_artifact_not_verified"
                    )
                )
            ),
            "requested_source_scope": {
                "R": 2,
                "all_odd_u_mod2_power": target_mod2_power,
                "u_mod3": source_u_mod3,
                "mod3_power": source_mod3_power,
            },
        },
        higher_r_transfer={
            "parameter": "integer block_count m >= 1",
            "source_coordinate": ("v2(u+1)=3*m; u+1=2^(3*m)*w with w odd"),
            "source_n": "n0 = 2^(3*m+2)*w - 5",
            "floor_loops": "m-1",
            "full_word": "(1,2)^m",
            "target_n": "n1 = 4*9^m*w - 5",
            "shift_identity": ("n1+5 = (9/8)^m * (n0+5)"),
            "next_depth": "R = 2 + v2(9^m*w - 1) >= 3",
            "target_unit": ("v = (9^m*w - 1) / 2^(R-2)"),
            "inverse_positive_integer_condition": (
                "2^(R-2)*v is congruent to -1 mod 9^m"
            ),
            "inverse_source": ("w = (2^(R-2)*v + 1)/9^m; u = 2^(3*m)*w - 1"),
            "fixtures": [
                phase_fixture_1.to_json_dict(),
                phase_fixture_2.to_json_dict(),
            ],
        },
        mixed_residue_transport={
            "target_mod2_power": target_mod2_power,
            "target_fixed_leaves_per_m_R": target_count,
            "source_precision": "3*m + R + k - 2",
            "source_w_residue": ("w == (1 + 2^(R-2)*b) * 9^(-m) mod 2^(R+k-2)"),
            "source_u_residue": ("u == 2^(3*m)*w - 1 mod 2^(3*m+R+k-2)"),
            "target_2adic_map": (
                f"bijection onto all {target_count} odd residues mod "
                f"2^{target_mod2_power} for every (m,R)"
            ),
            "available_target_mod3_power": ("source ell + 2*m"),
            "target_mod3_formula": (
                "v == 2^(-(R-2)) * (9^m*2^(-3*m)*(source_u+1) - 1) mod 3^(ell+2*m)"
            ),
            "lift_difference": (
                "Delta w=2^(R+k-2)*3^ell*t implies Delta v=2^k*3^(ell+2*m)*t"
            ),
        },
        phase_energy={
            "R2_phase_energy": ("E2(n) = (n+5)*c^(v2(n+5)-2)"),
            "higher_R_base_energy": "EH(n) = n+5",
            "base": _fraction_json(DEFAULT_NESTED_CUSP_BASE),
            "single_block_factor": _fraction_json(phase_lambda),
            "full_transfer_ratio": ("EH(n1)/E2(n0) = (11979/12167)^m"),
            "uniform_upper": _fraction_json(phase_lambda),
            "contracts_entire_higher_R_handoff": True,
            "scope": ("the maximal (1,2)^m phase including its final R>=3 exit"),
            "global_lyapunov": False,
        },
        first_higher_r_stage={
            "source": "N = 2^R*v - 1, R>=3, v odd",
            "forced_tail": "R-1 valuation-one steps",
            "post_q": "q = v2(3^R*v - 1) >= 1",
            "full_word": "(1^(R-1), q+1)",
            "landing": "Z = (3^R*v - 1)/2^q",
            "affine_identity": ("Z = (3^R*N + (3^R-2^R))/2^(R+q)"),
            "exact_descent_test": ("(2^(R+q)-3^R)*v > 2^q-1"),
            "uniform_descent_condition": ("2^q*(2^R-1) > 3^R-1"),
            "always_expanding_condition": "2^(R+q) <= 3^R",
            "nonuniform_case": (
                "when the affine slope contracts but the cutoff is positive, "
                "only a finite interval of source lifts remains live"
            ),
            "reentry_depth_if_not_descended": ("rho = v2(3^R*v + 2^q - 1)-q"),
            "reentry_rule": ("rho>=2 gives a tail reentry; rho=1 continues post-exit"),
            "reentry_target_unit": ("y = (3^R*v + 2^q - 1)/2^(q+rho)"),
            "reentry_target_fixed_source": (
                "v == 3^(-R)*(2^(q+rho)*b-(2^q-1)) mod 2^(q+rho+k)"
            ),
            "reentry_target_mod3_gain": "source target-unit precision + R",
            "target_fixed_helpers": [
                "higher_r_reentry_source_residue",
                "higher_r_reentry_target_mod3",
            ],
            "comparison_baseline": "the higher-R source N",
        },
        simple_cusp_obstruction={
            "candidate": ("K_c(n) = (n+5)*c^(v2(n+5)-2)"),
            "status": "exactly_refuted_after_higher_R_arrival",
            "canonical_source_chain": {
                "fixture_scope": {
                    "target_mod2_power": DEFAULT_TARGET_MOD2_POWER,
                    "source_u_mod3": DEFAULT_SOURCE_U_MOD3,
                    "source_mod3_power": DEFAULT_SOURCE_MOD3_POWER,
                },
                "R2_source_u": str(canonical_obstruction_phase.least_positive_u),
                "R2_source_n": str(canonical_obstruction_phase.source_n),
                "phase_target_n": str(obstruction_source),
                "phase_target_R": canonical_obstruction_phase.target_R,
                "phase_target_unit": str(canonical_obstruction_phase.target_unit),
                "next_word": list(obstruction_word),
                "next_target_n": str(obstruction_target),
            },
            "endpoint_cusp_exponents": {
                "source": simple_source_depth,
                "target": simple_target_depth,
            },
            "canonical_witness_ratio_for_every_c": _fraction_json(
                Fraction(obstruction_target + 5, obstruction_source + 5)
            ),
            "candidate_ratio_value": "125/33 > 1",
            "infinite_obstruction_cylinder": {
                "source_tail_state": ("N = 2^5*v-1, v == 37 mod 2^8, v == 37 mod 3^4"),
                "next_word": "(1,1,1,1,2)",
                "next_target": "T(N) = (243*v-1)/2",
                "endpoint_cusp_exponents": "both zero",
                "ratio": "(243*v+9)/(64*v+8) > 1 for v>0",
                "ratio_constant_over_cylinder": False,
            },
            "infinite_cylinder_not_isolated_integer": True,
            "interpretation": (
                "The -5 cusp pays for entrance to the higher-R phase, but "
                "does not pay for its next expanding affine word."
            ),
        },
        affine_ghost_theorem={
            "domain": (
                "any exact expanding accelerated word T(n)=(3^M*n+B)/2^A with 3^M>2^A"
            ),
            "linear_form": "L_W(n)=(3^M-2^A)*n+B",
            "negative_rational_ghost": "-B/(3^M-2^A)",
            "conjugacy_identity": ("L_W(T(n))=(3^M/2^A)*L_W(n)"),
            "valuation_update": "v2(L_W(T(n)))=v2(L_W(n))-A",
            "candidate": "K_W,c(n)=L_W(n)*c^v2(L_W(n))",
            "exact_factor": "(3^M/2^A)*c^(-A)",
            "contraction_condition": "c^A > 3^M/2^A",
            "finite_repeat_budget": (
                "if W repeats r consecutive times, then "
                "r*A <= v2(L_W(n)); one expanding word cannot repeat "
                "forever on a positive orbit"
            ),
            "word_specific": True,
            "cross_word_compatibility_verified": False,
            "chart_switch_identity": ("T_W(n)-g_V = (3^M_W/2^A_W)*(n-g_W) + (g_W-g_V)"),
            "chart_switch_linear_form_identity": (
                "L_V(T_W(n)) = [D_V*3^M_W/(2^A_W*D_W)]*L_W(n) + B_V-D_V*B_W/D_W"
            ),
            "chart_switch_obstruction": (
                "the additive ghost-gap term prevents the wordwise "
                "multiplicative factors from telescoping automatically"
            ),
            "algebraic_chart_switch_fixture_not_itinerary_claim": (
                canonical_chart_switch.to_json_dict()
            ),
            "canonical_certificates": [
                ghost_1183.to_json_dict(),
                ghost_r3.to_json_dict(),
            ],
            "interpretation": (
                "Persistent expanding words are organized by distances to "
                "their own negative rational affine fixed points. The next "
                "global problem is a compatible grammar between these charts."
            ),
        },
        finite_verification={
            "role": "regression_only_not_basis_of_symbolic_derivation",
            "block_count_min": 1,
            "block_count_max": verification_block_count_max,
            "target_R_min": 3,
            "target_R_max": verification_target_R_max,
            "target_mod2_power": target_mod2_power,
            "transfer_instances_verified": family_count,
            "transfer_instance_sha256": family_hash,
            "nonleast_lift_per_instance_verified": 1,
            "first_post_unit_mod2_power": (verification_first_post_unit_power),
            "first_post_stage_counts": post_counts,
            "first_post_stage_sha256": post_hash,
        },
        frontier={
            "status": "countable_two_parameter_open_higher_R_family",
            "source_family_parametrized": True,
            "target_fixed_residue_transport_exact": True,
            "target_depths": "every integer R>=3",
            "target_2adic_fibers": "all odd target residues at every (m,R)",
            "first_post_stage_exact": True,
            "full_post_exit_stopping_grammar_closed": False,
            "affine_ghost_chart_count_finite": False,
        },
        max_plus={
            "status": "not_applicable_open_cross_chart_grammar",
            "finite_karp_run": False,
            "cycles": [],
        },
        proof={
            "claim_kind": ("exact_symbolic_derivation_with_bounded_regression_checks"),
            "canonical_input_frontier_link_verified": canonical_provenance,
            "symbolic_higher_R_transfer_derived": True,
            "symbolic_mixed_residue_transport_derived": True,
            "symbolic_full_phase_energy_contraction_derived": True,
            "symbolic_first_higher_R_stage_derived": True,
            "symbolic_simple_cusp_obstruction_derived": True,
            "symbolic_affine_ghost_theorem_derived": True,
            "symbolic_finite_repeat_budget_derived": True,
            "symbolic_chart_switch_identity_derived": True,
            "bounded_machine_regression_passed": True,
            "programmatically_exhausted_all_positive_integers": False,
            "global_cross_chart_lyapunov_derived": False,
            "global_collatz_proof": False,
            "next_gap": (
                "Construct compatible inequalities when an orbit changes "
                "from one affine-ghost chart to another, retaining exact "
                "magnitude intervals on contracting-slope branches."
            ),
        },
    )


def main(argv: list[str] | None = None) -> None:
    """Write the exact higher-tail and affine-ghost artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-mod2-power", type=int, default=8)
    parser.add_argument("--source-u-mod3", type=int, default=2)
    parser.add_argument("--source-mod3-power", type=int, default=2)
    parser.add_argument(
        "--verification-block-count-max",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--verification-target-R-max",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--verification-first-post-unit-power",
        type=int,
        default=8,
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = higher_r_affine_ghost_report(
        target_mod2_power=args.target_mod2_power,
        source_u_mod3=args.source_u_mod3,
        source_mod3_power=args.source_mod3_power,
        verification_block_count_max=args.verification_block_count_max,
        verification_target_R_max=args.verification_target_R_max,
        verification_first_post_unit_power=(args.verification_first_post_unit_power),
        input_path=args.input,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.to_json() + "\n", encoding="utf-8")
    LOGGER.info(
        "wrote %s (status=%s; transfer_instances=%d)",
        args.output,
        report.status,
        report.finite_verification["transfer_instances_verified"],
    )


if __name__ == "__main__":
    main()
