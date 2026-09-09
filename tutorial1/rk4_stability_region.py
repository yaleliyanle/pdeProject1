"""Compute and plot the absolute-stability region of classical RK4.

This is the setup-week sanity check: it exercises NumPy, SciPy-independent
plotting, and the repository's figure-writing convention without displaying a
blocking GUI window.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def rk4_amplification(z: np.ndarray) -> np.ndarray:
    """Return the RK4 stability polynomial evaluated at complex ``z``."""

    return 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24


def make_stability_plot(output: Path, n: int = 700) -> None:
    """Write the contour ``|R(z)|=1`` to ``output``."""

    re = np.linspace(-4.5, 2.0, n)
    im = np.linspace(-4.5, 4.5, n)
    x, y = np.meshgrid(re, im)
    modulus = np.abs(rk4_amplification(x + 1j * y))

    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.contourf(x, y, modulus <= 1.0, levels=[0.5, 1.0], alpha=0.22,
                colors=["#4c78a8"])
    ax.contour(x, y, modulus, levels=[1.0], colors=["#1f4e79"], linewidths=1.5)
    ax.axhline(0.0, color="0.35", linewidth=0.7)
    ax.axvline(0.0, color="0.35", linewidth=0.7)
    ax.set(xlabel=r"Re$(z)$", ylabel=r"Im$(z)$",
           title="Classical RK4 absolute-stability region")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "figures" / "stability_regions.png")
    args = parser.parse_args()
    make_stability_plot(args.output)
    if not args.output.exists() or args.output.stat().st_size == 0:
        raise RuntimeError("stability plot was not written")
    print(f"PASS: wrote {args.output}")


if __name__ == "__main__":
    main()
