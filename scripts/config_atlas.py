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

All linear-x y-cut |I₀−I₂|², each field normalized to its own peak. Fields
also saved as field_*.npz in each subfolder.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian, axicon

LAM, N_MED, C_UM = 0.750, 1.3, 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas')
LEVELS = [0.5, 1, 2, 4, 6, 10, 20, 40, 60, 80, 100]
ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2


def mirror(Ih):
    return np.concatenate([Ih[:, ::-1][:, :-1], Ih], axis=1)


def render_card(h, v, I, title, outpath, base_tr=None, base_ax=None,
                hlabel='r (μm)', vlabel='z (μm)', base_label='uniform cw'):
    ih0 = np.argmin(np.abs(h))
    izpk = np.argmax(I[:, ih0])
    fig = plt.figure(figsize=(8.4, 4.8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.5, wspace=0.3)
    axm = fig.add_subplot(gs[:, 0])
    axt = fig.add_subplot(gs[0, 1])
    axa = fig.add_subplot(gs[1, 1])
    fig.suptitle(title, fontsize=11)

    HH, VV = np.meshgrid(h, v)
    ext = [h[0], h[-1], v[0], v[-1]]
    axm.imshow(I, extent=ext, origin='lower', aspect='auto', cmap='inferno',
               norm=LogNorm(vmin=1e-3, vmax=1))            # heat map
    axm.contour(HH, VV, 100.0 * I / I.max(), levels=LEVELS,
                colors='w', linewidths=0.4, alpha=0.45)    # + contour lines
    axm.set_xlabel(hlabel); axm.set_ylabel(vlabel)
    axm.set_title('(a) 2-D map: heat + contours', fontsize=9)

    axt.plot(h, I[izpk], 'k-', lw=1.4, label='this config')
    if base_tr is not None:
        axt.plot(h, base_tr, 'k:', lw=1.0, label=base_label)
    axt.set_ylim(0, 1.05); axt.set_xlim(h[0], h[-1])
    axt.set_xlabel(hlabel); axt.set_ylabel('norm. I')
    axt.set_title(f'(b) transverse (z={v[izpk]:.1f})', fontsize=9)
    axt.legend(fontsize=7)

    axa.plot(v, I[:, ih0], 'k-', lw=1.4)
    if base_ax is not None:
        axa.plot(v, base_ax, 'k:', lw=1.0)
    axa.set_ylim(0, 1.05); axa.set_xlim(v[0], v[-1])
    axa.set_xlabel(vlabel); axa.set_ylabel('norm. I')
    axa.set_title('(c) axial (r=0)', fontsize=9)

    fig.savefig(outpath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  saved", os.path.relpath(outpath, OUT))


def save_field(sub, name, h, v, I):
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, f'field_{name}.npz'),
                        intensity=I.astype(np.float32), h=h, v=v)
    return d


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
    na_fields[xna] = I
base = na_fields[0.1]
b_tr = base[np.argmax(base[:, np.argmin(np.abs(v_full))])]
b_ax = base[:, np.argmin(np.abs(v_full))]
for xna in NA_VALS:
    d = save_field('NA', f'NA{xna}', v_full, u_arr, na_fields[xna])
    render_card(v_full, u_arr, na_fields[xna], f'Uniform disk, NA={xna}',
                os.path.join(d, f'NA_{xna}.png'), b_tr, b_ax, 'v', 'u',
                base_label='NA=0.1 (scalar)')

# ── fixed-NA families (physical μm, NA=0.8; baseline = uniform cw) ──────────
r_half = np.linspace(0.0, 2.0, 161)
z_arr = np.linspace(-6.0, 6.0, 261)
r_full = np.concatenate([-r_half[::-1][:-1], r_half])
c8 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=801)
I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, c8.N_theta)
UNI = mirror(ydir(I0, I1, I2)); UNI /= UNI.max()
uni_tr = UNI[np.argmax(UNI[:, np.argmin(np.abs(r_full))])]
uni_ax = UNI[:, np.argmin(np.abs(r_full))]


def do_fixed(sub, name, title, I_half):
    I = mirror(I_half); I /= I.max()
    d = save_field(sub, name, r_full, z_arr, I)
    render_card(r_full, z_arr, I, title, os.path.join(d, f'{name}.png'),
                uni_tr, uni_ax)


print("Gaussian family …")
for at, nm in [(0.0, 'at0'), (0.5, 'at0p5'), (1.0, 'at1'), (2.0, 'at2'), (4.0, 'at4')]:
    A = None if at == 0 else gaussian(at, c8.sin2_alpha)
    I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, c8.N_theta, apodization=A)
    do_fixed('gaussian', nm, f'Gaussian apodization α_t={at:g} (NA=0.8)', ydir(I0, I1, I2))

print("Annular family …")
for eps in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
    I0, I1, I2 = compute_integrals_annular(r_half, z_arr, c8.k_c, c8.alpha, eps, c8.N_theta)
    do_fixed('annular', f'eps{eps}', f'Annular ε={eps} (NA=0.8)', ydir(I0, I1, I2))

print("Axicon family …")
for beta in [0, 5, 10, 20, 40]:
    A = None if beta == 0 else axicon(beta, c8.sin_alpha)
    I0, I1, I2 = compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, 2001, apodization=A)
    do_fixed('axicon', f'beta{beta}', f'Axicon β={beta} (NA=0.8)', ydir(I0, I1, I2))

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
    do_fixed('pulsed', nm, f'Pulsed τ={lab} (uniform, NA=0.8)', Ih)

print("atlas done →", OUT)
