"""Proof-facing certificate cover database and resumable search."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from heapq import heappop, heappush
from itertools import count
from pathlib import Path
from typing import Any

from .certificates import (
    DescentCertificate,
    certificate_from_residue,
    verify_descent_certificate,
)
from .formal_artifacts import certificate_artifact
from .search import forced_trace_for_residue


@dataclass
class _TrieNode:
    certificate_index: int | None = None
    children: dict[int, "_TrieNode"] = field(default_factory=dict)


class CertificateCover:
    """Binary low-bit trie of certified residue cylinders."""

    def __init__(self, certificates: tuple[DescentCertificate, ...] = ()) -> None:
        self._root = _TrieNode()
        self._certificates: list[DescentCertificate] = []
        for certificate in certificates:
            self.add(certificate)

    @property
    def certificates(self) -> tuple[DescentCertificate, ...]:
        active: list[DescentCertificate] = []

        def walk(node: _TrieNode) -> None:
            if node.certificate_index is not None:
                active.append(self._certificates[node.certificate_index])
                return
            for child in node.children.values():
                walk(child)

        walk(self._root)
        return tuple(active)

    def add(self, certificate: DescentCertificate) -> bool:
        """Insert a verified certificate, unless already covered."""

        if not verify_descent_certificate(certificate, verify_exceptions=True):
            raise ValueError("invalid descent certificate")
        if self.covering_certificate(certificate.residue, certificate.modulus_power):
            return False

        node = self._root
        for bit_index in range(certificate.modulus_power):
            bit = (certificate.residue >> bit_index) & 1
            node = node.children.setdefault(bit, _TrieNode())
            if node.certificate_index is not None:
                return False

        node.certificate_index = len(self._certificates)
        node.children = {}
        self._certificates.append(certificate)
        return True

    def covering_certificate(
        self, residue: int, modulus_power: int
    ) -> DescentCertificate | None:
        """Return a certificate covering ``residue mod 2^modulus_power``."""

        if modulus_power < 1:
            raise ValueError("modulus_power must be positive")
        if residue % 2 == 0:
            raise ValueError("residue must be odd")

        node = self._root
        if node.certificate_index is not None:
            return self._certificates[node.certificate_index]

        for bit_index in range(modulus_power):
            bit = (residue >> bit_index) & 1
            child = node.children.get(bit)
            if child is None:
                return None
            node = child
            if node.certificate_index is not None:
                return self._certificates[node.certificate_index]
        return None

    def is_covered(self, residue: int, modulus_power: int) -> bool:
        return self.covering_certificate(residue, modulus_power) is not None

    def to_json_list(self) -> list[dict[str, Any]]:
        return [
            certificate_artifact(certificate).to_json_dict()
            for certificate in self._certificates
        ]


@dataclass(frozen=True)
class CoverFrontierNode:
    residue: int
    modulus_power: int

    def to_json_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class CertificateCoverReport:
    type: str
    status: str
    max_depth: int
    max_nodes: int
    nodes_processed: int
    certificates: tuple[DescentCertificate, ...]
    frontier: tuple[CoverFrontierNode, ...]
    depth_counts: dict[int, int]
    covered_pruned: int
    duplicate_certificates: int
    unresolved_odd_density_num: int
    unresolved_odd_density_den: int
    complete: bool

    @property
    def unresolved_odd_density(self) -> Fraction:
        return Fraction(self.unresolved_odd_density_num, self.unresolved_odd_density_den)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "max_depth": self.max_depth,
            "max_nodes": self.max_nodes,
            "nodes_processed": self.nodes_processed,
            "certificates": [
                certificate_artifact(certificate).to_json_dict()
                for certificate in self.certificates
            ],
            "frontier": [node.to_json_dict() for node in self.frontier],
            "depth_counts": {str(k): v for k, v in sorted(self.depth_counts.items())},
            "covered_pruned": self.covered_pruned,
            "duplicate_certificates": self.duplicate_certificates,
            "unresolved_odd_density_num": self.unresolved_odd_density_num,
            "unresolved_odd_density_den": self.unresolved_odd_density_den,
            "complete": self.complete,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")


def certificate_from_json_dict(data: dict[str, Any]) -> DescentCertificate:
    return DescentCertificate(
        residue=int(data["residue"]),
        modulus_power=int(data["modulus_power"]),
        word=tuple(int(value) for value in data["word"]),
        A=int(data["A"]),
        B=int(data["B"]),
        m=int(data["m"]),
        threshold_num=int(data["threshold_num"]),
        threshold_den=int(data["threshold_den"]),
    )


def cover_report_from_json_dict(data: dict[str, Any]) -> CertificateCoverReport:
    return CertificateCoverReport(
        type=str(data["type"]),
        status=str(data["status"]),
        max_depth=int(data["max_depth"]),
        max_nodes=int(data["max_nodes"]),
        nodes_processed=int(data["nodes_processed"]),
        certificates=tuple(
            certificate_from_json_dict(item) for item in data["certificates"]
        ),
        frontier=tuple(
            CoverFrontierNode(
                residue=int(item["residue"]),
                modulus_power=int(item["modulus_power"]),
            )
            for item in data["frontier"]
        ),
        depth_counts={int(k): int(v) for k, v in data["depth_counts"].items()},
        covered_pruned=int(data["covered_pruned"]),
        duplicate_certificates=int(data["duplicate_certificates"]),
        unresolved_odd_density_num=int(data["unresolved_odd_density_num"]),
        unresolved_odd_density_den=int(data["unresolved_odd_density_den"]),
        complete=bool(data["complete"]),
    )


def load_cover_report(path: str | Path) -> CertificateCoverReport:
    return cover_report_from_json_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def frontier_density(frontier: tuple[CoverFrontierNode, ...]) -> Fraction:
    density = Fraction(0, 1)
    for node in frontier:
        density += Fraction(1, 1 << (node.modulus_power - 1))
    return density


def _push_frontier_node(
    heap: list[tuple[int, int, int, int, int]],
    sequence: count,
    node: CoverFrontierNode,
    max_certificate_steps: int,
    bucket_scale: int,
) -> None:
    trace = forced_trace_for_residue(
        node.residue,
        node.modulus_power,
        max_steps=max_certificate_steps,
        bucket_scale=bucket_scale,
    )
    heappush(
        heap,
        (
            node.modulus_power,
            -trace.bucket,
            next(sequence),
            node.residue,
            node.modulus_power,
        ),
    )


def _final_report(
    *,
    max_depth: int,
    max_nodes: int,
    nodes_processed: int,
    cover: CertificateCover,
    frontier: tuple[CoverFrontierNode, ...],
    depth_counts: dict[int, int],
    covered_pruned: int,
    duplicate_certificates: int,
    complete: bool,
) -> CertificateCoverReport:
    density = frontier_density(frontier)
    return CertificateCoverReport(
        type="certificate_cover_search_report",
        status="finite_cover_search_not_collatz_proof"
        if frontier
        else "finite_cover_closed_for_reported_root",
        max_depth=max_depth,
        max_nodes=max_nodes,
        nodes_processed=nodes_processed,
        certificates=cover.certificates,
        frontier=frontier,
        depth_counts=dict(depth_counts),
        covered_pruned=covered_pruned,
        duplicate_certificates=duplicate_certificates,
        unresolved_odd_density_num=density.numerator,
        unresolved_odd_density_den=density.denominator,
        complete=complete,
    )


def run_certificate_cover(
    max_depth: int = 18,
    max_nodes: int = 100_000,
    max_certificate_steps: int = 1_000,
    bucket_scale: int = 100,
    initial_report: CertificateCoverReport | None = None,
) -> CertificateCoverReport:
    """Run or resume a fair-priority certificate-cover search."""

    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    if max_nodes < 1:
        raise ValueError("max_nodes must be positive")

    cover = CertificateCover(initial_report.certificates if initial_report else ())
    frontier = (
        initial_report.frontier
        if initial_report is not None
        else (CoverFrontierNode(residue=1, modulus_power=1),)
    )
    heap: list[tuple[int, int, int, int, int]] = []
    sequence = count()
    for node in frontier:
        if not cover.is_covered(node.residue, node.modulus_power):
            _push_frontier_node(heap, sequence, node, max_certificate_steps, bucket_scale)

    depth_counts: dict[int, int] = (
        dict(initial_report.depth_counts) if initial_report else {}
    )
    nodes_processed = initial_report.nodes_processed if initial_report else 0
    covered_pruned = initial_report.covered_pruned if initial_report else 0
    duplicate_certificates = (
        initial_report.duplicate_certificates if initial_report else 0
    )
    terminal_frontier: list[CoverFrontierNode] = []

    while heap and nodes_processed < max_nodes:
        _, _, _, residue, modulus_power = heappop(heap)
        if cover.is_covered(residue, modulus_power):
            covered_pruned += 1
            continue

        nodes_processed += 1
        depth_counts[modulus_power] = depth_counts.get(modulus_power, 0) + 1

        certificate = certificate_from_residue(
            residue, modulus_power, max_steps=max_certificate_steps
        )
        if certificate is not None:
            if not cover.add(certificate):
                duplicate_certificates += 1
            continue

        if modulus_power >= max_depth:
            terminal_frontier.append(
                CoverFrontierNode(residue=residue, modulus_power=modulus_power)
            )
            continue

        children = (
            CoverFrontierNode(residue=residue, modulus_power=modulus_power + 1),
            CoverFrontierNode(
                residue=residue + (1 << modulus_power),
                modulus_power=modulus_power + 1,
            ),
        )
        for child in children:
            if cover.is_covered(child.residue, child.modulus_power):
                covered_pruned += 1
                continue
            _push_frontier_node(heap, sequence, child, max_certificate_steps, bucket_scale)

    remaining = tuple(terminal_frontier) + tuple(
        CoverFrontierNode(residue=residue, modulus_power=modulus_power)
        for _, _, _, residue, modulus_power in sorted(heap)
        if not cover.is_covered(residue, modulus_power)
    )
    return _final_report(
        max_depth=max_depth,
        max_nodes=max_nodes,
        nodes_processed=nodes_processed,
        cover=cover,
        frontier=remaining,
        depth_counts=depth_counts,
        covered_pruned=covered_pruned,
        duplicate_certificates=duplicate_certificates,
        complete=not remaining,
    )
