# Final technical code review record

This record combines the team-confirmed division of member review with the
AI-assisted technical audit and automated verification. The numerical audit
evidence is recorded in `code_audit_evidence.json`; the report's A4 and five
individual statements record personal responsibilities. No signature or
individual authorship is inferred from test results.

## Confirmed member responsibilities

| Member | Reviewed contribution |
|---|---|
| Yifan Chen (2362353) | Models, log-price transformation, EM/Milstein formulas, and strong/weak convergence interpretation. |
| Zeya Hu (2362375) | GBM coupling and updates, independent-pilot controls, and moment/distribution checks. |
| Yanle Li (2363600) | Correlated increments, simultaneous old-Y log-EM, nested grids, and numerical-reference interpretation. |
| Qingwen Ma (2361052) | Figures, signed intervals, independent-seed rate variability, and common-accuracy kernel costs. |
| Chenyi Xu (2359968) | Report consistency, reproduction commands, test/evidence distinctions, and archive organisation. |

These responsibilities follow the confirmed work reflected in the individual
statements. They do not assert that each member independently authored the
whole implementation or personally performed the complete production rerun.
The available Git history uses a shared `Apple` author label and is not
evidence of separate personal commits.

## Actual tests

The tested environment was Python 3.9.6, NumPy 2.0.2, Matplotlib 3.9.4, and
Numba 0.60.0 on macOS arm64. Numba was installed in an isolated virtual
environment; NumPy and Matplotlib were inherited from system site-packages.

- Seven unit tests passed: GBM recurrences/moments; old-state non-affine updates
  and constant-volatility reduction; rejection of invalid nested grids;
  correlated-driver scaling and aggregation; increment variance/correlation;
  exact control-variate centering by Gaussian quadrature; baseline Milstein
  positivity.
- The saved-run checker passed without changing production results. It checks
  all 18 non-affine coarse/reference rows, their SEs and CIs, both refinement
  rows, GBM coarse/fine raw statistics, analytic biases, and fitted slopes.
- A complete production rerun passed into a temporary artifact directory:
  160,000 GBM paths, 20,000 independent-pilot paths, and 100,000 non-affine paths.
  The GBM stage took about 7.4 seconds and the non-affine simulation about
  25.7 seconds on this machine. These are not a matched-accuracy timing study.
- `python code/run_all.py --smoke` passed with all baseline/supplementary figures
  and report inputs. The same command, saved-run check, and unit tests passed
  from a separate copied package outside the source repository.
- The final extracted ZIP passed all seven unit tests and saved-array
  verification. ZIP integrity checks passed; the manifest records the two
  final artifacts and the 70-file archive.

The rerun agrees with the original terminal arrays to floating-point roundoff:
GBM EM/Milstein endpoints are bit-identical, exact GBM differs by at most
`5.684e-14`, and the non-affine grids by at most `3.695e-13`. Displayed slopes
and the scientific interpretation are unchanged. Smoke results are execution
tests, not production convergence evidence.

## Verified implementation properties

| Location | Verified property |
|---|---|
| `code/nonaffine.py:79` | The grid interface requires a positive integer dividing the finest grid exactly and rejects invalid counts and malformed increment arrays. |
| `code/run_all.py:14` | The entry point resolves the package root, supports explicit output directories and isolated smoke runs, and operates from an extracted package outside the repository. |
| `requirements.txt` | Compatible dependency ranges support installation; the documented audit environment and historical production metadata identify the versions used for each run. |
| `code/gbm.py:114`, `code/nonaffine.py:127` | Time, price and density axes specify years, currency and inverse currency. |

The implementation uses fixed seeds, common Brownian increments, an
independent control-variate pilot and unclipped prices. Results distinguish
exact GBM errors from differences against finite numerical references.

## Review scope and scientific limits

Problem Pack page 1 explicitly replaces the deterministic stability/adaptivity
tasks for Direction 4. The required SDE oracle, price EM/Milstein comparison,
strong/weak errors, Monte Carlo uncertainty, and nested-grid validation were
checked. We do not claim to have implemented deterministic RK4, Newton,
absolute-stability regions, or an adaptive time controller.

The kernels are model-specific and parameterized, rather than a fully generic
swappable drift/diffusion solver. The constant-volatility reduction tests the
specified interface. Tests cover the documented protocol and do not establish
correctness for every parameter setting or platform.

Non-affine errors use finite numerical references; refinement differences do
not certify the residual error against the exact solution. Monte Carlo
intervals and repeated-seed slope variability exclude numerical-reference and
fit-window bias. Fine-grid weak slopes are withheld when signed intervals
contain zero. GBM negativity counts describe terminal prices. Cost timings
cover the stated numerical kernels and exclude RNG, grid aggregation and other
workflow costs. The AI-assisted production rerun and checks are evidence of
technical reproduction, not proof of personal intellectual ownership.
