r"""Side-by-side video of a long pulse (100 fs, effectively continuous beams) and a short one (10 fs), same lenses.

Each half shows, for its pulse width: the x–z map now (I₁·I₂ for 2CE, |E₁ + E₂|⁴ for 2PE) and the excitation accumulated
up to t, both with iso-value lines (stills: contour lines only, 10–80% of each map's peak, 50% in orange); below, the same along the axis, with the continuous-beam profile and the profile after
the pulses. The two runs are shown on their own clock, at the same t/τ, and both end on the total accumulated as the pulses pass the focus.
Fields and excitation as in cambaliza2000_pulse_video.py (all photon pairs, narrow 350-nm level, phase-locked).

    python scripts/cambaliza2000_pulse_compare_video.py [--2pe] [theta: 0 | pi2 | pi]      (default 2CE, pi)
    -> output/08_two_color/cambaliza2000/pulses/video/compare_<2ce|2pe>_<θ>_tau100_vs_10.mp4 and still frames
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.colors import PowerNorm

from cambaliza2000_pulse_video import compute, THETAS, CONTOURS, OUT, NA, XH, ZH
from mcdo.cutinset import place_legend

TAUS = (100.0, 10.0)
U = np.linspace(-2.1, 2.1, 150)                                     # t/τ of the frames
LINES = [0.1, 0.2, 0.4, 0.6, 0.8]                                  # iso-value lines of the stills (of the map's own peak)
HALF = '#ff7f0e'                                                    # the 50% line
HOLD = 20                                                           # frames on the total


def main(sig, tk):
    label, SIG = THETAS[tk][1], sig.upper()
    runs = [compute(tau, tk, sig) for tau in TAUS]
    idx = [list(np.abs(D['tf'][:, None] / tau - U[None, :]).argmin(0)) + [len(D['tf']) - 1] * HOLD for D, tau in zip(runs, TAUS)]
    nfr = len(idx[0])
    fig = plt.figure(figsize=(19, 12.5))
    gs = fig.add_gridspec(3, 4, height_ratios=[1.35, 0.8, 1])
    maps = [fig.add_subplot(gs[0, c]) for c in range(4)]
    now = [fig.add_subplot(gs[1, 0:2]), fig.add_subplot(gs[1, 2:4])]
    acc = [fig.add_subplot(gs[2, 0:2]), fig.add_subplot(gs[2, 2:4])]
    ext = (-XH, XH, ZH, -ZH)
    nowname = 'I₁·I₂' if sig == '2ce' else '|E₁ + E₂|⁴'
    art = []
    for j, (D, tau) in enumerate(zip(runs, TAUS)):
        m = D['maps']
        a0, a1 = maps[2 * j], maps[2 * j + 1]
        i0 = a0.imshow(m['P'][0], extent=ext, aspect='auto', cmap='Purples', norm=PowerNorm(0.45, vmin=0, vmax=m['P'].max()), interpolation='bilinear')
        i1 = a1.imshow(m['all'][0], extent=ext, aspect='auto', cmap='Greys', norm=PowerNorm(0.45, vmin=0, vmax=m['all'].max()), interpolation='bilinear')
        a0.set_title(f'{nowname} now, τ = {tau:g} fs'); a1.set_title(f'{SIG} accumulated up to t, τ = {tau:g} fs')
        for a in (a0, a1):
            a.set_xlabel('x (µm)')
        L, z = D['line'], D['zf']
        ln, = now[j].plot(z, L['P'][0] / L['P'].max(), color='#6a3d9a', lw=2.4)
        now[j].set_title(f'{nowname} along the axis now, τ = {tau:g} fs')
        acc[j].plot(z, D['cw'], color='k', ls='--', lw=1.8, label='continuous beams')
        acc[j].plot(z, L['all'][-1] / D['fin_all'], color='0.6', lw=1.4, label=f'total {SIG}')
        la, = acc[j].plot(z, L['all'][0] / D['fin_all'], color='k', lw=2.6, label=f'{SIG} accumulated up to t')
        acc[j].set_title(f'{SIG} along the axis, τ = {tau:g} fs')
        for a in (now[j], acc[j]):
            a.set_xlim(-ZH, ZH); a.set_xlabel('z (µm), at x = 0')
        now[j].set_ylim(0, 1.05); acc[j].set_ylim(0, 1.3)
        art.append((D, i0, i1, a0, a1, ln, la))
    maps[0].set_ylabel('z (µm)'); now[0].set_ylabel('Of its maximum'); acc[0].set_ylabel(f'{SIG} (peak of the total = 1)')
    sup = fig.suptitle('', fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    for a in acc:
        place_legend(a, fontsize=11)
    cs = []

    def frame(f, lines=False, now_at=None):
        for c in cs:
            c.remove()
        cs.clear()
        ts = []
        for (D, i0, i1, a0, a1, ln, la), ix, tau in zip(art, idx, TAUS):
            k = ix[f]
            kn = k if now_at is None else ix[now_at]                 # the 'now' panels may show another instant
            for im, a, q, kk in ((i0, a0, 'P', kn), (i1, a1, 'all', k)):
                mm = D['maps'][q][kk]
                im.set_data(mm); im.set_visible(not lines)
                if mm.max() <= 0.01 * D['maps'][q].max():
                    continue
                if lines:                                           # stills: contour lines only, 50% in orange
                    cs.extend([a.contour(D['xs'], D['zs'], mm / mm.max(), levels=LINES, colors='k', linewidths=0.9), a.contour(D['xs'], D['zs'], mm / mm.max(), levels=[0.5], colors=HALF, linewidths=2.2)])
                else:
                    cs.append(a.contour(D['xs'], D['zs'], mm / mm.max(), levels=CONTOURS, colors='0.15', linewidths=1.0))
            ln.set_ydata(D['line']['P'][kn] / D['line']['P'].max()); la.set_ydata(D['line']['all'][k] / D['fin_all'])
            ts.append(D['tf'][k])
        after = f >= len(U)
        sup.set_text(f'{label}, NA {NA}, zero delay, ' + ('total accumulated as the pulses pass the focus' if after else
                     f't/τ = {U[f]:+.2f} (t = {ts[0]:+.0f} fs at τ = 100 fs and {ts[1]:+.1f} fs at τ = 10 fs)'))
        return [a[1] for a in art] + [a[2] for a in art] + cs + [sup]

    name = os.path.join(OUT, f'compare_{sig}_{tk}_tau100_vs_10')
    FuncAnimation(fig, frame, frames=nfr, blit=False).save(name + '.mp4', writer=FFMpegWriter(fps=20, bitrate=4000), dpi=100)
    from matplotlib.lines import Line2D
    k0 = int(np.argmin(np.abs(U)))
    maps[0].legend([Line2D([], [], color='k', lw=0.9), Line2D([], [], color=HALF, lw=2.2)],
                         ['10, 20, 40, 60, 80% of the peak', '50%'], loc='upper left', fontsize=9, frameon=True, framealpha=0.9)
    for f, tag, na in ((k0, 'meeting', None), (nfr - 1, 'after', k0)):   # after: 'now' panels at t = 0, accumulated panels the total
        frame(f, lines=True, now_at=na)
        for j, tau in enumerate(TAUS):
            when = 'at t = 0' if na is not None else 'now'
            maps[2 * j].set_title(f'{nowname} {when}, τ = {tau:g} fs'); now[j].set_title(f'{nowname} along the axis {when}, τ = {tau:g} fs')
            maps[2 * j + 1].set_title(f'{SIG} ' + ('total' if na is not None else 'accumulated up to t = 0') + f', τ = {tau:g} fs')
        fig.savefig(f'{name}_{tag}.png', dpi=150)
    plt.close(fig)
    print('->', name + '.mp4', flush=True)


if __name__ == '__main__':
    sig = '2pe' if '--2pe' in sys.argv else '2ce'
    rest = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(sig, rest[0] if rest else 'pi')
