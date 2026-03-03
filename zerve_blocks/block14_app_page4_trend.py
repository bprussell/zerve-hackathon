import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── App Page 4: Parallel Trends (reads pre-saved PNG) ──
# No upstream dependencies — reads file saved by viz.track_a_trend block

_img = plt.imread("./track_a_trend.png")

trend_fig, _ax = plt.subplots(figsize=(12, 7), dpi=120)
_ax.imshow(_img)
_ax.axis("off")
trend_fig.patch.set_facecolor("white")
plt.tight_layout(pad=0)

print("Displaying parallel trends plot")

del _ax, _img
