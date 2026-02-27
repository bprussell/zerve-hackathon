# Track A: Difference-in-Differences Analysis
# EAB impact on golf scores
# Uses manual demeaning (Frisch-Waugh-Lovell) + clustered SEs
# Equivalent to fixest::feols(score_vs_par ~ treatment | player + course_name + year)

dt <- as.data.frame(track_a_df)

cat("Rows:", nrow(dt), "\n")
cat("Unique courses:", length(unique(dt$course_name)), "\n")
cat("Unique players:", length(unique(dt$player)), "\n")

# Show treatment courses (both pre and post EAB data)
eab_courses <- dt[dt$eab_county == 1, ]
course_summary <- aggregate(
  treatment ~ course_name,
  data = eab_courses,
  FUN = function(x) c(pre = sum(x == 0), post = sum(x == 1))
)
cat("\nEAB courses with pre AND post data:\n")
for (i in seq_len(nrow(course_summary))) {
  vals <- course_summary$treatment[i, ]
  if (vals["pre"] > 0 & vals["post"] > 0) {
    cat(sprintf("  %s: %d pre, %d post\n",
        course_summary$course_name[i], vals["pre"], vals["post"]))
  }
}

# Ensure correct types
dt$score_vs_par <- as.numeric(dt$score_vs_par)
dt$treatment <- as.numeric(dt$treatment)

# Drop rows with missing score_vs_par
dt <- dt[!is.na(dt$score_vs_par), ]
cat("\nRows after dropping NA scores:", nrow(dt), "\n")

# --- Iterative demeaning for multi-way fixed effects ---
# Absorbs player + course + year FEs via alternating projection
demean_fe <- function(x, fe_list, max_iter = 200, tol = 1e-12) {
  x_dm <- x
  for (iter in 1:max_iter) {
    x_old <- x_dm
    for (fe in fe_list) {
      gm <- tapply(x_dm, fe, mean)
      x_dm <- x_dm - gm[fe]
    }
    if (max(abs(x_dm - x_old)) < tol) break
  }
  cat(sprintf("  Converged in %d iterations\n", iter))
  x_dm
}

cat("\nDemeaning by player + course + year fixed effects...\n")
fe <- list(dt$player, dt$course_name, as.character(dt$year))

score_dm <- demean_fe(dt$score_vs_par, fe)
treatment_dm <- demean_fe(dt$treatment, fe)

# OLS on demeaned data (no intercept -- absorbed by FEs)
fit <- lm(score_dm ~ treatment_dm - 1)
coef_val <- coef(fit)[1]

# --- Clustered standard errors (by player, matches fixest default) ---
resid_vec <- residuals(fit)
X_dm <- as.matrix(treatment_dm)
clusters <- dt$player
unique_cl <- unique(clusters)
G <- length(unique_cl)
n <- nrow(dt)

# Bread: (X'X)^{-1}
XtX_inv <- solve(crossprod(X_dm))

# Meat: sum of cluster-level score outer products
meat <- matrix(0, 1, 1)
for (cl in unique_cl) {
  idx <- clusters == cl
  score_cl <- sum(X_dm[idx] * resid_vec[idx])
  meat <- meat + score_cl^2
}

# Sandwich with small-sample correction
K <- 1
correction <- (G / (G - 1)) * ((n - 1) / (n - K))
vcov_cl <- XtX_inv %*% meat %*% XtX_inv * correction
se_val <- sqrt(vcov_cl[1, 1])

# t-stat and p-value (G-1 degrees of freedom)
t_stat <- coef_val / se_val
p_val <- 2 * pt(abs(t_stat), df = G - 1, lower.tail = FALSE)

cat("\n=== DiD Results ===\n")
cat(sprintf("Dependent variable: score_vs_par (strokes relative to par)\n"))
cat(sprintf("Fixed effects: player + course + year\n"))
cat(sprintf("Clusters (player): %d\n", G))
cat(sprintf("Observations: %d\n", n))
cat(sprintf("\nCoefficient (treatment): %.4f\n", coef_val))
cat(sprintf("Clustered SE:            %.4f\n", se_val))
cat(sprintf("t-statistic:             %.3f\n", t_stat))
cat(sprintf("p-value:                 %.4f\n", p_val))

cat("\n=== Key Finding ===\n")
cat(sprintf("Treatment effect: %.3f strokes (SE: %.3f, p: %.4f)\n",
    coef_val, se_val, p_val))
if (p_val < 0.05) {
  cat("Result: STATISTICALLY SIGNIFICANT at 5% level\n")
  if (coef_val < 0) {
    cat("Direction: EAB IMPROVES golf scores (lower score = better)\n")
  } else {
    cat("Direction: EAB WORSENS golf scores\n")
  }
} else {
  cat("Result: Not statistically significant at 5% level\n")
}
