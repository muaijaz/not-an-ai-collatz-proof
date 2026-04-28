"""Experimental mixed ``2/3`` residue automaton.

The automaton is exploratory: it helps locate dangerous abstract states and
cycle candidates. Exact certificate and cycle classifications are still done
with integer arithmetic.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .certificates import certificate_from_word
from .cycles import CycleClassification, classify_cycle_word
from .core import debt_bucket, is_shrink_favorable, v2


@dataclass(frozen=True)
class MixedState:
    mod2_power: int
    residue2: int
    mod3_power: int
    residue3: int
    m: int
    A: int
    suffix: tuple[int, ...]


@dataclass(frozen=True)
class CycleCandidate:
    state: MixedState
    first_seen_step: int
    period_word: tuple[int, ...]
    classification: CycleClassification


@dataclass(frozen=True)
class MixedAutomatonReport:
    states_explored: int
    terminal_certified: int
    terminal_low_debt: int
    dominated_pruned: int
    mod3_truncations: int
    cycle_candidates: tuple[CycleCandidate, ...]
    unresolved_states: tuple[MixedState, ...]
    transitions: int


def forced_valuation(residue: int, mod2_power: int) -> int | None:
    """Return the valuation forced by ``n == residue mod 2^k``, if known."""

    if mod2_power < 1:
        raise ValueError("mod2_power must be positive")
    modulus = 1 << mod2_power
    r = residue % modulus
    if r % 2 == 0:
        raise ValueError("residue must be odd")

    valuation = v2(3 * r + 1)
    if valuation >= mod2_power:
        return None
    return valuation


def split_state(state: MixedState) -> tuple[MixedState, MixedState]:
    """Split one binary cylinder into its two children."""

    next_power = state.mod2_power + 1
    return (
        MixedState(
            mod2_power=next_power,
            residue2=state.residue2,
            mod3_power=state.mod3_power,
            residue3=state.residue3,
            m=state.m,
            A=state.A,
            suffix=state.suffix,
        ),
        MixedState(
            mod2_power=next_power,
            residue2=state.residue2 + (1 << state.mod2_power),
            mod3_power=state.mod3_power,
            residue3=state.residue3,
            m=state.m,
            A=state.A,
            suffix=state.suffix,
        ),
    )


def transition_state(
    state: MixedState,
    valuation: int,
    A: int,
    m: int,
    suffix_length: int,
    max_mod3_power: int,
) -> MixedState:
    """Advance a state by one forced accelerated odd step."""

    known_output_bits = state.mod2_power - valuation
    if known_output_bits <= 0:
        next_mod2_power = 1
        next_residue2 = 1
    else:
        next_mod2_power = known_output_bits
        next_residue2 = ((3 * state.residue2 + 1) >> valuation) % (
            1 << next_mod2_power
        )

    next_mod3_power = min(state.mod3_power + 1, max_mod3_power)
    modulus3 = 3**next_mod3_power
    inverse_power2 = pow(pow(2, valuation, modulus3), -1, modulus3)
    next_residue3 = ((3 * state.residue3 + 1) * inverse_power2) % modulus3
    suffix = (*state.suffix, valuation)[-suffix_length:]

    return MixedState(
        mod2_power=next_mod2_power,
        residue2=next_residue2,
        mod3_power=next_mod3_power,
        residue3=next_residue3,
        m=m,
        A=A,
        suffix=suffix,
    )


def project_state(state: MixedState, mod3_power_cap: int | None) -> MixedState:
    """Project exact mixed state to a finite quotient for reporting."""

    if mod3_power_cap is None or state.mod3_power <= mod3_power_cap:
        return state
    modulus3 = 3**mod3_power_cap
    return MixedState(
        mod2_power=state.mod2_power,
        residue2=state.residue2,
        mod3_power=mod3_power_cap,
        residue3=state.residue3 % modulus3,
        m=state.m,
        A=state.A,
        suffix=state.suffix,
    )


def cycle_key(
    state: MixedState,
    mod3_power_cap: int | None,
    bucket_scale: int,
) -> tuple[int, int, int, int, int, tuple[int, ...]]:
    """Finite abstract key for detecting projected automaton cycles."""

    projected = project_state(state, mod3_power_cap)
    return (
        projected.mod2_power,
        projected.residue2,
        projected.mod3_power,
        projected.residue3,
        debt_bucket(projected.A, projected.m, scale=bucket_scale),
        projected.suffix,
    )


def state_sort_key(state: MixedState) -> tuple[int, int, int, int, int, int, tuple[int, ...]]:
    """Stable ordering key for deterministic priority queues."""

    return (
        state.mod2_power,
        state.residue2,
        state.mod3_power,
        state.residue3,
        state.m,
        state.A,
        state.suffix,
    )


@dataclass(frozen=True)
class _Node:
    state: MixedState
    A: int
    m: int
    word: tuple[int, ...]


def initial_states(
    mod2_power: int,
    mod3_power: int,
    bucket_scale: int,
) -> tuple[MixedState, ...]:
    """Return all mixed residue states at the requested starting precision."""

    if mod2_power < 1 or mod3_power < 0:
        raise ValueError("mod2_power must be positive and mod3_power nonnegative")

    modulus2 = 1 << mod2_power
    modulus3 = 3**mod3_power
    states: list[MixedState] = []
    for residue2 in range(1, modulus2, 2):
        for residue3 in range(modulus3):
            states.append(
                MixedState(
                    mod2_power=mod2_power,
                    residue2=residue2,
                    mod3_power=mod3_power,
                    residue3=residue3,
                    m=0,
                    A=0,
                    suffix=(),
                )
            )
    return tuple(states)


def explore_mixed_automaton(
    initial_mod2_power: int = 5,
    mod3_power: int = 2,
    max_mod2_power: int = 14,
    max_states: int = 20_000,
    max_steps: int = 80,
    min_debt: float = -2.0,
    suffix_length: int = 8,
    bucket_scale: int = 100,
    max_mod3_power: int = 8,
    cycle_mod3_power: int | None = 4,
) -> MixedAutomatonReport:
    """Explore dangerous mixed residue states and report abstract cycles."""

    min_bucket = int(min_debt * bucket_scale)
    queue: deque[_Node] = deque(
        _Node(state=state, A=0, m=0, word=())
        for state in initial_states(initial_mod2_power, mod3_power, bucket_scale)
    )
    seen: dict[tuple[int, int, int, int, int, tuple[int, ...]], tuple[int, tuple[int, ...]]] = {}
    cycles: list[CycleCandidate] = []
    unresolved: list[MixedState] = []
    terminal_certified = 0
    terminal_low_debt = 0
    dominated_pruned = 0
    mod3_truncations = 0
    states_explored = 0
    transitions = 0
    strongest: dict[tuple[int, int, int, int], tuple[int, int]] = {}

    while queue and states_explored < max_states:
        node = queue.popleft()
        states_explored += 1

        residue_key = (
            node.state.mod2_power,
            node.state.residue2,
            node.state.mod3_power,
            node.state.residue3,
        )
        previous_strength = strongest.get(residue_key)
        if previous_strength is not None:
            previous_m, previous_A = previous_strength
            if previous_m >= node.m and previous_A <= node.A:
                dominated_pruned += 1
                continue
            if node.m >= previous_m and node.A <= previous_A:
                strongest[residue_key] = (node.m, node.A)
        else:
            strongest[residue_key] = (node.m, node.A)

        seen_key = cycle_key(node.state, cycle_mod3_power, bucket_scale)
        previous = seen.get(seen_key)
        if previous is not None:
            first_seen_step, previous_word = previous
            period_word = node.word[len(previous_word) :]
            if period_word:
                cycles.append(
                    CycleCandidate(
                        state=node.state,
                        first_seen_step=first_seen_step,
                        period_word=period_word,
                        classification=classify_cycle_word(period_word),
                    )
                )
            continue
        seen[seen_key] = (node.m, node.word)

        if node.m >= max_steps:
            unresolved.append(node.state)
            continue

        if node.m > 0 and is_shrink_favorable(node.A, node.m):
            certificate_from_word(node.word)
            terminal_certified += 1
            continue

        if debt_bucket(node.A, node.m, scale=bucket_scale) < min_bucket:
            terminal_low_debt += 1
            continue

        valuation = forced_valuation(node.state.residue2, node.state.mod2_power)
        if valuation is None:
            if node.state.mod2_power >= max_mod2_power:
                unresolved.append(node.state)
                continue
            for child in split_state(node.state):
                queue.append(_Node(state=child, A=node.A, m=node.m, word=node.word))
            transitions += 2
            continue

        next_A = node.A + valuation
        next_m = node.m + 1
        next_word = (*node.word, valuation)
        if node.state.mod3_power >= max_mod3_power:
            mod3_truncations += 1
        queue.append(
            _Node(
                state=transition_state(
                    node.state,
                    valuation=valuation,
                    A=next_A,
                    m=next_m,
                    suffix_length=suffix_length,
                    max_mod3_power=max_mod3_power,
                ),
                A=next_A,
                m=next_m,
                word=next_word,
            )
        )
        transitions += 1

    unresolved.extend(node.state for node in queue)

    return MixedAutomatonReport(
        states_explored=states_explored,
        terminal_certified=terminal_certified,
        terminal_low_debt=terminal_low_debt,
        dominated_pruned=dominated_pruned,
        mod3_truncations=mod3_truncations,
        cycle_candidates=tuple(cycles),
        unresolved_states=tuple(unresolved),
        transitions=transitions,
    )
