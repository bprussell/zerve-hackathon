# Track A: Difference-in-Differences Analysis
# Does EAB arrival affect golf scores at PGA Tour courses?
#
# Model: score_vs_par ~ treatment | player + course_name + year
#   - treatment = 1 if course is in EAB county AND year >= EAB arrival
#   - Player FE controls for skill differences
#   - Course FE controls for inherent course difficulty
#   - Year FE controls for league-wide scoring trends
#
# Requires: fixest package

library(fixest)
library(data.table)

# --- Load data ---
df <- fread("data/processed/track_a_analysis.csv")
cat("Loaded", nrow(df), "rows\n")

# Convert types
df[, year := as.factor(year)]
df[, treatment := as.integer(treatment)]
df[, eab_county := as.integer(eab_county)]
df[, post_eab := as.integer(post_eab)]
df[, score_vs_par := as.numeric(score_vs_par)]
df[, n_rounds := as.numeric(n_rounds)]

# Filter to players with 4 rounds (made the cut) for cleaner comparison
df_cut <- df[n_rounds == 4]
cat("After filtering to 4-round scores:", nrow(df_cut), "rows\n")

# --- Summary stats ---
cat("\n--- Sample Composition ---\n")
cat("EAB counties, pre-arrival: ", nrow(df_cut[eab_county == 1 & post_eab == 0]), "\n")
cat("EAB counties, post-arrival:", nrow(df_cut[eab_county == 1 & post_eab == 1]), "\n")
cat("Non-EAB counties:          ", nrow(df_cut[eab_county == 0]), "\n")
cat("Treatment courses:\n")
treatment_courses <- df_cut[eab_county == 1, .(
  pre = sum(post_eab == 0),
  post = sum(post_eab == 1),
  eab_year = eab_year[1]
), by = course_name]
print(treatment_courses[pre > 0 & post > 0])

# --- Model 1: Basic DiD (no fixed effects) ---
cat("\n=== Model 1: Basic DiD ===\n")
m1 <- feols(score_vs_par ~ treatment, data = df_cut)
summary(m1)

# --- Model 2: DiD with course + year FE ---
cat("\n=== Model 2: Course + Year FE ===\n")
m2 <- feols(score_vs_par ~ treatment | course_name + year, data = df_cut)
summary(m2)

# --- Model 3: DiD with player + course + year FE (preferred) ---
cat("\n=== Model 3: Player + Course + Year FE (preferred spec) ===\n")
m3 <- feols(score_vs_par ~ treatment | player + course_name + year, data = df_cut)
summary(m3)

# --- Model 4: Control for number of rounds (robustness) ---
cat("\n=== Model 4: With n_rounds control ===\n")
m4 <- feols(score_vs_par ~ treatment + n_rounds | player + course_name + year, data = df_cut)
summary(m4)

# --- Model 5: Strokes Gained decomposition (ASA data only, 2015+) ---
cat("\n=== Model 5: Strokes Gained Off-the-Tee (most relevant for tree removal) ===\n")
df_sg <- df_cut[sg_ott != "" & !is.na(as.numeric(sg_ott))]
df_sg[, sg_ott_num := as.numeric(sg_ott)]
if (nrow(df_sg) > 0) {
  m5 <- feols(sg_ott_num ~ treatment | player + course_name + year, data = df_sg)
  summary(m5)
  cat("\nInterpretation: SG:OTT measures strokes gained off the tee.\n")
  cat("If EAB tree removal widens fairways, we'd expect POSITIVE coefficient.\n")
} else {
  cat("No strokes gained data available for treatment courses.\n")
}

# --- Comparison table ---
cat("\n=== Model Comparison ===\n")
etable(m1, m2, m3, m4,
       headers = c("Basic", "Course+Year FE", "Player+Course+Year FE", "With Controls"),
       se = "hetero")

# --- Effect size interpretation ---
cat("\n=== Interpretation ===\n")
coef3 <- coef(m3)["treatment"]
se3 <- se(m3)["treatment"]
cat(sprintf("Preferred model (M3) treatment effect: %.3f strokes (SE: %.3f)\n", coef3, se3))
cat(sprintf("95%% CI: [%.3f, %.3f]\n", coef3 - 1.96*se3, coef3 + 1.96*se3))
if (abs(coef3) < 1) {
  cat("Effect is less than 1 stroke over 4 rounds — small in practical terms.\n")
}
pval <- 2 * pnorm(-abs(coef3/se3))
if (pval > 0.05) {
  cat(sprintf("p-value: %.4f — NOT statistically significant at 5%% level.\n", pval))
  cat("Conclusion: EAB does NOT appear to improve your golf game.\n")
} else {
  cat(sprintf("p-value: %.4f — Statistically significant at 5%% level.\n", pval))
  if (coef3 < 0) {
    cat("Conclusion: Scores IMPROVE (lower) after EAB — the beetle helps!\n")
  } else {
    cat("Conclusion: Scores WORSEN (higher) after EAB — the beetle hurts!\n")
  }
}
