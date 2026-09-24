"""Drawing an atlas card: the two-dimensional map with its two profiles.

Kept separate from the script that computes the fields, so a change to how a
card looks can be applied by redrawing from the saved fields rather than by
recomputing them.
"""

from __future__ import annotations

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


LEVELS = [0.5, 1, 2, 4, 6, 10, 20, 40, 60, 80, 100]


def _crop(h, v, I, keep=0.97, pad=1.15):
    """Trim a card to the region holding `keep` of the field's energy.

    The saved field is deliberately wide so the dashboard can be zoomed out of;
    a card drawn on that extent is mostly empty. Cropping on a fraction of the
    peak is the wrong criterion here, because an Airy pattern decays slowly and
    its rings carry real energy far out. Cropping on cumulative energy bounds
    what is lost directly.
    """
    w = np.abs(h)[None, :]                      # focal-plane area element
    e_h = (I * w).sum(axis=0)
    e_v = (I * w).sum(axis=1)

    def _limit(x, e):
        order = np.argsort(np.abs(x))
        c = np.cumsum(e[order])
        if c[-1] <= 0:
            return np.abs(x).max()
        idx = np.searchsorted(c / c[-1], keep)
        return np.abs(x)[order][min(idx, len(x) - 1)] * pad

    hr = max(_limit(h, e_h), (h.max() - h.min()) * 0.04)
    vr = max(_limit(v, e_v), (v.max() - v.min()) * 0.04)
    hk = np.abs(h) <= hr
    vk = np.abs(v) <= vr
    if hk.sum() < 8 or vk.sum() < 8:
        return h, v, I
    return h[hk], v[vk], I[np.ix_(vk, hk)]


def render_card(h, v, I, title, outpath, base_tr=None, base_ax=None, airy_um=None,
                hlabel='Radial position r (μm)', vlabel='Axial position z (μm)',
                base_label='Uniform disk, continuous wave', curve_label=None):
    if base_tr is not None and len(base_tr) == I.shape[1]:
        _hk = np.isin(h, _crop(h, v, I)[0])
        base_tr = np.asarray(base_tr)[_hk]
    if base_ax is not None and len(base_ax) == I.shape[0]:
        _vk = np.isin(v, _crop(h, v, I)[1])
        base_ax = np.asarray(base_ax)[_vk]
    h, v, I = _crop(h, v, I)
    ih0 = np.argmin(np.abs(h))
    izpk = np.argmax(I[:, ih0])
    fig = plt.figure(figsize=(11.3, 6.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.55, wspace=0.75)
    axm = fig.add_subplot(gs[:, 0])
    axt = fig.add_subplot(gs[0, 1])
    axa = fig.add_subplot(gs[1, 1])
    fig.suptitle(title, fontsize=11)

    HH, VV = np.meshgrid(h, v)
    ext = [h[0], h[-1], v[0], v[-1]]
    im = axm.imshow(I, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                    norm=LogNorm(vmin=1e-3, vmax=1))       # heat map
    cb = fig.colorbar(im, ax=axm, fraction=0.040, pad=0.02, shrink=0.85)
    cb.set_label('Normalized intensity', fontsize=8)
    cb.ax.tick_params(labelsize=7)
    axm.contour(HH, VV, 100.0 * I / I.max(), levels=LEVELS,
                colors='w', linewidths=0.4, alpha=0.45)    # + contour lines
    from mcdo.figio import mark_focus
    mark_focus(axm, HH, VV, I / I.max(), airy_um=airy_um)
    axm.set_xlabel(hlabel); axm.set_ylabel(vlabel)
    axm.set_title('(a) Two-dimensional map with contours', fontsize=9)

    # the selected curve needs no legend entry unless something is
    # drawn beside it to distinguish it from
    axt.plot(h, I[izpk], 'k-', lw=2.0,
             label=curve_label if (curve_label and base_tr is not None) else None)
    if base_tr is not None:
        axt.plot(h, base_tr, 'k:', lw=2.0, label=base_label)
    axt.set_ylim(0, 1.05); axt.set_xlim(h[0], h[-1])
    axt.set_xlabel(hlabel); axt.set_ylabel('Normalized intensity')
    axt.set_title('(b) Transverse profile', fontsize=9)
    axt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)

    axa.plot(v, I[:, ih0], 'k-', lw=2.0)
    if base_ax is not None:
        axa.plot(v, base_ax, 'k:', lw=2.0)
    axa.set_ylim(0, 1.05); axa.set_xlim(v[0], v[-1])
    axa.set_xlabel(vlabel); axa.set_ylabel('Normalized intensity')
    axa.set_title('(c) Axial profile (r = 0)', fontsize=9)

    fig.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  saved", os.path.basename(outpath))
