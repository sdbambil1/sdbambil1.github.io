#' Percentile Bootstrap Confidence Interval for a Mean
#'
#' Resamples observations with replacement to estimate a
#' confidence interval for a population mean.
#'
#' @param x Numeric vector with at least two finite observations.
#' @param B Number of bootstrap samples; a whole number of at least 2.
#' @param conf Confidence level strictly between 0 and 1.
#' @details Assumes independent, identically distributed observations
#' with finite population mean and variance. Uses type-7 quantiles.
#' Coverage may be poor for small or strongly skewed samples.
#' Set the seed before calling the function for reproducibility.
#' @return A list with estimate, lower, upper, and bootstrap_means.
#' @importFrom stats quantile
#' @examples
#' set.seed(1998)
#' result <- bootstrap_mean_ci(c(10, 20, 30, 40, 50))
#' c(lower = result$lower, upper = result$upper)
#' @export
bootstrap_mean_ci <- function (x, B = 2000, conf = 0.95) 
{
    if (!is.numeric(x) || !is.null(dim(x))) {
        stop("x must be a numeric vector.")
    }
    if (length(x) < 2L || any(!is.finite(x))) {
        stop("x must contain at least two observations, with no NA, NaN, or infinite values.")
    }
    if (!is.numeric(B) || length(B) != 1L || !is.finite(B) || 
        B < 2 || B != floor(B) || B > .Machine$integer.max) {
        stop("B must be a whole number between 2 and .Machine$integer.max.")
    }
    if (!is.numeric(conf) || length(conf) != 1L || !is.finite(conf) || 
        conf <= 0 || conf >= 1) {
        stop("conf must be a single number strictly between 0 and 1.")
    }
    bootstrap_means <- numeric(B)
    for (b in seq_len(B)) {
        x_boot <- sample(x, size = length(x), replace = TRUE)
        bootstrap_means[b] <- mean(x_boot)
    }
    alpha <- 1 - conf
    ci <- quantile(bootstrap_means, probs = c(alpha/2, 1 - alpha/2), 
        names = FALSE)
    list(estimate = mean(x), lower = ci[1], upper = ci[2], bootstrap_means = bootstrap_means)
}
