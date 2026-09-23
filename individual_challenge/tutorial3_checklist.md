# Tutorial 3 requirement check

The final deliverable was checked against `tutorial3_slides.pdf`.

| Slide requirement | Before | After | Evidence |
|---|---|---|---|
| Error against step size on log--log axes (p.3) | Yes | Yes | Both axes are logarithmic. |
| Theoretical slope overlaid (p.3, p.8) | Yes | Yes | Order (1/2) and order (1) guides are labelled. |
| Fitted slope with an error value (p.4) | No | Yes | Legend reports EM (0.499\pm0.0005) SE and Milstein (0.994\pm0.0004) SE. |
| 95% fitted-line band (p.5) | No | Yes | Shaded bands are empirical 2.5%--97.5% quantiles of fitted lines. |
| Monte Carlo repeats across seeds (p.5) | No | Yes | 20 independent seeds, 20,000 paths per seed. |
| Colourblind-safe curves plus non-colour encoding (p.7) | Partly | Yes | Blue circles and orange squares; distinct line styles. |
| Title states the conclusion (p.8) | No | Yes | “GBM strong slopes are close to 1/2 for EM and 1 for Milstein.” |
| Axes carry quantities and units (p.8) | Partly | Yes | Time units and price units are stated. |
| Every curve/band has a legend entry (p.8) | Yes | Yes | Data, fits, bands and theoretical guides are labelled. |
| Fixed output name and reproducible settings (p.8) | Partly | Yes | Fixed filenames, seeds, path counts and fit window are recorded. |
| Round-off floor annotated (p.8) | No | Yes | The annotation states that (epsilon S_0\approx2.2\times10^{-14}) is below the observed range. |
| One observation becomes a quantitative result (p.9) | No | Yes | The missing fit uncertainty is resolved numerically. |
| Separate before/after uploads (p.9) | No | Yes | `figure_before_improvement.png` and `figure_after_improvement.png`. |

The confidence bands quantify seed-to-seed Monte Carlo variability on the selected five-grid window. They do not include uncertainty from choosing that window, finite-step deviations from the asymptotic theory, or model assumptions. The exact theoretical orders therefore need not lie inside these sampling bands.

The remaining external action is posting the two PNG files and the prepared database text. It cannot be verified from the local project because the course database is not available here.
