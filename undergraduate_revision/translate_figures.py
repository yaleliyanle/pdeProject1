"""Chinese labels for the five existing report figures; no new experiment."""
from pathlib import Path
from statistics import NormalDist
import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "results"
OUT = HERE / "figures"
font = Path.home() / "Library/Fonts/NotoSansCJKsc-Regular.otf"
if font.exists():
    font_manager.fontManager.addfont(str(font))
plt.rcParams.update({"font.family": "Noto Sans CJK SC", "font.size": 10,
                     "axes.unicode_minus": False, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "legend.fontsize": 8, "legend.frameon": False})
COLORS = {"EM": "#276B98", "Milstein": "#BC593B", "Exact": "#43634C"}


def save(fig, name):
    fig.savefig(OUT / f"{name}_中文.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    with (SOURCE / "gbm_convergence.csv").open(encoding="utf-8-sig") as f:
        rows = [{k: v if k == "method" else float(v) for k, v in row.items()}
                for row in csv.DictReader(f)]
    na = json.loads((SOURCE / "nonaffine_summary.json").read_text())
    gs = json.loads((SOURCE / "gbm_summary.json").read_text())
    for weak in (False, True):
        fig, ax = plt.subplots(figsize=(6.5, 3.45), layout="constrained")
        for name in ("EM", "Milstein"):
            rr = [r for r in rows if r["method"] == name]
            h = np.array([r["h"] for r in rr])
            y = np.array([-r["weak_bias_cv"] if weak else r["strong_l1"] for r in rr])
            se = [1.96*r["weak_cv_se" if weak else "strong_se"] for r in rr]
            ax.errorbar(h, y, yerr=se, fmt="o-" if name == "EM" else "s-",
                        ms=4, capsize=2, color=COLORS[name], label=name)
        if weak:
            ax.plot(h, [-r["analytic_mean_bias"] for r in rr], "k--", label="解析偏差绝对值")
        else:
            em = [r for r in rows if r["method"] == "EM"]
            ax.plot(h, em[0]["strong_l1"]*np.sqrt(h/h[0]), ":", color="gray", label="半阶参考线")
            ax.plot(h, y[0]*(h/h[0]), "--", color="gray", label="一阶参考线")
        ax.set(xscale="log", yscale="log", xlabel="时间步长 h",
               ylabel="均值偏差的绝对值" if weak else "终值平均绝对误差")
        ax.grid(alpha=.2); ax.legend()
        save(fig, "report_gbm_weak" if weak else "report_gbm_strong")

    fig, ax = plt.subplots(figsize=(6.5, 3.45), layout="constrained")
    for ref, color in zip((2048, 4096, 8192), ("#C78A35", "#619666", "#276B98")):
        rr = [r for r in na["convergence"] if r["reference_steps"] == ref]
        ax.errorbar([r["h"] for r in rr], [r["strong_l1"]["mean"] for r in rr],
                    yerr=[1.96*r["strong_l1"]["standard_error"] for r in rr],
                    fmt="o-", ms=4, capsize=2, color=color, label=f"参考 {ref} 步")
    h = np.array([r["h"] for r in rr])
    ax.plot(h, rr[0]["strong_l1"]["mean"]*np.sqrt(h/h[0]), "k:", label="半阶参考线")
    ax.set(xscale="log", yscale="log", xlabel="粗网格步长 h", ylabel="与参考的终值平均绝对差")
    ax.grid(alpha=.2); ax.legend()
    save(fig, "report_nonaffine_strong")

    fig, ax = plt.subplots(figsize=(6.5, 3.45), layout="constrained")
    ax.errorbar(range(len(rr)), [r["weak_payoff_difference"]["mean"] for r in rr],
                yerr=[1.96*r["weak_payoff_difference"]["standard_error"] for r in rr],
                fmt="o-", capsize=4, color=COLORS["EM"])
    ax.axhline(0, color="gray", ls="--")
    ax.set(xticks=range(len(rr)), xticklabels=[f'1/{r["n_steps"]}' for r in rr],
           xlabel="粗网格步长 h", ylabel="带符号的配对收益差")
    ax.grid(axis="y", alpha=.2)
    save(fig, "report_nonaffine_weak")

    with np.load(SOURCE / "gbm_terminal_samples.npz") as data:
        samples = {"Exact": data["exact"], "EM": data["em_coarse"], "Milstein": data["milstein_coarse"]}
    labels = {"Exact": "精确模拟", "EM": "EM", "Milstein": "Milstein"}
    p = gs["parameters"]
    s0, mu, sigma, t = (p[k] for k in ("S0", "mu", "sigma", "T"))
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4), layout="constrained")
    lo = min(v.min() for v in samples.values()); hi = max(v.max() for v in samples.values())
    bins = np.linspace(lo, hi, 95)
    probs = np.linspace(.001, .999, 199)
    theoretical = s0*np.exp((mu-.5*sigma**2)*t+sigma*np.sqrt(t)*np.array([NormalDist().inv_cdf(q) for q in probs]))
    for name, values in samples.items():
        axes[0].hist(values, bins=bins, density=True, histtype="step", color=COLORS[name], label=labels[name])
        axes[1].plot(theoretical, np.quantile(values, probs), color=COLORS[name], label=labels[name])
    x = np.linspace(max(1e-3, lo*.9), hi*1.04, 1200)
    z = (np.log(x/s0)-(mu-.5*sigma**2)*t)/(sigma*np.sqrt(t))
    axes[0].plot(x, np.exp(-.5*z*z)/(x*sigma*np.sqrt(2*np.pi*t)), "k--", label="理论对数正态密度")
    axes[1].plot(theoretical, theoretical, "k--", label="相等参考线")
    axes[0].set(xlabel="终值价格", ylabel="概率密度", title="终值分布，h=1/8")
    axes[1].set(xlabel="理论对数正态分位数", ylabel="经验分位数", title="分位数比较")
    for ax in axes: ax.legend()
    save(fig, "gbm_distribution")
    print("Translated five figures from saved data.")


if __name__ == "__main__":
    main()
