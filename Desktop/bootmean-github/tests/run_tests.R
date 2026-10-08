# Run from the project root: source("tests/run_tests.R")
source("R/model_runtime.R")
fails <- function(expr) inherits(tryCatch({force(expr);NULL},error=function(e)e),"error")

# Always verify the shipped portable model, even when a native model is active.
temporary <- tempfile("portable-test-");dir.create(temporary)
dir.create(file.path(temporary,"portable"))
file.copy(list.files("model/portable",full.names=TRUE),file.path(temporary,"portable"))
portable <- load_loan_model(temporary)
unlink(temporary,recursive=TRUE)
fixtures <- read.csv("tests/fixtures.csv",stringsAsFactors=FALSE)
expected <- read.csv("tests/expected.csv",stringsAsFactors=FALSE)
actual <- score_loan_rows(portable,fixtures)
stopifnot(max(abs(actual$ProbabilityDefault-expected$ProbabilityDefault))<1e-10)
stopifnot(max(abs(actual$ProbabilityDefault+actual$ProbabilityNonDefault-1))<1e-12)
stopifnot(identical(actual$LoanID,expected$LoanID))
reordered <- fixtures[,rev(names(fixtures)),drop=FALSE]
stopifnot(identical(score_loan_rows(portable,reordered)$ProbabilityDefault,actual$ProbabilityDefault))
stopifnot(fails(score_loan_rows(portable,fixtures[,setdiff(names(fixtures),"Income")])) )
invalid <- fixtures;invalid$Income[1] <- NA;stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$Income[1] <- "not a number";stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$Income[1] <- 0;stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$Age[1] <- 35.2;stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$Education[1] <- "Unseen category";stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$LoanID[2] <- invalid$LoanID[1];stopifnot(fails(score_loan_rows(portable,invalid)))
invalid <- fixtures;invalid$LoanAmount[1] <- Inf;stopifnot(fails(score_loan_rows(portable,invalid)))
outside <- fixtures[1,,drop=FALSE];outside$Age <- 75
stopifnot(grepl("Outside training range",score_loan_rows(portable,outside)$InputSupport))
high <- score_loan_rows(portable,fixtures,threshold=1)
low <- score_loan_rows(portable,fixtures,threshold=0)
stopifnot(identical(high$ProbabilityDefault,low$ProbabilityDefault))
stopifnot(all(low$ReviewFlag=="Flagged for review"))
explanation <- sensitivity_comparison(portable,fixtures[1,,drop=FALSE])
stopifnot(nrow(explanation)==16,all(is.finite(explanation$DifferencePP)))

# Check the active native bundle too, when registered; do not compare its different fit to old coefficients.
active <- load_loan_model("model")
ref <- reference_applicant(active$schema)
one <- score_loan_rows(active,ref)
stopifnot(nrow(one)==1,is.finite(one$ProbabilityDefault))
if(active$engine=="native") {
  before <- active
  after <- compact_bundle(active)
  stopifnot(max(abs(score_loan_rows(before,ref)$ProbabilityDefault-
                    score_loan_rows(after,ref)$ProbabilityDefault))<1e-10)
}
message("Scoring tests passed: probability parity, schema validation, support warnings, threshold invariance and sensitivity.")
