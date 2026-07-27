"""Exact symbolic expansion of the ``R=2`` PECM target frontier.

The selected-cylinder pilot lands on all states

``(R, u mod 2^8, u mod 3^2) = (2, odd, 2)``.

Their outgoing cover is not a finite graph.  It has an exact mod-8
trichotomy and a countable reentry family indexed by the next tail depth.
This module records that family symbolically, derives a finite-state
pointwise-Lyapunov obstruction, and verifies the nested cusp coordinate and
maximal-loop exit grammar of the expanding ``R=2 -> 2`` subfamily.
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

from .core import v2
from .symbolic_branch_certificate import (
    ExactMixedCylinder,
    least_positive_mixed_representative,
    trace_post_exit_macro,
)


LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path(
    "docs/reports/pecm_exact_selected_cylinder_pilot.json"
)
DEFAULT_INPUT_SHA256 = (
    "8e70f4224cc379361de62675cb2b25028d95892c80523c51aadd2d52dd4948a1"
)
DEFAULT_OUTPUT_PATH = Path(
    "docs/reports/pecm_r2_recursive_tail_cusp.json"
)
DEFAULT_TARGET_MOD2_POWER = 8
DEFAULT_SOURCE_MOD3_POWER = 2
DEFAULT_SOURCE_U_MOD3 = 2
DEFAULT_NESTED_CUSP_BASE = Fraction(23, 22)


@dataclass(frozen=True)
class R2ReentryInstance:
    """One target-fixed member of the countable live ``R=2`` family."""

    target_R: int
    target_u_mod2: int
    target_mod2_power: int
    source: ExactMixedCylinder
    least_positive_u: int
    source_lift_modulus: int
    n0: int
    landing: int
    target_unit: int
    target: ExactMixedCylinder
    least_lift_size_ratio_upper: Fraction

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "target_R": self.target_R,
            "target_u_mod2": self.target_u_mod2,
            "target_mod2_power": self.target_mod2_power,
            "source": self.source.to_json_dict(),
            "least_positive_u": str(self.least_positive_u),
            "source_lift_modulus": str(self.source_lift_modulus),
            "n0": str(self.n0),
            "landing": str(self.landing),
            "target_unit": str(self.target_unit),
            "target": self.target.to_json_dict(),
            "least_lift_size_ratio_upper": _fraction_json(
                self.least_lift_size_ratio_upper
            ),
            "ratio_upper_reason": (
                "F(n)/n = 9/8 + 5/(8*n) is strictly decreasing for n>0"
            ),
        }


@dataclass(frozen=True)
class R2FloorLoopExit:
    """Maximal compression of consecutive ``R=2 -> 2`` floor loops."""

    initial_u: int
    initial_S: int
    loops: int
    exit_u: int
    exit_S: int
    exit_source_class: str
    next_status: str
    next_post_word: tuple[int, ...]
    next_landing: int
    next_target_R: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "initial_u": str(self.initial_u),
            "initial_S": self.initial_S,
            "loops": self.loops,
            "exit_u": str(self.exit_u),
            "exit_S": self.exit_S,
            "exit_source_class": self.exit_source_class,
            "next_status": self.next_status,
            "next_post_word": list(self.next_post_word),
            "next_landing": str(self.next_landing),
            "next_target_R": self.next_target_R,
        }


@dataclass(frozen=True)
class R2ExactFrontierReport:
    """Machine-readable exact symbolic frontier result."""

    type: str
    status: str
    input_frontier: dict[str, Any]
    source_partition: dict[str, Any]
    reentry_family: dict[str, Any]
    outer_tail_candidate_audit: dict[str, Any]
    finite_state_obstruction: dict[str, Any]
    nested_cusp: dict[str, Any]
    induced_exit_grammar: dict[str, Any]
    finite_verification: dict[str, Any]
    frontier: dict[str, Any]
    max_plus: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "input_frontier": dict(self.input_frontier),
            "source_partition": dict(self.source_partition),
            "reentry_family": dict(self.reentry_family),
            "outer_tail_candidate_audit": dict(
                self.outer_tail_candidate_audit
            ),
            "finite_state_obstruction": dict(self.finite_state_obstruction),
            "nested_cusp": dict(self.nested_cusp),
            "induced_exit_grammar": dict(self.induced_exit_grammar),
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


def _validate_input_frontier(
    path: Path,
    *,
    target_mod2_power: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> dict[str, Any]:
    """Validate that an input artifact really contains the requested fiber."""

    expected_count = 1 << (target_mod2_power - 1)
    expected_targets = {
        (
            2,
            target_u_mod2,
            target_mod2_power,
            source_u_mod3,
            source_mod3_power,
        )
        for target_u_mod2 in range(1, 1 << target_mod2_power, 2)
    }
    result: dict[str, Any] = {
        "exists": path.exists(),
        "json_parsed": False,
        "artifact_type_matches": False,
        "edge_records_valid": False,
        "target_fiber_matches_requested_scope": False,
        "root_partition_claim_matches": False,
        "frontier_metadata_matches": False,
        "prior_exact_partition_claim_present": False,
        "expected_target_count": expected_count,
        "actual_edge_count": None,
        "actual_distinct_target_count": None,
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
    result["artifact_type_matches"] = (
        payload.get("type") == "pecm_exact_selected_cylinder_pilot"
    )
    edges = payload.get("edges")
    if not isinstance(edges, list):
        result["errors"].append("input artifact edges are not a list")
        return result
    result["actual_edge_count"] = len(edges)

    targets: set[tuple[int, int, int, int, int]] = set()
    edge_records_valid = True
    for edge in edges:
        if not isinstance(edge, dict):
            edge_records_valid = False
            continue
        target = edge.get("target")
        if (
            not isinstance(target, dict)
            or edge.get("integer_realizable") is not True
            or edge.get("classification")
            != "exact_expanding_tail_reentry_branch"
        ):
            edge_records_valid = False
            continue
        values = (
            target.get("R"),
            target.get("u_mod2"),
            target.get("mod2_power"),
            target.get("u_mod3"),
            target.get("mod3_power"),
        )
        if not all(isinstance(value, int) for value in values):
            edge_records_valid = False
            continue
        targets.add(values)
    result["edge_records_valid"] = edge_records_valid
    result["actual_distinct_target_count"] = len(targets)
    result["target_fiber_matches_requested_scope"] = (
        len(edges) == expected_count
        and len(targets) == expected_count
        and targets == expected_targets
    )

    root = payload.get("root")
    partition = root.get("partition") if isinstance(root, dict) else None
    result["root_partition_claim_matches"] = bool(
        isinstance(partition, dict)
        and partition.get("actual_child_count") == expected_count
        and partition.get("unique_child_count") == expected_count
        and partition.get("distinct_target_count") == expected_count
        and partition.get("full_odd_2adic_target_fiber_covered") is True
        and partition.get("partition_verified") is True
    )

    frontier = payload.get("frontier")
    result["frontier_metadata_matches"] = bool(
        isinstance(frontier, dict)
        and frontier.get("fixed_target_source_leaves") == expected_count
        and frontier.get("open_target_nodes") == expected_count
        and frontier.get("unresolved_source_leaves") == 0
    )
    proof = payload.get("proof")
    result["prior_exact_partition_claim_present"] = bool(
        isinstance(proof, dict)
        and proof.get("exact_branch_replay_verified") is True
        and proof.get("exact_transition_partition_verified") is True
    )

    required_flags = (
        "artifact_type_matches",
        "edge_records_valid",
        "target_fiber_matches_requested_scope",
        "root_partition_claim_matches",
        "frontier_metadata_matches",
        "prior_exact_partition_claim_present",
    )
    result["fully_verified"] = all(result[key] is True for key in required_flags)
    if not result["fully_verified"]:
        result["errors"].append(
            "artifact content does not certify the requested target fiber"
        )
    return result


def r2_source_class(u: int) -> str:
    """Return the exact mod-8 branch class for one positive odd unit."""

    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be a positive odd integer")
    residue = u % 8
    if residue == 1:
        return "first_post_descent_u_mod8_1"
    if residue == 5:
        return "first_post_descent_u_mod8_5"
    if residue == 3:
        return "second_post_descent_u_mod8_3"
    if residue == 7:
        return "first_post_reentry_u_mod8_7"
    raise AssertionError("odd residues modulo eight were not exhausted")


def r2_reentry_source_residue(
    target_R: int,
    target_u_mod2: int,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
) -> tuple[int, int]:
    """Return the source residue fixing one parametric reentry target.

    For target unit ``b mod 2^k`` and tail depth ``r``, the exact source is

    ``u = (2^(r+1) b - 1) / 9 mod 2^(r+k+1)``.
    """

    if target_R < 2:
        raise ValueError("target_R must be at least two")
    if target_mod2_power < 1:
        raise ValueError("target_mod2_power must be positive")
    modulus_target = 1 << target_mod2_power
    if (
        not 0 <= target_u_mod2 < modulus_target
        or target_u_mod2 % 2 == 0
    ):
        raise ValueError("target_u_mod2 must be an odd canonical residue")
    source_power = target_R + target_mod2_power + 1
    modulus_source = 1 << source_power
    inverse9 = pow(9, -1, modulus_source)
    source_residue = (
        ((target_u_mod2 << (target_R + 1)) - 1) * inverse9
    ) % modulus_source
    return source_residue, source_power


def r2_reentry_event_residue(target_R: int) -> tuple[int, int]:
    """Return the exact source cylinder for reentry at depth ``target_R``."""

    if target_R < 2:
        raise ValueError("target_R must be at least two")
    power = target_R + 2
    modulus = 1 << power
    residue = (
        ((1 << (target_R + 1)) - 1) * pow(9, -1, modulus)
    ) % modulus
    return residue, power


def r2_reentry_target_mod3(
    target_R: int,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
) -> tuple[int, int]:
    """Return all target 3-adic digits forced by the source cylinder.

    Multiplication by ``9`` gains two 3-adic digits, so a source known modulo
    ``3^ell`` fixes the target unit modulo ``3^(ell+2)``.
    """

    if target_R < 2:
        raise ValueError("target_R must be at least two")
    if source_mod3_power < 0:
        raise ValueError("source_mod3_power must be nonnegative")
    source_modulus = 3**source_mod3_power
    if not 0 <= source_u_mod3 < source_modulus:
        raise ValueError("source_u_mod3 must be a canonical residue")
    target_power = source_mod3_power + 2
    target_modulus = 3**target_power
    numerator = (9 * source_u_mod3 + 1) % target_modulus
    denominator_inverse = pow(
        pow(2, target_R + 1, target_modulus),
        -1,
        target_modulus,
    )
    return (numerator * denominator_inverse) % target_modulus, target_power


def r2_reentry_instance(
    target_R: int,
    target_u_mod2: int,
    *,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
) -> R2ReentryInstance:
    """Construct and replay one exact target-fixed reentry cylinder."""

    source_residue, source_power = r2_reentry_source_residue(
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
    least_u, lift_modulus = least_positive_mixed_representative(source)
    trace = trace_post_exit_macro(2, least_u, max_post_steps=3)
    if (
        trace.status != "tail_reentry"
        or trace.post_word != (2,)
        or trace.landing_tail_depth != target_R
    ):
        raise AssertionError("parametric R=2 reentry formula failed replay")
    target_unit = (trace.landing + 1) >> target_R
    target_mod3, target_mod3_power = r2_reentry_target_mod3(
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
    if target.u_mod2 != target_u_mod2:
        raise AssertionError("target 2-adic residue formula failed")
    if target.u_mod3 != target_mod3:
        raise AssertionError("target 3-adic transport formula failed")
    return R2ReentryInstance(
        target_R=target_R,
        target_u_mod2=target_u_mod2,
        target_mod2_power=target_mod2_power,
        source=source,
        least_positive_u=least_u,
        source_lift_modulus=lift_modulus,
        n0=trace.n0,
        landing=trace.landing,
        target_unit=target_unit,
        target=target,
        least_lift_size_ratio_upper=Fraction(trace.landing, trace.n0),
    )


def verify_r2_reentry_instance(instance: R2ReentryInstance) -> bool:
    """Verify one stored member of the parametric family from scratch."""

    try:
        expected_residue, expected_power = r2_reentry_source_residue(
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
        least_u, lift_modulus = least_positive_mixed_representative(
            instance.source
        )
        if (
            least_u != instance.least_positive_u
            or lift_modulus != instance.source_lift_modulus
        ):
            return False
        trace = trace_post_exit_macro(2, least_u, max_post_steps=3)
        if (
            trace.status != "tail_reentry"
            or trace.post_word != (2,)
            or trace.landing_tail_depth != instance.target_R
            or trace.n0 != instance.n0
            or trace.landing != instance.landing
        ):
            return False
        target_unit = (trace.landing + 1) >> instance.target_R
        expected_mod3, expected_mod3_power = r2_reentry_target_mod3(
            instance.target_R,
            instance.source.u_mod3,
            instance.source.mod3_power,
        )
        return (
            target_unit == instance.target_unit
            and target_unit % (1 << instance.target_mod2_power)
            == instance.target_u_mod2
            and instance.target.R == instance.target_R
            and instance.target.mod2_power == instance.target_mod2_power
            and instance.target.u_mod2 == instance.target_u_mod2
            and instance.target.mod3_power == expected_mod3_power
            and instance.target.u_mod3 == expected_mod3
            and target_unit % (3**expected_mod3_power) == expected_mod3
            and instance.least_lift_size_ratio_upper
            == Fraction(instance.landing, instance.n0)
            and instance.least_lift_size_ratio_upper > 1
        )
    except (AssertionError, ValueError):
        return False


def finite_state_self_loop_witness(
    mod2_power: int = 4,
    mod3_power: int = 2,
) -> dict[str, Any]:
    """Construct a positive expanding leaf returning to one finite state."""

    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    refined_power = mod2_power + 3
    source = ExactMixedCylinder(
        R=2,
        u_mod2=(1 << refined_power) - 1,
        mod2_power=refined_power,
        u_mod3=(3**mod3_power) - 1 if mod3_power else 0,
        mod3_power=mod3_power,
    )
    u, lift_modulus = least_positive_mixed_representative(source)
    trace = trace_post_exit_macro(2, u, max_post_steps=2)
    if (
        trace.status != "tail_reentry"
        or trace.post_word != (2,)
        or trace.landing_tail_depth != 2
    ):
        raise AssertionError("finite-state self-loop construction failed")
    target_unit = (trace.landing + 1) >> 2
    modulus2 = 1 << mod2_power
    modulus3 = 3**mod3_power
    source_coarse = {
        "R": 2,
        "u_mod2": u % modulus2,
        "mod2_power": mod2_power,
        "u_mod3": u % modulus3 if modulus3 > 1 else 0,
        "mod3_power": mod3_power,
    }
    target_coarse = {
        "R": 2,
        "u_mod2": target_unit % modulus2,
        "mod2_power": mod2_power,
        "u_mod3": target_unit % modulus3 if modulus3 > 1 else 0,
        "mod3_power": mod3_power,
    }
    if source_coarse != target_coarse or trace.landing <= trace.n0:
        raise AssertionError("constructed branch is not an expanding coarse self-loop")
    return {
        "coarse_resolution": {
            "mod2_power": mod2_power,
            "mod3_power": mod3_power,
        },
        "refined_source": source.to_json_dict(),
        "least_positive_u": str(u),
        "source_lift_modulus": str(lift_modulus),
        "n0": str(trace.n0),
        "landing": str(trace.landing),
        "post_word": list(trace.post_word),
        "target_unit": str(target_unit),
        "source_coarse_state": source_coarse,
        "target_coarse_state": target_coarse,
        "size_ratio": _fraction_json(Fraction(trace.landing, trace.n0)),
        "size_expands": trace.landing > trace.n0,
        "same_coarse_state": True,
    }


def r2_floor_loop_target_unit(u: int) -> int:
    """Apply the exact ``R=2 -> 2`` reduced unit map."""

    if u <= 0 or u % 16 != 15:
        raise ValueError("an R=2 floor loop requires u == 15 mod 16")
    return (9 * u + 1) // 8


def r2_floor_loop_run_length(u: int) -> int:
    """Return the exact number of consecutive ``R=2 -> 2`` loops."""

    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be a positive odd integer")
    return max(0, (v2(u + 1) - 1) // 3)


def r2_induced_floor_loop_exit(u: int) -> R2FloorLoopExit:
    """Compress the maximal floor-loop run and classify its exact exit."""

    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be a positive odd integer")
    initial_S = v2(u + 1)
    loops = r2_floor_loop_run_length(u)
    denominator = 8**loops
    shifted_exit_numerator = 9**loops * (u + 1)
    if shifted_exit_numerator % denominator:
        raise AssertionError("maximal floor-loop affine identity is nonintegral")
    exit_u = shifted_exit_numerator // denominator - 1
    exit_S = v2(exit_u + 1)
    expected_exit_S = initial_S - 3 * loops
    if exit_S != expected_exit_S or exit_S not in {1, 2, 3}:
        raise AssertionError("maximal floor-loop residual is not canonical")

    exit_source_class = r2_source_class(exit_u)
    trace = trace_post_exit_macro(2, exit_u, max_post_steps=3)
    next_target_R: int | None
    if exit_S == 1:
        if (
            not exit_source_class.startswith("first_post_descent")
            or trace.status != "descended"
            or len(trace.post_word) != 1
        ):
            raise AssertionError("S_exit=1 did not give first-post descent")
        next_status = "descent_at_first_post_step"
        next_target_R = None
    elif exit_S == 2:
        if (
            exit_source_class != "second_post_descent_u_mod8_3"
            or trace.status != "descended"
            or len(trace.post_word) != 2
        ):
            raise AssertionError("S_exit=2 did not give second-post descent")
        next_status = "descent_at_second_post_step"
        next_target_R = None
    else:
        odd_part = (u + 1) >> initial_S
        predicted_target_R = 2 + v2(9 ** (loops + 1) * odd_part - 1)
        if (
            exit_source_class != "first_post_reentry_u_mod8_7"
            or trace.status != "tail_reentry"
            or trace.post_word != (2,)
            or trace.landing_tail_depth != predicted_target_R
            or predicted_target_R < 3
        ):
            raise AssertionError("S_exit=3 did not give higher-tail reentry")
        next_status = "higher_R_tail_reentry"
        next_target_R = predicted_target_R

    return R2FloorLoopExit(
        initial_u=u,
        initial_S=initial_S,
        loops=loops,
        exit_u=exit_u,
        exit_S=exit_S,
        exit_source_class=exit_source_class,
        next_status=next_status,
        next_post_word=trace.post_word,
        next_landing=trace.landing,
        next_target_R=next_target_R,
    )


def nested_cusp_factor(
    base: Fraction = DEFAULT_NESTED_CUSP_BASE,
) -> Fraction:
    """Return the exact loop ratio for ``(n+5) * base^v2(u+1)``."""

    if base <= 1:
        raise ValueError("base must be greater than one")
    return Fraction(9, 8) / base**3


def _nearest_consecutive_nested_base(
    max_numerator: int = 64,
) -> tuple[Fraction, Fraction]:
    if max_numerator < 2:
        raise ValueError("max_numerator must be at least two")
    chosen: tuple[Fraction, Fraction] | None = None
    for numerator in range(2, max_numerator + 1):
        base = Fraction(numerator, numerator - 1)
        factor = nested_cusp_factor(base)
        if factor < 1:
            chosen = base, factor
    if chosen is None:
        raise AssertionError("no consecutive rational nested-cusp base found")
    return chosen


def _verify_source_partition(
    verification_power: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> dict[str, int]:
    if verification_power < 3:
        raise ValueError("verification_power must be at least three")
    counts = {
        "first_post_descent_u_mod8_1": 0,
        "first_post_descent_u_mod8_5": 0,
        "second_post_descent_u_mod8_3": 0,
        "first_post_reentry_u_mod8_7": 0,
    }
    for residue in range(1, 1 << verification_power, 2):
        cylinder = ExactMixedCylinder(
            R=2,
            u_mod2=residue,
            mod2_power=verification_power,
            u_mod3=source_u_mod3,
            mod3_power=source_mod3_power,
        )
        u, _ = least_positive_mixed_representative(cylinder)
        branch_class = r2_source_class(u)
        trace = trace_post_exit_macro(2, u, max_post_steps=3)
        if branch_class.startswith("first_post_descent"):
            valid = trace.status == "descended" and len(trace.post_word) == 1
        elif branch_class == "second_post_descent_u_mod8_3":
            valid = trace.status == "descended" and len(trace.post_word) == 2
        else:
            valid = (
                trace.status == "tail_reentry"
                and trace.post_word == (2,)
                and trace.landing_tail_depth >= 2
            )
        if not valid:
            raise AssertionError(
                f"R=2 source partition replay failed for u={u}"
            )
        counts[branch_class] += 1
    return counts


def _verify_parametric_family(
    target_R_max: int,
    target_mod2_power: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> tuple[int, str]:
    if target_R_max < 2:
        raise ValueError("target_R_max must be at least two")
    digest = hashlib.sha256()
    verified = 0
    for target_R in range(2, target_R_max + 1):
        targets: set[int] = set()
        for target_u_mod2 in range(1, 1 << target_mod2_power, 2):
            instance = r2_reentry_instance(
                target_R,
                target_u_mod2,
                target_mod2_power=target_mod2_power,
                source_u_mod3=source_u_mod3,
                source_mod3_power=source_mod3_power,
            )
            if not verify_r2_reentry_instance(instance):
                raise AssertionError("parametric family instance did not verify")
            targets.add(instance.target.u_mod2)
            digest.update(
                (
                    f"{target_R}:{target_u_mod2}:"
                    f"{instance.source.u_mod2}:{instance.least_positive_u}:"
                    f"{instance.target.u_mod3}\n"
                ).encode()
            )
            verified += 1
        expected_targets = set(range(1, 1 << target_mod2_power, 2))
        if targets != expected_targets:
            raise AssertionError("one parametric depth missed target residues")
    return verified, digest.hexdigest()


def _verify_floor_loop_chains(
    max_loops: int,
    source_u_mod3: int,
    source_mod3_power: int,
) -> int:
    if max_loops < 1:
        raise ValueError("max_loops must be positive")
    verified = 0
    for loops in range(1, max_loops + 1):
        power = 3 * loops + 1
        source = ExactMixedCylinder(
            R=2,
            u_mod2=(1 << power) - 1,
            mod2_power=power,
            u_mod3=source_u_mod3,
            mod3_power=source_mod3_power,
        )
        u, _ = least_positive_mixed_representative(source)
        initial_u = u
        initial_S = v2(u + 1)
        if initial_S < power:
            raise AssertionError("CRT source lost required loop depth")
        for _ in range(loops):
            previous_S = v2(u + 1)
            target = r2_floor_loop_target_unit(u)
            if v2(target + 1) != previous_S - 3:
                raise AssertionError("nested cusp did not drop by three")
            u = target
        if u + 1 != 9**loops * (initial_u + 1) // (8**loops):
            raise AssertionError("iterated floor-loop affine identity failed")
        verified += 1
    return verified


def _verify_induced_exit_grammar(
    verification_power: int,
) -> tuple[dict[str, int], str]:
    if verification_power < 3:
        raise ValueError("verification_power must be at least three")
    counts = {
        "exit_S_1_first_post_descent": 0,
        "exit_S_2_second_post_descent": 0,
        "exit_S_3_higher_R_reentry": 0,
    }
    digest = hashlib.sha256()
    for u in range(1, 1 << verification_power, 2):
        exit_result = r2_induced_floor_loop_exit(u)
        key = {
            1: "exit_S_1_first_post_descent",
            2: "exit_S_2_second_post_descent",
            3: "exit_S_3_higher_R_reentry",
        }[exit_result.exit_S]
        counts[key] += 1
        digest.update(
            (
                f"{u}:{exit_result.initial_S}:{exit_result.loops}:"
                f"{exit_result.exit_u}:{exit_result.exit_S}:"
                f"{exit_result.next_status}:{exit_result.next_target_R}\n"
            ).encode()
        )
    return counts, digest.hexdigest()


def r2_exact_frontier_report(
    *,
    target_mod2_power: int = DEFAULT_TARGET_MOD2_POWER,
    source_u_mod3: int = DEFAULT_SOURCE_U_MOD3,
    source_mod3_power: int = DEFAULT_SOURCE_MOD3_POWER,
    verification_power: int = 12,
    verification_target_R_max: int = 20,
    verification_max_loops: int = 8,
    input_path: str | Path = DEFAULT_INPUT_PATH,
) -> R2ExactFrontierReport:
    """Build the exact symbolic frontier and nested-cusp report."""

    if target_mod2_power < 3:
        raise ValueError(
            "target_mod2_power must be at least three to expose the mod-8 "
            "partition"
        )
    if source_mod3_power < 0:
        raise ValueError("source_mod3_power must be nonnegative")
    source_modulus3 = 3**source_mod3_power
    if not 0 <= source_u_mod3 < source_modulus3:
        raise ValueError("source_u_mod3 must be a canonical residue")

    input_artifact = Path(input_path)
    input_hash = _sha256(input_artifact)
    input_validation = _validate_input_frontier(
        input_artifact,
        target_mod2_power=target_mod2_power,
        source_u_mod3=source_u_mod3,
        source_mod3_power=source_mod3_power,
    )
    default_scope_requested = (
        target_mod2_power == DEFAULT_TARGET_MOD2_POWER
        and source_u_mod3 == DEFAULT_SOURCE_U_MOD3
        and source_mod3_power == DEFAULT_SOURCE_MOD3_POWER
    )
    canonical_prior_frontier_verified = bool(
        default_scope_requested
        and input_hash == DEFAULT_INPUT_SHA256
        and input_validation["fully_verified"]
    )
    partition_counts = _verify_source_partition(
        verification_power,
        source_u_mod3,
        source_mod3_power,
    )
    expected_partition_count = 1 << (verification_power - 3)
    if set(partition_counts.values()) != {expected_partition_count}:
        raise AssertionError("finite R=2 replay did not split evenly mod eight")
    instances_verified, family_hash = _verify_parametric_family(
        verification_target_R_max,
        target_mod2_power,
        source_u_mod3,
        source_mod3_power,
    )
    chains_verified = _verify_floor_loop_chains(
        verification_max_loops,
        source_u_mod3,
        source_mod3_power,
    )
    induced_exit_counts, induced_exit_hash = _verify_induced_exit_grammar(
        verification_power
    )

    target_count = 1 << (target_mod2_power - 1)
    source_coarse_count = target_count
    mod8_coarse_count = source_coarse_count // 4
    event_cycle = [
        {
            "target_R_mod_6": target_R % 6,
            "representative_target_R": target_R,
            "retained_target_u_mod_9": r2_reentry_target_mod3(
                target_R,
                source_u_mod3,
                source_mod3_power,
            )[0]
            % 9,
        }
        for target_R in range(2, 8)
    ]
    event_spine_residue = (-pow(9, -1, 1 << target_mod2_power)) % (
        1 << target_mod2_power
    )

    outer_event_residue, outer_event_power = r2_reentry_event_residue(2)
    outer_event = ExactMixedCylinder(
        R=2,
        u_mod2=outer_event_residue,
        mod2_power=outer_event_power,
        u_mod3=source_u_mod3,
        mod3_power=source_mod3_power,
    )
    outer_event_u, _ = least_positive_mixed_representative(outer_event)
    outer_target_unit = (9 * outer_event_u + 1) // 8
    outer_witness = r2_reentry_instance(
        2,
        outer_target_unit % (1 << target_mod2_power),
        target_mod2_power=target_mod2_power,
        source_u_mod3=source_u_mod3,
        source_mod3_power=source_mod3_power,
    )
    if outer_witness.least_positive_u != outer_event_u:
        raise AssertionError("least same-R outer-cusp witness changed")

    finite_witness = finite_state_self_loop_witness(4, 2)
    nested_factor = nested_cusp_factor(DEFAULT_NESTED_CUSP_BASE)
    if nested_factor != Fraction(11979, 12167):
        raise AssertionError("nested-cusp factor regression")
    nearest_base, nearest_factor = _nearest_consecutive_nested_base()
    if nearest_base != Fraction(25, 24):
        raise AssertionError("nearest consecutive nested-cusp base changed")

    source_partition = {
        "scope": {
            "R": 2,
            "u_parity": "odd",
            "u_mod3": source_u_mod3,
            "mod3_power": source_mod3_power,
            "coarse_mod2_power": target_mod2_power,
            "coarse_states": source_coarse_count,
        },
        "complete_mod8_partition": [
            {
                "u_mod8": 1,
                "coarse_states": mod8_coarse_count,
                "status": "descended_at_first_post_step",
                "post_valuation_lower_bound": 4,
                "landing_upper": "(9*u - 1)/8",
                "exact_positive_gap_lower": "(23*u - 7)/8",
            },
            {
                "u_mod8": 5,
                "coarse_states": mod8_coarse_count,
                "status": "descended_at_first_post_step",
                "post_valuation": 3,
                "landing": "(9*u - 1)/4",
                "exact_positive_gap": "(7*u - 3)/4",
            },
            {
                "u_mod8": 3,
                "coarse_states": mod8_coarse_count,
                "status": "descended_at_second_post_step",
                "first_post_valuation": 2,
                "first_landing": "(9*u - 1)/2",
                "first_landing_minus_n": "(u + 1)/2",
                "first_landing_tail_depth": 1,
                "second_post_valuation_lower_bound": 2,
                "second_landing_upper": "(27*u - 1)/8",
                "exact_positive_gap_lower": "(5*u - 7)/8",
            },
            {
                "u_mod8": 7,
                "coarse_states": mod8_coarse_count,
                "status": "tail_reentry_parametric_family",
                "post_valuation": 2,
                "full_word": [1, 2],
                "landing": "(9*u - 1)/2",
                "landing_minus_n": "(u + 1)/2",
                "target_R": "v2(9*u + 1) - 1 >= 2",
            },
        ],
        "uniformly_descending_coarse_states": 3 * mod8_coarse_count,
        "live_family_coarse_states": mod8_coarse_count,
        "unresolved_positive_integer_sources": 0,
        "classification_kind": "exact_symbolic_not_sampled",
    }

    reentry_family = {
        "parameter": "integer target_R = r >= 2",
        "event_source_residue": (
            "u == (2^(r+1) - 1) * 9^(-1) mod 2^(r+2)"
        ),
        "landing": "F(4*u-1) = (9*u-1)/2",
        "target_unit": "v = (9*u+1)/2^(r+1)",
        "target_identity": "F(4*u-1) = 2^r*v - 1",
        "target_mod2_power": target_mod2_power,
        "target_fixed_source_power": f"r + {target_mod2_power + 1}",
        "target_fixed_source_residue": (
            "u == (2^(r+1)*b - 1) * 9^(-1) "
            f"mod 2^(r+{target_mod2_power + 1}), b odd mod "
            f"2^{target_mod2_power}"
        ),
        "target_fixed_leaves_per_r": target_count,
        "target_2adic_map": (
            f"bijection onto all {target_count} odd residues mod "
            f"2^{target_mod2_power}"
        ),
        "source_mod3": {
            "residue": source_u_mod3,
            "power": source_mod3_power,
        },
        "available_target_mod3_power": source_mod3_power + 2,
        "target_mod3_formula": (
            "(9*source_u_mod3 + 1) * 2^(-(r+1)) "
            f"mod 3^{source_mod3_power + 2}"
        ),
        "retained_mod9_cycle": event_cycle,
        "persistent_coarse_spine": {
            "valid_for_r_at_least": target_mod2_power - 1,
            "u_mod2": event_spine_residue,
            "mod2_power": target_mod2_power,
            "formula": "-9^(-1) mod 2^k",
        },
        "finite_refinement_terminates": False,
        "nontermination_reason": (
            "target precision r+k+1 is unbounded as r grows; the residual "
            "2-adic cylinder approaches u=-1/9"
        ),
    }

    outer_ratio = outer_witness.least_lift_size_ratio_upper
    return R2ExactFrontierReport(
        type="pecm_r2_exact_recursive_tail_cusp",
        status=(
            "outer_tail_candidate_exactly_refuted_"
            "nested_recursive_cusp_exact_open_frontier"
        ),
        input_frontier={
            "artifact": str(input_artifact),
            "artifact_sha256": input_hash,
            "expected_artifact_sha256": DEFAULT_INPUT_SHA256,
            "artifact_snapshot_match": input_hash == DEFAULT_INPUT_SHA256,
            "requested_source_scope": {
                "R": 2,
                "all_odd_u_mod2_power": target_mod2_power,
                "u_mod3": source_u_mod3,
                "mod3_power": source_mod3_power,
                "states": source_coarse_count,
            },
            "artifact_content_validation": input_validation,
            "scope_relation": (
                "canonical_prior_target_fiber_verified"
                if canonical_prior_frontier_verified
                else (
                    "artifact_matches_requested_noncanonical_scope"
                    if input_validation["fully_verified"]
                    else "artifact_does_not_verify_requested_scope"
                )
            ),
            "canonical_prior_frontier_verified": (
                canonical_prior_frontier_verified
            ),
        },
        source_partition=source_partition,
        reentry_family=reentry_family,
        outer_tail_candidate_audit={
            "candidate_class": "H(n,R) = n^alpha * c^R",
            "parameter_domain": "alpha > 0 and c > 0",
            "status": "exactly_refuted_on_same_R_reentry",
            "witness": outer_witness.to_json_dict(),
            "witness_source_u": str(outer_witness.least_positive_u),
            "witness_transition": (
                f"{outer_witness.n0} -> {outer_witness.landing}"
            ),
            "source_R": 2,
            "target_R": 2,
            "c_factor": "c^(2-2) = 1",
            "H_ratio": (
                f"({outer_witness.landing}/{outer_witness.n0})^alpha > 1"
            ),
            "witness_size_ratio": _fraction_json(outer_ratio),
            "uniform_cylinder_ratio_upper": _fraction_json(outer_ratio),
            "ratio_monotonicity": (
                "F(n)/n = 9/8 + 5/(8*n) is strictly decreasing for n>0; "
                "the least positive lift is the cylinder maximum"
            ),
            "prior_23_over_22_local_certificate_remains_valid": True,
            "global_23_over_22_outer_cusp_verified": False,
            "interpretation": (
                "Tail depth paid for the selected R=9 to R=2 expansion, "
                "but cannot pay for an expanding branch that preserves R."
            ),
        },
        finite_state_obstruction={
            "status": "exact_realizable_self_loop_at_every_finite_resolution",
            "scope_relation": {
                "role": (
                    "global candidate-class obstruction, not asserted to be "
                    "a direct edge of the requested source fiber"
                ),
                "default_frontier_relation": (
                    "the canonical u mod 9 = -1 fixture lies in the R=2, "
                    "u mod 9 = 8 next-generation fiber reached by the "
                    "current r=2 family"
                ),
                "canonical_fixture_resolution": {
                    "mod2_power": 4,
                    "mod3_power": 2,
                },
                "witness_depends_on_resolution": True,
                "profinite_limit": "u = -1, n = -5",
                "single_positive_orbit_or_cycle": False,
            },
            "general_construction": {
                "coarse_state": (
                    "(R,u mod2^k,u mod3^ell) = "
                    "(2,-1,-1)"
                ),
                "refined_source_leaf": (
                    "u == -1 mod 2^(k+3), u == -1 mod 3^ell"
                ),
                "target_unit": "T(u) = (9*u+1)/8",
                "same_state_identities": [
                    "T(u)+1 = 9*(u+1)/8 == 0 mod 2^k",
                    "T(u) == -1 mod 3^ell",
                ],
                "size_behavior": "4*T(u)-1 > 4*u-1",
            },
            "fixture": finite_witness,
            "excluded_candidate_class": (
                "strict one-step H(n,state)=n^alpha*h(finite mixed state), "
                "alpha >= 0, h positive"
            ),
            "reason": (
                "The state correction cancels on the exact coarse self-loop; "
                "size grows for alpha>0 and equality remains for alpha=0. "
                "This excludes finite mixed 2-adic/3-adic state corrections, "
                "not arbitrary history variables or residues at other primes."
            ),
            "negative_fixed_point": {
                "unit_map": "T(u) = (9*u+1)/8",
                "unit_fixed_point": "-1",
                "n_map": "F(n) = (9*n+5)/8",
                "n_fixed_point": "-5",
                "positive_cycle_claimed": False,
            },
        },
        nested_cusp={
            "status": "exact_contraction_on_every_R2_to_R2_floor_loop",
            "secondary_coordinate": "S = v2(u+1) = v2(n+5)-2",
            "loop_condition": "u == -1 mod 16, equivalently S >= 4",
            "unit_map": "T(u) = (9*u+1)/8",
            "unit_shift_identity": "T(u)+1 = 9*(u+1)/8",
            "coordinate_update": "S(T(u)) = S(u) - 3",
            "shifted_size_identity": "F(n)+5 = 9*(n+5)/8",
            "candidate": "K(n,u) = (n+5) * c^S",
            "exact_ratio": "(9/8) * c^(-3)",
            "base": _fraction_json(DEFAULT_NESTED_CUSP_BASE),
            "factor": _fraction_json(nested_factor),
            "margin_to_one": _fraction_json(Fraction(1, 1) - nested_factor),
            "contracts": nested_factor < 1,
            "nearest_consecutive_base_with_numerator_at_most_64": {
                "base": _fraction_json(nearest_base),
                "factor": _fraction_json(nearest_factor),
                "margin_to_one": _fraction_json(
                    Fraction(1, 1) - nearest_factor
                ),
            },
            "consecutive_loop_criterion": (
                "at least j loops iff S >= 3*j+1, equivalently "
                "u == -1 mod 2^(3*j+1)"
            ),
            "exact_run_length": "floor((S-1)/3)",
            "iterated_identities": [
                "T^j(u)+1 = (9/8)^j * (u+1)",
                "F^j(n)+5 = (9/8)^j * (n+5)",
                "K_j/K_0 = ((9/8)*c^(-3))^j",
            ],
            "interpretation": (
                "A finite mixed 2-adic/3-adic state correction cannot resolve "
                "the profinite self-loop. An unbounded cusp measuring "
                "distance to the negative fixed point n=-5 can resolve each "
                "consecutive same-R loop."
            ),
        },
        induced_exit_grammar={
            "status": "exact_maximal_floor_loop_exit_partition",
            "maximal_loop_count": "j = floor((S-1)/3)",
            "closed_form": (
                "u_j + 1 = 9^j*(u+1)/8^j; "
                "n_j + 5 = 9^j*(n+5)/8^j"
            ),
            "residual_coordinate": "S_exit = S-3*j in {1,2,3}",
            "branches": [
                {
                    "S_exit": 1,
                    "initial_S_congruence": "S == 1 mod 3",
                    "exit_u_mod8": [1, 5],
                    "outcome": "descent_at_first_post_step",
                    "conditional_odd_unit_2adic_Haar_mass": _fraction_json(
                        Fraction(4, 7)
                    ),
                },
                {
                    "S_exit": 2,
                    "initial_S_congruence": "S == 2 mod 3",
                    "exit_u_mod8": [3],
                    "outcome": "descent_at_second_post_step",
                    "conditional_odd_unit_2adic_Haar_mass": _fraction_json(
                        Fraction(2, 7)
                    ),
                },
                {
                    "S_exit": 3,
                    "initial_S_congruence": "S == 0 mod 3",
                    "exit_u_mod8": [7],
                    "outcome": "higher_R_tail_reentry",
                    "conditional_odd_unit_2adic_Haar_mass": _fraction_json(
                        Fraction(1, 7)
                    ),
                    "odd_part": "w = (u+1)/2^S",
                    "next_target_R": (
                        "2 + v2(9^(j+1)*w - 1) >= 3"
                    ),
                },
            ],
            "conditional_odd_unit_aggregate_2adic_Haar_mass": {
                "descent": _fraction_json(Fraction(6, 7)),
                "higher_R_reentry": _fraction_json(Fraction(1, 7)),
            },
            "Haar_mass_derivation": (
                "For normalized Haar measure on odd Z_2, "
                "P(v2(u+1)=s)=2^(-s). Summing over s mod 3 gives "
                "4/7, 2/7, and 1/7."
            ),
            "measure_caveat": (
                "These Haar proportions are an average renewal diagnostic, "
                "not a pointwise contraction statement. Descent is below "
                "the post-compression exit source, not necessarily below "
                "the original pre-loop value."
            ),
            "remaining_open_family": (
                "S_exit=3 higher-R targets and their subsequent induced "
                "returns"
            ),
        },
        finite_verification={
            "role": "regression_only_not_basis_of_symbolic_proof",
            "source_replay_power": verification_power,
            "source_representatives_replayed": 1 << (verification_power - 1),
            "source_class_counts": partition_counts,
            "parametric_target_R_min": 2,
            "parametric_target_R_max": verification_target_R_max,
            "parametric_instances_verified": instances_verified,
            "parametric_instance_sha256": family_hash,
            "floor_loop_chains_verified": chains_verified,
            "maximum_chain_length_verified": verification_max_loops,
            "induced_exit_representatives_replayed": (
                1 << (verification_power - 1)
            ),
            "induced_exit_counts": induced_exit_counts,
            "induced_exit_sha256": induced_exit_hash,
        },
        frontier={
            "status": "symbolic_countable_open_family",
            "source_cover_complete": True,
            "ordinary_integer_sources_unresolved": 0,
            "live_target_depths": "every integer r >= 2",
            "live_target_nodes_finite": False,
            "closed_transition_graph": False,
        },
        max_plus={
            "status": "not_applicable_countably_infinite_open_frontier",
            "finite_karp_run": False,
            "exact_finite_state_obstruction_recorded_instead": True,
            "cycles": [],
        },
        proof={
            "claim_kind": (
                "exact_symbolic_derivation_with_bounded_regression_checks"
            ),
            "canonical_input_frontier_link_verified": (
                canonical_prior_frontier_verified
            ),
            "symbolic_R2_source_partition_derived": True,
            "symbolic_countable_reentry_family_derived": True,
            "symbolic_outer_tail_candidate_refutation_derived": True,
            "symbolic_finite_mixed_state_pointwise_no_go_derived": True,
            "symbolic_nested_cusp_subfamily_contraction_derived": True,
            "symbolic_maximal_floor_loop_exit_grammar_derived": True,
            "bounded_machine_regression_passed": True,
            "programmatically_exhausted_all_positive_integers": False,
            "global_recursive_lyapunov_derived": False,
            "global_collatz_proof": False,
            "next_gap": (
                "Resolve the S_exit=3 higher-R family and determine the next "
                "negative-fixed-point coordinate or a contracting "
                "multi-return grammar across its induced returns."
            ),
        },
    )


def main(argv: list[str] | None = None) -> None:
    """Write the exact ``R=2`` recursive-cusp artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-mod2-power", type=int, default=8)
    parser.add_argument("--source-u-mod3", type=int, default=2)
    parser.add_argument("--source-mod3-power", type=int, default=2)
    parser.add_argument("--verification-power", type=int, default=12)
    parser.add_argument("--verification-target-R-max", type=int, default=20)
    parser.add_argument("--verification-max-loops", type=int, default=8)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = r2_exact_frontier_report(
        target_mod2_power=args.target_mod2_power,
        source_u_mod3=args.source_u_mod3,
        source_mod3_power=args.source_mod3_power,
        verification_power=args.verification_power,
        verification_target_R_max=args.verification_target_R_max,
        verification_max_loops=args.verification_max_loops,
        input_path=args.input,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.to_json() + "\n", encoding="utf-8")
    LOGGER.info(
        "wrote %s (status=%s; instances=%d)",
        args.output,
        report.status,
        report.finite_verification["parametric_instances_verified"],
    )


if __name__ == "__main__":
    main()
