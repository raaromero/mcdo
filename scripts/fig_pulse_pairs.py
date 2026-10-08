r"""Which photon pairs of two pulses excite the 2CE transition, and how the dye's absorption weights them.

With pulses, a two-photon (two-colour) absorption takes one photon from each pulse; the pair excites the
molecule according to its total frequency Ω = ω_1 + ω_2 and the dye's absorption line shape g(Ω):

    rate ∝ ∫ g(Ω) |P̃(Ω)|² dΩ,      P(t) = E_1(t) E_2(t),   P̃(Ω) = ∫ Ẽ_1(ω) Ẽ_2(Ω − ω) dω

For a flat g this is ∫ |E_1|²|E_2|² dt = ∫ I_1 I_2 dt (Parseval): the time-overlap signal used so far.
Fields here are the pulse envelopes at the focus (transform-limited Gaussians, intensity FWHM τ).

    python scripts/fig_pulse_pairs.py
    -> output/08_two_color/lim2002/slides/pulse_pairs_spectrum.png, pulse_pairs_weight.png, pulse_pairs.csv
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28,
                            'xtick.labelsize': 24, 'ytick.labelsize': 24, 'legend.fontsize': 22})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides')
C = 299.792458                                   # nm·PHz → ω in rad/fs: ω = 2πc/λ with c = 299.79 nm/fs
L1, L2 = 750.0, 656.0
w1, w2 = 2 * np.pi * C / L1, 2 * np.pi * C / L2  # rad/fs


def field_t(w0, tau, t):
    return np.exp(-2 * np.log(2) * t ** 2 / tau ** 2) * np.exp(-1j * w0 * t)


def pair_spectrum(tau):
    """|P̃(Ω)|² on a fine grid: P(t) = E_1 E_2 has a Gaussian envelope exp(−4 ln2 t²/τ²), so its spectrum is
    exp(−(Ω − Ω_0)² τ² / (8 ln2)) about Ω_0 = ω_1 + ω_2 (exact for these pulses)."""
    W0 = w1 + w2
    W = np.linspace(W0 - 2.0, W0 + 2.0, 40001)
    return W, np.exp(-(W - W0) ** 2 * tau ** 2 / (8 * np.log(2)))


def parseval(tau):
    """Flat band: ∫ I_1 I_2 dt against ∫ |P̃(Ω)|² dΩ / 2π, both numerical."""
    t = np.linspace(-8 * tau, 8 * tau, 2 ** 16); dt = t[1] - t[0]
    P = field_t(w1, tau, t) * field_t(w2, tau, t)
    return np.sum(np.abs(P) ** 2) * dt, np.sum(np.abs(np.fft.fft(P)) ** 2) * dt / t.size


rows = []
fig, ax = plt.subplots(figsize=(5.8, 6.2))
for tau, col in ((100, '#1f77b4'), (20, '#d62728'), (10, '#2ca02c')):
    W, S = pair_spectrum(tau)
    lam = 2 * np.pi * C / W
    o = np.argsort(lam)
    ax.plot(lam[o], S[o] / S.max(), color=col, lw=4, label=f'τ = {tau} fs')
    fw = np.ptp(lam[S >= S.max() / 2])
    rows.append((tau, fw, *parseval(tau)))
ax.axvline(350, color='k', lw=2, ls='--')
ax.set_xlim(335, 365); ax.set_xlabel('Pair wavelength λ$_e$ (nm)')
ax.set_ylabel('Pairs, normalized')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'pulse_pairs_spectrum.png'), dpi=600, bbox_inches='tight'); plt.close(fig)

# fraction of the flat-band signal kept when the dye absorbs in a Gaussian band of FWHM Δλ around 350 nm
taus = np.array([5, 7, 10, 15, 20, 30, 50, 100, 200])
fig, ax = plt.subplots(figsize=(11.0, 7.0))
for bw, col, ls in ((2, '#9467bd', ':'), (5, '#1f77b4', '-'), (10, '#d62728', '--'), (20, '#2ca02c', '-.')):
    frac = []
    for tau in taus:
        W, S = pair_spectrum(tau)
        lam = 2 * np.pi * C / W
        g = np.exp(-4 * np.log(2) * (lam - 350) ** 2 / bw ** 2)
        frac.append(np.sum(g * S) / np.sum(S))
    ax.plot(taus, frac, ls, color=col, lw=4, marker='o', ms=8, label=f'band FWHM {bw} nm')
    rows.append(('band', bw, *np.round(frac, 4)))
ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100, 200]); ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel('Pulse duration τ (fs)'); ax.set_ylabel('Signal kept, weighted / flat')
ax.set_ylim(0, 1.05); ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'pulse_pairs_weight.png'), dpi=600, bbox_inches='tight'); plt.close(fig)

with open(os.path.join(OUT, 'pulse_pairs.csv'), 'w') as fh:
    for r in rows:
        fh.write(','.join(str(x) for x in r) + '\n')
for r in rows[:3]:
    print(f'τ {r[0]} fs: pair-wavelength FWHM {r[1]:.1f} nm; flat-band check ∫I1I2 dt = {r[2]:.6g}, ∫|P̃|² dΩ/2π = {r[3]:.6g}')
for r in rows[3:]:
    print('band', r[1], 'nm, kept at τ =', dict(zip(taus.tolist(), r[2:])))
