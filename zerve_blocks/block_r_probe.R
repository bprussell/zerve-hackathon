# R Package Probe - run this to see what's available in Zerve
# Connect this directly to the ingest block (block1), NOT to wrangle

cat("=== R packages available ===\n\n")

# Check key packages for fixed-effects regression
pkgs <- c("fixest", "lfe", "plm", "lme4", "data.table", "stats")
for (p in pkgs) {
  avail <- requireNamespace(p, quietly = TRUE)
  cat(sprintf("  %-12s %s\n", p, ifelse(avail, "YES", "no")))
}

cat("\n=== All installed packages ===\n")
ip <- installed.packages()
cat(paste(sort(ip[, "Package"]), collapse = ", "), "\n")
