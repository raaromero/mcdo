r"""Color changes nothing for continuous light, and something for a pulse.

The Richards-Wolf integral sees the axial coordinate only through k z and the
radial one only through k r, so changing wavelength rescales every length and
leaves every ratio untouched. The extension an annulus gives is therefore
exactly color independent, and the depth of focus itself is exactly
proportional to wavelength. The top row shows both, measured rather than
assumed.

A pulse breaks that symmetry, because its bandwidth is fixed by the duration
and not by the color. At 1 fs the full width is 441 THz whatever the carrier,
so the fractional bandwidth runs from 0.74 at 500 nm to 1.47 at 1000 nm and the
same pulse is relatively twice as broadband in the infrared. The bottom row
shows what that does: nothing to a uniform pupil, and a doubling of the
erosion for a truncated one.

    python scripts/fig_wavelength.py
    -> output/03_annular/wavelength.png
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

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '03_annular')
CW = os.path.join(OUT, 'wavelength_sweep.npz')
PL = os.path.join(ROOT, 'output', '05_pulsed_pupils', 'wavelength_pulsed.npz')
for p in (CW, PL):
    if not os.path.exists(p):
        raise SystemExit(f'missing {p}')

c = np.load(CW, allow_pickle=True)
p = np.load(PL, allow_pickle=True)
c_in = [str(v) for v in c['input']]
p_in = [str(v) for v in p['input']]
p_tau = [str(v) for v in p['tau']]

LAMS = [0.500, 0.750, 1.000]
NAS = [0.1, 0.8, 1.2]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
LCOLOR = {0.500: '#1f77b4', 0.750: '#d62728', 1.000: '#2ca02c'}
NCOLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}
STYLE = {0.500: 'o-', 0.750: 's--', 1.000: '^:'}


def cw(lam, na, inp, eps, field):
    for i in range(len(c['eps'])):
        if (float(c['lam'][i]) == lam and float(c['na'][i]) == na
                and c_in[i].startswith(inp) and float(c['eps'][i]) == eps):
            return float(c[field][i])
    return np.nan


def pulsed(lam, na, inp, eps, tau, field):
    for i in range(len(p['eps'])):
        if (float(p['lam'][i]) == lam and float(p['na'][i]) == na
                and p_in[i].startswith(inp) and float(p['eps'][i]) == eps
                and p_tau[i] == tau):
            return float(p[field][i])
    return np.nan


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the extension is the same at every color ─────────────────────────────
ax = axes[0, 0]
for lam in LAMS:
    y = [cw(lam, 0.8, 'uniform', e, 'gain') for e in EPS]
    ax.plot(EPS, y, STYLE[lam], color=LCOLOR[lam], lw=2.2, ms=9,
            label=f'Wavelength {lam * 1000:.0f} nm')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Depth-of-focus extension against obstruction ratio, three center wavelengths — uniform, numerical aperture 0.8, continuous wave', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── while the depth itself scales with it ─────────────────────────────────
ax = axes[0, 1]
for na in NAS:
    d = [cw(lam, na, 'uniform', 0.0, 'depth_um') for lam in LAMS]
    ax.plot([l * 1000 for l in LAMS], d, 'o-', color=NCOLOR[na], lw=2.2, ms=9,
            label=f'Numerical aperture {na:g}')
    ref = d[1] * np.array(LAMS) / 0.750
    ax.plot([l * 1000 for l in LAMS], ref, 'k:', lw=2.0)
ax.set_yscale('log')
ax.set_xlabel('Center wavelength (nm)')
ax.set_ylabel('Depth of focus (um)')
ax.set_title('Depth of focus against center wavelength; dotted lines are '
             'exact proportionality\nUniform, obstruction ratio 0, continuous wave',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── a pulse is relatively broader in the infrared ─────────────────────────
ax = axes[1, 0]
frac = [(4 * np.log(2) / 1e-15) / (2 * np.pi * 2.99792458e14 / lam)
        for lam in LAMS]
for na in NAS:
    for inp, style, lab in (('uniform', 'o-', 'Uniform'),
                            ('Gaussian', 's--', 'Gaussian, alpha = 4')):
        y = [pulsed(lam, na, inp, 0.0, '1 fs', 'depth_um')
             / pulsed(lam, na, inp, 0.0, 'continuous wave', 'depth_um')
             for lam in LAMS]
        ax.plot(frac, y, style, color=NCOLOR[na], lw=2.0, ms=8,
                alpha=1.0 if inp == 'uniform' else 0.75,
                label=f'{lab}, numerical aperture {na:g}')
ax.axhline(1.0, color='#999999', lw=1.2)
ax.set_xlabel('Bandwidth divided by carrier frequency, at 1 fs')
ax.set_ylabel('Focus lengthening at 1 fs')
ax.set_title('Focus lengthening at 1 fs against relative bandwidth — obstruction ratio 0; 500, 750 and 1000 nm', fontsize=12)
ax.legend(fontsize=8, ncol=2)
ax.grid(alpha=0.25)

# ── so the truncated pupil loses more extension in the infrared ───────────
ax = axes[1, 1]
for na in NAS:
    for inp, style, lab in (('uniform', 'o-', 'Uniform'),
                            ('Gaussian', 's--', 'Gaussian, alpha = 4')):
        y = []
        for lam in LAMS:
            g_cw = pulsed(lam, na, inp, 0.99, 'continuous wave', 'gain')
            g_p = pulsed(lam, na, inp, 0.99, '1 fs', 'gain')
            y.append(100.0 * (1.0 - g_p / g_cw))
        ax.plot([l * 1000 for l in LAMS], y, style, color=NCOLOR[na], lw=2.0,
                ms=8, alpha=1.0 if inp == 'uniform' else 0.75,
                label=f'{lab}, numerical aperture {na:g}')
ax.axhline(0.0, color='#999999', lw=1.2)
ax.set_xlabel('Center wavelength (nm)')
ax.set_ylabel('Extension lost at 1 fs (%)')
ax.set_title('Extension lost at 1 fs against center wavelength — obstruction ratio 0.99', fontsize=12)
ax.legend(fontsize=8, ncol=2)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'wavelength')
out = os.path.join(OUT, 'wavelength.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nContinuous wave: extension spread across all colors run')
worst = 0.0
for na in NAS:
    for inp in ('uniform', 'Gaussian'):
        for e in EPS[1:]:
            g = [cw(lam, na, inp, e, 'gain') for lam in LAMS]
            worst = max(worst, max(g) / min(g) - 1)
print(f'  largest spread over every configuration: {100 * worst:.5f}%')
