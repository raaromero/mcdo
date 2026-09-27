"""Slides: reconstruction of Lim & Saloma (2002), one panel per slide, the
original beside the reconstruction, with explanatory slides in between.

Text supports x_c, z_c, λ_1, x^2, _{..} and ^{..} as real sub/superscripts.
Every slide with mathematics carries its LaTeX in the speaker notes, for pasting
into Keynote (Insert > Equation).

    python scripts/make_lim2002_slides.py
    -> ~/Downloads/Research/two_color/lim2002_reconstruction.pptx
"""

import os
import re

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.join(os.path.dirname(__file__), '..')
FIG = os.path.join(ROOT, 'output', '08_two_color', 'lim2002')
ORIG = os.path.join(FIG, 'original')
PAN = os.path.join(FIG, 'panels')
OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_reconstruction.pptx')
NAVY, GREY, CITE = RGBColor(0x0B, 0x3C, 0x5D), RGBColor(0x55, 0x55, 0x55), RGBColor(0x1F, 0x6F, 0xB4)
BLACK = RGBColor(0, 0, 0)
GREEN, RED, AMBER = RGBColor(0x1B, 0x7F, 0x3A), RGBColor(0xB0, 0x1E, 0x1E), RGBColor(0xB0, 0x6A, 0x00)
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]
TOK = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\}|_[A-Za-z0-9]|\^[A-Za-z0-9])')


def rich(p, text, size, color=BLACK, bold=False):
    """Add text to paragraph p, rendering _x, _{..}, ^x, ^{..} as sub/superscripts."""
    for part in TOK.split(text):
        if not part:
            continue
        base = 0
        if part[0] in '_^' and len(part) > 1:
            base = -25000 if part[0] == '_' else 30000
            part = part[2:-1] if part[1] == '{' else part[1:]
        r = p.add_run(); r.text = part
        r.font.size, r.font.bold = Pt(size), bold
        r.font.color.rgb = color
        if base:
            r.font._element.set('baseline', str(base))


def box(s, left, top, width, height):
    tf = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height)).text_frame
    tf.word_wrap = True
    return tf


def title(s, t):
    rich(box(s, 0.4, 0.2, W - 4.2, 0.8).paragraphs[0], t, 26, NAVY, True)


def bullets(s, items, left, top, width, height, size=16):
    tf = box(s, left, top, width, height)
    for i, it in enumerate(items):
        lvl, t = it[0], it[1]; cite = it[2] if len(it) > 2 else None
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        rich(p, ('•  ' if lvl == 0 else '–  ') + t, size if lvl == 0 else size - 2,
             BLACK if lvl == 0 else GREY)
        if cite:
            r = p.add_run(); r.text = f'  [{cite}]'
            r.font.size, r.font.color.rgb = Pt(size - 4), CITE
        p.space_after = Pt(5)


def notes(s, latex):
    s.notes_slide.notes_text_frame.text = '\n'.join(l.strip() for l in latex.strip().splitlines())


def fit(s, path, left, top, max_w, max_h):
    w, h = Image.open(path).size
    k = min(max_w / w, max_h / h)
    s.shapes.add_picture(path, Inches(left + (max_w - w * k) / 2), Inches(top),
                         Inches(w * k), Inches(h * k))


def label(s, left, top, width, t):
    rich(box(s, left, top, width, 0.4).paragraphs[0], t, 15, GREY, True)


VERDICT = {'match': ('Reproduced', GREEN), 'partial': ('Partly reproduced', AMBER),
           'no': ('Not reproduced', RED)}


def verdict(s, v):
    lab, col = VERDICT[v]
    rich(box(s, W - 3.6, 0.3, 3.3, 0.5).paragraphs[0], lab, 18, col, True)


def explain(ttl, items, latex=None, size=20):
    s = prs.slides.add_slide(BLANK); title(s, ttl)
    bullets(s, items, 0.6, 1.1, W - 1.2, H - 1.3, size=size)
    if latex:
        notes(s, latex)
    return s


def compare(ttl, orig, ours, v, items, cite, latex=None):
    """Original and reconstruction side by side, bullets on the right."""
    s = prs.slides.add_slide(BLANK); title(s, ttl); verdict(s, v)
    colw, top = 4.3, 1.35
    label(s, 0.3, 0.95, colw, f'Original [{cite}]')
    label(s, 0.3 + colw + 0.2, 0.95, colw, 'Reconstruction')
    fit(s, os.path.join(ORIG, orig), 0.3, top, colw, H - top - 0.2)
    fit(s, ours, 0.3 + colw + 0.2, top, colw, H - top - 0.2)
    bullets(s, items, 0.3 + 2 * colw + 0.5, 1.0, W - 2 * colw - 0.9, H - 1.2, size=15)
    if latex:
        notes(s, latex)


def compare3(ttl, orig, c_img, q_img, v, items, cite, latex=None,
             labels=('Original, labeled C', 'Reconstruction: C', 'Reconstruction: Q')):
    """Original beside two reconstructions (default: our C and our Q); bullets below."""
    s = prs.slides.add_slide(BLANK); title(s, ttl); verdict(s, v)
    colw, top, fh = 4.1, 1.35, 3.6
    for i, (lab, path) in enumerate(((f'{labels[0]} [{cite}]', os.path.join(ORIG, orig)),
                                      (labels[1], c_img),
                                      (labels[2], q_img))):
        x0 = 0.3 + i * (colw + 0.2)
        label(s, x0, 0.95, colw, lab)
        fit(s, path, x0, top, colw, fh)
    bullets(s, items, 0.4, top + fh + 0.15, W - 0.8, H - top - fh - 0.2, size=15)
    if latex:
        notes(s, latex)


P = lambda name: os.path.join(PAN, name)
LINFOOT_TEX = r'''
F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}
C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}
Q = \frac{\langle |a|\,|t| \rangle}{\langle t^2 \rangle}
2Q - C = F = 1 - \epsilon
'''

# ── background ────────────────────────────────────────────────────────────
BG = os.path.join(ROOT, 'docs', 'two_color')


def figslide(ttl, img, items, latex=None, layout='left', size=17):
    """A background figure with bullets, beside it ('left') or below it ('top')."""
    s = prs.slides.add_slide(BLANK); title(s, ttl)
    if layout == 'left':
        fit(s, os.path.join(BG, img), 0.3, 1.1, 6.2, H - 1.3)
        bullets(s, items, 6.8, 1.1, W - 7.1, H - 1.3, size=size)
    else:
        fit(s, os.path.join(BG, img), 0.3, 1.0, W - 0.6, 3.6)
        bullets(s, items, 0.5, 4.75, W - 1.0, H - 4.85, size=size)
    if latex:
        notes(s, latex)



def var_table(ttl, rows, latex=None):
    """Symbol, meaning and value, one variable per row."""
    s = prs.slides.add_slide(BLANK); title(s, ttl)
    tb = s.shapes.add_table(len(rows) + 1, 3, Inches(0.4), Inches(0.95),
                            Inches(W - 0.8), Inches(0.28 * (len(rows) + 1))).table
    for c, w in enumerate((2.0, 6.6, W - 0.8 - 8.6)):
        tb.columns[c].width = Inches(w)
    for r, row in enumerate([("Symbol", "Meaning", "Value")] + list(rows)):
        tb.rows[r].height = Inches(0.28)
        for c, txt in enumerate(row):
            cell = tb.cell(r, c)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            rich(cell.text_frame.paragraphs[0], txt, 13, BLACK, r == 0)
    if latex:
        notes(s, latex)


