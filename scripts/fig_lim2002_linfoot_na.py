r"""Lim & Saloma (2002) Figs. 5–6 against NA: Linfoot's criteria F, C, Q over the offset of O′,
drawn as the replication draws them (3D surfaces on the paper's offset grid and axes).

Three panels per figure: scalar 2CE at NA 0.5 (the replication), vector (Richards–Wolf) 2CE at
NA 0.7 and NA 0.9. Same window (±1 × ±5 µm, 100 × 100 points), same offsets (±1 × ±5 µm),
same definitions as fig_lim2002.py:

    F = 1 − ⟨(t − a)²⟩/⟨t²⟩,  C = ⟨a²⟩/⟨t²⟩,  Q = ⟨|a||t|⟩/⟨t²⟩

with t the aligned and a the misaligned PSF, each scaled to its own peak. 2CE beams are
unpolarized (average over two perpendicular input polarizations); 2PE beams are both polarized
perpendicular to the plane of the lens axes. Crossed lenses (θ = π/2) above NA 0.71 do not fit in air;
they are computed in water (n = 1.33), where they fit up to NA 0.94. Maps are cached as .npz.

    python scripts/fig_lim2002_linfoot_na.py              # uniform input
    ALPHA_T=4 python scripts/fig_lim2002_linfoot_na.py    # Gaussian input, suffix _at4
    -> output/08_two_color/lim2002/slides/linfoot3d_{F,C,Q}_{2ce,2pe}_{pi,pi2}[_at4].png
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
matplotlib.rcParams.update({'font.size': 26, 'axes.titlesize': 30, 'axes.labelsize': 30,
                            'xtick.labelsize': 26, 'ytick.labelsize': 26})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
OUT = os.path.join(D, 'slides')
CACHE = os.path.join(D, 'linfoot_na')
os.makedirs(CACHE, exist_ok=True)
AT = float(os.environ.get('ALPHA_T', '0'))
SUF = '' if AT == 0 else f'_at{AT:g}'
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
TH = {'pi': np.pi, 'pi2': np.pi / 2}
dx, dz, nx, nz, P = 0.02, 0.1, 50, 50, 50          # window ±1 × ±5 µm; offsets ±P steps of 2


NMED = os.environ.get('N_MED')                     # every case in this medium, e.g. 1.33 (water at the same NAs as air)
MSUF = '' if not NMED else f'_n{float(NMED):g}'


def medium(th, na):
    """Refractive index: water (1.33) for crossed lenses above NA 0.71, where they do not fit in air."""
    if NMED:
        return float(NMED)
    return 1.33 if th == 'pi2' and na > 1 / np.sqrt(2) else 1.0


def fields(lam, na, model, theta, X, Z, n=1.0):
    """Intensity (2CE, unpolarized) or field (2PE, polarized perpendicular to the plane of the axes) of one beam."""
    apod = gaussian(AT, (na / n) ** 2) if AT else None
    if model == 'scalar':
        return beam_field(X, Z, lam, na, n, theta=theta, apodization=apod)
    return [beam_field(X, Z, lam, na, n, theta=theta, apodization=apod, model='rw', psi=p) for p in (0.0, np.pi / 2)]


def where(th, na):
    return ', water' if medium(th, na) != 1 else ''


def maps(pair, th, model, na):
    n = medium(th, na)
    path = os.path.join(CACHE, f'{pair}_{th}_{model}_na{na:g}' + ('' if n == 1 else f'_n{n:g}') + f'{SUF}.npz')
    if os.path.exists(path):
        d = np.load(path)
        return d['xc'], d['zc'], d['F'], d['C'], d['Q']
    la, lb = LAMS[pair]
    xw, zw = np.arange(-nx, nx) * dx, np.arange(-nz, nz) * dz
    xe, ze = np.arange(-nx - P, nx + P) * dx, np.arange(-nz - P, nz + P) * dz
    XW, ZW = np.meshgrid(xw, zw); XE, ZE = np.meshgrid(xe, ze)
    f1, f2 = fields(la, na, model, 0.0, XW, ZW, n), fields(lb, na, model, TH[th], XE, ZE, n)
    sz, sx = XW.shape
    if pair == '2ce':
        avg = (lambda f: intensity(f)) if model == 'scalar' else (lambda f: 0.5 * sum(intensity(g) for g in f))
        I1, I2 = avg(f1), avg(f2)
        sig = lambda iz, ix: I1 * I2[P - iz:P - iz + sz, P - ix:P - ix + sx]
    else:
        E1, E2 = (f1, f2) if model == 'scalar' else (f1[1], f2[1])          # ψ = π/2: perpendicular to the plane
        sig = lambda iz, ix: intensity(E1 + E2[..., P - iz:P - iz + sz, P - ix:P - ix + sx]) ** 2
    t = sig(0, 0); tn = t / t.max(); t2 = np.mean(tn ** 2)
    IX = IZ = np.arange(-P, P + 1, 2)
    F = np.zeros((IZ.size, IX.size)); C = np.zeros_like(F); Q = np.zeros_like(F)
    for i, iz in enumerate(IZ):
        for j, ix in enumerate(IX):
            a = sig(iz, ix); an = a / a.max()
            F[i, j] = 1 - np.mean((tn - an) ** 2) / t2
            C[i, j] = np.mean(an ** 2) / t2
            Q[i, j] = np.mean(np.abs(an) * np.abs(tn)) / t2
    xc, zc = IX * dx / la, IZ * dz / la                                       # in λ_1 (2CE) or λ_2p (2PE), as in the paper
    np.savez_compressed(path, xc=xc, zc=zc, F=F, C=C, Q=Q)
    print('computed', os.path.basename(path), flush=True)
    return xc, zc, F, C, Q


if os.environ.get('GRID'):        # meeting figures, 2CE θ = π, NA 0.5, 0.7, 0.9 (Gaussian input with ALPHA_T=4)
    # GRID_CASES=2ce:pi,2ce:pi2,2pe:pi,2pe:pi2 for the other cases; N_MED=1.33 for all of them in water
    NAS3 = (0.5, 0.7, 0.9)

    def surf_grid(rows, name):
        fig = plt.figure(figsize=(19.5, 6.5 * len(rows)))
        for r, (label, get) in enumerate(rows):
            for c, na in enumerate(NAS3):
                xc, zc, F = get(na)
                XC, ZC = np.meshgrid(xc, zc)
                ax = fig.add_subplot(len(rows), 3, 3 * r + c + 1, projection='3d')
                ax.plot_surface(XC, ZC, np.clip(F, -3, 1), cmap='viridis', edgecolor='k', linewidth=0.2, rstride=1, cstride=1)
                ax.set_zlim(-3, 1); ax.set_ylim(zc.max(), zc.min())
                ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks(np.arange(-6, 7, 3)); ax.set_zticks(np.arange(-3, 1.01, 1.0))
                ax.set_box_aspect((1.0, 1.0, 0.9), zoom=1.1)
                ax.zaxis.set_ticks_position('lower'); ax.zaxis.set_label_position('lower')
                ax.set_xlabel('x$_c$', labelpad=16); ax.set_ylabel('z$_c$', labelpad=16); ax.set_zlabel('F', labelpad=14)
                ax.set_title(f'{label}, NA {na:g}' + where(th, na)); ax.view_init(elev=22, azim=120)
        fig.subplots_adjust(left=0.04, right=1.0, wspace=0.08, hspace=0.32)
        fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig); print('Saved ->', name)

    def diff_row(a, b, label, name):
        d = []
        for na in NAS3:
            xc, zc, A = a(na); _, _, B = b(na); d.append((na, xc, zc, A - B))
        lim = max(float(np.ceil(max(np.percentile(np.abs(x[3]), 98) for x in d) * 20) / 20), 0.05)
        fig, axes = plt.subplots(1, 3, figsize=(21.0, 7.4))
        for ax, (na, xc, zc, dM) in zip(axes, d):
            pm = ax.pcolormesh(xc, zc, dM, cmap='RdBu_r', vmin=-lim, vmax=lim, shading='nearest', rasterized=True)
            ax.contour(xc, zc, dM, levels=[0.0], colors='k', linewidths=1.5)
            ax.set_box_aspect(1.0); ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks(np.arange(-6, 7, 2))
            ax.set_xlabel(f'x$_c$ ({unit})'); ax.set_title(f'NA {na:g}' + where(th, na))
        axes[0].set_ylabel(f'z$_c$ ({unit})')
        fig.colorbar(pm, ax=list(axes), fraction=0.02, pad=0.02, extend='both').set_label(label)
        fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig); print('Saved ->', name)

    for case in os.environ.get('GRID_CASES', '2ce:pi').split(','):
        pair, th = case.split(':')
        unit = 'λ$_1$' if pair == '2ce' else 'λ$_{2p}$'
        cur = lambda model: (lambda na: tuple(maps(pair, th, model, na)[:3]))
        nsuf = lambda na: '' if medium(th, na) == 1 else f'_n{medium(th, na):g}'
        uni = lambda na: (lambda d: (d['xc'], d['zc'], d['F']))(
            np.load(os.path.join(CACHE, f'{pair}_{th}_vector_na{na:g}{nsuf(na)}.npz')))
        surf_grid((('Vector', cur('vector')), ('Scalar', cur('scalar'))), f'linfoot3d_F_{pair}_{th}_grid{SUF}{MSUF}.png')
        surf_grid((('Vector', cur('vector')),), f'linfoot3d_F_{pair}_{th}_vec{SUF}{MSUF}.png')      # one row, for a wide slot
        diff_row(cur('vector'), cur('scalar'), 'ΔF = vector − scalar', f'linfoot_diff3_F_{pair}_{th}{SUF}{MSUF}.png')
        if AT:
            surf_grid((('Uniform, vector', uni), ('Gaussian, vector', cur('vector'))),
                      f'linfoot3d_F_{pair}_{th}_gauss_uniform{MSUF}.png')
            diff_row(cur('vector'), uni, 'ΔF = Gaussian − uniform', f'linfoot_diff3_F_{pair}_{th}_gauss_uniform{MSUF}.png')
    sys.exit(0)


PANELS = (('scalar', 0.5, 'Scalar 2CE, NA 0.5'), ('vector', 0.7, 'Vector, NA 0.7'), ('vector', 0.9, 'Vector, NA 0.9'))
LIM = {'F': (-3, 1), 'C': (0, 3), 'Q': (0, 1)}       # C rises above 1 for a broader misaligned PSF
for pair in ('2ce', '2pe'):
    for th in ('pi', 'pi2'):
        data = [maps(pair, th, m, na) for m, na, _ in PANELS]
        for k, sym in enumerate('FCQ'):
            fig = plt.figure(figsize=(19.5, 7.0))
            for i, ((m, na, title), (xc, zc, *M)) in enumerate(zip(PANELS, data)):
                XC, ZC = np.meshgrid(xc, zc)
                lim = LIM[sym]
                ax = fig.add_subplot(1, 3, i + 1, projection='3d')
                ax.plot_surface(XC, ZC, np.clip(M[k], *lim), cmap='viridis', edgecolor='k', linewidth=0.2,
                                rstride=1, cstride=1)
                ax.set_zlim(*lim)
                ax.set_ylim(zc.max(), zc.min())                                # z_c from −6 in front to +6 behind
                ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks(np.arange(-6, 7, 3))
                ax.set_zticks({'F': np.arange(-3, 1.01, 1.0), 'C': np.arange(0, 3.01, 1.0), 'Q': np.arange(0, 1.01, 0.5)}[sym])
                ax.set_box_aspect((1.0, 1.0, 0.9), zoom=1.1)
                ax.zaxis.set_ticks_position('lower'); ax.zaxis.set_label_position('lower')
                ax.set_xlabel('x$_c$', labelpad=16); ax.set_ylabel('z$_c$', labelpad=16); ax.set_zlabel(sym, labelpad=14)
                ax.set_title(title + where(th, na))
                ax.view_init(elev=22, azim=120)                                # as in the replication
            fig.subplots_adjust(left=0.04, right=1.0, wspace=0.08)
            fig.savefig(os.path.join(OUT, f'linfoot3d_{sym}_{pair}_{th}{SUF}.png'), dpi=300, bbox_inches='tight')
            plt.close(fig)
            print('Saved ->', f'linfoot3d_{sym}_{pair}_{th}{SUF}.png', flush=True)


# ── difference from the scalar baseline at the same NA: Δ = vector − scalar 2CE ──
NAME = {'F': 'F', 'C': 'C', 'Q': 'Q'}
for pair in ('2ce', '2pe'):
    for th in ('pi', 'pi2'):
        unit = 'λ$_1$' if pair == '2ce' else 'λ$_{2p}$'
        diffs = []
        for na in (0.7, 0.9):
            xc, zc, *V = maps(pair, th, 'vector', na)
            _, _, *S = maps(pair, th, 'scalar', na)
            diffs.append((na, xc, zc, V, S))
        for k, sym in enumerate('FCQ'):
            lim = max(np.percentile(np.abs(V[k] - S[k]), 98) for _, _, _, V, S in diffs)   # a few extreme points set no scale
            lim = max(float(np.ceil(lim * 20) / 20), 0.05)
            fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.4))
            for ax, (na, xc, zc, V, S) in zip(axes, diffs):
                dM = V[k] - S[k]
                pm = ax.pcolormesh(xc, zc, dM, cmap='RdBu_r', vmin=-lim, vmax=lim, shading='nearest', rasterized=True)
                ax.contour(xc, zc, dM, levels=[0.0], colors='k', linewidths=1.5)
                ax.set_box_aspect(1.0)
                ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-6, 7, 2))
                ax.set_xlabel(f'x$_c$ ({unit})')
                ax.set_title(f'NA {na}' + where(th, na))
            axes[0].set_ylabel(f'z$_c$ ({unit})')
            fig.colorbar(pm, ax=list(axes), fraction=0.03, pad=0.03, extend='both').set_label(f'Δ{sym} = vector − scalar')
            fig.savefig(os.path.join(OUT, f'linfoot_diff_{sym}_{pair}_{th}{SUF}.png'), dpi=300, bbox_inches='tight')
            plt.close(fig)
            print('Saved ->', f'linfoot_diff_{sym}_{pair}_{th}{SUF}.png', flush=True)


# ── scalar 2CE at NA 0.5: uniform input against Gaussian input (α_t = 4) ──
if AT:
    for pair in ('2ce', '2pe'):
        for th in ('pi', 'pi2'):
            u = np.load(os.path.join(CACHE, f'{pair}_{th}_scalar_na0.5.npz'))
            g = np.load(os.path.join(CACHE, f'{pair}_{th}_scalar_na0.5{SUF}.npz'))
            for sym in 'FCQ':
                fig = plt.figure(figsize=(14.0, 7.4))
                for i, (dd, title) in enumerate(((u, 'Uniform input'), (g, 'Gaussian input, α$_t$ = 4'))):
                    XC, ZC = np.meshgrid(dd['xc'], dd['zc']); lim = LIM[sym]
                    ax = fig.add_subplot(1, 2, i + 1, projection='3d')
                    ax.plot_surface(XC, ZC, np.clip(dd[sym], *lim), cmap='viridis', edgecolor='k', linewidth=0.2,
                                    rstride=1, cstride=1)
                    ax.set_zlim(*lim); ax.set_ylim(dd['zc'].max(), dd['zc'].min())
                    ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks(np.arange(-6, 7, 3))
                    ax.set_zticks({'F': np.arange(-3, 1.01, 1.0), 'C': np.arange(0, 3.01, 1.0), 'Q': np.arange(0, 1.01, 0.5)}[sym])
                    ax.set_box_aspect((1.0, 1.0, 0.9), zoom=1.1)
                    ax.zaxis.set_ticks_position('lower'); ax.zaxis.set_label_position('lower')
                    ax.set_xlabel('x$_c$', labelpad=16); ax.set_ylabel('z$_c$', labelpad=16); ax.set_zlabel(sym, labelpad=14)
                    ax.set_title(title, fontsize=28)
                    ax.view_init(elev=22, azim=120)
                fig.subplots_adjust(left=0.04, right=1.0, wspace=0.08)
                fig.savefig(os.path.join(OUT, f'linfoot3d_{sym}_{pair}_{th}_input.png'), dpi=300, bbox_inches='tight')
                plt.close(fig)
                print('Saved ->', f'linfoot3d_{sym}_{pair}_{th}_input.png', flush=True)
