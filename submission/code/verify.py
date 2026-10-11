"""Deterministic checks of the imported algorithms and saved-run consistency."""
from pathlib import Path
import argparse
import csv
import json
import math
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / ".deps"))
import numpy as np
import gbm
import nonaffine as na

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == "code" else SCRIPT_DIR
ROOT = Path(os.environ.get("FINANCIAL_SDE_OUTPUT_DIR", PROJECT_DIR)).resolve()

def check_gbm():
    fine = .003 * np.sin(np.arange(3*1024).reshape(3, 1024)/13)
    class FixedRng:
        def normal(self, loc, scale, shape):
            assert shape == fine.shape
            return fine.copy()
    for n, exact, endpoints, controls in gbm.simulate_batch(FixedRng(), 3):
        h = 1/n
        np.testing.assert_allclose(exact,100*np.exp(.005+.3*fine.sum(1)),rtol=1e-14)
        reference = np.full((3,2),100.)
        for k in range(n):
            d = fine[:,k*(1024//n):(k+1)*(1024//n)].sum(1)
            reference[:,0] += .05*reference[:,0]*h + .3*reference[:,0]*d
            reference[:,1] += (.05*reference[:,1]*h+.3*reference[:,1]*d
                                +.045*reference[:,1]*(d*d-h))
        np.testing.assert_allclose(endpoints, reference, rtol=5e-14)
        assert controls.shape == (3,5)
    # Gaussian quadrature independently validates both analytic discrete moments.
    nodes, weights = np.polynomial.hermite.hermgauss(5)
    for n in [1,8,1024]:
        h = 1/n
        d = np.sqrt(2*h)*nodes
        for name in gbm.METHODS:
            factor = 1+.05*h+.3*d
            if name == "Milstein":
                factor += .045*(d*d-h)
            m1 = np.dot(weights,factor)/np.sqrt(np.pi)
            m2 = np.dot(weights,factor*factor)/np.sqrt(np.pi)
            expected = (100*m1**n,10000*(m2**n-m1**(2*n)))
            np.testing.assert_allclose(gbm.analytic_discrete_moments(n,name),
                                       expected,rtol=1e-10)

def check_nonaffine():
    dw = .04*np.cos(np.arange(8*3*2).reshape(8,3,2)/7)
    p = na.PARAMETERS.copy()
    got, diag = na.em_terminal(dw,4,p)
    expected = []
    for path in range(3):
        x,y = math.log(100),0.
        for k in range(4):
            d = dw[2*k:2*k+2,path].sum(0)
            g = .1+.4/(1+math.exp(-y))
            xn = x+(.05-.5*g*g)*.25+g*d[0]
            yn = y+2*(-.2-y)*.25+.6*math.sqrt(1+y*y)*d[1]
            x,y = xn,yn
        expected.append(math.exp(x))
    np.testing.assert_allclose(got,expected,rtol=1e-13)
    assert diag["updates"] == 12
    # When volatility is constant, log EM agrees with exact GBM at every grid.
    p["g_min"] = p["g_max"] = .3
    target = 100*np.exp(.005+.3*dw[:,:,0].sum(0))
    for n in [1,2,4,8]:
        got,_ = na.em_terminal(dw,n,p)
        np.testing.assert_allclose(got,target,rtol=1e-13)
    m = na.Moments()
    m.add(np.array([-2.,1.,3.,6.]))
    result = m.summary()
    assert result["mean"] == 2.
    np.testing.assert_allclose(result["standard_error"],
                              np.std([-2,1,3,6],ddof=1)/2)

def check_saved_outputs(output_dir=None):
    results = (ROOT if output_dir is None else Path(output_dir).resolve())/"results"
    g = json.loads((results/"gbm_summary.json").read_text(encoding="utf-8"))
    a = np.load(results/"gbm_terminal_samples.npz")
    with (results/"gbm_convergence.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for method,stem in [("EM","em"),("Milstein","milstein")]:
        for n,suffix in [(8,"coarse"),(1024,"fine")]:
            row = next(r for r in rows if r["method"]==method and int(r["N"])==n)
            difference = a[f"{stem}_{suffix}"]-a["exact"]
            np.testing.assert_allclose(np.mean(abs(difference)),
                                       float(row["strong_l1"]),rtol=1e-12)
            np.testing.assert_allclose(np.mean(difference),
                                       float(row["weak_bias_paired"]),rtol=1e-9,atol=1e-13)
            np.testing.assert_allclose(np.std(difference,ddof=1)/math.sqrt(len(difference)),
                                       float(row["weak_paired_se"]),rtol=1e-12)
        selected = [r for r in rows if r["method"]==method][-5:]
        fitted = np.polyfit(np.log([float(r["h"]) for r in selected]),
                           np.log([float(r["strong_l1"]) for r in selected]),1)[0]
        np.testing.assert_allclose(fitted,g["slopes"][method]["strong_l1_finest_5"],rtol=1e-12)
    for row in rows:
        exact_mean,_ = gbm.exact_moments()
        n_steps = int(row["N"])
        h = gbm.T/n_steps
        analytic_bias = exact_mean*math.expm1(n_steps*math.log1p(gbm.MU*h)-gbm.MU*gbm.T)
        # log1p/expm1 rounding can differ across the recorded Windows/macOS runs.
        np.testing.assert_allclose(analytic_bias,float(row["analytic_mean_bias"]),rtol=1e-12,atol=1e-14)
    n = json.loads((results/"nonaffine_summary.json").read_text(encoding="utf-8"))
    b = np.load(results/"nonaffine_terminals.npz")
    ref = n["simulation"]["finest_steps"]
    for row in n["convergence"]:
        coarse = b[f"S_{row['n_steps']}"]
        fine = b[f"S_{row['reference_steps']}"]
        strong_values = abs(coarse-fine)
        weak_values = np.maximum(coarse-100,0)-np.maximum(fine-100,0)
        strong = np.mean(strong_values)
        weak = np.mean(weak_values)
        np.testing.assert_allclose(strong,row["strong_l1"]["mean"],rtol=1e-12)
        np.testing.assert_allclose(weak,row["weak_payoff_difference"]["mean"],
                                   rtol=1e-11,atol=1e-14)
        for values,key in [(strong_values,"strong_l1"),(weak_values,"weak_payoff_difference")]:
            se = float(np.std(values,ddof=1)/math.sqrt(len(values)))
            stats = row[key]
            np.testing.assert_allclose(se,stats["standard_error"],rtol=1e-11)
            np.testing.assert_allclose(stats["mean"]+np.array([-1.96,1.96])*se,
                                       [stats["ci95_low"],stats["ci95_high"]],rtol=1e-10,atol=1e-14)
    for row in n["reference_checks"]:
        coarse,fine = b[f"S_{row['coarser_steps']}"],b[f"S_{row['finer_steps']}"]
        np.testing.assert_allclose(np.mean(abs(coarse-fine)),row["strong_l1"]["mean"],rtol=1e-12)
        np.testing.assert_allclose(np.mean(np.maximum(coarse-100,0)-np.maximum(fine-100,0)),
                                   row["weak_payoff_difference"]["mean"],rtol=1e-10,atol=1e-14)
    assert n["diagnostics"]["total_path_updates"] == n["simulation"]["expected_total_path_updates"]
    return {"gbm_paths":g["paths"],"nonaffine_paths":n["simulation"]["n_paths"],
            "nonaffine_finest_steps":ref}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=ROOT,
                        help="Artifact root containing results/")
    parser.add_argument("--no-write",action="store_true",
                        help="Check supplied evidence without modifying verification.json")
    args = parser.parse_args()
    check_gbm()
    print("PASS GBM coupled increments, exact solution, EM/Milstein recurrences and moments")
    check_nonaffine()
    print("PASS non-affine old-state update, constant-volatility reduction and sample statistics")
    evidence = check_saved_outputs(args.output_dir)
    print("PASS saved terminal arrays reproduce strong and signed weak statistics")
    log = {"status":"PASS","deterministic_checks":True,"saved_results_consistent":True,
           "evidence":evidence}
    if not args.no_write:
        (args.output_dir/"results"/"verification.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
    print(json.dumps(log,indent=2))


if __name__ == "__main__":
    main()

