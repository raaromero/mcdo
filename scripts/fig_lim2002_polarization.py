r"""Polarization of the two beams as a decision: unpolarized (A) against fixed
linear polarizations s–s and p–p (B), vector focus, air, uniform input.

  s: both beams polarized along y, perpendicular to the plane of the two axes;
     the fields of the two beams stay parallel for any θ.
  p: both beams polarized in that plane (beam 1 along x).

Reads the results of fig_lim2002_na_breakdown.py and fig_lim2002_quoted_vs_na.py
run with POL = s and p (suffixes _pols, _polp) next to the unpolarized ones.
2PE is always polarized; its default (the unpolarized set) is s.

  polarization_spot.png        why they differ: one beam's focal profile across x
                               at NA 0.5 and 0.9, s against p against unpolarized
  polarization_tolerances.png  2CE 20% tolerances against NA, A / s / p
  polarization_quoted.png      Lim & Saloma's five quoted losses against NA, A / s / p

    python scripts/fig_lim2002_polarization.py
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.twobeam import beam_field, intensity

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
CASES = [('', 'A: unpolarized', 'k', '-'), ('_pols', 'B: s–s (perpendicular to the plane)', '#1f77b4', '-'),
         ('_polp', 'B: p–p (in the plane)', '#d62728', '--')]
QUOTED = ['2CE, θ = π/2, x$_c$ = 1.33 λ$_1$', '2CE, θ = π, x$_c$ = 0.37 λ$_1$', '2PE, θ = π/2, x$_c$ = 0.5 λ$_{2p}$',
          '2CE, θ = π, z$_c$ = 2.7 λ$_1$', '2CE, θ = π/2, z$_c$ = 2.7 λ$_1$']


def rows(pattern):
    out = [np.loadtxt(p, delimiter=',', ndmin=2) for p in glob.glob(pattern)]
    out = [a for a in out if a.size]
    if not out:
        return None
    a = np.concatenate(out)
    return a[np.argsort(a[:, 0])]


def save(fig, name):
    fig.savefig(os.path.join(D, name), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', name)


# ── why: one beam's profile across x, s (field along y) against p (field along x) ──
x = np.linspace(-1.2, 1.2, 481)
fig, axes = plt.subplots(1, 2, figsize=(22.0, 8.5))
for ax, na in zip(axes, (0.5, 0.9)):
    I = {p: intensity(beam_field(x, 0 * x, 0.750, na, model='rw', psi=p)) for p in (0.0, np.pi / 2)}
    m = max(v.max() for v in I.values())
    ax.plot(x, I[np.pi / 2] / m, '-', color='#1f77b4', lw=4, label='s: field along y, across the profile')
    ax.plot(x, I[0.0] / m, '--', color='#d62728', lw=4, label='p: field along x, along the profile')
    ax.plot(x, 0.5 * (I[0.0] + I[np.pi / 2]) / m, '-', color='k', lw=2.5, label='Unpolarized (average)')
    fw = {k: np.ptp(x[v >= 0.5 * v.max()]) for k, v in I.items()}
    ax.set_title(f'NA {na}: FWHM p/s = {fw[0.0] / fw[np.pi / 2]:.2f}')
    ax.set_xlabel('x (µm)'); ax.set_ylabel('Intensity (normalized)')
    print(f'NA {na}: focal FWHM along x, s {fw[np.pi / 2]:.3f} µm, p {fw[0.0]:.3f} µm')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=24)
fig.suptitle('One beam at focus, 750 nm: the spot is wider along the polarization', fontsize=32, y=1.03)
plt.tight_layout()
save(fig, 'polarization_spot.png')

# ── 2CE 20% tolerances ──
fig, axes = plt.subplots(2, 2, figsize=(20.0, 16.0), sharex=True)
for r, key in enumerate(('pi2', 'pi')):
    for c, lab in enumerate(('x', 'z')):                    # columns: NA, scalar_x, scalar_z, rw_x, rw_z, F, wx, wz
        ax = axes[r, c]
        for suf, name, colr, ls in CASES:
            a = rows(os.path.join(D, f'na_breakdown{suf}_{key}.csv'))
            if a is None:
                continue
            a = a[a[:, 0] <= 0.95 + 1e-9]
            ax.plot(a[:, 0], a[:, 3 if lab == 'x' else 4], ls, color=colr, lw=3.5, label=name)
        ax.set_xscale('log'); ax.set_yscale('log')
        ax.set_title(f'{"θ = π/2" if key == "pi2" else "θ = π"}, along {lab}$_c$')
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.set_xticks([0.1, 0.2, 0.3, 0.5, 0.7, 0.95])
        if key == 'pi2':
            ax.axvspan(1 / np.sqrt(2), 0.97, color='none', hatch='//', ec='#999999', lw=0, zorder=0)
        if r == 1:
            ax.set_xlabel('NA')
        if c == 0:
            ax.set_ylabel('Offset for 20% loss (µm)')
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.06), frameon=False, fontsize=24)
fig.suptitle('2CE: offset of O′ costing 20% of the peak, by polarization', fontsize=32, y=1.0)
plt.tight_layout()
save(fig, 'polarization_tolerances.png')

# ── the five quoted losses ──
fig, axes = plt.subplots(1, 5, figsize=(36.0, 8.0))
for k, ax in enumerate(axes, 1):
    for suf, name, colr, ls in CASES:
        if k == 3 and suf == '':                              # 2PE has no unpolarized case
            continue
        use = '' if (k == 3 and suf == '_pols') else suf      # 2PE's default set is already s
        a = rows(os.path.join(D, f'quoted_vs_na{use}_m{k}*.csv'))
        if a is None:
            continue
        a = a[(a[:, 0] >= 0.1 - 1e-9) & (a[:, 0] <= 0.95 + 1e-9)]
        ax.plot(a[:, 0], a[:, 1], ls, color=colr, lw=3.5, label=name)
    ax.set_title(QUOTED[k - 1])
    ax.set_xlabel('NA'); ax.set_ylim(0, 100); ax.set_xlim(0.1, 0.95)
    if k == 1:
        ax.set_ylabel('Peak lost (%)')
    if k in (1, 3, 5):
        ax.axvspan(1 / np.sqrt(2), 0.95, color='none', hatch='//', ec='#999999', lw=0, zorder=0)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.14), frameon=False, fontsize=24)
fig.suptitle('Lim & Saloma’s quoted losses against NA, by polarization (2PE: s–s and p–p only)', fontsize=32, y=1.05)
plt.tight_layout()
save(fig, 'polarization_quoted.png')

# ── numbers for the slides ──
for key in ('pi', 'pi2'):
    for na in (0.5, 0.9):
        vals = []
        for suf, name, _, _ in CASES:
            a = rows(os.path.join(D, f'na_breakdown{suf}_{key}.csv'))
            if a is not None and np.any(np.isclose(a[:, 0], na)):
                r = a[np.isclose(a[:, 0], na)][0]
                vals.append(f'{name.split(":")[0] + (name.split(":")[1][:4] if ":" in name else "")}: x {r[3]:.3f} z {r[4]:.3f}')
        print(f'{key} NA {na}:', ' | '.join(vals))
