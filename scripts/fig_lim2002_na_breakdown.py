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
    POL=s python scripts/fig_lim2002_na_breakdown.py       # both beams linearly polarized, s or p (suffix _pols, _polp)
    -> output/08_two_color/lim2002/na_breakdown_metrics.png, na_breakdown_severity.png,
       na_breakdown[_at4]_{pi,pi2}.csv (one row per NA, written as computed)
"""

import glob
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
N = float(os.environ.get('N_MED', '1'))            # medium index; 1 = air, 1.33 = water (to reach NA > 1)
POL = os.environ.get('POL', 'unpol')                # 2CE beams: 'unpol' (averaged), 's' (both along y, perpendicular
                                                   # to the plane of the two axes) or 'p' (both in that plane)
PSIS = {'unpol': (0.0, np.pi / 2), 's': (np.pi / 2,), 'p': (0.0,)}[POL]
SUF = ('' if AT == 0 else f'_at{AT:g}') + ('' if N == 1 else f'_n{N:g}') + ('' if POL == 'unpol' else f'_pol{POL}')
APOD = lambda na: gaussian(AT, (na / N) ** 2) if AT else None
MEDIUM = '' if N == 1 else f', n = {N:g}'
PAPER = {('pi2', 'x'): 1.826 * L1, ('pi2', 'z'): 2.033 * L1,
         ('pi', 'x'): 0.37 * L1, ('pi', 'z'): 2.7 * L1}
SWEEP = {k: np.round(np.arange(0.10, 0.9501, 0.025), 3) for k in ('pi', 'pi2')}   # 35 NAs per angle
if os.environ.get('NA_LIST'):                      # a coarser NA grid, e.g. 0.3,0.5,0.7,0.9
    SWEEP = {k: np.array([float(v) for v in os.environ['NA_LIST'].split(',')]) for k in SWEEP}
THETA = {'pi': np.pi, 'pi2': np.pi / 2}
TL = {'pi': 'θ = π', 'pi2': 'θ = π/2'}


def _beam_I(x, z, lam, na, theta, model):
    if model == 'paraxial':
        return intensity(beam_field(x, z, lam, na, N, theta=theta, apodization=APOD(na)))
    return sum(intensity(beam_field(x, z, lam, na, N, theta=theta, model='rw', psi=psi,
                                    apodization=APOD(na)))
               for psi in PSIS) / len(PSIS)


def beam_I(x, z, lam, na, theta, model, chunk=15000):
    """Intensity (unpolarized, or s or p per POL), computed in chunks of points to bound memory."""
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
    grow = (1.0 if AT == 0 else 1.7) * N                     # a Gaussian input enlarges the spot, and the tolerance
    mx = int(round(grow * (0.6 * sx if theta == np.pi else 1.8 * sz) / dx))
    mz = int(round(60 * grow))                        # 6 (0.5/NA)² µm along, more for a Gaussian input
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


R = {}
HEADER = ('NA,scalar_x_um,scalar_z_um,rw_x_um,rw_z_um,F_scalar_vs_rw,'
          'width_x_scalar_over_rw,length_z_scalar_over_rw')
TAG = os.environ.get('RUN_TAG', '')                  # extra NA points go to their own file, e.g. '_lo'
csv_of = lambda key: os.path.join(OUT, f'na_breakdown{SUF}_{key}{TAG}.csv')   # one file per angle (and tag)
all_csv = lambda key: sorted(glob.glob(os.path.join(OUT, f'na_breakdown{SUF}_{key}.csv'))
                             + glob.glob(os.path.join(OUT, f'na_breakdown{SUF}_{key}_*.csv')))
SEL = os.environ.get('THETA_SEL')                     # compute one angle only ('pi' or 'pi2')
REPLOT = os.environ.get('REPLOT') == '1'              # redraw from the saved files
if not REPLOT:
    for key in ((SEL,) if SEL else ('pi', 'pi2')):
        with open(csv_of(key), 'w') as fh:
            fh.write('# ' + HEADER + '\n')
        for na in SWEEP[key]:
            th = THETA[key]
            sc, rw = tolerances(na, th, 'paraxial'), tolerances(na, th, 'rw')
            F, rx, rz = shape(na, th)
            with open(csv_of(key), 'a') as fh:     # saved at once, so a stopped run keeps its points
                fh.write(','.join(f'{v:.6g}' for v in (na, *sc, *rw, F, rx, rz)) + '\n')
            print(f"{TL[key]} NA {na:.3f}: 20% offset x_c scalar {sc[0]:.3f} vs RW {rw[0]:.3f} µm, "
                  f"z_c scalar {sc[1]:.3f} vs RW {rw[1]:.3f} µm; F {F:.4f}; widths scalar/RW x {rx:.3f} z {rz:.3f}",
                  flush=True)
    if SEL or TAG:
        sys.exit(0)                                   # figures come from REPLOT=1 once both angles are saved
for key in ('pi', 'pi2'):
    for f in all_csv(key):
        for na, sx_, sz_, rx_, rz_, F, wx, wz in np.atleast_2d(np.loadtxt(f, delimiter=',')):
            R[(key, round(na, 3))] = dict(sc_x=sx_, sc_z=sz_, rw_x=rx_, rw_z=rz_, F=F, wx=wx, wz=wz)

# ── the paper's metrics against NA: vector, paraxial scalar, power-law fits; Lim & Saloma as reference ──
def powerfit(nas, v):
    """t = A NA^(−p), least squares in log–log."""
    slope, intercept = np.polyfit(np.log(nas), np.log(v), 1)
    return np.exp(intercept), -slope


fig, axes = plt.subplots(1, 4, figsize=(18.2, 5.6))     # one row at twice the slide width: 24-pt text shows at 12 pt
for r, key in enumerate(('pi2', 'pi')):
    nas = np.array(sorted(na for (k, na) in R if k == key))
    for c, ax_ in enumerate(('x', 'z')):
        a = axes[2 * r + c]
        rw = np.array([R[(key, na)][f'rw_{ax_}'] for na in nas])
        sc = np.array([R[(key, na)][f'sc_{ax_}'] for na in nas])
        Av, pv = powerfit(nas, rw)
        lo_na = nas <= 0.5 + 1e-9                      # the paraxial scalar model's stated range
        fit_s = lo_na.sum() >= 3                       # a fit needs a few points (water runs start at NA 0.5)
        As, ps = powerfit(nas[lo_na], sc[lo_na]) if fit_s else (np.nan, np.nan)
        fine = np.linspace(nas[0], nas[-1], 200)
        fine_s = np.linspace(nas[0], 0.5, 100)
        a.plot(nas, rw, 'o', color='#1f77b4', ms=10, label='Vector')
        a.plot(fine, Av * fine ** -pv, '-', color='#1f77b4', lw=3, label='Vector fit')
        a.plot(nas[lo_na], sc[lo_na], 's', color='#d62728', ms=10, mfc='none', mew=2.5, label='Paraxial scalar (NA ≤ 0.5)')
        if fit_s:
            a.plot(fine_s, As * fine_s ** -ps, ':', color='#d62728', lw=3, label='Scalar fit')
        a.hlines(PAPER[(key, ax_)], nas[0], 0.5, colors='k', linestyles='--', lw=3,
                 label='Lim & Saloma, NA 0.5' + (' (uniform)' if AT else ''))
        a.set_xscale('log'); a.set_yscale('log')
        if key == 'pi2' and nas[-1] > N / np.sqrt(2):
            a.axvspan(N / np.sqrt(2), nas[-1] * 1.03, color='none', hatch='//', ec='#999999', lw=0, zorder=0,
                      label='Lenses cannot cross')
        a.set_xlim(nas[0] / 1.15, max(1.02, nas[-1] * 1.03))
        a.set_xticks([t for t in (0.03, 0.1, 0.3, 1.0) if t >= nas[0] - 1e-9])
        a.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        lo, hi = min(rw.min(), sc.min(), PAPER[(key, ax_)]) / 1.25, max(rw.max(), sc.max()) * 60
        a.set_ylim(lo, hi)                             # room above the data for the fit formulas (in µm, as the axis)
        a.set_yticks([t for t in (0.01, 0.1, 1, 10, 100, 1000, 10000) if lo <= t <= hi])
        a.set_xlabel('NA')
        if r == 0 and c == 0:
            a.set_ylabel('Offset for 20% loss (µm)')
        a.set_title(f'{TL[key]}, along {ax_}$_c$')
        a.text(0.97, 0.95, f'{Av:.3g} NA$^{{{-pv:.2f}}}$', transform=a.transAxes, ha='right',
               va='top', color='#1f77b4', fontsize=24)
        if fit_s:
            a.text(0.97, 0.83, f'{As:.3g} NA$^{{{-ps:.2f}}}$', transform=a.transAxes,
                   ha='right', va='top', color='#d62728', fontsize=24)
        print(f"fit {TL[key]} {ax_}_c: vector {Av:.3f} NA^{-pv:.2f}, paraxial scalar {As:.3f} NA^{-ps:.2f}")
h, l = axes[0].get_legend_handles_labels()
fig.suptitle('2CE: offset of O′ costing 20% of the peak' + (f', α$_t$ = {AT:g}' if AT else '') + MEDIUM, fontsize=32, y=1.0)
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.2), frameon=False)
plt.tight_layout(rect=(0, 0.0, 1, 0.94), w_pad=0.8)
fig.savefig(os.path.join(OUT, f'na_breakdown_metrics{SUF}.png'), dpi=600, bbox_inches='tight')
plt.close(fig)

# ── severity of the scalar model's defect ──
fig, axes = plt.subplots(1, 2, figsize=(10.6, 6.0), sharey=True)   # twice its width on the slide
series = [('x', 'Tolerance along x$_c$', '#1f77b4', '-'), ('z', 'Tolerance along z$_c$', '#9467bd', '-'),
          ('wx', 'Lateral width (FWHM)', '#2ca02c', '--'), ('wz', 'Depth of focus', '#ff7f0e', '--'),
          ('F', 'PSF shape, 1 − F', '#555555', ':')]
print('\nNA at which the scalar–vector deviation first exceeds 5% and 10%:')
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
        a.axvspan(N / np.sqrt(2), max(1.0, nas.max()), color='none', hatch='//', ec='#999999', lw=0, zorder=0)
    a.axvline(0.5, color='#999999', lw=2)
    a.set_xlabel('NA')
    a.set_title(TL[key])
    a.set_ylim(0, 50)
axes[0].set_ylabel('Scalar – vector deviation (%)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.2), frameon=False)
fig.suptitle('2CE: scalar–vector deviation' + (f', α$_t$ = {AT:g}' if AT else '') + MEDIUM, fontsize=32, y=1.02)
plt.tight_layout()
fig.savefig(os.path.join(OUT, f'na_breakdown_severity{SUF}.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> na_breakdown_metrics{SUF}.png, na_breakdown_severity{SUF}.png, na_breakdown{SUF}.csv')
