"""Small, NumPy-only companion to the Chinese Problem 4 tutorial.

Run from the package directory:
    python3 tutorial_zh/teaching_demo.py --self-check
    python3 tutorial_zh/teaching_demo.py --paths 2000 --seed 2026090804

This script prints results and never writes files. Its small grids, sample size,
and lack of control variates are for learning, not reproducing the full report.
"""
from __future__ import annotations

import argparse
import math
import platform

import numpy as np


GBM_LEVELS = (8, 16, 32, 64, 128, 256, 512)
COARSE = (16, 32, 64, 128)
REFERENCES = (256, 512, 1024)
PARAMETERS = dict(S0=100.0, Y0=0.0, mu=0.05, kappa=2.0,
                  theta=-0.2, xi=0.6, rho=-0.7, T=1.0,
                  strike=100.0, g_min=0.1, g_max=0.5)


class Moments:
    """Accumulate independent scalar observations in batches."""

    def __init__(self):
        self.n = 0
        self.total = 0.0
        self.total2 = 0.0

    def add(self, values):
        values = np.asarray(values, dtype=float)
        if values.ndim != 1 or not np.isfinite(values).all():
            raise ValueError("Expected one finite scalar observation per path")
        self.n += values.size
        self.total += float(values.sum())
        self.total2 += float(values @ values)

    def summary(self):
        if self.n < 2:
            raise ValueError("At least two paths are needed for a standard error")
        mean = self.total / self.n
        variance = max(0.0, (self.total2 - self.total * mean) / (self.n - 1))
        se = math.sqrt(variance / self.n)
        return mean, se, mean - 1.96 * se, mean + 1.96 * se


