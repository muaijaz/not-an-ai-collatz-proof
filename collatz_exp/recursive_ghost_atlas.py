"""Exact recursive grammars beyond the first affine Collatz ghost atlas.

The predecessor :mod:`collatz_exp.affine_ghost_atlas` proves that an
expanding accelerated valuation word ``W`` has a positive affine coordinate

``L_W(n) = (3^M - 2^A)*n + B``

whose 2-adic valuation counts the remaining exact copies of ``W``.  This
module resolves the next chart-selection layer without using an orbit
stress test.

At an exhausted ``W`` state write ``L_W(n)=2^e*z`` with ``z`` odd and
``1 <= e <= A``.  The *source-relative first-free rule* follows all next
valuations that are forced by ``e`` and stops after the first valuation
whose extra depth depends on ``z``.  It gives a deterministic exit word
once the source chart has been chosen.  Every such exit is valuation
resonant:

``v2(B_V*D_W - D_V*B_W) = e``.

The four expanding children left open by the predecessor artifact have 18
first-free residual templates.  A parametric subgrammar inside them is

``J_m=(1^m) -> K_m=(1^(m-1),2) -> J_(m+1)``, for every ``m >= 2``.

Every finite prefix has a nonempty exact positive cylinder and increasing
chart-boundary values.  The nested prefixes determine one explicit
2-adic integer, but it is not known whether that 2-adic point is an
ordinary positive integer.  Consequently this module does not prove the
Collatz conjecture or construct a divergent positive orbit.

Chart parsing is not intrinsic.  The shortest-divergence parser closes on
seven states from ``(1,1,1,3)``, while the identity

``J_m || K_m = K_(2m)`` (valuation-word concatenation)

exhibits the same valuations as an infinite self-similar macro family.
Both layers are recorded so that finite parser closure is not mistaken for
a global Lyapunov certificate.
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

from .affine_ghost_atlas import (
    AffineGhostChart,
    W112,
    exact_word_residue,
    expanding_ghost_chart,
    word_is_exact,
)
from .core import affine_from_word, apply_word, v2, valuation_word


LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("docs/reports/pecm_affine_ghost_atlas.json")
DEFAULT_INPUT_SHA256 = (
    "93fad5a48ad639d6ea7a778a2cea0976e569d226155edad71e64c89c22660eaf"
)
DEFAULT_OUTPUT_PATH = Path("docs/reports/pecm_recursive_ghost_atlas.json")
DEFAULT_VERIFICATION_M_MAX = 32
DEFAULT_PREFIX_ROUNDS = 5

W12 = (1, 2)
J3 = (1, 1, 1)
J4 = (1, 1, 1, 1)
W1112 = (1, 1, 1, 2)
W1113 = (1, 1, 1, 3)
SEED_WORDS = (W12, J4, W1112, W1113)


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


def _signed_v2(value: int) -> int:
    if value == 0:
        raise ValueError("the 2-adic valuation of zero is infinite")
    return v2(abs(value))


def _word_text(word: Iterable[int]) -> str:
    return "(" + ",".join(str(value) for value in word) + ")"


@dataclass(frozen=True)
class FirstFreeExitTemplate:
    """The first source-relative exit valuation that depends on the odd lift."""

    source_word: tuple[int, ...]
    source_M: int
    source_A: int
    source_B: int
    source_D: int
    residual_depth: int
    fixed_prefix: tuple[int, ...]
    free_offset: int
    q_coefficient: int
    q_constant: int
    expanding_q: tuple[int, ...]
    first_contracting_q: int

    @property
    def target_M(self) -> int:
        return len(self.fixed_prefix) + 1

    @property
    def fixed_valuation_total(self) -> int:
        return sum(self.fixed_prefix) + self.free_offset

    def exit_word(self, q: int) -> tuple[int, ...]:
        if q < 1:
            raise ValueError("q must be positive")
        return self.fixed_prefix + (self.free_offset + q,)

    def q_formula(self) -> str:
        sign = "+" if self.q_constant >= 0 else "-"
        return (
            f"q = v2({self.q_coefficient}*z {sign} "
            f"{abs(self.q_constant)})"
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.source_word),
            "source_affine": {
                "M": self.source_M,
                "A": self.source_A,
                "B": str(self.source_B),
                "D": str(self.source_D),
                "linear_form": f"{self.source_D}*n + {self.source_B}",
            },
            "normal_form": (
                f"{self.source_D}*n + {self.source_B} = "
                f"2^{self.residual_depth}*z, z odd"
            ),
            "residual_depth": self.residual_depth,
            "fixed_prefix": list(self.fixed_prefix),
            "free_valuation": {
                "offset": self.free_offset,
                "q_minimum": 1,
                "formula": self.q_formula(),
                "coefficient": str(self.q_coefficient),
                "constant": str(self.q_constant),
            },
            "fixed_valuation_total_before_q": self.fixed_valuation_total,
            "target_total_valuation": (
                f"{self.residual_depth} + q"
            ),
            "target_step_count": self.target_M,
            "expanding_q": list(self.expanding_q),
            "first_contracting_q": self.first_contracting_q,
        }


@dataclass(frozen=True)
class PostSourceCopyLift:
    """A positive CRT lift with one exact source-chart predecessor."""

    source_word: tuple[int, ...]
    two_adic_residue: int
    two_adic_modulus: int
    source_landing_n: int
    source_predecessor_n: int
    source_mod3_residue: int
    source_mod3_modulus: int
    combined_modulus: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.source_word),
            "required_two_adic_class": {
                "residue": str(self.two_adic_residue),
                "modulus": str(self.two_adic_modulus),
            },
            "inherited_source_condition": (
                "for L_W(landing)=2^e*z, z is divisible by 3^M_W"
            ),
            "required_landing_mod_3_power": {
                "residue": str(self.source_mod3_residue),
                "modulus": str(self.source_mod3_modulus),
            },
            "positive_composed_subcylinder": {
                "landing_residue": str(self.source_landing_n),
                "modulus": str(self.combined_modulus),
                "parameterization": (
                    f"n = {self.source_landing_n} + "
                    f"{self.combined_modulus}*t, t >= 0"
                ),
            },
            "positive_source_predecessor": str(self.source_predecessor_n),
            "source_word_exact_at_predecessor": True,
            "source_word_lands_at_composed_residue": True,
        }


@dataclass(frozen=True)
class FirstFreeExitBranch:
    """One exact ``q`` branch of a first-free template."""

    template: FirstFreeExitTemplate
    q: int
    target_word: tuple[int, ...]
    target_M: int
    target_A: int
    target_B: int
    target_D: int
    target_residue: int
    target_modulus: int
    target_linear_at_residue: int
    target_linear_v2_at_residue: int | None
    gap_G: int
    gap_v2: int
    classification: str
    target_ghost: Fraction | None
    contracting_non_descent_count: int | None
    contracting_first_non_descent: int | None
    contracting_last_non_descent: int | None
    post_source_copy_lift: PostSourceCopyLift

    @property
    def is_expanding(self) -> bool:
        return self.target_D > 0

    @property
    def is_resonant(self) -> bool:
        return self.gap_v2 == self.template.residual_depth

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.template.source_word),
            "residual_depth": self.template.residual_depth,
            "q": self.q,
            "target_word": list(self.target_word),
            "target_affine": {
                "M": self.target_M,
                "A": self.target_A,
                "B": str(self.target_B),
                "D": str(self.target_D),
                "slope": _fraction_json(
                    Fraction(3**self.target_M, 1 << self.target_A)
                ),
                "ghost": (
                    None
                    if self.target_ghost is None
                    else _fraction_json(self.target_ghost)
                ),
            },
            "exact_two_adic_source_cylinder": {
                "residue": str(self.target_residue),
                "modulus": str(self.target_modulus),
                "parameterization": (
                    f"n = {self.target_residue} + "
                    f"{self.target_modulus}*t, t >= 0"
                ),
            },
            "target_linear_at_representative": str(
                self.target_linear_at_residue
            ),
            "target_linear_v2_at_representative": (
                "infinity"
                if self.target_linear_v2_at_residue is None
                else self.target_linear_v2_at_residue
            ),
            "gap_G": str(self.gap_G),
            "gap_v2": self.gap_v2,
            "resonant_at_source_residual": self.is_resonant,
            "classification": self.classification,
            "contracting_non_descent": {
                "count": self.contracting_non_descent_count,
                "first_source": (
                    None
                    if self.contracting_first_non_descent is None
                    else str(self.contracting_first_non_descent)
                ),
                "last_source": (
                    None
                    if self.contracting_last_non_descent is None
                    else str(self.contracting_last_non_descent)
                ),
            },
            "post_source_copy_reachability": (
                self.post_source_copy_lift.to_json_dict()
            ),
            "composed_source_copy_is_last_possible": True,
        }


@dataclass(frozen=True)
class FirstFreeExitStage:
    """The exact first-free exit at one exhausted positive source."""

    source_n: int
    source_word: tuple[int, ...]
    source_linear_value: int
    residual_depth: int
    odd_z: int
    q: int
    branch: FirstFreeExitBranch
    landing_n: int
    outcome: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_n": str(self.source_n),
            "source_word": list(self.source_word),
            "source_linear_value": str(self.source_linear_value),
            "residual_depth": self.residual_depth,
            "odd_z": str(self.odd_z),
            "q": self.q,
            "exit_word": list(self.branch.target_word),
            "landing_n": str(self.landing_n),
            "outcome": self.outcome,
            "branch": self.branch.to_json_dict(),
        }


@dataclass(frozen=True)
class ShortestParserEdge:
    """One expanding edge in the parametric shortest-divergence parser."""

    source_m: int
    source_a: int
    residual_depth: int
    q: int | None
    kind: str
    target_m: int
    target_a: int
    gap_G: int
    gap_v2: int

    @property
    def source_word(self) -> tuple[int, ...]:
        return p_word(self.source_m, self.source_a)

    @property
    def target_word(self) -> tuple[int, ...]:
        return p_word(self.target_m, self.target_a)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source": {
                "m": self.source_m,
                "a": self.source_a,
                "word": list(self.source_word),
            },
            "residual_depth": self.residual_depth,
            "q": self.q,
            "kind": self.kind,
            "target": {
                "m": self.target_m,
                "a": self.target_a,
                "word": list(self.target_word),
            },
            "gap_G": str(self.gap_G),
            "gap_v2": self.gap_v2,
            "resonant": self.gap_v2 == self.residual_depth,
        }


@dataclass(frozen=True)
class ParametricLadderEdge:
    """One of the two exact edge families in the ``J_m/K_m`` ladder."""

    m: int
    direction: str
    source_word: tuple[int, ...]
    target_word: tuple[int, ...]
    residual_depth: int
    q: int
    gap_G: int
    gap_v2: int
    gap_formula: str
    target_residue: int
    target_modulus: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "m": self.m,
            "direction": self.direction,
            "source_word": list(self.source_word),
            "target_word": list(self.target_word),
            "residual_depth": self.residual_depth,
            "q": self.q,
            "gap_G": str(self.gap_G),
            "gap_v2": self.gap_v2,
            "gap_formula": self.gap_formula,
            "resonant": self.gap_v2 == self.residual_depth,
            "target_exact_cylinder": {
                "residue": str(self.target_residue),
                "modulus": str(self.target_modulus),
            },
        }


@dataclass(frozen=True)
class ResonanceDepthWitness:
    """One exact cylinder with a prescribed target ghost-coordinate depth."""

    source_word: tuple[int, ...]
    target_word: tuple[int, ...]
    residual_depth: int
    requested_target_depth: int
    source_n: int
    modulus: int
    source_linear_v2: int
    target_linear_v2: int
    target_repeat_count: int
    gap_G: int
    gap_v2: int
    post_source_copy_lift: PostSourceCopyLift

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_word": list(self.source_word),
            "target_word": list(self.target_word),
            "source_residual_depth": self.residual_depth,
            "requested_target_depth": self.requested_target_depth,
            "exact_cylinder": {
                "residue": str(self.source_n),
                "modulus": str(self.modulus),
                "parameterization": (
                    f"n = {self.source_n} + {self.modulus}*t, t >= 0"
                ),
            },
            "source_linear_v2": self.source_linear_v2,
            "target_linear_v2": self.target_linear_v2,
            "target_maximal_repeat_count": self.target_repeat_count,
            "gap_G": str(self.gap_G),
            "gap_v2": self.gap_v2,
            "source_is_exhausted": True,
            "target_word_is_exact": True,
            "post_source_copy_reachability": (
                self.post_source_copy_lift.to_json_dict()
            ),
            "composed_source_copy_is_last_possible": True,
        }


@dataclass(frozen=True)
class LadderPrefixCertificate:
    """One exact positive cylinder for a finite ladder prefix."""

    start_m: int
    rounds: int
    blocks: tuple[tuple[int, ...], ...]
    word: tuple[int, ...]
    M: int
    A: int
    B: int
    D: int
    residue: int
    modulus: int
    boundary_values: tuple[int, ...]
    maximal_blocks_certified: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "start_m": self.start_m,
            "rounds": self.rounds,
            "paired_identity": (
                "valuation-word concatenation J_m || K_m equals K_(2m)"
            ),
            "blocks": [list(block) for block in self.blocks],
            "concatenated_word": list(self.word),
            "affine": {
                "M": self.M,
                "A": self.A,
                "B": str(self.B),
                "D": str(self.D),
                "expanding": self.D > 0,
            },
            "exact_cylinder": {
                "residue": str(self.residue),
                "modulus": str(self.modulus),
                "parameterization": (
                    f"n = {self.residue} + {self.modulus}*t, t >= 0"
                ),
            },
            "representative_boundary_values": [
                str(value) for value in self.boundary_values
            ],
            "strictly_increasing_at_chart_boundaries": all(
                right > left
                for left, right in zip(
                    self.boundary_values,
                    self.boundary_values[1:],
                )
            ),
            "block_count": len(self.blocks),
            "maximal_blocks_certified_by_a_successor": (
                self.maximal_blocks_certified
            ),
            "final_block_post_exit_is_unconstrained": True,
            "every_accelerated_step_is_increasing_claim": False,
        }


@dataclass(frozen=True)
class RecursiveGhostAtlasReport:
    """Machine-readable recursive atlas and parametric ladder report."""

    type: str
    status: str
    provenance: dict[str, Any]
    selection_rules: dict[str, Any]
    universal_induced_resonance: dict[str, Any]
    seed_exit_grammar: dict[str, Any]
    shortest_parser: dict[str, Any]
    parametric_ladder: dict[str, Any]
    infinite_boundary: dict[str, Any]
    finite_verification: dict[str, Any]
    frontier: dict[str, Any]
    max_plus: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "provenance": dict(self.provenance),
            "selection_rules": dict(self.selection_rules),
            "universal_induced_resonance": dict(
                self.universal_induced_resonance
            ),
            "seed_exit_grammar": dict(self.seed_exit_grammar),
            "shortest_parser": dict(self.shortest_parser),
            "parametric_ladder": dict(self.parametric_ladder),
            "infinite_boundary": dict(self.infinite_boundary),
            "finite_verification": dict(self.finite_verification),
            "frontier": dict(self.frontier),
            "max_plus": dict(self.max_plus),
            "proof": dict(self.proof),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def derive_first_free_exit_template(
    source_word: Iterable[int],
    residual_depth: int,
) -> FirstFreeExitTemplate:
    """Derive the first lift-dependent valuation after an exhausted chart.

    With ``D*n+B=2^e*z``, maintain the exact symbolic current value

    ``x = (p*z+c)/D``.

    If the two terms in ``3*x+1`` have unequal 2-adic orders, the next
    valuation is forced.  Equality is the first point where the odd lift
    ``z`` supplies an extra valuation ``q >= 1``.
    """

    values = _word_tuple(source_word)
    chart = expanding_ghost_chart(values)
    if not 1 <= residual_depth <= chart.A:
        raise ValueError("residual_depth must lie in the source chart range")

    p = 1 << residual_depth
    c = -chart.B
    fixed_prefix: list[int] = []
    max_symbolic_steps = 4 * (chart.M + chart.A + 1)

    for _ in range(max_symbolic_steps):
        numerator_p = 3 * p
        numerator_c = 3 * c + chart.D
        p_depth = v2(numerator_p)
        c_depth = (
            None if numerator_c == 0 else v2(abs(numerator_c))
        )

        if c_depth is not None and p_depth == c_depth:
            coefficient = numerator_p >> p_depth
            constant = numerator_c // (1 << p_depth)
            if coefficient % 2 == 0 or constant % 2 == 0:
                raise AssertionError("first-free q form is not odd plus odd")
            fixed_total = sum(fixed_prefix) + p_depth
            if fixed_total != residual_depth:
                raise AssertionError(
                    "first-free valuation total does not equal the residual"
                )
            target_M = len(fixed_prefix) + 1
            expanding_q: list[int] = []
            q = 1
            while 3**target_M > 1 << (residual_depth + q):
                expanding_q.append(q)
                q += 1
            return FirstFreeExitTemplate(
                source_word=values,
                source_M=chart.M,
                source_A=chart.A,
                source_B=chart.B,
                source_D=chart.D,
                residual_depth=residual_depth,
                fixed_prefix=tuple(fixed_prefix),
                free_offset=p_depth,
                q_coefficient=coefficient,
                q_constant=constant,
                expanding_q=tuple(expanding_q),
                first_contracting_q=q,
            )

        if c_depth is None:
            forced = p_depth
        else:
            forced = min(p_depth, c_depth)
        if forced < 1:
            raise AssertionError("a symbolic accelerated valuation was not positive")
        fixed_prefix.append(forced)
        p = numerator_p >> forced
        c = numerator_c // (1 << forced)

    raise RuntimeError("first-free valuation was not reached symbolically")


def post_source_copy_lift(
    source_word: Iterable[int],
    two_adic_residue: int,
    two_adic_modulus: int,
) -> PostSourceCopyLift:
    """Compose a binary branch cylinder with an exact source predecessor.

    A landing ``n=T_W(y)`` must satisfy

    ``2^A*n = B (mod 3^M)``.

    This odd-modulus condition is independent of the supplied binary
    cylinder, so CRT gives a positive subcylinder.  Equivalently, after a
    source copy the normalized exhausted coordinate has the inherited factor
    ``3^M``.
    """

    source = expanding_ghost_chart(_word_tuple(source_word))
    if (
        two_adic_modulus < 2
        or two_adic_modulus & (two_adic_modulus - 1)
    ):
        raise ValueError("two_adic_modulus must be a positive power of two")
    residue = two_adic_residue % two_adic_modulus
    if residue % 2 == 0:
        raise ValueError("two_adic_residue must be odd")

    mod3 = 3**source.M
    landing_mod3 = (
        source.B * pow(1 << source.A, -1, mod3)
    ) % mod3
    lift_parameter = (
        (landing_mod3 - residue)
        * pow(two_adic_modulus, -1, mod3)
    ) % mod3
    combined_modulus = two_adic_modulus * mod3
    landing = residue + two_adic_modulus * lift_parameter
    while (1 << source.A) * landing <= source.B:
        landing += combined_modulus
    predecessor = (
        (1 << source.A) * landing - source.B
    ) // mod3

    if predecessor <= 0 or predecessor % 2 == 0:
        raise AssertionError("CRT source predecessor is not positive odd")
    if valuation_word(predecessor, source.M) != source.word:
        raise AssertionError("CRT predecessor does not realize the source word")
    if apply_word(predecessor, source.word) != landing:
        raise AssertionError("CRT predecessor misses the branch landing")
    if landing % two_adic_modulus != residue:
        raise AssertionError("CRT landing left the binary branch")
    if landing % mod3 != landing_mod3:
        raise AssertionError("CRT landing misses the source inverse class")

    return PostSourceCopyLift(
        source_word=source.word,
        two_adic_residue=residue,
        two_adic_modulus=two_adic_modulus,
        source_landing_n=landing,
        source_predecessor_n=predecessor,
        source_mod3_residue=landing_mod3,
        source_mod3_modulus=mod3,
        combined_modulus=combined_modulus,
    )


def instantiate_first_free_branch(
    template: FirstFreeExitTemplate,
    q: int,
) -> FirstFreeExitBranch:
    """Instantiate and exactly certify one ``q`` cylinder."""

    if q < 1:
        raise ValueError("q must be positive")
    target_word = template.exit_word(q)
    target_affine = affine_from_word(target_word)
    target_D = 3**target_affine.m - (1 << target_affine.A)
    if target_affine.A != template.residual_depth + q:
        raise AssertionError("first-free target valuation total changed")
    target_residue, target_modulus = exact_word_residue(target_word)

    source_linear = (
        template.source_D * target_residue + template.source_B
    )
    if v2(source_linear) != template.residual_depth:
        raise AssertionError("target cylinder is not in the source residual class")
    z = source_linear >> template.residual_depth
    q_value = (
        template.q_coefficient * z + template.q_constant
    )
    if q_value == 0 or _signed_v2(q_value) != q:
        raise AssertionError("target cylinder does not realize the requested q")
    if valuation_word(target_residue, target_affine.m) != target_word:
        raise AssertionError("exact target residue failed orbit replay")

    target_linear = target_D * target_residue + target_affine.B
    target_linear_depth = (
        None if target_linear == 0 else v2(abs(target_linear))
    )
    if (
        target_linear_depth is not None
        and target_linear_depth < target_affine.A + 1
    ):
        raise AssertionError("target exactness depth is too small")

    gap = (
        target_affine.B * template.source_D
        - target_D * template.source_B
    )
    if gap == 0:
        raise AssertionError("an induced first-free gap cannot vanish")
    gap_depth = v2(abs(gap))
    if gap_depth != template.residual_depth:
        raise AssertionError("the induced first-free edge is not resonant")
    source_lift = post_source_copy_lift(
        template.source_word,
        target_residue,
        target_modulus,
    )
    lifted_source_linear = (
        template.source_D * source_lift.source_landing_n
        + template.source_B
    )
    if v2(lifted_source_linear) != template.residual_depth:
        raise AssertionError("post-source CRT lift changed the source residual")
    lifted_z = lifted_source_linear >> template.residual_depth
    if lifted_z % (3**template.source_M) != 0:
        raise AssertionError("post-source CRT lift lost 3-adic inheritance")

    target_ghost: Fraction | None = None
    non_descent_count: int | None = None
    first_non_descent: int | None = None
    last_non_descent: int | None = None
    if target_D > 0:
        classification = "expanding_chart"
        target_ghost = Fraction(-target_affine.B, target_D)
    else:
        contraction_gap = -target_D
        non_descent_threshold = target_affine.B // contraction_gap
        if target_residue > non_descent_threshold:
            non_descent_count = 0
            classification = "contracting_all_positive_sources_descend"
        else:
            non_descent_count = (
                (non_descent_threshold - target_residue) // target_modulus
            ) + 1
            first_non_descent = target_residue
            last_non_descent = (
                target_residue
                + (non_descent_count - 1) * target_modulus
            )
            equality = (
                contraction_gap * last_non_descent == target_affine.B
            )
            if non_descent_count == 1 and equality and last_non_descent == 1:
                classification = "contracting_terminal_equality_at_one"
            else:
                classification = "contracting_with_finite_small_exceptions"

    return FirstFreeExitBranch(
        template=template,
        q=q,
        target_word=target_word,
        target_M=target_affine.m,
        target_A=target_affine.A,
        target_B=target_affine.B,
        target_D=target_D,
        target_residue=target_residue,
        target_modulus=target_modulus,
        target_linear_at_residue=target_linear,
        target_linear_v2_at_residue=target_linear_depth,
        gap_G=gap,
        gap_v2=gap_depth,
        classification=classification,
        target_ghost=target_ghost,
        contracting_non_descent_count=non_descent_count,
        contracting_first_non_descent=first_non_descent,
        contracting_last_non_descent=last_non_descent,
        post_source_copy_lift=source_lift,
    )


def first_free_exit_stage(
    source_word: Iterable[int],
    source_n: int,
) -> FirstFreeExitStage:
    """Classify one exhausted source state by the first-free rule."""

    values = _word_tuple(source_word)
    chart = expanding_ghost_chart(values)
    if source_n <= 0 or source_n % 2 == 0:
        raise ValueError("source_n must be a positive odd integer")
    source_linear = chart.D * source_n + chart.B
    residual = v2(source_linear)
    if not 1 <= residual <= chart.A:
        raise ValueError("source_n is not exhausted for the source chart")
    z = source_linear >> residual
    template = derive_first_free_exit_template(values, residual)
    q_expression = template.q_coefficient * z + template.q_constant
    if q_expression == 0:
        raise ValueError("the first-free valuation is infinite")
    q = _signed_v2(q_expression)
    branch = instantiate_first_free_branch(template, q)
    if source_n % branch.target_modulus != branch.target_residue:
        raise AssertionError("stage source is outside its exact branch cylinder")
    landing = apply_word(source_n, branch.target_word)
    if branch.is_expanding:
        if landing <= source_n:
            raise AssertionError("an expanding branch failed to increase")
        outcome = "switch_to_expanding_chart"
    elif landing < source_n:
        outcome = "descent_below_exhausted_source"
    elif landing == source_n:
        if source_n != 1:
            raise AssertionError("unexpected nonterminal Collatz equality")
        outcome = "terminal_equality"
    else:
        outcome = "contracting_small_source_increase"
    return FirstFreeExitStage(
        source_n=source_n,
        source_word=values,
        source_linear_value=source_linear,
        residual_depth=residual,
        odd_z=z,
        q=q,
        branch=branch,
        landing_n=landing,
        outcome=outcome,
    )


def first_free_expanding_edges(
    source_word: Iterable[int],
) -> tuple[FirstFreeExitBranch, ...]:
    """Return every expanding first-free branch of one source chart."""

    values = _word_tuple(source_word)
    chart = expanding_ghost_chart(values)
    branches: list[FirstFreeExitBranch] = []
    for residual in range(1, chart.A + 1):
        template = derive_first_free_exit_template(values, residual)
        branches.extend(
            instantiate_first_free_branch(template, q)
            for q in template.expanding_q
        )
    if any(not branch.is_expanding for branch in branches):
        raise AssertionError("expanding edge enumeration retained a contraction")
    return tuple(branches)


def resonance_depth_witness(
    source_word: Iterable[int],
    target_word: Iterable[int],
    residual_depth: int,
    target_depth: int,
) -> ResonanceDepthWitness:
    """Construct an exact positive lift with any requested target depth.

    This is a pure congruence theorem for an already known legal resonant
    edge.  Solving ``L_V(n)=2^S (mod 2^(S+1))`` fixes the target depth to
    ``S``.  If ``v2(G_(V,W))=e<S``, the integer gap identity then forces
    the source depth to remain exactly ``e``.
    """

    source = expanding_ghost_chart(_word_tuple(source_word))
    target = expanding_ghost_chart(_word_tuple(target_word))
    if not 1 <= residual_depth <= source.A:
        raise ValueError("residual_depth is outside the source chart")
    if target_depth < target.A + 1:
        raise ValueError("target_depth is too small for target exactness")

    gap = target.B * source.D - target.D * source.B
    if gap == 0 or v2(abs(gap)) != residual_depth:
        raise ValueError("the supplied charts do not have the requested resonance")
    modulus = 1 << (target_depth + 1)
    residue = (
        ((1 << target_depth) - target.B)
        * pow(target.D, -1, modulus)
    ) % modulus
    if residue <= 0 or residue % 2 == 0:
        raise AssertionError("target-depth residue is not positive odd")

    source_linear_depth = v2(source.D * residue + source.B)
    target_linear_depth = v2(target.D * residue + target.B)
    if source_linear_depth != residual_depth:
        raise AssertionError("resonant witness changed the source residual")
    if target_linear_depth != target_depth:
        raise AssertionError("resonant witness missed the requested target depth")
    if not word_is_exact(target.word, residue):
        raise AssertionError("resonant witness is not in the target cylinder")
    if word_is_exact(source.word, residue):
        raise AssertionError("resonant witness did not exhaust the source chart")
    source_lift = post_source_copy_lift(
        source.word,
        residue,
        modulus,
    )
    lifted_source_depth = v2(
        source.D * source_lift.source_landing_n + source.B
    )
    lifted_target_depth = v2(
        target.D * source_lift.source_landing_n + target.B
    )
    if (
        lifted_source_depth != residual_depth
        or lifted_target_depth != target_depth
    ):
        raise AssertionError("CRT composition changed a resonance depth")

    return ResonanceDepthWitness(
        source_word=source.word,
        target_word=target.word,
        residual_depth=residual_depth,
        requested_target_depth=target_depth,
        source_n=residue,
        modulus=modulus,
        source_linear_v2=source_linear_depth,
        target_linear_v2=target_linear_depth,
        target_repeat_count=(target_depth - 1) // target.A,
        gap_G=gap,
        gap_v2=v2(abs(gap)),
        post_source_copy_lift=source_lift,
    )


def p_word(m: int, a: int) -> tuple[int, ...]:
    """Return ``P_(m,a)=(1^(m-1),a)``."""

    if m < 1:
        raise ValueError("m must be positive")
    if a < 1:
        raise ValueError("a must be positive")
    return (1,) * (m - 1) + (a,)


def p_expanding_a_max(m: int) -> int:
    """Return the largest ``a`` for which ``P_(m,a)`` is expanding."""

    if m < 1:
        raise ValueError("m must be positive")
    return (3**m).bit_length() - m


def p_chart_coefficients(m: int, a: int) -> tuple[int, int, int]:
    """Return ``(A,B,D)`` for the parametric ``P_(m,a)`` family."""

    values = p_word(m, a)
    affine = affine_from_word(values)
    expected_A = m - 1 + a
    expected_B = 3**m - 2**m
    D = 3**m - (1 << expected_A)
    if affine.A != expected_A or affine.B != expected_B:
        raise AssertionError("parametric P chart formula failed")
    return expected_A, expected_B, D


def _shortest_parser_branch(
    source_m: int,
    source_a: int,
    residual_depth: int,
    *,
    q: int | None,
) -> ShortestParserEdge | None:
    source_A, source_B, source_D = p_chart_coefficients(source_m, source_a)
    if source_D <= 0:
        raise ValueError("shortest parser source must be expanding")
    if not 1 <= residual_depth <= source_A:
        raise ValueError("residual_depth is outside the source chart")

    if residual_depth <= source_m - 1:
        if q is None or q < 1:
            raise ValueError("a positive q is required on a downward free exit")
        target_m = residual_depth
        target_a = 1 + q
        kind = "downward_first_free"
    elif residual_depth < source_A:
        if q is not None:
            raise ValueError("q is not used on a forced same-row exit")
        target_m = source_m
        target_a = residual_depth - (source_m - 1)
        kind = "forced_same_row"
    else:
        if q is None or q < 1:
            raise ValueError("a positive q is required on the terminal free exit")
        target_m = source_m
        target_a = source_a + q
        kind = "terminal_same_row_first_free"

    _, target_B, target_D = p_chart_coefficients(target_m, target_a)
    if target_D <= 0:
        return None
    gap = target_B * source_D - target_D * source_B
    if gap == 0:
        raise AssertionError("shortest parser edge has zero gap")
    gap_depth = v2(abs(gap))
    if gap_depth != residual_depth:
        raise AssertionError("shortest parser edge is not resonant")
    return ShortestParserEdge(
        source_m=source_m,
        source_a=source_a,
        residual_depth=residual_depth,
        q=q,
        kind=kind,
        target_m=target_m,
        target_a=target_a,
        gap_G=gap,
        gap_v2=gap_depth,
    )


def shortest_parser_expanding_edges(
    m: int,
    a: int,
) -> tuple[ShortestParserEdge, ...]:
    """Enumerate the exact expanding shortest-divergence exits of ``P_(m,a)``."""

    source_A, _, source_D = p_chart_coefficients(m, a)
    if source_D <= 0:
        raise ValueError("shortest parser source must be expanding")
    edges: list[ShortestParserEdge] = []
    for residual in range(1, source_A + 1):
        if residual <= m - 1:
            q_max = p_expanding_a_max(residual) - 1
            for q in range(1, q_max + 1):
                edge = _shortest_parser_branch(
                    m,
                    a,
                    residual,
                    q=q,
                )
                if edge is not None:
                    edges.append(edge)
        elif residual < source_A:
            edge = _shortest_parser_branch(
                m,
                a,
                residual,
                q=None,
            )
            if edge is not None:
                edges.append(edge)
        else:
            q_max = p_expanding_a_max(m) - a
            for q in range(1, q_max + 1):
                edge = _shortest_parser_branch(
                    m,
                    a,
                    residual,
                    q=q,
                )
                if edge is not None:
                    edges.append(edge)
    return tuple(edges)


def shortest_parser_component(
    start_m: int = 4,
    start_a: int = 3,
) -> tuple[tuple[tuple[int, int], ...], tuple[ShortestParserEdge, ...]]:
    """Close the finite expanding parser component from one ``P`` chart."""

    _, _, start_D = p_chart_coefficients(start_m, start_a)
    if start_D <= 0:
        raise ValueError("parser start must be expanding")
    pending = [(start_m, start_a)]
    nodes: set[tuple[int, int]] = set()
    edges: dict[
        tuple[int, int, int, int | None, int, int],
        ShortestParserEdge,
    ] = {}
    while pending:
        node = pending.pop()
        if node in nodes:
            continue
        nodes.add(node)
        for edge in shortest_parser_expanding_edges(*node):
            key = (
                edge.source_m,
                edge.source_a,
                edge.residual_depth,
                edge.q,
                edge.target_m,
                edge.target_a,
            )
            edges[key] = edge
            target = (edge.target_m, edge.target_a)
            if target not in nodes:
                pending.append(target)
    return (
        tuple(sorted(nodes)),
        tuple(edges[key] for key in sorted(edges)),
    )


def mersenne_chart(m: int) -> AffineGhostChart:
    """Return ``J_m=(1^m)``."""

    if m < 2:
        raise ValueError("the ladder uses m at least two")
    return expanding_ghost_chart((1,) * m)


def one_two_chart(m: int) -> AffineGhostChart:
    """Return ``K_m=(1^(m-1),2)``."""

    if m < 2:
        raise ValueError("the ladder uses m at least two")
    return expanding_ghost_chart((1,) * (m - 1) + (2,))


def resonant_ladder_edges(m: int) -> tuple[ParametricLadderEdge, ...]:
    """Return the exact ``J_m -> K_m -> J_(m+1)`` edge pair."""

    j = mersenne_chart(m)
    k = one_two_chart(m)
    j_next = mersenne_chart(m + 1)
    c_m = 3**m - 2**m
    c_next = 3 ** (m + 1) - 2 ** (m + 1)

    gap_jk = k.B * j.D - k.D * j.B
    gap_kj = j_next.B * k.D - j_next.D * k.B
    if gap_jk != c_m * (1 << m):
        raise AssertionError("J_m-to-K_m gap formula failed")
    if gap_kj != -c_next * (1 << m):
        raise AssertionError("K_m-to-J_(m+1) gap formula failed")

    k_residue, k_modulus = exact_word_residue(k.word)
    j_residue, j_modulus = exact_word_residue(j_next.word)
    edges = (
        ParametricLadderEdge(
            m=m,
            direction="J_m_to_K_m",
            source_word=j.word,
            target_word=k.word,
            residual_depth=m,
            q=1,
            gap_G=gap_jk,
            gap_v2=v2(abs(gap_jk)),
            gap_formula="(3^m - 2^m)*2^m",
            target_residue=k_residue,
            target_modulus=k_modulus,
        ),
        ParametricLadderEdge(
            m=m,
            direction="K_m_to_J_m_plus_1",
            source_word=k.word,
            target_word=j_next.word,
            residual_depth=m,
            q=1,
            gap_G=gap_kj,
            gap_v2=v2(abs(gap_kj)),
            gap_formula="-(3^(m+1) - 2^(m+1))*2^m",
            target_residue=j_residue,
            target_modulus=j_modulus,
        ),
    )
    for edge in edges:
        if edge.gap_v2 != m:
            raise AssertionError("parametric ladder edge is not resonant")
        source = expanding_ghost_chart(edge.source_word)
        source_linear = source.D * edge.target_residue + source.B
        if v2(source_linear) != m:
            raise AssertionError("ladder target cylinder has wrong source residual")
    return edges


def ladder_prefix_blocks(
    start_m: int,
    rounds: int,
) -> tuple[tuple[int, ...], ...]:
    """Return ``J_m,K_m`` pairs for ``m=start_m,...,start_m+rounds-1``."""

    if start_m < 2:
        raise ValueError("start_m must be at least two")
    if rounds < 1:
        raise ValueError("rounds must be positive")
    blocks: list[tuple[int, ...]] = []
    for m in range(start_m, start_m + rounds):
        blocks.append(mersenne_chart(m).word)
        blocks.append(one_two_chart(m).word)
    return tuple(blocks)


def ladder_prefix_word(start_m: int, rounds: int) -> tuple[int, ...]:
    """Return the concatenated exact valuation word of a finite ladder prefix."""

    return tuple(
        value
        for block in ladder_prefix_blocks(start_m, rounds)
        for value in block
    )


def ladder_partial_theta_residue(
    start_m: int,
    rounds: int,
) -> tuple[int, int]:
    """Evaluate the infinite boundary series at finite exact precision.

    After ``rounds`` paired blocks the total valuation is

    ``A_r = r*(2*m0+r)``.

    Terms after ``m=m0+r`` vanish modulo ``2^(A_r+1)``.  The retained
    rational terms have odd denominators and can therefore be evaluated
    exactly in the binary residue ring.
    """

    word = ladder_prefix_word(start_m, rounds)
    affine = affine_from_word(word)
    expected_M = rounds * (2 * start_m + rounds - 1)
    expected_A = rounds * (2 * start_m + rounds)
    if affine.m != expected_M or affine.A != expected_A:
        raise AssertionError("paired ladder cumulative exponents changed")
    modulus = 1 << (affine.A + 1)
    residue = (-1) % modulus
    for m in range(start_m + 1, start_m + rounds + 1):
        numerator_power = m * m - start_m * start_m - 1
        denominator_power = (
            m * (m - 1) - start_m * (start_m - 1)
        )
        term = (
            (1 << numerator_power)
            * pow(3**denominator_power, -1, modulus)
        )
        residue = (residue - term) % modulus
    exact_residue, exact_modulus = exact_word_residue(word)
    if modulus != exact_modulus or residue != exact_residue:
        raise AssertionError(
            "partial-theta truncation disagrees with the exact prefix cylinder"
        )
    return residue, modulus


def ladder_prefix_certificate(
    start_m: int,
    rounds: int,
) -> LadderPrefixCertificate:
    """Certify one finite, macro-increasing source-relative ladder path."""

    blocks = ladder_prefix_blocks(start_m, rounds)
    word = tuple(value for block in blocks for value in block)
    affine = affine_from_word(word)
    D = 3**affine.m - (1 << affine.A)
    if D <= 0:
        raise AssertionError("a ladder prefix composite is not expanding")
    residue, modulus = exact_word_residue(word)
    theta_residue, theta_modulus = ladder_partial_theta_residue(
        start_m,
        rounds,
    )
    if (theta_residue, theta_modulus) != (residue, modulus):
        raise AssertionError("ladder boundary representations disagree")
    x = residue
    boundaries = [x]

    for index, block in enumerate(blocks):
        if valuation_word(x, len(block)) != block:
            raise AssertionError("ladder block is not exact at its boundary")
        x_next = apply_word(x, block)
        if x_next <= x:
            raise AssertionError("ladder block boundary failed to increase")
        boundaries.append(x_next)

        if index + 1 < len(blocks):
            source_chart = expanding_ghost_chart(block)
            source_linear = source_chart.D * x_next + source_chart.B
            source_residual = v2(source_linear)
            pair_offset = index // 2
            expected_residual = start_m + pair_offset
            if source_residual != expected_residual:
                raise AssertionError("ladder source residual changed")
            if word_is_exact(block, x_next):
                raise AssertionError("ladder block was not one-copy maximal")
        x = x_next

    return LadderPrefixCertificate(
        start_m=start_m,
        rounds=rounds,
        blocks=blocks,
        word=word,
        M=affine.m,
        A=affine.A,
        B=affine.B,
        D=D,
        residue=residue,
        modulus=modulus,
        boundary_values=tuple(boundaries),
        maximal_blocks_certified=len(blocks) - 1,
    )


def _validate_input_artifact(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "json_parsed": False,
        "type_matches": False,
        "w112_exit_partition_complete": False,
        "chart_selection_left_open": False,
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
        payload.get("type") == "pecm_exact_affine_ghost_repeat_atlas"
    )
    partition = payload.get("w112_exit_partition")
    result["w112_exit_partition_complete"] = bool(
        isinstance(partition, dict)
        and partition.get("status") == "exact_complete_residual_partition"
        and partition.get("remaining_expanding_target_charts")
        == [list(word) for word in SEED_WORDS]
    )
    frontier = payload.get("frontier")
    result["chart_selection_left_open"] = bool(
        isinstance(frontier, dict)
        and frontier.get("induced_chart_selection_rule_complete") is False
        and frontier.get("all_expanding_exit_charts_recursively_closed") is False
    )
    proof = payload.get("proof")
    result["global_proof_disclaimed"] = bool(
        isinstance(proof, dict)
        and proof.get("global_chart_atlas_closed") is False
        and proof.get("global_collatz_proof") is False
    )
    required = (
        "type_matches",
        "w112_exit_partition_complete",
        "chart_selection_left_open",
        "global_proof_disclaimed",
    )
    result["fully_verified"] = all(result[key] is True for key in required)
    if not result["fully_verified"]:
        result["errors"].append(
            "artifact content does not certify the prior open recursive frontier"
        )
    return result


def _formula_verification(
    *,
    verification_m_max: int,
    prefix_rounds: int,
) -> dict[str, Any]:
    if verification_m_max < 8:
        raise ValueError("verification_m_max must be at least eight")
    if prefix_rounds < 2:
        raise ValueError("prefix_rounds must be at least two")

    digest = hashlib.sha256()
    template_count = 0
    branch_count = 0
    unbounded_depth_witness_count = 0
    for source_word in SEED_WORDS:
        chart = expanding_ghost_chart(source_word)
        for residual in range(1, chart.A + 1):
            template = derive_first_free_exit_template(source_word, residual)
            template_count += 1
            q_limit = template.first_contracting_q + 1
            for q in range(1, q_limit + 1):
                branch = instantiate_first_free_branch(template, q)
                branch_count += 1
                digest.update(
                    (
                        f"template:{source_word}:{residual}:{q}:"
                        f"{branch.target_word}:{branch.gap_G}\n"
                    ).encode()
                )
        for branch in first_free_expanding_edges(source_word):
            requested_depth = branch.target_A * 3 + 1
            witness = resonance_depth_witness(
                source_word,
                branch.target_word,
                branch.template.residual_depth,
                requested_depth,
            )
            if witness.target_repeat_count != 3:
                raise AssertionError("unbounded-depth witness repeat count changed")
            unbounded_depth_witness_count += 1
            digest.update(
                (
                    f"depth:{source_word}:{branch.target_word}:"
                    f"{requested_depth}:{witness.source_n}\n"
                ).encode()
            )

    ladder_edge_count = 0
    renormalization_count = 0
    for m in range(2, verification_m_max + 1):
        edges = resonant_ladder_edges(m)
        ladder_edge_count += len(edges)
        for edge in edges:
            digest.update(
                (
                    f"ladder:{m}:{edge.direction}:{edge.gap_G}:"
                    f"{edge.target_residue}\n"
                ).encode()
            )
        for a in range(1, p_expanding_a_max(m) + 1):
            for repeats in (1, 2, 3):
                left = p_word(m, 1) * repeats + p_word(m, a)
                right = p_word((repeats + 1) * m, a)
                if left != right:
                    raise AssertionError("P-family renormalization failed")
                left_affine = affine_from_word(left)
                right_affine = affine_from_word(right)
                if left_affine != right_affine:
                    raise AssertionError("renormalized affine maps differ")
                renormalization_count += 1

    prefix_certificates = tuple(
        ladder_prefix_certificate(4, rounds)
        for rounds in range(1, prefix_rounds + 1)
    )
    seeded_prefix_lifts = tuple(
        post_source_copy_lift(
            W112,
            certificate.residue,
            certificate.modulus,
        )
        for certificate in prefix_certificates
    )
    w112_chart = expanding_ghost_chart(W112)
    for certificate, lift in zip(prefix_certificates, seeded_prefix_lifts):
        landing_linear = (
            w112_chart.D * lift.source_landing_n + w112_chart.B
        )
        if v2(landing_linear) != 3:
            raise AssertionError("seeded ladder landing has wrong W112 residual")
        seed_stage = first_free_exit_stage(W112, lift.source_landing_n)
        if seed_stage.q != 1 or seed_stage.branch.target_word != J4:
            raise AssertionError("seeded ladder misses the W112-to-J4 edge")
        if valuation_word(
            lift.source_landing_n,
            certificate.M,
        ) != certificate.word:
            raise AssertionError("seeded landing misses its ladder prefix")
    for previous, current in zip(
        prefix_certificates,
        prefix_certificates[1:],
    ):
        if current.residue % previous.modulus != previous.residue:
            raise AssertionError("ladder prefix cylinders are not nested")
    for certificate, lift in zip(prefix_certificates, seeded_prefix_lifts):
        digest.update(
            (
                f"prefix:{certificate.rounds}:{certificate.residue}:"
                f"{certificate.modulus}:{certificate.boundary_values[-1]}:"
                f"{lift.source_predecessor_n}:{lift.source_landing_n}\n"
            ).encode()
        )

    parser_nodes, parser_edges = shortest_parser_component()
    if parser_nodes != (
        (2, 1),
        (2, 2),
        (3, 1),
        (3, 2),
        (4, 1),
        (4, 2),
        (4, 3),
    ):
        raise AssertionError("shortest parser component changed")
    if any(edge.gap_v2 != edge.residual_depth for edge in parser_edges):
        raise AssertionError("shortest parser contains a nonresonant edge")

    return {
        "role": "bounded_exact_formula_regression_not_orbit_stress_test",
        "seed_template_count": template_count,
        "seed_q_branches_checked": branch_count,
        "seed_branch_post_source_compositions_checked": branch_count,
        "unbounded_depth_witnesses_checked": unbounded_depth_witness_count,
        "ladder_m_range": [2, verification_m_max],
        "ladder_edges_checked": ladder_edge_count,
        "renormalization_identities_checked": renormalization_count,
        "prefix_rounds_checked": prefix_rounds,
        "partial_theta_prefix_residues_checked": prefix_rounds,
        "seeded_ladder_prefix_compositions_checked": prefix_rounds,
        "shortest_parser_node_count": len(parser_nodes),
        "shortest_parser_edge_count": len(parser_edges),
        "digest_sha256": digest.hexdigest(),
        "passed": True,
    }


def recursive_ghost_atlas_report(
    *,
    input_path: Path = DEFAULT_INPUT_PATH,
    verification_m_max: int = DEFAULT_VERIFICATION_M_MAX,
    prefix_rounds: int = DEFAULT_PREFIX_ROUNDS,
) -> RecursiveGhostAtlasReport:
    """Build the recursive first-free, parser, and ladder report."""

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

    seed_templates = tuple(
        derive_first_free_exit_template(source_word, residual)
        for source_word in SEED_WORDS
        for residual in range(
            1,
            expanding_ghost_chart(source_word).A + 1,
        )
    )
    seed_edges = tuple(
        branch
        for source_word in SEED_WORDS
        for branch in first_free_expanding_edges(source_word)
    )
    seed_link_template = derive_first_free_exit_template(W112, 3)
    seed_link = instantiate_first_free_branch(seed_link_template, 1)
    if seed_link.target_word != J4:
        raise AssertionError("W112 no longer links to the J/K ladder")
    depth_witnesses = tuple(
        resonance_depth_witness(
            J4,
            W1112,
            4,
            target_depth,
        )
        for target_depth in (6, 11, 16)
    )

    parser_nodes, parser_edges = shortest_parser_component()
    ladder_samples = tuple(
        edge
        for m in range(2, 9)
        for edge in resonant_ladder_edges(m)
    )
    prefix_certificates = tuple(
        ladder_prefix_certificate(4, rounds)
        for rounds in range(1, prefix_rounds + 1)
    )
    seeded_prefix_lifts = tuple(
        post_source_copy_lift(
            W112,
            certificate.residue,
            certificate.modulus,
        )
        for certificate in prefix_certificates
    )
    w112_chart = expanding_ghost_chart(W112)
    for certificate, lift in zip(prefix_certificates, seeded_prefix_lifts):
        landing_linear = (
            w112_chart.D * lift.source_landing_n + w112_chart.B
        )
        if v2(landing_linear) != 3:
            raise AssertionError("seeded ladder landing has wrong W112 residual")
        seed_stage = first_free_exit_stage(W112, lift.source_landing_n)
        if seed_stage.q != 1 or seed_stage.branch.target_word != J4:
            raise AssertionError("seeded ladder misses the W112-to-J4 edge")
        if valuation_word(
            lift.source_landing_n,
            certificate.M,
        ) != certificate.word:
            raise AssertionError("seeded landing misses its ladder prefix")
    first_pair = prefix_certificates[0]
    expected_first_residue = 3 * (1 << (2 * first_pair.start_m)) - 1
    expected_first_modulus = 1 << (2 * first_pair.start_m + 2)
    if (
        first_pair.residue != expected_first_residue
        or first_pair.modulus != expected_first_modulus
    ):
        raise AssertionError("first ladder pair residue formula failed")
    if v2(first_pair.residue + 1) != 2 * first_pair.start_m:
        raise AssertionError("ladder boundary valuation formula failed")

    finite_verification = _formula_verification(
        verification_m_max=verification_m_max,
        prefix_rounds=prefix_rounds,
    )

    adjacency: dict[str, list[dict[str, Any]]] = {}
    for node in parser_nodes:
        key = f"P_{node[0]},{node[1]}"
        adjacency[key] = [
            {
                "target": f"P_{edge.target_m},{edge.target_a}",
                "residual_depth": edge.residual_depth,
                "q": edge.q,
            }
            for edge in parser_edges
            if (edge.source_m, edge.source_a) == node
        ]

    return RecursiveGhostAtlasReport(
        type="pecm_recursive_affine_ghost_atlas",
        status=(
            "exact_source_relative_exit_grammar_with_finite_parser_and_"
            "infinite_parametric_resonant_ladder"
        ),
        provenance={
            "input_path": str(input_path),
            "expected_sha256": DEFAULT_INPUT_SHA256,
            "actual_sha256": input_sha,
            "artifact_snapshot_match": snapshot_match,
            "artifact_content_validation": validation,
            "canonical_prior_frontier_verified": canonical_provenance,
            "scope_relation": scope_relation,
        },
        selection_rules={
            "source_relative_first_free": {
                "status": "exact_deterministic_after_source_chart_is_chosen",
                "definition": (
                    "follow every valuation forced by the exhausted residual "
                    "e, then include the first valuation offset+q whose extra "
                    "depth q depends on the odd lift z"
                ),
                "fixed_valuation_total_before_q": "e",
                "target_total_valuation": "A_target=e+q",
                "globally_intrinsic_parsing_claim": False,
            },
            "shortest_divergence": {
                "status": "exact_alternative_parser",
                "definition": (
                    "stop at the first expanding P_(m,a) chart that differs "
                    "from the exhausted source chart"
                ),
                "finite_from_W1113": True,
            },
            "normalization_dependence": {
                "identity": (
                    "valuation-word concatenation J_m || K_m equals K_(2m)"
                ),
                "consequence": (
                    "a finite parser and an infinite macro family can encode "
                    "the same valuation itinerary"
                ),
                "dynamical_contradiction": False,
            },
        },
        universal_induced_resonance={
            "status": "exact_theorem",
            "setting": (
                "an exhausted expanding source W with v2(L_W(n))=e and "
                "its source-relative first-free exact target V"
            ),
            "target_total_valuation": "A_V=e+q with q>=1",
            "integer_identity": (
                "G_(V,W)=D_W*L_V(n)-D_V*L_W(n)"
            ),
            "gap_definition": "G_(V,W)=B_V*D_W-D_V*B_W",
            "proof": (
                "target exactness gives v2(L_V)>=A_V+1>e, while "
                "v2(D_V*L_W)=e; therefore G is nonzero and v2(G)=e"
            ),
            "applies_to_contracting_targets_too": True,
            "every_seed_first_free_edge_resonant": all(
                edge.is_resonant for edge in seed_edges
            ),
            "chart_resonance_is_exceptional_claim": False,
            "unbounded_target_depth": {
                "status": "exact_congruence_theorem_on_every_legal_edge",
                "construction": (
                    "for arbitrary S>=A_V+1 solve "
                    "L_V(n)=2^S mod 2^(S+1); the gap identity forces "
                    "v2(L_W(n))=v2(G)=e"
                ),
                "consequence": (
                    "the target repeat count floor((S-1)/A_V) is unbounded"
                ),
                "sample_edge": "J_4_to_K_4",
                "samples": [
                    witness.to_json_dict() for witness in depth_witnesses
                ],
                "uniform_resonance_depth_cap_exists": False,
            },
        },
        seed_exit_grammar={
            "status": "exact_complete_first_free_partition",
            "seed_words": [list(word) for word in SEED_WORDS],
            "residual_template_count": len(seed_templates),
            "templates": [
                template.to_json_dict() for template in seed_templates
            ],
            "expanding_edge_count": len(seed_edges),
            "expanding_edges": [
                edge.to_json_dict() for edge in seed_edges
            ],
            "W112_seed_link": seed_link.to_json_dict(),
            "all_omitted_q_are_contracting": True,
            "contracting_branches_descend_except_terminal_one": True,
        },
        shortest_parser={
            "status": "exact_finite_parametric_parser_component",
            "family": {
                "word": "P_(m,a)=(1^(m-1),a)",
                "A": "m-1+a",
                "B": "3^m-2^m",
                "D": "3^m-2^(m-1+a)",
                "expanding_criterion": (
                    "1 <= a <= floor(m*log2(3))-m+1"
                ),
            },
            "exit_theorem": {
                "e=j<=m-1": "P_(j,1+q), q>=1",
                "e=m-1+k with 1<=k<a": "forced P_(m,k)",
                "e=A": "P_(m,a+q), q>=1",
                "retain": "exactly the expanding targets",
            },
            "nodes": [
                {
                    "m": m,
                    "a": a,
                    "word": list(p_word(m, a)),
                }
                for m, a in parser_nodes
            ],
            "edges": [edge.to_json_dict() for edge in parser_edges],
            "adjacency": adjacency,
            "node_count": len(parser_nodes),
            "edge_count": len(parser_edges),
            "every_edge_resonant": all(
                edge.gap_v2 == edge.residual_depth
                for edge in parser_edges
            ),
            "m_never_increases_inside_this_parser": True,
            "finite_parser_is_global_lyapunov_certificate": False,
            "static_node_weight_cycle_obstruction": {
                "cycle": ["P_2,1", "P_2,2", "P_2,1"],
                "exit_word_slopes": [
                    _fraction_json(Fraction(9, 8)),
                    _fraction_json(Fraction(9, 4)),
                ],
                "cycle_product": _fraction_json(Fraction(81, 32)),
                "result": (
                    "positive static node weights cancel around the cycle, "
                    "so they cannot make both expanding edge factors below one"
                ),
            },
            "reason": (
                "resonant directed cycles and the macro renormalization hide "
                "unbounded cylinder depth and chart complexity"
            ),
        },
        parametric_ladder={
            "status": "exact_source_relative_first_free_subgrammar",
            "families": {
                "J_m": {
                    "word": "(1^m)",
                    "M": "m",
                    "A": "m",
                    "B": "C_m=3^m-2^m",
                    "D": "C_m",
                    "ghost": "-1",
                },
                "K_m": {
                    "word": "(1^(m-1),2)",
                    "M": "m",
                    "A": "m+1",
                    "B": "C_m=3^m-2^m",
                    "D": "E_m=3^m-2^(m+1)",
                    "ghost": "-C_m/E_m",
                },
            },
            "transition_schema": "J_m -> K_m -> J_(m+1), for every m>=2",
            "J_exit": {
                "normal_form": "C_m*(n+1)=2^m*z",
                "q": "v2(3^m*z-C_m)",
                "q_equals_one_target": "K_m",
            },
            "K_exit": {
                "normal_form": "E_m*n+C_m=2^m*z",
                "q": "v2(3^(m+1)*z+E_m-6*C_m)",
                "q_equals_one_target": "J_(m+1)",
            },
            "sample_edges_m_2_through_8": [
                edge.to_json_dict() for edge in ladder_samples
            ],
            "seed_reachability": {
                "source": list(W112),
                "residual_depth": 3,
                "q": 1,
                "target": list(J4),
                "gap_G": str(seed_link.gap_G),
                "gap_v2": seed_link.gap_v2,
                "finite_prefix_compositions": [
                    {
                        "rounds": certificate.rounds,
                        "ladder_prefix_residue": str(certificate.residue),
                        "ladder_prefix_modulus": str(certificate.modulus),
                        "W112_residual_at_landing": 3,
                        "W112_first_free_q": 1,
                        "composition": lift.to_json_dict(),
                    }
                    for certificate, lift in zip(
                        prefix_certificates,
                        seeded_prefix_lifts,
                    )
                ],
            },
            "finite_prefix_certificates": [
                certificate.to_json_dict()
                for certificate in prefix_certificates
            ],
            "arbitrarily_long_finite_positive_paths_derived": True,
            "each_edge_forces_the_next_edge_for_every_lift": False,
            "literal_reachable_chart_labels_unbounded": True,
            "finite_parametric_schema_derived": True,
            "full_recursive_grammar_derived": False,
            "acyclic_escape": (
                "m increases after each two-edge ladder segment"
            ),
        },
        infinite_boundary={
            "status": "explicit_2_adic_point_positive_integer_status_open",
            "infinite_word": (
                "product over m>=m0 of valuation-word concatenations "
                "(J_m || K_m), "
                "equivalently product over m>=m0 of K_(2m)"
            ),
            "partial_theta_formula": (
                "xi_m0 = -1 - (1/2)*sum_(m=m0+1)^infinity "
                "2^(m^2-m0^2) / 3^(m*(m-1)-m0*(m0-1)) in Z_2"
            ),
            "exact_boundary_valuation": "v2(xi_m0+1)=2*m0",
            "paired_prefix_exponents": {
                "after_r_pairs_M": "r*(2*m0+r-1)",
                "after_r_pairs_A": "r*(2*m0+r)",
                "finite_series_check": (
                    "terms m=m0+1,...,m0+r reproduce the exact prefix "
                    "residue modulo 2^(A_r+1)"
                ),
            },
            "proof_of_boundary_valuation": (
                "including the outer 1/2, the first term of xi+1 is "
                "-2^(2*m0)/3^(2*m0); the next valuation is 4*m0+3"
            ),
            "tschakaloff_reduction": {
                "definition": (
                    "T_q(z)=sum_(k>=0) z^k*q^(-k*(k-1)/2)"
                ),
                "q": _fraction_json(Fraction(9, 4)),
                "functional_equation": "T_q(z)=1+z*T_q(z/q)",
                "formula": (
                    "xi_m0=-1-(4/9)^m0*T_(9/4)"
                    "(2*(4/9)^(m0+1))"
                ),
                "master_equivalence": (
                    "rationality of any ladder boundary reduces through the "
                    "functional equation to Q_2-rationality of T_(9/4)(2)"
                ),
                "sufficient_exclusion_target": (
                    "prove T_(9/4)(2) is not rational in Q_2"
                ),
                "irrationality_derived": False,
            },
            "first_pair_cylinder": {
                "general_residue": "3*2^(2*m0)-1",
                "general_modulus": "2^(2*m0+2)",
                "m0": first_pair.start_m,
                "residue": str(first_pair.residue),
                "modulus": str(first_pair.modulus),
                "v2_residue_plus_one": v2(first_pair.residue + 1),
            },
            "positive_integer_realizability": "open",
            "positive_integer_infinite_ladder_realizability_derived": False,
            "if_positive_then": (
                "the chart-boundary values would grow without bound"
            ),
            "divergent_positive_collatz_orbit_constructed": False,
            "next_theorem_target": (
                "prove the explicit 2-adic partial-theta value is not a "
                "nonnegative integer, or control the m-to-infinity escape "
                "with a coercive cylinder-depth-dependent Lyapunov function"
            ),
        },
        finite_verification=finite_verification,
        frontier={
            "source_relative_first_free_selection_rule_complete": True,
            "four_seed_first_free_partitions_complete": True,
            "shortest_parser_component_closed": True,
            "finite_literal_first_free_chart_list_closed": False,
            "finite_parametric_ladder_schema_derived": True,
            "full_recursive_grammar_derived": False,
            "every_legal_parser_edge_resonant": True,
            "resonance_depth_uniformly_bounded": False,
            "node_only_lyapunov_can_contract_every_parser_cycle": False,
            "positive_integer_infinite_ladder_realizability_derived": False,
            "global_chart_lyapunov_derived": False,
            "finite_exceptional_set_derived": False,
            "next_exact_task": (
                "analyze the explicit nested 2-adic ladder boundary and add "
                "the resonance lift/cylinder depth to the symbolic state"
            ),
        },
        max_plus={
            "status": "finite_node_only_cycle_test_is_insufficient",
            "finite_parser_available": True,
            "finite_karp_proves_global_contraction": False,
            "reason": (
                "all parser charts expand, static node weights cancel around "
                "directed cycles, and renormalization exposes escape to "
                "unbounded macro complexity"
            ),
            "required_extension": (
                "an n-dependent, cylinder-depth-dependent, or bundled-exit "
                "weight"
            ),
        },
        proof={
            "claim_kind": (
                "exact_symbolic_grammar_and_parametric_obstruction_with_"
                "bounded_formula_regression"
            ),
            "canonical_input_frontier_link_verified": canonical_provenance,
            "deterministic_source_relative_first_free_rule_derived": True,
            "universal_induced_resonance_theorem_derived": True,
            "all_four_seed_partitions_derived": True,
            "finite_shortest_parser_component_derived": True,
            "parametric_ladder_subgrammar_derived": True,
            "arbitrarily_long_finite_increasing_chart_paths_derived": True,
            "explicit_infinite_2_adic_boundary_derived": True,
            "positive_integer_infinite_path_derived": False,
            "global_recursive_grammar_closed": False,
            "global_cross_chart_lyapunov_derived": False,
            "global_collatz_proof": False,
            "potential_signal": (
                "yes: the obstruction has an exact finite-parser plus "
                "self-similar macro description and an explicit 2-adic "
                "boundary; no: its positive-integer exclusion is still open"
            ),
        },
    )


def main(argv: list[str] | None = None) -> None:
    """Write the recursive affine-ghost atlas artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--verification-m-max",
        type=int,
        default=DEFAULT_VERIFICATION_M_MAX,
    )
    parser.add_argument(
        "--prefix-rounds",
        type=int,
        default=DEFAULT_PREFIX_ROUNDS,
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = recursive_ghost_atlas_report(
        input_path=args.input,
        verification_m_max=args.verification_m_max,
        prefix_rounds=args.prefix_rounds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.to_json() + "\n", encoding="utf-8")
    LOGGER.info(
        "wrote %s (templates=%d; edges=%d; ladder_m_max=%d)",
        args.output,
        report.seed_exit_grammar["residual_template_count"],
        report.seed_exit_grammar["expanding_edge_count"],
        args.verification_m_max,
    )


if __name__ == "__main__":
    main()
