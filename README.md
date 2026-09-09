# Problem 4 Financial SDE Coursework

This package follows the supplied 12-page coursework example: an English PDF report, editable LaTeX source, executable code, numerical results, and figures.

## Start here

- Problem4_FinancialSDE_Coursework.pdf — compiled 12-page report.
- Problem4_FinancialSDE_Coursework.tex — editable report source.
- run_all.py — reproduce both experiments, validate the saved results, and rebuild report tables/plots.
- gbm.py — exact GBM, price EM, and scalar Milstein, with an independent control-variate pilot.
- nonaffine.py — coupled log-EM for the prescribed non-affine model, with three reference grids.
- verify.py — independent deterministic checks and saved-array/statistics consistency checks.
- build_report_data.py — generate report tables, numeric macros, and four report-specific figures from JSON/CSV.
- numerical_summary.txt — compact account of the actual completed run.
- results/ — full-precision JSON/CSV, terminal samples in NPZ, verification evidence, and run logs.
- figures/ — vector PDF and high-resolution PNG figures.
- source/problem_pack.pdf — supplied assignment.

The cover uses “Coursework Report”. The example author's name, student ID, and unrelated course number were not copied. To add your own details, edit the LaTeX author field and compile again.

## Reproduce

Tested with Python 3.12.14, NumPy 2.5.3, Matplotlib 3.11.1, and Numba 0.67.0 on Windows.

In a terminal opened in this directory:

    python -m pip install -r requirements.txt
    python run_all.py

The run generates all numerical outputs before the final report-building step. It does not require internet access after dependencies are installed. Run logs and metadata describe the completed experiment; timing will vary by machine.

To check the supplied results without resimulating all paths:

    python verify.py

To rebuild the figures/tables without resimulation:

    python build_report_data.py

To compile the report, install a LaTeX distribution with the packages listed in the preamble, then run twice:

    pdflatex -interaction=nonstopmode -halt-on-error Problem4_FinancialSDE_Coursework.tex
    pdflatex -interaction=nonstopmode -halt-on-error Problem4_FinancialSDE_Coursework.tex

The PDF is already compiled, so LaTeX is not needed just to read the report or run the experiments.

## Experimental settings

GBM (chosen baseline): S0=100, mu=0.05, sigma=0.30, T=1.
Production paths: 160,000. Independent pilot: 20,000.
Production seed: 2026090804. Pilot seed: 2026090805. Batch size: 2,000.
Time steps: 1/8, 1/16, ..., 1/1024.
Strong and controlled weak slopes use the five finest grids.

Non-affine model (prescribed baseline): S0=100, Y0=0, mu=0.05, kappa=2,
theta=-0.2, xi=0.6, rho=-0.7, sigma_min=0.10, sigma_max=0.50, T=1.
Paths: 100,000. Seed: 2026090804. Batch size: 512.
Coarse grids: N=8,16,32,64,128,256.
Reference grids: N=2048,4096,8192.
The prespecified principal strong-rate window uses N=8,16,32,64.

All coarse increments sum the finest Brownian increments. The two models are separate experiments; using the same seed does not imply a pathwise comparison between models. Preserve path count, grid sizes, seeds, batch sizes, and package versions to reproduce the saved realizations. In particular, changing the non-affine batch size changes which pseudorandom draws are assigned to a path.

The .deps lookup in scripts is optional support for the development environment. This clean package does not contain .deps; a regular Python installation with requirements.txt is sufficient.

## Interpretation

Strong error is terminal L1, not a path-supremum norm. Weak error uses signed paired differences and 95% pointwise Monte Carlo confidence intervals. The GBM CSV contains raw paired and control-variate estimates separately. Exact discrete-mean bias is a validation target, never substituted for simulated results.

Non-affine differences are relative to numerical references. The last refinement difference passes a practical 10% sensitivity screen on the stated principal strong-rate window, but does not rigorously bound error against an exact solution. The finer coarse grids retain greater reference sensitivity. No weak order is claimed when the paired confidence intervals include zero.

The call quantity is an undiscounted payoff expectation under the supplied drift, not a risk-neutral option price. The correct mean alone is not a weak-order test: the non-affine log-EM scheme preserves the asset's first moment in expectation at any step.

## Sources

- Supplied Problem Pack, Direction 4, pages 6–7 (included in source/).
- D. J. Higham (2001), SIAM Review 43(3), 525–546:
  https://doi.org/10.1137/S0036144500378302
- P. E. Kloeden and E. Platen (1992), Numerical Solution of Stochastic Differential Equations:
  https://doi.org/10.1007/978-3-662-12616-5

The earlier numerical-differentiation coursework was used only as a style and structure reference; its numerical results and references were not reused for this problem.

