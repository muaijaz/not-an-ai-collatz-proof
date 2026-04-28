"""Finite checks for local Collatz tuple merging patterns.

This module turns informal "neighboring trajectories merge" observations into
small exact artifacts.  These are useful graph diagnostics, not global proofs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MergeWitness:
    """First common value reached by several ordinary Collatz trajectories."""

    value: int
    times: tuple[int, ...]
    max_time: int
    lag: int


@dataclass(frozen=True)
class TupleFamily:
    """A consecutive or near-consecutive tuple family ``modulus*k + offsets``."""

    name: str
    modulus: int
    offsets: tuple[int, ...]
    expected_max_time: int
    source: str


@dataclass(frozen=True)
class TupleFamilyCheck:
    """Finite sample check for one tuple family."""

    family: TupleFamily
    samples_checked: int
    passed: bool
    witnesses: tuple[MergeWitness, ...]
    failures: tuple[tuple[int, tuple[int, ...]], ...]


@dataclass(frozen=True)
class TupleMergeReport:
    """A bundle of finite local tuple-merge checks."""

    type: str
    status: str
    families: tuple[TupleFamilyCheck, ...]


REDDIT_TUPLE_FAMILIES: tuple[TupleFamily, ...] = (
    TupleFamily(
        name="FP",
        modulus=8,
        offsets=(4, 5),
        expected_max_time=3,
        source="reddit_consecutive_tuple_thread",
    ),
    TupleFamily(
        name="PP1",
        modulus=16,
        offsets=(2, 3),
        expected_max_time=5,
        source="reddit_consecutive_tuple_thread",
    ),
    TupleFamily(
        name="PP2",
        modulus=32,
        offsets=(22, 23),
        expected_max_time=5,
        source="reddit_consecutive_tuple_thread",
    ),
    TupleFamily(
        name="ET1",
        modulus=32,
        offsets=(4, 5, 6),
        expected_max_time=6,
        source="reddit_consecutive_tuple_thread",
    ),
    TupleFamily(
        name="OT1",
        modulus=128,
        offsets=(49, 50, 51),
        expected_max_time=12,
        source="reddit_consecutive_tuple_thread",
    ),
)


def collatz_step(n: int) -> int:
    """One ordinary Collatz step on a positive integer."""

    if n <= 0:
        raise ValueError("Collatz step expects a positive integer")
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def orbit_hits(n: int, max_steps: int) -> dict[int, int]:
    """Map each value hit by ``n`` to its first ordinary-step time."""

    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    hits = {n: 0}
    x = n
    for step in range(1, max_steps + 1):
        x = collatz_step(x)
        hits.setdefault(x, step)
    return hits


def merge_witness(values: tuple[int, ...], max_steps: int) -> MergeWitness | None:
    """Return the earliest bounded asynchronous merge witness, if one exists."""

    if not values:
        raise ValueError("values must be nonempty")
    hit_maps = tuple(orbit_hits(value, max_steps) for value in values)
    common = set(hit_maps[0])
    for hits in hit_maps[1:]:
        common &= set(hits)
    if not common:
        return None

    def key(value: int) -> tuple[int, int, int]:
        times = tuple(hits[value] for hits in hit_maps)
        return (max(times), max(times) - min(times), value)

    value = min(common, key=key)
    times = tuple(hits[value] for hits in hit_maps)
    return MergeWitness(
        value=value,
        times=times,
        max_time=max(times),
        lag=max(times) - min(times),
    )


def check_tuple_family(
    family: TupleFamily,
    samples: int = 16,
    start_k: int = 0,
    max_steps: int | None = None,
) -> TupleFamilyCheck:
    """Check a tuple family for finitely many ``k`` values."""

    if samples < 1:
        raise ValueError("samples must be positive")
    if start_k < 0:
        raise ValueError("start_k must be nonnegative")
    step_bound = family.expected_max_time if max_steps is None else max_steps
    if step_bound < 0:
        raise ValueError("max_steps must be nonnegative")

    witnesses: list[MergeWitness] = []
    failures: list[tuple[int, tuple[int, ...]]] = []
    for k in range(start_k, start_k + samples):
        values = tuple(family.modulus * k + offset for offset in family.offsets)
        witness = merge_witness(values, step_bound)
        if witness is None or witness.max_time > family.expected_max_time:
            failures.append((k, values))
        else:
            witnesses.append(witness)
    return TupleFamilyCheck(
        family=family,
        samples_checked=samples,
        passed=not failures,
        witnesses=tuple(witnesses),
        failures=tuple(failures),
    )


def tuple_merge_report(
    families: tuple[TupleFamily, ...] = REDDIT_TUPLE_FAMILIES,
    samples: int = 16,
    max_steps: int | None = None,
) -> TupleMergeReport:
    """Check the built-in local tuple families on a finite sample."""

    checks = tuple(
        check_tuple_family(family, samples=samples, max_steps=max_steps)
        for family in families
    )
    return TupleMergeReport(
        type="local_tuple_merge_report",
        status="finite_tuple_merge_samples_not_collatz_proof",
        families=checks,
    )
