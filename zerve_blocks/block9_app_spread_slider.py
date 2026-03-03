import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── EAB Spread Map — Fast file-based frame lookup ──
# selected_year comes from the Input block (slider 2002-2022)
# Frames pre-rendered to ./frames/ by app.prerender_frames (run once, no DAG link)

try:
    _yr = int(selected_year)
except NameError:
    _yr = 2022

# Clamp to valid range
_yr = max(2002, min(2022, _yr))

# Read the pre-rendered PNG from disk
_img = plt.imread(f"./frames/{_yr}.png")

# Display
spread_map_fig, _ax = plt.subplots(figsize=(12, 7), dpi=100)
_ax.imshow(_img)
_ax.axis("off")
spread_map_fig.patch.set_facecolor("#1D1D20")
plt.tight_layout(pad=0)

print(f"Displaying frame for {_yr}")

del _ax, _img, _yr
