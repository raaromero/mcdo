"""Inset that shows where a profile or width is measured: the computed PSF in the x–z plane with the cut drawn on it.

    from mcdo.cutinset import cut_inset
    cut_inset(ax, 'x')                          # across the axis, at z = 0 (2CE, θ = π/2, NA 0.5 by default)
    cut_inset(ax, 'z', sig='2PE', theta=np.pi)  # along the axis, at x = 0
    cut_inset(ax, 'xz')                         # both cuts (e.g. FWHM and DOF on one plot)

The map is the paraxial scalar PSF of Eqs. 1-6 (2CE 750 + 656 nm, 2PE 700 nm), equal scales in x and z, on white:
filled contours (25/50/75% of the peak) with the half-maximum contour in black; the plotted cut as a red line labelled
"z = 0" (across) or "x = 0" (along); the measured width (FWHM or DOF) as a dimension line beside the spot, from the
half-maximum crossings; x and z arrows; a scale bar in µm.

Call it after the curves and the axis limits are set: the inset (a fixed square in inches) goes to the corner with the
fewest plotted points,
or outside the axes at the right when every corner would cover a curve.
Orientation as in the setup diagram: x to the right, z (the axis of lens L1) downwards.
"""

from __future__ import annotations

import numpy as np
from functools import lru_cache

from mcdo.twobeam import beam_field, two_color, two_photon

CUT = '#00e5ff'
CUT_LINE = '#d62728'                                     # the plotted cut, on the white inset


@lru_cache(maxsize=64)
def _psf(sig, theta, na, n, eps, half, npx=161):
    s = np.linspace(-half, half, npx)
    X, Z = np.meshgrid(s, s)
    if sig == '2PE':
        f = two_photon(beam_field(X, Z, 0.700, na, n, eps=eps), beam_field(X, Z, 0.700, na, n, theta=theta, eps=eps))
    else:
        f = two_color(beam_field(X, Z, 0.750, na, n, eps=eps), beam_field(X, Z, 0.656, na, n, theta=theta, eps=eps))
    return f / f.max()


def _points(ax):
    """Plotted points of ax in axes coordinates (lines and markers)."""
    to_axes = ax.transData + ax.transAxes.inverted()
    pts = []
    for ln in ax.lines:
        xy = np.column_stack(ln.get_data()).astype(float)
        if len(xy) > 1:                                     # densify so long straight segments count
            t = np.linspace(0, 1, 8)[:, None, None]
            xy = (xy[:-1] * (1 - t) + xy[1:] * t).reshape(-1, 2)
        pts.append(xy)
    for c in ax.collections:
        off = c.get_offsets()
        if len(off):
            pts.append(np.asarray(off, float))
    out = to_axes.transform(np.concatenate(pts)) if pts else np.zeros((0, 2))
    out = out[np.isfinite(out).all(axis=1)]
    leg = ax.get_legend()
    if leg is not None:                                       # a legend inside the axes is occupied space too
        ax.figure.canvas.draw()
        b = leg.get_window_extent().transformed(ax.transAxes.inverted())
        if b.x0 >= -0.01 and b.x1 <= 1.01 and b.y0 >= -0.01 and b.y1 <= 1.01:
            gx, gy = np.meshgrid(np.linspace(b.x0, b.x1, 12), np.linspace(b.y0, b.y1, 12))
            out = np.concatenate([out, np.column_stack([gx.ravel(), gy.ravel()])])
    return out


