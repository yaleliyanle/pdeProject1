# Numerical Simulation of Financial SDEs

Problem 4 — Team 6

Yifan Chen (2362353), Zeya Hu (2362375), Yanle Li (2363600), Qingwen Ma (2361052), and Chenyi Xu (2359968).

## Project scope

This submission studies geometric Brownian motion (GBM) and the prescribed non-affine stochastic-volatility model. GBM provides an exact pathwise benchmark for price-based Euler–Maruyama (EM) and scalar Milstein. The second model is integrated with simultaneous log-price EM and assessed against three coupled numerical references. The experiments address strong and weak convergence, sampling uncertainty, terminal distributions, positivity diagnostics, independent-seed variability, and cost at a common accuracy threshold.

The work follows the SDE-specific criteria for Direction 4 in the supplied problem pack. The report includes the Team AI Transparency Log and one Individual Contribution Statement per member.

## Archive contents

| Path | Purpose |
| --- | --- |
| `code/gbm.py` | Exact GBM simulation, price EM/Milstein, and independent-pilot control variates |
| `code/nonaffine.py` | Correlated drivers, simultaneous log-EM, nested grids, and state diagnostics |
| `code/verify.py` | Separate recurrence and quadrature checks; saved-array/statistic consistency |
| `code/build_report_data.py` | Report tables, numerical macros, and production convergence plots |
| `code/submission_experiments.py` | Independent-seed repetitions and matched-threshold kernel-cost study |
| `code/run_all.py` | Complete numerical reproduction and isolated reduced smoke mode |
| `code/prepare_submission.py` | Artifact preflight, PDF/ZIP packaging, and checksum manifest |
| `tests/` | Seven deterministic and statistical unit tests |
| `results/` | JSON/CSV results, terminal samples in NPZ, verification evidence, and LaTeX tables |
| `figures/` | PDF and PNG versions of the experimental figures |
| `report/` | Report source, AI Transparency Log, and individual statements |
| `source/problem_pack.pdf` | Supplied assignment |
| `numerical_summary.txt` | Summary of the recorded production experiments |

The compiled report is supplied separately as `Financial_SDE_Report.pdf`. The code archive contains no virtual environment, cache, Git database, presentation files, original empty forms, or internal preparation notes.

## Dependencies and execution environment

Python 3.9 or later is required. Dependencies are specified in `requirements.txt`: NumPy, Matplotlib, and Numba. No external market data or network access is required after installation.

Cross-platform verification used macOS arm64, Python 3.9.6, NumPy 2.0.2, Matplotlib 3.9.4, and Numba 0.60.0. The original production runs retain their recorded environment metadata in `results/gbm_summary.json` and `results/nonaffine_summary.json`. Compatible dependency ranges allow installation for the host interpreter; small floating-point differences and machine-dependent timings are expected.

## Verification workflow

Commands below are relative to the extracted archive's top-level directory:

```sh
python -m venv .venv
# Activate the environment on macOS/Linux:
source .venv/bin/activate
# Windows PowerShell alternative:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python code/verify.py --no-write
python code/run_all.py --smoke
```

The tests cover GBM recurrences and moments, the non-affine old-state update and constant-volatility reduction, invalid nested grids, Brownian correlation and aggregation, increment variance, exact control centering, and the baseline Milstein multiplier. The saved-data checker recomputes terminal strong and signed weak statistics from the supplied arrays.

All seven tests and saved-array checks passed in the verification environment. A complete production rerun reproduced the displayed scientific results. The smoke mode exercises the pipeline with smaller samples and writes to an isolated temporary directory; its estimates are not the report's production evidence.

## Production reproduction

```sh
python code/run_all.py
```

This command regenerates the production simulations, supplementary experiments, numerical summaries, tables, and figures. Outputs are written to `results/`, `figures/`, and `numerical_summary.txt`. A separate output root is supported:

```sh
python code/run_all.py --output-dir reproduced_output
```

`FINANCIAL_SDE_OUTPUT_DIR` provides the equivalent environment setting. The full non-affine experiment comprises approximately 1.484 billion path updates; batching limits memory use. Runtime depends on the hardware and compilation overhead.

Report typesetting is separate from numerical execution. The supplied source can be compiled from `report/` with `tectonic report.tex` or two runs of `pdflatex report.tex`. LaTeX is not required for the Python experiments.

## Regeneration from saved results

```sh
python code/build_report_data.py
python code/submission_experiments.py --figures-only
```

These commands rebuild the tables, numerical macros, production convergence plots, and supplementary plots from saved JSON/CSV evidence without resimulating paths or remeasuring cost. The GBM distribution figure is generated by `gbm.py` during the complete workflow.

