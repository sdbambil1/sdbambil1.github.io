# Open Silas-Bambil.Rproj in RStudio, then run source("preview.R").
find_quarto <- function() {
  on_path <- Sys.which("quarto")
  if (nzchar(on_path)) return(unname(on_path))
  candidates <- c(
    "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto",
    "/Applications/RStudio.app/Contents/Resources/quarto/bin/quarto",
    path.expand("~/Desktop/RStudio.app/Contents/Resources/app/quarto/bin/quarto"),
    "/opt/homebrew/bin/quarto", "/usr/local/bin/quarto"
  )
  available <- candidates[file.exists(candidates)]
  if (length(available)) return(available[[1L]])
  stop("Quarto was not found. Use a recent RStudio installation or install Quarto from https://quarto.org/docs/get-started/.", call. = FALSE)
}
if (!file.exists("_quarto.yml")) stop("Open Silas-Bambil.Rproj first so the site folder is your working directory.", call. = FALSE)
quarto_bin <- find_quarto()
message("Starting Quarto preview. Press Esc in the RStudio Console to stop.")
status <- system2(quarto_bin, c("preview", "."))
if (!identical(status, 0L)) message("Quarto preview exited with status ", status, ".")
