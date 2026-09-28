r"""Consistency of Gaussian truncation at low NA, scalar against vector.

Three checks, for 2CE at NA 0.3 and 0.5 (air), unpolarized, input truncation
α_t = 0, 0.5, 1, 2, 3, 4 with A(ϑ) = exp(−α_t sin²ϑ / sin²α) in both models
(in the scalar model this is exactly exp(−α_t ρ²) on the pupil):

  1. the scalar model at α_t = 0 against Lim & Saloma's quoted NA 0.5 values;
  2. the scalar model with truncation: every metric should move smoothly and
     monotonically with α_t (a larger spot, so larger tolerances);
  3. the vector (Richards–Wolf) model with truncation against the scalar model
     at the same α_t: they should agree at low NA, as they do at α_t = 0.

Metrics: the paper's 20%-loss offsets along x_c and z_c at θ = π and π/2, and
the aligned 2CE spot's widths at half maximum across (x) and along (z).

    python scripts/fig_lim2002_truncation_check.py
    -> output/08_two_color/lim2002/truncation_check_metrics.png,
       truncation_check_agreement.png, truncation_check.csv
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

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
NAS = (0.3, 0.5)
ATS = (0, 0.5, 1, 2, 3, 4)
LIM = {('pi2', 'x'): 1.826 * L1, ('pi2', 'z'): 2.033 * L1, ('pi', 'x'): 0.37 * L1, ('pi', 'z'): 2.7 * L1}
THETA = {'pi': np.pi, 'pi2': np.pi / 2}
TL = {'pi': 'θ = π', 'pi2': 'θ = π/2'}


def _I(x, z, lam, na, theta, model, at):
    apod = gaussian(at, na ** 2) if at else None
    if model == 'scalar':
        return intensity(beam_field(x, z, lam, na, 1.0, theta=theta, apodization=apod))
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, theta=theta, model='rw', psi=psi,
                                          apodization=apod)) for psi in (0.0, np.pi / 2))


def beam_I(x, z, lam, na, theta, model, at, chunk=15000):
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    fx, fz = x.ravel(), z.ravel()
    return np.concatenate([_I(fx[i:i + chunk], fz[i:i + chunk], lam, na, theta, model, at)
                           for i in range(0, fx.size, chunk)]).reshape(x.shape)


def tolerances(na, theta, model, at):
    sx, sz = 0.5 / na, (0.5 / na) ** 2
    dx, dz = 0.02 * sx, 0.1 * sz
    nx = nz = 50
    mx, mz = int(round(2.6 * sz / dx)), 90
    XW, ZW = np.meshgrid(np.arange(-nx, nx) * dx, np.arange(-nz, nz) * dz)
    XE, ZE = np.meshgrid(np.arange(-nx - mx, nx + mx) * dx, np.arange(-nz - mz, nz + mz) * dz)
    I1 = beam_I(XW, ZW, L1, na, 0.0, model, at)
    I2 = beam_I(XE, ZE, L2, na, theta, model, at)
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


def widths(na, theta, model, at):
    hx, hz = 3.0 * L1 / na, 6.0 * L1 / na ** 2
    xs, zs = np.linspace(-hx, hx, 6001), np.linspace(-hz, hz, 12001)
    wx = fwhm(beam_I(xs, 0 * xs, L1, na, 0.0, model, at) * beam_I(xs, 0 * xs, L2, na, theta, model, at), xs)
    wz = fwhm(beam_I(0 * zs, zs, L1, na, 0.0, model, at) * beam_I(0 * zs, zs, L2, na, theta, model, at), zs)
    return wx, wz


R = {}
rows = []
CSV = os.path.join(OUT, 'truncation_check.csv')
REPLOT = os.environ.get('REPLOT') == '1' and os.path.exists(CSV)   # redraw from the saved run
if REPLOT:
    for na, t, at, m, tx, tz, wx, wz in np.loadtxt(CSV, delimiter=','):
        R[(round(na, 2), 'pi' if t == 0 else 'pi2', at if at % 1 else int(at), 'scalar' if m == 0 else 'vector')] = \
            dict(x=tx, z=tz, wx=wx, wz=wz)
for na in (() if REPLOT else NAS):
    for key in ('pi', 'pi2'):
        for at in ATS:
            for model in ('scalar', 'vector'):
                tx, tz = tolerances(na, THETA[key], model, at)
                wx, wz = widths(na, THETA[key], model, at)
                R[(na, key, at, model)] = dict(x=tx, z=tz, wx=wx, wz=wz)
                rows.append((na, 0 if key == 'pi' else 1, at, 0 if model == 'scalar' else 1, tx, tz, wx, wz))
                print(f"NA {na} {TL[key]} α_t={at} {model}: 20% offsets x_c {tx:.3f}, z_c {tz:.3f} µm; "
                      f"FWHM x {wx * 1e3:.0f}, z {wz * 1e3:.0f} nm", flush=True)
if not REPLOT:
    np.savetxt(CSV, np.array(rows), delimiter=',', fmt='%.5f',
               header='NA,theta(0=pi,1=pi/2),alpha_t,model(0=scalar,1=vector),tol_x_um,tol_z_um,fwhm_x_um,fwhm_z_um')

# check 1: scalar at α_t = 0, NA 0.5 against Lim
print('\nCheck 1, scalar α_t = 0 at NA 0.5 against Lim & Saloma:')
for key in ('pi', 'pi2'):
    for m in ('x', 'z'):
        v = R[(0.5, key, 0, 'scalar')][m]
        print(f"  {TL[key]}, {m}_c: ours {v:.3f} µm, paper {LIM[(key, m)]:.3f} µm ({100 * (v / LIM[(key, m)] - 1):+.1f}%)")
# check 2: monotonic in α_t
print('\nCheck 2, scalar metrics monotonic in α_t:')
for na in NAS:
    for key in ('pi', 'pi2'):
        for m in ('x', 'z', 'wx', 'wz'):
            v = np.array([R[(na, key, at, 'scalar')][m] for at in ATS])
            ok = np.all(np.diff(v) > 0)
            print(f"  NA {na} {TL[key]} {m}: {'increasing' if ok else 'NOT monotonic'} "
                  f"({v[0]:.3f} → {v[-1]:.3f}, ×{v[-1] / v[0]:.2f})")
# check 3: vector against scalar at the same α_t
print('\nCheck 3, scalar error relative to vector, |scalar/vector − 1| (%), max over α_t:')
for na in NAS:
    for key in ('pi', 'pi2'):
        e = {m: max(abs(R[(na, key, at, 'scalar')][m] / R[(na, key, at, 'vector')][m] - 1) * 100 for at in ATS)
             for m in ('x', 'z', 'wx', 'wz')}
        print(f"  NA {na} {TL[key]}: " + ', '.join(f'{m} {v:.1f}%' for m, v in e.items()))

# ── figure 1: the paper's metrics against α_t, scalar and vector, Lim as baseline ──
fig, axes = plt.subplots(2, 2, figsize=(22.0, 18.0))
col = {0.3: '#1f77b4', 0.5: '#d62728'}
for r, key in enumerate(('pi2', 'pi')):
    for c, m in enumerate(('x', 'z')):
        a = axes[r, c]
        for na in NAS:
            a.plot(ATS, [R[(na, key, at, 'vector')][m] for at in ATS], '-o', color=col[na], lw=4, ms=10,
                   label=f'vector (Richards–Wolf), NA {na}')
            a.plot(ATS, [R[(na, key, at, 'scalar')][m] for at in ATS], '--s', color=col[na], lw=3, ms=10,
                   mfc='none', mew=3, label=f'scalar, NA {na}')
        a.plot([0], [LIM[(key, m)]], 'k*', ms=30, label='Lim & Saloma, NA 0.5')
        a.set_yscale('log')
        a.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.yaxis.set_minor_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.set_xlabel('Truncation parameter α$_t$')
        a.set_ylabel(f'{m}$_c$ costing 20% of peak (µm)')
        a.set_title(f'2CE, {TL[key]}, offset along {m}$_c$')
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.04))
plt.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(os.path.join(OUT, 'truncation_check_metrics.png'), dpi=600, bbox_inches='tight')
plt.close(fig)

# ── figure 2: vector against scalar at the same α_t ──
fig, axes = plt.subplots(1, 2, figsize=(28.0, 12.0), sharey=True)
series = [('x', 'tolerance along x$_c$', '#1f77b4', '-'), ('z', 'tolerance along z$_c$', '#9467bd', '-'),
          ('wx', 'spot width across', '#2ca02c', '--'), ('wz', 'spot length along', '#ff7f0e', '--')]
for a, na in zip(axes, NAS):
    for key, mk in (('pi', 'o'), ('pi2', 's')):
        for m, lab, cl, ls in series:
            a.plot(ATS, [100 * (R[(na, key, at, 'scalar')][m] / R[(na, key, at, 'vector')][m] - 1) for at in ATS],
                   ls, marker=mk, color=cl, lw=3, ms=10, label=f'{lab}, {TL[key]}')
    a.axhline(0, color='#999999', lw=2)
    a.set_xlabel('Truncation parameter α$_t$')
    a.set_title(f'NA {na}, air')
axes[0].set_ylabel('Scalar model error, scalar / vector − 1 (%)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1))
plt.tight_layout(rect=(0, 0.14, 1, 1))
fig.savefig(os.path.join(OUT, 'truncation_check_agreement.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved -> truncation_check_metrics.png, truncation_check_agreement.png, truncation_check.csv')