def place_legend(ax, ncol_outside=None, **kw):
    """Legend inside the axes where it covers no plotted point; otherwise in one row just above the axes.

    Call after the curves and the axis limits are set, and before cut_inset (which then avoids the legend)."""
    fig = ax.figure
    opts = dict(frameon=False, handlelength=1.3, handletextpad=0.4, labelspacing=0.25, borderaxespad=0.4, columnspacing=1.0)
    opts.update(kw)
    xy = _points(ax) if ax.get_legend() is None else None
    if xy is None:
        ax.get_legend().remove()
        xy = _points(ax)
    for loc in ('upper right', 'upper left', 'center right', 'center left', 'lower right', 'lower left', 'upper center',
                'lower center', 'center'):
        leg = ax.legend(loc=loc, **opts)
        fig.canvas.draw()
        b = leg.get_window_extent().transformed(ax.transAxes.inverted())
        pad = 0.015
        if not np.any((xy[:, 0] > b.x0 - pad) & (xy[:, 0] < b.x1 + pad) & (xy[:, 1] > b.y0 - pad) & (xy[:, 1] < b.y1 + pad)):
            return leg
        leg.remove()
    n = len(ax.get_legend_handles_labels()[0])
    opts['borderaxespad'] = 0.2
    off = 0.0
    if ax.get_title():                                        # above the title, not on it
        fig.canvas.draw()
        off = (ax.title.get_window_extent().y1 - ax.bbox.y1) / ax.bbox.height + 0.01
    leg = ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0 + off), ncol=ncol_outside or n, **opts)
    fig.canvas.draw()
    if ncol_outside is None and leg.get_window_extent().width > 1.05 * ax.bbox.width:   # wider than the plot: two rows
        leg.remove()
        leg = ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0 + off), ncol=-(-n // 2), **opts)
    leg.set_label('<outside>')
    return leg


def cut_inset(ax, cut: str, size: float = 2.2, where: str = 'auto', label_size: float = 28, sig: str = '2CE',
              theta: float = np.pi / 2, na: float = 0.5, n: float = 1.0, eps: float = 0.0, half: float | None = None,
              profile: bool = False):
    """profile=True: the plot is a whole profile, not a width (e.g. Fig. 8): caption "Profile at x = 0", no dimension line."""
    """Draw a size × size inch inset of the computed PSF on ax; returns the inset axes."""
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    fig = ax.figure
    import warnings
    with warnings.catch_warnings():                           # lay the figure out first, so the free-corner test sees the
        warnings.simplefilter('ignore')                       # final axes size (tight_layout later would shrink the axes
        try:                                                  # under a fixed-size inset and uncover hidden points)
            fig.tight_layout()
        except Exception:
            pass
    pos = ax.get_position()
    W, H = fig.get_size_inches()
    xy = _points(ax) if where == 'auto' else None

    def caption(sz):                                          # the inset's title: one line per cut, or two when the inset is small
        two = sz < 2.4
        text = '\n'.join(((f'{nm}\nat {at}' if two else f'{nm} at {at}')
                          for nm, at in ((('Profile' if profile else 'FWHM'), 'z = 0') if a == 'x' else (('Profile' if profile else 'DOF'), 'x = 0')
                                         for a in cut)))
        nl = text.count('\n') + 1
        width = 0.62 * label_size / 72 * max(len(t) for t in text.split('\n'))
        return text, 1.2 * nl * label_size / 72 + 0.08, width

    def corners(sz):
        _, cap_h, cap_w = caption(sz)
        w = max(sz, cap_w) / (pos.width * W)                   # inset box + caption, in axes fractions
        h = (sz + cap_h) / (pos.height * H)
        m = 0.03
        return w, h, {'upper right': (1 - m - w, 1 - m - h), 'upper left': (m, 1 - m - h),
                      'lower right': (1 - m - w, m), 'lower left': (m, m)}

    def load(sz, c):
        w, h, cs = corners(sz)
        x0, y0 = cs[c]
        pad = 0.08
        return np.sum((xy[:, 0] > x0 - pad) & (xy[:, 0] < x0 + w + pad) & (xy[:, 1] > y0 - pad) & (xy[:, 1] < y0 + h + pad))

    if where == 'auto':
        # inside the axes only where no plotted point is near; otherwise outside the plots, never over a curve:
        # a single plot puts it at its right; in a figure of several plots a crowded panel passes its cut on, and the
        # rightmost panel draws one inset at the right of the figure, captioned with every cut passed on
        plots = [a for a in fig.axes if a.get_label() != '<inset>']
        rightmost = max(a.get_position().x1 for a in plots) - pos.x1 < 1e-6
        pending = getattr(fig, '_cut_pending', '')
        where = None
        if not (rightmost and pending):
            for sz in (size, 0.8 * size):
                c = min(corners(sz)[2], key=lambda k: load(sz, k))   # dict order: upper right wins a tie
                if load(sz, c) == 0:
                    size, where = sz, c
                    break
        if where is None:
            if len(plots) > 1 and not rightmost:
                fig._cut_pending = pending + ''.join(a for a in cut if a not in pending)
                return None
            cut = ''.join(dict.fromkeys(pending + cut))        # this panel's cut and those passed on
            fig._cut_pending = ''
            where = 'outside'
    if where == 'outside':
        ins = inset_axes(ax, width=size, height=size, loc='upper left', bbox_to_anchor=(1.04, 1 - (caption(size)[1] + 0.1) / (pos.height * H)),
                         bbox_transform=ax.transAxes, borderpad=0)
    else:
        ins = inset_axes(ax, width=size, height=size, loc=where, borderpad=0.9)
        if not where.startswith('lower'):                     # leave room above the frame for the caption
            ins.remove()
            fy = 1 - (caption(size)[1] + 0.1) / (pos.height * H)
            ins = inset_axes(ax, width=size, height=size, loc=where, borderpad=0.9,
                             bbox_to_anchor=(0, 0, 1, fy), bbox_transform=ax.transAxes)
    ins.set_label('<inset>')
    ins.set_xticks([]); ins.set_yticks([])
    for sp in ins.spines.values():
        sp.set_color('#999999'); sp.set_linewidth(1.2)
    if half is None:                                          # window: a few depths of focus at this NA
        perp = abs(np.sin(theta)) > 0.9                       # crossed beams: a compact spot
        half = float(np.clip((1.2 * (0.5 / na) if perp else 2.4 * (0.5 / na) ** 1.5) * n, 0.6, 8.0))
    for _ in range(4):                                        # grow the window until the half-maximum region fits
        f = _psf(sig, float(theta), float(na), float(n), float(eps), float(half))
        s = np.linspace(-half, half, f.shape[0])
        X, Z = np.meshgrid(s, s)
        on = f >= 0.5                                         # fit only the direction(s) measured
        reach = max(([np.abs(X[on]).max()] if 'x' in cut else []) + ([np.abs(Z[on]).max()] if 'z' in cut else []))
        fit = 0.62
        if reach <= fit * half:
            break
        half = float(np.ceil(reach / fit * 10) / 10)
    ins.set_facecolor('white')
    # the spot: filled contours of the computed PSF (light), its half-maximum contour in black
    ins.contourf(s, s, f, levels=[0.02, 0.25, 0.5, 0.75, 1.01], colors=['#e8eef7', '#c6d4ea', '#93acd6', '#5f83c2'])
    ins.contour(s, s, f, levels=[0.5], colors='k', linewidths=1.3)
    # orientation: x to the right, z down (as in the setup diagram)
    ar = dict(arrowstyle='-|>', color='#555555', lw=1.0, mutation_scale=9, shrinkA=0, shrinkB=0)
    o = (-0.9 * half, 0.42 * half)                               # bottom left
    ins.annotate('', xy=(o[0] + 0.32 * half, o[1]), xytext=o, arrowprops=ar)
    ins.annotate('', xy=(o[0], o[1] + 0.32 * half), xytext=o, arrowprops=ar)
    ins.text(o[0] + 0.36 * half, o[1], 'x', ha='left', va='center', fontsize=label_size, color='#555555')
    ins.text(o[0], o[1] + 0.36 * half, 'z', ha='center', va='top', fontsize=label_size, color='#555555')
    # the cut that is plotted, labelled with where it is taken
    i0 = f.shape[0] // 2
    for axis in cut:
        if axis == 'x':
            ins.plot([-half, half], [0, 0], color=CUT_LINE, lw=2.4)
        else:
            ins.plot([0, 0], [-half, half], color=CUT_LINE, lw=2.4)
    # caption: what is measured, and where (the inset's title, above the frame)
    side = 'left' if where.endswith('left') else 'right' if where.endswith('right') else 'center'
    ins.set_title(caption(size)[0], fontsize=label_size, color=CUT_LINE, fontweight='bold', pad=4, loc=side)
    # the width measured on the cut: a dimension line beside the spot, between the half-maximum crossings
    for axis in ('' if profile else cut):
        y = f[i0, :] if axis == 'x' else f[:, i0]
        if y[i0] < 0.5:
            continue
        r = i0 + np.argmax(y[i0:] < 0.5) if (y[i0:] < 0.5).any() else len(y) - 1
        l = i0 - np.argmax(y[i0::-1] < 0.5) if (y[i0::-1] < 0.5).any() else 0
        lo, hi = np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]]), np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]])
        inside = f >= 0.5                                       # how far the half-maximum region reaches beside the cut
        if axis == 'x':
            reach = s[np.any(inside[:, (s >= lo) & (s <= hi)], axis=1)].max()
            off = min(0.6 * half, reach + 0.12 * half)          # below the spot (z down)
            pts = ((lo, off), (hi, off)); ext = [((lo, 0), (lo, off)), ((hi, 0), (hi, off))]
        else:
            reach = s[np.any(inside[(s >= lo) & (s <= hi), :], axis=0)].max()
            off = min(0.85 * half, reach + 0.12 * half)         # right of the spot
            pts = ((off, lo), (off, hi)); ext = [((0, lo), (off, lo)), ((0, hi), (off, hi))]
        for (x0, y0), (x1, y1) in ext:
            ins.plot([x0, x1], [y0, y1], color='k', lw=0.8, ls=(0, (2, 2)))
        dim = dict(color='k', lw=1.4, mutation_scale=9, shrinkA=0, shrinkB=0)
        if hi - lo > 0.25 * half:
            ins.annotate('', xy=pts[1], xytext=pts[0], arrowprops=dict(arrowstyle='<|-|>', **dim))
        else:                                                   # narrow: arrows pointing in from outside
            d = 0.22 * half
            outer = (((lo - d, off), (hi + d, off)) if axis == 'x' else ((off, lo - d), (off, hi + d)))
            for q, p_ in zip(outer, pts):
                ins.annotate('', xy=p_, xytext=q, arrowprops=dict(arrowstyle='-|>', **dim))
    # scale bar
    bar = min((v for v in (0.1, 0.2, 0.5, 1, 2, 5) if v >= 0.35 * half), default=5)
    ins.plot([0.82 * half - bar, 0.82 * half], [0.9 * half, 0.9 * half], color='k', lw=2.4, solid_capstyle='butt')   # bottom right
    ins.text(0.82 * half - bar / 2, 0.84 * half, f'{bar:g} µm', ha='center', va='bottom', fontsize=label_size)
    ins.set_xlim(-half, half); ins.set_ylim(half, -half)
    return ins


