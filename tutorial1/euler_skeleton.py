"""Tutorial 1 explicit-Euler scaffold and Van der Pol challenge.

The solver is deliberately dimension-agnostic: ``rhs`` receives the whole
state vector and NumPy performs the component arithmetic in one expression.
Run ``python tutorial1/euler_skeleton.py`` to execute all checks and generate
the oracle phase-plane plot.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

Array = np.ndarray
RHS = Callable[[float, Array], Array]
Exact = Callable[[float], Array]


def explicit_euler(rhs: RHS, t0: float, t1: float, y0: Sequence[float], h: float) -> tuple[Array, Array]:
    """Integrate ``y'=rhs(t,y)`` with explicit Euler.

    The time buffer has ``n_steps + 1`` entries.  A final shortened step is
    allowed for general intervals; the tutorial's prescribed steps divide T
    exactly, so no shortened step occurs there.
    """

    if h <= 0 or t1 <= t0:
        raise ValueError("require t1 > t0 and h > 0")
    y0_arr = np.asarray(y0, dtype=float)
    if y0_arr.ndim != 1:
        raise ValueError("y0 must be a one-dimensional state vector")
    n_steps = int(np.ceil((t1 - t0) / h - 1e-14))
    t = np.empty(n_steps + 1, dtype=float)
    y = np.empty((n_steps + 1, y0_arr.size), dtype=float)
    t[0] = t0
    y[0] = y0_arr
    for n in range(n_steps):
        step = min(h, t1 - t[n])
        y[n + 1] = y[n] + step * np.asarray(rhs(t[n], y[n]), dtype=float)
        t[n + 1] = t[n] + step
    t[-1] = t1  # remove round-off in the endpoint
    return t, y


def convergence_study(rhs: RHS, exact: Exact, t0: float, t1: float,
                      y0: Sequence[float], hs: Sequence[float]) -> tuple[Array, Array, float]:
    """Return step sizes, max-norm errors, and the observed log-log order."""

    hs_arr = np.asarray(hs, dtype=float)
    errors = np.empty(hs_arr.size, dtype=float)
    for i, h in enumerate(hs_arr):
        t, y = explicit_euler(rhs, t0, t1, y0, float(h))
        reference = np.stack([np.asarray(exact(float(ti)), dtype=float) for ti in t])
        errors[i] = np.max(np.abs(y - reference))
    order = float(np.polyfit(np.log(hs_arr), np.log(errors), 1)[0])
    return hs_arr, errors, order


def logistic_rhs(r: float = 2.0, K: float = 3.0) -> RHS:
    def rhs(_t: float, y: Array) -> Array:
        return r * y * (1.0 - y / K)
    return rhs


def logistic_exact(y0: float, r: float = 2.0, K: float = 3.0) -> Exact:
    def exact(t: float) -> Array:
        value = K / (1.0 + (K / y0 - 1.0) * np.exp(-r * t))
        return np.array([value])
    return exact


def vanderpol_rhs(mu: float = 1.0) -> RHS:
    def rhs(_t: float, y: Array) -> Array:
        return np.array([y[1], mu * (1.0 - y[0] ** 2) * y[1] - y[0]])
    return rhs


def make_vanderpol_oracle(rhs: RHS, y0: Sequence[float], t1: float) -> Exact:
    """Build a dense, high-accuracy reference using independent DOP853."""

    sol = solve_ivp(rhs, [0.0, t1], np.asarray(y0, dtype=float), method="DOP853",
                    rtol=1e-12, atol=1e-14, dense_output=True)
    if not sol.success or sol.sol is None:
        raise RuntimeError(f"oracle solve failed: {sol.message}")

    def exact(t: float) -> Array:
        return np.asarray(sol.sol(t), dtype=float).reshape(-1)
    return exact


def run_checks(output_dir: Path) -> dict[str, float]:
    """Run the analytic logistic check and the prescribed Van der Pol task."""

    # Analytic scalar check: confirms the generic vector-state implementation.
    logistic = logistic_rhs()
    _, logistic_errors, logistic_order = convergence_study(
        logistic, logistic_exact(0.4), 0.0, 1.0, [0.4], [0.2, 0.1, 0.05, 0.025])
    if not (0.8 < logistic_order < 1.2):
        raise AssertionError(f"logistic observed order {logistic_order:.3f} is not first order")
    print(f"PASS logistic: observed order = {logistic_order:.2f}, final error = {logistic_errors[-1]:.3e}")

    # Individual challenge: mu=1, y(0)=(0.5,0), T=10.
    y0 = np.array([0.5, 0.0])
    t1 = 10.0
    rhs = vanderpol_rhs(mu=1.0)
    exact = make_vanderpol_oracle(rhs, y0, t1)
    hs = [0.1, 0.05, 0.025, 0.0125]
    hs_arr, errors, order = convergence_study(rhs, exact, 0.0, t1, y0, hs)
    oracle_terminal = exact(t1)
    if not (0.7 < order < 1.3):
        raise AssertionError(f"Van der Pol observed order {order:.3f} is not first order")

    output_dir.mkdir(parents=True, exist_ok=True)
    phase_path = output_dir / "vanderpol_phase_plane.png"
    dense_t = np.linspace(0.0, t1, 4000)
    trajectory = np.stack([exact(float(ti)) for ti in dense_t])
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    ax.plot(trajectory[:, 0], trajectory[:, 1], color="#2c7fb8", linewidth=1.2)
    ax.scatter([y0[0]], [y0[1]], color="#d95f02", s=24, zorder=3, label="initial state")
    ax.set(xlabel=r"$y_1(t)$", ylabel=r"$y_2(t)$",
           title=r"Van der Pol parametric curve ($\mu=1$, $0\leq t\leq 10$)")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(phase_path, dpi=150)
    plt.close(fig)

    print("PASS Van der Pol:")
    print("  h          max error")
    for h, error in zip(hs_arr, errors):
        print(f"  {h:<10g} {error:.6e}")
    print(f"  observed order = {order:.2f}")
    print(f"  oracle y1(T) = {oracle_terminal[0]:.3f}")
    print(f"  phase plot = {phase_path}")
    return {"logistic_order": logistic_order, "vanderpol_order": order,
            "vanderpol_y1_T": float(oracle_terminal[0])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).parent / "figures")
    args = parser.parse_args()
    run_checks(args.output_dir)
    print("PASS all Tutorial 1 checks")


if __name__ == "__main__":
    main()
