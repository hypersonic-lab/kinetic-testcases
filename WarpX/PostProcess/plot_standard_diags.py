#!/usr/bin/env python3
"""
Quick-look plots for the default WarpX diagnostic in diags/diag1
  (1) Ez field snapshot
  (2) charge density rho
  (3) z-pz phase space of electrons
Produces: Ez.png , rho.png , phase_space.png
"""

import matplotlib.pyplot as plt
from openpmd_viewer import OpenPMDTimeSeries as TS
import numpy as np

ts = TS("diags/diag1")           # <-- top-level folder

## Pick the last recorded iteration
idx = -1
it = ts.iterations[idx]
t  = ts.t[idx]                    # physical time (s)


# -------- 1. Ez field snapshot --------------------------------------------
# For 1-D: returns 1-D array (z-axis)
# For ≥2-D: returns 2-D slice; you can pick slice normal if needed
Ez, meta = ts.get_field("E", "z", it)   # cartesian component

plt.figure()
if Ez.ndim == 1:
    z = np.linspace(meta.zmin, meta.zmax, Ez.size)
    plt.plot(z*1e3, Ez)                 # mm if you like
    plt.xlabel("z [mm]")
    plt.ylabel("Ez [V/m]")
else:
    extent = [meta.zmin*1e3, meta.zmax*1e3,
              meta.ymin*1e3, meta.ymax*1e3]
    plt.imshow(Ez.T, extent=extent, origin='lower', aspect='auto')
    plt.xlabel("z [mm]"); plt.ylabel("y [mm]")
    plt.colorbar(label="Ez [V/m]")
plt.title(f"Ez at t = {t*1e9:.2f} ns")
plt.tight_layout(); plt.savefig("Ez.png")

# -------- 2. Charge density rho -------------------------------------------
rho, meta = ts.get_field("rho", iteration=it, species="electron")
plt.figure()
if rho.ndim == 1:
    z = np.linspace(meta.zmin, meta.zmax, rho.size)
    plt.plot(z*1e3, rho)
    plt.xlabel("z [mm]"); plt.ylabel("rho [C/m³]")
else:
    extent = [meta.zmin*1e3, meta.zmax*1e3,
              meta.ymin*1e3, meta.ymax*1e3]
    plt.imshow(rho.T, extent=extent, origin='lower', aspect='auto')
    plt.xlabel("z [mm]"); plt.ylabel("y [mm]")
    plt.colorbar(label="rho [C/m³]")
plt.title(f"Electron charge density at t = {t*1e9:.2f} ns")
plt.tight_layout(); plt.savefig("rho.png")

# -------- 3. z-pz phase space of electrons --------------------------------
z, uz, w = ts.get_particle(["z", "uz", "w"], iteration =it, species="electron")
                         
pz = uz * 511e3                     # approx MeV/c (unit-momentum × m_e·c)

plt.figure()
plt.hist2d(z*1e3, pz, bins=200, weights=w,
           norm='log', cmap='viridis')
plt.xlabel("z [mm]"); plt.ylabel("pz [keV/c]")
plt.colorbar(label="log₁₀(count)")
plt.title("Electron phase space")
plt.tight_layout(); plt.savefig("phase_space.png")

print("Wrote Ez.png, rho.png, phase_space.png")
