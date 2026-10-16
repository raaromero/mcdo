r"""Cambaliza & Saloma (2000) Fig. 8: axial 2PE and 2CE through a scattering slab, θ = π (Monte Carlo).

Method of Blanca & Saloma, Appl. Opt. 37 (1998) 8092: geometric photons of a focused Gaussian beam, Henyey-Greenstein
scattering (g = 0.9), free paths d = −d_s ln ξ, at most 40 scattering events; the axial excitation at depth z′ is
I(z′) = N_E(z′) w₀² / (N_e w²(z′)), with N_E the photons crossing the plane z′ inside the unscattered beam radius w(z′).
2PE: (I₁ + I₂)²; 2CE: I₁ I₂ (interference neglected, as in the paper).

Not stated in the paper (assumptions):
  slab −h ≤ z ≤ h, focus at its centre, h = 100 µm (H_UM; scan of 20–1000 µm: 100 µm gives the paper's narrow
  peak and low 2CE background; 20 µm gives a broad pedestal, 1 mm no background); plotted and counted over |z| ≤ 20 µm;
  d_s ∝ λ² (g = 0.9 case of Blanca & Saloma 1998: h/d_s = 4 at λ/2 ↔ 1 at λ), h/d_s = 8 at λ_2p = 0.7 µm;
  Gaussian waist w₀ = λ / (π NA), NA 0.5 (NA_ for other NA: plane spacing scaled by (0.5/NA)²), n = 1.
Each beam: 10 trials × 10⁶ photons (10⁷, as in the paper); per-trial profiles saved.

    [H_UM=100] [NA_=0.5] python scripts/replicate_cambaliza2000_fig8.py [--rerun]
    -> output/08_two_color/cambaliza2000/fig8_mc_h<h>.npz, panels/fig8{a,b}.png (h = 100), panels/h<h>/fig8{a,b}.png;
       NA ≠ 0.5: fig8_mc_h<h>_na<NA>.npz, panels/h<h>_na<NA>/
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.scatter import hg_sample, rotate

_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
G, HDS, LREF, MAXS = 0.9, 8.0, 0.700, 40
NA = float(os.environ.get('NA_', 0.5))
H = float(os.environ.get('H_UM', 100.0))                  # slab half-thickness h (µm)
TAG = f'h{H:g}' + ('' if NA == 0.5 else f'_na{NA:g}')
PAN = os.path.join(OUT, 'panels', *(() if TAG == 'h100' else (TAG,)))     # other h, NA: backup panels in panels/<tag>/
os.makedirs(PAN, exist_ok=True)
N_PH, N_TR = 1_000_000, 10
DZ = 0.25 * min(1.0, (0.5 / NA) ** 2)                    # plane spacing: resolves the focus at every NA
ZP = np.arange(-20.0, 20.0 + DZ / 2, DZ)                # counting planes (µm): the plotted range


def waist(lam):
    return lam / (np.pi * NA)


def w_of_z(lam, z):
    w0 = waist(lam)
    return w0 * np.sqrt(1 + (z * lam / (np.pi * w0 ** 2)) ** 2)


def trial(lam, rng):
    """Axial excitation I(z′) of one beam entering at z = −h and focused at z = 0 (one trial of N_PH photons)."""
    ds = (H / HDS) * (lam / LREF) ** 2
    w0 = waist(lam); th0 = lam / (np.pi * w0)
    x0, y0 = rng.normal(0, w0 / 2, (2, N_PH))          # Gaussian beam: waist position and ray angle independent
    tx, ty = rng.normal(0, th0 / 2, (2, N_PH))
    pos = np.vstack((x0 - tx * H, y0 - ty * H, np.full(N_PH, -H)))
    mu = np.vstack((tx, ty, np.ones(N_PH))); mu /= np.linalg.norm(mu, axis=0)
    w2 = w_of_z(lam, ZP) ** 2
    count = np.zeros(ZP.size)
    alive = np.ones(N_PH, bool)
    for k in range(MAXS + 1):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        p, m = pos[:, idx], mu[:, idx]
        d = -ds * np.log(rng.random(idx.size))
        q = p + d * m
        out = (q[2] < -H) | (q[2] > H)                  # leaves the slab: stop at the face
        tz = np.where(m[2] > 0, (H - p[2]) / np.where(m[2] == 0, 1, m[2]), (-H - p[2]) / np.where(m[2] == 0, 1, m[2]))
        q[:, out] = p[:, out] + tz[out] * m[:, out]
        za, zb = p[2], q[2]
        lo = np.ceil((np.minimum(za, zb) - ZP[0]) / DZ - 1e-9).astype(int)
        hi = np.floor((np.maximum(za, zb) - ZP[0]) / DZ + 1e-9).astype(int)
        hi = np.minimum(hi, ZP.size - 1); lo = np.maximum(lo, 0)
        nc = np.maximum(hi - lo + 1, 0)
        start = np.zeros(idx.size, bool)
        if k > 0:                                        # a plane at the start point was counted on the previous step
            on = np.abs((za - ZP[0]) / DZ - np.round((za - ZP[0]) / DZ)) < 1e-9
            start = on
        seg = np.repeat(np.arange(idx.size), nc)
        j = lo[seg] + (np.arange(seg.size) - np.repeat(np.cumsum(nc) - nc, nc))
        dz = (zb - za)[seg]
        t = np.where(dz == 0, 0.0, (ZP[j] - za[seg]) / np.where(dz == 0, 1, dz))
        x = p[0, seg] + t * (q[0, seg] - p[0, seg]); y = p[1, seg] + t * (q[1, seg] - p[1, seg])
        keep = (x * x + y * y < w2[j]) & ~(start[seg] & (np.abs(ZP[j] - za[seg]) < 1e-9))
        count += np.bincount(j[keep], minlength=ZP.size)
        pos[:, idx] = q
        alive[idx[out]] = False
        if k == MAXS:
            break
        sc = idx[~out]
        c, ph = hg_sample(G, sc.size, rng)
        mu[:, sc] = rotate(mu[:, sc], c, ph)
    return count / N_PH * w0 ** 2 / w2


def run():
    rng = np.random.default_rng(20001)
    res = {}
    for key, lam in (('2p_a', 0.700), ('2p_b', 0.700), ('l1', 0.750), ('l2', 0.656)):
        t0 = time.time()
        res[key] = np.array([trial(lam, rng) for _ in range(N_TR)])
        print(f'{key} λ = {lam} µm: {time.time() - t0:.0f} s', flush=True)
    np.savez(os.path.join(OUT, f'fig8_mc_{TAG}.npz'), z=ZP, **res, h=H, h_ds=HDS, g=G, na=NA, n_photons=N_PH)
    return res


def ref(lam):
    """Unscattered axial excitation of a Gaussian beam, I ∝ w₀²/w²(z)."""
    return (waist(lam) / w_of_z(lam, ZP)) ** 2


if __name__ == '__main__':
    path = os.path.join(OUT, f'fig8_mc_{TAG}.npz')
    R = dict(np.load(path)) if os.path.exists(path) and '--rerun' not in sys.argv else run()
    z = ZP
    m = {k: R[k].mean(0) for k in ('2p_a', '2p_b', 'l1', 'l2')}
    E1, E2 = m['2p_a'], m['2p_b'][::-1]                 # beam from L2 (θ = π) enters at z = +h
    C1, C2 = m['l1'], m['l2'][::-1]
    F2p = (E1 + E2) ** 2; F2c = C1 * C2
    r2p = (ref(0.7) + ref(0.7)[::-1]) ** 2; r2c = ref(0.75) * ref(0.656)[::-1]
    nz = lambda v: v / v.max()
    BOX = {'fig8a': 503 / 258, 'fig8b': 503 / 265}            # plot boxes of the original panels (pixels)
    for key, title, exc, F, Fr, labs in (
            ('fig8a', '2PE', (E1, E2), F2p, r2p, ('Excitation, θ = 0', 'Excitation, θ = π')),
            ('fig8b', '2CE', (C1, C2), F2c, r2c, ('Excitation, λ₁', 'Excitation, λ₂'))):
        fig, ax = plt.subplots(figsize=(9, 9 / BOX[key] + 2.5)); ax.set_box_aspect(1 / BOX[key])
        for e, ls, lab in zip(exc, ('-.', ':'), labs):
            ax.plot(z, nz(e), ls, color='#555555', lw=2.5, label=lab)
        ax.plot(z, nz(Fr), '-', color='k', lw=3, label='No scattering')
        k = max(1, round(0.5 / DZ))                                  # markers 0.5 µm apart
        ax.plot(z[::k], nz(F)[::k], 'o', mfc='none', mec='#1f77b4', mew=2, ms=9, label='Fluorescence')
        ax.set_xlim(-20, 20); ax.set_ylim(0, 1); ax.set_xticks(np.arange(-20, 21, 5))
        ax.set_xlabel('z (µm)'); ax.set_ylabel('Intensity'); ax.tick_params(axis='x', pad=12)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125 * BOX[key] - 0.08), ncol=2, frameon=False)
        fig.savefig(os.path.join(PAN, f'{key}.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
        print('Saved ->', key)
    sd = lambda k: R[k].std(0)
    i0 = np.argmin(np.abs(z))
    for k in ('2p_a', 'l1', 'l2'):
        print(f'{k}: I(0) = {m[k][i0]:.3e} ± {sd(k)[i0]:.1e}; I(0)/max = {m[k][i0] / m[k].max():.3f}; '
              f'ballistic e^(-h/d_s) = {np.exp(-HDS * (LREF / {"2p_a": .7, "l1": .75, "l2": .656}[k]) ** 2):.2e}')
    far = np.abs(z) > 10
    print(f'out-of-focus fluorescence (|z| > 10 µm), mean of normalized: 2PE {nz(F2p)[far].mean():.3f}, 2CE {nz(F2c)[far].mean():.4f}')
