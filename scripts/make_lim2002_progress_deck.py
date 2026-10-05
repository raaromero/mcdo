r"""Progress report on two-color excitation (2CE), one deck per section.

  00 overview     overall summary, next steps
  01 replication  scalar 2CE rebuilt from the paper (make_lim2002_replication_deck.py)
  02 vector       vector 2CE, uniform input, against NA
  03 fidelity     Linfoot's criteria F, C, Q against NA
  04 gaussian     vector 2CE, Gaussian input (α_t = 4): the results of 02 and 03
  05 delay        a delay in time between continuous beams
  06 delay_space  2PE: a delay in time against a misalignment in space

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
from mcdo.deckstyle import (CARD, FIG, GREY, MSO_SHAPE, NAVY, PALE, PURPLE, RED, WHITE, bullets, card, dots, equation,
                            figure, notes, prs, shape, slide, text, where)

SECTIONS = ['overview', 'replication', 'vector', 'fidelity', 'gaussian', 'delay', 'delay_space']
SECTION = os.environ.get('SECTION')
DIR = os.path.expanduser('~/Downloads/Research/two_color')
HERE = os.path.dirname(__file__)
SL = lambda name: os.path.join(FIG, 'slides', name)
PD = lambda name: os.path.join(FIG, 'phase_delay', name)
ds.CITE = ''

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
    figure(s, path, 0.45, 0.95, 9.1, 3.72)
    bullets(s, 0.6, 4.72, 8.9, 0.55, items, 11.5)
    notes(s, main, script, latex)


def side(name, path, items, main, script, latex=None, fw=5.3):
    s = slide(name, '')
    figure(s, path, 0.45, 0.95, fw, 4.25)
    bullets(s, 0.45 + fw + 0.25, 1.05, 9.5 - fw - 0.7, 4.15, items, 12)
    notes(s, main, script, latex)


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
    'Vector 2CE': ('the same signals with the Richards–Wolf focus (exact phase and polarization)', 'overview vector fidelity gaussian'),
    'Scalar Debye': ('scalar focus with the exact phase, no polarization', 'vector'),
    'Peak lost': ('drop of the peak of the misaligned PSF, in percent of the aligned peak', 'replication vector gaussian delay delay_space'),
    '20% tolerance': ('the misalignment x_c or z_c that reduces the 2CE peak by 20%', 'vector gaussian'),
    'F, C, Q': ('Linfoot’s criteria: fidelity, structural content and correlation quality', 'replication fidelity gaussian delay'),
    'α_t': ('truncation parameter of the Gaussian input; 0 is uniform input', 'overview gaussian'),
    'Unpolarized': ('averaged over two perpendicular input polarizations, equal to circular', 'vector fidelity gaussian'),
    'Δt, φ': ('delay of beam 2; the phase it adds, φ = ωΔt', 'overview delay delay_space'),
    'K': ('fringe wavevector of the two 2PE beams, |K| = 2k sin(θ/2)', 'delay delay_space'),
}


def glossary():
    rows = [f'{t}: {m}.' for t, (m, use) in GLOSS.items() if use == 'all' or SECTION in use.split()]
    pages = [rows[i:i + 9] for i in range(0, len(rows), 9)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''), '')
        bullets(s, 0.6, 1.1, 8.9, 4.1, page, 12.5)
        notes(s, 'Glossary.', ' '.join(page))


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
    s = slide(title, takeaway)
    w = 9.0 if side is None and fig is None else (5.9 if fig is None else 5.5)
    t = 1.4
    for tex, wh in eqs:
        h = equation(s, 0.55, t, w, tex, size)
        t += h + 0.06
        if wh:
            t += where(s, 0.6, t, w - 0.6, wh)
        t += 0.1
    if side:
        head, lines = side
        card(s, 6.75, 1.4, 2.75, 3.7, head, RED, lines, 10.5, bulleted=False)
    if fig:
        figure(s, fig, 6.15, 1.35, 3.4, 3.8)
    notes(s, main, script, latex)
    return s


ZB = r'z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta'
UPAR = r'U(u,v) \propto e^{ikz}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\,\rho\, d\rho'


def scalar_fields():
    eqslide('Field equations: scalar 2CE', 'Each beam is the paraxial scalar Debye field; beam 2 is the same field rotated by θ '
            'and centred at O′.', [
        (UPAR, 'r, z = distance from the focus across and along the axis; ρ = radius in the pupil over its edge.'),
        (r'u = \frac{k\,\mathrm{NA}^2 z}{n}, \qquad v = k\,\mathrm{NA}\, r, \qquad k = \frac{2\pi n}{\lambda}',
         'u, v = axial and transverse optical coordinates; λ = vacuum wavelength; n = refractive index.'),
        (ZB, 'x_b, z_b = coordinates of beam 2, rotated by θ about O′ = (x_c, z_c).'),
        (r'F_{2c} = \kappa_{2c}\, I_1 I_2, \qquad F_{2p} = \kappa_{2p}\, |U_1 + U_2|^4', 'I = |U|^2; 2CE multiplies the two '
         'intensities, 2PE adds the two fields.')],
        'The scalar 2CE model: paraxial fields, beam 2 rotated and shifted, 2CE as a product and 2PE as a sum.',
        'The model of the paper, used for the delay study at NA 0.5.',
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
    side('The θ = π/2 lens problem', os.path.join(os.path.dirname(FIG), 'na_crossing_general.png'), [
        'Each lens fills a cone of half-angle α around its axis, with sin α = NA/n.',
        'Two lenses with axes at an angle θ fit side by side while α ≤ θ/2, that is NA ≤ n sin(θ/2).',
        'At θ = π/2 this is NA 0.71 in air, 0.94 in water and 1.07 in oil.',
        'Crossed-beam results above these values are hatched: they assume both full cones reach the focus.'],
        'Crossed lenses fit up to NA n sin(theta/2).',
        'The limit is geometric: two cones meeting at a right angle overlap once their half-angles exceed 45 degrees.',
        r'\mathrm{NA} \le n \sin(\theta/2)', fw=5.0)


FCQ = (r'F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \qquad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, '
       r'\qquad Q = \frac{\langle t\, a \rangle}{\langle t^2 \rangle}')
SPOT = r'\tilde{x} = \frac{x_c\,\mathrm{NA}}{\lambda}, \qquad \tilde{z} = \frac{z_c\,\mathrm{NA}^2}{n\lambda}'


def linfoot():
    eqslide('Linfoot’s criteria', 'Fidelity, structural content and correlation quality compare the misaligned PSF with the '
            'aligned PSF over the window.', [
        (FCQ, 't = aligned PSF; a = misaligned PSF, each scaled to its own peak; ⟨ ⟩ = mean over the window.'),
        (r'2Q - C = F', 'each criterion is 1 when a = t; we follow where each stays within 20%: F ≥ 0.8, Q ≥ 0.8, C ≤ 1.2.'),
        (SPOT, 'misalignment in units of the spot; for 2PE, misalignments along the fringes are in λ/n. In these units scalar 2CE '
               'gives the same map at all NAs.')],
        'Linfoot’s three criteria compare the misaligned PSF with the aligned one.',
        'Measured in units of the spot, a spot that only shrinks with NA gives the same map at all NAs.',
        '\n'.join((FCQ, r'2Q - C = F', SPOT)),
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


def linfoot_maps(suf, tag):
    for case, lab in CASES:
        for key in 'FCQ':
            path = SL(f'fidelity_{case}{suf}.png' if key == 'F' else f'linfoot{key}_{case}{suf}.png')
            what = LINF_G[(case, key)] if suf else LINF[(case, key)]
            side(f'{NAME[key]}{tag}: {lab}' if suf else f'{NAME[key]} against NA: {lab}', path, [
                f'Each line is the contour {LEV[key]} at one NA, from low NA (dark) to NA 1.2 (yellow), in units of the spot.',
                what],
                f'{lab}: {NAME[key].lower()} against NA.',
                'Solid: vector 2CE in air, to NA 0.99; dashed: water, to NA 1.2; red dotted: scalar 2CE, the same at all NAs in '
                'these units.', fw=5.3)


FIGTXT = {
    (2, 'a'): ('2CE, θ = π', 'At NA 0.9 the aligned 2CE spot is a little over half as wide and about a third as long as at '
               'NA 0.5, so it is less elongated.'),
    (2, 'b'): ('2PE, θ = π', 'The 2PE standing wave keeps its fringe spacing, λ_{2p}/2, while the spot around it shrinks; at '
               'NA 0.9 it holds a few fringes.'),
    (2, 'c'): ('2CE, θ = π/2', 'With crossed beams the aligned 2CE spot is set by the widths of the two beams, so it changes '
               'little between NA 0.5 and 0.7.'),
    (2, 'd'): ('2PE, θ = π/2', 'The tilted 2PE fringes remain; at NA 0.7 the side fringes are weaker as the spot shrinks.'),
    (3, 'a'): ('2CE, θ = π', 'With O′ at (0.4, 1.0) µm the 2CE spot still forms between O and O′; at NA 0.9 it is smaller and '
               'tilted toward O′.'),
    (3, 'b'): ('2PE, θ = π', 'At NA 0.9 the misaligned 2PE spot breaks into a few separate fringes between O and O′.'),
    (3, 'c'): ('2CE, θ = π/2', 'With crossed beams the misaligned 2CE spot follows beam 2 along z at both NAs.'),
    (3, 'd'): ('2PE, θ = π/2', 'The misaligned 2PE spot breaks into separate pieces along the fringes at both NAs.'),
    (4, 'a'): ('2CE, θ = π', 'The misalignments that keep 80% of the 2CE peak reach about ±2 µm along the axis at NA 0.5 and '
               'about ±0.5 µm at NA 0.9.'),
    (4, 'b'): ('2PE, θ = π', 'The 2PE peak map shrinks in the same way; the standing-wave fringes make it vary slightly along z.'),
    (4, 'c'): ('2CE, θ = π/2', 'With crossed beams the 2CE peak barely depends on x_c at either NA; the range along z_c shrinks '
               'as the beams narrow.'),
    (4, 'd'): ('2PE, θ = π/2', 'The tilted bands of the 2PE peak map, from interference, narrow at NA 0.7.'),
}


def maps(suf, tag):
    for (no, t), (lab, line) in FIGTXT.items():
        na2 = '0.7' if 'π/2' in lab else '0.9'
        where = {2: 'aligned foci', 3: 'O′ at (0.4, 1.0) µm', 4: 'peak against the misalignment (x_c, z_c)'}[no]
        if suf and no == 4:
            line = ('With the Gaussian input the region that keeps the peak is larger than with uniform input at the same NA, '
                    'and it shrinks in the same way as NA grows.')
        elif suf:
            line = ('With the Gaussian input the spot is wider and longer than with uniform input at the same NA, and it shrinks '
                    'in the same way as NA grows.')
        wide(f'Fig. {no}({t}) against NA{tag}: {lab}', SL(f'map_fig{no}{t}{suf}.png'), [line],
             f'Fig. {no}({t}) of scalar 2CE at NA 0.5 and {na2}.',
             f'Fig. {no}({t}) of scalar 2CE, {lab}, {where}, with vector 2CE at NA 0.5 and {na2}, on the same axes. Heat '
             'map: percent of the peak; white lines: 20, 50 and 80 percent. Crossed beams stop at NA 0.7, where the lenses '
             'still fit in air.')


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
LEGEND = ('Blue: vector 2CE; red: scalar 2CE, up to NA 0.5 (grey band); dashed: the reported scalar 2CE loss at NA 0.5.')


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
            items.append('Above NA 0.71 (hatched) the two lenses do not fit in air.')
        side(name, SL(f'peaklost_{k}{suf}.png'), items, f'{name}.', LEGEND)


NEXT = ['Polarization of the two beams: whether to account for it (unpolarized against linear polarization).',
        'Crossed lenses that do not physically fit above NA n sin(θ/2): report as computed values, or stop at that NA.',
        'Delay in time against NA, compared with scalar 2CE.',
        'Pulsed 2CE: how to account for the range of wavelengths in a pulse.']


SUMMARIES = {   # section: (main point, supporting, supporting, speaker script); the overview shows them all
    'overview': (
        'At high NA the 2CE alignment tolerances shrink with the size of the focus: with facing lenses, as 1/NA across the axis '
        'and 1/NA^2 along it.',
        'Rebuilt from its equations, scalar 2CE reproduces the paper: the 2CE PSF is more robust against misalignment than the 2PE '
        'PSF, most of all with crossed beams.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.45, which validates it there; a Gaussian input makes the '
        'tolerances about 1.4 times larger.',
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments along the axis than scalar 2CE predicts.',
        'A delay between continuous beams leaves the 2CE PSF unchanged but shifts the 2PE fringes, with the same effect as a '
        'misalignment of cΔt/n in space.',
        'With vector fields, the alignment tolerances follow the width and length of the focus as NA grows. The paper is '
        'reproduced, its scalar model agrees with the vector one where the paper uses it, a Gaussian input loosens the tolerances, '
        'and a delay acts on 2PE through its fringes while 2CE does not change.'),
    'replication': (
        'Rebuilt from its equations, the scalar 2CE model reproduces the six figures and, within a few percent, the losses '
        'reported in the paper.',
        'What holds: the 2CE PSF is more robust against misalignment than the 2PE PSF, most of all when the two beams cross at '
        'θ = π/2.',
        'What differs: C and Q are swapped in Figs. 5–6, Eq. (2) has to be applied as a rotation in space, Figs. 6(c)–(d) are '
        'most likely θ = 0, and the reported losses differ from ours by up to 3 points (20% against 18%, 30% against 27%).',
        'The figures and losses come back, and the conclusion holds. Four things differ: the C and Q labels, the rotation as '
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
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments along the axis than scalar 2CE predicts.',
        'In units of the spot the scalar 2CE maps are the same at all NAs, so the change comes from the vector focus.',
        'For 2PE, Linfoot’s criteria are set by the fringes, whose spacing does not depend on NA, and change little.',
        'Linfoot’s criteria of the paper, followed against NA. For 2CE the vector focus keeps a faithful PSF over a smaller range '
        'of misalignments than the paraxial model predicts. For 2PE the fringes set the criteria.'),
    'gaussian': (
        'With a Gaussian input (α_t = 4) the alignment tolerances are about 1.4 times larger than with uniform input.',
        'The dim edge of the pupil removes the high-angle rays, so the focus is wider and longer; at NA 0.5 the same '
        'misalignments cost about half the peak they cost with uniform input.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.525, against 0.45 with uniform input.',
        'With a Gaussian input the high-angle rays are dim, so the focus behaves like a lower NA: larger tolerances, and a '
        'paraxial model that holds to a higher NA.'),
    'delay': (
        'A delay Δt between continuous beams is a phase ωΔt: it leaves the 2CE PSF unchanged and shifts the 2PE fringes.',
        'The 2CE signal I_1 I_2 depends on intensities, which do not carry the phase.',
        'For 2PE at θ = π/2, half an optical period (1.17 fs) puts the centre on a dark fringe and loses 29% of the peak; at '
        'θ = π the peak stays but the fidelity drops to −0.85.',
        'Delaying a continuous beam multiplies its field by a phase. Two-color excitation multiplies intensities, so the phase '
        'drops out. Two-photon excitation adds fields, so the phase moves its fringes.'),
    'delay_space': (
        'For 2PE a delay Δt shifts the fringes by cΔt / [2n sin(θ/2)]; at θ = π/2 this equals a misalignment x_c or z_c of '
        'cΔt/n.',
        'The 2PE loss of a misalignment is mainly this fringe phase: the matching delay brings the loss of a 0.5 λ_{2p} '
        'misalignment from 26% to about 1%.',
        '2CE has no fringes, so its loss comes from how well the two foci overlap, and a delay cannot change it.',
        'A delay and a misalignment both change the phase of the 2PE fringes at the peak. The phase of a misalignment can be '
        'cancelled by a delay; the overlap of the two foci cannot.'),
}
PART_TITLE = {'replication': 'Part 1: Replication of scalar 2CE', 'vector': 'Part 2: Vector 2CE, uniform input',
              'fidelity': 'Part 3: Linfoot’s criteria against NA', 'gaussian': 'Part 4: Vector 2CE, Gaussian input',
              'delay': 'Part 5: Delay in time', 'delay_space': 'Part 6: Delay in time against misalignment in space'}


# ══ sections ═════════════════════════════════════════════════════════════
if SECTION == 'overview':
    title('Progress Report', 'Two-color excitation: scalar 2CE, vector 2CE, and delays in time')
    summary(*SUMMARIES['overview'])
    for sec, name in PART_TITLE.items():                     # one summary slide per section
        main, s1, s2, script = SUMMARIES[sec]
        sl = slide(name, '')
        bullets(sl, 0.6, 1.1, 8.9, 4.1, [main, '– ' + s1, '– ' + s2], 14, bold=True)
        notes(sl, main, script)
    words('Next steps', NEXT, 'Polarization, the crossed-lens limit, the delay against NA, then pulses.',
          'These are the next items, in order.')
    wide('Next steps: polarization of the two beams', SL('polarization_spot.png'), [
        'One beam at focus, across x. At high NA the focused spot is wider along the polarization than across it, so results '
        'across the axis can depend on the polarization. To review: whether to account for it, unpolarized against linear.'],
        'At high NA the spot depends on the polarization.',
        'Blue: field along y; red: field along x. At NA 0.5 the two nearly coincide; at NA 0.9 they differ.')
    side('Next steps: crossed lenses at high NA', os.path.join(os.path.dirname(FIG), 'na_crossing_general.png'), [
        'Two lenses with axes at an angle θ fit side by side while NA ≤ n sin(θ/2).',
        'At θ = π/2 this is NA 0.71 in air and 0.94 in water.',
        'To decide: report crossed-beam results above this NA as computed values, or stop at that NA.'],
        'Crossed lenses fit up to NA n sin(theta/2).', 'The limit is geometric.', r'\mathrm{NA} \le n \sin(\theta/2)', fw=5.0)
    side('Next steps: delay in time against NA', PD('time_vs_space.png'), [
        'So far the delay was computed with scalar 2CE at NA 0.5 (Parts 5–6).',
        'Next: the same delay with vector 2CE against NA, compared with scalar 2CE.',
        'Expected: the fringe period does not depend on NA, while the overlap of the two foci does.'],
        'The delay study, so far at NA 0.5, extended against NA.',
        'Peak lost against the delay and against the matching misalignment, 2PE, theta = pi/2, NA 0.5.')
    wide('Next steps: pulsed 2CE', SL('pulse_spectra.png'), [
        'A pulse contains a range of wavelengths, wider for shorter pulses. The 750 and 656 nm spectra overlap for pulses below '
        'about 8 fs. To settle: how to account for the range of wavelengths in each pulse.'],
        'A short pulse is a range of wavelengths; how to account for it is open.',
        'Spectra of the two pulses at 5 and 20 fs, transform-limited Gaussian pulses.')

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
            ('pi2', 'θ = π/2', 'With crossed beams both tolerances fall as about NA^{−2.1}: a misalignment in x_c is along the axis '
             'of beam 2 and one in z_c is along the axis of beam 1, so both follow the length of the focus.')):
        wide(f'20% tolerances against NA, {lab}', SL(f'tolerance_{key}.png'), [
            'The tolerance is the misalignment of O′ that reduces the 2CE peak by 20%. ' + line],
            f'At {lab} the 20% tolerances shrink as a power of NA.',
            'Blue: vector 2CE; red: scalar 2CE, up to NA 0.5; dashed: the reported scalar 2CE tolerance at NA 0.5.')
    wide('Scalar 2CE against vector 2CE, 20% tolerances', SL('deviation.png'), [
        'The difference between the 20% tolerances of scalar and vector 2CE passes 5% at NA 0.45 and 10% at NA 0.6 along the '
        'axis, and with crossed beams in both directions. Across the axis at θ = π it stays within 5% up to NA 0.8.'],
        'Scalar 2CE is within 5% up to NA 0.45; along the axis it departs first.',
        'The paraxial focus is longer than the vector one, so it overestimates the tolerance along the axis. Across the axis the two '
        'differ through polarization, which is small up to NA 0.8. The vertical line is NA 0.5, the value used in scalar 2CE.')
    wide('20% tolerances in water, θ = π', SL('tolerance_pi_n1.33.png'), [
        'In water (n = 1.33) the tolerances follow the same power laws. Scalar 2CE (not drawn) departs by 5% at NA 0.6 and 10% '
        'at NA 0.8, 1.33 times the values in air: the difference is set by the angle of the cone, sin α = NA/n.'],
        'In water scalar 2CE holds to 1.33 times the NA it holds to in air.',
        'The same 20% tolerances in water, up to NA 1.2.')
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
    title('Part 3: Linfoot’s criteria against NA', 'Linfoot’s criteria (F, C and Q) of the misaligned PSF, vector 2CE and scalar 2CE, NA 0.1 to 1.2')
    summary(*SUMMARIES['fidelity'])
    geometry(); vector_fields(); linfoot()
    linfoot_maps('', '')

elif SECTION == 'gaussian':
    title('Part 4: Vector 2CE, Gaussian input', 'Both lenses filled by a Gaussian beam, truncation parameter α_t = 4')
    summary(*SUMMARIES['gaussian'])
    geometry(); vector_fields()
    eqslide('Gaussian input: the pupil of both beams', 'Each lens is filled by a Gaussian beam truncated at α_t = 4; the '
            'same pupil amplitude on both lenses and for both wavelengths.', [
        (r'A(\beta) = \exp\left(-\alpha_t\, \frac{\sin^2\beta}{\sin^2\alpha}\right), \qquad \sin\alpha = \mathrm{NA}/n',
         'A(β) = pupil amplitude in the Richards–Wolf integrals; α_t = truncation parameter; 0 is uniform input.'),
        (r'A(\rho) = e^{-\alpha_t \rho^2}', 'the same amplitude in scalar 2CE, with ρ = radius in the pupil over its edge.'),
        (r'A(\rho = 1) = e^{-4} \approx 0.02 \quad (\alpha_t = 4)', 'the field at the edge of the pupil is about 2% of the '
                                                                     'centre, so the steepest rays carry little light.')],
        'Each lens is filled by a Gaussian beam truncated at alpha_t = 4.',
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
            'dashed line is the reported uniform-input scalar 2CE value at NA 0.5.'],
            f'Gaussian input: the tolerances at {lab} are larger by about 1.4.',
            'Blue: vector 2CE; red: scalar 2CE up to NA 0.5.')
    wide('Scalar 2CE against vector 2CE, Gaussian input', SL('deviation_at4.png'), [
        'With α_t = 4 the scalar 2CE tolerances depart by 5% at NA 0.525 and 10% at NA 0.7, against 0.45 and 0.6 for uniform '
        'input: the dim pupil edge removes the rays for which the small-angle phase is worst.'],
        'With a Gaussian input the paraxial focus holds to a higher NA.',
        'The difference between scalar and vector 20% tolerances, Gaussian input.')
    wide('20% tolerances in water, Gaussian input, θ = π', SL('tolerance_pi_at4_n1.33.png'), [
        'In water with α_t = 4 the tolerances follow the same power laws. Scalar 2CE (not drawn) departs by 5% at NA 0.7 and 10% '
        'at NA 0.9.'],
        'In water with a Gaussian input scalar 2CE holds to NA 0.7.', 'The same tolerances in water, up to NA 1.2.')
    lens_problem()
    peaks('_at4')
    linfoot()
    linfoot_maps('_at4', ', Gaussian input')

elif SECTION == 'delay':
    title('Part 5: Delay in time', 'A delay Δt between two continuous beams, scalar 2CE, NA 0.5')
    summary(*SUMMARIES['delay'])
    geometry(); scalar_fields()
    D1 = r'U_2(P, t - \Delta t) = U_2(P, t)\, e^{i\phi}, \qquad \phi = \omega\Delta t = \frac{2\pi c\,\Delta t}{\lambda}'
    D2 = r'F_{2c} = \kappa_{2c}\, I_1 \left|U_2 e^{i\phi}\right|^2 = \kappa_{2c}\, I_1 I_2'
    D3 = r'\left|U_1 + U_2 e^{i\phi}\right|^2 = I_1 + I_2 + 2|U_1 U_2| \cos(\mathbf{K}\cdot\mathbf{r} - \phi)'
    eqslide('Delay between continuous beams', 'A delay of a continuous beam is a phase: 2CE does not see it, the 2PE fringes '
            'move with it.', [
        (D1, 'Δt = delay of beam 2; φ = phase it adds; c = speed of light; λ = vacuum wavelength.'),
        (D2, '2CE multiplies intensities, which do not carry the phase.'),
        (D3, '2PE adds the fields, F_{2p} = κ_{2p}|U_1 + U_2 e^{iφ}|^4; K = fringe wavevector, |K| = 2k sin(θ/2): the delay moves '
             'the fringes.')],
        'A delay is a phase: 2CE does not see it, 2PE fringes move with it.',
        'For continuous beams a delay is a constant phase on beam 2. The two-color signal uses only intensities. The two-photon '
        'signal contains the interference term, whose fringes shift with the phase.', '\n'.join((D1, D2, D3)), size=17)
    words('Choice of delays: φ = 0, π/2, π', [
        'The effect of a delay repeats with each optical period: φ = 2π is Δt = λ/c, 2.33 fs at 700 nm.',
        'φ and 2π − φ give the same loss, so φ from 0 to π covers all delays.',
        'φ = 0 is the aligned case. φ = π/2 (Δt = 0.58 fs) moves the fringes by a quarter of their period. φ = π (Δt = 1.17 fs) '
        'moves them by half a period, so bright and dark fringes swap: the largest effect.',
        'φ = π is the delay in time that matches the 2PE misalignment of 0.5 λ_{2p} used in scalar 2CE.'],
        'One optical period covers every delay; pi is the largest effect.',
        'The delays are chosen as fractions of the optical period, the time version of misalignments in fractions of a '
        'wavelength.')
    wide('Peak lost and fidelity against the delay', PD('phase_delay.png'), [
        'The 2CE peak and shape do not change with the delay at either angle. For 2PE at θ = π/2 the peak drops to 71% at φ = π, '
        'as the centre falls on a dark fringe; at θ = π a bright fringe stays near the centre, so the peak stays but F drops '
        'to −0.85 as the standing wave moves.'],
        'The delay leaves 2CE unchanged and changes 2PE through its fringes.',
        'Left: peak lost against phi; right: fidelity F against the aligned PSF. The small zigzag of the 2PE theta = pi peak '
        'curve, under 1.3 percent, comes from the grid: the moving fringes fall between grid points.')

elif SECTION == 'delay_space':
    title('Part 6: Delay in time against misalignment in space', 'A delay of the 2PE beams compared with a misalignment of O′')
    summary(*SUMMARIES['delay_space'])
    geometry(); scalar_fields()
    K1 = r'\mathbf{K} = k\left(\hat{\mathbf{k}}_1 - \hat{\mathbf{k}}_2\right), \qquad |\mathbf{K}| = 2k\sin(\theta/2)'
    K2 = r'\Delta s = \frac{\phi}{|\mathbf{K}|} = \frac{c\,\Delta t}{2n\sin(\theta/2)}'
    K3 = r'\theta = \pi:\ \Delta z = \frac{c\,\Delta t}{2n}, \qquad \theta = \pi/2:\ x_c = z_c = \frac{c\,\Delta t}{n}'
    eqslide('Delay in time as a shift of the fringes', 'A delay moves the 2PE fringes along K; at θ = π/2 it matches a '
            'misalignment of cΔt/n.', [
        (K1, 'k̂_1, k̂_2 = directions of the two beams; k = 2πn/λ; the 2PE fringes vary as cos(K·r − φ).'),
        (K2, 'Δs = shift of the fringes along K for a delay Δt.'),
        (K3, 'the misalignment that gives the fringes the same phase as the delay.')],
        'A delay moves the 2PE fringes by c Delta t over 2n sin(theta/2).',
        'The fringe pattern of two plane waves has wavevector K, the difference of the two wavevectors. A phase phi moves it by '
        'phi over the magnitude of K.', '\n'.join((K1, K2, K3)), size=17)
    P1 = r'\phi_{eq} = \mathbf{K}\cdot\mathbf{r}_c + k\,\hat{\mathbf{k}}_2\cdot\mathbf{d}'
    P2 = r'\omega\,\Delta t = \phi_{eq}'
    eqslide('Misalignment in space as a phase', 'A misalignment changes the phase of the fringe at the peak; a delay of the '
            'same phase cancels it.', [
        (P1, 'd = misalignment of O′; r_c = centre of the overlap of the two beams; k k̂_2·d = phase beam 2 gains by moving along '
             'its own direction; K·r_c = fringe phase where the beams now overlap.'),
        (P2, 'a delay with this phase puts a bright fringe back on the peak.')],
        'A misalignment changes the fringe phase at the peak by phi_eq; a delay can cancel it.',
        'The phase has two parts: beam 2 moving along its own direction, and the overlap of the two beams moving to another '
        'fringe. At theta = pi the two cancel for a misalignment along z.', '\n'.join((P1, P2)),
        side=('Cases', ['θ = π/2: x_c = 0.5 λ_{2p} or z_c = 0.5 λ_{2p} gives φ_{eq} = π.', '',
                        'θ = π, misalignment along z: the two terms cancel, φ_{eq} = 0, so the fringe at the centre stays bright '
                        'and the peak barely drops.']), size=18)
    side('Delay and misalignment, 2PE, θ = π/2', PD('time_vs_space.png'), [
        'Peak lost against the delay Δt (bottom axis) and against a misalignment cΔt/n of the same phase (top axis). Up to half '
        'a period the curves follow each other. Beyond it the misalignment also moves the overlap of the two foci, so its loss '
        'peaks slightly later and does not return to zero after one wavelength, while the delay does.'],
        'A delay and the matching misalignment cost the 2PE peak about the same.',
        'Blue: delay, aligned foci. Red and green: misalignment x_c or z_c of c Delta t over n, no delay. Vertical lines: phi = '
        'pi/2, pi and 3 pi/2.')
    words('Cancelling a misalignment with a delay', [
        'At θ = π/2 a misalignment x_c = 0.5 λ_{2p} reduces the 2PE peak by 26%; with a delay of φ = 0.92π the loss is 1.3%.',
        'A misalignment z_c = 0.5 λ_{2p} gives the same: 26% without the delay and 1.3% with it.',
        'At x_c = 0.25 λ_{2p} the loss falls from 7% to 0.3% with φ = 0.46π.',
        'The best delays are slightly below the predicted π and π/2, most likely from the Gouy phase of the focused beams, which '
        'the plane-wave form leaves out.',
        'What remains, about 1%, is the loss of overlap of the two foci: the part 2CE also has.'],
        'The 2PE loss of a misalignment is mainly phase, and a delay removes most of it.',
        'Scalar model, NA 0.5. The delay that best restores the peak is close to phi_eq.', size=12.5)

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
    if path.endswith('.png'):                                    # every figure, assuming 24-pt text drawn at 600 dpi
        im = Image.open(path)
        pt = 24 * shown / (im.size[0] / (im.info.get('dpi') or (600, 600))[0])
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
            im = im.convert('RGB').resize((w, int(round(w * im.size[1] / im.size[0]))), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', dpi=(600, 600), optimize=True)
            ipart._blob = buf.getvalue()
        done.add(id(ipart))
OUT = os.path.join(DIR, f'2ce_{SECTIONS.index(SECTION):02d}_{SECTION}.pptx')
os.makedirs(os.path.join(DIR, 'pdfs'), exist_ok=True)
ds.keynote_fonts()
prs.save(OUT)
# Keynote rejects the file as written by python-pptx; a re-save through PowerPoint makes it load. Also export the PDF.
tmp = OUT.replace('.pptx', '.resaved.pptx')
subprocess.run(['osascript', '-e', f'''tell application "Microsoft PowerPoint"
open POSIX file "{OUT}"
save active presentation in POSIX file "{tmp}" as save as Open XML presentation
save active presentation in POSIX file "{os.path.join(DIR, 'pdfs', os.path.basename(OUT)[:-5])}.pdf" as save as PDF
close active presentation saving no
end tell'''], capture_output=True)
if os.path.getsize(tmp) if os.path.exists(tmp) else 0:
    os.replace(tmp, OUT)
print(f'Saved -> {OUT} ({len(prs.slides)} slides)' + (f'; below {FLOOR:g} pt: {sorted(low)}' if low else ''))
