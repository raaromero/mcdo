r"""Focal fields across obstruction ratio, one figure per truncation parameter.

The same configurations that `fig_master_grid` plots as curves, drawn as
two-dimensional fields on a shared axial scale so the elongation can be seen
rather than read off an axis. Half-maximum contour in orange, depth of focus in
the panel title.

Top row is continuous wave, bottom row a 1 fs pulse, on the same scale.

    python scripts/fig_alpha_fields.py
    -> output/03_annular/fields_alpha0.png
       output/03_annular/fields_alpha2.png
       output/03_annular/fields_alpha4.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.rw_integrals import compute_integrals

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)

LAM, N_MED, X_NA, NT = 0.750, 1.3, 0.8, 801
ALPHAS = [0.0, 2.0, 4.0]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9]
cfg = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)

rh = np.linspace(0.0, 2.5, 261)
rf = np.concatenate([-rh[::-1][:-1], rh])
z = np.linspace(-16.0, 16.0, 701)


NFREQ = 101


def _one(eps, at, k):
    apod = None if at == 0.0 else gaussian(at, cfg.sin2_alpha)
    if eps == 0.0:
        A = compute_integrals(rh, z, k, cfg.alpha, NT, apodization=apod)
    else:
        A = compute_integrals_annular(rh, z, k, cfg.alpha, eps, NT,
                                      apodization=apod)
    return vec_intensity(A[0], A[1], A[2])


def field(eps, at, tau=np.inf):
    if not np.isfinite(tau):
        I = _one(eps, at, cfg.k_c)
    else:
        c = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=tau,
                      N_freq=NFREQ, N_theta=NT)
        om = c.omega_grid()
        wt = c.spectral_power(om)
        I = np.zeros((len(z), len(rh)))
        for o, w in zip(om, wt):
            if o <= 0:
                continue
            I += w * _one(eps, at, c.k_for_omega(o))
    I = np.concatenate([I[:, ::-1][:, :-1], I], axis=1)
    return I / I.max()


def depth(I):
    ax = I[:, int(np.argmin(np.abs(rf)))]
    pk = int(np.argmax(ax))
    l = np.where(ax[:pk] < 0.5)[0][-1]
    r = pk + np.where(ax[pk:] < 0.5)[0][0]
    a = np.interp(0.5, [ax[l], ax[l + 1]], [z[l], z[l + 1]])
    b = np.interp(0.5, [ax[r], ax[r - 1]], [z[r], z[r - 1]])
    return b - a


ROWS = [(np.inf, 'Continuous wave'), (1e-15, '1 fs pulse')]

for at in ALPHAS:
    fig, axes = plt.subplots(len(ROWS), len(EPS),
                             figsize=(4.0 * len(EPS), 6.4 * len(ROWS)),
                             sharey=True, sharex=True)
    for row, (tau, rlab) in enumerate(ROWS):
        for col, eps in enumerate(EPS):
            ax = axes[row, col]
            I = field(eps, at, tau)
            m = ax.pcolormesh(rf, z, np.maximum(I, 1e-4), cmap='inferno',
                              norm=LogNorm(vmin=1e-4, vmax=1.0),
                              shading='auto')
            ax.contour(rf, z, I, levels=[0.5], colors=['#ff7f0e'],
                       linewidths=2.4)
            ax.set_title(f'Obstruction ratio {eps:g}: {depth(I):.2f} µm', fontsize=12)
            if row == len(ROWS) - 1:
                ax.set_xlabel('Radial position r (µm)')
            ax.set_xlim(-2.5, 2.5)
        axes[row, 0].set_ylabel(f'{rlab}\nAxial position z (µm)')
    name = 'Uniform (α = 0)' if at == 0.0 else f'α = {at:g}'
    fig.suptitle(f'{name}, numerical aperture 0.8, 750 nm — '
                 f'top row continuous wave, bottom row 1 fs pulse',
                 fontsize=12, y=0.99)
    fig.colorbar(m, ax=axes, label='Intensity, normalized to the peak',
                 fraction=0.02, pad=0.015)
    tag = f'alpha{int(at)}'
    out = os.path.join(OUT, f'fields_{tag}.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved -> {out}')

print(f"\n{'α':>4} {'source':<17} " + '  '.join(f'ε = {e:<5}' for e in EPS))
for at in ALPHAS:
    for tau, rlab in ROWS:
        print(f'{at:>4.0f} {rlab:<17} ' +
              '  '.join(f'{depth(field(e, at, tau)):7.2f} µm' for e in EPS))
