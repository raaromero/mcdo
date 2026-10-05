r"""Every figure of the Lim & Saloma (2002) progress report, sized for its slide.

Drawn from the saved results of the study scripts (and, for the profile and
on-axis figures, from the field models directly). Each figure has at most two
panels, so each panel fills about half the slide; text is 24/28/32 pt in a figure
about twice its width on the slide, so it reads at 12–16 pt. No figure title
repeats its slide title; 2-D maps are heat maps with contour lines and a
continuous colorbar.

    python scripts/fig_lim2002_slides.py
    -> output/08_two_color/lim2002/slides/*.png
"""

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32, 'axes.labelsize': 28,
                            'xtick.labelsize': 24, 'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
OUT = os.path.join(D, 'slides')
os.makedirs(OUT, exist_ok=True)
L1, L2, L2P = 0.750, 0.656, 0.700
PAPER = {('pi2', 'x'): 1.826 * L1, ('pi2', 'z'): 2.033 * L1, ('pi', 'x'): 0.37 * L1, ('pi', 'z'): 2.7 * L1}
TH = {'pi': 'θ = π', 'pi2': 'θ = π/2'}
WIDE = (16.4, 6.8)                      # two panels across a 9-in slide
BLUE, RED = '#1f77b4', '#d62728'


def rows(pattern):
    """All saved rows for one case: the main file and any tagged extensions (file_*.csv), sorted by NA."""
    base = pattern.replace('*', '')
    paths = [base] if os.path.exists(base) else []
    paths += glob.glob(base.replace('.csv', '_*.csv'))
    out = [np.loadtxt(p, delimiter=',', ndmin=2) for p in paths]
    out = [a for a in out if a.size]
    if not out:
        return None
    a = np.concatenate(out)
    return a[np.argsort(a[:, 0])]


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', name)


def logaxes(ax, nas):
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xticks([t for t in (0.03, 0.1, 0.3, 1.0) if nas[0] - 1e-9 <= t <= nas[-1] * 1.05] if nas[0] < 0.3 else (0.5, 0.7, 1.0))
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        a.set_minor_formatter(matplotlib.ticker.NullFormatter())


