"""Bridge-obstruction ledger for finite Collatz diagnostics."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .mersenne import initial_mersenne_run, profile_mersenne


@dataclass(frozen=True)
class MersennePostRunSample:
    R: int
    initial_run_length: int
    next_valuation_after_initial_run: int
    post_run_steps_to_descent: int
    post_run_valuation_to_descent: int
    initial_debt: float
    max_debt: float
    landing_debt: float
    landing_below_start: bool
    spike_count: int
    first_spikes: tuple[tuple[int, int], ...]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersennePostRunReport:
    type: str
    status: str
    sample_R: tuple[int, ...]
    source: str
    samples: tuple[MersennePostRunSample, ...]
    interpretation: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_R": list(self.sample_R),
            "source": self.source,
            "samples": [sample.to_json_dict() for sample in self.samples],
            "interpretation": self.interpretation,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class BridgeObservation:
    name: str
    source_reports: tuple[str, ...]
    finite_signal: str
    missing_implication: str
    next_test: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FiniteToInfiniteBridgeAudit:
    type: str
    status: str
    thesis: str
    input_reports: tuple[str, ...]
    observations: tuple[BridgeObservation, ...]
    candidate_bridge_statement: str
    falsifiable_next_step: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "thesis": self.thesis,
            "input_reports": list(self.input_reports),
            "observations": [
                observation.to_json_dict() for observation in self.observations
            ],
            "candidate_bridge_statement": self.candidate_bridge_statement,
            "falsifiable_next_step": self.falsifiable_next_step,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def mersenne_post_run_report(
    sample_R: tuple[int, ...] = (32, 40, 56, 64, 72, 80, 88, 90),
    spike_limit: int = 6,
) -> MersennePostRunReport:
    """Profile finite Mersenne post-run descent rows as a saved artifact."""

    samples: list[MersennePostRunSample] = []
    for R in sample_R:
        run = initial_mersenne_run(R)
        profile = profile_mersenne(R)
        samples.append(
            MersennePostRunSample(
                R=R,
                initial_run_length=run.run_length,
                next_valuation_after_initial_run=run.next_valuation,
                post_run_steps_to_descent=profile.post_run_steps,
                post_run_valuation_to_descent=profile.post_run_valuation,
                initial_debt=profile.initial_debt,
                max_debt=profile.max_debt,
                landing_debt=profile.landing_debt,
                landing_below_start=profile.landing < (1 << R) - 1,
                spike_count=len(profile.spikes),
                first_spikes=tuple(
                    (step, valuation)
                    for step, valuation, _landing in profile.spikes[:spike_limit]
                ),
            )
        )
    return MersennePostRunReport(
        type="mersenne_post_run_descent",
        status="finite_mersenne_family_post_run_diagnostic",
        sample_R=sample_R,
        source="collatz_exp.mersenne.profile_mersenne",
        samples=tuple(samples),
        interpretation=(
            "Each sampled Mersenne start follows the initial all-one tail, then "
            "descends below its start in the measured post-run window. This "
            "does not address nonempty finite-depth sieve survival; it measures "
            "the post-run behavior after that all-one branch."
        ),
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_to_infinite_bridge_audit(
    reports_dir: str | Path = "docs/reports",
) -> FiniteToInfiniteBridgeAudit:
    """Synthesize the current finite diagnostics into an obstruction ledger."""

    reports_path = Path(reports_dir)
    tail_markov_path = reports_path / "tail_aware_markov_lyapunov.json"
    karp_path = reports_path / "constrained_karp_jsr.json"
    slope_path = reports_path / "christoffel_slope_constrained_jsr.json"
    mersenne_path = reports_path / "mersenne_post_run_descent.json"

    tail_markov = _read_json(tail_markov_path)
    karp = _read_json(karp_path)
    slope = _read_json(slope_path)
    mersenne = _read_json(mersenne_path)

    tail_level = tail_markov["levels"][-1]
    karp_level = karp["levels"][-1]
    slope_level = slope["levels"][-1]
    mersenne_samples = mersenne["samples"]
    max_post_run_steps = max(
        int(sample["post_run_steps_to_descent"]) for sample in mersenne_samples
    )
    max_sample_R = max(int(sample["R"]) for sample in mersenne_samples)

    observations = (
        BridgeObservation(
            name="worst_typical_split",
            source_reports=(str(tail_markov_path),),
            finite_signal=(
                "The largest saved LTE-closed tail graph has worst-case factor "
                f"{tail_level['worst_case_jsr_factor']} and lift-count typical "
                f"factor {tail_level['largest_component_typical_factor_per_accelerated_step']}."
            ),
            missing_implication=(
                "A typical contraction does not exclude an individual compatible "
                "schedule that repeatedly selects high-growth edges."
            ),
            next_test=(
                "Track whether high-growth product paths must eventually force "
                "a visible high-valuation exit in the tail coordinates."
            ),
        ),
        BridgeObservation(
            name="compatible_product_graph",
            source_reports=(str(karp_path), str(slope_path)),
            finite_signal=(
                "The constrained Karp product graph reports exact rational "
                f"{karp_level['exact_rational_factor']} at the largest saved "
                "product level, while the slope-constrained bounded scan has "
                f"{slope_level['slope_constrained_cycles']} survivor at its "
                "largest saved level."
            ),
            missing_implication=(
                "A period-capped balanced-word automaton does not cover every "
                "possible infinite compatible scheduler."
            ),
            next_test=(
                "Increase automaton period and slope precision together, and "
                "record whether non-elementary compatible cycles appear."
            ),
        ),
        BridgeObservation(
            name="mersenne_bypass_vs_post_run",
            source_reports=(str(mersenne_path),),
            finite_signal=(
                "The sampled Mersenne post-run table reaches descent below the "
                f"start for R up to {max_sample_R}, with maximum measured "
                f"post-run steps {max_post_run_steps}."
            ),
            missing_implication=(
                "Post-run descent rows do not contradict finite-depth all-one "
                "sieve survival, because they start measuring after the all-one "
                "branch has already been followed."
            ),
            next_test=(
                "Attach each Mersenne post-run profile to the same compatibility "
                "coordinate used by the product graph, then check whether the "
                "forced post-run spike can be detected before descent."
            ),
        ),
    )

    return FiniteToInfiniteBridgeAudit(
        type="finite_to_infinite_bridge_audit",
        status="finite_obstruction_ledger_no_global_arithmetic_step",
        thesis=(
            "The current diagnostics identify a single missing implication: "
            "finite or distributional contraction must be upgraded to exclusion "
            "of every individual infinite compatible schedule."
        ),
        input_reports=(
            str(tail_markov_path),
            str(karp_path),
            str(slope_path),
            str(mersenne_path),
        ),
        observations=observations,
        candidate_bridge_statement=(
            "Every infinite compatible tail schedule over the LTE-closed graph "
            "must force either a high-valuation exit visible at some finite "
            "level or a Mersenne-style post-run descent event."
        ),
        falsifiable_next_step=(
            "Search for compatible product paths whose finite prefixes avoid "
            "both high-valuation exits and the Mersenne post-run descent marker; "
            "any persistent family would refocus the obstruction."
        ),
    )
