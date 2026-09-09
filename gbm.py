"""Reproducible GBM experiments for problem 4.
Self-selected parameters: S0=100, mu=.05, sigma=.30, T=1.
Run: python gbm.py [--paths 160000] [--pilot-paths 20000] [--batch-size 2000]
Requires NumPy and Matplotlib. Independent-pilot controls reduce weak MC noise.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
from pathlib import Path
from statistics import NormalDist
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".deps"))
import numpy as np

S0, MU, SIGMA, T = 100.0, 0.05, 0.30, 1.0
LEVELS = np.array([8, 16, 32, 64, 128, 256, 512, 1024], dtype=int)
METHODS = ("EM", "Milstein")
SEED = 2026090804
Z95 = 1.959963984540054


def exact_moments():
    mean = S0 * math.exp(MU * T)
    variance = S0**2 * math.exp(2 * MU * T) * math.expm1(SIGMA**2 * T)
    return mean, variance


def analytic_discrete_moments(n, method):
    h = T / n
    second_factor = (1 + MU * h)**2 + SIGMA**2 * h
    if method == "Milstein":
        second_factor += 0.5 * SIGMA**4 * h**2
    mean = S0 * math.exp(n * math.log1p(MU * h))
    variance = S0**2 * second_factor**n - mean**2
    return mean, variance


def simulate_batch(rng, size):
    """All levels aggregate the same fine Brownian increments.

    Weighting by ST/E[ST] exponentially tilts independent dW to N(sigma*h,h).
    If Q=sum(dW^2-h), H3=sum(dW^3-3h*dW), then
    E_tilt Q=sigma^2*T*h; E_tilt H3=sigma^3*T*h^2;
    E_tilt Q^2=2*T*h+4*sigma^2*T*h^2+sigma^4*T^2*h^2.
    These formulas give five exactly zero-mean controls.
    """
    nfine = int(LEVELS[-1])
    fine = rng.normal(0, math.sqrt(T / nfine), (size, nfine))
    w = fine.sum(axis=1)
    exact = S0 * np.exp((MU - 0.5 * SIGMA**2) * T + SIGMA * w)
    weighted = exact / exact_moments()[0]
    for n in LEVELS:
        h = T / int(n)
        dw = fine.reshape(size, int(n), nfine // int(n)).sum(axis=2)
        dw2 = dw * dw
        base = 1 + MU * h + SIGMA * dw
        em = S0 * np.prod(base, axis=1)
        mil = S0 * np.prod(base + 0.5 * SIGMA**2 * (dw2 - h), axis=1)
        q = dw2.sum(axis=1) - T
        h3 = (dw * (dw2 - 3 * h)).sum(axis=1)
        eq2 = 2*T*h + 4*SIGMA**2*T*h**2 + SIGMA**4*T**2*h**2
        controls = np.column_stack((
            weighted - 1,
            weighted * (w-SIGMA*T) / math.sqrt(T),
            weighted * (q-SIGMA**2*T*h) / math.sqrt(2*T*h),
            weighted * (h3-SIGMA**3*T*h**2) / math.sqrt(6*T*h**2),
            weighted * (q*q-eq2) / (math.sqrt(8)*T*h),
        ))
        yield int(n), exact, np.column_stack((em, mil)), controls


def fit_controls(rng, count, batch):
    """Centered OLS on a pilot independent of all final MC estimates."""
    sx, sy = np.zeros((len(LEVELS),5)), np.zeros((len(LEVELS),2))
    sxx, sxy = np.zeros((len(LEVELS),5,5)), np.zeros((len(LEVELS),5,2))
    for offset in range(0, count, batch):
        for k, (_, exact, endpoints, x) in enumerate(simulate_batch(rng, min(batch,count-offset))):
            y = endpoints-exact[:,None]
            sx[k] += x.sum(axis=0)
            sy[k] += y.sum(axis=0)
            sxx[k] += x.T @ x
            sxy[k] += x.T @ y
    betas = np.empty((len(LEVELS),5,2))
    for k in range(len(LEVELS)):
        covx = sxx[k] - np.outer(sx[k],sx[k])/count
        covxy = sxy[k] - np.outer(sx[k],sy[k])/count
        betas[k] = np.linalg.solve(covx,covxy)
    return betas


def mean_se(total, squares, count):
    means = total/count
    variances = np.maximum((squares-total*total/count)/(count-1),0)
    return means, np.sqrt(variances/count)


def write_csv(path, rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figures(rows, samples, summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family":"DejaVu Sans","font.size":10,"axes.labelsize":11,
        "axes.titlesize":12,"axes.spines.top":False,"axes.spines.right":False,
        "axes.linewidth":.7,"xtick.direction":"out","ytick.direction":"out",
        "legend.frameon":False,"savefig.dpi":320,"pdf.fonttype":42,"ps.fonttype":42,
    })
    colors={"EM":"#2C6E9B","Milstein":"#C65A36","Exact":"#273D32"}
    def save(fig,stem):
        for ext in ("png","pdf"):
            fig.savefig(output/f"{stem}.{ext}",bbox_inches="tight",facecolor="white")
        plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10.2,4.1),constrained_layout=True)
    for method in METHODS:
        records=[r for r in rows if r["method"]==method]
        h=np.array([r["h"] for r in records])
        strong=np.array([r["strong_l1"] for r in records])
        strongse=np.array([r["strong_se"] for r in records])
        weak=np.array([r["weak_bias_cv"] for r in records])
        weakse=np.array([r["weak_cv_se"] for r in records])
        p=summary["slopes"][method]["strong_l1_finest_5"]
        axes[0].errorbar(h,strong,yerr=Z95*strongse,fmt="o-",markersize=4,
            linewidth=1.4,capsize=2,color=colors[method],label=f"{method}, slope {p:.3f}")
        axes[1].errorbar(h,-weak,yerr=Z95*weakse,
            fmt="o-" if method=="EM" else "s-",
            markerfacecolor="white" if method=="Milstein" else colors[method],
            markersize=4,linewidth=1.2,capsize=2,color=colors[method],
            label=f"{method}, MC + controls")
    ab=np.array([-r["analytic_mean_bias"] for r in rows if r["method"]=="EM"])
    axes[1].plot(h,ab,"--",color="#444444",linewidth=1.25,label="Analytic bias (both methods)",zorder=5)
    for ax in axes:
        ax.set_xscale("log",base=2)
        ax.set_yscale("log")
        ax.set_xlabel("Time step h")
        ax.set_xticks(h[::2],[f"1/{int(round(1/x))}" for x in h[::2]])
        ax.legend(fontsize=8.5,loc="upper left")
        ax.grid(axis="y",alpha=.15,linewidth=.5)
    axes[0].set_ylabel(r"Terminal strong error $E|S_T^h-S_T|$")
    axes[1].set_ylabel(r"Mean bias magnitude $E[S_T]-E[S_T^h]$")
    axes[0].set_title("(a) Strong convergence: 1/2 versus 1",loc="left")
    axes[1].set_title("(b) First-order weak error for f(s) = s",loc="left")
    fig.suptitle(f"GBM | {summary['paths']:,} coupled paths; error bars: 95% Monte Carlo CI",fontsize=12)
    save(fig,"gbm_convergence")

    rng=np.random.default_rng(SEED+2)
    n,ns,count=1024,32,3
    fine=rng.normal(0,math.sqrt(T/n),(count,n))
    t=np.linspace(0,T,n+1)
    exact=S0*np.exp((MU-.5*SIGMA**2)*t[None,:]+SIGMA*np.column_stack((np.zeros(count),np.cumsum(fine,axis=1))))
    dw=fine.reshape(count,ns,n//ns).sum(axis=2)
    h=T/ns
    base=1+MU*h+SIGMA*dw
    em=S0*np.column_stack((np.ones(count),np.cumprod(base,axis=1)))
    mil=S0*np.column_stack((np.ones(count),np.cumprod(base+.5*SIGMA**2*(dw*dw-h),axis=1)))
    tc=np.linspace(0,T,ns+1)
    fig,axes=plt.subplots(1,3,figsize=(10.3,3.6),sharey=True,constrained_layout=True)
    for i,ax in enumerate(axes):
        ax.plot(t,exact[i],color=colors["Exact"],linewidth=1.2,label="Exact")
        ax.plot(tc,em[i],"o--",color=colors["EM"],linewidth=.85,markersize=2.5,label="EM")
        ax.plot(tc,mil[i],"s:",color=colors["Milstein"],linewidth=.95,markersize=2.2,label="Milstein")
        ax.set_xlabel("Time t")
        ax.set_title(f"({chr(97+i)}) Coupled path {i+1}",loc="left")
    axes[0].set_ylabel("Asset price S(t)")
    axes[-1].legend(loc="best",fontsize=8)
    fig.suptitle("Exact GBM and numerical price paths | coarse time step h = 1/32",fontsize=12)
    save(fig,"gbm_paths")

    fig,axes=plt.subplots(1,2,figsize=(10.2,4.0),constrained_layout=True)
    vmin=min(float(x.min()) for x in samples.values())
    vmax=max(float(x.max()) for x in samples.values())
    bins=np.linspace(vmin,vmax,95)
    for name in ("Exact","EM","Milstein"):
        axes[0].hist(samples[name],bins=bins,density=True,histtype="step",
            linewidth=1.2,color=colors[name],label=name)
    x=np.linspace(max(1e-3,vmin*.9),vmax*1.04,1200)
    z=(np.log(x/S0)-(MU-.5*SIGMA**2)*T)/(SIGMA*math.sqrt(T))
    density=np.exp(-.5*z*z)/(x*SIGMA*math.sqrt(2*math.pi*T))
    axes[0].plot(x,density,color="#222222",linestyle="--",linewidth=1.1,label="Exact lognormal density")
    axes[0].set_xlabel("Terminal price")
    axes[0].set_ylabel("Probability density")
    axes[0].set_title("(a) Terminal distributions, h = 1/8",loc="left")
    axes[0].legend(fontsize=8)
    probs=np.linspace(.001,.999,199)
    nd=NormalDist()
    theoretical=S0*np.exp((MU-.5*SIGMA**2)*T+SIGMA*math.sqrt(T)*np.array([nd.inv_cdf(float(p)) for p in probs]))
    for name in ("Exact","EM","Milstein"):
        axes[1].plot(theoretical,np.quantile(samples[name],probs),color=colors[name],
            linewidth=1.25,linestyle={"Exact":"-","EM":"--","Milstein":":"}[name],label=name)
    axes[1].plot(theoretical,theoretical,color="#666666",linewidth=.8,linestyle="-.",label="Identity")
    axes[1].set_xlabel("Exact lognormal quantiles")
    axes[1].set_ylabel("Empirical terminal quantiles")
    axes[1].set_title("(b) Quantile comparison, p = .001 to .999",loc="left")
    axes[1].legend(fontsize=8)
    fig.suptitle("Distribution sanity check | all simulated endpoints included",fontsize=12)
    save(fig,"gbm_distribution")


def run(paths,pilot_paths,batch_size):
    import matplotlib
    start=time.perf_counter()
    results,figures=ROOT/"results",ROOT/"figures"
    results.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    log_lines=[]
    def log(text):
        print(text,flush=True)
        log_lines.append(text)
    log("GBM problem 4 experiment; self-selected S0=100, mu=.05, sigma=.30, T=1")
    log(f"seed={SEED}; paths={paths}; independent pilot={pilot_paths}; batch={batch_size}; finest N={LEVELS[-1]}")
    betas=fit_controls(np.random.default_rng(SEED+1),pilot_paths,batch_size)
    log(f"Independent-pilot control fit finished in {time.perf_counter()-start:.1f}s")
    sums=np.zeros((len(LEVELS),2,3))
    squares=np.zeros_like(sums)
    terminal_sums=np.zeros((len(LEVELS),2,2))
    negatives=np.zeros((len(LEVELS),2),dtype=np.int64)
    exact_samples,em_samples,mil_samples=[],[],[]
    finest_em,finest_mil=[],[]
    rng=np.random.default_rng(SEED)
    for offset in range(0,paths,batch_size):
        size=min(batch_size,paths-offset)
        for k,(_,exact,endpoints,controls) in enumerate(simulate_batch(rng,size)):
            error=endpoints-exact[:,None]
            corrected=error-controls@betas[k]
            metrics=np.stack((np.abs(error),error,corrected),axis=2)
            sums[k]+=metrics.sum(axis=0)
            squares[k]+=(metrics*metrics).sum(axis=0)
            terminal_sums[k,:,0]+=endpoints.sum(axis=0)
            terminal_sums[k,:,1]+=(endpoints*endpoints).sum(axis=0)
            negatives[k]+=(endpoints<=0).sum(axis=0)
            if k==0:
                exact_samples.append(exact.copy())
                em_samples.append(endpoints[:,0].copy())
                mil_samples.append(endpoints[:,1].copy())
            if k==len(LEVELS)-1:
                finest_em.append(endpoints[:,0].copy())
                finest_mil.append(endpoints[:,1].copy())
        if (offset+size)%40000==0 or offset+size==paths:
            log(f"Main simulation: {offset+size:,}/{paths:,} paths; elapsed {time.perf_counter()-start:.1f}s")
    samples={"Exact":np.concatenate(exact_samples),"EM":np.concatenate(em_samples),"Milstein":np.concatenate(mil_samples)}
    np.savez_compressed(results/"gbm_terminal_samples.npz",exact=samples["Exact"],
        em_coarse=samples["EM"],milstein_coarse=samples["Milstein"],
        em_fine=np.concatenate(finest_em),milstein_fine=np.concatenate(finest_mil))
    estimates,se=mean_se(sums,squares,paths)
    exact_mean,exact_variance=exact_moments()
    rows,moment_rows=[],[]
    for k,n in enumerate(LEVELS):
        h=T/int(n)
        analytic_bias=exact_mean*math.expm1(int(n)*math.log1p(MU*h)-MU*T)
        for m,method in enumerate(METHODS):
            row={"method":method,"N":int(n),"h":h}
            for metric,index,se_name in (("strong_l1",0,"strong_se"),("weak_bias_paired",1,"weak_paired_se"),("weak_bias_cv",2,"weak_cv_se")):
                row[metric]=float(estimates[k,m,index])
                row[se_name]=float(se[k,m,index])
                row[metric+"_ci_low"]=float(estimates[k,m,index]-Z95*se[k,m,index])
                row[metric+"_ci_high"]=float(estimates[k,m,index]+Z95*se[k,m,index])
            row["analytic_mean_bias"]=analytic_bias
            row["cv_variance_reduction"]=float((se[k,m,1]/se[k,m,2])**2)
            row["cv_z_vs_analytic"]=float((estimates[k,m,2]-analytic_bias)/se[k,m,2])
            rows.append(row)
            amean,avar=analytic_discrete_moments(int(n),method)
            totals=terminal_sums[k,m]
            emean=totals[0]/paths
            evar=(totals[1]-totals[0]**2/paths)/(paths-1)
            mse=math.sqrt(evar/paths)
            moment_rows.append({
                "method":method,"N":int(n),"h":h,"empirical_mean":float(emean),
                "analytic_discrete_mean":amean,"continuous_exact_mean":exact_mean,
                "mean_se":mse,"mean_z_vs_discrete":float((emean-amean)/mse),
                "empirical_variance":float(evar),"analytic_discrete_variance":avar,
                "continuous_exact_variance":exact_variance,
                "variance_relative_error_vs_discrete":float(evar/avar-1),
                "nonpositive_terminal_count":int(negatives[k,m])})
    write_csv(results/"gbm_convergence.csv",rows)
    write_csv(results/"gbm_terminal_stats.csv",moment_rows)
    nd=NormalDist()
    quantiles=[]
    for p in [.001,.01,.05,.25,.5,.75,.95,.99,.999]:
        q=S0*math.exp((MU-.5*SIGMA**2)*T+SIGMA*math.sqrt(T)*nd.inv_cdf(p))
        quantiles.append({
            "probability":p,"exact_lognormal_quantile":q,
            **{f"{name.lower()}_empirical_quantile_h_1_8":float(np.quantile(values,p))
               for name,values in samples.items()}})
    write_csv(results/"gbm_quantiles.csv",quantiles)
    slopes={}
    for method in METHODS:
        subset=[r for r in rows if r["method"]==method]
        x=np.log([r["h"] for r in subset])
        slopes[method]={
            "strong_l1_all_8":float(np.polyfit(x,np.log([r["strong_l1"] for r in subset]),1)[0]),
            "strong_l1_finest_5":float(np.polyfit(x[-5:],np.log([r["strong_l1"] for r in subset[-5:]]),1)[0]),
            "weak_cv_all_8":float(np.polyfit(x,np.log(np.abs([r["weak_bias_cv"] for r in subset])),1)[0]),
            "weak_cv_finest_5":float(np.polyfit(x[-5:],np.log(np.abs([r["weak_bias_cv"] for r in subset[-5:]])),1)[0]),
            "weak_analytic_all_8":float(np.polyfit(x,np.log(np.abs([r["analytic_mean_bias"] for r in subset])),1)[0])}
    emean=float(samples["Exact"].mean())
    evar=float(samples["Exact"].var(ddof=1))
    mse=math.sqrt(evar/paths)
    positivity=[]
    for n in LEVELS:
        h=T/int(n)
        # erfc preserves tiny Gaussian lower-tail probabilities unlike 1-cdf.
        zem=-(1+MU*h)/(SIGMA*math.sqrt(h))
        pem=.5*math.erfc(-zem/math.sqrt(2))
        positivity.append({
            "N":int(n),"h":h,"em_one_step_negative_probability":pem,
            "milstein_minimum_step_multiplier":.5*(1+(2*MU-SIGMA**2)*h),
            "milstein_one_step_negative_probability":0.0})
    summary={
        "experiment":"Problem 4: GBM numerical SDE experiment",
        "parameter_source":"Self-selected GBM benchmark; not specified by the assignment",
        "environment":{"python":platform.python_version(),"numpy":np.__version__,
            "matplotlib":matplotlib.__version__,"platform":platform.platform()},
        "timing_note":"runtime_seconds includes RNG, independent pilot, production simulation, result preparation, and figure generation. Non-affine timings are measured separately and are not a matched-work comparison.",
        "parameters":{"S0":S0,"mu":MU,"sigma":SIGMA,"T":T},
        "seed":SEED,"pilot_seed":SEED+1,"path_figure_seed":SEED+2,
        "paths":paths,"pilot_paths":pilot_paths,"batch_size":batch_size,
        "finest_steps":int(LEVELS[-1]),"step_counts":LEVELS.tolist(),
        "strong_error":"Terminal L1: sample mean of abs(S_h(T)-S_exact(T))",
        "weak_observable":"f(s)=s; signed bias E[S_h(T)]-E[S_exact(T)]",
        "coupling":"Fine increments aggregated for every coarse time step; same exact ST on every level",
        "confidence_intervals":"Pointwise normal 95% Monte Carlo intervals; no discretization or slope uncertainty included",
        "control_variates":{
            "description":"Five exactly centered Gaussian-tilt controls; centered OLS fitted only on an independent pilot",
            "features":["ST/M - 1","ST/M*(W-sigma*T)/sqrt(T)",
                "ST/M*(Q-sigma^2*T*h)/sqrt(2*T*h)",
                "ST/M*(H3-sigma^3*T*h^2)/sqrt(6*T*h^2)",
                "ST/M*(Q^2-[2*T*h+4*sigma^2*T*h^2+sigma^4*T^2*h^2])/(sqrt(8)*T*h)"],
            "definitions":"M=E[ST]; Q=sum(dW^2-h); H3=sum(dW^3-3*h*dW); W=sum(dW)",
            "betas_by_level_feature_method":betas.tolist()},
        "slopes":slopes,
        "exact_terminal_moments":{
            "analytic_mean":exact_mean,"analytic_variance":exact_variance,
            "empirical_mean":emean,"empirical_variance":evar,
            "empirical_mean_se":mse,"mean_z":(emean-exact_mean)/mse,
            "variance_relative_error":evar/exact_variance-1},
        "finest_step_errors":[r for r in rows if r["N"]==int(LEVELS[-1])],
        "positivity":{
            "scope":"Primary benchmark only; sigma^2=.09 < 2*mu=.10, hence all Milstein factors strictly positive",
            "levels":positivity},
        "checks":{
            "all_finite":bool(np.isfinite(estimates).all() and np.isfinite(se).all()),
            "strong_errors_decrease":bool(np.all(np.diff(estimates[:,:,0],axis=0)<0)),
            "all_cv_weak_biases_negative":bool(np.all(estimates[:,:,2]<0)),
            "max_abs_cv_z_vs_analytic":max(abs(r["cv_z_vs_analytic"]) for r in rows),
            "note":"A 95% interval need not contain the truth at every level; levels are correlated by Brownian coupling.",
            "total_nonpositive_terminal_count_across_levels":int(negatives.sum())},
        "runtime_seconds_before_figures":time.perf_counter()-start}
    make_figures(rows,samples,summary,figures)
    summary["runtime_seconds"]=time.perf_counter()-start
    (results/"gbm_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    log(json.dumps({"slopes":slopes,"exact_moments":summary["exact_terminal_moments"],"checks":summary["checks"]},ensure_ascii=False,indent=2))
    log(f"Completed in {summary['runtime_seconds']:.1f}s; figures and CSV/JSON saved under {ROOT}")
    (results/"gbm_run.log").write_text("\n".join(log_lines)+"\n",encoding="utf-8")
    assert summary["checks"]["all_finite"],"Non-finite simulation results"
    assert summary["checks"]["strong_errors_decrease"],"Strong errors fail to decrease"
    return summary


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths",type=int,default=160000)
    parser.add_argument("--pilot-paths",type=int,default=20000)
    parser.add_argument("--batch-size",type=int,default=2000)
    args=parser.parse_args()
    if args.paths<2 or args.pilot_paths<20 or args.batch_size<1:
        parser.error("Require paths >= 2, pilot-paths >= 20, batch-size >= 1")
    run(args.paths,args.pilot_paths,args.batch_size)

