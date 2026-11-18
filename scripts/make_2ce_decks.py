r"""The two 2CE decks, built from the same slide definitions:

    DECK=high_na  two-color excitation at high NA: the extension of Cambaliza & Saloma (2000) from the paraxial scalar
                  model at NA 0.5 to the vector (Richards–Wolf) focus at high NA, for collinear, crossed and facing lenses
    DECK=pulses   two-color excitation with femtosecond pulses at high NA, and the delay between the two pulses

    DECK=high_na python scripts/make_2ce_decks.py         -> output/08_two_color/decks/2ce_high_na.pptx
    DECK=pulses  python scripts/make_2ce_decks.py         -> output/08_two_color/decks/2ce_pulses.pptx
    MAIN=1 DECK=… python scripts/make_2ce_decks.py        -> …/2ce_high_na_main.pptx, 2ce_pulses_main.pptx (the main results)

Both decks start after the replication of Cambaliza & Saloma (2000) (presented on 2026-10-29) and show the extension.
Slides carried over from that meeting take their text word for word from scripts/approved_slides_2ce_meeting.py; the
delay slides come from scripts/pulse_delay_slides.py (shared with make_pulse_delay_deck.py). Slides with a matching view
in the dashboard carry a link to it (pulse_delay_slides.LINKS). Run scripts/pptx_resave_pdf.py on a deck afterwards so
that Keynote loads it, and look at the PDF before showing it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image

import mcdo.deckstyle as ds
from mcdo.deckstyle import NAVY, PALE, PURPLE, WHITE, bullets, dots, equation, figure, label, prs, slide, text, where

from approved_slides_2ce_meeting import SLIDES as APPROVED
from pulse_delay_slides import delay_slides, finish, fitted

Image.MAX_IMAGE_PIXELS = None
ds.CITE = ''
O = os.path.join(os.path.dirname(__file__), '..', 'output')
TC = os.path.join(O, '08_two_color')
CB = os.path.join(TC, 'cambaliza2000')
PU = os.path.join(CB, 'pulses')
OUT = os.path.join(TC, 'decks')
os.makedirs(OUT, exist_ok=True)
BOTTOM = 5.22                                                       # figures end above the page number ...
LOW = 5.45                                                          # ... or lower, when they end left of it
MISSING = []


def path(*p):
    f = os.path.join(*p)
    if not os.path.exists(f):
        MISSING.append(f)
    return f


def notes(s, main, script, latex=None):
    """Speaker notes in full sentences: the main point, the details, then the equations in LaTeX on their own lines."""
    body = f'{main}\n\n{script}'
    if latex:
        body += '\n\nThe equation in LaTeX is\n' + '\n'.join(ln.strip() for ln in latex.strip().splitlines())
    s.notes_slide.notes_text_frame.text = body


def navy(title, lines=()):
    s = prs.slides.add_slide(ds.BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    dots(s, 0.6, 0.7, 0.2, 0.27)
    text(s, 0.6, 1.15, 8.8, 1.5, title, 30, WHITE, True, 'Helvetica Neue')
    for i, (line, size, col) in enumerate(lines):
        text(s, 0.6, 2.85 + i * 0.4, 8.8, 0.4, line, size, col)
    return s


slide = fitted(slide)


def head(title, items):
    """Title and one or two one-line bullets; returns the slide and the top of the figure area."""
    s = slide(title, '')
    hb = sum(0.27 * -(-len(it) // 100) + 0.1 for it in items)          # about 100 characters per line at 13 pt
    bullets(s, 0.5, 0.86, 9.0, hb, items, 13)
    return s, 0.9 + hb


def fit(ratio, top, gaps=0.1):
    """Height of a figure (or of a row of panels whose widths add to ratio × height) that fills the slide: down to
    LOW when the row then ends left of the page number (framed width at most 7.9 in), else down to BOTTOM."""
    h = LOW - top - 0.1
    if ratio * h + gaps > 7.9:
        h = min(BOTTOM - top - 0.1, (9.7 - gaps) / ratio)
    return h


def big(title, items, fig, main, script, latex=None):
    """One or two one-line bullets and one figure across the full width of the slide."""
    iw, ih = Image.open(path(fig)).size
    if iw / ih < 1.4:                                   # one tall panel: bullets in a column beside it, so the figure
        s = slide(title, '')                            # takes the full height under the title
        bullets(s, 0.5, 1.2, 3.6, 3.5, items, 14)
        figure(s, fig, 4.3, 0.86, 5.55, BOTTOM - 0.86)       # above the page number
        notes(s, main, script, latex)
        return s
    s, top = head(title, items)
    h = fit(iw / ih, top)
    figure(s, fig, 0.15, top, 9.7, h + 0.1)
    notes(s, main, script, latex)
    return s


def pair(title, items, left, right, main, script, labels=None, latex=None):
    """One or two bullets and two panels side by side at the same height, as large as the slide allows; with labels,
    the published panel is on the left and current work on the right."""
    if isinstance(labels, str):                         # the equation for the notes, given without its keyword
        labels, latex = None, labels
    s, top = head(title, items)
    if labels:
        top += 0.27
    a1, a2 = (Image.open(path(f)).size for f in (left, right))
    r1, r2 = a1[0] / a1[1], a2[0] / a2[1]
    gap = 0.15
    h = fit(r1 + r2, top, gap + 0.2)
    w1, w2 = r1 * h, r2 * h
    l0 = (10 - (w1 + w2 + gap + 0.2)) / 2
    figure(s, left, l0, top, w1 + 0.1, h + 0.1)
    figure(s, right, l0 + w1 + 0.1 + gap, top, w2 + 0.1, h + 0.1)
    if labels:
        label(s, l0, top - 0.27, w1 + 0.1, labels[0])
        label(s, l0 + w1 + 0.1 + gap, top - 0.27, w2 + 0.1, labels[1], PURPLE)
    notes(s, main, script, latex)
    return s


def words(title, items, main, script, size=15, h=4.2):
    s = slide(title, '')
    bullets(s, 0.5, 0.95, 9.0, h, items, size)
    notes(s, main, script)
    return s



DECK = os.environ.get('DECK', 'high_na')
MAIN = bool(os.environ.get('MAIN'))
HN = os.path.join(CB, 'high_na')
NS = os.path.join(PU, 'na_sweep')
LO = os.path.join(TC, 'lim2002')


def approved(title, n=None, fig=None, new_title=None):
    """A slide of the meeting of 2026-10-29, with its title, bullets and notes word for word."""
    a = APPROVED[title]
    items = a['items'] if n is None else a['items'][:n]
    return big(new_title or title, items, path(O, fig or a['figs'][0]), a['main'], a['notes'])


def maps(sig, tk, title, items, main, script):
    return big(title, items, path(HN, 'maps', f'psf_{sig}_{tk}.png'), main, script)


GLOSS_CW = [
    'NA: numerical aperture, n sin α; α is the half-angle of the focusing cone and n the refractive index of the medium.',
    'L1, L2; O: the two lenses and their common focus, the origin.',
    'θ: angle between the two lens axes (0 collinear, π/2 crossed, π facing).',
    'λ_1, λ_2, λ_{2p}: 2CE wavelengths 750 and 656 nm, with 1/λ_e = 1/λ_1 + 1/λ_2 and λ_e = 350 nm; 2PE wavelength 700 nm.',
    '2CE, 2PE: two-color excitation, signal ∝ I_1 I_2; two-photon excitation, signal ∝ |U_1 + U_2|^4.',
    'PSF: point spread function: the fluorescence from one point, scaled to its peak.',
    'Central spot, depth of focus (DOF): FWHM of the PSF across and along the axis.']
GLOSS_MODEL = [
    'Paraxial scalar model: small-angle phase, no polarization (Cambaliza & Saloma, 2000, Eq. 1).',
    'Vector focus: the Richards–Wolf focus (exact phase and polarization), both beams polarized perpendicular to the plane '
    'of the lens axes.',
    "F, C, Q: Linfoot's criteria: fidelity, structural content and correlation quality.",
    'ε: obstruction ratio of an annular pupil, inner radius over outer radius.',
    'α: truncation parameter of the Gaussian input; 0 is uniform input.']
GLOSS_PULSE = [
    'τ: pulse width: full width at half maximum of the intensity; Δν = 0.441/τ for a transform-limited pulse.',
    '350-nm, 375-nm and 328-nm pairs: photon pairs of 750 + 656 nm, 750 + 750 nm and 656 + 656 nm.',
    'Δt: delay of the 656-nm pulse relative to the 750-nm pulse.']


def glossary(extra=()):
    words('Glossary (1/2)', GLOSS_CW, 'Glossary.', 'Symbols and terms used in the deck.', size=13)
    words('Glossary (2/2)', GLOSS_MODEL + list(extra), 'Glossary.', 'Symbols and terms used in the deck.', size=13)


def title_slide(title, line):
    s = navy(title, [('Roland Albert A. Romero', 18, WHITE),
                     ('National Institute of Physics, University of the Philippines Diliman', 13, PALE), (line, 13, PALE)])
    notes(s, title + '.', 'Cambaliza & Saloma, Opt. Commun. 184, 25 (2000). Lim & Saloma, Opt. Commun. 207, 121 (2002), and '
          'Appl. Opt. 42, 3398 (2003). Romallosa, Bantang & Saloma, Phys. Rev. A 68, 033812 (2003).')


if DECK == 'high_na':
    title_slide('Two-color excitation at high NA',
                'Extension of Cambaliza & Saloma (2000) from the paraxial scalar model to the vector (Richards–Wolf) focus')
    words('Summary', [
        'Extended the 2CE and 2PE point spread functions of Cambaliza & Saloma (2000) from NA 0.5 to high NA, with the '
        'vector (Richards–Wolf) focus in place of the paraxial scalar model, in air and in water.',
        'Compared the two models for collinear, crossed and facing lenses, at NA 0.5 and as NA increases, with the central '
        "spot, the depth of focus, the side lobes and Linfoot's criteria.",
        'Found that the paraxial model gives the central spot of the vector focus up to NA 0.86 in air, but overestimates '
        'the depth of focus above NA 0.43, by 7% at NA 0.5 and by 36% at NA 0.9.',
        'Found that with crossed lenses the paraxial and vector PSFs agree within 4% wherever the two lenses fit, and the '
        '2PE central spot keeps its width of 0.26 µm at all NAs.',
        'Found that the conclusions of Cambaliza & Saloma (2000) hold at high NA, while the differences between 2PE and '
        '2CE shrink: the 2PE side lobes weaken and the 2CE spot approaches the 2PE one.'],
        'The paraxial model of Cambaliza & Saloma (2000) gives the spot at high NA but makes the focus too long.',
        'Air unless a slide says otherwise; the same comparisons in water are on the slides of widths against NA. Crossed '
        'lenses fit up to NA 0.71 in air and 0.94 in water. The paraxial depth of focus is 5% longer than the vector one from '
        'NA 0.43 in air (0.57 in water); the central spot stays within 5% up to NA 0.86 (1.14 in water).', size=14, h=4.3)
    s = slide('Two-color excitation with two confocal beams at an angle θ', '')
    figure(s, path(TC, 'setup_model.png'), 0.4, 0.95, 4.2, 4.25)
    bullets(s, 4.85, 0.95, 4.75, 1.9, [
        'Lens L2 is lens L1 rotated by θ about the common focus O; L1 focuses 750 nm and L2 656 nm.',
        '2CE absorbs one photon of each color, so the signal is the product of the two intensities.',
        '2PE uses 700 nm in both beams, so the two fields add first and interfere.'], 13)
    EQ1 = r'\frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}'
    EQ2 = r'F_{2c} = \kappa\, I_1 I_2'
    EQ3 = r"F_{2p} = \kappa'\, |U_1 + U_2|^4"
    t = 2.95
    for tex in (EQ1, EQ2, EQ3):
        t += equation(s, 5.0, t, 4.5, tex, 20) + 0.12
    where(s, 5.0, t + 0.05, 4.5, 'λ_e = 350 nm; I_1 and I_2 are the focused intensities and U_1 and U_2 the fields; '
          'θ = 0, π/2 and π are collinear, crossed and facing lenses.', 11)
    notes(s, 'Two lenses focus two colors onto one point, at an angle θ.',
          'Cambaliza & Saloma (2000), pp. 26–28. 2CE absorbs one photon of each beam, so it forms where the two beams '
          'overlap; the two beams do not interfere. Two-photon excitation (2PE) uses one wavelength in both lenses, so '
          'the two fields add and interfere before the fourth power. κ and κ′ are the fluorescence cross-sections. Lim & '
          'Saloma (2002) displace the focus of L2 by x_c across and z_c along the axis of L1, and Lim & Saloma (2003) give '
          'each beam a primary spherical aberration.', '\n'.join((EQ1, EQ2, EQ3)))


    EQ_P = r'U(u, v) = e^{ikz}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\,\rho\, d\rho'
    EQ_A = r'1 - \cos\alpha \approx \frac{\sin^2\alpha}{2}, \qquad \frac{\mathrm{DOF}_{\mathrm{paraxial}}}{\mathrm{DOF}_{\mathrm{vector}}} \approx 1 + \tan^2\frac{\alpha}{2}'
    s = slide('Paraxial scalar model and vector (Richards–Wolf) focus', '')
    bullets(s, 0.5, 0.95, 9.0, 1.45, [
        'The paraxial model of Cambaliza & Saloma (2000, Eq. 1) uses the small-angle form of the phase of each ray, which '
        'makes the focus too long at high NA.',
        'The vector (Richards–Wolf) focus keeps the exact phase and the three field components; both beams are polarized '
        'perpendicular to the plane of the lens axes.'], 13)
    h = equation(s, 1.5, 2.5, 7.0, EQ_P, 20)
    h += equation(s, 1.5, 2.7 + h, 7.0, EQ_A, 20)
    where(s, 1.5, 2.95 + h, 7.0, 'u = (2π/λ) NA² z/n and v = (2π/λ) NA r are the optical coordinates along and across the '
          'axis, and α is the half-angle of the focusing cone, sin α = NA/n. At NA 0.5 the factor 1 + tan²(α/2) is 1.07 and '
          'at NA 0.9 it is 1.39.', 12)
    notes(s, 'The two models differ in the phase of each ray; the difference grows with the half-angle of the cone.',
          'The paraxial phase −uρ²/2 is the small-angle form of kz cos ϑ. With 1 − cos α replaced by sin²α/2 the depth of focus '
          'is lengthened by the factor 1 + tan²(α/2). The scalar Debye integral with the exact phase gives the vector '
          'profile along the axis, so the phase, not the polarization, causes the difference along the axis.', EQ_P + '\n' + EQ_A)

    maps('2ce', '0', '2CE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0 and π', [
        'At NA 0.5, the paraxial and vector 2CE PSFs with collinear and facing lenses coincide across the axis, and the '
        'paraxial PSF is 7% longer along it.',
        'At NA 0.9, the paraxial PSF is 6% wider and 36% longer than the vector one, so the paraxial model overestimates '
        'the depth of focus at high NA.'],
        'At high NA the paraxial 2CE focus is too long with collinear and facing lenses.',
        'Heat map: vector PSF; solid contours: vector, at 10, 50 and 90% of the peak; dashed: paraxial scalar. Air, circular '
        'pupils. The 2CE PSF is the same with collinear and facing lenses, since I_1 I_2 does not depend on the direction '
        'of beam 2. FWHM across the axis 0.510 µm (vector) and 0.516 µm (paraxial) at NA 0.5, 0.270 and 0.286 µm at NA 0.9; '
        'depth of focus 3.33 and 3.56 µm at NA 0.5, 0.81 and 1.10 µm at NA 0.9.')
    approved('Central spot and depth of focus against NA: 2CE, θ = 0 and π')
    maps('2ce', 'pi2', '2CE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2', [
        'With crossed lenses, the paraxial and vector 2CE PSFs coincide within 1.4% at NA 0.5 and 3.4% at NA 0.7, the '
        'largest NA at which two crossed lenses fit in air.',
        'Each width of the crossed-lens PSF is set by the narrow transverse spot of the other beam, which the paraxial '
        'model reproduces.'],
        'With crossed lenses the paraxial model gives the 2CE PSF of the vector focus.',
        'Heat map: vector PSF; solid contours: vector, at 10, 50 and 90% of the peak; dashed: paraxial scalar. FWHM 0.752 by '
        '0.662 µm (vector) and 0.763 by 0.670 µm (paraxial) at NA 0.5; 0.521 by 0.461 µm and 0.539 by 0.476 µm at NA 0.7.')
    approved('Central spot and depth of focus against NA: 2CE, θ = π/2')
    maps('2pe', '0', '2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0', [
        'With collinear lenses the 2PE PSF has the shape of the 2CE PSF, and the paraxial model departs from the vector '
        'focus in the same way: 7% longer at NA 0.5 and 36% longer at NA 0.9.'],
        'With collinear lenses 2PE and 2CE depart from the vector focus in the same way.',
        'Heat map: vector PSF; solid: vector; dashed: paraxial scalar; contours at 10, 50 and 90% of the peak. FWHM 0.511 µm '
        'and depth of focus 3.33 µm (vector) at NA 0.5; 0.271 and 0.81 µm at NA 0.9.')
    approved('Central spot and depth of focus against NA: 2PE, θ = 0')
    maps('2pe', 'pi2', '2PE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2', [
        'With crossed lenses the 2PE central spot is one interference fringe of the two beams, 0.256 µm wide in both '
        'models at NA 0.5 and at NA 0.7.',
        'As NA increases, the fringes beside the central spot weaken, so the 2PE PSF approaches a single spot.'],
        'With crossed lenses the 2PE central spot does not change with NA.',
        'Heat map: vector PSF; solid: vector; dashed: paraxial scalar; contours at 10, 50 and 90% of the peak. The two models '
        'differ by 0.1% at NA 0.5 and 0.4% at NA 0.7. The side lobe falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7.')
    approved('Central spot and depth of focus against NA: 2PE, θ = π/2')
    maps('2pe', 'pi', '2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = π', [
        'With facing lenses the 2PE PSF is a standing wave along the axis, with fringes about λ_{2p}/2 = 350 nm apart in '
        'both models; the spacing widens slightly as NA increases, because the converging waves cross the axis at an angle.',
        'At NA 0.9, the paraxial envelope is longer than the vector one, so the paraxial PSF has side fringes above 10% of '
        'the peak (dashed) where the vector PSF has none.'],
        'With facing lenses the 2PE standing wave keeps its fringes; the paraxial envelope is too long at high NA.',
        'Heat map: vector PSF; solid: vector; dashed: paraxial scalar; contours at 10, 50 and 90% of the peak. The central '
        'fringe is 0.136 µm long at NA 0.5 in both models and 0.166 µm (vector) against 0.158 µm (paraxial) at NA 0.9; '
        'across the axis the paraxial spot is 1.2% wider at NA 0.5 and 5.9% wider at NA 0.9. The fringe spacing is about '
        '0.37 µm at NA 0.5 and 0.44 µm at NA 0.9, compared to λ_{2p}/2 = 0.35 µm.')
    approved('Central spot and depth of focus against NA: 2PE, θ = π')
    approved('Paraxial over vector widths of 2CE against NA')
    approved('Paraxial over vector widths of 2PE against NA')
    approved('Whole-profile difference of 2CE, paraxial against vector')
    approved("Linfoot’s criteria against NA: 2CE, θ = 0 and π")
    approved("Linfoot’s criteria against NA: 2CE, θ = π/2")
    approved('2PE and 2CE central spots against NA, circular pupils')
    approved('2CE and 2PE depth of focus against NA, θ = π/2')
    approved('Side lobes of 2PE against NA: distance from the peak and height')
    approved('Annular pupils: depth of focus against NA, air')
    approved('Annular central spots against NA: the comparisons of p. 31')
    approved('Annular depth of focus against NA: the comparisons of p. 32')
    approved('2CE response to the wavelength gap Δλ against NA, θ = π/2')
    big('Largest NA of two crossed lenses', [
        'Two lenses with crossed axes (θ = π/2) fit side by side while the half-angle of each focusing cone is at most 45°, so NA ≤ n sin 45°: 0.71 in air and 0.94 in water.',
        'Cambaliza & Saloma (2000) note that dual-beam excitation with two identical objectives is possible for NA ≤ 0.7 (p. 34).'],
        os.path.join(TC, 'na_crossing_limit_air.png'),
        'Crossed lenses of the same NA fit up to NA n/√2.',
        'The half-angle of each cone must be at most 45°, so NA ≤ n sin 45° = n/√2: 0.71 in air and 0.94 in water. '
        'Cambaliza & Saloma (2000), p. 34: dual-beam excitation with two identical objectives for 0 ≤ θ ≤ π/2 is possible '
        'for NA ≤ 0.7.',
        r'\mathrm{NA} \le n \sin 45^\circ = \frac{n}{\sqrt{2}}')


    words('Summary: high NA', APPROVED['Summary: high NA']['items'], APPROVED['Summary: high NA']['main'],
          APPROVED['Summary: high NA']['notes'], size=14, h=4.3)
    glossary()
    navy('Backup')
    approved('Whole-profile difference of 2PE, paraxial against vector')
    approved("Linfoot’s criteria against NA: 2PE, θ = 0")
    approved("Linfoot’s criteria against NA: 2PE, θ = π/2")
    approved("Linfoot’s criteria against NA: 2PE, θ = π")
    big('Axial 2CE PSF at NA 0.5 and NA 0.9: paraxial and vector focus', [
        'At NA 0.5, the paraxial scalar and vector 2CE distributions along the axis nearly coincide: the paraxial depth of focus is 7% longer.',
        'At NA 0.9, the paraxial depth of focus is 36% longer than the vector one (1.10 µm compared to 0.81 µm), because the paraxial model uses the small-angle form of the phase of each ray.'],
        os.path.join(LO, 'slides', 'axial_2ce_paraxial_vector_na0.5_na0.9.png'),
        'At high NA the paraxial model gives too long a 2CE focus.',
        'Continuous beams, 750 and 656 nm, air, uniform input; red dashed: paraxial scalar; blue: vector (Richards–Wolf). '
        'The 2CE depth of focus is 3.56 µm against 3.33 µm at NA 0.5, and 1.10 µm against 0.81 µm at NA 0.9. The profile '
        'along the axis is the same with collinear and facing lenses, since I_1 I_2 does not depend on the direction of '
        'beam 2. The scalar Debye integral with the exact phase gives the vector profile along the axis, so the '
        'small-angle phase of the paraxial model causes the difference.',
        r'1 - \cos\alpha \approx \frac{\sin^2\alpha}{2}')

    SLD = os.path.join(LO, 'slides')
    big('Misalignment for a 20% loss of the 2CE peak against NA, θ = π', [
        'As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis and 1/NA² along it, following the width and the length of the focus.',
        'The paraxial scalar model overestimates the tolerated misalignment along the axis, by 7% at NA 0.5 and by 47% near NA 0.95.'],
        os.path.join(SLD, 'tolerance_media_pi.png'),
        'As NA increases the displacement that 2CE tolerates decreases as a power of NA, set by the width and the length '
        'of the focus.',
        'Facing lenses. The displacement of the focus of L2 that lowers the 2CE peak by 20%, across the axis (left) and '
        'along it (right). The fitted exponent is −0.99 across the axis and −2.04 along it (fits from NA 0.1 to 0.5), so the displacement along the axis falls as about 1/NA². Blue: vector; red: paraxial scalar; '
        'filled: air; open: water; star: Lim & Saloma (2002) at NA 0.5. The paraxial model gives a larger tolerance along '
        'the axis than the vector model, by 7% at NA 0.5 and 47% near NA 0.95. A Gaussian input (α = 4) makes the '
        'tolerances about 1.4 times larger.')

    big('Misalignment for a 20% loss of the 2CE peak against NA, θ = π/2', [
        'With crossed lenses, both tolerated misalignments decrease as about 1/NA², because each lies along the length of the focus of one of the two beams.',
        'The vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.'],
        os.path.join(SLD, 'tolerance_media_pi2.png'),
        'With crossed lenses both tolerated displacements follow the length of the focus.',
        'Crossed lenses; vector in air up to NA 0.71, where the lenses fit, and in water up to 0.94. Fits from NA 0.1 to '
        '0.5 give exponents −2.03 and −2.04. Blue: vector; red: paraxial scalar; filled: air; open: water.')


    KEEP = {'Summary', 'Two-color excitation with two confocal beams at an angle θ',
            'Paraxial scalar model and vector (Richards–Wolf) focus',
            '2CE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0 and π',
            'Central spot and depth of focus against NA: 2CE, θ = 0 and π',
            '2CE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2',
            '2PE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2', '2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = π',
            'Paraxial over vector widths of 2CE against NA', '2PE and 2CE central spots against NA, circular pupils',
            'Side lobes of 2PE against NA: distance from the peak and height', 'Largest NA of two crossed lenses',
            'Summary: high NA', 'Glossary (1/2)', 'Glossary (2/2)'}
    NAME = '2ce_high_na'

else:
    title_slide('Two-color excitation with femtosecond pulses at high NA',
                'Extension of Cambaliza & Saloma (2000) and Lim & Saloma (2003) to optical pulses')
    words('Summary', [
        'Extended the 2CE and 2PE point spread functions from continuous beams to transform-limited femtosecond pulses of '
        '4 to 1000 fs, from NA 0.1 to 0.95 in air, to 1.25 in water and to 1.45 in oil, with circular and annular pupils '
        'and Gaussian input.',
        'Found that at 100 fs pulsed 2CE is the same as with continuous beams at all three lens angles, and that with '
        'collinear and crossed lenses it keeps the continuous-beam depth of focus to within a few percent.',
        'Found that with facing lenses pulsed 2CE forms where the two pulses meet, so its depth of focus is shorter than '
        'with continuous beams, more so at lower NA: the pulse width that matches continuous beams grows from 25 fs at '
        'NA 0.9 to 610 fs at NA 0.2.',
        'Found that below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to '
        'lose its weak background in scattering media.',
        'Delayed one pulse relative to the other: the peak 2CE fluorescence decreases as their temporal overlap, except '
        'with facing lenses at low NA, where the peak moves along the axis and is largely retained.'],
        'With pulses, the lens angle and the NA decide how much of the continuous-beam 2CE is kept.',
        'Vector (Richards–Wolf) model in air unless a slide says otherwise. At 10 fs the 375- and 328-nm pairs have 18% and '
        '14% of the amplitude of the 350-nm pairs; at 20 fs both are below 1%.', size=13, h=4.4)
    navy('1. Optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses, from NA 0.1 '
         'to 0.95')
    PE = r'E(t) = \int a(\omega)\, e^{-i\omega t}\, d\omega, \quad a(\omega) = \exp\left[-\frac{(\omega-\omega_0)^2\tau^2}' \
        r'{8\ln 2}\right]'
    big('An optical pulse in time', [
        'The optical spectrum of a short pulse is a Gaussian in frequency about the carrier frequency (left), and each frequency is a continuous wave (right).'],
        os.path.join(PU, 'pulse_waves_spectrum.png'),
        'A pulse is a sum of continuous waves that are in phase near t = 0.',
        'Left: the Gaussian spectrum of a 10-fs pulse at 750 nm, with nine frequencies marked. Right: the waves at those '
        'frequencies, each with its weight a(ω); they are in phase at t = 0 (solid line) and out of phase at 15 fs (dashed '
        'line).', PE)

    big('Sum of the frequencies of a 10-fs optical pulse', [
        'At t = 0 all the frequencies are in phase and add up; away from t = 0 they drift out of phase, so their sum falls off as a Gaussian of width τ, the pulse.'],
        os.path.join(PU, 'pulse_waves_sum.png'),
        'The sum of the waves is the pulse.',
        'The sum over the whole spectrum of the 10-fs pulse at 750 nm: the field E(t) and its envelope |E(t)|. The waves '
        'are in phase at t = 0 (solid line) and out of phase at 15 fs (dashed line), where the envelope has fallen to a '
        'few percent of its peak.', PE)

    big('Pulse width and spectral bandwidth', [
        'A transform-limited Gaussian pulse is Gaussian in time (left) and in frequency (right), with spectral bandwidth Δν = 0.441/τ.'],
        os.path.join(PU, 'pulse_gaussian_time_frequency.png'),
        'Shorter pulses have wider spectra.',
        'Left: intensity in time exp(−4 ln2 t²/τ²), FWHM τ, the pulse width. Right: power spectrum against frequency, at '
        '750 nm (solid) and 656 nm (dashed). Spectral bandwidth (FWHM) 88 THz at 5 fs, 44 THz at 10 fs, 22 THz at 20 fs '
        'and 4.4 THz at 100 fs. The dotted line is 428 THz (700 nm).')

    big('Pulse spectra against wavelength, τ = 5, 10, 20 and 100 fs', [
        'Against wavelength, both colors lie at the red edge of the visible range.',
        'Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.'],
        os.path.join(PU, 'pulse_gaussian_wavelength.png'),
        'Short pulses reach 700 nm.',
        'Power spectrum per unit wavelength at 750 nm (solid) and 656 nm (dashed), for 5, 10, 20 and 100 fs; the visible '
        'range, 380 to 750 nm, is shaded. At 10 fs each spectrum has 31% of its peak at 700 nm (428 THz); at 20 fs and '
        'longer it has almost none.')

    s = slide('Photon pairs that excite the 350-nm level', '')
    bullets(s, 0.5, 0.9, 9.0, 1.3, [
        'Each lens focuses a transform-limited Gaussian pulse of width τ; the centres of both pulses reach the focus at t = 0.',
        'The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level, then squares the total: the '
        '350-nm pairs (750 + 656 nm), the 375-nm pairs (750 + 750 nm) and the 328-nm pairs (656 + 656 nm).'], 13)
    PA1 = r'A = A^{11} + 2A^{12} + A^{22}, \qquad A^{ab} = \int E_a E_b\, e^{i\omega_e t}\, dt'
    PA2 = r'F = |A|^2'
    h = equation(s, 1.5, 2.4, 7.0, PA1, 20)
    h += equation(s, 1.5, 2.6 + h, 7.0, PA2, 20)
    where(s, 1.5, 2.85 + h, 7.0, 'E_1 and E_2 are the fields of the 750- and 656-nm pulses at a point, ω_e is the frequency '
          'of the 350-nm level and F is the total 2CE accumulated as the pulses pass the focus. For long pulses F becomes '
          'I_1 I_2, the result of Cambaliza & Saloma (2000).', 12)
    notes(s, 'The excitation counts the photon pairs that add up to 350 nm.',
          '2A¹² takes one photon from each beam, the 350-nm pairs (750 + 656 nm). A¹¹ and A²² take both photons from one '
          'beam, the 375-nm pairs (750 + 750 nm) and the 328-nm pairs (656 + 656 nm), which reach the 350-nm level through '
          'the edges of the spectra. Each beam is a transform-limited Gaussian pulse of intensity FWHM τ, the two pulses '
          'are phase-locked, and the 350-nm level is narrow compared with the spectra. The results are for the vector model '
          'in air with the circular pupil, both beams polarized perpendicular to the plane of the lens axes, unless a slide '
          'says otherwise. The derivations and their checks are in docs/review/07_two_color_pulses/review_07.pdf.',
          PA1 + '\n' + PA2)

    big('2CE with 100-fs pulses and with continuous beams, θ = 0 and π', [
        'At 100 fs, pulsed 2CE is the same as with continuous beams at all three lens angles, so the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of that length.'],
        os.path.join(PU, 'sweep', 'profiles_100fs_2ce_0_pi.png'),
        'At 100 fs the pulses give the continuous-beam 2CE.',
        'Total 2CE accumulated as the pulses pass the focus, along the axis, paraxial model, NA 0.5, air. The depth of '
        'focus is 3.56 µm with collinear lenses, and 3.52 against 3.56 µm with facing lenses, where the pulses overlap '
        'over 21 µm, six times the focus. So the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of '
        'that length.')

    big('2CE with 100-fs pulses and with continuous beams, θ = π/2', [
        'With crossed lenses, the pulsed 2CE distribution across the axis at 100 fs is also the same as with continuous beams.'],
        os.path.join(PU, 'sweep', 'profiles_100fs_2ce_pi2.png'),
        'At 100 fs the pulses give the continuous-beam 2CE with crossed lenses too.',
        'Total 2CE accumulated as the pulses pass the focus, across the axis, paraxial model, NA 0.5, air. The width is '
        '0.76 µm with pulses and with continuous beams; the widths at the three lens angles agree to within 1%.')

    big('2CE depth of focus against pulse width, facing lenses', [
        'With facing lenses, the pulsed 2CE depth of focus falls below the continuous-beam value as the pulses get '
        'shorter, and more at lower NA, because 2CE forms where the two pulses meet.',
        'At NA 0.9 it is 97% of the continuous-beam value at 10 fs; at NA 0.5 it is 81% at 20 fs, and at NA 0.2 it is 70% '
        'at 100 fs.'],
        path(NS, 'key_dof_vs_tau_2ce_rw_air_pi.png'),
        'With facing lenses, shorter pulses and lower NA shorten the 2CE focus.',
        'Vector (Richards–Wolf) model in air, all photon pairs, depth of focus through the fringe crests over its '
        'continuous-beam value, one line per NA from 0.1 to 0.95. At 20 fs the ratio is 0.19 at NA 0.2, 0.41 at NA 0.3, '
        '0.81 at NA 0.5, 0.95 at NA 0.7 and 0.99 at NA 0.9.')
    big('2CE depth of focus against pulse width, collinear and crossed lenses', [
        'With collinear lenses, pulsed 2CE keeps the continuous-beam depth of focus to within 0.5% down to 4 fs, because '
        'the two pulses travel together and overlap over the whole focus.',
        'With crossed lenses, it stays within 1% from 20 fs at NA 0.3 and above (2% at NA 0.2); below 15 fs it grows by up '
        'to 7% at high NA, because the 375-nm pairs of L1 alone extend along its axis.'],
        path(NS, 'key_dof_vs_tau_2ce_rw_air_0_pi2.png'),
        'Collinear and crossed lenses keep the continuous-beam depth of focus.',
        'Vector model in air. With crossed lenses the ratio is 1.07 at 5 fs and NA 0.7, and 0.88 at 4 fs and NA 0.2. '
        'Crossed lenses fit up to NA 0.71 in air.')
    big('2CE depth of focus against NA, facing lenses', [
        'As NA increases, the ratio of the 2CE depth of focus with pulses to that with continuous beams returns to 1 with '
        'facing lenses at each pulse width, because the focus becomes shorter than the stretch where the pulses overlap.'],
        path(NS, 'key_dof_vs_na_2ce_rw_air_pi.png'),
        'Higher NA brings the pulsed 2CE focus back to the continuous-beam one.',
        'Vector model in air, one line per pulse width from 4 to 1000 fs. The stretch where the pulses overlap has FWHM '
        'cτ/√2: 4.2 µm at 20 fs, longer than the focus from about NA 0.5.')
    big('2CE along the axis with pulses at NA 0.5 and NA 0.9, facing lenses', [
        'At NA 0.5, 20-fs pulses shorten the 2CE along the axis, and at 10 fs the 375- and 328-nm pairs add fringes 350 nm '
        'apart.',
        'At NA 0.9 the focus is shorter than the stretch where the pulses meet, so 100- and 20-fs pulses give the '
        'continuous-beam profile; at 10 fs the fringes remain.'],
        path(NS, 'profiles_pi_rw_air_na0.5_na0.9.png'),
        'At high NA the pulsed 2CE keeps the continuous-beam profile down to 20 fs.',
        'Vector model in air, all photon pairs. Depth of focus through the fringe crests: at NA 0.5, 3.33 µm for continuous '
        'beams, 3.29 µm at 100 fs, 2.70 µm at 20 fs and 2.08 µm at 10 fs; at NA 0.9, 0.81, 0.81, 0.80 and 0.78 µm.')

    big('Overlap in time of the two facing pulses', [
        'Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs.',
        'The pulsed 2CE is the continuous-beam profile times this overlap: at 20 fs the product gives 2.74 µm and the full calculation 2.78 µm.'],
        os.path.join(PU, 'sweep', 'gate_pi.png'),
        'The overlap of the pulses in time cuts the 2CE focus.',
        'The 2CE depth of focus at 20 fs is 2.78 µm with all pairs and 2.81 µm with the 350-nm pairs. The continuous-beam '
        'profile times this overlap gives 2.74 µm, against 2.78 µm computed with all pairs. Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap over a stretch of FWHM '
        'G = cτ/√2 n (4.2 µm at 20 fs, 21 µm at 100 fs). With D the continuous-beam depth of focus, the pulsed one is '
        'DG/√(D² + G²). At 10 fs the computed 2CE (2.14 µm) is longer than the product (1.83 µm), because the 375- and '
        '328-nm pairs need no overlap.',
        r'G(z) = \int I_1(t - z/c)\, I_2(t + z/c)\, dt \propto \exp\left[-\frac{8\ln 2\, z^2}{(c\tau)^2}\right], \qquad '
        r'\mathrm{DOF}_{\mathrm{pulsed}} = \frac{DG}{\sqrt{D^2 + G^2}}')

    big('Signal added by the 375- and 328-nm pairs', [
        'Below about 15 fs the spectra reach 700 nm, so two photons of one pulse also excite the 350-nm level, through the 375- and 328-nm pairs.',
        'Their amplitude interferes with that of the 350-nm pairs, which gives the fringes, and one beam alone now excites, so 2CE starts to lose the weak background of continuous beams.'],
        os.path.join(PU, 'sweep', 'strength_vs_tau.png'),
        'Pairs within one pulse matter below 15 fs.',
        'With continuous beams, 2CE needs both beams, which gives its weak background in scattering media. The amplitude '
        'of the 375- and 328-nm pairs is 18% and 14% of that of the 350-nm pairs at 10 fs, and below 1% for both at 20 fs. The peak of the '
        'total over that of the 350-nm pairs is 1.02 at 20 fs, 1.15 at 15 fs, 1.73 at 10 fs and 3.1 at 5 fs.')

    big('Pulse width that matches continuous beams against NA, θ = π', [
        'With facing lenses, the pulsed 2CE matches the continuous-beam 2CE once the pulses are longer than about 25 fs at NA 0.9, 87 fs at NA 0.5 and 264 fs at NA 0.3 in air, because a lower NA gives a longer focus for the pulses to overlap over.',
        'In water and in oil a longer pulse is needed at the same NA (164 fs and 216 fs at NA 0.5), because the focus is longer in a medium of higher refractive index.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2ce_pi.png'),
        'Facing lenses need the longest pulses to behave like continuous beams, more so at lower NA.',
        'The pulse width from which the largest difference between the pulsed and continuous-beam profiles stays below 1% '
        'of the peak. Facing lenses, 2CE, vector model in air: about 25 fs at NA 0.9, 87 fs at NA 0.5, 264 fs at NA 0.3 '
        'and 610 fs at NA 0.2. For 2PE it is shorter (62 fs at NA 0.5), because the 350-nm pairs within one pulse need no '
        'overlap. At NA 0.5: 87 fs in air, 164 fs in water and 216 fs in oil. With collinear lenses 4-fs pulses already '
        'give the continuous-beam profiles, and with crossed lenses 2CE does from about 20 to 28 fs (next slide). Solid: '
        'vector; dashed: scalar, drawn up to NA 0.5, where the paraxial model holds. The open triangles mark NAs where '
        'the longest pulse computed is still outside the tolerance.')

    big('Pulse width that matches continuous beams, θ = 0 and π/2', [
        'With collinear lenses, the pulsed 2CE matches the continuous-beam 2CE at all pulse widths computed, down to 4 fs, because the two pulses travel together and overlap over the whole focus.',
        'With crossed lenses, it matches once the pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2ce_0_pi2.png'),
        'Collinear and crossed lenses match continuous beams with short pulses.',
        'The same measure as the previous slide: the pulse width from which the largest difference between the pulsed '
        'and continuous-beam 2CE profiles stays below 1% of the peak. With collinear lenses the two pulses travel together '
        'and overlap over the whole focus, so the shortest pulse computed, 4 fs, already matches. With crossed lenses '
        '(vector model in air) it is 28 fs at NA 0.2 and 21 fs at NA 0.7; at NA 0.1 it is 54 fs. Crossed lenses fit up to '
        'NA 0.71 in air and 0.94 in water.')

    big('Pulse width that matches continuous beams: pupils, θ = π', [
        'With facing lenses, a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous beams: at NA 0.5, 100 fs for the circular pupil, 162 fs for the Gaussian input (α = 4) and 466 fs for the annular pupil with ε = 0.9.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2ce_pi.png'),
        'Annular pupils and Gaussian input need longer pulses with facing lenses.',
        'Vector model in air. The figure gives the pulse width from which the 2CE depth of focus stays within 1% of its '
        'continuous-beam value: at NA 0.5 with facing lenses, 100 fs for the circular pupil, 162 fs for the Gaussian input '
        '(α = 4) and 466 fs for the annular pupil with ε = 0.9. By the largest difference between the profiles, the measure '
        'of the slides before, the same three are 87, 139 and 405 fs. The annular pupil with ε = 0.99 stays outside the '
        'tolerance at the longest pulse computed below NA 0.8.')

    big('Pulse width that matches continuous beams: pupils, θ = 0, π/2', [
        'With collinear lenses, the 2CE depth of focus matches its continuous-beam value at all pulse widths computed, for all pupils and inputs.',
        'With crossed lenses, it matches once the pulses are longer than about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2ce_0_pi2.png'),
        'With collinear and crossed lenses the pupil changes the pulse width needed by little.',
        'Vector model in air, pulse width from which the 2CE depth of focus stays within 1% of its continuous-beam value. '
        'With crossed lenses it is 13 to 15 fs for the circular pupil from NA 0.4 to 0.7, 14 to 16 fs for the annular '
        'pupils and 11 to 14 fs for the Gaussian input (α = 4). Below NA 0.4 it rises to 82 fs for the Gaussian input at '
        'NA 0.1 and 54 fs for the circular pupil.')


    navy('2. Delay between the two pulses: peak 2CE fluorescence against a misalignment of the two pulses in time, at '
         'θ = 0, π/2 and π')
    delay_slides(slide, big, notes)
    words('Summary: 2CE with optical pulses', [
        'At 100 fs, pulsed 2CE is the same as with continuous beams.',
        'With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent.',
        'With facing lenses, pulsed 2CE forms where the pulses meet, so its depth of focus is shorter than with continuous beams, more so at lower NA; 2PE shortens less.',
        'Below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to lose its weak background.',
        'With a delay between the two pulses, the peak 2CE fluorescence decreases as their temporal overlap, to one quarter at a delay of one pulse width; with facing lenses at low NA the peak moves along the axis and is largely retained.',
        'The results assume phase-locked, transform-limited pulses and a 350-nm level that is narrow compared to the pulse spectra.'],
        'The lens angle decides what a pulse changes.',
        'Collinear θ = 0, crossed θ = π/2, facing θ = π.')

    words('Next steps', [
        'Compute pulsed 2CE through a highly scattering medium, where Cambaliza & Saloma (2000) found the main advantage of 2CE compared to 2PE.',
        'Compute pulses of unequal width and chirped pulses, which change the overlap in time of the two pulses.',
        'Replace the narrow 350-nm level with a broad absorption band.'],
        'Pulsed 2CE through a scattering medium is the first candidate.',
        'The scattering medium combines the Monte Carlo model of docs/review/06 with the pulse model; it would show '
        'whether 2CE with pulses keeps its weak background. With unequal pulse widths the overlap becomes exp[−4 ln2 Δt²/(τ₁² + τ₂²)]. '
        'For a broad absorption band the signal of the 350-nm pairs is the integral of I₁ I₂ over time.')

    glossary(GLOSS_PULSE)
    navy('Backup')
    big('Pulse width that matches continuous beams: 2PE, θ = π', [
        'With facing lenses, the pulsed 2PE matches the continuous-beam 2PE at shorter pulse widths than 2CE (62 fs compared to 87 fs at NA 0.5 in air), because pairs of photons from one pulse need no overlap.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2pe_pi.png'),
        'With facing lenses 2PE needs shorter pulses than 2CE.',
        'Largest difference between the pulsed and continuous-beam 2PE profiles below 1% of the peak. At NA 0.5 in air '
        '(vector model) 2PE matches from 62 fs, against 87 fs for 2CE, because the photon pairs within one pulse need no '
        'overlap of the two pulses. Solid: vector; dashed: scalar, drawn up to NA 0.5.')

    big('Pulse width that matches continuous beams: 2PE, θ = 0, π/2', [
        'With collinear lenses, the pulsed 2PE matches the continuous-beam 2PE at all pulse widths computed, down to 4 fs.',
        'With crossed lenses, it matches once the pulses are longer than 37 fs at NA 0.1 and 6 fs at NA 0.5.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2pe_0_pi2.png'),
        'With collinear and crossed lenses 2PE matches continuous beams with short pulses.',
        'Largest difference below 1% of the peak. With crossed lenses in air (vector model) the pulse width is 37 fs at '
        'NA 0.1, 5.7 fs at NA 0.5 and 4 fs, the shortest computed, from NA 0.6.')

    big('Pulse width that matches continuous beams: 2PE, pupils, θ = π', [
        'With facing lenses, a pupil or an input that gives a longer depth of focus also needs a longer pulse for 2PE to match continuous beams.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2pe_pi.png'),
        'Pupils with a longer focus need longer pulses for 2PE too.',
        'Vector model in air, pulse width from which the 2PE depth of focus stays within 1% of its continuous-beam value. '
        'At NA 0.5 it is 72 fs for the circular pupil.')

    big('Pulse width that matches continuous beams: 2PE, pupils, θ = 0, π/2', [
        'With collinear lenses, the 2PE depth of focus matches its continuous-beam value at all pulse widths computed, for all pupils and inputs.',
        'With crossed lenses, the pulse width needed is largest at low NA (68 fs for the Gaussian input at NA 0.1) and falls below 10 fs at NA 0.7.'],
        os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2pe_0_pi2.png'),
        'With collinear and crossed lenses the pupils need short pulses for 2PE.',
        'Vector model in air, depth of focus within 1%. With crossed lenses the pulse width is largest at low NA, 68 fs for '
        'the Gaussian input and 44 fs for the circular pupil at NA 0.1, and falls below 10 fs at NA 0.7 for all pupils.')

    KEEP = {'Summary', 'Photon pairs that excite the 350-nm level',
            '2CE with 100-fs pulses and with continuous beams, θ = 0 and π',
            '2CE depth of focus against pulse width, facing lenses',
            '2CE depth of focus against pulse width, collinear and crossed lenses',
            '2CE along the axis with pulses at NA 0.5 and NA 0.9, facing lenses',
            'Pulse width that matches continuous beams against NA, θ = π', 'Signal added by the 375- and 328-nm pairs',
            'Delay between the two pulses and their temporal overlap',
            'Peak 2CE fluorescence and its position against the delay, θ = π',
            'Peak 2CE fluorescence at a delay of one pulse width against NA', 'Summary: 2CE with optical pulses',
            'Next steps', 'Glossary (1/2)', 'Glossary (2/2)'}
    NAME = '2ce_pulses'

finish(prs, KEEP if MAIN else None)
ds.keynote_fonts()
out = os.path.join(OUT, NAME + ('_main' if MAIN else '') + '.pptx')
prs.save(out)
print('Saved ->', out, f'({len(prs.slides)} slides)')
for f in MISSING:
    print('MISSING', f)
