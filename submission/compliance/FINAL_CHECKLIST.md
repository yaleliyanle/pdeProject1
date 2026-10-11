# Submission checklist — actual status

The generic ODE items are interpreted using the explicit Direction 4 exception on the problem pack's first page. This is an automated preparation record, not a signed student review.

## Technical checks completed

- [x] Report follows the attached template's structure; at least eight pages.
- [x] Equations compile and use dynamic references; captions interpret every scientific figure.
- [x] GBM exact/price EM/Milstein comparison; two observed strong orders.
- [x] Mean weak errors, raw/CV estimates and sampling intervals; identical mean-bias explanation.
- [x] Lognormal histogram/quantiles and moment oracle checks; optional positivity formulas and terminal frequencies.
- [x] Prescribed non-affine model and simultaneous old-Y log-EM.
- [x] Shared nested Brownian increments, three reference grids, strong/weak paired intervals.
- [x] Driver variance/correlation and intermediate-state finiteness/positivity checks.
- [x] Eight independent-seed repetitions; uncertainty wording excludes reference/window bias.
- [x] Two-method error-versus-measured-cost experiment at a common accuracy target, with overshoot and exclusions stated.
- [x] Team AI log A1–A3 drafted from actual assistance and automated evidence; A4 and five ICS pages included as uncompleted forms.
- [x] README, compatible dependencies, fixed seeds and no developer-machine paths in executable code.
- [x] Full production rerun, saved-array verification, seven unit tests and isolated end-to-end smoke run pass.
- [x] Slide deck has 15 timed main pages plus four explicitly labelled Q&A backups, with simple-English notes for a ten-minute presentation.
- [x] Portable ZIP excludes virtual environments, caches and Git internals, while preserving figure assets and report sources.

## Not applicable or limited — do not mark as an unperformed required ODE experiment

- Deterministic three-method stability regions, RK4/implicit Newton and adaptive ODE control: replaced by SDE-specific tasks in the problem pack.
- Stiffness ratio / conservation law: no such quantity is asserted for this stochastic financial model.
- A completely model-agnostic production solver: not claimed. The implementation is specialised and parameterised; a constant-volatility special case verifies its interface. This is a documented maintainability limitation, not a fabricated generic solver.
- GBM negativity: terminal frequencies only; no all-time negative-path diagnostic or full option-price stress test is claimed.
- Actual presentation duration: notes are designed for ten minutes; only a real rehearsal can confirm delivery time.

## Remaining blockers before final upload

- [ ] Confirm team number and five names/student IDs.
- [ ] Each member completes their own ICS in their own voice, citing genuine contributions and evidence.
- [ ] Each member confirms and signs A4 intellectual ownership; confirm all actual AI tools.
- [ ] Complete and record human intra-team code review; automated tests do not replace it.
- [ ] Rehearse main slides within ten minutes.
- [ ] Remove completed-form draft notices, recompile PDFs and rebuild final ZIP; do not rename a DRAFT into a final file without completing its contents.

Current status: **technical verification complete; not yet ready for final upload because personal declarations and confirmation are missing.**
