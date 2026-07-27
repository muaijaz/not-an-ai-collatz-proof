"""Exact seeded branch certificates for the post-exit Collatz map.

This module is deliberately narrower than a quotient-wide proof.  A numerical
PECM vector may nominate a cylinder, but every branch assertion made here is
then checked with integer or rational arithmetic.  The selected cylinder is
partitioned deeply enough to fix its target residue; targets outside that
selected source cylinder remain an explicit open frontier.

The module also contains a small exact max-times difference-constraint solver.
It is intended for a future *closed* branch graph.  The pilot report refuses to
run it on the present open frontier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

from .core import accelerated_step, affine_from_word, apply_word, v2
from .cycles import classify_cycle_word
from .post_exit_map import post_exit_landing


LOGGER = logging.getLogger(__name__)

DEFAULT_PROVENANCE_PATH = Path(
    "docs/reports/pecm_cross_resolution_consistency.json"
)
DEFAULT_PROVENANCE_SHA256 = (
    "13f8bd222451582320c5fc7872b5a53846b5755c3f525efa95e310ec41038a05"
)
DEFAULT_PROVENANCE_MAX_RATIO = "1.9956723465910398"
DEFAULT_OUTPUT_PATH = Path(
    "docs/reports/pecm_exact_selected_cylinder_pilot.json"
)


class CylinderBudgetExceeded(RuntimeError):
    """Raised when an exact cylinder partition exceeds its explicit budget."""


@dataclass(frozen=True)
class ExactMixedCylinder:
    """One mixed ``2``-adic/``3``-adic tail cylinder.

    It represents positive odd units ``u`` satisfying the two stored
    congruences, with associated Collatz value ``n = 2^R u - 1``.
    """

    R: int
    u_mod2: int
    mod2_power: int
    u_mod3: int
    mod3_power: int

    def __post_init__(self) -> None:
        if self.R < 2:
            raise ValueError("R must be at least two")
        if self.mod2_power < 1:
            raise ValueError("mod2_power must be positive")
        if self.mod3_power < 0:
            raise ValueError("mod3_power must be nonnegative")
        modulus2 = 1 << self.mod2_power
        modulus3 = 3**self.mod3_power
        if not (0 <= self.u_mod2 < modulus2) or self.u_mod2 % 2 == 0:
            raise ValueError("u_mod2 must be an odd canonical residue")
        if not 0 <= self.u_mod3 < modulus3:
            raise ValueError("u_mod3 must be a canonical residue")

    @property
    def lift_modulus(self) -> int:
        return (1 << self.mod2_power) * (3**self.mod3_power)

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceCheckpoint:
    """One exact accelerated-map checkpoint."""

    accelerated_step_index: int
    phase: str
    valuation: int
    cumulative_A: int
    value: int
    tail_depth: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "accelerated_step_index": self.accelerated_step_index,
            "phase": self.phase,
            "valuation": self.valuation,
            "cumulative_A": self.cumulative_A,
            "value": str(self.value),
            "tail_depth": self.tail_depth,
        }


@dataclass(frozen=True)
class PostExitMacroTrace:
    """Exact first stopping event after a forced Mersenne-tail exit."""

    R: int
    u: int
    n0: int
    post_start: int
    post_word: tuple[int, ...]
    full_word: tuple[int, ...]
    status: str
    landing: int
    landing_tail_depth: int
    checkpoints: tuple[TraceCheckpoint, ...]

    @property
    def post_total_A(self) -> int:
        return sum(self.post_word)

    @property
    def full_total_A(self) -> int:
        return sum(self.full_word)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "R": self.R,
            "u": str(self.u),
            "n0": str(self.n0),
            "post_start": str(self.post_start),
            "post_word": list(self.post_word),
            "full_word": list(self.full_word),
            "post_steps": len(self.post_word),
            "full_steps": len(self.full_word),
            "post_total_A": self.post_total_A,
            "full_total_A": self.full_total_A,
            "status": self.status,
            "landing": str(self.landing),
            "landing_tail_depth": self.landing_tail_depth,
            "checkpoints": [
                checkpoint.to_json_dict() for checkpoint in self.checkpoints
            ],
        }


@dataclass(frozen=True)
class ExactBranch:
    """One exact edge for the rational max-times solver."""

    edge_id: int
    source: int
    target: int
    valuation_word: tuple[int, ...]
    least_n: int
    ratio_upper: Fraction

    def __post_init__(self) -> None:
        if self.edge_id < 0:
            raise ValueError("edge_id must be nonnegative")
        if self.source < 0 or self.target < 0:
            raise ValueError("source and target must be nonnegative")
        if self.least_n < 1 or self.least_n % 2 == 0:
            raise ValueError("least_n must be a positive odd integer")
        if self.ratio_upper <= 0:
            raise ValueError("ratio_upper must be positive")
        if any(value < 1 for value in self.valuation_word):
            raise ValueError("valuation words must contain positive integers")

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "valuation_word": list(self.valuation_word),
            "least_n": str(self.least_n),
            "ratio_upper": _fraction_json(self.ratio_upper),
        }


@dataclass(frozen=True)
class RationalDifferenceCertificate:
    """Exact feasibility result for multiplicative branch inequalities."""

    feasible: bool
    alpha: Fraction
    contraction: Fraction
    potential_powers: tuple[Fraction, ...] | None
    witness_edge_ids: tuple[int, ...]
    witness_gain: Fraction | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "feasible": self.feasible,
            "alpha": _fraction_json(self.alpha),
            "contraction": _fraction_json(self.contraction),
            "potential_powers": (
                None
                if self.potential_powers is None
                else [
                    _fraction_json(value) for value in self.potential_powers
                ]
            ),
            "witness_edge_ids": list(self.witness_edge_ids),
            "witness_gain": (
                None
                if self.witness_gain is None
                else _fraction_json(self.witness_gain)
            ),
        }


@dataclass(frozen=True)
class ExactCylinderPilotReport:
    """Machine-readable exact selected-cylinder report."""

    type: str
    status: str
    provenance: dict[str, Any]
    scope: dict[str, Any]
    root: dict[str, Any]
    edges: tuple[dict[str, Any], ...]
    frontier: dict[str, Any]
    symbolic_candidate: dict[str, Any]
    max_plus: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "provenance": dict(self.provenance),
            "scope": dict(self.scope),
            "root": dict(self.root),
            "edges": [dict(edge) for edge in self.edges],
            "frontier": dict(self.frontier),
            "symbolic_candidate": dict(self.symbolic_candidate),
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


def _comparison_to_one(value: Fraction) -> str:
    if value < 1:
        return "less_than_one"
    if value > 1:
        return "greater_than_one"
    return "equal_to_one"


def exact_word_residue(word: tuple[int, ...]) -> tuple[int, int]:
    """Return the unique exact-word residue modulo ``2^(A+1)``.

    The extra bit is essential.  Divisibility modulo ``2^A`` fixes the
    requested denominator, but not the exact final valuation.
    """

    affine = affine_from_word(word)
    modulus_power = affine.A + 1
    modulus = 1 << modulus_power
    inverse = pow(pow(3, affine.m, modulus), -1, modulus)
    residue = (((1 << affine.A) - affine.B) * inverse) % modulus
    return residue, modulus_power


def post_word_u_residue(R: int, word: tuple[int, ...]) -> tuple[int, int]:
    """Return the exact ``u mod 2^A`` class for one post-exit word."""

    if R < 2:
        raise ValueError("R must be at least two")
    affine = affine_from_word(word)
    exact_x_residue, _ = exact_word_residue(word)
    modulus = 1 << affine.A
    inverse = pow(pow(3, R - 1, modulus), -1, modulus)
    residue = (((exact_x_residue + 1) // 2) * inverse) % modulus
    return residue, affine.A


def least_positive_mixed_representative(
    cylinder: ExactMixedCylinder,
) -> tuple[int, int]:
    """Return the least positive unit and period for a mixed cylinder."""

    modulus2 = 1 << cylinder.mod2_power
    modulus3 = 3**cylinder.mod3_power
    if modulus3 == 1:
        value = cylinder.u_mod2
    else:
        inverse = pow(modulus2, -1, modulus3)
        lift = (
            (cylinder.u_mod3 - cylinder.u_mod2) * inverse
        ) % modulus3
        value = cylinder.u_mod2 + modulus2 * lift
    if value <= 0:
        value += modulus2 * modulus3
    return value, modulus2 * modulus3


def trace_post_exit_macro(
    R: int,
    u: int,
    *,
    max_post_steps: int = 64,
    tail_reentry_min_R: int = 2,
) -> PostExitMacroTrace:
    """Trace the first exact post-exit descent or tail reentry."""

    if R < 2:
        raise ValueError("R must be at least two")
    if u <= 0 or u % 2 == 0:
        raise ValueError("u must be a positive odd integer")
    if max_post_steps < 1:
        raise ValueError("max_post_steps must be positive")
    if tail_reentry_min_R < 1:
        raise ValueError("tail_reentry_min_R must be positive")

    n0 = (1 << R) * u - 1
    x = n0
    word: list[int] = []
    checkpoints: list[TraceCheckpoint] = []
    cumulative_A = 0

    for step in range(1, R):
        x, valuation = accelerated_step(x)
        if valuation != 1:
            raise AssertionError("the forced Mersenne-tail word was not all ones")
        word.append(valuation)
        cumulative_A += valuation
        checkpoints.append(
            TraceCheckpoint(
                accelerated_step_index=step,
                phase="forced_tail",
                valuation=valuation,
                cumulative_A=cumulative_A,
                value=x,
                tail_depth=v2(x + 1),
            )
        )

    expected_post_start = post_exit_landing(R, u)
    if x != expected_post_start:
        raise AssertionError("forced-tail affine identity failed")
    if x < n0:
        return PostExitMacroTrace(
            R=R,
            u=u,
            n0=n0,
            post_start=x,
            post_word=(),
            full_word=tuple(word),
            status="descended_at_post_start",
            landing=x,
            landing_tail_depth=v2(x + 1),
            checkpoints=tuple(checkpoints),
        )

    post_word: list[int] = []
    for post_step in range(1, max_post_steps + 1):
        x, valuation = accelerated_step(x)
        word.append(valuation)
        post_word.append(valuation)
        cumulative_A += valuation
        tail_depth = v2(x + 1)
        checkpoints.append(
            TraceCheckpoint(
                accelerated_step_index=R - 1 + post_step,
                phase="post_exit",
                valuation=valuation,
                cumulative_A=cumulative_A,
                value=x,
                tail_depth=tail_depth,
            )
        )
        if x < n0:
            status = "descended"
            break
        if tail_depth >= tail_reentry_min_R:
            status = "tail_reentry"
            break
    else:
        status = "max_steps_exceeded"

    return PostExitMacroTrace(
        R=R,
        u=u,
        n0=n0,
        post_start=expected_post_start,
        post_word=tuple(post_word),
        full_word=tuple(word),
        status=status,
        landing=x,
        landing_tail_depth=v2(x + 1),
        checkpoints=tuple(checkpoints),
    )


def _branch_gain(
    branch: ExactBranch,
    alpha: Fraction,
    contraction: Fraction,
) -> Fraction:
    p = alpha.numerator
    q = alpha.denominator
    return branch.ratio_upper**p / contraction**q


def solve_rational_difference_constraints(
    state_count: int,
    branches: Sequence[ExactBranch],
    *,
    alpha: Fraction,
    contraction: Fraction,
) -> RationalDifferenceCertificate:
    """Solve exact max-times branch inequalities with Bellman--Ford.

    The returned powers ``P`` satisfy

    ``P[target] >= P[source] * ratio_upper**p / contraction**q``

    for ``alpha = p/q``.  Then

    ``H(n, state) = n**(p/q) * P[state]**(-1/q)``

    contracts by at most ``contraction`` on every supplied branch.
    Feasibility is meaningful only when the caller has supplied a closed,
    exhaustive branch graph.
    """

    if state_count < 1:
        raise ValueError("state_count must be positive")
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    if not 0 < contraction < 1:
        raise ValueError("contraction must lie strictly between zero and one")
    if len({branch.edge_id for branch in branches}) != len(branches):
        raise ValueError("edge_id values must be unique")
    if any(
        branch.source >= state_count or branch.target >= state_count
        for branch in branches
    ):
        raise ValueError("branch endpoint is outside the state range")

    gains = [
        _branch_gain(branch, alpha, contraction) for branch in branches
    ]
    potentials = [Fraction(1, 1) for _ in range(state_count)]
    predecessor: list[int | None] = [None for _ in range(state_count)]
    updated_vertex: int | None = None

    for _ in range(state_count):
        updated_vertex = None
        for edge_index, (branch, gain) in enumerate(zip(branches, gains, strict=True)):
            candidate = potentials[branch.source] * gain
            if candidate > potentials[branch.target]:
                potentials[branch.target] = candidate
                predecessor[branch.target] = edge_index
                updated_vertex = branch.target
        if updated_vertex is None:
            certificate = RationalDifferenceCertificate(
                feasible=True,
                alpha=alpha,
                contraction=contraction,
                potential_powers=tuple(potentials),
                witness_edge_ids=(),
                witness_gain=None,
            )
            if not verify_rational_difference_certificate(
                certificate, state_count, branches
            ):
                raise AssertionError("constructed rational certificate did not verify")
            return certificate

    if updated_vertex is None:
        raise AssertionError("unreachable Bellman--Ford state")
    cycle_vertex = updated_vertex
    for _ in range(state_count):
        edge_index = predecessor[cycle_vertex]
        if edge_index is None:
            raise AssertionError("missing predecessor for an improving cycle")
        cycle_vertex = branches[edge_index].source

    backward_edges: list[int] = []
    current = cycle_vertex
    while True:
        edge_index = predecessor[current]
        if edge_index is None:
            raise AssertionError("broken predecessor cycle")
        backward_edges.append(edge_index)
        current = branches[edge_index].source
        if current == cycle_vertex:
            break
        if len(backward_edges) > state_count:
            raise AssertionError("predecessor witness did not close")

    cycle_edge_indices = tuple(reversed(backward_edges))
    witness_gain = Fraction(1, 1)
    for edge_index in cycle_edge_indices:
        witness_gain *= gains[edge_index]
    if witness_gain <= 1:
        raise AssertionError("improving-cycle witness does not have gain above one")

    certificate = RationalDifferenceCertificate(
        feasible=False,
        alpha=alpha,
        contraction=contraction,
        potential_powers=None,
        witness_edge_ids=tuple(
            branches[index].edge_id for index in cycle_edge_indices
        ),
        witness_gain=witness_gain,
    )
    if not verify_rational_difference_certificate(
        certificate, state_count, branches
    ):
        raise AssertionError("constructed obstruction witness did not verify")
    return certificate


def verify_rational_difference_certificate(
    certificate: RationalDifferenceCertificate,
    state_count: int,
    branches: Sequence[ExactBranch],
) -> bool:
    """Verify a feasible potential or an infeasible exact cycle witness."""

    if state_count < 1 or certificate.alpha <= 0:
        return False
    if not 0 < certificate.contraction < 1:
        return False
    edge_by_id = {branch.edge_id: branch for branch in branches}
    if len(edge_by_id) != len(branches):
        return False
    if any(
        branch.source >= state_count or branch.target >= state_count
        for branch in branches
    ):
        return False

    if certificate.feasible:
        if certificate.potential_powers is None:
            return False
        if certificate.witness_edge_ids or certificate.witness_gain is not None:
            return False
        if len(certificate.potential_powers) != state_count:
            return False
        if any(value <= 0 for value in certificate.potential_powers):
            return False
        for branch in branches:
            gain = _branch_gain(
                branch, certificate.alpha, certificate.contraction
            )
            if (
                certificate.potential_powers[branch.target]
                < certificate.potential_powers[branch.source] * gain
            ):
                return False
        return True

    if certificate.potential_powers is not None:
        return False
    if not certificate.witness_edge_ids or certificate.witness_gain is None:
        return False
    try:
        witness = [
            edge_by_id[edge_id] for edge_id in certificate.witness_edge_ids
        ]
    except KeyError:
        return False
    if any(
        left.target != right.source
        for left, right in zip(witness, witness[1:], strict=False)
    ):
        return False
    if witness[-1].target != witness[0].source:
        return False
    gain = Fraction(1, 1)
    for branch in witness:
        gain *= _branch_gain(
            branch, certificate.alpha, certificate.contraction
        )
    return gain == certificate.witness_gain and gain > 1


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _reported_concrete_branch_ratio(path: Path) -> str | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    for profile in data.get("branch_ratio_oscillation", ()):
        if profile.get("ratio_kind") == "concrete_finest_sample_branch_ratio":
            value = profile.get("max_live_target_ratio")
            return None if value is None else repr(value)
    return None


def _partition_hash(source_residues: Iterable[int]) -> str:
    payload = ",".join(str(value) for value in source_residues).encode()
    return hashlib.sha256(payload).hexdigest()


def _prefix_growth_records(
    trace: PostExitMacroTrace,
) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    first_checked = trace.R - 1
    for prefix_length in range(first_checked, len(trace.full_word) + 1):
        prefix = trace.full_word[:prefix_length]
        affine = affine_from_word(prefix)
        slope = Fraction(3**affine.m, 1 << affine.A)
        survival_upper = None
        if slope < 1:
            survival_upper = affine.B // ((1 << affine.A) - 3**affine.m)
        records.append(
            {
                "prefix_length": prefix_length,
                "A": affine.A,
                "B": str(affine.B),
                "m": affine.m,
                "slope": _fraction_json(slope),
                "slope_comparison_to_one": _comparison_to_one(slope),
                "survival_n_upper_if_contracting": (
                    None if survival_upper is None else str(survival_upper)
                ),
            }
        )
    return tuple(records)


def _choose_consecutive_tail_base(
    worst_size_ratio: Fraction,
    depth_drop: int,
    *,
    max_numerator: int,
) -> tuple[Fraction, Fraction] | None:
    if depth_drop <= 0:
        return None
    chosen: tuple[Fraction, Fraction] | None = None
    for numerator in range(2, max_numerator + 1):
        base = Fraction(numerator, numerator - 1)
        corrected = worst_size_ratio / base**depth_drop
        if corrected < 1:
            chosen = base, corrected
    return chosen


def _default_selection_provenance(
    provenance_path: Path,
) -> dict[str, Any]:
    actual_sha256 = _sha256(provenance_path)
    actual_max_ratio = _reported_concrete_branch_ratio(provenance_path)
    return {
        "selection_kind": (
            "hard_coded_exact_seed_from_prior_replayed_sample_argmax"
        ),
        "sampling_used_for_root_selection": True,
        "sampling_used_for_branch_coverage": False,
        "input_artifact": str(provenance_path),
        "input_artifact_sha256": actual_sha256,
        "expected_input_artifact_sha256": DEFAULT_PROVENANCE_SHA256,
        "input_artifact_snapshot_match": (
            actual_sha256 == DEFAULT_PROVENANCE_SHA256
        ),
        "input_artifact_reported_max_live_target_ratio": actual_max_ratio,
        "expected_reported_max_live_target_ratio": (
            DEFAULT_PROVENANCE_MAX_RATIO
        ),
        "reported_max_ratio_match": (
            actual_max_ratio == DEFAULT_PROVENANCE_MAX_RATIO
        ),
        "artifact_records_argmax_value_but_not_witness": True,
        "witness_provenance_note": (
            "The witness was replayed when the named artifact had the "
            "expected hash and metric above. This command verifies the "
            "snapshot metadata but does not recompute the numerical argmax."
        ),
        "replayed_witness": {
            "source_state_id": 8309,
            "source": {
                "R": 9,
                "u_mod2": 55,
                "mod2_power": 8,
                "u_mod3": 2,
                "mod3_power": 2,
            },
            "sample_u": "4151",
            "sample_n": "2125311",
            "landing": "2872411",
            "target_state_id": 101,
            "target": {
                "R": 2,
                "u_mod2": 23,
                "mod2_power": 8,
                "u_mod3": 2,
                "mod3_power": 2,
            },
        },
    }


def exact_selected_cylinder_pilot_report(
    *,
    root: ExactMixedCylinder = ExactMixedCylinder(9, 55, 11, 2, 2),
    target_mod2_power: int = 8,
    max_post_steps: int = 32,
    max_leaves: int = 4096,
    cusp_search_max_numerator: int = 64,
    provenance_path: str | Path = DEFAULT_PROVENANCE_PATH,
) -> ExactCylinderPilotReport:
    """Build the exact adversarial-cylinder pilot.

    The default root is selected from the worst concrete branch of the current
    finite PECM consistency run.  Selection is sampled; coverage *inside* that
    root is an exact congruence partition.
    """

    if target_mod2_power < 1:
        raise ValueError("target_mod2_power must be positive")
    if max_leaves < 1:
        raise ValueError("max_leaves must be positive")
    if cusp_search_max_numerator < 2:
        raise ValueError("cusp_search_max_numerator must be at least two")

    least_u, root_lift_modulus = least_positive_mixed_representative(root)
    trace = trace_post_exit_macro(
        root.R,
        least_u,
        max_post_steps=max_post_steps,
    )
    if trace.status == "max_steps_exceeded":
        raise ValueError("selected root has an unresolved max-steps frontier")
    if trace.status != "tail_reentry":
        raise ValueError("selected root does not produce a tail-reentry branch")

    post_affine = affine_from_word(trace.post_word)
    full_affine = affine_from_word(trace.full_word)
    target_R = trace.landing_tail_depth
    required_word_power = post_affine.A
    required_event_power = post_affine.A + target_R
    required_target_power = (
        post_affine.A + target_R + target_mod2_power - 1
    )
    if root.mod2_power < required_event_power:
        raise ValueError(
            "root does not fix its reentry event; "
            f"needs mod2_power >= {required_event_power}"
        )

    prefix_records = _prefix_growth_records(trace)
    if any(
        record["slope_comparison_to_one"] == "less_than_one"
        for record in prefix_records
    ):
        raise ValueError(
            "selected root has a magnitude-dependent stopping event; "
            "an infinite congruence cylinder is not uniform"
        )

    refined_power = max(root.mod2_power, required_target_power)
    child_count = 1 << (refined_power - root.mod2_power)
    if child_count > max_leaves:
        raise CylinderBudgetExceeded(
            f"exact partition needs {child_count} leaves, budget is {max_leaves}"
        )

    exact_full_residue, exact_full_power = exact_word_residue(trace.full_word)
    exact_post_u_residue, exact_post_u_power = post_word_u_residue(
        root.R, trace.post_word
    )
    if root.u_mod2 % (1 << exact_post_u_power) != exact_post_u_residue:
        raise AssertionError("root does not lie in the exact post-word cylinder")
    if trace.n0 % (1 << exact_full_power) != exact_full_residue:
        raise AssertionError("least root representative misses exact full word")
    if apply_word(trace.n0, trace.full_word) != trace.landing:
        raise AssertionError("full affine word does not replay the landing")

    expected_source_residues = tuple(
        root.u_mod2 + (index << root.mod2_power)
        for index in range(child_count)
    )
    child_rows: list[dict[str, Any]] = []
    exact_rows: list[
        tuple[
            ExactMixedCylinder,
            int,
            int,
            PostExitMacroTrace,
            ExactMixedCylinder,
            Fraction,
        ]
    ] = []
    seen_targets: set[tuple[int, int]] = set()

    LOGGER.info(
        "partitioning R=%d, u=%d mod 2^%d into %d exact target-fixed leaves",
        root.R,
        root.u_mod2,
        root.mod2_power,
        child_count,
    )
    for child_index, source_residue in enumerate(expected_source_residues):
        source = ExactMixedCylinder(
            R=root.R,
            u_mod2=source_residue,
            mod2_power=refined_power,
            u_mod3=root.u_mod3,
            mod3_power=root.mod3_power,
        )
        child_u, child_lift_modulus = least_positive_mixed_representative(source)
        child_trace = trace_post_exit_macro(
            root.R,
            child_u,
            max_post_steps=max_post_steps,
        )
        if (
            child_trace.status != "tail_reentry"
            or child_trace.full_word != trace.full_word
            or child_trace.landing_tail_depth != target_R
        ):
            raise AssertionError(
                f"child {child_index} does not share the exact root branch"
            )
        if apply_word(child_trace.n0, trace.full_word) != child_trace.landing:
            raise AssertionError(f"child {child_index} failed exact word replay")
        target_u = (child_trace.landing + 1) >> target_R
        target = ExactMixedCylinder(
            R=target_R,
            u_mod2=target_u % (1 << target_mod2_power),
            mod2_power=target_mod2_power,
            u_mod3=target_u % (3**root.mod3_power),
            mod3_power=root.mod3_power,
        )
        ratio_upper = Fraction(child_trace.landing, child_trace.n0)
        exact_rows.append(
            (
                source,
                child_u,
                child_lift_modulus,
                child_trace,
                target,
                ratio_upper,
            )
        )
        seen_targets.add((target.u_mod2, target.u_mod3))

    worst_ratio = max(row[-1] for row in exact_rows)
    worst_row_index = max(
        range(len(exact_rows)),
        key=lambda index: exact_rows[index][-1],
    )
    tail_choice = _choose_consecutive_tail_base(
        worst_ratio,
        root.R - target_R,
        max_numerator=cusp_search_max_numerator,
    )
    if tail_choice is None:
        raise AssertionError("no local consecutive-rational cusp factor found")
    tail_base, local_lambda = tail_choice

    slope = Fraction(3**full_affine.m, 1 << full_affine.A)
    for edge_id, (
        source,
        child_u,
        child_lift_modulus,
        child_trace,
        target,
        ratio_upper,
    ) in enumerate(exact_rows):
        corrected_ratio = ratio_upper * tail_base ** (target.R - source.R)
        child_rows.append(
            {
                "edge_id": edge_id,
                "source": source.to_json_dict(),
                "source_congruence": (
                    f"u == {source.u_mod2} mod 2^{source.mod2_power}; "
                    f"u == {source.u_mod3} mod 3^{source.mod3_power}"
                ),
                "least_positive_u": str(child_u),
                "source_lift_modulus": str(child_lift_modulus),
                "least_n": str(child_trace.n0),
                "landing": str(child_trace.landing),
                "target": target.to_json_dict(),
                "valuation_word": list(trace.full_word),
                "integer_realizable": True,
                "classification": "exact_expanding_tail_reentry_branch",
                "affine_slope": _fraction_json(slope),
                "affine_slope_comparison_to_one": _comparison_to_one(slope),
                "least_lift_size_ratio_upper": _fraction_json(ratio_upper),
                "size_ratio_monotonicity": (
                    "strictly_decreasing_in_n_because_affine_B_is_positive"
                ),
                "local_symbolic_ratio_upper": _fraction_json(corrected_ratio),
                "local_symbolic_ratio_below_one": corrected_ratio < 1,
            }
        )

    fixed_target_mod3_residues = {
        target.u_mod3 for _, _, _, _, target, _ in exact_rows
    }
    expected_targets = (
        {
            (residue2, next(iter(fixed_target_mod3_residues)))
            for residue2 in range(1, 1 << target_mod2_power, 2)
        }
        if len(fixed_target_mod3_residues) == 1
        else set()
    )
    partition_verified = (
        len(expected_source_residues) == child_count
        and len(set(expected_source_residues)) == child_count
        and all(
            residue % (1 << root.mod2_power) == root.u_mod2
            for residue in expected_source_residues
        )
    )
    target_coverage_complete = seen_targets == expected_targets
    if not partition_verified:
        raise AssertionError("source child partition is incomplete or duplicated")

    cycle_classification = classify_cycle_word(trace.full_word)
    worst_source, worst_u, _, worst_trace, worst_target, _ = exact_rows[
        worst_row_index
    ]
    available_target_mod3_power = root.mod3_power + full_affine.m
    available_target_mod3_modulus = 3**available_target_mod3_power
    worst_target_u = (worst_trace.landing + 1) >> target_R

    provenance_file = Path(provenance_path)
    default_root = ExactMixedCylinder(9, 55, 11, 2, 2)
    provenance = (
        _default_selection_provenance(provenance_file)
        if root == default_root and target_mod2_power == 8
        else {
            "selection_kind": "caller_supplied_seeded_root",
            "sampling_used_for_root_selection": False,
            "sampling_used_for_branch_coverage": False,
            "input_artifact": None,
            "input_artifact_sha256": None,
        }
    )

    root_json = {
        "source_cylinder": root.to_json_dict(),
        "source_congruence": (
            f"u == {root.u_mod2} mod 2^{root.mod2_power}; "
            f"u == {root.u_mod3} mod 3^{root.mod3_power}"
        ),
        "least_positive_u": str(least_u),
        "source_lift_modulus": str(root_lift_modulus),
        "least_n": str(trace.n0),
        "trace": trace.to_json_dict(),
        "post_affine": {
            "m": post_affine.m,
            "A": post_affine.A,
            "B": str(post_affine.B),
        },
        "full_affine": {
            "m": full_affine.m,
            "A": full_affine.A,
            "B": str(full_affine.B),
            "identity": (
                f"F(n) = ({3**full_affine.m}*n + {full_affine.B})"
                f"/{1 << full_affine.A}"
            ),
            "slope": _fraction_json(slope),
            "slope_comparison_to_one": _comparison_to_one(slope),
        },
        "exact_word_cylinder": {
            "n_residue": str(exact_full_residue),
            "n_modulus_power": exact_full_power,
            "post_u_residue": str(exact_post_u_residue),
            "post_u_modulus_power": exact_post_u_power,
            "extra_bit_used_to_fix_final_valuation": True,
        },
        "precision_proof": {
            "required_source_power_for_exact_post_word": required_word_power,
            "required_source_power_for_exact_reentry": required_event_power,
            "root_source_power": root.mod2_power,
            "target_mod2_power": target_mod2_power,
            "required_source_power_for_fixed_target": required_target_power,
            "refined_source_power": refined_power,
            "target_precision_formula": "A_post + R_target + k_target - 1",
            "retained_target_mod3_power": root.mod3_power,
            "available_target_mod3_power": available_target_mod3_power,
            "worst_target_u_mod_available_3_power": str(
                worst_target_u % available_target_mod3_modulus
            ),
        },
        "uniform_stopping_proof": {
            "all_checked_prefix_slopes_at_least_one": True,
            "magnitude_interval_lift_index_min": 0,
            "magnitude_interval_lift_index_max": None,
            "prefixes": list(prefix_records),
        },
        "partition": {
            "coarse_mod2_power": root.mod2_power,
            "refined_mod2_power": refined_power,
            "expected_child_count": child_count,
            "actual_child_count": len(exact_rows),
            "unique_child_count": len(set(expected_source_residues)),
            "partition_verified": partition_verified,
            "source_residue_sha256": _partition_hash(
                expected_source_residues
            ),
            "distinct_target_count": len(seen_targets),
            "expected_full_target_fiber_count": len(expected_targets),
            "full_odd_2adic_target_fiber_covered": target_coverage_complete,
        },
        "cycle_fixed_point_audit": {
            "classification": cycle_classification.kind,
            "value": _fraction_json(cycle_classification.value),
            "interpretation": (
                "The one-word affine fixed-point equation has no integer "
                "solution. This excludes only a periodic integer orbit with "
                "this exact macro word; it does not remove an expanding "
                "itinerary through changing cylinders."
            ),
        },
    }

    symbolic_candidate = {
        "candidate_class": "tail_cusp_power",
        "formula": (
            f"H(n,R) = n * ({tail_base.numerator}/{tail_base.denominator})^R"
        ),
        "alpha": _fraction_json(Fraction(1, 1)),
        "tail_base": _fraction_json(tail_base),
        "selection_rule": (
            "closest_to_one_consecutive_fraction_a_over_a_minus_one_within_"
            f"a_at_most_{cusp_search_max_numerator}_that_contracts_this_scope"
        ),
        "source_R": root.R,
        "target_R": target_R,
        "tail_depth_drop": root.R - target_R,
        "worst_size_ratio_upper": _fraction_json(worst_ratio),
        "worst_source": worst_source.to_json_dict(),
        "worst_least_u": str(worst_u),
        "worst_least_n": str(worst_trace.n0),
        "worst_landing": str(worst_trace.landing),
        "worst_target": worst_target.to_json_dict(),
        "lambda_scope": _fraction_json(local_lambda),
        "margin_to_one": _fraction_json(Fraction(1, 1) - local_lambda),
        "exact_scope_inequality_verified": local_lambda < 1
        and all(
            _fraction_from_json(row["local_symbolic_ratio_upper"])
            <= local_lambda
            for row in child_rows
        ),
        "scope": "all_positive_integers_in_the_selected_root_cylinder",
        "global_inequality_verified": False,
        "interpretation": (
            "The expanding size branch is absorbed locally by a positive "
            "tail-depth cusp correction. The open target frontier must be "
            "expanded before this formula can be assessed globally."
        ),
    }

    proof_ineligibility_reasons: list[str] = []
    if provenance["sampling_used_for_root_selection"]:
        proof_ineligibility_reasons.append(
            "The default source root was historically selected from a finite "
            "sampled PECM diagnostic."
        )
    else:
        proof_ineligibility_reasons.append(
            "The caller supplied one source root; no global source partition "
            "was attempted."
        )
    proof_ineligibility_reasons.extend(
        (
            "Only one source cylinder has been covered.",
            f"The {len(seen_targets)} exact retained target nodes form an "
            "open outgoing frontier.",
            "No closed exact branch graph or global exceptional set is available.",
        )
    )
    target_mod3_description = ",".join(
        str(value) for value in sorted(fixed_target_mod3_residues)
    )

    return ExactCylinderPilotReport(
        type="pecm_exact_selected_cylinder_pilot",
        status=(
            "exact_selected_cylinder_partition_open_frontier_not_global_proof"
        ),
        provenance=provenance,
        scope={
            "root_cylinders": 1,
            "target_mod2_power": target_mod2_power,
            "target_mod3_power": root.mod3_power,
            "max_post_steps": max_post_steps,
            "max_leaves": max_leaves,
            "exact_within_selected_roots": True,
            "global_domain_coverage": False,
            "transition_graph_closed": False,
        },
        root=root_json,
        edges=tuple(child_rows),
        frontier={
            "status": "open",
            "open_target_nodes": len(seen_targets),
            "unresolved_source_leaves": 0,
            "fixed_word_source_leaves": len(exact_rows),
            "fixed_target_source_leaves": len(exact_rows),
            "reason": (
                f"The {len(seen_targets)} exact retained targets at R={target_R}, "
                f"u mod 2^{target_mod2_power}, and u mod "
                f"3^{root.mod3_power} in {{{target_mod3_description}}} have "
                "not yet been expanded into target-fixed outgoing branches."
            ),
        },
        symbolic_candidate=symbolic_candidate,
        max_plus={
            "weight_model": "exact_multiplicative_branch_ratios",
            "graph_closed": False,
            "karp_status": "not_applicable_open_frontier",
            "exact_difference_solver_status": "not_run_open_frontier",
            "cycles": [],
            "float_log_weights_used_for_certificate": False,
        },
        proof={
            "exact_transition_partition_verified": partition_verified,
            "exact_branch_replay_verified": True,
            "exact_local_symbolic_lyapunov_verified": symbolic_candidate[
                "exact_scope_inequality_verified"
            ],
            "exact_global_symbolic_lyapunov_verified": False,
            "proof_eligible": False,
            "global_collatz_proof": False,
            "proof_ineligibility_reasons": proof_ineligibility_reasons,
        },
    )


def _fraction_from_json(data: dict[str, str]) -> Fraction:
    return Fraction(int(data["numerator"]), int(data["denominator"]))


def _parse_root(value: str) -> ExactMixedCylinder:
    try:
        R, u2, k, u3, ell = (int(part) for part in value.split(":"))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "root must have form R:u_mod2:k:u_mod3:ell"
        ) from error
    return ExactMixedCylinder(R, u2, k, u3, ell)


def main(argv: list[str] | None = None) -> None:
    """Write the exact selected-cylinder pilot artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=_parse_root,
        default=ExactMixedCylinder(9, 55, 11, 2, 2),
        help="selected root as R:u_mod2:k:u_mod3:ell",
    )
    parser.add_argument("--target-mod2-power", type=int, default=8)
    parser.add_argument("--max-post-steps", type=int, default=32)
    parser.add_argument("--max-leaves", type=int, default=4096)
    parser.add_argument(
        "--cusp-search-max-numerator",
        type=int,
        default=64,
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=DEFAULT_PROVENANCE_PATH,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = exact_selected_cylinder_pilot_report(
        root=args.root,
        target_mod2_power=args.target_mod2_power,
        max_post_steps=args.max_post_steps,
        max_leaves=args.max_leaves,
        cusp_search_max_numerator=args.cusp_search_max_numerator,
        provenance_path=args.provenance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.to_json() + "\n", encoding="utf-8")
    LOGGER.info(
        "wrote %s (%d exact leaves; status=%s)",
        args.output,
        len(report.edges),
        report.status,
    )


if __name__ == "__main__":
    main()
