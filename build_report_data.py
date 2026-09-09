"""Generate LaTeX tables and report-specific plots from saved experiment results."""
from pathlib import Path
import csv
import json
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/".deps"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R,F=ROOT/"results",ROOT/"figures"
g=json.loads((R/"gbm_summary.json").read_text(encoding="utf-8"))
a=json.loads((R/"nonaffine_summary.json").read_text(encoding="utf-8"))
with (R/"gbm_convergence.csv").open(encoding="utf-8-sig") as stream:
    rows=[{k:(v if k=="method" else float(v)) for k,v in r.items()}
          for r in csv.DictReader(stream)]
ref=a["simulation"]["finest_steps"]
na=[r for r in a["convergence"] if r["reference_steps"]==ref]
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
    "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,
    "savefig.dpi":240,"legend.frameon":False})

def write(name,text):
    (R/name).write_text(text+"\n",encoding="utf-8")

def table(name,caption,cols,headers,data):
    lines=[r"\begin{table}[H]\centering\small",r"\caption{"+caption+"}",
           r"\begin{tabular}{"+cols+r"}\toprule"," & ".join(headers)+r"\\\midrule"]
    lines += [" & ".join(map(str,row))+r"\\" for row in data]
    lines += [r"\bottomrule\end{tabular}",r"\end{table}"]
    write(name,"\n".join(lines))

def num(v,d=5):
    return f"{v:.{d}f}"
def sci(v):
    mantissa,exponent=f"{v:.3e}".split("e")
    return r"$"+mantissa+r"\times10^{"+str(int(exponent))+r"}$"
def interval(lo,hi,d=5):
    return "["+num(lo,d)+", "+num(hi,d)+"]"
def pm(mean,se,d=5):
    return "$"+num(mean,d)+r"\pm"+num(1.96*se,d)+"$"
def save(fig,name):
    for ext in ("png","pdf"):
        fig.savefig(F/(name+"."+ext),bbox_inches="tight")
    plt.close(fig)

macros={}
def macro(k,v):
    macros[k]=str(v)
for method,label in [("EM","EM"),("Milstein","Mil")]:
    s=g["slopes"][method]
    macro("GBM"+label+"Rate",num(s["strong_l1_finest_5"],3))
    macro("GBM"+label+"WeakRate",num(s["weak_cv_finest_5"],3))
macro("GBMAnalyticWeakRate",num(g["slopes"]["EM"]["weak_analytic_all_8"],4))
macro("GBMFitWindow",r"$N=64,128,256,512,1024$")
mom=g["exact_terminal_moments"]
macro("GBMExactMean",num(mom["empirical_mean"],4))
macro("GBMExactVariance",num(mom["empirical_variance"],4))
macro("GBMExactMeanCI",interval(mom["empirical_mean"]-1.96*mom["empirical_mean_se"],
                            mom["empirical_mean"]+1.96*mom["empirical_mean_se"],4))
fit=a["rate_fits"][str(ref)]["strong_coarse"]
macro("NARate",num(fit["slope"],3))
macro("NAFitWindow","$N="+",".join(map(str,fit["steps"]))+"$")
m=a["terminal_asset_mean"][str(ref)]
p=a["terminal_payoff_mean"][str(ref)]
macro("NAExactMean",num(m["mean"],5))
macro("NAExactMeanCI",interval(m["ci95_low"],m["ci95_high"],5))
macro("NAPayoff",num(p["mean"],5))
macro("NAPayoffCI",interval(p["ci95_low"],p["ci95_high"],5))
unresolved=[r["n_steps"] for r in na if r["weak_payoff_difference"]["ci95_low"]
            *r["weak_payoff_difference"]["ci95_high"]<=0]
if unresolved:
    text=("The 95\\% intervals include zero at $N="+",".join(map(str,unresolved))+
          "$. No weak order is assigned to the complete grid range. ")
else:
    text="All displayed intervals exclude zero, but this alone does not establish an asymptotic order. "
wf=a["rate_fits"][str(ref)]["weak_coarse"]
if wf.get("slope") is not None:
    text+=(f"The prespecified coarse-window descriptive slope is {wf['slope']:.3f}; "
           "it is not presented as a verified theoretical weak order. ")
