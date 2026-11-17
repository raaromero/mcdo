r"""Progress report on two-color excitation (2CE), one deck per section.

  00 overview     overall summary, next steps
  01 replication  scalar 2CE rebuilt from the paper (make_lim2002_replication_deck.py)
  02 vector       vector 2CE, uniform input, against NA
  03 fidelity     Linfoot's criteria F, C, Q against NA
  04 gaussian     vector 2CE, Gaussian input (α_t = 4): the results of 02 and 03
  05 delay        time delay between continuous beams, and against a misalignment in space
  06 polarization s–s and p–p linear polarization against unpolarized beams

Each deck stands on its own: title, summary (main point and two supporting
sentences), the geometry and field equations it uses, its results, and a glossary.
Figures come from fig_lim2002_slides.py, fig_lim2002_phase_delay.py and the
replication scripts; equations are displayed on the slides with LaTeX in the notes.

    python scripts/make_lim2002_progress_deck.py              # every section, each in its own process
    SECTION=vector python scripts/make_lim2002_progress_deck.py
    -> ~/Downloads/Research/two_color/2ce_<NN>_<section>.pptx
"""

import io
import os
import runpy
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DECK_APPEND'] = '1'

from PIL import Image

import mcdo.deckstyle as ds
from mcdo.deckstyle import (CARD, FIG, GREY, MSO_SHAPE, NAVY, ORIG, PALE, PAN, PURPLE, RED, WHITE, bullets, card, dots, equation,
                            figure, label, notes, prs, shape, slide, text, where)

SECTIONS = ['overview', 'replication', 'vector', 'fidelity', 'gaussian', 'delay', 'polarization', 'pulses']
MEETING = 'meeting'                                            # SECTION=meeting: highlights for one meeting, not in the full build
CMEETING = 'cmeeting'                                          # SECTION=cmeeting: meeting on Cambaliza & Saloma (2000)
SECTION = os.environ.get('SECTION')
DIR = os.path.expanduser(os.environ.get('DECK_DIR', '~/Downloads/Research/two_color'))
HERE = os.path.dirname(__file__)
SL = lambda name: os.path.join(FIG, 'slides', name)
PD = lambda name: os.path.join(FIG, 'phase_delay', name)
ds.CITE = ''

# what each slide is built from (figure sources, equations, panel labels), for the slide manifest the dashboard reads
_REC = {}
_figure0, _equation0, _where0, _label0 = figure, equation, where, label


def _rec(s):
    return _REC.setdefault(s.slide_id, {'figs': [], 'eqs': [], 'labels': []})


def figure(s, path, *a, **k):
    _rec(s)['figs'].append(os.path.abspath(path))
    return _figure0(s, path, *a, **k)


def equation(s, l, t, w, tex, *a, **k):
    _rec(s)['eqs'].append({'tex': tex, 'where': ''})
    return _equation0(s, l, t, w, tex, *a, **k)


def where(s, l, t, w, txt, *a, **k):
    if _rec(s)['eqs']:
        _rec(s)['eqs'][-1]['where'] = txt
    return _where0(s, l, t, w, txt, *a, **k)


def label(s, l, t, w, txt, *a, **k):
    _rec(s)['labels'].append(txt)
    return _label0(s, l, t, w, txt, *a, **k)

if SECTION is None:                                            # build each section in a fresh process
    for sec in SECTIONS:
        r = subprocess.run([sys.executable, __file__], env={**os.environ, 'SECTION': sec}, capture_output=True, text=True)
        print(r.stdout.strip() if r.returncode == 0 else f'{sec} FAILED:\n{r.stderr[-3000:]}')
    sys.exit()