| Report figure stem | Generator and evidence |
| --- | --- |
| `report_gbm_strong` | `build_report_data.py`; GBM convergence CSV and summary |
| `report_gbm_weak` | `build_report_data.py`; raw/controlled estimates and analytic discrete-mean bias |
| `gbm_distribution` | `gbm.py`; simulated terminal prices, exact lognormal density, and quantiles |
| `report_nonaffine_strong` | `build_report_data.py`; coupled coarse/reference comparisons |
| `report_nonaffine_weak` | `build_report_data.py`; signed paired payoff differences and intervals |
| `submission_gbm_repeat_slopes` | `submission_experiments.py`; independent GBM seed repetitions |
| `submission_nonaffine_repeat_slopes` | `submission_experiments.py`; independent non-affine seed repetitions |
| `submission_cost_accuracy` | `submission_experiments.py`; paired exact oracle and measured kernel costs |

## Parameters and numerical protocol

GBM parameters are `S0=100, mu=0.05, sigma=0.30, T=1`. Production uses 160,000 paths, an independent 20,000-path pilot, batch size 2,000, production seed 2026090804, and pilot seed 2026090805. The grids are `N=8,16,32,64,128,256,512,1024`; strong and controlled weak fits use `N=64,128,256,512,1024`.

The prescribed non-affine parameters are `S0=100, Y0=0, mu=0.05, kappa=2, theta=-0.2, xi=0.6, rho=-0.7, sigma_min=0.10, sigma_max=0.50, T=1`. The call strike is 100. Production uses 100,000 paths, batch size 512, and seed 2026090804. Coarse grids are `N=8,16,32,64,128,256`; references are `N=2048,4096,8192`. The principal strong fit uses `N=8,16,32,64`.

Within each experiment, coarse increments are sums of the same finest-grid increments, and each method reruns its states on its own grid. Both non-affine log-EM coefficients use the old volatility factor. The two models are separate experiments; a common seed does not imply cross-model path coupling. Seeds, path counts, grid sizes, batch sizes, and software versions determine the recorded realizations.

Supplementary studies comprise eight GBM repetitions with 5,000 production paths and independent 1,000-path pilots, and eight non-affine repetitions with 1,000 paths and reference 8192. The cost study uses 10,000 shared paths, finest grid 3072, seven warmed timings per grid, and a terminal L1 threshold of 0.25 currency units. The additional grid `N=6` divides 3072 exactly. Individual seeds, fitted slopes, and timings are recorded in `results/submission_experiments.json`.

Time is measured in years; prices, payoffs, and errors use currency units; the latent factor `Y` is dimensionless.

## Interpretation and limitations

GBM terminal strong slopes are approximately 0.500 for EM and 0.991 for Milstein. Both schemes have the same first-order terminal-mean bias because their expected update multipliers coincide. Raw and controlled Monte Carlo estimates remain separate from the analytic bias, which serves as a verification target.

Strong error is terminal L1 error rather than a path-supremum norm. Non-affine comparisons measure differences from finite numerical references, with an empirical strong slope of approximately 0.491 on the stated window. The 10% reference-sensitivity criterion is a practical diagnostic, not a bound on residual exact-solution error. Sampling intervals and across-seed variability exclude reference and fit-window bias. No fine-grid weak order is claimed where signed payoff intervals include zero.

The call quantity is an undiscounted payoff expectation under the specified drift, not a risk-neutral option price. The non-affine log-EM mean is preserved in expectation for any step size, so first-moment agreement alone is not a weak-order test. GBM negative-price counts describe terminal values, not every intermediate state.

The cost statistic is median wall-clock latency of the NumPy price-update kernel, including its temporary allocations. It excludes random-number generation, Brownian aggregation, input preparation, reference evaluation, imports, warm-up, statistical summaries, plotting, and file I/O. The selected methods meet the same tolerance but have different achieved errors; the study is not an end-to-end or cross-machine speedup claim.

## Repository workflow and transparency

One team member committed and pushed the code on behalf of the group. Repository submissions therefore do not by themselves describe the distribution of individual work. Contributions are recorded in the five Individual Contribution Statements, and AI assistance and the verification of significant AI-assisted claims are documented in the report's Team AI Transparency Log.

## References

- Supplied problem pack, introductory SDE criteria and Direction 4, pp. 6–7.
- D. J. Higham (2001), *An algorithmic introduction to numerical simulation of stochastic differential equations*, [DOI: 10.1137/S0036144500378302](https://doi.org/10.1137/S0036144500378302).
- P. E. Kloeden and E. Platen (1992), *Numerical Solution of Stochastic Differential Equations*, [DOI: 10.1007/978-3-662-12616-5](https://doi.org/10.1007/978-3-662-12616-5).
