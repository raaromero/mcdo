r"""Where does Lim & Saloma's scalar model break down? The paper's own 2CE
metrics against NA, scalar paraxial against Richards–Wolf.

Metrics (the paper's Section 3.2): the offset of O′ that costs 20% of the 2CE
peak, along x_c and along z_c, at θ = π and θ = π/2. The paper's own values at
NA 0.5 are the baseline:
    θ = π/2, x_c: −0.06 x_c² + 1        → 20% at 1.83 λ1 = 1.37 µm
    θ = π/2, z_c: −0.045 z_c² + 0.986   → 20% at 2.03 λ1 = 1.52 µm
    θ = π,   x_c: 20% at 0.37 λ1        = 0.28 µm
    θ = π,   z_c: 20% at 2.7 λ1         = 2.03 µm
Also the aligned PSF itself: Linfoot F of scalar against vector, and the
scalar/vector ratio of widths at half maximum across and along the axis.

Severity = |scalar − vector| / vector for each metric; the NA at which it
first exceeds 5% and 10% is reported. Air, uniform input, unpolarized beams
(mean of two orthogonal input polarizations). θ = π runs to NA 0.95; θ = π/2
stops at 0.70, above which two cones cannot cross in air. In immersion the
defect follows NA/n = sin α, so the NA axis reads as NA/n.

The window (the paper's ±1 × ±5 µm at NA 0.5, 100 × 100 points) and the
offset range scale with the spot, as 1/NA across and 1/NA² along.

    python scripts/fig_lim2002_na_breakdown.py
    -> output/08_two_color/lim2002/na_breakdown_metrics.png, na_breakdown_severity.png,
       na_breakdown.csv
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo import linfoot
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
PAPER = {('pi2', 'x'): 1.826 * L1, ('pi2', 'z'): 2.033 * L1,
         ('pi', 'x'): 0.37 * L1, ('pi', 'z'): 2.7 * L1}
SWEEP = {'pi': np.round(np.arange(0.30, 0.951, 0.05), 2), 'pi2': np.round(np.arange(0.30, 0.701, 0.05), 2)}
THETA = {'pi': np.pi, 'pi2': np.pi / 2}
TL = {'pi': 'θ = π', 'pi2': 'θ = π/2'}


def _beam_I(x, z, lam, na, theta, model):
    if model == 'paraxial':
        return intensity(beam_field(x, z, lam, na, 1.0, theta=theta))
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, theta=theta, model='rw', psi=psi))
                     for psi in (0.0, np.pi / 2))


def beam_I(x, z, lam, na, theta, model, chunk=15000):
    """Unpolarized intensity, computed in chunks of points to bound memory."""
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    fx, fz = x.ravel(), z.ravel()
    out = np.concatenate([_beam_I(fx[i:i + chunk], fz[i:i + chunk], lam, na, theta, model)
                          for i in range(0, fx.size, chunk)])
    return out.reshape(x.shape)


def tolerances(na, theta, model):
    """Offsets (µm) costing 20% of the 2CE peak along x_c and along z_c."""
    sx, sz = 0.5 / na, (0.5 / na) ** 2
    dx, dz = 0.02 * sx, 0.1 * sz                      # the paper's grid at NA 0.5
    nx = nz = 50
    mx, mz = int(round(1.8 * sz / dx)), 60            # offsets to 1.8 (0.5/NA)² µm across, 6 along
    XW, ZW = np.meshgrid(np.arange(-nx, nx) * dx, np.arange(-nz, nz) * dz)
    XE, ZE = np.meshgrid(np.arange(-nx - mx, nx + mx) * dx, np.arange(-nz - mz, nz + mz) * dz)
    I1 = beam_I(XW, ZW, L1, na, 0.0, model)
    I2 = beam_I(XE, ZE, L2, na, theta, model)
    s0, s1 = XW.shape
    peak = lambda ix, iz: (I1 * I2[mz - iz:mz - iz + s0, mx - ix:mx - ix + s1]).max()
    p0 = peak(0, 0)
    out = []
    for n_steps, d, along_x in ((mx, dx, True), (mz, dz, False)):
        prev, val = 1.0, np.nan
        for i in range(1, n_steps + 1):
            p = (peak(i, 0) if along_x else peak(0, i)) / p0
            if p < 0.8:
                val = d * (i - 1 + (prev - 0.8) / (prev - p))
                break
            prev = p
        out.append(val)
    return out


def fwhm(c, g):
    c = c / c.max(); i = int(np.argmax(c)); l = r = i
    while l > 0 and c[l] >= 0.5:
        l -= 1
    while r < len(c) - 1 and c[r] >= 0.5:
        r += 1
    return (np.interp(0.5, [c[r], c[r - 1]], [g[r], g[r - 1]])
            - np.interp(0.5, [c[l], c[l + 1]], [g[l], g[l + 1]]))


def shape(na, theta):
    """Linfoot F of scalar against vector aligned 2CE PSF; scalar/vector widths across and along."""
    hx, hz = 3.0 * L1 / na, 6.0 * L1 / na ** 2
    g = np.linspace(-1, 1, 201)
    X, Z = np.meshgrid(hx * g, hz * g)
    t = beam_I(X, Z, L1, na, 0.0, 'rw') * beam_I(X, Z, L2, na, theta, 'rw')
    a = beam_I(X, Z, L1, na, 0.0, 'paraxial') * beam_I(X, Z, L2, na, theta, 'paraxial')
    F = linfoot.fidelity(t / t.max(), a / a.max())
    xs, zs = np.linspace(-hx, hx, 6001), np.linspace(-hz, hz, 12001)
    w = {m: (fwhm(beam_I(xs, 0 * xs, L1, na, 0.0, m) * beam_I(xs, 0 * xs, L2, na, theta, m), xs),
             fwhm(beam_I(0 * zs, zs, L1, na, 0.0, m) * beam_I(0 * zs, zs, L2, na, theta, m), zs))
         for m in ('paraxial', 'rw')}
    return F, w['paraxial'][0] / w['rw'][0], w['paraxial'][1] / w['rw'][1]


rows = []
R = {}
CSV = os.path.join(OUT, 'na_breakdown.csv')
REPLOT = os.environ.get('REPLOT') == '1' and os.path.exists(CSV)   # redraw from the saved sweep
if REPLOT:
    for t, na, sx_, sz_, rx_, rz_, F, wx, wz in np.loadtxt(CSV, delimiter=','):
        key = 'pi' if t == 0 else 'pi2'
        R[(key, round(na, 2))] = dict(sc_x=sx_, sc_z=sz_, rw_x=rx_, rw_z=rz_, F=F, wx=wx, wz=wz)
for key in (() if REPLOT else ('pi', 'pi2')):
    for na in SWEEP[key]:
        th = THETA[key]
        sc, rw = tolerances(na, th, 'paraxial'), tolerances(na, th, 'rw')
        F, rx, rz = shape(na, th)
        R[(key, na)] = dict(sc_x=sc[0], sc_z=sc[1], rw_x=rw[0], rw_z=rw[1], F=F, wx=rx, wz=rz)
        rows.append((key, na, *sc, *rw, F, rx, rz))
        print(f"{TL[key]} NA {na:.2f}: 20% offset x_c scalar {sc[0]:.3f} vs RW {rw[0]:.3f} µm, "
              f"z_c scalar {sc[1]:.3f} vs RW {rw[1]:.3f} µm; F {F:.4f}; widths scalar/RW x {rx:.3f} z {rz:.3f}",
              flush=True)

if not REPLOT:
    np.savetxt(CSV,
               np.array([[0 if r[0] == 'pi' else 1, *r[1:]] for r in rows], float), delimiter=',', fmt='%.5f',
               header='theta(0=pi,1=pi/2),NA,scalar_x_um,scalar_z_um,rw_x_um,rw_z_um,F_scalar_vs_rw,'
                      'width_x_scalar_over_rw,length_z_scalar_over_rw')

# ── the paper's metrics against NA, with the paper's own values as the baseline ──
fig, axes = plt.subplots(2, 2, figsize=(22.0, 18.0))
for r, key in enumerate(('pi2', 'pi')):
    nas = SWEEP[key]
    for c, ax_ in enumerate(('x', 'z')):
        a = axes[r, c]
        a.plot(nas, [R[(key, na)][f'rw_{ax_}'] for na in nas], '-o', color='#1f77b4', lw=4, ms=10,
               label='Richards–Wolf (vector)')
        a.plot(nas, [R[(key, na)][f'sc_{ax_}'] for na in nas], '--s', color='#d62728', lw=4, ms=10,
               label='paraxial scalar (paper’s model)')
        a.plot([0.5], [PAPER[(key, ax_)]], 'k*', ms=30, label='paper’s quoted value, NA 0.5')
        a.set_yscale('log')
        a.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.yaxis.set_minor_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.set_xlabel('NA (air), or NA/n in immersion')
        a.set_ylabel(f'{ax_}$_c$ costing 20% of peak (µm)')
        a.set_title(f'2CE, {TL[key]}, offset along {ax_}$_c$')
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.03))
plt.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(OUT, 'na_breakdown_metrics.png'), dpi=600, bbox_inches='tight')
plt.close(fig)

# ── severity of the scalar model's defect ──
fig, axes = plt.subplots(1, 2, figsize=(28.0, 12.0), sharey=True)
series = [('x', 'tolerance along x$_c$', '#1f77b4', '-'), ('z', 'tolerance along z$_c$', '#9467bd', '-'),
          ('wx', 'spot width across', '#2ca02c', '--'), ('wz', 'spot length along', '#ff7f0e', '--'),
          ('F', 'PSF shape, 1 − F', '#555555', ':')]
print('\nNA at which the scalar error first exceeds 5% and 10%:')
for a, key in zip(axes, ('pi', 'pi2')):
    nas = SWEEP[key]
    for s, lab, col, ls in series:
        if s in ('x', 'z'):
            e = [abs(R[(key, na)][f'sc_{s}'] / R[(key, na)][f'rw_{s}'] - 1) for na in nas]
        elif s == 'F':
            e = [1 - R[(key, na)]['F'] for na in nas]
        else:
            e = [abs(R[(key, na)][s] - 1) for na in nas]
        e = 100 * np.array(e)
        a.plot(nas, e, ls, color=col, lw=4, label=lab)
        cross = {t: next((na for na, v in zip(nas, e) if v > t), None) for t in (5, 10)}
        print(f"  {TL[key]}, {lab.replace('$_c$', '_c')}: 5% at NA {cross[5]}, 10% at NA {cross[10]}")
    for t in (5, 10):
        a.axhline(t, color='#999999', lw=2, ls=':')
    a.axvline(0.5, color='#999999', lw=2)
    a.set_xlabel('NA (air), or NA/n in immersion')
    a.set_title(f'2CE, {TL[key]}')
    a.set_ylim(0, 50)
axes[0].set_ylabel('Scalar model error (%)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.06))
plt.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(os.path.join(OUT, 'na_breakdown_severity.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved -> na_breakdown_metrics.png, na_breakdown_severity.png, na_breakdown.csv')
