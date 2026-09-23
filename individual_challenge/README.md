# Tutorial 3 Individual Challenge

The final deliverable follows pages 3--9 of `tutorial3_slides.pdf`.

- `figure_before_improvement.png`: the actual original GBM strong-convergence figure.
- `figure_after_improvement.png`: the improved quantitative figure required by Tutorial 3.
- PDF versions of both figures are included for vector output.
- `submission.md`: upload instructions, quantitative result, caption, and short database text.
- `build_convergence_before_after.py`: fixed-seed reproduction script.
- `convergence_repeat_results.json`: full independent-seed errors, slopes, and intervals.

The selected observation is that the original convergence figure did not put the fitted slope and its uncertainty on the plot and did not annotate round-off. The revised figure contains log--log error against step size, theoretical order guides, fitted slopes with standard errors, 95% bands based on independent seeds, units, a claim title, and a round-off annotation.

Run from the project root:

```sh
python3 individual_challenge/build_convergence_before_after.py
```

Use the two files named `figure_before_improvement.png` and `figure_after_improvement.png` in the corresponding database fields. The earlier positivity infographic was an exploratory alternative and is not the final Tutorial 3 submission.
