r"""Linfoot fidelity, structural content and correlation quality over the offset
of O′ (Lim & Saloma's Figs. 5–6), as a function of NA; vector (Richards–Wolf)
against Lim & Saloma's paraxial scalar model at every NA.

Maps are on offsets in spot units, so different NAs compare directly:
    2CE, θ = π:    x̃ = x_c / (λ/NA),    z̃ = z_c / (nλ/NA²)
    2CE, θ = π/2:  x̃ = x_c / (nλ/NA²),  z̃ = z_c / (λ/NA)   (x_c slides beam 2 along
                   its own length, z_c across its width)
    2PE:           along a fringe direction the unit is λ/n instead (z at θ = π,
                   both at θ = π/2), since the standing-wave fringes, period λ/2n,
                   set F there; offsets ±1 λ/n in 41 steps resolve them
41 × 41 offsets per map. Linfoot's criteria as Lim & Saloma define them
(p. 126), each PSF scaled to its own peak, averaged over the PSF window.

One case per process, chosen by the environment:
    PAIR = 2ce | 2pe,  THETA = pi | pi2,  ALPHA_T = 0 | 4
NA 0.1–0.99 in air (2PE from 0.3, where its fringes stay resolvable) and NA
1.0–1.2 in water (n = 1.33). Each NA is saved as soon as it is done:

    output/08_two_color/lim2002/fidelity/{pair}_{theta}[_at4]_na{NA}_n{n}.npz
        xt, zt (spot units), ux_um, uz_um, and F, C, Q for 'vec' and 'sca'
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import linfoot
from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'fidelity')
os.makedirs(OUT, exist_ok=True)
L1, L2, L2P = 0.750, 0.656, 0.700
PAIR = os.environ.get('PAIR', '2ce')
TH = os.environ.get('THETA', 'pi')
THETA = np.pi if TH == 'pi' else np.pi / 2
AT = float(os.environ.get('ALPHA_T', '0'))
SUF = '' if AT == 0 else f'_at{AT:g}'
NO = 20                                          # offsets −NO..NO steps each way: 41 × 41
MAX_POINTS = 2.5e6                               # skip an NA whose extended grid would be larger

air = [round(v, 3) for v in np.arange(0.1 if PAIR == '2ce' else 0.3, 0.951, 0.05)] + [0.99]
water = [1.0, 1.05, 1.1, 1.15, 1.2]
PLAN = [(na, 1.0) for na in air] + [(na, 1.33) for na in water]


def chunked(f, X, Z, chunk=15000):
    fx, fz = X.ravel(), Z.ravel()
    out = np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)], axis=-1)
    return out.reshape(out.shape[:-1] + X.shape)


def beam(lam, na, n, model, X, Z, theta=0.0, field=False):
    """Intensity (2CE, unpolarized for the vector model) or field (2PE, polarized along y) on a grid."""
    ap = gaussian(AT, (na / n) ** 2) if AT else None
    if field:
        kw = {} if model == 'sca' else dict(model='rw', psi=np.pi / 2)
        return chunked(lambda x, z: beam_field(x, z, lam, na, n, theta=theta, apodization=ap, **kw), X, Z)
    if model == 'sca':
        return chunked(lambda x, z: intensity(beam_field(x, z, lam, na, n, theta=theta, apodization=ap)), X, Z)
    return chunked(lambda x, z: 0.5 * sum(intensity(beam_field(x, z, lam, na, n, theta=theta, model='rw', psi=p,
                                                                apodization=ap)) for p in (0.0, np.pi / 2)), X, Z)


def maps(na, n, model):
    lam = L1 if PAIR == '2ce' else L2P
    sw, sl = lam / na, n * lam / na ** 2           # spot width and length (µm)
    fr = lam / n                                   # 2PE: offsets along a fringe direction in λ/n (fringes shift by λ/2n)
    if TH == 'pi':
        ux, uz, rx, rz = sw, (sl if PAIR == '2ce' else fr), 0.8, (2.0 if PAIR == '2ce' else 1.0)
        wx, wz = 1.2 * sw, 2.5 * sl
    elif PAIR == '2ce':
        ux, uz, rx, rz = sl, sw, 2.0, 0.8            # x_c slides beam 2 along its length, z_c across its width
        wx, wz = 1.2 * sw, rz * uz + 1.2 * sw        # the product lives where the two beams cross
    else:
        ux, uz, rx, rz = fr, fr, 1.0, 1.0
        wx = wz = 1.2 * sl + fr                      # |E1|⁴ and |E2|⁴ each fill their own beam's length
    res = 0.03 * sw if PAIR == '2ce' else min(0.03 * sw, lam / (10 * n))
    stx, stz = rx * ux / NO, rz * uz / NO          # offset steps (µm)
    kx, kz = max(1, math.ceil(stx / res)), max(1, math.ceil(stz / res))
    dx, dz = stx / kx, stz / kz
    nx, nz = math.ceil(wx / dx), math.ceil(wz / dz)
    mx, mz = NO * kx, NO * kz
    if (2 * nx + 2 * mx) * (2 * nz + 2 * mz) > MAX_POINTS:
        return None
    XW, ZW = np.meshgrid(np.arange(-nx, nx) * dx, np.arange(-nz, nz) * dz)
    XE, ZE = np.meshgrid(np.arange(-nx - mx, nx + mx) * dx, np.arange(-nz - mz, nz + mz) * dz)
    s0, s1 = XW.shape
    if PAIR == '2ce':
        B1, B2 = beam(L1, na, n, model, XW, ZW), beam(L2, na, n, model, XE, ZE, THETA)
        sig = lambda ix, iz: B1 * B2[mz - iz:mz - iz + s0, mx - ix:mx - ix + s1]
    else:
        E1, E2 = beam(L2P, na, n, model, XW, ZW, field=True), beam(L2P, na, n, model, XE, ZE, THETA, field=True)
        def sig(ix, iz):
            E = E1 + E2[..., mz - iz:mz - iz + s0, mx - ix:mx - ix + s1]
            return (np.sum(np.abs(E) ** 2, axis=0) if E.ndim == 3 else np.abs(E) ** 2) ** 2
    t = sig(0, 0); t = t / t.max()
    offs_x, offs_z = np.arange(-NO, NO + 1) * kx, np.arange(-NO, NO + 1) * kz
    F = np.empty((2 * NO + 1, 2 * NO + 1)); C = np.empty_like(F); Q = np.empty_like(F)
    for i, iz in enumerate(offs_z):
        for j, ix in enumerate(offs_x):
            a = sig(ix, iz); a = a / a.max()
            c = linfoot.all_criteria(t, a)
            F[i, j], C[i, j], Q[i, j] = c['F'], c['S'], c['Q']
    return dict(xt=np.arange(-NO, NO + 1) * rx / NO, zt=np.arange(-NO, NO + 1) * rz / NO, ux_um=ux, uz_um=uz,
                F=F, C=C, Q=Q)


for na, n in PLAN:
    path = os.path.join(OUT, f'{PAIR}_{TH}{SUF}_na{na:.3f}_n{n:g}.npz')
    if os.path.exists(path):
        continue                                     # already done (restarts resume)
    vec, sca = maps(na, n, 'vec'), maps(na, n, 'sca')
    if vec is None:
        print(f'{PAIR} {TH}{SUF} NA {na} n {n}: grid too large, skipped', flush=True)
        continue
    np.savez_compressed(path, xt=vec['xt'], zt=vec['zt'], ux_um=vec['ux_um'], uz_um=vec['uz_um'],
                        **{f'{k}_vec': vec[k] for k in 'FCQ'}, **{f'{k}_sca': sca[k] for k in 'FCQ'})
    print(f'{PAIR} {TH}{SUF} NA {na} n {n}: saved', flush=True)
print('DONE')