# ══ helpers ══════════════════════════════════════════════════════════════
def navy(title, lines):
    s = prs.slides.add_slide(ds.BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    dots(s, 0.6, 0.7, 0.2, 0.27)
    text(s, 0.6, 1.15, 8.8, 1.5, title, 30, WHITE, True, 'Helvetica Neue')
    for i, (line, size, col) in enumerate(lines):
        text(s, 0.6, 2.85 + i * 0.4, 8.8, 0.4, line, size, col)
    return s


def title(name, what):
    s = navy(name, [('Roland Albert A. Romero', 18, WHITE),
                    ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
                    (what, 13, PALE)])
    notes(s, name + '.', what)


def summary(main, *rest):
    """Main point in bold, its supporting points beneath; the last item is the speaker script."""
    *support, script = rest
    s = slide('Summary', '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, [main] + ['– ' + x for x in support], 14 if len(support) <= 2 else 13, bold=True)
    notes(s, main, script)


def words(name, items, main, script, latex=None, size=13):
    s = slide(name, '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, items, size)
    notes(s, main, script, latex)


def wide(name, path, items, main, script, latex=None):
    s = slide(name, '')
    if SECTION in ('cambaliza', CMEETING):                     # figure as tall as the bullets beneath allow
        import re as _re
        nl = sum(-(-len(_re.sub(r'[_^]\{([^}]*)\}', r'\1', t_)) // 105) for t_ in items)   # wrapped lines at 13 pt
        h = 4.12 - 0.25 * (nl - 1) - 0.05 * (len(items) - 1)
        figure(s, path, 0.45, 0.92, 9.1, h)
        bullets(s, 0.6, 0.98 + h, 8.6, 0.25 * nl + 0.05 * len(items), items, 13)
    else:
        figure(s, path, 0.45, 0.95, 9.1, 3.72)
        bullets(s, 0.6, 4.72, 8.9, 0.55, items, 11.5)
    notes(s, main, script, latex)


def side(name, path, items, main, script, latex=None, fw=5.3):
    s = slide(name, '')
    figure(s, path, 0.45, 0.95, fw, 4.25)
    bullets(s, 0.45 + fw + 0.25, 1.05, 9.5 - fw - 0.7, 4.15, items, 12)
    notes(s, main, script, latex)


CB = os.path.join(FIG, '..', 'cambaliza2000')                 # Cambaliza & Saloma (2000) figures


def trimmed(path, pad=6):
    """Copy of a scanned panel without its white margin (in the system temp folder), so it fills its slot."""
    import tempfile
    out = os.path.join(tempfile.gettempdir(), 'cpanel_trim', os.path.basename(path))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im = Image.open(path).convert('RGB')
    box = Image.eval(im.convert('L'), lambda v: 255 if v < 235 else 0).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(out)
    return out


def side(title, path, items, main, script, size=14):
    """Figure at the left, as large as the slide allows; bullets at the right."""
    s = slide(title, '')
    figure(s, path, 0.3, 0.95, 5.9, 4.45)
    bullets(s, 6.35, 1.1, 3.35, 4.2, items, size)
    notes(s, main, script)


def cpanel(title, key, ours, line, script=None):
    """Original panel of Cambaliza & Saloma (2000) beside current work, one line (or one per curve) beneath."""
    lines = [line] if isinstance(line, str) else list(line)
    import re as _re
    vis = lambda t_: len(_re.sub(r'[_^]\{([^}]*)\}', r'\1', t_))      # characters shown, markup removed
    nl = sum(-(-vis(t_) // 100) for t_ in lines)                    # wrapped lines at 13 pt beside the inset
    hmax = 3.9 - 0.24 * (nl - 1)
    s = slide(title, '')
    left, right = trimmed(os.path.join(CB, 'original', f'{key}.png')), os.path.join(CB, 'panels', ours)
    a1, a2 = (Image.open(p).size[0] / Image.open(p).size[1] for p in (left, right))
    if os.path.exists(os.path.join(CB, 'panels', 'inset_' + ours)):
        hmax = min(hmax, 5.25 - 1.22 - 1.2)                    # leave 1.2 in under the panels for the cut inset
    h = min(hmax, (9.5 - 0.15 - 0.2) / (a1 + a2) + 0.1)        # same height for both, as large as the width allows
    w1, w2 = a1 * (h - 0.1) + 0.1, a2 * (h - 0.1) + 0.1
    x1 = (10 - (w1 + w2 + 0.15)) / 2
    label(s, x1, 0.9, w1, 'Cambaliza & Saloma (2000)' + (f', Fig. {key[3:]}' if key.startswith('fig') else ''))   # figure number here, not in the title
    label(s, x1 + w1 + 0.15, 0.9, w2, 'Current work', PURPLE)
    figure(s, left, x1, 1.15, w1, h)
    figure(s, right, x1 + w1 + 0.15, 1.15, w2, h)
    ins = os.path.join(CB, 'panels', 'inset_' + ours)        # where the profile is cut: beside the bullets, not in the plot
    bw = 8.6
    if os.path.exists(ins):
        ih = min(5.25 - (1.22 + h), 1.35)
        iw = ih * Image.open(ins).size[0] / Image.open(ins).size[1]
        figure(s, ins, x1 + w1 + 0.15 + w2 - iw, 1.22 + h, iw, ih)
        bw = x1 + w1 + 0.15 + w2 - iw - 0.75
    bullets(s, 0.6, 1.2 + h, bw, 0.24 * nl + 0.1, lines, 14 if nl == 1 else 13)
    notes(s, title, script or ' '.join(lines))


def coverlay(keys, ttl, line):
    """Four panels of current work drawn over the original figures."""
    s = slide(ttl, '')
    for q, k in enumerate(keys):
        figure(s, os.path.join(CB, 'overlay', f'{k}.png'), 0.45 + (q % 2) * 4.6, 0.95 + (q // 2) * 2.0, 4.45, 1.95)
    bullets(s, 0.6, 4.98, 8.6, 0.4, [line], 14)
    notes(s, ttl, line)


def cmodel(fig=None):
    U1 = r'U(P;\theta) = -j\,\frac{\pi\,\mathrm{NA}^2 A\, e^{\,j (2f/D)^2 u}}{\lambda}\,\left[C(v_r, w_r, u_r) - jS(v_r, w_r, u_r)\right]'
    U2 = r'u_r = u\cos\theta - v\sin\theta, \quad v_r = v\cos\theta + u\sin\theta, \quad u = \frac{2\pi\mathrm{NA}^2}{\lambda}z, \quad v = \frac{2\pi\mathrm{NA}}{\lambda}x'
    U3 = r'F_{2c} = \kappa\,|U_1|^2|U_2|^2, \qquad F_{2p} = \kappa\,'"'"r'|U_1 + U_2|^4, \qquad U_a = U_R - U_{\varepsilon R}'
    eqslide('Paraxial scalar model: Eqs. 1–6', 'Beam 2 is rotated in real space; Eq. 1 writes the rotation in (u, v).', [
        (U1, 'Eq. 1: C, S = Lommel functions; f = focal length, D = pupil diameter; NA 0.5.'),
        (U2, 'rotated coordinates of beam 2 (Eq. 1); θ = angle between the lens axes.'),
        (U3, 'Eqs. 2–6: 2CE (750 + 656 nm), 2PE (700 nm); annular ε = 0.99.')],
        'Paraxial scalar model, Eqs. 1-6.', 'Equations 1 to 6.', '\n'.join((U1, U2, U3)), fig=fig, size=14)


def chigh_na(part='High NA', water_x=False, summary=None):
    """Part on high NA of the Cambaliza decks: scalar against vector widths, air and water, and the paper's comparisons."""
    hn = os.path.join(CB, 'high_na')
    navy(part, [])
    if summary:
        words(*summary, size=16)
    if SECTION == CMEETING:                                    # one configuration per slide: medium and θ
        WHY_0 = 'Why: the paraxial phase uses sin²α/2 for 1 − cos α, which lengthens the focus by tan²(α/2).'
        WHY_P2 = 'Why: each beam is cut by the other beam’s narrow spot, which the paraxial model reproduces.'
        WHY_PI = 'Why: the 2PE width along the axis is the interference fringe, set by the wavelength, not by the focus.'
        WHY_0 = 'Why: the paraxial phase uses sin²α/2 for 1 − cos α, which lengthens the focus by tan²(α/2).'
        for key, ttl, items in (
                ('2ce_0', '2CE, θ = 0 and π', [
                    'As NA increases both widths shrink, but the paraxial depth of focus shrinks more slowly than the vector one and becomes too long.',
                    'The paraxial DOF of F_{2c}(0, 0, z; 0) is 5% longer from NA 0.43 in air (0.57 in water), below the NA 0.7 stated on p. 27; '
                    'the central spot stays within 5% up to NA 0.86.',
                    'Eq. (1) uses sin²α/2 for 1 − cos α, which lengthens the DOF by the factor 1 + tan²(α/2).']),
                ('2ce_pi2', '2CE, θ = π/2', [
                    'As NA increases both widths of F_{2c} at θ = π/2 shrink, and the paraxial model follows the vector focus within 4% '
                    'wherever crossed lenses fit (NA 0.71 in air, 0.94 in water).',
                    'Each width is set by the narrow transverse spot of the other beam, which Eq. (1) reproduces.']),
                ('2pe_0', '2PE, θ = 0', [
                    'F_{2p} at θ = 0 is identical with F_{2c} at θ = 0, so it changes with NA in the same way: the paraxial DOF is 5% '
                    'longer from NA 0.43 in air.']),
                ('2pe_pi2', '2PE, θ = π/2', [
                    'As NA increases the central spot of F_{2p} at θ = π/2 keeps its width, 0.26 µm in air and 0.19 µm in water, '
                    'in both models (within 0.4%).',
                    'The spot is one interference fringe of the two crossed beams, so its width is set by the wavelength in the medium, λ_{2p}/n (n = 1 air, 1.33 water), not by the NA.',
                    'It stays the sharpest distribution at every NA, as at NA 0.5 (p. 28).']),
                ('2pe_pi', '2PE, θ = π', [
                    'Across the axis, F_{2p}(x, 0, 0; π) is identical with F_{2p}(x, 0, 0; 0).',
                    'As NA increases fewer fringes fit inside the focus, about 9 at NA 0.5 and 2 at NA 0.9 in air: the focus '
                    'shortens as 1/NA², while the fringes stay about λ/2n apart, half the wavelength in the medium (0.37 µm at NA 0.5, 0.44 µm at NA 0.9; λ/2n = 0.35 µm in air).',
                    'The fringes spread slightly with NA because the converging waves cross the axis at an angle; the central '
                    'fringe widens from 0.13 to 0.17 µm, and paraxial and vector agree within 5% up to NA 0.91 in air.'])):
            wide(f'Central spot and depth of focus against NA: {ttl}', os.path.join(hn, f'cfg_{key}.png'), items,
                 f'Scalar against vector widths, {ttl}.',
                 'Solid: vector (Richards-Wolf), beams along y; dashed: paraxial scalar. Blue: air; green: water. '
                 'Linear axes. Gap numbers from high_na/split.txt.' + (
                 ' Facing lenses: the two beams form a standing wave with peaks about lambda/2n apart (n = refractive '
                 'index; lambda/2n = 0.35 um in air, 0.26 um in water): 0.37 um at NA 0.5 and 0.44 um at NA 0.9 in air. The '
                 'spacing grows a little with NA because the converging waves cross the axis at an angle. Fringes inside '
                 'the focus (its length over the spacing): air about 9 at NA 0.5, 4 at 0.7, 2 at 0.9; water about 17 at '
                 'NA 0.5, 4 at 0.9, 2 at 1.2. The focus shortens as 1/NA^2 while the spacing stays near lambda/2n.'
                 if key == '2pe_pi' else ''))
        wide('Paraxial over vector widths of 2CE against NA', os.path.join(hn, 'gap_2ce.png'), [
            'As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis.',
            'Along the axis at θ = 0 and π the difference reaches 5% at NA 0.43 in air (0.57 in water); across the axis at NA 0.86 '
            '(1.14); with crossed lenses it stays within 4%.'],
            'Where the paraxial 2CE widths depart from the vector ones.',
            'Gap = scalar / vector - 1. Diamonds: NA where the gap reaches 5% (interpolated).')
        wide('Paraxial over vector widths of 2PE against NA', os.path.join(hn, 'gap_2pe.png'), [
            'As NA increases the paraxial 2PE widths at θ = 0 depart as the 2CE ones; with crossed lenses they stay within 0.4%.',
            'At θ = π the paraxial central fringe becomes narrower than the vector one, by 5% at NA 0.91 in air (1.21 in water).'],
            'Where the paraxial 2PE widths depart from the vector ones.',
            'Gap = scalar / vector - 1. 2PE across the axis at theta = pi equals theta = 0 and is not drawn twice.')
        LF1 = r'\sum_k a_k\,\Delta s = \sum_k r_k\,\Delta s = 1'
        LF2 = r'\mathrm{NRMSE} = \sqrt{\frac{\sum_k (a_k - r_k)^2}{\sum_k r_k^2}}'
        LF3 = (r'F = 1 - \frac{\sum_k (a_k - r_k)^2}{\sum_k r_k^2}, \qquad C = \frac{\sum_k a_k^2}{\sum_k r_k^2}, \qquad '
               r'Q = \frac{\sum_k a_k\, r_k}{\sum_k r_k^2}')
        LF4 = r'F = 2Q - C, \qquad \mathrm{NRMSE} = \sqrt{1 - F}'
        eqslide('Whole-profile measures: NRMSE and Linfoot’s F, C, Q', 'Both profiles are scaled to the same energy, so the '
                'comparison counts the side lobes and the tails, not only the width.', [
            (LF1, 'Both profiles scaled to the same energy, so side lobes and tails count, not only the width.'),
            (LF2, 'NRMSE: the root-mean-square difference of the two profiles; 0 when they are identical.'),
            (LF3, 'Fidelity F, structural content C, correlation quality Q: 1 for identical profiles; C < 1 for a flatter, longer focus.'),
            (LF4, 'F, C and Q are linked; NRMSE carries the same information as F.')],
            'Whole-profile measures and their equations.',
            'Linfoot (1956) criteria with the vector profile as reference. Unit energy over the window: a profile that is '
            'longer but lower is not counted as better. The dashboard shows these on the profile (How it is measured).',
            '\n'.join((LF1, LF2, LF3, LF4)), size=15)
        wide('Whole-profile difference of 2CE, paraxial against vector', os.path.join(hn, 'nrmse_2ce.png'), [
            'As NA increases the paraxial F_{2c} departs from the vector one along the axis much more than across it.',
            'Along the axis at θ = 0 and π: 6% at NA 0.5 and 25% at NA 0.9 in air; across the axis 1% and 5%; with crossed lenses 3% or less.'],
            'Whole profiles: the same picture as the widths.',
            'r = vector profile, a = scalar profile, both normalized to unit area over the plotted window (x +-1 um x 0.5/NA, '
            'z +-5 um x n (0.5/NA)^2), 401 points. NRMSE = sqrt(1 - F), F = Linfoot fidelity.')
        wide('Whole-profile difference of 2PE, paraxial against vector', os.path.join(hn, 'nrmse_2pe.png'), [
            'As NA increases the paraxial F_{2p} departs as F_{2c} at θ = 0; along the axis at θ = π by 7% at NA 0.5 and 29% at NA 0.9 in air.',
            'With crossed lenses it differs by 5% or less: the fringes are set by the wavelength in both models.'],
            'Whole 2PE profiles, scalar against vector.',
            'Same normalization as the 2CE slide. 2PE across the axis at theta = pi equals theta = 0.')
        # Linfoot's criteria against NA: a section of its own, one slide per signal and angle (as the width slides)
        LD = os.path.join(hn, 'linfoot')
        navy('Linfoot’s criteria against NA: paraxial scalar against vector, air and water', [])
        words('Summary: Linfoot’s criteria', [
            'As NA increases the paraxial profiles keep their shape across the axis: F ≥ 0.996 for both signals and all θ.',
            'Along the axis with facing lenses they become longer and lower than the vector ones: C < 0.95 from NA 0.44 in air '
            '(0.58 in water), where the DOF departs by 5%.',
            'With crossed lenses (θ = π/2), F ≥ 0.997 and C ≥ 0.9 wherever the lenses fit.',
            'F falls below 0.99 from NA 0.6 in air; C responds first, because the paraxial focus is longer and lower.'],
            'Linfoot’s criteria: main points.',
            'F = 1 - sum (a-r)^2 / sum r^2, C = sum a^2 / sum r^2, Q = sum a r / sum r^2, with r = vector, a = scalar, each '
            'normalized to unit energy over the window (circular pupils, uniform input). All cases, also annular and Gaussian: '
            'output/08_two_color/cambaliza2000/high_na/linfoot/linfoot_<signal>_<pupil>_<input>.png and the dashboard.', size=16)
        wide('Linfoot’s criteria against NA: 2CE, θ = 0 and π', os.path.join(LD, 'linfoot_na_2ce_0.png'), [
            'As NA increases the paraxial F_{2c}(0, 0, z; π) becomes longer and lower than the vector one, so C falls first: '
            'below 0.95 from NA 0.44 in air (0.58 in water).',
            'F stays above 0.99 up to NA 0.63 (0.84 in water); across the axis F ≥ 0.996 at all NA.'],
            'F changes least; C and Q show the split first, along the axis.',
            'Why C falls first: with unit energy, the longer scalar focus has a lower peak, so sum a^2 drops below sum r^2.')
        wide('Linfoot’s criteria against NA: 2CE, θ = π/2', os.path.join(LD, 'linfoot_na_2ce_pi2.png'), [
            'As NA increases the paraxial and vector F_{2c} at θ = π/2 stay alike: F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 wherever '
            'crossed lenses fit (NA 0.71 in air, 0.94 in water).',
            'With crossed lenses, Eq. (1) gives the profiles of the vector focus.'],
            'Crossed lenses: scalar and vector profiles agree.', 'Same normalization; crossed lenses fit up to NA = n sin 45 degrees.')
        wide('Linfoot’s criteria against NA: 2PE, θ = 0', os.path.join(LD, 'linfoot_na_2pe_0.png'), [
            'As NA increases F_{2p} at θ = 0 departs as F_{2c} at θ = 0: along the axis C < 0.95 from NA 0.44 in air and F < 0.99 from NA 0.63.',
            'Across the axis F ≥ 0.996 at all NA.'],
            '2PE at theta = 0: as 2CE.', 'Same normalization.')
        wide('Linfoot’s criteria against NA: 2PE, θ = π/2', os.path.join(LD, 'linfoot_na_2pe_pi2.png'), [
            'As NA increases the paraxial F_{2p} at θ = π/2 keeps F ≥ 0.997 wherever the lenses fit.',
            'Along the axis C falls to 0.91; across the axis F, C and Q stay above 0.97.'],
            '2PE with crossed lenses: close agreement.', 'Same normalization.')
        wide('Linfoot’s criteria against NA: 2PE, θ = π', os.path.join(LD, 'linfoot_na_2pe_pi.png'), [
            'As NA increases the paraxial envelope of the F_{2p}(0, 0, z; π) fringes becomes too long: C < 0.95 from NA 0.44 in air '
            '(0.58 in water), F < 0.99 from NA 0.58 (0.78).',
            'At NA 0.95 in air F = 0.85, the lowest of all cases.'],
            '2PE with facing lenses: the envelope sets the difference.', 'Same normalization.')
        wide('Side lobes of 2PE against NA: distance from the peak and height', os.path.join(hn, 'sidelobes.png'), [
            'As NA increases the 2PE side lobes weaken: at θ = π/2 from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7 (air); '
            'at θ = π from 0.97 to 0.42 at NA 0.9.',
            'Their distance from the peak follows the wavelength in the medium (n = 1 air, 1.33 water): λ/2n with facing lenses (the standing-wave fringe) and λ/n '
            'with crossed lenses, at low NA.',
            'Weaker side lobes give images of higher contrast, so the drawback of 2PE reported at NA 0.5 (pp. 28–29) shrinks at high NA.'],
            'The 2PE side lobes follow the wavelength: lambda/2n facing, lambda/n crossed.',
            'At theta = pi/2 the side lobe rides on the narrow spot of the other beam, which narrows with NA, so it moves in '
            'and drops. First local maximum beyond the first minimum, vector (solid) and scalar (dashed); lambda = 0.7 um. At theta = pi '
            'the vector side lobe is lower than the scalar one at high NA (0.42 against 0.65 at NA 0.9 in air), because the '
            'vector focus, which sets the fringe envelope, is shorter. 2CE side lobes stay below 1e-3 of the peak.')
    else:
        wide('Widths across the axis against NA, air', os.path.join(hn, 'widths_air_x.png'), [
            'Across the axis the paraxial widths agree with the vector ones within 6% up to NA 0.9.'],
            'The paraxial model holds across the axis.',
            'Solid vector, dashed paraxial scalar; both beams polarized along y. Scalar wider by up to 1.4% at NA 0.5, 3.4% at '
            '0.7, 5.9% at 0.9. theta = 0 and pi coincide; theta = pi/2 to NA 0.71 (lenses fit at 90 degrees).')
        wide('Depth of focus against NA, air', os.path.join(hn, 'widths_air_z.png'), [
            'The paraxial depth of focus is too long at high NA: by 36% at NA 0.9.'],
            'Along the axis the paraxial model gives too long a focus at high NA.',
            'Scalar DOF longer by 7% at NA 0.5, 16% at 0.7, 36% at 0.9: the factor tan^2(alpha/2) from the small-angle phase. '
            '2PE at theta = pi/2 and pi: the width of the central interference fringe, set by the wavelength.')
        if water_x:
            wide('Widths across the axis against NA, water', os.path.join(hn, 'widths_water_x.png'), [
                'In water the paraxial widths across the axis agree within 3% up to NA 0.9.'],
                'The paraxial model holds across the axis in water.',
                'Scalar wider by up to 0.7% at NA 0.5, 1.6% at 0.7, 3.1% at 0.9, 7.2% at 1.25. theta = pi/2 to NA 0.94.')
        wide('Depth of focus against NA, water', os.path.join(hn, 'widths_water_z.png'), [
            'In water the paraxial error at the same NA is about half that in air: 15% at NA 0.9.'],
            'In water the paraxial model holds to a higher NA.',
            'Scalar DOF longer by 4% at NA 0.5, 8% at 0.7, 15% at 0.9, 44% at 1.25 (tan^2(alpha/2) with sin(alpha) = NA/1.33). '
            'theta = pi/2 to NA 0.94 (lenses fit at 90 degrees).')
    if SECTION != CMEETING:
     wide('Scalar over vector width against NA, θ = 0 and π', os.path.join(hn, 'split_0pi.png'), [
        'Across the axis the scalar width is 5% larger at NA 0.86 in air and 1.14 in water.',
        'Along the axis the paraxial depth of focus is 5% longer at NA 0.43 in air and 0.57 in water.'],
        'The paraxial model departs first along the axis.',
        'Gap = scalar / vector - 1. Diamonds: NA where the gap reaches 5% (interpolated). theta = 0 and pi give the same '
        'widths except 2PE along the axis, where facing lenses give fringes; the 2PE fringe at pi reaches -5% at NA 0.91 '
        '(air) and 1.21 (water). 2PE and 2CE gaps coincide at theta = 0.')
    if SECTION != CMEETING:
     wide('Scalar over vector width against NA, θ = π/2', os.path.join(hn, 'split_pi2.png'), [
        'At θ = π/2 the two agree within 4% up to NA 0.7 in air and 0.9 in water, where the lenses fit.'],
        'At theta = pi/2 the two models do not split.',
        'Crossed lenses fit up to a half-angle of 45 degrees: NA 0.71 in air, 0.94 in water. Largest gap: 2CE across the '
        'axis, 3.4% (air, NA 0.7) and 3.1% (water, NA 0.9).')
    wide('2PE and 2CE central spots against NA, circular pupils', os.path.join(hn, 'ratios_x.png'), [
        'As NA increases the 2CE spot at θ = π/2 shrinks while the 2PE spot keeps its width: 2.9 times the 2PE spot at NA 0.5, 2.0 at NA 0.7 in air.',
        'Relative to θ = 0, the 2PE spot at θ = π/2 is 0.50 times as wide at NA 0.5 and 0.71 at NA 0.7.',
        '2PE at θ = π/2 stays the sharpest distribution at every NA, as on p. 28; scalar and vector agree within 4%.'],
        'The 2CE-2PE comparisons hold at high NA; their size depends on NA.',
        'Within 4% to NA 0.7 (air) and 0.9 (water). 2CE over 2PE at theta = pi/2: 2.9x at NA 0.5, 2.0x at NA 0.7 in air. '
        '2PE crossed over facing: 0.50 at NA 0.5, 0.71 at NA 0.7 in air.')
    wide('2CE and 2PE depth of focus against NA, θ = π/2', os.path.join(hn, 'ratios_z.png'), [
        'As NA increases the 2CE DOF shortens while the 2PE DOF stays one fringe: 2.6 times the 2PE DOF at NA 0.5, 1.8 at NA 0.7 in air.',
        'The “broader DOF” of 2CE at θ = π/2 (p. 30) remains at high NA, but the difference shrinks.'],
        'The DOF comparison holds at high NA.',
        'DOF of 2CE over 2PE at theta = pi/2: 2.6 at NA 0.5, 1.8 at NA 0.7 in air; 3.5 at 0.5, 1.9 at 0.9 in water. '
        'Scalar and vector within 4%. The 2PE width is that of the central fringe, which does not change with NA, '
        'so the ratio falls as the 2CE focus shortens.')


def green(marks):
    """Lines that show current work is correct, in green: {slide title: (phrases)}."""
    for sl in prs.slides:
        frames = [sh.text_frame for sh in sl.shapes if sh.has_text_frame]
        key = next((f.text for f in frames if f.text in marks), None)
        if key is None:
            continue
        for f in frames:
            for para in f.paragraphs:
                if any(k in para.text for k in marks[key]):
                    for r_ in para.runs:
                        r_.font.color.rgb = GREEN


GREEN = ds.RGBColor.from_string('1E8449')


def red(diff):
    """Slides where current work and the paper differ: the title and the difference in red."""
    for sl in prs.slides:
        frames = [sh.text_frame for sh in sl.shapes if sh.has_text_frame]
        if not any(f.text in diff for f in frames):
            continue
        key = next(f.text for f in frames if f.text in diff)
        for f in frames:
            for para in f.paragraphs:
                if para.text == key or any(k in para.text for k in diff[key]):
                    for r in para.runs:
                        r.font.color.rgb = RED


GLOSS = {   # term: (meaning, sections that use it)
    'NA': ('numerical aperture, n sin α; α is the half-angle of the focusing cone', 'all'),
    'n': ('refractive index of the medium, 1 for air and 1.33 for water', 'all'),
    'L1, L2; O, O′': ('the two lenses and their foci; O is the origin', 'all'),
    'x_c, z_c': ('misalignment of O′ across and along the axis of L1', 'all'),
    'θ': ('angle between the two lens axes (π facing, π/2 crossed)', 'all'),
    'λ_1, λ_2, λ_{2p}': ('2CE wavelengths 750 and 656 nm; 2PE wavelength 700 nm', 'all'),
    '2CE, 2PE': ('two-color excitation, signal ∝ I_1 I_2; two-photon excitation, signal ∝ |U_1 + U_2|^4', 'all'),
    'PSF': ('point spread function: the fluorescence from one point, scaled to its peak', 'all'),
    'Scalar 2CE': ('the paraxial scalar model (small-angle phase, no polarization)', 'all'),
    'Vector 2CE': ('the same signals with the Richards–Wolf focus (exact phase and polarization)', 'overview vector fidelity gaussian polarization pulses cmeeting'),
    'Scalar Debye': ('scalar focus with the exact phase, no polarization', 'vector'),
    'Peak lost': ('drop of the peak of the misaligned PSF, in percent of the aligned peak', 'overview replication vector gaussian delay polarization'),
    '20% tolerance': ('the misalignment x_c or z_c that reduces the 2CE peak by 20%', 'overview vector gaussian polarization'),
    '20% tolerance in time': ('the time delay Δt that reduces the 2CE peak by 20%', 'pulses'),
    'F, C, Q': ('Linfoot’s criteria: fidelity, structural content and correlation quality', 'overview replication fidelity gaussian delay pulses'),
    'α_t': ('truncation parameter of the Gaussian input; 0 is uniform input', 'overview gaussian'),
    'Unpolarized': ('averaged over two perpendicular input polarizations, equal to circular', 'overview vector fidelity gaussian polarization pulses'),
    's–s, p–p': ('both beams polarized perpendicular to (s) or in (p) the plane of the two lens axes', 'polarization'),
    'Δt, φ': ('time delay of beam 2; the phase it adds, φ = ωΔt', 'overview delay pulses'),
    'τ': ('pulse duration: full width at half maximum of the intensity', 'pulses cambaliza cmeeting'),
    'FWHM, DOF': ('full width at half maximum; depth of focus, the FWHM along the axis', 'cambaliza cmeeting'),
    'L1, L2': ('the two focusing lenses; L1 carries λ_1 along z, L2 carries λ_2 and is turned by θ', 'cmeeting'),
    'U_1, U_2; I_1, I_2': ('focused fields of lenses L1 and L2; their intensities |U|^2', 'cmeeting'),
    'Excitation (2PE)': ('|U_1 + U_2|^2, the focused intensity; the 2PE signal is its square (Eq. 6)', 'cmeeting'),
    'ε': ('obstruction ratio of the annular pupil: inner over outer radius, 0.99 here', 'cmeeting'),
    'Δλ': ('gap λ_1 − λ_2 between the 2CE wavelengths, with 1/λ_1 + 1/λ_2 = 1/350 nm fixed', 'cmeeting'),
    'Transform-limited pulse': ('the shortest pulse for its spectrum, with no chirp', 'cmeeting'),
    'h, d_s, g': ('slab half-thickness; mean free path between scattering events; anisotropy ⟨cos⟩ of one scattering', 'cambaliza cmeeting'),
    'ν_a, ν_b, ν_e': ('photon frequencies from the 750 and 656 nm lasers, and of the transition (ν = c/λ)', 'pulses'),
    'p_i(ν)': ('spectral probability density of a photon of laser i', 'pulses'),
    'P(ν_a), δ': ('joint probability of a resonant pair; detuning ν_e − (ν_1 + ν_2) of the transition', 'pulses'),
    'A(P)': ('two-photon amplitude: the sum of the resonant pairs; the 2CE signal is |A|²', 'pulses'),
    'O(P, Δt), t_1, t_2': ('overlap in time of the two pulses; times at which they pass P (t_2 includes Δt)', 'pulses'),
    'N': ('number of wavelengths sampled per pulse', 'pulses'),
    'K': ('fringe wavevector of the two 2PE beams, |K| = 2k sin(θ/2)', 'delay'),
}


GLOSS_TEX = [   # meeting deck on Cambaliza & Saloma (2000): (LaTeX symbol, meaning)
    (r'\mathrm{NA} = n\sin\alpha', 'numerical aperture; α is the half-angle of the focusing cone'),
    (r'n', 'refractive index of the medium: 1 for air, 1.33 for water'),
    (r'\theta', 'angle between the axes of the two lenses: 0 collinear, π/2 crossed, π facing'),
    (r'L_1,\ L_2', 'the two focusing lenses; L₂ is turned by θ about the common focus'),
    (r'\lambda_1,\ \lambda_2,\ \lambda_{2p}', '2CE wavelengths, 750 nm on L₁ and 656 nm on L₂; 2PE wavelength, 700 nm'),
    (r'\Delta\lambda = \lambda_1 - \lambda_2', 'gap between the 2CE wavelengths, with 1/λ₁ + 1/λ₂ = 1/λₑ fixed, λₑ = 350 nm'),
    (r'U_1,\ U_2;\quad I = |U|^2', 'focused fields of L₁ and L₂, and their intensities'),
    (r'F_{2c} = \kappa\, I_1 I_2', 'two-color excitation (2CE) fluorescence'),
    (r"F_{2p} = \kappa'\, |U_1 + U_2|^4", 'two-photon excitation (2PE) fluorescence; |U₁ + U₂|² is the excitation'),
    (r'\varepsilon', 'obstruction ratio of the annular pupil, inner over outer radius: 0.99'),
    (r'\mathrm{FWHM},\ \mathrm{DOF}', 'full width at half maximum of the central peak; depth of focus, the FWHM along the axis'),
    (r'\mathrm{scalar},\ \mathrm{vector}', 'paraxial scalar model (Eqs. 1–6); Richards–Wolf focus, with exact phase and polarization'),
    (r'\theta_{\mathrm{opt}}', 'direction of beam 2 in optical coordinates (u, v); tan θ_opt = tan θ / NA'),
    (r'\mathrm{NRMSE}', 'root-mean-square difference of two profiles over the root-mean-square of the reference, unit energy'),
    (r'F,\ C,\ Q', 'Linfoot’s criteria: fidelity, structural content, correlation quality (1 for identical profiles)'),
    (r'\tau', 'pulse duration, FWHM of the intensity; transform-limited pulses are the shortest for their spectrum'),
    (r'p_i(\mathbf{r}, t),\ p_i(\nu)', 'probability of a photon of beam i at r and time t; probability of its frequency ν'),
    (r'h,\ d_s,\ g', 'slab half-thickness; mean free path between scattering events; anisotropy, the mean cosine of one scattering'),
]


def glossary_tex():
    """Glossary with each symbol set in LaTeX on the left and its meaning on the right; LaTeX source in the notes."""
    pages = [GLOSS_TEX[i:i + 7] for i in range(0, len(GLOSS_TEX), 7)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''), '')
        t = 1.05
        for tex, meaning in page:
            h = max(equation(s, 0.55, t, 3.0, tex, 17, number=False), 0.36)
            text(s, 3.45, t, 6.1, h, meaning, 14, NAVY, anchor=ds.MSO_ANCHOR.MIDDLE)
            t += h + 0.14
        notes(s, 'Glossary.', ' '.join(f'{tx}: {m}.' for tx, m in page), '\n'.join(tx for tx, _ in page))


def glossary():
    if SECTION == CMEETING:
        return glossary_tex()
    skip = {'Scalar Debye', 'p_i(ν)', 'A(P)', 'N', 's–s, p–p', 'K'}       # terms the meeting deck does not use
    if SECTION == CMEETING:                                    # no misalignment in the Cambaliza study
        skip = {'x_c, z_c', 'PSF', 'L1, L2; O, O′'}
    rows = [f'{t}: {m}.' for t, (m, use) in GLOSS.items()
            if (use == 'all' or (SECTION == MEETING and t not in skip) or SECTION in use.split())
            and not (SECTION == CMEETING and t in skip)]
    pages = [rows[i:i + 9] for i in range(0, len(rows), 9)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''), '')
        bullets(s, 0.6, 1.1, 8.9, 4.1, page, 12.5)
        notes(s, 'Glossary.', ' '.join(page))


def checks_slide(part):
    """The physics checks of one part, from scripts/check_lim2002_physics.py."""
    import csv as _csv
    path = os.path.join(FIG, 'physics_checks.csv')
    parts = part if isinstance(part, tuple) else (part,)
    if not os.path.exists(path) or not part:
        return
    rows_ = [r for r in _csv.DictReader(open(path)) if r['part'] in parts]
    if not rows_:
        return
    s = slide('Physics checks', '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, [f"{r['check']}: expected {r['expected']}, obtained {r['obtained']}"
                                    + ('' if r['passed'] == 'yes' else ' (fails)') for r in rows_], 12)
    notes(s, 'Each result is checked against an analytic limit, a symmetry or an independent calculation.',
          ' '.join(f"{r['check']}: {r['obtained']}." for r in rows_))


# ── shared setup slides ──
def geometry():
    side('Geometry: x_c, z_c and θ', os.path.join(FIG, 'fig1_geometry.png'), [
        'Lens L1 focuses beam 1 at O, the origin. Lens L2 focuses beam 2 at O′.',
        'x_c is the misalignment of O′ across the axis of L1, in its focal plane; z_c is the misalignment along that axis.',
        'θ is the angle between the two lens axes: θ = π for lenses facing each other, θ = π/2 for crossed lenses.',
        '2CE: λ_1 = 750 nm and λ_2 = 656 nm. 2PE: both beams at λ_{2p} = 700 nm.'],
        'O prime is misaligned from O by x_c across and z_c along the axis of L1.',
        'The geometry of scalar 2CE. Each result is a loss of peak fluorescence, or a change of shape, when O prime moves away '
        'from O, with facing or crossed lenses.', fw=4.4)


def eqslide(title, takeaway, eqs, main, script, latex, side=None, fig=None, size=17):
    """Equation slide: numbered LaTeX equations, each with its 'where' line; a card or a figure at the right."""
    meeting = SECTION == CMEETING                              # meeting deck: no subtitle; one line under each equation
    s = slide(title, '' if meeting else takeaway)
    w = 9.0 if side is None and fig is None else (5.9 if fig is None else 5.5)
    t = 1.05 if meeting else 1.4
    for tex, wh in eqs:
        h = equation(s, 0.55, t, w, tex, size)
        t += h + 0.06
        if wh and meeting:
            line = wh[0].upper() + wh[1:]
            bullets(s, 0.7, t, w - 0.6, 0.5, [line], 12)
            t += 0.21 * -(-len(line) // int((w - 0.6) * 13)) + 0.06
        elif wh:
            t += where(s, 0.6, t, w - 0.6, wh)
        t += 0.12 if meeting else 0.1
    if side and meeting:
        head, lines = side
        bullets(s, 6.75, 1.15, 2.75, 3.9, lines, 13)
    elif side:
        head, lines = side
        card(s, 6.75, 1.4, 2.75, 3.7, head, RED, lines, 10.5, bulleted=False)
    if fig:
        figure(s, fig, 6.15, 1.35, 3.4, 3.8)
    notes(s, main, script, latex)
    return s


def peqslide(title, eqs, main, script, size=17, lead=None):
    """Equations numbered as in the source paper (number None: unnumbered), each followed by the steps it takes, one
    bullet per step (a string or a list); lead = the context line above the first equation."""
    s = slide(title, '')
    t = 1.0
    latex = []
    if lead:
        bullets(s, 0.55, t, 8.9, 0.3, [lead], 13.5)
        t += 0.24 * -(-len(lead) // 110) + 0.14
    for tex, num, line in eqs:
        if num is not None:
            ds.EQN[0] = num - 1
        h = equation(s, 0.55, t, 9.0, tex, size, number=num is not None)
        t += h + 0.06
        lines = [line] if isinstance(line, str) else list(line)
        bullets(s, 0.7, t, 8.6, 0.6, lines, 12.5)
        t += sum(0.22 * -(-len(l_) // 118) + 0.06 for l_ in lines) + 0.24
        latex.append(tex)
    ds.EQN[0] = max(n for _, n, _ in eqs if n is not None)
    notes(s, main, script, '\n'.join(latex))
    return s


ZB = r'z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta'
UPAR = r'U(u,v) \propto e^{i n k_0 z}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\,\rho\, d\rho'


def scalar_fields():
    eqslide('Field equations: scalar 2CE', 'Each beam is the paraxial scalar Debye field; beam 2 is the same field rotated by θ '
            'and centred at O′.', [
        (UPAR, 'r, z = distance from the focus across and along the axis; ρ = radius in the pupil over its edge.'),
        (r'u = \frac{k_0\,\mathrm{NA}^2 z}{n}, \qquad v = k_0\,\mathrm{NA}\, r, \qquad k_0 = \frac{2\pi}{\lambda}',
         'u, v = axial and transverse optical coordinates; λ = vacuum wavelength; n = refractive index.'),
        (ZB, 'x_b, z_b = coordinates of beam 2, rotated by θ about O′ = (x_c, z_c).'),
        (r'F_{2c} = \kappa_{2c}\, I_1 I_2, \qquad F_{2p} = \kappa_{2p}\, |U_1 + U_2|^4', 'I = |U|^2; 2CE multiplies the two '
         'intensities, 2PE adds the two fields.')],
        'The scalar 2CE model: paraxial fields, beam 2 rotated and shifted, 2CE as a product and 2PE as a sum.',
        'The model of the paper, used for the time-delay study at NA 0.5.',
        '\n'.join((UPAR, r'u = k\,\mathrm{NA}^2 z/n, \quad v = k\,\mathrm{NA}\, r', ZB,
                   r'F_{2c} = \kappa_{2c} I_1 I_2, \qquad F_{2p} = \kappa_{2p} |U_1 + U_2|^4')), size=16)


IM = r'I_m = \int_0^\alpha A(\beta)\sqrt{\cos\beta}\,\sin\beta\; g_m(\beta)\, J_m(kr\sin\beta)\, e^{ikz\cos\beta}\, d\beta'
EVEC = r'\mathbf{E} \propto \left(I_0 + I_2\cos 2\phi,\;\; I_2\sin 2\phi,\;\; 2i I_1\cos\phi\right)'
GM = r'g_0 = 1 + \cos\beta, \qquad g_1 = \sin\beta, \qquad g_2 = 1 - \cos\beta, \qquad \sin\alpha = \mathrm{NA}/n'
UNPOL = r'I = \frac{1}{2}\left(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2\right), \qquad F_{2c} = \kappa_{2c}\, I_1 I_2'
F2PV = r'F_{2p} = \kappa_{2p}\, |\mathbf{E}_1 + \mathbf{E}_2|^4'


def vector_fields():
    side('Focusing by an aplanatic lens', os.path.join(os.path.dirname(FIG), 'bg_focusing_geometry.png'), [
        'Each ray leaves the lens toward the focus at an angle β to the axis, up to the cone half-angle α, sin α = NA/n.',
        'After the lens the polarization is transverse to each ray, so the focused field gains a component along z.',
        'Scalar 2CE replaces the phase kz cos β by its small-angle form and leaves out that component; the Richards–Wolf field '
        'keeps both.'],
        'The aplanatic lens bends each ray toward the focus and turns its polarization with it.',
        'This is what the vector model adds: the exact phase of steep rays and the field component along the axis.', fw=5.5)
    eqslide('Field equations: vector 2CE (Richards–Wolf)', 'The Richards–Wolf field keeps the exact phase of each ray and the '
            'three components of the electric field.', [
        (EVEC, 'E = focal field for input polarized along x; φ = angle about the axis.'),
        (IM, 'β = ray angle; r, z = distance from the focus; A(β) = pupil amplitude, 1 for uniform input; √cos β = aplanatic '
             'factor.'),
        (GM, 'α = half-angle of the focusing cone; m = 0, 1, 2.')],
        'The vector Richards–Wolf field.',
        'At low NA it reduces to the paraxial scalar field.', '\n'.join((EVEC, IM, GM)),
        side=('Against scalar 2CE', ['Exact phase kz cos β instead of its small-angle form.', '',
                                     'Three field components; the one along z grows with NA.', '',
                                     'At low NA it reduces to the paraxial scalar field.']), size=15)
    eqslide('Two beams: placement and signals', 'Beam 2 is the same field rotated by θ and centred at O′; 2CE multiplies '
            'unpolarized intensities, 2PE adds polarized fields.', [
        (ZB, 'x_b, z_b = coordinates of beam 2, rotated by θ about O′ = (x_c, z_c).'),
        (UNPOL, 'ψ = input polarization angle; the average over ψ = 0 and π/2 equals circular polarization.'),
        (F2PV, 'both 2PE beams at 700 nm, polarized perpendicular to the plane of the two lens axes, so their fields add.')],
        'Beam 2 is rotated and shifted; 2CE multiplies unpolarized intensities, 2PE adds polarized fields.',
        'In scalar 2CE, I = |U|^2 and F2p = kappa |U1 + U2|^4.', '\n'.join((ZB, UNPOL, F2PV)), size=16)


def lens_problem():
    s = slide('Largest NA of two crossed lenses', 'Two lenses with crossed axes fit side by side while each cone half-angle is at '
              'most 45°.')
    figure(s, os.path.join(os.path.dirname(FIG), 'na_crossing_limit.png'), 0.45, 1.3, 9.1, 3.2)
    h = equation(s, 0.55, 4.6, 5.2, r'\alpha \leq \theta/2 \;\Leftrightarrow\; \mathrm{NA} \leq n\sin(\theta/2)', 17)
    bullets(s, 5.9, 4.6, 3.6, 0.7, ['Any lens: NA = n sin α ≤ n, so NA < 1 in air. θ = π/2: NA 0.71 in air, 0.94 in water; above '
                                     'NA 0.71 our crossed lenses are in water.'], 11)
    notes(s, 'Crossed lenses fit up to NA n sin(theta/2).',
          'Each lens fills a cone of half-angle alpha, sin alpha = NA/n. Two cones meeting at a right angle overlap once their '
          'half-angles exceed 45 degrees: NA 0.71 in air, 0.94 in water. Above NA 0.71 the crossed lenses are computed in '
          'water (n = 1.33). A medium raises the NA but not the cone angle, so in water at NA 0.9 the crossed focus has the '
          'shape of the focus in air at NA 0.68 (0.9/1.33), 1.33 times smaller.', r'\mathrm{NA} \le n \sin(\theta/2)')


FCQ = (r'F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \qquad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, '
       r'\qquad Q = \frac{\langle t\, a \rangle}{\langle t^2 \rangle}')
SPOT = r'\tilde{x} = \frac{x_c\,\mathrm{NA}}{\lambda}, \qquad \tilde{z} = \frac{z_c\,\mathrm{NA}^2}{n\lambda}'


def linfoot():
    eqslide('Linfoot’s criteria', 'Fidelity, structural content and correlation quality compare the misaligned PSF with the '
            'aligned PSF over the window.', [
        (FCQ, 't = aligned PSF; a = misaligned PSF, each scaled to its own peak; ⟨ ⟩ = mean over the 100 × 100 x–z window.'),
        (r'2Q - C = F', 'each criterion is 1 when a = t.'),
        (r'\Delta F = F_{\mathrm{vector}} - F_{\mathrm{scalar}} \quad (\mathrm{same\ NA})',
         'the difference maps compare vector and scalar 2CE at the same NA, so they isolate the exact phase and polarization.')],
        'Linfoot’s three criteria compare the misaligned PSF with the aligned one.',
        'Shown as surfaces over the offset of O prime, as in Figs. 5–6 of the paper, then as differences from scalar 2CE.',
        '\n'.join((FCQ, r'2Q - C = F', r'\Delta F = F_{vector} - F_{scalar}')),
        side=('F, C and Q', ['F, fidelity: overall similarity; 1 − normalized mean-squared error.', '',
                             'C, structural content: relative energy; rises above 1 for a broader PSF.', '',
                             'Q, correlation quality: overlap of the two PSFs.']), size=16)


CASES = [('2ce_pi', '2CE, θ = π'), ('2ce_pi2', '2CE, θ = π/2'), ('2pe_pi', '2PE, θ = π'), ('2pe_pi2', '2PE, θ = π/2')]
LINF = {   # (case, criterion): what the map shows, with uniform input
    ('2ce_pi', 'F'): 'At high NA the region F ≥ 0.8 is shorter along the axis than the scalar 2CE region (red dotted) and '
                     'slightly wider across it: the vector focus is less elongated, so a misalignment along the axis changes '
                     'the shape sooner.',
    ('2ce_pi', 'C'): 'C rises as O′ moves away. At high NA the region C ≤ 1.2 is shorter along the axis than the scalar 2CE '
                     'region, as for F.',
    ('2ce_pi', 'Q'): 'Near the aligned point the region Q ≥ 0.8 changes little with NA. Farther out Q rises again, because the '
                     'misaligned PSF, scaled to its own peak, is broad and covers the aligned one.',
    ('2ce_pi2', 'F'): 'With crossed beams the region F ≥ 0.8 becomes narrower in x_c and longer in z_c at high NA: a '
                      'misalignment in x_c moves O′ along beam 2, whose focus is shorter in the vector model.',
    ('2ce_pi2', 'C'): 'With crossed beams C stays within 20% up to about one spot unit in x_c; at high NA this range narrows.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0; the band changes little with NA near the aligned point.',
    ('2pe_pi', 'F'): 'The 2PE region F ≥ 0.8 is set by the standing-wave fringes, whose spacing λ_{2p}/2n does not depend on '
                     'NA, and changes little with NA.',
    ('2pe_pi', 'C'): 'C stays within 20% for x_c up to about 0.35 spot units (x_c NA/λ) and changes little with NA.',
    ('2pe_pi', 'Q'): 'Q ≥ 0.8 near the aligned point and again near the next fringes; both change little with NA.',
    ('2pe_pi2', 'F'): 'With crossed beams the regions F ≥ 0.8 repeat with the fringes, one wavelength apart, and change little '
                      'with NA.',
    ('2pe_pi2', 'C'): 'The regions C ≤ 1.2 follow the tilted fringes; at high NA they close into loops around the aligned point.',
    ('2pe_pi2', 'Q'): 'Q ≥ 0.8 near the aligned point and near the next fringes, one wavelength away; at high NA the central '
                      'region tilts with the fringes.',
}
LINF_G = {   # the same maps with Gaussian input (α_t = 4)
    ('2ce_pi', 'F'): 'At high NA the region F ≥ 0.8 is slightly shorter along the axis than the scalar 2CE region, by less than '
                     'with uniform input: the Gaussian focus is closer to paraxial.',
    ('2ce_pi', 'C'): 'The region C ≤ 1.2 is an ellipse; at high NA it is shorter along the axis than the scalar 2CE region.',
    ('2ce_pi', 'Q'): 'Q stays above 0.8 between the two lines, over the whole computed range along the axis; the lines change '
                     'little with NA.',
    ('2ce_pi2', 'F'): 'With crossed beams the region F ≥ 0.8 changes less with NA than with uniform input.',
    ('2ce_pi2', 'C'): 'In scalar 2CE the region C ≤ 1.2 is bounded in x_c and open along z_c; at high NA the vector region closes '
                      'into an ellipse.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0, about ±0.3 spot units wide, which changes little with NA.',
    ('2pe_pi', 'F'): 'As with uniform input, the region F ≥ 0.8 is set by the standing-wave fringes and changes little with NA.',
    ('2pe_pi', 'C'): 'C stays within 20% for x_c up to about 0.4 spot units (x_c NA/λ) and changes little with NA.',
    ('2pe_pi', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0, about ±0.15 λ/n wide, which changes little with NA.',
    ('2pe_pi2', 'F'): 'With crossed beams the regions F ≥ 0.8 repeat with the fringes, one wavelength apart, and change little '
                      'with NA.',
    ('2pe_pi2', 'C'): 'The regions C ≤ 1.2 follow the tilted fringes as diagonal bands.',
    ('2pe_pi2', 'Q'): 'Q ≥ 0.8 near the aligned point and near the next fringes, one wavelength apart.',
}
LEV = {'F': 'F = 0.8', 'C': 'C = 1.2', 'Q': 'Q = 0.8'}
NAME = {'F': 'Fidelity', 'C': 'Structural content', 'Q': 'Correlation quality'}


SURF = {   # (case, criterion): what the surfaces show, scalar 2CE at NA 0.5 against vector 2CE at NA 0.7 and 0.9
    ('2ce_pi', 'F'): 'The peak of F around the aligned point narrows along z_c as NA grows, and F falls below −1 over most of the '
                     'misalignments: the spot is smaller, so the same misalignment changes its shape more.',
    ('2ce_pi', 'C'): 'C rises above 1 as O′ moves away; the region near 1 shrinks to a small well around the aligned point at '
                     'high NA.',
    ('2ce_pi', 'Q'): 'Q dips next to the aligned point and returns toward 1 farther out; the pattern becomes finer as NA '
                     'grows.',
    ('2ce_pi2', 'F'): 'With crossed beams F stays high along x_c in scalar 2CE; at NA 0.9 the high region closes in x_c as well.',
    ('2ce_pi2', 'C'): 'C stays near 1 in a band around z_c = 0; at high NA the band becomes uneven along x_c.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0 in scalar 2CE; at NA 0.9 the band becomes a closed region.',
    ('2pe_pi', 'F'): 'The 2PE F is set by the standing-wave fringes; at high NA the region near the aligned point narrows and the '
                     'side structure becomes finer.',
    ('2pe_pi', 'C'): 'C rises steeply as O′ moves across the axis; at high NA the well around the aligned point narrows.',
    ('2pe_pi', 'Q'): 'Q dips near the aligned point and returns toward 1 at the next fringes; the dip narrows as NA grows.',
    ('2pe_pi2', 'F'): 'With crossed beams F peaks at each bright fringe, about one wavelength apart in x_c; the peaks stay at the '
                      'same places as NA grows.',
    ('2pe_pi2', 'C'): 'C follows the tilted fringes and rises quickly away from them.',
    ('2pe_pi2', 'Q'): 'Q is high near the aligned point and near the next fringes, one wavelength apart.',
}


def linfoot_maps(suf, tag):
    """For each case and criterion: the 3D surfaces (scalar 2CE, NA 0.7, NA 0.9), then the difference from scalar 2CE."""
    for case, lab in CASES:
        for key in 'FCQ':
            t = f'{NAME[key]}{tag}: {lab}'
            if suf:
                wide(f'{key}: uniform against Gaussian input, {lab}', SL(f'linfoot3d_{key}_{case}_input.png'), [
                    'Scalar 2CE at NA 0.5 with uniform input (left) and Gaussian input, α_t = 4 (right): the effect of the '
                    'Gaussian input alone, before NA is raised.'],
                    f'{lab}: {NAME[key].lower()}, uniform against Gaussian input.',
                    'Same model, NA, window and offsets; only the pupil amplitude changes.')
            side3 = ('With the Gaussian input the surfaces are smoother and change less with NA than with uniform input, '
                     'because the dim pupil edge keeps the focus closer to paraxial.') if suf else SURF[(case, key)]
            wide(t, SL(f'linfoot3d_{key}_{case}{suf}.png'), [side3 + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'pi2' in case else '')],
                 f'{lab}: {NAME[key].lower()} against the misalignment, scalar 2CE and vector 2CE.',
                 'Surfaces over (x_c, z_c) on the axes of Figs. 5–6, in units of lambda_1 (2CE) or lambda_2p (2PE): scalar 2CE at '
                 'NA 0.5, then vector 2CE at NA 0.7 and 0.9. Crossed lenses at NA 0.9 are in water (n = 1.33).')
            wide(f'{key}{tag}, vector − scalar: {lab}', SL(f'linfoot_diff_{key}_{case}{suf}.png'), [
                f'Δ{key} = {key} of vector 2CE minus {key} of scalar 2CE at the same NA: red where the vector value is higher, blue '
                'where it is lower; black line: no difference. The difference grows from NA 0.7 to NA 0.9.'],
                f'{lab}: where vector and scalar {NAME[key].lower()} differ.',
                'Both computed at the same NA, so the difference is the effect of the exact phase and polarization alone. The '
                'colour scale covers 98 percent of the points; the arrows mark values beyond it.')


FIGTXT = {
    (2, 'a'): ('2CE, θ = π', 'From scalar 2CE at NA 0.5 to vector 2CE at NA 0.9 the aligned 2CE spot becomes a little over half '
               'as wide and about a third as long, so it is less elongated.'),
    (2, 'b'): ('2PE, θ = π', 'The 2PE standing wave keeps its fringe spacing, λ_{2p}/2, while the spot around it shrinks; at '
               'NA 0.9 it holds a few fringes.'),
    (2, 'c'): ('2CE, θ = π/2', 'With crossed beams the aligned 2CE spot is set by the widths of the two beams; it shrinks in both '
               'directions as NA grows.'),
    (2, 'd'): ('2PE, θ = π/2', 'The 2PE PSF keeps its tilted fringes and shrinks as NA grows; the weak 1% halo of scalar 2CE disappears.'),
    (3, 'a'): ('2CE, θ = π', 'With O′ at (0.4, 1.0) µm the 2CE spot still forms between O and O′; at high NA it is smaller and '
               'tilted toward O′.'),
    (3, 'b'): ('2PE, θ = π', 'At NA 0.9 the misaligned 2PE spot breaks into a few separate fringes between O and O′.'),
    (3, 'c'): ('2CE, θ = π/2', 'With crossed beams the misaligned 2CE peak follows beam 2 along z; at NA 0.9 it also moves toward O′ in x.'),
    (3, 'd'): ('2PE, θ = π/2', 'The misaligned 2PE PSF breaks into separate pieces along the fringes; at NA 0.9 a second maximum appears near O.'),
    (4, 'a'): ('2CE, θ = π', 'The misalignments that keep 80% of the 2CE peak reach about ±2.7 λ_1 along the axis in scalar 2CE and '
               'about ±0.7 λ_1 at NA 0.9.'),
    (4, 'b'): ('2PE, θ = π', 'The 2PE peak map shrinks in the same way; the standing-wave fringes make it vary slightly along z.'),
    (4, 'c'): ('2CE, θ = π/2', 'In scalar 2CE the peak barely depends on x_c; with vector 2CE at high NA the region that keeps the '
               'peak closes in x_c as well as in z_c.'),
    (4, 'd'): ('2PE, θ = π/2', 'The tilted bands of the 2PE peak map, from interference, narrow as NA grows.'),
}


def maps(suf, tag):
    for (no, t), (lab, line) in FIGTXT.items():
        where = {2: 'aligned foci', 3: 'O′ at (0.4, 1.0) µm', 4: 'peak against the misalignment (x_c, z_c)'}[no]
        if suf and no == 4:
            line = ('With the Gaussian input the region that keeps the peak is larger than with uniform input at the same NA, '
                    'and it shrinks in the same way as NA grows.')
        elif suf:
            line = ('With the Gaussian input the spot is wider and longer than with uniform input at the same NA, and it shrinks '
                    'in the same way as NA grows.')
        if suf:
            wide(f'Fig. {no}({t}), uniform against Gaussian input: {lab}', SL(f'map_fig{no}{t}_input.png'), [
                'Scalar 2CE at NA 0.5, the case of the paper, with uniform input (left) and Gaussian input, α_t = 4 (right): the '
                'effect of the Gaussian input alone, before NA is raised.'],
                f'Fig. {no}({t}): the effect of the Gaussian input at NA 0.5.',
                'Same model, NA and axes; only the pupil amplitude changes. Contours in percent of the peak; orange: 50 percent.')
        wide(f'Fig. {no}({t}) against NA{tag}: {lab}', SL(f'map_fig{no}{t}{suf}.png'), [line + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'π/2' in lab else '')],
             f'Fig. {no}({t}): scalar 2CE at NA 0.5 against vector 2CE at NA 0.7 and 0.9.',
             f'Fig. {no}({t}), {lab}, {where}: scalar 2CE at NA 0.5 (the replication), then vector 2CE at NA 0.7 and 0.9, on the '
             'axes of the paper. Contours in percent of the peak; orange: 50 percent.'
             + (' At theta = pi/2, NA 0.9 is in water (n = 1.33): the two lenses do not fit in air above NA 0.71.'
                if 'π/2' in lab else ''))
        wide(f'Fig. {no}({t}), scalar and vector at the same NA{tag}: {lab}', SL(f'map_fig{no}{t}_samena{suf}.png'), [
            'Scalar 2CE and vector 2CE at the same NA, 0.7 and 0.9: the difference between the two models alone, without the '
            'change of NA.' + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'π/2' in lab else '')],
            f'Fig. {no}({t}): scalar against vector at equal NA.', 'Same NA, same axes; contours in percent of the peak.')


PEAK = [
    ('2CE, θ = π/2, x_c = 1.33 λ_1', 'We move O′ by 1.33 λ_1 across the axis of L1, which is along the axis of beam 2.',
     'At NA 0.5 the 2CE peak drops by about 12%; scalar 2CE gives 11%.',
     'The loss grows to about 45% at NA 0.7: the misalignment is along beam 2, so it follows the length of its focus, which '
     'shrinks as 1/NA^2.'),
    ('2CE, θ = π, x_c = 0.37 λ_1', 'We move O′ by 0.37 λ_1 across the axis, with the lenses facing each other.',
     'At NA 0.5 the 2CE peak drops by 17%; scalar 2CE gives 20%.',
     'At NA 0.9 the same misalignment reduces the peak by about 42%: the spot narrows as 1/NA, so the same shift is a larger '
     'part of it.'),
    ('2PE, θ = π/2, x_c = 0.5 λ_{2p}', 'We move O′ by half a wavelength across the axis of L1, with crossed beams at 700 nm.',
     'At NA 0.5 the 2PE peak drops by 26%; scalar 2CE gives 30%.',
     'The loss grows to about 44% at NA 0.7, as the spot shrinks while the fringes keep their spacing. Below NA 0.3 the grid '
     'of misalignments is coarser than the fringes, so those points are left out.'),
    ('2CE, θ = π, z_c = 2.7 λ_1', 'We move O′ by 2.7 λ_1 along the axis, with the lenses facing each other.',
     'At NA 0.5 the 2CE peak drops by 22%; scalar 2CE gives 20%.',
     'The loss rises to about 70% at NA 0.7 and 95% at NA 0.9: the length of the focus shrinks as 1/NA^2, faster than its '
     'width.'),
    ('2CE, θ = π/2, z_c = 2.7 λ_1', 'We move O′ by 2.7 λ_1 along the axis of L1, with crossed beams.',
     'At NA 0.5 the 2CE peak drops by 36%; scalar 2CE gives 30%.',
     'The loss rises to about 90% at NA 0.7: the misalignment slides beam 2 along the length of beam 1. Below NA 0.2 the grid '
     'of misalignments is too coarse for the long focus, so those points are left out.'),
]
PEAK_G = [(51, 'about 6%'), (24, 'about 8%'), (38, 'about 14%'), (72, 'about 11%'), (75, 'about 19%')]
LEGEND = ('Blue: vector 2CE; red: scalar 2CE; star: the loss reported at NA 0.5; grey: NA above 0.5, where the paraxial model '
          'is expected to break down.')


def peaks(suf):
    for k, (lab, how, low, high) in enumerate(PEAK, 1):
        if suf:
            v9, v5 = PEAK_G[k - 1]
            items = [how, f'With α_t = 4 the peak drops by {v5} at NA 0.5, about half the loss with uniform input, and by '
                          f'about {v9}% at NA 0.9.', 'The Gaussian focus is larger, so the same misalignment is a smaller part of it.']
            name = f'Peak lost, Gaussian input: {lab}'
        else:
            items, name = [how, low, high], f'Peak lost against NA: {lab}'
        if 'π/2' in lab:
            items.append('Above NA 0.71 the two lenses do not fit in air; open circles: the lenses in water (n = 1.33).')
        side(name, SL(f'peaklost_{k}{suf}.png'), items, f'{name}.', LEGEND)


DECIDE = ['Polarization of the two beams: keep unpolarized (circular) beams, or account for linear polarization.',
          'Optical pulses: weight the photon pairs by the dye’s absorption (which dye, which band).']

SUMMARIES = {   # section: (main point, supporting, supporting, speaker script); the overview shows them all
    'overview': (
        'At high NA the 2CE alignment tolerances shrink with the size of the focus: with facing lenses, as 1/NA across the axis '
        'and 1/NA^2 along it.',
        'Rebuilt from its equations, scalar 2CE reproduces the paper: the 2CE PSF is more robust against misalignment than the 2PE '
        'PSF, most of all with crossed beams.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.45, which validates it there; a Gaussian input makes the '
        'tolerances about 1.4 times larger.',
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments along the axis than scalar 2CE predicts.',
        'A time delay between continuous beams leaves the 2CE PSF unchanged but shifts the 2PE fringes, with the same effect as a '
        'misalignment of cΔt/n in space.',
        'With vector fields, the alignment tolerances follow the width and length of the focus as NA grows. The paper is '
        'reproduced, its scalar model agrees with the vector one where the paper uses it, a Gaussian input loosens the tolerances, '
        'and a time delay acts on 2PE through its fringes while 2CE does not change.'),
    'replication': (
        'Rebuilt from its equations, the scalar 2CE model reproduces the six figures and, within a few percent, the losses '
        'reported in the paper.',
        'What holds: the 2CE PSF is more robust against misalignment than the 2PE PSF, most of all when the two beams cross at '
        'θ = π/2.',
        'What differs: C and Q are swapped in Figs. 5–6, Eq. (2) has to be applied as a rotation in space, Figs. 6(c)–(d) are '
        'most likely θ = 0, and the reported losses differ from ours by up to 3 points (20% against 18%, 30% against 27%).',
        'The figures and losses are reproduced, and the conclusion holds. Four things differ: the C and Q labels, the rotation as '
        'printed, the caption of the bottom row of Fig. 6, and the reported losses by a few points.'),
    'vector': (
        'With vector 2CE the alignment tolerances shrink as NA grows, following the size of the focus.',
        'With facing lenses the 20% tolerances shrink as NA^{−0.97} across the axis and NA^{−2.12} along it; with crossed lenses '
        'both shrink as about NA^{−2.1}.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.45, which validates it there; above it, its small-angle phase '
        'overestimates the tolerance along the axis, and in water this starts at 1.33 times the NA in air.',
        'Recomputed with the vector focus, the tolerances follow the width and length of the focus. The paraxial model agrees to '
        'five percent up to NA 0.45; above that, its longer focus overestimates the tolerance along the axis.'),
    'fidelity': (
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments than scalar 2CE predicts.',
        'With facing lenses the region of high fidelity narrows along z_c from scalar 2CE to vector NA 0.9; with crossed lenses '
        'it also closes in x_c.',
        'For 2PE, Linfoot’s criteria are set by the fringes, whose spacing does not depend on NA; the vector−scalar differences '
        'follow the fringes.',
        'Linfoot’s criteria of the paper, as surfaces against the misalignment for scalar 2CE and vector 2CE at NA 0.7 and 0.9, '
        'and as differences from scalar 2CE at the same NA.'),
    'gaussian': (
        'With a Gaussian input (α_t = 4) the alignment tolerances are about 1.4 times larger than with uniform input.',
        'The dim edge of the pupil removes the high-angle rays, so the focus is wider and longer; at NA 0.5 the same '
        'misalignments cost about half the peak they cost with uniform input.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.525, against 0.45 with uniform input.',
        'With a Gaussian input the high-angle rays are dim, so the focus behaves like a lower NA: larger tolerances, and a '
        'paraxial model that holds to a higher NA.'),
    'delay': (
        'A time delay Δt between continuous beams is a phase ωΔt: it leaves the 2CE PSF unchanged and shifts the 2PE fringes, '
        'as a misalignment of cΔt/n does.',
        'The 2CE signal I_1 I_2 depends on intensities, which do not carry the phase; for 2PE at θ = π/2, half an optical period '
        '(1.17 fs) puts the centre on a dark fringe and loses 29% of the peak.',
        'The 2PE loss of a misalignment is mainly this fringe phase: the matching time delay brings the loss of a 0.5 λ_{2p} '
        'misalignment from 26% to about 1%. 2CE has no fringes, so a time delay cannot change its loss.',
        'Delaying a continuous beam multiplies its field by a phase. Two-color excitation multiplies intensities, so the phase '
        'drops out. Two-photon excitation adds fields, so the phase moves its fringes, by the same amount as a misalignment of '
        'c Delta t over n at theta = pi/2.'),
}
PART_TITLE = {'replication': 'Part 1: Replication of scalar 2CE', 'vector': 'Part 2: Vector 2CE, uniform input',
              'fidelity': 'Part 3: Linfoot’s criteria against NA', 'gaussian': 'Part 4: Vector 2CE, Gaussian input',
              'delay': 'Part 5: Time delay'}


# ══ sections ═════════════════════════════════════════════════════════════
if SECTION == 'overview':
    title('Progress Report', 'Two-color excitation: scalar 2CE, vector 2CE, time delay and optical pulses')
    words('Things done', [
        'Part 1: Replication of scalar 2CE.',
        '– Rebuilt from its equations, the model reproduces the figures and reported losses: 2CE is more robust against '
        'misalignment than 2PE, most of all with crossed beams.',
        'Part 2: Vector 2CE, uniform input, against NA.',
        '– The alignment tolerances shrink as NA grows, as 1/NA across the axis and 1/NA^2 along it; scalar 2CE agrees within 5% '
        'up to NA 0.45. Crossed lenses above NA 0.71 do not fit in air and are computed in water.',
        'Part 3: Linfoot’s criteria against NA.',
        '– At high NA the 2CE PSF keeps its shape over a smaller range of misalignments than scalar 2CE predicts.',
        'Part 4: Vector 2CE, Gaussian input.',
        '– The tolerances are about 1.4 times larger than with uniform input, and scalar 2CE holds to NA 0.525.',
        'Part 5: Time delay between continuous beams.',
        '– A time delay leaves the 2CE PSF unchanged and shifts the 2PE fringes, as a misalignment of cΔt/n does.',
        'Part 6: Polarization, s and p.',
        '– At high NA linear polarization changes the 2CE results across the axis with facing lenses, and decides whether '
        'crossed-beam 2PE interferes; results along the axis do not change.',
        'Part 7: Optical pulses and time delay.',
        '– A time delay lowers 2CE because the photon pairs that reach the transition add out of phase where the two pulses do '
        'not arrive together; with crossed lenses 20% of the peak is lost at a delay of 0.4 τ.'],
        'Seven parts, each with its main result.',
        ' '.join(SUMMARIES[k][3] for k in PART_TITLE), size=11.5)
    words('New since the last meeting', [
        'Photon pairs: the probability of each pair of wavelengths, one from each pulse, that reaches the 350 nm transition, '
        'derived in closed form. Shorter pulses bring in more pairs (Part 7).',
        'Pulsed 2CE counts those pairs: the PSF is the continuous-beam PSF times the probability that a pair reaches the '
        'transition, times the overlap in time of the two pulses. At equal pulse energy, shorter pulses give no more signal '
        '(Part 7).',
        'Time delay between pulses: with crossed lenses the PSF keeps its shape and loses 20% of its peak at a delay of 0.4 τ; '
        'with facing lenses and 10–20 fs pulses the PSF moves along the axis with the plane where the pulses meet (Part 7).',
        'Crossed lenses above NA 0.71 are computed in water, so the crossed-lens results continue to NA 0.9 (Parts 2–4).',
        'Air and water at the same NA: the same power laws; in water the focus is about 1.4 times longer, and the departure '
        'from the paraxial law starts at 1.33 times the NA (Part 2).',
        'Scalar 2CE and vector 2CE compared at the same NA, 0.7 and 0.9, which shows the difference between the two models '
        'alone (Parts 2–4 and 7).'],
        'Photon pairs, pulsed 2CE with a time delay, and crossed lenses in water.',
        'Since the last meeting: the photon-pair calculation, the pulsed PSF with a time delay, water for crossed lenses, '
        'air against water at the same NA, and scalar against vector at the same NA.', size=13)
    words('Next steps: points to settle', DECIDE, 'Two points to settle before the next results.',
          'The polarization of the beams, and the dye that weights the photon pairs.')
    words('To consider: polarization of the two beams', [
        'Polarization is the direction in which a beam’s electric field oscillates; it is always perpendicular to the direction '
        'the beam travels.',
        'The two lens axes lie in one plane (the x–z plane of the geometry). s polarization: the field is perpendicular to that '
        'plane (out of the page). p polarization: the field lies in that plane. s–s and p–p mean both beams are s, or both p.',
        'So far each 2CE beam is unpolarized (averaged over both directions, the same as circular polarization), which gives a '
        'round focal spot.',
        'At high NA a linearly polarized spot is wider along its field, so results across the axis depend on the direction of '
        'the misalignment. For 2PE with crossed beams, s–s fields are parallel and interfere; p–p fields are perpendicular and '
        'barely interfere.',
        'To decide: keep unpolarized beams, or account for linear (s or p) polarization.'],
        'Polarization is the direction of the field; s is perpendicular to the plane of the lens axes, p lies in it.',
        'The definitions of s and p, and why the choice matters at high NA.', size=12.5)
    wide('To consider: polarization, focal spot', SL('polarization_spot.png'), [
        'One beam at focus, across x. At high NA the focused spot is wider along the polarization than across it, so results '
        'across the axis depend on how the misalignment is oriented.'],
        'At high NA the spot depends on the polarization.',
        'Blue: field along y; red: field along x. At NA 0.5 the two nearly coincide; at NA 0.9 the spot is about 1.35 times '
        'wider along the polarization.')
    RATE = r'\text{rate} \propto \int g(\Omega)\, \bigl|\tilde{P}(\Omega)\bigr|^2 d\Omega, \qquad P(t) = E_1(t)\, E_2(t)'
    eqslide('To consider: weighting the pairs by the dye', 'The dye’s absorption g weights each pair by its total frequency; a '
            'flat g gives the time-overlap signal used so far.', [
        (RATE, 'Ω = ω_1 + ω_2 = total frequency of a pair; g(Ω) = absorption of the dye; P̃ = spectrum of the product field.'),
        (r'g = \text{const.}: \quad \int g\,|\tilde{P}|^2 d\Omega \;\propto\; \int I_1(t)\, I_2(t)\, dt',
         'Parseval: a flat absorption gives exactly the current signal (checked numerically: equal to 6 digits).'),
        (r'\text{equal Gaussian pulses: } |\tilde{P}(\Omega)|^2 \propto e^{-(\Omega-\Omega_0)^2 \tau^2/8\ln 2}\ \text{at every point}',
         'the pair spectrum has the same shape everywhere, so weighting scales the signal by one factor and leaves the PSF '
         'shapes and tolerances unchanged.')],
        'Weighting by the dye changes how much signal there is, not the shape of the PSF, for equal Gaussian pulses.',
        'The weighted rate integrates the dye absorption against the spectrum of the product field.', RATE, size=14)
    wide('To consider: signal kept by the dye weighting', SL('pulse_pairs_weight.png'), [
        'Signal kept when the dye absorbs in a Gaussian band around 350 nm, relative to a flat band. At 100 fs nearly all '
        'pairs fall within a 10 nm band; at 20 fs about 60% do, and at 10 fs about 35%. To decide: which dye, and so which g.'],
        'Short pulses waste pairs outside the dye band.', 'Gaussian absorption bands of FWHM 2, 5, 10 and 20 nm centred at 350 nm.')

elif SECTION == 'replication':
    at = len(prs.slides)
    try:
        runpy.run_path(os.path.join(HERE, 'make_lim2002_replication_deck.py'), run_name='__main__')
    except SystemExit:
        pass

elif SECTION == 'vector':
    title('Part 2: Vector 2CE, uniform input', 'The results of scalar 2CE with the Richards–Wolf focus, NA 0.03 to 1.2')
    summary(*SUMMARIES['vector'])
    geometry(); vector_fields()
    maps('', '')
    for key, lab, line in (
            ('pi', 'θ = π', 'Across the axis the tolerance falls as NA^{−0.97}, close to 1/NA, as the width of the spot does; '
             'along the axis it falls as NA^{−2.12}, close to 1/NA^2, as its length does.'),
            ('pi2', 'θ = π/2', 'With crossed beams both tolerances fall as about NA^{−2}: a misalignment in x_c is along the axis '
             'of beam 2 and one in z_c is along the axis of beam 1, so both follow the length of the focus. Above NA 0.71 the '
             'lenses are in water (open circles), where the focus is 1.33 times longer at the same NA.')):
        wide(f'20% tolerances against NA, {lab}', SL(f'tolerance_{key}.png'), [
            'The tolerance is the misalignment of O′ that reduces the 2CE peak by 20%. ' + line],
            f'At {lab} the 20% tolerances shrink as a power of NA.',
            'Blue: vector 2CE; red: scalar 2CE; star: the tolerance reported at NA 0.5; grey: NA above 0.5, where the paraxial model is '
            'expected to break down.')
    wide('Scalar 2CE against vector 2CE, 20% tolerances', SL('deviation.png'), [
        'The difference between the 20% tolerances of scalar and vector 2CE passes 5% at NA 0.45 and 10% at NA 0.6 along the '
        'axis, and with crossed beams in both directions. Across the axis at θ = π it stays within 5% up to NA 0.8. With '
        'crossed lenses in water (dashed), the difference at NA 0.9 is 14%, as in air at NA 0.68: it follows the cone angle.'],
        'Scalar 2CE is within 5% up to NA 0.45; along the axis it departs first.',
        'The paraxial focus is longer than the vector one, so it overestimates the tolerance along the axis. Across the axis the two '
        'differ through polarization, which is small up to NA 0.8. The vertical line is NA 0.5, the value used in scalar 2CE.')
    wide('20% tolerances in water, θ = π', SL('tolerance_pi_n1.33.png'), [
        'In water (n = 1.33) the tolerances follow the same power laws. Scalar 2CE departs by 5% at NA 0.6 and 10% '
        'at NA 0.8, 1.33 times the values in air: the difference is set by the angle of the cone, sin α = NA/n.'],
        'In water scalar 2CE holds to 1.33 times the NA it holds to in air.',
        'The same 20% tolerances in water, up to NA 1.2.')
    for key, lab, line in (
            ('pi', 'θ = π', 'Facing lenses, vector 2CE, uniform input. At the same NA the tolerance across the axis is the same '
             'in air and water, and along the axis it is about 1.4 times larger in water. Fitted over NA 0.5–0.7, where both '
             'media are computed, the power laws are the same: close to 1/NA across the axis and 1/NA^2 along it. Air is a '
             'little steeper along the axis, because its wider cone departs from the paraxial law sooner.'),
            ('pi2', 'θ = π/2', 'Crossed lenses, vector 2CE, uniform input; in air the lenses fit up to NA 0.71. At the same NA '
             'both tolerances are about 1.4 times larger in water, because both follow the length of the focus. Fitted over '
             'NA 0.5–0.7 both media follow about 1/NA^2; air is a little steeper.')):
        wide(f'20% tolerances in air and water, {lab}', SL(f'air_water_{key}.png'), [line],
             'Water keeps the power laws and moves the high-NA departure to 1.33 times the NA.',
             'Filled: air; open: water. Lines: power-law fits over NA 0.5 to 0.7, solid for air and dashed for water. At the '
             'same NA the cone in water is narrower, sin alpha = NA/n, so the focus is about as wide and 1.33 times longer.')
    lens_problem()
    peaks('')
    wide('Profiles at NA 0.8, θ = π', SL('profiles_pi_na0.8.png'), [
        'The aligned 2CE spot at NA 0.8 with three foci. Across the axis the three agree. Along the axis the paraxial spot is '
        'longer, while the scalar Debye focus, which keeps the exact phase but no polarization, matches the vector one: the '
        'small-angle phase causes the difference.'],
        'The small-angle phase, not polarization, lengthens the paraxial focus.',
        'Three foci of the same beams: paraxial scalar, scalar Debye with the exact phase kz cos beta, and vector.')
    wide('Check: scalar and vector focus at NA 0.5', SL('onaxis_scalar_vector_na0.5.png'), [
        'At NA 0.5, the value used in scalar 2CE, the scalar and vector foci of one beam nearly coincide along the axis, for uniform '
        'input and for a Gaussian input (α_t = 4).'],
        'At NA 0.5 the two foci nearly coincide.', 'A single beam at 750 nm, intensity along the axis.')

elif SECTION == 'fidelity':
    title('Part 3: Linfoot’s criteria against NA', 'Linfoot’s criteria (F, C and Q) of the misaligned PSF: scalar 2CE, and vector 2CE at NA 0.7 and 0.9')
    summary(*SUMMARIES['fidelity'])
    geometry(); vector_fields(); linfoot()
    linfoot_maps('', '')

elif SECTION == 'gaussian':
    title('Part 4: Vector 2CE, Gaussian input', 'Both lenses filled by a Gaussian beam, truncation parameter α_t = 4')
    summary(*SUMMARIES['gaussian'])
    geometry(); vector_fields()
    eqslide('Gaussian input: the pupil of both beams', 'Each lens is filled by a Gaussian beam with α_t = 4, which the aperture barely truncates; the '
            'same pupil amplitude on both lenses and for both wavelengths.', [
        (r'A(\beta) = \exp\left(-\alpha_t\, \frac{\sin^2\beta}{\sin^2\alpha}\right), \qquad \sin\alpha = \mathrm{NA}/n',
         'A(β) = pupil amplitude in the Richards–Wolf integrals; α_t = truncation parameter; 0 is uniform input.'),
        (r'A(\rho) = e^{-\alpha_t \rho^2}', 'the same amplitude in scalar 2CE, with ρ = radius in the pupil over its edge.'),
        (r'A(\rho = 1) = e^{-4} \approx 0.02 \quad (\alpha_t = 4)', 'the field at the edge of the pupil is about 2% of the '
                                                                     'centre and the aperture cuts off about 0.03% of the beam power: nearly untruncated.')],
        'Each lens is filled by a nearly untruncated Gaussian beam, alpha_t = 4.',
        'The apodization enters the Richards–Wolf integrals as A(beta).',
        r'A(\beta) = \exp\!\left(-\alpha_t \frac{\sin^2\beta}{\sin^2\alpha}\right), \quad \sin\alpha = \mathrm{NA}/n \qquad A(\rho) = e^{-\alpha_t \rho^2}',
        fig=SL('pupil_apodization.png'), size=17)
    wide('Check: uniform input is the limit α_t → 0', os.path.join(FIG, 'axial_lim_vs_truncation.png'), [
        'The scalar focus along the axis for several α_t. As α_t decreases the focus returns to the uniform focus; at α_t = 0.5 '
        'the two already overlap.'],
        'The Gaussian focus returns to the uniform one as alpha_t goes to zero.',
        'A single beam at 750 nm. Larger alpha_t lengthens the focus and fills its zeros.')
    wide('Gaussian input against uniform input', SL('onaxis_gaussian_uniform.png'), [
        'Along the axis the Gaussian focus (α_t = 4) is longer than the uniform one and has no zeros, at NA 0.5 and at NA 0.9.'],
        'A Gaussian input lengthens the focus.', 'A single beam at 750 nm, vector focus, intensity along the axis.')
    maps('_at4', ', Gaussian input')
    for key, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
        wide(f'20% tolerances, Gaussian input, {lab}', SL(f'tolerance_{key}_at4.png'), [
            'With α_t = 4 the tolerances follow the same power laws as with uniform input and are about 1.4 times larger. The '
            'star is the value reported for uniform input at NA 0.5.'],
            f'Gaussian input: the tolerances at {lab} are larger by about 1.4.',
            'Blue: vector 2CE; red: scalar 2CE up to NA 0.5.')
    wide('Scalar 2CE against vector 2CE, Gaussian input', SL('deviation_at4.png'), [
        'With α_t = 4 the scalar 2CE tolerances depart by 5% at NA 0.525 and 10% at NA 0.7, against 0.45 and 0.6 for uniform '
        'input: the dim pupil edge removes the rays for which the small-angle phase is worst.'],
        'With a Gaussian input the paraxial focus holds to a higher NA.',
        'The difference between scalar and vector 20% tolerances, Gaussian input.')
    wide('20% tolerances in water, Gaussian input, θ = π', SL('tolerance_pi_at4_n1.33.png'), [
        'In water with α_t = 4 the tolerances follow the same power laws. Scalar 2CE departs by 5% at NA 0.7 and 10% '
        'at NA 0.9.'],
        'In water with a Gaussian input scalar 2CE holds to NA 0.7.', 'The same tolerances in water, up to NA 1.2.')
    lens_problem()
    peaks('_at4')
    linfoot()
    linfoot_maps('_at4', ', Gaussian input')

elif SECTION == 'delay':
    title('Part 5: Time delay', 'A time delay Δt between two continuous beams, and its relation to a misalignment, scalar 2CE, NA 0.5')
    summary(*SUMMARIES['delay'])
    geometry(); scalar_fields()
    D1 = r'U_2(P, t - \Delta t) = U_2(P, t)\, e^{i\phi}, \qquad \phi = \omega\Delta t = \frac{2\pi c\,\Delta t}{\lambda}'
    D2 = r'F_{2c} = \kappa_{2c}\, I_1 \left|U_2 e^{i\phi}\right|^2 = \kappa_{2c}\, I_1 I_2'
    D3 = r'\left|U_1 + U_2 e^{i\phi}\right|^2 = I_1 + I_2 + 2|U_1 U_2| \cos(\mathbf{K}\cdot\mathbf{r} - \phi)'
    eqslide('Time delay between continuous beams', 'A time delay of a continuous beam is a phase: 2CE does not see it, the 2PE fringes '
            'move with it.', [
        (D1, 'Δt = time delay of beam 2; φ = phase it adds; c = speed of light; λ = vacuum wavelength.'),
        (D2, '2CE multiplies intensities, which do not carry the phase.'),
        (D3, '2PE adds the fields, F_{2p} = κ_{2p}|U_1 + U_2 e^{iφ}|^4; K = fringe wavevector, |K| = 2k sin(θ/2): the time delay moves '
             'the fringes.')],
        'A time delay is a phase: 2CE does not see it, 2PE fringes move with it.',
        'For continuous beams a time delay is a constant phase on beam 2. The two-color signal uses only intensities. The two-photon '
        'signal contains the interference term, whose fringes shift with the phase.', '\n'.join((D1, D2, D3)), size=17)
    words('Choice of time delays: φ = 0, π/2, π', [
        'The effect of a time delay repeats with each optical period: φ = 2π is Δt = λ/c, 2.33 fs at 700 nm.',
        'φ and 2π − φ give the same loss, so φ from 0 to π covers all time delays.',
        'φ = 0 is the aligned case. φ = π/2 (Δt = 0.58 fs) moves the fringes by a quarter of their period. φ = π (Δt = 1.17 fs) '
        'moves them by half a period, so bright and dark fringes swap: the largest effect.',
        'φ = π is the time delay that matches the 2PE misalignment of 0.5 λ_{2p} used in scalar 2CE.'],
        'One optical period covers every time delay; pi is the largest effect.',
        'The time delays are chosen as fractions of the optical period, the time version of misalignments in fractions of a '
        'wavelength.')
    wide('Peak lost and fidelity against time delay', PD('phase_delay.png'), [
        'The 2CE peak and shape do not change with the time delay at either angle. For 2PE at θ = π/2 the peak drops to 71% at φ = π, '
        'as the centre falls on a dark fringe; at θ = π a bright fringe stays near the centre, so the peak stays but F drops '
        'to −0.85 as the standing wave moves.'],
        'A time delay leaves 2CE unchanged and changes 2PE through its fringes.',
        'Left: peak lost against phi; right: fidelity F against the aligned PSF. phi = pi is a time delay of 1.17 fs. The peak '
        'is found on a fine grid near the focus, so the moving fringes are resolved.')

    K1 = r'\mathbf{K} = k\left(\hat{\mathbf{k}}_1 - \hat{\mathbf{k}}_2\right), \qquad |\mathbf{K}| = 2k\sin(\theta/2)'
    K2 = r'\Delta s = \frac{\phi}{|\mathbf{K}|} = \frac{c\,\Delta t}{2n\sin(\theta/2)}'
    K3 = r'\theta = \pi:\ \Delta z = \frac{c\,\Delta t}{2n}, \qquad \theta = \pi/2:\ x_c = z_c = \frac{c\,\Delta t}{n}'
    eqslide('Time delay as a shift of the fringes', 'A time delay moves the 2PE fringes along K; at θ = π/2 it matches a '
            'misalignment of cΔt/n.', [
        (K1, 'k̂_1, k̂_2 = directions of the two beams; k = 2πn/λ; the 2PE fringes vary as cos(K·r − φ).'),
        (K2, 'Δs = shift of the fringes along K for a time delay Δt.'),
        (K3, 'the misalignment that gives the fringes the same phase as the time delay.')],
        'A time delay moves the 2PE fringes by c Delta t over 2n sin(theta/2).',
        'The fringe pattern of two plane waves has wavevector K, the difference of the two wavevectors. A phase phi moves it by '
        'phi over the magnitude of K.', '\n'.join((K1, K2, K3)), size=17)
    P1 = r'\phi_{eq} = \mathbf{K}\cdot\mathbf{r}_c + k\,\hat{\mathbf{k}}_2\cdot\mathbf{d}'
    P2 = r'\omega\,\Delta t = \phi_{eq}'
    eqslide('Misalignment in space as a phase', 'A misalignment changes the phase of the fringe at the peak; a time delay of the '
            'same phase cancels it.', [
        (P1, 'd = misalignment of O′; r_c = centre of the overlap of the two beams; k k̂_2·d = phase beam 2 gains by moving along '
             'its own direction; K·r_c = fringe phase where the beams now overlap.'),
        (P2, 'a time delay with this phase puts a bright fringe back on the peak.')],
        'A misalignment changes the fringe phase at the peak by phi_eq; a time delay can cancel it.',
        'The phase has two parts: beam 2 moving along its own direction, and the overlap of the two beams moving to another '
        'fringe. At theta = pi the two cancel for a misalignment along z.', '\n'.join((P1, P2)),
        side=('Cases', ['θ = π/2: x_c = 0.5 λ_{2p} or z_c = 0.5 λ_{2p} gives φ_{eq} = π.', '',
                        'θ = π, misalignment along z: the two terms cancel, φ_{eq} = 0, so the fringe at the centre stays bright '
                        'and the peak barely drops.']), size=18)
    wide('Time delay and misalignment, 2PE, θ = π/2', PD('time_vs_space.png'), [
        'Blue: a time delay Δt with the foci aligned. Red, green: a misalignment of the same fringe phase with no delay. One axis serves '
        'both, since a time delay of one period T shifts the fringes as much as a misalignment of one wavelength. Up to half a period '
        'the losses agree; beyond it the misalignment also separates the two foci, so its loss stays above that of the time delay.'],
        'A time delay and the matching misalignment cost the 2PE peak about the same up to half a period.',
        'The time-delay curve is symmetric about half a period and returns to zero after one, because a full period restores the '
        'fringes. Its sharp top is where the brightest fringe hands over from one side of the focus to the other.')
    words('Cancelling a misalignment with a time delay', [
        'At θ = π/2 a misalignment x_c = 0.5 λ_{2p} reduces the 2PE peak by 26%; with a time delay of φ = 0.92π the loss is 1.3%.',
        'A misalignment z_c = 0.5 λ_{2p} gives the same: 26% without the time delay and 1.3% with it.',
        'At x_c = 0.25 λ_{2p} the loss falls from 7% to 0.3% with φ = 0.46π.',
        'The best time delays are slightly below the predicted π and π/2, most likely from the Gouy phase of the focused beams, which '
        'the plane-wave form leaves out.',
        'What remains, about 1%, is the loss of overlap of the two foci: the part 2CE also has.'],
        'The 2PE loss of a misalignment is mainly phase, and a time delay removes most of it.',
        'Scalar model, NA 0.5. The time delay that best restores the peak is close to phi_eq.', size=12.5)

elif SECTION == 'polarization':
    title('Part 6: Polarization, s and p', 'Linear polarization of the two beams against unpolarized (circular) beams, vector 2CE')
    summary('At high NA, linear polarization (s: field perpendicular to the plane of the lens axes; p: field in it) changes the '
            '2CE results across the axis with facing lenses, and decides whether crossed-beam 2PE interferes; results along the '
            'axis do not change.',
            'At NA 0.9, θ = π, a misalignment of 0.37 λ_1 across the axis reduces the 2CE peak by about 51% for s–s, 42% '
            'unpolarized and 32% for p–p: the spot is wider along the polarization.',
            'For 2PE with crossed beams, p–p fields are perpendicular and barely interfere: a misalignment of 0.5 λ_{2p} costs a '
            'few percent of the peak up to NA 0.7, against 26–44% for s–s.',
            'Unpolarized beams give a round spot. Linear polarization makes the spot wider along the field, so results across the '
            'axis depend on the orientation of the misalignment. For 2PE the relative orientation of the two fields decides the '
            'interference.')
    geometry()
    words('Polarization: s and p', [
        'Light is a transverse wave: its electric field oscillates in a direction perpendicular to the direction the beam travels. '
        'That direction of oscillation is the polarization.',
        'A laser beam is usually linearly polarized: the field oscillates along one fixed direction.',
        'Circular polarization: the field direction rotates once per optical period, so on average no direction is preferred.',
        'Unpolarized light, or the average over two perpendicular linear polarizations, gives the same time-averaged intensity '
        'as circular polarization.',
        'In the paraxial scalar model of the paper the field has no direction at all, so polarization cannot enter.'],
        'Polarization is the direction in which the electric field oscillates.',
        'The scalar model has no direction for the field; the vector model does, so polarization enters at high NA.', size=13)
    side('s and p polarization', SL('polarization_sp_diagram.png'), [
        'The two lens axes lie in one plane, the x–z plane of the geometry.',
        's (German senkrecht, perpendicular): the field is perpendicular to that plane, along y, out of the page.',
        'p (parallel): the field lies in that plane, perpendicular to each beam: along x for beam 1, along z for beam 2.',
        's–s: both beams s; their fields are parallel for any θ.',
        'p–p: both beams p; with crossed beams (θ = π/2) their fields are perpendicular.'],
        's is perpendicular to the plane of the two lens axes, p lies in it.',
        'Diagram: crossed beams, beam 1 (red) travelling along z, beam 2 (blue) along x.', fw=4.6)
    eqslide('Polarization in the field equations', 'The input polarization sets the direction of the focused field; the '
            'unpolarized case averages two perpendicular directions.', [
        (r'\mathbf{E}_\psi = \cos\psi\,\mathbf{E}_{x} + \sin\psi\,\mathbf{E}_{y}',
         'E_x, E_y = Richards–Wolf focal fields for input polarized along x and along y of the beam’s own frame; ψ = input '
         'polarization angle: ψ = π/2 is s, ψ = 0 is p.'),
        (r'I_{\mathrm{unpol}} = \frac{1}{2}\left(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2\right)',
         'unpolarized: the average of the two, equal to circular polarization; the focal spot is round.'),
        (r'F_{2c} = \kappa_{2c}\, |\mathbf{E}_1|^2\, |\mathbf{E}_2|^2', '2CE uses the two intensities, so it depends on '
         'polarization only through the shape of each spot.'),
        (r'F_{2p} = \kappa_{2p}\, |\mathbf{E}_1 + \mathbf{E}_2|^4 \;\ni\; 2\,\mathrm{Re}\,(\mathbf{E}_1\cdot\mathbf{E}_2^{*})',
         '2PE interferes through E_1·E_2*: full interference for parallel fields (s–s), almost none for perpendicular fields '
         '(p–p at θ = π/2).')],
        'The input polarization angle psi enters the vector field; 2PE interference depends on E1 dot E2.',
        'Same Richards-Wolf fields as Parts 2-4, with a fixed input polarization instead of the average.',
        r"""\mathbf{E}_\psi = \cos\psi\,\mathbf{E}_x + \sin\psi\,\mathbf{E}_y
I_{unpol} = \tfrac{1}{2}(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2)
F_{2p} \ni 2\,\mathrm{Re}(\mathbf{E}_1\cdot\mathbf{E}_2^*)""", size=15)
    wide('Focal spot and polarization', SL('polarization_spot.png'), [
        'One beam at focus, across x. At NA 0.5 the two polarizations nearly coincide; at NA 0.9 the spot is about 1.35 times '
        'wider along the field than across it, because the focused field gains a component along z, strongest along the '
        'polarization.'],
        'At high NA the focal spot is wider along the polarization.',
        'Blue: field along y (s), so x is across the polarization. Red: field along x (p).')
    wide('20% tolerances and polarization, θ = π', SL('polarization_tolerance_pi.png'), [
        'Along the axis the three give the same tolerance. Across the axis, at NA 0.9, the tolerance is about 160 nm for s–s, '
        '180 nm unpolarized and 210 nm for p–p: wider along the polarization, as the spot is.'],
        'With facing lenses polarization changes the tolerance across the axis only.',
        'The 20 percent tolerances against NA for unpolarized, s–s and p–p beams.')
    wide('20% tolerances and polarization, θ = π/2', SL('polarization_tolerance_pi2.png'), [
        'With crossed beams the three nearly coincide in both directions: a misalignment in x_c is along the axis of beam 2, so '
        'it follows the length of the focus, which polarization barely changes (335, 328 and 346 nm at NA 0.9).'],
        'With crossed beams polarization barely changes the tolerances.',
        'Hatched: crossed lenses above NA 0.71.')
    wide('Peak lost and polarization', SL('polarization_peaklost.png'), [
        'Left: at NA 0.9, θ = π, a misalignment of 0.37 λ_1 across the axis costs about 51% (s–s), 42% (unpolarized) and 32% '
        '(p–p) of the 2CE peak. Right: for crossed-beam 2PE, p–p fields barely interfere, so a misalignment of 0.5 λ_{2p} costs '
        'a few percent up to NA 0.7, against 26–44% for s–s.'],
        'Polarization changes the losses across the axis, and for crossed-beam 2PE decides whether the beams interfere.',
        'Above NA 0.7 the p–p loss rises because the focused fields gain components that are no longer perpendicular.')
    words('Parts 2–4 with s and p polarization', [
        'Part 2, facing lenses: tolerances and losses across the axis move by up to about ±20% at NA 0.9; along the axis they do '
        'not change.',
        'Part 2, crossed lenses: 2CE tolerances change by a few percent at most.',
        '2PE with crossed beams: with p–p the fringes vanish, so the 2PE loss of a misalignment, and its link to a time delay '
        '(Part 5), largely disappear; s–s is the case the paper describes.',
        'Part 4, Gaussian input: the same pattern, smaller, since the Gaussian focus is closer to paraxial.'],
        'Linear polarization moves the results across the axis and removes crossed-beam 2PE interference for p–p.',
        'A summary of what would change in each earlier part if the beams were linearly polarized.', size=13)
    MOL = (r'\langle |\mathbf{E}_1\cdot\hat{\mathbf{d}}|^2\, |\mathbf{E}_2\cdot\hat{\mathbf{d}}|^2 \rangle = \frac{|\mathbf{E}_1|^2'
           r'|\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2^{*}|^2}{15}')
    eqslide('Orientation of the dye molecules', 'With linear polarization the orientation of each molecule’s transition '
            'dipole also enters the 2CE signal.', [
        (MOL, 'd̂ = direction of the molecule’s transition dipole; ⟨ ⟩ = average over randomly oriented molecules.'),
        (r'\text{parallel fields: } \tfrac{3}{15}\,|\mathbf{E}_1|^2|\mathbf{E}_2|^2, \qquad \text{perpendicular fields: } '
         r'\tfrac{1}{15}\,|\mathbf{E}_1|^2|\mathbf{E}_2|^2',
         'the signal is three times larger for parallel fields; the unpolarized product I_1 I_2 assumes this does not matter.')],
        'With linear polarization the molecular orientation factor enters the signal.',
        'For randomly oriented molecules the average of the two dipole projections gives this factor.', MOL, size=16)

elif SECTION == 'pulses':
    PS = SL
    title('Part 7: Optical pulses and time delay', 'Photon pairs from two Gaussian pulses, derived step by step; scalar 2CE at '
          'NA 0.5, 0.7 and 0.9 and vector 2CE at NA 0.7 and 0.9; τ = 10, 20 and 100 fs')
    summary('A time delay lowers 2CE because the photon pairs that reach the transition add out of phase where the two pulses do '
            'not arrive together: the signal is the pair probability times the overlap in time of the two pulses.',
            'With crossed lenses the PSF keeps its shape and its peak falls with the delay, by 20% at Δt = 0.4 τ; with facing lenses the delay moves the plane where the pulses meet, and with 10–20 fs pulses the PSF moves with it along the axis.',
            'Counting the pairs that reach the transition gives the same PSF shapes as the overlap in time; it changes the signal '
            'level, which at equal pulse energy no longer grows for shorter pulses.',
            'At the same NA, scalar and vector 2CE lose the same peak to a time delay, except with 10 fs pulses and facing lenses, '
            'where the longer paraxial focus follows the plane where the pulses meet further.',
            'Each pulse is a band of wavelengths. Two-color excitation takes one photon from each pulse, and the two frequencies '
            'must add up to the transition. Where the two pulses pass together these pairs add in phase; a time delay makes them '
            'add out of phase, which is the overlap in time. With crossed lenses the delay lowers the whole PSF; with facing '
            'lenses it moves the place where the pulses meet.')
    geometry(); scalar_fields()
    eqslide('Step 1: a pulse in time', 'A pulse is a fast oscillation (the carrier) inside a slowly varying envelope.', [
        (r'E(t) = A(t)\,\cos(\omega_0 t)', 'ω_0 = carrier frequency (2πc/750 nm, one oscillation every 2.5 fs); A(t) = '
                                           'envelope, which sets how long the pulse lasts.'),
        (r'I(t) = A(t)^2', 'intensity: what the molecule responds to, averaged over each fast oscillation.')],
        'A pulse is a carrier wave inside an envelope.',
        'The envelope is the slow shape; the carrier is the fast oscillation. Only the envelope matters for when the pulse is '
        'present.', r'E(t) = A(t)\cos(\omega_0 t), \qquad I(t) = A(t)^2', fig=PS('pulse_in_time.png'), size=18)
    eqslide('Step 2: a Gaussian envelope', 'We take the envelope to be a Gaussian in t; its intensity is then a Gaussian of '
            'full width at half maximum τ.', [
        (r'A(t) = \exp\left(-\frac{2\ln 2\; t^2}{\tau^2}\right)', 'Gaussian envelope, largest at t = 0.'),
        (r'I(t) = A(t)^2 = \exp\left(-\frac{4\ln 2\; t^2}{\tau^2}\right)', 'squaring doubles the exponent.'),
        (r'I\!\left(\tfrac{\tau}{2}\right) = \exp\left(-\frac{4\ln 2}{\tau^2}\cdot\frac{\tau^2}{4}\right) = e^{-\ln 2} = '
         r'\frac{1}{2}', 'at t = ±τ/2 the intensity is half its peak: τ is the full width at half maximum, the pulse duration.')],
        'The Gaussian envelope gives an intensity of FWHM tau.',
        'The constant 4 ln 2 is chosen so that tau is the full width at half maximum of the intensity.',
        r'A(t) = e^{-2\ln 2\, t^2/\tau^2}, \quad I(t) = e^{-4\ln 2\, t^2/\tau^2}, \quad I(\tau/2) = 1/2', size=18)
    eqslide('Step 3: a pulse is a sum of frequencies', 'A short pulse needs a range of frequencies; a Gaussian spread of '
            'frequencies adds up to a Gaussian pulse.', [
        (r'E(t) = \int a(\omega)\, e^{-i\omega t}\, d\omega', 'each frequency ω is a continuous wave; a(ω) = its amplitude.'),
        (r'a(\omega) = \exp\left(-\frac{(\omega-\omega_0)^2\,\tau^2}{8\ln 2}\right)', 'Gaussian spectrum centred on ω_0; its '
         'width is set by 1/τ.'),
        (r'\Delta\nu \approx \frac{0.441}{\tau}', 'spectral width (FWHM): about 22 THz at 20 fs, so a 750 nm pulse spans about '
                                                 '730–770 nm.')],
        'Adding many frequencies with a Gaussian spread gives a Gaussian pulse.',
        'With few frequencies the waves never cancel; with many they cancel everywhere except near t = 0, which is the pulse.',
        r'E(t) = \int a(\omega) e^{-i\omega t}\, d\omega, \quad a(\omega) = e^{-(\omega-\omega_0)^2\tau^2/8\ln 2}', size=17)
    wide('Step 3: adding frequencies, seen', PS('pulse_sum_of_frequencies.png'), [
        'Three frequencies added give a wave that never dies out. Nine give a pulse that repeats. Many frequencies with a '
        'Gaussian spread give one Gaussian pulse of duration τ = 20 fs.'],
        'Many frequencies make one pulse.', 'Same carrier, Gaussian weights, 3, 9 and 201 frequencies.')
    eqslide('Step 4: the pulse travels through the focus', 'Each frequency is focused by the lens; added together, the focused '
            'pulse moves through the focus at c/n.', [
        (r't_i(P) = \frac{n\, z_{b,i}}{c}', 'the time pulse i passes point P; z_{b,i} = distance of P along beam i from its '
                                            'focus (pulse i is at its focus at t = 0).'),
        (r'I_i(P, t) = I_i^{\mathrm{CW}}(P)\; \exp\left(-\frac{4\ln 2\,\left(t - t_i(P)\right)^2}{\tau^2}\right)',
         'the focused pulse: the continuous-beam intensity I^CW (the focal spot of the paper), switched on only while the '
         'pulse passes.'),
        (r't_2(P) = \frac{n\, z_{b,2}}{c} + \Delta t', 'beam 2 is sent a time Δt later: the time delay.')],
        'At each point the focused pulse is the continuous-beam spot, switched on while the pulse passes.',
        'This separates space and time: I^CW carries the shape of the focus, the Gaussian carries when the pulse is there. It '
        'neglects the small change of spot size across the spectrum.',
        r't_i = n z_{b,i}/c, \quad I_i(P,t) = I_i^{CW}(P)\, e^{-4\ln 2 (t-t_i)^2/\tau^2}, \quad t_2 = n z_{b,2}/c + \Delta t',
        size=16)
    wide('Step 5: photon pairs at the two-photon resonance', SL('pairs_overlap.png'), [
        '(a) Spectral probability density of each pulse at 20 fs. (b) Joint probability of the photon pairs at the two-photon '
        'resonance ν_a + ν_b = ν_e (λ_e = 350 nm), against the 750 nm photon (red axis) and its partner from the 656 nm laser '
        '(blue axis). Shorter pulses bring in more pairs; continuous beams have the single pair 750 + 656 nm.'],
        'The resonant photon pairs form a Gaussian that narrows as the pulses get longer.',
        'One photon from each pulse; the pair excites the dye when the two frequencies add up to the transition. Independent '
        'lasers, so the joint probability is the product of the two spectral probabilities. Derivation on the next slides.')
    R1 = r'h\nu_a + h\nu_b = h\nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{\lambda_e}'
    R2 = r'p_i(\nu) \propto \exp\left(-\frac{4\ln 2\,(\nu - \nu_i)^2}{\Delta\nu^2}\right), \qquad \Delta\nu = \frac{0.441}{\tau}'
    R3 = r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)'
    eqslide('Step 6: resonance and joint probability', 'A pair excites the 350 nm transition when its photon energies add up to '
            'the transition energy; photons of the two lasers are independent.', [
        (R1, 'two-photon resonance (energy conservation); ν = c/λ is the photon frequency.'),
        (R2, 'spectral probability density of laser i (i = 1: 750 nm, i = 2: 656 nm) for a τ-long Gaussian pulse (Step 3).'),
        (R3, 'joint probability of the resonant pair whose 750 nm photon has frequency ν_a: independent lasers, so the '
             'probabilities multiply.')],
        'Resonant pairs: energies add up to the transition; independent photons, so probabilities multiply.',
        'Which photon pairs reach the transition.', '\n'.join((R1, R2, R3)), size=16)
    S1 = r'\delta = \nu_e - (\nu_1 + \nu_2)'
    S2 = (r'(\nu_a - \nu_1)^2 + (\nu_a - \nu_1 - \delta)^2 = 2\left(\nu_a - \nu_1 - \tfrac{\delta}{2}\right)^2 '
          r'+ \tfrac{\delta^2}{2}')
    S3 = (r'P(\nu_a) \propto \exp\left(-\frac{8\ln 2\,(\nu_a - \nu_1 - \delta/2)^2}{\Delta\nu^2}\right)\, '
          r'\exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right)')
    eqslide('Step 7: complete the square', 'The product of two Gaussians is a Gaussian; δ measures how far the target sits from '
            'the design pair.', [
        (S1, 'detuning of the target ν_e from the design pair 750 + 656 nm; δ = 0 for λ_e = 350 nm.'),
        (S2, 'the two exponents of P(ν_a), with ν_e − ν_a − ν_2 = ν_1 + δ − ν_a, expanded and regrouped.'),
        (S3, 'a Gaussian in ν_a centred at ν_1 + δ/2, times a factor that depends only on δ.')],
        'The resonant pairs form a Gaussian.', 'Complete the square in nu_a.', '\n'.join((S1, S2, S3)), size=16)
    T1 = r'\mathrm{FWHM}_{\nu_a} = \frac{\Delta\nu}{\sqrt{2}}'
    T2 = (r'\int P(\nu_a)\, d\nu_a \;\propto\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) = '
          r'\exp\left(-\frac{4\ln 2\,\delta^2}{(\sqrt{2}\,\Delta\nu)^2}\right)')
    T3 = (r'\Delta\lambda_a \approx \frac{\lambda_1^2}{c}\,\frac{\Delta\nu}{\sqrt{2}} \approx \frac{585\ \mathrm{nm\,fs}}{\tau}, '
          r'\quad \Delta\lambda_b \approx \frac{448\ \mathrm{nm\,fs}}{\tau}, \quad '
          r'\Delta\lambda_e \approx \frac{255\ \mathrm{nm\,fs}}{\tau}')
    eqslide('Step 8: width and probability of the resonant pairs', 'The resonant pairs are √2 narrower than either pulse; the probability of '
            'reaching ν_e is a Gaussian √2 wider.', [
        (T1, 'spread of the 750 nm photons in resonant pairs, and of their partners: the exponent 8 ln2/Δν² of Step 7.'),
        (T2, 'probability that a pair reaches ν_e, summed over all pairs: a Gaussian in δ of FWHM √2 Δν, the spread of pair '
             'frequencies.'),
        (T3, 'in wavelength (|dλ| = λ²dν/c): 29, 22 and 13 nm at 20 fs; 6, 4.5 and 2.5 nm at 100 fs. τ → ∞ gives the single '
             'pair 750 + 656 nm.')],
        'Which pairs, and how many, in closed form.', 'Width of the resonant pairs and of the pair frequencies.',
        '\n'.join((T1, T2, T3)), size=15)
    eqslide('Step 9: the two pulses must overlap in time', 'A pair needs one photon from each pulse at the molecule at the same '
            'time; the overlap in time of the two intensities measures how much the pulses coincide.', [
        (r'O(P, \Delta t) = \int_{-\infty}^{\infty} I_1(P, t)\, I_2(P, t)\, dt', 'overlap in time at point P; with continuous '
         'beams the integrand is constant in time and O is the I_1 I_2 of the paper.'),
        (r'= I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \int e^{-a (t-t_1)^2}\, e^{-a (t-t_2)^2}\, dt, \qquad '
         r'a = \frac{4\ln 2}{\tau^2}', 'substituting Step 4: the spatial part comes out of the integral.')],
        'The overlap in time of the two pulses at each point.',
        'Only the time integral of two Gaussians is left to do.',
        r'O = \int I_1 I_2\, dt = I_1^{CW} I_2^{CW} \int e^{-a(t-t_1)^2} e^{-a(t-t_2)^2} dt', size=17)
    eqslide('Step 10: the Gaussian integral, line by line', 'Complete the square in t; one Gaussian integral is left.', [
        (r'(t-t_1)^2 + (t-t_2)^2 = 2\left(t - \bar{t}\right)^2 + \frac{(t_1 - t_2)^2}{2}, \qquad \bar{t} = \frac{t_1+t_2}{2}',
         'expand both squares and regroup: the cross terms collect into the second term.'),
        (r'\int e^{-a(t-t_1)^2} e^{-a(t-t_2)^2} dt = e^{-a (t_1-t_2)^2/2} \int e^{-2a (t-\bar{t})^2} dt',
         'the second term does not depend on t, so it leaves the integral.'),
        (r'\int_{-\infty}^{\infty} e^{-2a u^2} du = \sqrt{\frac{\pi}{2a}}', 'standard Gaussian integral, u = t − t̄: a '
         'constant, the same at every point.'),
        (r'\Rightarrow\; O \;\propto\; I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)',
         'with a = 4 ln2/τ², a/2 = 2 ln2/τ².')],
        'The time integral of two Gaussians is a Gaussian in the difference of their arrival times.',
        'Completing the square separates a part that depends on t from one that depends only on t1 − t2.',
        r'(t-t_1)^2+(t-t_2)^2 = 2(t-\bar t)^2 + (t_1-t_2)^2/2; \int e^{-2au^2}du = \sqrt{\pi/2a}', size=15)
    PA = r'A(P) = \int \sqrt{P(\nu_a)}\; U_1(P, \nu_a)\, U_2(P, \nu_e - \nu_a)\, d\nu_a, \qquad F_{2c}(P) = \kappa_{2c}\, |A(P)|^2'
    PU = r'U_i(P, \nu) \approx U_i^{\mathrm{CW}}(P)\, e^{\,i 2\pi \nu\, t_i(P)}'
    PH = r'2\pi\nu_a t_1 + 2\pi(\nu_e - \nu_a)\, t_2 = 2\pi\nu_e t_2 + 2\pi\nu_1 (t_1 - t_2) + 2\pi(\nu_a - \nu_1)(t_1 - t_2)'
    eqslide('Step 11: phase of the resonant pairs', 'The two-photon amplitude adds all resonant pairs; '
            'each pair carries the phase of the times at which the two pulses pass the point.', [
        (PA, 'A = two-photon amplitude; √P = amplitude of the pair whose 750 nm photon has frequency ν_a (its square is the joint '
             'probability of Step 6); U_i(P, ν) = focal field of beam i at frequency ν. The signal is the square of the sum.'),
        (PU, 'each frequency passes P with its pulse, at t_i = n z_{b,i}/c (Step 4); t_2 includes the delay Δt.'),
        (PH, 'phase of a pair: the first two terms are the same for all pairs; the last differs between pairs unless t_1 = t_2.')],
        'The pairs add with the phase of the arrival times; they add fully where the pulses arrive together.',
        'Where the two pulses pass at the same time, all pairs have the same phase and add up. Where they pass at different times, '
        'the phase changes across the spread of pairs, and the pairs partly cancel.', '\n'.join((PA, PU, PH)), size=15)
    G1 = (r'\sqrt{P(\nu_a)} \propto \exp\left(-\frac{4\ln 2\,(\nu_a - \nu_1 - \delta/2)^2}{\Delta\nu^2}\right) '
          r'\exp\left(-\frac{\ln 2\,\delta^2}{\Delta\nu^2}\right)')
    G2 = (r'-a x^2 + i k x = -a\left(x - \frac{ik}{2a}\right)^2 - \frac{k^2}{4a} \;\Rightarrow\; '
          r'\int e^{-a x^2 + ikx}\, dx = \sqrt{\frac{\pi}{a}}\; e^{-k^2/4a}')
    G3 = (r'a = \frac{4\ln 2}{\Delta\nu^2},\ \ k = 2\pi (t_1 - t_2),\ \ \Delta\nu = \frac{2\ln 2}{\pi\tau}:\quad '
          r'\frac{k^2}{4a} = \frac{\ln 2\,(t_1 - t_2)^2}{\tau^2}')
    eqslide('Step 12: the sum over pairs, line by line', 'With Gaussian pulses the sum over pairs is a Gaussian integral with a '
            'phase; it gives a Gaussian in the difference of the arrival times.', [
        (G1, 'square root of the joint probability of Step 7; x = ν_a − ν_1 − δ/2 is the variable of the sum.'),
        (G2, 'complete the square in x; the shifted Gaussian integrates to √(π/a), as in Step 10.'),
        (G3, 'Δν = 0.441/τ = 2 ln2/(πτ) (Step 3). So |A| falls as exp(−ln2 (t_1 − t_2)²/τ²), and |A|² as '
             'exp(−2 ln2 (t_1 − t_2)²/τ²): the overlap in time of Step 10.')],
        'The sum over pairs gives the same Gaussian in the arrival times as the overlap in time.',
        'The Fourier transform of a Gaussian is a Gaussian. The square of the amplitude has the exponent of Step 10.',
        '\n'.join((G1, G2, G3)), size=15)
    CF = (r'F_{2c}(P, \Delta t) \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) '
          r'\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)')
    T12 = r't_1 - t_2 = \frac{n\,(z_{b,1} - z_{b,2})}{c} - \Delta t'
    eqslide('Step 13: closed form of the pulsed 2CE PSF', 'The pulsed PSF is the continuous-beam PSF of the paper, times the '
            'probability that a pair reaches the transition, times the overlap in time.', [
        (CF, 'I^CW_1 I^CW_2 = the 2CE PSF of the paper; first exponential = probability that a pair reaches ν_e (Step 8), the '
             'same at all points; second = overlap in time (Steps 10 and 12).'),
        (T12, 'difference of the arrival times at P (Step 4): it sets where the pulses meet.'),
        (r'\tau \to \infty:\quad F_{2c} \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}', 'long pulses recover the '
         'continuous-beam result of the paper.')],
        'Pulsed PSF = continuous-beam PSF times pair probability times overlap in time.', 'Steps 8, 10 and 12 combined.',
        '\n'.join((CF, T12)), size=15)
    eqslide('Step 14: meeting plane of the two pulses', 'The overlap depends on z_{b,1} − z_{b,2}, which differs for facing and crossed '
            'lenses.', [
        (r'\theta = \pi:\ z_{b,1} = z,\ z_{b,2} = -z \;\Rightarrow\; \text{overlap peaks at } z = \frac{c\,\Delta t}{2n},\ '
         r'\mathrm{FWHM} = \frac{c\sqrt{2}\,\tau}{2n}',
         'facing pulses meet on a thin slab that a time delay slides along the axis: 4.2 µm long at 20 fs, 2.1 µm at 10 fs. '
         'Near the focus the pulse moves faster than c/n, so the slab sits about 6% further at NA 0.5 and 30% at NA 0.9; '
         'the full calculation includes this.'),
        (r'\theta = \pi/2:\ z_{b,1} = z,\ z_{b,2} = x \;\Rightarrow\; \exp\left(-\frac{2\ln 2}{\tau^2}'
         r'\left(\frac{n(z - x)}{c} - \Delta t\right)^2\right)',
         'crossed pulses meet along a diagonal band, much wider than the crossed spot.'),
        (r'\text{at the focus: } \exp\left(-2\ln 2\,(\Delta t/\tau)^2\right) = 0.71,\ 0.25\ \text{at}\ \Delta t = \tau/2,\ \tau',
         'how much a time delay lowers the PSF where the band is wider than the spot.')],
        'Facing pulses meet on a thin moving slab; crossed pulses on a wide band.', 'The overlap for each geometry. The arrival '
        'times n z/c hold away from the focus. Near the focus the pulse is a sum of plane waves tilted up to the cone angle, '
        'and the point where each crosses the axis moves at c/(n cos beta), faster than c/n: the pulse arrives at 0.94 z n/c '
        'at NA 0.5, 0.87 at NA 0.7 and 0.76 at NA 0.9 (vector). The plane where facing pulses meet is then at about '
        'c Delta t/(2n) divided by these factors. The pair calculation includes this through the phase of each frequency.',
        r'\theta=\pi: z = c\Delta t/2n,\ \mathrm{FWHM} = c\sqrt{2}\tau/2n', size=14)
    wide('Step 14: facing pulses meet, seen', PS('pulse_facing_meet.png'), [
        'Pulse 1 (red) travels toward +z and pulse 2 (blue) toward −z. Both are present at the same place only near z = 0, '
        'around t = 0 (green): that is where 2CE happens.'],
        'Facing pulses overlap only where they meet.', 'τ = 20 fs, no time delay.')
    wide('Step 14: the overlap against the time delay', PS('pulse_overlap.png'), [
        'Left: crossed beams, the overlap at the focus falls as exp(−2 ln2 (Δt/τ)²). Right: facing beams, a time delay slides '
        'the meeting slab along the axis by cΔt/2n.'],
        'A time delay lowers the crossed overlap and moves the facing slab.', 'From Step 14.')
    wide('Wavelengths per pulse', PS('pairs_convergence.png'), [
        'Largest change of the 2CE PSF against the number of wavelengths per pulse N, compared with N = 257, over the window, '
        'with O′ at the extreme offsets and Δt up to ±2τ. From N = 17 the change is below 2×10⁻⁵ of the peak; the runs use '
        'N = 25, where it is below 10⁻⁶.'],
        'Twenty-five wavelengths per pulse: more wavelengths change the PSF by less than one part in a million.',
        'Each pair adds with the phase of its arrival time, so the wavelengths must be sampled finely enough to resolve the '
        'largest difference of arrival times on the grid: facing lenses, the far end of the window, O prime offset by 4.8 '
        'micrometres and a delay of two pulse durations. Checked for scalar 2CE at NA 0.5 for all pulse durations and both '
        'geometries, and for vector 2CE at NA 0.9 in the 10 fs facing case. Scalar 2CE at 10 fs with facing lenses needs the most '
        'wavelengths; the vector focus at NA 0.9 is dimmer far from the focus and needs fewer.')
    words('Check: closed form against the full calculation', [
        'The full calculation focuses 25 wavelengths of each pulse separately and adds all resonant pairs with their phases '
        '(Step 11), with no envelope approximation.',
        'Largest difference over the window, relative to the aligned peak, at Δt = 0, τ/2 and τ: crossed lenses 0.6% or less at 10, 20 and 100 fs; facing lenses 0.4% at 100 fs, 1.9% at 20 fs and 3.9% at 10 fs. The difference is the change of spot size across the spectrum, which the closed form leaves out.'],
        'The closed form matches the full sum over pairs.', 'Scalar 2CE, NA 0.5.', size=13)
    eqslide('2PE with pulses', '2PE adds the two fields, so with pulses it has two kinds of terms: each beam alone, and the '
            'interference of the two.', [
        (r'F_{2p}(P, \Delta t) = \kappa_{2p} \int \left|E_1(P,t) + E_2(P,t)\right|^4 dt', 'both beams at 700 nm; E_2 is '
                                                                                         'delayed by Δt.'),
        (r'\ni\ \int \left(I_1^2 + I_2^2\right) dt', 'each pulse alone excites 2PE, whether or not the pulses overlap.'),
        (r'\Delta t \gg \tau:\quad \frac{F_{2p}}{F_{2p}(\Delta t = 0)} \to \frac{1^2 + 1^2}{2^4} = \frac{1}{8}',
         'at the aligned peak the two fields add to twice one field, so 2PE never falls below 1/8 of its peak.')],
        '2PE keeps a floor of 1/8 because each beam alone excites it.',
        'The interference terms need the pulses to overlap; the single-beam terms do not. 2PE is computed with the overlap in '
        'time of the fields.', r'F_{2p} = \kappa_{2p}\int |E_1+E_2|^4 dt \ni \int (I_1^2 + I_2^2) dt', size=17)
    TXT = {('2ce', 'pi'): 'With facing lenses the 2CE PSF shrinks along z as the pulses get shorter: at 10 fs the slab where the pulses meet (2.1 µm) is shorter than the focus.',
           ('2ce', 'pi2'): 'With crossed lenses the 2CE PSF does not change with the pulse duration: the band where the pulses meet is wider than the spot.',
           ('2pe', 'pi'): 'With facing lenses the 2PE standing wave is confined to where the pulses meet.',
           ('2pe', 'pi2'): 'With crossed lenses the 2PE PSF keeps its fringes; pulses barely change it.'}
    for key, no, what in (('psf2', 2, 'aligned'), ('psf3', 3, 'O′ at (0.4, 1.0) µm')):
        for pair, lab2 in (('2ce', '2CE'), ('2pe', '2PE')):
            for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
                wide(f'Pulsed Fig. {no}: {lab2}, {lab}', PS(f'pulse_{key}_{pair}_{th}.png'), [TXT[(pair, th)]],
                     f'Pulsed Fig. {no}, {lab2}, {lab}.', f'Scalar model, NA 0.5, {what}, no time delay; continuous beams (CW) '
                     'and tau = 100, 20, 10 fs. Contours at 1, 10, 20, 40, 60 and 80 percent of the peak; orange: 50 percent. 2CE from the resonant '
                     'pairs, 2PE from the overlap in time.')
    for pair, lab2 in (('2ce', '2CE'), ('2pe', '2PE')):
        for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
            wide(f'Pulsed Fig. 4: {lab2}, {lab}', PS(f'pulse_peakmap_{pair}_{th}.png'), [
                'With no time delay the peak against the misalignment of O′ changes little with the pulse duration: each pulse '
                'is timed to reach its own focus, so the pulses meet midway between the two foci.'],
                f'Pulsed Fig. 4, {lab2}, {lab}.', 'Scalar model, NA 0.5, tau = 100, 20, 10 fs.')
    words('Misalignment in time and in space', [
        'In space (the paper): O′ moves away from O, so the two focal spots no longer coincide. The 2CE PSF is their product, so '
        'its peak drops and moves; the tolerance is set by the size of the focal spot.',
        'In time: pulse 2 arrives Δt late. The two focal spots still coincide, but at the focus the pulses pass at different '
        'times, so the resonant pairs add out of phase (Steps 11–12) and the signal there drops as exp(−2 ln2 Δt²/τ²). The '
        'tolerance is set by the pulse duration τ.',
        'The pairs still add in phase where the pulses meet: on the plane z = cΔt/2n for facing lenses, and along the line '
        'z − x = cΔt/n for crossed lenses (Step 14).',
        'Crossed lenses: the pulses meet along a band wider than the focal spot, so the PSF keeps its shape and its peak drops by the factor at the focus.',
        'Facing lenses: the plane where the pulses meet moves along the axis by cΔt/2n. With 100 fs pulses the slab (21 µm) is longer than the focus and the PSF behaves as with crossed lenses; with 10–20 fs pulses the slab (2–4 µm) is about as long as the focus, so the PSF moves along the axis toward it, much like an axial misalignment, and its peak drops less.'],
        'A time delay moves where the pulses meet; a misalignment in space moves where the spots meet.',
        'The paper misaligns the foci in space. Here the foci stay aligned and the pulses are misaligned in time. Each causes a '
        'loss of peak and a change of shape, for different reasons and with different scales.', size=12.5)
    PSFTXT = {10: 'With 10 fs pulses the slab where the pulses meet (2.1 µm) is shorter than the focus, so the PSF follows it (blue): at Δt = τ the peak moves 1.15 µm along the axis and keeps 68% of its value, much like an axial misalignment.', 20: 'With 20 fs pulses the slab (4.2 µm) is about as long as the focus: at Δt = τ/2 the PSF moves 0.6 µm toward the plane where the pulses meet (blue) and keeps 81% of its peak; at Δt = τ it moves 1.25 µm and keeps 43%.', 100: 'With 100 fs pulses the slab (21 µm) is much longer than the focus: the PSF stays nearly in place (0.4 µm at Δt = τ) and its peak falls as at the focus, to 71% at τ/2 and 26% at τ.'}
    for tau in (10, 20, 100):
        wide(f'PSF against the time delay: θ = π, τ = {tau} fs', PS(f'pairs_time_psf_pi_tau{tau}.png'), [PSFTXT[tau]],
             f'Facing lenses, {tau} fs.', 'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Contours at 1, 10, 20, 40, 60 and 80 percent of '
             'the peak at zero delay; orange: 50 percent; blue dashed: the plane where the pulses meet, z = c Delta t / 2n.')
    wide('PSF against the time delay: θ = π/2, τ = 10 fs', PS('pairs_time_psf_pi2_tau10.png'), ['With crossed lenses the pulses meet along a band wider than the spot, so even at 10 fs the PSF keeps its shape and its peak falls as at the focus: 72% at τ/2 and 27% at τ.'],
         'Crossed lenses, 10 fs.', 'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Contours at 1, 10, 20, 40, 60 and 80 percent of the '
         'peak at zero delay; orange: 50 percent.')
    wide('Peak against the time delay', PS('pairs_time_peak.png'), ['Crossed lenses: the peak follows the overlap at the focus, exp(−2 ln2 Δt²/τ²), at 10, 20 and 100 fs. Facing lenses: with 10 and 20 fs pulses the peak falls more slowly, because the PSF moves with the slab where the pulses meet.'],
         'The peak against the time delay, as Fig. 4 of the paper against the misalignment.',
         'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Orange: the overlap at the focus, exp(-2 ln2 Delta t^2 / tau^2).')
    LINTXT = {'pi': 'Facing lenses: as the PSF moves along the axis, F and Q fall, more for shorter pulses; at Δt = τ, F is 0.23 at 10 fs, 0.55 at 20 fs and 0.97 at 100 fs. C stays near 1 because the moved PSF keeps nearly the same size.', 'pi2': 'Crossed lenses: F, C and Q stay above 0.93 up to Δt = τ at 10, 20 and 100 fs: the delay lowers the PSF without changing its shape.'}
    for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
        wide(f'Linfoot’s criteria against the time delay: {lab}', PS(f'pairs_time_linfoot_{th}.png'), [LINTXT[th]],
             f'Linfoot’s criteria against the time delay, {lab}.', 'Scalar 2CE, NA 0.5, resonant pairs. F, C and Q compare the '
             'delayed PSF with the aligned one, each scaled to its own peak, as in Figs. 5 and 6 of the paper.')
    wide('20% tolerance in time', PS('pairs_time_tolerance.png'), ['With crossed lenses a time delay of 0.40 τ reduces the 2CE peak by 20% at all NA, scalar and vector alike. With facing lenses and 10 fs pulses the tolerance is 0.76 τ at NA 0.5 and falls toward 0.40 τ as NA grows (0.43 τ at NA 0.9): a longer focus lets the PSF follow the plane where the pulses meet.'],
         'The time delay that costs 20% of the 2CE peak.', 'Scalar 2CE (dashed) and vector 2CE (solid); NA by colour. Orange '
         'dotted: 0.40 tau, the value at the focus.')
    wide('Scalar 2CE against vector 2CE at the same NA: θ = π', PS('pairs_time_samena.png'), ['At the same NA, scalar and vector 2CE lose the same peak with 100 fs pulses. With 10 fs pulses the scalar PSF keeps slightly more of its peak (42% against 38% at Δt = τ, NA 0.7) and changes shape more, because the paraxial focus is longer along the axis than the vector one and follows the plane where the pulses meet further.'],
         'Scalar and vector 2CE against the time delay at the same NA.', 'Facing lenses, NA 0.7 and 0.9, tau = 10, 20, 100 fs. '
         'Black: scalar 2CE, the paraxial model; red: vector 2CE, the Richards–Wolf focus, unpolarized. With crossed lenses the '
         'two agree (previous slide).')
    wide('Time delay and axial misalignment: θ = π', PS('pairs_time_z.png'), ['Peak against the axial misalignment z_c and the time delay, facing lenses. For each z_c the best time delay recovers less than 0.5% of the peak: each pulse is timed to its own focus, so the pulses meet between the two foci, and a delay moves them away from there.'],
         'A time delay and an axial misalignment together.', 'Scalar 2CE, NA 0.5, resonant pairs. Contours in percent of the '
         'aligned peak; orange: 50 percent.')
    wide('Peak against the time delay: 2PE', PS('pulse_delay_peak_2pe.png'), [
        'The 2PE peak falls with the time delay but levels off at 1/8 (dotted), where each pulse alone excites 2PE and the '
        'interference is lost.'],
        '2PE keeps a floor of 1/8 when the pulses no longer overlap.', 'Scalar model, NA 0.5, overlap in time of the fields.')
    wide('Resonant pairs against all pairs', PS('pairs_vs_every_pair.png'), ['Aligned 2CE peak at equal pulse energies. Counting all pairs (the overlap in time) the signal grows as 1/τ, 10 times larger at 10 fs than at 100 fs. Counting the pairs that reach ν_e it stays the same, because a shorter pulse spreads its pairs over more transition frequencies. The PSF shapes and time-delay curves of the two agree within 0.3%.'],
         'The resonant pairs change the signal level, not the PSF shape.',
         'Aligned peak at the focus against the pulse duration, at equal pulse energies, scalar 2CE at NA 0.5.')
    RATE = r'\text{rate} \propto \int g(\Omega)\, \bigl|\tilde{P}(\Omega)\bigr|^2 d\Omega, \qquad P(t) = E_1(t)\, E_2(t)'
    eqslide('Weighting the pairs by the dye', 'The dye’s absorption g weights each pair by its total frequency: a narrow band '
            'keeps the resonant pairs, a flat band counts all pairs.', [
        (RATE, 'Ω = ω_1 + ω_2 = total frequency of a pair; g(Ω) = absorption of the dye; P̃ = spectrum of the product field.'),
        (r'g = \text{const.}: \quad \int g\,|\tilde{P}|^2 d\Omega \;\propto\; \int I_1(t)\, I_2(t)\, dt',
         'Parseval: a flat absorption gives the overlap in time of Step 9 for all pairs (checked numerically).'),
        (r'g = \delta(\Omega - \Omega_e): \quad \text{rate} \propto |\tilde{P}(\Omega_e)|^2 = |A|^2',
         'a narrow band gives the resonant pairs of Steps 11–13; for equal Gaussian pulses both give the same PSF shapes.')],
        'Weighting by the dye changes how much signal there is, not the shape of the PSF.', 'The weighted rate.', RATE, size=14)
    wide('Signal kept by the dye weighting', SL('pulse_pairs_weight.png'), [
        'Shorter pulses spread the photon pairs over more wavelengths, so a dye that absorbs only near 350 nm uses fewer of '
        'them: with a 10 nm band, about 97% is kept at 100 fs, 60% at 20 fs and 35% at 10 fs.'],
        'Short pulses waste pairs outside the dye band.', 'Gaussian absorption bands of FWHM 2, 5, 10 and 20 nm at 350 nm.')
    words('Conclusions: optical pulses', ['With pulses, 2CE counts the photon pairs whose frequencies add up to the transition. For Gaussian pulses the PSF is the continuous-beam PSF times the probability that a pair reaches the transition, times the overlap in time of the two pulses.', 'A time delay makes the resonant pairs add out of phase where the two pulses do not arrive together. At the focus the signal falls as exp(−2 ln2 Δt²/τ²), so 20% is lost at Δt = 0.40 τ.', 'Crossed lenses: the PSF keeps its shape and its peak falls by that factor. Facing lenses: the delay moves the plane where the pulses meet; with 10–20 fs pulses the PSF moves with it along the axis, much like an axial misalignment, and loses less peak.', 'Counting the resonant pairs instead of all pairs leaves the PSF shapes and time-delay curves unchanged (within 0.3%) and changes the signal level: at equal pulse energy, shorter pulses give no more signal.', 'At the same NA, scalar and vector 2CE lose the same peak to a time delay with crossed lenses and with 100 fs pulses. With 10 fs pulses and facing lenses the scalar PSF keeps slightly more peak, because the paraxial focus is longer along the axis.', 'A time delay does not recover the loss from an axial misalignment. Open: the dye’s absorption band decides between the resonant pairs and all pairs.'],
          'Pulsed 2CE = continuous-beam PSF times pair probability times overlap in time.', 'Summary of the pulsed study.',
          size=12.5)

elif SECTION == MEETING:
    title('Two-color excitation: progress report', '')
    words('Summary', [
        'Extended the 2CE misalignment study to high NA (vector focus), water, Gaussian input and optical pulses.',
        '– Offset for 20% loss: ∝ 1/NA across the axis, 1/NA^2 along it (width and length of the focus). Paraxial model within '
        '5% up to NA 0.45; along the axis off by tan^2(α/2).',
        '– Air and water: same power laws; focus 1.4× longer in water at the same NA. Crossed lenses fit to NA 0.71 in air, '
        '0.94 in water.',
        '– Fidelity: at high NA, F high over a smaller range of misalignments; vector and scalar differ more at NA 0.9.',
        '– Gaussian input: wider, longer focus; offsets 1.4× larger, same power laws.',
        '– Continuous beams: a time delay is a phase; shifts the 2PE fringes, no change in 2CE.',
        '– Optical pulses: 2CE counts photon pairs with ν_a + ν_b = ν_e, one photon from each pulse; shorter pulses, more pairs.'],
        'Extended the misalignment study to high NA, water, Gaussian input and pulses.', 'One line per section.', size=15)
    geometry()
    def section(k, name, line):
        navy(f'{k}. {name}', [(line, 15, PALE)])

    section(1, 'Offset for 20% loss against NA', 'Extended to high NA, vector focus.')
    lens_problem()
    scalar_fields()
    eqslide('Field equations: vector 2CE (Richards–Wolf)', 'Exact phase of each ray and all three field components.', [
        (EVEC, 'E = focal field for input polarized along x; φ = angle about the axis; unpolarized = mean of x and y input.'),
        (IM, 'β = ray angle; r, z = distance from the focus; A(β) = pupil amplitude (1 uniform, Gaussian for α_t = 4); '
             '√cos β = aplanatic factor; k = 2πn/λ.'),
        (GM, 'α = half-angle of the focusing cone; m = 0, 1, 2.')],
        'The vector Richards–Wolf field.', 'At low NA it reduces to the paraxial scalar field.', '\n'.join((EVEC, IM, GM)), size=15)
    words('Scalar and vector focal fields at the same NA', [
        'Scalar (paraxial): small-angle phase k n z sin²θ/2; no polarization.',
        'Vector (Richards–Wolf): exact phase k n z cos θ; field components E_x, E_y, E_z; pupil weight √cos θ.',
        'Across the axis: same width, ≈ λ/NA; polarization widens the vector spot slightly along the field.',
        'Along the axis: paraxial focus longer by 2/(1 + cos α): 7% at NA 0.5, 39% at NA 0.9 (air).'],
        'Same NA: same width; the paraxial focus is longer along the axis.', 'Scalar against vector focal fields.', size=14)
    wide('Focal field along the axis at NA 0.8, θ = π', SL('profiles_pi_na0.8.png'), [
        'Aligned 2CE spot, three focal fields. Across: all agree. Along: paraxial longer.',
        'Scalar with the exact phase = vector: the small-angle phase causes the difference.'],
        'The small-angle phase, not polarization, lengthens the paraxial focus.',
        'Paraxial scalar, scalar Debye with the exact phase, and vector.')
    wide('Offset for 20% loss against NA, θ = π', SL('tolerance_media_pi.png'), [
        'T: offset of O′ for 20% loss of the 2CE peak. Lines: power law, fit NA 0.1–0.5.',
        'Insets: scalar = vector at low NA; scalar above vector at high NA, along z first.'],
        'The offsets follow power laws in NA set by the width and length of the focus.',
        'Blue: vector; red: paraxial scalar; filled: air; open: water. Star: value of the paper at NA 0.5. Air ends at NA 1.')
    wide('Offset for 20% loss against NA, θ = π/2', SL('tolerance_media_pi2.png'), [
        'Crossed lenses: both ∝ 1/NA^2, both misalignments along the length of a beam.', 'Air to NA 0.71 (lenses fit); water to 0.94.'],
        'Crossed lenses: both offsets follow the length of the focus.',
        'Blue: vector; red: paraxial scalar; filled: air, up to NA 0.71; open: water.')
    SA1 = r'\text{exact: } k n z\,(1 - \cos\theta), \quad \text{paraxial: } k n z\,\frac{\sin^2\theta}{2}'
    SA2 = r'\frac{\text{paraxial length}}{\text{exact length}} = \frac{2}{1 + \cos\alpha}'
    SA3 = r'\frac{|T_{\mathrm{scalar}} - T_{\mathrm{vector}}|}{T_{\mathrm{vector}}} \approx \tan^2\frac{\alpha}{2}, \quad \sin\alpha = \frac{\mathrm{NA}}{n}'
    s = slide('Scalar 2CE against vector 2CE', '')
    figure(s, SL('deviation_media.png'), 0.4, 0.95, 5.6, 4.3)
    t = 1.05
    for tex, wh in ((SA1, 'axial phase of a ray at angle θ'), (SA2, 'small-angle phase: focus too long'),
                    (SA3, 'black curves; α = half-angle of the cone')):
        t += equation(s, 6.15, t, 3.4, tex, 13) + 0.02
        t += where(s, 6.2, t, 3.3, wh) + 0.12
    bullets(s, 6.15, t + 0.05, 3.4, 1.2, ['T: offset for 20% loss. At NA 0.5: 7% in air, 4% in water along z.'], 11)
    notes(s, 'The along-axis difference is tan^2(alpha/2), from the small-angle phase.',
          'Same sinc^2 along the axis, stretched by 2/(1 + cos alpha); no free parameter.', '\n'.join((SA1, SA2, SA3)))

    section(2, 'Air and water at the same NA', 'Same power laws; longer focus in water at the same NA.')
    wide('Offset for 20% loss in air and water, θ = π', SL('air_water_pi.png'), [
        'Same NA: across, equal in air and water; along, 1.4× larger in water.', 'Same power laws (fit NA 0.1–0.7).'],
        'Water keeps the power laws and enlarges the offset along the axis.', 'Filled: air; open: water.')
    wide('Offset for 20% loss in air and water, θ = π/2', SL('air_water_pi2.png'), [
        'Crossed lenses: both 1.4× larger in water at the same NA.', 'Same power laws, ∝ 1/NA^2 (fit NA 0.1–0.7).'],
        'Crossed lenses: water keeps the power laws.', 'Filled: air, up to NA 0.71; open: water.')

    section(3, 'Fidelity against NA', 'Linfoot fidelity F of the misaligned 2CE PSF, vector and scalar.')
    wide('Fidelity: 2CE, θ = π', SL('linfoot3d_F_2ce_pi_grid.png'), [
        'F: similarity of misaligned and aligned PSF (1 = identical). Top: vector; bottom: scalar; NA 0.5, 0.7, 0.9.',
        'Vector: high-F region shrinks along z_c as NA grows.'],
        'At high NA the PSF keeps its shape over a smaller range of misalignments.', 'Axes in lambda_1.')
    wide('Fidelity, vector − scalar at the same NA: 2CE, θ = π', SL('linfoot_diff3_F_2ce_pi.png'), [
        'ΔF = F_{vector} − F_{scalar}, same NA: 0.5, 0.7, 0.9. Red: vector higher; blue: lower.', 'Grows with NA.'],
        'At the same NA the vector and scalar fidelity differ, more at NA 0.9.', 'Same NA, same axes.')

    section(4, 'Gaussian input', 'Gaussian input (α_t = 4) against uniform input.')
    wide('Offset for 20% loss, Gaussian input, θ = π', SL('tolerance_media_pi_at4.png'), [
        'Dim pupil edge → wider, longer focus; offsets 1.4× larger than with uniform input.', 'Same power laws in air and water.'],
        'A Gaussian input gives 1.4 times larger offsets.', 'Blue: vector; red: scalar; filled: air; open: water.')
    wide('Offset for 20% loss, Gaussian input, θ = π/2', SL('tolerance_media_pi2_at4.png'), [
        'Crossed lenses: both ∝ 1/NA^2, as with uniform input.', 'Air to NA 0.71 (lenses fit); water to 0.94.'],
        'Crossed lenses with a Gaussian input.', 'Blue: vector; red: scalar; filled: air; open: water.')
    wide('Scalar 2CE against vector 2CE, Gaussian input', SL('deviation_media_at4.png'), [
        'Difference in T = |T_{scalar} − T_{vector}| / T_{vector}, same NA; black: tan^2(α/2), uniform pupil (Gaussian input lies below).',
        'Passes 5% at NA 0.525 in air and 0.675 in water (uniform input: 0.45 and 0.575): dim pupil edge, fewer high-angle rays.'],
        'With a Gaussian input the paraxial model holds to a higher NA.', 'Same axes as for uniform input.')
    wide('Fidelity, Gaussian input: 2CE, θ = π', SL('linfoot3d_F_2ce_pi_grid_at4.png'), [
        'Top: vector; bottom: scalar; NA 0.5, 0.7, 0.9.', 'Smoother and changes less with NA than with uniform input.'],
        'Gaussian input: fidelity changes less with NA.', 'Axes in lambda_1.')
    wide('Fidelity, vector − scalar, Gaussian input: 2CE, θ = π', SL('linfoot_diff3_F_2ce_pi_at4.png'), [
        'ΔF = F_{vector} − F_{scalar}, same NA, Gaussian input.', 'Smaller than with uniform input at the same NA.'],
        'Gaussian input: vector and scalar fidelity closer.', 'Same NA, same axes.')
    wide('Fidelity, Gaussian vs uniform input: vector, θ = π', SL('linfoot3d_F_2ce_pi_gauss_uniform.png'), [
        'Top: uniform input; bottom: Gaussian input; vector, NA 0.5, 0.7, 0.9.', 'Gaussian: high-F region larger at each NA.'],
        'A Gaussian input keeps the PSF shape over a larger range.', 'Axes in lambda_1.')
    wide('Fidelity, Gaussian − uniform input: vector, θ = π', SL('linfoot_diff3_F_2ce_pi_gauss_uniform.png'), [
        'ΔF = F_{Gaussian} − F_{uniform}, vector, same NA.', 'Red: Gaussian input higher.'],
        'Fidelity difference from the input alone.', 'Same NA, same axes.')
    section(5, 'Time delay, continuous beams', 'A time delay is a phase on each field.')
    wide('Time delay with continuous beams', PD('phase_delay.png'), [
        'Delay Δt → phase φ = ωΔt on the field (φ = π: half an optical period, 1.17 fs at 700 nm).',
        '2PE ∝ |E₁ + E₂|⁴: interference term carries φ → fringes shift. 2CE ∝ |E₁|²|E₂|²: φ cancels → no change.'],
        'A time delay changes 2PE through its fringes; 2CE does not change.', 'Peak lost and fidelity against the phase.')

    section(6, 'Optical pulses', 'A pulse holds a range of wavelengths; 2CE needs one photon from each pulse.')
    wide('Photon pairs at the two-photon resonance', SL('pairs_overlap.png'), [
        'Joint probability: chance that the 750 nm pulse gives λ_a and the 656 nm pulse gives λ_b; independent lasers → p₁(λ_a)·p₂(λ_b).',
        '(b): pairs with 1/λ_a + 1/λ_b = 1/350 nm. Shorter pulses: more pairs.'],
        'The pairs that reach the transition, from the two pulse spectra.', 'Continuous beams: the single pair 750 + 656 nm.')
    wide('Pairs that reach 350 nm', SL('pair_line.png'), [
        'Shading: joint probability of any pair, 20 fs. Line: pairs with 1/λ_a + 1/λ_b = 1/λ_e.',
        'Pairs on the 350 nm line excite the transition.'],
        'The line of pairs with the same total photon energy.', 'Dashed: 345 and 355 nm.')
    n0 = len(prs.slides)
    PT = r'I_i(P, t) = I_i^{\mathrm{CW}}(P)\, \exp\left(-\frac{4\ln 2\,(t - t_i)^2}{\tau^2}\right), \qquad t_1 = \frac{n z_{b,1}}{c}, \quad t_2 = \frac{n z_{b,2}}{c} + \Delta t'
    eqslide('Working on: closed form, term 1: the continuous-beam PSF', 'Each pulse: continuous-beam focus, passing P at its own time.', [
        (r'F_{2c}^{\mathrm{CW}}(P) \propto I_1^{\mathrm{CW}}(P)\; I_2^{\mathrm{CW}}(P)', 'the 2CE PSF of the paper: the '
         'product of the two focused intensities.'),
        (PT, 'pulse i at P: the continuous-beam intensity times a Gaussian in time of FWHM τ, centred on the time t_i at which '
             'the pulse passes P; z_{b,i} = distance of P along beam i from its focus; Δt = time delay of pulse 2.')],
        'Term 1: the focused intensities of the paper, each pulse passing P at its own time.',
        'The spatial part is the continuous-beam focus; the pulse adds a Gaussian envelope in time.',
        r'F^{CW} \propto I_1^{CW} I_2^{CW}' + '\n' + PT, size=15)
    T2M = r'\int P(\nu_a)\, d\nu_a \;\propto\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right), \qquad \delta = \nu_e - (\nu_1 + \nu_2)'
    eqslide('Working on: closed form, term 2: the pair probability', 'Resonant pair: energies add to the transition; independent lasers.', [
        (R1M := r'h\nu_a + h\nu_b = h\nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{\lambda_e}',
         'two-photon resonance; ν = c/λ.'),
        (R2M := r'p_i(\nu) \propto \exp\left(-\frac{4\ln 2\,(\nu - \nu_i)^2}{\Delta\nu^2}\right), \qquad \Delta\nu = \frac{0.441}{\tau}',
         'spectral probability density of laser i (750 and 656 nm) for a τ-long Gaussian pulse.'),
        (R3M := r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)', 'joint probability of the pair whose 750 nm photon has '
         'frequency ν_a: independent lasers, so the probabilities multiply.'),
        (T2M, 'summed over all pairs (complete the square in ν_a): the probability that a pair reaches ν_e; δ = 0 for '
              '750 + 656 nm → 350 nm.')],
        'Term 2: the probability that a pair of photons reaches the transition.',
        'Resonance, the two spectra, their product, and the sum over pairs.', '\n'.join((R1M, R2M, R3M, T2M)), size=14)
    eqslide('Working on: closed form, term 3: the overlap in time', 'One photon from each pulse at P at the same time.', [
        (r'O(P, \Delta t) = \int I_1(P, t)\, I_2(P, t)\, dt = I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \int e^{-a (t-t_1)^2} '
         r'e^{-a (t-t_2)^2} dt, \quad a = \frac{4\ln 2}{\tau^2}', 'overlap in time at P, with term 1 substituted.'),
        (r'(t-t_1)^2 + (t-t_2)^2 = 2\left(t - \bar{t}\right)^2 + \frac{(t_1 - t_2)^2}{2}, \qquad \bar{t} = \frac{t_1+t_2}{2}',
         'complete the square in t; the second term does not depend on t.'),
        (r'O \;\propto\; I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)',
         'the remaining Gaussian integral is a constant, √(π/2a); a/2 = 2 ln2/τ².')],
        'Term 3: the overlap in time is a Gaussian in the difference of the arrival times.',
        'Completing the square separates the part in t from the part in t1 − t2.',
        r'O \propto I_1^{CW} I_2^{CW} \exp(-2\ln 2 (t_1-t_2)^2/\tau^2)', size=15)
    CF = (r'F_{2c}(P, \Delta t) \propto \underbrace{I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}}_{\text{term 1}}\; '
          r'\underbrace{\exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right)}_{\text{term 2}}\; '
          r'\underbrace{\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)}_{\text{term 3}}')
    T12 = r't_1 - t_2 = \frac{n\,(z_{b,1} - z_{b,2})}{c} - \Delta t'
    eqslide('Working on: closed form, combined', 'Pulsed PSF = term 1 × term 2 × term 3, for Gaussian pulses.', [
        (CF, 'continuous-beam PSF × probability that a pair reaches ν_e (the same at all points) × overlap in time.'),
        (T12, 'difference of the arrival times at P: it sets where the pulses meet; Δt moves that place.'),
        (r'\tau \to \infty:\quad F_{2c} \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}', 'long pulses recover the '
         'continuous-beam result of the paper.')],
        'Pulsed PSF = term 1 × term 2 × term 3.', 'The three terms of the previous slides, multiplied.',
        '\n'.join((CF, T12)), size=15)
    for sl_ in list(prs.slides)[n0:]:
        sl_._element.set('show', '0')                  # hidden: closed form in progress

    navy('Next steps', [('Time delay between optical pulses.', 15, PALE)])
    words('Time delay between two pulses', [
        'Each laser emits a train of short pulses; the two trains are synchronized.',
        'Δt: arrival of pulse 2 at the focus after pulse 1, set by the path of beam 2 (1 µm longer → 3.34 fs).',
        'A pulse (no chirp) carries all its wavelengths throughout: the spectrum gives which wavelengths, the envelope '
        '(FWHM τ) gives when.',
        'Δt = 0: the pulses overlap at the focus. Δt ≫ τ: no pair forms there.'],
        'Delay = arrival of pulse 2 after pulse 1 at the focus.', 'What is delayed, and which wavelengths are present.', size=14)
    s = slide('Optical pulses with a time delay: steps', '')
    BOX = ['Pulse spectra: 750 and 656 nm, duration τ', 'Pairs λ_a + λ_b reaching 350 nm (joint probability)',
           'Focus each wavelength (vector field)', 'Delay pulse 2 by Δt: phase e^{iωΔt} per wavelength',
           'Add the pairs at each point → 2CE PSF(Δt)', 'Offset and delay for 20% loss; fidelity']
    for i, txt in enumerate(BOX):
        r, c = divmod(i, 3)
        c = c if r == 0 else 2 - c                      # snake: left to right, then right to left
        l, tp = 0.6 + c * 3.05, 1.3 + r * 1.9
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, tp, 2.6, 1.15, CARD, NAVY, 1.25)
        text(s, l + 0.1, tp + 0.08, 2.4, 1.0, f'{i + 1}. {txt}', 13, NAVY, anchor=ds.MSO_ANCHOR.MIDDLE)
        if i in (0, 1):
            shape(s, MSO_SHAPE.RIGHT_ARROW, l + 2.65, tp + 0.42, 0.35, 0.3, NAVY)
        elif i == 2:
            shape(s, MSO_SHAPE.DOWN_ARROW, l + 1.15, tp + 1.2, 0.3, 0.6, NAVY)
        elif i in (3, 4):
            shape(s, MSO_SHAPE.LEFT_ARROW, l - 0.4, tp + 0.42, 0.35, 0.3, NAVY)
    notes(s, 'Steps of the pulsed 2CE calculation with a time delay.', ' '.join(BOX))
    s._element.set('show', '0')                         # hidden: steps of the running calculation
    words('Next steps', ['Run the time delay between optical pulses (currently running).',
                         'Derive the closed form of the pulsed PSF for Gaussian pulses.',
                         'Draft the paper: main point, offsets follow the size of the focus; sub-points, larger focus (water, '
                         'Gaussian input) and optical pulses.'],
          'Run pulses with a delay, derive the closed form, draft the paper.', 'Next steps.', size=14)

elif SECTION == 'cambaliza':
    title('Replication: Cambaliza & Saloma (2000)', 'Opt. Commun. 184 (2000) 25–35: 2CE and 2PE with two confocal beams, circular and annular pupils')
    words('Summary', [
        'Replicated Figs. 2–7 exactly from Eqs. 1–6, and Fig. 8 with assumed slab settings.',
        'The text differs from the figures in places: three quoted values, the Fig. 5 caption, 2PE in Figs. 6a and 7a.'],
        'Replicated the figures; the text differs in places.', 'Rebuilt from Eqs. 1-6 (paraxial scalar, NA 0.5): on every curve of Figs. 2, 3, 6, 7 and the lines of Fig. 5. 2CE exact everywhere. 2PE: Figs. 2a, 3a are |U1+U2|^4 (Eq. 6); Figs. 6a, 7a are |U1+U2|^2. Beam 2 rotated in real space; the (u, v) rotation of Eq. 1 gives other curves. Fig. 5 caption fit differs from the plotted lines. Three quoted values differ from the figures: 0.67, 1.58x wider, 20% longer. Fig. 8: shapes reproduced with h = 100 um; 2CE background higher.', size=18)
    cmodel()

    for key, title_, line in (
            ('fig2a', 'Fig. 2(a): 2PE, transverse, circular', 'θ = π/2: narrow spot with side lobes.'),
            ('fig2b', 'Fig. 2(b): 2CE, transverse, circular', 'θ = π/2 wider; θ = 0 and π coincide.'),
            ('fig3a', 'Fig. 3(a): 2PE, axial, circular', 'θ = π: standing-wave fringes.'),
            ('fig3b', 'Fig. 3(b): 2CE, axial, circular', 'θ = π/2 short along z.'),
            ('fig4a', 'Fig. 4(a): 2CE, θ = π/2, transverse, against Δλ', 'Spot widens slightly with Δλ.'),
            ('fig4b', 'Fig. 4(b): 2CE, θ = π/2, axial, against Δλ', 'DOF shortens slightly with Δλ.'),
            ('fig5', 'Fig. 5: FWHM and DOF against Δλ', 'Plotted lines match; caption numbers differ.'),
            ('fig6a', 'Fig. 6(a): 2PE, transverse, annular', 'With Eq. 6 (|U₁ + U₂|⁴): side lobes lower than printed.'),
            ('fig6b', 'Fig. 6(b): 2CE, transverse, annular', 'θ = π/2 wider, with side lobes.'),
            ('fig7a', 'Fig. 7(a): 2PE, axial, annular', 'With Eq. 6: θ = π/2 background 1/16; printed ≈ 0.25.'),
            ('fig7b', 'Fig. 7(b): 2CE, axial, annular', 'θ = π/2: 1 µm spot; θ = 0 and π flat.')):
        cpanel(title_, key, f'{key}.png', line)
    for key, title_, line in (
            ('fig6a', 'Fig. 6(a) with the excitation |U₁ + U₂|²', 'With |U₁ + U₂|²: minimum 0.086, as printed (0.08).'),
            ('fig7a', 'Fig. 7(a) with the excitation |U₁ + U₂|²', 'With |U₁ + U₂|²: background 0.25, as printed.')):
        cpanel(title_, key, f'{key}_excitation.png', line)
    coverlay(('fig2a', 'fig2b', 'fig3a', 'fig3b'), 'Current work over the paper: Figs. 2–3, circular',
             'Current work (red, blue) lies on the printed curves.')
    coverlay(('fig6a', 'fig6b', 'fig7a', 'fig7b'), 'Current work over the paper: Figs. 6–7, annular',
             'Orange (|U₁ + U₂|²) and blue lie on the printed curves.')
    words('Quoted values against the paper’s own figures', [
        'Most quoted values match; 0.67, "1.58× wider" and "20% longer" do not.',
        'Fig. 5 caption fit and Fig. 4 sign of Δλ differ from the plots.'],
        'Three quoted values do not match the figures.', 'Match: 30% (29.7%), 35% (34.0% with |U1+U2|^2), 32% (29.1%), 1 um (1.01 zero to zero). Width measure not stated: 0.75 and 0.82 give 0.68-0.87; 40% gives 30-37%; DOF 2x gives 2.2-2.6. Not in the figures: 0.67 -> 0.43-0.50; 1.58x -> 2.5-3.0; 20% longer -> 38-85%. Fig. 5 caption: 2.4e-4 dl + 0.0356 against plotted 5.2e-4 dl + 0.713; DOF slope printed with +. Fig. 4 caption dl = l2 - l1; text dl = l1 - l2.', size=18)
    for key, title_, line in (
            ('fig8a', 'Fig. 8(a): 2PE through a scattering slab, θ = π',
             'Ballistic peak at focus; 2PE background 0.09 (paper: 0.1–0.2).'),
            ('fig8b', 'Fig. 8(b): 2CE through a scattering slab, θ = π',
             '2CE background 0.07 (paper: near 0).')):
        cpanel(title_, key, f'{key}.png', line)
    words('Fig. 8: Monte Carlo settings', [
        'Not in the paper: slab half-thickness h and λ dependence of d_s; used h = 100 µm, d_s ∝ λ².',
        'h sets the background: broad at 20 µm, none at 1 mm.'],
        'Fig. 8 depends on two settings the paper does not give.', "Method of Blanca & Saloma (1998): Gaussian-beam photons, Henyey-Greenstein g = 0.9, up to 40 events; I(z) = photons inside w(z) per area; 10 trials x 1e6 photons per beam. Not stated: h and the lambda dependence of d_s. Used d_s ~ lambda^2, h/d_s = 8 at 700 nm. h = 20 um: broad pedestal; 1 mm: no background; 100 um: paper's narrow peak. In current work scattered light passes the focus, so the 2CE background (0.07) stays near 2PE (0.09).", size=18)
    chigh_na(water_x=True)
    navy('Optical pulses', [('Transform-limited pulses, zero delay, NA 0.5.', 15, PALE)])
    wide('Axial response with pulses, θ = π', os.path.join(CB, 'pulses', 'axial_pi.png'), [
        'Short pulses shorten the 2CE DOF: 3.6 µm → 1.9 µm at 10 fs.', 'θ = 0 and π/2: no change (2% or less).'],
        'Short pulses shorten the 2CE response along the axis at theta = pi.',
        'Head-on pulses overlap within sqrt(2) c tau / 2 of the focus (2.1 um at 10 fs). 2CE DOF 3.56 um continuous, 3.52 at 100 fs, 2.81 at 20 fs, 1.92 at 10 fs. 2PE fringes kept only where the pulses overlap.')
    words('Next steps', ['Decide the slab half-thickness h for Fig. 8.', 'Run pulses with a time delay and at high NA.'],
          'Fig. 8 setting, time delay.', 'Next steps.', size=18)
    DIFF = {                                                   # slides where current work and the paper differ: text in red
        'Summary': ('The text differs',),
        'Paraxial scalar model: Eqs. 1–6': ('Eq. 1 writes',),
        'Fig. 5: FWHM and DOF against Δλ': ('caption numbers differ',),
        'Fig. 6(a): 2PE, transverse, annular': ('lower than printed',),
        'Fig. 7(a): 2PE, axial, annular': ('printed ≈ 0.25',),
        'Quoted values against the paper’s own figures': ('do not', 'differ'),
        'Fig. 8(b): 2CE through a scattering slab, θ = π': ('paper: near 0',)}
    red(DIFF)

elif SECTION == CMEETING:
    title('Replication of Cambaliza & Saloma (2000) and its extension to high NA and optical pulses',
          'M. O. Cambaliza and C. Saloma, “Advantages of two-color excitation fluorescence microscopy with two confocal '
          'excitation beams,” Opt. Commun. 184 (2000) 25–35')
    words('Summary', [
        'Replication of Cambaliza & Saloma (2000), paraxial scalar model, NA = 0.5',
        '– Figs. 2–8 are reproduced.',
        '– With circular pupils 2CE offers no definite advantage in resolution; with annular pupils at θ = π/2 its profile '
        'has zero points and weaker side lobes.',
        '– Three ratios in the text differ from the published curves: 0.49 for 0.67 (p. 28), 2.98 for 1.58 (p. 29), and '
        '85% for 20% (p. 32).',
        'Extension to high NA, vector (Richards–Wolf) focus, air and water',
        '– The main conclusion holds at high NA: 2CE offers no definite advantage in resolution, and 2PE at θ = π/2 stays '
        'the sharpest distribution, but its lead shrinks (2CE spot 2.9 times wider at NA 0.5, 2.0 at NA 0.7).',
        '– The 2PE side lobes weaken with NA (0.11 to 0.04 of the peak at θ = π/2), so the higher contrast of 2CE matters less.',
        '– Crossed lenses (θ = π/2) fit only up to NA 0.71 in air and 0.94 in water, the limit of NA 0.7 noted on p. 34.',
        '– The paraxial Eq. (1) gives the right spot width up to NA 0.86, but overestimates the depth of focus above NA 0.43 '
        '(by 36% at NA 0.9).',
        'Extension to femtosecond pulses',
        '– A transform-limited pulse has a spectral width Δν = 0.441/τ: 44 THz at 10 fs, 83 nm at 750 nm and 63 nm at 656 nm.',
        '– At 100 and 20 fs the spectra stay apart: with facing lenses, 20-fs pulses shorten the 2CE depth of focus from 3.3 '
        'to 2.7 µm at NA 0.5; 2PE changes by 2% or less.',
        '– At 10 fs the spectra overlap, so every photon pair from both beams, with their interference, is needed: next step.'],
        'What the results mean in practice.',
        'Part 1: Eqs. 1-6 at NA 0.5. Figs. 6a and 7a plot the 2PE excitation |U1+U2|^2, not Eq. 6. '
        'Part 2: paraxial DOF error grows as tan^2(alpha/2); theta = pi/2 within 4% where the lenses fit (NA 0.71 air, '
        '0.94 water). Part 3: head-on pulses overlap within sqrt(2) c tau / 2 of the focus (2.1 um at 10 fs in air); '
        '2CE DOF at 10 fs: 0.57 of the continuous value at NA 0.5, 0.96 at NA 0.9 (air); 2PE: 0.995 at every NA. '
        '2PE side lobe at theta = pi/2 (vector, air): 0.42 of the peak at NA 0.3, 0.11 at 0.5, 0.04 at 0.7.', size=12)
    navy('1. Replication of Cambaliza & Saloma (2000): 2PE and 2CE point spread functions, paraxial scalar model, NA 0.5', [])
    words('Summary: replication', [
        'Reproduced with Eqs. (1)–(6), paraxial scalar model, NA = 0.5',
        '– 2PE and 2CE profiles for circular pupils (Figs. 2–3) and three wavelength gaps (Fig. 4).',
        '– 2CE profiles for annular pupils (Figs. 6b, 7b); the 2PE panels of Figs. 6a and 7a are the excitation |U_1 + U_2|^2, not Eq. (6).',
        'Different from the published figures',
        '– Fig. 5: the same linear trends, with slopes 5–9% apart; the caption fits do not describe the plotted lines.',
        '– Three ratios in the text: the curves give 0.49, 2.98 and 85% where pp. 28, 29 and 32 state 0.67, 1.58 and 20%.'],
        'Replication: main points.', 'Eqs. 1-6 computed at NA 0.5 (paraxial scalar); every panel of Figs. 2-8 compared with '
        'the published one. Ranges for the quoted ratios depend on the width measure, which the text does not state. '
        'Fig. 5 caption: FWHM = 2.4e-4 dl + 0.0356, DOF = +4.81e-4 dl + 0.7112; plotted: 5.2e-4 dl + 0.713, -4.6e-4 dl + 0.713.', size=13)
    side('Two-color excitation with two confocal beams at an angle θ', os.path.join(FIG, '..', 'setup_model.png'), [
        '2CE: “two excitation photons of different wavelengths,” with 1/λ_e = 1/λ_1 + 1/λ_2 (p. 26).',
        'The two beams “do not interfere with each other” (p. 26).',
        'θ = angle between the two lens axes: θ = 0 is single-beam 2PE, θ = π is 4Pi 2PE (p. 26).'],
        'Two lenses focus two colors onto one point, at an angle theta.',
        'pp. 26-27: 2PE is the special case lambda1 = lambda2 = 2 lambda_e = lambda_2p. L1 defines the z-axis; at theta = 0 '
        'only one lens is needed. Detector: large area, along the z-axis of L1.', size=13)
    peqslide('Field near the focus of a lens with a circular pupil', [
        (r'U(P;\theta) = -j\,\frac{\pi\,(\mathrm{NA})^2 A\, \exp[\,j(2f/D)^2 u\,]}{\lambda}\,'
         r'\left[C(v_r, w_r, u_r) - jS(v_r, w_r, u_r)\right]', 1,
         ['A lens with a uniformly illuminated circular pupil focuses a plane wave; Eq. (1) is its field at P near the focus.',
          'C and S are Lommel functions. The paraxial form is “accurate for small to moderate NA values (NA < 0.7)” (p. 27).']),
        (r'u_r = u\cos\theta - v\sin\theta, \quad v_r = v\cos\theta + u\sin\theta, \quad '
         r'u = \frac{2\pi\mathrm{NA}^2}{\lambda}z, \quad v = \frac{2\pi\mathrm{NA}}{\lambda}x', None,
         ['Lens L2 is turned by θ about the focus: its field is Eq. (1) at the rotated coordinates u_r and v_r.',
          'u and v are the distances along and across the axis of L1, in optical units.']),
        (r'I(P) = |U(P)|^2, \qquad U_1(P) = U(P;\,0)\ \mathrm{at}\ \lambda_1, \qquad U_2(P;\theta)\ \mathrm{at}\ \lambda_2', None,
         'Each beam’s intensity is |U|^2: U_1 from L1 at λ_1 along z, U_2 from L2 at λ_2, turned by θ.')],
        'Eq. (1): the field of one lens near its focus.',
        'Section 2.1, p. 27. f = focal length, D = pupil diameter, A/f = amplitude of the incident plane wave, '
        'w = 2 pi NA y / lambda. Current work evaluates the integral form of Eq. 1 by Simpson\'s rule (401 radii).',
        lead='Each lens focuses one color onto the common focus O; P(x, y, z) is a point near O.')
    peqslide('Fluorescence from two colors (2CE) and from two photons of one color (2PE)', [
        (r'F_{2c}(P;\theta) = \kappa\,|U_1(P)|^2\,|U_2(P;\theta)|^2 = \kappa\, I_1(P)\, I_2(P;\theta)', 2,
         ['2CE absorbs one photon of each color, so the signal is the product of the two intensities.',
          'It is generated “only in regions where there is a simultaneous presence of I_1(P) and I_2(P; θ)” (p. 28).']),
        (r'|U_1(P) + U_2(P;\theta)|^2 = I_1 + I_2 + 2\,\mathrm{Re}\left[U_1 U_2^{*}\right]', None,
         '2PE uses one color in both beams, so the two fields add first: the excitation has interference terms (p. 28).'),
        (r"F_{2p}(P;\theta) = \kappa'\,|U_1(P) + U_2(P;\theta)|^4", 3,
         ['2PE absorbs two photons, so the signal is the square of the excitation: the fourth power of the summed field.',
          '2PE is “possible even with only one excitation beam” (p. 28): I_1^2 and I_2^2 remain where the other beam is absent.'])],
        'Eqs. (2)-(3): 2CE multiplies two intensities; 2PE squares the summed intensity of two interfering beams.',
        'kappa, kappa\' = fluorescence cross-sections. 2CE: lambda1 = 0.750 um on L1, lambda2 = 0.656 um on L2. '
        '2PE: lambda_2p = 0.7 um on both.', lead='At each point P, the fluorescence depends on how the two focused beams combine.')
    peqslide('Fields and fluorescence with annular (ring) pupils', [
        (r'U_a(P;\theta) = U_R(P;\theta) - U_{\varepsilon R}(P;\theta)', 4,
         ['A ring is a full pupil of radius R with its centre, of radius εR, blocked: its field is the difference of two Eq. (1) fields.',
          'As ε → 1 “the transverse PSF approaches a J_0 distribution while the axial PSF exhibits an infinitely long DOF” (p. 28).']),
        (r'F_{2c/a}(P;\theta) = \kappa\,|U_{a1}(P)|^2\,|U_{a2}(P;\theta)|^2 = \kappa\, I_{a1}(P)\, I_{a2}(P;\theta)', 5,
         '2CE with ring pupils: Eq. (2) with the two annular intensities.'),
        (r"F_{2p/a}(P;\theta) = \kappa'\,|U_{a1}(P) + U_{a2}(P;\theta)|^4", 6,
         '2PE with ring pupils: Eq. (3) with the two annular fields, which add and interfere before the fourth power.')],
        'Eqs. (4)-(6): the same signals with ring pupils.',
        'Section 2.2, p. 28. epsilon = inner over outer radius; epsilon = 0.99 in Section 3.2, with the same outer '
        'diameter as the circular pupil.', lead='Section 2.2 repeats Eqs. (1)–(3) with a ring-shaped pupil in each lens.')
    eqslide('Rotating beam 2: in real space (x, z) or in optical coordinates (u, v)',
            'u and v scale z and x by different factors, so a rotation in (u, v) is not a rotation of the lens.', [
        (r'u = \frac{2\pi\,\mathrm{NA}^2}{\lambda}\,z, \qquad v = \frac{2\pi\,\mathrm{NA}}{\lambda}\,x',
         'optical coordinates: z is scaled by NA², x by NA.'),
        (r'\mathrm{Eq.\ 1:}\quad u_r = u\cos\theta - v\sin\theta, \qquad v_r = v\cos\theta + u\sin\theta',
         'the rotation as written with Eq. (1), in (u, v).'),
        (r'\mathrm{lens\ turned\ by\ }\theta:\quad u_r = u\cos\theta - \mathrm{NA}\,v\sin\theta, \qquad '
         r'v_r = v\cos\theta + \frac{u}{\mathrm{NA}}\sin\theta',
         'rotation in (x, z), then scaled: the sin θ terms carry NA and 1/NA; both forms agree at θ = 0 and π.'),
        (r'\tan\theta_{\mathrm{opt}} = \frac{\tan\theta}{\mathrm{NA}}',
         'a lens turned by θ points at θ_{opt} in (u, v): 63° for θ = 45° at NA 0.5; the two angles agree at 0, π/2 and π.')],
        'Beam 2 should be rotated in real space.',
        'At theta = pi/2 the (u, v) rotation gives v_r = u: the transverse coordinate of beam 2 along z is scaled by NA^2 '
        'instead of NA, which stretches beam 2 along z by 1/NA (2x at NA 0.5) and shortens it along x by NA. '
        'Direction (sin t, cos t) in (x, z) maps to (NA sin t, NA^2 cos t) in (v, u), hence tan t_opt = tan t / NA.',
        '\n'.join((r'u = 2\pi\mathrm{NA}^2 z/\lambda, \quad v = 2\pi\mathrm{NA}\, x/\lambda',
                   r'u_r = u\cos\theta - v\sin\theta, \quad v_r = v\cos\theta + u\sin\theta',
                   r'u_r = u\cos\theta - \mathrm{NA}\,v\sin\theta, \quad v_r = v\cos\theta + (u/\mathrm{NA})\sin\theta',
                   r'\tan\theta_{\mathrm{opt}} = \tan\theta / \mathrm{NA}')), size=14)
    cpanel('Axial 2CE PSF at θ = π/2 with beam 2 rotated in (x, z) or in (u, v), NA 0.5', 'fig3b', '../evidence/rotation.png', (
        'At θ = 0 and π both rotations give the same curve, as published.',
        'At θ = π/2 the published depth of focus, 0.67 µm, is that of the (x, z) rotation; the (u, v) rotation gives 1.31 µm.',
        'Current work rotates beam 2 in (x, z).'),
        '2CE, theta = pi/2, NA 0.5. Across the axis (Fig. 2b) the two rotations nearly coincide.')
    words('Numerical parameters and method', [
        'NA = 0.5, λ_1 = 0.750 µm, λ_2 = 0.656 µm, λ_e = 0.35 µm; 2PE at λ_{2p} = 0.7 µm (p. 28).',
        'Detector along the z-axis of lens L1 (p. 28).',
        'Both foci at O. In the laboratory, one lens is moved until the 2CE signal from a thin fluorescent layer peaks.',
        'Current work: Simpson’s rule over the pupil (Eq. 1); pulses as sums over frequency and time.'],
        'Section 3 parameters, and how current work computes them.',
        'A misaligned focus lowers the 2CE peak (Lim & Saloma 2002, confocality condition). Pulses: frequency sum with at '
        'least 21 samples over +-3.5 sigma; time integral as a Riemann sum with dt = tau/15 over +-(3 tau + travel time). '
        'Sampling check: uniform sums converge to machine precision by about 20 frequencies. Integration: no Runge-Kutta.', size=14)
    CQ = {   # Sections 3.1-3.2 panels: what Cambaliza & Saloma (2000) point out on each figure, in their words
        'fig2a': ('Transverse 2PE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π', 'fig2a.png', (
            'θ = 0 and π: identical profiles. θ = π/2: “the sharpest distribution” (p. 28).',
            'θ = π/2: “stronger side lobes” from interference, so images of “lower contrast” (p. 28).')),
        'fig2b': ('Transverse 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π', 'fig2b.png', (
            'θ = 0 and π: identical, and equal to 2PE at θ = 0. θ = π/2: no “second-order interference effects” (p. 29).',
            'Circular pupils: 2CE does “not offer a definite advantage” in transverse resolution (p. 29).')),
        'fig3a': ('Axial 2PE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π', 'fig3a.png', (
            'θ = π: “strong intensity modulation”, so “unsuitable for imaging thick samples” (p. 29).',
            'θ = π/2: central peak “in the order of λ_{2p}”, but “strong side lobes” (p. 29).')),
        'fig3b': ('Axial 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π', 'fig3b.png', (
            'θ = 0 and π: identical, and equal to 2PE at θ = 0 (p. 29).',
            'θ = π/2: “weaker side lobes” than 2PE, “but with a broader DOF” (p. 30).')),
        'fig4a': ('Transverse 2CE PSF for three wavelength gaps Δλ, θ = π/2, NA 0.5', 'fig4a.png', (
            'From Δλ = 10 to 94 nm, “the FWHM increases by less than 6%” (p. 30).',
            'The spot follows the focus of L1, which grows with λ_1 (+6.4%).')),
        'fig4b': ('Axial 2CE PSF for three wavelength gaps Δλ, θ = π/2, NA 0.5', 'fig4b.png', (
            'The DOF “becomes sharper with increasing Δλ” (p. 30).',
            'The depth of focus follows the focus of L2, which shrinks with λ_2 (−5.6%).')),
        'fig5': ('2CE central spot and depth of focus against the wavelength gap Δλ, θ = π/2', 'fig5.png', (
            '“A trade-off” between central spot sharpness and DOF for a given Δλ (p. 30).',
            'Same linear trends; FWHM slope 5.2 against 4.9 × 10^{−4} µm/nm from the published points.')),
        'fig6a': ('Transverse 2PE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π', 'fig6a_excitation.png', (
            'θ = π/2: narrower spot, “stronger side lobes”, and it “lacks zero points”: images “of low contrast” (p. 31).',
            'The published curve is the excitation |U_1 + U_2|^2 (minimum 0.08); the 2PE signal of Eq. (6) is its square, 0.08^2 ≈ 0.007.')),
        'fig6b': ('Transverse 2CE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π', 'fig6b.png', (
            'θ = 0 and π: identical; θ = π/2: wider spot, “stronger side lobes” (p. 31).',
            'Both “possess zero points”, unlike annular 2PE at θ = π/2 (p. 31).')),
        'fig7a': ('Axial 2PE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π', 'fig7a_excitation.png', (
            'θ = 0: constant along z; θ = π: “uniform sinusoidal modulation”; no “optical sectioning capability” (p. 32).',
            'θ = π/2: no zero points, “much stronger side lobes” (p. 32).',
            'The published curve is the excitation |U_1 + U_2|^2 (background 0.25); the 2PE signal of Eq. (6) is its square, 0.25^2 ≈ 0.06.')),
        'fig7b': ('Axial 2CE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π', 'fig7b.png', (
            'θ = 0 and π: 1.0 along z, no “optical sectioning capability” (p. 32).',
            'θ = π/2: central spot “about 1 µm (1.43λ_{2p})”, with “zero points” (p. 32).'))}

    def cq(key, script=''):
        ttl, ours, lines = CQ[key]
        cpanel(ttl, key, ours, lines, f'{ttl}. Current work matches the published curves. {script}')

    def ratio(ttl, path, items, main, script):
        wide(ttl, path, items, main, script)

    words('Circular pupils: what is compared', [
        'Circular pupils (ε = 0): 2PE and 2CE at θ = 0, π/2 and π (Figs. 2–3).',
        'Across the axis: the central spot. Along the axis: the depth of focus (DOF).',
        'Each published panel beside current work, from Eqs. (1)–(3).'],
        'Section 3.1: circular pupils, Figs. 2-5.',
        'pp. 28-30. The text compares central-spot diameters and depths of focus; it does not state the width measure.', size=16)
    cq('fig2a')
    ratio('2PE central spot at θ = π/2 relative to θ = 0, circular pupils', os.path.join(CB, 'evidence', 'ratio_fig2a.png'), [
        'Stated: the 2PE spot at θ = π/2 is “approximately 0.67 times” that at θ = 0 (p. 28).',
        'Current work matches Fig. 2a: FWHM 0.256 against 0.517 µm, a ratio of 0.49.',
        'Measured at 1/e² (13.5%) of the peak instead of at half, the widths give the same ratio, 0.49.'],
        'Fig. 2a gives 0.49, not 0.67.',
        'Current work matches the published curves (previous slide). With the zero-to-zero width the ratio is 0.43-0.50.')
    cq('fig2b')
    ratio('2CE central spot relative to 2PE at θ = π/2, circular pupils', os.path.join(CB, 'evidence', 'ratio_158.png'), [
        'Stated: the 2CE spot at θ = π/2 is “1.58 times wider” than the 2PE spot (p. 29).',
        'Current work matches Figs. 2a and 2b: FWHM 0.763 against 0.256 µm, a ratio of 2.98.',
        'Measured at 1/e² (13.5%) of the peak instead of at half, the widths give 2.93.'],
        'Figs. 2a and 2b give 2.98, not 1.58.',
        'Other width measures give 2.5-3.0. 1.58 is also not the 2CE spot at pi/2 over the 2PE spot at 0 (1.48).')
    cq('fig3a')
    cq('fig3b')
    words('Gap Δλ between the two 2CE wavelengths: what is compared', [
        'Δλ = λ_1 − λ_2 = 10, 39 and 94 nm, with 1/λ_1 + 1/λ_2 = 1/λ_e fixed (p. 30).',
        '“The shorter excitation wavelength λ_2 is focused using lens L2” (p. 30).',
        'Circular pupils, θ = π/2, NA = 0.5.'],
        'Section 3.1: the wavelength gap, Figs. 4-5.',
        'Circular pupils, NA 0.5, theta = pi/2. Fig. 4: profiles for three gaps; Fig. 5: FWHM and DOF against the gap, '
        'with a linear fit.', size=16)
    cq('fig4a')
    cq('fig4b')
    cq('fig5', 'Caption: FWHM = 2.4e-4 dl + 0.0356, DOF = +4.81e-4 dl + 0.7112; plotted lines: 5.2e-4 dl + 0.713 and '
       '-4.6e-4 dl + 0.713. A +-5 nm laser-diode tolerance moves the spot by +-0.7%.')
    side('Slopes against Δλ: current work, published points and caption fits', os.path.join(CB, 'evidence', 'fig5_overlay.png'), [
        'Blue and green: current work. Orange dashed: the DOF fit given in the caption.',
        'Current work lies within 0.004 µm of the published points.',
        'The published points scatter by 0.002 µm rms, so their slope is uncertain by ±0.2 × 10^{−4} µm/nm, half the difference.',
        'Current work follows Eqs. (1)–(3); its slopes match the scaling of the two foci with λ_1 and λ_2.',
        'The fit equations in the caption match neither plotted line; the FWHM fit lies off the plot.'],
        'Fig. 5: same trends; slopes differ; caption fits inconsistent with the plot.',
        'Published points digitized from the scan: FWHM slope 4.86e-4, intercept 0.712, rms scatter 0.0016 um. The '
        'wavelength pairs (705, 695), (720, 681), (750, 656) nm satisfy 1/l1 + 1/l2 = 1/350 nm. Reading the width at the '
        'nearest sample of a 5-nm grid scatters the points as in the published plot but raises the FWHM slope to 5.7e-4. '
        'Current work: +5.24e-4 dl + 0.7131 and -4.57e-4 dl + 0.7131.')
    words('Annular pupils: what is compared', [
        'Thin ring pupils, ε = 0.99, with the outer diameter of Section 3.1 (p. 30).',
        'At θ = π/2, annular 2CE gives a PSF “superior to the 2PE microscope” (p. 26).'],
        'Section 3.2: annular pupils, Figs. 6-7.',
        'pp. 30-32: epsilon = inner over outer radius of the ring.', size=16)
    cq('fig6a')
    cq('fig6b')
    cq('fig7a')
    cq('fig7b')
    wide('2PE with annular pupils: excitation |U₁ + U₂|² against the signal |U₁ + U₂|⁴', os.path.join(CB, 'evidence', 'eq6_excitation.png'), [
        'The excitation |U_1 + U_2|^2 (orange) is the focused intensity; the 2PE signal of Eq. (6), |U_1 + U_2|^4 (red), is its square.',
        'Squaring lowers every value below the peak: the minimum across the axis goes from 0.08 to 0.007, the background along it from 0.25 to 0.06.',
        'The published annular 2PE curves show 0.08 and 0.25, so they plot the excitation, not the signal.',
        'The published circular 2PE curves follow Eq. (3), |U_1 + U_2|^4, as current work does.'],
        'Figs. 6a and 7a plot the excitation, not the 2PE signal of Eq. 6.',
        'The side peaks of the published Fig. 7a curve at theta = pi/2 match |U1+U2|^2 within 0.02 um (correlation 0.98).')
    ratio('Annular 2CE depth of focus relative to circular 2PE at θ = π/2', os.path.join(CB, 'evidence', 'ratio_20pct.png'), [
        'Stated: the annular 2CE DOF at θ = π/2 is “20% longer” than the circular 2PE DOF (p. 32).',
        'Current work matches Figs. 3a and 7b: 0.473 against 0.256 µm, 85% longer.',
        'Measured at 1/e² (13.5%) of the peak instead of at half, the widths give 76%.'],
        'Figs. 3a and 7b give 85%, not 20%.', 'Other width measures give 38-85%.')
    words('Ratios stated in the text against the published curves', [
        'Four values stated on pp. 31–32 agree with the published figures: 30%, 35%, 32% and 1 µm.',
        'Four more agree for some width measure, which the text does not state: 0.75, 0.82, 40% and "twice".',
        'Three do not agree with the published figures:',
        '– p. 28: the 2PE spot at θ = π/2 is "0.67" times that at θ = 0; the curves give 0.49.',
        '– p. 29: the 2CE spot at θ = π/2 is "1.58 times wider" than the 2PE spot; the curves give 2.98.',
        '– p. 32: the annular 2CE depth of focus at θ = π/2 is "20% longer" than the circular 2PE one; the curves give 85%.'],
        'Values stated in the text against the published figures.', 'Match: 30% (29.7%), 35% (34.0% with |U1+U2|^2), 32% '
        '(29.1%), 1 um (1.01 zero to zero). Width measure not stated: 0.75 and 0.82 give 0.68-0.87; 40% gives 30-37%; DOF '
        '2x gives 2.2-2.6. Fig. 4 caption dl = l2 - l1; text dl = l1 - l2.', size=15)
    words('Discussion and conclusion of Cambaliza & Saloma (2000)', [
        'Circular pupils: the 2CE advantage “is arguable” (p. 34).',
        'Annular lenses: the 2CE advantage “is more apparent” (p. 34).',
        'Main advantage: “observation of objects through highly scattering media”, not resolution (p. 34).',
        'Long-DOF axicons ease “the confocality condition for the two excitation beams” (p. 34).'],
        'Conclusions of Cambaliza & Saloma (2000).',
        'p. 34 also: dual-beam excitation with two identical objectives for 0 <= theta <= pi/2 is possible only for NA <= 0.7; '
        'a cw excitation beam could replace femtosecond pulses when the intermediate state is real.', size=15)
    chigh_na('2. Extension to high NA: paraxial scalar model against the vector (Richards–Wolf) focus, air and water', summary=('Summary: high NA', [
        'The conclusions of Cambaliza & Saloma hold at high NA, but the differences between 2PE and 2CE shrink.',
        '2PE at θ = π/2 stays the sharpest distribution at all NA: its spot is one interference fringe, 0.26 µm in air, while '
        'the 2CE spot shrinks with NA, from 2.9 times the 2PE spot at NA 0.5 to 2.0 at NA 0.7.',
        'The 2PE side lobes weaken with NA, from 0.11 to 0.04 of the peak at θ = π/2 (NA 0.5 to 0.7) and from 0.97 to 0.42 '
        'at θ = π (NA 0.5 to 0.9), so 2PE images gain contrast.',
        'Crossed lenses (θ = π/2) fit only up to NA 0.71 in air and 0.94 in water, the limit of NA 0.7 noted on p. 34.',
        'The paraxial Eq. (1) gives the right spot width up to NA 0.86 in air, but overestimates the depth of focus above '
        'NA 0.43 (by 36% at NA 0.9).'],
        'High NA: main points.', 'Vector = Richards-Wolf, both beams polarized along y. Paraxial DOF error grows as '
        'tan^2(alpha/2); in water it is about half that in air at the same NA. Annular pupils: paraxial DOF 2.2x too long '
        'at NA 0.9 in air.'))
    PU = os.path.join(CB, 'high_na', 'pupils')
    wide('Annular pupils: depth of focus against NA, air', os.path.join(PU, 'annular_widths_air_z.png'), [
        'As NA increases the paraxial annular DOF departs sooner than the circular one: 15% too long at NA 0.5 and 2.2 times at NA 0.9 in air.',
        'A thin ring uses the edge of the pupil, where the paraxial phase error is largest.'],
        'Along the axis the paraxial model departs sooner with annular pupils.',
        'Vector (Richards-Wolf) with the annulus sin(theta) >= eps sin(alpha) (sine condition), beams polarized along y. '
        'Annular DOF (2CE, theta = 0), vector / scalar: 155 / 179 um at NA 0.5 (scalar 15% longer), 65 / 91 um at 0.7 '
        '(39%), 25 / 55 um at 0.9 (125%). Water: 221 / 238 at 0.5, 54 / 73 at 0.9, 18 / 41 at 1.2. Annular over circular '
        'DOF: 47x at NA 0.5, 42x at 0.7, 31x at 0.9 (paraxial: 1/(1 - eps^2) = 50). Spot across the axis: 0.70x the '
        'circular one at all NA. theta = pi/2: set by the narrow transverse spot of the other beam, so scalar and vector '
        'agree within 2%.')
    wide('Annular central spots against NA: the comparisons of p. 31', os.path.join(PU, 'annular_quoted_x.png'), [
        'As NA increases the annular 2CE spot at θ = 0 stays 0.67 of that at θ = π/2, and the annular 2PE spot loses its lead '
        'over 2CE: 53% narrower at NA 0.5, 34% at NA 0.7 in air.',
        'Star: value stated on p. 31; cross: the same ratio on the published curves. 0.82 stated, 0.67 on Fig. 6b; 35% stated, '
        '34% on Fig. 6a, which plots the excitation (Eq. (6) gives 53%).'],
        'Annular comparisons across the axis.',
        'Stars: values quoted at NA 0.5. Solid: vector; dashed: paraxial scalar; filled: air; open: water. The replication '
        'gives 0.67 at NA 0.5 for the Fig. 6b ratio.')
    wide('Annular depth of focus against NA: the comparisons of p. 32', os.path.join(PU, 'annular_quoted_z.png'), [
        'As NA increases the annular 2CE DOF at θ = π/2 stays about 30% shorter than the circular one, and its lead over the 2PE DOF '
        'shrinks: 85% longer at NA 0.5.',
        'Star: value stated on p. 32; cross: the same ratio on the published curves. 40% stated, 30% on the curves; 20% stated, 85%.'],
        'Annular comparisons along the axis.',
        'Stars: values quoted at NA 0.5. Solid: vector; dashed: paraxial scalar; filled: air; open: water.')
    wide('2CE response to the wavelength gap Δλ against NA, θ = π/2', os.path.join(PU, 'dlambda_vs_na.png'), [
        'As NA increases the effect of Δλ stays the same: from 10 to 94 nm the central spot grows by about 6% and the DOF '
        'shrinks by about 5%, from NA 0.3 to 0.9, in air and water.',
        'At θ = π/2 the central spot follows λ_1 and the DOF follows λ_2 at all NA, so the trade-off of p. 30 holds.'],
        'The wavelength gap changes the 2CE response by the same fraction at all NA.',
        '2CE, theta = pi/2, circular pupils; 1/lambda1 + 1/lambda2 = 1/350 nm. From 10 to 94 nm the FWHM grows by 6.3% at '
        'NA 0.3, 6.1% at 0.5, 5.7% at 0.7 (air), 5.8% at 0.9 (water); the DOF shrinks by 5.5% to 5.2%. Vector (y), '
        'unpolarized and scalar within 0.3% of each other in this relative change.')
    navy('3. Extension to optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses', [])
    words('Summary: optical pulses', [
        'A transform-limited pulse of duration τ has the same spectral width Δν = 0.441/τ for every color: 4.4, 22 and 44 THz '
        'at τ = 100, 20 and 10 fs.',
        'In wavelength the width differs by color: 83 nm at 750 nm and 63 nm at 656 nm for 10 fs.',
        'At 100 and 20 fs the two 2CE spectra stay apart, so one photon from each beam describes 2CE completely.',
        'There, with facing lenses, 20-fs pulses shorten the 2CE depth of focus from 3.3 to 2.7 µm at NA 0.5 (19%), and '
        '100-fs pulses by about 1%; 2PE and the other angles change by 2% or less.',
        'At 10 fs the spectra overlap (31% of each peak at 700 nm): the PSFs must sum every photon pair from both beams, '
        'with their interference. Next step.'],
        'Optical pulses: main points.', 'Vector focus, beams along y. Head-on pulses overlap within sqrt(2) c tau / 2 of '
        'the focus (2.1 um at 10 fs in air). The NA 0.5 slide uses the paraxial model: 3.6 to 1.9 um.', size=14)
    PE1 = r'E(t) = A(t)\cos(2\pi\nu_0 t), \qquad A(t) = e^{-2\ln 2\, t^2/\tau^2}, \qquad \Delta\nu = \frac{0.441}{\tau}'
    PE2 = r't_i(P) = \frac{n\, z_{b,i}(P)}{c}'
    eqslide('What an optical pulse adds', 'A pulse lasts τ, carries a spread of frequencies Δν, and passes each point at its own time.', [
        (PE1, 'A transform-limited Gaussian pulse: its duration τ fixes its spectral width Δν.'),
        (PE2, 'The time at which pulse i passes the point P.')],
        'A pulse has a duration, a spectrum and an arrival time.',
        'Continuous beams have one frequency and are present at all times; a pulse has a band of frequencies and is present '
        'at each point only for about tau. 10 fs: delta nu = 44 THz, about 40 nm at 750 nm.', '\n'.join((PE1, PE2)), size=17)
    wide('Pulse spectra against frequency, τ = 100, 20 and 10 fs', os.path.join(CB, 'pulses', 'spectra_frequency.png'), [
        'A transform-limited pulse of duration τ has the same spectral width Δν = 0.441/τ for every color: 4.4, 22 and 44 THz.',
        'At 10 fs the 750- and 656-nm spectra overlap, and each still has 31% of its peak at 428 THz (700 nm), where two '
        'photons of one beam add up to the 350-nm transition.'],
        'Spectra of the three lasers against frequency.',
        'Gaussian, transform-limited: delta nu = 0.441 / tau. Centres: 399.7 THz (750 nm), 457.0 THz (656 nm), 428.3 THz '
        '(700 nm). Spectrum at 700 nm relative to its peak: 0.31 at 10 fs, 0.01 at 20 fs.')
    wide('Pulse spectra against wavelength, τ = 100, 20 and 10 fs', os.path.join(CB, 'pulses', 'spectra_wavelength.png'), [
        'In wavelength the width is λ²Δν/c, so it differs by color: 8, 41 and 83 nm at 750 nm; 6, 32 and 63 nm at 656 nm.',
        'Current work keeps one photon from each beam (the 2CE pairs of the next slides); the single-beam pairs at 10 fs are '
        'not included.'],
        'Spectra of the three lasers against wavelength.',
        'Spectral FWHM (nm), 100 / 20 / 10 fs: 750 nm 8.3 / 41.4 / 83.0; 656 nm 6.3 / 31.7 / 63.5; 700 nm 7.2 / 36.1 / 72.3. '
        'Rough estimate of the single-beam two-photon rate at 10 fs: about 10% of the 2CE rate for each beam, for a narrow '
        'transition.')
    words('Next steps', [
        'Scattering medium',
        '– Compare the 2PE and 2CE backgrounds for the slab half-thicknesses h that give the published curves.',
        '– Count each photon once, in one depth bin, and compare the noise with the published curves.',
        'Optical pulses',
        '– Sum every photon pair from both beams, with their interference, and recompute the pulsed 2CE and 2PE PSFs.',
        '– Then the time delay between the two pulses.',
        'High NA',
        '– Oil immersion (n = 1.515), up to NA 1.4.'],
        'Next steps.', 'Scattering backgrounds against h; time-delay results; oil immersion.', size=15)
    navy('Backup: pulsed PSFs with one photon from each beam (to be recomputed with all photon pairs)', [])
    PJ1 = r'p_i(\mathbf{r}, t) \propto I_i(\mathbf{r}, t) = I_i^{\mathrm{CW}}(\mathbf{r})\; A_i^2\!\left(t - t_i(\mathbf{r})\right)'
    PJ2 = r"p_i(\nu) = \frac{|\tilde{E}_i(\nu)|^2}{\int |\tilde{E}_i(\nu')|^2\, d\nu'}"
    PJ3 = (r'P_{12}(\mathbf{r}) \propto \int p_1(\mathbf{r}, t)\, p_2(\mathbf{r}, t)\, dt \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}\; '
           r'\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)')
    eqslide('Joint probability of a photon pair in space and time', 'The intensity is the probability of finding a photon '
            'there and then; the spectrum is the probability of its frequency.', [
        (PJ1, 'The intensity is the probability of finding a photon of beam i at r and time t.'),
        (PJ2, 'The spectrum is the probability that the photon has frequency ν.'),
        (PJ3, 'A 2CE event needs one photon of each beam at the same place and time: the pulses must arrive within about τ.')],
        'A 2CE event needs one photon of each beam at the same point and time.',
        'With A^2(t) = exp(-4 ln2 t^2 / tau^2): integral over t of A^2(t - t1) A^2(t - t2) = tau sqrt(pi / (8 ln2)) '
        'exp(-2 ln2 (t1 - t2)^2 / tau^2). The same factor comes out of the sum over photon pairs (next slides).',
        '\n'.join((PJ1, PJ2, PJ3)), size=16)
    PP1 = r'\nu_a + \nu_b = \nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{350\ \mathrm{nm}}'
    PP2 = r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)'
    PP3 = r'A(P) = \int \sqrt{P(\nu_a)}\; U_1(P, \nu_a)\, U_2(P, \nu_e - \nu_a)\, d\nu_a, \qquad F_{2c} = \kappa_{2c}\, |A|^2'
    eqslide('Photon pairs: which pairs excite the transition', '2CE needs one photon from each laser whose frequencies add up to the '
            'transition; every such pair contributes.', [
        (PP1, 'One photon of each laser, whose energies add up to the 350-nm transition.'),
        (PP2, 'The two lasers are independent, so the probabilities of the two frequencies multiply.'),
        (PP3, 'The two-photon amplitude sums every resonant pair; the 2CE signal is its square.')],
        'Pairwise probabilities: resonant pairs, weighted by their joint probability, summed in amplitude.',
        'The pairs add with the phase of the times at which the two pulses pass P. Where the pulses arrive together all pairs '
        'add in phase; where they arrive apart, the pairs partly cancel.', '\n'.join((PP1, PP2, PP3)), size=16)
    PC1 = (r'F_{2c}(P) \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) '
           r'\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)')
    PC2 = r'\theta = \pi:\quad t_1 - t_2 = \frac{2nz}{c} \;\Rightarrow\; \mathrm{FWHM}_z = \frac{\sqrt{2}\, c\,\tau}{2n}'
    eqslide('Pulsed 2CE PSF: the pulses must meet', 'Summing the pairs gives the continuous PSF times the overlap of the two pulses '
            'in time; at θ = π they meet only near the focus.', [
        (PC1, 'The pulsed 2CE PSF: the continuous PSF times the overlap of the two pulses in time.'),
        (PC2, 'Facing pulses overlap only near the focus: 2.1 µm in air at 10 fs. At θ = 0 they travel together.')],
        'The photon-pair sum and the overlap in time give the same pulsed PSF at zero delay.',
        'The Gaussian sum over pairs gives exp(-2 ln2 (t1-t2)^2/tau^2), the same as the integral of I1(t) I2(t) over t. '
        'tau -> infinity recovers the continuous PSF.', '\n'.join((PC1, PC2)), size=16)
    P2E1 = r'|E_1 + E_2|^2 = I_1 + I_2 + 2\sqrt{I_1 I_2}\,\cos\varphi'
    P2E2 = (r'\int |E_1 + E_2|^4\, dt = \underbrace{\int (I_1^2 + I_2^2)\, dt}_{\text{one beam}} + '
            r'\underbrace{\int \left[4(I_1 + I_2)\sqrt{I_1 I_2}\cos\varphi + 4 I_1 I_2 \cos^2\varphi\right] dt}_{\text{both beams}}')
    eqslide('Pulsed 2PE: what the pulses change', 'Both 2PE beams come from the same 700-nm laser, so '
            'one beam alone can excite: pulses change 2PE much less than 2CE.', [
        (P2E1, 'The two 2PE beams interfere: fringes λ/2n apart along the axis at θ = π, half the wavelength in the medium (0.35 µm in air).'),
        (P2E2, 'One beam alone excites 2PE without any overlap; the fringes need both pulses at once.')],
        'Pulsed 2PE: the single-beam terms stay, the fringes fade where the pulses do not meet.',
        'Depth of focus (FWHM of the central fringe, set by lambda): 0.995 of the continuous value at 10 fs at every NA. '
        'Share of the axial 2PE signal outside the central fringe at NA 0.5 in air: 89% continuous, 85% at 10 fs. '
        '2CE has no single-beam term (I1 I2 only), so it is gated completely by the pulse overlap.',
        '\n'.join((P2E1, P2E2)), side=('Result', ['The 2PE depth of focus changes by 0.5% at 10 fs, at all NA.',
                                                    'The central fringe is set by λ, not by the pulse.',
                                                    'Away from the focus the fringes fade; each beam’s own 2PE remains.']), size=15)
    wide('Axial 2PE and 2CE PSF with pulses, facing lenses, NA 0.5 (paraxial model)', os.path.join(CB, 'pulses', 'axial_pi.png'), [
        'Facing pulses meet only within 2.1 µm of the focus, so 10-fs pulses shorten the 2CE DOF from 3.6 to 1.9 µm.',
        'The 2PE central fringe does not change; the outer fringes fade where the pulses do not meet.'],
        'Short pulses shorten the 2CE response along the axis at theta = pi.',
        'Paraxial scalar. 2CE DOF 3.56 um continuous, 3.52 at 100 fs, 2.81 at 20 fs, 1.92 at 10 fs. theta = 0 and pi/2: '
        'change of 2% or less. 2PE fringes kept only where the pulses overlap.')
    PH = os.path.join(CB, 'pulses', 'high_na')
    if os.path.exists(os.path.join(PH, 'dof_pi.png')):
        wide('Depth of focus with pulses against NA, facing lenses', os.path.join(PH, 'dof_pi.png'), [
            'As NA increases the shortening of the 2CE DOF by the pulses fades: the focus becomes shorter than the pulse overlap.',
            'The 2PE DOF is the central fringe, much shorter than the overlap, and changes by 0.5% at every NA.'],
            'The effect of the pulse length fades as NA grows.',
            'Vector (Richards-Wolf), both beams polarized along y, zero delay. DOF = central-peak FWHM along z; '
            'pulsed over continuous. Widths (um), CW | 20 fs | 10 fs: '
            + '; '.join(l for l in open(os.path.join(PH, 'widths.txt')).read().splitlines()[1:] if ' z π |' in l))
    PULSE = {
        ('air', 0.5): ('The 3.3-µm 2CE focus is longer than the 2.1-µm pulse overlap, so 10-fs pulses shorten the 2CE DOF to 1.9 µm.',
                       'The 2PE central fringe does not change; of the 9 fringes in the 3.3-µm focus, only those within about 1 µm of the focus remain.'),
        ('air', 0.7): ('The 2CE focus, 1.6 µm, is now shorter than the overlap, so 10-fs pulses shorten it less, to 1.3 µm.',
                       'The 2PE central fringe does not change; about 4 fringes fit in the 1.6-µm focus, and the outer ones drop.'),
        ('air', 0.9): ('The 2CE focus, 0.81 µm, is well inside the 2.1-µm overlap: the pulses change the 2CE DOF by 4%, to 0.77 µm.',
                       'The 2PE central fringe does not change; only about 2 fringes fit in the 0.81-µm focus.'),
        ('water', 0.5): ('In water the focus is longer (4.6 µm) and the overlap shorter (1.6 µm), so 10-fs pulses shorten the 2CE DOF to 1.6 µm.',
                         'Of the 17 2PE fringes in the 4.6-µm focus, only those within the 1.6-µm overlap of the pulses remain.'),
        ('water', 0.9): ('The 2CE focus, 1.3 µm, is close to the 1.6-µm overlap: 10-fs pulses shorten the 2CE DOF to 1.0 µm.',
                         'The 2PE central fringe does not change; about 4 fringes fit in the 1.3-µm focus, and the outer ones drop.'),
        ('water', 1.2): ('The 2CE focus, 0.60 µm, is well inside the 1.6-µm overlap: the pulses change the 2CE DOF by 4%, to 0.58 µm.',
                         'The 2PE central fringe does not change; only about 2 fringes fit in the 0.60-µm focus.')}
    for (med, na), items in PULSE.items():
        path = os.path.join(PH, f'axial_pi_{med}_na{na:g}.png')
        if os.path.exists(path):
            wide(f'Axial 2PE and 2CE PSF with pulses, facing lenses, NA {na:g}, {med}', path, list(items),
                 f'Pulses at NA {na:g}, {med}.',
                 'Vector (Richards-Wolf), beams along y (unpolarized 2CE: the same on the axis). 2PE: continuous and 10 fs '
                 '(100 and 20 fs lie between the two, on the continuous curve); '
                 '2CE: continuous and tau = 100, 20, 10 fs; zero delay; each curve normalized to its own peak.')
    navy('Backup: fluorescence imaging in highly scattering media, Monte Carlo simulation (Section 3.3)', [])
    words('Scattering slab: what is simulated', [
        'Monte Carlo, forward-scattering medium: g = 0.9, h/d_s = 8, facing lenses (θ = π) (p. 32).',
        'Focal plane at the centre of a slab of thickness 2h; h/d_s = scattering events before the focus (pp. 32–33).'],
        'Section 3.3: scattering, Fig. 8.',
        'Method of Blanca & Saloma (1998): Gaussian-beam photons, Henyey-Greenstein phase function, g = 0.9, up to 40 '
        'events; 1e7 photons per beam as published.', size=15)
    cpanel('Axial 2PE profile through a scattering slab, facing lenses', 'fig8a', 'fig8a.png', (
        'At z = 0: “mostly … unscattered (ballistic) photons” (p. 33).',
        'Out of focus: 2PE “considerably reduced but still not to negligible values” (p. 33).',
        'Current work: background 0.09 (published 0.1–0.2), with 10⁷ photons per beam.'))
    cpanel('Axial 2CE profile through a scattering slab, facing lenses', 'fig8b', 'fig8b.png', (
        '2CE: no “significant contributions from the out-of-focus planes” (p. 33).',
        'Current work: background 0.07 (published near 0).'),
        'Current work is smoother: the mean of 10 runs of 1e6 photons, and I(z) counts each photon at every plane it crosses '
        'inside the beam radius w(z) (Blanca & Saloma 1998), so neighbouring points share photons. The published curves '
        'use 1e7 photons; their binning is not stated.')
    wide('Monte Carlo noise: one run of 10⁶ photons', os.path.join(CB, 'panels', 'fig8_noise.png'), [
        'One run of 10⁶ photons is nearly as smooth as the mean of 10 runs: 0.5% noise away from the focus.',
        'Each photon counts at every plane it crosses inside w(z), so each point of I(z) uses most photons.',
        'Counting each photon once, in one depth bin, gives more scatter; the published count is not stated.'],
        'The smooth curves come from the counting, not from the number of photons.',
        'Relative SD of one run (10 runs): 2PE excitation 0.55% for |z| > 10 um and 5.1% for |z| < 1 um; lambda_1 0.43% '
        'and 3.2%; lambda_2 0.61% and 5.8%. Fluorescence of one run against the mean, rms for |z| > 10 um: 2PE 0.004, '
        '2CE 0.005, on backgrounds of 0.09 and 0.07.')
    wide('Out-of-focus background against the slab half-thickness h', os.path.join(CB, 'panels', 'fig8_h_scan.png'), [
        'h is not given: a thin slab gives a broad background pedestal, a thick slab none.',
        'No single h gives the published 2PE background (0.1–0.2) and no 2CE background; h = 100 µm is used.'],
        'Fig. 8 depends on h, which is not given.',
        "Not stated: h and the lambda dependence of d_s; used d_s ~ lambda^2, h/d_s = 8 at 700 nm for every h. Background "
        "for |z| > 10 um, 2PE / 2CE: h = 20 um broad pedestal; 50 um 0.26 / 0.14; 100 um 0.09 / 0.07; 300 um 0.004 / 0.005; "
        "1 mm none.")
    green({
        'Axial 2CE PSF at θ = π/2 with beam 2 rotated in (x, z) or in (u, v), NA 0.5': ('Current work rotates',),
        'Slopes against Δλ: current work, published points and caption fits': ('Current work follows Eqs.',),
        '2PE with annular pupils: excitation |U₁ + U₂|² against the signal |U₁ + U₂|⁴': ('as current work does',),
        '2PE central spot at θ = π/2 relative to θ = 0, circular pupils': ('Current work matches',),
        '2CE central spot relative to 2PE at θ = π/2, circular pupils': ('Current work matches',),
        'Annular 2CE depth of focus relative to circular 2PE at θ = π/2': ('Current work matches',)})
    red({                                                     # differences from the published text, on their own slides only
        'Transverse 2PE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π': ('the 2PE signal of Eq. (6)',),
        'Axial 2PE PSF, annular pupils, NA 0.5: θ = 0, π/2 and π': ('the 2PE signal of Eq. (6)',),
        'Ratios stated in the text against the published curves': ('Three do not agree', '"0.67"', '"1.58', '"20%'),
        '2PE central spot at θ = π/2 relative to θ = 0, circular pupils': ('Stated:',),
        '2CE central spot relative to 2PE at θ = π/2, circular pupils': ('Stated:',),
        'Annular 2CE depth of focus relative to circular 2PE at θ = π/2': ('Stated:',),
        'Slopes against Δλ: current work, published points and caption fits': ('match neither',),
        '2PE with annular pupils: excitation |U₁ + U₂|² against the signal |U₁ + U₂|⁴': ('so they plot the excitation',),
        '2CE central spot and depth of focus against the wavelength gap Δλ, θ = π/2': ('FWHM slope',)})

pass                                                         # physics checks: see scripts/check_lim2002_physics.py
glossary()

# ── renumber, check legibility, embed at 600 dpi, save ──
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
FLOOR = 11.0          # pt; 16 arcmin (ISO 9241-3) at four slide heights on a 5.625-in slide
Image.MAX_IMAGE_PIXELS = None
low = set()
for path, shown in ds.FIGURES:
    if path.endswith('.png'):                                    # 24-pt smallest text at 600 dpi; the pair figures use 28 pt
        im = Image.open(path)
        small = 28 if os.path.basename(path).startswith('pairs_') else 24
        if 'cambaliza2000' in path.replace(os.sep, '/').split('/'):   # the 2color excitation scripts: 28-pt smallest text
            small = 28
        if os.path.basename(os.path.dirname(path)) == 'evidence' and os.path.basename(path) in ('fig5_caption.png', 'rotation.png'):
            small = 31
        if os.path.basename(path) == 'fig5_overlay.png':
            continue                                             # the published scan; its text is the paper's own                                           # panel-slot figures of evidence_cambaliza2000.py: 31-pt legend
        pt = small * shown / (im.size[0] / (im.info.get('dpi') or (600, 600))[0])
        if pt < FLOOR:
            low.add((os.path.basename(path), round(pt, 1)))
done = set()
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.shape_type != 13:
            continue
        ipart = sh.part.related_part(sh._element.blipFill.blip.rEmbed)
        if id(ipart) in done:
            continue
        im = Image.open(io.BytesIO(ipart.blob))
        w = int(round(600 * sh.width / 914400))
        if im.size[0] > 1.05 * w:
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB').resize((w, int(round(w * im.size[1] / im.size[0]))), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', dpi=(600, 600), optimize=True)
            ipart._blob = buf.getvalue()
        done.add(id(ipart))
if SECTION == CMEETING:                                         # slide manifest for the dashboard
    import json
    import re
    man = []
    for i, sl in enumerate(prs.slides, 1):
        rec = _REC.get(sl.slide_id, {'figs': [], 'eqs': [], 'labels': []})
        dark = sl.background.fill.type is not None and sl.background.fill.fore_color.rgb == NAVY
        title_, sub, items, texts = '', '', [], []
        for sh in sl.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            top, left, txt = sh.top / 914400, sh.left / 914400, sh.text_frame.text.strip()
            if (abs(left - 9.0) < 0.01 and abs(top - 5.28) < 0.01) or re.fullmatch(r'\(\d+\)', txt) \
                    or txt.startswith('where ') or txt in rec['labels']:
                continue
            if not title_:
                title_ = txt
                continue
            if not dark and abs(top - 0.78) < 0.01 and abs(left - 0.5) < 0.01:
                sub = txt
                continue
            for para in sh.text_frame.paragraphs:
                t_ = para.text.strip()
                if not t_:
                    continue
                cols = {str(r_.font.color.rgb) for r_ in para.runs if r_.font.color and r_.font.color.type is not None}
                tag = 'diff' if str(RED) in cols else 'ok' if str(GREEN) in cols else ''
                pp = para._p.pPr
                sub_item = t_.startswith('– ') or (pp is not None and pp.get('marL') == '457200')   # '– ' items of bullets()
                items.append({'text': t_[2:] if t_.startswith('– ') else t_, 'sub': sub_item, 'tag': tag})
                texts.append(t_)
        body = sl.notes_slide.notes_text_frame.text if sl.has_notes_slide else ''
        main_ = body.split('\n\n')[0].replace('MAIN POINT: ', '') if body else ''
        script_ = body.split('\n\n')[1] if body.count('\n\n') >= 1 else ''
        kind = 'title' if i == 1 else 'section' if dark else 'glossary' if title_.startswith('Glossary') else 'slide'
        man.append({'n': i, 'kind': kind, 'title': title_, 'subtitle': sub, 'items': items, 'figs': rec['figs'],
                    'labels': rec['labels'], 'eqs': rec['eqs'], 'main': main_, 'notes': script_})
    MAN = os.path.join(HERE, '..', 'output', '08_two_color', 'decks', '2ce_meeting_manifest.json')
    os.makedirs(os.path.dirname(MAN), exist_ok=True)
    json.dump(man, open(MAN, 'w'), ensure_ascii=False, indent=1)
    print('Manifest ->', os.path.abspath(MAN))
OUT = os.path.join(DIR, {MEETING: '2ce_meeting_2026-10-15.pptx', 'cambaliza': '2ce_cambaliza_replication.pptx',
                         CMEETING: '2ce_meeting_cambaliza.pptx'}.get(
    SECTION) or f'2ce_{SECTIONS.index(SECTION):02d}_{SECTION}.pptx')
os.makedirs(os.path.join(DIR, 'pdfs'), exist_ok=True)
ds.keynote_fonts()
prs.save(OUT)
# Keynote rejects the file as written by python-pptx; a re-save in place through PowerPoint makes it load. Opening through
# Finder (open -a) lets the sandboxed PowerPoint access a new file. Then export the PDF.
subprocess.run(['open', '-a', 'Microsoft PowerPoint', OUT])
import time as _time
_time.sleep(8)
subprocess.run(['osascript', '-e', f'''tell application "Microsoft PowerPoint"
save active presentation
save active presentation in POSIX file "{os.path.join(DIR, 'pdfs', os.path.basename(OUT)[:-5])}.pdf" as save as PDF
close active presentation saving no
end tell'''], capture_output=True)
for f in (OUT, os.path.join(DIR, 'pdfs', os.path.basename(OUT)[:-5] + '.pdf')):   # PowerPoint marks its saves as
    if os.path.exists(f):                                                            # quarantined, which Keynote refuses;
        data = open(f, 'rb').read()                                                  # a fresh copy drops the mark
        os.remove(f)
        open(f, 'wb').write(data)
print(f'Saved -> {OUT} ({len(prs.slides)} slides)' + (f'; below {FLOOR:g} pt: {sorted(low)}' if low else ''))
