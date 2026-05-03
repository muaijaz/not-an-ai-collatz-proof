"""Rozier mu-hit diagnostics for Collatz shortcut orbits."""

from __future__ import annotations

import json
import math
import random
import sys
import time
from dataclasses import dataclass
from math import gcd
from pathlib import Path
from typing import Any

from sympy import factorint, isprime


try:
    sys.set_int_max_str_digits(0)
except AttributeError:
    pass


def shortcut_T(n: int) -> int:
    """Rozier's shortcut Collatz map."""

    if n <= 0:
        raise ValueError("shortcut_T expects a positive integer")
    return (3 * n + 1) // 2 if n % 2 else n // 2


def accelerated_odd_step(n: int) -> int:
    """Return the next odd value under the accelerated Collatz map."""

    if n <= 0 or n % 2 == 0:
        raise ValueError("accelerated_odd_step expects an odd positive integer")
    x = 3 * n + 1
    return x >> ((x & -x).bit_length() - 1)


def mu_from_factorization(factors: dict[int, int]) -> float:
    """Compute Rozier's mu from a prime factorization dictionary."""

    total = 0.0
    for prime, exponent in factors.items():
        if exponent <= 0:
            raise ValueError("factor exponents must be positive")
        total += math.log(prime)
        if exponent > 1:
            total += math.log(exponent)
    return total


def mu(n: int) -> float:
    """Rozier's ``mu(n) = log rad(n) + sum_{p|n} log(nu_p(n))``."""

    if n < 1:
        raise ValueError("mu expects a positive integer")
    if n == 1:
        return 0.0
    return mu_from_factorization(factorint(n))


