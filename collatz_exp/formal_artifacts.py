"""Machine-readable certificate artifacts and a local independent verifier."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .certificates import DescentCertificate, verify_descent_certificate


@dataclass(frozen=True)
class CertificateArtifact:
    type: str
    status: str
    residue: str
    modulus_power: int
    word: tuple[int, ...]
    m: int
    A: int
    B: str
    threshold_num: str
    threshold_den: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["word"] = list(self.word)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class FormalArtifactReport:
    type: str
    status: str
    exported: int
    verified: bool
    lean_skeleton_status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def certificate_artifact(certificate: DescentCertificate) -> CertificateArtifact:
    if not verify_descent_certificate(certificate):
        raise ValueError("cannot export invalid certificate")
    return CertificateArtifact(
        type="descent_certificate",
        status="machine_readable_certificate_verified_by_local_integer_checker",
        residue=str(certificate.residue),
        modulus_power=certificate.modulus_power,
        word=certificate.word,
        m=certificate.m,
        A=certificate.A,
        B=str(certificate.B),
        threshold_num=str(certificate.threshold_num),
        threshold_den=str(certificate.threshold_den),
    )


def certificate_from_artifact(data: dict[str, Any]) -> DescentCertificate:
    if data.get("type") != "descent_certificate":
        raise ValueError("unsupported artifact type")
    return DescentCertificate(
        residue=int(data["residue"]),
        modulus_power=int(data["modulus_power"]),
        word=tuple(int(value) for value in data["word"]),
        m=int(data["m"]),
        A=int(data["A"]),
        B=int(data["B"]),
        threshold_num=int(data["threshold_num"]),
        threshold_den=int(data["threshold_den"]),
    )


def verify_certificate_artifact(data: dict[str, Any]) -> bool:
    try:
        certificate = certificate_from_artifact(data)
    except (KeyError, TypeError, ValueError):
        return False
    return verify_descent_certificate(certificate)


def lean_skeleton(certificate: DescentCertificate, theorem_name: str = "collatz_descent_cert") -> str:
    """Emit an unchecked Lean-style theorem skeleton for future formalization."""

    return "\n".join(
        [
            f"-- unchecked template for {certificate.residue} mod 2^{certificate.modulus_power}",
            f"theorem {theorem_name} : True := by",
            "  -- TODO: expand affine identity and threshold inequality in Lean",
            "  trivial",
        ]
    )


def formal_artifact_report(certificate: DescentCertificate) -> FormalArtifactReport:
    artifact = certificate_artifact(certificate)
    return FormalArtifactReport(
        type="formal_certificate_artifact_report",
        status=artifact.status,
        exported=1,
        verified=verify_certificate_artifact(artifact.to_json_dict()),
        lean_skeleton_status="lean_skeleton_unchecked_template_not_formal_proof",
    )