def background_slides():
    """Background: microscopy, one and two photons, two colors, focus size, interference, two lenses."""
    explain('What a fluorescence microscope measures', [
        (0, 'Fluorescent molecules in the sample absorb light at one wavelength and re-emit it at a longer one.'),
        (0, 'A lens focuses the excitation light to a small spot, and the spot is scanned point by point through the sample.'),
        (0, 'The fluorescence collected at each scan position becomes one pixel of the image.'),
        (0, 'The point spread function (PSF) is the pattern of excitation around the focus: the image of a single point-like molecule.'),
        (1, 'The image is the sample blurred by the PSF, so a smaller PSF means sharper images.'),
        (1, 'Side lobes of the PSF produce false detail, and a weaker PSF peak means less signal.'),
        (0, 'Lim & Saloma ask how the PSF and its peak change when the two excitation foci that form it do not coincide.', 'LS02 p. 122'),
    ], size=19)

    figslide('One photon versus two photons', 'bg_nonlinear.png', [
        (0, 'In one-photon excitation the absorption rate is proportional to the intensity I.'),
        (1, 'Every plane through the beam carries the same power, so one-photon fluorescence comes from the whole cone of light (blue).'),
        (0, 'Two photons can be absorbed together through a short-lived virtual state, at a rate proportional to I^2.', 'Göppert-Mayer 1931'),
        (1, 'I^2 integrated over a plane falls away from the focus, so excitation is confined to the focal volume (red).'),
        (0, 'This confinement gives three-dimensional sectioning without a pinhole, the basis of two-photon microscopy.', 'Denk 1990'),
        (0, 'The plot is computed for NA 0.5 at 700 nm, the 2PE setting of the paper.'),
    ], r'''
    R_{1} \propto I, \qquad R_{2} \propto I^2
    \int I\, dA = \text{const}, \qquad \int I^2\, dA \ \text{peaks at the focus}
    ''', size=16)

    figslide('Two-color excitation', 'bg_energy_levels.png', [
        (0, 'The two photons can come from two beams of different color, as long as their energies add up to the transition.'),
        (1, 'ħω_1 + ħω_2 = ħω_e, or 1/λ_1 + 1/λ_2 = 1/λ_e.'),
        (1, 'Here 750 nm and 656 nm reach the same 3.54 eV state as 350 nm (one photon) or 700 + 700 nm (two photons).'),
        (0, 'Two-color two-photon excitation of fluorescence has been observed experimentally.', 'Lakowicz 1996'),
        (0, 'The rate is proportional to the product I_1 I_2, so fluorescence exists only where both foci overlap.', 'CS00'),
        (0, 'Each beam alone could still drive ordinary two-photon absorption if its photons suffice, so probes are chosen to suppress it.', 'LS03'),
    ], r'''
    \hbar\omega_1 + \hbar\omega_2 = \hbar\omega_e \quad\Longleftrightarrow\quad \frac{1}{\lambda_1} + \frac{1}{\lambda_2} = \frac{1}{\lambda_e}
    F_{2c}(P) = \kappa_{2c}\, I_1(P)\, I_2(P)
    ''', size=16)

    explain('How big a focus is', [
        (0, 'A lens of numerical aperture NA = n sin α focuses light from a cone of half-angle α.', 'Born & Wolf'),
        (0, 'Across the axis the focus is an Airy pattern, whose first dark ring lies at r = 0.61 λ/NA.'),
        (1, 'For λ = 750 nm and NA 0.5 this is 0.92 µm, and the intensity full width at half maximum is 0.51 λ/NA = 0.77 µm.'),
        (0, 'Along the axis the intensity falls as sinc^2(u/4), whose first zero lies at z = 2nλ/NA^2.'),
        (1, 'For the same lens this is 6.0 µm, and the full width at half maximum is 5.3 µm.'),
        (0, 'The focus is therefore about seven times longer along the axis than across it.'),
        (1, 'This is why the paper’s PSF plots span ±1 µm across and ±5 µm along the axis.'),
        (1, 'It is also why a second beam at an angle can shorten the region where both beams overlap.'),
        (0, 'The paper’s model is the scalar paraxial one, adequate up to NA ≈ 0.5.', 'LS02 p. 122'),
    ], r'''
    \mathrm{NA} = n\sin\alpha
    r_0 = 0.61\,\frac{\lambda}{\mathrm{NA}}, \qquad \Delta r_{1/2} = 0.51\,\frac{\lambda}{\mathrm{NA}}
    I(0,z) \propto \mathrm{sinc}^2\!\left(\frac{u}{4}\right), \qquad u = \frac{2\pi}{\lambda}\,\frac{\mathrm{NA}^2}{n}\, z, \qquad z_0 = \frac{2n\lambda}{\mathrm{NA}^2}
    ''', size=18)

    figslide('Why one color interferes and two colors do not', 'bg_beating.png', [
        (0, 'Two beams at the same point give |E_1 + E_2|^2 = |E_1|^2 + |E_2|^2 + 2 Re[E_1 E_2^* e^{−i(ω_1 − ω_2)t}].'),
        (0, 'For one color (ω_1 = ω_2) the cross term is steady and set by the relative phase, so the beams interfere into fringes (left).', 'CS00'),
        (0, 'For two colors it oscillates at the difference frequency, here 57 THz with a 17.5 fs period, and averages to I_1 + I_2 (right).'),
        (0, 'So 2PE with two beams follows |U_1 + U_2|^4 and has fringes, while 2CE follows I_1 I_2 and has none.', 'LS02 p. 123'),
    ], r'''
    |\mathbf{E}|^2 = |\mathbf{E}_1|^2 + |\mathbf{E}_2|^2 + 2\,\mathrm{Re}\!\left[\mathbf{E}_1\cdot\mathbf{E}_2^{*}\, e^{-i(\omega_1-\omega_2)t}\right]
    F_{2p} = \kappa_{2p}\,|U_1 + U_2|^4, \qquad F_{2c} = \kappa_{2c}\, I_1 I_2
    ''', layout='top', size=16)

    figslide('Two lenses at an angle', 'setup.png', [
        (0, 'Two opposed lenses (θ = π) form the 4Pi arrangement, which shortens the focus along the axis.', 'Hell 1992'),
        (0, 'Two perpendicular lenses (θ = π/2) are the idea of theta microscopy: each beam’s narrow width cuts the other’s long axis.', 'Lindek 1999'),
        (0, 'Two cones of half-angle α fit at θ = π/2 only if α ≤ 45°, that is NA ≤ n/√2 = 0.71 in air.', 'CS00 p. 34'),
        (0, 'Both schemes need the two foci to coincide, which is the confocality condition this paper tests.', 'LS02 p. 123'),
    ], r'''
    \alpha \le 45^\circ \quad\Longleftrightarrow\quad \mathrm{NA} \le \frac{n}{\sqrt{2}}
    ''', size=17)

    explain('Where this paper sits', [
        (0, 'Cambaliza & Saloma (2000) introduced the comparison of 2CE against 2PE with two focused beams, including circular against annular pupils and the gap between the two wavelengths, always with the foci aligned.', 'CS00'),
        (0, 'Lim & Saloma (2002), reconstructed here, moves the focus of beam 2 away from that of beam 1 and measures the damage.', 'LS02'),
        (0, 'Lim & Saloma (2003) keeps the foci together but gives each beam spherical aberration.', 'LS03'),
        (0, 'All three use the same scalar paraxial focus at NA 0.5, n = 1, with λ_1 = 750 nm, λ_2 = 656 nm and 700 nm for 2PE.'),
    ], size=19)

    explain('Background references', [
        (0, 'Born & Wolf: M. Born and E. Wolf, Principles of Optics, 7th ed. (Cambridge University Press, 1999).'),
        (0, 'Göppert-Mayer 1931: M. Göppert-Mayer, Ann. Phys. 401, 273–294 (1931), doi:10.1002/andp.19314010303.'),
        (0, 'Denk 1990: W. Denk, J. H. Strickler and W. W. Webb, Science 248, 73–76 (1990), doi:10.1126/science.2321027.'),
        (0, 'Lakowicz 1996: J. R. Lakowicz, I. Gryczynski, H. Malak and Z. Gryczynski, Photochem. Photobiol. 64, 632–635 (1996), doi:10.1111/j.1751-1097.1996.tb03116.x.'),
        (0, 'Hell 1992: S. Hell and E. H. K. Stelzer, J. Opt. Soc. Am. A 9, 2159 (1992), doi:10.1364/JOSAA.9.002159.'),
        (0, 'Lindek 1999: S. Lindek and E. H. K. Stelzer, Opt. Lett. 24, 1505–1507 (1999), doi:10.1364/OL.24.001505.'),
        (0, 'CS00: M. O. Cambaliza and C. Saloma, Opt. Commun. 184, 25–35 (2000), doi:10.1016/S0030-4018(00)00929-9.'),
        (0, 'LS02: M. Lim and C. Saloma, Opt. Commun. 207, 121–130 (2002), doi:10.1016/S0030-4018(02)01530-4.'),
        (0, 'LS03: M. Lim and C. Saloma, Appl. Opt. 42, 3398–3406 (2003), doi:10.1364/AO.42.003398.'),
    ], size=14)