def _merge_factorizations(*items: dict[int, int]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for factors in items:
        for prime, exponent in factors.items():
            merged[prime] = merged.get(prime, 0) + exponent
    return merged


def mu_hit_gain(a: int, b: int, c: int) -> float:
    """Return ``log(c) - mu(abc)`` for a candidate triple."""

    if a < 1 or b < 1 or c < 1:
        raise ValueError("mu-hit triples must be positive")
    factors = _merge_factorizations(factorint(a), factorint(b), factorint(c))
    return math.log(c) - mu_from_factorization(factors)


def is_mu_hit(a: int, b: int, c: int) -> bool:
    """Check whether ``(a,b,c)`` is a Rozier mu-hit."""

    if a + b != c or gcd(a, b) != 1:
        return False
    return mu_hit_gain(a, b, c) > 0.0


def enumerate_N_j(j: int) -> list[int]:
    """Return the j elements of Rozier's ``N(j)`` below ``2^j``.

    Rozier's equation (7) is ``n == -1 - (2/3)^k mod 2^j`` for the element
    whose unique even shortcut iterate occurs at position ``k``.
    """

    if j < 2:
        raise ValueError("j must be at least two")
    modulus = 1 << j
    values: list[int] = []
    for k in range(j):
        inverse = pow(3, -k, modulus)
        values.append((-1 - (pow(2, k, modulus) * inverse)) % modulus)
    return values


def _shortcut_orbit_prefix(n: int, length: int) -> tuple[int, ...]:
    values: list[int] = []
    x = n
    for _ in range(length):
        values.append(x)
        x = shortcut_T(x)
    return tuple(values)


def theorem_4_1_check(n: int, j: int) -> dict[str, Any]:
    """Check Rozier Theorem 4.1 for one shortcut orbit prefix.

    The paper's statement uses the mu-hit ``(1, b, b+1)`` with
    ``b = T^k(n) + 1``. The prompt variant ``(1, T^k(n), T^k(n)+1)`` is
    also recorded for comparison.
    """

    if n <= 0:
        raise ValueError("n must be positive")
    if j < 2:
        raise ValueError("j must be at least two")
    orbit = _shortcut_orbit_prefix(n, j)
    even_positions = [index for index, value in enumerate(orbit) if value % 2 == 0]
    if len(even_positions) != 1:
        raise ValueError("n is not in N(j): expected exactly one even term")
    k = even_positions[0]
    tk = orbit[k]
    lower_bound_satisfied = (n + 1) * 3 * j * j > (1 << (j + 1))
    theorem_b = tk + 1
    theorem_gain = mu_hit_gain(1, theorem_b, theorem_b + 1)
    theorem_mu_hit = theorem_gain > 0.0
    prompt_gain = mu_hit_gain(1, tk, tk + 1)
    prompt_mu_hit = prompt_gain > 0.0
    return {
        "n": n,
        "j": j,
        "k": k,
        "T_k_n": tk,
        "lower_bound_satisfied": lower_bound_satisfied,
        "mu_hit_found": theorem_mu_hit,
        "mu_hit_gain": theorem_gain,
        "mu_hit_triple": [1, theorem_b, theorem_b + 1],
        "prompt_variant_mu_hit_found": prompt_mu_hit,
        "prompt_variant_gain": prompt_gain,
        "prompt_variant_triple": [1, tk, tk + 1],
        "theorem_4_1_violation": not (lower_bound_satisfied or theorem_mu_hit),
    }


def theorem_4_1_audit(
    j_min: int = 10,
    j_max: int = 50,
) -> tuple[dict[str, dict[str, int]], list[dict[str, int]]]:
    """Run the finite Theorem 4.1 sanity check for ``j_min <= j <= j_max``."""

    summaries: dict[str, dict[str, int]] = {}
    violations: list[dict[str, int]] = []
    for j in range(j_min, j_max + 1):
        stats = {
            "n_count": 0,
            "lower_bound_satisfied_count": 0,
            "mu_hit_found_count": 0,
            "both_count": 0,
            "neither_count": 0,
            "i_only_count": 0,
            "ii_only_count": 0,
            "theorem_4_1_violation_count": 0,
        }
        for n in enumerate_N_j(j):
            check = theorem_4_1_check(n, j)
            lower = bool(check["lower_bound_satisfied"])
            hit = bool(check["mu_hit_found"])
            stats["n_count"] += 1
            stats["lower_bound_satisfied_count"] += int(lower)
            stats["mu_hit_found_count"] += int(hit)
            stats["both_count"] += int(lower and hit)
            stats["i_only_count"] += int(lower and not hit)
            stats["ii_only_count"] += int(hit and not lower)
            stats["neither_count"] += int(not lower and not hit)
            if check["theorem_4_1_violation"]:
                stats["theorem_4_1_violation_count"] += 1
                violations.append({"j": j, "k": check["k"], "n": n})
        summaries[str(j)] = stats
    return summaries, violations


def _partial_mu_upper_from_factorization(factors: dict[int, int]) -> float:
    """Upper-bound mu when factorint may contain composite cofactors."""

    total = 0.0
    for base, exponent in factors.items():
        total += math.log(base)
        if exponent > 1:
            total += math.log(exponent)
    return total


def _n239_family_entry(
    k: int,
    factor_limit: int = 1_000_000,
    exact_digit_limit: int = 20,
) -> dict[str, Any]:
    n = 239
    exponent = 1 << k
    c_log = exponent * math.log(n)
    c_digits = int(c_log / math.log(10)) + 1
    predicted = math.log(2 * 13**3 / 239) - math.log(k + 4)
    known_b_factors = {2: k + 4, 13: 4}
    known_factor_log = (k + 4) * math.log(2) + 4 * math.log(13)
    known_factor_mu = mu_from_factorization(known_b_factors)
    mu_c = math.log(n) + math.log(exponent)
    log_b = math.log(math.expm1(c_log)) if c_log < 700 else c_log
    upper_mu_b = known_factor_mu + log_b - known_factor_log
    gain_lower_bound = c_log - mu_c - upper_mu_b
    factors_b = known_b_factors
    fully_factored = False
    exact_gain = None
    exact_mu_hit = None

    if c_digits <= exact_digit_limit:
        c = pow(n, exponent)
        b = c - 1
        factors_b = factorint(b, limit=factor_limit)
        fully_factored = all(isprime(base) for base in factors_b)
    if fully_factored and c_digits <= exact_digit_limit:
        c = pow(n, exponent)
        b = c - 1
        exact_gain = mu_hit_gain(1, b, c)
        exact_mu_hit = exact_gain > 0.0
        gain_lower_bound = exact_gain
    elif gain_lower_bound > 0.0:
        exact_mu_hit = True
    return {
        "k": k,
        "c": f"239^(2^{k})",
        "c_digits": c_digits,
        "mu_hit": exact_mu_hit,
        "exact_gain": exact_gain,
        "gain": gain_lower_bound,
        "gain_kind": (
            "exact"
            if exact_gain is not None
            else "certified_lower_bound_from_known_divisibility"
        ),
        "partial_factor_limit": factor_limit,
        "exact_digit_limit": exact_digit_limit,
        "partial_factorization_complete": fully_factored,
        "predicted_lower_bound": predicted,
        "predicted_lower_bound_holds": gain_lower_bound + 1e-8 >= predicted,
        "known_factors": {
            str(base): exponent for base, exponent in sorted(factors_b.items())
        },
    }


def n239_family_extension(
    k_min: int = 2,
    k_max: int = 20,
    factor_limit: int = 1_000_000,
) -> list[dict[str, Any]]:
    """Extend Rozier's ``(1,239^(2^k)-1,239^(2^k))`` computation."""

    return [
        _n239_family_entry(k, factor_limit=factor_limit)
        for k in range(k_min, k_max + 1)
    ]


def orbit_mu_hit_search(
    sample_count: int = 10_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 230615284,
    time_budget_seconds: float = 300.0,
    max_steps_per_orbit: int = 10_000,
) -> dict[str, Any]:
    """Search sampled accelerated odd Collatz orbits for Rozier mu-hits."""

    started = time.perf_counter()
    rng = random.Random(random_seed)
    hits: list[dict[str, Any]] = []
    completed_orbits = 0
    cache: dict[int, bool] = {1: True}

    def reaches_one(x: int) -> bool:
        path: list[int] = []
        y = x
        for _ in range(max_steps_per_orbit):
            if y in cache:
                result = cache[y]
                for item in path:
                    cache[item] = result
                return result
            path.append(y)
            y = accelerated_odd_step(y)
        for item in path:
            cache[item] = False
        return False

    for _ in range(sample_count):
        if time.perf_counter() - started >= time_budget_seconds:
            break
        start = rng.randrange(start_min | 1, start_max + 1, 2)
        if not reaches_one(start):
            continue
        completed_orbits += 1
        x = start
        for position in range(max_steps_per_orbit):
            if time.perf_counter() - started >= time_budget_seconds:
                break
            gain1 = mu_hit_gain(1, x, x + 1)
            if gain1 > 0.0:
                hits.append(
                    {
                        "starting_n": start,
                        "position_in_orbit": position,
                        "mu_hit_value": x,
                        "triple": [1, x, x + 1],
                        "gain": gain1,
                    }
                )
            if x > 1:
                triple2 = (2, x - 1, x + 1)
                if gcd(triple2[0], triple2[1]) == 1:
                    gain2 = mu_hit_gain(*triple2)
                    if gain2 > 0.0:
                        hits.append(
                            {
                                "starting_n": start,
                                "position_in_orbit": position,
                                "mu_hit_value": x,
                                "triple": list(triple2),
                                "gain": gain2,
                            }
                        )
            if x == 1:
                break
            x = accelerated_odd_step(x)

    hits.sort(key=lambda item: item["gain"], reverse=True)
    return {
        "sample_count_requested": sample_count,
        "sample_count_completed": completed_orbits,
        "random_seed": random_seed,
        "elapsed_seconds": time.perf_counter() - started,
        "time_budget_seconds": time_budget_seconds,
        "hits": hits[:100],
        "hit_count": len(hits),
        "status": (
            "time_budget_reached"
            if completed_orbits < sample_count
            else "sample_complete"
        ),
    }


@dataclass(frozen=True)
class RozierABCAuditReport:
    type: str
    status: str
    caveat: str
    theorem_4_1_results: dict[str, dict[str, int]]
    theorem_4_1_violations: list[dict[str, int]]
    n_239_family_extension: list[dict[str, Any]]
    orbit_mu_hits: list[dict[str, Any]]
    summary: dict[str, Any]
    scan_policy: dict[str, Any]
    source_notes: dict[str, str]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "theorem_4_1_results": self.theorem_4_1_results,
            "theorem_4_1_violations": self.theorem_4_1_violations,
            "n_239_family_extension": self.n_239_family_extension,
            "orbit_mu_hits": self.orbit_mu_hits,
            "summary": self.summary,
            "scan_policy": self.scan_policy,
            "source_notes": self.source_notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json() + "\n")


