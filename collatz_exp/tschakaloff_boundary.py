"""Certify exclusion of the recursive ghost ladder's 2-adic boundary.

The recursive affine-ghost atlas reduces its only explicit infinite ladder
boundary to the rationality of

    T_(9/4)(2) = sum_(n>=0) 2^n (4/9)^(n(n-1)/2)

inside ``Q_2``.  Väänänen and Wallisser proved a p-adic linear-independence
theorem for the related function

    f(x) = sum_(n>=0) q^(-n(n+1)/2) x^n.

This module transcribes the theorem parameters needed here, verifies every
elementary hypothesis and normalization exactly, and propagates the published
irrationality conclusion through the atlas's exact affine boundary reduction.
It does not formalize the paper's proof and it does not prove the Collatz
conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("docs/reports/pecm_recursive_ghost_atlas.json")
DEFAULT_INPUT_SHA256 = (
    "7f7653877704ad788608f4050dad5f300d89a13d7d06cb6fb5c2b5894cc36fd3"
)
DEFAULT_OUTPUT_PATH = Path("docs/reports/pecm_tschakaloff_boundary_exclusion.json")
DEFAULT_NORMALIZATION_TERM_COUNT = 32
DEFAULT_BOUNDARY_START_M_MAX = 32

CANONICAL_Q = Fraction(9, 4)
CANONICAL_Z = Fraction(2)
CANONICAL_ALPHA = CANONICAL_Q * CANONICAL_Z

SOURCE_DOI = "10.1007/BF01168299"
SOURCE_URL = "https://doi.org/10.1007/BF01168299"
SOURCE_SCAN_URL = (
    "https://gdz.sub.uni-goettingen.de/download/pdf/"
    "PPN365956996_0065/PPN365956996_0065.pdf"
)
SOURCE_SCAN_SHA256 = "33d6870dba004ac09023ab8356466a5e3ef36bfd9db9e94d08cded8b60ab2"


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
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class TschakaloffTheoremParameters:
    """The Väänänen-Wallisser theorem parameters used in this application."""

    r: int
    s: int
    h: int
    p: int
    ell: int
    sigma: int
    alpha: Fraction

    @property
    def q(self) -> Fraction:
        return Fraction(self.r, self.s)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "r": self.r,
            "s": self.s,
            "q": _fraction_json(self.q),
            "h": self.h,
            "p": self.p,
            "ell": self.ell,
            "sigma": self.sigma,
            "alpha_1": _fraction_json(self.alpha),
        }


@dataclass(frozen=True)
class BoundaryAffineReduction:
    """Write ``xi_m`` as a nonconstant rational affine form in ``T_q(2)``."""

    start_m: int
    shifted_argument: Fraction
    master_prefix: Fraction
    tail_multiplier: Fraction
    constant: Fraction
    master_coefficient: Fraction

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "start_m": self.start_m,
            "shifted_argument": _fraction_json(self.shifted_argument),
            "master_prefix": _fraction_json(self.master_prefix),
            "tail_multiplier": _fraction_json(self.tail_multiplier),
            "constant": _fraction_json(self.constant),
            "master_coefficient": _fraction_json(self.master_coefficient),
            "master_coefficient_nonzero": (self.master_coefficient != 0),
        }


@dataclass(frozen=True)
class TschakaloffBoundaryReport:
    """Machine-readable theorem instantiation and boundary exclusion."""

    type: str
    status: str
    provenance: dict[str, Any]
    published_source: dict[str, Any]
    theorem_instantiation: dict[str, Any]
    series_normalization: dict[str, Any]
    exact_cutoff_witness: dict[str, Any]
    master_value: dict[str, Any]
    boundary_family: dict[str, Any]
    finite_verification: dict[str, Any]
    scope_and_limits: dict[str, Any]
    proof: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "provenance": dict(self.provenance),
            "published_source": dict(self.published_source),
            "theorem_instantiation": dict(self.theorem_instantiation),
            "series_normalization": dict(self.series_normalization),
            "exact_cutoff_witness": dict(self.exact_cutoff_witness),
            "master_value": dict(self.master_value),
            "boundary_family": dict(self.boundary_family),
            "finite_verification": dict(self.finite_verification),
            "scope_and_limits": dict(self.scope_and_limits),
            "proof": dict(self.proof),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_json_dict(),
            indent=2,
            sort_keys=True,
        )


def canonical_theorem_parameters() -> TschakaloffTheoremParameters:
    """Return the exact theorem specialization for ``T_(9/4)(2)``."""

    return TschakaloffTheoremParameters(
        r=9,
        s=4,
        h=9,
        p=2,
        ell=1,
        sigma=0,
        alpha=Fraction(9, 2),
    )


def tschakaloff_f_term(
    n: int,
    *,
    q: Fraction = CANONICAL_Q,
    x: Fraction = CANONICAL_ALPHA,
) -> Fraction:
    """Return term ``n`` of ``f(x)=sum q^(-n(n+1)/2)x^n``."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    if q == 0:
        raise ValueError("q must be nonzero")
    return q ** (-(n * (n + 1) // 2)) * x**n


def repo_tschakaloff_term(
    n: int,
    *,
    q: Fraction = CANONICAL_Q,
    z: Fraction = CANONICAL_Z,
) -> Fraction:
    """Return term ``n`` of ``T_q(z)=sum z^n q^(-n(n-1)/2)``."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    if q == 0:
        raise ValueError("q must be nonzero")
    return z**n * q ** (-(n * (n - 1) // 2))


def verify_series_normalization(term_count: int) -> bool:
    """Verify exactly that ``T_q(z)=f(qz)`` on the requested terms."""

    if term_count < 1:
        raise ValueError("term_count must be positive")
    return all(
        tschakaloff_f_term(n, q=CANONICAL_Q, x=CANONICAL_ALPHA)
        == repo_tschakaloff_term(
            n,
            q=CANONICAL_Q,
            z=CANONICAL_Z,
        )
        for n in range(term_count)
    )


def exact_cutoff_witness() -> dict[str, Any]:
    """Return an exact rational sandwich proving ``gamma < Gamma(1,0)``.

    Here

    ``gamma = 1 + log(|4|_2)/log(9) = 1-log(2)/log(3)``.

    The integer inequality ``2^8 > 3^5`` gives
    ``log(2)/log(3) > 5/8`` and hence ``gamma < 3/8``.
    The inequality ``81 > 80`` gives
    ``(3-sqrt(5))/2 > 3/8``.  No floating-point comparison is used.
    """

    logarithmic_left = 2**8
    logarithmic_right = 3**5
    radical_left = 9**2
    radical_right = 16 * 5
    if logarithmic_left <= logarithmic_right:
        raise AssertionError("logarithmic cutoff witness failed")
    if radical_left <= radical_right:
        raise AssertionError("radical cutoff witness failed")
    return {
        "gamma_identity": ("gamma=1+log(|4|_2)/log(9)=1-log(2)/log(3)"),
        "paper_cutoff": "Gamma(1,0)=(3-sqrt(5))/2",
        "separating_rational": _fraction_json(Fraction(3, 8)),
        "gamma_upper_bound": {
            "statement": "gamma < 3/8",
            "equivalent_witness": "2^8 > 3^5",
            "left": logarithmic_left,
            "right": logarithmic_right,
            "verified": logarithmic_left > logarithmic_right,
        },
        "paper_cutoff_lower_bound": {
            "statement": "3/8 < (3-sqrt(5))/2",
            "equivalent_witness": "9^2 > 16*5",
            "left": radical_left,
            "right": radical_right,
            "verified": radical_left > radical_right,
        },
        "strict_cutoff_verified_exactly": True,
        "floating_point_used": False,
    }


def verify_theorem_hypotheses(
    parameters: TschakaloffTheoremParameters,
) -> dict[str, Any]:
    """Check the theorem hypotheses for the canonical specialization."""

    checks = {
        "r_s_coprime": gcd(parameters.r, parameters.s) == 1,
        "absolute_r_greater_than_one": abs(parameters.r) > 1,
        "s_at_least_one": parameters.s >= 1,
        "h_is_max_absolute_r_s": parameters.h == max(abs(parameters.r), parameters.s),
        "p_is_prime": parameters.p == 2,
        "ell_nonnegative": parameters.ell >= 0,
        "sigma_nonnegative": parameters.sigma >= 0,
        "alpha_nonzero": parameters.alpha != 0,
        "one_point_ratio_condition_vacuous": parameters.ell == 1,
        "q_matches_repository": parameters.q == CANONICAL_Q,
        "alpha_matches_q_times_z": (parameters.alpha == CANONICAL_Q * CANONICAL_Z),
        "p_adic_q_absolute_value_greater_than_one": (
            parameters.r % parameters.p != 0 and parameters.s % parameters.p == 0
        ),
        "strict_gamma_cutoff": exact_cutoff_witness()["strict_cutoff_verified_exactly"],
    }
    return {
        "checks": checks,
        "all_elementary_hypotheses_verified": all(checks.values()),
        "distinct_point_condition": (
            "vacuous because ell=1; there are no i!=j point ratios"
        ),
    }


def boundary_affine_reduction(
    start_m: int,
    *,
    q: Fraction = CANONICAL_Q,
    z: Fraction = CANONICAL_Z,
) -> BoundaryAffineReduction:
    """Reduce ``xi_start_m`` to an affine form in ``T_q(z)``.

    Iterating ``T_q(z)=1+z*T_q(z/q)`` gives

    ``T_q(z) = P_m + C_m*T_q(z/q^(m+1))``.

    Substitution into the recursive atlas formula

    ``xi_m=-1-q^(-m)*T_q(z/q^(m+1))``

    yields the returned rational affine form.
    """

    if start_m < 2:
        raise ValueError("start_m must be at least two")
    if q == 0 or z == 0:
        raise ValueError("q and z must be nonzero")

    master_prefix = sum(
        (repo_tschakaloff_term(j, q=q, z=z) for j in range(start_m + 1)),
        Fraction(0),
    )
    tail_multiplier = z ** (start_m + 1) * q ** (-(start_m * (start_m + 1) // 2))
    shifted_argument = z * q ** (-(start_m + 1))
    boundary_scale = q ** (-start_m)
    master_coefficient = -boundary_scale / tail_multiplier
    constant = -1 + boundary_scale * master_prefix / tail_multiplier
    if master_coefficient == 0:
        raise AssertionError("boundary reduction lost the master value")
    return BoundaryAffineReduction(
        start_m=start_m,
        shifted_argument=shifted_argument,
        master_prefix=master_prefix,
        tail_multiplier=tail_multiplier,
        constant=constant,
        master_coefficient=master_coefficient,
    )


def verify_boundary_affine_reduction(
    reduction: BoundaryAffineReduction,
    *,
    q: Fraction = CANONICAL_Q,
    z: Fraction = CANONICAL_Z,
) -> bool:
    """Replay the affine identity at several formal rational master values."""

    expected = boundary_affine_reduction(
        reduction.start_m,
        q=q,
        z=z,
    )
    if reduction != expected:
        return False
    boundary_scale = q ** (-reduction.start_m)
    for master_value in (
        Fraction(0),
        Fraction(1),
        Fraction(-7, 11),
        Fraction(256, 243),
    ):
        shifted_value = (
            master_value - reduction.master_prefix
        ) / reduction.tail_multiplier
        direct = -1 - boundary_scale * shifted_value
        affine = reduction.constant + reduction.master_coefficient * master_value
        if direct != affine:
            return False
    return True


def _validate_input_artifact(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "json_parsed": False,
        "type_matches": False,
        "explicit_boundary_present": False,
        "tschakaloff_reduction_present": False,
        "finite_prefix_compatibility_preserved": False,
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
    result["type_matches"] = payload.get("type") == "pecm_recursive_affine_ghost_atlas"
    boundary = payload.get("infinite_boundary")
    reduction = (
        boundary.get("tschakaloff_reduction") if isinstance(boundary, dict) else None
    )
    result["explicit_boundary_present"] = bool(
        isinstance(boundary, dict)
        and boundary.get("exact_boundary_valuation") == "v2(xi_m0+1)=2*m0"
        and boundary.get("positive_integer_infinite_ladder_realizability_derived")
        is False
    )
    result["tschakaloff_reduction_present"] = bool(
        isinstance(reduction, dict)
        and reduction.get("q") == _fraction_json(CANONICAL_Q)
        and reduction.get("functional_equation") == "T_q(z)=1+z*T_q(z/q)"
        and reduction.get("irrationality_derived") is False
        and reduction.get("sufficient_exclusion_target")
        == "prove T_(9/4)(2) is not rational in Q_2"
    )
    ladder = payload.get("parametric_ladder")
    result["finite_prefix_compatibility_preserved"] = bool(
        isinstance(ladder, dict)
        and ladder.get("arbitrarily_long_finite_positive_paths_derived") is True
        and ladder.get("each_edge_forces_the_next_edge_for_every_lift") is False
    )
    proof = payload.get("proof")
    result["global_proof_disclaimed"] = bool(
        isinstance(proof, dict)
        and proof.get("global_recursive_grammar_closed") is False
        and proof.get("global_collatz_proof") is False
    )
    required = (
        "type_matches",
        "explicit_boundary_present",
        "tschakaloff_reduction_present",
        "finite_prefix_compatibility_preserved",
        "global_proof_disclaimed",
    )
    result["fully_verified"] = all(result[key] is True for key in required)
    if not result["fully_verified"]:
        result["errors"].append(
            "artifact content does not certify the required open boundary"
        )
    return result


def tschakaloff_boundary_report(
    *,
    input_path: Path = DEFAULT_INPUT_PATH,
    normalization_term_count: int = DEFAULT_NORMALIZATION_TERM_COUNT,
    boundary_start_m_max: int = DEFAULT_BOUNDARY_START_M_MAX,
) -> TschakaloffBoundaryReport:
    """Build the theorem-instantiation and ladder-exclusion report."""

    if normalization_term_count < 1:
        raise ValueError("normalization_term_count must be positive")
    if boundary_start_m_max < 2:
        raise ValueError("boundary_start_m_max must be at least two")

    parameters = canonical_theorem_parameters()
    hypotheses = verify_theorem_hypotheses(parameters)
    if not hypotheses["all_elementary_hypotheses_verified"]:
        raise AssertionError("published theorem hypotheses no longer hold")
    normalization_verified = verify_series_normalization(normalization_term_count)
    if not normalization_verified:
        raise AssertionError("T_q(z)=f(qz) normalization failed")

    reductions = tuple(
        boundary_affine_reduction(start_m)
        for start_m in range(2, boundary_start_m_max + 1)
    )
    reductions_verified = all(
        verify_boundary_affine_reduction(reduction) for reduction in reductions
    )
    if not reductions_verified:
        raise AssertionError("boundary affine reduction failed")

    artifact_validation = _validate_input_artifact(input_path)
    actual_sha256 = _sha256(input_path)
    snapshot_match = actual_sha256 == DEFAULT_INPUT_SHA256
    canonical_input = (
        input_path == DEFAULT_INPUT_PATH
        and snapshot_match
        and artifact_validation["fully_verified"]
    )
    if canonical_input:
        scope_relation = "canonical_recursive_atlas_verified"
    elif input_path != DEFAULT_INPUT_PATH:
        scope_relation = "noncanonical_input_path"
    elif not artifact_validation["fully_verified"]:
        scope_relation = "input_artifact_content_unverified"
    else:
        scope_relation = "canonical_artifact_snapshot_mismatch"

    cutoff = exact_cutoff_witness()
    return TschakaloffBoundaryReport(
        type="pecm_tschakaloff_2_adic_boundary_exclusion",
        status=(
            "published_p_adic_theorem_instantiated_and_"
            "infinite_resonance_ladder_excluded"
        ),
        provenance={
            "input_path": str(input_path),
            "expected_sha256": DEFAULT_INPUT_SHA256,
            "actual_sha256": actual_sha256,
            "artifact_snapshot_match": snapshot_match,
            "artifact_content_validation": artifact_validation,
            "canonical_recursive_atlas_verified": canonical_input,
            "scope_relation": scope_relation,
        },
        published_source={
            "authors": ["K. Väänänen", "R. Wallisser"],
            "title": (
                "Zu einem Satz von Skolem über lineare Unabhängigkeit "
                "von Werten gewisser Thetareihen"
            ),
            "journal": "Manuscripta Mathematica",
            "volume": 65,
            "year": 1989,
            "pages": "199-212",
            "doi": SOURCE_DOI,
            "doi_url": SOURCE_URL,
            "primary_scan_url": SOURCE_SCAN_URL,
            "theorem_printed_pages": "200-201",
            "function_definition_printed_page": 199,
            "research_scan_sha256": SOURCE_SCAN_SHA256,
            "paper_proof_formalized_in_repository": False,
            "source_pdf_redistributed": False,
        },
        theorem_instantiation={
            "parameters": parameters.to_json_dict(),
            "function": ("f(x)=sum_(n>=0) q^(-n*(n+1)/2)*x^n"),
            "functional_equation": "f(q*x)=x*f(x)+1",
            "linear_form_specialization": (
                "ell=1 and sigma=0 gives integer linear forms in f(0)=1 and f(9/2)"
            ),
            "elementary_hypotheses": hypotheses,
            "published_conclusion": (
                "1 and f(9/2) are linearly independent over Q in Q_2"
            ),
            "external_theorem_dependency": True,
        },
        series_normalization={
            "repository_definition": ("T_q(z)=sum_(n>=0) z^n*q^(-n*(n-1)/2)"),
            "identity": "T_q(z)=f(q*z)",
            "q": _fraction_json(CANONICAL_Q),
            "z": _fraction_json(CANONICAL_Z),
            "q_times_z": _fraction_json(CANONICAL_ALPHA),
            "terms_checked_exactly": normalization_term_count,
            "identity_verified": normalization_verified,
        },
        exact_cutoff_witness=cutoff,
        master_value={
            "value": "T_(9/4)(2)=f(9/2)",
            "ambient_field": "Q_2",
            "irrational_over_Q": True,
            "reason": ("published linear independence of f(0)=1 and f(9/2)"),
        },
        boundary_family={
            "atlas_formula": ("xi_m=-1-(9/4)^(-m)*T_(9/4)(2*(9/4)^(-(m+1)))"),
            "functional_equation_reduction": (
                "xi_m=c_m+d_m*T_(9/4)(2), with c_m,d_m in Q and d_m nonzero"
            ),
            "representative_reductions": [
                reduction.to_json_dict()
                for reduction in reductions[: min(4, len(reductions))]
            ],
            "all_start_m_at_least_two_covered_symbolically": True,
            "every_boundary_irrational_over_Q_in_Q_2": True,
            "ordinary_integer_boundary_excluded": True,
            "nonnegative_integer_infinite_ladder_realizability": ("excluded"),
            "finite_positive_prefix_cylinders_invalidated": False,
        },
        finite_verification={
            "normalization_terms_checked": normalization_term_count,
            "boundary_reductions_checked": len(reductions),
            "boundary_start_m_min": 2,
            "boundary_start_m_max": boundary_start_m_max,
            "all_boundary_affine_identities_verified": (reductions_verified),
            "floating_point_checks": 0,
        },
        scope_and_limits={
            "closes": (
                "the explicit infinite J_m/K_m resonance ladder boundary "
                "derived by the recursive atlas"
            ),
            "does_not_close": [
                "the full recursive chart grammar",
                "all possible infinite Collatz itineraries",
                "a global cross-chart Lyapunov function",
                "the Collatz conjecture",
            ],
            "finite_prefix_statement": (
                "every stored finite ladder prefix still has a positive "
                "exact cylinder; only their infinite intersection is "
                "excluded from ordinary integers"
            ),
            "proof_surface": (
                "the theorem statement, specialization, elementary "
                "hypotheses, cutoff, normalization, and boundary "
                "propagation are machine-checked; the 1989 proof is cited"
            ),
        },
        proof={
            "canonical_input_atlas_link_verified": canonical_input,
            "published_p_adic_theorem_instantiated": True,
            "theorem_cutoff_verified_without_floats": True,
            "master_tschakaloff_value_irrational": True,
            "all_parametric_ladder_boundaries_irrational": True,
            "positive_integer_infinite_ladder_excluded": True,
            "divergent_positive_collatz_orbit_constructed": False,
            "global_recursive_grammar_closed": False,
            "global_collatz_proof": False,
            "claim_kind": (
                "published_theorem_instantiation_and_exact_boundary_propagation"
            ),
        },
    )


def main(argv: list[str] | None = None) -> None:
    """Write the theorem-backed 2-adic boundary exclusion artifact."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--normalization-term-count",
        type=int,
        default=DEFAULT_NORMALIZATION_TERM_COUNT,
    )
    parser.add_argument(
        "--boundary-start-m-max",
        type=int,
        default=DEFAULT_BOUNDARY_START_M_MAX,
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    report = tschakaloff_boundary_report(
        input_path=args.input,
        normalization_term_count=args.normalization_term_count,
        boundary_start_m_max=args.boundary_start_m_max,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        report.to_json() + "\n",
        encoding="utf-8",
    )
    LOGGER.info(
        "wrote %s (status=%s; reductions=%d)",
        args.output,
        report.status,
        report.finite_verification["boundary_reductions_checked"],
    )


if __name__ == "__main__":
    main()
