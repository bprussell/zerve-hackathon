import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Track A: Parallel trends (DiD) ──
# Upstream: track_a_df from Block 2

ORANGE = "#D55E00"  # EAB courses
BLUE = "#0072B2"    # Non-EAB courses

dt = track_a_df.copy()
dt["score_vs_par"] = dt["score_vs_par"].astype(float)
dt["year"] = dt["year"].astype(int)
dt["eab_county"] = dt["eab_county"].astype(int)

# Annual means by group
eab = dt[dt["eab_county"] == 1].groupby("year")["score_vs_par"].mean()
non_eab = dt[dt["eab_county"] == 0].groupby("year")["score_vs_par"].mean()

# Average EAB arrival year for treatment courses
eab_courses = dt[(dt["eab_county"] == 1) & (dt["eab_year"].notna())]
avg_eab_year = eab_courses["eab_year"].astype(float).mean()
print(f"Average EAB arrival year: {avg_eab_year:.1f}")

# Counts
eab_n = dt[dt["eab_county"] == 1].shape[0]
non_eab_n = dt[dt["eab_county"] == 0].shape[0]

fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

ax.plot(eab.index, eab.values, color=ORANGE, linewidth=2, marker="o",
        markersize=6, label="EAB Courses", zorder=3)
ax.plot(non_eab.index, non_eab.values, color=BLUE, linewidth=2, marker="o",
        markersize=6, label="Non-EAB Courses", zorder=3)

# Vertical line at avg EAB arrival
ax.axvline(x=avg_eab_year, linestyle="--", color="#555555", linewidth=1)
ax.text(avg_eab_year + 0.3, ax.get_ylim()[1] * 0.95,
        f"Avg EAB\narrival ({avg_eab_year:.0f})",
        fontsize=9, color="#555555", ha="left", va="top")

ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Avg Score vs Par (strokes)", fontsize=13)
fig.suptitle("Golf Scores Before & After Emerald Ash Borer Arrival",
             fontsize=15, fontweight="bold", y=0.97)
ax.set_title("Average strokes vs par by year (4-round tournament scores)",
             fontsize=11, color="#555555", pad=12)
ax.legend(loc="upper right", fontsize=11, framealpha=0.9)
ax.grid(axis="y", alpha=0.3)
ax.set_facecolor("#fafafa")

plt.tight_layout()
plt.savefig("track_a_trend.png", bbox_inches="tight")
plt.show()

print(f"\nTrend chart saved.")
print(f"Years: {eab.index.min()}-{eab.index.max()}")
print(f"EAB course-years: {eab_n}, Non-EAB course-years: {non_eab_n}")

del fig, ax, dt, eab, non_eab, eab_courses, avg_eab_year, eab_n, non_eab_n
del ORANGE, BLUE