def rozier_abc_audit_report(
    j_min: int = 10,
    j_max: int = 50,
    n239_k_min: int = 2,
    n239_k_max: int = 20,
    n239_factor_limit: int = 1_000_000,
    orbit_sample_count: int = 10_000,
    orbit_time_budget_seconds: float = 300.0,
) -> RozierABCAuditReport:
    """Run the combined Rozier abc/Collatz finite audit."""

    theorem_results, theorem_violations = theorem_4_1_audit(j_min, j_max)
    family = n239_family_extension(
        k_min=n239_k_min,
        k_max=n239_k_max,
        factor_limit=n239_factor_limit,
    )
    orbit_search = orbit_mu_hit_search(
        sample_count=orbit_sample_count,
        time_budget_seconds=orbit_time_budget_seconds,
    )
    predicted_holds = all(
        bool(entry["predicted_lower_bound_holds"]) for entry in family
    )
    known_deeper_hits = [
        entry for entry in family if entry["k"] >= 15 and entry["mu_hit"] is True
    ]
    summary = {
        "theorem_4_1_holds_empirically": not theorem_violations,
        "theorem_4_1_total_violations": len(theorem_violations),
        "mu_hits_in_orbit_cache_count": orbit_search["hit_count"],
        "orbit_sample_count_completed": orbit_search["sample_count_completed"],
        "orbit_search_status": orbit_search["status"],
        "predicted_lower_bound_holds_for_n239_family": predicted_holds,
        "n239_exact_deeper_mu_hits_found_count": len(known_deeper_hits),
        "n239_exact_status_note": (
            "Exact mu-hit status is reported only when the bounded "
            "factorization finished; otherwise gain is a certified lower bound "
            "from partial factorization."
        ),
    }
    return RozierABCAuditReport(
        type="rozier_abc_collatz_audit",
        status="finite_empirical_diagnostic_complete",
        caveat=(
            "This is a finite empirical diagnostic and a finite sanity check "
            "of Rozier's Theorem 4.1, not a proof of Collatz or of any abc-type "
            "conjecture. Large n=239 family entries use bounded factorization "
            "certificates where complete factorization is infeasible."
        ),
        theorem_4_1_results=theorem_results,
        theorem_4_1_violations=theorem_violations,
        n_239_family_extension=family,
        orbit_mu_hits=orbit_search["hits"],
        summary=summary,
        scan_policy={
            "j_min": j_min,
            "j_max": j_max,
            "n239_k_min": n239_k_min,
            "n239_k_max": n239_k_max,
            "n239_factor_limit": n239_factor_limit,
            "orbit_sample_count": orbit_sample_count,
            "orbit_time_budget_seconds": orbit_time_budget_seconds,
        },
        source_notes={
            "N_j_congruence": (
                "Rozier arXiv:2306.15284v2 equation (7): "
                "n == -1 - (2/3)^k mod 2^j."
            ),
            "theorem_4_1_mu_hit_shift": (
                "Theorem 4.1 uses (1,b,b+1) with b = T^k(n)+1; "
                "the prompt variant with b = T^k(n) is recorded separately "
                "inside theorem_4_1_check but is not the theorem predicate."
            ),
        },
    )