text+=("The finest-reference payoff is estimated as "+num(p["mean"],5)+
       " with interval "+interval(p["ci95_low"],p["ci95_high"],5)+".")
macro("NAWeakInterpretation",text)
ratios=a["interpretation"]["reference_residual_to_coarse_strong_ratio"]
selected=[ratios[str(n)] for n in fit["steps"]]
coarsest=a["simulation"]["reference_steps"][0]
last=a["reference_checks"][-1]
text=(f"The last refinement discrepancy is {last['strong_l1']['mean']:.5f}. "
      f"It is {100*min(selected):.1f}\\% to {100*max(selected):.1f}\\% of the coarse "
      "strong differences on the prespecified fitting window. ")
if max(selected)<.1:
    text+=("This meets the practical 10\\% reference-sensitivity criterion used for that window. ")
else:
    text+=("The 10\\% reference-sensitivity criterion is not met throughout that window. ")
text+=(f"For $N=256$, the ratio is {100*ratios['256']:.1f}\\%, so the finest coarse points "
       "are retained as sensitivity evidence, not used for the principal rate claim. "
       "The two refinements decrease the strong discrepancy; their paired payoff intervals "
       "assess whether the benchmark changes at a detectable weak scale. "
       "Neither a small refinement difference nor a zero-containing interval is a rigorous bound "
       "on the unknown continuous-time error.")
macro("NAReferenceInterpretation",text)
write("report_values.tex","\n".join(r"\newcommand{\\".replace("\\\\","\\")+k+"}{"+v+"}"
                                  for k,v in macros.items()))

protocol=[
["GBM production paths",f"{g['paths']:,}","Independent pilot",f"{g['pilot_paths']:,}"],
["GBM seed",str(g["seed"]),"Pilot seed",str(g["pilot_seed"])],
["GBM grids $N$","8 to 1024","GBM batch",str(g["batch_size"])],
["Non-affine paths",f"{a['simulation']['n_paths']:,}","Seed",str(a["simulation"]["seed"])],
["Coarse $N$","8,16,32,64,128,256","Reference $N$",",".join(map(str,a["simulation"]["reference_steps"]))],
["GBM elapsed",f"{g['runtime_seconds']:.1f} s","Non-affine elapsed",f"{a['simulation']['elapsed_seconds']:.1f} s"],
]
table("protocol_table.tex","Computational protocol; grids are nested powers of two.","lrlr",
      ["Quantity","Value","Quantity","Value"],protocol)

strong=[]
weak=[]
for n in [8,16,32,64,128,256,512,1024]:
    em=next(r for r in rows if r["method"]=="EM" and r["N"]==n)
    mi=next(r for r in rows if r["method"]=="Milstein" and r["N"]==n)
    strong.append([f"1/{n}",pm(em["strong_l1"],em["strong_se"]),
                   pm(mi["strong_l1"],mi["strong_se"])])
    if n in [8,32,128,512,1024]:
        weak.append([f"1/{n}",sci(em["analytic_mean_bias"]),
             sci(em["weak_bias_cv"])+r" $\pm$ "+sci(1.96*em["weak_cv_se"]),
             sci(mi["weak_bias_cv"])+r" $\pm$ "+sci(1.96*mi["weak_cv_se"])])
table("gbm_strong_table.tex","GBM strong error estimates with 95\\% interval half-widths.","rrr",
      ["$h$","EM","Milstein"],strong)
table("gbm_weak_table.tex","Signed weak bias; controlled estimates plus 95\\% half-widths.","rrrr",
      ["$h$","Analytic bias","EM controlled","Milstein controlled"],weak)

with (R/"gbm_quantiles.csv").open(encoding="utf-8-sig") as stream:
    quant=list(csv.DictReader(stream))
table("gbm_quantile_table.tex","Terminal quantiles; numerical columns use $h=1/8$.","rrrrr",
      ["$p$","Lognormal","Exact simulation","EM","Milstein"],
      [[f"{float(r['probability']):.2f}"]+[num(float(r[k]),3) for k in
        ["exact_lognormal_quantile","exact_empirical_quantile_h_1_8",
         "em_empirical_quantile_h_1_8","milstein_empirical_quantile_h_1_8"]]
        for r in quant if .01<=float(r["probability"])<=.99])

