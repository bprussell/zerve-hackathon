import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── App Page 2: Extinction Timeline (self-contained, no upstream deps) ──
# Reads pre-saved PNG from viz.extinction_timeline block

_img = plt.imread("./extinction_timeline.png")

extinction_fig, _ax = plt.subplots(figsize=(12, 7), dpi=120)
_ax.imshow(_img)
_ax.axis("off")
extinction_fig.patch.set_facecolor("white")
plt.tight_layout(pad=0)

print("Displaying extinction timeline")

del _ax, _img
