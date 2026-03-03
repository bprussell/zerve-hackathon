import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Track A: Coefficient plot (DiD treatment effect) ──
# Hardcoded from Block 3 results

ORANGE = "#D55E00"

coef_val = -0.759
se_val = 0.245
p_val = 0.002

ci_lo = coef_val - 1.96 * se_val
ci_hi = coef_val + 1.96 * se_val

print(f"Treatment effect: {coef_val:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]")

fig, ax = plt.subplots(figsize=(9, 3.5), dpi=120)

# Null hypothesis line
ax.axvline(x=0, linestyle="--", color="#999999", linewidth=1)

# CI error bar (horizontal)
ax.errorbar(x=coef_val, y=0, xerr=[[coef_val - ci_lo], [ci_hi - coef_val]],
            fmt="o", color=ORANGE, markersize=10, capsize=6,
            elinewidth=2.5, capthick=2, zorder=3)

# Annotations
ax.text(coef_val, 0.25,
        f"{coef_val:.2f} strokes  (p = {p_val:.3f})",
        fontsize=12, fontweight="bold", color=ORANGE, ha="center")
ax.text(coef_val, -0.25,
        f"95% CI: [{ci_lo:.2f}, {ci_hi:.2f}]",
        fontsize=10, color="#555555", ha="center")

ax.set_xlim(-1.5, 0.5)
ax.set_ylim(-0.6, 0.6)
ax.set_yticks([0])
ax.set_yticklabels(["EAB Treatment"], fontsize=13, fontweight="bold")
ax.set_xlabel("Effect on Score vs Par (strokes)", fontsize=13)
fig.suptitle("EAB Impact on Golf Scores", fontsize=16, fontweight="bold", y=1.02)
ax.set_title("DiD estimate with player, course, and year fixed effects | Clustered SEs by player",
             fontsize=10, color="#555555", pad=12)
ax.grid(axis="x", alpha=0.3)
ax.set_facecolor("#fafafa")

# Remove top/right spines and y gridlines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="y", length=0)

plt.tight_layout()
plt.savefig("track_a_coef.png", bbox_inches="tight")
plt.show()

print("\nCoefficient plot saved.")
print(f"The beetle helps your golf game: {coef_val:.2f} strokes (p = {p_val:.3f})")

del fig, ax, coef_val, se_val, p_val, ci_lo, ci_hi, ORANGE
