r"""Cambaliza & Saloma (2000) at high NA: whole-profile comparison of the paraxial scalar and vector (Richards-Wolf)
2PE and 2CE responses, and the side lobes against NA.

Profiles from scripts/dashboard_cambaliza_data.py (circular pupils, uniform input, both beams along y): transverse
F(x, 0, 0; θ) and axial F(0, 0, z; θ) on the window x ±1 µm × (0.5/NA), z ±5 µm × n (0.5/NA)², 401 points.

Profile difference: each profile normalized to unit energy over the window (Σ F Δs = 1), vector r = reference, scalar a:
    NRMSE = sqrt(Σ (a − r)² / Σ r²),   Linfoot: F = 1 − Σ (a − r)² / Σ r²,  C = Σ a² / Σ r²,  Q = Σ a r / Σ r²
so NRMSE = sqrt(1 − F).
Side lobes of 2PE: position of the first side peak (first local maximum beyond the first minimum), its distance from
the centre in units of λ/n (λ = 0.7 µm), and its height; dotted: λ/2n (facing beams) and λ/n (crossed beams).

    python scripts/cambaliza2000_profile_metrics.py
    -> output/08_two_color/cambaliza2000/high_na/{nrmse_2ce,nrmse_2pe,linfoot_2ce,sidelobes}.png, metrics.txt
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import cut_inset, fig_legend

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 32, 'xtick.labelsize': 28,
                            'ytick.labelsize': 28, 'legend.fontsize': 28})   # ≥ 11 pt on the slide with the inset beside the plots

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'data')
OUT = os.path.join(ROOT, 'output', '08_two_color', 'cambaliza2000', 'high_na')
LP = 0.700
META = json.load(open(os.path.join(DATA, 'meta.json')))
MEDIA = (('air', 1.0, 'o', '-'), ('water', 1.33, 's', '--'))
TH = {'0': 'θ = 0', 'pi2': 'θ = π/2', 'pi': 'θ = π'}


def load(medium, na):
    d = json.load(open(os.path.join(DATA, 'profiles', f'{medium}_{na:g}.json')))
    grid = {a: np.linspace(-d[f'grid|{a}'][0], d[f'grid|{a}'][0], int(d[f'grid|{a}'][1])) for a in ('x', 'z')}
    return d, grid


def metrics(a, r, ds):
    a = np.asarray(a, float); r = np.asarray(r, float)
    a, r = a / (a.sum() * ds), r / (r.sum() * ds)              # unit energy over the window
    rr = np.sum(r * r)
    F = 1 - np.sum((a - r) ** 2) / rr
    return {'nrmse': np.sqrt(max(0.0, 1 - F)), 'F': F, 'C': np.sum(a * a) / rr, 'Q': np.sum(a * r) / rr}


def first_side_lobe(s, y):
    """(distance from the centre, height) of the first side peak at s > 0, by a parabola through the sample maximum."""
    y = np.asarray(y, float); y = y / y[np.argmin(np.abs(s))]
    i = int(np.argmin(np.abs(s)))
    while i < len(y) - 1 and y[i + 1] <= y[i]:                 # down to the first minimum
        i += 1
    j = i
    while j < len(y) - 1 and y[j + 1] >= y[j]:                 # up to the first side peak
        j += 1
    if j >= len(y) - 1 or j == i:
        return np.nan, np.nan
    y0, y1, y2 = y[j - 1], y[j], y[j + 1]
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return s[j] + d * (s[1] - s[0]), y1 - 0.25 * (y0 - y2) * d


def fits(th, na, n):
    return th != 'pi2' or na <= n * np.sin(np.pi / 4) + 1e-9


M, S = {}, {}                                                  # metrics; side lobes
for med, n, _, _ in MEDIA:
    for na in META['na'][med]:
        d, grid = load(med, na)
        for sig in ('2PE', '2CE'):
            for axis in ('x', 'z'):
                s = grid[axis]
                for th in TH:
                    if not fits(th, na, n):
                        continue
                    r, a = d[f'{sig}|{axis}|{th}|vector|circ|uni'], d[f'{sig}|{axis}|{th}|scalar|circ|uni']
                    M[(med, na, sig, axis, th)] = metrics(a, r, s[1] - s[0])
                    S[(med, na, sig, axis, th, 'vector')] = first_side_lobe(s, r)
                    S[(med, na, sig, axis, th, 'scalar')] = first_side_lobe(s, a)


def series(med, sig, axis, th, key, src=M, model=None):
    k = [na for na in META['na'][med] if (med, na, sig, axis, th) + ((model,) if model else ()) in src]
    v = [src[(med, na, sig, axis, th) + ((model,) if model else ())] for na in k]
    return np.array(k), (np.array([x[key] for x in v]) if isinstance(key, str) else np.array([x[key] for x in v]))


# ── profile difference (NRMSE, %) against NA, one signal per figure ──
COL = {'0': '#ff7f0e', 'pi2': '#d62728', 'pi': '#1f77b4'}
for sig, ths in (('2CE', ('0', 'pi2')), ('2PE', ('0', 'pi2', 'pi'))):
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 7.0))
    for ax, axis in zip(axes, ('x', 'z')):
        for th in ths:
            if sig == '2PE' and th == 'pi' and axis == 'x':
                continue                                       # across the axis θ = π equals θ = 0
            for med, n, mk, ls in MEDIA:
                na, v = series(med, sig, axis, th, 'nrmse')
                lab = ('θ = 0 and π' if sig == '2CE' and th == '0' else TH[th]) + f', {med}'
                ax.plot(na, 100 * v, ls + mk, color=COL[th], lw=3, ms=8, mfc=COL[th] if n == 1 else 'white', label=lab)
        ax.set_xlabel('NA'); ax.set_xlim(0.15, 1.3); ax.set_ylim(bottom=0)
        ax.set_title('Across the axis' if axis == 'x' else 'Along the axis')
        cut_inset(ax, axis, sig=sig, theta={'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}[ths[-1]])
    axes[0].set_ylabel('NRMSE (%)')
    h, l = axes[1].get_legend_handles_labels()
    fig_legend(fig, h, l)
    fig.savefig(os.path.join(OUT, f'nrmse_{sig.lower()}.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
    print(f'Saved -> nrmse_{sig.lower()}.png')

# ── Linfoot's criteria, 2CE θ = 0 and π (where the models split first), air and water ──
fig, axes = plt.subplots(1, 2, figsize=(18.5, 7.0), sharey=True)
LC = {'F': ('#1f77b4', 'Fidelity F'), 'C': ('#2ca02c', 'Structural content C'), 'Q': ('#9467bd', 'Correlation quality Q')}
for ax, axis in zip(axes, ('x', 'z')):
    ax.axhline(1, color='#888888', lw=1.5)
    for key, (c, lab) in LC.items():
        for med, n, mk, ls in MEDIA:
            na, v = series(med, '2CE', axis, '0', key)
            ax.plot(na, v, ls + mk, color=c, lw=3, ms=8, mfc=c if n == 1 else 'white', label=f'{lab}, {med}')
    ax.set_xlabel('NA'); ax.set_xlim(0.15, 1.3)
    ax.set_title(('Across the axis' if axis == 'x' else 'Along the axis') + ', 2CE, θ = 0 and π')
    cut_inset(ax, axis, theta=0.0)
axes[0].set_ylabel('Scalar against vector')
h, l = axes[1].get_legend_handles_labels()
fig_legend(fig, h, l)
fig.savefig(os.path.join(OUT, 'linfoot_2ce.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> linfoot_2ce.png')

# ── first side lobe against NA: distance in units of λ/n, and height; vector solid, scalar dashed ──
SL = (('2PE', 'z', 'pi', '#1f77b4', '2PE along, θ = π'), ('2PE', 'x', 'pi2', '#d62728', '2PE, θ = π/2'))
# θ = π/2: along equals across (symmetric crossing). 2CE is left out: its side lobes (I₁I₂, rings of two wavelengths)
# stay below 10⁻³ of the peak, beyond the 4-digit precision of the stored profiles.
fig, axes = plt.subplots(1, 2, figsize=(18.5, 7.0))
for sig, axis, th, c, lab in SL:
    for med, n, mk, _ in MEDIA:
        for model, ls in (('vector', '-'), ('scalar', '--')):
            na, v = series(med, sig, axis, th, 0, S, model)
            _, hgt = series(med, sig, axis, th, 1, S, model)
            keep = na >= 0.3                                    # NA 0.2: the 401-point window does not resolve λ/2n
            na, v, hgt = na[keep], v[keep], hgt[keep]
            kw = dict(color=c, lw=3 if model == 'vector' else 2.5, ms=8 if model == 'vector' else 0, mfc=c if n == 1 else 'white')
            axes[0].plot(na, v / (LP / n), ls + mk, label=f'{lab}, {med}' if model == 'vector' else None, **kw)
            axes[1].plot(na, hgt, ls + mk, **kw)
axes[0].set_ylabel('Distance (λ/n)'); axes[1].set_ylabel('Height (peak = 1)')
axes[0].axhline(0.5, color='#1f77b4', lw=1.5, ls=':'); axes[0].axhline(1.0, color='#d62728', lw=1.5, ls=':')
axes[0].set_ylim(0.4, 1.1)
for ax, ttl in zip(axes, ('First side lobe: distance from the centre', 'First side lobe: height')):
    ax.set_xlabel('NA'); ax.set_xlim(0.25, 1.3); ax.set_title(ttl, fontsize=26)
axes[1].set_yscale('log'); axes[1].set_ylim(0.02, 1.5)
h, l = axes[0].get_legend_handles_labels()
h += [plt.Line2D([], [], color='k', lw=3), plt.Line2D([], [], color='k', lw=2.5, ls='--')]
l += ['vector', 'scalar']
fig_legend(fig, h, l)
fig.savefig(os.path.join(OUT, 'sidelobes.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> sidelobes.png')

L = []
for (med, na, sig, axis, th), m in sorted(M.items(), key=lambda t: (t[0][0], t[0][2], t[0][3], t[0][4], t[0][1])):
    if na in (0.5, 0.7, 0.9, 1.2):
        L.append(f'{med} NA {na} {sig} {axis} {TH[th]}: NRMSE {100 * m["nrmse"]:.1f}% F {m["F"]:.3f} C {m["C"]:.3f} Q {m["Q"]:.3f}')
for sig, axis, th, _, lab in SL:
    for med, n, _, _ in MEDIA:
        for na in (0.3, 0.5, 0.7, 0.9, 1.2):
            for model in ('vector', 'scalar'):
                k = (med, na, sig, axis, th, model)
                if k in S:
                    L.append(f'side lobe {lab}, {med} NA {na} {model}: at {S[k][0]:.3f} µm = {S[k][0] / (LP / n):.3f} λ/n, '
                             f'height {S[k][1]:.3f}')
open(os.path.join(OUT, 'metrics.txt'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
