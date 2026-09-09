# Tutorial 1 — setup and first scaffold

This folder implements the complete coding deliverable described in
`tutorial1_slides.pdf`:

1. `environment_setup.md` gives the environment/version sanity check.
2. `rk4_stability_region.py` is the plotting scaffold sanity test.
3. `euler_skeleton.py` provides a dimension-agnostic explicit-Euler solver,
   an analytic logistic check, the DOP853 `solve_ivp` oracle, the Van der Pol
   challenge, and its oracle phase-plane plot.

Run from the project root:

```bash
python tutorial1/rk4_stability_region.py
python tutorial1/euler_skeleton.py
```

The Van der Pol experiment follows the slides exactly: `mu=1`,
`y0=(0.5, 0)`, `T=10`, and `h=(0.1, 0.05, 0.025, 0.0125)`. The script prints
the observed first-order convergence and oracle `y1(T)` to three decimals.
It also writes `tutorial1/figures/vanderpol_phase_plane.png`, the requested
parametric curve `(y1(t), y2(t))` for `0 <= t <= 10`; generated figures and
numerical output are intentionally ignored by Git.
