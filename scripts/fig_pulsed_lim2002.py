r"""Figures for the pulsed 2CE deck: the Gaussian pulse step by step, and the pulsed results.

Setup figures are analytic. Results come from run_pulsed_lim2002.py (scalar NA 0.5; τ = 10, 20, 100 fs) and are compared with the continuous-beam (CW) PSFs on the same grid. 2CE uses the
photon pairs that reach the transition (SIGNAL=pairs runs); 2PE the overlap in time. The 2CE results against
the time delay are in fig_pulsed_pairs.py.

    python scripts/fig_pulsed_lim2002.py
    -> output/08_two_color/lim2002/slides/pulse_*.png
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28,
                            'xtick.labelsize': 24, 'ytick.labelsize': 24, 'legend.fontsize': 22})

from mcdo.twobeam import beam_field, intensity

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
PD = os.path.join(D, 'pulsed_lim2002')
OUT = os.path.join(D, 'slides')
C = 0.299792458                                  # µm/fs
BLUE, RED, GREEN, GREY = '#1f77b4', '#d62728', '#2ca02c', '#777777'
LN2 = np.log(2)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight'); plt.close(fig); print('Saved ->', name)


# ── 1. a pulse in time: carrier under a Gaussian envelope; intensity with its FWHM ──
tau = 20.0
t = np.linspace(-40, 40, 4001)
w0 = 2 * np.pi * C / 0.75
A = np.exp(-2 * LN2 * t ** 2 / tau ** 2)
fig, axes = plt.subplots(2, 1, figsize=(7.2, 8.0))
axes[0].plot(t, A * np.cos(w0 * t), color=BLUE, lw=1.5, label='field E(t)')
axes[0].plot(t, A, color=RED, lw=4, label='envelope A(t)'); axes[0].plot(t, -A, color=RED, lw=4)
axes[0].set_xlabel('t (fs)'); axes[0].set_ylim(-1.15, 1.15)
axes[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=1, frameon=False, fontsize=24)
axes[1].plot(t, A ** 2, color=RED, lw=4)
axes[1].annotate('', xy=(tau / 2, 0.5), xytext=(-tau / 2, 0.5), arrowprops=dict(arrowstyle='<->', lw=3))
axes[1].set_xlabel('t (fs)'); axes[1].set_title('Intensity I(t)')
axes[1].text(13.5, 0.5, 'FWHM = τ', ha='left', va='center', fontsize=24)      # beside the arrow, clear of the curve; axes[1].set_ylim(0, 1.1)
plt.tight_layout(); save(fig, 'pulse_in_time.png')

# ── 2. a pulse is a sum of frequencies: three, nine and many frequencies added ──
fig, axes = plt.subplots(1, 3, figsize=(16.4, 5.4), sharey=True)
s = 2 * np.sqrt(LN2) / tau
for ax, n in zip(axes, (3, 9, 201)):
    w = w0 + np.linspace(-3.5 * s, 3.5 * s, n)
    a = np.exp(-(w - w0) ** 2 / (2 * s ** 2))
    f = (a[:, None] * np.cos(np.outer(w, t))).sum(0)
    ax.plot(t, f / np.abs(f).max(), color=BLUE, lw=1.5)
    ax.set_title(f'{n} frequencies'); ax.set_xlabel('t (fs)')
axes[0].set_ylabel('field, normalized')
plt.tight_layout(); save(fig, 'pulse_sum_of_frequencies.png')

# ── 3. facing pulses meet: intensity along z at four times, and where both are present ──
z = np.linspace(-15, 15, 3001)
fig, axes = plt.subplots(1, 4, figsize=(17.0, 5.0), sharey=True)
for ax, tt in zip(axes, (-30, -15, 0, 15)):
    I1 = np.exp(-4 * LN2 * (tt - z / C) ** 2 / tau ** 2)       # pulse 1 travels +z, at z = c t
    I2 = np.exp(-4 * LN2 * (tt + z / C) ** 2 / tau ** 2)       # pulse 2 travels −z, at z = −c t
    ax.plot(z, I1, color=RED, lw=3.5, label='pulse 1 (750 nm)'); ax.plot(z, I2, color=BLUE, lw=3.5, label='pulse 2 (656 nm)')
    ax.fill_between(z, I1 * I2, color=GREEN, alpha=0.5, lw=0, label='both present')
    ax.set_title(f't = {tt} fs'); ax.set_xlabel('z (µm)')
axes[0].set_ylabel('intensity')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.15), frameon=False)
plt.tight_layout(); save(fig, 'pulse_facing_meet.png')

# ── 4. overlap against time delay: exp(−2 ln2 (Δt/τ)²), and where the slab sits ──
x = np.linspace(-2.5, 2.5, 501)
fig, axes = plt.subplots(1, 2, figsize=(16.4, 6.4))
axes[0].plot(x, np.exp(-2 * LN2 * x ** 2), color=GREEN, lw=4)
for v in (0.5, 1.0, 1.5):
    y = np.exp(-2 * LN2 * v ** 2); axes[0].plot(v, y, 'ko', ms=10); axes[0].text(v + 0.1, y + 0.05, f'{y:.2f}', fontsize=24)
axes[0].set_xlabel('Δt / τ'); axes[0].set_ylabel('overlap at the focus'); axes[0].set_ylim(0, 1.1)
axes[0].set_title('Crossed')
zz = np.linspace(-6, 6, 1201)
for dt_, col in ((0, GREEN), (10, '#ff7f0e'), (20, '#9467bd')):
    axes[1].plot(zz, np.exp(-2 * LN2 * (2 * zz / C - dt_) ** 2 / tau ** 2), color=col, lw=4, label=f'Δt = {dt_} fs')
axes[1].set_xlabel('z (µm)'); axes[1].set_ylabel('overlap'); axes[1].set_ylim(0, 1.1)
axes[1].set_title('Facing, τ = 20 fs')
axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
plt.tight_layout(); save(fig, 'pulse_overlap.png')

# ── results ──
TAUS = (100, 20, 10)
x = np.arange(-50, 51) * 0.02; zg = np.arange(-100, 101) * 0.05
X, Z = np.meshgrid(x, zg)
LAMS = {'2ce': (0.75, 0.656), '2pe': (0.7, 0.7)}
TH = {'pi': np.pi, 'pi2': np.pi / 2}


def cw_psf(pair, th, xc=0.0, zc=0.0):
    la, lb = LAMS[pair]
    U1, U2 = beam_field(X, Z, la, 0.5), beam_field(X, Z, lb, 0.5, theta=TH[th], xc=xc, zc=zc)
    F = intensity(U1) * intensity(U2) if pair == '2ce' else intensity(U1 + U2) ** 2
    return F / F.max()


def load(model, tau, pair='2pe'):
    return np.load(os.path.join(PD, f'{model}_tau{tau}' + ('_pairs' if pair == '2ce' else '') + '.npz'))


LEVELS = [1, 10, 20, 40, 60, 80]
RINGS = {1: 230, 10: 270, 20: 90}                     # label angles (degrees) of the outer rings, apart from each other
ZWIN = {('2ce', 'pi2'): 1.5, ('2pe', 'pi2'): 3.0}    # half-window along z (µm): crossed spots are small along z
for key, xc_, zc_, title in (('psf2', 0.0, 0.0, 'aligned'), ('psf3', 0.4, 1.0, 'misaligned')):
    for pair in ('2ce', '2pe'):
        for th in ('pi', 'pi2'):
            fig, axes = plt.subplots(1, 4, figsize=(19.5, 7.6))
            panels = [('CW', cw_psf(pair, th, xc_, zc_))] + [(f'τ = {tau} fs', load('scalar_na0.5', tau, pair)[f'{pair}_{th}_{key}'])
                                                             for tau in TAUS]
            zw = ZWIN.get((pair, th))
            if zw:                                     # window along z, centred on the CW peak to the nearest 0.5 µm
                z0 = np.round(2 * zg[np.unravel_index(np.argmax(panels[0][1]), panels[0][1].shape)[0]]) / 2
            for ax, (lab, M) in zip(axes, panels):
                M = 100 * M / M.max()
                cs = ax.contour(x, zg, M, levels=LEVELS, colors='k', linewidths=1.8)
                if (pair, th) != ('2pe', 'pi'):        # the 2PE standing wave along z leaves no room for labels
                    ring_labels(ax, cs, (x[np.argmax(M.max(0))], zg[np.argmax(M.max(1))]), RINGS, 24)   # not 40-80
                ax.contour(x, zg, M, levels=[50], colors='#ff7f0e', linewidths=3)
                ax.set_box_aspect(1.0); ax.set_title(lab); ax.set_xlabel('x (µm)')
                ax.set_xticks([-1, 0, 1]); ax.set_yticks(np.arange(-4, 5, 2))
                if zw:
                    ax.set_ylim(z0 - zw, z0 + zw); ax.set_yticks(np.arange(np.ceil(z0 - zw), np.floor(z0 + zw) + 1, 1 if zw < 2 else 2))
            axes[0].set_ylabel('z (µm)')
            plt.tight_layout(); save(fig, f'pulse_{key}_{pair}_{th}.png')

# peak maps (Fig. 4) pulsed against CW, 2CE facing and crossed
for pair in ('2ce', '2pe'):
    for th in ('pi', 'pi2'):
        fig, axes = plt.subplots(1, 3, figsize=(17.0, 7.4))
        for ax, tau in zip(axes, TAUS):
            d = load('scalar_na0.5', tau, pair)
            la = LAMS[pair][0]
            M = 100 * d[f'{pair}_{th}_peak']
            cs = ax.contour(d[f'{pair}_{th}_xc'] / la, d[f'{pair}_{th}_zc'] / la, M, levels=[10, 20, 40, 60, 80], colors='k', linewidths=1.8)
            ax.clabel(cs, fmt='%d', fontsize=24)
            ax.contour(d[f'{pair}_{th}_xc'] / la, d[f'{pair}_{th}_zc'] / la, M, levels=[50], colors='#ff7f0e', linewidths=3)
            ax.set_box_aspect(1.0); ax.set_title(f'τ = {tau} fs')
            u = 'λ$_1$' if pair == '2ce' else 'λ$_{2p}$'
            ax.set_xlabel(f'x$_c$ ({u})')
        axes[0].set_ylabel(f'z$_c$ ({u})')
        plt.tight_layout(); save(fig, f'pulse_peakmap_{pair}_{th}.png')

# peak against the time delay, 2PE, scalar, three pulse lengths, with the closed form at the focus
for pair in ('2pe',):
    fig, axes = plt.subplots(1, 2, figsize=(16.4, 6.8), sharey=True)
    for ax, th, lab in ((axes[0], 'pi', 'θ = π'), (axes[1], 'pi2', 'θ = π/2')):
        for tau, col in zip(TAUS, (BLUE, RED, GREEN)):
            d = load('scalar_na0.5', tau)
            r = d[f'{pair}_{th}_delays'] / tau
            ax.plot(r, d[f'{pair}_{th}_delay_peak'], 'o-', color=col, lw=3.5, ms=8, label=f'τ = {tau} fs')
        rr = np.linspace(-2, 2, 401)
        ax.plot(rr, np.exp(-2 * LN2 * rr ** 2), '--', color='k', lw=3, label='overlap at the focus')
        if pair == '2pe':
            ax.axhline(1 / 8, color=GREY, lw=2, ls=':')
        ax.set_title(lab); ax.set_xlabel('Δt / τ'); ax.set_ylim(0, 1.05)
    axes[0].set_ylabel('peak, relative to Δt = 0')
    h, l = axes[0].get_legend_handles_labels()
    plt.tight_layout()
    fig.legend(h, l, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 0.0), frameon=False, fontsize=24)
    save(fig, f'pulse_delay_peak_{pair}.png')