def equations_slides():
    """All equations and variables, with LaTeX in the notes."""
    # ── equations and variables, as text (LaTeX in the notes) ─────────────────
    explain('Equations', [
        (0, 'One focused beam, Eq. 1: U(u, v) = (2πi a^2 A / λ f^2) e^{−i(f/a)²u} ∫_0^1 J_0(vρ) e^{−iuρ²/2} ρ dρ', 'p. 122'),
        (0, 'Optical coordinates: u = (2π/λ)(a/f)^2 z and v = (2π/λ)(a/f)(x^2 + y^2)^{1/2}, with a/f = NA.', 'p. 122'),
        (0, 'Two-color energy condition: 1/λ_e = 1/λ_1 + 1/λ_2.', 'p. 121'),
        (0, 'Intensities: I_1(P) = |U_1(P)|^2 and I_2(P; θ; x_c, z_c) = |U_2(P; θ; x_c, z_c)|^2.', 'p. 123'),
        (0, '2CE signal: F_{2c}(P; θ; x_c, z_c) = κ_{2c} I_2(P; θ; x_c, z_c) I_1(P).', 'p. 123'),
        (0, '2PE signal: F_{2p}(P; θ; x_c, z_c) = κ_{2p} |U_2(P; θ; x_c, z_c) + U_1(P)|^4.', 'p. 123'),
        (0, 'Focus separation: d = (x_c^2 + z_c^2)^{1/2}.', 'p. 123'),
        (0, 'Linfoot: F = 1 − ⟨(t − a)^2⟩/⟨t^2⟩, C = ⟨a^2⟩/⟨t^2⟩, Q = ⟨|a||t|⟩/⟨t^2⟩, and 2Q − C = F = 1 − ε.', 'p. 126'),
    ], r'''
    U(u,v) = \frac{2\pi i a^2 A}{\lambda f^2}\, e^{-i (f/a)^2 u} \int_0^1 J_0(v\rho)\, e^{-\frac{i}{2} u \rho^2}\, \rho\, d\rho
    u = \frac{2\pi}{\lambda} \left(\frac{a}{f}\right)^2 z, \qquad v = \frac{2\pi}{\lambda}\, \frac{a}{f}\, \sqrt{x^2 + y^2}
    \frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}
    I_1(P) = |U_1(P)|^2, \qquad I_2(P;\theta;x_c,z_c) = |U_2(P;\theta;x_c,z_c)|^2
    F_{2c}(P;\theta;x_c,z_c) = \kappa_{2c}\, I_2(P;\theta;x_c,z_c)\, I_1(P)
    F_{2p}(P;\theta;x_c,z_c) = \kappa_{2p}\, \left| U_2(P;\theta;x_c,z_c) + U_1(P) \right|^4
    d = \left(x_c^2 + z_c^2\right)^{1/2}
    F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \quad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, \quad Q = \frac{\langle |a|\,|t| \rangle}{\langle t^2 \rangle}, \quad 2Q - C = F = 1 - \epsilon
    ''', size=17)

    var_table('Variables and definitions', [
        ('λ_1', 'wavelength of beam 1 in 2CE', '750 nm'),
        ('λ_2', 'wavelength of beam 2 in 2CE', '656 nm'),
        ('λ_{2p}', 'wavelength of both beams in 2PE', '700 nm'),
        ('λ_e', 'single-photon excitation wavelength, taken equal to the fluorescence λ_f', '350 nm'),
        ('NA = a/f', 'numerical aperture: aperture radius a over focal length f', '0.5'),
        ('n', 'refractive index of the medium', '1 (air)'),
        ('u, v', 'axial and radial optical coordinates', 'u = (2π/λ) NA^2 z, v = (2π/λ) NA r'),
        ('ρ', 'normalized radius on the pupil', '0 to 1'),
        ('L1, L2', 'the lenses that focus beams 1 and 2', 'identical'),
        ('O, O′', 'geometric foci of L1 and L2', 'O at the origin, O′ = (x_c, z_c)'),
        ('θ', 'angle between the optical axes of L1 and L2', '0, π/2, π'),
        ('x_c, z_c', 'offsets of O′ across and along the axis of L1', 'in λ_1 (λ_{2p} for 2PE)'),
        ('d', 'separation of the foci', '(x_c^2 + z_c^2)^{1/2}'),
        ('P', 'observation point', '(x, y, z)'),
        ('U_1, U_2', 'fields of beams 1 and 2 at P', 'Eq. (2)'),
        ('I_1, I_2', 'intensities of beams 1 and 2 at P', 'I = |U|^2'),
        ('F_{2c}, F_{2p}', '2CE and 2PE fluorescence at P', 'κ_{2c} I_1 I_2, κ_{2p} |U_1 + U_2|^4'),
        ('κ_{2c}, κ_{2p}', '2CE and 2PE cross-sections of the sample', 'constants'),
        ('F^p', 'peak fluorescence relative to the aligned peak', '0 to 1'),
        ('t, a', 'aligned and misaligned PSFs, each scaled to a peak of 1', '100 × 100 point x–z field'),
        ('F, C, Q', 'Linfoot’s fidelity, structural content and correlation quality', 'F = 2Q − C'),
    ], r'''
    \lambda_1 = 750\ \mathrm{nm},\ \lambda_2 = 656\ \mathrm{nm},\ \lambda_{2p} = 700\ \mathrm{nm},\ \lambda_e = \lambda_f = 350\ \mathrm{nm}
    \mathrm{NA} = a/f = 0.5, \quad n = 1
    O' = (x_c, z_c), \quad d = \left(x_c^2 + z_c^2\right)^{1/2}
    F^{p}_{2c},\ F^{p}_{2p}, \quad \kappa_{2c},\ \kappa_{2p}
    ''')



