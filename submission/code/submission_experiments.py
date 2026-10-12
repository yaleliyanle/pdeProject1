"""Supplementary independent-seed and matched-target cost experiments.

This is not a replacement for the production experiments in gbm.py/nonaffine.py.
Run from the package root: python code/submission_experiments.py
Regenerate only figures: python code/submission_experiments.py --figures-only
Every stochastic study has fixed seeds. Wall-clock times are machine-dependent.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = Path(os.environ.get("FINANCIAL_SDE_OUTPUT_DIR",
                                   str(HERE.parent if HERE.name=="code" else HERE)))
if not (HERE / "gbm.py").exists():
    sys.path.insert(0, str(HERE.parent.parent))
import gbm
import nonaffine
import numpy as np

BASE_SEED = 2026101100
GBM_FIT_STEPS = (64, 128, 256, 512, 1024)
NA_FIT_STEPS = (8, 16, 32, 64)
NA_REFERENCE = 8192
TIMING_STEPS = (6, 8, 16, 32, 64, 128, 256, 512, 1024)
TIMING_FINEST = math.lcm(*TIMING_STEPS)
ACCURACY_TARGET = 0.25
Z95 = 1.959963984540054
METHODS = ("EM", "Milstein")


def _statistics(values):
    values = np.asarray(values, dtype=np.float64)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(values.size))
    return dict(mean=mean, standard_error=se,
                ci95_low=mean-Z95*se, ci95_high=mean+Z95*se)


def _moments(total, squares, count):
    mean = total / count
    variance = np.maximum((squares-total*mean)/(count-1), 0.0)
    return mean, np.sqrt(variance/count)


def _fit(h, error):
    slope, intercept = np.polyfit(np.log(h), np.log(error), 1)
    return dict(slope=float(slope), intercept=float(intercept))


def _slope_summary(fits):
    slopes = np.asarray([f["slope"] for f in fits])
    # Student-t critical values for the small independent-repeat ensemble.
    # This interval concerns the mean empirical slope, not theoretical order.
    t95 = {1:12.7062, 2:4.3027, 3:3.1824, 4:2.7764, 5:2.5706,
           6:2.4469, 7:2.3646, 8:2.3060, 9:2.2622, 10:2.2281,
           11:2.2010, 12:2.1788, 13:2.1604, 14:2.1448, 15:2.1314,
           16:2.1199, 17:2.1098, 18:2.1009, 19:2.0930}
    sd = float(slopes.std(ddof=1))
    se = sd/math.sqrt(slopes.size)
    df = slopes.size-1
    # Accurate large-df expansion avoids adding SciPy as a dependency.
    approximate_t95 = (Z95+(Z95**3+Z95)/(4*df)
                       +(5*Z95**5+16*Z95**3+3*Z95)/(96*df**2)
                       +(3*Z95**7+19*Z95**5+17*Z95**3-15*Z95)/(384*df**3))
    critical = t95.get(df, approximate_t95)
    mean = float(slopes.mean())
    return dict(repeats=int(slopes.size), mean=mean, standard_deviation=sd,
                standard_error_of_mean=se, mean_slope_ci95_low=mean-critical*se,
                mean_slope_ci95_high=mean+critical*se,
                minimum=float(slopes.min()), maximum=float(slopes.max()),
                interval_method="Approximate Student-t interval across independent seed-run slopes",
                limitation="Sampling repeatability only; excludes fit-window and reference bias.")


def gbm_repeat_study(repeats, paths, pilot_paths, batch):
    records = []
    levels = list(map(int, gbm.LEVELS))
    selected = [levels.index(n) for n in GBM_FIT_STEPS]
    for repeat in range(repeats):
        seed = BASE_SEED+100+2*repeat
        pilot_seed = seed+1
        betas = gbm.fit_controls(np.random.default_rng(pilot_seed), pilot_paths, batch)
        totals = np.zeros((len(levels), 2, 2))
        squares = np.zeros_like(totals)
        rng = np.random.default_rng(seed)
        for offset in range(0, paths, batch):
            size = min(batch, paths-offset)
            for k, (_, exact, endpoints, controls) in enumerate(gbm.simulate_batch(rng, size)):
                difference = endpoints-exact[:, None]
                metrics = np.stack((np.abs(difference), difference-controls@betas[k]), axis=2)
                totals[k] += metrics.sum(axis=0)
                squares[k] += (metrics*metrics).sum(axis=0)
        means, ses = _moments(totals, squares, paths)
        h = gbm.T/np.asarray(GBM_FIT_STEPS)
        method_records = {}
        for j, method in enumerate(METHODS):
            strong = means[selected, j, 0]
            weak = means[selected, j, 1]
            weak_se = ses[selected, j, 1]
            weak_resolved = bool(np.all((weak-Z95*weak_se)*(weak+Z95*weak_se)>0))
            method_records[method] = dict(
                h=h.tolist(), strong_error=strong.tolist(),
                strong_se=ses[selected, j, 0].tolist(), weak_signed_cv=weak.tolist(),
                weak_cv_se=weak_se.tolist(), strong_fit=_fit(h, strong),
                weak_fit=_fit(h, np.abs(weak)) if weak_resolved else None,
                weak_all_pointwise_cis_exclude_zero=weak_resolved)
        records.append(dict(repeat=repeat, seed=seed, independent_pilot_seed=pilot_seed,
                            methods=method_records))
        print(f"GBM repeat {repeat+1}/{repeats}: " + ", ".join(
            f"{m} strong slope={method_records[m]['strong_fit']['slope']:.5f}" for m in METHODS),
            flush=True)
    summaries = {}
    for method in METHODS:
        all_fits = [r["methods"][method] for r in records]
        weak_fits = [r["weak_fit"] for r in all_fits if r["weak_fit"] is not None]
        summaries[method] = dict(
            strong=_slope_summary([r["strong_fit"] for r in all_fits]),
            weak=_slope_summary(weak_fits) if len(weak_fits)>1 else None,
            weak_accepted_repeats=len(weak_fits))
    return dict(parameters=dict(S0=gbm.S0, mu=gbm.MU, sigma=gbm.SIGMA, T=gbm.T),
                paths_per_repeat=paths, independent_pilot_paths_per_repeat=pilot_paths,
                fit_steps=list(GBM_FIT_STEPS), finest_steps=int(gbm.LEVELS[-1]),
                repeats=records, slope_summary=summaries,
                controls="Five analytically zero-mean controls fitted on independent pilot paths.",
                seed_coupling="Independent seeds across repeats; common Brownian increments across grids within each repeat.")


def nonaffine_repeat_study(repeats, paths, batch):
    records = []
    nonaffine.em_terminal(np.zeros((1, 1, 2)), 1, nonaffine.PARAMETERS)
    p = nonaffine.PARAMETERS
    for repeat in range(repeats):
        seed = BASE_SEED+1000+2*repeat
        rng = np.random.default_rng(seed)
        totals = np.zeros(len(NA_FIT_STEPS))
        squares = np.zeros_like(totals)
        all_finite_positive = True
        for offset in range(0, paths, batch):
            size = min(batch, paths-offset)
            dw = rng.standard_normal((NA_REFERENCE, size, 2))
            dw[:, :, 1] = p["rho"]*dw[:, :, 0]+math.sqrt(1-p["rho"]**2)*dw[:, :, 1]
            dw *= math.sqrt(p["T"]/NA_REFERENCE)
            reference, diagnostic = nonaffine.em_terminal(dw, NA_REFERENCE, p)
            all_finite_positive &= diagnostic["all_asset_states_positive_finite"]
            for k, n in enumerate(NA_FIT_STEPS):
                endpoints, diagnostic = nonaffine.em_terminal(dw, n, p)
                all_finite_positive &= diagnostic["all_asset_states_positive_finite"]
                difference = np.abs(endpoints-reference)
                totals[k] += difference.sum()
                squares[k] += np.dot(difference, difference)
        means, ses = _moments(totals, squares, paths)
        h = p["T"]/np.asarray(NA_FIT_STEPS)
        fit = _fit(h, means)
        records.append(dict(repeat=repeat, seed=seed, h=h.tolist(),
                            strong_error=means.tolist(), strong_se=ses.tolist(),
                            fit=fit, all_states_finite_and_prices_positive=bool(all_finite_positive)))
        print(f"Non-affine repeat {repeat+1}/{repeats}: slope={fit['slope']:.5f}", flush=True)
    return dict(parameters=dict(p), paths_per_repeat=paths, fit_steps=list(NA_FIT_STEPS),
                finite_reference_steps=NA_REFERENCE, repeats=records,
                slope_summary=_slope_summary([r["fit"] for r in records]),
                limitation="Reference discrepancy, not exact-solution error. Production reference-refinement evidence is separate.")


def _price_endpoints(dw, method):
    """Same vectorized price update/product representation as gbm.py."""
    h = gbm.T/dw.shape[1]
    factor = 1+gbm.MU*h+gbm.SIGMA*dw
    if method == "Milstein":
        factor += 0.5*gbm.SIGMA**2*(dw*dw-h)
    return gbm.S0*np.prod(factor, axis=1)


def cost_accuracy_study(paths, timing_repeats):
    seed = BASE_SEED+2000
    rng = np.random.default_rng(seed)
    fine = rng.normal(0, math.sqrt(gbm.T/TIMING_FINEST), (paths, TIMING_FINEST))
    exact = gbm.S0*np.exp((gbm.MU-0.5*gbm.SIGMA**2)*gbm.T+gbm.SIGMA*fine.sum(axis=1))
    records = []
    for n in TIMING_STEPS:
        dw = fine.reshape(paths, n, TIMING_FINEST//n).sum(axis=2)
        # Warm both implementations. Generation and aggregation are not timed.
        for method in METHODS:
            _price_endpoints(dw, method)
        elapsed = {method:[] for method in METHODS}
        endpoints = {}
        # Alternate execution order to reduce systematic order/cache effects.
        for repetition in range(timing_repeats):
            for method in METHODS if repetition%2==0 else METHODS[::-1]:
                started = time.perf_counter()
                endpoints[method] = _price_endpoints(dw, method)
                elapsed[method].append(time.perf_counter()-started)
        for method in METHODS:
            estimate = _statistics(np.abs(endpoints[method]-exact))
            records.append(dict(method=method, n_steps=n, h=gbm.T/n,
                                strong_error=estimate, timed_seconds=elapsed[method],
                                median_seconds=float(np.median(elapsed[method])),
                                minimum_seconds=min(elapsed[method]),
                                maximum_seconds=max(elapsed[method]), path_updates=n*paths))
    choices = {}
    for method in METHODS:
        # Require the upper pointwise sampling bound to meet the common target.
        feasible = [r for r in records if r["method"]==method and
                    r["strong_error"]["ci95_high"]<=ACCURACY_TARGET]
        choices[method] = min(feasible, key=lambda r:r["n_steps"]) if feasible else None
    ratio, error_difference = None, None
    if all(choices[m] is not None for m in METHODS):
        ratio = choices["EM"]["median_seconds"]/choices["Milstein"]["median_seconds"]
        error_difference = abs(choices["EM"]["strong_error"]["mean"]-
                               choices["Milstein"]["strong_error"]["mean"])/choices["EM"]["strong_error"]["mean"]
    print("Matched target selections: " + ", ".join(
        f"{m}: N={choices[m]['n_steps']}" if choices[m] is not None else f"{m}: unresolved"
        for m in METHODS), flush=True)
    return dict(seed=seed, finest_brownian_steps=TIMING_FINEST,
                paths=paths, timing_repeats=timing_repeats,
                target_terminal_l1_currency=ACCURACY_TARGET,
                target_rule="Coarsest tested grid whose upper pointwise 95% Monte Carlo bound is <= target.",
                cost_measure="Median wall-clock seconds for vectorized price-update/product kernel, for the same number of paths.",
                included="Arithmetic, temporary array allocation, and product reduction inside price-update kernel.",
                excluded="RNG, Brownian aggregation, reference evaluation, import/setup, warmup, statistics, plotting, file IO.",
                implementation="NumPy vectorized product formulation, matching gbm.py; no compilation is involved.",
                limitation="Discrete grids overshoot the common tolerance by different amounts; not identical achieved errors. Implementation- and machine-specific kernel latency, not full-workflow cost.",
                records=records, matched_target_choices=choices,
                em_to_milstein_median_kernel_cost_ratio=ratio,
                achieved_error_relative_difference_vs_em=error_difference)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summary_lines(summary):
    lines = ["Supplementary submission evidence: independent-seed repeats and common-tolerance cost",
             "Slope uncertainty below is sampling repeatability, not reference/window uncertainty."]
    for method, records in summary["gbm_repeat_study"]["slope_summary"].items():
        for metric in ("strong", "weak"):
            stats = records[metric]
            if stats is not None:
                lines.append(f"GBM {method} {metric}: mean slope {stats['mean']:.8f}, "
                             f"seed SD {stats['standard_deviation']:.8f}, "
                             f"approximate mean-slope 95% CI [{stats['mean_slope_ci95_low']:.8f}, "
                             f"{stats['mean_slope_ci95_high']:.8f}]")
    stats = summary["nonaffine_repeat_study"]["slope_summary"]
    lines.append(f"Non-affine strong: mean slope {stats['mean']:.8f}, "
                 f"seed SD {stats['standard_deviation']:.8f}, "
                 f"approximate mean-slope 95% CI [{stats['mean_slope_ci95_low']:.8f}, "
                 f"{stats['mean_slope_ci95_high']:.8f}]; finite reference N={NA_REFERENCE}.")
    cost = summary["cost_accuracy_study"]
    lines.append(f"Common terminal L1 tolerance: {ACCURACY_TARGET:g} currency; "
                 f"same {cost['paths']} paths; median of {cost['timing_repeats']} kernel timings.")
    for method, chosen in cost["matched_target_choices"].items():
        if chosen:
            stats = chosen["strong_error"]
            lines.append(f"{method}: N={chosen['n_steps']}, strong error {stats['mean']:.8f}, "
                         f"95% MC CI [{stats['ci95_low']:.8f}, {stats['ci95_high']:.8f}], "
                         f"median kernel seconds {chosen['median_seconds']:.9f}; "
                         f"path updates {chosen['path_updates']}")
    ratio = cost["em_to_milstein_median_kernel_cost_ratio"]
    if ratio is not None:
        lines.append(f"EM/Milstein matched-tolerance median kernel-cost ratio: {ratio:.6f}")
        lines.append(f"Achieved-error absolute difference / EM error: "
                     f"{100*cost['achieved_error_relative_difference_vs_em']:.3f}%")
    lines.extend(["The discrete grids achieve different errors below the same tolerance.",
                  "Cost excludes RNG, Brownian aggregation, reference evaluation, setup/warmup, statistics, plotting and file IO.",
                  "Cost includes kernel arithmetic, temporary allocation and product reduction; no JIT compilation in NumPy GBM kernel.",
                  "Wall-clock cost is machine dependent and not an end-to-end workflow speedup."])
    return lines


def write_outputs(summary, output):
    results = output/"results"
    results.mkdir(parents=True, exist_ok=True)
    with (results/"submission_experiments.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
    with (results/"submission_experiments_summary.txt").open("w", encoding="utf-8") as stream:
        stream.write("\n".join(summary_lines(summary))+"\n")
    rows = []
    for repeat in summary["gbm_repeat_study"]["repeats"]:
        for method, r in repeat["methods"].items():
            rows.append(dict(model="GBM", method=method, seed=repeat["seed"],
                             paths=summary["gbm_repeat_study"]["paths_per_repeat"],
                             strong_slope=r["strong_fit"]["slope"],
                             weak_slope=r["weak_fit"]["slope"] if r["weak_fit"] else "",
                             finite_reference_steps="exact"))
    for repeat in summary["nonaffine_repeat_study"]["repeats"]:
        rows.append(dict(model="Non-affine", method="log-EM", seed=repeat["seed"],
                         paths=summary["nonaffine_repeat_study"]["paths_per_repeat"],
                         strong_slope=repeat["fit"]["slope"], weak_slope="",
                         finite_reference_steps=NA_REFERENCE))
    _write_csv(results/"submission_repeat_slopes.csv", rows)
    rows = []
    for r in summary["cost_accuracy_study"]["records"]:
        rows.append(dict(method=r["method"], n_steps=r["n_steps"], h=r["h"],
                         error_mean=r["strong_error"]["mean"],
                         error_ci95_low=r["strong_error"]["ci95_low"],
                         error_ci95_high=r["strong_error"]["ci95_high"],
                         median_kernel_seconds=r["median_seconds"],
                         minimum_kernel_seconds=r["minimum_seconds"],
                         maximum_kernel_seconds=r["maximum_seconds"],
                         path_updates=r["path_updates"]))
    _write_csv(results/"submission_cost_accuracy.csv", rows)


def make_figures(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10,
                         "axes.spines.top":False, "axes.spines.right":False,
                         "legend.frameon":False, "savefig.dpi":240, "pdf.fonttype":42})
    figures = output/"figures"
    figures.mkdir(parents=True, exist_ok=True)
    colors = {"EM":"#2166ac", "Milstein":"#d95f02", "log-EM":"#357554"}

    def save(fig, stem):
        for extension in ("pdf", "png"):
            fig.savefig(figures/f"{stem}.{extension}", bbox_inches="tight", facecolor="white")
        plt.close(fig)

    def panel(ax, fits, h, errors, color, label, theory):
        h = np.asarray(h)
        lx = np.linspace(np.log(h.min()), np.log(h.max()), 100)
        lines = np.exp(np.array([f["slope"]*lx+f["intercept"] for f in fits]))
        lower, upper = np.quantile(lines, [0.025, 0.975], axis=0)
        ax.fill_between(np.exp(lx), lower, upper, color=color, alpha=0.22)
        for error in errors:
            ax.loglog(h, error, color=color, alpha=0.20, lw=0.6)
        mean_error = np.mean(errors, axis=0)
        marker = "s" if label.startswith("Milstein") else "o"
        ax.loglog(h, mean_error, marker+"-", color=color, ms=4, label=label,
                  markerfacecolor="white" if marker=="s" else color)
        ax.loglog(np.exp(lx), np.exp(np.mean(np.log(lines), axis=0)), "--",
                  color=color, lw=1)
        guide = mean_error[0]*(h/h[0])**theory
        ax.loglog(h, guide*1.3, ":", color=color, lw=1,
                  label=f"slope {theory:g} guide")
        ax.set(xlabel="Time step h [years]", ylabel="Terminal L1 error [currency]")
        ax.grid(which="both", alpha=0.13)
        ax.legend(fontsize=8)

    study = summary["gbm_repeat_study"]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3), layout="constrained")
    for method in METHODS:
        rr = [r["methods"][method] for r in study["repeats"]]
        stats = study["slope_summary"][method]["strong"]
        label = f"{method}: p={stats['mean']:.3f}, seed SD={stats['standard_deviation']:.3f}"
        panel(axes[0], [r["strong_fit"] for r in rr], rr[0]["h"],
              [r["strong_error"] for r in rr], colors[method], label,
              0.5 if method=="EM" else 1.0)
        accepted = [r for r in rr if r["weak_fit"] is not None]
        if len(accepted)>1:
            stats = study["slope_summary"][method]["weak"]
            label = f"{method}: p={stats['mean']:.3f}, seed SD={stats['standard_deviation']:.3f}"
            panel(axes[1], [r["weak_fit"] for r in accepted], accepted[0]["h"],
                  [np.abs(r["weak_signed_cv"]) for r in accepted], colors[method], label, 1.0)
    axes[0].set_title("Strong slopes repeat across independent seeds")
    axes[1].set_title("Controlled weak slopes both remain near one")
    axes[1].set_ylabel("Absolute mean bias [currency]")
    fig.suptitle(f"GBM: {len(study['repeats'])} seeds, {study['paths_per_repeat']:,} paths/seed; N=64..1024")
    fig.supxlabel("Shading: empirical central 95% spread of independent-run fitted curves, not a guaranteed confidence band.", fontsize=8)
    save(fig, "submission_gbm_repeat_slopes")

    study = summary["nonaffine_repeat_study"]
    rr = study["repeats"]
    stats = study["slope_summary"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6), layout="constrained")
    panel(ax, [r["fit"] for r in rr], rr[0]["h"], [r["strong_error"] for r in rr],
          colors["log-EM"], f"log-EM: p={stats['mean']:.3f}, seed SD={stats['standard_deviation']:.3f}", 0.5)
    ax.set_ylabel("Coupled reference discrepancy [currency]")
    ax.set_title("Non-affine half-order behaviour survives independent seeds")
    fig.suptitle(f"{len(rr)} seeds, {study['paths_per_repeat']:,} paths/seed; finite EM reference N={study['finite_reference_steps']}", fontsize=11)
    fig.supxlabel("Shading: empirical central 95% fitted-curve spread; reference bias is not included.", fontsize=8)
    save(fig, "submission_nonaffine_repeat_slopes")

    cost = summary["cost_accuracy_study"]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.5), layout="constrained")
    for method in METHODS:
        rows = [r for r in cost["records"] if r["method"]==method]
        x = np.array([r["median_seconds"] for r in rows])
        error = np.array([r["strong_error"]["mean"] for r in rows])
        se = np.array([r["strong_error"]["standard_error"] for r in rows])
        axes[0].errorbar(x, error, yerr=Z95*se, fmt="o-", color=colors[method],
                         capsize=3, ms=4, label=method)
        chosen = cost["matched_target_choices"][method]
        if chosen:
            axes[0].scatter([chosen["median_seconds"]], [chosen["strong_error"]["mean"]],
                            s=90, facecolors="none", edgecolors=colors[method], zorder=4)
            axes[0].annotate(f"{method}, N={chosen['n_steps']}",
                             (chosen["median_seconds"], chosen["strong_error"]["mean"]),
                             xytext=(6, 9 if method=="EM" else -16),
                             textcoords="offset points", fontsize=8)
    axes[0].axhline(ACCURACY_TARGET, color="#555555", ls="--", lw=1,
                    label=f"common target: {ACCURACY_TARGET:g} currency")
    axes[0].set(xscale="log", yscale="log", xlabel="Median kernel wall time [seconds]",
                ylabel="Terminal L1 error [currency]", title="Match tolerance before comparing kernel cost")
    axes[0].legend(fontsize=8)
    choices = cost["matched_target_choices"]
    if all(choices[m] for m in METHODS):
        chosen_times = [choices[m]["median_seconds"] for m in METHODS]
        axes[1].bar(METHODS, chosen_times, color=[colors[m] for m in METHODS], width=0.55)
        for k, method in enumerate(METHODS):
            chosen = choices[method]
            axes[1].text(k, chosen_times[k]*1.04,
                         f"N={chosen['n_steps']}\nerror={chosen['strong_error']['mean']:.3f}",
                         ha="center", va="bottom", fontsize=9)
        axes[1].set_ylim(0, max(chosen_times)*1.30)
    axes[1].set(ylabel="Median kernel wall time [seconds]",
                title=f"Same paths; both upper 95% bounds <= {ACCURACY_TARGET:g}")
    for ax in axes:
        ax.grid(axis="y", alpha=0.15)
    fig.suptitle(f"GBM cost-accuracy: {cost['paths']:,} shared paths; median of {cost['timing_repeats']} timings")
    fig.supxlabel("NumPy price-update kernel only; excludes RNG, aggregation, setup, statistics and plotting. Discrete grids overshoot target.", fontsize=8)
    save(fig, "submission_cost_accuracy")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--gbm-paths", type=int, default=5000)
    parser.add_argument("--gbm-pilot-paths", type=int, default=1000)
    parser.add_argument("--nonaffine-paths", type=int, default=1000)
    parser.add_argument("--nonaffine-batch-size", type=int, default=100)
    parser.add_argument("--timing-paths", type=int, default=10000)
    parser.add_argument("--timing-repeats", type=int, default=7)
    parser.add_argument("--figures-only", action="store_true")
    args = parser.parse_args()
    if args.repeats<2 or min(args.gbm_paths, args.nonaffine_paths,
                           args.timing_paths)<2 or args.timing_repeats<5 or args.nonaffine_batch_size<1:
        parser.error("Need >=2 independent repeats/paths, >=5 timing repeats, and a positive batch size.")
    if args.gbm_pilot_paths<20:
        parser.error("Need >=20 independent pilot paths to fit the five controls.")
    if args.figures_only:
        with (args.output_dir/"results"/"submission_experiments.json").open(encoding="utf-8") as stream:
            summary = json.load(stream)
    else:
        start = time.perf_counter()
        summary = dict(
            protocol_version="1.0", fixed_seed_base=BASE_SEED,
            environment=dict(python=platform.python_version(), numpy=np.__version__,
                             numba=nonaffine.numba_version, platform=platform.platform(),
                             processor=platform.processor()),
            gbm_repeat_study=gbm_repeat_study(args.repeats, args.gbm_paths,
                                             args.gbm_pilot_paths, 250),
            nonaffine_repeat_study=nonaffine_repeat_study(args.repeats, args.nonaffine_paths,
                                                        args.nonaffine_batch_size),
            cost_accuracy_study=cost_accuracy_study(args.timing_paths, args.timing_repeats))
        summary["elapsed_seconds_excluding_figures"] = time.perf_counter()-start
        write_outputs(summary, args.output_dir)
    make_figures(summary, args.output_dir)
    for line in summary_lines(summary):
        print(line, flush=True)
    print(f"Saved supplementary evidence to {args.output_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