table("nonaffine_strong_table.tex",f"Strong discrepancy against $h_{{\\rm ref}}=1/{ref}$; 95\\% half-widths.",
      "rrr",["$h$","$\\mathbb E|S_h-S_{\\rm ref}|$","Last reference difference / error"],
      [[f"1/{r['n_steps']}",pm(r["strong_l1"]["mean"],r["strong_l1"]["standard_error"]),
        f"{100*ratios[str(r['n_steps'])]:.1f}\\%"] for r in na])
table("nonaffine_weak_table.tex",f"Signed paired payoff differences against $h_{{\\rm ref}}=1/{ref}$.",
      "rrrr",["$h$","Estimated bias","95\\% interval","Zero excluded"],
      [[f"1/{r['n_steps']}",num(r["weak_payoff_difference"]["mean"]),
        interval(r["weak_payoff_difference"]["ci95_low"],r["weak_payoff_difference"]["ci95_high"]),
        "No" if r["n_steps"] in unresolved else "Yes"] for r in na])
table("nonaffine_reference_table.tex","Coupled refinement of the numerical reference.",
      "rrr",["Refinement $N_a\\to N_b$","Strong difference","Signed payoff difference and 95\\% CI"],
      [[f"{r['coarser_steps']} $\\to$ {r['finer_steps']}",
        pm(r["strong_l1"]["mean"],r["strong_l1"]["standard_error"]),
        num(r["weak_payoff_difference"]["mean"],6)+" "+
        interval(r["weak_payoff_difference"]["ci95_low"],r["weak_payoff_difference"]["ci95_high"],6)]
        for r in a["reference_checks"]])
b=a["diagnostics"]["brownian"]
st=a["diagnostics"]["states"][str(ref)]
drows=[
["Increment variance 1",sci(b["variance"][0]),sci(b["grid_h"])],
["Increment variance 2",sci(b["variance"][1]),sci(b["grid_h"])],
["Increment correlation",num(b["correlation"],6),"$-0.700000$"],
["Sampled increments",f"{b['n_increments']:,}","Predetermined first batch"],
["Total path updates",f"{a['diagnostics']['total_path_updates']:,}","All grids"],
["Finite intermediate states","Pass" if st["all_states_finite"] else "Fail","$X$ and $Y$"],
["Positive finite prices","Pass" if st["all_asset_states_positive_finite"] else "Fail","All observed states"],
]
write("nonaffine_diagnostics_table.tex",r"\begin{tabular}{lrr}\toprule Quantity & Observed & Target or scope\\\midrule"+
      "\n"+"\n".join(" & ".join(row)+r"\\" for row in drows)+
      "\n"+r"\bottomrule\end{tabular}")

colors={"EM":"#276B98","Milstein":"#BC593B"}
fig,ax=plt.subplots(figsize=(6.5,3.45),layout="constrained")
for name in colors:
    rr=[r for r in rows if r["method"]==name]
    h=np.array([r["h"] for r in rr])
    y=np.array([r["strong_l1"] for r in rr])
    ax.errorbar(h,y,yerr=[1.96*r["strong_se"] for r in rr],
                fmt="o-",capsize=2,color=colors[name],label=name)
    power=.5 if name=="EM" else 1
    ax.plot(h,y[-1]*1.45*(h/h[-1])**power,"--",color=colors[name],alpha=.55,
            label=f"Order {power:g} guide")
ax.set(xscale="log",yscale="log",xlabel="Time step h",ylabel="Terminal strong L1 error")
ax.legend(fontsize=9)
ax.grid(alpha=.15)
save(fig,"report_gbm_strong")

fig,ax=plt.subplots(figsize=(6.5,3.1),layout="constrained")
for name in colors:
    rr=[r for r in rows if r["method"]==name]
    ax.errorbar([r["h"] for r in rr],[-r["weak_bias_cv"] for r in rr],
                yerr=[1.96*r["weak_cv_se"] for r in rr],fmt="o-" if name=="EM" else "s-",
                mfc="white",capsize=2,color=colors[name],label=name+" with controls")
