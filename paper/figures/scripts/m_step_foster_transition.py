#!/usr/bin/env python3
"""Plot m-step obstruction counts and residual table."""

from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.compression"] = 0
import matplotlib.pyplot as plt


random.seed(0)

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/reports/m_step_foster_drift.json"
OUT = Path(__file__).resolve().parents[1] / "m_step_foster_transition.pdf"


def main() -> None:
    data = json.loads(ARTIFACT.read_text())
    m_values = data["m_steps_grid"]

    strict_counts = []
    eps_counts = []
    for m in m_values:
        strict_counts.append(
            max(
                row["strict_residue_obstruction_count"]
                for window in data["window_reports"]
                for row in window["m_step_reports"]
                if row["m"] == m
            )
        )
        eps_counts.append(
            max(
                row["eps_0p1_residue_obstruction_count"]
                for window in data["window_reports"]
                for row in window["m_step_reports"]
                if row["m"] == m
            )
        )

    residuals = [row["max_window_residual"] for row in data["m_step_drift_residual_table"]]

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    ax1.plot(m_values, strict_counts, marker="o", label="strict obstructions")
    ax1.plot(m_values, eps_counts, marker="s", label="epsilon=0.1 obstructions")
    ax1.set_xscale("log", base=2)
    ax1.set_xlabel("m")
    ax1.set_ylabel("max obstruction count")
    ax1.grid(True, linewidth=0.35, alpha=0.45)

    ax2 = ax1.twinx()
    ax2.plot(m_values, residuals, color="#f58518", marker="^", label="residual table")
    ax2.set_ylabel("max window residual")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="upper center")
    ax1.set_title("m-step Foster transition")
    fig.tight_layout()
    fig.savefig(
        OUT,
        metadata={"Creator": "collatz-renewal-framework", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