def setup_slides():
    """The paper's question and model, piece by piece, ending with Fig. 1."""
    # ── the paper, piece by piece ─────────────────────────────────────────────
    explain('The question the paper asks', [
        (0, 'In two-color excitation (2CE), a molecule absorbs one photon from each of two beams of different color.'),
        (1, 'The photon energies add, so 1/λ_e = 1/λ_1 + 1/λ_2; here 750 nm and 656 nm photons together reach a 350 nm transition.', 'p. 121'),
        (0, 'Each beam is focused by its own lens, and fluorescence happens only where the two foci overlap.'),
        (0, 'The confocality condition requires the two foci to sit at the same point.'),
        (0, 'The paper asks how quickly the signal and the shape of the focus degrade when the two foci are separated.', 'p. 122'),
        (0, 'It compares 2CE against two-photon excitation (2PE), in which both beams have the same color.'),
    ], r'''
    \frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}
    ''')

    explain('Why two colors behave differently from one', [
        (0, 'The two-photon absorption rate grows as the square of the intensity, so excitation is confined to the focus.'),
        (0, 'In 2CE the rate is proportional to the product I_1 I_2 of the two beams’ intensities.', 'p. 123'),
        (1, 'The product is zero wherever either beam is absent.'),
        (1, 'Two different colors do not interfere, because their cross term oscillates at the difference frequency and averages out.'),
        (0, 'In 2PE with two beams of one color, the rate is proportional to |U_1 + U_2|^4.', 'p. 123'),
        (1, 'The fields add before squaring, so the two beams interfere and produce fringes.'),
        (0, 'One therefore expects 2CE to tolerate misalignment better, since it has no fringes to shift.'),
    ], r'''
    F_{2c}(P;\theta;x_c,z_c) = \kappa_{2c}\, I_2(P;\theta;x_c,z_c)\, I_1(P)
    F_{2p}(P;\theta;x_c,z_c) = \kappa_{2p}\, \left| U_2(P;\theta;x_c,z_c) + U_1(P) \right|^4
    I_1(P) = |U_1(P)|^2, \qquad I_2(P;\theta;x_c,z_c) = |U_2(P;\theta;x_c,z_c)|^2
    ''')

    explain('How one focused beam is computed', [
        (0, 'Each lens focuses a uniform plane wave with numerical aperture NA = 0.5 in air (n = 1).', 'p. 122'),
        (0, 'In the Debye picture, the focus is a sum of plane waves arriving from every direction inside the lens’s cone.'),
        (0, 'At low NA this sum reduces to the scalar paraxial field U(u, v) of Eq. 1.', 'p. 122'),
        (1, 'U(u, v) ∝ e^{−i(f/a)²u} ∫_0^1 J_0(vρ) e^{−iuρ²/2} ρ dρ'),
        (1, 'v = (2π/λ)(a/f) r is the radial distance and u = (2π/λ)(a/f)^2 z is the axial distance, both scaled by NA and λ.'),
        (0, 'The result is an Airy spot across the axis and a sinc^2 profile along it.'),
        (0, 'Polarization is ignored, which is acceptable at NA 0.5 but at the edge of where scalar theory holds.'),
    ], r'''
    U(u,v) = \frac{2\pi i a^2 A}{\lambda f^2}\, e^{-i (f/a)^2 u} \int_0^1 J_0(v\rho)\, e^{-\frac{i}{2} u \rho^2}\, \rho\, d\rho
    u = \frac{2\pi}{\lambda} \left(\frac{a}{f}\right)^2 z, \qquad v = \frac{2\pi}{\lambda}\, \frac{a}{f}\, \sqrt{x^2 + y^2}, \qquad \frac{a}{f} = \mathrm{NA}
    ''')

    explain('The geometry, symbol by symbol', [
        (0, 'L1 is the lens that focuses beam 1, of wavelength λ_1 = 750 nm, along the z axis.', 'p. 123'),
        (0, 'L2 is an identical lens that focuses beam 2, of wavelength λ_2 = 656 nm.', 'p. 123'),
        (0, 'O is the geometric focus of L1, taken as the origin of the coordinates.'),
        (0, 'O′ = (x_c, z_c) is the geometric focus of L2.'),
        (1, 'x_c is the offset of O′ across the axis of L1, and z_c is its offset along that axis, both in units of λ_1.'),
        (0, 'θ is the angle between the optical axes of L2 and L1: θ = π means the lenses face each other, θ = π/2 means they are perpendicular.'),
        (0, 'd = (x_c^2 + z_c^2)^{1/2} is the separation of the foci; the confocality condition holds only when d = 0.', 'p. 123'),
        (0, 'P = (x, y, z) is the observation point, and U_1(P) and U_2(P) are the fields of the two beams there.'),
        (0, 'For 2PE both beams have λ_{2p} = 700 nm, and offsets are in units of λ_{2p}.', 'p. 125'),
    ], r'''
    O' = (x_c, z_c), \qquad d = \left(x_c^2 + z_c^2\right)^{1/2}
    \lambda_1 = 750\ \mathrm{nm}, \quad \lambda_2 = 656\ \mathrm{nm}, \quad \lambda_e = 350\ \mathrm{nm}, \quad \lambda_{2p} = 700\ \mathrm{nm}
    ''', size=18)

    explain('Rotating beam 2 into place', [
        (0, 'The field of beam 2 at P is the one-beam field evaluated in beam 2’s own frame, which is rotated by θ and centered on O′.'),
        (0, 'In real space, the point P is expressed in that frame by the rotation below.'),
        (1, 'z_b = (x − x_c) sin θ + (z − z_c) cos θ'),
        (1, 'x_b = (x − x_c) cos θ − (z − z_c) sin θ'),
        (0, 'The paper writes the rotation on the optical coordinates instead: u_r = u cos θ − v sin θ and v_r = v cos θ + u sin θ.', 'p. 122'),
        (1, 'Because u and v scale differently with NA, this is not a rotation of space.'),
        (0, 'The optical-coordinate form gives a θ = π/2 in-plane loss of −0.21 x_c^2, while the paper reports −0.06 x_c^2.'),
        (0, 'The real-space rotation gives −0.063 x_c^2, so the reconstruction uses it throughout.'),
    ], r'''
    z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta
    x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta
    u_r = u\cos\theta - v\sin\theta, \qquad v_r = v\cos\theta + u\sin\theta
    ''', size=18)

    # ── Fig. 1 ────────────────────────────────────────────────────────────────
    compare('Fig. 1: geometry', 'orig_fig1.png', os.path.join(FIG, 'fig1_geometry.png'), 'match', [
        (0, 'Beam 1, of wavelength λ_1, is focused by lens L1 along the z axis to the point O.'),
        (0, 'Beam 2, of wavelength λ_2, is focused by lens L2, whose axis makes the angle θ with the z axis, to the point O′ = (x_c, z_c).'),
        (0, 'The reconstruction draws the same elements and labels.', 'p. 123'),
    ], 'p. 123', r"O' = (x_c, z_c)")



def read_psf_slide():
    """How to read Figs. 2-3."""
    # ── how to read Figs. 2-3 ─────────────────────────────────────────────────
    explain('Reading a point spread function (Figs. 2–3)', [
        (0, 'The point spread function (PSF) is the fluorescence pattern produced by a single point in the sample.'),
        (1, 'It is F_{2c} or F_{2p} itself, normalized so that its peak is 100.', 'p. 123'),
        (0, 'The plots show contours at 1, 10, 20, 40, 60 and 80% of the peak in the x–z plane.'),
        (1, 'x runs across beam 1 and z along it; each plot is 2 µm wide and 10 µm tall.'),
        (0, 'A compact PSF without side lobes gives sharp images.'),
        (0, 'Side lobes and fringes create false detail and lower the image contrast.'),
        (0, 'Fig. 2 has the foci aligned, and Fig. 3 moves beam 2’s focus to x_c = 0.4 µm, z_c = 1 µm.'),
    ])



def read_peak_slide():
    """How to read Fig. 4."""
    # ── how to read Fig. 4 ────────────────────────────────────────────────────
    explain('Peak fluorescence against misalignment (Fig. 4)', [
        (0, 'For each position O′ = (x_c, z_c) of beam 2’s focus, the PSF is computed and its maximum taken.'),
        (0, 'Dividing by the aligned maximum gives F_{2c}^p or F_{2p}^p, the fraction of the signal that survives.', 'p. 126'),
        (0, 'Each point of the contour map over (x_c, z_c) therefore stands for one whole misaligned PSF.'),
        (1, 'A contour labeled 80 marks the offsets at which 80% of the aligned signal survives.'),
        (0, 'Losing signal lowers the signal-to-noise ratio of the image.'),
        (0, 'The paper fits the loss with polynomials in x_c and z_c.', 'p. 126'),
    ], r'''
    F^{p}_{2c}(\pi/2) = -0.06\,x_c^2 + 1
    F^{p}_{2c}(0) = -0.37\,x_c^4 + 0.01\,x_c^3 - 1.14\,x_c^2 + 0.98
    F^{p}_{2c}(0) = -0.027\,z_c^2 + 0.996, \qquad F^{p}_{2c}(\pi/2) = -0.045\,z_c^2 + 0.986
    ''')



def linfoot_slides():
    """Linfoot's criteria and the C/Q labels."""
    # ── how to read Figs. 5-6 ─────────────────────────────────────────────────
    explain("Linfoot's criteria (Figs. 5–6)", [
        (0, 'Peak signal alone is not enough, because the shape of the PSF matters too.', 'p. 126'),
        (0, 'The misaligned PSF a is compared with the aligned PSF t, each scaled to a peak of 1, over the whole plot.'),
        (0, 'Fidelity F measures overall similarity: 1 means identical, and negative values mean worse than a blank image.'),
        (0, 'Structural content C measures relative sharpness: above 1 means the misaligned PSF has broader peaks.', 'p. 126'),
        (0, 'Correlation quality Q measures how well the peaks overlap, and falls as they move apart.'),
        (0, 'The three are tied by F = 2Q − C.', 'p. 126'),
        (0, 'Each criterion is plotted as a surface over (x_c, z_c).'),
    ], LINFOOT_TEX)

    explain('The C and Q labels in Figs. 5–6', [
        (0, 'The paper’s text and panels describe a quantity labeled C that falls to about 0 at |z_c| = 1.33 λ_1 while F ≈ −0.8.', 'p. 128'),
        (0, 'Because Q ≥ 0, the identity F = 2Q − C requires C ≥ −F, so F = −0.8 needs C ≥ 0.8.'),
        (0, 'The reconstruction gives C = 1.00 and Q = 0.04 there, with F = −0.91.'),
        (0, 'The paper also says Q rises above 1 at θ = π; in the reconstruction it is C that rises above 1 there, up to 2.37.', 'p. 127'),
        (0, 'The paper therefore appears to swap the names C and Q, so its second column corresponds to our Q.'),
        (0, 'The next slides show the paper’s panel beside both our C and our Q.'),
    ], LINFOOT_TEX, size=19)