# ── 20% tolerances: one figure per angle, x_c and z_c side by side ──
def tolerance(key, suf, n):
    a = rows(os.path.join(D, f'na_breakdown{suf}_{key}.csv'))
    if a is None:
        return
    nas = a[:, 0]
    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    for ax, col, lab in ((axes[0], 3, 'x'), (axes[1], 4, 'z')):
        rw, sc = a[:, col], a[:, col - 2]
        sl, ic = np.polyfit(np.log(nas), np.log(rw), 1)
        ax.plot(nas, rw, 'o', color=BLUE, ms=8, label='Vector')
        ax.plot(nas, np.exp(ic) * nas ** sl, '-', color=BLUE, lw=3)
        lo = nas <= 0.5 + 1e-9
        if lo.sum() >= 3:
            ax.plot(nas[lo], sc[lo], 's', color=RED, ms=8, mfc='none', mew=2.5, label='Paraxial scalar (NA ≤ 0.5)')
        if nas[0] < 0.5:
            ax.hlines(PAPER[(key, lab)], nas[0], 0.5, colors='k', linestyles='--', lw=3, label='Reported, NA 0.5')
        if key == 'pi2' and nas[-1] > n / np.sqrt(2):
            ax.axvspan(n / np.sqrt(2), nas[-1] * 1.03, color='none', hatch='//', ec='#999999', lw=0, zorder=0,
                       label='Lenses cannot cross')
        logaxes(ax, nas)
        ax.set_xlim(nas[0] / 1.1, nas[-1] * 1.05)
        ax.set_title(f'Along {lab}$_c$')
        ax.text(0.96, 0.95, f'∝ NA$^{{{sl:.2f}}}$', transform=ax.transAxes, ha='right', va='top', color=BLUE, fontsize=28)
        ax.set_xlabel('NA')
    axes[0].set_ylabel('Offset for 20% loss (µm)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=len(l), bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, f'tolerance_{key}{suf}.png')


# ── how far the paraxial scalar tolerance departs from the vector one ──
def deviation(suf):
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, key in zip(axes, ('pi', 'pi2')):
        a = rows(os.path.join(D, f'na_breakdown{suf}_{key}.csv'))
        if a is None:
            continue
        for col, lab, c in ((3, 'Across the axis (x$_c$)', BLUE), (4, 'Along the axis (z$_c$)', '#9467bd')):
            ax.plot(a[:, 0], 100 * np.abs(a[:, col - 2] / a[:, col] - 1), '-', color=c, lw=4, label=lab)
        for t in (5, 10):
            ax.axhline(t, color='#999999', lw=2, ls=':')
        ax.axvline(0.5, color='#999999', lw=2)
        if key == 'pi2':
            ax.axvspan(1 / np.sqrt(2), 1.0, color='none', hatch='//', ec='#999999', lw=0, zorder=0)
        ax.set_title(TH[key]); ax.set_xlabel('NA'); ax.set_ylim(0, 50); ax.set_xlim(0, 1.0)
    axes[0].set_ylabel('Scalar vs vector (%)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, f'deviation{suf}.png')


# ── peak lost against NA, one metric per slide ──
LOWCUT = {3: 0.3, 5: 0.2}                # 2PE fringes (3) and the long low-NA focus (5) outrun the grid
METRICS = {1: ('pi2', 11), 2: ('pi', 20), 3: ('pi2', 30), 4: ('pi', 20), 5: ('pi2', 30)}


def peaklost(k, suf, pol=''):
    a = rows(os.path.join(D, f'quoted_vs_na{suf}{pol}_m{k}.csv'))
    if a is None:
        return
    if k in LOWCUT:                             # below this NA the grid of offsets is too coarse for the peak
        a = a[a[:, 0] >= LOWCUT[k] - 1e-9]
    nas = a[:, 0]
    key, paper = METRICS[k]
    fig, ax = plt.subplots(figsize=(9.6, 7.4))
    ax.axvspan(0, 0.5, color='#e6e6e6', zorder=0, label='Paraxial range (NA ≤ 0.5)')
    if key == 'pi2':
        ax.axvspan(1 / np.sqrt(2), 1.0, color='none', hatch='//', ec='#999999', lw=0, zorder=0, label='Lenses cannot cross')
    ax.plot(nas, a[:, 1], '-o', color=BLUE, lw=4, ms=7, label='Vector')
    lo = nas <= 0.5 + 1e-9
    ax.plot(nas[lo], a[lo, 2], ':s', color=RED, lw=3, ms=7, mfc='none', mew=2, label='Paraxial scalar')
    ax.hlines(paper, nas[0], 0.5, colors='k', linestyles='--', lw=3, label='Reported, NA 0.5')
    ax.set_xlim(0, 1.0); ax.set_ylim(0, 100)
    ax.set_xlabel('NA'); ax.set_ylabel('Peak lost (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, columnspacing=1.0)
    save(fig, f'peaklost_{k}{suf}.png')


# ── PSF and peak maps: NA 0.5 against the highest NA shown, heat map with contours ──
def maps(stem, xkey, zkey, key_fmt, tag, theta, suf, xlabel, zlabel):
    path = os.path.join(D, f'{stem}{suf}.npz')
    if not os.path.exists(path):
        return
    d = np.load(path)
    nas = (0.5, 0.9) if theta == 'pi' else (0.5, 0.7)
    fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.6))
    for ax, na in zip(axes, nas):
        M = d[key_fmt.format(na)]
        M = 100 * M / M.max()
        pm = ax.pcolormesh(d[xkey], d[zkey], M, cmap='viridis', vmin=0, vmax=100, shading='nearest', rasterized=True)
        ax.contour(d[xkey], d[zkey], M, levels=[20, 50, 80], colors='w', linewidths=1.2)
        ax.set_box_aspect(1.0)
        ax.set_title(f'NA {na}' + (';  lenses cannot cross' if theta == 'pi2' and na > 0.71 else ''))
        ax.set_xlabel(xlabel)
    axes[0].set_ylabel(zlabel)
    fig.colorbar(pm, ax=list(axes), fraction=0.025, pad=0.02).set_label('% of peak')
    save(fig, f'{tag}{suf}.png')


# ── one beam pair's aligned profiles at NA 0.8, θ = π: three models ──
def profiles():
    na = 0.8
    xs, zs = np.linspace(-0.8, 0.8, 801), np.linspace(-2.0, 2.0, 1601)

    def I(x, z, lam, th, model):
        if model == 'rw':
            return 0.5 * sum(intensity(beam_field(x, z, lam, na, theta=th, model='rw', psi=p)) for p in (0.0, np.pi / 2))
        kw = {} if model == 'paraxial' else dict(model='debye')
        return intensity(beam_field(x, z, lam, na, theta=th, **kw))
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for model, lab, c, ls in (('paraxial', 'Paraxial scalar', RED, '--'), ('debye', 'Scalar Debye', '#ff7f0e', ':'),
                              ('rw', 'Vector', BLUE, '-')):
        px = I(xs, 0 * xs, L1, 0, model) * I(xs, 0 * xs, L2, np.pi, model)
        pz = I(0 * zs, zs, L1, 0, model) * I(0 * zs, zs, L2, np.pi, model)
        axes[0].plot(xs, px / px.max(), ls, color=c, lw=4, label=lab)
        axes[1].plot(zs, pz / pz.max(), ls, color=c, lw=4)
    axes[0].set_title('Across the axis'); axes[1].set_title('Along the axis')
    axes[0].set_xlabel('x (µm)'); axes[1].set_xlabel('z (µm)'); axes[0].set_ylabel('2CE signal, normalized')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'profiles_pi_na0.8.png')


