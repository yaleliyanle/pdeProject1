# Problem 4: 10-minute presentation notes

Use these notes for the 15 main slides. Suggested speech timings total
9 minutes 10 seconds. Allow up to 50 seconds for pauses, pointing at the plots,
and changing speakers. The four backup slides are for the separate 3-minute Q&A.
Do not read the displayed equations line by line. Say what each equation does.
No speaker roles have been assigned here; the team should choose its own split.

## Slide 1 — Financial SDEs (15 seconds)

Hello everyone. Our project studies numerical methods for financial SDEs.
We use two models. The first has an exact answer. The second does not.
Our main question is simple. How can we tell numerical error from sampling
noise?

## Slide 2 — Two models (35 seconds)

We start with GBM. It gives us an exact benchmark. We compare EM and Milstein
against that benchmark. Then we move to a non-affine stochastic-volatility
model. Here, the volatility changes with another random state. We cannot
simulate its transition exactly in a practical way. We therefore build a
fine-grid reference. These models have different roles. One checks the method.
The other checks how we use it when the answer is unknown.

## Slide 3 — Two types of error (40 seconds)

Strong error asks whether individual paths are close. The numerical path and
the reference must use the same random input. Weak error asks whether a chosen
average is close. That average could be a price or a payoff. There is also
sampling noise. A smaller time step does not remove this noise. We need more
paths or better variance reduction. So we track both the grid error and the
uncertainty of the average.

## Slide 4 — GBM updates (40 seconds)

For GBM, both drift and noise depend on the current price. Its exact solution
is available, so we can measure the error directly. EM uses the drift and
Brownian increment for each step. Milstein adds one correction. That correction
has zero mean, but it improves individual paths. All three calculations share
the same increments. This gives a fair comparison. We discretise the price
itself. A log-price update would already be exact for this model.

## Slide 5 — Strong results (45 seconds)

Here, the horizontal axis is the time step. The vertical axis is the average
absolute terminal error. Both axes use a log scale. The slope therefore tells
us the convergence order. EM follows the half-order guide. Milstein follows
the order-one guide. The fitted values are close to these predictions. We also
state the fitting window and show uncertainty. The result is not just that
Milstein has a smaller error. Its error decreases faster as we refine the grid.

## Slide 6 — Why the weak slopes match (45 seconds)

For this test, the observable is the terminal mean. Milstein's extra correction
averages to zero, even when we condition on the old price. Both methods
therefore have the same expected growth in each step. Repeating the steps
gives the same numerical mean for both methods. That mean differs from the
exact mean by a term proportional to the time step. So both weak slopes
approach one. Better paths do not improve this particular mean.

## Slide 7 — Weak results (35 seconds)

That explanation is visible in this plot. The two weak-error curves almost
overlap. This is expected. It is not a plotting mistake. The analytic bias is
the same for both methods. The MC estimates differ slightly because of
sampling. We use control variates to make that sampling error smaller. Their
coefficients come from a separate pilot sample. The plotted estimates are
still simulation results, not exact values copied into the graph.

## Slide 8 — Distribution and positivity (30 seconds)

We also compare the terminal distribution with the exact lognormal law. The
histogram and quantile plot give two different checks. We check the mean and
variance as well. No negative terminal values occurred in the reported runs.
But that observation is not a general positivity proof for EM. We do not clip
negative values, because clipping would change the method being tested.

## Slide 9 — Cost at matched accuracy (35 seconds)

Order alone is not a complete cost comparison. We first choose a common strong
error target. Then we find a suitable grid for each method. Each grid must meet
the same error tolerance. Their achieved errors do not have to be exactly equal. We measure both
methods on the same machine and state what the timing includes. This plot
connects achieved accuracy with measured work. A coarser grid may be enough
for the higher-order method. The important comparison is the cost of meeting
the same goal, not the speed of two unrelated runs.

## Slide 10 — The non-affine model (40 seconds)

In the second model, X is the log price. Y controls its volatility. The two
Brownian drivers are correlated. We use the benchmark parameters from the
problem pack. EM updates X and Y together. Both updates must use the old Y.
We then recover the price by exponentiating X. This preserves positivity in
the mathematical update. We also check finite, positive values in the code.
We do not assume that scalar Milstein results apply to this two-noise system.

## Slide 11 — What the nested grid does (45 seconds)

This diagram shows the coupling. We first generate increments on the finest
grid. We add neighbouring increments to build a coarser grid. The total random
motion over a coarse interval is then the same. We rerun EM on every grid.
We do not just take every second price from the fine path. The reference uses
many more steps than the coarse solutions. But it is still numerical. That
is why we call the result a reference difference, not a known exact error.

## Slide 12 — Strong differences and reference checks (40 seconds)

The non-affine strong differences follow an approximately half-order slope.
We repeat the comparison with three reference grids. The slopes remain close.
We also compare successive reference solutions with each other. This is useful
evidence that the main conclusion is stable. We fit only the stated coarse
window. At finer coarse levels, reference error becomes more important. Similar
slopes are reassuring, but they are not a rigorous bound on the unknown exact
solution.

## Slide 13 — Why we do not report a weak order (40 seconds)

The mean is not a useful weak test here. The log-EM update preserves it exactly
in expectation. So we use a nonlinear call payoff instead. The coarse-grid
differences are statistically visible. At the finer grids, the confidence
intervals include zero. Sampling noise is then too large for a reliable rate
fit. We therefore do not report a weak order. Also, this is an undiscounted
payoff statistic. We are not claiming a risk-neutral option price.

## Slide 14 — Diagnostics and reproducibility (30 seconds)

A convincing plot is not enough. We check the input noise, including its
variance and correlation. We check finite states and positivity. We compare
the mean with an exact structural identity. We refine the reference more than
once. Finally, we record the seeds and environment, and provide scripts to
reproduce the tables and figures. These checks help us catch errors that a
convergence line alone might miss.

## Slide 15 — Conclusions (35 seconds)

Our main lesson is that accuracy depends on what we measure. Milstein gives
better strong convergence for GBM. It does not improve this model's weak mean
bias. In the non-affine model, nested-grid tests support half-order strong
behaviour. The weak payoff rate remains unresolved at our current budget.
We use exact answers when available. Otherwise, we refine the reference and
report the limits of the evidence. Thank you. We are happy to take questions.

## Backup slide 1 — Sources

Use only if asked about the problem specification, the standard convergence
results, or how to reproduce the project. The code README is the practical
entry point. These backup slides are not part of the timed main talk.

## Backup slide 2 — Exact log-EM mean

Use only if asked why the second model's mean cannot show weak bias. Conditional
on the current information, the volatility coefficient is fixed. The Gaussian
exponential has a known expectation. Its variance term cancels the correction
in the log-price drift. This leaves exactly the prescribed mean growth in each
step. An exact mean does not make the full terminal distribution exact.

## Backup slide 3 — Independent-seed GBM repeats

Use only if asked about fitted-slope uncertainty. We repeat a smaller experiment
with eight independent seeds. The grid window matches the production fit. The
shading shows the empirical spread across these runs. It is not a rigorous
confidence band for the true convergence curve.

## Backup slide 4 — Independent-seed non-affine repeats

Use only if asked whether the second model's slope depends on one seed. The
repeat check uses fewer paths than the main experiment, but keeps the same
fitting window and fine reference. The results remain close to half order.
This supports repeatability. It does not turn the reference into an exact
solution.
