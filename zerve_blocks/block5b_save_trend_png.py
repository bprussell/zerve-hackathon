import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Save trend plot PNG from R's aggregated data ──
# Upstream: trend_data (dataframe with year, group, score_vs_par) from viz.track_a_trend

ORANGE = "#D55E00"
BLUE = "#0072B2"

eab = trend_data[trend_data["group"] == "EAB Courses"].sort_values("year")
non_eab = trend_data[trend_data["group"] == "Non-EAB Courses"].sort_values("year")

# Average EAB arrival year (hardcoded — same as R block)
avg_eab_arrival = 2010.9

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

ax.plot(eab["year"], eab["score_vs_par"], color=ORANGE, linewidth=2,
        marker="o", markersize=6, label="EAB Courses", zorder=3)
ax.plot(non_eab["year"], non_eab["score_vs_par"], color=BLUE, linewidth=2,
        marker="o", markersize=6, label="Non-EAB Courses", zorder=3)

ax.axvline(x=avg_eab_arrival, linestyle="--", color="#555555", linewidth=1)
ax.text(avg_eab_arrival + 0.3, ax.get_ylim()[1] * 0.95,
        f"Avg EAB\narrival ({avg_eab_arrival:.0f})",
        fontsize=9, color="#555555", ha="left", va="top")

ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Avg Score vs Par (strokes)", fontsize=13)
fig.suptitle("Golf Scores Before & After Emerald Ash Borer Arrival",
             fontsize=15, fontweight="bold", y=0.97)
ax.set_title("Average strokes vs par by year (4-round tournament scores)",
             fontsize=11, color="#555555", pad=12)
ax.legend(loc="upper left", fontsize=11, framealpha=0.9)
ax.grid(axis="y", alpha=0.3)
ax.set_facecolor("#fafafa")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("track_a_trend.png", bbox_inches="tight")
plt.show()

print("Saved track_a_trend.png")

del fig, ax, eab, non_eab, avg_eab_arrival, ORANGE, BLUE
