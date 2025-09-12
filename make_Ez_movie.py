# Create one Ez-slice PNG per diagnostic dump and
#combine them into an animated GIF (Ez_evolution.gif).

# Requires: openpmd-viewer, matplotlib, numpy, imageio


import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio        # v2 API is stable
from openpmd_viewer import OpenPMDTimeSeries as TS
from pathlib import Path

# ----------------------------------------------------------------------
# 0.  where are the diagnostics?
diag_dir = "diags/diag1"             # change if your folder is elsewhere
ts = TS(diag_dir)

# make a folder for the png frames (optional)
png_dir = Path("Ez_frames")
png_dir.mkdir(exist_ok=True)

frames = []                          # will hold images for the GIF
for idx, it in enumerate(ts.iterations):
    # ------------------------------------------------------------------
    # 1.  get Ez field (1-D) at this iteration
    Ez, meta = ts.get_field("E", "z", iteration=it)
    z_mm = np.linspace(meta.zmin, meta.zmax, Ez.size) * 1e3  # convert to mm

    # 2.  plot
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(z_mm, Ez)
    ax.set_xlabel("z [mm]")
    ax.set_ylabel("Ez [V/m]")
    ax.set_title(f"Ez  –  step {it}   t = {ts.t[idx]*1e9:.2f} ns")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    # 3.  save PNG
    png_name = png_dir / f"Ez_{it:07d}.png"
    fig.savefig(png_name, dpi=120)
    plt.close(fig)                   # free memory

    # 4.  append to GIF frame list
    frames.append(imageio.imread(png_name))

# ----------------------------------------------------------------------
# 5.  write the GIF  (200 ms per frame; adjust as you like)
gif_name = "Ez_evolution.gif"
imageio.mimsave(gif_name, frames, duration=0.2)

print(f"Wrote {len(frames)} PNGs to {png_dir}/ and animation {gif_name}")

