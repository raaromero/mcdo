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
(mean of two orthogonal input polarizations). Air, NA 0.1–0.95 at both angles;
above NA 0.71 two lenses cannot cross at θ = π/2 in air, so that range is
computed but hatched as not realizable. In immersion the
defect follows NA/n = sin α, so the NA axis reads as NA/n.

The window (the paper's ±1 × ±5 µm at NA 0.5, 100 × 100 points) and the
offset range scale with the spot, as 1/NA across and 1/NA² along.

    python scripts/fig_lim2002_na_breakdown.py
    ALPHA_T=4 python scripts/fig_lim2002_na_breakdown.py   # the same with input truncation α_t = 4
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
from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
AT = float(os.environ.get('ALPHA_T', '0'))       # input truncation; 0 = uniform, Lim & Saloma's case
SUF = '' if AT == 0 else f'_at{AT:g}'
APOD = lambda na: gaussian(AT, na ** 2) if AT else None
PAPER = {('pi2', 'x'): 1.826 * L1, ('pi2', 'z'): 2.033 * L1,
         ('pi', 'x'): 0.37 * L1, ('pi', 'z'): 2.7 * L1}
SWEEP = {'pi': np.round(np.arange(0.10, 0.951, 0.05), 2), 'pi2': np.round(np.arange(0.10, 0.951, 0.05), 2)}
if os.environ.get('NA_LIST'):                      # a coarser NA grid, e.g. 0.3,0.5,0.7,0.9
    SWEEP = {k: np.array([float(v) for v in os.environ['NA_LIST'].split(',')]) for k in SWEEP}
THETA = {'pi': np.pi, 'pi2': np.pi / 2}
TL = {'pi': 'θ = π', 'pi2': 'θ = π/2'}


def _beam_I(x, z, lam, na, theta, model):
    if model == 'paraxial':
        return intensity(beam_field(x, z, lam, na, 1.0, theta=theta, apodization=APOD(na)))
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, theta=theta, model='rw', psi=psi,
                                          apodization=APOD(na)))
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
    # offsets across: at θ = π the tolerance scales with the width (0.30 µm at NA 0.5), at θ = π/2 with the
    # other beam's length (1.37 µm at NA 0.5); along: with the length at both angles
    mx = int(round((0.6 * sx if theta == np.pi else 1.8 * sz) / dx))
    mz = 60                                           # 6 (0.5/NA)² µm along
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
CSV = os.path.join(OUT, f'na_breakdown{SUF}.csv')
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

# ── the paper's metrics against NA: vector, paraxial scalar, power-law fits; Lim & Saloma as reference ──
def powerfit(nas, v):
    """t = A NA^(−p), least squares in log–log."""
    slope, intercept = np.polyfit(np.log(nas), np.log(v), 1)
    return np.exp(intercept), -slope


