r"""Cambaliza & Saloma (2000) Figs. 2-3 with optical pulses: transform-limited Gaussian pulses, zero delay.

Paraxial scalar model of the paper (Eq. 1, with the propagation phase), NA 0.5, circular pupils.
2CE: ∫ I₁(P, t) I₂(P, t) dt (mcdo.pulsed2ce.two_color_pulsed), λ₁ = 0.750 µm on L1, λ₂ = 0.656 µm on L2.
2PE: ∫ |E₁(P, t) + E₂(P, t)|⁴ dt, both pulses at λ_2p = 0.700 µm (same spectrum, so they interfere).
Pulse FWHM τ = 100, 20, 10 fs; continuous beams for reference. θ = 0, π/2, π.

    python scripts/cambaliza2000_pulses.py -> output/08_two_color/cambaliza2000/pulses/{axial_pi.png, widths.txt}
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.twobeam import beam_field, two_color, two_photon
from mcdo.pulsed2ce import two_color_pulsed, _fields, C_UM_FS

_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses')
os.makedirs(OUT, exist_ok=True)
NA, L1, L2, LP = 0.5, 0.750, 0.656, 0.700
TAUS = (100.0, 20.0, 10.0)
THETAS = ((0.0, 'θ = 0'), (np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π'))
xs = np.linspace(-1.0, 1.0, 801)
zs = np.linspace(-5.0, 5.0, 2001)


def two_photon_pulsed(x, z, theta, tau):
    """∫ |E₁ + E₂|⁴ dt for two equal pulses at λ_2p reaching their foci at t = 0."""
    reach = np.sqrt(np.max(x ** 2 + z ** 2)) / C_UM_FS
    tw = 3 * tau + reach
    dt = tau / 15
    t = np.arange(-tw, tw + dt / 2, dt)
    d1, c1, E1 = _fields(x, z, LP, tau, 2 * tw, NA, 1.0, 0.0, 0.0, 0.0, 'paraxial', None, None)
    _, _, E2 = _fields(x, z, LP, tau, 2 * tw, NA, 1.0, theta, 0.0, 0.0, 'paraxial', None, None)
    S = np.zeros(x.shape)
    for tt in t:
        ph = c1 * np.exp(-1j * d1 * tt)
        E = np.tensordot(ph, E1 + E2, axes=(0, 0))
        S += np.abs(E) ** 4 * dt
    return S


def fwhm(s, y):
    i0 = int(np.argmin(np.abs(s)))
    y = y / y[i0]
    r = i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    l = i0
    while l > 0 and y[l] >= 0.5:
        l -= 1
    if y[r] >= 0.5 or y[l] >= 0.5:
        return np.nan
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


P = {}
for axis, s in (('x', xs), ('z', zs)):
    X, Z = (s, 0 * s) if axis == 'x' else (0 * s, s)
    for th, _ in THETAS:
        P[('2PE', axis, th, 'cw')] = two_photon(beam_field(X, Z, LP, NA), beam_field(X, Z, LP, NA, theta=th))
        P[('2CE', axis, th, 'cw')] = two_color(beam_field(X, Z, L1, NA), beam_field(X, Z, L2, NA, theta=th))
        for tau in TAUS:
            P[('2PE', axis, th, tau)] = two_photon_pulsed(X, Z, th, tau)
            P[('2CE', axis, th, tau)] = two_color_pulsed(X, Z, NA, theta=th, tau1=tau, model='paraxial')
        print(f'{axis} θ = {th:.3f} done', flush=True)
np.savez(os.path.join(OUT, 'profiles.npz'), x=xs, z=zs,
         **{f'{k[0]}_{k[1]}_{k[2]:.4f}_{k[3]}': v for k, v in P.items()})

lines = ['signal axis θ | CW | 100 fs | 20 fs | 10 fs   (central-peak FWHM, µm)']
for sig in ('2PE', '2CE'):
    for axis, s in (('x', xs), ('z', zs)):
        for th, lab in THETAS:
            ws = [fwhm(s, P[(sig, axis, th, k)]) for k in ('cw',) + TAUS]
            lines.append(f'{sig} {axis} {lab} | ' + ' | '.join(f'{w:.3f}' for w in ws))
open(os.path.join(OUT, 'widths.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

# ── axial profiles at θ = π (head-on pulses), 2PE and 2CE ──
STY = {'cw': ('k', '-', 3.5, 'Continuous'), 100.0: ('#1f77b4', '--', 3, 'τ = 100 fs'),
       20.0: ('#ff7f0e', '-', 3, 'τ = 20 fs'), 10.0: ('#d62728', '-', 3, 'τ = 10 fs')}
fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.2), sharey=True)
for ax, sig in zip(axes, ('2PE', '2CE')):
    for k in ('cw',) + TAUS:
        c, ls, lw, lab = STY[k]
        v = P[(sig, 'z', np.pi, k)]
        ax.plot(zs, v / v.max(), ls, color=c, lw=lw, label=lab)
    ax.set_xlim(-5, 5); ax.set_ylim(0, 1.0); ax.set_xlabel('z (µm)'); ax.set_title(f'{sig}, axial, θ = π')
axes[0].set_ylabel('Intensity')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1), frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'axial_pi.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> axial_pi.png')
