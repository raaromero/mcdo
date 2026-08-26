"""Figure output helpers shared by the canonical scripts.

`save_panels` writes each axes of a multi-panel figure as its own PNG, so the
same computation serves both the compact multi-panel figure (for reports) and
one-plot-per-slide figures (for the deck). No values are recomputed.
"""

from __future__ import annotations

import json
import os
import re


def trim_xlim(ax, floor=1e-3, pad=1.08, symmetric=False):
    """Trim the x-axis to where the plotted curves still carry signal.

    Converting an axis from optical to physical units often leaves a window
    sized for the old coordinate, so most of the panel ends up empty. This
    keeps the range out to the last point where any curve exceeds `floor`
    times its own peak.
    """
    lo, hi = None, None
    for line in ax.get_lines():
        x, y = line.get_xdata(), line.get_ydata()
        if len(x) < 2:
            continue
        import numpy as _np
        y = _np.abs(_np.asarray(y, dtype=float))
        if not _np.isfinite(y).any() or y.max() <= 0:
            continue
        keep = _np.asarray(x, dtype=float)[y >= floor * y.max()]
        if keep.size == 0:
            continue
        lo = keep.min() if lo is None else min(lo, keep.min())
        hi = keep.max() if hi is None else max(hi, keep.max())
    if lo is None or hi == lo:
        return
    if symmetric:
        m = max(abs(lo), abs(hi)) * pad
        ax.set_xlim(-m, m)
    else:
        ax.set_xlim(lo if lo < 0 else 0, hi * pad)


def save_panels(fig, axes, outdir: str, prefix: str, dpi: int = 200, pad: float = 0.35):
    """Save each axes in `axes` as ``<outdir>/<prefix>_p<i>.png``.

    Parameters
    ----------
    fig    : the Figure the axes belong to
    axes   : iterable of Axes (row-major order defines the panel numbering)
    outdir : destination directory (created if needed)
    prefix : filename stem, e.g. ``"verify_na_convergence"``
    """
    os.makedirs(outdir, exist_ok=True)
    # A previous run with more panels would leave orphans behind, and those get
    # picked up by review folders and decks as if they were current.
    for stale in os.listdir(outdir):
        if re.fullmatch(re.escape(prefix) + r"_p\d+\.png", stale):
            os.remove(os.path.join(outdir, stale))
    axes = list(axes)
    paths = []
    # Any figure-level title/legend would bleed into a single-panel crop.
    suptitle = fig._suptitle
    sup_vis = suptitle.get_visible() if suptitle is not None else None
    for i, ax in enumerate(axes, start=1):
        # Hide every other axes so the crop cannot pick up a neighbour's spine.
        states = [(other, other.get_visible()) for other in axes if other is not ax]
        for other, _ in states:
            other.set_visible(False)
        if suptitle is not None:
            suptitle.set_visible(False)
        # A panel letter like "(a) " is meaningless once the panel stands alone.
        orig_title = ax.get_title()
        stripped = re.sub(r"^\(\s*[a-zA-Z]\s*\)\s*", "", orig_title)
        if stripped != orig_title:
            ax.set_title(stripped)
        fig.canvas.draw()
        bbox = ax.get_tightbbox(fig.canvas.get_renderer())
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted()).padded(pad)
        path = os.path.join(outdir, f"{prefix}_p{i}.png")
        fig.savefig(path, dpi=dpi, bbox_inches=bbox)
        paths.append(path)
        if stripped != orig_title:
            ax.set_title(orig_title)
        for other, vis in states:
            other.set_visible(vis)
        if suptitle is not None:
            suptitle.set_visible(sup_vis)
    # Record what each panel index actually contains. Changing a figure's
    # layout renumbers its panels, and without this the deck can keep pointing
    # a slide at an index that now holds a different plot.
    manifest = {}
    for i, ax in enumerate(axes, start=1):
        manifest[f"{prefix}_p{i}.png"] = re.sub(
            r"^\(\s*[a-zA-Z]\s*\)\s*", "", ax.get_title())
    with open(os.path.join(outdir, f"{prefix}_panels.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    fig.canvas.draw()
    return paths


def mark_focus(ax, rr, zz, intensity, airy_um=None, level=0.5):
    """Highlight the half-maximum contour (orange) and the Airy radius (red
    dashed) on a 2-D intensity map, the convention used on every field map."""
    cs = ax.contour(rr, zz, intensity, levels=[level],
                    colors=["#ff7f0e"], linewidths=2.4)
    ax.clabel(cs, inline=True, fontsize=9, fmt="%.2f")
    if airy_um is not None:
        for x in (-airy_um, airy_um):
            ax.axvline(x, color="red", ls="--", lw=1.6)
    return cs
