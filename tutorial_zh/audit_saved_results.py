"""Independently audit saved coursework statistics with NumPy only.

Run from any directory. This script reads the supplied CSV/JSON/NPZ files and
writes only tutorial_zh/validation_saved.json. It does not import, rerun, or
change gbm.py, nonaffine.py, verify.py, or the supplied results.
"""
from pathlib import Path
import csv
import json
import math

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def read_csv(name):
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def statistics(values):
    return float(np.mean(values)), float(np.std(values, ddof=1) / np.sqrt(len(values)))


def main():
    checks = []
    largest = {}

    def close(name, actual, expected, rtol=2e-10, atol=2e-12):
        actual = np.asarray(actual, dtype=float)
        expected = np.asarray(expected, dtype=float)
        np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol,
                                   err_msg=name)
        largest[name] = max(largest.get(name, 0.0),
                            float(np.max(np.abs(actual - expected))))

    gbm = json.loads((RESULTS / "gbm_summary.json").read_text())
    with np.load(RESULTS / "gbm_terminal_samples.npz") as data:
        exact = data["exact"]
        assert len(exact) == gbm["paths"]
        mean, se = statistics(exact)
        record = gbm["exact_terminal_moments"]
        close("GBM_exact_sample_mean_and_SE", (mean, se),
              (record["empirical_mean"], record["empirical_mean_se"]))
        close("GBM_exact_sample_variance", np.var(exact, ddof=1),
              record["empirical_variance"])
        for row in read_csv("gbm_convergence.csv"):
            n = int(row["N"])
            if n not in (8, 1024):
                continue
            method = "em" if row["method"] == "EM" else "milstein"
            sample = data[f"{method}_{'coarse' if n == 8 else 'fine'}"]
            difference = sample - exact
            for values, field, se_field in (
                    (np.abs(difference), "strong_l1", "strong_se"),
                    (difference, "weak_bias_paired", "weak_paired_se")):
                close("GBM_saved_endpoint_statistics", statistics(values),
                      (float(row[field]), float(row[se_field])))
        for row in read_csv("gbm_quantiles.csv"):
            probability = float(row["probability"])
            for name, key in (("exact", "exact"), ("em", "em_coarse"),
                              ("milstein", "milstein_coarse")):
                close("GBM_saved_quantiles", np.quantile(data[key], probability),
                      float(row[f"{name}_empirical_quantile_h_1_8"]))
        for key in data.files:
            assert np.isfinite(data[key]).all(), key
            assert (data[key] > 0).all(), key
    checks.append("GBM saved coarse/fine strong and raw weak means/SEs, exact sample moments, quantiles, and terminal positivity")

    parameters = gbm["parameters"]
    s0, mu, sigma, terminal = (parameters[k] for k in ("S0", "mu", "sigma", "T"))
    exact_mean = s0 * math.exp(mu * terminal)
    close("GBM_analytic_continuous_moments",
          (exact_mean, s0*s0 * math.exp(2*mu*terminal) * math.expm1(sigma*sigma*terminal)),
          (gbm["exact_terminal_moments"]["analytic_mean"],
           gbm["exact_terminal_moments"]["analytic_variance"]))
    nodes, weights = np.polynomial.hermite.hermgauss(5)
    for row in read_csv("gbm_terminal_stats.csv"):
        n = int(row["N"])
        h = terminal / n
        dw = math.sqrt(2*h) * nodes
        factor = 1 + mu*h + sigma*dw
        if row["method"] == "Milstein":
            factor += 0.5*sigma*sigma*(dw*dw-h)
        first = float(np.dot(weights, factor) / math.sqrt(math.pi))
        second = float(np.dot(weights, factor*factor) / math.sqrt(math.pi))
        close("GBM_discrete_moments_by_Gaussian_quadrature",
              (s0*first**n, s0*s0*(second**n - first**(2*n))),
              (float(row["analytic_discrete_mean"]),
               float(row["analytic_discrete_variance"])), rtol=1e-9)
        assert int(row["nonpositive_terminal_count"]) == 0
    checks.append("GBM analytic continuous moments and all discrete first/second moments via independent Gaussian quadrature")

    na = json.loads((RESULTS / "nonaffine_summary.json").read_text())
    strike = na["parameters"]["strike"]
    count = na["simulation"]["n_paths"]
    with np.load(RESULTS / "nonaffine_terminals.npz") as data:
        def check_record(values, record, name):
            mean, se = statistics(values)
            close(name, (mean, se, mean-1.96*se, mean+1.96*se),
                  (record["mean"], record["standard_error"],
                   record["ci95_low"], record["ci95_high"]))
            assert len(values) == record["n"] == count

        def compare(first, second, record):
            a, b = data[f"S_{first}"], data[f"S_{second}"]
            check_record(np.abs(a-b), record["strong_l1"], "NA_strong_statistics")
            check_record(np.maximum(a-strike, 0)-np.maximum(b-strike, 0),
                         record["weak_payoff_difference"], "NA_weak_statistics")

        for row in na["convergence"]:
            compare(row["n_steps"], row["reference_steps"], row)
        for row in na["reference_checks"]:
            compare(row["coarser_steps"], row["finer_steps"], row)
        for n, record in na["terminal_asset_mean"].items():
            sample = data[f"S_{n}"]
            assert np.isfinite(sample).all() and (sample > 0).all()
            check_record(sample, record, "NA_terminal_asset_statistics")
            check_record(np.maximum(sample-strike, 0), na["terminal_payoff_mean"][n],
                         "NA_terminal_payoff_statistics")
    checks.append("All 18 non-affine coarse/reference pairs and both reference refinements: strong and signed weak means, SEs, 95% intervals")
    checks.append("All nine non-affine terminal asset/payoff means, SEs, 95% intervals, and saved terminal positivity")

    for reference, fits in na["rate_fits"].items():
        for field in ("strong_coarse", "strong_all"):
            fit = fits[field]
            rows = [r for r in na["convergence"]
                    if r["reference_steps"] == int(reference)
                    and r["n_steps"] in fit["steps"]]
            slope = np.polyfit(np.log([r["h"] for r in rows]),
                               np.log([r["strong_l1"]["mean"] for r in rows]), 1)[0]
            close("NA_descriptive_slope", slope, fit["slope"])
    expected_updates = count * sum(na["simulation"]["coarse_steps"] +
                                   na["simulation"]["reference_steps"])
    assert expected_updates == na["diagnostics"]["total_path_updates"] == 1484000000
    checks.append("All six non-affine strong descriptive slopes and total path update accounting")

    result = {
        "status": "PASS",
        "audit": "Independent NumPy recomputation from supplied saved endpoints and tables; original simulation modules are not imported",
        "gbm_production_paths": gbm["paths"],
        "nonaffine_production_paths": count,
        "checks": checks,
        "largest_absolute_differences": largest,
        "limitations": [
            "GBM controlled weak estimates cannot be recomputed from endpoint-only NPZ files; Brownian controls and production increments are not saved.",
            "GBM nonpositive counts cover terminal values only. Positive terminal values do not rule out earlier negative steps.",
            "Saved non-affine Brownian and intermediate-state diagnostics cannot be independently recomputed from terminal-only NPZ files.",
            "These checks audit saved statistical consistency, not a fresh stochastic run or exact-solution error for the non-affine model.",
        ],
    }
    destination = Path(__file__).resolve().parent / "validation_saved.json"
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
