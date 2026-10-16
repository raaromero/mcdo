r"""Figures for pulsed 2CE from the photon pairs that reach the transition, and for misalignment in time.

Results come from ``SIGNAL=pairs`` runs of run_pulsed_lim2002.py (scalar NA 0.5; scalar and vector at
the same NA, 0.7 and 0.9; τ = 10, 20, 100 fs) and the wavelength-count check (check_pair_count.py). The time-misalignment figures
follow the paper's figures for misalignment in space: the PSF (Fig. 3), the peak (Fig. 4) and Linfoot's
criteria (Figs. 5–6), here against the time delay Δt of pulse 2.

    python scripts/fig_pulsed_pairs.py
    -> output/08_two_color/lim2002/slides/pairs_*.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style, ring_labels
_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 30, 'xtick.labelsize': 28,
                            'ytick.labelsize': 28, 'legend.fontsize': 28})

from mcdo.pulsed2ce import two_color_pairs

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
PD = os.path.join(D, 'pulsed_lim2002')
OUT = os.path.join(D, 'slides')
LN2 = np.log(2)
TAUS = (10, 20, 100)
LS = {10: ':', 20: '-.', 50: '--', 100: '-'}                 # line style by pulse duration, as in the pairs figure
GEOM = (('pi', 'Facing lenses, θ = π'), ('pi2', 'Crossed lenses, θ = π/2'))
LEVELS = [1, 10, 20, 40, 60, 80]
RINGS = {1: 230, 10: 270, 20: 90}                     # label angles (degrees) of the outer rings, apart from each other


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight'); plt.close(fig); print('Saved ->', name)


def load(model, tau, kind='_pairs'):
    p = os.path.join(PD, f'{model}_tau{tau}{kind}.npz')
    return np.load(p) if os.path.exists(p) else None


def t20(r, peak):
    """Delay (in units of τ) at which the peak falls to 80%, from the positive side of the curve."""
    k = r >= 0
    r, p = r[k], peak[k]
    i = int(np.flatnonzero(p < 0.8)[0])
    return r[i - 1] + (r[i] - r[i - 1]) * (p[i - 1] - 0.8) / (p[i - 1] - p[i])


# ── wavelength count: largest change of the PSF against N = 257 ──
fig, axes = plt.subplots(1, 2, figsize=(15.5, 8.6), sharey=True)
for ax, (th, title) in zip(axes, GEOM):
    for f, lab, col in (('pairs_convergence_paraxial_na0.5.csv', 'scalar, NA 0.5', 'k'),
                        ('pairs_convergence_rw_na0.9.csv', 'vector, NA 0.9', '#d62728')):
        p = os.path.join(D, f)
        if not os.path.exists(p):
            continue
        a = np.genfromtxt(p, delimiter=',', names=True, dtype=None, encoding=None)
        for tau in TAUS:
            k = (a['tau_fs'] == tau) & (a['theta'] == th) & (a['n_wavelengths'] < 257)
            if not k.any():
                continue
            ax.plot(a['n_wavelengths'][k], a['max_change_rel_peak'][k], LS[tau], color=col, lw=4, marker='o', ms=9,
                    label=f'{lab}, τ = {tau} fs')
    ax.axvline(25, color='#ff7f0e', lw=3)
    ax.text(27, 3e-1, 'N = 25, used', color='#ff7f0e', fontsize=28, va='top')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(1e-8, 3)
    ax.set_xlabel('wavelengths per pulse, N'); ax.set_title(title)
axes[0].set_ylabel('largest change of the PSF\nrelative to its peak')
h, l = axes[0].get_legend_handles_labels()
plt.tight_layout(w_pad=2.0)
fig.legend(h, l, loc='center left', bbox_to_anchor=(1.0, 0.5), frameon=False)
save(fig, 'pairs_convergence.png')

# ── PSF against the time delay (as Fig. 3), facing and crossed, scalar NA 0.5 ──
for th, gname in GEOM:
    for tau in TAUS:
        d = load('scalar_na0.5', tau)
        if d is None:
            continue
        x, z, r = d[f'2ce_{th}_x'], d[f'2ce_{th}_z'], d[f'2ce_{th}_delays'] / tau
        fig, axes = plt.subplots(1, 3, figsize=(20.5, 8.4))
        for ax, v in zip(axes, (0.0, 0.5, 1.0)):
            M = 100 * d[f'2ce_{th}_delay_psf'][int(np.argmin(np.abs(r - v)))]
            cs = ax.contour(x, z, M, levels=[v_ for v_ in LEVELS if v_ < M.max()], colors='k', linewidths=2.2)
            ring_labels(ax, cs, (x[0, np.argmax(M.max(0))] if x.ndim == 2 else x[np.argmax(M.max(0))],
                                 z[np.argmax(M.max(1)), 0] if z.ndim == 2 else z[np.argmax(M.max(1))]), RINGS, 28)   # not 40-80
            if M.max() > 50:
                ax.contour(x, z, M, levels=[50], colors='#ff7f0e', linewidths=3.5)
            lab = 'Δt = 0' if v == 0 else f"Δt = {'τ/2' if v == 0.5 else 'τ'} = {v * tau:g} fs"
            ax.set_title(f'{lab}\npeak {M.max():.0f}%')
            ax.set_box_aspect(1.0); ax.set_xlabel('x (µm)'); ax.set_xticks([-1, 0, 1]); ax.set_yticks(np.arange(-4, 5, 2))
            if th == 'pi2':                                # the crossed spot is small along z
                ax.set_ylim(-1.5, 1.5); ax.set_yticks([-1, 0, 1])
            if th == 'pi':
                zm = 0.299792458 * v * tau / 2
                if abs(zm) < 5:
                    ax.axhline(zm, color='#1f77b4', lw=3, ls='--', label='plane where the pulses meet, z = cΔt/2n')
        axes[0].set_ylabel('z (µm)')
        plt.tight_layout()
        if th == 'pi':
            h, l = axes[0].get_legend_handles_labels()
            fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), frameon=False)
        save(fig, f'pairs_time_psf_{th}_tau{tau}.png')

# ── peak against the time delay (as Fig. 4), scalar 2CE at NA 0.5 ──
FOCUS = np.linspace(-2, 2, 401)
fig, axes = plt.subplots(1, 2, figsize=(22.0, 7.9), sharey=True)
for ax, (th, title) in zip(axes, GEOM):
    for tau in TAUS:
        d = load('scalar_na0.5', tau)
        if d is not None:
            ax.plot(d[f'2ce_{th}_delays'] / tau, d[f'2ce_{th}_delay_peak'], LS[tau], color='k', lw=4, label=f'τ = {tau} fs')
    ax.plot(FOCUS, np.exp(-2 * LN2 * FOCUS ** 2), '-', color='#ff7f0e', lw=2.5, label='at the focus, exp(−2 ln2 Δt²/τ²)')
    ax.set_xlabel('time delay Δt / τ'); ax.set_title(title); ax.set_xlim(-2, 2); ax.set_ylim(0, 1.05)
    ax.set_xticks([-2, -1, 0, 1, 2])
axes[0].set_ylabel('peak, relative to Δt = 0')
h, l = axes[0].get_legend_handles_labels()
plt.tight_layout(w_pad=2.0)
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False)
save(fig, 'pairs_time_peak.png')

# ── Linfoot's criteria against the time delay (as Figs. 5–6), scalar 2CE at NA 0.5 ──
for th, title in GEOM:
    fig, axes = plt.subplots(1, 3, figsize=(22.5, 7.9))
    for ax, (key, lab) in zip(axes, (('F', 'fidelity F'), ('C', 'structural content C'), ('Q', 'correlation quality Q'))):
        for tau in TAUS:
            d = load('scalar_na0.5', tau)
            if d is not None:
                ax.plot(d[f'2ce_{th}_delays'] / tau, d[f'2ce_{th}_delay_{key}'], LS[tau], color='k', lw=4, label=f'τ = {tau} fs')
        ax.set_xlabel('time delay Δt / τ'); ax.set_title(lab); ax.set_xlim(-2, 2); ax.set_xticks([-2, -1, 0, 1, 2])
    h, l = axes[0].get_legend_handles_labels()
    plt.tight_layout(w_pad=2.0)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    save(fig, f'pairs_time_linfoot_{th}.png')

# ── scalar 2CE against vector 2CE at the same NA: peak against the time delay, facing lenses ──
fig, axes = plt.subplots(1, 2, figsize=(22.0, 7.2), sharey=True)
for ax, na in zip(axes, ('0.7', '0.9')):
    for model, lab, col in ((f'scalar_na{na}', 'scalar 2CE', 'k'), (f'rw_na{na}', 'vector 2CE', '#d62728')):
        for tau in TAUS:
            d = load(model, tau)
            if d is not None:
                ax.plot(d['2ce_pi_delays'] / tau, d['2ce_pi_delay_peak'], LS[tau], color=col, lw=4,
                        label=f'{lab}, τ = {tau} fs')
    ax.set_xlabel('time delay Δt / τ'); ax.set_title(f'Facing lenses, NA {na}'); ax.set_xlim(-2, 2); ax.set_ylim(0, 1.05)
    ax.set_xticks([-2, -1, 0, 1, 2])
axes[0].set_ylabel('peak, relative to Δt = 0')
h, l = axes[0].get_legend_handles_labels()
order = [0, 3, 1, 4, 2, 5]                                    # columns by τ, rows scalar then vector
plt.tight_layout(w_pad=2.0)
fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3,
           frameon=False)
save(fig, 'pairs_time_samena.png')

# ── 20% tolerance in time: the delay that lowers the 2CE peak by 20%, against τ ──
# medium(th, na) → file suffix of the medium; KIND the suffix of the input ('' uniform, '_at4' Gaussian)
def tolerance(medium, kind_sfx, name, where, csv):
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(22.0, 7.2), sharey=True)
    NACOL = {'0.5': 'k', '0.7': '#1f77b4', '0.9': '#d62728'}
    for ax, (th, title) in zip(axes, GEOM):
        for kind, ls, mlab in (('scalar', '--', 'scalar 2CE'), ('rw', '-', 'vector 2CE')):
            for na in ('0.5', '0.7', '0.9'):
                model = f'{kind}_na{na}' + medium(th, na)
                tt = [(tau, t20(d[f'2ce_{th}_delays'] / tau, d[f'2ce_{th}_delay_peak']) * tau)
                      for tau in TAUS if (d := load(model, tau, '_pairs' + kind_sfx)) is not None and f'2ce_{th}_delays' in d]
                if tt:
                    ax.plot(*zip(*tt), ls, color=NACOL[na], lw=4, marker='o', ms=12, label=f'{mlab}, NA {na}')
                    rows += [(model + kind_sfx, th, tau, v) for tau, v in tt]
        tg = np.array([7, 140])
        ax.plot(tg, np.sqrt(np.log(1.25) / (2 * LN2)) * tg, ':', color='#ff7f0e', lw=3, label='at the focus, Δt = 0.40 τ')
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(7, 140)
        ax.set_xticks(TAUS); ax.set_xticklabels([str(t) for t in TAUS]); ax.minorticks_off()
        ax.set_xlabel('pulse duration τ (fs)'); ax.set_title(title + where(th))
    axes[0].set_ylabel('time delay for\n20% peak loss (fs)')
    axes[0].set_yticks([3, 10, 30, 100]); axes[0].set_yticklabels(['3', '10', '30', '100'])
    h, l = axes[0].get_legend_handles_labels()
    keys = ('scalar 2CE, NA 0.5', 'at the focus, Δt = 0.40 τ', 'scalar 2CE, NA 0.7', 'vector 2CE, NA 0.7',
            'scalar 2CE, NA 0.9', 'vector 2CE, NA 0.9')                                  # columns by NA
    order = [l.index(k) for k in keys if k in l]
    plt.tight_layout(w_pad=2.0)
    fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3,
               frameon=False)
    save(fig, name)
    with open(os.path.join(D, csv), 'w') as fh:
        fh.write('model,theta,tau_fs,delay_20pct_fs\n')
        for r_ in rows:
            fh.write(f'{r_[0]},{r_[1]},{r_[2]},{r_[3]:.3f}\n')


crossed_water = lambda th, na: '_n1.33' if th == 'pi2' and float(na) > 0.71 else ''      # crossed above 0.71: water
tolerance(crossed_water, '', 'pairs_time_tolerance.png', lambda th: ', NA 0.9 in water' if th == 'pi2' else '',
          'pairs_time_tolerance.csv')
tolerance(lambda th, na: '_n1.33', '', 'pairs_time_tolerance_water.png', lambda th: ', water', 'pairs_time_tolerance_water.csv')
tolerance(crossed_water, '_at4', 'pairs_time_tolerance_gaussian.png',
          lambda th: ', NA 0.9 in water' if th == 'pi2' else '', 'pairs_time_tolerance_gaussian.csv')   # input: slide title

# ── time delay with axial misalignment, facing lenses (peak over z_c and Δt) ──
fig, axes = plt.subplots(1, 3, figsize=(21.0, 8.0))
for ax, tau in zip(axes, TAUS):
    d = load('scalar_na0.5', tau)
    if d is None:
        continue
    zc, dl, M = d['2ce_pi_zc'], d['2ce_pi_delays'], 100 * d['2ce_pi_delay_z_peak']
    cs = ax.contour(zc, dl, M, levels=[10, 20, 40, 60, 80], colors='k', linewidths=2.2)
    ax.clabel(cs, fmt='%d', fontsize=28)
    ax.contour(zc, dl, M, levels=[50], colors='#ff7f0e', linewidths=3.5)
    ax.set_box_aspect(1.0); ax.set_title(f'τ = {tau} fs'); ax.set_xlabel('z$_c$ (µm)')
axes[0].set_ylabel('time delay Δt (fs)')
plt.tight_layout(); save(fig, 'pairs_time_z.png')

# ── what the pair condition changes: aligned peak against τ, equal pulse energies ──
taus = np.array([5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200], float)
pairs, every = [], []
for tau in taus:
    pairs.append(two_color_pairs(np.zeros(1), np.zeros(1), 0.5, tau1=tau, model='paraxial')[0])
    s = 2 * np.sqrt(LN2) / tau
    dets = np.linspace(-6, 6, 61) * s * np.sqrt(2)
    every.append(sum(two_color_pairs(np.zeros(1), np.zeros(1), 0.5, tau1=tau, model='paraxial', detuning=v)[0]
                     for v in dets) * (dets[1] - dets[0]))
pairs, every = np.array(pairs), np.array(every)
pairs, every = pairs / pairs[taus == 100][0], every / every[taus == 100][0]
fig, ax = plt.subplots(figsize=(12.5, 8.4))
ax.plot(taus, every, '-', color='#777777', lw=4, marker='o', ms=10, label='all pairs, ∫ I$_1$ I$_2$ dt')
ax.plot(taus, pairs, '-', color='k', lw=4, marker='o', ms=10, label='pairs that reach ν$_e$')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xticks([5, 10, 20, 50, 100, 200])
ax.set_xticklabels(['5', '10', '20', '50', '100', '200'])
ax.set_xlabel('pulse duration τ (fs)'); ax.set_ylabel('2CE peak at equal pulse energy,\nrelative to τ = 100 fs')
plt.tight_layout()
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=1, frameon=False)
save(fig, 'pairs_vs_every_pair.png')
print('peak ratio, every pair / pairs that reach ν_e, τ = 10 fs vs 100 fs:', every[taus == 10][0], pairs[taus == 10][0])