def theta0_slides():
    """Fig. 6(c)-(d) against our theta = pi/2 and theta = 0."""
    # ── Fig. 6(c)–(d) against θ = 0 ───────────────────────────────────────────
    compare3('Fig. 6(c) against θ = π/2 and θ = 0',
             'orig_fig6c.png', P('fig6_linfoot_p3.png'), P('fig6_theta0_p1.png'), 'partial', [
        (0, 'The paper’s F is a smooth dome between about −1.2 and 1, longer along z_c than along x_c, with ripples at the edges.'),
        (0, 'Our F at θ = π/2 has three narrow spikes on a floor that reaches −5, so it does not match.'),
        (0, 'Our F at θ = 0, with no other change to the model, is a dome between −0.91 and 1 with rippled edges, matching the paper’s shape.')],
        'p. 129', LINFOOT_TEX,
        labels=('Original, captioned θ = π/2', 'Ours, θ = π/2', 'Ours, θ = 0'))
    compare3('Fig. 6(d) against θ = π/2 and θ = 0',
             'orig_fig6d.png', P('fig6_linfoot_p4.png'), P('fig6_theta0_p2.png'), 'partial', [
        (0, 'The paper’s panel is labeled C and fluctuates between about 0.3 and 1 over the whole map.'),
        (0, 'Our Q at θ = π/2 has isolated spikes and does not match.'),
        (0, 'Our Q at θ = 0 fluctuates between 0.38 and 1 with wavy ridges, matching the paper’s shape; values above 1 are clipped at the top of the axis, as in the paper.'),
        (0, 'Our C at θ = 0 lies between 0.85 and 3.3, so the panel again shows Q rather than C.')],
        'p. 129', LINFOOT_TEX,
        labels=('Original, labeled C', 'Ours: Q, θ = π/2', 'Ours: Q, θ = 0'))
    explain('Why Fig. 6(c)–(d) do not match at θ = π/2', [
        (0, 'The same model reproduces the paper’s θ = π/2 panels in Fig. 4(d) and Fig. 5(c)–(d), so the θ = π/2 geometry itself is right.'),
        (0, 'Five changes to the model were tested for 2PE at θ = π/2, and none gives the paper’s dome:'),
        (1, 'Normalizing the misaligned PSF to the aligned peak gives a flat plane with three spikes.'),
        (1, 'Putting the carrier e^{ikz} on the lab z axis, as the paper’s Eq. (2) is written, gives a ridge along z_c.'),
        (1, 'Rotating beam 2 in optical coordinates (u, v), as Eq. (2) is written, gives many spikes.'),
        (1, 'Combining both of these gives a ridge along z_c.'),
        (0, 'At a true θ = π/2 the two crossed 700 nm beams form interference fringes, so F swings sharply as O′ moves; the paper itself describes “rapid fluctuations” from interference.', 'p. 129'),
        (0, 'Our unchanged model at θ = 0, where the two beams travel in the same direction, reproduces both panels’ shapes.'),
        (0, 'The paper evaluates θ = 0, π/2 and π but shows no separate θ = 0 panel, so Fig. 6(c)–(d) are most likely θ = 0 mislabeled as θ = π/2.', 'p. 122'),
        (0, 'This rests on shape and range only, because the paper quotes no numbers for Fig. 6(c)–(d).'),
    ], size=16)



def conclusions_slide():
    """The paper's conclusions."""
    # ── conclusions, findings, summary ────────────────────────────────────────
    explain('What the paper concludes', [
        (0, 'The paper concludes that 2CE is more tolerant of misalignment than 2PE.', 'p. 129'),
        (1, 'At θ = π/2 the 2CE peak drops by less than 20% for in-plane offsets |x_c| ≤ 1.5 λ_1.'),
        (1, 'Along z the 2CE peak drops by less than 20% for |z_c| < 1.8 λ_1 at θ = π/2 and |z_c| < 2.7 λ_1 at θ = 0 and π.'),
        (0, 'Misalignment narrows the 2CE spot and can introduce spurious peaks.', 'p. 129'),
        (0, 'The 2PE focus is degraded by interference between its two beams.', 'p. 129–130'),
        (0, 'The reconstruction agrees with each of these statements.'),
    ], size=19)


def swap_slide():
    """The C/Q swap along one cut."""
    s = prs.slides.add_slide(BLANK); title(s, 'The swap, shown along one cut')
    fit(s, os.path.join(FIG, 'labeling_FCQ.png'), 0.3, 1.0, 7.6, H - 1.2)
    bullets(s, [
        (0, 'This cut is 2CE at θ = π/2 with x_c = 0, the case the paper quotes on p. 128.'),
        (0, 'The paper reports F ≈ −0.8 (red circles) and "C" ≈ 0 (black squares) at |z_c| = 1.33 λ_1.'),
        (0, 'Our F is −0.91 there, close to the paper’s value.'),
        (0, 'Our C is 1.00, far from the paper’s "C", while our Q is 0.04, matching it.'),
        (0, 'The identity F = 2Q − C holds in the reconstruction to 10^{−15}.'),
    ], 8.1, 1.1, W - 8.4, H - 1.3, size=16)
    notes(s, LINFOOT_TEX)




# ── full deck: one panel per slide ────────────────────────────────────────
# ── title ─────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
rich(box(s, 0.8, 2.3, W - 1.6, 1.0).paragraphs[0], 'Reconstruction of Lim & Saloma (2002)', 40, NAVY, True)
rich(box(s, 0.8, 3.4, W - 1.6, 1.5).paragraphs[0],
     '"Confocality condition in two-color excitation microscopy with two focused excitation '
     'beams," Opt. Commun. 207, 121–130 (2002), doi:10.1016/S0030-4018(02)01530-4', 18, GREY)

background_slides()
equations_slides()
setup_slides()
read_psf_slide()
F23 = [
    ('2', 'a', '2CE, θ = π, foci aligned', 'match', [
        (0, 'With two opposed lenses of different color, the PSF is a single smooth spot with no fringes.'),
        (0, 'In both plots the 1% contour reaches x ≈ ±0.6 µm and z ≈ ±4 µm.')]),
    ('2', 'b', '2PE, θ = π, foci aligned', 'match', [
        (0, 'With two opposed beams of one color, the beams interfere into a standing wave along z.'),
        (0, 'In both plots the fringes fill an envelope reaching z ≈ ±4 µm.')]),
    ('2', 'c', '2CE, θ = π/2, foci aligned', 'match', [
        (0, 'With perpendicular lenses, the product of two elongated spots is short along z and long along x.'),
        (0, 'In both plots the 1% contour reaches x ≈ ±0.8 µm, with 1% side lobes at z ≈ ±1.1 µm.')]),
    ('2', 'd', '2PE, θ = π/2, foci aligned', 'match', [
        (0, 'Perpendicular beams of one color interfere in tilted fringes.'),
        (0, 'In both plots the fringes rise to the right and the 1% envelope reaches z ≈ ±2.8 µm.')]),
    ('3', 'a', '2CE, θ = π, x_c = 0.4 µm, z_c = 1 µm', 'match', [
        (0, 'When misaligned, the 2CE spot moves between the two foci but stays clean.'),
        (0, 'The paper places the peak at the midpoint of O and O′, which is (0.20, 0.50) µm.', 'p. 126'),
        (0, 'The reconstruction places it at (0.23, 0.55) µm.'),
        (0, 'In both plots the 1% contour bulges to the left near z = 0.')]),
    ('3', 'b', '2PE, θ = π, x_c = 0.4 µm, z_c = 1 µm', 'match', [
        (0, 'The 2PE fringes follow the misaligned beam and their envelope shifts toward O′.'),
        (0, 'The reconstruction places the peak at (0.20, 0.50) µm.')]),
    ('3', 'c', '2CE, θ = π/2, x_c = 0.4 µm, z_c = 1 µm', 'match', [
        (0, 'The perpendicular 2CE spot follows beam 2 along z only.', 'p. 126'),
        (0, 'The reconstruction places the peak at (0.01, 1.00) µm.')]),
    ('3', 'd', '2PE, θ = π/2, x_c = 0.4 µm, z_c = 1 µm', 'match', [
        (0, 'The tilted 2PE fringes distort and spread when the foci are misaligned.'),
        (0, 'In both plots the fringes sit near z ≈ 1 µm and the 1% envelope runs from z ≈ −3 to +2.5 µm.')]),
]
for n, t, lab, v, items in F23:
    k = 'abcd'.index(t) + 1
    compare(f'Fig. {n}({t}): {lab}', f'orig_fig{n}{t}.png', P(f'fig{n}_contours_p{k}.png'), v,
            items, 'p. 124' if n == '2' else 'p. 125')

