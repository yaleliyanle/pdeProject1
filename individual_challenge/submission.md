# Individual Challenge: quantitative positivity diagnostic

## Observation selected

I used one of our own issue tickets: **“The positivity discussion was verbal; the simulated negative-terminal frequency was not reported explicitly.”** The original discussion derived when an Euler--Maruyama or Milstein update could be negative, but a reader could not see the actual count, denominator, frequency, or sampling resolution of the diagnostic.

## Quantitative change

I audited `results/gbm_terminal_stats.csv`, which contains 16 method/grid rows: EM and Milstein on (N=8,16,32,64,128,256,512,1024), with 160,000 paths for every row.

- EM: (0/160{,}000=0.000\%) nonpositive terminal values at every grid.
- Milstein: (0/160{,}000=0.000\%) nonpositive terminal values at every grid.
- For zero events in 160,000 trials, the exact one-sided 95% binomial upper limit for the terminal frequency at any one method/grid is
  
  \[
  1-0.05^{1/160000}=1.8723\times10^{-5}=0.0018723\%.
  \]
- For EM, the largest theoretical one-step negative probability in the tested grids occurs at (N=8):
  
  \[
  \Phi\!\left(-\frac{1+\mu h}{\sigma\sqrt h}\right)
  =1.1887\times10^{-21}.
  \]
  Thus zero observed events are consistent with the formula.
- With the chosen parameters, the Milstein multiplier is strictly positive, so its theoretical one-step negative probability is zero.

The saved diagnostic concerns terminal values only. It does not measure whether a path became negative at an intermediate step and subsequently returned to a positive terminal value. Therefore the result does not establish general positivity preservation for EM.

## Before/after figure

Upload `positivity_before_after.png` to the Individual-Challenge Database.

Suggested caption:

> **Before/after: GBM positivity diagnostic.** The original discussion described positivity verbally. The revised result reports the simulated count and denominator on all tested grids, adds an exact one-sided 95% upper limit for zero observed events, and checks consistency with the theoretical update probabilities. All saved terminal counts were (0/160{,}000); the diagnostic does not cover intermediate path values.

## Short database text

> Observation: the positivity analysis was verbal and did not explicitly report the simulated negative-terminal frequency. I converted it into a quantitative diagnostic using the saved fixed-seed data. For both EM and Milstein, every tested grid (N=8,ldots,1024) had (0/160{,}000=0.000\%) nonpositive terminal values. The exact one-sided 95% upper limit for zero events at any one method/grid is (1.8723\times10^{-5}). The largest tested EM one-step negative probability is only (1.1887\times10^{-21}) at (N=8), while the Milstein multiplier is strictly positive for this parameter set. The result is limited to terminal values because intermediate GBM states were not saved.

## Reproduce the figure

From the project root:

```sh
python3 individual_challenge/build_before_after.py
```

The script reads saved data only and does not rerun the SDE simulation.
