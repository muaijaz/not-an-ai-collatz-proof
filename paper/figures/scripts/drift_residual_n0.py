#!/usr/bin/env python3
"""Plot phase-decomposed renewal residuals from the saved JSON artifact."""

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
ARTIFACT = ROOT / "docs/reports/renewal_drift_phase_decomposed_n0_stability.json"
OUT = Path(__file__).resolve().parents[1] / "drift_residual_n0.pdf"


def series(rows: list[list[float]]) -> tuple[list[float], list[float], list[float]]:
    return [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]


def main() -> None:
    data = json.loads(ARTIFACT.read_text())
    x_total, y_total, e_total = series(data["total_drift_deviations"])
    x_post, y_post, e_post = series(data["post_exit_valuation_deviations"])

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.axhline(0.0, color="0.25", linewidth=0.8)
    ax.errorbar(
        x_total,
        y_total,
        yerr=e_total,
        marker="o",
        linewidth=1.4,
        capsize=3,
        label="total drift residual",
    )
    ax.errorbar(
        x_post,
        y_post,
        yerr=e_post,
        marker="s",
        linewidth=1.4,
        capsize=3,
        label="post-exit valuation residual",
    )
    ax.set_xlabel("midpoint log10 n")
    ax.set_ylabel("residual")
    ax.set_title("Phase-decomposed n0 stability")
    ax.legend(frameon=False)
    ax.grid(True, linewidth=0.35, alpha=0.45)
    fig.tight_layout()
    fig.savefig(
        OUT,
        metadata={"Creator": "collatz-renewal-framework", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