read_peak_slide()
F4 = [
    ('a', 'peak fluorescence, 2CE, θ = π', 'match', [
        (0, 'The contours are elongated, so the signal tolerates offsets along z far better than across it.'),
        (0, 'The paper reports a 20% drop at x_c = 0.37 λ_1; the reconstruction gives 17.6%.', 'p. 126'),
        (0, 'The paper fits −0.027 z_c^2 + 0.996 along z; the reconstruction gives −0.027 z_c^2 + 0.998.', 'p. 126'),
        (0, 'The paper reports a 20% drop at z_c = 2.7 λ_1; the reconstruction gives 19.3%.', 'p. 126'),
        (0, 'The paper’s quartic fit in x_c matches ours up to x_c = 0.37 (0.818 against 0.824) but turns negative at x_c = 0.9, so it holds only near the axis.', 'p. 126')]),
    ('b', 'peak fluorescence, 2PE, θ = π', 'match', [
        (0, 'The 2PE map looks almost the same as the 2CE map, because the peak alone hides the fringes.'),
        (0, 'In both plots the contours are ellipses, with small 10% islands at x_c ≈ ±1.35.')]),
    ('c', 'peak fluorescence, 2CE, θ = π/2', 'match', [
        (0, 'The contours are horizontal bands, so offsets across the axis barely matter while offsets along it do.'),
        (0, 'The paper fits −0.06 x_c^2 + 1 in plane; the reconstruction gives −0.063 x_c^2 + 0.999.', 'p. 126'),
        (0, 'The paper reports an 11% drop at x_c = 1.33 λ_1; the reconstruction gives 11.1%.', 'p. 126'),
        (0, 'The paper fits −0.045 z_c^2 + 0.986 along z; the reconstruction gives −0.045 z_c^2 + 0.996.', 'p. 126'),
        (0, 'The paper reports a 30% drop at z_c = 2.7 λ_1; the reconstruction gives 32.3%.', 'p. 126')]),
    ('d', 'peak fluorescence, 2PE, θ = π/2', 'match', [
        (0, 'The bands are tilted and rippled by interference, which makes the loss less predictable.'),
        (0, 'The paper reports that the in-plane peak fluctuates between 1 and 0.7; the reconstruction gives 0.70 to 1.00.', 'p. 126'),
        (0, 'The paper reports a 30% drop at x_c ≈ 0.5 λ_1; the reconstruction gives 26%.', 'p. 126')]),
]
for t, lab, v, items in F4:
    compare(f'Fig. 4({t}): {lab}', f'orig_fig4{t}.png', P(f'fig4_peak_p{"abcd".index(t) + 1}.png'),
            v, items, 'p. 127')

linfoot_slides()
for n, t, lab, v, items in [
    ('5', 'a', '2CE, θ = π, F', 'match', [
        (0, 'Near alignment the PSF shape stays similar, and it degrades toward the corners of the map.'),
        (0, 'In both plots F peaks at 1 in the center and dips at the corners, with spikes at the edges.'),
        (0, 'The reconstruction gives F = 0.71 at x_c = 0.4 and F = −0.18 at x_c = 1.0.')]),
    ('5', 'c', '2CE, θ = π/2, F', 'match', [
        (0, 'The PSF stays similar only while |z_c| is small, and x_c hardly matters.', 'p. 128'),
        (0, 'In both plots F forms a ridge at 1 along z_c ≈ 0 across all x_c.'),
        (0, 'The paper reports F ≈ −0.8 at |z_c| = 1.33 λ_1; the reconstruction gives −0.91.', 'p. 128'),
        (0, 'In both plots F plateaus near −1 and drops jaggedly toward −2.5 at the far edge.')]),
    ('6', 'a', '2PE, θ = π, F', 'match', [
        (0, 'Interference makes the 2PE shape jump with small offsets, so the surface is noisy.', 'p. 128'),
        (0, 'In both plots F forms a rippled dome that falls to about −2.5 at the x_c edges.')]),
    ('6', 'c', '2PE, θ = π/2, F', 'no', [
        (0, 'The paper’s F is a broad dome lying mostly between −0.5 and 1.'),
        (0, 'The reconstructed F has three narrow peaks near z_c ≈ 0 and falls to −1 to −3 elsewhere.'),
        (0, 'Normalizing the misaligned PSF to the aligned peak brings ours to −0.4 to 0.1, but the paper states that each PSF is normalized to its own peak.', 'p. 126'),
        (0, 'The panel instead matches our θ = 0 surface, as the following slides show.')]),
]:
    compare(f'Fig. {n}({t}): {lab}', f'orig_fig{n}{t}.png',
            P(f'fig{n}_linfoot_p{"abcd".index(t) + 1}.png'), v, items,
            'p. 128' if n == '5' else 'p. 129', LINFOOT_TEX)

for n, t, row, lab, v, items in [
    ('5', 'b', 1, '2CE, θ = π, second column', 'match', [
        (0, 'The paper’s panel has a central maximum of 1, dips on either side of x_c = 0, and rises again at the corners.'),
        (0, 'Our C stays between 0.84 and 1.1 near the center, so it does not show these dips.'),
        (0, 'Our Q shows the same shape: 0.84 at x_c = 0.4, 0.37 at x_c = 1.0, rising again at the corners.'),
        (0, 'The paper’s minimum is about 0.2, deeper than our minimum of 0.32.')]),
    ('5', 'd', 2, '2CE, θ = π/2, second column', 'match', [
        (0, 'The paper’s panel is a ridge of 1 along z_c ≈ 0 and about 0 everywhere else.'),
        (0, 'Our C stays at 1 everywhere, because a shifted spot keeps its sharpness.'),
        (0, 'Our Q reproduces the ridge, falling to 0.04 at |z_c| = 1.33 λ_1.')]),
    ('6', 'b', 1, '2PE, θ = π, second column', 'match', [
        (0, 'The paper’s panel is a bowl whose walls fluctuate strongly and reach 1.'),
        (0, 'Our Q has the same bowl with fluctuating walls; our C rises well above 1 and does not.')]),
    ('6', 'd', 2, '2PE, θ = π/2, second column', 'no', [
        (0, 'The paper’s panel fluctuates between about 0.3 and 1 over the whole map.'),
        (0, 'Our Q has three peaks near z_c ≈ 0 and stays near 0.2 elsewhere, and our C does not match either.'),
        (0, 'The panel instead matches our θ = 0 surface, as the following slides show.')]),
]:
    compare3(f'Fig. {n}({t}): {lab}', f'orig_fig{n}{t}.png', P(f'fig{n}_C_p{row}.png'),
             P(f'fig{n}_linfoot_p{2 * row}.png'), v, items,
             'p. 128' if n == '5' else 'p. 129', LINFOOT_TEX)

theta0_slides()
conclusions_slide()
swap_slide()
s = prs.slides.add_slide(BLANK); title(s, 'F, C and Q maps, all four cases')
fit(s, os.path.join(FIG, 'diagnostic_FCQ_maps.png'), 0.3, 0.95, W - 0.6, H - 1.05)
notes(s, LINFOOT_TEX)

explain('Summary', [
    (0, 'The reconstruction reproduces 22 of the paper’s 24 figure panels.'),
    (0, 'Every number quoted in the paper’s Section 3.2 is reproduced within a few percent.'),
    (0, 'Beam 2 has to be rotated in real space; the optical-coordinate rotation written in the paper does not reproduce its results.'),
    (0, 'The paper’s quartic fit for θ = 0 holds only near x_c = 0.'),
    (0, 'The paper appears to swap the labels C and Q in its Figs. 5–6 and in the accompanying text.'),
    (0, 'Figs. 6(c) and 6(d), captioned 2PE at θ = π/2, are not reproduced at θ = π/2 but match our θ = 0 surfaces in shape, so they are most likely θ = 0.'),
], size=20)

