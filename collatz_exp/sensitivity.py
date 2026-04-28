"""Sensitivity diagnostics for Collatz-derived maps."""

from __future__ import annotations

from dataclasses import dataclass

from .tuple_merges import collatz_step


@dataclass(frozen=True)
class SensitivitySample:
    n: int
    flipped: int
    steps: int
    hamming_distance: int


@dataclass(frozen=True)
class SensitivityReport:
    type: str
    status: str
    start: int
    count: int
    bit: int
    steps: int
    width: int
    samples: tuple[SensitivitySample, ...]
    mean_hamming_distance: float
    max_hamming_distance: int


def iterate_collatz(n: int, steps: int) -> int:
    """Apply the ordinary Collatz map for a fixed number of steps."""

    if n <= 0:
        raise ValueError("n must be positive")
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    x = n
    for _ in range(steps):
        x = collatz_step(x)
    return x


def hamming_distance(a: int, b: int, width: int) -> int:
    """Hamming distance after masking to ``width`` low bits."""

    if width < 1:
        raise ValueError("width must be positive")
    mask = (1 << width) - 1
    return ((a ^ b) & mask).bit_count()


def sensitivity_report(
    start: int = 1,
    count: int = 128,
    bit: int = 0,
    steps: int = 32,
    width: int = 64,
) -> SensitivityReport:
    """Measure finite bit-flip sensitivity after fixed Collatz iterations."""

    if count < 1:
        raise ValueError("count must be positive")
    if bit < 0:
        raise ValueError("bit must be nonnegative")
    samples: list[SensitivitySample] = []
    for n in range(start, start + count):
        flipped = n ^ (1 << bit)
        if flipped == 0:
            flipped = n | (1 << bit)
        image = iterate_collatz(n, steps)
        flipped_image = iterate_collatz(flipped, steps)
        samples.append(
            SensitivitySample(
                n=n,
                flipped=flipped,
                steps=steps,
                hamming_distance=hamming_distance(image, flipped_image, width),
            )
        )
    distances = [sample.hamming_distance for sample in samples]
    return SensitivityReport(
        type="collatz_sensitivity_report",
        status="finite_chaos_diagnostic_not_collatz_proof",
        start=start,
        count=count,
        bit=bit,
        steps=steps,
        width=width,
        samples=tuple(samples),
        mean_hamming_distance=sum(distances) / len(distances),
        max_hamming_distance=max(distances),
    )
