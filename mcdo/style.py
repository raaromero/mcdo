"""One place that sets how every figure in the deck looks.

Scripts call :func:`apply` immediately after importing pyplot. It sets a
seaborn-style font scale, a 300 dpi output resolution, and larger default
figure sizes, so text stays readable when a figure is projected.

    from mcdo.style import apply
    apply()                     # deck standard
    apply(font_scale=1.6)       # denser slide
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

#: Deck standard. Everything below is multiplied by this.
FONT_SCALE = 1.45

#: Base point sizes at font scale 1.0.
BASE = {
    "font.size": 11.0,
    "axes.titlesize": 12.0,
    "axes.labelsize": 11.5,
    "legend.fontsize": 10.0,
    "legend.title_fontsize": 10.5,
    "xtick.labelsize": 10.0,
    "ytick.labelsize": 10.0,
    "figure.titlesize": 13.0,
}


def apply(font_scale: float = FONT_SCALE, dpi: int = 300) -> None:
    """Apply the deck figure style."""
    rc = {key: size * font_scale for key, size in BASE.items()}
    rc.update({
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.axisbelow": True,
        "lines.linewidth": 2.0,
        "lines.markersize": 6.0,
        "axes.linewidth": 1.1,
        "xtick.major.width": 1.1,
        "ytick.major.width": 1.1,
        "legend.frameon": False,
        "figure.constrained_layout.use": False,
    })
    plt.rcParams.update(rc)


def outside_legend(ax, **kwargs):
    """Place a legend clear of the axes, never on top of the data."""
    kwargs.setdefault("loc", "upper left")
    kwargs.setdefault("bbox_to_anchor", (1.02, 1.0))
    kwargs.setdefault("frameon", False)
    kwargs.setdefault("borderaxespad", 0.0)
    return ax.legend(**kwargs)


def ring_labels(ax, cs, center, angles, fontsize):
    """Label nested contour rings at set angles around ``center``, so labels on close rings do not sit side by side.

    ``angles`` maps a contour level to the angle (degrees, in data coordinates) of its label; levels left out stay
    unlabelled. Each label goes on the longest piece of its contour.
    """
    levels, pos = [], []
    for level, segs in zip(cs.levels, cs.allsegs):
        if level not in angles or not segs:
            continue
        v = max(segs, key=len)
        a = np.degrees(np.arctan2(v[:, 1] - center[1], v[:, 0] - center[0]))
        k = int(np.argmin(np.abs((a - angles[level] + 180.0) % 360.0 - 180.0)))
        levels.append(level)
        pos.append((v[k, 0], v[k, 1]))
    if levels:
        ax.clabel(cs, levels, manual=pos, fmt='%d', fontsize=fontsize)
