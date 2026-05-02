#!/usr/bin/env python3
"""Plot the positive k=6 one-step residue obstructions."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.compression"] = 0
import matplotlib.pyplot as plt


random.seed(0)

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/reports/phase_lyapunov_foster_drift.json"
OUT = Path(__file__).resolve().parents[1] / "foster_residue_obstruction.pdf"


def main() -> None:
    data = json.loads(ARTIFACT.read_text())
    by_residue: dict[int, list[dict]] = defaultdict(list)
    for item in data["residue_obstruction_witnesses"]:
        if item["k"] == 6:
            by_residue[item["residue"]].append(item)

    residues = sorted(by_residue)
    estimates = []
    lows = []
    highs = []
    for residue in residues:
        chosen = max(by_residue[residue], key=lambda row: row["drift"]["estimate"])
        drift = chosen["drift"]
        estimates.append(drift["estimate"])
        lows.append(drift["estimate"] - drift["ci_low"])
        highs.append(drift["ci_high"] - drift["estimate"])

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.axhline(0.0, color="0.25", linewidth=0.8)
    ax.bar([str(r) for r in residues], estimates, color="#4c78a8")
    ax.errorbar(
        [str(r) for r in residues],
        estimates,
        yerr=[lows, highs],
        fmt="none",
        ecolor="0.15",
        capsize=3,
        linewidth=1.0,
    )
    ax.set_xlabel("residue mod 64")
    ax.set_ylabel("one-step conditional drift")
    ax.set_title("Positive residue obstructions at k=6")
    ax.grid(axis="y", linewidth=0.35, alpha=0.45)
    fig.tight_layout()
    fig.savefig(
        OUT,
        metadata={"Creator": "collatz-renewal-framework", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
