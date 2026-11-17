r"""Deck of the work up to the delay between the pulses: the focus at high NA with the Richards–Wolf theory, two-color excitation (2CE) with
continuous beams at high NA, and 2CE with optical pulses. Figures are the existing ones (mcdo/deck.py stages 1 to 5,
the Cambaliza & Saloma and Lim & Saloma replications and their high-NA extension, and the pulse figures); numbers are
in the speaker notes. The delay between the pulses is in the separate deck pulse_delay.pptx.

    python scripts/make_2ce_high_na_pulses_deck.py -> output/08_two_color/decks/2ce_high_na_pulses.pptx
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image

import mcdo.deckstyle as ds
from mcdo.deckstyle import NAVY, PALE, PURPLE, WHITE, bullets, dots, equation, figure, label, prs, slide, text, where

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
        figure(s, fig, 4.3, 0.86, 5.55, LOW - 0.86)
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


# ── title and summary ────────────────────────────────────────────────────
s = navy('Two-color excitation at high NA and with optical pulses', [
    ('Roland Albert A. Romero', 18, WHITE),
    ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
    ('Extension of Romallosa, Bantang & Saloma (2003), Cambaliza & Saloma (2000) and Lim & Saloma (2002, 2003)', 13,
     PALE)])
notes(s, 'Two-color excitation (2CE) at high NA and with optical pulses.',
      'Romallosa, Bantang & Saloma, Phys. Rev. A 68, 033812 (2003). Cambaliza & Saloma, Opt. Commun. 184, 25 (2000). '
      'Lim & Saloma, Opt. Commun. 207, 121 (2002), and Appl. Opt. 42, 3398 (2003). The delay between the two pulses '
      'is in the separate deck pulse_delay.pptx.')

words('Summary', [
    'Reproduced the focus of few-cycle pulses of Romallosa, Bantang & Saloma (2003) with the Richards–Wolf theory, '
    'and extended it to Gaussian input and annular pupils.',
    'Reproduced Cambaliza & Saloma (2000) and Lim & Saloma (2002, 2003) on two-color excitation (2CE), and extended '
    'them to high NA, where the paraxial model gives too long a depth of focus above NA 0.43.',
    'Extended 2CE to optical pulses, and found that at 100 fs it is the same as with continuous beams at the three '
    'lens angles.',
    'Found that with facing lenses pulsed 2CE forms where the two pulses meet, so its depth of focus is shorter than '
    'with continuous beams, more so at lower NA.',
    'Found that below about 15 fs one beam alone also excites the 350-nm level, so 2CE starts to lose its weak '
    'background in scattering media.',
    'Added a delay between the two pulses, which weakens 2CE through their temporal overlap; these results are in '
    'a separate deck.'],
    'Richards–Wolf focus, then 2CE at high NA, then 2CE with optical pulses.',
    'The paraxial depth of focus of 2CE with collinear and facing lenses is 5% longer than the vector one from NA 0.43 '
    'in air (0.57 in water), 7% at NA 0.5 and 36% at NA 0.9. With facing lenses at NA 0.5, the 2CE depth of focus is '
    'about 80% of the continuous-beam value at 20 fs and 60% at 10 fs; at NA 0.3 and 20 fs it is 40%. The 375- and '
    '328-nm pairs have 18% of the amplitude of the 350-nm pairs at 10 fs and below 1% at 20 fs.', size=14, h=4.3)

# ── Part 1. The focus at high NA with the Richards–Wolf theory ───────────
navy('Part 1. The focus at high NA with the Richards–Wolf theory')
R1 = os.path.join(O, '01_romallosa', 'panels')
A2 = os.path.join(O, '02_na_apodization', 'panels')
A3 = os.path.join(O, '03_annular', 'panels')
A5 = os.path.join(O, '05_pulsed_pupils', 'panels')

pair('Focus of a 1-fs pulse and a continuous beam, NA 0.8', [
    'A 1-fs pulse fills the zeros of the continuous-beam focus, as in Romallosa et al. (2003).',
    'The structural content along the axis is 1.058, against 1.057 in Romallosa et al. (2003).'],
    os.path.join(R1, 'fig2_profiles_p1.png'), os.path.join(R1, 'fig2_profiles_p2.png'),
    'The five figures of Romallosa, Bantang & Saloma (2003) are reproduced.',
    'Left: across the axis at z = 0; right: along the axis at r = 0; 750 nm, NA 0.8, n = 1.3, continuous beam and '
    '1-fs pulse. The transverse FWHM is 472.8 nm. The remaining differences are within 1% for Fig. 4 and about 3% for '
    'Fig. 3 at 1 fs. Romallosa et al. integrate the whole positive spectrum, from 0 to 2ω_c; the band they quote, '
    '483 nm to 1.67 µm, is the FWHM of the spectrum. With the FWHM band alone, 24% of the spectral weight is lost and '
    'the quoted values are not reproduced. Three conventions had to be found from the figures: the panel labels of '
    'Fig. 2 are exchanged, Fig. 3 is an integral along a line, and the Linfoot arrays are in optical coordinates. '
    'Details are in docs/review/01_romallosa/review_01.pdf.')

pair("Linfoot's criteria against NA and against pulse width", [
    'Fidelity and structural content do not depend on NA, as in Romallosa et al. (2003).',
    'Below about 2 fs the fidelity falls below 1 and the structural content rises above 1.'],
    os.path.join(R1, 'fig4_linfoot_p1.png'), os.path.join(R1, 'fig4_linfoot_p2.png'),
    'Pulses shorter than about 2 fs change the focus; the change does not depend on NA.',
    'Left: the criteria at 1 fs against NA; right: against the pulse width at NA 0.8 (Romallosa et al. (2003), '
    'Fig. 4). Open symbols are the fidelity F and filled symbols the structural content S, along and across the axis; '
    'the lines are the reference curves quoted by Romallosa et al. The criteria do not depend on NA because the '
    'Linfoot arrays are in optical coordinates.',
    r'F = 1 - \frac{\sum (a - r)^2}{\sum r^2}, \quad S = \frac{\sum a^2}{\sum r^2}, \quad Q = \frac{\sum a r}{\sum r^2}')

pair('Spot width against NA, scalar and vector theory', [
    'As NA increases the vector spot becomes wider than the scalar Debye spot.',
    'The difference is the longitudinal field E_z, which fills the zeros and widens the spot.'],
    os.path.join(A2, 'verify_na_convergence_p3.png'), os.path.join(A2, 'fig_na_profiles_p3.png'),
    'The scalar theory departs from the vector theory first across the axis, along the polarization.',
    'Left: FWHM of the focal spot in optical units against NA, for the vector field with all three components, the '
    'scalar Debye integral and the Airy pattern; 750 nm, continuous beam, uniform input. Right: the three field '
    'components at NA 1.2. At NA 0.1 the vector theory, the scalar Debye integral and the Airy pattern agree to 1e-4. '
    'For linear polarization the FWHM along the polarization differs by 1% at NA 0.30 and by 5% at NA 0.60; along the '
    'axis the difference reaches 1% at NA 1.15. Details are in docs/review/02_na_apodization/review_02.pdf.',
    r'E_x = -i(I_0 + I_2\cos 2\phi), \quad E_y = -i I_2 \sin 2\phi, \quad E_z = -2 I_1 \cos\phi')

big('Focal spot at NA 0.3 and 0.9, scalar and vector', [
    'At NA 0.3 the scalar and vector spots have the same width, to about 1%.',
    'At NA 0.9 the vector spot is wider along the polarization and its zeros fill, because of E_z.'],
    os.path.join(O, '02_na_apodization', 'check2_na0.3_na0.9.png'),
    'As NA increases the vector spot widens along the polarization and its zeros fill.',
    'Intensity in the focal plane against the optical radius v = k r sin α, on a log scale; 750 nm, n = 1.3, continuous '
    'beam, uniform input. Grey: scalar Debye; red: vector field along the polarization (x); blue dashed: vector field '
    'across it (y). At NA 0.3 the FWHM along the polarization is 3.27 in optical units against 3.23 for the scalar '
    'field, 1% wider. At NA 0.9 it is 3.62 against 3.19, 14% wider, and the first zero along the polarization is '
    'filled to 1e-2 of the peak. Across the polarization the vector spot keeps its zeros and is about 1% narrower '
    'than the scalar one. The longitudinal field E_z is zero across the polarization and largest along it, so it '
    'widens the spot along the polarization and not across it.',
    r'E_x = -i(I_0 + I_2\cos 2\phi), \quad E_z = -2 I_1 \cos\phi')

pair('Gaussian input against uniform input at high NA', [
    'A Gaussian input (α = 4) keeps the scalar theory accurate to a higher NA.',
    'It gives less weight to the marginal rays, which carry the longitudinal field.'],
    os.path.join(A2, 'verify_apod_thresholds_p1.png'), os.path.join(A2, 'fig_focal_plane_gaussian_p5.png'),
    'A Gaussian input extends the range of NA where the scalar theory holds.',
    'Left: deviation of the vector focal width from the scalar one against NA, for uniform input and Gaussian input '
    'with truncation parameter α = 1 and 4; it passes 1% near NA 0.45 for uniform input and 0.55 for α = 4, and 5% '
    'near 0.90 and 1.15. Along the polarization, the 1% and 5% points are NA 0.40 and 0.85 for α = 4, against 0.30 and '
    '0.60 for uniform input. Right: the profile along the axis at NA 0.9, where the Richards–Wolf and Debye profiles '
    'for the Gaussian input agree and the uniform input gives a shorter focus.',
    r'A(\rho) = \exp(-\alpha \rho^2)')

pair('Depth of focus and peak against ε, annular pupils', [
    'At low NA the depth of focus grows as 1/(1 − ε²); at high NA it grows less.',
    'The peak intensity falls as (1 − ε²)², the cost of the longer focus.'],
    os.path.join(A3, 'verify_annular_p3.png'), os.path.join(A3, 'verify_annular_energy_p1.png'),
    'An annular pupil lengthens the focus and lowers the peak.',
    'The field of an annular pupil is the field of the full pupil minus that of the obstructed part. At ε = 0.99 the '
    'depth of focus over that of the full pupil is 50.13 at low NA against 50.25 from 1/(1 − ε²), and 30.4 at '
    'sin α = 0.9. A thin annulus gives the J₀² profile of Durnin at low NA; at high NA the vector profile is narrower '
    'than the scalar one (FWHM 2.06 against 2.25 in optical units). Details are in review_03.pdf and review_04.pdf.',
    r'U_{\mathrm{annular}} = U_R - U_{\varepsilon R}, \quad \frac{\mathrm{DOF}(\varepsilon)}{\mathrm{DOF}(0)} = '
    r'\frac{1}{1 - \varepsilon^2}')

pair('Depth of focus of annular pupils with few-cycle pulses', [
    'The longer depth of focus of an annular pupil is kept with few-cycle pulses, down to 1 fs.'],
    os.path.join(A5, 'verify_pulsed_annular_p4.png'), os.path.join(A5, 'verify_pulsed_annular_p3.png'),
    'Few-cycle pulses keep the depth of focus that an annular pupil gives.',
    'Left: depth of focus over that of the full pupil against ε, continuous beam and 5, 2 and 1 fs, NA 0.8, 750 nm. '
    'At ε = 0.99 the ratio is 44.35 for a continuous beam and 44.33 at 1 fs. Right: the profile along the axis at '
    'ε = 0.99; at 1 fs the focus is 1.010 times longer than with a continuous beam. Details are in review_05.pdf.')

pair('Transverse profile with pulses, full and annular pupils', [
    'The contrast of the transverse rings decreases with shorter pulses, for both pupils.',
    'This is the loss of focal quality of Romallosa et al. (2003), here with annular pupils.'],
    os.path.join(A5, 'verify_pulsed_annular_p2.png'), os.path.join(A5, 'verify_pulsed_annular_p1.png'),
    'Pulses fill the zeros between the rings, with the full pupil and with the annular one.',
    'Left: full pupil; right: annular pupil with ε = 0.99; NA 0.8, 750 nm, continuous beam and 5, 2 and 1 fs. The '
    'structural content across the axis is about 1.06 at 1 fs for both pupils.')

# ── Part 2. Two-color excitation with continuous beams ───────────────────
navy('Part 2. Two-color excitation with continuous beams')
s = slide('Two beams focused at an angle θ', '')
figure(s, path(TC, 'setup_model.png'), 0.4, 0.95, 4.2, 4.25)
bullets(s, 4.85, 0.95, 4.75, 1.4, [
    'Lens L2 is lens L1 turned by θ about the focus O, with θ = 0, π/2 or π.',
    '2CE absorbs one photon of each color, so the signal is the product of the two intensities.'], 13)
EQ1 = r'\frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}'
EQ2 = r'F_{2c} = \kappa\, I_1 I_2'
EQ3 = r"F_{2p} = \kappa'\, |U_1 + U_2|^4"
t = 2.45
for tex in (EQ1, EQ2, EQ3):
    t += equation(s, 5.0, t, 4.5, tex, 20) + 0.12
where(s, 5.0, t + 0.05, 4.5, 'λ_1 = 750 nm on L1, λ_2 = 656 nm on L2 and λ_e = 350 nm; I_1 and I_2 are the focused '
      'intensities and U_1 and U_2 the fields. 2PE uses 700 nm in both lenses. θ = 0, π/2 and π are collinear, '
      'crossed and facing lenses.', 11)
notes(s, 'Two lenses focus two colors onto one point, at an angle θ.',
      'Cambaliza & Saloma (2000), pp. 26–28. 2CE absorbs one photon of each beam, so it forms where the two beams '
      'overlap; the two beams do not interfere. Two-photon excitation (2PE) uses one wavelength in both lenses, so '
      'the two fields add and interfere before the fourth power. κ and κ′ are the fluorescence cross-sections. Lim & '
      'Saloma (2002) displace the focus of L2 by x_c across and z_c along the axis of L1, and Lim & Saloma (2003) give '
      'each beam a primary spherical aberration.', '\n'.join((EQ1, EQ2, EQ3)))

pair('Transverse 2CE profiles, NA 0.5 (Fig. 2b)', [
    'At θ = π/2 the 2CE spot is wider; at θ = 0 and π the profiles are identical.'],
    path(CB, 'original', 'fig2b.png'), path(CB, 'panels', 'fig2b.png'),
    'Current work reproduces the transverse 2CE profiles of Cambaliza & Saloma (2000).',
    'Paraxial scalar model, NA 0.5, circular pupils, as published. Current work lies on the published curves. The '
    'FWHM is 0.763 µm at θ = π/2 and 0.517 µm at θ = 0 and π. Beam 2 is rotated in real space (x, z). Several ratios '
    'quoted in the text of Cambaliza & Saloma (2000) differ from their own curves at θ = π/2 (for example 0.67 '
    'against 0.49 for the 2PE spot at π/2 over that at 0), while the plotted widths agree with current work.',
    labels=('Cambaliza & Saloma (2000), Fig. 2b', 'Current work'))

pair('Axial 2CE profiles, NA 0.5 (Fig. 3b)', [
    'At θ = π/2 the 2CE depth of focus is shorter; at θ = 0 and π the profiles are identical.'],
    path(CB, 'original', 'fig3b.png'), path(CB, 'panels', 'fig3b.png'),
    'Current work reproduces the axial 2CE profiles of Cambaliza & Saloma (2000).',
    'Paraxial scalar model, NA 0.5. The published depth of focus at θ = π/2, 0.67 µm, is that of beam 2 rotated in '
    '(x, z); a rotation in the optical coordinates (u, v) gives 1.31 µm. The depth of focus at θ = 0 and π is '
    '3.56 µm. With crossed lenses the 2CE has weaker side lobes than 2PE but a broader depth of focus (p. 30).',
    labels=('Cambaliza & Saloma (2000), Fig. 3b', 'Current work'))

LO = os.path.join(TC, 'lim2002')
pair('2CE peak against displacement of L2, θ = π', [
    'Displacing the focus of L2 lowers the 2CE peak, more slowly along the axis than across it.'],
    path(LO, 'original', 'orig_fig4a.png'), path(LO, 'panels', 'fig4_peak_p1.png'),
    'With facing lenses the 2CE peak tolerates a larger displacement along the axis.',
    'Lim & Saloma (2002), Fig. 4(a): the 2CE peak in percent of the aligned peak against the displacement x_c, z_c of '
    'the focus of L2, in units of λ_1, paraxial scalar model, NA 0.5. Fits of current work: −0.601 x_c² + 0.888 '
    'across the axis and −0.027 z_c² + 0.998 along it.',
    labels=('Lim & Saloma (2002), Fig. 4a', 'Current work'))

pair('2CE peak against displacement of L2, θ = π/2', [
    'With crossed lenses the peak falls along z_c, set by the length of the focus of L1.'],
    path(LO, 'original', 'orig_fig4c.png'), path(LO, 'panels', 'fig4_peak_p3.png'),
    'With crossed lenses the 2CE peak changes little across the axis of L1.',
    'Lim & Saloma (2002), Fig. 4(c). Across the axis the fit is −0.063 x_c² + 0.999 against −0.06 x_c² + 1 in Lim & '
    'Saloma (2002); along the axis it is −0.045 z_c² + 0.995 against −0.045 z_c² + 0.986. The maps of fidelity, '
    'structural content and correlation quality behave as described by Lim & Saloma (2002).',
    labels=('Lim & Saloma (2002), Fig. 4c', 'Current work'))

pair('2CE peak against aberration, θ = 0 and π', [
    'The 2CE peak is kept when the two coefficients are equal at θ = 0 and opposite at θ = π.'],
    path(TC, 'panels', 'aberration_peak_p2.png'), path(TC, 'panels', 'aberration_peak_p6.png'),
    'Equal or opposite spherical aberration in the two beams keeps the 2CE peak, as in Lim & Saloma (2003).',
    'Peak in percent of the peak without aberration against the primary spherical aberration coefficients φ₁ and φ₂ '
    'of the two beams, paraxial scalar model, NA 0.5. At θ = 0 the peak at φ₁ = φ₂ = ±60 is 0.84 of the peak without '
    'aberration, and at φ₁ = −φ₂ = ±60 it is 0.07; at θ = π the two are exchanged. With crossed lenses the 2CE '
    'fidelity stays above 0.9 for coefficients up to 40, as in Lim & Saloma (2003), pp. 3401 and 3403.')

SLD = os.path.join(LO, 'slides')
big('Displacement for 20% peak loss against NA, θ = π', [
    'The tolerated displacement falls as about 1/NA across the axis and 1/NA² along it.'],
    os.path.join(SLD, 'tolerance_media_pi.png'),
    'As NA increases the displacement that 2CE tolerates decreases as a power of NA, set by the width and the length '
    'of the focus.',
    'Facing lenses. The displacement of the focus of L2 that lowers the 2CE peak by 20%, across the axis (left) and '
    'along it (right). The fitted exponent is −0.99 across the axis and −2.04 along it (fits from NA 0.1 to 0.5), so the displacement along the axis falls as about 1/NA². Blue: vector; red: paraxial scalar; '
    'filled: air; open: water; star: Lim & Saloma (2002) at NA 0.5. The paraxial model gives a larger tolerance along '
    'the axis than the vector model, by 7% at NA 0.5 and 47% near NA 0.95. A Gaussian input (α = 4) makes the '
    'tolerances about 1.4 times larger.')

big('Displacement for 20% peak loss against NA, θ = π/2', [
    'With crossed lenses both displacements fall as about 1/NA², along the length of a beam.'],
    os.path.join(SLD, 'tolerance_media_pi2.png'),
    'With crossed lenses both tolerated displacements follow the length of the focus.',
    'Crossed lenses; vector in air up to NA 0.71, where the lenses fit, and in water up to 0.94. Fits from NA 0.1 to '
    '0.5 give exponents −2.03 and −2.04. Blue: vector; red: paraxial scalar; filled: air; open: water.')

HN = os.path.join(CB, 'high_na')
big('Spot and depth of focus against NA: 2CE, θ = 0 and π', [
    'As NA increases the paraxial depth of focus shrinks more slowly than the vector one.',
    'The scalar model gives a longer depth of focus, by 7% at NA 0.5 and 36% at NA 0.9.'],
    os.path.join(HN, 'cfg_2ce_0.png'),
    'Along the axis the paraxial model gives too long a focus at high NA.',
    'Solid: vector (Richards–Wolf), beams polarized along y; dashed: paraxial scalar; blue: air; green: water. The '
    'paraxial depth of focus is 5% longer from NA 0.43 in air (0.57 in water); the central spot stays within 5% up to '
    'NA 0.86. The paraxial model uses sin²α/2 for 1 − cos α, which lengthens the depth of focus by the factor '
    '1 + tan²(α/2). The depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9 (vector, air).',
    r'1 - \cos\alpha \approx \frac{\sin^2\alpha}{2}, \qquad \frac{\mathrm{DOF}_{\mathrm{paraxial}}}'
    r'{\mathrm{DOF}_{\mathrm{vector}}} \approx 1 + \tan^2\frac{\alpha}{2}')

big('2CE along the axis at NA 0.5 and 0.9, θ = 0 and π', [
    'At NA 0.9 the paraxial 2CE focus is 36% longer than the vector one, and 7% at NA 0.5.'],
    os.path.join(LO, 'slides', 'axial_2ce_paraxial_vector_na0.5_na0.9.png'),
    'At high NA the paraxial model gives too long a 2CE focus.',
    'Continuous beams, 750 and 656 nm, air, uniform input; red dashed: paraxial scalar; blue: vector (Richards–Wolf). '
    'The 2CE depth of focus is 3.56 µm against 3.33 µm at NA 0.5, and 1.10 µm against 0.81 µm at NA 0.9. The profile '
    'along the axis is the same with collinear and facing lenses, since I_1 I_2 does not depend on the direction of '
    'beam 2. The scalar Debye integral with the exact phase gives the vector profile along the axis, so the '
    'small-angle phase of the paraxial model causes the difference.',
    r'1 - \cos\alpha \approx \frac{\sin^2\alpha}{2}')

big('Spot and depth of focus against NA: 2CE, θ = π/2', [
    'As NA increases both 2CE widths decrease as about 1/NA, set by the spot of the other beam.',
    'The paraxial model follows the vector focus within 4% wherever crossed lenses fit.'],
    os.path.join(HN, 'cfg_2ce_pi2.png'),
    'With crossed lenses the paraxial model gives the right widths.',
    'The 2CE spot is 0.75 by 0.66 µm at NA 0.5. The depth of focus is shorter than with collinear lenses, and this '
    'advantage decreases as NA increases: 13 times shorter at NA 0.2 and 3.4 times at NA 0.7. Crossed lenses fit up to '
    'NA 0.71 in air and 0.94 in water.')

big('Paraxial over vector widths of 2CE against NA', [
    'As NA increases the paraxial 2CE widths exceed the vector ones, first along the axis.',
    'The difference comes from the paraxial phase, not from the polarization.'],
    os.path.join(HN, 'gap_2ce.png'),
    'The paraxial 2CE widths depart from the vector ones first along the axis.',
    'Gap = paraxial width over vector width − 1. Along the axis with collinear and facing lenses the gap reaches 5% '
    'at NA 0.43 in air (0.57 in water); across the axis at NA 0.86 (1.14); with crossed lenses it stays within 4%. '
    'The scalar Debye integral with the exact phase gives the vector widths along the axis, so the small-angle phase '
    'causes the difference.')

big("Linfoot's criteria against NA: 2CE, θ = 0 and π", [
    'The paraxial focus becomes longer and lower, so the structural content C falls first.',
    'Across the axis the fidelity F stays at 0.996 or above at all NA.'],
    os.path.join(HN, 'linfoot', 'linfoot_na_2ce_0.png'),
    'The structural content shows the paraxial error along the axis first.',
    'Fidelity F, structural content C and correlation quality Q of the paraxial profile a against the vector profile '
    'r, each normalized to unit energy over the window. Along the axis C is below 0.95 from NA 0.44 in air (0.58 in '
    'water), where the depth of focus departs by 5%. F stays above 0.99 up to NA 0.63 (0.84 in water). With unit '
    'energy, the longer scalar focus has a lower peak, so the sum of a² drops below that of r².',
    r'F = 1 - \frac{\sum (a - r)^2}{\sum r^2}, \quad C = \frac{\sum a^2}{\sum r^2}, \quad Q = \frac{\sum a r}{\sum r^2}')

big("Linfoot's criteria against NA: 2CE, θ = π/2", [
    'With crossed lenses the paraxial and vector 2CE stay alike wherever the lenses fit.'],
    os.path.join(HN, 'linfoot', 'linfoot_na_2ce_pi2.png'),
    'With crossed lenses the paraxial model gives the profiles of the vector focus.',
    'F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 up to NA 0.71 in air and 0.94 in water. The scalar 2CE and 2PE profiles stay '
    'within 5% of the vector ones up to NA 0.86 across the axis and NA 0.43 along it in air; in water the two limits '
    'are NA 1.14 and 0.57.')

big('Annular pupils: depth of focus against NA, air', [
    'As NA increases the paraxial annular depth of focus departs sooner than the circular one.',
    'A thin ring uses the edge of the pupil, where the paraxial phase error is largest.'],
    os.path.join(HN, 'pupils', 'annular_widths_air_z.png'),
    'Along the axis the paraxial model departs sooner with annular pupils.',
    'Left: 2PE; right: 2CE; annular pupils with ε = 0.99. Vector (Richards–Wolf) with the annulus sin θ ≥ ε sin α, '
    'beams polarized along y. Annular depth of focus (2CE, θ = 0), vector against scalar: 155 against 179 µm at NA '
    '0.5 (scalar 15% longer), 65 against 91 µm at 0.7, 25 against 55 µm at 0.9. Annular over circular depth of focus: '
    '47 times at NA 0.5, 42 at 0.7 and 31 at 0.9, against 1/(1 − ε²) = 50 in the paraxial model.')

big('Crossed lenses above NA 0.71', [
    'Two lenses of the same NA fit at right angles up to NA 0.71 in air, where the cones touch.',
    'In water the limit is NA 0.94; Cambaliza & Saloma (2000) note NA 0.7 on p. 34.'],
    os.path.join(TC, 'na_crossing_limit_air.png'),
    'Crossed lenses of the same NA fit up to NA n/√2.',
    'The half-angle of each cone must be at most 45°, so NA ≤ n sin 45° = n/√2: 0.71 in air and 0.94 in water. '
    'Cambaliza & Saloma (2000), p. 34: dual-beam excitation with two identical objectives for 0 ≤ θ ≤ π/2 is possible '
    'for NA ≤ 0.7.',
    r'\mathrm{NA} \le n \sin 45^\circ = \frac{n}{\sqrt{2}}')

# ── Part 3. Two-color excitation with optical pulses ─────────────────────
navy('Part 3. Two-color excitation with optical pulses')
PE = r'E(t) = \int a(\omega)\, e^{-i\omega t}\, d\omega, \quad a(\omega) = \exp\left[-\frac{(\omega-\omega_0)^2\tau^2}' \
    r'{8\ln 2}\right]'
big('Spectrum and waves of a 10-fs pulse', [
    'A pulse is a sum of continuous waves, in phase at t = 0 and out of phase away from it.'],
    os.path.join(PU, 'pulse_waves_spectrum.png'),
    'A pulse is a sum of continuous waves that are in phase near t = 0.',
    'Left: the Gaussian spectrum of a 10-fs pulse at 750 nm, with nine frequencies marked. Right: the waves at those '
    'frequencies, each with its weight a(ω); they are in phase at t = 0 (solid line) and out of phase at 15 fs (dashed '
    'line).', PE)

big('An optical pulse in time', [
    'The sum of the waves falls off away from t = 0 as a Gaussian of width τ, which is the pulse.'],
    os.path.join(PU, 'pulse_waves_sum.png'),
    'The sum of the waves is the pulse.',
    'The sum over the whole spectrum of the 10-fs pulse at 750 nm: the field E(t) and its envelope |E(t)|. The waves '
    'are in phase at t = 0 (solid line) and out of phase at 15 fs (dashed line), where the envelope has fallen to a '
    'few percent of its peak.', PE)

big('Pulse width and spectral bandwidth', [
    'A transform-limited Gaussian pulse of width τ has a spectral bandwidth Δν = 0.441/τ.'],
    os.path.join(PU, 'pulse_gaussian_time_frequency.png'),
    'Shorter pulses have wider spectra.',
    'Left: intensity in time exp(−4 ln2 t²/τ²), FWHM τ, the pulse width. Right: power spectrum against frequency, at '
    '750 nm (solid) and 656 nm (dashed). Spectral bandwidth (FWHM) 88 THz at 5 fs, 44 THz at 10 fs, 22 THz at 20 fs '
    'and 4.4 THz at 100 fs. The dotted line is 428 THz (700 nm).')

big('Spectra of the two pulses against wavelength', [
    'Below about 15 fs the spectra reach 700 nm, where two photons of one pulse make 350 nm.'],
    os.path.join(PU, 'pulse_gaussian_wavelength.png'),
    'Short pulses reach 700 nm.',
    'Power spectrum per unit wavelength at 750 nm (solid) and 656 nm (dashed), for 5, 10, 20 and 100 fs; the visible '
    'range, 380 to 750 nm, is shaded. At 10 fs each spectrum has 31% of its peak at 700 nm (428 THz); at 20 fs and '
    'longer it has almost none.')

s = slide('Photon pairs at the 350-nm level', '')
bullets(s, 0.5, 0.9, 9.0, 1.0, [
    'The signal adds the amplitudes of all photon pairs that reach 350 nm, then squares the sum.',
    'The 350-nm pairs are 750 + 656 nm; the 375- and 328-nm pairs are 750 + 750 and 656 + 656 nm.'], 13)
PA1 = r'A = A^{11} + 2A^{12} + A^{22}, \qquad A^{ab} = \int E_a E_b\, e^{i\omega_e t}\, dt'
PA2 = r'F = |A|^2'
h = equation(s, 1.5, 2.1, 7.0, PA1, 20)
h += equation(s, 1.5, 2.3 + h, 7.0, PA2, 20)
where(s, 1.5, 2.55 + h, 7.0, 'E_1 and E_2 are the fields of the 750- and 656-nm pulses at a point, ω_e is the frequency '
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

big('2CE at 100 fs and with continuous beams, θ = 0 and π', [
    'At 100 fs, pulsed 2CE is the same as with continuous beams with collinear and facing lenses.'],
    os.path.join(PU, 'sweep', 'profiles_100fs_2ce_0_pi.png'),
    'At 100 fs the pulses give the continuous-beam 2CE.',
    'Total 2CE accumulated as the pulses pass the focus, along the axis, paraxial model, NA 0.5, air. The depth of '
    'focus is 3.56 µm with collinear lenses, and 3.52 against 3.56 µm with facing lenses, where the pulses overlap '
    'over 21 µm, six times the focus. So the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of '
    'that length.')

big('2CE at 100 fs and with continuous beams, θ = π/2', [
    'At 100 fs, pulsed 2CE is the same as with continuous beams with crossed lenses.'],
    os.path.join(PU, 'sweep', 'profiles_100fs_2ce_pi2.png'),
    'At 100 fs the pulses give the continuous-beam 2CE with crossed lenses too.',
    'Total 2CE accumulated as the pulses pass the focus, across the axis, paraxial model, NA 0.5, air. The width is '
    '0.76 µm with pulses and with continuous beams; the widths at the three lens angles agree to within 1%.')

big('Depth of focus, collinear and crossed lenses', [
    'With collinear and crossed lenses the 2CE depth of focus stays within a few percent.'],
    os.path.join(PU, 'sweep', 'dof_na_0_pi2.png'),
    'Collinear and crossed lenses keep their depth of focus, so crossed lenses keep the sharpest profile.',
    'Depth of focus with pulses over that with continuous beams, paraxial model, NA 0.3 to 0.5. With collinear '
    'lenses the pulses travel together and overlap over the whole focus, so 2CE keeps its profile down to 4 fs. '
    'With crossed lenses the depth of focus changes by a few percent below about 20 fs; '
    'the 2CE depth of focus grows by up to 6% below 10 fs, because the 375-nm pairs from L1 alone extend along its '
    'axis. In the vector model in air, the crossed-lens profiles match the continuous-beam ones from about 20 to 28 fs '
    'for 2CE.')

big('Depth of focus, facing lenses', [
    'With facing lenses, 2CE forms where the pulses meet, so its depth of focus is shorter.',
    'It shortens more at lower NA, because the focus grows while that stretch stays the same.'],
    os.path.join(PU, 'sweep', 'dof_na_pi.png'),
    'Pulses shorten the 2CE depth of focus with facing lenses, more at lower NA.',
    'Paraxial model, NA 0.3 to 0.5. At NA 0.5 the 2CE depth of focus is 3.56 µm for continuous beams, 2.81 µm at '
    '20 fs and 1.92 µm at 10 fs, about 80% and 60% of the continuous-beam value. At NA 0.3 and 20 fs it is 40% of the '
    'continuous-beam value. 2PE shortens less, because the 350-nm pairs within one pulse need no overlap.')

big('Overlap of the facing pulses in time', [
    'At 20 fs the facing pulses overlap over 4.2 µm, which cuts the 2CE focus to 2.78 µm.'],
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
    'Below about 15 fs one beam alone also excites, through the 375- and 328-nm pairs.',
    '2CE then carries fringes and starts to lose the weak background of continuous beams.'],
    os.path.join(PU, 'sweep', 'strength_vs_tau.png'),
    'Pairs within one pulse matter below 15 fs.',
    'With continuous beams, 2CE needs both beams, which gives its weak background in scattering media. The amplitude '
    'of the 375- and 328-nm pairs is 18% of that of the 350-nm pairs at 10 fs and below 1% at 20 fs. The peak of the '
    'total over that of the 350-nm pairs is 1.02 at 20 fs, 1.15 at 15 fs, 1.73 at 10 fs and 3.1 at 5 fs.')

big('τ to match continuous beams against NA, θ = π', [
    'With facing lenses the pulse width needed to match continuous beams grows as NA decreases.',
    'In water and oil the same results hold at a higher NA, since the focus depends on NA/n.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2ce_pi.png'),
    'Facing lenses need the longest pulses to behave like continuous beams, more so at lower NA.',
    'The pulse width from which the largest difference between the pulsed and continuous-beam profiles stays below 1% '
    'of the peak. Facing lenses, 2CE, vector model in air: about 25 fs at NA 0.9, 87 fs at NA 0.5, 260 fs at NA 0.3 '
    'and 610 fs at NA 0.2. For 2PE it is shorter (62 fs at NA 0.5), because the 350-nm pairs within one pulse need no '
    'overlap. At NA 0.5: 87 fs in air, 164 fs in water and 216 fs in oil. With collinear lenses 4-fs pulses already '
    'give the continuous-beam profiles, and with crossed lenses 2CE does from about 20 to 28 fs (next slide). Solid: '
    'vector; dashed: scalar, drawn up to NA 0.5, where the paraxial model holds. The open triangles mark NAs where '
    'the longest pulse computed is still outside the tolerance.')

big('τ to match continuous beams, θ = 0 and π/2', [
    'With collinear lenses 4-fs pulses, the shortest computed, give the continuous-beam profiles.',
    'With crossed lenses, from NA 0.2 up, 2CE matches continuous beams from about 20 to 28 fs.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2ce_0_pi2.png'),
    'Collinear and crossed lenses match continuous beams with short pulses.',
    'The same measure as the previous slide: the pulse width from which the largest difference between the pulsed '
    'and continuous-beam 2CE profiles stays below 1% of the peak. With collinear lenses the two pulses travel together '
    'and overlap over the whole focus, so the shortest pulse computed, 4 fs, already matches. With crossed lenses '
    '(vector model in air) it is 28 fs at NA 0.2 and 21 fs at NA 0.7; at NA 0.1 it is 54 fs. Crossed lenses fit up to '
    'NA 0.71 in air and 0.94 in water.')

big('τ to match continuous beams, pupils, θ = π', [
    'A longer depth of focus needs a longer pulse to match continuous beams with facing lenses.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2ce_pi.png'),
    'Annular pupils and Gaussian input need longer pulses with facing lenses.',
    'Vector model in air. The figure gives the pulse width from which the 2CE depth of focus stays within 1% of its '
    'continuous-beam value: at NA 0.5 with facing lenses, 100 fs for the circular pupil, 162 fs for the Gaussian input '
    '(α = 4) and 466 fs for the annular pupil with ε = 0.9. By the largest difference between the profiles, the measure '
    'of the slides before, the same three are 87, 139 and 405 fs. The annular pupil with ε = 0.99 stays outside the '
    'tolerance at the longest pulse computed below NA 0.8.')

big('τ to match continuous beams, pupils, θ = 0 and π/2', [
    'With collinear lenses the depth of focus matches continuous beams at 4 fs for all pupils.',
    'With crossed lenses it matches from about 11 to 16 fs at NA 0.4 and above, for all pupils.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2ce_0_pi2.png'),
    'With collinear and crossed lenses the pupil changes the pulse width needed by little.',
    'Vector model in air, pulse width from which the 2CE depth of focus stays within 1% of its continuous-beam value. '
    'With crossed lenses it is 13 to 15 fs for the circular pupil from NA 0.4 to 0.7, 14 to 16 fs for the annular '
    'pupils and 11 to 14 fs for the Gaussian input (α = 4). Below NA 0.4 it rises to 82 fs for the Gaussian input at '
    'NA 0.1 and 54 fs for the circular pupil.')

# ── Part 4. Summary and next steps ───────────────────────────────────────
words('Summary by lens angle', [
    'With collinear lenses a pulse changes nothing down to 4 fs, because the two pulses travel together.',
    'With crossed lenses pulses change the profiles by a few percent below about 20 fs, so crossed lenses keep the '
    'sharpest profile; the lenses fit up to NA 0.71 in air.',
    'With facing lenses pulses shorten the 2CE focus, more so at lower NA, because 2CE forms where the pulses meet.',
    'At the three angles, the paraxial model gives the right spot across the axis to high NA, and too long a focus '
    'along it above about NA 0.43 with collinear and facing lenses.'],
    'The lens angle decides what a pulse changes.',
    'Collinear θ = 0, crossed θ = π/2, facing θ = π. The delay between the two pulses is in the separate deck '
    'pulse_delay.pptx.')

words('Next steps', [
    'Compute pulsed 2CE through a scattering medium, with the Monte Carlo model of the focus and the pulse model.',
    'Give the two pulses unequal widths, which changes their temporal overlap.',
    'Add a chirp, which lengthens the pulses at the focus.',
    'Replace the narrow 350-nm level with a broad absorption band.'],
    'Pulsed 2CE through a scattering medium is the first candidate.',
    'The scattering medium combines the Monte Carlo model of docs/review/06 with the pulse model; it would show '
    'whether 2CE with pulses keeps its weak background. With unequal pulse widths the overlap becomes exp[−4 ln2 Δt²/(τ₁² + τ₂²)]. '
    'For a broad absorption band the signal of the 350-nm pairs is the integral of I₁ I₂ over time.')

words('Glossary (1/2)', [
    'NA = n sin α is the numerical aperture, with α the half-angle of the focusing cone and n the refractive index.',
    'θ is the angle between the axes of lenses L1 and L2, 0 for collinear, π/2 for crossed and π for facing lenses.',
    'λ_1 = 750 nm and λ_2 = 656 nm are the 2CE wavelengths, with 1/λ_e = 1/λ_1 + 1/λ_2 and λ_e = 350 nm.',
    '2CE is two-color excitation, F_{2c} = κ I_1 I_2; 2PE is two-photon excitation at 700 nm, F_{2p} = κ′|U_1 + U_2|^4.',
    'The depth of focus is the FWHM along the axis, and the central spot is the FWHM across it.',
    'x_c and z_c are the displacements of the focus of L2 across and along the axis of L1.'],
    'Glossary.', 'Symbols and terms used in the deck.', size=14)

words('Glossary (2/2)', [
    'The obstruction ratio ε is the inner over the outer radius of an annular pupil.',
    'The truncation parameter α sets how strongly the pupil edge clips a Gaussian input.',
    "Linfoot's fidelity F, structural content C and correlation quality Q are 1 for identical profiles.",
    'The scalar model is the paraxial field of Cambaliza & Saloma (2000); the vector model is the Richards–Wolf field.',
    'τ is the pulse width, the FWHM of the intensity; a transform-limited pulse has Δν = 0.441/τ.',
    'The 350-nm pairs are 750 + 656 nm, the 375-nm pairs 750 + 750 nm and the 328-nm pairs 656 + 656 nm.'],
    'Glossary.', 'Symbols and terms used in the deck.', size=14)

# ── Backup ───────────────────────────────────────────────────────────────
navy('Backup')
big('Spot and depth of focus against NA: 2PE, θ = π/2', [
    'As NA increases the 2PE spot keeps its width, set by the interference of the two beams.'],
    os.path.join(HN, 'cfg_2pe_pi2.png'),
    'With crossed lenses the 2PE spot is one interference fringe.',
    'The 2PE central spot stays at 0.256 µm in air at all NAs, and 0.19 µm in water, in both models within 0.4%. 2PE '
    'is narrower than 2CE and has stronger side lobes, as in Cambaliza & Saloma (2000).')

big('τ to match continuous beams, 2PE, θ = π', [
    'With facing lenses 2PE matches continuous beams at shorter pulses than 2CE, 62 fs at NA 0.5.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2pe_pi.png'),
    'With facing lenses 2PE needs shorter pulses than 2CE.',
    'Largest difference between the pulsed and continuous-beam 2PE profiles below 1% of the peak. At NA 0.5 in air '
    '(vector model) 2PE matches from 62 fs, against 87 fs for 2CE, because the photon pairs within one pulse need no '
    'overlap of the two pulses. Solid: vector; dashed: scalar, drawn up to NA 0.5.')

big('τ to match continuous beams, 2PE, θ = 0 and π/2', [
    'With collinear lenses 2PE matches at 4 fs, and with crossed lenses at 37 fs or shorter.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_2pe_0_pi2.png'),
    'With collinear and crossed lenses 2PE matches continuous beams with short pulses.',
    'Largest difference below 1% of the peak. With crossed lenses in air (vector model) the pulse width is 37 fs at '
    'NA 0.1, 5.7 fs at NA 0.5 and 4 fs, the shortest computed, from NA 0.6.')

big('τ to match continuous beams, 2PE, pupils, θ = π', [
    'With facing lenses a longer depth of focus also needs a longer pulse for 2PE.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2pe_pi.png'),
    'Pupils with a longer focus need longer pulses for 2PE too.',
    'Vector model in air, pulse width from which the 2PE depth of focus stays within 1% of its continuous-beam value. '
    'At NA 0.5 it is 72 fs for the circular pupil.')

big('τ to match continuous beams, 2PE, pupils, θ = 0, π/2', [
    'With collinear lenses all pupils match at 4 fs, and with crossed lenses at 68 fs or shorter.'],
    os.path.join(PU, 'na_sweep', 'tau_cw_vs_na_pupils_2pe_0_pi2.png'),
    'With collinear and crossed lenses the pupils need short pulses for 2PE.',
    'Vector model in air, depth of focus within 1%. With crossed lenses the pulse width is largest at low NA, 68 fs for '
    'the Gaussian input and 44 fs for the circular pupil at NA 0.1, and falls below 10 fs at NA 0.7 for all pupils.')

big('Side lobes of 2PE against NA', [
    'As NA increases the 2PE side lobes weaken, so 2PE images gain contrast.'],
    os.path.join(HN, 'sidelobes.png'),
    'The 2PE side lobes follow the wavelength in the medium.',
    'At θ = π/2 the side lobe falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7 in air; at θ = π from 0.97 to '
    '0.42 at NA 0.9. Their distance from the peak is λ/2n with facing lenses and λ/n with crossed lenses at low NA. '
    '2CE side lobes stay below 1e-3 of the peak.')

ds.keynote_fonts()
out = os.path.join(OUT, '2ce_high_na_pulses.pptx')
prs.save(out)
print('Saved ->', out, f'({len(prs.slides)} slides)')
for f in MISSING:
    print('MISSING', f)
