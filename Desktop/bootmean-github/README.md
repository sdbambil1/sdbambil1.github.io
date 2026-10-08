# bootmean

An R package for percentile bootstrap confidence intervals for a
population mean.

Authors: Silas Bambil and Yasmeen Babagana  
Maintainer: Silas Bambil <sbambil1@student.gsu.edu>  
Course: STAT 8670 — Computational Methods in Statistics

## Installation

From a terminal, install the source package folder:

```sh
R CMD INSTALL bootmean
```

Alternatively, in R, replace the path below with the location of the
downloaded package folder:

```r
install.packages("path/to/bootmean", repos = NULL, type = "source")
```

## Minimal example

```r
library(bootmean)

set.seed(1998)
result <- bootstrap_mean_ci(
  x = c(10, 20, 30, 40, 50),
  B = 2000,
  conf = 0.95
)

result$estimate
c(lower = result$lower, upper = result$upper)
```

The function returns the original sample mean, lower and upper
interval endpoints, and the bootstrap means.

## Method and assumptions

The implementation draws samples of the original size with replacement,
calculates their means, and takes the required percentiles using
R's default type-7 quantiles.

Observations should be independent and identically distributed,
with finite population mean and variance. Missing and infinite values
are rejected. Percentile intervals may under-cover for small or
strongly skewed samples.

## Tests

From R, run the tests against the package source:

```r
testthat::test_local("path/to/bootmean")
```

Tests cover constant data, invalid inputs, and agreement with an
index-based resampling reference.

## Package checks

From a terminal, in the directory containing the package folder:

```sh
R CMD build bootmean
R CMD check --no-manual bootmean_0.1.0.tar.gz
```

The development version passed with 0 errors, 0 warnings, and 0 notes
on R 4.4.1, macOS, Apple Silicon. The PDF reference manual was excluded
using --no-manual.

## Worked example

The source vignette is `vignettes/bootstrap-mean.Rmd`.
After installation from a source archive built with vignettes, open it:

```r
vignette("bootstrap-mean", package = "bootmean")
```

## Simulation study

The study compares percentile bootstrap and standard t-intervals using:

- Normal populations with mean 2 and standard deviation 1.
- Exponential populations with rate 1 and mean 1.
- Sample sizes of 30 and 100.
- 1,000 datasets per setting.
- 2,000 bootstrap resamples per dataset.
- Seed 1998, set once at the start of each setting.

Evaluation measures are coverage, average interval width, and computing
time. Experiment scripts and reproduction commands will be added before
submission.

## Attribution

The resampling loop and interval construction were written for this
course project. Supporting calculations use base R and the stats package.
Tests use testthat; documentation uses roxygen2; the vignette uses knitr
and rmarkdown; timing experiments use microbenchmark; plots use ggplot2.

Method reference:

Efron, B. and Tibshirani, R. J. (1993).
*An Introduction to the Bootstrap*. Chapman & Hall.

## License

MIT. See LICENSE and LICENSE.md.



## Reproduce the experiments and figures

Install the experiment dependencies:

```r
install.packages(c("ggplot2", "microbenchmark"))
```

Install bootmean as described above. Then, from R, set the path to
the downloaded package folder and run:

```r
package_path <- "path/to/bootmean"

source(
  file.path(package_path, "experiments", "run_simulations.R"),
  chdir = TRUE
)

source(
  file.path(package_path, "experiments", "make_plots.R"),
  chdir = TRUE
)

source(
  file.path(package_path, "experiments", "run_timing.R"),
  chdir = TRUE
)
```

The scripts write:

- Individual simulation results and summaries to `experiments/results/`.
- Coverage and interval-width graphs to `experiments/figures/`.
- Timing summaries, raw measurements, and software information to
  `experiments/results/`.

Experiment scripts are included in the repository and submission ZIP,
but excluded from the installable source archive using .Rbuildignore.

Simulation results are reproducible with the same software environment,
random-generator settings, and sequence of calls. Execution timings vary
with computer load and hardware. A microbenchmark timer-precision warning
was observed; very small timing differences should not be overinterpreted.

