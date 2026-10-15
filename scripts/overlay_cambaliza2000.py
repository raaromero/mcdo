r"""Current work drawn over the original panels of Cambaliza & Saloma (2000), on the paper's own axes.

Each panel is calibrated from its axis lines (pixel columns of the x limits, pixel rows of y = 0 and the top tick).
Red: 2PE as in Eq. 6, |U1 + U2|^4; orange dashed: |U1 + U2|^2; blue: 2CE, I1 I2.

    python scripts/overlay_cambaliza2000.py -> output/08_two_color/cambaliza2000/overlay/fig*.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from mcdo.twobeam import beam_field

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
OUT = os.path.join(D, 'overlay'); os.makedirs(OUT, exist_ok=True)
NA, L1, L2, LP = 0.5, 0.750, 0.656, 0.700
# panel: (x0 data, x1 data, col x0, col x1, y0 data, y1 data, row y0, row y1)
CAL = {'fig2a': (-1, 1, 109, 587, 0, 1, 288, 43), 'fig2b': (-1, 1, 109, 587, 0, 1, 293, 50),
       'fig3a': (-5, 5, 113, 600, 0, 1, 320, 50), 'fig3b': (-5, 5, 113, 600, 0, 1, 347, 53),
       'fig6a': (-1, 1, 98, 589, 0, 1, 295, 39), 'fig6b': (-1, 1, 98, 590, 0, 1, 325, 42),
       'fig7a': (-5, 5, 113, 602, 0, 1, 372, 81), 'fig7b': (-5, 5, 113, 605, 0, 1, 319, 31)}
TH = (0.0, np.pi / 2, np.pi)


def U(x, z, lam, th, eps):
    return beam_field(x, z, lam, NA, theta=th, eps=eps)


def curves(key):
    eps = 0.99 if key[3] in '67' else 0.0
    axial = key[3] in '37'
    s = np.linspace(-5, 5, 4001) if axial else np.linspace(-1, 1, 1601)
    X, Z = (0 * s, s) if axial else (s, 0 * s)
    out = []
    for th in TH:
        if key[-1] == 'a':
            E = np.abs(U(X, Z, LP, 0, eps) + U(X, Z, LP, th, eps)) ** 2
            out += [(s, E ** 2 / (E ** 2).max(), '#d62728', '-'), (s, E / E.max(), '#ff7f0e', '--')]
        else:
            v = np.abs(U(X, Z, L1, 0, eps)) ** 2 * np.abs(U(X, Z, L2, th, eps)) ** 2
            out.append((s, v / v.max(), '#1f77b4', '-'))
    return out


for key, (x0, x1, c0, c1, y0, y1, r0, r1) in CAL.items():
    im = np.array(Image.open(os.path.join(D, 'original', f'{key}.png')).convert('L'))
    H, W = im.shape
    sx, sy = (x1 - x0) / (c1 - c0), (y1 - y0) / (r1 - r0)
    ext = (x0 - c0 * sx, x0 + (W - c0) * sx, y0 + (H - r0) * sy, y0 - r0 * sy)
    fig, ax = plt.subplots(figsize=(10, 10 * H / W))
    ax.imshow(im, cmap='gray', extent=ext, aspect='auto', alpha=0.55)
    for s, v, c, ls in curves(key):
        ax.plot(s, y0 + v * (y1 - y0), ls, color=c, lw=1.6, alpha=0.9)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.axis('off')
    fig.savefig(os.path.join(OUT, f'{key}.png'), dpi=200, bbox_inches='tight', pad_inches=0); plt.close(fig)
    print('Saved ->', key)
