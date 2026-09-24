r"""The spectrum is still wide when the focus has stopped noticing it.

Two crossovers sit on the same axis and they are not the same crossover.

The spectral width falls as one over the duration, so it is still 22% of the
carrier at 5 fs and does not reach a tenth until about 11 fs. The depth of
focus stops responding much earlier: it is within 1% of its continuous-wave
value by 2 fs for a uniform pupil and by 5 fs for a truncated one, because the
depth depends on the transmitted angular band and that band carries no
wavelength.

So the optical effect vanishes while the pulse is still broadband. A 5 fs pulse
spans 675 to 843 nm and focuses to a depth indistinguishable from a single
wavelength.

    python scripts/fig_bandwidth_vs_effect.py
    -> output/05_pulsed_pupils/bandwidth_vs_effect.png
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

from mcdo import SimConfig
from mcdo.figio import save_panels

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '05_pulsed_pupils')
DUR = os.path.join(OUT, 'duration_sweep.npz')
if not os.path.exists(DUR):
    raise SystemExit('run scripts/verify_duration.py first')

d = np.load(DUR, allow_pickle=True)
names = [str(v) for v in d['input']]
LAM_C, N_MED = 0.750, 1.3
TAUS = [1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
cfg_c = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=np.inf,
                  N_freq=3, N_theta=101)
om_c = cfg_c.omega_c


def depth(inp, tau_fs, eps=0.0):
    for i in range(len(d['eps'])):
        if (names[i].startswith(inp) and float(d['eps'][i]) == eps
                and ((tau_fs is None and not np.isfinite(d['tau_fs'][i]))
                     or (tau_fs is not None and np.isfinite(d['tau_fs'][i])
                         and float(d['tau_fs'][i]) == tau_fs))):
            return float(d['depth_um'][i])
    return np.nan


fig, ax = plt.subplots(figsize=(11.0, 7.2))

tau_fine = np.logspace(np.log10(0.8), np.log10(40.0), 400)
frac = np.array([SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=t * 1e-15,
                           N_freq=3, N_theta=101).spectral_bandwidth
                 for t in tau_fine]) / om_c
ax.plot(tau_fine, 100.0 * frac, '-', color='#1d1d1f', lw=3.0,
        label='Spectral width, as a percentage of the carrier')

for inp, color, lab in (('uniform', '#1f77b4', 'Uniform'),
                        ('Gaussian', '#d62728', 'Gaussian, α = 4')):
    cw = depth(inp, None)
    y = [100.0 * abs(depth(inp, t) / cw - 1.0) for t in TAUS]
    ax.plot(TAUS, y, 'o-', color=color, lw=2.6, ms=9,
            label=f'{lab}, departure of the depth of focus')

ax.axhline(1.0, color='#bbbbbb', lw=1.8)
ax.text(24, 1.15, 'One percent', fontsize=10, color='#666666')
for inp, color, t_hit in (('uniform', '#1f77b4', 2.0),
                          ('Gaussian', '#d62728', 5.0)):
    ax.plot([t_hit, t_hit], [0.004, 1.0], ':', color=color, lw=2.0)
    ax.annotate(f'{t_hit:.0f} fs', xy=(t_hit, 0.006), fontsize=10,
                color=color, ha='center')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(0.8, 40)
ax.set_xlabel('Pulse duration (fs)')
ax.set_ylabel('Percent')
ax.set_title(''
             'Spectral width and depth-of-focus change against pulse duration\nNumerical aperture 0.8, 750 nm, no obstruction',
             fontsize=12)
ax.legend(fontsize=10, loc='lower left')
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'bandwidth_vs_effect')
out = os.path.join(OUT, 'bandwidth_vs_effect.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'duration':>10} {'width % of carrier':>20} {'uniform depth':>15} "
      f"{'Gaussian depth':>16}")
for t in TAUS:
    f = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=t * 1e-15,
                  N_freq=3, N_theta=101).spectral_bandwidth / om_c
    u = 100.0 * abs(depth('uniform', t) / depth('uniform', None) - 1.0)
    g = 100.0 * abs(depth('Gaussian', t) / depth('Gaussian', None) - 1.0)
    print(f'{t:>8.0f} fs {100 * f:>19.1f}% {u:>14.3f}% {g:>15.3f}%')
