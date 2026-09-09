"""Problem 4: coupled non-affine Euler--Maruyama experiment.

Usage: python nonaffine.py --paths 100000 --batch-size 512 --seed 2026090804
Errors are relative to finite EM references, not an exact solution.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".deps"))
import numpy as np
from numba import njit, __version__ as numba_version

PARAMETERS = dict(S0=100., Y0=0., mu=.05, kappa=2., theta=-.2, xi=.6,
                  rho=-.7, T=1., strike=100., g_min=.1, g_max=.5)
COARSE = (8, 16, 32, 64, 128, 256)
REFERENCES = (2048, 4096, 8192)
LEVELS = COARSE + REFERENCES


class Moments:
    """Streaming moments of independent path observations."""
    def __init__(self):
        self.n = 0
        self.total = 0.
        self.total2 = 0.

    def add(self, values):
        self.n += values.size
        self.total += float(np.sum(values, dtype=np.float64))
        self.total2 += float(np.dot(values, values))

    def summary(self):
        mean = self.total / self.n
        variance = max(0., (self.total2 - self.total * mean) / (self.n - 1))
        se = math.sqrt(variance / self.n)
        return dict(n=self.n, mean=mean, standard_error=se,
                    ci95_low=mean-1.96*se, ci95_high=mean+1.96*se)


@njit(cache=False)
def _em_kernel(increments, h, s0, y0, mu, kappa, theta, xi, g_min, g_max):
    """Compiled time-major scalar kernel, with both coefficients at old Y."""
    n_steps, n_paths, _ = increments.shape
    x = np.full(n_paths, math.log(s0))
    y = np.full(n_paths, y0)
    x_min = x_max = math.log(s0)
    y_min = y_max = y0
    all_finite = True
    for step in range(n_steps):
        for j in range(n_paths):
            old_y = y[j]
            if old_y >= 0:
                sigmoid = 1.0/(1.0+math.exp(-old_y))
            else:
                exp_y = math.exp(old_y)
                sigmoid = exp_y/(1.0+exp_y)
            g = g_min+(g_max-g_min)*sigmoid
            x[j] += (mu-0.5*g*g)*h+g*increments[step,j,0]
            y[j] += kappa*(theta-old_y)*h+xi*math.sqrt(1.0+old_y*old_y)*increments[step,j,1]
            if not (math.isfinite(x[j]) and math.isfinite(y[j])):
                all_finite = False
            x_min, x_max = min(x_min,x[j]), max(x_max,x[j])
            y_min, y_max = min(y_min,y[j]), max(y_max,y[j])
    return np.exp(x), x_min, x_max, y_min, y_max, all_finite


def em_terminal(dw, n_steps, p):
    """Both updates use Y_n. All grids aggregate the same finest increments."""
    finest, n_paths, _ = dw.shape
    ratio = finest // n_steps
    increments = dw if ratio == 1 else dw.reshape(n_steps,ratio,n_paths,2).sum(axis=1)
    h = p["T"]/n_steps
    s,x_min,x_max,y_min,y_max,all_finite = _em_kernel(increments,h,
        p["S0"],p["Y0"],p["mu"],p["kappa"],p["theta"],p["xi"],p["g_min"],p["g_max"])
    diagnostic = dict(x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,
        updates=n_steps*n_paths,all_states_finite=bool(all_finite),
        all_asset_states_positive_finite=bool(
            all_finite and x_min>math.log(np.nextafter(0.,1.)) and
            x_max<math.log(np.finfo(np.float64).max)),
        all_terminal_assets_positive_finite=bool(np.isfinite(s).all() and (s>0).all()))
    return s,diagnostic


def rate_fit(rows, key, steps):
    selected = [r for r in rows if r["n_steps"] in steps]
    if key == "weak_payoff_difference" and not all(
            r[key]["ci95_low"]*r[key]["ci95_high"] > 0 for r in selected):
        return dict(steps=list(steps), slope=None, accepted=False,
            reason="At least one paired 95% CI includes zero; weak slope is not resolved.")
    lx = np.log([r["h"] for r in selected])
    ly = np.log(np.abs([r[key]["mean"] for r in selected]))
    slope, intercept = np.polyfit(lx, ly, 1)
    residual = ly - (slope*lx+intercept)
    r2 = 1-np.sum(residual**2)/np.sum((ly-ly.mean())**2)
    return dict(steps=list(steps), slope=float(slope), intercept=float(intercept),
        r_squared=float(r2), accepted=True,
        reason="Descriptive empirical slope against a finite reference, not exact error.")


def draw_plots(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
        "axes.spines.top":False, "axes.spines.right":False, "figure.dpi":130,
        "savefig.dpi":220, "axes.titleweight":"bold", "pdf.fonttype":42})
    rows = summary["convergence"]
    colors = dict(zip(REFERENCES, ("#d18c2e", "#639565", "#256ba5")))

    def save(fig, stem):
        for ext in ("png","pdf"):
            fig.savefig(ROOT/"figures"/f"{stem}.{ext}", bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4,5.4), layout="constrained")
    for ref in REFERENCES:
        rr = [r for r in rows if r["reference_steps"] == ref]
        h = np.array([r["h"] for r in rr])
        err = np.array([r["strong_l1"]["mean"] for r in rr])
        ci = np.array([1.96*r["strong_l1"]["standard_error"] for r in rr])
        ax.errorbar(h, err, yerr=ci, color=colors[ref], marker="o", lw=1.7,
                    ms=4, capsize=2, label=f"EM reference h = 1/{ref}")
    ax.plot(h, err[0]*1.3*np.sqrt(h/h[0]), "--", color="#98597e", label="Slope 1/2 guide")
    ax.set(xscale="log", yscale="log", xlabel="Coarse step h",
           ylabel=r"Coupled strong discrepancy $\mathbb{E}|S_h-S_{\rm ref}|$",
           title="Non-affine SDE: terminal strong error")
    ax.set_xticks(h, [f"1/{n}" for n in COARSE])
    ax.invert_xaxis()
    ax.grid(which="both", alpha=.18)
    ax.legend(fontsize=9, loc="lower left")
    fig.supxlabel("Pointwise 95% Monte Carlo CIs; finite-reference discrepancies.", fontsize=9)
    save(fig, "nonaffine_strong")

    rr = [r for r in rows if r["reference_steps"] == max(REFERENCES)]
    bias = np.array([r["weak_payoff_difference"]["mean"] for r in rr])
    ci = np.array([1.96*r["weak_payoff_difference"]["standard_error"] for r in rr])
    fig, ax = plt.subplots(figsize=(8.4,5.4), layout="constrained")
    ax.errorbar(range(len(COARSE)), bias, yerr=ci, color=colors[max(REFERENCES)],
                marker="o", capsize=5, lw=1.7)
    ax.axhline(0, color="#98597e", ls="--", lw=1)
    ax.set(xticks=range(len(COARSE)), xticklabels=[f"1/{n}" for n in COARSE],
           xlabel="Coarse step h", ylabel="Paired signed payoff difference",
           title="Non-affine SDE: weak error for call payoff")
    ax.grid(axis="y", alpha=.2)
    fig.supxlabel("Payoff max(S - 100, 0); reference 1/8192; pointwise paired 95% CIs.", fontsize=9)
    save(fig, "nonaffine_weak")

    fig, axes = plt.subplots(1, 2, figsize=(10.2,4.8), layout="constrained")
    refs = summary["reference_checks"]
    axes[0].errorbar([0,1], [r["strong_l1"]["mean"] for r in refs],
        yerr=[1.96*r["strong_l1"]["standard_error"] for r in refs],
        fmt="o-", color=colors[max(REFERENCES)], capsize=5)
    axes[0].set(xticks=[0,1], xticklabels=["2048 to 4096","4096 to 8192"],
        ylabel=r"$\mathbb{E}|S_a-S_b|$", xlabel="Reference refinement (steps)",
        title="Nested reference sensitivity", ylim=(0,None))
    mm = [summary["terminal_asset_mean"][str(n)] for n in REFERENCES]
    axes[1].errorbar(range(3), [m["mean"] for m in mm],
        yerr=[1.96*m["standard_error"] for m in mm],
        fmt="o", color=colors[max(REFERENCES)], capsize=5, label="Mean and 95% CI")
    axes[1].axhline(summary["diagnostics"]["asset_expectation_target"],
        ls="--", color="#98597e", label=r"$100e^{0.05}$")
    axes[1].set(xticks=range(3), xticklabels=[f"1/{n}" for n in REFERENCES],
        xlabel="Reference h", ylabel=r"Terminal asset mean", title="Implementation sanity check")
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.grid(axis="y", alpha=.2)
    fig.supxlabel("The first moment is also exactly preserved by log-EM in expectation; it does not measure weak order.",
                  fontsize=9)
    save(fig, "nonaffine_reference")


def write_csv(path, rows, identifiers):
    stats = ("mean","standard_error","ci95_low","ci95_high")
    keys = ("strong_l1","weak_payoff_difference")
    fields = list(identifiers) + [f"{k}_{s}" for k in keys for s in stats]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for row in rows:
            flat = {k:row[k] for k in identifiers}
            flat.update({f"{k}_{s}":row[k][s] for k in keys for s in stats})
            writer.writerow(flat)


def run(n_paths=100000, batch_size=512, seed=2026090804):
    if n_paths < 2 or batch_size < 1:
        raise ValueError("Need at least 2 paths and a positive batch size")
    for folder in ("results","figures"):
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    jit_t0 = time.perf_counter()
    em_terminal(np.zeros((1,1,2)),1,PARAMETERS)
    jit_warmup_seconds = time.perf_counter()-jit_t0
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    strong = {(n,r):Moments() for n in COARSE for r in REFERENCES}
    weak = {(n,r):Moments() for n in COARSE for r in REFERENCES}
    ref_pairs = tuple(zip(REFERENCES[:-1],REFERENCES[1:]))
    ref_strong = {pair:Moments() for pair in ref_pairs}
    ref_weak = {pair:Moments() for pair in ref_pairs}
    means = {n:Moments() for n in LEVELS}
    payoffs = {n:Moments() for n in LEVELS}
    state_diagnostics = {}
    terminal_samples = {n:np.empty(n_paths,dtype=np.float64) for n in LEVELS}
    brownian = None
    finest = max(LEVELS)
    hfinest = PARAMETERS["T"]/finest
    completed = 0
    while completed < n_paths:
        m = min(batch_size, n_paths-completed)
        dw = rng.standard_normal((finest,m,2))
        dw[:,:,1] = PARAMETERS["rho"]*dw[:,:,0] + math.sqrt(1-PARAMETERS["rho"]**2)*dw[:,:,1]
        dw *= math.sqrt(hfinest)
        if brownian is None:
            sample = dw.reshape(-1,2)
            cov = np.cov(sample, rowvar=False, ddof=1)
            brownian = dict(n_increments=int(sample.shape[0]), grid_h=hfinest,
                mean=sample.mean(axis=0).tolist(), variance=cov.diagonal().tolist(),
                covariance=float(cov[0,1]),
                correlation=float(cov[0,1]/math.sqrt(cov[0,0]*cov[1,1])),
                target_variance=hfinest, target_covariance=PARAMETERS["rho"]*hfinest,
                target_correlation=PARAMETERS["rho"],
                diagnostic_sample="All increments in the predetermined first batch")
            count = brownian["n_increments"]
            brownian["mean_z_scores"] = (np.array(brownian["mean"])/math.sqrt(hfinest/count)).tolist()
            brownian["variance_z_scores"] = ((np.array(brownian["variance"])-hfinest)/(hfinest*math.sqrt(2/(count-1)))).tolist()
            brownian["correlation_fisher_z_score"] = (np.arctanh(brownian["correlation"])-np.arctanh(PARAMETERS["rho"]))*math.sqrt(count-3)
            brownian["all_diagnostic_z_scores_within_5"] = bool(max(abs(v) for v in brownian["mean_z_scores"]+brownian["variance_z_scores"]+[brownian["correlation_fisher_z_score"]]) < 5)
        terminal, payoff = {}, {}
        for n in LEVELS:
            s, d = em_terminal(dw, n, PARAMETERS)
            terminal[n] = s
            terminal_samples[n][completed:completed+m] = s
            payoff[n] = np.maximum(s-PARAMETERS["strike"],0)
            means[n].add(s)
            payoffs[n].add(payoff[n])
            if n not in state_diagnostics:
                state_diagnostics[n] = d
            else:
                old = state_diagnostics[n]
                for k in ("x_min","y_min"):
                    old[k] = min(old[k],d[k])
                for k in ("x_max","y_max"):
                    old[k] = max(old[k],d[k])
                old["updates"] += d["updates"]
                for k in ("all_states_finite","all_asset_states_positive_finite",
                          "all_terminal_assets_positive_finite"):
                    old[k] = old[k] and d[k]
        for n,r in strong:
            strong[n,r].add(np.abs(terminal[n]-terminal[r]))
            weak[n,r].add(payoff[n]-payoff[r])
        for a,b in ref_pairs:
            ref_strong[a,b].add(np.abs(terminal[a]-terminal[b]))
            ref_weak[a,b].add(payoff[a]-payoff[b])
        completed += m
        if completed == n_paths or completed % (batch_size*5) == 0:
            print(f"Non-affine EM: {completed:,}/{n_paths:,} paths, {time.perf_counter()-t0:.1f}s", flush=True)
    rows = [dict(n_steps=n, h=PARAMETERS["T"]/n, reference_steps=r,
        reference_h=PARAMETERS["T"]/r, strong_l1=strong[n,r].summary(),
        weak_payoff_difference=weak[n,r].summary()) for r in REFERENCES for n in COARSE]
    refs = [dict(coarser_steps=a, finer_steps=b, strong_l1=ref_strong[a,b].summary(),
        weak_payoff_difference=ref_weak[a,b].summary()) for a,b in ref_pairs]
    fits = {}
    for r in REFERENCES:
        rr = [row for row in rows if row["reference_steps"] == r]
        fits[str(r)] = dict(strong_coarse=rate_fit(rr,"strong_l1",(8,16,32,64)),
            strong_all=rate_fit(rr,"strong_l1",COARSE),
            weak_coarse=rate_fit(rr,"weak_payoff_difference",(8,16,32,64)),
            weak_all=rate_fit(rr,"weak_payoff_difference",COARSE))
    rr = [r for r in rows if r["reference_steps"] == max(REFERENCES)]
    ratios = {str(r["n_steps"]):refs[-1]["strong_l1"]["mean"]/r["strong_l1"]["mean"] for r in rr}
    target = PARAMETERS["S0"]*math.exp(PARAMETERS["mu"]*PARAMETERS["T"])
    mean_summary = {str(n):means[n].summary() for n in LEVELS}
    for value in mean_summary.values():
        value["target_within_ci95"] = value["ci95_low"] <= target <= value["ci95_high"]
        value["z_from_target"] = (value["mean"]-target)/value["standard_error"]
    summary = dict(model="nonaffine_log_asset_stochastic_volatility", parameters=PARAMETERS,
        simulation=dict(n_paths=n_paths, batch_size=batch_size, seed=seed,
            rng="numpy.random.default_rng / PCG64", finest_steps=finest,
            coarse_steps=list(COARSE), reference_steps=list(REFERENCES),
            coupling="Each coarse/ref grid sums contiguous finest 1/8192 increments from the same Brownian path.",
            update="Left endpoint, simultaneous X/Y Euler-Maruyama.",
            started_utc=started, elapsed_seconds=time.perf_counter()-t0,
            jit_warmup_seconds=jit_warmup_seconds, implementation="Numba compiled kernel",
            expected_total_path_updates=n_paths*sum(LEVELS)),
        environment=dict(python=sys.version,numpy=np.__version__,numba=numba_version,platform=platform.platform(),
            executable=sys.executable),
        diagnostics=dict(brownian=brownian, states={str(k):v for k,v in state_diagnostics.items()},
            asset_expectation_target=target,
            asset_expectation_note="Bounded g makes the exact stochastic exponential a martingale. Log-EM also preserves this first moment in expectation. This checks implementation, not weak order.",
            total_path_updates=sum(d["updates"] for d in state_diagnostics.values())),
        terminal_asset_mean=mean_summary,
        terminal_payoff_mean={str(n):payoffs[n].summary() for n in LEVELS},
        convergence=rows, reference_checks=refs, rate_fits=fits,
        interpretation=dict(reference_residual_to_coarse_strong_ratio=ratios,
            reference_residual_below_ten_percent={n:ratio<.1 for n,ratio in ratios.items()},
            prespecified_strong_fit_steps=[8,16,32,64],
            fit_window_reference_screen_passed=all(ratios[str(n)]<.1 for n in (8,16,32,64)),
            strong="Empirical strong slopes use a finite EM reference. The prespecified coarsest-four-level fit is less reference-sensitive; all-level fits are descriptive only.",
            weak="Weak bias is the SIGNED mean of P_h-P_ref; it is not E[abs(P_h-P_ref)]. A confidence interval crossing zero does not resolve the bias.",
            reference="Nested 2048->4096 and 4096->8192 checks share Brownian paths. Last refinement discrepancy indicates reference sensitivity; it is not a rigorous bound on exact-solution error.",
            uncertainty="Pointwise normal 95% CIs quantify Monte Carlo sampling error only, not discretization error or simultaneous coverage."))
    assert summary["diagnostics"]["total_path_updates"] == n_paths*sum(LEVELS)
    assert all(d["all_states_finite"] and d["all_asset_states_positive_finite"] and
               d["all_terminal_assets_positive_finite"] for d in state_diagnostics.values())
    (ROOT/"results"/"nonaffine_summary.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    write_csv(ROOT/"results"/"nonaffine_convergence.csv",rows,
        ("n_steps","h","reference_steps","reference_h"))
    write_csv(ROOT/"results"/"nonaffine_reference_checks.csv",refs,("coarser_steps","finer_steps"))
    np.savez_compressed(ROOT/"results"/"nonaffine_terminals.npz",
        **{f"S_{n}":s for n,s in terminal_samples.items()}, seed=seed, n_paths=n_paths)
    draw_plots(summary)
    print(json.dumps(dict(elapsed_seconds=summary["simulation"]["elapsed_seconds"],
        finest_reference_rate_fits=fits[str(max(REFERENCES))],
        reference_residual_to_coarse_strong_ratio=ratios),indent=2),flush=True)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths",type=int,default=100000)
    parser.add_argument("--batch-size",type=int,default=512)
    parser.add_argument("--seed",type=int,default=2026090804)
    args = parser.parse_args()
    run(args.paths,args.batch_size,args.seed)