# ── single beam on axis: scalar against vector at NA 0.5, and uniform against Gaussian input ──
def onaxis(na, at, model):
    z = np.linspace(-3.0 * 2 * L1 / na ** 2, 3.0 * 2 * L1 / na ** 2, 1201)
    ap = gaussian(at, na ** 2) if at else None
    kw = dict(model='rw', psi=0.0) if model == 'rw' else {}
    I = intensity(beam_field(0 * z, z, L1, na, apodization=ap, **kw))
    return z, I / I.max()


def axial_checks():
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, at in zip(axes, (0, 4)):
        for model, lab, c, ls in (('scalar', 'Paraxial scalar', RED, '-'), ('rw', 'Vector', BLUE, '--')):
            z, I = onaxis(0.5, at, model)
            ax.plot(z, I, ls, color=c, lw=4, label=lab)
        ax.set_title('Uniform input' if at == 0 else 'Gaussian input, α$_t$ = 4'); ax.set_xlabel('z (µm)')
    axes[0].set_ylabel('On-axis intensity, NA 0.5')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'onaxis_scalar_vector_na0.5.png')
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, na in zip(axes, (0.5, 0.9)):
        for at, lab, c, ls in ((0, 'Uniform input', 'k', '-'), (4, 'Gaussian input, α$_t$ = 4', RED, '--')):
            z, I = onaxis(na, at, 'rw')
            ax.plot(z, I, ls, color=c, lw=4, label=lab)
        ax.set_title(f'NA {na}'); ax.set_xlabel('z (µm)')
    axes[0].set_ylabel('On-axis intensity, vector')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'onaxis_gaussian_uniform.png')


# ── fidelity: the F = 0.8 contour at every NA, offsets in spot units ──
UNITS = {('2ce', 'pi'): ('x$_c$ NA/λ', 'z$_c$ NA²/nλ'), ('2ce', 'pi2'): ('x$_c$ NA²/nλ', 'z$_c$ NA/λ'),
         ('2pe', 'pi'): ('x$_c$ NA/λ', 'z$_c$ n/λ'), ('2pe', 'pi2'): ('x$_c$ n/λ', 'z$_c$ n/λ')}


LEVELS = {'F': 0.8, 'Q': 0.8, 'C': 1.2}   # F, Q fall from 1 and C rises from 1 as O′ moves: each contour is a 20% change


def fidelity_map(pair, th, suf, key='F'):
    files = sorted(glob.glob(os.path.join(D, 'fidelity', f'{pair}_{th}{suf}_na*_n*.npz')))
    if not files:
        return
    runs = []
    for p in files:
        na = float(p.split('_na')[1].split('_n')[0]); n = float(p.rsplit('_n', 1)[1][:-4])
        runs.append((na, n, np.load(p)))
    runs.sort(key=lambda r: r[0])
    nas = np.array([r[0] for r in runs]); cmap = plt.get_cmap('viridis')
    fig, ax = plt.subplots(figsize=(9.6, 8.0))
    for na, n, d in runs:
        ax.contour(d['xt'], d['zt'], d[f'{key}_vec'], levels=[LEVELS[key]], colors=[cmap((na - nas.min()) / np.ptp(nas))],
                   linewidths=3, linestyles='-' if n == 1 else '--')
    ref = min(runs, key=lambda r: abs(r[0] - 0.5))
    ax.contour(ref[2]['xt'], ref[2]['zt'], ref[2][f'{key}_sca'], levels=[LEVELS[key]], colors=RED, linewidths=5, linestyles=':')
    ulx, ulz = UNITS[(pair, th)]
    ax.set_xlabel(ulx); ax.set_ylabel(ulz)
    keep = np.zeros_like(runs[0][2]['F_vec'], bool)          # zoom to the regions within 20% of the aligned value
    for _, _, d in runs:
        inside = (lambda v: v <= LEVELS[key]) if key == 'C' else (lambda v: v >= LEVELS[key])
        keep |= inside(d[f'{key}_vec']) | inside(d[f'{key}_sca'])
    zz, xx = np.nonzero(keep)
    xt, zt = runs[0][2]['xt'], runs[0][2]['zt']
    hx, hz = 1.4 * np.abs(xt[xx]).max(), 1.4 * np.abs(zt[zz]).max()
    ax.set_xlim(-hx, hx); ax.set_ylim(-hz, hz)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(nas.min(), nas.max()))
    fig.colorbar(sm, ax=ax, fraction=0.05, pad=0.03).set_label('NA (vector)')
    save(fig, f'fidelity_{pair}_{th}{suf}.png' if key == 'F' else f'linfoot{key}_{pair}_{th}{suf}.png')


