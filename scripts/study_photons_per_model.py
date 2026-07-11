r"""
How many photons does each model need? Sufficient-N study across every
configuration family — NA, Gaussian apodization α_t, annular ε, axicon β.

For each configuration we run an N-ladder, compute RMS(MC − deterministic) over a
fixed x–z slice (scalar MC vs scalar Debye with the matching pupil), and read off
the photon count for 1% and 0.5% RMS. Because RMS ∝ 1/√N in the asymptotic
regime, N(target) = N·(RMS/target)² extrapolates the requirement from the
largest-N point.

Takeaway pattern: smooth/low-NA pupils are cheap; structure that creates deep
zeros and phase cancellation (high NA, strong annulus, axicon) costs more photons.

NA family is uniform; the α_t / ε / β families are at NA=0.8. λ_c=750 nm, n=1.3.
Output: output/06_monte_carlo/photons_per_model.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons, coherent_intensity
from mcdo.apodization import gaussian, axicon

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 8.5, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

LAM, N_MED, NT = 0.750, 1.3, 801
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
NS = np.array([1000, 3000, 10000, 30000, 100000])
x = np.linspace(-1.2, 1.2, 51)
z = np.linspace(-3.0, 3.0, 51)
Z, X = np.meshgrid(z, x, indexing='ij'); Y = np.zeros_like(X)


def annular_apod(eps, sin_alpha):
    th_in = np.arcsin(eps * sin_alpha)
    def A(theta):
        return (np.asarray(theta, dtype=float) >= th_in).astype(float)
    return A


def rms_curve(cfg, apod):
    """RMS(MC, deterministic) over the x–z slice for each N in the ladder."""
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, NT, apodization=apod)
    ref = ref / ref.max()
    out = []
    for N in NS:
        kx, ky, kz, w = sample_photons(cfg, int(N), apod=apod,
                                       rng=np.random.default_rng(0))
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I = I / I.max()
        out.append(np.sqrt(np.mean((I - ref) ** 2)))
    return np.array(out)


def n_for(rms, target):
    """Photons for `target` RMS, via the 1/√N law from the largest-N point."""
    return NS[-1] * (rms[-1] / target) ** 2


# families: (title, parameter label, [(value, cfg, apod), ...])
def cfg08():
    return SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=NT)

families = {}
families['NA (uniform)'] = ('NA', [
    (na, SimConfig(lam_c=LAM, X_NA=na, n=N_MED, N_theta=NT), None)
    for na in (0.1, 0.3, 0.5, 0.8, 1.0, 1.2)])
families['Gaussian α_t (NA=0.8)'] = ('α_t', [
    (at, cfg08(), (None if at == 0 else gaussian(at, cfg08().sin2_alpha)))
    for at in (0, 1, 2, 3, 4)])
families['annular ε (NA=0.8)'] = ('ε', [
    (ep, cfg08(), (None if ep == 0 else annular_apod(ep, cfg08().sin_alpha)))
    for ep in (0.0, 0.5, 0.7, 0.9, 0.99)])
families['axicon β (NA=0.8)'] = ('β', [
    (be, cfg08(), (None if be == 0 else axicon(be, cfg08().sin_alpha)))
    for be in (0, 5, 10, 20, 40)])

fig, axes = plt.subplots(2, 2, figsize=(14, 9.5))
fig.suptitle('Photons needed per model — RMS(MC − deterministic) vs N '
             '(λ_c=750 nm, n=1.3)', fontsize=14)
summary = {}
for ax, (fam, (plabel, items)) in zip(axes.ravel(), families.items()):
    cols = plt.cm.viridis(np.linspace(0, 0.85, len(items)))
    rows = []
    for (val, cfg, apod), c in zip(items, cols):
        rms = rms_curve(cfg, apod)
        n1, n05 = n_for(rms, 0.01), n_for(rms, 0.005)
        rows.append((val, n1, n05))
        ax.loglog(NS, rms, 'o-', color=c, ms=5, lw=1.5,
                  label=f'{plabel}={val:g}  (N₁%≈{n1:,.0f})')
    ax.axhline(0.01, color='0.4', ls='--', lw=0.9)
    ax.text(NS[0], 0.0105, '1% RMS', color='0.4', fontsize=8, va='bottom')
    ax.axhline(0.005, color='0.4', ls=':', lw=0.9)
    ax.set_xlabel('N photons'); ax.set_ylabel('RMS vs deterministic')
    ax.set_title(fam); ax.legend()
    summary[fam] = (plabel, rows)

plt.tight_layout()
out = os.path.join(OUT, 'photons_per_model.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)

print("Photons needed per model (extrapolated via RMS ∝ 1/√N):\n")
for fam, (plabel, rows) in summary.items():
    print(f"{fam}:")
    print(f"   {plabel:>6} {'N(1%)':>12} {'N(0.5%)':>12}")
    for val, n1, n05 in rows:
        print(f"   {val:>6g} {n1:>12,.0f} {n05:>12,.0f}")
    print()
print(f"Saved → {out}")