prs.save(OUT)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')


# ══ research-meeting deck: conclusions first, then figures, then setup and theory ══
MEETING = os.path.expanduser('~/Downloads/Research/two_color/lim2002_meeting.pptx')
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]
QUOTE = RGBColor(0x33, 0x33, 0x33)



def abstract(ttl, quote, items, imgs=(), latex=None, size=16):
    """One abstract sentence, quoted, then explained; optional paper panels at the right."""
    s = prs.slides.add_slide(BLANK); title(s, ttl)
    tf = box(s, 0.5, 0.95, W - 1.0, 1.1)
    p = tf.paragraphs[0]; rich(p, '“' + quote + '”', 17, QUOTE)
    for r in p.runs:
        r.font.italic = True
    right = 5.0 if imgs else 0
    bullets(s, items, 0.5, 2.25, W - 1.0 - right, H - 2.4, size=size)
    for i, (lab, img) in enumerate(imgs):
        x0 = W - right - 0.1 + i * right / len(imgs)
        wcol = right / len(imgs) - 0.1
        label(s, x0, 2.2, wcol, lab)
        fit(s, os.path.join(ORIG, img), x0, 2.6, wcol, H - 2.8)
    if latex:
        notes(s, latex)
def compare_wide(ttl, orig, ours, v, items, cite, latex=None):
    """A whole original figure beside the whole reconstruction, bullets below."""
    s = prs.slides.add_slide(BLANK); title(s, ttl); verdict(s, v)
    colw, top, fh = 6.2, 1.3, 4.25
    label(s, 0.3, 0.9, colw, f'Original [{cite}]')
    label(s, 0.3 + colw + 0.33, 0.9, colw, 'Reconstruction')
    fit(s, os.path.join(ORIG, orig), 0.3, top, colw, fh)
    fit(s, ours, 0.3 + colw + 0.33, top, colw, fh)
    bullets(s, items, 0.5, top + fh + 0.1, W - 1.0, H - top - fh - 0.15, size=14)
    if latex:
        notes(s, latex)


# ── title and main points ─────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
rich(box(s, 0.8, 2.1, W - 1.6, 1.2).paragraphs[0],
     'Two-color excitation with misaligned foci: reconstructing Lim & Saloma (2002)', 36, NAVY, True)
rich(box(s, 0.8, 3.6, W - 1.6, 1.5).paragraphs[0],
     'M. Lim and C. Saloma, "Confocality condition in two-color excitation microscopy with two focused '
     'excitation beams," Opt. Commun. 207, 121–130 (2002)', 18, GREY)