# ── polarization ──
POLS = [('', 'Unpolarized', 'k', '-'), ('_pols', 's–s', BLUE, '-'), ('_polp', 'p–p', RED, '--')]


def polarization():
    x = np.linspace(-1.2, 1.2, 481)
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, na in zip(axes, (0.5, 0.9)):
        I = {p: intensity(beam_field(x, 0 * x, L1, na, model='rw', psi=p)) for p in (0.0, np.pi / 2)}
        m = max(v.max() for v in I.values())
        ax.plot(x, I[np.pi / 2] / m, '-', color=BLUE, lw=4, label='Field along y (s)')
        ax.plot(x, I[0.0] / m, '--', color=RED, lw=4, label='Field along x (p)')
        ax.set_title(f'NA {na}'); ax.set_xlabel('x (µm)')
    axes[0].set_ylabel('Intensity at focus, normalized')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'polarization_spot.png')

    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    for ax, col, lab in ((axes[0], 3, 'x'), (axes[1], 4, 'z')):
        for suf, name, c, ls in POLS:
            a = rows(os.path.join(D, f'na_breakdown{suf}_pi.csv'))
            if a is None:
                continue
            a = a[(a[:, 0] >= 0.1 - 1e-9) & (a[:, 0] <= 0.95 + 1e-9)]
            ax.plot(a[:, 0], a[:, col], ls, color=c, lw=4, label=name)
        logaxes(ax, np.array([0.1, 0.95])); ax.set_title(f'θ = π, along {lab}$_c$'); ax.set_xlabel('NA')
        ax.set_xticks((0.1, 0.2, 0.5)); ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(subs=(1, 2, 5)))
    axes[0].set_ylabel('Offset for 20% loss (µm)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'polarization_tolerance_pi.png')

    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, k, title in ((axes[0], 2, '2CE, θ = π, x$_c$ = 0.37 λ$_1$'), (axes[1], 3, '2PE, θ = π/2, x$_c$ = 0.5 λ$_{2p}$')):
        for suf, name, c, ls in POLS:
            if k == 3 and suf == '':                   # 2PE beams are polarized; the default set is s–s
                continue
            use = '' if (k == 3 and suf == '_pols') else suf
            a = rows(os.path.join(D, f'quoted_vs_na{use}_m{k}.csv'))
            if a is None:
                continue
            a = a[(a[:, 0] >= (0.3 if k == 3 else 0.1) - 1e-9) & (a[:, 0] <= 0.95 + 1e-9)]
            ax.plot(a[:, 0], a[:, 1], ls, color=c, lw=4, label=name)
        if k == 3:
            ax.axvspan(1 / np.sqrt(2), 0.95, color='none', hatch='//', ec='#999999', lw=0, zorder=0)
        ax.set_title(title, fontsize=28); ax.set_xlabel('NA'); ax.set_ylim(0, 100); ax.set_xlim(0.1, 0.95)
    axes[0].set_ylabel('Peak lost (%)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    save(fig, 'polarization_peaklost.png')


if __name__ == '__main__':
    for suf, n in (('', 1.0), ('_at4', 1.0), ('_n1.33', 1.33), ('_at4_n1.33', 1.33)):
        for key in ('pi', 'pi2'):
            tolerance(key, suf, n)
    for suf in ('', '_at4'):
        deviation(suf)
        for k in range(1, 6):
            peaklost(k, suf)
        for tag, th in (('a', 'pi'), ('b', 'pi'), ('c', 'pi2'), ('d', 'pi2')):
            for no in (2, 3):
                maps(f'na_contours_fig{no}{tag}', 'x_um', 'z_um', 'F_na{:g}', f'map_fig{no}{tag}', th, suf, 'x (µm)', 'z (µm)')
            maps(f'na_peakmaps_fig4{tag}', 'x_c_um', 'z_c_um', 'P_na{:g}', f'map_fig4{tag}', th, suf, 'x$_c$ (µm)', 'z$_c$ (µm)')
        for pair in ('2ce', '2pe'):
            for th in ('pi', 'pi2'):
                for key in 'FCQ':
                    fidelity_map(pair, th, suf, key)
    profiles()
    axial_checks()
    polarization()
