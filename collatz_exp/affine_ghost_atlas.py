"""Exact repeat and chart-switch laws for affine Collatz ghost charts.

For a nonempty accelerated valuation word ``W`` write

``T_W(n) = (3^M n + B) / 2^A``.

When ``D = 3^M - 2^A > 0``, the affine map is expanding and its negative
fixed point defines the positive linear coordinate ``L_W(n) = D*n + B``.
This module proves three exact facts.

* ``W`` is the next exact valuation word at an odd ``n`` exactly when
  ``v2(L_W(n)) >= A + 1``.
* The maximal consecutive repeat count is therefore
  ``floor((v2(L_W(n)) - 1) / A)``.
* For two expanding charts, a single integer
  ``G = B_V*D_W - D_V*B_W`` controls the 2-adic depth at a chart switch.
  Away from one equality of valuations, depth is the smaller of two known
  values; at equality it can resonate upward.

The first atlas slice applies these laws to ``W=(1,1,2)``.  It records its
complete residual exit partition, the resonant switch to ``(1,1,2,2)``, and
an exact refined cylinder whose fixed 13-step word descends.  The atlas is
not closed under every possible chart switch and is not a proof of the
Collatz conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from .core import affine_from_word, apply_word, v2, valuation_word


LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("docs/reports/pecm_higher_r_affine_ghost.json")
DEFAULT_INPUT_SHA256 = (
    "9ac0bd58a054911bd694b0ee96218c014aa842c679926dc020721a8e450d11db"
)
DEFAULT_OUTPUT_PATH = Path("docs/reports/pecm_affine_ghost_atlas.json")
DEFAULT_VERIFICATION_POWER = 14

W112 = (1, 1, 2)
W1122 = (1, 1, 2, 2)
K1123 = (1, 1, 2, 3)
V2112 = (2, 1, 1, 2)
C322 = (3, 2, 2)
CANONICAL_SOURCE = 38119
CANONICAL_FULL_WORD = (
    1,
    1,
    2,
    1,
    1,
    2,
    2,
    1,
    1,
    2,
    3,
    2,
    2,
)


def _word_tuple(word: Iterable[int]) -> tuple[int, ...]:
    values = tuple(word)
    if not values:
        raise ValueError("valuation word must be nonempty")
    if any(value < 1 for value in values):
        raise ValueError("valuation words must contain positive integers")
    return values


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


def _ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


@dataclass(frozen=True)
class AffineGhostChart:
    """One expanding affine valuation-word chart."""

    word: tuple[int, ...]
    M: int
    A: int
    B: int
    D: int
    slope: Fraction
    ghost: Fraction
    exact_residue: int
    exact_modulus: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "word": list(self.word),
            "M": self.M,
            "A": self.A,
            "B": str(self.B),
            "D": str(self.D),
            "map": f"T(n) = (3^{self.M}*n + {self.B}) / 2^{self.A}",
            "linear_form": f"{self.D}*n + {self.B}",
            "slope": _fraction_json(self.slope),
            "ghost": _fraction_json(self.ghost),
            "exact_word_cylinder": {
                "residue": str(self.exact_residue),
                "modulus": str(self.exact_modulus),
                "criterion": f"v2({self.D}*n + {self.B}) >= {self.A + 1}",
            },
        }


@dataclass(frozen=True)
class GhostRepeatRun:
    """The exact maximal run of one expanding word from one source."""

    chart: AffineGhostChart
    source_n: int
    source_linear_value: int
    source_linear_v2: int
    repeat_count: int
    landing_n: int
    landing_linear_value: int
    residual_depth: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "chart": self.chart.to_json_dict(),
            "source_n": str(self.source_n),
            "source_linear_value": str(self.source_linear_value),
            "source_linear_v2": self.source_linear_v2,
            "repeat_count": self.repeat_count,
            "repeat_count_formula": "floor((source_linear_v2 - 1) / A)",
            "landing_n": str(self.landing_n),
            "landing_linear_value": str(self.landing_linear_value),
            "residual_depth": self.residual_depth,
            "word_is_exhausted_at_landing": True,
        }


@dataclass(frozen=True)
class ChartSwitchResonance:
    """Exact valuation certificate for one expanding-chart switch."""

    source_chart: AffineGhostChart
    target_chart: AffineGhostChart
    source_n: int
    after_source_n: int
    source_linear_v2: int
    residual_depth: int
    gap_G: int
    gap_v2: int | None
    target_linear_value: int
    target_linear_v2: int
    valuation_case: str
    resonance_lift: int
    target_word_exact: bool

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.source_chart.word),
            "target_word": list(self.target_chart.word),
            "source_n": str(self.source_n),
            "after_source_n": str(self.after_source_n),
            "source_linear_v2": self.source_linear_v2,
            "residual_depth": self.residual_depth,
            "gap_G": str(self.gap_G),
            "gap_v2": self.gap_v2,
            "target_linear_value": str(self.target_linear_value),
            "target_linear_v2": self.target_linear_v2,
            "valuation_case": self.valuation_case,
            "resonance_lift": self.resonance_lift,
            "target_word_exact": self.target_word_exact,
            "identity": {
                "integer_gap": "G = B_target*D_source - D_target*B_source",
                "coordinate": (
                    "L_target(T_source(n)) = "
                    "(D_target*3^M_source*2^residual*z + G) / D_source"
                ),
                "z": "L_source(n) / 2^source_linear_v2 is odd",
            },
        }


@dataclass(frozen=True)
class W112ExitStage:
    """One member of the exact residual exit partition for ``(1,1,2)``."""

    source_n: int
    residual_depth: int
    odd_z: int
    branch_q: int
    exit_word: tuple[int, ...]
    landing_n: int
    outcome: str
    target_ghost: Fraction | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_n": str(self.source_n),
            "residual_depth": self.residual_depth,
            "odd_z": str(self.odd_z),
            "branch_q": self.branch_q,
            "exit_word": list(self.exit_word),
            "landing_n": str(self.landing_n),
            "outcome": self.outcome,
            "target_ghost": (
                None if self.target_ghost is None else _fraction_json(self.target_ghost)
            ),
        }


@dataclass(frozen=True)
class ExactDescentCylinder:
    """A complete exact-word cylinder on which the word descends."""

    word: tuple[int, ...]
    M: int
    A: int
    B: int
    contraction_gap: int
    fixed_point: Fraction
    residue: int
    modulus: int
    source_n: int
    landing_n: int
    all_positive_members_descend: bool

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "word": list(self.word),
            "M": self.M,
            "A": self.A,
            "B": str(self.B),
            "slope": _fraction_json(Fraction(3**self.M, 1 << self.A)),
            "contraction_gap": str(self.contraction_gap),
            "positive_fixed_point": _fraction_json(self.fixed_point),
            "exact_cylinder": {
                "residue": str(self.residue),
                "modulus": str(self.modulus),
                "parameterization": f"n = {self.residue} + {self.modulus}*t, t >= 0",
            },
            "witness_source_n": str(self.source_n),
            "witness_landing_n": str(self.landing_n),
            "all_positive_members_descend": self.all_positive_members_descend,
            "descent_inequality": (f"{self.contraction_gap}*n > {self.B}"),
        }


@dataclass(frozen=True)
class AffineGhostAtlasReport:
    """Machine-readable first exact affine-ghost atlas slice."""

    type: str
    status: str
    provenance: dict[str, Any]
    universal_word_cylinder: dict[str, Any]
    repeat_grammar: dict[str, Any]
    haar_exit_law: dict[str, Any]
    chart_switch_resonance: dict[str, Any]
    w112_exit_partition: dict[str, Any]
    atlas_path_fixtures: dict[str, Any]
    refined_descent_cylinder: dict[str, Any]
    finite_verification: dict[str, Any]
    frontier: dict[str, Any]
    max_plus: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "provenance": dict(self.provenance),
            "universal_word_cylinder": dict(self.universal_word_cylinder),
            "repeat_grammar": dict(self.repeat_grammar),
            "haar_exit_law": dict(self.haar_exit_law),
            "chart_switch_resonance": dict(self.chart_switch_resonance),
            "w112_exit_partition": dict(self.w112_exit_partition),
            "atlas_path_fixtures": dict(self.atlas_path_fixtures),
            "refined_descent_cylinder": dict(self.refined_descent_cylinder),
            "finite_verification": dict(self.finite_verification),
            "frontier": dict(self.frontier),
            "max_plus": dict(self.max_plus),
            "proof": dict(self.proof),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def exact_word_residue(word: Iterable[int]) -> tuple[int, int]:
    """Return the unique odd residue modulo ``2^(A+1)`` realizing ``word``."""

    values = _word_tuple(word)
    affine = affine_from_word(values)
    modulus = 1 << (affine.A + 1)
    residue = ((1 << affine.A) - affine.B) * pow(3**affine.m, -1, modulus) % modulus
    if residue % 2 == 0:
        raise AssertionError("exact valuation-word residue is not odd")
    return residue, modulus


def word_is_exact(word: Iterable[int], n: int) -> bool:
    """Return whether the next accelerated valuations at ``n`` equal ``word``.

    The implementation uses the exact terminal congruence, not orbit
    simulation.  Uniqueness follows because ``3^M`` is invertible modulo
    ``2^(A+1)``.
    """

    values = _word_tuple(word)
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    affine = affine_from_word(values)
    D = 3**affine.m - (1 << affine.A)
    return (D * n + affine.B) % (1 << (affine.A + 1)) == 0


def expanding_ghost_chart(word: Iterable[int]) -> AffineGhostChart:
    """Build the exact chart for one expanding valuation word."""

    values = _word_tuple(word)
    affine = affine_from_word(values)
    numerator = 3**affine.m
    denominator = 1 << affine.A
    D = numerator - denominator
    if D <= 0:
        raise ValueError("ghost chart requires an expanding valuation word")
    residue, modulus = exact_word_residue(values)
    return AffineGhostChart(
        word=values,
        M=affine.m,
        A=affine.A,
        B=affine.B,
        D=D,
        slope=Fraction(numerator, denominator),
        ghost=Fraction(-affine.B, D),
        exact_residue=residue,
        exact_modulus=modulus,
    )


def maximal_ghost_repeat_run(
    word: Iterable[int],
    source_n: int,
) -> GhostRepeatRun:
    """Return the exact consecutive run of an expanding word.

    An already exhausted source is valid and produces a zero-use run with
    residual depth in ``{1,...,A}``.
    """

    chart = expanding_ghost_chart(word)
    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    source_linear = chart.D * source_n + chart.B
    source_s = v2(source_linear)
    repeat_count = (source_s - 1) // chart.A
    landing = source_n
    for _ in range(repeat_count):
        landing = apply_word(landing, chart.word)
    landing_linear = chart.D * landing + chart.B
    residual = v2(landing_linear)
    if residual != source_s - repeat_count * chart.A:
        raise AssertionError("ghost-coordinate valuation drop failed")
    if not 1 <= residual <= chart.A:
        raise AssertionError("maximal repeat did not leave a residual depth")
    if word_is_exact(chart.word, landing):
        raise AssertionError("word remains exact after claimed maximal run")
    return GhostRepeatRun(
        chart=chart,
        source_n=source_n,
        source_linear_value=source_linear,
        source_linear_v2=source_s,
        repeat_count=repeat_count,
        landing_n=landing,
        landing_linear_value=landing_linear,
        residual_depth=residual,
    )


def ghost_exit_haar_masses(total_A: int) -> tuple[Fraction, ...]:
    """Return the conditional odd-2-adic masses of residual depths ``1..A``."""

    if total_A < 1:
        raise ValueError("total_A must be positive")
    denominator = (1 << total_A) - 1
    masses = tuple(
        Fraction(1 << (total_A - residual), denominator)
        for residual in range(1, total_A + 1)
    )
    if sum(masses, Fraction()) != 1:
        raise AssertionError("exit masses do not sum to one")
    return masses


def chart_switch_resonance(
    source_word: Iterable[int],
    target_word: Iterable[int],
    source_n: int,
) -> ChartSwitchResonance:
    """Certify the exact 2-adic valuation law after one chart switch."""

    source = expanding_ghost_chart(source_word)
    target = expanding_ghost_chart(target_word)
    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    if not word_is_exact(source.word, source_n):
        raise ValueError("source_word is not exact at source_n")

    source_linear = source.D * source_n + source.B
    source_s = v2(source_linear)
    residual = source_s - source.A
    if residual < 1:
        raise AssertionError("exact source word left no residual valuation")
    z = source_linear >> source_s
    if z % 2 == 0:
        raise AssertionError("normalized source coordinate is not odd")

    after_source = apply_word(source_n, source.word)
    target_linear = target.D * after_source + target.B
    target_s = v2(target_linear)
    gap = target.B * source.D - target.D * source.B
    gap_s = None if gap == 0 else v2(abs(gap))
    predicted_numerator = target.D * (3**source.M) * (1 << residual) * z + gap
    if target_linear * source.D != predicted_numerator:
        raise AssertionError("integer ghost-gap identity failed")

    if gap_s is None:
        valuation_case = "zero_gap_no_resonance"
        expected = residual
        resonance_lift = 0
    elif residual < gap_s:
        valuation_case = "residual_below_gap"
        expected = residual
        resonance_lift = 0
    elif residual > gap_s:
        valuation_case = "gap_below_residual"
        expected = gap_s
        resonance_lift = 0
    else:
        valuation_case = "resonance"
        if target_s <= gap_s:
            raise AssertionError("equal-depth chart switch did not resonate")
        expected = target_s
        resonance_lift = target_s - gap_s
    if target_s != expected:
        raise AssertionError("chart-switch valuation law failed")

    return ChartSwitchResonance(
        source_chart=source,
        target_chart=target,
        source_n=source_n,
        after_source_n=after_source,
        source_linear_v2=source_s,
        residual_depth=residual,
        gap_G=gap,
        gap_v2=gap_s,
        target_linear_value=target_linear,
        target_linear_v2=target_s,
        valuation_case=valuation_case,
        resonance_lift=resonance_lift,
        target_word_exact=word_is_exact(target.word, after_source),
    )


def same_point_ghost_gap_threshold(
    source_word: Iterable[int],
    target_word: Iterable[int],
    ratio_upper: Fraction,
) -> int:
    """Give a sufficient source-coordinate threshold for a chart change.

    At the same positive odd integer,

    ``L_V/L_W = D_V/D_W + (B_V - D_V*B_W/D_W)/L_W``.

    The returned integer ``N`` guarantees ``L_V/L_W <= ratio_upper`` whenever
    ``L_W >= N``.  A finite large-coordinate threshold exists in this form
    only when ``ratio_upper`` is strictly above the limiting linear ratio.
    """

    source = expanding_ghost_chart(source_word)
    target = expanding_ghost_chart(target_word)
    limiting = Fraction(target.D, source.D)
    if ratio_upper <= limiting:
        raise ValueError("ratio_upper must exceed the limiting linear ratio")
    additive = Fraction(
        target.B * source.D - target.D * source.B,
        source.D,
    )
    if additive <= 0:
        return 1
    return max(1, _ceil_fraction(additive / (ratio_upper - limiting)))


def w112_exit_stage(source_n: int) -> W112ExitStage:
    """Classify one exhausted ``(1,1,2)`` chart state exactly."""

    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    chart = expanding_ghost_chart(W112)
    linear = chart.D * source_n + chart.B
    residual = v2(linear)
    if not 1 <= residual <= chart.A:
        raise ValueError("source_n is not an exhausted (1,1,2) chart state")
    z = linear >> residual
    if z % 2 == 0:
        raise AssertionError("residual quotient is not odd")

    target_ghost: Fraction | None = None
    if residual == 1:
        q = v2(3 * z - 23)
        word = (1 + q,)
        outcome = (
            "terminal_equality" if source_n == 1 else "descent_below_exhausted_source"
        )
    elif residual == 2:
        q = v2(9 * z - 29)
        word = (1, 1 + q)
        if q == 1:
            outcome = "switch_to_expanding_ghost"
            target_ghost = expanding_ghost_chart(word).ghost
        else:
            outcome = "descent_below_exhausted_source"
    elif residual == 3:
        q = v2(81 * z - 103)
        word = (1, 1, 1, q)
        if q <= 3:
            outcome = "switch_to_expanding_ghost"
            target_ghost = expanding_ghost_chart(word).ghost
        else:
            outcome = "descent_below_exhausted_source"
    else:
        q = v2(27 * z - 19)
        word = (1, 1, 2 + q)
        outcome = "descent_below_exhausted_source"

    landing = apply_word(source_n, word)
    if outcome == "descent_below_exhausted_source" and not landing < source_n:
        raise AssertionError("claimed exit branch did not descend")
    if outcome == "terminal_equality" and landing != source_n:
        raise AssertionError("terminal branch is not equality")
    if outcome == "switch_to_expanding_ghost":
        affine = affine_from_word(word)
        if 3**affine.m <= 1 << affine.A:
            raise AssertionError("claimed target chart is not expanding")
    return W112ExitStage(
        source_n=source_n,
        residual_depth=residual,
        odd_z=z,
        branch_q=q,
        exit_word=word,
        landing_n=landing,
        outcome=outcome,
        target_ghost=target_ghost,
    )


def exact_descent_cylinder(
    word: Iterable[int],
    source_n: int,
) -> ExactDescentCylinder:
    """Certify descent on the complete exact cylinder for a contracting word."""

    values = _word_tuple(word)
    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    affine = affine_from_word(values)
    gap = (1 << affine.A) - 3**affine.m
    if gap <= 0:
        raise ValueError("descent cylinder requires a contracting word")
    residue, modulus = exact_word_residue(values)
    if source_n % modulus != residue:
        raise ValueError("source_n is not in the exact word cylinder")
    landing = apply_word(source_n, values)
    if landing * (1 << affine.A) != 3**affine.m * source_n + affine.B:
        raise AssertionError("affine descent formula failed")
    all_descend = gap * residue > affine.B
    if all_descend and not landing < source_n:
        raise AssertionError("canonical member failed certified descent")
    return ExactDescentCylinder(
        word=values,
        M=affine.m,
        A=affine.A,
        B=affine.B,
        contraction_gap=gap,
        fixed_point=Fraction(affine.B, gap),
        residue=residue,
        modulus=modulus,
        source_n=source_n,
        landing_n=landing,
        all_positive_members_descend=all_descend,
    )


def _validate_input_artifact(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "json_parsed": False,
        "type_matches": False,
        "affine_ghost_theorem_present": False,
        "open_cross_chart_gap_present": False,
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
    result["type_matches"] = (
        payload.get("type") == "pecm_higher_r_affine_ghost_phase_transfer"
    )
    theorem = payload.get("affine_ghost_theorem")
    result["affine_ghost_theorem_present"] = bool(
        isinstance(theorem, dict)
        and theorem.get("valuation_update") == "v2(L_W(T(n)))=v2(L_W(n))-A"
        and isinstance(theorem.get("finite_repeat_budget"), str)
    )
    frontier = payload.get("frontier")
    result["open_cross_chart_gap_present"] = bool(
        isinstance(frontier, dict)
        and frontier.get("affine_ghost_chart_count_finite") is False
        and frontier.get("full_post_exit_stopping_grammar_closed") is False
    )
    proof = payload.get("proof")
    result["global_proof_disclaimed"] = bool(
        isinstance(proof, dict)
        and proof.get("global_cross_chart_lyapunov_derived") is False
        and proof.get("global_collatz_proof") is False
    )
    required = (
        "type_matches",
        "affine_ghost_theorem_present",
        "open_cross_chart_gap_present",
        "global_proof_disclaimed",
    )
    result["fully_verified"] = all(result[key] is True for key in required)
    if not result["fully_verified"]:
        result["errors"].append(
            "artifact content does not certify the prior affine-ghost frontier"
        )
    return result


def _verify_exact_word_theorem(
    verification_power: int,
) -> tuple[int, int, str]:
    if verification_power < 7:
        raise ValueError(
            "verification_power must be at least seven to cover every "
            "configured exact cylinder"
        )
    words = (
        (1, 2),
        W112,
        W1122,
        (1, 1, 1, 1),
        (1, 1, 1, 2),
        (1, 1, 1, 3),
    )
    digest = hashlib.sha256()
    memberships = 0
    repeat_runs = 0
    limit = 1 << verification_power
    for word in words:
        word_repeat_runs = 0
        for n in range(1, limit, 2):
            exact_by_orbit = valuation_word(n, len(word)) == word
            exact_by_linear = word_is_exact(word, n)
            if exact_by_orbit != exact_by_linear:
                raise AssertionError("exact word-cylinder criterion failed")
            memberships += 1
            if not exact_by_linear:
                continue
            run = maximal_ghost_repeat_run(word, n)
            x = n
            actual_repeats = 0
            while valuation_word(x, len(word)) == word:
                x = apply_word(x, word)
                actual_repeats += 1
            if actual_repeats != run.repeat_count or x != run.landing_n:
                raise AssertionError("exact maximal repeat formula failed")
            repeat_runs += 1
            word_repeat_runs += 1
            digest.update(
                f"{word}:{n}:{run.repeat_count}:{run.residual_depth}\n".encode()
            )
        if word_repeat_runs == 0:
            raise AssertionError("bounded verification missed an exact cylinder")
    return memberships, repeat_runs, digest.hexdigest()


def affine_ghost_atlas_report(
    *,
    verification_power: int = DEFAULT_VERIFICATION_POWER,
    input_path: Path = DEFAULT_INPUT_PATH,
) -> AffineGhostAtlasReport:
    """Build the first exact repeat-and-resonance atlas report."""

    validation = _validate_input_artifact(input_path)
    input_sha = _sha256(input_path)
    snapshot_match = input_sha == DEFAULT_INPUT_SHA256
    canonical_provenance = bool(
        input_path == DEFAULT_INPUT_PATH
        and snapshot_match
        and validation["fully_verified"]
    )
    if canonical_provenance:
        scope_relation = "canonical_prior_frontier_verified"
    elif not validation["exists"]:
        scope_relation = "input_artifact_missing"
    elif not validation["fully_verified"]:
        scope_relation = "input_artifact_structurally_invalid"
    elif not snapshot_match:
        scope_relation = "canonical_artifact_snapshot_mismatch"
    else:
        scope_relation = "canonical_snapshot_at_noncanonical_path"

    w_chart = expanding_ghost_chart(W112)
    w_run = maximal_ghost_repeat_run(W112, CANONICAL_SOURCE)
    switch = chart_switch_resonance(
        W112,
        W1122,
        CANONICAL_SOURCE,
    )
    u_run = maximal_ghost_repeat_run(W1122, switch.after_source_n)
    if (
        w_run.repeat_count != 2
        or w_run.landing_n != 108553
        or switch.after_source_n != 64327
        or switch.gap_G != 480
        or switch.gap_v2 != 5
        or switch.target_linear_v2 != 12
        or switch.resonance_lift != 7
        or u_run.repeat_count != 1
        or u_run.landing_n != 81415
    ):
        raise AssertionError("canonical expanding atlas path changed")

    k_affine = affine_from_word(K1123)
    k_landing = apply_word(u_run.landing_n, K1123)
    if (
        k_affine.A != 7
        or k_affine.B != 73
        or 3**k_affine.m - (1 << k_affine.A) != -47
        or k_landing != 51521
    ):
        raise AssertionError("canonical contracting sibling changed")
    tail_landing = apply_word(k_landing, (2, 2))
    if tail_landing != 28981:
        raise AssertionError("canonical terminal descent changed")

    maximal_w_source = switch.after_source_n
    maximal_switch = chart_switch_resonance(
        W112,
        V2112,
        maximal_w_source,
    )
    maximal_w_run = maximal_ghost_repeat_run(W112, maximal_w_source)
    v_run = maximal_ghost_repeat_run(V2112, maximal_switch.after_source_n)
    c_descent = exact_descent_cylinder(C322, v_run.landing_n)
    if (
        maximal_w_run.repeat_count != 1
        or maximal_w_run.landing_n != 108553
        or maximal_switch.gap_G != 810
        or maximal_switch.gap_v2 != 1
        or maximal_switch.residual_depth != 1
        or maximal_switch.target_linear_v2 != 8
        or maximal_switch.resonance_lift != 7
        or not maximal_switch.target_word_exact
        or v_run.repeat_count != 1
        or v_run.landing_n != 137389
        or v_run.residual_depth != 2
        or c_descent.landing_n != tail_landing
    ):
        raise AssertionError("canonical maximal-word atlas path changed")
    v_affine = affine_from_word(V2112)
    c_affine = affine_from_word(C322)
    c_gap = c_affine.B * (3**v_affine.m - (1 << v_affine.A)) - (
        (3**c_affine.m - (1 << c_affine.A)) * v_affine.B
    )
    if c_gap != 11508 or v2(c_gap) != 2:
        raise AssertionError("canonical V2112-to-C322 resonance changed")

    descent = exact_descent_cylinder(
        CANONICAL_FULL_WORD,
        CANONICAL_SOURCE,
    )
    if (
        descent.M != 13
        or descent.A != 21
        or descent.B != 3563675
        or descent.contraction_gap != 502829
        or descent.residue != CANONICAL_SOURCE
        or descent.modulus != 1 << 22
        or descent.landing_n != tail_landing
        or not descent.all_positive_members_descend
    ):
        raise AssertionError("canonical refined descent cylinder changed")
    proper_prefix_D = []
    for prefix_length in range(1, len(CANONICAL_FULL_WORD)):
        prefix = affine_from_word(CANONICAL_FULL_WORD[:prefix_length])
        proper_prefix_D.append(3**prefix.m - (1 << prefix.A))
    if not all(D > 0 for D in proper_prefix_D):
        raise AssertionError("canonical descent is no longer first at step 13")

    exit_fixtures = tuple(
        w112_exit_stage(n) for n in (108553, 3, 11, 31, 47, 79, 15, 23)
    )
    fixture_classes = {
        (stage.residual_depth, stage.branch_q, stage.outcome) for stage in exit_fixtures
    }
    expected_classes = {
        (1, 1, "descent_below_exhausted_source"),
        (2, 3, "descent_below_exhausted_source"),
        (2, 1, "switch_to_expanding_ghost"),
        (3, 1, "switch_to_expanding_ghost"),
        (3, 2, "switch_to_expanding_ghost"),
        (3, 3, "switch_to_expanding_ghost"),
        (3, 5, "descent_below_exhausted_source"),
        (4, 3, "descent_below_exhausted_source"),
    }
    if fixture_classes != expected_classes:
        raise AssertionError("W112 exit fixtures no longer cover every class")

    membership_checks, repeat_checks, verification_digest = _verify_exact_word_theorem(
        verification_power
    )
    masses = ghost_exit_haar_masses(w_chart.A)
    gap_threshold = same_point_ghost_gap_threshold(
        W112,
        W1122,
        Fraction(2),
    )

    return AffineGhostAtlasReport(
        type="pecm_exact_affine_ghost_repeat_atlas",
        status=("exact_repeat_and_resonance_theorems_with_first_open_atlas_slice"),
        provenance={
            "input_path": str(input_path),
            "expected_sha256": DEFAULT_INPUT_SHA256,
            "actual_sha256": input_sha,
            "artifact_snapshot_match": snapshot_match,
            "artifact_content_validation": validation,
            "canonical_prior_frontier_verified": canonical_provenance,
            "scope_relation": scope_relation,
        },
        universal_word_cylinder={
            "status": "exact_theorem",
            "setting": "every nonempty positive accelerated valuation word W",
            "affine_map": "T_W(n) = (3^M*n+B)/2^A",
            "linear_form": "L_W(n) = (3^M-2^A)*n+B",
            "equivalence": (
                "W is exact at positive odd n iff "
                "v2(|L_W(n)|) >= A+1, with v2(0)=infinity"
            ),
            "terminal_congruence": ("3^M*n+B = 2^A (mod 2^(A+1))"),
            "unique_cylinder": (
                "one odd residue modulo 2^(A+1), because 3^M is invertible"
            ),
            "proof_method": (
                "the terminal congruence selects one odd residue; the standard "
                "backward valuation-cylinder construction selects the same "
                "unique residue"
            ),
        },
        repeat_grammar={
            "status": "exact_theorem_for_expanding_words",
            "coordinate_identity": ("L_W(T_W(n)) = (3^M/2^A)*L_W(n)"),
            "valuation_drop_per_copy": "A",
            "maximal_repeat_count": "floor((v2(L_W(n))-1)/A)",
            "residual_depth": "e = v2(L_W(n)) mod A, represented in {1,...,A}",
            "fixed_expanding_word_repeats_forever": False,
            "canonical_W112_run": w_run.to_json_dict(),
        },
        haar_exit_law={
            "status": "exact_conditional_odd_2_adic_measure_not_pointwise_rate",
            "conditioning": (
                "positive odd n lies in the exact W cylinder before maximal "
                "repetition; the single profinite ghost has Haar measure zero"
            ),
            "formula": "P(e) = 2^(A-e)/(2^A-1), e=1,...,A",
            "W112_A": w_chart.A,
            "W112_residual_masses": [
                {
                    "residual_depth": residual,
                    "mass": _fraction_json(mass),
                }
                for residual, mass in enumerate(masses, start=1)
            ],
            "iid_or_orbit_independence_claim": False,
        },
        chart_switch_resonance={
            "status": "exact_theorem_for_two_expanding_charts",
            "integer_gap": "G = B_V*D_W - D_V*B_W",
            "after_one_W": (
                "v2(L_V(T_W(n))) = v2(D_V*3^M_W*2^r*z + G), r=v2(L_W(n))-A_W and z odd"
            ),
            "nonresonant_rule": (
                "if r != v2(G), the new depth is min(r,v2(G)); "
                "if G=0 the new depth is r"
            ),
            "resonant_rule": (
                "if r=v2(G), the two odd leading terms cancel and the "
                "new depth is strictly greater than r"
            ),
            "maximal_exit_complexity_corollary": {
                "hypothesis": (
                    "W is used for its last possible copy, and V is exact "
                    "immediately afterward"
                ),
                "result": (
                    "every nonresonant legal edge has A_V < A_W; "
                    "every legal edge with A_V >= A_W is resonant"
                ),
                "proof": (
                    "the post-W residual e lies in {1,...,A_W}; a "
                    "nonresonant target has v2(L_V)=min(e,v2(G)), while "
                    "exactness requires v2(L_V)>=A_V+1"
                ),
                "cycle_consequence": (
                    "every directed cycle of maximal expanding-word charts "
                    "contains a resonance edge"
                ),
                "global_termination_consequence": False,
            },
            "canonical_W112_to_W1122": switch.to_json_dict(),
            "canonical_maximal_W112_to_V2112": (maximal_switch.to_json_dict()),
            "same_point_large_coordinate_lemma": {
                "identity": ("L_V/L_W = D_V/D_W + (B_V-D_V*B_W/D_W)/L_W"),
                "example_ratio_upper": _fraction_json(Fraction(2)),
                "example_sufficient_L_W_threshold": str(gap_threshold),
                "global_weighted_switch_bound_derived": False,
            },
        },
        w112_exit_partition={
            "status": "exact_complete_residual_partition",
            "chart": w_chart.to_json_dict(),
            "normal_form": "11*n+19 = 2^e*z with z odd and e in {1,2,3,4}",
            "comparison_baseline": (
                "source_n is the exhausted W112 state, not the pre-run chart entry"
            ),
            "descent_below_pre_run_entry_claim": False,
            "branches": [
                {
                    "e": 1,
                    "forced_word": "(1+q), q=v2(3*z-23)>=1",
                    "outcome": (
                        "descent below exhausted source for n>1; "
                        "n=1 is terminal equality"
                    ),
                },
                {
                    "e": 2,
                    "forced_word": "(1,1+q), q=v2(9*z-29)>=1",
                    "outcome": (
                        "q=1 switches to expanding ghost -5; q>=2 descends "
                        "below exhausted source"
                    ),
                },
                {
                    "e": 3,
                    "forced_word": "(1,1,1,q), q=v2(81*z-103)>=1",
                    "outcome": (
                        "q=1,2,3 switch to ghosts -1,-65/49,-65/17; "
                        "q>=4 descends below exhausted source"
                    ),
                },
                {
                    "e": 4,
                    "forced_word": "(1,1,2+q), q=v2(27*z-19)>=1",
                    "outcome": "descent below exhausted source",
                },
            ],
            "exact_fixtures": [fixture.to_json_dict() for fixture in exit_fixtures],
            "remaining_expanding_target_charts": [
                [1, 2],
                [1, 1, 1, 1],
                [1, 1, 1, 2],
                [1, 1, 1, 3],
            ],
        },
        atlas_path_fixtures={
            "status": ("exact_itinerary_fixtures_not_a_complete_chart_selection_rule"),
            "induced_chart_selection_rule_complete": False,
            "lands_below_original_source": tail_landing < CANONICAL_SOURCE,
            "maximal_word_decomposition": {
                "values": [
                    "38119",
                    "64327",
                    "108553",
                    "137389",
                    "28981",
                ],
                "macro_words": [
                    list(W112),
                    list(W112),
                    list(V2112),
                    list(C322),
                ],
                "second_W_run": maximal_w_run.to_json_dict(),
                "resonant_W112_to_V2112_switch": (maximal_switch.to_json_dict()),
                "V2112_repeat": v_run.to_json_dict(),
                "contracting_C322": c_descent.to_json_dict(),
                "V2112_to_C322_integer_gap": str(c_gap),
                "V2112_to_C322_gap_v2": v2(c_gap),
                "decomposition_role": (
                    "this maximal-word grouping supports the strict "
                    "nonresonant A-decrease corollary"
                ),
            },
            "exact_higher_tail_return_regrouping": {
                "values": [
                    "38119",
                    "64327",
                    "81415",
                    "51521",
                    "38641",
                    "28981",
                ],
                "macro_words": [
                    list(W112),
                    list(W1122),
                    list(K1123),
                    [2],
                    [2],
                ],
                "W112_chart": w_chart.to_json_dict(),
                "resonant_W112_to_W1122_switch": switch.to_json_dict(),
                "W1122_repeat": u_run.to_json_dict(),
                "contracting_sibling": {
                    "word": list(K1123),
                    "map": "T(n)=(81*n+73)/128",
                    "D": "-47",
                    "positive_fixed_point": _fraction_json(Fraction(73, 47)),
                    "source_n": "81415",
                    "landing_n": str(k_landing),
                    "descends_for_every_positive_exact_source_n_at_least_3": True,
                },
                "decomposition_role": (
                    "natural higher-tail returns; its W-to-W1122 switch "
                    "occurs before W is maximally exhausted"
                ),
            },
        },
        refined_descent_cylinder={
            **descent.to_json_dict(),
            "first_descent_is_exactly_step": 13,
            "proper_prefix_count": len(proper_prefix_D),
            "all_proper_prefix_affine_D_positive": True,
            "lift_formula": {
                "source": "38119 + 4194304*t",
                "landing": "28981 + 3188646*t",
                "source_minus_landing": "9138 + 1005658*t",
                "valid_for_every_integer_t_at_least_zero": True,
            },
            "mixed_higher_tail_subfamily": {
                "source_tail_depth_R": 3,
                "source_unit_mod_3_power": {
                    "residue": "67",
                    "power": 4,
                },
                "parameterization": ("n = 38119 + 2^22*3^4*t, t >= 0"),
                "why_extra_factor": (
                    "inside n=38119+2^22*s, preserving "
                    "(n+1)/8 = 67 (mod 3^4) requires s=0 (mod 3^4)"
                ),
            },
            "specific_word_precision": {
                "claim": (
                    "2^22 precision is necessary to force this specific "
                    "13-step valuation word"
                ),
                "older_mixed_period": "2^11*3^4",
                "counterexample_source_n": "204007",
                "counterexample_identity": "204007 = 38119 + 2^11*3^4",
                "counterexample_word_prefix": [
                    1,
                    1,
                    2,
                    1,
                    1,
                    2,
                    2,
                    3,
                ],
                "first_word_difference_step": 8,
                "other_coarse_cylinder_descent_proofs_excluded": False,
            },
        },
        finite_verification={
            "role": "bounded_regression_of_exact_formulas_not_proof_by_search",
            "verification_power": verification_power,
            "odd_inputs_per_word": 1 << (verification_power - 1),
            "expanding_words_checked": 6,
            "word_membership_checks": membership_checks,
            "maximal_repeat_runs_checked": repeat_checks,
            "digest_sha256": verification_digest,
            "w112_exit_fixture_count": len(exit_fixtures),
            "passed": True,
        },
        frontier={
            "W112_exhausted_exit_partition_complete": True,
            "closed_transition_graph": False,
            "all_expanding_exit_charts_recursively_closed": False,
            "all_expanding_words_covered": False,
            "all_edge_strata_covered": False,
            "induced_chart_selection_rule_complete": False,
            "edge_composability_verified": False,
            "positive_integer_itinerary_coverage_complete": False,
            "resonances_can_raise_2_adic_depth": True,
            "number_of_reachable_ghost_charts_proved_finite": False,
            "every_maximal_chart_cycle_requires_a_resonance": True,
            "resonance_depth_reset_bound_derived": False,
            "weighted_chart_switch_inequalities_closed": False,
            "finite_exceptional_set_derived": False,
            "next_exact_task": (
                "recursively partition the four expanding W112 exit charts, "
                "track their integer gaps G, and determine whether a "
                "well-founded chart complexity or a closed weighted graph exists"
            ),
        },
        max_plus={
            "status": "not_applicable_open_transition_graph",
            "finite_karp_run": False,
            "cycles": [],
            "reason": (
                "chart selection, edge strata, and recursive target coverage "
                "are not closed"
            ),
        },
        proof={
            "claim_kind": ("exact_symbolic_theorems_with_bounded_formula_regression"),
            "canonical_input_frontier_link_verified": canonical_provenance,
            "universal_exact_word_cylinder_theorem_derived": True,
            "exact_maximal_repeat_formula_derived": True,
            "exact_conditional_haar_exit_law_derived": True,
            "exact_chart_switch_resonance_lemma_derived": True,
            "nonresonant_maximal_edges_strictly_decrease_A": True,
            "exact_W112_exit_partition_derived": True,
            "exact_refined_descent_cylinder_derived": True,
            "bounded_machine_regression_passed": True,
            "programmatically_exhausted_all_positive_integers": False,
            "global_chart_atlas_closed": False,
            "global_cross_chart_lyapunov_derived": False,
            "global_collatz_proof": False,
            "potential_signal": (
                "yes: repeat and switch behavior has a low-complexity exact "
                "2-adic grammar; no: closure or global descent is not yet known"
            ),
        },
    )


def main(argv: list[str] | None = None) -> None:
    """Write the exact affine-ghost atlas artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verification-power",
        type=int,
        default=DEFAULT_VERIFICATION_POWER,
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = affine_ghost_atlas_report(
        verification_power=args.verification_power,
        input_path=args.input,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.to_json() + "\n", encoding="utf-8")
    LOGGER.info(
        "wrote %s (status=%s; membership_checks=%d; repeat_runs=%d)",
        args.output,
        report.status,
        report.finite_verification["word_membership_checks"],
        report.finite_verification["maximal_repeat_runs_checked"],
    )


if __name__ == "__main__":
    main()
