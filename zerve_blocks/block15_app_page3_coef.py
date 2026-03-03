import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── App Page 3: DiD Coefficient Plot (reads pre-saved PNG) ──
# No upstream dependencies — reads file saved by viz.track_a_coef block

_img = plt.imread("./track_a_coef.png")

coef_fig, _ax = plt.subplots(figsize=(12, 7), dpi=120)
_ax.imshow(_img)
_ax.axis("off")
coef_fig.patch.set_facecolor("white")
plt.tight_layout(pad=0)

print("Displaying coefficient plot")

del _ax, _img
