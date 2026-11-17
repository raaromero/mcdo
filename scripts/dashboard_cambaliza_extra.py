r"""Extra data for the interactive dashboard (dashboard/cambaliza): profile metrics against NA, pulses, scattering, scans.

  metrics.json     "signal|axis|theta|pupil|input|medium" -> [[NA, NRMSE, F, C, Q, side-lobe distance (λ/n), height], ...]
                   scalar against vector, each profile at unit energy over its window (profiles/*.json); side lobe of the
                   vector profile (first maximum beyond the first minimum), λ = 0.7 µm
  pulses.json      DOF of the pulsed response over the continuous one at θ = π against NA (widths.csv), and the axial
                   θ = π profiles at the NAs computed (axial_pi_profiles.npz), vector, beams along y
  scattering.json  Fig. 8 Monte Carlo: I(z) of 2PE and 2CE for each slab half-thickness h (mean of 10 runs and one run)
  img/paper/       the published panels (Figs. 2-8), margins trimmed

    python scripts/dashboard_cambaliza_extra.py
"""
import json
import os

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'output', '08_two_color', 'cambaliza2000')
DATA = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'data')
IMG = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'img', 'paper')
LP = 0.7
META = json.load(open(os.path.join(DATA, 'meta.json')))
r4 = lambda v: float(f'{v:.4g}')


def unit(y, ds):
    y = np.asarray(y, float)
    return y / (y.sum() * ds)


def side_lobe(s, y):
    y = np.asarray(y, float); y = y / y[np.argmin(np.abs(s))]
    i = int(np.argmin(np.abs(s)))
    while i < len(y) - 1 and y[i + 1] <= y[i]:
        i += 1
    j = i
    while j < len(y) - 1 and y[j + 1] >= y[j]:
        j += 1
    if j >= len(y) - 1 or j == i or y[j] < 1e-3:                # none, or below the 4-digit precision of the profiles
        return None, None
    y0, y1, y2 = y[j - 1], y[j], y[j + 1]
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return s[j] + d * (s[1] - s[0]), y1 - 0.25 * (y0 - y2) * d


# ── metrics against NA ──
M = {}
for med, nas in META['na'].items():
    n = META['n'][med]
    for na in nas:
        d = json.load(open(os.path.join(DATA, 'profiles', f'{med}_{na:g}.json')))
        grid = {a: np.linspace(-d[f'grid|{a}'][0], d[f'grid|{a}'][0], int(d[f'grid|{a}'][1])) for a in ('x', 'z')}
        for key in d:
            parts = key.split('|')
            if parts[0] == 'grid' or parts[3] != 'vector':
                continue
            sig, axis, th, _, pupil, inp = parts
            sk = f'{sig}|{axis}|{th}|scalar|{pupil}|{inp}'
            if sk not in d:
                continue
            s = grid[axis]; ds = s[1] - s[0]
            r, a = unit(d[key], ds), unit(d[sk], ds)
            rr = np.sum(r * r)
            F = 1 - np.sum((a - r) ** 2) / rr
            sl, sh = side_lobe(s, d[key])
            M.setdefault(f'{sig}|{axis}|{th}|{pupil}|{inp}|{med}', []).append(
                [na, r4(100 * np.sqrt(max(0.0, 1 - F))), r4(F), r4(np.sum(a * a) / rr), r4(np.sum(a * r) / rr),
                 None if sl is None else r4(sl / (LP / n)), None if sh is None else r4(sh)])
json.dump(M, open(os.path.join(DATA, 'metrics.json'), 'w'), separators=(',', ':'))