fig, axes = plt.subplots(2, 2, figsize=(18.0, 16.0), sharex=True)
for r, key in enumerate(('pi2', 'pi')):
    nas = np.array(SWEEP[key]) if not REPLOT else np.array(sorted(na for (k, na) in R if k == key))
    for c, ax_ in enumerate(('x', 'z')):
        a = axes[r, c]
        rw = np.array([R[(key, na)][f'rw_{ax_}'] for na in nas])
        sc = np.array([R[(key, na)][f'sc_{ax_}'] for na in nas])
        Av, pv = powerfit(nas, rw)
        lo_na = nas <= 0.5 + 1e-9                      # the paraxial scalar model's stated range
        As, ps = powerfit(nas[lo_na], sc[lo_na])
        fine = np.linspace(nas[0], nas[-1], 200)
        fine_s = np.linspace(nas[0], 0.5, 100)
        a.plot(nas, rw, 'o', color='#1f77b4', ms=10, label='Vector (Richards–Wolf)')
        a.plot(fine, Av * fine ** -pv, '-', color='#1f77b4', lw=3, label='Vector, power-law fit')
        a.plot(nas[lo_na], sc[lo_na], 's', color='#d62728', ms=10, mfc='none', mew=2.5, label='Paraxial scalar (NA ≤ 0.5)')
        a.plot(fine_s, As * fine_s ** -ps, ':', color='#d62728', lw=3, label='Paraxial scalar, power-law fit')
        a.hlines(PAPER[(key, ax_)], nas[0], 0.5, colors='k', linestyles='--', lw=3,
                 label='Lim & Saloma (2002), NA 0.5' + (' (uniform input)' if AT else ''))
        a.set_xscale('log'); a.set_yscale('log')
        if key == 'pi2' and nas[-1] > 1 / np.sqrt(2):
            a.axvspan(1 / np.sqrt(2), nas[-1] * 1.03, color='none', hatch='//', ec='#999999', lw=0, zorder=0,
                      label='not buildable in air')
        a.set_xlim(0.28, 0.98)
        a.set_xticks([0.3, 0.5, 0.7, 0.9])
        a.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        lo, hi = min(rw.min(), sc.min(), PAPER[(key, ax_)]) / 1.25, max(rw.max(), sc.max()) * 1.6
        a.set_ylim(lo, hi)                             # room above the data for the fit formulas
        a.set_yticks([t for t in (0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5, 7, 10) if lo <= t <= hi])
        if r == 1:
            a.set_xlabel('NA')
        if c == 0:
            a.set_ylabel('Offset for 20% loss (µm)')
        a.set_title(f'{TL[key]}, along {ax_}$_c$')
        a.text(0.97, 0.95, f'{Av:.3g} NA$^{{-{pv:.2f}}}$ µm', transform=a.transAxes, ha='right',
               va='top', color='#1f77b4', fontsize=22)
        a.text(0.97, 0.83, f'{As:.3g} NA$^{{-{ps:.2f}}}$ µm', transform=a.transAxes,
               ha='right', va='top', color='#d62728', fontsize=22)
        print(f"fit {TL[key]} {ax_}_c: vector {Av:.3f} NA^-{pv:.2f}, paraxial scalar {As:.3f} NA^-{ps:.2f}")
h, l = axes[1, 0].get_legend_handles_labels()
fig.suptitle('2CE: offset of O′ costing 20% of the peak' + (f', α$_t$ = {AT:g}' if AT else ''), fontsize=32, y=1.0)
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.08), frameon=False)
plt.tight_layout(rect=(0, 0.0, 1, 0.96), h_pad=1.5, w_pad=1.5)
fig.savefig(os.path.join(OUT, f'na_breakdown_metrics{SUF}.png'), dpi=600, bbox_inches='tight')
plt.close(fig)

# ── severity of the scalar model's defect ──
fig, axes = plt.subplots(1, 2, figsize=(20.0, 8.5), sharey=True)
series = [('x', 'tolerance along x$_c$', '#1f77b4', '-'), ('z', 'tolerance along z$_c$', '#9467bd', '-'),
          ('wx', 'spot width across', '#2ca02c', '--'), ('wz', 'spot length along', '#ff7f0e', '--'),
          ('F', 'PSF shape, 1 − F', '#555555', ':')]
print('\nNA at which the scalar error first exceeds 5% and 10%:')
for a, key in zip(axes, ('pi', 'pi2')):
    nas = np.array(sorted(na for (k, na) in R if k == key))
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
    if key == 'pi2':
        a.axvspan(1 / np.sqrt(2), 1.0, color='none', hatch='//', ec='#999999', lw=0, zorder=0)
    a.axvline(0.5, color='#999999', lw=2)
    a.set_xlabel('NA')
    a.set_title(f'2CE, {TL[key]}' + (f', α$_t$ = {AT:g}' if AT else ''))
    a.set_ylim(0, 50)
axes[0].set_ylabel('Scalar model error (%)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.06))
plt.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(os.path.join(OUT, f'na_breakdown_severity{SUF}.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> na_breakdown_metrics{SUF}.png, na_breakdown_severity{SUF}.png, na_breakdown{SUF}.csv')
