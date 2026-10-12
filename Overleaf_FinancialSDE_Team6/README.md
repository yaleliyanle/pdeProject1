# Team 6 — Financial SDE Report Source

This source package accompanies the coursework report *Numerical Simulation of Financial SDEs: Problem 4 — GBM Benchmark and Non-Affine Volatility*. It contains 15 LaTeX source files and eight PDF figures for the current 27-page report, including the team AI Transparency Log and five Individual Contribution Statements.

Team 6 comprises Yifan Chen (2362353), Zeya Hu (2362375), Yanle Li (2363600), Qingwen Ma (2361052), and Chenyi Xu (2359968).

## Compilation

The Overleaf main document is `main.tex`, and the compiler is XeLaTeX. The source also supports local compilation with `tectonic main.tex` from this folder. Its typesetting dependencies are standard LaTeX packages; no Python environment, market-data download, result generation, custom fonts, or separate bibliography file is required.

Official Overleaf documentation: [project upload](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project) and [compiler selection](https://docs.overleaf.com/getting-started/recompiling-your-project/selecting-a-tex-live-version-and-latex-compiler).

## Source organisation

| File or directory | Contents |
| --- | --- |
| `main.tex` | Report text, mathematical analysis, algorithms, references, and source inclusion |
| `team_metadata.tex` | Team identification, authors, student numbers, and submission date |
| `ai_transparency.tex` | Team AI Transparency Log and declaration |
| `individual_statements.tex` | Five Individual Contribution Statements |
| `results/report_values.tex` | Numerical values referenced throughout the report |
| Other `.tex` files in `results/` | Numerical tables, experimental protocol, repeat-study results, and cost comparison |
| `figures/` | Eight PDF figures used in the report |

The numerical tables and figures were produced by the separately supplied code archive and are included here as fixed results. The executable code and raw result files cited in the report are supplied in that archive and are not dependencies of this LaTeX source package.
