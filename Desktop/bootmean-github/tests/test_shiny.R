# Requires Shiny; checks reactive scoring and rejection, not browser layout.
source("tests/run_tests.R")
app_object <- source("app.R")$value
shiny::testServer(app_object,{
  values <- as.list(reference_applicant(bundle$schema)[1,])
  values$threshold <- bundle$threshold
  do.call(session$setInputs,values)
  session$setInputs(score=1)
  stopifnot(!is.null(result()$score),is.finite(result()$score$ProbabilityDefault))
  session$setInputs(Income=-1,score=2)
  stopifnot(!is.null(result()$error),is.null(result()$score))
})
message("Shiny server smoke test passed.")
