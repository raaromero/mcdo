r"""Why a uniform annulus is bandwidth invariant and a truncated one is not.

The extension an annulus gives is a ratio of two depths of focus, so it is
unchanged by anything that lengthens both by the same factor. This draws that
factor directly: R = depth at 1 fs over depth at continuous wave, for the same
pupil.

Under uniform illumination R is 1.009 at every obstruction ratio, constant to
0.02%. Both depths in the extension broaden identically and the ratio cancels,
which is what bandwidth invariance is. Under a truncated Gaussian R starts at
1.091 unobstructed and decays onto the uniform value as the ring thins, because
at ratio 0.99 the two pupils pass the same rim rays and are the same pupil. The
measured erosion is exactly that decay: 1 - R(eps)/R(0), drawn against the
sweep in the third panel.

What is not explained here is why R is 1.09 for a truncated Gaussian and 1.009
for a uniform pupil. At 1 fs the spectrum spans (0, 2 omega_c), so the wave
number varies by a factor of two and this is not a small-perturbation argument.

Sweeps only. Nothing is recomputed.

    python scripts/fig_bandwidth_response.py
    -> output/05_pulsed_pupils/bandwidth_response.png
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

from mcdo.figio import save_panels

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
GRID = os.path.join(OUT, 'pulsed_annular_grid.npz')
APS = os.path.join(OUT, 'pulsed_annular_apertures.npz')
for p in (GRID, APS):
    if not os.path.exists(p):
        raise SystemExit(f'missing {p}')

g = np.load(GRID, allow_pickle=True)
a = np.load(APS, allow_pickle=True)
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
NAS = [0.1, 0.8, 1.2]
COLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}
STYLE = {'uniform': ('#1f77b4', 'o-'), 'Gaussian': ('#d62728', 's--')}


def _rows(na):
    return (g, False) if na == 0.8 else (a, True)


def depth(na, inp, eps, tau):
    src, has_na = _rows(na)
    names = [str(v) for v in src['input']]
    taus = [str(v) for v in src['tau']]
    for i in range(len(src['eps'])):
        if (names[i].startswith(inp) and float(src['eps'][i]) == eps
                and taus[i] == tau and (not has_na or float(src['na'][i]) == na)):
            return float(src['depth_um'][i])
    return np.nan


def R(na, inp, eps, tau='1 fs'):
    return depth(na, inp, eps, tau) / depth(na, inp, eps, 'continuous wave')


def gain(na, inp, eps, tau):
    src, has_na = _rows(na)
    names = [str(v) for v in src['input']]
    taus = [str(v) for v in src['tau']]
    for i in range(len(src['eps'])):
        if (names[i].startswith(inp) and float(src['eps'][i]) == eps
                and taus[i] == tau and (not has_na or float(src['na'][i]) == na)):
            return float(src['gain'][i])
    return np.nan


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the factor itself, at the deck's aperture ─────────────────────────────
ax = axes[0, 0]
for inp, lab in (('uniform', 'Uniform'), ('Gaussian', 'Gaussian, alpha = 4')):
    color, style = STYLE[inp]
    ax.plot(EPS, [R(0.8, inp, e) for e in EPS], style, color=color, lw=2.2,
            ms=8, label=lab)
ax.axhline(1.0, color='#999999', lw=1.2)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth at 1 fs, divided by depth at continuous wave')
ax.set_title('Uniform illumination — '
             'Numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

# ── the same factor across apertures, truncated pupil ─────────────────────
ax = axes[0, 1]
for na in NAS:
    ax.plot(EPS, [R(na, 'Gaussian', e) for e in EPS], 'o-', color=COLOR[na],
            lw=2.2, ms=8, label=f'Numerical aperture {na:g}')
ax.axhline(1.0091, color='#999999', ls=':', lw=1.6)
ax.text(0.30, 1.0115, 'the uniform value, 1.009', fontsize=9, color='#666666')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth at 1 fs, divided by depth at continuous wave')
ax.set_title('Gaussian, α = 4 — '
             'Gaussian, alpha = 4, 750 nm', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

# ── the erosion reconstructed from the factor ─────────────────────────────
ax = axes[1, 0]
for na in NAS:
    measured = [100.0 * (1.0 - gain(na, 'Gaussian', e, '1 fs')
                         / gain(na, 'Gaussian', e, 'continuous wave'))
                for e in EPS]
    predicted = [100.0 * (1.0 - R(na, 'Gaussian', e) / R(na, 'Gaussian', 0.0))
                 for e in EPS]
    ax.plot(EPS, measured, 'o', color=COLOR[na], ms=10,
            label=f'Measured, numerical aperture {na:g}')
    ax.plot(EPS, predicted, '-', color=COLOR[na], lw=2.0,
            label=f'From the broadening factor, {na:g}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Extension lost at 1 fs (%)')
ax.set_title('Extension lost at 1 fs against obstruction ratio — numerical aperture 0.8, 750 nm',
             fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

# ── where the two responses differ: the unobstructed focus ────────────────
ax = axes[1, 1]
for inp, lab in (('uniform', 'Uniform'), ('Gaussian', 'Gaussian, alpha = 4')):
    color, _ = STYLE[inp]
    for tau, ls, alpha_v in (('continuous wave', '-', 1.0), ('1 fs', ':', 0.85)):
        key = f'0.8|{inp if inp == "uniform" else "Gaussian, alpha = 4"}|0.0|{tau}|z'
        if key not in g.files:
            continue
        p = g[key]
        z, y = p[0], p[1] / p[1].max()
        ax.plot(z, y, ls, color=color, lw=2.2, alpha=alpha_v,
                label=f'{lab}, {tau}')
ax.axhline(0.5, color='#999999', lw=1.2)
ax.set_xlim(0, 4)
ax.set_xlabel('Axial position (um)')
ax.set_ylabel('On-axis intensity, normalized to the peak')
ax.set_title('On-axis intensity at obstruction ratio 0 — numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'bandwidth_response')
out = os.path.join(OUT, 'bandwidth_response.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nBroadening factor R and the erosion it accounts for')
print(f"{'NA':>5} {'input':<10} " + ' '.join(f'{e:>7}' for e in EPS))
for na in NAS:
    for inp in ('uniform', 'Gaussian'):
        row = ' '.join(f'{R(na, inp, e):>7.4f}' for e in EPS)
        print(f'{na:>5} {inp:<10} {row}')
