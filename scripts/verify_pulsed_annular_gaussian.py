"""Does the bandwidth invariance of the annular depth of focus survive a
Gaussian input?

The uniform case is known: the depth-of-focus extension a ring provides is the
same for a continuous wave and for a one femtosecond pulse. A truncated
Gaussian weights the pupil differently — it puts less light on the marginal
rays the ring keeps — so the extension itself is weaker, and the question is
whether spectral broadening now interacts with it.

Both illuminations are computed here in the same run, on the same grids and
with the same intensity definition (all three field components), so the
comparison is like for like.

    python scripts/verify_pulsed_annular_gaussian.py

Output: output/05_pulsed_pupils/verify_pulsed_annular_gaussian.png (+ panels/)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 401, 41      # 41 samples: convergence shown earlier
C_UM = 2.99792458e14
EPS = [0.0, 0.3, 0.5, 0.7, 0.9]
TAUS = [(np.inf, 'continuous wave'), (2e-15, '2 fs'), (1e-15, '1 fs')]
ILLUM = [(0.0, 'uniform'), (4.0, 'Gaussian, truncation coefficient 4')]
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
Z_UM = np.linspace(0.0, 60.0, 1200)              # on-axis, one side; profile is even


def axial_profile(tau, eps, alpha_t):
    """On-axis intensity against defocus, for one pulse width and pupil."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau, N_freq=NFREQ, N_theta=NT)
    apod = gaussian(alpha_t, cfg.sin2_alpha) if alpha_t > 0 else None
    r0 = np.array([0.0])
    if np.isinf(tau):
        I0, I1, I2 = compute_integrals_annular(r0, Z_UM, cfg.k_c, cfg.alpha, eps, NT,
                                               apodization=apod)
        return vec_intensity(I0[:, 0], I1[:, 0], I2[:, 0])
    total = np.zeros_like(Z_UM)
    omegas = cfg.omega_grid()
    weights = cfg.spectral_power(omegas)
    for om, w in zip(omegas, weights):
        if om <= 0:
            continue
        k = cfg.n * om / C_UM
        I0, I1, I2 = compute_integrals_annular(r0, Z_UM, k, cfg.alpha, eps, NT,
                                               apodization=apod)
        total += w * vec_intensity(I0[:, 0], I1[:, 0], I2[:, 0])
    return total


def depth_of_focus(profile):
    """Full width at half maximum of the even on-axis profile, in micrometres."""
    p = profile / profile.max()
    below = np.where(p < 0.5)[0]
    if below.size == 0:
        return float('nan')
    i = below[0]
    half = Z_UM[i - 1] + (Z_UM[i] - Z_UM[i - 1]) * (p[i - 1] - 0.5) / (p[i - 1] - p[i])
    return 2 * half


results = {}
for alpha_t, illum in ILLUM:
    for tau, tlabel in TAUS:
        dofs = [depth_of_focus(axial_profile(tau, e, alpha_t)) for e in EPS]
        results[(illum, tlabel)] = np.array(dofs)
        print(f'{illum:38s} {tlabel:16s} ' +
              '  '.join(f'{d:6.2f}' for d in dofs))

print('\nDepth of focus relative to the unobstructed pupil:')
print(f"{'illumination':>38} {'pulse':>16} " + ' '.join(f'{e:>7}' for e in EPS))
for (illum, tlabel), d in results.items():
    ratio = d / d[0]
    print(f'{illum:>38} {tlabel:>16} ' + ' '.join(f'{r:7.2f}' for r in ratio))

fig, axes = plt.subplots(1, 2, figsize=(20.5, 6.5))
styles = {'continuous wave': '-o', '2 fs': '--s', '1 fs': ':^'}
colors = {'uniform': '#1f77b4', 'Gaussian, truncation coefficient 4': '#0a3a66'}

ax = axes[0]
for (illum, tlabel), d in results.items():
    ax.plot(EPS, d / d[0], styles[tlabel], color=colors[illum], lw=2.0, ms=5,
            label=f'{"uniform" if illum == "uniform" else "Gaussian"}, {tlabel}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus, relative to no obstruction')
ax.set_title('(a) Depth of focus against obstruction ratio, 750 nm', fontsize=11)
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

ax = axes[1]
for illum, c in colors.items():
    cw = results[(illum, 'continuous wave')]
    one = results[(illum, '1 fs')]
    ax.plot(EPS, one / cw, '-o', color=c, lw=2.0, ms=5,
            label='uniform' if illum == 'uniform' else 'Gaussian')
ax.axhline(1.0, color='#999', ls=':', lw=1.2)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus, 1 fs relative to continuous wave')
ax.set_title('(b) Depth of focus, pulsed relative to continuous wave, 750 nm', fontsize=11)
ax.grid(alpha=0.25)
ax.legend(fontsize=9, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'verify_pulsed_annular_gaussian')
out = os.path.join(OUT, 'verify_pulsed_annular_gaussian.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
