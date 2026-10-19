r"""Cambaliza & Saloma (2000) at high NA, every pupil and input: circular and annular (ε = 0.99) pupils, uniform and
Gaussian (α_t = 4) input, three polarizations of the vector focus, paraxial scalar for reference; air and water.
Also the wavelength gap Δλ of Figs. 4-5 against NA.

Polarization of the vector focus (the choice open for Lim & Saloma 2002, so the two studies can share it):
  s      both beams along y, perpendicular to the plane of the two axes (cambaliza2000_high_na.py)
  p      both beams in that plane (beam 1 along x)
  unpol  2CE only: each beam's intensity averaged over s and p, as in the Lim & Saloma runs (2PE stays s there)
Width: FWHM of the central peak, transverse F(x, 0, 0; θ) and axial F(0, 0, z; θ) (DOF). The window grows until the
profile falls to half (an annular pupil stretches the DOF by up to 1/(1 − ε²) = 50).
θ = π/2 needs both lenses to fit at 90°: NA ≤ n sin 45° (air 0.71, water 0.94).

    [WORKERS=6] python scripts/cambaliza2000_high_na_pupils.py [--rerun]
    -> output/08_two_color/cambaliza2000/high_na/pupils/{widths.csv, dlambda.csv, numbers.txt, *.png}
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.twobeam import beam_field, intensity
from mcdo.apodization import gaussian

_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'high_na', 'pupils')
os.makedirs(OUT, exist_ok=True)
L1, L2, LP, LE = 0.750, 0.656, 0.700, 0.350
EPS, AT = 0.99, 4.0
THETAS = (0.0, np.pi / 2, np.pi)
TLAB = {0.0: 'θ = 0', np.pi / 2: 'θ = π/2', np.pi: 'θ = π'}
TCOL = {0.0: 'k', np.pi / 2: '#d62728', np.pi: '#1f77b4'}
MEDIA = ((1.0, np.round(np.arange(0.2, 0.951, 0.05), 3)), (1.33, np.round(np.arange(0.2, 1.251, 0.05), 3)))
LADDER = (1, 8, 64)                                    # window growth until the profile falls to half


def fwhm(s, y):
    """FWHM of the central peak (at s = 0), normalized to its value at s = 0; nan if it never falls to half."""
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


def fits(na, n, th):
    return th != np.pi / 2 or na <= n * np.sin(np.pi / 4) + 1e-9


def signals(X, Z, na, n, eps, at, ths=THETAS, lams=None):
    """{(signal, θ, model): profile}; model 'scalar' or the vector polarization 's', 'p', 'unpol' (2CE only)."""
    apod = gaussian(at, (na / n) ** 2) if at else None
    l1, l2 = lams or (L1, L2)
    out = {}
    for model in ('scalar', 'rw'):
        def f(lam, th, psi=None):
            if model == 'scalar':
                return beam_field(X, Z, lam, na, n, theta=th, eps=eps, apodization=apod)
            return beam_field(X, Z, lam, na, n, theta=th, eps=eps, apodization=apod, model='rw', psi=psi,
                              n_theta=121 if eps else 301)             # thin annulus: 121 angles resolve it
        if model == 'scalar':
            p1, c1 = f(LP, 0.0), f(l1, 0.0)
            for th in ths:
                if lams is None:
                    out[('2PE', th, 'scalar')] = intensity(p1 + f(LP, th)) ** 2
                out[('2CE', th, 'scalar')] = intensity(c1) * intensity(f(l2, th))
            continue
        P1 = {pol: f(LP, 0.0, psi) for pol, psi in (('s', np.pi / 2), ('p', 0.0))} if lams is None else {}
        C1 = {pol: intensity(f(l1, 0.0, psi)) for pol, psi in (('s', np.pi / 2), ('p', 0.0))}
        for th in ths:
            C2 = {pol: intensity(f(l2, th, psi)) for pol, psi in (('s', np.pi / 2), ('p', 0.0))}
            for pol in ('s', 'p'):
                if lams is None:
                    out[('2PE', th, pol)] = intensity(P1[pol] + f(LP, th, {'s': np.pi / 2, 'p': 0.0}[pol])) ** 2
                out[('2CE', th, pol)] = C1[pol] * C2[pol]
            out[('2CE', th, 'unpol')] = 0.25 * (C1['s'] + C1['p']) * (C2['s'] + C2['p'])
    return out


def widths(na, n, eps, at, ths=THETAS, lams=None):
    """{(signal, axis, θ, model): FWHM (µm)}, each from the first window in which the profile falls to half.
    At θ = π/2 the narrow transverse spot of the other beam sets both widths, so its window is the transverse one."""
    res = {}
    for axis in ('x', 'z'):
        for group in ([t for t in ths if t == np.pi / 2], [t for t in ths if t != np.pi / 2]):
            need = [t for t in group if fits(na, n, t)]
            long_ = axis == 'z' and np.pi / 2 not in group
            base = 6 * LP * n / na ** 2 if long_ else 2.5 * LP / na
            for g in LADDER:
                if not need:
                    break
                s = np.linspace(-g * base, g * base, 4001 if long_ else 2001)
                if long_:                                  # fine core: the λ/4n-wide central 2PE fringe at θ = π
                    s = np.union1d(s, np.linspace(-1.0, 1.0, 1001))
                X, Z = (s, 0 * s) if axis == 'x' else (0 * s, s)
                for (sig, th, model), v in signals(X, Z, na, n, eps, at, need, lams).items():
                    key = (sig, axis, th, model)
                    if key not in res or np.isnan(res[key]):
                        res[key] = fwhm(s, v)
                need = sorted({k[2] for k, v in res.items() if k[1] == axis and k[2] in group and np.isnan(v)})
    return res


def one(job):
    n, na, eps, at = job
    W = widths(na, n, eps, at)
    print(f'n {n} NA {na:.2f} ε {eps} α_t {at} done', flush=True)
    return [dict(n=n, NA=na, eps=eps, alpha_t=at, signal=sig, axis=ax, theta=th, model=m, fwhm=w)
            for (sig, ax, th, m), w in W.items()]


def pair(dl):
    """λ1 − λ2 = dl with 1/λ1 + 1/λ2 = 1/λe (µm), as in replicate_cambaliza2000.py."""
    b, c = dl - 2 * LE, -LE * dl
    l2 = (-b + np.sqrt(b * b - 4 * c)) / 2
    return l2 + dl, l2


DLS = np.arange(0.010, 0.0941, 0.0105)
DL_NA = ((1.0, (0.3, 0.5, 0.7)), (1.33, (0.5, 0.7, 0.9)))


def one_dl(job):
    n, na, dl = job
    W = widths(na, n, 0.0, 0.0, ths=(np.pi / 2,), lams=pair(dl))
    return [dict(n=n, NA=na, dl_nm=round(dl * 1000, 2), axis=ax, model=m, fwhm=w) for (_, ax, _, m), w in W.items()]


CSV, DCSV = os.path.join(OUT, 'widths.csv'), os.path.join(OUT, 'dlambda.csv')


def compute():
    from multiprocessing import Pool
    jobs = [(n, na, eps, at) for n, nas in MEDIA for na in nas for eps in (0.0, EPS) for at in (0.0, AT)]
    jobs.sort(key=lambda j: j[1])
    djobs = [(n, na, dl) for n, nas in DL_NA for na in nas for dl in DLS]
    with Pool(int(os.environ.get('WORKERS', 6))) as pool:
        if '--rerun' in sys.argv or not os.path.exists(DCSV):
            pd.DataFrame([r for rs in pool.map(one_dl, djobs, chunksize=1) for r in rs]).to_csv(DCSV, index=False)
            print('Saved ->', DCSV, flush=True)
        if '--rerun' in sys.argv or not os.path.exists(CSV):
            pd.DataFrame([r for rs in pool.map(one, jobs, chunksize=1) for r in rs]).to_csv(CSV, index=False)
            print('Saved ->', CSV, flush=True)


# ─────────────────────────────── figures ───────────────────────────────

def log_na_axes(ax, xmax=1.25):
    ax.set_xscale('log')
    ax.set_xticks([0.2, 0.3, 0.5, 0.7, 1.0]); ax.set_xticklabels(['0.2', '0.3', '0.5', '0.7', '1'])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel('NA')


def save(fig, name, axes, ncol, legend_axes=None):
    h, l = (legend_axes or axes[0]).get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=ncol, bbox_to_anchor=(0.5, 0.0), frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved ->', name)


def figures():
    D = pd.read_csv(CSV)

    def sel(n, eps, at, sig, axis, th, model):
        d = D[(D.n == n) & (D.eps == eps) & (D.alpha_t == at) & (D.signal == sig) & (D.axis == axis)
              & np.isclose(D.theta, th) & (D.model == model)].sort_values('NA')
        return d.NA.values, d.fwhm.values

    # 1. annular pupils: widths against NA, vector (s) solid, scalar dashed — as widths_<medium>_<axis>.png for circular
    for n, tag in ((1.0, 'air'), (1.33, 'water')):
        for axis in ('x', 'z'):
            fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.7))
            for ax, sig in zip(axes, ('2PE', '2CE')):
                for th in THETAS:
                    ax.plot(*sel(n, EPS, 0, sig, axis, th, 's'), '-o', color=TCOL[th], lw=3, ms=8, label=f'{TLAB[th]}, vector')
                    ax.plot(*sel(n, EPS, 0, sig, axis, th, 'scalar'), '--', color=TCOL[th], lw=2.5,
                            label=f'{TLAB[th]}, scalar')
                log_na_axes(ax); ax.set_yscale('log')
                ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
                ax.set_title(f'{sig}, annular, {"transverse FWHM" if axis == "x" else "DOF"}'); ax.set_ylabel('Width (µm)')
            save(fig, f'annular_widths_{tag}_{axis}.png', axes, 3)

    # 2. annular / circular width against NA (vector s), air solid, water dashed
    for axis in ('x', 'z'):
        fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.7), sharey=True)
        for ax, sig in zip(axes, ('2PE', '2CE')):
            for n, ls, tag in ((1.0, '-o', 'air'), (1.33, '--s', 'water')):
                for th in THETAS:
                    a, wa = sel(n, EPS, 0, sig, axis, th, 's'); c, wc = sel(n, 0.0, 0, sig, axis, th, 's')
                    ax.plot(a, wa / wc, ls, color=TCOL[th], lw=3, ms=8, mfc=TCOL[th] if n == 1 else 'white',
                            label=f'{TLAB[th]}, {tag}')
            log_na_axes(ax); ax.set_yscale('log')
            ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
            ax.set_title(f'{sig}, {"transverse FWHM" if axis == "x" else "DOF"}, annular / circular')
        axes[0].set_ylabel('Width ratio')
        save(fig, f'annular_over_circular_{axis}.png', axes, 3)

    # 3. the paper's annular comparisons (pp. 31-32) against NA, vector (s) solid, scalar dashed, air and water
    P = np.pi / 2
    same, less, more = (lambda r: r), (lambda r: 1 - r), (lambda r: r - 1)
    RAT = (('2CE spot, θ = 0 over θ = π/2 (Fig. 6b)', ('2CE', 'x', 0.0, EPS), ('2CE', 'x', P, EPS), 0.82, same),
           ('2PE spot narrower than 2CE, θ = π/2 (p. 31)', ('2PE', 'x', P, EPS), ('2CE', 'x', P, EPS), 0.35, less),
           ('2CE DOF shorter than circular, θ = π/2 (p. 32)', ('2CE', 'z', P, EPS), ('2CE', 'z', P, 0.0), 0.40, less),
           ('2CE DOF longer than 2PE, θ = π/2 (p. 32)', ('2CE', 'z', P, EPS), ('2PE', 'z', P, 0.0), 0.20, more))
    for part, rats in (('x', RAT[:2]), ('z', RAT[2:])):           # two comparisons per slide: larger panels
        fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.9))
        for ax, (lab, a, b, paper, tr) in zip(axes, rats):
            for n, mk, tag in ((1.0, 'o', 'air'), (1.33, 's', 'water')):
                for model, c, ls in (('s', '#1f77b4', '-'), ('scalar', '#d62728', '--')):
                    na_a, wa = sel(n, a[3], 0, a[0], a[1], a[2], model); na_b, wb = sel(n, b[3], 0, b[0], b[1], b[2], model)
                    m = np.intersect1d(na_a, na_b)
                    r = tr(wa[np.isin(na_a, m)] / wb[np.isin(na_b, m)])
                    ax.plot(m, r, ls + mk, color=c, lw=3, ms=9, mfc=c if n == 1 else 'white',
                            label=f'{"Vector" if model == "s" else "Scalar"}, {tag}')
            ax.plot([0.5], [paper], '*', color='k', ms=22, label='Published (NA 0.5)')
            ax.set_title(lab, fontsize=24); ax.set_xlabel('NA')
        save(fig, f'annular_quoted_{part}.png', axes, 5)

    # 4. Gaussian input (α_t = 4) / uniform: width ratio against NA, vector (s), circular and annular
    for eps, etag in ((0.0, 'circular'), (EPS, 'annular')):
        fig, axes = plt.subplots(2, 2, figsize=(18.5, 6.7)); axes = axes.ravel()
        for i, sig in enumerate(('2PE', '2CE')):
            for j, axis in enumerate(('x', 'z')):
                ax = axes[2 * i + j]
                for n, ls, tag in ((1.0, '-o', 'air'), (1.33, '--s', 'water')):
                    for th in THETAS:
                        g, wg = sel(n, eps, AT, sig, axis, th, 's'); u, wu = sel(n, eps, 0, sig, axis, th, 's')
                        ax.plot(g, wg / wu, ls, color=TCOL[th], lw=3, ms=8, mfc=TCOL[th] if n == 1 else 'white',
                                label=f'{TLAB[th]}, {tag}')
                ax.axhline(1, color='#999999', lw=2, ls=':')
                ax.set_title(f'{sig}, {"FWHM" if axis == "x" else "DOF"}')
                ax.set_xlabel('NA')
        axes[0].set_ylabel('Gaussian / uniform'); axes[2].set_ylabel('Gaussian / uniform')
        save(fig, f'gaussian_over_uniform_{etag}.png', axes, 3)

    # 5. polarization: 2CE widths with unpolarized and p beams over s beams, circular, uniform
    for eps, etag in ((0.0, 'circular'), (EPS, 'annular')):
        fig, axes = plt.subplots(2, 2, figsize=(18.5, 6.7)); axes = axes.ravel()
        for i, model in enumerate(('unpol', 'p')):
            for j, axis in enumerate(('x', 'z')):
                ax = axes[2 * i + j]
                for n, ls, tag in ((1.0, '-o', 'air'), (1.33, '--s', 'water')):
                    for th in THETAS:
                        a, wa = sel(n, eps, 0, '2CE', axis, th, model); b, wb = sel(n, eps, 0, '2CE', axis, th, 's')
                        ax.plot(a, wa / wb, ls, color=TCOL[th], lw=3, ms=8, mfc=TCOL[th] if n == 1 else 'white',
                                label=f'{TLAB[th]}, {tag}')
                ax.axhline(1, color='#999999', lw=2, ls=':')
                ax.set_title(f'{"FWHM" if axis == "x" else "DOF"}, {"unpol." if model == "unpol" else "p"} / s')
                ax.set_xlabel('NA')
        axes[0].set_ylabel('2CE width ratio'); axes[2].set_ylabel('2CE width ratio')
        save(fig, f'polarization_2ce_{etag}.png', axes, 3)

    # 6. polarization: vector / scalar 2CE width against NA, for s, p and unpolarized beams (circular, uniform)
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.7), sharey=True)
    PC = {'s': '#1f77b4', 'p': '#2ca02c', 'unpol': '#ff7f0e'}
    PL = {'s': 's', 'p': 'p', 'unpol': 'unpolarized'}
    for ax, axis in zip(axes, ('x', 'z')):
        for model in ('s', 'p', 'unpol'):
            for n, ls, tag in ((1.0, '-o', 'air'), (1.33, '--s', 'water')):
                a, wa = sel(n, 0.0, 0, '2CE', axis, np.pi, model); b, wb = sel(n, 0.0, 0, '2CE', axis, np.pi, 'scalar')
                ax.plot(a, wa / wb, ls, color=PC[model], lw=3, ms=8, mfc=PC[model] if n == 1 else 'white',
                        label=f'{PL[model]}, {tag}')
        ax.axhline(1, color='#999999', lw=2, ls=':')
        ax.set_xlabel('NA'); ax.set_title(f'2CE θ = π, {"transverse FWHM" if axis == "x" else "DOF"}, vector / scalar')
    axes[0].set_ylabel('Width ratio')
    save(fig, 'polarization_vector_over_scalar.png', axes, 3)

    # 7. Δλ (Figs. 4-5) against NA: 2CE θ = π/2 width relative to Δλ = 10 nm, vector (s) solid, scalar dashed
    E = pd.read_csv(DCSV)
    NCOL = {(1.0, 0.3): '#9467bd', (1.0, 0.5): 'k', (1.0, 0.7): '#1f77b4',
            (1.33, 0.5): '#ff7f0e', (1.33, 0.7): '#2ca02c', (1.33, 0.9): '#d62728'}
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.0), sharey=True)
    for ax, axis in zip(axes, ('x', 'z')):
        for (n, na), c in NCOL.items():
            for model, ls in (('s', '-o'), ('scalar', '--')):
                d = E[(E.n == n) & np.isclose(E.NA, na) & (E.axis == axis) & (E.model == model)].sort_values('dl_nm')
                ax.plot(d.dl_nm, d.fwhm / d.fwhm.iloc[0], ls, color=c, lw=3 if model == 's' else 2.5, ms=8,
                        label=f'NA {na:g} {"air" if n == 1 else "water"}, {"vector" if model == "s" else "scalar"}')
        ax.set_xlabel('Δλ (nm)'); ax.set_xlim(0, 100)
        ax.set_title(f'2CE θ = π/2, {"FWHM" if axis == "x" else "DOF"} / value at 10 nm')
    axes[0].set_ylabel('Relative width')
    save(fig, 'dlambda_vs_na.png', axes, 4)

    # numbers quoted on the slides
    L = []
    for n in (1.0, 1.33):
        for na in (0.5, 0.7, 0.9, 1.2):
            for axis in ('x', 'z'):
                for th in THETAS:
                    def g(eps, at, model, sig='2CE'):
                        d = D[(D.n == n) & np.isclose(D.NA, na) & (D.eps == eps) & (D.alpha_t == at) & (D.signal == sig)
                              & (D.axis == axis) & np.isclose(D.theta, th) & (D.model == model)]
                        return d.fwhm.values[0] if len(d) else np.nan
                    if np.isnan(g(0.0, 0, 's')):
                        continue
                    L.append(f'n {n} NA {na} {axis} {TLAB[th]}: 2CE circ s {g(0.0, 0, "s"):.3f} p {g(0.0, 0, "p"):.3f} '
                             f'unpol {g(0.0, 0, "unpol"):.3f} scalar {g(0.0, 0, "scalar"):.3f} | annular s '
                             f'{g(EPS, 0, "s"):.3f} scalar {g(EPS, 0, "scalar"):.3f} | Gaussian s {g(0.0, AT, "s"):.3f} '
                             f'| 2PE circ s {g(0.0, 0, "s", "2PE"):.3f} p {g(0.0, 0, "p", "2PE"):.3f}')
    for (n, na) in NCOL:
        for axis in ('x', 'z'):
            for model in ('s', 'unpol', 'scalar'):
                d = E[(E.n == n) & np.isclose(E.NA, na) & (E.axis == axis) & (E.model == model)].sort_values('dl_nm')
                L.append(f'Δλ n {n} NA {na} {axis} {model}: 10 nm {d.fwhm.iloc[0]:.4f} µm, 94 nm {d.fwhm.iloc[-1]:.4f} µm, '
                         f'change {d.fwhm.iloc[-1] / d.fwhm.iloc[0] - 1:+.3f}')
    open(os.path.join(OUT, 'numbers.txt'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    compute()
    figures()
