
test_that("constant data produce the known interval", {
  set.seed(1998)
  result <- bootstrap_mean_ci(rep(5, 10), B = 2000)

  expect_equal(result$estimate, 5)
  expect_equal(result$lower, 5)
  expect_equal(result$upper, 5)
  expect_equal(result$bootstrap_means, rep(5, 2000))
})

test_that("invalid inputs give useful errors", {
  expect_error(
    bootstrap_mean_ci(c(10, NA, 30)),
    "no NA, NaN, or infinite values",
    fixed = TRUE
  )
  expect_error(
    bootstrap_mean_ci(c(10, 20, 30), B = 2.5),
    "B must be a whole number",
    fixed = TRUE
  )
  expect_error(
    bootstrap_mean_ci(c(10, 20, 30), conf = 95),
    "conf must be a single number",
    fixed = TRUE
  )
})

test_that("resampling and endpoints agree with a reference", {
  x <- c(10, 20, 30, 40, 50)
  B <- 200

  set.seed(1998)
  result <- bootstrap_mean_ci(x, B = B)

  set.seed(1998)
  reference_means <- replicate(B, {
    indices <- sample.int(length(x), length(x), replace = TRUE)
    mean(x[indices])
  })

  reference_ci <- stats::quantile(
    reference_means,
    probs = c(0.025, 0.975),
    names = FALSE
  )

  expect_equal(result$estimate, 30)
  expect_equal(result$bootstrap_means, reference_means, tolerance = 1e-12)
  expect_equal(
    c(result$lower, result$upper),
    reference_ci,
    tolerance = 1e-12
  )
})