def fig_legend(fig, handles, labels, **kw):
    """Legend of a multi-panel figure, placed so the plots keep the space.

    In order: inside one of the plots where it covers no plotted point and no inset; in the free column under an inset
    that sits outside at the right; in one row above the plots. Lays the figure out first (no tight_layout after it)."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            fig.tight_layout()
        except Exception:
            pass
    opts = dict(frameon=False, handlelength=1.6, handletextpad=0.4, labelspacing=0.25, borderaxespad=0.4, columnspacing=1.0)
    opts.update(kw)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    plots = [a for a in fig.axes if a.get_label() != '<inset>' and a.get_visible()]
    insets = [a for a in fig.axes if a.get_label() == '<inset>']
    occ = [a.get_tightbbox(r) for a in insets]

    def hits(bb, others):
        return any(bb.x0 < o.x1 and bb.x1 > o.x0 and bb.y0 < o.y1 and bb.y1 > o.y0 for o in others)

    for ax in plots:
        old = ax.get_legend()
        if old is not None:
            continue
        xy = _points(ax)
        for loc in ('upper right', 'upper left', 'center right', 'center left', 'lower right', 'lower left', 'upper center',
                    'lower center', 'center'):
            for nc in (1, 2):
                leg = ax.legend(handles, labels, loc=loc, ncol=nc, **opts)
                fig.canvas.draw()
                bb = leg.get_window_extent(r)
                b = bb.transformed(ax.transAxes.inverted())
                pad = 0.015
                inside = (b.x0 >= -0.001 and b.x1 <= 1.001 and b.y0 >= -0.001 and b.y1 <= 1.001)
                if inside and not hits(bb, occ) and not np.any((xy[:, 0] > b.x0 - pad) & (xy[:, 0] < b.x1 + pad)
                                                               & (xy[:, 1] > b.y0 - pad) & (xy[:, 1] < b.y1 + pad)):
                    return leg
                leg.remove()
    to_fig = fig.transFigure.inverted()
    right = max(a.get_position().x1 for a in plots)
    bottom = min(a.get_position().y0 for a in plots)
    for ins in insets:                                          # the free column under an inset outside at the right
        tb = ins.get_tightbbox(r)
        x0, y0 = to_fig.transform((tb.x0, tb.y0))
        if x0 < right:
            continue
        leg = fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(x0, y0 - 0.01), ncol=1, **opts)
        fig.canvas.draw()
        lb = leg.get_window_extent(r).transformed(fig.transFigure)
        lb = leg.get_window_extent(r)
        ly0 = to_fig.transform((lb.x0, lb.y0))[1]
        if ly0 >= bottom - 0.12:                               # ends near the bottom of the plots
            return leg
        leg.remove()
    top = max(a.get_tightbbox(r).y1 for a in plots)
    top = to_fig.transform((0, top))[1]
    leg = fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, top), ncol=len(handles), **opts)
    fig.canvas.draw()
    if leg.get_window_extent(r).width > fig.bbox.width * 1.05:  # too wide for one row: two rows
        leg.remove()
        leg = fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, top), ncol=-(-len(handles) // 2), **opts)
    return leg


def inset_figure(path, cut, size=2.2, **kw):
    """The cut inset on its own, saved to path, for a slide that places it beside the plot instead of inside it."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(size + 1.0, size + 1.6))
    ax = fig.add_axes([0, 0, 1, 1])
    cut_inset(ax, cut, size=size, where='lower left', **kw)
    ax.set_visible(False)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