def gbm_endpoints(fine, n, s0=100.0, mu=0.05, sigma=0.3, T=1.0):
    """Path-major input: fine.shape == (number_of_paths, finest_steps)."""
    paths, finest = fine.shape
    if n < 1 or finest % n:
        raise ValueError("The requested grid must divide the finest grid")
    h = T / n
    dw = fine.reshape(paths, n, finest // n).sum(axis=2)
    exact = s0 * np.exp((mu - 0.5 * sigma**2) * T
                        + sigma * fine.sum(axis=1))
    base = 1.0 + mu * h + sigma * dw
    em = s0 * np.prod(base, axis=1)
    milstein = s0 * np.prod(base + 0.5 * sigma**2 * (dw * dw - h), axis=1)
    return exact, np.column_stack((em, milstein))


def logistic(y):
    """Evaluate 1/(1+exp(-y)) without exponentiating large positive values."""
    result = np.empty_like(y, dtype=float)
    nonnegative = y >= 0.0
    result[nonnegative] = 1.0 / (1.0 + np.exp(-y[nonnegative]))
    exp_y = np.exp(y[~nonnegative])
    result[~nonnegative] = exp_y / (1.0 + exp_y)
    return result


def nonaffine_terminal(fine, n, p=PARAMETERS):
    """Time-major input: fine.shape == (finest_steps, number_of_paths, 2)."""
    finest, paths, components = fine.shape
    if components != 2 or n < 1 or finest % n:
        raise ValueError("Expected two noises and a grid dividing the finest grid")
    dw = fine.reshape(n, finest // n, paths, 2).sum(axis=1)
    h = p["T"] / n
    x = np.full(paths, math.log(p["S0"]))
    y = np.full(paths, p["Y0"])
    for step in range(n):
        old_y = y.copy()
        g = p["g_min"] + (p["g_max"] - p["g_min"]) * logistic(old_y)
        x += (p["mu"] - 0.5 * g * g) * h + g * dw[step, :, 0]
        y += (p["kappa"] * (p["theta"] - old_y) * h
              + p["xi"] * np.sqrt(1.0 + old_y * old_y) * dw[step, :, 1])
        if not (np.isfinite(x).all() and np.isfinite(y).all()):
            raise FloatingPointError("Nonfinite intermediate state")
    terminal = np.exp(x)
    if not (np.isfinite(terminal).all() and (terminal > 0).all()):
        raise FloatingPointError("Nonfinite or nonpositive terminal price")
    return terminal


def run_gbm(paths, seed, batch_size):
    rng = np.random.default_rng(seed)
    strong = {(n, method): Moments() for n in GBM_LEVELS for method in range(2)}
    weak = {(n, method): Moments() for n in GBM_LEVELS for method in range(2)}
    for start in range(0, paths, batch_size):
        size = min(batch_size, paths - start)
        fine = rng.normal(0.0, math.sqrt(1.0 / GBM_LEVELS[-1]),
                          (size, GBM_LEVELS[-1]))
        for n in GBM_LEVELS:
            exact, numerical = gbm_endpoints(fine, n)
            error = numerical - exact[:, None]
            for method in range(2):
                strong[n, method].add(np.abs(error[:, method]))
                weak[n, method].add(error[:, method])
    print("\nGBM: exact reference, paired raw weak estimates, no controls")
    print("N    method     strong_L1 (SE)       weak_signed [95% CI]        analytic_bias")
    exact_mean = 100.0 * math.exp(0.05)
    for n in GBM_LEVELS:
        bias = exact_mean * math.expm1(n * math.log1p(0.05 / n) - 0.05)
        for method, name in enumerate(("EM", "Milstein")):
            sm, ss, _, _ = strong[n, method].summary()
            wm, _, lo, hi = weak[n, method].summary()
            print(f"{n:<4d} {name:<8s} {sm:9.6f} ({ss:.6f})  "
                  f"{wm:+.6f} [{lo:+.6f}, {hi:+.6f}]  {bias:+.6f}")


def run_nonaffine(paths, seed, batch_size):
    rng = np.random.default_rng(seed)
    p = PARAMETERS
    finest = REFERENCES[-1]
    strong = {(n, ref): Moments() for n in COARSE for ref in REFERENCES}
    weak = {(n, ref): Moments() for n in COARSE for ref in REFERENCES}
    pairs = tuple(zip(REFERENCES[:-1], REFERENCES[1:]))
    ref_strong = {pair: Moments() for pair in pairs}
    ref_weak = {pair: Moments() for pair in pairs}
    mean_asset = Moments()
    mean_payoff = Moments()
    for start in range(0, paths, batch_size):
        size = min(batch_size, paths - start)
        fine = rng.standard_normal((finest, size, 2))
        fine[:, :, 1] = (p["rho"] * fine[:, :, 0]
                         + math.sqrt(1.0 - p["rho"]**2) * fine[:, :, 1])
        fine *= math.sqrt(p["T"] / finest)
        terminal = {n: nonaffine_terminal(fine, n, p) for n in COARSE + REFERENCES}
        payoff = {n: np.maximum(s - p["strike"], 0.0) for n, s in terminal.items()}
        for n, ref in strong:
            strong[n, ref].add(np.abs(terminal[n] - terminal[ref]))
            weak[n, ref].add(payoff[n] - payoff[ref])
        for a, b in pairs:
            ref_strong[a, b].add(np.abs(terminal[a] - terminal[b]))
            ref_weak[a, b].add(payoff[a] - payoff[b])
        mean_asset.add(terminal[finest])
        mean_payoff.add(payoff[finest])
    print("\nNon-affine: log-EM against FINITE numerical references")
    print("N    ref    strong_L1 (SE)       paired_payoff_signed [95% CI]")
    for ref in REFERENCES:
        for n in COARSE:
            sm, ss, _, _ = strong[n, ref].summary()
            wm, _, lo, hi = weak[n, ref].summary()
            print(f"{n:<4d} {ref:<5d} {sm:9.6f} ({ss:.6f})  "
                  f"{wm:+.6f} [{lo:+.6f}, {hi:+.6f}]")
    print("Reference refinement (not an exact-error bound):")
    for a, b in pairs:
        sm, ss, _, _ = ref_strong[a, b].summary()
        wm, _, lo, hi = ref_weak[a, b].summary()
        print(f"{a} -> {b}: strong={sm:.6f} (SE {ss:.6f}); "
              f"payoff={wm:+.6f} [{lo:+.6f}, {hi:+.6f}]")
    for label, moment in (("Finest asset mean", mean_asset),
                          ("Finest undiscounted payoff", mean_payoff)):
        value, _, lo, hi = moment.summary()
        print(f"{label}: {value:.6f} [{lo:.6f}, {hi:.6f}]")
    print(f"Asset mean target: {p['S0'] * math.exp(p['mu'] * p['T']):.6f}")
    print("Small-sample teaching output; no convergence order is certified.")


def self_check():
    """Deterministic algorithm checks, independent of a lucky random sample."""
    fine = 0.003 * np.sin(np.arange(3 * 32).reshape(3, 32) / 13.0)
    for n in (1, 4, 8, 32):
        exact, got = gbm_endpoints(fine, n)
        expected = np.full((3, 2), 100.0)
        h = 1.0 / n
        for step in range(n):
            d = fine[:, step * (32 // n):(step + 1) * (32 // n)].sum(axis=1)
            expected[:, 0] += (0.05 * expected[:, 0] * h
                                + 0.3 * expected[:, 0] * d)
            expected[:, 1] += (0.05 * expected[:, 1] * h
                                + 0.3 * expected[:, 1] * d
                                + 0.045 * expected[:, 1] * (d * d - h))
        np.testing.assert_allclose(got, expected, rtol=1e-13)
        np.testing.assert_allclose(exact, 100.0 * np.exp(0.005 + 0.3 * fine.sum(1)),
                                   rtol=1e-14)
        dw = fine.reshape(3, n, 32 // n).sum(axis=2)
        np.testing.assert_allclose(dw.sum(1), fine.sum(1), atol=1e-16)
    print("PASS GBM recurrence, exact formula and Brownian aggregation")

    fine = 0.04 * np.cos(np.arange(8 * 3 * 2).reshape(8, 3, 2) / 7.0)
    got = nonaffine_terminal(fine, 4)
    expected = []
    for path in range(3):
        x, y = math.log(100.0), 0.0
        for step in range(4):
            d = fine[2 * step:2 * step + 2, path].sum(axis=0)
            g = 0.1 + 0.4 / (1.0 + math.exp(-y))
            next_x = x + (0.05 - 0.5 * g * g) * 0.25 + g * d[0]
            next_y = y + 2.0 * (-0.2 - y) * 0.25 + 0.6 * math.sqrt(1.0 + y * y) * d[1]
            x, y = next_x, next_y
        expected.append(math.exp(x))
    np.testing.assert_allclose(got, expected, rtol=1e-13)
    p = dict(PARAMETERS, g_min=0.3, g_max=0.3)
    target = 100.0 * np.exp(0.005 + 0.3 * fine[:, :, 0].sum(axis=0))
    for n in (1, 2, 4, 8):
        np.testing.assert_allclose(nonaffine_terminal(fine, n, p), target, rtol=1e-13)
    print("PASS non-affine simultaneous old-state update and constant-volatility limit")

    with np.errstate(over="raise", invalid="raise"):
        np.testing.assert_allclose(logistic(np.array([-1000.0, 0.0, 1000.0])),
                                   [0.0, 0.5, 1.0])
    moment = Moments()
    moment.add(np.array([-2.0, 1.0]))
    moment.add(np.array([3.0, 6.0]))
    mean, se, _, _ = moment.summary()
    assert mean == 2.0
    np.testing.assert_allclose(se, np.std([-2.0, 1.0, 3.0, 6.0], ddof=1) / 2.0)
    print("PASS stable logistic and batch-accumulated Monte Carlo standard error")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026090804)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.paths < 2 or args.batch_size < 1 or args.seed < 0:
        parser.error("Require paths >= 2, batch-size >= 1, seed >= 0")
    if args.self_check:
        self_check()
        return
    print(f"Python {platform.python_version()}; NumPy {np.__version__}; "
          f"paths={args.paths}; batch={args.batch_size}")
    print(f"GBM seed={args.seed}; non-affine seed={args.seed + 1}; "
          "RNG=numpy.random.default_rng")
    run_gbm(args.paths, args.seed, args.batch_size)
    run_nonaffine(args.paths, args.seed + 1, args.batch_size)


if __name__ == "__main__":
    main()
