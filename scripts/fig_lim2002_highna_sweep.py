r"""Lim & Saloma (2002) 2CE results at high NA, with the Richards–Wolf focus.

1. Tolerance: the offset of O′ that costs 20% of the 2CE peak (the paper's
   tolerance), along x_c and z_c at θ = π and π/2, for NA 0.5 (air), 0.75 and
   0.9 (water, n = 1.33: in air θ = π/2 needs NA ≤ 0.71), and for input
   truncation α_t = 0 (uniform), 1 and 4, A(ϑ) = exp(−α_t sin²ϑ / sin²α).
2. Scalar against vector: how far the paper's paraxial scalar 2CE PSF departs
   from the Richards–Wolf one as NA grows (uniform input, air), by Linfoot's
   F, C, Q (reference t = Richards–Wolf) and by the ratio of widths at half
   maximum. θ = π runs to NA 0.95; θ = π/2 stops at 0.70, where two cones in
   air can still cross.

Beams unpolarized: each intensity is the mean over two orthogonal input
polarizations. λ1 = 750 nm, λ2 = 656 nm in vacuum.

    python scripts/fig_lim2002_highna_sweep.py
    -> output/08_two_color/lim2002/highna_tolerance_sweep.png, highna_scalar_vs_vector.png
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo import linfoot
from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656


def beam_I(x, z, lam, na, n, theta=0.0, model='rw', alpha_t=0):
    if model == 'paraxial':
        return intensity(beam_field(x, z, lam, na, n, theta=theta))
    apod = gaussian(alpha_t, (na / n) ** 2) if alpha_t else None
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, n, theta=theta, model='rw', psi=psi,
                                          apodization=apod)) for psi in (0.0, np.pi / 2))


# ── 1. tolerance against NA and truncation ────────────────────────────────
ONLY_SCALAR = os.environ.get('ONLY') == 'scalar'   # rerun part 2 alone
DX, DZ = 0.02, 0.1
NX, NZ, MX, MZ = 50, 50, 75, 60                   # window ±1 × ±5 µm; offsets to 1.5 × 6 µm
XW, ZW = np.meshgrid(np.arange(-NX, NX) * DX, np.arange(-NZ, NZ) * DZ)
XE, ZE = np.meshgrid(np.arange(-NX - MX, NX + MX) * DX, np.arange(-NZ - MZ, NZ + MZ) * DZ)


def tolerance(model, na, n, theta, alpha_t):
    I1 = beam_I(XW, ZW, L1, na, n, 0.0, model, alpha_t)
    I2 = beam_I(XE, ZE, L2, na, n, theta, model, alpha_t)
    sz, sx = XW.shape
    peak = lambda ix, iz: (I1 * I2[MZ - iz:MZ - iz + sz, MX - ix:MX - ix + sx]).max()
    p0 = peak(0, 0)
    out = []
    for steps, d, key in ((range(MX + 1), DX, 'x'), (range(MZ + 1), DZ, 'z')):
        prev = 1.0
        val = None
        for i in steps:
            p = (peak(i, 0) if key == 'x' else peak(0, i)) / p0
            if p < 0.8:
                val = d * (i - 1 + (prev - 0.8) / (prev - p))
                break
            prev = p
        out.append(val)
    return out


NAS = ((0.5, 1.0), (0.75, 1.33), (0.9, 1.33))
ATS = (0, 1, 4)
TOL = {}
if ONLY_SCALAR:
    NAS, ATS = (), ()
ref = {th: tolerance('paraxial', 0.5, 1.0, th, 0) for th in (np.pi, np.pi / 2)} if not ONLY_SCALAR else {}
for th in (() if ONLY_SCALAR else (np.pi, np.pi / 2)):
    for at in ATS:
        for na, n in NAS:
            TOL[(th, at, na)] = tolerance('rw', na, n, th, at)
            tx, tz = TOL[(th, at, na)]
            f = lambda v, lim: f'{v:.2f}' if v is not None else f'>{lim:.1f}'
            print(f"tolerance θ={'π' if th == np.pi else 'π/2'} α_t={at} NA {na} n={n}: "
                  f"x_c {f(tx, MX * DX)} µm, z_c {f(tz, MZ * DZ)} µm")
    print(f"  paper model NA 0.5, θ={'π' if th == np.pi else 'π/2'}: x_c {ref[th][0]}, z_c {ref[th][1]}")

if not ONLY_SCALAR:
    fig, axes = plt.subplots(2, 2, figsize=(22.0, 18.0))
    cols = {0: '#1f77b4', 1: '#ff7f0e', 4: '#d62728'}
    nas = [na for na, _ in NAS]
    handles = []
    for r, (th, tl) in enumerate(((np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π'))):
        for c, (k, xl) in enumerate(((0, 'x$_c$'), (1, 'z$_c$'))):
            ax = axes[r, c]
            for at in ATS:
                v = [TOL[(th, at, na)][k] for na in nas]
                ok = [(na, y) for na, y in zip(nas, v) if y is not None]
                h, = ax.plot(*zip(*ok), 'o-', color=cols[at], lw=4, ms=14,
                             label='uniform, α$_t$ = 0' if at == 0 else f'Gaussian, α$_t$ = {at}')
                if r == 0 and c == 0:
                    handles.append(h)
            if ref[th][k] is not None:
                h, = ax.plot([0.5], [ref[th][k]], 'k*', ms=26, label='paper model, NA 0.5')
                if r == 0 and c == 0:
                    handles.append(h)
            ax.set_xlabel('NA (0.5 in air; 0.75, 0.9 in water)')
            ax.set_ylabel(f'{xl} costing 20% of peak (µm)')
            ax.set_title(f'2CE, {tl}, offset along {xl}')
            ax.set_xticks(nas); ax.set_ylim(bottom=0)
    fig.legend(handles=handles, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.04))
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(os.path.join(OUT, 'highna_tolerance_sweep.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved -> highna_tolerance_sweep.png')


# ── 2. scalar against vector, as NA grows ─────────────────────────────────
def fwhm(c, g):
    """Full width at half maximum of the central lobe, half-max crossings linearly interpolated."""
    c = c / c.max(); i = int(np.argmax(c)); l = r = i
    while l > 0 and c[l] >= 0.5:
        l -= 1
    while r < len(c) - 1 and c[r] >= 0.5:
        r += 1
    gl = np.interp(0.5, [c[l], c[l + 1]], [g[l], g[l + 1]])
    gr = np.interp(0.5, [c[r], c[r - 1]], [g[r], g[r - 1]])
    return gr - gl


SWEEP = {np.pi: np.round(np.arange(0.3, 0.951, 0.05), 2), np.pi / 2: np.round(np.arange(0.3, 0.701, 0.05), 2)}
RES = {}
for th in (np.pi, np.pi / 2):
    for na in SWEEP[th]:
        ax_ = 3.0 * L1 / na                          # window scales with the spot
        az_ = 3.0 * 2 * L1 / na ** 2
        g = np.linspace(-1, 1, 201)
        X, Z = np.meshgrid(ax_ * g, az_ * g)
        t = beam_I(X, Z, L1, na, 1.0) * beam_I(X, Z, L2, na, 1.0, th)
        a = beam_I(X, Z, L1, na, 1.0, model='paraxial') * beam_I(X, Z, L2, na, 1.0, th, model='paraxial')
        t, a = t / t.max(), a / a.max()
        c = linfoot.all_criteria(t, a)
        xs = np.linspace(-ax_, ax_, 6001); zs = np.linspace(-az_, az_, 12001)
        wx = [fwhm(beam_I(xs, 0 * xs, L1, na, 1.0, 0, m) * beam_I(xs, 0 * xs, L2, na, 1.0, th, m), xs)
              for m in ('paraxial', 'rw')]
        wz = [fwhm(beam_I(0 * zs, zs, L1, na, 1.0, 0, m) * beam_I(0 * zs, zs, L2, na, 1.0, th, m), zs)
              for m in ('paraxial', 'rw')]
        RES[(th, na)] = (c['F'], c['S'], c['Q'], wx[0] / wx[1], wz[0] / wz[1])
        print(f"scalar vs RW θ={'π' if th == np.pi else 'π/2'} NA {na}: F {c['F']:.4f} C {c['S']:.3f} "
              f"Q {c['Q']:.4f}; FWHM scalar/RW x {wx[0] / wx[1]:.3f} z {wz[0] / wz[1]:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(26.0, 11.0))
for th, tl, ls in ((np.pi, 'θ = π', '-'), (np.pi / 2, 'θ = π/2', '--')):
    nas_ = SWEEP[th]
    axes[0].plot(nas_, [RES[(th, na)][0] for na in nas_], ls, color='#d62728', lw=4, label=f'F, {tl}')
    axes[0].plot(nas_, [RES[(th, na)][2] for na in nas_], ls, color='#2ca02c', lw=4, label=f'Q, {tl}')
    axes[1].plot(nas_, [RES[(th, na)][3] for na in nas_], ls, color='#1f77b4', lw=4, label=f'width across, {tl}')
    axes[1].plot(nas_, [RES[(th, na)][4] for na in nas_], ls, color='#9467bd', lw=4, label=f'length along, {tl}')
for a in axes:
    a.axvline(0.5, color='#999999', lw=2, ls=':')
    a.set_xlabel('NA (air)')
axes[0].set_ylabel('Scalar PSF against vector PSF'); axes[0].set_title('Linfoot fidelity and correlation')
axes[1].set_ylabel('Scalar / vector width at half maximum'); axes[1].set_title('Spot size error of the scalar model')
axes[1].axhline(1, color='#999999', lw=2)
for a in axes:
    a.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'highna_scalar_vs_vector.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved -> highna_scalar_vs_vector.png')
