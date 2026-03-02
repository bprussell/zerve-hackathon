# Track A: Parallel trends visualization (DiD)
# Avg score_vs_par by year for EAB vs non-EAB courses
# Upstream: track_a_df from Block 2

library(ggplot2)

dt <- as.data.frame(track_a_df)
dt$score_vs_par <- as.numeric(dt$score_vs_par)
dt$year <- as.integer(dt$year)
dt$eab_county <- as.integer(dt$eab_county)

# Label groups
dt$group <- ifelse(dt$eab_county == 1, "EAB Courses", "Non-EAB Courses")

# Compute annual means by group
agg <- aggregate(score_vs_par ~ year + group, data = dt, FUN = mean)

# Average EAB arrival year for treatment courses (for vertical line)
eab_courses <- dt[dt$eab_county == 1 & !is.na(dt$eab_year), ]
avg_eab_year <- mean(as.numeric(eab_courses$eab_year), na.rm = TRUE)
cat(sprintf("Average EAB arrival year: %.1f\n", avg_eab_year))

# Count obs per group-year
counts <- aggregate(score_vs_par ~ year + group, data = dt, FUN = length)
names(counts)[3] <- "n"

p <- ggplot(agg, aes(x = year, y = score_vs_par, color = group)) +
  geom_line(linewidth = 1.2) +
  geom_point(size = 2.5) +
  geom_vline(xintercept = avg_eab_year, linetype = "dashed",
             color = "#555555", linewidth = 0.8) +
  annotate("text", x = avg_eab_year + 0.3, y = max(agg$score_vs_par),
           label = sprintf("Avg EAB\narrival (%.0f)", avg_eab_year),
           hjust = 0, vjust = 1, size = 3.5, color = "#555555") +
  scale_color_manual(
    values = c("EAB Courses" = "#D55E00", "Non-EAB Courses" = "#0072B2")
  ) +
  labs(
    title = "Golf Scores Before & After Emerald Ash Borer Arrival",
    subtitle = "Average strokes vs par by year (4-round tournament scores)",
    x = "Year",
    y = "Avg Score vs Par (strokes)",
    color = NULL
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 15),
    plot.subtitle = element_text(size = 11, color = "#555555"),
    legend.position = "top",
    panel.grid.minor = element_blank()
  )

print(p)
ggsave("track_a_trend.png", p, width = 10, height = 6, dpi = 150)

cat("\nTrend chart saved.\n")
cat(sprintf("Years: %d-%d\n", min(agg$year), max(agg$year)))
cat(sprintf("EAB course-years: %d, Non-EAB course-years: %d\n",
    sum(counts$n[counts$group == "EAB Courses"]),
    sum(counts$n[counts$group == "Non-EAB Courses"])))
