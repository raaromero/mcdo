"""
Configuration atlas — every developed configuration as an INDIVIDUAL
Romallosa-style card: a contour 2-D map (Fig. 1 style) + transverse and axial
line cross-sections (Fig. 2 style, with the uniform-CW baseline dotted for
comparison). One PNG per configuration, organized in per-family subfolders.

  output/atlas/NA/        uniform disk, NA = 0.3 … 1.2   (optical coords v,u)
  output/atlas/gaussian/  NA=0.8, α_t = 0,1,2,4
  output/atlas/annular/   NA=0.8, ε = 0,0.3,0.5,0.7,0.9,0.99
  output/atlas/axicon/    NA=0.8, β = 0,10,20,40
  output/atlas/pulsed/    NA=0.8 uniform, τ = cw,5,2,1 fs

All azimuthally averaged total intensity <|E|^2>, each field normalized to its own peak. Fields
also saved as field_*.npz in each subfolder.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')

from mcdo.atlascard import render_card
from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian, axicon

import argparse
from mcdo import components as _comp

#: Which focal intensity the atlas cards plot. 'full' is the measurable total.
COMPONENTS = {
    'full':   (_comp.full,    'full'),           # <|Ex|^2+|Ey|^2+|Ez|^2>
    'ex':     (_comp.ex_only, 'ex-only'),        # <|Ex|^2>
    'scalar': (_comp.scalar,  'scalar'),         # |I0|^2, no polarization
    'ycut':   (_comp.y_cut,   'y-cut'),          # |I0-I2|^2, the Rom03 cut
}
_ap = argparse.ArgumentParser(description='Focal-field atlas cards.')
_ap.add_argument('--component', choices=sorted(COMPONENTS), default='full',
                 help='which focal intensity to plot (default: full)')
_args, _ = _ap.parse_known_args()
ydir, COMPONENT_LABEL = COMPONENTS[_args.component]

LAM, N_MED, C_UM = 0.750, 1.3, 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas')
if _args.component != 'full':
    OUT = OUT + '_' + _args.component   # never overwrite another component's cards


def save_field(sub, name, h, v, I):
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, f'field_{name}.npz'),
                        intensity=I.astype(np.float32), h=h, v=v)
    return d


def mirror(Ih):
    return np.concatenate([Ih[:, ::-1][:, :-1], Ih], axis=1)



# ── NA family (optical coords; baseline = NA 0.3, near-scalar) ─────────────
print("NA family …")
v_half = np.linspace(0, 12, 121)
u_arr = np.linspace(-26, 26, 261)
v_full = np.concatenate([-v_half[::-1][:-1], v_half])
NA_VALS = [0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 1.2]
na_fields = {}
for xna in NA_VALS:
    c = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=901)
    r_half = v_half / (c.k_c * c.sin_alpha)
    z_arr = u_arr / (c.k_c * c.sin2_alpha)
    I0, I1, I2 = compute_integrals(r_half, z_arr, c.k_c, c.alpha, c.N_theta)
    I = mirror(ydir(I0, I1, I2)); I /= I.max()
    # keep the physical grids so each card carries micrometres, not optical units
    na_fields[xna] = (I, np.concatenate([-r_half[::-1][:-1], r_half]), z_arr)
base, base_r, base_z = na_fields[0.1]
b_tr = base[np.argmax(base[:, np.argmin(np.abs(base_r))])]
b_ax = base[:, np.argmin(np.abs(base_r))]
for xna in NA_VALS:
    I, r_full_na, z_arr_na = na_fields[xna]
    d = save_field('NA', f'NA{xna}', r_full_na, z_arr_na, I)
    # the NA=0.1 baseline lives on its own (much wider) grid, so interpolate it
    # no cross-NA baseline here: in micrometres each NA has its own scale, so
    # overlaying NA 0.1 would read as a flat line rather than a comparison.
    render_card(r_full_na, z_arr_na, I, f'Uniform disk, NA = {xna}',
                os.path.join(d, f'NA_{xna}.png'),
                airy_um=0.61 * LAM / xna, curve_label=f'NA = {xna}')

# ── fixed-NA families (physical μm, NA=0.8; baseline = uniform cw) ──────────
r_half = np.linspace(0.0, 5.0, 301)      # wide enough to zoom out of
z_arr = np.linspace(-15.0, 15.0, 481)
r_full = np.concatenate([-r_half[::-1][:-1], r_half])
c8 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=801)
I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, c8.N_theta)
UNI = mirror(ydir(I0, I1, I2)); UNI /= UNI.max()
uni_tr = UNI[np.argmax(UNI[:, np.argmin(np.abs(r_full))])]
uni_ax = UNI[:, np.argmin(np.abs(r_full))]


def do_fixed(sub, name, title, I_half, curve_label='This configuration'):
    airy_um = 0.61 * LAM / 0.8
    I = mirror(I_half); I /= I.max()
    d = save_field(sub, name, r_full, z_arr, I)
    render_card(r_full, z_arr, I, title, os.path.join(d, f'{name}.png'),
                uni_tr, uni_ax, airy_um=airy_um, curve_label=curve_label)


print("Gaussian family …")
for at, nm in [(0.0, 'at0'), (0.5, 'at0p5'), (1.0, 'at1'), (2.0, 'at2'), (4.0, 'at4')]:
    A = None if at == 0 else gaussian(at, c8.sin2_alpha)
    I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, c8.N_theta, apodization=A)
    do_fixed('gaussian', nm, f'Gaussian apodization, alpha {at:g} (NA = 0.8)', ydir(I0, I1, I2),
             curve_label=f'Alpha {at:g}')

print("Annular family …")
for eps in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
    I0, I1, I2 = compute_integrals_annular(r_half, z_arr, c8.k_c, c8.alpha, eps, c8.N_theta)
    do_fixed('annular', f'eps{eps}', f'Annular aperture, obstruction ratio {eps} (NA = 0.8)', ydir(I0, I1, I2),
             curve_label=f'Obstruction ratio {eps}')

# ── annular across the baseline grid: aperture x input x ratio ────────────
# The annular family above sits at one aperture with uniform light, so it cannot
# be compared against the baseline sweep. This spans the same grid: each card's
# window is sized from its own aperture and its own unobstructed depth, so the
# maps stay legible from numerical aperture 0.1 to 1.2.
print("Annular grid family …")
for xna_g in [0.1, 0.8, 1.2]:
    cg = SimConfig(lam_c=LAM, X_NA=xna_g, n=N_MED, tau=np.inf,
                   N_freq=3, N_theta=801)
    rh = np.linspace(0.0, 7.5 * LAM / xna_g, 301)
    zg = np.linspace(-20.0 * LAM / xna_g ** 2, 20.0 * LAM / xna_g ** 2, 481)
    rf = np.concatenate([-rh[::-1][:-1], rh])
    B0, B1, B2 = compute_integrals(rh, zg, cg.k_c, cg.alpha, cg.N_theta)
    REF = mirror(ydir(B0, B1, B2)); REF /= REF.max()
    ref_tr = REF[np.argmin(np.abs(zg))]
    ref_ax = REF[:, np.argmin(np.abs(rf))]
    for at_g, in_nm, in_lab in [(None, 'uniform', 'uniform'),
                                (4.0, 'gaussian', 'Gaussian, alpha = 4')]:
        A = None if at_g is None else gaussian(at_g, cg.sin2_alpha)
        for eps in [0.0, 0.5, 0.9, 0.99]:
            if eps == 0.0:
                G0, G1, G2 = compute_integrals(rh, zg, cg.k_c, cg.alpha,
                                               cg.N_theta, apodization=A)
            else:
                G0, G1, G2 = compute_integrals_annular(rh, zg, cg.k_c, cg.alpha,
                                                       eps, cg.N_theta, apodization=A)
            I = mirror(ydir(G0, G1, G2)); I /= I.max()
            nm_g = f'na{str(xna_g).replace(".", "p")}_{in_nm}_eps{str(eps).replace(".", "p")}'
            d = save_field('annular_grid', nm_g, rf, zg, I)
            render_card(rf, zg, I,
                        f'Obstruction ratio {eps:g}, {in_lab} input, '
                        f'numerical aperture {xna_g:g}',
                        os.path.join(d, f'{nm_g}.png'), ref_tr, ref_ax,
                        airy_um=0.61 * LAM / xna_g,
                        curve_label=f'Obstruction ratio {eps:g}')
    print(f"  numerical aperture {xna_g:g}: 8 cards")

# ── alpha crossed with obstruction ratio ─────────────────
# The annular grid varies the illumination as a binary. This sweeps the
# alpha so the trend can be followed rather than inferred.
print("Truncation grid family …")
for at_t in [0.0, 1.0, 2.0, 4.0, 8.0]:
    A_t = None if at_t == 0 else gaussian(at_t, c8.sin2_alpha)
    for eps_t in [0.0, 0.5, 0.9, 0.99]:
        if eps_t == 0.0:
            T0, T1, T2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha,
                                           c8.N_theta, apodization=A_t)
        else:
            T0, T1, T2 = compute_integrals_annular(r_half, z_arr, c8.k_c, c8.alpha,
                                                   eps_t, c8.N_theta, apodization=A_t)
        I = mirror(ydir(T0, T1, T2)); I /= I.max()
        nm_t = (f'at{str(at_t).replace(".", "p")}'
                f'_eps{str(eps_t).replace(".", "p")}')
        d = save_field('truncation_grid', nm_t, r_full, z_arr, I)
        render_card(r_full, z_arr, I,
                    f'alpha {at_t:g}, obstruction ratio {eps_t:g}, '
                    f'numerical aperture 0.8',
                    os.path.join(d, f'{nm_t}.png'), uni_tr, uni_ax,
                    airy_um=0.61 * LAM / 0.8,
                    curve_label=f'Alpha {at_t:g}, ratio {eps_t:g}')
    print(f"  coefficient {at_t:g}: 4 cards")

# ── pulsed against continuous wave, for each illumination ─────────────────
print("Pulsed illumination family …")
for at_p, in_nm in [(None, 'uniform'), (4.0, 'gaussian')]:
    A_p = None if at_p is None else gaussian(at_p, c8.sin2_alpha)
    for eps_p in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
        for tau_p, t_nm, t_lab in [(np.inf, 'cw', 'continuous wave'),
                                   (1e-15, '1fs', '1 fs')]:
            cfg_p = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau_p,
                              N_freq=201 if np.isfinite(tau_p) else 3,
                              N_theta=801)
            if np.isfinite(tau_p):
                acc = np.zeros((len(z_arr), len(r_half)))
                om = cfg_p.omega_grid(); wt = cfg_p.spectral_power(om)
                for o, wgt in zip(om, wt):
                    if o <= 0:
                        continue
                    k = cfg_p.k_for_omega(o)
                    if eps_p == 0.0:
                        Q0, Q1, Q2 = compute_integrals(r_half, z_arr, k, cfg_p.alpha,
                                                       801, apodization=A_p)
                    else:
                        Q0, Q1, Q2 = compute_integrals_annular(r_half, z_arr, k,
                                                               cfg_p.alpha, eps_p, 801,
                                                               apodization=A_p)
                    acc += wgt * ydir(Q0, Q1, Q2)
                I_half = acc
            else:
                if eps_p == 0.0:
                    Q0, Q1, Q2 = compute_integrals(r_half, z_arr, cfg_p.k_c,
                                                   cfg_p.alpha, 801, apodization=A_p)
                else:
                    Q0, Q1, Q2 = compute_integrals_annular(r_half, z_arr, cfg_p.k_c,
                                                           cfg_p.alpha, eps_p, 801,
                                                           apodization=A_p)
                I_half = ydir(Q0, Q1, Q2)
            I = mirror(I_half); I /= I.max()
            nm_p = f'{in_nm}_eps{str(eps_p).replace(".", "p")}_{t_nm}'
            d = save_field('pulsed_illumination', nm_p, r_full, z_arr, I)
            lab = 'uniform' if in_nm == 'uniform' else 'Gaussian, alpha = 4'
            render_card(r_full, z_arr, I,
                        f'{lab}, obstruction ratio {eps_p:g}, {t_lab}',
                        os.path.join(d, f'{nm_p}.png'), uni_tr, uni_ax,
                        airy_um=0.61 * LAM / 0.8,
                        curve_label=f'Ratio {eps_p:g}, {t_lab}')
    print(f"  {in_nm}: 8 cards")

print("Axicon family …")
for beta in [0, 5, 10, 20, 40]:
    A = None if beta == 0 else axicon(beta, c8.sin_alpha)
    I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, 2001, apodization=A)
    do_fixed('axicon', f'beta{beta}', f'Axicon, conical phase depth {beta} (NA = 0.8)', ydir(I0, I1, I2),
             curve_label=f'Conical phase depth {beta}')

print("Pulsed family …")
for tau, nm, lab in [(np.inf, 'cw', 'cw'), (5e-15, '5fs', '5 fs'), (3e-15, '3fs', '3 fs'),
                     (2e-15, '2fs', '2 fs'), (1.5e-15, '1p5fs', '1.5 fs'), (1e-15, '1fs', '1 fs')]:
    cp = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau, N_freq=201, N_theta=801)
    if np.isinf(tau):
        I0, I1, I2 = compute_integrals(r_half, z_arr, cp.k_c, cp.alpha, 801)
        Ih = ydir(I0, I1, I2)
    else:
        oms = cp.omega_grid(); S = cp.spectral_power(oms)
        Ih = np.zeros((len(z_arr), len(r_half)))
        for om, s in zip(oms, S):
            k = cp.n * om / C_UM
            if k > 0:
                I0, I1, I2 = compute_integrals(r_half, z_arr, k, cp.alpha, 801)
                Ih += s * ydir(I0, I1, I2)
    do_fixed('pulsed', nm, f'Pulsed source, {lab} (uniform disk, NA = 0.8)', Ih,
             curve_label=f'Pulse, {lab}')

print("Pulsed annular family …")
for eps in [0.5, 0.9]:
    for tau, nm, lab in [(np.inf, 'cw', 'continuous wave'), (2e-15, '2fs', '2 fs'),
                         (1e-15, '1fs', '1 fs')]:
        cp = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau, N_freq=41, N_theta=601)
        if np.isinf(tau):
            I0, I1, I2 = compute_integrals_annular(r_half, z_arr, cp.k_c, cp.alpha, eps, 601)
            Ih = ydir(I0, I1, I2)
        else:
            oms = cp.omega_grid(); S = cp.spectral_power(oms)
            Ih = np.zeros((len(z_arr), len(r_half)))
            for om, sw in zip(oms, S):
                k = cp.n * om / C_UM
                if k > 0:
                    I0, I1, I2 = compute_integrals_annular(r_half, z_arr, k, cp.alpha, eps, 601)
                    Ih += sw * ydir(I0, I1, I2)
        tag = f'eps{str(eps).replace(".", "p")}_{nm}'
        do_fixed('pulsed_annular', tag,
                 f'Obstruction ratio {eps}, {lab} (NA = 0.8)', Ih,
                 curve_label=f'Obstruction {eps}, {lab}')

print("atlas done →", OUT)
