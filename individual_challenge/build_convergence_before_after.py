"""Build the Tutorial 3 Individual Challenge convergence figures.

The BEFORE file is the report's existing GBM strong-convergence figure. The
AFTER file retains the production data and adds fitted slopes, independent-seed
uncertainty bands, theoretical-order guides, units, a claim title, and a
round-off-floor annotation.

The repeat experiment is deliberately limited to terminal GBM strong errors:
20 independent seeds x 20,000 paths, using the fixed five-grid fit window.
"""
from pathlib import Path
import csv
import json
import math
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
S0, MU, SIGMA, T = 100.0, 0.05, 0.30, 1.0
LEVELS = np.array([64, 128, 256, 512, 1024], dtype=int)
METHODS = ("EM", "Milstein")
REPEATS, PATHS, BATCH = 20, 20_000, 2_000
SEEDS = np.arange(2026092300, 2026092300 + REPEATS, dtype=np.int64)
T_CRIT_95_DF19 = 2.093024054


def production_data():
    with (ROOT / "results" / "gbm_convergence.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    data = {}
    for method in METHODS:
        selected = [r for r in rows
                    if r["method"] == method and int(r["N"]) in LEVELS]
        selected.sort(key=lambda r: int(r["N"]))
        assert [int(r["N"]) for r in selected] == LEVELS.tolist()
        data[method] = {
            "h": np.array([float(r["h"]) for r in selected]),
            "error": np.array([float(r["strong_l1"]) for r in selected]),
            "se": np.array([float(r["strong_se"]) for r in selected]),
        }
    return data


def repeat_errors():
    output = np.zeros((REPEATS, len(METHODS), len(LEVELS)))
    finest = int(LEVELS[-1])
    fine_h = T/finest
    for repeat, seed in enumerate(SEEDS):
        rng = np.random.default_rng(int(seed))
        totals = np.zeros((len(METHODS), len(LEVELS)))
        count = 0
        while count < PATHS:
            size = min(BATCH, PATHS-count)
            fine = rng.normal(0, math.sqrt(fine_h), (size, finest))
            exact = S0*np.exp((MU-.5*SIGMA**2)*T+SIGMA*fine.sum(axis=1))
            for k, n in enumerate(LEVELS):
                h = T/int(n)
                dw = fine.reshape(size, int(n), finest//int(n)).sum(axis=2)
                base = 1+MU*h+SIGMA*dw
                em = S0*np.prod(base, axis=1)
                mil = S0*np.prod(base+.5*SIGMA**2*(dw*dw-h), axis=1)
                totals[0, k] += np.abs(em-exact).sum(dtype=np.float64)
                totals[1, k] += np.abs(mil-exact).sum(dtype=np.float64)
            count += size
        output[repeat] = totals/PATHS
        print(f"repeat {repeat+1:02d}/{REPEATS}: seed={seed}")
    return output


def fit_repeats(errors):
    log_h = np.log(T/LEVELS)
    slopes = np.empty((REPEATS, len(METHODS)))
    intercepts = np.empty_like(slopes)
    for r in range(REPEATS):
        for m in range(len(METHODS)):
            slopes[r, m], intercepts[r, m] = np.polyfit(
                log_h, np.log(errors[r, m]), 1)
    return slopes, intercepts


def save_results(errors, slopes, intercepts):
    summary = {
        "experiment": "Independent-seed uncertainty for GBM terminal strong slopes",
        "repeats": REPEATS, "paths_per_repeat": PATHS, "batch_size": BATCH,
        "seeds": SEEDS.tolist(), "levels": LEVELS.tolist(),
        "coupling": "Within each repeat, every grid aggregates the same 1024-step increments",
        "methods": {},
    }
    for m, method in enumerate(METHODS):
        sd = float(slopes[:, m].std(ddof=1))
        se = sd/math.sqrt(REPEATS)
        mean = float(slopes[:, m].mean())
        summary["methods"][method] = {
            "repeat_slopes": slopes[:, m].tolist(),
            "mean_slope": mean, "slope_sd_across_seeds": sd,
            "slope_standard_error": se,
            "mean_slope_ci95": [mean-T_CRIT_95_DF19*se,
                                mean+T_CRIT_95_DF19*se],
            "errors_by_repeat_and_level": errors[:, m, :].tolist(),
            "fit_intercepts": intercepts[:, m].tolist(),
        }
    (OUT / "convergence_repeat_results.json").write_text(
        json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    return summary


def make_after(data, errors, slopes, intercepts, summary):
    colors = {"EM": "#2878A5", "Milstein": "#D55E00"}
    markers = {"EM": "o", "Milstein": "s"}
    log_h_line = np.linspace(np.log((T/LEVELS).min()),
                             np.log((T/LEVELS).max()), 160)
    h_line = np.exp(log_h_line)
    fig, ax = plt.subplots(figsize=(10.5, 6.6))
    fig.subplots_adjust(left=.095, right=.985, top=.91, bottom=.17)

    for m, method in enumerate(METHODS):
        d = data[method]
        fitted = np.exp(slopes[:, m, None]*log_h_line[None, :]
                        + intercepts[:, m, None])
        low, high = np.quantile(fitted, [.025, .975], axis=0)
        mean_fit = np.exp(slopes[:, m].mean()*log_h_line
                          + intercepts[:, m].mean())
        result = summary["methods"][method]
        ax.fill_between(h_line, low, high, color=colors[method], alpha=.17,
                        label=f"{method} 95% independent-seed fit band")
        ax.plot(h_line, mean_fit, "--", color=colors[method], lw=2,
                label=(f'{method} fit: slope {result["mean_slope"]:.3f} '
                       f'± {result["slope_standard_error"]:.4f} SE'))
        ax.errorbar(d["h"], d["error"], yerr=1.96*d["se"],
                    fmt=markers[method]+"-", color=colors[method], ms=6,
                    lw=1.5, capsize=3, label=f"{method} production data (95% pointwise CI)")

    h_mid = T/256
    em_anchor = data["EM"]["error"][2]
    mil_anchor = data["Milstein"]["error"][2]
    ax.plot(h_line, em_anchor*(h_line/h_mid)**.5, color="#333333", ls=":", lw=1.6,
            label="Theoretical order 1/2")
    ax.plot(h_line, mil_anchor*(h_line/h_mid), color="#333333", ls="-.", lw=1.6,
            label="Theoretical order 1")

    roundoff = np.finfo(float).eps*S0
    minimum = min(data[m]["error"].min() for m in METHODS)
    ax.text(.025, .035,
            f"Round-off floor not reached: $\\epsilon S_0\\approx{roundoff:.1e}$ "
            f"(minimum error $={minimum:.2e}$)",
            transform=ax.transAxes, fontsize=9.5, color="#5b365f",
            bbox=dict(boxstyle="round,pad=.3", fc="#f5eef6", ec="#9b78a1", alpha=.95))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Time step $h$ [time units]", fontsize=11)
    ax.set_ylabel("Terminal $L^1$ strong error [price units]", fontsize=11)
    ax.set_title("GBM strong slopes are close to 1/2 for EM and 1 for Milstein",
                 fontsize=14, fontweight="bold")
    ax.grid(which="both", alpha=.18)
    ax.legend(fontsize=8.4, ncol=2, loc="upper left", frameon=True)
    ax.set_ylim(minimum*.55, data["EM"]["error"].max()*2.0)
    fig.text(.5, .035,
             "Fit window: N=64,128,256,512,1024. Bands use 20 independent seeds × "
             "20,000 paths; within-seed grids are Brownian-coupled.",
             ha="center", fontsize=8.8, color="#4d5965")
    for suffix, dpi in (("png", 220), ("pdf", None)):
        fig.savefig(OUT / f"figure_after_improvement.{suffix}", dpi=dpi,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    for suffix in ("png", "pdf"):
        shutil.copyfile(ROOT / "figures" / f"report_gbm_strong.{suffix}",
                        OUT / f"figure_before_improvement.{suffix}")
    data = production_data()
    errors = repeat_errors()
    slopes, intercepts = fit_repeats(errors)
    summary = save_results(errors, slopes, intercepts)
    make_after(data, errors, slopes, intercepts, summary)
    for method in METHODS:
        r = summary["methods"][method]
        print(f'{method}: slope={r["mean_slope"]:.6f}, '
              f'SE={r["slope_standard_error"]:.6f}, '
              f'95% CI={r["mean_slope_ci95"]}')


if __name__ == "__main__":
    main()
