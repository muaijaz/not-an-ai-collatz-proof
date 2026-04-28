"""Adaptive residue-cover search."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count

from .certificates import DescentCertificate, certificate_from_residue
from .core import accelerated_step, debt_bucket


@dataclass(frozen=True)
class CoverSearchResult:
    certificates: tuple[DescentCertificate, ...]
    unresolved: tuple[tuple[int, int], ...]
    nodes_processed: int
    depth_counts: dict[int, int]
    strategy: str = "debt-priority"
    dominated_pruned: int = 0


@dataclass(frozen=True)
class ResidueTrace:
    A: int
    m: int
    word: tuple[int, ...]
    bucket: int


def forced_trace_for_residue(
    residue: int,
    modulus_power: int,
    max_steps: int = 1_000,
    bucket_scale: int = 100,
) -> ResidueTrace:
    """Trace the forced valuation prefix visible at a binary residue node."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    if residue % 2 == 0:
        raise ValueError("residue must be odd")

    x = residue % (1 << modulus_power)
    if x == 0:
        x = 1 << modulus_power

    A = 0
    word: list[int] = []
    while len(word) < max_steps and A < modulus_power:
        x, valuation = accelerated_step(x)
        word.append(valuation)
        A += valuation

    m = len(word)
    return ResidueTrace(A=A, m=m, word=tuple(word), bucket=debt_bucket(A, m, bucket_scale))


def _push_node(
    heap: list[tuple[int, int, int, int, int]],
    sequence: count,
    residue: int,
    modulus_power: int,
    max_certificate_steps: int,
    bucket_scale: int,
) -> None:
    trace = forced_trace_for_residue(
        residue,
        modulus_power,
        max_steps=max_certificate_steps,
        bucket_scale=bucket_scale,
    )
    # Fair priority: finish shallower tiers first, but expand the most
    # dangerous debt within each tier.
    heappush(heap, (modulus_power, -trace.bucket, next(sequence), residue, modulus_power))


def adaptive_cover_bfs(
    max_depth: int = 25,
    max_nodes: int = 1_000_000,
    max_certificate_steps: int = 1_000,
) -> CoverSearchResult:
    """Legacy breadth-first split of odd residue classes modulo powers of two."""

    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    if max_nodes < 1:
        raise ValueError("max_nodes must be positive")

    queue = [(1, 1)]
    cursor = 0
    certificates: list[DescentCertificate] = []
    unresolved: list[tuple[int, int]] = []
    depth_counts: defaultdict[int, int] = defaultdict(int)
    nodes = 0

    while cursor < len(queue) and nodes < max_nodes:
        residue, modulus_power = queue[cursor]
        cursor += 1
        nodes += 1
        depth_counts[modulus_power] += 1

        certificate = certificate_from_residue(
            residue, modulus_power, max_steps=max_certificate_steps
        )
        if certificate is not None:
            certificates.append(certificate)
            continue

        if modulus_power >= max_depth:
            unresolved.append((residue, modulus_power))
            continue

        queue.append((residue, modulus_power + 1))
        queue.append((residue + (1 << modulus_power), modulus_power + 1))

    unresolved.extend(queue[cursor:])

    return CoverSearchResult(
        certificates=tuple(certificates),
        unresolved=tuple(unresolved),
        nodes_processed=nodes,
        depth_counts=dict(depth_counts),
        strategy="bfs",
        dominated_pruned=0,
    )


def adaptive_cover(
    max_depth: int = 25,
    max_nodes: int = 1_000_000,
    max_certificate_steps: int = 1_000,
    bucket_scale: int = 100,
) -> CoverSearchResult:
    """Best-first split prioritized by current valuation debt."""

    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    if max_nodes < 1:
        raise ValueError("max_nodes must be positive")

    heap: list[tuple[int, int, int, int, int]] = []
    sequence = count()
    _push_node(heap, sequence, 1, 1, max_certificate_steps, bucket_scale)

    certificates: list[DescentCertificate] = []
    unresolved: list[tuple[int, int]] = []
    depth_counts: defaultdict[int, int] = defaultdict(int)
    strongest_trace: dict[tuple[int, int], tuple[int, int]] = {}
    dominated_pruned = 0
    nodes = 0

    while heap and nodes < max_nodes:
        _, _, _, residue, modulus_power = heappop(heap)
        nodes += 1
        depth_counts[modulus_power] += 1

        trace = forced_trace_for_residue(
            residue,
            modulus_power,
            max_steps=max_certificate_steps,
            bucket_scale=bucket_scale,
        )
        residue_key = (residue % (1 << modulus_power), modulus_power)
        previous = strongest_trace.get(residue_key)
        if previous is not None:
            previous_m, previous_A = previous
            if previous_m >= trace.m and previous_A <= trace.A:
                dominated_pruned += 1
                continue
            if trace.m >= previous_m and trace.A <= previous_A:
                strongest_trace[residue_key] = (trace.m, trace.A)
        else:
            strongest_trace[residue_key] = (trace.m, trace.A)

        certificate = certificate_from_residue(
            residue, modulus_power, max_steps=max_certificate_steps
        )
        if certificate is not None:
            certificates.append(certificate)
            continue

        if modulus_power >= max_depth:
            unresolved.append((residue, modulus_power))
            continue

        _push_node(
            heap,
            sequence,
            residue,
            modulus_power + 1,
            max_certificate_steps,
            bucket_scale,
        )
        _push_node(
            heap,
            sequence,
            residue + (1 << modulus_power),
            modulus_power + 1,
            max_certificate_steps,
            bucket_scale,
        )

    unresolved.extend((residue, modulus_power) for _, _, _, residue, modulus_power in heap)

    return CoverSearchResult(
        certificates=tuple(certificates),
        unresolved=tuple(unresolved),
        nodes_processed=nodes,
        depth_counts=dict(depth_counts),
        strategy="debt-priority",
        dominated_pruned=dominated_pruned,
    )
