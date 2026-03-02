import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Ash extinction timeline: literature vs calibrated ──
# Dual-line chart with shaded uncertainty range

ORANGE = "#D55E00"  # literature / treatment
BLUE = "#0072B2"    # calibrated / control

fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

years = extinction_df["year"].values
pct_lit = extinction_df["pct_lit"].values
pct_cal = extinction_df["pct_cal"].values

# Shaded area between curves (uncertainty range)
ax.fill_between(years, pct_lit, pct_cal,
                alpha=0.15, color="#888888", label="Uncertainty range")

# Literature projection (aggressive)
ax.plot(years, pct_lit, color=ORANGE, linewidth=2.5, linestyle="--",
        label="Literature rate (mature canopy trees)", zorder=3)

# Calibrated projection (FIA observed)
ax.plot(years, pct_cal, color=BLUE, linewidth=2.5, linestyle="-",
        label="FIA observed (all size classes)", zorder=3)

# Reference lines at 50% and 10%
ax.axhline(y=50, color="#999", linewidth=0.8, linestyle=":", alpha=0.7)
ax.axhline(y=10, color="#999", linewidth=0.8, linestyle=":", alpha=0.7)
ax.text(2074, 51, "50%", fontsize=9, color="#666", ha="right", va="bottom")
ax.text(2074, 11, "10%", fontsize=9, color="#666", ha="right", va="bottom")

# "Today" vertical line
ax.axvline(x=2026, color="#333", linewidth=1.2, linestyle="-.", alpha=0.6)
ax.text(2026.5, 95, "Today\n(2026)", fontsize=9, color="#333",
        ha="left", va="top")

# Find and annotate 50% crossing points
for pct_col, color, label, offset_y in [
    (pct_lit, ORANGE, "Literature", -6),
    (pct_cal, BLUE, "Calibrated", 4),
]:
    cross_idx = np.where(pct_col <= 50)[0]
    if len(cross_idx) > 0:
        cross_year = years[cross_idx[0]]
        ax.plot(cross_year, 50, "o", color=color, markersize=8, zorder=4)
        ax.annotate(f"50% by {cross_year}",
                    xy=(cross_year, 50),
                    xytext=(cross_year + 3, 50 + offset_y),
                    fontsize=10, fontweight="bold", color=color,
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                    zorder=5)

ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Ash Trees Remaining (%)", fontsize=13)
ax.set_title("US Ash Tree Population Decline Under EAB Spread",
             fontsize=15, fontweight="bold", pad=12)
ax.legend(loc="upper right", fontsize=11, framealpha=0.9)
ax.set_xlim(2002, 2075)
ax.set_ylim(0, 105)
ax.grid(axis="y", alpha=0.3)
ax.set_facecolor("#fafafa")

plt.tight_layout()
plt.savefig("extinction_timeline.png", bbox_inches="tight")
plt.show()

print(f"Extinction timeline: {len(extinction_df)} years plotted")
print(f"  Current (2026): lit={extinction_df[extinction_df['year']==2026]['pct_lit'].values[0]:.1f}%, "
      f"cal={extinction_df[extinction_df['year']==2026]['pct_cal'].values[0]:.1f}%")

# Cleanup for Zerve
del fig, ax, years, pct_lit, pct_cal, cross_idx, cross_year
del ORANGE, BLUE
del color, label, offset_y, pct_col
