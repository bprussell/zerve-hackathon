import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── App Page 4: Static Spread Map (reads pre-saved PNG) ──
# No upstream dependencies — reads file saved by viz.spread_map block

_img = plt.imread("./spread_map.png")

static_map_fig, _ax = plt.subplots(figsize=(12, 7), dpi=120)
_ax.imshow(_img)
_ax.axis("off")
static_map_fig.patch.set_facecolor("white")
plt.tight_layout(pad=0)

print("Displaying static spread map")

del _ax, _img
