"""Terras-style parity-vector artifacts for the accelerated-by-one Collatz map.

Here ``T(n) = n/2`` for even ``n`` and ``T(n) = (3n+1)/2`` for odd ``n``.
For any fixed parity vector of length ``k`` there is exactly one residue
class modulo ``2^k`` that realizes it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import comb
from typing import Any


@dataclass(frozen=True)
class ParityAffine:
    bits: tuple[int, ...]
    odd_steps: int
    divisions: int
    offset: int
    residue: int
    coefficient_num: int
    coefficient_den: int
    descent_threshold: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ParityLayerReport:
    type: str
    status: str
    length: int
    vectors: int
    favorable_vectors: int
    favorable_density_num: int
    favorable_density_den: int
    worst_threshold: int | None
    top_thresholds: tuple[ParityAffine, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "length": self.length,
            "vectors": self.vectors,
            "favorable_vectors": self.favorable_vectors,
            "favorable_density_num": self.favorable_density_num,
            "favorable_density_den": self.favorable_density_den,
            "worst_threshold": self.worst_threshold,
            "top_thresholds": [
                item.to_json_dict() for item in self.top_thresholds
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def terras_step(n: int) -> int:
    """One step of Terras' halved Collatz map."""

    if n <= 0:
        raise ValueError("n must be positive")
    if n % 2 == 0:
        return n // 2
    return (3 * n + 1) // 2


def parity_vector(n: int, length: int) -> tuple[int, ...]:
    """Return the first ``length`` parity bits under the Terras map."""

    if length < 0:
        raise ValueError("length must be nonnegative")
    x = n
    bits: list[int] = []
    for _ in range(length):
        bits.append(x % 2)
        x = terras_step(x)
    return tuple(bits)


def affine_for_parity(bits: tuple[int, ...]) -> tuple[int, int, int]:
    """Return ``(odd_steps, divisions, offset)`` for a parity vector.

    After ``k`` Terras steps with ``q`` odd steps,
    ``T^k(n) = (3^q*n + offset) / 2^k``.
    """

    q = 0
    offset = 0
    for index, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError("parity bits must be 0 or 1")
        if bit:
            offset = 3 * offset + (1 << index)
            q += 1
    return q, len(bits), offset


def residue_for_parity(bits: tuple[int, ...]) -> int:
    """Return the unique residue modulo ``2^len(bits)`` realizing ``bits``."""

    residue = 0
    modulus = 1
    prefix: list[int] = []
    for bit in bits:
        q, _, offset = affine_for_parity(tuple(prefix))
        candidates = (residue, residue + modulus)
        for candidate in candidates:
            current = (3**q * candidate + offset) // modulus
            if current % 2 == bit:
                residue = candidate
                break
        else:
            raise RuntimeError("failed to lift parity residue")
        prefix.append(bit)
        modulus <<= 1
    return residue % modulus


def parity_affine(bits: tuple[int, ...]) -> ParityAffine:
    """Build the exact affine/residue artifact for one parity vector."""

    q, k, offset = affine_for_parity(bits)
    residue = residue_for_parity(bits)
    den = 1 << k
    num = 3**q
    threshold = None
    if num < den:
        threshold = offset // (den - num) + 1
    return ParityAffine(
        bits=bits,
        odd_steps=q,
        divisions=k,
        offset=offset,
        residue=residue,
        coefficient_num=num,
        coefficient_den=den,
        descent_threshold=threshold,
    )


def parity_layer_report(length: int = 16, top_n: int = 12) -> ParityLayerReport:
    """Summarize all parity cylinders of a fixed length."""

    if length < 1:
        raise ValueError("length must be positive")
    if top_n < 1:
        raise ValueError("top_n must be positive")
    vectors = tuple(
        parity_affine(
            tuple((mask >> index) & 1 for index in range(length))
        )
        for mask in range(1 << length)
    )
    favorable = tuple(item for item in vectors if item.descent_threshold is not None)
    sorted_thresholds = tuple(
        sorted(
            favorable,
            key=lambda item: (
                item.descent_threshold if item.descent_threshold is not None else -1,
                item.odd_steps,
            ),
            reverse=True,
        )[:top_n]
    )
    favorable_count = sum(comb(length, q) for q in range(length + 1) if 3**q < (1 << length))
    return ParityLayerReport(
        type="parity_layer_report",
        status="finite_terras_parity_layer_not_collatz_proof",
        length=length,
        vectors=1 << length,
        favorable_vectors=len(favorable),
        favorable_density_num=favorable_count,
        favorable_density_den=1 << length,
        worst_threshold=max(
            item.descent_threshold for item in favorable if item.descent_threshold is not None
        ),
        top_thresholds=sorted_thresholds,
    )
