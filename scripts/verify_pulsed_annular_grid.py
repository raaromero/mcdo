r"""
Goal-1 sweep: optical pulses through an annulus, across aperture and input.

The existing pulsed-annular scripts each fix one numerical aperture (0.8).
This one runs the full grid the depth-of-focus question actually needs:

    numerical aperture  0.1 (low)  and  1.2 (high)
    input               uniform    and  Gaussian, truncation coefficient 4
    obstruction ratio   0, 0.5, 0.99
    pulse duration      continuous wave, 2 fs, 1 fs

and reports, for every cell, the transverse focal width, the depth of focus,
and the depth-of-focus gain over that cell's own unobstructed reference.

The question it answers: the ring's depth-of-focus gain is bandwidth invariant
at numerical aperture 0.8 for uniform light and erodes slightly for Gaussian.
Does that still hold at low and high aperture?

Physics reuses mcdo.annular.compute_integrals_annular (field-level Babinet, so
coherent cross terms survive) and mcdo.components.full (total intensity of all
three components). Nothing is recomputed here that the package already does.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 501, 201
ALPHA_T = 4.0
NA_CASES = [0.1, 1.2]
EPS = [0.0, 0.5, 0.99]
TAUS = [(np.inf, 'continuous wave'), (2e-15, '2 fs'), (1e-15, '1 fs')]
INPUTS = ['uniform', 'Gaussian, truncation coefficient 4']

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)


def _fwhm(x, y):
    """Full width at half maximum of a profile sampled from its peak outward."""
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


def _profile(cfg, eps, apod, tau, coords, axis):
    """Transverse or axial profile, continuous-wave or pulsed, total intensity."""
    r = coords if axis == 'r' else np.array([0.0])
    z = np.array([0.0]) if axis == 'r' else coords

    def _one(k):
        I0, I1, I2 = compute_integrals_annular(r, z, k, cfg.alpha, eps, NT,
                                               apodization=apod)
        return (vec_intensity(I0[0], I1[0], I2[0]) if axis == 'r'
                else vec_intensity(I0[:, 0], I1[:, 0], I2[:, 0]))

    if not np.isfinite(tau):
        return _one(cfg.k_c)

    omegas = cfg.omega_grid()
    weights = cfg.spectral_power(omegas)
    total = np.zeros(len(coords))
    for omega, w in zip(omegas, weights):
        if omega <= 0:
            continue
        total += w * _one(cfg.k_for_omega(omega))
    return total


rows = []
print(f"{'NA':>5} {'input':<38} {'eps':>5} {'pulse':<17} "
      f"{'width nm':>9} {'depth um':>9} {'gain':>6}")

for xna in NA_CASES:
    # windows scale with aperture: the focus is ~lambda/NA wide, ~lambda/NA^2 long
    r_arr = np.linspace(0.0, 3.0 * LAM / xna, 500)
    # 1/(1-eps^2) diverges as the ring thins, so it cannot size the window on
    # its own: at eps = 0.99 it asks for centimetres, and a fixed point count
    # then samples far coarser than the axial structure. Hold the sampling step
    # fixed instead and grow the window until the profile actually crosses half.
    dz = 0.05 * LAM / xna ** 2          # step, not span: resolution stays fixed
    z_span = {e: 12.0 * LAM / xna ** 2 * min(1.0 / (1.0 - e ** 2), 60.0)
              for e in EPS}
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=NFREQ, N_theta=NT)
    for label in INPUTS:
        apod = None if label == 'uniform' else gaussian(ALPHA_T, cfg.sin2_alpha)
        for tau, tlab in TAUS:
            c = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=tau,
                          N_freq=NFREQ, N_theta=NT)
            base_depth = None
            for eps in EPS:
                span = z_span[eps]
                for _attempt in range(4):
                    z_arr = np.arange(0.0, span, dz)
                    d = _fwhm(z_arr, _profile(c, eps, apod, tau, z_arr, 'z'))
                    if np.isfinite(d) and d < 1.8 * span:
                        break          # a crossing well inside the window
                    span *= 2.0        # otherwise the window was the limit
                else:
                    d = np.nan         # report nothing rather than the edge
                w = _fwhm(r_arr, _profile(c, eps, apod, tau, r_arr, 'r')) * 1000.0
                if eps == 0.0:
                    base_depth = d
                gain = d / base_depth
                rows.append(dict(na=xna, input=label, eps=eps, tau=tlab,
                                 width_nm=w, depth_um=d, gain=gain))
                print(f"{xna:>5.1f} {label:<38} {eps:>5.2f} {tlab:<17} "
                      f"{w:>9.1f} {d:>9.3f} {gain:>6.2f}")

np.savez(os.path.join(OUT, 'pulsed_annular_grid.npz'),
         **{k: np.array([r[k] for r in rows]) for k in rows[0]})

# ── figure: depth-of-focus gain against pulse duration, one panel per cell ──
fig, axes = plt.subplots(2, 2, figsize=(20.5, 13.0))
COLOR = {0.0: '#1f77b4', 0.5: '#d62728', 0.99: '#2ca02c'}
x = np.arange(len(TAUS))
for i, xna in enumerate(NA_CASES):
    for j, label in enumerate(INPUTS):
        ax = axes[i, j]
        for eps in EPS:
            g = [next(r['gain'] for r in rows
                      if r['na'] == xna and r['input'] == label
                      and r['eps'] == eps and r['tau'] == t[1]) for t in TAUS]
            ax.plot(x, g, 'o-', color=COLOR[eps], lw=2.0, ms=7,
                    label=f'obstruction ratio {eps:g}')
        ax.set_xticks(x)
        ax.set_xticklabels([t[1] for t in TAUS])
        ax.set_yscale('log')
        ax.set_xlabel('Pulse duration')
        ax.set_ylabel('Depth-of-focus gain over the full disk')
        short = 'uniform' if label == 'uniform' else 'Gaussian, coefficient 4'
        ax.set_title(f'Numerical aperture {xna:g}, {short} input, 750 nm',
                     fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'pulsed_annular_grid')
out = os.path.join(OUT, 'pulsed_annular_grid.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")

# ── what changes with bandwidth, stated as a number per cell ───────────────
print("\nBandwidth sensitivity of the gain (1 fs against continuous wave):")
for xna in NA_CASES:
    for label in INPUTS:
        for eps in [0.5, 0.99]:
            def _g(t):
                return next(r['gain'] for r in rows if r['na'] == xna
                            and r['input'] == label and r['eps'] == eps
                            and r['tau'] == t)
            cw, fs1 = _g('continuous wave'), _g('1 fs')
            print(f"  NA {xna:>3}  {label:<38} eps {eps:<5} "
                  f"{cw:>7.2f} -> {fs1:>7.2f}  ({100*(fs1/cw-1):+5.1f}%)")
