"""One sample-size study plus report summaries from existing coursework data.

Run: python3 undergraduate_revision/sample_size_study.py
Requires NumPy. No new paths, resampling, seed search, or model fitting.
Writes only this revision's results/ folder; original results stay unchanged.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "results"
OUT = HERE / "results"
SIZES = (10_000, 40_000, 100_000)
COARSE, REFERENCE, STRIKE = 64, 8192, 100.0


def write_table(filename, caption, label, headers, rows, columns):
    text = "\\begin{table}[H]\\centering\\small\n"
    text += f"\\caption{{{caption}}}\\label{{{label}}}\n"
    text += f"\\begin{{tabular}}{{{columns}}}\\toprule\n"
    text += " & ".join(headers) + "\\\\\\midrule\n"
    text += "\n".join(" & ".join(row) + "\\\\" for row in rows)
    text += "\n\\bottomrule\\end{tabular}\n\\end{table}\n"
    (OUT / filename).write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    source = SOURCE / "nonaffine_terminals.npz"
    with np.load(source) as data:
        coarse = data[f"S_{COARSE}"]
        fine = data[f"S_{REFERENCE}"]
        assert coarse.shape == fine.shape == (100_000,)
        differences = np.maximum(coarse - STRIKE, 0) - np.maximum(fine - STRIKE, 0)
    assert np.isfinite(differences).all()
    records = []
    for m in SIZES:
        sample = differences[:m]  # Same paired rows, original saved order.
        mean = float(sample.mean())
        sd = float(sample.std(ddof=1))
        se = sd / math.sqrt(m)
        records.append(dict(paths=m, mean=mean, sample_sd=sd, se=se,
                            ci_low=mean-1.96*se, ci_high=mean+1.96*se))

    summary = json.loads((SOURCE / "nonaffine_summary.json").read_text())
    original = next(r["weak_payoff_difference"] for r in summary["convergence"]
                    if r["n_steps"] == COARSE and r["reference_steps"] == REFERENCE)
    np.testing.assert_allclose(
        [records[-1]["mean"], records[-1]["se"]],
        [original["mean"], original["standard_error"]], rtol=1e-11, atol=1e-14)

    for rec in records:
        rec["se_ratio_to_10000"] = rec["se"] / records[0]["se"]
        rec["constant_variance_ratio"] = math.sqrt(SIZES[0]/rec["paths"])
    result = dict(source="../../results/nonaffine_terminals.npz",
                  sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  coarse_steps=COARSE, reference_steps=REFERENCE, strike=STRIKE,
                  selection="First M paired rows in saved order; nested subsets",
                  independent_comparisons=False, new_paths_generated=0,
                  full_sample_crosscheck="PASS", records=records,
                  interpretation="SE is for signed paired payoff difference. "
                  "Intervals quantify sampling uncertainty, not reference-solution error. "
                  "Nested means are not independent repetitions or known true biases.")
    (OUT / "sample_size_study.json").write_text(json.dumps(result, indent=2)+"\n")
    with (OUT / "sample_size_study.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    rows = [[f'{r["paths"]:,}', f'{r["mean"]:.6f}', f'{r["se"]:.6f}',
             f'[{r["ci_low"]:.6f}, {r["ci_high"]:.6f}]'] for r in records]
    for suffix, caption, headers in [
        ("", "One fixed grid pair: $N=64$ versus $N_{\\rm ref}=8192$. "
         "Nested prefixes of the saved paired sample.",
         ["Paths $M$", "Signed payoff difference", "Standard error", "95\\% interval"]),
        ("_中文", "固定网格 $N=64$ 与参考 $N_{\\rm ref}=8192$；使用保存样本的嵌套前缀。",
         ["路径数 $M$", "带符号收益差", "标准误差", "95\\% 区间"]),
    ]:
        write_table(f"sample_size_table{suffix}.tex", caption, "tab:sample-size",
                    headers, rows, "rrrr")

    rates = []
    for ref in (2048, 4096, 8192):
        fit = summary["rate_fits"][str(ref)]["strong_coarse"]
        assert fit["steps"] == [8, 16, 32, 64]
        rates.append([str(ref), f'{fit["slope"]:.6f}'])
    for suffix, caption, headers in [
        ("", "Same fitting window $N=8,16,32,64$, different numerical references.",
         ["Reference steps", "Empirical strong slope"]),
        ("_中文", "固定拟合窗口 $N=8,16,32,64$，仅改变数值参考。",
         ["参考步数", "经验强斜率"]),
    ]:
        write_table(f"reference_slopes_table{suffix}.tex", caption, "tab:reference-slopes",
                    headers, rates, "rr")

    with (SOURCE / "gbm_convergence.csv").open(encoding="utf-8-sig") as f:
        gbm = list(csv.DictReader(f))
    rows = [[r["method"], f'{float(r["weak_paired_se"]):.3e}',
             f'{float(r["weak_cv_se"]):.3e}'] for r in gbm if int(r["N"]) == 1024]
    for suffix, caption, headers in [
        ("", "GBM at $N=1024$: standard errors of the paired mean-bias estimates.",
         ["Method", "Before controls", "After controls"]),
        ("_中文", "GBM 在 $N=1024$ 时，配对均值偏差估计的标准误差。",
         ["方法", "控制变量处理前", "控制变量处理后"]),
    ]:
        write_table(f"control_se_table{suffix}.tex", caption, "tab:control-se",
                    headers, rows, "lrr")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
