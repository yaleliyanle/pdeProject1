# Final submission record

Recorded on 12 October 2026 for Team 6: Yifan Chen (2362353), Zeya Hu
(2362375), Yanle Li (2363600), Qingwen Ma (2361052), and Chenyi Xu
(2359968).

## Report and declarations

- The compiled report has 27 pages, follows the supplied report structure and
  uses numbered equations with dynamic references and explanatory captions.
- The AI Transparency Log records mathematical, implementation, verification
  and document assistance, including the limits of AI-assisted checks.
- A4 occupies page 21; the five completed individual contribution statements
  occupy pages 22–26, one page per member. They identify specific review work,
  obstacles, AI-assisted material, reflections and limits of understanding.
- Signature and date lines are personal signing fields.
- The PDF compiled successfully, with no unresolved references or overfull
  boxes. Recorded underfull boxes and an algorithm comment-encoding warning
  do not prevent output.

## Scientific and technical evidence

- GBM exact, price EM and scalar Milstein use shared Brownian paths. Strong
  errors, raw and controlled weak estimates, confidence intervals, moment and
  distribution checks, and terminal negativity frequencies are recorded.
- The prescribed non-affine model uses simultaneous old-Y log-EM, correlated
  drivers and nested increments. Three numerical references, paired error
  intervals and intermediate-state diagnostics are included.
- Eight independent-seed repetitions quantify sampling variability. The
  common-accuracy cost study reports achieved errors and its kernel timing
  boundary.
- A full production rerun, saved-array/statistic checks, seven unit tests and
  isolated smoke runs passed. The extracted code archive also passed all
  seven tests and saved-array verification.
- Member review responsibilities are recorded in `CODE_REVIEW.md` and the
  individual statements. The technical verification was AI-assisted and does
  not constitute an independent human audit.

## Final artifacts

`upload/` contains `Financial_SDE_Report.pdf`, `Financial_SDE_Code.zip` and
`manifest.json`. The manifest records their sizes and SHA-256 checksums. The
ZIP contains 70 files, including runnable code, tests, saved results,
figures, report sources and the supplied problem pack. Integrity validation
passed. It excludes internal compliance notes, empty declaration templates,
presentation files, historical archives, local environments, caches and Git
metadata.

The presentation is completed. Presentation files are excluded from the final
report/code archive.

## Scope and interpretation

The Direction 4 exception replaces generic deterministic ODE stability and
adaptivity tasks with the SDE requirements. The solver kernels are
model-specific and parameterised. GBM negativity observations are terminal
frequencies. Non-affine grid differences are numerical-reference differences,
not exact-solution errors; the reference-sensitivity screen is not a rigorous
residual bound. Sampling intervals and seed variability exclude reference
and fitting-window bias. Cost measurements cover the stated update kernels,
not the complete workflow.

Repository submissions were centralised under the shared `Apple` author
label; individual contributions are described in the contribution statements.
The report and code are the final technical deliverables, with the verified
scope and scientific limitations recorded above.
