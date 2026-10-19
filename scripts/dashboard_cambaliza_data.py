r"""Data for the Cambaliza & Saloma (2000) dashboard (dashboard/cambaliza/): replication at NA 0.5 and the extension to high and
low NA, air and water, circular and annular (ε = 0.99) pupils, uniform and Gaussian (α = 4) input.

Profiles: transverse F(x, 0, 0; θ) and axial F(0, 0, z; θ) of 2PE and 2CE, θ = 0, π/2, π, paraxial scalar (the paper's
Eq. 1) and vector (Richards-Wolf, both beams along y), each normalized to its own maximum, on the paper's window scaled
with NA: x ±1 µm × (0.5/NA), z ±5 µm × n (0.5/NA)² (Figs. 2-3 and 6-7 at NA 0.5 in air).
Widths: from cambaliza2000_high_na_pupils.py (widths.csv, dlambda.csv) — run that first.

    python scripts/dashboard_cambaliza_data.py -> dashboard/cambaliza/public/data/{meta,widths,dlambda}.json, profiles/*.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import pandas as pd
from PIL import Image

from mcdo.twobeam import beam_field, intensity
from mcdo.apodization import gaussian

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'output', '08_two_color', 'cambaliza2000')
OUT = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'data')
IMG = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'img')
L1, L2, LP = 0.750, 0.656, 0.700
EPS, AT = 0.99, 4.0
THETAS = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}
NPT = 401


def fits(na, n, th):
    return th != 'pi2' or na <= n * np.sin(np.pi / 4) + 1e-9


def profiles(na, n):
    """{key: [values]} with key 'signal|axis|theta|model|pupil|input'; values normalized, 4 significant digits."""
    out = {}
    for axis in ('x', 'z'):
        half = 1.0 * 0.5 / na if axis == 'x' else 5.0 * n * (0.5 / na) ** 2
        s = np.linspace(-half, half, NPT)
        X, Z = (s, 0 * s) if axis == 'x' else (0 * s, s)
        for pupil, eps in (('circ', 0.0), ('ann', EPS)):
            for inp, at in (('uni', 0.0), ('gau', AT)):
                apod = gaussian(at, (na / n) ** 2) if at else None
                for model in ('scalar', 'vector'):
                    def f(lam, th):
                        if model == 'scalar':
                            return beam_field(X, Z, lam, na, n, theta=th, eps=eps, apodization=apod)
                        return beam_field(X, Z, lam, na, n, theta=th, eps=eps, apodization=apod, model='rw',
                                          psi=np.pi / 2, n_theta=121 if eps else 301)
                    p1, c1 = f(LP, 0.0), intensity(f(L1, 0.0))
                    for tk, th in THETAS.items():
                        if not fits(na, n, tk):
                            continue
                        for sig, v in (('2PE', intensity(p1 + f(LP, th)) ** 2), ('2CE', c1 * intensity(f(L2, th)))):
                            out[f'{sig}|{axis}|{tk}|{model}|{pupil}|{inp}'] = [float(f'{u:.4g}') for u in v / v.max()]
        out[f'grid|{axis}'] = [round(float(half), 5), NPT]
    return out


def main():
    os.makedirs(os.path.join(OUT, 'profiles'), exist_ok=True)
    W = pd.read_csv(os.path.join(SRC, 'high_na', 'pupils', 'widths.csv'))
    W = W[W.model.isin(['s', 'scalar'])].copy()
    W['model'] = W.model.map({'s': 'vector', 'scalar': 'scalar'})
    W['theta'] = W.theta.map(lambda t: '0' if t < 0.1 else ('pi2' if t < 2 else 'pi'))
    W['pupil'] = W.eps.map(lambda e: 'ann' if e > 0 else 'circ')
    W['input'] = W.alpha_t.map(lambda a: 'gau' if a > 0 else 'uni')
    W['medium'] = W.n.map(lambda n: 'air' if n == 1 else 'water')
    widths = {}
    for r in W.itertuples():
        if np.isfinite(r.fwhm):
            widths.setdefault(f'{r.signal}|{r.axis}|{r.theta}|{r.model}|{r.pupil}|{r.input}|{r.medium}', []).append(
                [round(r.NA, 3), round(float(r.fwhm), 5)])
    for v in widths.values():
        v.sort()
    json.dump(widths, open(os.path.join(OUT, 'widths.json'), 'w'), separators=(',', ':'))
    D = pd.read_csv(os.path.join(SRC, 'high_na', 'pupils', 'dlambda.csv'))
    D = D[D.model.isin(['s', 'scalar'])]
    dl = {}
    for (n, na, axis, model), g in D.groupby(['n', 'NA', 'axis', 'model']):
        g = g.sort_values('dl_nm')
        dl[f'{"air" if n == 1 else "water"}|{na:g}|{axis}|{"vector" if model == "s" else "scalar"}'] = \
            [[float(a), round(float(b), 5)] for a, b in zip(g.dl_nm, g.fwhm)]
    json.dump(dl, open(os.path.join(OUT, 'dlambda.json'), 'w'), separators=(',', ':'))
    nas = {'air': sorted({round(v, 3) for v in W[W.medium == 'air'].NA}),
           'water': sorted({round(v, 3) for v in W[W.medium == 'water'].NA})}
    for med, n in (('air', 1.0), ('water', 1.33)):
        for na in nas[med]:
            path = os.path.join(OUT, 'profiles', f'{med}_{na:g}.json')
            if not os.path.exists(path) or '--rerun' in sys.argv:
                json.dump(profiles(na, n), open(path, 'w'), separators=(',', ':'))
                print(f'{med} NA {na:g}', flush=True)
    json.dump({'na': nas, 'n': {'air': 1.0, 'water': 1.33}, 'lam': {'l1': L1, 'l2': L2, 'lp': LP}, 'eps': EPS,
               'alpha': AT}, open(os.path.join(OUT, 'meta.json'), 'w'))
    os.makedirs(IMG, exist_ok=True)                    # the replication overlays (current work over the paper)
    for k in ('fig2a', 'fig2b', 'fig3a', 'fig3b', 'fig6a', 'fig6b', 'fig7a', 'fig7b'):
        im = Image.open(os.path.join(SRC, 'overlay', f'{k}.png'))
        im.thumbnail((1200, 1200))
        im.save(os.path.join(IMG, f'{k}.png'), optimize=True)
    for k, f in (('paper4a', 'original/fig4a'), ('paper4b', 'original/fig4b'), ('paper5', 'original/fig5'),
                 ('cw4a', 'panels/fig4a'), ('cw4b', 'panels/fig4b'), ('cw5', 'panels/fig5')):
        im = Image.open(os.path.join(SRC, f'{f}.png')).convert('RGB')   # Figs. 4-5: the paper and current work side by side
        im.thumbnail((1200, 1200))
        im.save(os.path.join(IMG, f'{k}.png'), optimize=True)
    print('Saved ->', OUT)


if __name__ == '__main__':
    main()
