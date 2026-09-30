r"""Two slides: the main result of the NA study, the 20% alignment tolerances
against NA with power-law fits, in the deck style (mcdo.deckstyle), and the next steps.

    python scripts/make_lim2002_main_result_slide.py
    -> ~/Downloads/lim2002_main_result.pptx (and a copy in Downloads/Research/two_color)
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mcdo.deckstyle as ds
from mcdo.deckstyle import FIG, bullets, figure, notes, prs, slide

OUT = os.path.expanduser('~/Downloads/lim2002_main_result.pptx')
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), at high NA'
ds.PAGE[0] = -1                                    # a single slide, numbered 1

import glob

import numpy as np


def saved(key):
    """NA and the 20% tolerances (scalar x, z; vector x, z) from the saved uniform-input sweep."""
    files = glob.glob(os.path.join(FIG, f'na_breakdown_{key}.csv')) + glob.glob(os.path.join(FIG, f'na_breakdown_{key}_*.csv'))
    a = np.concatenate([np.loadtxt(f, delimiter=',', ndmin=2) for f in files])
    return a[np.argsort(a[:, 0])]


def slope(na, v):
    return -np.polyfit(np.log(na), np.log(v), 1)[0]


pi, pi2 = saved('pi'), saved('pi2')
p_x, p_z = slope(pi[:, 0], pi[:, 3]), slope(pi[:, 0], pi[:, 4])
p2 = 0.5 * (slope(pi2[:, 0], pi2[:, 3]) + slope(pi2[:, 0], pi2[:, 4]))
at05 = pi[np.argmin(abs(pi[:, 0] - 0.5))]
err05 = 100 * (at05[2] / at05[4] - 1)                 # scalar over vector, axial tolerance at θ = π
na_lo, na_hi = pi[0, 0], pi[-1, 0]

s = slide('Main result: alignment tolerance against NA',
          'Tolerances fall as a power of NA; Lim & Saloma’s scalar model holds only up to NA ≈ 0.5.')
figure(s, os.path.join(FIG, 'na_breakdown_metrics.png'), 0.3, 1.3, 4.1, 3.95)
bullets(s, 4.6, 1.4, 4.95, 3.85, [
    'The tolerance is the offset of O′ that costs 20% of the two-color peak.',
    'Every tolerance shrinks steeply as NA grows, following a power law in NA.',
    f'At θ = π the tolerance across the axis falls as NA^{{−{p_x:.2f}}} and the one along the axis as NA^{{−{p_z:.2f}}} '
    f'(fits over NA {na_lo:g}–{na_hi:g}).',
    f'At θ = π/2 both tolerances fall as about NA^{{−{p2:.1f}}}.',
    'Lim & Saloma’s paraxial scalar model scales exactly as NA^{−1} and NA^{−2} and tracks the vector result up to NA 0.5.',
    f'Lim & Saloma state their model for NA ≤ 0.5; at that edge its length-set tolerances are {err05:.0f}% above the vector ones, and the gap grows beyond it.'], 11.5)
notes(s, 'Tolerances fall as a power of NA; Lim and Saloma’s scalar model holds only up to NA 0.5.',
      'Each panel shows the offset of beam 2’s focus that costs twenty percent of the two-color peak, against NA, for '
      'the facing and crossed geometries and for offsets across and along the axis. Blue is the vector focus, red Lim '
      'and Saloma’s paraxial scalar model within its stated range, and the black dashed line their quoted value at NA '
      '0.5. The fits are power laws, straight lines on these log–log axes. The scalar model scales exactly as one over '
      'NA and one over NA squared; the vector focus departs from that, so the scalar model gives larger values for the tolerances '
      'set by the focal length, by about seven percent already at NA 0.5.',
      r'x_c^{20\%},\ z_c^{20\%} = A\,\mathrm{NA}^{-p}')
s = slide('Next steps', 'Extending the NA study, then adding optical pulses.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'Gaussian input (α_t = 4): repeat the tolerance analysis against NA and compare it with uniform input.',
    'Wider NA range: down to NA 0.1, and θ = π/2 above NA 0.71, computed though two lenses cannot cross there in air.',
    'Two-dimensional tolerance maps over (x_c, z_c) at NA 0.5, 0.7 and 0.9.',
    'Optical pulses: fields resolved in time, and the two-color signal as a function of the delay between the pulses.',
    'Open question for pulses: how the broad spectrum enters, since the two colors interfere unless each pulse is '
    'longer than about 8 fs.'], 14)
notes(s, 'Extending the NA study, then adding optical pulses.',
      'Three extensions of the NA study, then pulses. The Gaussian input repeats the same tolerance analysis with a '
      'truncation parameter of 4. The NA range extends down to 0.1 and, for crossed beams, past the lens limit. The '
      'two-dimensional maps show the whole tolerance region. With pulses, the two-color signal becomes the overlap of '
      'the two pulses in time, which depends on the delay between them.',
      r'F_{2c}(\Delta t) = \kappa_{2c} \int I_1(P,t)\, I_2(P,t-\Delta t)\, dt')
prs.save(OUT)
shutil.copy(OUT, os.path.expanduser('~/Downloads/Research/two_color/'))
print('Saved ->', OUT)
