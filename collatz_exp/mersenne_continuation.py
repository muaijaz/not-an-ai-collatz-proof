"""Mersenne post-run continuation graphs over parameter classes ``R mod M``."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import gcd
from typing import Any

from .core import accelerated_step
from .mersenne import MersenneProfile, initial_mersenne_run, mersenne_value, profile_mersenne


@dataclass(frozen=True)
class MersenneContinuationSample:
    R: int
    residue_class: int
    post_run_steps: int
    post_run_valuation: int
    landing_debt: float
    max_debt: float
    landing: int
    spike_count: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersenneResidueClassSummary:
    residue_class: int
    count: int
    min_landing_debt: float
    max_landing_debt: float
    max_post_run_steps: int
    min_post_run_valuation: int
    max_spike_count: int
    worst_R: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersenneContinuationEdge:
    source_class: int
    target_class: int
    count: int
    min_gain: int
    max_gain: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersenneContinuationGraph:
    type: str
    status: str
    modulus: int
    R_min: int
    R_max: int
    samples: int
    classes: tuple[MersenneResidueClassSummary, ...]
    edges: tuple[MersenneContinuationEdge, ...]
    worst_samples: tuple[MersenneContinuationSample, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "modulus": self.modulus,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "samples": self.samples,
            "classes": [item.to_json_dict() for item in self.classes],
            "edges": [item.to_json_dict() for item in self.edges],
            "worst_samples": [item.to_json_dict() for item in self.worst_samples],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class MersenneRefinementLink:
    parent_modulus: int
    parent_class: int
    child_modulus: int
    child_class: int
    parent_max_landing_debt: float
    child_max_landing_debt: float
    child_worst_R: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersenneModulusWorst:
    modulus: int
    worst_class: int
    worst_R: int
    max_landing_debt: float
    samples: int
    classes: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MersenneRefinementReport:
    type: str
    status: str
    R_min: int
    R_max: int
    moduli: tuple[int, ...]
    worst_by_modulus: tuple[MersenneModulusWorst, ...]
    refinement_links: tuple[MersenneRefinementLink, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "moduli": list(self.moduli),
            "worst_by_modulus": [
                item.to_json_dict() for item in self.worst_by_modulus
            ],
            "refinement_links": [
                item.to_json_dict() for item in self.refinement_links
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class MersenneProgressionSample:
    R: int
    t: int
    post_run_steps: int
    post_run_valuation: int
    landing_debt: float
    word_prefix: tuple[int, ...]
    spike_positions: tuple[tuple[int, int], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["word_prefix"] = list(self.word_prefix)
        data["spike_positions"] = [list(item) for item in self.spike_positions]
        return data


@dataclass(frozen=True)
class MersenneProgressionReport:
    type: str
    status: str
    base_R: int
    modulus: int
    t_min: int
    t_max: int
    samples: tuple[MersenneProgressionSample, ...]
    common_prefix: tuple[int, ...]
    worst_R: int
    worst_landing_debt: float
    distinct_prefixes: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "base_R": self.base_R,
            "modulus": self.modulus,
            "t_min": self.t_min,
            "t_max": self.t_max,
            "samples": [sample.to_json_dict() for sample in self.samples],
            "common_prefix": list(self.common_prefix),
            "worst_R": self.worst_R,
            "worst_landing_debt": self.worst_landing_debt,
            "distinct_prefixes": self.distinct_prefixes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class MersenneBranchNode:
    prefix: tuple[int, ...]
    count: int
    worst_R: int
    worst_landing_debt: float
    min_landing_debt: float
    children: tuple["MersenneBranchNode", ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "prefix": list(self.prefix),
            "count": self.count,
            "worst_R": self.worst_R,
            "worst_landing_debt": self.worst_landing_debt,
            "min_landing_debt": self.min_landing_debt,
            "children": [child.to_json_dict() for child in self.children],
        }


@dataclass(frozen=True)
class MersenneBranchReport:
    type: str
    status: str
    base_R: int
    modulus: int
    t_min: int
    t_max: int
    max_depth: int
    root: MersenneBranchNode

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "base_R": self.base_R,
            "modulus": self.modulus,
            "t_min": self.t_min,
            "t_max": self.t_max,
            "max_depth": self.max_depth,
            "root": self.root.to_json_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PrefixResidueSummary:
    modulus: int
    counts: tuple[tuple[int, int], ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "modulus": self.modulus,
            "counts": [list(item) for item in self.counts],
        }


@dataclass(frozen=True)
class MersennePrefixFamilyReport:
    type: str
    status: str
    base_R: int
    modulus: int
    t_min: int
    t_max: int
    target_prefix: tuple[int, ...]
    hit_count: int
    miss_count: int
    hits: tuple[MersenneProgressionSample, ...]
    near_misses: tuple[MersenneProgressionSample, ...]
    hit_gaps: tuple[int, ...]
    gcd_hit_gap: int
    hit_residues_by_power: tuple[PrefixResidueSummary, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "base_R": self.base_R,
            "modulus": self.modulus,
            "t_min": self.t_min,
            "t_max": self.t_max,
            "target_prefix": list(self.target_prefix),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hits": [sample.to_json_dict() for sample in self.hits],
            "near_misses": [sample.to_json_dict() for sample in self.near_misses],
            "hit_gaps": list(self.hit_gaps),
            "gcd_hit_gap": self.gcd_hit_gap,
            "hit_residues_by_power": [
                item.to_json_dict() for item in self.hit_residues_by_power
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def post_run_word_for_mersenne(R: int, max_steps: int = 10_000) -> tuple[int, ...]:
    """Return post-run valuations until descending below ``2^R - 1``."""

    run = initial_mersenne_run(R)
    original = mersenne_value(R)
    x = run.post_run_value
    word: list[int] = []
    while x >= original and len(word) < max_steps:
        x, valuation = accelerated_step(x)
        word.append(valuation)
    if x >= original:
        raise RuntimeError(f"no Mersenne post-run descent found for R={R}")
    return tuple(word)


def common_prefix(words: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    if not words:
        return ()
    limit = min(len(word) for word in words)
    prefix: list[int] = []
    for index in range(limit):
        value = words[0][index]
        if any(word[index] != value for word in words[1:]):
            break
        prefix.append(value)
    return tuple(prefix)


def spike_positions(word: tuple[int, ...], threshold: int = 4) -> tuple[tuple[int, int], ...]:
    return tuple(
        (index + 1, valuation)
        for index, valuation in enumerate(word)
        if valuation >= threshold
    )


def sample_from_profile(R: int, modulus: int, profile: MersenneProfile) -> MersenneContinuationSample:
    return MersenneContinuationSample(
        R=R,
        residue_class=R % modulus,
        post_run_steps=profile.post_run_steps,
        post_run_valuation=profile.post_run_valuation,
        landing_debt=profile.landing_debt,
        max_debt=profile.max_debt,
        landing=profile.landing,
        spike_count=len(profile.spikes),
    )


def sample_progression_R(
    R: int,
    t: int,
    prefix_length: int,
    spike_threshold: int,
    max_steps: int = 10_000,
) -> MersenneProgressionSample:
    profile = profile_mersenne(R)
    word = post_run_word_for_mersenne(R, max_steps=max_steps)
    return MersenneProgressionSample(
        R=R,
        t=t,
        post_run_steps=profile.post_run_steps,
        post_run_valuation=profile.post_run_valuation,
        landing_debt=profile.landing_debt,
        word_prefix=word[:prefix_length],
        spike_positions=spike_positions(word, threshold=spike_threshold),
    )


def _branch_node(
    samples: tuple[MersenneProgressionSample, ...],
    depth: int,
    max_depth: int,
) -> MersenneBranchNode:
    if not samples:
        raise ValueError("samples must be nonempty")
    prefix = common_prefix(tuple(sample.word_prefix for sample in samples))
    worst = max(samples, key=lambda sample: sample.landing_debt)
    if depth >= max_depth:
        children: tuple[MersenneBranchNode, ...] = ()
    else:
        split_index = len(prefix)
        buckets: dict[int | None, list[MersenneProgressionSample]] = {}
        for sample in samples:
            key = (
                sample.word_prefix[split_index]
                if split_index < len(sample.word_prefix)
                else None
            )
            buckets.setdefault(key, []).append(sample)
        children = tuple(
            _branch_node(tuple(bucket), depth + 1, max_depth)
            for _, bucket in sorted(
                buckets.items(),
                key=lambda item: (
                    item[0] is None,
                    -max(sample.landing_debt for sample in item[1]),
                    -len(item[1]),
                ),
            )
        )
    return MersenneBranchNode(
        prefix=prefix,
        count=len(samples),
        worst_R=worst.R,
        worst_landing_debt=worst.landing_debt,
        min_landing_debt=min(sample.landing_debt for sample in samples),
        children=children,
    )


def summarize_residue_class(
    residue_class: int,
    samples: tuple[MersenneContinuationSample, ...],
) -> MersenneResidueClassSummary:
    if not samples:
        raise ValueError("samples must be nonempty")
    worst = max(samples, key=lambda sample: sample.landing_debt)
    return MersenneResidueClassSummary(
        residue_class=residue_class,
        count=len(samples),
        min_landing_debt=min(sample.landing_debt for sample in samples),
        max_landing_debt=max(sample.landing_debt for sample in samples),
        max_post_run_steps=max(sample.post_run_steps for sample in samples),
        min_post_run_valuation=min(sample.post_run_valuation for sample in samples),
        max_spike_count=max(sample.spike_count for sample in samples),
        worst_R=worst.R,
    )


def continuation_edges(
    modulus: int,
    samples: tuple[MersenneContinuationSample, ...],
) -> tuple[MersenneContinuationEdge, ...]:
    """Build a coarse graph from ``R mod M`` to ``(R + post_steps) mod M``."""

    buckets: dict[tuple[int, int], list[int]] = {}
    for sample in samples:
        target = (sample.R + sample.post_run_steps) % modulus
        gain = sample.post_run_valuation - sample.post_run_steps
        buckets.setdefault((sample.residue_class, target), []).append(gain)

    return tuple(
        MersenneContinuationEdge(
            source_class=source,
            target_class=target,
            count=len(gains),
            min_gain=min(gains),
            max_gain=max(gains),
        )
        for (source, target), gains in sorted(buckets.items())
    )


def build_mersenne_continuation_graph(
    R_min: int = 2,
    R_max: int = 128,
    modulus: int = 16,
    worst_n: int = 10,
) -> MersenneContinuationGraph:
    """Profile Mersenne post-run behavior and group it by ``R mod modulus``."""

    if R_min < 2:
        raise ValueError("R_min must be at least 2")
    if R_max < R_min:
        raise ValueError("R_max must be at least R_min")
    if modulus < 1:
        raise ValueError("modulus must be positive")
    if worst_n < 1:
        raise ValueError("worst_n must be positive")

    samples = tuple(
        sample_from_profile(R, modulus, profile_mersenne(R))
        for R in range(R_min, R_max + 1)
    )
    class_map: dict[int, list[MersenneContinuationSample]] = {}
    for sample in samples:
        class_map.setdefault(sample.residue_class, []).append(sample)

    summaries = tuple(
        summarize_residue_class(residue_class, tuple(items))
        for residue_class, items in sorted(class_map.items())
    )
    worst_samples = tuple(
        sorted(samples, key=lambda sample: sample.landing_debt, reverse=True)[:worst_n]
    )
    return MersenneContinuationGraph(
        type="mersenne_continuation_parameter_graph",
        status="finite_parameter_graph_not_collatz_proof",
        modulus=modulus,
        R_min=R_min,
        R_max=R_max,
        samples=len(samples),
        classes=summaries,
        edges=continuation_edges(modulus, samples),
        worst_samples=worst_samples,
    )


def _class_summary_map(
    graph: MersenneContinuationGraph,
) -> dict[int, MersenneResidueClassSummary]:
    return {summary.residue_class: summary for summary in graph.classes}


def refine_mersenne_continuation_moduli(
    R_min: int = 2,
    R_max: int = 192,
    moduli: tuple[int, ...] = (16, 32, 64, 128),
) -> MersenneRefinementReport:
    """Compare worst Mersenne continuation classes across nested moduli."""

    if not moduli:
        raise ValueError("moduli must be nonempty")
    if any(modulus < 1 for modulus in moduli):
        raise ValueError("all moduli must be positive")
    if tuple(sorted(moduli)) != moduli:
        raise ValueError("moduli must be sorted increasingly")
    for parent, child in zip(moduli, moduli[1:]):
        if child % parent != 0:
            raise ValueError("each child modulus must refine the previous modulus")

    graphs = {
        modulus: build_mersenne_continuation_graph(
            R_min=R_min,
            R_max=R_max,
            modulus=modulus,
        )
        for modulus in moduli
    }
    summary_maps = {
        modulus: _class_summary_map(graph)
        for modulus, graph in graphs.items()
    }

    worst_by_modulus: list[MersenneModulusWorst] = []
    for modulus in moduli:
        graph = graphs[modulus]
        worst = max(graph.classes, key=lambda item: item.max_landing_debt)
        worst_by_modulus.append(
            MersenneModulusWorst(
                modulus=modulus,
                worst_class=worst.residue_class,
                worst_R=worst.worst_R,
                max_landing_debt=worst.max_landing_debt,
                samples=graph.samples,
                classes=len(graph.classes),
            )
        )

    links: list[MersenneRefinementLink] = []
    for parent_modulus, child_modulus in zip(moduli, moduli[1:]):
        parent_map = summary_maps[parent_modulus]
        child_map = summary_maps[child_modulus]
        for parent_class, parent_summary in sorted(parent_map.items()):
            children = [
                summary
                for child_class, summary in child_map.items()
                if child_class % parent_modulus == parent_class
            ]
            if not children:
                continue
            child = max(children, key=lambda item: item.max_landing_debt)
            links.append(
                MersenneRefinementLink(
                    parent_modulus=parent_modulus,
                    parent_class=parent_class,
                    child_modulus=child_modulus,
                    child_class=child.residue_class,
                    parent_max_landing_debt=parent_summary.max_landing_debt,
                    child_max_landing_debt=child.max_landing_debt,
                    child_worst_R=child.worst_R,
                )
            )

    return MersenneRefinementReport(
        type="mersenne_continuation_refinement_report",
        status="finite_refinement_graph_not_collatz_proof",
        R_min=R_min,
        R_max=R_max,
        moduli=moduli,
        worst_by_modulus=tuple(worst_by_modulus),
        refinement_links=tuple(links),
    )


def analyze_mersenne_progression(
    base_R: int = 134,
    modulus: int = 256,
    t_min: int = 0,
    t_max: int = 8,
    prefix_length: int = 80,
    spike_threshold: int = 4,
    max_steps: int = 10_000,
) -> MersenneProgressionReport:
    """Analyze exact post-run words for ``R = base_R + modulus*t``."""

    if base_R < 2:
        raise ValueError("base_R must be at least 2")
    if modulus < 1:
        raise ValueError("modulus must be positive")
    if t_min < 0 or t_max < t_min:
        raise ValueError("invalid t range")
    if prefix_length < 1:
        raise ValueError("prefix_length must be positive")

    samples = tuple(
        sample_progression_R(
            R=base_R + modulus * t,
            t=t,
            prefix_length=prefix_length,
            spike_threshold=spike_threshold,
            max_steps=max_steps,
        )
        for t in range(t_min, t_max + 1)
    )
    prefix = common_prefix(tuple(sample.word_prefix for sample in samples))
    worst = max(samples, key=lambda sample: sample.landing_debt)
    return MersenneProgressionReport(
        type="mersenne_progression_word_report",
        status="finite_progression_word_analysis_not_collatz_proof",
        base_R=base_R,
        modulus=modulus,
        t_min=t_min,
        t_max=t_max,
        samples=samples,
        common_prefix=prefix,
        worst_R=worst.R,
        worst_landing_debt=worst.landing_debt,
        distinct_prefixes=len({sample.word_prefix for sample in samples}),
    )


def analyze_mersenne_branches(
    base_R: int = 134,
    modulus: int = 256,
    t_min: int = 0,
    t_max: int = 16,
    prefix_length: int = 120,
    max_depth: int = 4,
    spike_threshold: int = 4,
    max_steps: int = 10_000,
) -> MersenneBranchReport:
    """Build a valuation-prefix branch tree for a Mersenne progression."""

    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    progression = analyze_mersenne_progression(
        base_R=base_R,
        modulus=modulus,
        t_min=t_min,
        t_max=t_max,
        prefix_length=prefix_length,
        spike_threshold=spike_threshold,
        max_steps=max_steps,
    )
    return MersenneBranchReport(
        type="mersenne_progression_branch_report",
        status="finite_branch_tree_not_collatz_proof",
        base_R=base_R,
        modulus=modulus,
        t_min=t_min,
        t_max=t_max,
        max_depth=max_depth,
        root=_branch_node(progression.samples, depth=0, max_depth=max_depth),
    )


def _residue_summaries(
    values: tuple[int, ...],
    powers: tuple[int, ...],
) -> tuple[PrefixResidueSummary, ...]:
    summaries: list[PrefixResidueSummary] = []
    for power in powers:
        if power < 0:
            raise ValueError("residue powers must be nonnegative")
        modulus = 1 << power
        counts: dict[int, int] = {}
        for value in values:
            residue = value % modulus
            counts[residue] = counts.get(residue, 0) + 1
        summaries.append(
            PrefixResidueSummary(
                modulus=modulus,
                counts=tuple(sorted(counts.items())),
            )
        )
    return tuple(summaries)


def analyze_mersenne_prefix_family(
    base_R: int = 134,
    modulus: int = 256,
    target_prefix: tuple[int, ...] = (4, 1, 2, 1, 1, 1, 6),
    t_min: int = 0,
    t_max: int = 32,
    prefix_length: int = 80,
    spike_threshold: int = 4,
    max_steps: int = 10_000,
    residue_powers: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8),
    near_miss_limit: int = 12,
) -> MersennePrefixFamilyReport:
    """Check whether a target valuation prefix recurs along a Mersenne progression."""

    if not target_prefix:
        raise ValueError("target_prefix must be nonempty")
    if prefix_length < len(target_prefix):
        prefix_length = len(target_prefix)
    if near_miss_limit < 0:
        raise ValueError("near_miss_limit must be nonnegative")

    progression = analyze_mersenne_progression(
        base_R=base_R,
        modulus=modulus,
        t_min=t_min,
        t_max=t_max,
        prefix_length=prefix_length,
        spike_threshold=spike_threshold,
        max_steps=max_steps,
    )
    hits = tuple(
        sample
        for sample in progression.samples
        if sample.word_prefix[: len(target_prefix)] == target_prefix
    )
    parent_prefix = target_prefix[:-1]
    near_misses = tuple(
        sorted(
            (
                sample
                for sample in progression.samples
                if sample.word_prefix[: len(parent_prefix)] == parent_prefix
                and sample.word_prefix[: len(target_prefix)] != target_prefix
            ),
            key=lambda sample: sample.landing_debt,
            reverse=True,
        )[:near_miss_limit]
    )
    hit_ts = tuple(sample.t for sample in hits)
    hit_gaps = tuple(
        right - left for left, right in zip(hit_ts, hit_ts[1:])
    )
    gap_gcd = 0
    for gap in hit_gaps:
        gap_gcd = gcd(gap_gcd, gap)
    return MersennePrefixFamilyReport(
        type="mersenne_prefix_family_report",
        status="finite_prefix_family_analysis_not_collatz_proof",
        base_R=base_R,
        modulus=modulus,
        t_min=t_min,
        t_max=t_max,
        target_prefix=target_prefix,
        hit_count=len(hits),
        miss_count=len(progression.samples) - len(hits),
        hits=hits,
        near_misses=near_misses,
        hit_gaps=hit_gaps,
        gcd_hit_gap=gap_gcd,
        hit_residues_by_power=_residue_summaries(hit_ts, residue_powers),
    )