# ── pulses ──
W = np.loadtxt(os.path.join(SRC, 'pulses', 'high_na', 'widths.csv'), delimiter=',', ndmin=2)
P = np.load(os.path.join(SRC, 'pulses', 'high_na', 'axial_pi_profiles.npz'))
pul = {'ratio': {}, 'profiles': {}}
for n, med in ((1.0, 'air'), (1.33, 'water')):
    for is2ce, sig in ((0, '2PE'), (1, '2CE')):
        sel = lambda tau: W[(W[:, 0] == n) & (W[:, 2] == is2ce) & (W[:, 3] == 1) & np.isclose(W[:, 4], np.pi) & (W[:, 5] == tau)]
        cw = sel(0.0); cw = cw[np.argsort(cw[:, 1])]
        pul['ratio'][f'{sig}|{med}|cw'] = [[r4(a), r4(c)] for a, c in zip(cw[:, 1], cw[:, 6])]
        for tau in (20.0, 10.0):
            t = sel(tau); t = t[np.argsort(t[:, 1])]
            pul['ratio'][f'{sig}|{med}|{tau:g}'] = [[r4(a), r4(b / c)] for a, b, c in zip(t[:, 1], t[:, 6], cw[:, 6])]
for k in P.files:
    if not k.endswith('_z'):
        continue
    tag = k[:-2]                                                # n1_na0.5
    n, na = tag.split('_')
    med = 'air' if n == 'n1' else 'water'
    z = P[k]; idx = np.linspace(0, len(z) - 1, 501).round().astype(int)
    prof = {'z': [r4(v) for v in z[idx]]}
    for sig, key in (('2PE', '2PE'), ('2CE', '2CE_y')):
        for tau in ('cw', '100', '20', '10'):
            v = P[f'{tag}_{key}_{tau}'][idx]
            prof[f'{sig}|{tau}'] = [r4(x) for x in v / v.max()]
    pul['profiles'][f'{med}|{float(na[2:]):g}'] = prof
json.dump(pul, open(os.path.join(DATA, 'pulses.json'), 'w'), separators=(',', ':'))

# ── scattering (Fig. 8) ──
sc = {}
for h in (20, 50, 100, 300, 1000):
    R = np.load(os.path.join(SRC, f'fig8_mc_h{h}.npz'))
    z = R['z']
    f2p = lambda a, b: (a + b[::-1]) ** 2
    f2c = lambda a, b: a * b[::-1]
    out = {'z': [r4(v) for v in z]}
    for sig, f, a, b in (('2PE', f2p, '2p_a', '2p_b'), ('2CE', f2c, 'l1', 'l2')):
        mean = f(R[a].mean(0), R[b].mean(0)); one = f(R[a][0], R[b][0])
        top = mean.max()
        out[sig] = [r4(v) for v in mean / top]
        out[f'{sig}|one'] = [r4(v) for v in one / top]
        out[f'{sig}|bg'] = r4((mean / top)[np.abs(z) > 10].mean())
        # each beam's excitation (beam 2 enters at z = +h), normalized to its own peak, as the dashed curves of Fig. 8
        for k, key, flip in (('e1', a, False), ('e2', b, True)):
            for tag, v in (('', R[key].mean(0)), ('|one', R[key][0])):
                v = v[::-1] if flip else v
                out[f'{sig}|{k}{tag}'] = [r4(x) for x in v / v.max()]
    # no scattering: Gaussian beams, I ∝ w0²/w²(z)
    na = float(R['na']) if 'na' in R else 0.5
    I = lambda lam: 1 / (1 + (z * lam / (np.pi * (lam / (np.pi * na)) ** 2)) ** 2)
    for sig, v in (('2PE', (I(0.7) + I(0.7)[::-1]) ** 2), ('2CE', I(0.75) * I(0.656)[::-1])):
        out[f'{sig}|ref'] = [r4(x) for x in v / v.max()]
    sc[str(h)] = out
json.dump(sc, open(os.path.join(DATA, 'scattering.json'), 'w'), separators=(',', ':'))

# ── published panels ──
os.makedirs(IMG, exist_ok=True)
for f in sorted(os.listdir(os.path.join(SRC, 'original'))):
    im = Image.open(os.path.join(SRC, 'original', f)).convert('RGB')
    box = Image.eval(im.convert('L'), lambda v: 255 if v < 235 else 0).getbbox()
    if box:
        im = im.crop((max(box[0] - 6, 0), max(box[1] - 6, 0), min(box[2] + 6, im.width), min(box[3] + 6, im.height)))
    im.save(os.path.join(IMG, f), optimize=True)
print('metrics', len(M), '| pulses', len(pul['ratio']), len(pul['profiles']), '| scattering', len(sc), '| paper',
      len(os.listdir(IMG)))
