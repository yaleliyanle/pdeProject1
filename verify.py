"""Deterministic checks of the imported algorithms and saved-run consistency."""
from pathlib import Path
import csv
import json
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / ".deps"))
import numpy as np
import gbm
import nonaffine as na

ROOT = Path(__file__).resolve().parent

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

def check_saved_outputs():
    results = ROOT/"results"
    g = json.loads((results/"gbm_summary.json").read_text(encoding="utf-8"))
    a = np.load(results/"gbm_terminal_samples.npz")
    with (results/"gbm_convergence.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for method,key in [("EM","em_fine"),("Milstein","milstein_fine")]:
        row = next(r for r in rows if r["method"]==method and int(r["N"])==1024)
        np.testing.assert_allclose(np.mean(abs(a[key]-a["exact"])),
                                   float(row["strong_l1"]),rtol=1e-12)
    n = json.loads((results/"nonaffine_summary.json").read_text(encoding="utf-8"))
    b = np.load(results/"nonaffine_terminals.npz")
    ref = n["simulation"]["finest_steps"]
    for row in n["convergence"]:
        if row["reference_steps"] != ref:
            continue
        coarse = b[f"S_{row['n_steps']}"]
        fine = b[f"S_{ref}"]
        strong = np.mean(abs(coarse-fine))
        weak = np.mean(np.maximum(coarse-100,0)-np.maximum(fine-100,0))
        np.testing.assert_allclose(strong,row["strong_l1"]["mean"],rtol=1e-12)
        np.testing.assert_allclose(weak,row["weak_payoff_difference"]["mean"],
                                   rtol=1e-11,atol=1e-14)
    assert n["diagnostics"]["total_path_updates"] == n["simulation"]["expected_total_path_updates"]
    return {"gbm_paths":g["paths"],"nonaffine_paths":n["simulation"]["n_paths"],
            "nonaffine_finest_steps":ref}

if __name__ == "__main__":
    check_gbm()
    print("PASS GBM coupled increments, exact solution, EM/Milstein recurrences and moments")
    check_nonaffine()
    print("PASS non-affine old-state update, constant-volatility reduction and sample statistics")
    evidence = check_saved_outputs()
    print("PASS saved terminal arrays reproduce strong and signed weak statistics")
    log = {"status":"PASS","deterministic_checks":True,"saved_results_consistent":True,
           "evidence":evidence}
    (ROOT/"results"/"verification.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
    print(json.dumps(log,indent=2))

