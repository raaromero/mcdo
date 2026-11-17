r"""What a transform-limited Gaussian pulse contains, in time and in frequency (pulse extension of Cambaliza & Saloma 2000).

First figure: (a) the Gaussian spectrum of a 10-fs pulse at 750 nm, with nine frequencies marked; (b) the continuous
waves at those frequencies, each with its weight a(ω), all present at all times; (c) their sum over the whole spectrum:
the waves are in phase at t = 0 and drift out of phase away from it, so the sum falls off as a Gaussian of width τ.
Second figure: (a) the intensity in time, a Gaussian of FWHM τ (pulse width), for 5, 10, 20 and 100 fs; (b) the power
spectrum against frequency, a Gaussian of FWHM Δν = 0.441/τ (spectral bandwidth), at 750 and 656 nm; (c) the same
against wavelength, per unit wavelength. The visible range (380–750 nm) is shaded and 428 THz (700 nm) marked.

    E(t) = ∫ a(ω) e^{−iωt} dω,  a(ω) = exp[−(ω − ω₀)² τ² / (8 ln 2)],  |E(t)|² = exp(−4 ln 2 t²/τ²)

    python scripts/cambaliza2000_pulse_time_frequency.py -> output/08_two_color/cambaliza2000/pulses/{pulse_waves, pulse_gaussian}.png (one slide each)
    PANELS=1 python scripts/cambaliza2000_pulse_time_frequency.py -> the same, at most two panels across:
        pulse_waves_spectrum.png ((a), (b)), pulse_waves_sum.png ((c)), pulse_gaussian_time_frequency.png ((a), (b)),
        pulse_gaussian_wavelength.png ((c))
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
matplotlib.rcParams.update({'font.size': 26, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses')
C = 0.299792458                                                    # µm/fs
LN2 = np.log(2)
TAU_COL = {5: '#b07aa1', 10: '#e15759', 20: '#f28e2b', 100: '#4e79a7'}
VIS = (380, 750)                                                    # visible range, nm


def weight(w, w0, tau):
    return np.exp(-(w - w0) ** 2 * tau ** 2 / (8 * LN2))


tau, lam = 10.0, 0.750
w0 = 2 * np.pi * C / lam
s = 2 * np.sqrt(LN2) / tau                                          # standard deviation of a(ω), rad/fs
t = np.linspace(-30, 30, 4001)
wk = w0 + np.linspace(-2, 2, 9) * s                                 # nine continuous waves across the spectrum
cols = plt.cm.turbo(np.linspace(0.95, 0.08, len(wk)))               # low frequency red, high frequency blue


def waves(ax, fs=22):
    """(b) the nine waves, offset for clarity, over a short stretch so the crests can be followed."""
    ta = np.linspace(-4, 20, 3001)
    for j, (w, c) in enumerate(zip(wk, cols)):
        ax.plot(ta, 2.2 * j + weight(w, w0, tau) * np.cos(w * ta), color=c, lw=1.6 if fs == 22 else 2.2)
    for t0, ls, lab in ((0, '-', 'in phase'), (15, '--', 'out of phase')):
        ax.axvline(t0, color='k', lw=2, ls=ls)
        ax.text(t0 + 0.3, 2.2 * len(wk) - 0.5, lab, ha='left' if t0 == 0 else 'center', va='bottom', fontsize=fs,
                bbox=dict(fc='white', ec='none', pad=2))
    ax.set_ylim(-1.5, 2.2 * len(wk) + 0.9)
    ax.set_yticks(2.2 * np.arange(len(wk)), [f'{1e3 * w / (2 * np.pi):.0f}' for w in wk])
    ax.set_xlabel('Time t (fs)'); ax.set_xlim(-4, 20)
    ax.set_title('(b) Waves at these frequencies')
    ax.tick_params(labelleft=False)


def spectrum(sp):
    """(a) the Gaussian weight of each frequency, on the same frequency axis as (b)."""
    wc = w0 + np.linspace(-2.6, 2.6, 400) * s
    yc = 2.2 * (2 * (wc - w0) / s + 4)                              # wave j sits at 2.2 j, frequency w0 + (j/2 − 2) s
    sp.plot(weight(wc, w0, tau), yc, color='k', lw=2.4)
    sp.scatter(weight(wk, w0, tau), 2.2 * np.arange(len(wk)), c=cols, s=140, zorder=3)
    sp.set_xlim(1.1, 0); sp.set_xticks([1, 0.5, 0])
    sp.set_xlabel('Weight a(ω)'); sp.set_ylabel('Frequency (THz)')
    sp.set_title('(a) Spectrum')


def pulse_sum(ax, fs=22):
    """(c) the sum over the whole spectrum."""
    wf = w0 + np.linspace(-3.5, 3.5, 401) * s
    E = (weight(wf, w0, tau)[:, None] * np.exp(-1j * np.outer(wf, t))).sum(0)
    E /= np.abs(E).max()
    ax.set_title('(c) Their sum, the pulse')
    ax.plot(t, E.real, color='#d62728', lw=1.8 if fs == 22 else 2.2, label='field E(t)')
    ax.plot(t, np.abs(E), ':', color='0.35', lw=2.4, label='envelope |E(t)|')
    ax.plot(t, -np.abs(E), ':', color='0.35', lw=2.4)
    ax.set_xlabel('Time t (fs)'); ax.set_ylabel('Field, normalized to its peak (a.u.)'); ax.set_ylim(-1.1, 1.4)
    for t0, ls in ((0, '-'), (15, '--')):                            # the same two times as in (b)
        ax.axvline(t0, color='k', lw=2, ls=ls)
    ax.legend(loc='upper center', ncol=2, frameon=False, fontsize=fs)


def intensity(ax, fs=22):
    """(a) intensity in time."""
    tt = np.linspace(-120, 120, 4001)
    for T, c in TAU_COL.items():
        ax.plot(tt, np.exp(-4 * LN2 * tt ** 2 / T ** 2), color=c, lw=3)
    ax.axhline(0.5, color='0.5', lw=1.2 if fs == 22 else 2, ls=':')
    ax.set_xlabel('Time t (fs)'); ax.set_ylabel('Intensity |E(t)|², normalized (a.u.)'); ax.set_ylim(0, 1.08)
    ax.set_title('(a) Intensity in time, FWHM τ')


def spectra(ax, x, to_nu, jac):
    """Power spectrum of each pulse at 750 and 656 nm on the axis x, each of its peak; jac = 1/λ² per unit wavelength."""
    nu = to_nu(x)
    for T, c in TAU_COL.items():
        for lm, ls in ((0.750, '-'), (0.656, '--')):
            S = np.exp(-4 * LN2 * (nu - 1e3 * C / lm) ** 2 / (0.441 / T * 1e3) ** 2) * jac(x)
            ax.plot(x, S / S.max(), ls, color=c, lw=2.6)
    ax.set_ylim(0, 1.12); ax.set_ylabel('Power spectrum, normalized (a.u.)')


def against_frequency(ax, fs=22):
    """(b) against frequency; the visible range shaded, 700 nm (428 THz) marked."""
    nu = np.linspace(280, 620, 3001)                                # THz
    spectra(ax, nu, lambda v: v, lambda v: 1.0)
    ax.axvspan(1e3 * C / (VIS[1] * 1e-3), 1e3 * C / (VIS[0] * 1e-3), color='#fff3b0', zorder=0)
    ax.axvline(1e3 * C / 0.700, color='k', lw=1.6 if fs == 22 else 2, ls=':')
    ax.text(1e3 * C / 0.700 + 3, 1.02, '428 THz', fontsize=fs, va='bottom')
    ax.set_xlim(nu[0], nu[-1]); ax.set_xlabel('Frequency ν (THz)')
    ax.set_title('(b) Spectrum, FWHM Δν = 0.441/τ')


def against_wavelength(ax, fs=22):
    """(c) against wavelength, per unit wavelength."""
    lam = np.linspace(480, 1070, 4001)                              # nm
    spectra(ax, lam, lambda l: 1e3 * C / (l * 1e-3), lambda l: 1 / l ** 2)
    ax.axvspan(*VIS, color='#fff3b0', zorder=0)
    ax.axvline(700, color='k', lw=1.6 if fs == 22 else 2, ls=':')
    ax.text(703, 1.02, '700 nm', fontsize=fs, va='bottom')
    ax.set_xlim(lam[0], lam[-1]); ax.set_xlabel('Wavelength λ (nm)')
    ax.set_title('(c) Spectrum against wavelength')


def keys():
    h = [plt.Line2D([], [], color=c, lw=3) for c in TAU_COL.values()] + \
        [plt.Line2D([], [], color='k', lw=2.6, ls='-'), plt.Line2D([], [], color='k', lw=2.6, ls='--'),
         plt.Rectangle((0, 0), 1, 1, fc='#fff3b0')]
    return h, [f'τ = {T} fs' for T in TAU_COL] + ['750 nm (L1)', '656 nm (L2)', f'visible, {VIS[0]}–{VIS[1]} nm']


if os.environ.get('PANELS'):
    # PANELS=1: the same curves, at most two panels across, for slides (fonts 32, 28, 24; about 11 × 10 in per panel;
    # 600 DPI). Writes new files and leaves pulse_waves.png and pulse_gaussian.png as they are.
    matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                                'ytick.labelsize': 24, 'legend.fontsize': 24, 'figure.dpi': 100})
    strip = lambda ax: ax.set_title(ax.get_title()[4:])
    fig = plt.figure(figsize=(16, 10))
    g = fig.add_gridspec(1, 2, width_ratios=[0.45, 1], wspace=0.06)
    sp = fig.add_subplot(g[0]); ax = fig.add_subplot(g[1], sharey=sp)
    spectrum(sp); waves(ax, 24); strip(sp); strip(ax)
    fig.savefig(os.path.join(OUT, 'pulse_waves_spectrum.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 10))
    pulse_sum(ax, 24); ax.set_title('Sum of the waves at all frequencies')
    fig.savefig(os.path.join(OUT, 'pulse_waves_sum.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
    fig, a2 = plt.subplots(1, 2, figsize=(22, 10))
    fig.subplots_adjust(wspace=0.28)
    intensity(a2[0], 24); against_frequency(a2[1], 24); strip(a2[0]); strip(a2[1])
    fig.legend(*keys(), loc='lower center', bbox_to_anchor=(0.5, a2[0].get_position().y1 + 0.05), ncol=4, frameon=False, handlelength=1.6,
               columnspacing=1.2)
    fig.savefig(os.path.join(OUT, 'pulse_gaussian_time_frequency.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 10))
    against_wavelength(ax, 24); strip(ax)
    fig.legend(*keys(), loc='lower center', bbox_to_anchor=(0.5, ax.get_position().y1 + 0.05), ncol=3, frameon=False, handlelength=1.6,
               columnspacing=1.2)
    fig.savefig(os.path.join(OUT, 'pulse_gaussian_wavelength.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
    print('Saved ->', OUT, 'pulse_waves_spectrum.png, pulse_waves_sum.png, pulse_gaussian_time_frequency.png, '
          'pulse_gaussian_wavelength.png')
    sys.exit()

fig = plt.figure(figsize=(24, 7.8))
gw = fig.add_gridspec(1, 3, width_ratios=[0.45, 1, 1], wspace=0.08)
sp = fig.add_subplot(gw[0])
ax = {(0, 0): fig.add_subplot(gw[1], sharey=sp), (0, 1): fig.add_subplot(gw[2])}
waves(ax[0, 0])
spectrum(sp)
pulse_sum(ax[0, 1])
fig.subplots_adjust(wspace=0.08)
pos = ax[0, 1].get_position(); ax[0, 1].set_position([pos.x0 + 0.05, pos.y0, pos.width - 0.05, pos.height])
fig.savefig(os.path.join(OUT, 'pulse_waves.png'), dpi=250, bbox_inches='tight'); plt.close(fig)

fig, a2 = plt.subplots(1, 3, figsize=(30, 7.8))
fig.subplots_adjust(wspace=0.26)
intensity(a2[0])
against_frequency(a2[1])
against_wavelength(a2[2])
fig.legend(*keys(), loc='lower center', bbox_to_anchor=(0.5, 0.93), ncol=7, frameon=False)
fig.savefig(os.path.join(OUT, 'pulse_gaussian.png'), dpi=250, bbox_inches='tight'); plt.close(fig)
print('Saved ->', OUT, 'pulse_waves.png, pulse_gaussian.png')
