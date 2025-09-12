#!/usr/bin/env python3
"""
Plots:  (1) number of electrons reaching z_hi vs. iteration
        (2) kinetic-energy PDF of those electrons
"""
import glob, numpy as np, matplotlib.pyplot as plt
from openpmd_viewer import OpenPMDTimeSeries

# ---- locate scrape files ----------------------------------------------------
scrape_dir = "diags/diag_scrape/particles_at_zhi"
series     = OpenPMDTimeSeries(scrape_dir, species='electron')

# ---- time evolution of escaping electron number -----------------------------
steps  = series.iterations
counts = []

for it in steps:
    q, m, w = series.get_particle(it, species='electron', var_list=['weighting'])
    counts.append(w.sum())        # total physical electrons at this dump

plt.figure()
plt.plot(steps, counts, marker='o')
plt.xlabel('PIC iteration')
plt.ylabel('electrons escaping @ z_hi')
plt.title('Electron flux at sheath edge')
plt.tight_layout()
plt.savefig('flux_vs_time.png')

# ---- energy spectrum at final dump -----------------------------------------
last_it = steps[-1]
ux, uy, uz, w = series.get_particle(
    last_it, species='electron',
    var_list=['ux','uy','uz','weighting'])

gamma = np.sqrt(1 + ux**2 + uy**2 + uz**2)
ke_eV = (gamma - 1) * 511e3                 # ΔE = (γ−1)m_ec²  [eV]

plt.figure()
plt.hist(ke_eV, bins=120, weights=w, density=False)
plt.yscale('log')
plt.xlabel('Kinetic energy [eV]')
plt.ylabel('electron count')
plt.title(f'Escaping electrons (iter {last_it})')
plt.tight_layout()
plt.savefig('energy_hist.png')
print("Wrote flux_vs_time.png  and  energy_hist.png")