ax.plot(h,[-r["analytic_mean_bias"] for r in rr],"k--",lw=1.1,label="Analytic mean bias")
ax.set(xscale="log",yscale="log",xlabel="Time step h",ylabel="Mean bias magnitude")
ax.legend(fontsize=9)
ax.grid(alpha=.15)
save(fig,"report_gbm_weak")

fig,ax=plt.subplots(figsize=(6.5,3.55),layout="constrained")
for reference,color in zip(a["simulation"]["reference_steps"],["#B99043","#5B8F6A","#276B98"]):
    rr=[r for r in a["convergence"] if r["reference_steps"]==reference]
    h=np.array([r["h"] for r in rr])
    y=np.array([r["strong_l1"]["mean"] for r in rr])
    ax.errorbar(h,y,yerr=[1.96*r["strong_l1"]["standard_error"] for r in rr],
       marker="o",capsize=2,color=color,label=f"Reference 1/{reference}")
ax.plot(h,y[0]*1.2*np.sqrt(h/h[0]),"--",color="#777777",label="Order 1/2 guide")
ax.set(xscale="log",yscale="log",xlabel="Coarse time step h",ylabel="Terminal strong discrepancy")
ax.legend(fontsize=8.5)
ax.grid(alpha=.15)
save(fig,"report_nonaffine_strong")

fig,ax=plt.subplots(figsize=(6.5,3.5),layout="constrained")
ax.errorbar(range(len(na)),[r["weak_payoff_difference"]["mean"] for r in na],
    yerr=[1.96*r["weak_payoff_difference"]["standard_error"] for r in na],
    fmt="o-",color="#276B98",capsize=4)
ax.axhline(0,ls="--",color="#777777",lw=1)
ax.set(xticks=range(len(na)),xticklabels=[f"1/{r['n_steps']}" for r in na],
       xlabel="Coarse time step h",ylabel="Signed paired payoff difference")
ax.grid(axis="y",alpha=.15)
save(fig,"report_nonaffine_weak")
print("Generated report values, 8 tables, and 4 report figures from saved results.")


summary_lines=[
    "Problem 4 Financial SDE Coursework - completed run",
    "="*58,
    f"GBM production paths: {g['paths']}; independent pilot: {g['pilot_paths']}",
    "Strong slopes (N=64,128,256,512,1024):",
    f"  EM: {g['slopes']['EM']['strong_l1_finest_5']:.8f}",
    f"  Milstein: {g['slopes']['Milstein']['strong_l1_finest_5']:.8f}",
    "Controlled weak mean slopes (same window):",
    f"  EM: {g['slopes']['EM']['weak_cv_finest_5']:.8f}",
    f"  Milstein: {g['slopes']['Milstein']['weak_cv_finest_5']:.8f}",
    f"Analytic weak mean slope (all 8 grids): {g['slopes']['EM']['weak_analytic_all_8']:.8f}",
    f"GBM elapsed, including pilot, production and figures: {g['runtime_seconds']:.2f} s",
    "",
    f"Non-affine paths: {a['simulation']['n_paths']}",
    f"Reference step counts: {a['simulation']['reference_steps']}",
    f"Principal strong window: {fit['steps']}",
    f"Empirical strong slope: {fit['slope']:.8f}",
    f"Final reference strong difference: {last['strong_l1']['mean']:.8f}",
    f"Last reference difference/coarse strong error: {100*min(selected):.2f}% to {100*max(selected):.2f}% on principal window",
    f"Unresolved paired payoff bias (95% CI includes zero), N={unresolved}",
    f"Finest terminal mean: {m['mean']:.8f}, CI [{m['ci95_low']:.8f}, {m['ci95_high']:.8f}]",
    f"Finest undiscounted payoff mean: {p['mean']:.8f}, CI [{p['ci95_low']:.8f}, {p['ci95_high']:.8f}]",
    f"Non-affine elapsed: {a['simulation']['elapsed_seconds']:.2f} s (JIT warmup separately logged)",
    "",
    "No theoretical weak order is claimed for the non-affine payoff.",
    "Reference discrepancies are numerical evidence, not exact-solution errors.",
    "Pointwise Monte Carlo intervals do not cover discretization uncertainty.",
    "See results/verification.json for independent checks and README.md for reproduction."
]
(ROOT/"numerical_summary.txt").write_text("\n".join(summary_lines)+"\n",encoding="utf-8")

