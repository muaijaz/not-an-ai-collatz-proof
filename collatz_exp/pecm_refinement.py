"""Exact refinement maps for mixed 2-adic/3-adic PECM state spaces.

The PECM operator acts on functions of a source state: each source row stores
uniformly weighted target samples.  For a refinement ``fine -> coarse`` this
module distinguishes two notions that are easy to conflate:

``K_f I = I K_c``
    Every fine source row, after its targets are restricted to the coarse
    state space, agrees with its coarse parent row (pointwise intertwining).

``A K_f I = K_c``
    The same identity holds only after averaging over every fine source in a
    coarse fiber (Galerkin/conditional intertwining).

All kernel comparisons below use :class:`fractions.Fraction`; no tolerance or
floating-point spectral estimate is involved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from numbers import Integral
from typing import Any, Iterable, Iterator, Sequence, TypeVar

from .post_exit_map import PostExitState


ValueT = TypeVar("ValueT")
Target = int | None


class RefinementError(ValueError):
    """Raised when two mixed-adic levels do not form a natural refinement."""


class StateOrderError(ValueError):
    """Raised when states do not use the canonical PECM row order."""


@dataclass(frozen=True)
class MixedAdicLevel:
    """A finite PECM state level ``(R, u mod 2^k, u mod 3^ell)``.

    Only odd 2-adic residues occur.  State order is the existing PECM order:
    ``R`` first, then increasing odd 2-adic residue, then increasing 3-adic
    residue.
    """

    mod2_power: int
    mod3_power: int
    R_values: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "R_values", tuple(self.R_values))
        if self.mod2_power < 1:
            raise ValueError("mod2_power must be positive")
        if self.mod3_power < 0:
            raise ValueError("mod3_power must be nonnegative")
        if not self.R_values:
            raise ValueError("R_values must be nonempty")
        if any(R < 2 for R in self.R_values):
            raise ValueError("all R_values must be at least two")
        if len(set(self.R_values)) != len(self.R_values):
            raise ValueError("R_values must not contain duplicates")

    @property
    def residue2_count(self) -> int:
        return 1 << (self.mod2_power - 1)

    @property
    def residue3_count(self) -> int:
        return 3**self.mod3_power

    @property
    def state_count(self) -> int:
        return len(self.R_values) * self.residue2_count * self.residue3_count

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_values": list(self.R_values),
            "state_count": self.state_count,
        }


def decode_state_index(level: MixedAdicLevel, index: int) -> PostExitState:
    """Decode one canonical PECM row index."""

    if index < 0 or index >= level.state_count:
        raise IndexError(f"state index {index} is outside [0, {level.state_count})")
    rows_per_R = level.residue2_count * level.residue3_count
    R_index, remainder = divmod(index, rows_per_R)
    residue2_index, residue3 = divmod(remainder, level.residue3_count)
    return PostExitState(
        R=level.R_values[R_index],
        u_mod2=2 * residue2_index + 1,
        u_mod2_power=level.mod2_power,
        u_mod3=residue3,
        u_mod3_power=level.mod3_power,
    )


def encode_state_index(level: MixedAdicLevel, state: PostExitState) -> int:
    """Encode a state, rejecting noncanonical residues and wrong resolutions."""

    if state.u_mod2_power != level.mod2_power:
        raise ValueError(
            f"state has u_mod2_power={state.u_mod2_power}, expected {level.mod2_power}"
        )
    if state.u_mod3_power != level.mod3_power:
        raise ValueError(
            f"state has u_mod3_power={state.u_mod3_power}, expected {level.mod3_power}"
        )
    if state.R not in level.R_values:
        raise ValueError(f"state R={state.R} is not in R_values")
    modulus2 = 1 << level.mod2_power
    modulus3 = 3**level.mod3_power
    if state.u_mod2 < 0 or state.u_mod2 >= modulus2 or state.u_mod2 % 2 == 0:
        raise ValueError("u_mod2 must be an odd canonical residue")
    if state.u_mod3 < 0 or state.u_mod3 >= modulus3:
        raise ValueError("u_mod3 must be a canonical residue")
    R_index = level.R_values.index(state.R)
    return (
        R_index * level.residue2_count * level.residue3_count
        + (state.u_mod2 // 2) * level.residue3_count
        + state.u_mod3
    )


def iter_canonical_states(level: MixedAdicLevel) -> Iterator[PostExitState]:
    """Yield canonical states without materializing a potentially large tuple."""

    for index in range(level.state_count):
        yield decode_state_index(level, index)


def validate_state_order(
    states: Iterable[PostExitState],
    level: MixedAdicLevel,
) -> None:
    """Require exactly the PECM state set in canonical row order."""

    seen = 0
    for index, state in enumerate(states):
        if index >= level.state_count:
            raise StateOrderError(
                f"state sequence has more than the expected {level.state_count} rows"
            )
        expected = decode_state_index(level, index)
        if state != expected:
            raise StateOrderError(
                f"state order mismatch at row {index}: expected {expected!r}, got {state!r}"
            )
        seen += 1
    if seen != level.state_count:
        raise StateOrderError(
            f"state sequence has {seen} rows, expected {level.state_count}"
        )


def _exact_average(total: Any, denominator: int) -> Any:
    if isinstance(total, Integral):
        return Fraction(int(total), denominator)
    return total / denominator


@dataclass(frozen=True)
class MixedAdicRefinement:
    """The natural child-to-parent map between two PECM residue levels."""

    coarse: MixedAdicLevel
    fine: MixedAdicLevel

    def __post_init__(self) -> None:
        if self.fine.mod2_power < self.coarse.mod2_power:
            raise RefinementError("fine mod2_power must be at least the coarse power")
        if self.fine.mod3_power < self.coarse.mod3_power:
            raise RefinementError("fine mod3_power must be at least the coarse power")
        if self.fine.R_values != self.coarse.R_values:
            raise RefinementError(
                "fine and coarse levels must have identical ordered R_values"
            )

    @property
    def mod2_degree(self) -> int:
        return 1 << (self.fine.mod2_power - self.coarse.mod2_power)

    @property
    def mod3_degree(self) -> int:
        return 3 ** (self.fine.mod3_power - self.coarse.mod3_power)

    @property
    def fiber_size(self) -> int:
        return self.mod2_degree * self.mod3_degree

    def restrict_state(self, fine_state: PostExitState) -> PostExitState:
        """Reduce one fine mixed-adic state to its unique coarse parent."""

        encode_state_index(self.fine, fine_state)
        return PostExitState(
            R=fine_state.R,
            u_mod2=fine_state.u_mod2 % (1 << self.coarse.mod2_power),
            u_mod2_power=self.coarse.mod2_power,
            u_mod3=fine_state.u_mod3 % (3**self.coarse.mod3_power),
            u_mod3_power=self.coarse.mod3_power,
        )

    def restrict_index(self, fine_index: int) -> int:
        """Map a canonical fine row index to its canonical coarse row index."""

        return encode_state_index(
            self.coarse,
            self.restrict_state(decode_state_index(self.fine, fine_index)),
        )

    def parent_indices(self) -> tuple[int, ...]:
        """Return the child-to-parent row map in canonical fine order."""

        return tuple(self.restrict_index(index) for index in range(self.fine.state_count))

    def fiber(self, coarse_index: int) -> tuple[int, ...]:
        """Return all legal fine lifts of one coarse row, in fine row order."""

        coarse_state = decode_state_index(self.coarse, coarse_index)
        modulus2 = 1 << self.coarse.mod2_power
        modulus3 = 3**self.coarse.mod3_power
        children = []
        for digit2 in range(self.mod2_degree):
            residue2 = coarse_state.u_mod2 + digit2 * modulus2
            for digit3 in range(self.mod3_degree):
                residue3 = coarse_state.u_mod3 + digit3 * modulus3
                children.append(
                    encode_state_index(
                        self.fine,
                        PostExitState(
                            R=coarse_state.R,
                            u_mod2=residue2,
                            u_mod2_power=self.fine.mod2_power,
                            u_mod3=residue3,
                            u_mod3_power=self.fine.mod3_power,
                        ),
                    )
                )
        return tuple(children)

    def fibers(self) -> tuple[tuple[int, ...], ...]:
        """Enumerate every coarse fiber."""

        return tuple(self.fiber(index) for index in range(self.coarse.state_count))

    def validate_coarse_state_order(self, states: Iterable[PostExitState]) -> None:
        validate_state_order(states, self.coarse)

    def validate_fine_state_order(self, states: Iterable[PostExitState]) -> None:
        validate_state_order(states, self.fine)

    def prolong(self, coarse_values: Sequence[ValueT]) -> tuple[ValueT, ...]:
        """Pull a coarse function back to the fine state space (``I``)."""

        if len(coarse_values) != self.coarse.state_count:
            raise ValueError(
                f"coarse vector has length {len(coarse_values)}, "
                f"expected {self.coarse.state_count}"
            )
        return tuple(coarse_values[parent] for parent in self.parent_indices())

    def conditional_average(self, fine_values: Sequence[Any]) -> tuple[Any, ...]:
        """Average a fine function over each complete legal fiber (``A``)."""

        if len(fine_values) != self.fine.state_count:
            raise ValueError(
                f"fine vector has length {len(fine_values)}, "
                f"expected {self.fine.state_count}"
            )
        averages = []
        for children in self.fibers():
            first, *rest = children
            total = fine_values[first]
            for child in rest:
                total = total + fine_values[child]
            averages.append(_exact_average(total, self.fiber_size))
        return tuple(averages)


@dataclass(frozen=True)
class UniformTargetOperator:
    """A finite kernel represented by equally weighted target samples.

    Rows are source states and entries are target state indices. ``None`` is a
    cemetery/descent target whose function value is fixed to zero.
    """

    rows: tuple[tuple[Target, ...], ...]
    label: str = "uniform_target_operator"

    def __post_init__(self) -> None:
        normalized = tuple(tuple(row) for row in self.rows)
        object.__setattr__(self, "rows", normalized)
        if not normalized:
            raise ValueError("operator must contain at least one source row")
        sample_count = len(normalized[0])
        if sample_count < 1:
            raise ValueError("operator rows must contain at least one sample")
        if any(len(row) != sample_count for row in normalized):
            raise ValueError("all operator rows must have the same sample count")
        state_count = len(normalized)
        for source, row in enumerate(normalized):
            for target in row:
                if target is not None and (
                    not isinstance(target, int) or target < 0 or target >= state_count
                ):
                    raise ValueError(
                        f"invalid target {target!r} in source row {source}; "
                        f"expected None or an index in [0, {state_count})"
                    )

    @classmethod
    def from_target_array(
        cls,
        targets: Iterable[Iterable[Any]],
        *,
        cemetery: int = -1,
        label: str = "sampled_target_array",
    ) -> UniformTargetOperator:
        """Normalize a PECM-style target array, including NumPy arrays."""

        rows = []
        for row in targets:
            normalized_row = []
            for target in row:
                value = int(target)
                normalized_row.append(None if value == cemetery else value)
            rows.append(tuple(normalized_row))
        return cls(rows=tuple(rows), label=label)

    @property
    def state_count(self) -> int:
        return len(self.rows)

    @property
    def sample_count(self) -> int:
        return len(self.rows[0])

    def row_distribution(
        self,
        source: int,
    ) -> tuple[tuple[Target, Fraction], ...]:
        """Return one exact row distribution in deterministic target order."""

        if source < 0 or source >= self.state_count:
            raise IndexError(f"source row {source} is outside [0, {self.state_count})")
        distribution = _row_distribution(self.rows[source])
        return tuple(
            (target, distribution[target])
            for target in sorted(
                distribution,
                key=lambda item: (-1 if item is None else item),
            )
        )

    def apply(self, values: Sequence[Any]) -> tuple[Any, ...]:
        """Apply the kernel to a function, using value zero at the cemetery."""

        if len(values) != self.state_count:
            raise ValueError(
                f"vector has length {len(values)}, expected {self.state_count}"
            )
        image = []
        for row in self.rows:
            live_targets = [target for target in row if target is not None]
            if live_targets:
                total = values[live_targets[0]]
                for target in live_targets[1:]:
                    total = total + values[target]
            else:
                total = 0
            image.append(_exact_average(total, self.sample_count))
        return tuple(image)

    def to_target_rows(self, *, cemetery: int = -1) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(cemetery if target is None else target for target in row)
            for row in self.rows
        )

    def to_json_dict(
        self,
        *,
        include_rows: bool = False,
        cemetery: int = -1,
    ) -> dict[str, Any]:
        """Serialize stable kernel metadata and, optionally, target rows."""

        cemetery_samples = sum(
            target is None for row in self.rows for target in row
        )
        data: dict[str, Any] = {
            "type": "uniform_target_operator",
            "label": self.label,
            "state_count": self.state_count,
            "sample_count": self.sample_count,
            "cemetery_sample_count": cemetery_samples,
            "live_sample_count": self.state_count * self.sample_count
            - cemetery_samples,
        }
        if include_rows:
            data["cemetery_sentinel"] = cemetery
            data["rows"] = [list(row) for row in self.to_target_rows(cemetery=cemetery)]
        return data


def galerkin_coarsen(
    refinement: MixedAdicRefinement,
    fine_operator: UniformTargetOperator,
    *,
    label: str | None = None,
) -> UniformTargetOperator:
    """Construct the exact coarse kernel ``A K_f I``.

    Each coarse row concatenates the target samples from every fine source in
    its fiber and restricts those targets to coarse parents.  Consequently the
    returned uniform row denominator is
    ``fine_operator.sample_count * refinement.fiber_size``.
    """

    if fine_operator.state_count != refinement.fine.state_count:
        raise ValueError(
            f"fine operator has {fine_operator.state_count} rows, "
            f"expected {refinement.fine.state_count}"
        )
    coarse_rows = []
    for children in refinement.fibers():
        row: list[Target] = []
        for fine_source in children:
            for fine_target in fine_operator.rows[fine_source]:
                row.append(
                    None
                    if fine_target is None
                    else refinement.restrict_index(fine_target)
                )
        coarse_rows.append(tuple(row))
    return UniformTargetOperator(
        rows=tuple(coarse_rows),
        label=label or f"galerkin({fine_operator.label})",
    )


def _row_distribution(row: Sequence[Target]) -> dict[Target, Fraction]:
    denominator = len(row)
    counts: dict[Target, int] = {}
    for target in row:
        counts[target] = counts.get(target, 0) + 1
    return {
        target: Fraction(count, denominator)
        for target, count in counts.items()
    }


def _total_variation(
    left: dict[Target, Fraction],
    right: dict[Target, Fraction],
) -> Fraction:
    targets = left.keys() | right.keys()
    return sum(
        (abs(left.get(target, Fraction()) - right.get(target, Fraction())) for target in targets),
        start=Fraction(),
    ) / 2


def _row_l1(
    left: dict[Target, Fraction],
    right: dict[Target, Fraction],
    *,
    include_cemetery: bool,
) -> Fraction:
    targets = left.keys() | right.keys()
    if not include_cemetery:
        targets = targets - {None}
    return sum(
        (abs(left.get(target, Fraction()) - right.get(target, Fraction())) for target in targets),
        start=Fraction(),
    )


def _fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class OperatorIntertwiningDiagnostic:
    """Exact adjacent-level defects for pointwise and Galerkin identities."""

    coarse_level: MixedAdicLevel
    fine_level: MixedAdicLevel
    coarse_operator_label: str
    fine_operator_label: str
    coarse_sample_count: int
    fine_sample_count: int
    fiber_size: int
    pointwise_compatible: bool
    galerkin_compatible: bool
    full_projective_identity_exact: bool
    galerkin_identity_exact: bool
    pointwise_mismatched_fine_rows: int
    galerkin_mismatched_coarse_rows: int
    pointwise_max_total_variation: Fraction
    galerkin_max_total_variation: Fraction
    pointwise_max_live_row_l1: Fraction
    pointwise_max_augmented_row_l1: Fraction
    galerkin_max_live_row_l1: Fraction
    galerkin_max_augmented_row_l1: Fraction
    pointwise_max_cemetery_mass_defect: Fraction
    galerkin_max_cemetery_mass_defect: Fraction
    worst_fine_row: int | None
    worst_coarse_row: int | None
    status: str
    interpretation: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["coarse_level"] = self.coarse_level.to_json_dict()
        data["fine_level"] = self.fine_level.to_json_dict()
        data["pointwise_max_total_variation"] = _fraction_json(
            self.pointwise_max_total_variation
        )
        data["galerkin_max_total_variation"] = _fraction_json(
            self.galerkin_max_total_variation
        )
        data["pointwise_max_live_row_l1"] = _fraction_json(
            self.pointwise_max_live_row_l1
        )
        data["pointwise_max_augmented_row_l1"] = _fraction_json(
            self.pointwise_max_augmented_row_l1
        )
        data["galerkin_max_live_row_l1"] = _fraction_json(
            self.galerkin_max_live_row_l1
        )
        data["galerkin_max_augmented_row_l1"] = _fraction_json(
            self.galerkin_max_augmented_row_l1
        )
        data["pointwise_max_cemetery_mass_defect"] = _fraction_json(
            self.pointwise_max_cemetery_mass_defect
        )
        data["galerkin_max_cemetery_mass_defect"] = _fraction_json(
            self.galerkin_max_cemetery_mass_defect
        )
        return data


@dataclass(frozen=True)
class ConditionalExpectationIntertwiningDiagnostic:
    """Exact defect in the full identity ``A K_f = K_c A``.

    Unlike the coarse-observable identity ``A K_f I = K_c``, this compares the
    two operators on every fine observable.  It therefore detects nonuniform
    target mass inside a coarse fiber even when the Galerkin identity holds.
    """

    coarse_level: MixedAdicLevel
    fine_level: MixedAdicLevel
    coarse_operator_label: str
    fine_operator_label: str
    exact: bool
    mismatched_coarse_rows: int
    max_live_row_l1: Fraction
    max_augmented_row_l1: Fraction
    max_cemetery_mass_defect: Fraction
    worst_coarse_row: int | None
    status: str
    interpretation: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["coarse_level"] = self.coarse_level.to_json_dict()
        data["fine_level"] = self.fine_level.to_json_dict()
        data["max_live_row_l1"] = _fraction_json(self.max_live_row_l1)
        data["max_augmented_row_l1"] = _fraction_json(
            self.max_augmented_row_l1
        )
        data["max_cemetery_mass_defect"] = _fraction_json(
            self.max_cemetery_mass_defect
        )
        return data


def diagnose_conditional_expectation_intertwining(
    refinement: MixedAdicRefinement,
    coarse_operator: UniformTargetOperator,
    fine_operator: UniformTargetOperator,
) -> ConditionalExpectationIntertwiningDiagnostic:
    """Measure ``A K_f - K_c A`` as an exact row-L1 operator defect.

    The left row averages fine transition rows over a source fiber.  The right
    row first follows the coarse kernel and then averages uniformly over the
    target fiber.  Cemetery mass is retained as an explicit target.
    """

    if coarse_operator.state_count != refinement.coarse.state_count:
        raise ValueError(
            f"coarse operator has {coarse_operator.state_count} rows, "
            f"expected {refinement.coarse.state_count}"
        )
    if fine_operator.state_count != refinement.fine.state_count:
        raise ValueError(
            f"fine operator has {fine_operator.state_count} rows, "
            f"expected {refinement.fine.state_count}"
        )

    mismatches = 0
    max_live = Fraction()
    max_augmented = Fraction()
    max_cemetery = Fraction()
    worst_coarse_row: int | None = None
    for coarse_source, source_fiber in enumerate(refinement.fibers()):
        left_row = tuple(
            target
            for fine_source in source_fiber
            for target in fine_operator.rows[fine_source]
        )
        right_targets: list[Target] = []
        for coarse_target in coarse_operator.rows[coarse_source]:
            if coarse_target is None:
                right_targets.extend([None] * refinement.fiber_size)
            else:
                right_targets.extend(refinement.fiber(coarse_target))

        left_distribution = _row_distribution(left_row)
        right_distribution = _row_distribution(right_targets)
        live = _row_l1(
            left_distribution,
            right_distribution,
            include_cemetery=False,
        )
        augmented = _row_l1(
            left_distribution,
            right_distribution,
            include_cemetery=True,
        )
        cemetery = abs(
            left_distribution.get(None, Fraction())
            - right_distribution.get(None, Fraction())
        )
        if augmented:
            mismatches += 1
        if augmented > max_augmented:
            worst_coarse_row = coarse_source
        max_live = max(max_live, live)
        max_augmented = max(max_augmented, augmented)
        max_cemetery = max(max_cemetery, cemetery)

    exact = mismatches == 0
    return ConditionalExpectationIntertwiningDiagnostic(
        coarse_level=refinement.coarse,
        fine_level=refinement.fine,
        coarse_operator_label=coarse_operator.label,
        fine_operator_label=fine_operator.label,
        exact=exact,
        mismatched_coarse_rows=mismatches,
        max_live_row_l1=max_live,
        max_augmented_row_l1=max_augmented,
        max_cemetery_mass_defect=max_cemetery,
        worst_coarse_row=worst_coarse_row,
        status=(
            "exact_conditional_expectation_intertwining"
            if exact
            else "conditional_expectation_intertwining_defect"
        ),
        interpretation=(
            "This is the exact full-observable defect A K_f - K_c A. "
            "It is stronger than the Galerkin identity A K_f I = K_c and "
            "retains cemetery mass explicitly."
        ),
    )


def diagnose_operator_intertwining(
    refinement: MixedAdicRefinement,
    coarse_operator: UniformTargetOperator,
    fine_operator: UniformTargetOperator,
) -> OperatorIntertwiningDiagnostic:
    """Measure exact defects in ``K_f I = I K_c`` and ``A K_f I = K_c``.

    For source-row kernels acting on observables, ``K_f I = I K_c`` is dual to
    the full measure identity ``P K_f* = K_c* P``.  The weaker averaged
    identity ``A K_f I = K_c`` is Galerkin compatibility only.
    """

    if coarse_operator.state_count != refinement.coarse.state_count:
        raise ValueError(
            f"coarse operator has {coarse_operator.state_count} rows, "
            f"expected {refinement.coarse.state_count}"
        )
    if fine_operator.state_count != refinement.fine.state_count:
        raise ValueError(
            f"fine operator has {fine_operator.state_count} rows, "
            f"expected {refinement.fine.state_count}"
        )

    coarse_distributions = tuple(
        _row_distribution(row) for row in coarse_operator.rows
    )
    pointwise_mismatches = 0
    pointwise_max = Fraction()
    pointwise_live_l1_max = Fraction()
    pointwise_augmented_l1_max = Fraction()
    pointwise_cemetery_max = Fraction()
    worst_fine_row: int | None = None
    for fine_source, fine_row in enumerate(fine_operator.rows):
        coarse_source = refinement.restrict_index(fine_source)
        pushed_row = tuple(
            None if target is None else refinement.restrict_index(target)
            for target in fine_row
        )
        pushed_distribution = _row_distribution(pushed_row)
        coarse_distribution = coarse_distributions[coarse_source]
        defect = _total_variation(pushed_distribution, coarse_distribution)
        live_l1 = _row_l1(
            pushed_distribution,
            coarse_distribution,
            include_cemetery=False,
        )
        augmented_l1 = _row_l1(
            pushed_distribution,
            coarse_distribution,
            include_cemetery=True,
        )
        pointwise_live_l1_max = max(pointwise_live_l1_max, live_l1)
        pointwise_augmented_l1_max = max(
            pointwise_augmented_l1_max,
            augmented_l1,
        )
        cemetery_defect = abs(
            pushed_distribution.get(None, Fraction())
            - coarse_distribution.get(None, Fraction())
        )
        pointwise_cemetery_max = max(pointwise_cemetery_max, cemetery_defect)
        if defect:
            pointwise_mismatches += 1
        if defect > pointwise_max:
            pointwise_max = defect
            worst_fine_row = fine_source

    galerkin = galerkin_coarsen(refinement, fine_operator)
    galerkin_mismatches = 0
    galerkin_max = Fraction()
    galerkin_live_l1_max = Fraction()
    galerkin_augmented_l1_max = Fraction()
    galerkin_cemetery_max = Fraction()
    worst_coarse_row: int | None = None
    for coarse_source, galerkin_row in enumerate(galerkin.rows):
        galerkin_distribution = _row_distribution(galerkin_row)
        coarse_distribution = coarse_distributions[coarse_source]
        defect = _total_variation(galerkin_distribution, coarse_distribution)
        live_l1 = _row_l1(
            galerkin_distribution,
            coarse_distribution,
            include_cemetery=False,
        )
        augmented_l1 = _row_l1(
            galerkin_distribution,
            coarse_distribution,
            include_cemetery=True,
        )
        galerkin_live_l1_max = max(galerkin_live_l1_max, live_l1)
        galerkin_augmented_l1_max = max(
            galerkin_augmented_l1_max,
            augmented_l1,
        )
        cemetery_defect = abs(
            galerkin_distribution.get(None, Fraction())
            - coarse_distribution.get(None, Fraction())
        )
        galerkin_cemetery_max = max(
            galerkin_cemetery_max,
            cemetery_defect,
        )
        if defect:
            galerkin_mismatches += 1
        if defect > galerkin_max:
            galerkin_max = defect
            worst_coarse_row = coarse_source

    pointwise_compatible = pointwise_mismatches == 0
    galerkin_compatible = galerkin_mismatches == 0
    if pointwise_compatible:
        status = "exact_pointwise_intertwining"
    elif galerkin_compatible:
        status = "exact_galerkin_intertwining_only"
    else:
        status = "sampled_operators_not_refinement_compatible"
    interpretation = (
        "This compares the supplied finite uniform-sample kernels exactly. "
        "Pointwise compatibility is the observable form K_f I = I K_c, dual "
        "to full projective compatibility on measures. Galerkin "
        "compatibility is only the averaged identity A K_f I = K_c. "
        "Failure records incompatibility of those sampling schemes; it is not "
        "a counterexample to compatibility of the underlying Collatz map or "
        "of a differently constructed projective operator ladder."
    )
    return OperatorIntertwiningDiagnostic(
        coarse_level=refinement.coarse,
        fine_level=refinement.fine,
        coarse_operator_label=coarse_operator.label,
        fine_operator_label=fine_operator.label,
        coarse_sample_count=coarse_operator.sample_count,
        fine_sample_count=fine_operator.sample_count,
        fiber_size=refinement.fiber_size,
        pointwise_compatible=pointwise_compatible,
        galerkin_compatible=galerkin_compatible,
        full_projective_identity_exact=pointwise_compatible,
        galerkin_identity_exact=galerkin_compatible,
        pointwise_mismatched_fine_rows=pointwise_mismatches,
        galerkin_mismatched_coarse_rows=galerkin_mismatches,
        pointwise_max_total_variation=pointwise_max,
        galerkin_max_total_variation=galerkin_max,
        pointwise_max_live_row_l1=pointwise_live_l1_max,
        pointwise_max_augmented_row_l1=pointwise_augmented_l1_max,
        galerkin_max_live_row_l1=galerkin_live_l1_max,
        galerkin_max_augmented_row_l1=galerkin_augmented_l1_max,
        pointwise_max_cemetery_mass_defect=pointwise_cemetery_max,
        galerkin_max_cemetery_mass_defect=galerkin_cemetery_max,
        worst_fine_row=worst_fine_row,
        worst_coarse_row=worst_coarse_row,
        status=status,
        interpretation=interpretation,
    )


def diagnose_galerkin_coarsening(
    refinement: MixedAdicRefinement,
    fine_operator: UniformTargetOperator,
) -> OperatorIntertwiningDiagnostic:
    """Diagnose the exact Galerkin kernel derived from ``fine_operator``.

    The Galerkin defect is zero by construction.  The full projective defect
    is still measured independently and will generally be nonzero.
    """

    coarse_operator = galerkin_coarsen(refinement, fine_operator)
    return diagnose_operator_intertwining(
        refinement,
        coarse_operator,
        fine_operator,
    )


def diagnose_target_array_intertwining(
    refinement: MixedAdicRefinement,
    coarse_targets: Iterable[Iterable[Any]],
    fine_targets: Iterable[Iterable[Any]],
    *,
    cemetery: int = -1,
) -> OperatorIntertwiningDiagnostic:
    """Convenience adapter for existing PECM target arrays."""

    return diagnose_operator_intertwining(
        refinement,
        UniformTargetOperator.from_target_array(
            coarse_targets,
            cemetery=cemetery,
            label="coarse_sampled_target_array",
        ),
        UniformTargetOperator.from_target_array(
            fine_targets,
            cemetery=cemetery,
            label="fine_sampled_target_array",
        ),
    )