explain('Main points', [
    (0, 'Question: how badly does two-color excitation (2CE) suffer when its two excitation foci do not coincide, compared with two-beam two-photon excitation (2PE)?'),
    (0, 'Method: move the focus of beam 2 to O′ = (x_c, z_c) at beam angles θ = 0, π/2 and π, and track the peak signal (Fig. 4) and the shape of the PSF (Figs. 5–6).'),
    (0, 'Answer: 2CE is the more tolerant; at θ = π/2 its peak stays above 89% for in-plane offsets up to 1.33 λ_1, while 2PE fluctuates through interference.'),
    (0, 'Our reconstruction reproduces every number in the paper’s Section 3.2 and 22 of its 24 figure panels.'),
    (0, 'It also shows three problems in the paper:'),
    (1, 'the labels C and Q are swapped in Figs. 5–6 and in the text;'),
    (1, 'beam 2 must be rotated in real space, not in optical coordinates as Eq. (2) is written;'),
    (1, 'Figs. 6(c)–(d), captioned θ = π/2, match θ = 0.'),
    (0, 'The paper treats spatial overlap only; overlap in time, with pulses, is our next step.'),
], size=18)
# ── conclusions: the paper's, with the figures that show them ─────────────
abstract('Conclusion: 2CE is more resilient', 'Our calculations reveal that 2CE imaging is more resilient to the ill-effects of misalignment than '
            'the two-beam 2PE.', [
    (0, '2CE loses signal smoothly and predictably, and its PSF has no fringes to be distorted.'),
    (0, '2PE loses signal at least as fast and fluctuates, because its PSF is an interference pattern.'),
    (0, 'The paper’s tolerance: at θ = π/2 the 2CE peak drops by less than 20% for in-plane offsets up to 1.5 λ_1.', 'p. 129'),
    (0, 'The reconstruction agrees with this conclusion; the problems we found concern labels and one figure caption, not the conclusion.'),
], size=18)
abstract('θ = π/2 in-plane: 2CE degrades less than 2PE', 'At θ = π/2, the F_{2c}^p degrades less rapidly than the peak 2PE fluorescence intensity (F_{2p}^p) '
            'for misalignments that are confined within the focal plane of the focusing lens L1 for λ_1.', [
    (0, 'Focal-plane misalignment means z_c = 0: beam 2’s focus slides sideways by x_c.'),
    (0, 'At θ = π/2 that slide is along beam 2’s own axis, the long direction of its focus, so the overlap barely changes.'),
    (0, 'Reconstruction: the 2CE peak falls smoothly, as −0.063 x_c^2 against the paper’s −0.06 x_c^2, and stays above 0.89 for |x_c| ≤ 1.33 λ_1.', 'p. 126'),
    (0, 'The 2PE peak drops to 0.73 at x_c = 0.5 λ, as the paper states (30% drop), then recovers to 0.94 at 1.0 λ: it fluctuates with the fringes.', 'p. 126'),
], imgs=(('Paper Fig. 4(c): 2CE', 'orig_fig4c.png'), ('Paper Fig. 4(d): 2PE', 'orig_fig4d.png')), size=15)
abstract('θ = π: 2CE and 2PE degrade alike', 'At θ = π, F_{2c}^p and F_{2p}^p degrade in a similar manner.', [
    (0, 'At θ = π the two lenses face each other, so a sideways offset x_c moves beam 2 across its narrow direction.'),
    (0, 'Both signals therefore fall quickly with x_c.'),
    (0, 'Reconstruction, peak at x_c = 0.37, 0.5 and 1.0 λ:'),
    (1, '2CE: 0.82, 0.70, 0.22. The paper states a 20% drop at 0.37 λ_1.', 'p. 126'),
    (1, '2PE: 0.84, 0.73, 0.27.'),
], imgs=(('Paper Fig. 4(a): 2CE', 'orig_fig4a.png'), ('Paper Fig. 4(b): 2PE', 'orig_fig4b.png')), size=15)
abstract('θ = π/2 axial: 2CE smooth, 2PE fluctuates', 'For misalignments along the optical axis of L1 and at θ = π/2, the F_{2c}^p degrades monotonically '
            'while the F_{2p}^p degradation is accompanied by fluctuations caused by two-beam interference.', [
    (0, 'Axial misalignment means x_c = 0: beam 2’s focus moves along z, across beam 2’s narrow direction.'),
    (0, 'Reconstruction, 2CE peak at z_c = 1.33, 1.8 and 2.7 λ_1: 0.91, 0.84, 0.68, falling at every step.'),
    (0, 'Reconstruction, 2PE: 0.85, 0.72, 0.51, with 14 rises and falls on the way as the fringes pass the peak.'),
    (0, 'The contour maps show the same thing: smooth bands for 2CE, wavy tilted contours for 2PE.'),
], imgs=(('Paper Fig. 4(c): 2CE', 'orig_fig4c.png'), ('Paper Fig. 4(d): 2PE', 'orig_fig4d.png')), size=15)
# ── conclusions: ours ─────────────────────────────────────────────────────
swap_slide()
theta0_slides()
# ── supporting figures ────────────────────────────────────────────────────
read_psf_slide()
compare_wide('Fig. 2: aligned PSFs', 'orig_fig2.png', os.path.join(FIG, 'fig2_contours.png'), 'match', [
    (0, 'Columns: 2CE (left) and 2PE (right); rows: θ = π (top) and θ = π/2 (bottom); contours at 1–80% of the peak.'),
    (0, '2CE gives one smooth spot; 2PE gives a standing wave along z at θ = π and tilted fringes at θ = π/2.'),
    (0, 'The contour extents agree in all four panels, e.g. the 2CE θ = π 1% contour reaches x ≈ ±0.6 µm and z ≈ ±4 µm in both.'),
], 'p. 124')
compare_wide('Fig. 3: PSFs with O′ = (0.4, 1.0) µm', 'orig_fig3.png', os.path.join(FIG, 'fig3_contours.png'), 'match', [
    (0, 'The 2CE spot moves toward O′ but stays clean: at θ = π its peak is at (0.23, 0.55) µm, against the paper’s midpoint (0.20, 0.50).', 'p. 126'),
    (0, 'At θ = π/2 the 2CE spot follows beam 2 along z only; its peak is at (0.01, 1.00) µm.'),
    (0, 'The 2PE fringes distort and spread, as in the paper.'),
], 'p. 125')
read_peak_slide()
compare_wide('Fig. 4: peak signal against the position of O′', 'orig_fig4.png', os.path.join(FIG, 'fig4_peak.png'), 'match', [
    (0, '2CE, θ = π/2: −0.063 x_c^2 + 0.999 against the paper’s −0.06 x_c^2 + 1.', 'p. 126'),
    (0, '2CE, θ = π: 17.6% drop at x_c = 0.37 λ_1 against the paper’s 20%; along z, −0.027 z_c^2 + 0.998 against −0.027 z_c^2 + 0.996.', 'p. 126'),
    (0, '2PE, θ = π/2: fluctuates between 0.72 and 1 with a 27% drop at 0.5 λ, against the paper’s 1 to 0.7 and 30%.', 'p. 126'),
], 'p. 127')
linfoot_slides()
compare_wide('Fig. 5: Linfoot’s criteria for 2CE', 'orig_fig5.png', os.path.join(FIG, 'fig5_linfoot.png'), 'match', [
    (0, 'First column F, second column the paper’s "C", which is our Q; rows θ = π and θ = π/2.'),
    (0, 'At θ = π/2 both show a ridge along z_c ≈ 0: the PSF survives in-plane offsets but not axial ones.'),
    (0, 'At |z_c| = 1.33 λ_1 the paper gives F ≈ −0.8 and "C" ≈ 0; we get F = −0.91, Q = 0.04 and C = 1.00.', 'p. 128'),
], 'p. 128', LINFOOT_TEX)
compare_wide('Fig. 6: Linfoot’s criteria for 2PE', 'orig_fig6.png', os.path.join(FIG, 'fig6_linfoot.png'), 'partial', [
    (0, 'Top row, θ = π: the rippled dome of F and the fluctuating bowl of Q are reproduced.'),
    (0, 'Bottom row, captioned θ = π/2: our θ = π/2 surfaces are spiky and do not match.'),
    (0, 'The same panels match our θ = 0 surfaces, as the next slides show.'),
], 'p. 129', LINFOOT_TEX)
# ── setup and assumptions ─────────────────────────────────────────────────
abstract('Abstract 1/5: the question', 'We evaluate the point spread function (PSF) of the two-color excitation (2CE) microscope when the '
            'confocality condition is not strictly satisfied by the two focused excitation beams which are '
            'separated by an angle θ ≠ 0.', [
    (0, 'The PSF is the fluorescence pattern produced by a single point in the sample; the image is the sample blurred by it.'),
    (0, 'In 2CE two beams, each focused by its own lens, must both be present for a molecule to fluoresce.'),
    (0, 'The confocality condition is that the two geometric foci, O and O′, are the same point.'),
    (0, 'θ is the angle between the two lenses’ optical axes: θ = π means facing lenses, θ = π/2 perpendicular lenses.'),
    (0, 'The paper asks what happens to the PSF when O′ is moved away from O.'),
])
abstract('Abstract 2/5: the energy condition', 'The 2CE wavelengths λ_1 and λ_2 are related to the single-photon excitation wavelength λ_e of the '
            'sample according to: 1/λ_e = 1/λ_1 + 1/λ_2.', [
    (0, 'The molecule absorbs one photon from each beam, and the two photon energies add up to the transition energy.'),
    (0, 'Photon energy is hc/λ, so energy conservation reads 1/λ_e = 1/λ_1 + 1/λ_2.'),
    (0, 'The paper uses λ_1 = 750 nm and λ_2 = 656 nm, which together reach λ_e = 350 nm (3.54 eV).'),
    (0, 'Two-photon excitation (2PE) reaches the same state with two 700 nm photons.'),
    (0, 'Each photon alone has too little energy, so a single beam cannot excite the molecule through 2CE.'),
], latex=r'\frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}')
abstract('Abstract 3/5: simultaneity', 'Spatio-temporal simultaneity for the two excitation beams is essential in 2CE (λ_1 ≠ λ_2).', [
    (0, 'The two photons must be absorbed together, through a short-lived virtual state.'),
    (0, 'So both beams must be present at the same place (spatial simultaneity) and at the same time (temporal simultaneity).'),
    (0, 'The signal is proportional to the product I_1 I_2 and vanishes wherever either beam is absent.', 'p. 123'),
    (0, 'This paper studies the spatial part only: it moves the foci apart and keeps the beams continuous.'),
    (0, 'With pulsed beams, the pulses must also arrive together; a time delay between them is the extension we take up next.'),
], latex=r'F_{2c}(P) = \kappa_{2c}\, I_1(P)\, I_2(P)')
abstract('Abstract 4/5: what is computed', 'Only aberration-free misalignment of the geometrical foci is considered and the degradation of the peak '
            '2CE fluorescence intensity (F_{2c}^p) is determined as a function of the focus separation for '
            'θ = 0, π/2 and π. The deterioration of the fluorescence PSF is also evaluated using the Linfoot’s '
            'criteria of fidelity, structural content and correlation quality.', [
    (0, 'Aberration-free: each lens forms a perfect focus; only its position is wrong. Aberrations are the subject of the 2003 paper.', 'LS03'),
    (0, 'The focus separation is d = (x_c^2 + z_c^2)^{1/2}, the distance from O to O′.'),
    (0, 'Two measures of damage are used:'),
    (1, 'F_{2c}^p, the peak signal relative to perfect alignment, which sets the brightness (Fig. 4);'),
    (1, 'Linfoot’s fidelity F, structural content C and correlation quality Q, which compare the shape of the misaligned PSF with the aligned one (Figs. 5–6).'),
], latex=LINFOOT_TEX)
abstract('Abstract 5/5: the 2PE comparison', 'We compare the 2CE PSF behavior with that of the two-photon excitation (2PE) fluorescence (λ_1 = λ_2) '
            'under the same misalignment settings.', [
    (0, 'In two-beam 2PE both beams have the same wavelength, 700 nm.'),
    (0, 'The fields then add before squaring, F_{2p} ∝ |U_1 + U_2|^4, so the two beams interfere and form fringes.', 'p. 123'),
    (0, 'In 2CE the cross term oscillates at the difference frequency and averages away, so F_{2c} ∝ I_1 I_2 has no fringes.'),
    (0, 'Moving one focus shifts 2PE fringes as well as the envelope, which is why 2PE is expected to be more sensitive.'),
], latex=r'F_{2p} = \kappa_{2p}\,|U_1 + U_2|^4, \qquad F_{2c} = \kappa_{2c}\, I_1 I_2')
setup_slides()
equations_slides()
background_slides()
explain('Summary and next steps', [
    (0, 'The reconstruction reproduces the paper’s conclusion and every number in its Section 3.2.'),
    (0, 'Three problems in the paper, each checked against its own text:'),
    (1, 'the labels C and Q are swapped in Figs. 5–6 and in the text;'),
    (1, 'beam 2 must be rotated in real space, not in optical coordinates;'),
    (1, 'Figs. 6(c)–(d) are most likely θ = 0, not θ = π/2.'),
    (0, 'The paper’s quartic fit for θ = 0 holds only near x_c = 0.'),
    (0, 'Next: the same misalignment study with the high-NA vector (Richards–Wolf) focus.'),
    (0, 'Later: pulsed beams and a time delay between them, the temporal half of spatio-temporal simultaneity.'),
], size=19)
os.makedirs(os.path.dirname(MEETING), exist_ok=True)
prs.save(MEETING)
print('Saved ->', MEETING, f'({len(prs.slides)} slides)')
