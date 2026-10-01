r"""Lim & Saloma (2002) 2CE with pulses and a time delay: vector focus, air.

The signal is the time overlap ∫ I1(P,t) I2(P,t−Δt) dt (mcdo.pulsed2ce), for
transform-limited pulses of intensity FWHM τ = 100 fs and 20 fs, against the
continuous-wave (CW) signal I1 I2. λ1 = 750 nm, λ2 = 656 nm, both beams
unpolarized, uniform input. One part per process (PART):

  maps   aligned 2CE PSF at NA 0.5 on Lim & Saloma's axes (x ±1, z ±5 µm),
         θ = π and π/2, CW / 100 fs / 20 fs, contours at their levels
  delay  peak signal against Δt, θ = π and π/2, τ = 100 and 20 fs, NA 0.5;
         at θ = π also where the peak sits along z (the gate centre cΔt/2n)
  na     axial FWHM at θ = π against NA 0.2–0.99, CW / 100 fs / 20 fs, with
         the gate width c√2 τ/2n

    PART=maps  python scripts/fig_lim2002_pulsed.py
    -> output/08_two_color/lim2002/pulsed/pulsed_{maps,delay,na}.{npz,png}
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

from mcdo.pulsed2ce import C_UM_FS, gate_fwhm, two_color_cw, two_color_pulsed

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'pulsed')
os.makedirs(OUT, exist_ok=True)
PART = os.environ.get('PART', 'maps')
REPLOT = os.environ.get('REPLOT') == '1'
TAUS = (100.0, 20.0)
COL = {'CW': 'k', 100.0: '#1f77b4', 20.0: '#d62728'}
LAB = {'CW': 'CW', 100.0: 'τ = 100 fs', 20.0: 'τ = 20 fs'}
TH = {'pi': (np.pi, 'θ = π'), 'pi2': (np.pi / 2, 'θ = π/2')}
LEVELS = [1, 10, 20, 40, 60, 80]


def fwhm(z, p):
    p = p / p.max()
    above = np.nonzero(p >= 0.5)[0]
    i, j = above[0], above[-1]
    zl = z[i - 1] + (z[i] - z[i - 1]) * (0.5 - p[i - 1]) / (p[i] - p[i - 1])
    zr = z[j] + (z[j + 1] - z[j]) * (p[j] - 0.5) / (p[j] - p[j + 1])
    return zr - zl


def savefig(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', name, flush=True)


if PART == 'maps':
    path = os.path.join(OUT, 'pulsed_maps.npz')
    x, z = np.linspace(-1.0, 1.0, 101), np.linspace(-5.0, 5.0, 201)
    X, Z = np.meshgrid(x, z)
    if not REPLOT:
        d = {}
        for key, (th, _) in TH.items():
            d[f'{key}_CW'] = two_color_cw(X, Z, 0.5, theta=th)
            for tau in TAUS:
                d[f'{key}_{tau:g}'] = two_color_pulsed(X, Z, 0.5, theta=th, tau1=tau)
                np.savez_compressed(path, x_um=x, z_um=z, **d)
                print(key, tau, 'fs done', flush=True)
    d = np.load(path)
    fig, axes = plt.subplots(2, 3, figsize=(21.0, 17.0))
    for r, (key, (th, tl)) in enumerate(TH.items()):
        for c, lab in enumerate(('CW', 100.0, 20.0)):
            F = d[f'{key}_{"CW" if lab == "CW" else f"{lab:g}"}']
            F = 100 * F / F.max()
            ax = axes[r, c]
            cs = ax.contour(x, z, F, levels=LEVELS, colors='k', linewidths=2.0)
            ax.clabel(cs, fmt='%d', fontsize=24)
            ax.set_box_aspect(1.0)
            ax.set_xticks([-1, 0, 1]); ax.set_yticks([-4, -2, 0, 2, 4])
            ax.set_xlabel('x (µm)')
            if c == 0:
                ax.set_ylabel('z (µm)')
            ax.set_title(f'{tl}, {LAB[lab]}')
            iz = np.argmin(np.abs(x))
            print(f'{tl} {LAB[lab]}: axial FWHM {fwhm(z, F[:, iz]):.3f} µm, lateral FWHM '
                  f'{fwhm(x, F[np.argmin(np.abs(z)), :]):.3f} µm')
    fig.suptitle('Aligned 2CE PSF with pulses, vector focus, NA 0.5, air', fontsize=32, y=1.0)
    plt.tight_layout()
    savefig(fig, 'pulsed_maps.png')

elif PART == 'delay':
    path = os.path.join(OUT, 'pulsed_delay.npz')
    grids = {'pi': np.meshgrid(np.linspace(-1.0, 1.0, 41), np.linspace(-8.0, 8.0, 161)),
             'pi2': np.meshgrid(np.linspace(-1.0, 1.0, 41), np.linspace(-1.0, 1.0, 41))}
    delays = {100.0: np.linspace(-300, 300, 25), 20.0: np.linspace(-60, 60, 25)}
    if not REPLOT:
        d = {}
        for key, (th, _) in TH.items():
            X, Z = grids[key]
            for tau in TAUS:
                S = two_color_pulsed(X, Z, 0.5, theta=th, tau1=tau, delay=delays[tau])
                d[f'{key}_{tau:g}_peak'] = S.reshape(len(S), -1).max(axis=1)
                d[f'{key}_{tau:g}_zpeak'] = np.array([Z.ravel()[np.argmax(s)] for s in S.reshape(len(S), -1)])
                d[f'delays_{tau:g}'] = delays[tau]
                np.savez_compressed(path, **d)
                print(key, tau, 'fs done', flush=True)
    d = np.load(path)
    fig, axes = plt.subplots(1, 3, figsize=(30.0, 9.0))
    for key, (th, tl) in TH.items():
        for tau in TAUS:
            dl, pk = d[f'delays_{tau:g}'], d[f'{key}_{tau:g}_peak']
            i0 = np.argmin(np.abs(dl))
            axes[0 if key == 'pi' else 1].plot(dl / tau, 100 * pk / pk[i0], 'o-', color=COL[tau], lw=3, ms=8,
                                               label=LAB[tau])
            lost = 100 * (1 - pk / pk[i0])
            pos = dl >= 0
            cross = np.interp(20.0, lost[pos], dl[pos]) if lost[pos].max() >= 20 else np.nan
            print(f'{tl}, {LAB[tau]}: 20% of the peak lost at Δt = {cross:.1f} fs ({cross / tau:.2f} τ)')
    for a, key in zip(axes[:2], TH):
        a.set_xlabel('Delay Δt / τ'); a.set_ylabel('Peak signal (% of Δt = 0)')
        a.set_title(TH[key][1]); a.axhline(80, color='#999999', lw=2, ls=':')
        a.set_ylim(0, 105)
    for tau in TAUS:
        dl, zp = d[f'delays_{tau:g}'], d[f'pi_{tau:g}_zpeak']
        axes[2].plot(dl, zp, 'o', color=COL[tau], ms=9, label=LAB[tau])
    dd = np.linspace(-300, 300, 200)
    axes[2].plot(dd, C_UM_FS * dd / 2, '--', color='#555555', lw=2.5, label='cΔt/2n')
    axes[2].set_xlim(-310, 310); axes[2].set_ylim(-6, 6)
    axes[2].set_xlabel('Delay Δt (fs)'); axes[2].set_ylabel('z of the peak (µm)'); axes[2].set_title('θ = π, where the peak sits')
    h, l = axes[2].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    fig.suptitle('2CE peak against the delay between the pulses, vector focus, NA 0.5', fontsize=32, y=1.04)
    plt.tight_layout()
    savefig(fig, 'pulsed_delay.png')

elif PART == 'na':
    path = os.path.join(OUT, 'pulsed_na.npz')
    nas = np.array([0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99])
    if not REPLOT:
        rows = []
        for na in nas:
            half = 3.0 * 0.750 / na ** 2 + 2.0 * gate_fwhm(100.0)
            z = np.linspace(-half, half, int(round(2 * half / min(0.05, 0.02 / na ** 2 * 2))) + 1)
            x = np.zeros_like(z)
            row = [na, fwhm(z, two_color_cw(x, z, na))]
            row += [fwhm(z, two_color_pulsed(x, z, na, tau1=tau)) for tau in TAUS]
            rows.append(row)
            np.savez_compressed(path, rows=np.array(rows))
            print(f'NA {na}: axial FWHM CW {row[1]:.3f}, 100 fs {row[2]:.3f}, 20 fs {row[3]:.3f} µm', flush=True)
    rows = np.load(path)['rows']
    fig, axes = plt.subplots(1, 2, figsize=(22.0, 9.0))
    for j, lab in enumerate(('CW', 100.0, 20.0)):
        axes[0].plot(rows[:, 0], rows[:, 1 + j], 'o-', color=COL[lab], lw=3, ms=9, label=LAB[lab])
        if lab != 'CW':
            axes[0].axhline(gate_fwhm(lab), color=COL[lab], lw=2, ls='--')
            axes[1].plot(rows[:, 0], 100 * (1 - rows[:, 1 + j] / rows[:, 1]), 'o-', color=COL[lab], lw=3, ms=9)
    axes[0].set_yscale('log'); axes[0].set_xlabel('NA'); axes[0].set_ylabel('Depth of focus (µm)')
    axes[0].set_title('θ = π; dashed: gate c√2 τ/2n')
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
    axes[1].set_xlabel('NA'); axes[1].set_ylabel('Shortening against CW (%)'); axes[1].set_title('How much the pulse shortens the focus')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    fig.suptitle('2CE depth of focus with pulses against NA, vector model, air', fontsize=32, y=1.04)
    plt.tight_layout()
    savefig(fig, 'pulsed_na.png')
