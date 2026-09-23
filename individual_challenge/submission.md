# Tutorial 3 Individual Challenge: GBM strong-convergence figure

## Observation selected

I used an issue identified in our own figure review:

> **The strong-convergence plot showed the data and theoretical guide lines, but it did not display fitted slopes with uncertainty bands, a claim title, units, or the round-off floor.**

This is a concrete visualization issue and matches the Tutorial 3 requirement: one observation must be turned into one quantitative figure.

## Figure before improvement

Upload **figure_before_improvement.png**.

The original report figure already used log--log axes, pointwise Monte Carlo error bars, and theoretical order guides. Its limitations were that the fitted slope was not shown on the plot, no uncertainty band was attached to that slope, the title did not state a conclusion, the axes omitted units, and round-off was not discussed.

## Quantitative improvement

The revised figure keeps the original production data and adds:

1. fitted lines on the stated window $N=64,128,256,512,1024$;
2. slope estimates with standard errors;
3. 95% fitted-line bands based on 20 independent random seeds, with 20,000 paths per seed;
4. theoretical order-$1/2$ and order-$1$ reference lines;
5. a conclusion in the title, units on both axes, and a reproducibility note;
6. an annotation showing that the round-off floor was not reached.

The repeat experiment gave:

- EM mean fitted slope: $0.498704$, standard error $0.000515$, 95% confidence interval $[0.497625,0.499782]$;
- Milstein mean fitted slope: $0.993809$, standard error $0.000382$, 95% confidence interval $[0.993009,0.994609]$.

These independent-seed results are close to the theoretical orders $1/2$ and $1$. Their narrow intervals describe repeat-to-repeat Monte Carlo variability on this fixed five-grid window; they do not include finite-step, fitting-window, or model-theory uncertainty. The exact theoretical values therefore need not lie inside these sampling intervals.

The smallest production error was $1.53\times10^{-3}$, whereas the simple floating-point scale $\epsilon S_0$ is about $2.22\times10^{-14}$. The experiment therefore did not reach a round-off floor.

Within each seed, all five grids aggregate the same 1024-step Brownian increments, so the strong-error comparison remains pathwise coupled. The uncertainty bands are formed from the spread of fitted lines across independent seeds, following the Tutorial 3 warning that a Monte Carlo claim requires repeats across seeds.

## Figure after improvement

Upload **figure_after_improvement.png**.

Suggested caption:

> **GBM terminal strong convergence before and after quantitative review.** The improved log--log figure reports fitted slopes and independent-seed uncertainty bands on $N=64,128,256,512,1024$, together with theoretical order guides. Across 20 independent seeds of 20,000 paths, the EM slope was $0.4987\pm0.0005$ SE and the Milstein slope was $0.9938\pm0.0004$ SE. The minimum observed error remained about eleven orders of magnitude above $\epsilon S_0$, so no round-off floor was reached.

## Short database text

> Observation: our original GBM strong-convergence plot had log--log data and theoretical guides, but it did not show fitted-slope uncertainty or annotate round-off. I retained the original production results and added fitted lines, 95% bands from 20 independent seeds (20,000 paths per seed), units, a claim title, and a round-off annotation. On $N=64,128,256,512,1024$, EM gave slope $0.4987\pm0.0005$ SE and Milstein gave $0.9938\pm0.0004$ SE, close to theoretical orders $1/2$ and $1$. The smallest error was $1.53\times10^{-3}$, far above $\epsilon S_0\approx2.22\times10^{-14}$, so round-off was not reached. The confidence bands quantify seed-to-seed sampling variability on this fitting window.

## Reproduce the result

From the project root, run:

    python3 individual_challenge/build_convergence_before_after.py

The script copies the original report figure as the before image, reads the saved production convergence table, runs the documented independent-seed repeat experiment, and writes the after image plus **convergence_repeat_results.json**.
