"""Compute the atlas fields the dashboard offers but does not have.

The dashboard's controls span 161 reachable combinations of aperture,
illumination, obstruction ratio and pulse duration. The atlas families were
each written for a particular figure, so together they covered 66 of them:
selecting any of the other 95 drew nothing. This fills the gap.

    annular grid        ratios 0.3, 0.7, 0.95 at all three apertures
    truncation grid     the same three ratios across the alpha sweep
    pulsed grid         2 fs at aperture 0.8, and both pulse durations at
                        apertures 0.1 and 1.2, for every ratio

Existing files are skipped, so the run is resumable. Windows, point counts,
component and N_theta match the family each field belongs to, so a filled cell
is indistinguishable from one computed in the original pass. Pulsed cells use
201 frequencies, as the pulsed families already do.

    python scripts/fill_atlas_gaps.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as ydir
from mcdo.rw_integrals import compute_integrals
from mcdo.atlascard import render_card

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 801, 201
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas')
NEW_EPS = [0.3, 0.7, 0.95]
ALL_EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]


def tag(x):
    return str(x).replace('.', 'p')


def mirror(Ih):
    return np.concatenate([Ih[:, ::-1][:, :-1], Ih], axis=1)


def save(sub, name, h, v, I):
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, f'field_{name}.npz'),
                        intensity=I.astype(np.float32), h=h, v=v)
    return d


def have(sub, name):
    return os.path.exists(os.path.join(OUT, sub, f'field_{name}.npz'))


def field(r, z, k, alpha, eps, apod):
    """One continuous-wave focal field, unobstructed or annular."""
    if eps == 0.0:
        return ydir(*compute_integrals(r, z, k, alpha, NT, apodization=apod))
    return ydir(*compute_integrals_annular(r, z, k, alpha, eps, NT,
                                           apodization=apod))


def pulsed_field(cfg, r, z, eps, apod):
    """Time-integrated focal field: the spectrum weighted, frequency by frequency."""
    acc = np.zeros((len(z), len(r)))
    om = cfg.omega_grid()
    for o, w in zip(om, cfg.spectral_power(om)):
        if o <= 0:
            continue
        acc += w * field(r, z, cfg.k_for_omega(o), cfg.alpha, eps, apod)
    return acc


t0 = time.time()
made = 0

# ── annular grid: the three ratios the original pass skipped ───────────────
print('Annular grid gaps ...', flush=True)
for xna in [0.1, 0.8, 1.2]:
    cg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                   N_freq=3, N_theta=NT)
    rh = np.linspace(0.0, 7.5 * LAM / xna, 301)
    zg = np.linspace(-20.0 * LAM / xna ** 2, 20.0 * LAM / xna ** 2, 481)
    rf = np.concatenate([-rh[::-1][:-1], rh])
    REF = mirror(field(rh, zg, cg.k_c, cg.alpha, 0.0, None))
    REF /= REF.max()
    ref_tr = REF[np.argmin(np.abs(zg))]
    ref_ax = REF[:, np.argmin(np.abs(rf))]
    for at, nm_in, lab in [(None, 'uniform', 'uniform'),
                           (4.0, 'gaussian', 'Gaussian, alpha = 4')]:
        A = None if at is None else gaussian(at, cg.sin2_alpha)
        for eps in NEW_EPS:
            nm = f'na{tag(xna)}_{nm_in}_eps{tag(eps)}'
            if have('annular_grid', nm):
                continue
            I = mirror(field(rh, zg, cg.k_c, cg.alpha, eps, A))
            I /= I.max()
            d = save('annular_grid', nm, rf, zg, I)
            render_card(rf, zg, I,
                        f'Obstruction ratio {eps:g}, {lab} input, '
                        f'numerical aperture {xna:g}',
                        os.path.join(d, f'{nm}.png'), ref_tr, ref_ax,
                        airy_um=0.61 * LAM / xna,
                        curve_label=f'Obstruction ratio {eps:g}')
            made += 1
            print(f'  {nm}', flush=True)

# ── truncation grid: same three ratios, across the alpha sweep ─────────────
print('Truncation grid gaps ...', flush=True)
r_half = np.linspace(0.0, 5.0, 301)
z_arr = np.linspace(-15.0, 15.0, 481)
r_full = np.concatenate([-r_half[::-1][:-1], r_half])
c8 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
UNI = mirror(field(r_half, z_arr, c8.k_c, c8.alpha, 0.0, None))
UNI /= UNI.max()
uni_tr = UNI[np.argmin(np.abs(z_arr))]
uni_ax = UNI[:, np.argmin(np.abs(r_full))]
for at in [0.0, 1.0, 2.0, 4.0, 8.0]:
    A = None if at == 0 else gaussian(at, c8.sin2_alpha)
    for eps in NEW_EPS:
        nm = f'at{tag(at)}_eps{tag(eps)}'
        if have('truncation_grid', nm):
            continue
        I = mirror(field(r_half, z_arr, c8.k_c, c8.alpha, eps, A))
        I /= I.max()
        d = save('truncation_grid', nm, r_full, z_arr, I)
        render_card(r_full, z_arr, I,
                    f'alpha {at:g}, obstruction ratio {eps:g}, '
                    f'numerical aperture 0.8',
                    os.path.join(d, f'{nm}.png'), uni_tr, uni_ax,
                    airy_um=0.61 * LAM / 0.8,
                    curve_label=f'Alpha {at:g}, ratio {eps:g}')
        made += 1
        print(f'  {nm}', flush=True)

print(f'continuous-wave gaps done, {made} fields, '
      f'{(time.time() - t0) / 60:.1f} min', flush=True)

# ── pulsed grid: every aperture, both illuminations, every ratio ──────────
# Aperture 0.8 already has continuous wave and 1 fs from the pulsed
# illumination family, so only 2 fs is computed there; the other two
# apertures have no pulsed fields at all.
print('Pulsed grid ...', flush=True)
JOBS = [(0.8, '2fs', 2e-15)]
for xna in (0.1, 1.2):
    JOBS += [(xna, '2fs', 2e-15), (xna, '1fs', 1e-15)]

for xna, t_nm, tau in JOBS:
    rh = np.linspace(0.0, 7.5 * LAM / xna, 301)
    zg = np.linspace(-20.0 * LAM / xna ** 2, 20.0 * LAM / xna ** 2, 481)
    rf = np.concatenate([-rh[::-1][:-1], rh])
    cg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                   N_freq=3, N_theta=NT)
    REF = mirror(field(rh, zg, cg.k_c, cg.alpha, 0.0, None))
    REF /= REF.max()
    ref_tr = REF[np.argmin(np.abs(zg))]
    ref_ax = REF[:, np.argmin(np.abs(rf))]
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=tau,
                    N_freq=NFREQ, N_theta=NT)
    for at, nm_in, lab in [(None, 'uniform', 'uniform'),
                           (4.0, 'gaussian', 'Gaussian, alpha = 4')]:
        A = None if at is None else gaussian(at, cg.sin2_alpha)
        for eps in ALL_EPS:
            nm = f'na{tag(xna)}_{nm_in}_eps{tag(eps)}_{t_nm}'
            if have('pulsed_grid', nm):
                continue
            t1 = time.time()
            I = mirror(pulsed_field(cfg, rh, zg, eps, A))
            I /= I.max()
            d = save('pulsed_grid', nm, rf, zg, I)
            render_card(rf, zg, I,
                        f'{lab}, obstruction ratio {eps:g}, {t_nm[0]} fs pulse, '
                        f'numerical aperture {xna:g}',
                        os.path.join(d, f'{nm}.png'), ref_tr, ref_ax,
                        airy_um=0.61 * LAM / xna,
                        curve_label=f'Ratio {eps:g}, {t_nm[0]} fs')
            made += 1
            print(f'  {nm}  ({time.time() - t1:.0f}s)', flush=True)

print(f'\n{made} fields written in {(time.time() - t0) / 60:.1f} min')
