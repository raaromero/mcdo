r"""Videos of the two pulses passing through the common focus, with the 2CE they leave (NA 0.5, paraxial, zero delay).

Frames in time t (fs; t = 0 when both pulse centres reach the focus). Top row, x–z maps: I₁(x, z, t) (750 nm, lens
L1, travelling +z), I₂(x, z, t) (656 nm, lens L2, rotated by θ), their product I₁·I₂ (where the pulses overlap now),
and the 2CE accumulated up to t, |A(x, z, t)|², counting all photon pairs from both beams (narrow 350-nm transition, phase-locked):

    A(P, t) = ∫₋∞ᵗ E(P, t′)² e^{iω_e t′} dt′ = A₁₁ + 2A₁₂ + A₂₂     (cambaliza2000_pulses_allpairs.py),

each map on a fixed colour scale (its maximum over the run), with iso-value lines at 0.25, 0.5 and 0.75 of the
frame's own maximum. Middle row, along the axis (x = 0): I₁ and I₂ now, I₁·I₂
now, and the 2CE accumulated up to t (all pairs) against the total accumulated as the pulses pass the focus and the
continuous-beam profile. Bottom row: the spectrum of each pulse arriving at the focus now (its full spectrum, scaled by
the pulse's intensity at the focus), and 428 THz (700 nm), where two photons of one beam reach 350 nm.

With --2pe both pulses are at 700 nm (2PE, Eq. 6 of the paper). The same sum then holds all three terms at resonance for
any τ: A₁₁ and A₂₂ (350-nm pairs within one pulse) wherever that pulse passes, and 2A₁₂ (350-nm pairs across the pulses) only where
the two pulses overlap; the continuous-beam profile is |U₁ + U₂|⁴.

    python scripts/cambaliza2000_pulse_video.py [--2pe] [tau_fs ...]   (default 5 10 20 100; θ = 0, π/2, π for each)
    -> output/08_two_color/cambaliza2000/pulses/video/pulse_<2ce|2pe>_<θ>_tau<τ>.mp4 and still frames
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.colors import PowerNorm
from scipy.interpolate import CubicSpline

from mcdo.style import apply as _apply_style
from mcdo.pulsed2ce import _fields, C_UM_FS
from mcdo.twobeam import beam_field
from mcdo.cutinset import place_legend

_apply_style()
plt.rcParams.update({'font.size': 15, 'axes.titlesize': 16, 'axes.labelsize': 15, 'xtick.labelsize': 13,
                     'ytick.labelsize': 13, 'legend.fontsize': 13, 'axes.grid': False})
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'video')
os.makedirs(OUT, exist_ok=True)
NA, N, LE = 0.5, 1.0, 0.350
WE = 2 * np.pi * C_UM_FS / LE                                      # rad/fs
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
XH, ZH = 1.5, 5.0                                                   # half-widths of the map, µm
THETAS = {'0': (0.0, 'collinear lenses, θ = 0'), 'pi2': (np.pi / 2, 'crossed lenses, θ = π/2'),
          'pi': (np.pi, 'facing lenses, θ = π')}
N_FRAMES = 180
CONTOURS = [0.25, 0.5, 0.75]                                        # of each frame's own maximum


class Beam:
    """Spectral samples of one pulse on a set of points; envelope at any time t."""

    def __init__(self, x, z, lam, tau, theta, window):
        self.dw, self.c, self.E = _fields(x, z, lam, tau, window, NA, N, theta, 0.0, 0.0, 'paraxial', None, None)
        self.nu = (self.dw + 2 * np.pi * C_UM_FS / lam) / (2 * np.pi) * 1e3      # THz

    def at(self, t):
        return (self.c * np.exp(-1j * self.dw * t)) @ self.E

    def spectrum(self, i0):
        S = np.abs(self.c * self.E[:, i0]) ** 2
        return self.nu, S / S.max()


def compute(tau, tk, sig='2ce'):
    """All frames of one run: maps, axis lines, spectra at the focus, the continuous-beam profile."""
    theta = THETAS[tk][0]
    L1, L2 = LAMS[sig]
    W1, W2 = 2 * np.pi * C_UM_FS / L1, 2 * np.pi * C_UM_FS / L2
    xs, zs = np.linspace(-XH, XH, 61), np.linspace(-ZH, ZH, 201)
    X, Z = np.meshgrid(xs, zs)
    zf = np.linspace(-ZH, ZH, 1001)                                 # axis line, fine enough for 0.35-µm fringes
    px = np.concatenate([X.ravel(), 0 * zf])
    pz = np.concatenate([Z.ravel(), zf])
    nm = X.size
    reach = N * np.hypot(XH, ZH) / C_UM_FS
    dt = min(tau / 20, 0.4)                                         # resolves ω₂ − ω₁ = 0.36 rad/fs (2CE)
    t = np.arange(-(2 * tau + reach), 2 * tau + reach + dt / 2, dt)
    window = 2 * (3 * tau + reach)
    b1, b2 = Beam(px, pz, L1, tau, 0.0, window), Beam(px, pz, L2, tau, theta, window)
    every = max(1, int(np.ceil(len(t) / N_FRAMES)))
    kf = np.arange(0, len(t), every)
    A11 = np.zeros(px.size, complex); A12 = np.zeros_like(A11); A22 = np.zeros_like(A11)
    fr = {q: [] for q in ('I1', 'I2', 'P', 'all', 'one')}
    i0 = nm + np.argmin(np.abs(zf))
    a1, a2 = [], []
    for k, tt in enumerate(t):
        e1, e2 = b1.at(tt), b2.at(tt)
        A11 += e1 * e1 * np.exp(1j * (WE - 2 * W1) * tt) * dt
        A12 += e1 * e2 * np.exp(1j * (WE - W1 - W2) * tt) * dt
        A22 += e2 * e2 * np.exp(1j * (WE - 2 * W2) * tt) * dt
        if k in kf or k == len(t) - 1:
            I1, I2 = np.abs(e1) ** 2, np.abs(e2) ** 2
            now = I1 * I2 if sig == '2ce' else np.abs(e1 + e2) ** 4      # 2PE: the two 700-nm fields add (Eq. 6 at this instant)
            for q, v in (('I1', I1), ('I2', I2), ('P', now), ('all', np.abs(A11 + 2 * A12 + A22) ** 2),
                         ('one', np.abs(2 * A12) ** 2)):
                fr[q].append(v)
            a1.append(I1[i0]); a2.append(I2[i0])
    tf = t[np.append(kf, len(t) - 1) if kf[-1] != len(t) - 1 else kf]
    fr = {q: np.array(v) for q, v in fr.items()}
    a1, a2 = np.array(a1) / max(a1), np.array(a2) / max(a2)
    maps = {q: fr[q][:, :nm].reshape((len(tf),) + X.shape) for q in fr}
    line = {q: fr[q][:, nm:] for q in fr}
    fin_all = line['all'][-1].max()
    u1, u2 = beam_field(0 * zf, zf, L1, NA), beam_field(0 * zf, zf, L2, NA, theta=theta)
    cw = np.abs(u1) ** 2 * np.abs(u2) ** 2 if sig == '2ce' else np.abs(u1 + u2) ** 4
    cw /= cw.max()

    nu1, S1 = b1.spectrum(i0); nu2, S2 = b2.spectrum(i0)
    return dict(xs=xs, zs=zs, zf=zf, tf=tf, maps=maps, line=line, fin_all=fin_all, cw=cw, a1=a1, a2=a2,
                spec=(nu1, S1, nu2, S2))


def run(tau, tk, sig='2ce'):
    theta, label = THETAS[tk]
    L1, L2 = LAMS[sig]
    SIG = sig.upper()
    n1, n2 = f'{L1 * 1e3:.0f} nm', f'{L2 * 1e3:.0f} nm'
    D = compute(tau, tk, sig)
    xs, zs, zf, tf, maps, line, fin_all, cw, a1, a2 = (D[k] for k in ('xs', 'zs', 'zf', 'tf', 'maps', 'line', 'fin_all', 'cw', 'a1', 'a2'))
    nu1, S1, nu2, S2 = D['spec']

    fig = plt.figure(figsize=(19, 13))
    gs = fig.add_gridspec(3, 4, height_ratios=[1.35, 1, 0.85])
    top = [fig.add_subplot(gs[0, c]) for c in range(4)]
    mid = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2:])]
    axs = fig.add_subplot(gs[2, :])
    ext = (-XH, XH, ZH, -ZH)                                        # z downwards, as in the setup diagram
    ims = []
    for a, q, ttl, cm in ((top[0], 'I1', f'I₁, {n1}, L1', 'Reds'), (top[1], 'I2', f'I₂, {n2}, L2', 'Blues'),
                          (top[2], 'P', 'I₁·I₂ now, where the pulses overlap' if sig == '2ce' else '|E₁ + E₂|⁴ now', 'Purples'),
                          (top[3], 'all', f'{SIG} accumulated up to t', 'Greys')):
        ims.append(a.imshow(maps[q][0], extent=ext, aspect='auto', cmap=cm,
                            norm=PowerNorm(0.45, vmin=0, vmax=maps[q].max()), interpolation='bilinear'))
        a.set_title(ttl); a.set_xlabel('x (µm)')        # γ = 0.45: the weak pulse far from the focus stays visible
        a.axvline(0, color='k', lw=0.6, ls=':')
    top[0].set_ylabel('z (µm)')
    l1, = mid[0].plot(zf, line['I1'][0] / line['I1'].max(), color='#d62728', lw=2.5, label='I₁')
    l2, = mid[0].plot(zf, line['I2'][0] / line['I2'].max(), color='#1f77b4', lw=2.5, label='I₂')
    mid[0].set_title('I₁, I₂ along the axis, now')
    lp, = mid[1].plot(zf, line['P'][0] / line['P'].max(), color='#6a3d9a', lw=2.5)
    mid[1].set_title('I₁·I₂ along the axis, now' if sig == '2ce' else '|E₁ + E₂|⁴ along the axis, now')
    mid[2].plot(zf, cw, color='k', lw=1.8, ls='--', label='continuous beams')
    mid[2].plot(zf, line['all'][-1] / fin_all, color='0.6', lw=1.2, label=f'total {SIG}')
    la, = mid[2].plot(zf, line['all'][0] / fin_all, color='k', lw=2.6, label=f'{SIG} accumulated up to t')
    mid[2].set_title(f'{SIG} along the axis, accumulated up to t')
    for a in mid:
        a.set_xlim(-ZH, ZH); a.set_ylim(0, 1.05); a.set_xlabel('z (µm), at x = 0')
    mid[2].set_ylim(0, 1.25)
    mid[0].set_ylabel('Of its maximum')
    nug = np.linspace(300, 560, 800)
    smooth = lambda nu, S: np.where((nug > nu[0]) & (nug < nu[-1]), np.clip(CubicSpline(nu, S)(nug), 0, None), 0)
    sp1, sp2 = smooth(nu1, S1), smooth(nu2, S2)
    s1, = axs.plot(nug, sp1 * a1[0], color='#d62728', lw=3, label=f'beam 1 ({n1}) at the focus')
    s2, = axs.plot(nug, sp2 * a2[0], color='#1f77b4', lw=3, label=f'beam 2 ({n2}) at the focus')
    axs.plot(nug, sp1, color='#d62728', lw=1, ls=':'); axs.plot(nug, sp2, color='#1f77b4', lw=1, ls=':')
    axs.axvline(C_UM_FS / 0.700 * 1e3, color='k', ls='--', lw=1.5, label='428 THz (700 nm): two photons of one beam reach 350 nm')
    axs.set_xlim(300, 560); axs.set_ylim(0, 1.05); axs.set_xlabel('Frequency (THz)'); axs.set_ylabel('Spectrum now')
    axs.set_title('Spectrum arriving at the focus now, with the full spectrum dotted')
    sup = fig.suptitle('', fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    place_legend(mid[0], fontsize=11); place_legend(mid[2], fontsize=11); place_legend(axs, fontsize=12)

    cs = []

    def frame(k):
        for c in cs:                                                # iso-value lines of this frame
            c.remove()
        cs.clear()
        for a, im, q in zip(top, ims, ('I1', 'I2', 'P', 'all')):
            im.set_data(maps[q][k])
            m = maps[q][k]
            if m.max() > 0.01 * maps[q].max():
                cs.append(a.contour(xs, zs, m / m.max(), levels=CONTOURS, colors='0.15', linewidths=1.0))
        l1.set_ydata(line['I1'][k] / line['I1'].max()); l2.set_ydata(line['I2'][k] / line['I2'].max())
        lp.set_ydata(line['P'][k] / line['P'].max())
        la.set_ydata(line['all'][k] / fin_all)
        s1.set_ydata(sp1 * a1[k]); s2.set_ydata(sp2 * a2[k])
        sup.set_text(f'{label}, τ = {tau:g} fs, NA {NA}, zero delay, t = {tf[k]:+.1f} fs')
        return ims + cs + [l1, l2, lp, la, s1, s2, sup]

    name = os.path.join(OUT, f'pulse_{sig}_{tk}_tau{tau:g}')
    FuncAnimation(fig, frame, frames=len(tf), blit=False).save(name + '.mp4', writer=FFMpegWriter(fps=20, bitrate=4000), dpi=100)
    for tt in (-tau, 0.0, tf[-1]):                                  # stills: before, at the meeting, at the end
        k = int(np.argmin(np.abs(tf - tt)))
        frame(k)
        fig.savefig(f'{name}_t{tf[k]:+.0f}fs.png', dpi=120)
    plt.close(fig)
    print(f'{sig} {tk} tau {tau:g} fs: {len(tf)} frames -> {name}.mp4', flush=True)


if __name__ == '__main__':
    sig = '2pe' if '--2pe' in sys.argv else '2ce'
    for tau in [float(a) for a in sys.argv[1:] if not a.startswith('--')] or [5.0, 10.0, 20.0, 100.0]:
        for tk in THETAS:
            run(tau, tk, sig)
