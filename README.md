# Numerical Simulation of Financial SDEs

Problem 4 — Team 6

Yifan Chen (2362353), Zeya Hu (2362375), Yanle Li (2363600), Qingwen Ma (2361052), and Chenyi Xu (2359968).

This project compares exact simulation, price-based Euler–Maruyama (EM), and scalar Milstein for geometric Brownian motion (GBM). It then studies the prescribed non-affine stochastic-volatility model using correlated Brownian drivers, simultaneous log-price EM, and nested numerical references. The report evaluates terminal strong error, weak observables, Monte Carlo uncertainty, distributional diagnostics, reference sensitivity, and computational cost.

## Assessment materials

| Material | Location |
| --- | --- |
| Report, AI Transparency Log, and five Individual Contribution Statements | [Financial_SDE_Report.pdf](submission/upload/Financial_SDE_Report.pdf) |
| Portable code archive with README, tests, results, and figures | [Financial_SDE_Code.zip](submission/upload/Financial_SDE_Code.zip) |
| Dependencies, reproduction commands, and figure-to-source mapping | [Submission README](submission/README.md) |
| Executable implementation and tests | `submission/code/` and `submission/tests/` |
| Full-precision numerical evidence and terminal samples | `submission/results/` |
| Report source and figures | `submission/report/` and `submission/figures/` |
| Artifact sizes and SHA-256 checksums | `submission/upload/manifest.json` |
| Self-contained report source for Overleaf | `Overleaf_FinancialSDE_Team6/` |

The report has 27 pages, including the transparency and individual-contribution appendices. The assessed implementation is in `submission/`; other repository directories retain the earlier numerical baseline and supporting coursework materials.

## Validation and reproduction

The following commands are executed from `submission/`:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python code/verify.py --no-write
python code/run_all.py --smoke
```

The seven unit tests and saved-array checks verify update formulas, Brownian coupling, increment scaling, discrete moments, control centering, and numerical statistics. The reduced smoke run checks execution and figure generation, not scientific convergence rates.

The production workflow is `python code/run_all.py`. The [submission README](submission/README.md) records path counts, seeds, grid sizes, fit windows, dependencies, output locations, and the scope of the timing measurements.

## Main findings and interpretation

GBM terminal strong slopes are approximately 0.500 for EM and 0.991 for Milstein. Their terminal-mean biases are nevertheless identical because both methods have the same expected one-step multiplier. For the non-affine model, the empirical strong slope is approximately 0.491 on the specified coarse-grid window. Fine-grid payoff differences are unresolved by their sampling intervals, so no weak order is assigned to those estimates.

Strong error is terminal L1 error, not a path-supremum norm. Non-affine comparisons use finite numerical references rather than an exact transition oracle. The call observable is an undiscounted expected payoff under the specified drift, not a risk-neutral option price. The cost study uses a common accuracy threshold and reports update-kernel latency rather than end-to-end runtime.

## Repository submissions and individual contributions

The team used a centralized Git submission workflow, with one member responsible for committing and pushing the code on behalf of the group. The Git history therefore records repository submissions rather than the full distribution of individual work. Contributions to mathematical analysis, code review, interpretation of results, figures, and the report are documented in the Individual Contribution Statements. AI assistance and the checks of significant AI-assisted claims are disclosed in the report's Team AI Transparency Log.

