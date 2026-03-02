# Track A: Coefficient plot (DiD treatment effect)
# Hardcoded from Block 3 results (console-only output)

library(ggplot2)

# DiD results from Block 3
coef_val <- -0.759
se_val <- 0.245
p_val <- 0.002

# 95% confidence interval
ci_lo <- coef_val - 1.96 * se_val
ci_hi <- coef_val + 1.96 * se_val

cat(sprintf("Treatment effect: %.3f [%.3f, %.3f]\n", coef_val, ci_lo, ci_hi))

# Build data frame for plotting
coef_df <- data.frame(
  term = "EAB Treatment",
  estimate = coef_val,
  ci_low = ci_lo,
  ci_high = ci_hi
)

coef_plot <- ggplot(coef_df, aes(x = estimate, y = term)) +
  # Null hypothesis line
  geom_vline(xintercept = 0, linetype = "dashed",
             color = "#999999", linewidth = 0.8) +
  # CI error bar
  geom_errorbarh(aes(xmin = ci_low, xmax = ci_high),
                 height = 0.15, linewidth = 1.2, color = "#D55E00") +
  # Point estimate
  geom_point(size = 5, color = "#D55E00") +
  # Annotation
  annotate("text",
           x = coef_val, y = 1.35,
           label = sprintf("%.2f strokes  (p = %.3f)", coef_val, p_val),
           size = 5, fontface = "bold", color = "#D55E00") +
  annotate("text",
           x = coef_val, y = 0.65,
           label = sprintf("95%% CI: [%.2f, %.2f]", ci_lo, ci_hi),
           size = 4, color = "#555555") +
  # Labeling
  labs(
    title = "EAB Impact on Golf Scores",
    subtitle = "DiD estimate with player, course, and year fixed effects | Clustered SEs by player",
    x = "Effect on Score vs Par (strokes)",
    y = NULL
  ) +
  scale_x_continuous(limits = c(-1.5, 0.5), breaks = seq(-1.5, 0.5, 0.5)) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    plot.subtitle = element_text(size = 10, color = "#555555"),
    axis.text.y = element_text(size = 13, face = "bold"),
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank()
  )

cat("\nCoefficient plot ready.\n")
cat("The beetle helps your golf game: -0.76 strokes (p = 0.002)\n")
