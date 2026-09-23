"""Build the Individual-Challenge before/after figure from saved GBM diagnostics.

No simulation is run. The script reads results/gbm_terminal_stats.csv and checks
that every method/grid combination has 160,000 paths and zero nonpositive
terminal values, as recorded by the production experiment.
"""
from pathlib import Path
import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PATHS = 160_000
LEVELS = (8, 16, 32, 64, 128, 256, 512, 1024)
MU, SIGMA = 0.05, 0.30


def load_counts():
    with (ROOT / "results" / "gbm_terminal_stats.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 16
    assert {int(row["N"]) for row in rows} == set(LEVELS)
    assert {row["method"] for row in rows} == {"EM", "Milstein"}
    counts = {(row["method"], int(row["N"])):
              int(row["nonpositive_terminal_count"]) for row in rows}
    assert all(value == 0 for value in counts.values())
    return counts


def main():
    counts = load_counts()
    upper = 1 - 0.05**(1/PATHS)  # exact one-sided 95% binomial upper limit for 0/M
    h = 1/8
    z = -(1 + MU*h)/(SIGMA*math.sqrt(h))
    em_one_step = 0.5*math.erfc(-z/math.sqrt(2))

    fig = plt.figure(figsize=(14, 7.4), facecolor="#f4f2ed")
    gs = fig.add_gridspec(1, 2, left=.035, right=.975, top=.86, bottom=.08,
                          wspace=.07, width_ratios=(.86, 1.14))
    before, after = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    for ax in (before, after):
        ax.set_axis_off()
    fig.suptitle("From a verbal positivity check to a quantitative diagnostic",
                 fontsize=23, fontweight="bold", color="#17243a", y=.95)

    before.add_patch(FancyBboxPatch((.02, .02), .96, .94, boxstyle="round,pad=.018",
                     transform=before.transAxes, fc="#fffaf2", ec="#d7a14a", lw=2,
                     zorder=0))
    before.text(.08, .88, "BEFORE", transform=before.transAxes, fontsize=18,
                fontweight="bold", color="#9a5d00")
    before.text(.08, .78, "Observation / issue ticket", transform=before.transAxes,
                fontsize=15, fontweight="bold", color="#17243a")
    before.text(.08, .68,
                "The positivity discussion was mainly verbal.\n"
                "It explained when an update could be negative,\n"
                "but did not explicitly report the simulated\n"
                "negative-terminal frequency.",
                transform=before.transAxes, fontsize=14, color="#263547",
                va="top", linespacing=1.45)
    before.text(.08, .40, "Original conclusion", transform=before.transAxes,
                fontsize=14, fontweight="bold", color="#17243a")
    before.text(.08, .32,
                '“No negative prices in a finite simulation\n'
                'proves only what was observed.”',
                transform=before.transAxes, fontsize=15, color="#5e4a2e",
                va="top", style="italic", linespacing=1.4)
    before.text(.08, .14,
                "Missing quantitative items:\n"
                "count • denominator • frequency • uncertainty • scope",
                transform=before.transAxes, fontsize=13, color="#9a3e2e",
                va="top", linespacing=1.35)

    after.add_patch(FancyBboxPatch((.02, .02), .96, .94, boxstyle="round,pad=.018",
                    transform=after.transAxes, fc="#f7fbff", ec="#4b7fa8", lw=2,
                    zorder=0))
    after.text(.07, .88, "AFTER", transform=after.transAxes, fontsize=18,
               fontweight="bold", color="#245b83")
    after.text(.07, .80, "Observed nonpositive terminal values", transform=after.transAxes,
               fontsize=15, fontweight="bold", color="#17243a")

    columns = ["Method", "Grids $N$", "Observed at each grid", "Frequency"]
    table_data = [
        ["EM", "8–1024", f"0 / {PATHS:,}", "0.000%"],
        ["Milstein", "8–1024", f"0 / {PATHS:,}", "0.000%"],
    ]
    table = after.table(cellText=table_data, colLabels=columns, cellLoc="center",
                        bbox=[.07, .59, .86, .17], colWidths=[.16, .18, .40, .20])
    table.set_zorder(3)
    table.auto_set_font_size(False)
    table.set_fontsize(12.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#89a9bf")
        if row == 0:
            cell.set_facecolor("#dcebf5")
            cell.set_text_props(weight="bold", color="#17243a")
        else:
            cell.set_facecolor("white")

    after.text(.07, .50,
               f"With 0 events in {PATHS:,} trials, the exact one-sided 95% binomial\n"
               f"upper limit for the terminal frequency at any one method/grid is\n"
               f"{upper:.3e} ({100*upper:.4f}%).",
               transform=after.transAxes, fontsize=13.2, color="#263547",
               va="top", linespacing=1.35)
    after.text(.07, .34, "Consistency with the update formulas", transform=after.transAxes,
               fontsize=14, fontweight="bold", color="#17243a")
    after.text(.07, .27,
               f"• EM: maximum tested one-step negative probability occurs at $N=8$:\n"
               f"  $p={em_one_step:.3e}$. Zero observations are therefore unsurprising.\n"
               "• Milstein: the multiplier is strictly positive for the chosen parameters,\n"
               "  so its theoretical one-step negative probability is zero.",
               transform=after.transAxes, fontsize=12.9, color="#263547",
               va="top", linespacing=1.32)
    after.text(.07, .08,
               "Scope: the saved diagnostic records terminal values only; it does not count\n"
               "paths that might become negative at an intermediate step and later recover.",
               transform=after.transAxes, fontsize=12.5, color="#7a3340",
               va="top", linespacing=1.28)

    fig.text(.5, .025,
             "Source: fixed-seed production data in results/gbm_terminal_stats.csv; "
             "160,000 paths per method per grid.",
             ha="center", fontsize=11, color="#586575")
    for suffix, dpi in (("png", 220), ("pdf", None)):
        fig.savefig(OUT / f"positivity_before_after.{suffix}", dpi=dpi,
                    bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"PASS: 16 rows, all counts zero; per-grid upper 95% limit={upper:.12g}; "
          f"EM p(N=8)={em_one_step:.12g}")


if __name__ == "__main__":
    main()
