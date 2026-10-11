# Pre-submission technical code audit

This is an AI-assisted technical audit, not a signed intra-team human review.
The members still need to record their own review and confirm their ownership.
The machine-readable record is `code_audit_evidence.json` in this directory.

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

The rerun agrees with the original terminal arrays to floating-point roundoff:
GBM EM/Milstein endpoints are bit-identical, exact GBM differs by at most
`5.684e-14`, and the non-affine grids by at most `3.695e-13`. Displayed slopes
and the scientific interpretation are unchanged. Smoke results are execution
tests, not production convergence evidence.

## Findings fixed

| Severity | Location | Finding and resolution |
|---|---|---|
| Major | `code/nonaffine.py:79` | Invalid non-divisor grids could silently advance the wrong terminal time. Require a positive integer dividing the finest grid and test rejection. |
| Major | `code/run_all.py:14` | The legacy artifact layout was not compatible with the required `code/` entry point. Add package-root resolution, explicit output roots, and isolated smoke runs. |
| Minor | `requirements.txt` | Old exact pins did not describe this audit environment. Use compatible ranges and preserve historical production metadata. |
| Minor | `code/gbm.py:114`, `code/nonaffine.py:127` | Missing time/price/density units. Label years, currency and inverse currency. |

Keep the fixed seeds, common Brownian increments, independent CV pilot,
unclipped prices, and explicit distinction between exact errors and finite
reference discrepancies. These are strong features of the implementation.

## Checklist scope and remaining ownership

Problem Pack page 1 explicitly replaces the deterministic stability/adaptivity
tasks for Direction 4. The required SDE oracle, price EM/Milstein comparison,
strong/weak errors, Monte Carlo uncertainty, and nested-grid validation were
checked. We do not claim to have implemented deterministic RK4, Newton,
absolute-stability regions, or an adaptive time controller.

The kernels are model-specific and parameterized, not a fully generic swappable
drift/diffusion solver. This limitation is stated rather than hidden behind a
generic `f(t,y)` claim. Each member must still review the code, provide honest
contribution evidence, and complete their own ICS/declaration/signature. The
automated audit does not establish who authored or reviewed any artifact.
