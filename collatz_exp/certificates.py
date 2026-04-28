"""Residue-cylinder descent certificates."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .core import affine_from_word, accelerated_step


@dataclass(frozen=True)
class DescentCertificate:
    """A certificate that a residue cylinder eventually descends above a bound."""

    residue: int
    modulus_power: int
    word: tuple[int, ...]
    A: int
    B: int
    m: int
    threshold_num: int
    threshold_den: int

    @property
    def modulus(self) -> int:
        return 1 << self.modulus_power

    @property
    def threshold(self) -> Fraction:
        return Fraction(self.threshold_num, self.threshold_den)

    def summary(self) -> str:
        return (
            f"n == {self.residue} mod 2^{self.modulus_power}; "
            f"m={self.m}, A={self.A}, "
            f"threshold={self.threshold_num}/{self.threshold_den}"
        )

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["type"] = "descent_certificate"
        data["word"] = list(self.word)
        data["residue"] = str(self.residue)
        data["B"] = str(self.B)
        data["threshold_num"] = str(self.threshold_num)
        data["threshold_den"] = str(self.threshold_den)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def residue_for_word(word: tuple[int, ...]) -> int:
    """Return the unique residue modulo ``2^A`` that realizes ``word``."""

    affine = affine_from_word(word)
    modulus = 1 << affine.A
    inverse = pow(pow(3, affine.m, modulus), -1, modulus)
    return (-affine.B * inverse) % modulus


def certificate_from_word(word: tuple[int, ...]) -> DescentCertificate:
    """Build the exact descent certificate associated with a shrink-favorable word."""

    affine = affine_from_word(word)
    numerator = 1 << affine.A
    denominator = numerator - 3**affine.m
    if denominator <= 0:
        raise ValueError("word is not shrink-favorable: 2^A must exceed 3^m")

    threshold = Fraction(affine.B, denominator)
    return DescentCertificate(
        residue=residue_for_word(affine.word),
        modulus_power=affine.A,
        word=affine.word,
        A=affine.A,
        B=affine.B,
        m=affine.m,
        threshold_num=threshold.numerator,
        threshold_den=threshold.denominator,
    )


def certificate_from_residue(
    residue: int, modulus_power: int, max_steps: int = 1_000
) -> DescentCertificate | None:
    """Try to certify descent for the forced word from one ``mod 2^k`` node."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    if residue % 2 == 0:
        raise ValueError("residue must be odd")

    x = residue % (1 << modulus_power)
    if x == 0:
        x = 1 << modulus_power

    word: list[int] = []
    A = 0

    while len(word) < max_steps and A < modulus_power:
        x, a = accelerated_step(x)
        word.append(a)
        A += a
        if A <= modulus_power and (1 << A) > 3 ** len(word):
            cert = certificate_from_word(tuple(word))
            if residue % (1 << cert.modulus_power) == cert.residue:
                return cert

    return None


def verify_descent_certificate(
    certificate: DescentCertificate, verify_exceptions: bool = False
) -> bool:
    """Verify the exact algebra and optional finite below-threshold exceptions."""

    affine = affine_from_word(certificate.word)
    if (affine.A, affine.B, affine.m) != (
        certificate.A,
        certificate.B,
        certificate.m,
    ):
        return False

    if certificate.modulus_power != certificate.A:
        return False

    if certificate.residue != residue_for_word(certificate.word):
        return False

    denominator = (1 << certificate.A) - 3**certificate.m
    if denominator <= 0:
        return False

    threshold = Fraction(certificate.B, denominator)
    if (certificate.threshold_num, certificate.threshold_den) != (
        threshold.numerator,
        threshold.denominator,
    ):
        return False

    if verify_exceptions:
        modulus = 1 << certificate.modulus_power
        n = certificate.residue if certificate.residue > 1 else certificate.residue + modulus
        while n <= threshold:
            x = n
            for expected in certificate.word:
                x, actual = accelerated_step(x)
                if actual != expected:
                    return False
            if x >= n:
                return False
            n += modulus

    return True
