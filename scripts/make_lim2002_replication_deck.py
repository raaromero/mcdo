r"""Replication deck for Lim & Saloma (2002), in the style of
~/Downloads/lim02_2ce_presentation.pptx: 16:9 at 10 × 5.625 in, navy title
slide, three colored dots, Cambria titles with a one-line takeaway, grey cards,
framed figures, and a MAIN POINT speaker script in the notes.

Equations are text on the slides with their LaTeX in the notes, for pasting
into Keynote. Text supports x_c, λ_1, x^2, _{..} and ^{..} as real
sub/superscripts.

    python scripts/make_lim2002_replication_deck.py
    -> ~/Downloads/Research/two_color/lim2002_replication.pptx
"""

import os
import re

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.join(os.path.dirname(__file__), '..')
FIG = os.path.join(ROOT, 'output', '08_two_color', 'lim2002')
ORIG = os.path.join(FIG, 'original')
PAN = os.path.join(FIG, 'panels')
OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_replication.pptx')

NAVY, RED, ORANGE, PURPLE = (RGBColor.from_string(c) for c in ('14213D', 'B23A48', 'D9731F', '5B3FA8'))
GREY, CARD, FRAME, PALE = (RGBColor.from_string(c) for c in ('5C6370', 'F2F3F8', 'D5D8E0', 'C9CEDF'))
WHITE, GREEN = RGBColor(0xFF, 0xFF, 0xFF), RGBColor.from_string('1B7F3A')
W, H = 10.0, 5.625
CITE = 'Replication of Lim & Saloma, Opt. Commun. 207, 121–130 (2002)'
TOK = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\}|_[A-Za-z0-9]|\^[A-Za-z0-9])')

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


# ── primitives ────────────────────────────────────────────────────────────

def runs(p, text, size, color=NAVY, bold=False, font='Calibri', italic=False):
    """Add text to paragraph p, rendering _x, _{..}, ^x, ^{..} as sub/superscripts."""
    for part in TOK.split(text):
        if not part:
            continue
        base = 0
        if part[0] in '_^' and len(part) > 1:
            base = -25000 if part[0] == '_' else 30000
            part = part[2:-1] if part[1] == '{' else part[1:]
        r = p.add_run(); r.text = part
        f = r.font
        f.size, f.bold, f.italic, f.name, f.color.rgb = Pt(size), bold, italic, font, color
        if base:
            f._element.set('baseline', str(base))


def text(s, l, t, w, h, txt, size, color=NAVY, bold=False, font='Calibri',
         anchor=MSO_ANCHOR.TOP, align=None, italic=False):
    tf = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate(txt.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align:
            p.alignment = align
        runs(p, line, size, color, bold, font, italic)
    return tf


def bullets(s, l, t, w, h, items, size=12.5, color=NAVY):
    """Bulleted list as in the style deck: • with hanging indent, 8 pt after."""
    tf = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', '228600'); pPr.set('indent', '-228600')
        spc = pPr.makeelement(qn('a:spcAft'), {}); pts = spc.makeelement(qn('a:spcPts'), {'val': '700'})
        spc.append(pts); pPr.append(spc)
        pPr.append(pPr.makeelement(qn('a:buSzPct'), {'val': '100000'}))
        pPr.append(pPr.makeelement(qn('a:buChar'), {'char': '•'}))
        runs(p, it, size, color)
    return tf


def shape(s, kind, l, t, w, h, fill, line=None, line_w=1.0):
    sh = s.shapes.add_shape(kind, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line or fill; sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.08
    return sh


def dots(s, x0, y, d, gap):
    for i, c in enumerate((RED, ORANGE, PURPLE)):
        shape(s, MSO_SHAPE.OVAL, x0 + i * gap, y, d, d, c)


def chip(s, l, t, w, label, fill, fg=WHITE):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, 0.36, fill)
    text(s, l, t, w, 0.36, label, 12, fg, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)


def notes(s, main, script, latex=None):
    body = f'MAIN POINT: {main}\n\n{script}'
    if latex:
        body += '\n\nLaTeX:\n' + '\n'.join(l.strip() for l in latex.strip().splitlines())
    s.notes_slide.notes_text_frame.text = body


PAGE = [0]


def slide(title, takeaway):
    """White content slide: dots, Cambria title, purple takeaway, footer."""
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
    PAGE[0] += 1
    dots(s, 0.5, 0.42, 0.13, 0.2)
    text(s, 1.2, 0.28, 8.6, 0.45, title, 24, NAVY, True, 'Cambria', MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 0.78, 9.0, 0.5, takeaway, 13, PURPLE)
    text(s, 0.5, 5.28, 6.0, 0.22, CITE, 8.5, GREY)
    text(s, 9.0, 5.28, 0.5, 0.22, str(PAGE[0] + 1), 8.5, GREY)
    return s


def card(s, l, t, w, h, heading, hcolor, items, size=12, bulleted=True):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h, CARD)
    text(s, l + 0.2, t + 0.12, w - 0.4, 0.35, heading, 14, hcolor, True, 'Cambria')
    if bulleted:
        bullets(s, l + 0.2, t + 0.55, w - 0.4, h - 0.65, items, size)
    else:
        text(s, l + 0.2, t + 0.55, w - 0.4, h - 0.65, '\n'.join(items), size)


def figure(s, path, l, t, w, h):
    """Image inside a thin grey frame, as in the style deck; returns the frame box."""
    iw, ih = Image.open(path).size
    k = min((w - 0.1) / iw, (h - 0.1) / ih)
    fw, fh = iw * k + 0.1, ih * k + 0.1
    fl = l + (w - fw) / 2
    shape(s, MSO_SHAPE.RECTANGLE, fl, t, fw, fh, WHITE, FRAME, 0.75)
    s.shapes.add_picture(path, Inches(fl + 0.05), Inches(t + 0.05), Inches(iw * k), Inches(ih * k))
    return fl, t, fw, fh


def label(s, l, t, w, txt, color=GREY):
    text(s, l, t, w, 0.25, txt, 10, color, True, align=PP_ALIGN.CENTER)


def verdict(s, ok):
    lab, col = {'match': ('REPRODUCED', GREEN), 'partial': ('PARTLY REPRODUCED', ORANGE),
                'no': ('NOT REPRODUCED', RED)}[ok]
    text(s, 7.2, 0.3, 2.3, 0.3, lab, 10, col, True, align=PP_ALIGN.RIGHT)


def stat(s, l, t, value, vcolor, lines):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, 2.9, 1.35, CARD)
    text(s, l, t + 0.05, 1.45, 0.8, value, 34, vcolor, True, 'Cambria', MSO_ANCHOR.MIDDLE, PP_ALIGN.CENTER)
    text(s, l + 1.45, t + 0.15, 1.4, 1.1, lines, 10.5, NAVY, True)


def numbered(s, n, color, t, txt, size=13):
    shape(s, MSO_SHAPE.OVAL, 0.6, t, 0.45, 0.45, color)
    text(s, 0.6, t, 0.45, 0.45, str(n), 15, WHITE, True, 'Cambria', MSO_ANCHOR.MIDDLE, PP_ALIGN.CENTER)
    text(s, 1.3, t - 0.02, 8.2, 0.55, txt, size, NAVY, anchor=MSO_ANCHOR.MIDDLE)


def compare(title, takeaway, orig, ours, ok, items, caption, main, script, latex=None):
    """Original and reconstruction side by side, framed; points at the right."""
    s = slide(title, takeaway); verdict(s, ok)
    label(s, 0.45, 1.3, 3.2, 'Paper')
    label(s, 3.75, 1.3, 3.2, 'Reconstruction', PURPLE)
    figure(s, os.path.join(ORIG, orig), 0.45, 1.58, 3.2, 3.2)
    figure(s, ours, 3.75, 1.58, 3.2, 3.2)
    bullets(s, 7.15, 1.45, 2.4, 3.4, items, 11.5)
    text(s, 0.45, 4.85, 6.5, 0.4, caption, 9, GREY)
    notes(s, main, script, latex)
    return s


P = lambda name: os.path.join(PAN, name)
LINFOOT_TEX = r'''
F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \quad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, \quad Q = \frac{\langle |a|\,|t| \rangle}{\langle t^2 \rangle}
2Q - C = F = 1 - \epsilon
'''

# ══ 1. title ═════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
dots(s, 0.6, 0.7, 0.2, 0.27)
text(s, 0.6, 1.15, 8.8, 1.5, 'Reconstructing Lim & Saloma (2002): two-color excitation with misaligned foci',
     30, WHITE, True, 'Cambria')
text(s, 0.6, 2.85, 8.8, 0.4, 'Roland Albert A. Romero', 18, WHITE)
text(s, 0.6, 3.25, 8.8, 0.35, 'National Institute of Physics, University of the Philippines Diliman', 13, PALE)
text(s, 0.6, 3.6, 8.8, 0.35, 'Replication of Opt. Commun. 207 (2002) 121–130', 13, PALE)
chip(s, 0.6, 4.45, 1.15, '750 nm', RED)
text(s, 1.8, 4.45, 0.35, 0.36, '+', 16, WHITE, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
chip(s, 2.2, 4.45, 1.15, '656 nm', ORANGE)
text(s, 3.4, 4.45, 0.35, 0.36, '→', 16, WHITE, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
chip(s, 3.8, 4.45, 1.15, '350 nm', PURPLE)
text(s, 5.1, 4.45, 3.5, 0.36, 'rebuilt from the equations, checked number by number', 12, PALE, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'We rebuilt every figure of Lim & Saloma (2002) from its equations; the physics holds, three details of the paper do not.',
      'This talk is the replication of the paper just summarized. We rebuilt the model from the paper’s equations, '
      'regenerated all six figures, and checked every number the paper quotes. The conclusion survives; '
      'three details of the paper do not, and we show the evidence for each.')

# ══ 2. main points ═══════════════════════════════════════════════════════
s = slide('Main points', 'The paper’s conclusion reproduces; three details of the paper do not.')
numbered(s, 1, PURPLE, 1.45, 'Every number in the paper’s Section 3.2 and 22 of its 24 figure panels reproduce, within a few percent.')
numbered(s, 2, RED, 2.15, 'The labels C and Q are swapped in Figs. 5–6 and in the text: the paper’s own identity F = 2Q − C proves it.')
numbered(s, 3, ORANGE, 2.85, 'Beam 2 must be rotated in real space; the optical-coordinate rotation printed as Eq. (2) gives a 3.5× steeper loss.')
numbered(s, 4, NAVY, 3.55, 'Figs. 6(c)–(d), captioned θ = π/2, match our θ = 0 surfaces instead.')
text(s, 0.6, 4.5, 8.9, 0.4, 'Next: the same study with the high-NA vector (Richards–Wolf) focus; later, pulses and a time delay.', 12, GREY)
notes(s, 'The paper’s conclusion reproduces; three details of the paper do not.',
      'Four points. First, the reconstruction reproduces every number the paper quotes in Section 3.2 and 22 of its 24 panels. '
      'Second, the paper swaps the labels C and Q; its own identity F = 2Q − C shows the panel called C cannot be C. '
      'Third, the rotation of beam 2 has to be done in real space; the rotation printed in the paper, in optical coordinates, '
      'gives a quadratic loss 3.5 times too steep. Fourth, the bottom row of Fig. 6, captioned theta = pi/2, matches theta = 0. '
      'The next steps are the high-NA vector focus, then pulses with a time delay.',
      r'F = 2Q - C')

# ══ 3. what we built ═════════════════════════════════════════════════════
s = slide('What we built', 'The paper’s model, rebuilt from its equations and pinned down by physics tests.')
card(s, 0.5, 1.45, 2.9, 3.55, 'Model', PURPLE, [
    'Scalar paraxial Debye focus, NA 0.5, n = 1',
    'λ_1 = 750 nm, λ_2 = 656 nm; 2PE at 700 nm',
    'Beam 2 rotated by θ and moved to O′ = (x_c, z_c)',
    'PSF on the paper’s 100 × 100 grid, ±1 µm × ±5 µm'], 11.5)
card(s, 3.55, 1.45, 2.9, 3.55, 'Signals', RED, [
    '2CE: F_{2c} = κ_{2c} I_1 I_2, no fringes',
    '2PE: F_{2p} = κ_{2p} |U_1 + U_2|^4, fringes',
    'Peak F^p relative to the aligned peak (Fig. 4)',
    'Linfoot F, C, Q against the aligned PSF (Figs. 5–6)'], 11.5)
card(s, 6.6, 1.45, 2.9, 3.55, 'Checks (11 tests)', NAVY, [
    'On axis: sinc^2(u/4); focal plane: Airy',
    'θ = π mirrors, θ = π/2 swaps the axes',
    'Standing wave for 2PE, none for 2CE',
    'F = 2Q − C; the paper’s −0.06 x_c^2 and 20% at 0.37 λ_1'], 11.5)
notes(s, 'The paper’s model, rebuilt from its equations and pinned down by physics tests.',
      'The field of each beam is the scalar paraxial Debye field at NA 0.5 in air, as in the paper. Beam 2 is rotated by theta '
      'and its focus moved to O prime. The two-color signal is the product of intensities; the two-photon signal is the fourth '
      'power of the summed field, so it carries fringes. Eleven physics tests guard the code: the analytic on-axis and focal-plane '
      'profiles, the symmetries at theta = pi and pi/2, the standing wave, the Linfoot identity, and two of the paper’s numbers.',
      r'''
U(u,v) \propto e^{ikz}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\rho\, d\rho, \quad u = k\,\mathrm{NA}^2 z/n, \quad v = k\,\mathrm{NA}\, r
F_{2c} = \kappa_{2c} I_1 I_2, \qquad F_{2p} = \kappa_{2p} |U_1 + U_2|^4
''')

# ══ 4. rotation convention ═══════════════════════════════════════════════
s = slide('Rotating beam 2: real space, not (u, v)',
          'Only a real-space rotation reproduces the paper’s own θ = π/2 numbers.')
card(s, 0.5, 1.45, 4.4, 1.7, 'As printed, Eq. (2)', RED, [
    'u_r = u cos θ − v sin θ,  v_r = v cos θ + u sin θ',
    'u = k NA^2 z and v = k NA r scale differently, so this is not a rotation of space'], 11.5)
card(s, 5.1, 1.45, 4.4, 1.7, 'Real space', PURPLE, [
    'z_b = (x − x_c) sin θ + (z − z_c) cos θ',
    'x_b = (x − x_c) cos θ − (z − z_c) sin θ, then form u, v in beam 2’s frame'], 11.5)
stat(s, 0.5, 3.35, '−0.06', NAVY, 'x_c^2 coefficient\npaper, 2CE, θ = π/2')
stat(s, 3.55, 3.35, '−0.063', PURPLE, 'x_c^2 coefficient\nreal-space rotation')
stat(s, 6.6, 3.35, '−0.21', RED, 'x_c^2 coefficient\n(u, v) rotation')
notes(s, 'Only a real-space rotation reproduces the paper’s own theta = pi/2 numbers.',
      'The paper writes the rotation on the optical coordinates u and v. But u carries NA squared and v carries NA, so rotating '
      '(u, v) stretches beam 2 across its axis by 1/NA = 2 and shortens it by NA. The in-plane 2CE loss at theta = pi/2 decides: '
      'the paper reports −0.06 x_c squared; the real-space rotation gives −0.063 and the printed rotation gives −0.21. '
      'At theta = pi both forms agree, so only theta = pi/2 can tell them apart.',
      r'''
u_r = u\cos\theta - v\sin\theta, \qquad v_r = v\cos\theta + u\sin\theta
z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta
F^p_{2c}(\pi/2) = -0.06\, x_c^2 + 1
''')

# ══ 5–7. Figs. 2–4 ═══════════════════════════════════════════════════════
compare('Fig. 2: aligned PSFs', 'All four aligned PSFs reproduce, fringes and all.',
        'orig_fig2.png', os.path.join(FIG, 'fig2_contours.png'), 'match', [
            '2CE: one smooth spot; at θ = π/2 it is shortest in z',
            '2PE: standing wave at θ = π, tilted fringes at θ = π/2',
            'Extents agree: 2CE θ = π 1% contour at x ≈ ±0.6 µm, z ≈ ±4 µm in both'],
        'x ±1 µm, z ±5 µm; contours 1–80% of peak. Left 2CE, right 2PE; top θ = π, bottom θ = π/2.',
        'All four aligned PSFs reproduce, fringes and all.',
        'The aligned case. Two-color gives a single smooth spot at both angles; two-photon shows the standing wave at theta = pi '
        'and tilted fringes at theta = pi/2. The contour extents agree panel by panel.')
compare('Fig. 3: misaligned PSFs', 'With O′ at (0.4, 1.0) µm the 2CE spot moves as the paper says; 2PE fringes warp.',
        'orig_fig3.png', os.path.join(FIG, 'fig3_contours.png'), 'match', [
            '2CE, θ = π: peak at (0.23, 0.55) µm; paper: the O–O′ midpoint (0.20, 0.50)',
            '2CE, θ = π/2: peak at (0.01, 1.00) µm, shifted only in z, as stated',
            '2PE: fringes shift and distort in both'],
        'Same axes as Fig. 2 with O′ at x_c = 0.4 µm, z_c = 1 µm (0.533 λ_1, 1.33 λ_1).',
        'With O prime at (0.4, 1.0) micrometres the 2CE spot moves as the paper says; 2PE fringes warp.',
        'The paper says the theta = pi two-color peak sits at the midpoint of O and O prime, 0.2 and 0.5 micrometres; ours is at '
        '0.23 and 0.55. At theta = pi/2 it follows beam 2 along z only; ours sits at z = 1.00 with x = 0.01.')
compare('Fig. 4: peak signal against O′', 'Contours of the surviving peak reproduce at both angles, including the 2PE ripples.',
        'orig_fig4.png', os.path.join(FIG, 'fig4_peak.png'), 'match', [
            'θ = π: ellipses, steep in x_c, gentle in z_c',
            '2CE, θ = π/2: flat bands, x_c barely matters',
            '2PE, θ = π/2: wavy tilted bands from interference'],
        'Peak (% of aligned) against O′; x_c ±1.33, z_c ±6.6 in λ_1 (2PE: ±1.43, ±7.1 in λ_{2p}), the paper’s ±1 × ±5 µm.',
        'Contours of the surviving peak reproduce at both angles, including the 2PE ripples.',
        'Each point of these maps is one whole misaligned PSF reduced to its peak. The paper spans the same physical range for 2CE '
        'and 2PE, one micrometre across and five along, which is why the 2PE axes extend slightly further in its own wavelength.')

# ══ 8. the numbers ═══════════════════════════════════════════════════════
s = slide('The quoted numbers', 'Every loss the paper quotes in Section 3.2 comes back within a few percent.')
stat(s, 0.5, 1.45, '11%', PURPLE, 'paper 11%\n2CE, θ = π/2\nx_c = 1.33 λ_1')
stat(s, 3.55, 1.45, '17.6%', RED, 'paper 20%\n2CE, θ = π\nx_c = 0.37 λ_1')
stat(s, 6.6, 1.45, '27%', NAVY, 'paper 30%\n2PE, θ = π/2\nx_c = 0.5 λ')
bullets(s, 0.6, 3.05, 8.9, 2.1, [
    'In-plane, 2CE θ = π/2: −0.063 x_c^2 + 0.999 against the paper’s −0.06 x_c^2 + 1.',
    'Along z, θ = π: −0.027 z_c^2 + 0.998 against −0.027 z_c^2 + 0.996; 19.3% lost at 2.7 λ_1 against 20%.',
    '2PE, θ = π/2: fluctuates between 0.72 and 1 with a period of about λ, as the paper states.',
    'The paper’s θ = 0 quartic fit holds only near x_c = 0: 0.818 against our 0.824 at 0.37 λ_1, but it turns negative by 0.9 λ_1.'], 11.5)
notes(s, 'Every loss the paper quotes in Section 3.2 comes back within a few percent.',
      'Big numbers are ours, with the paper’s value underneath. The two-color loss at theta = pi/2 is 11 percent at 1.33 lambda_1 in both. '
      'At theta = pi, 17.6 against the paper’s 20 percent at 0.37 lambda_1. The two-photon loss at theta = pi/2 is 27 against 30 percent. '
      'The fits agree to the second decimal. One caveat: the paper’s quartic fit at theta = 0 is only good near zero offset.',
      r'''
F^p_{2c}(\pi/2) = -0.06\,x_c^2 + 1
F^p_{2c}(0) = -0.37\,x_c^4 + 0.01\,x_c^3 - 1.14\,x_c^2 + 0.98
F^p_{2c}(0) = -0.027\,z_c^2 + 0.996
''')

# ══ 9. Fig. 5 ════════════════════════════════════════════════════════════
compare('Fig. 5: Linfoot scores for 2CE', 'Our F and Q reproduce the paper’s two columns; its second column is Q, not C.',
        'orig_fig5.png', os.path.join(FIG, 'fig5_linfoot.png'), 'match', [
            'θ = π/2: a ridge along z_c ≈ 0 in both columns',
            'At |z_c| = 1.33 λ_1: paper F ≈ −0.8, "C" ≈ 0',
            'Ours: F = −0.91, Q = 0.04, but C = 1.00'],
        'F (left, −3 to 1) and the paper’s "C" = our Q (right, 0 to 1) against x_c, z_c in λ_1. Top θ = π, bottom θ = π/2.',
        'Our F and Q reproduce the paper’s two columns; its second column is Q, not C.',
        'The surfaces reproduce once the second column is read as Q. At |z_c| = 1.33 lambda_1 the paper gives F about −0.8 and C '
        'about zero; we get F = −0.91, Q = 0.04 and C = 1.00.', LINFOOT_TEX)

# ══ 10. the C/Q swap ═════════════════════════════════════════════════════
s = slide('C and Q are swapped', 'The paper’s own identity rules out its "C" ≈ 0; the panel is Q.')
figure(s, os.path.join(FIG, 'labeling_FCQ.png'), 0.45, 1.4, 5.3, 3.6)
card(s, 5.95, 1.4, 3.55, 3.6, 'The argument', RED, [
    'Paper: F = 2Q − C, and Q ≥ 0, so F ≥ −C',
    'At |z_c| = 1.33 λ_1 it reports F ≈ −0.8 with "C" ≈ 0: impossible',
    'Ours there: C = 1.00, Q = 0.04',
    'Paper: "Q rises above 1" at θ = π; ours: C does, up to 2.37'], 11)
notes(s, 'The paper’s own identity rules out its "C" is about 0; the panel is Q.',
      'The paper defines F = 2Q − C. Q cannot be negative, so F is at least −C. The paper then reports F about −0.8 together with '
      'C about zero at the same point, which breaks its own identity. Our calculation gives C = 1 there, because a shifted spot keeps '
      'its sharpness, and Q = 0.04, which is the paper’s number. The text makes the same swap when it says Q rises above 1 at theta = pi.',
      LINFOOT_TEX)

# ══ 11–13. Fig. 6 ════════════════════════════════════════════════════════
compare('Fig. 6: Linfoot scores for 2PE', 'The θ = π row reproduces; the row captioned θ = π/2 does not.',
        'orig_fig6.png', os.path.join(FIG, 'fig6_linfoot.png'), 'partial', [
            'θ = π: rippled dome of F, fluctuating bowl of Q, in both',
            'Captioned θ = π/2: the paper’s surfaces are smooth; ours are spiky',
            'Next slide: the same panels at θ = 0'],
        'Same axes as Fig. 5 for 2PE at 700 nm. Top θ = π, bottom captioned θ = π/2.',
        'The theta = pi row reproduces; the row captioned theta = pi/2 does not.',
        'The top row matches. In the bottom row the paper shows smooth surfaces, while crossed 700 nm beams give fringes that make '
        'F swing sharply as O prime moves. The next slide shows what the bottom row matches instead.', LINFOOT_TEX)

s = slide('Fig. 6(c)–(d) are θ = 0', 'The unchanged model at θ = 0 gives the paper’s smooth dome; at θ = π/2 it does not.')
verdict(s, 'partial')
for i, (lab, path, col) in enumerate((('Paper 6(c), captioned θ = π/2', os.path.join(ORIG, 'orig_fig6c.png'), GREY),
                                      ('Ours, θ = π/2', P('fig6_linfoot_p3.png'), PURPLE),
                                      ('Ours, θ = 0', P('fig6_theta0_p1.png'), PURPLE))):
    label(s, 0.45 + i * 3.1, 1.3, 2.9, lab, col)
    figure(s, path, 0.45 + i * 3.1, 1.58, 2.9, 2.75)
bullets(s, 0.6, 4.45, 8.9, 0.8, [
    'F: paper about −1.2 to 1, a dome; ours at θ = π/2 falls to −5 with spikes; ours at θ = 0 spans −0.91 to 1, a dome.',
    'Second column: ours at θ = 0 is Q from 0.38 up, clipped at 1 as in the paper; C at θ = 0 reaches 3.3, so again the panel is Q.'], 10.5)
notes(s, 'The unchanged model at theta = 0 gives the paper’s smooth dome; at theta = pi/2 it does not.',
      'Same model, same window, same normalization; only theta changes. At theta = pi/2 the crossed beams’ fringes make F spiky. '
      'At theta = 0 the beams travel together and F becomes the smooth dome of the paper. The paper evaluates theta = 0, pi/2 and pi '
      'but never shows theta = 0 on its own, so the bottom row is most likely theta = 0 mislabeled. This rests on shape and range: '
      'the paper quotes no numbers for these panels.', LINFOOT_TEX)

s = slide('What else we ruled out', 'Five changes to the model at θ = π/2; none gives the paper’s dome.')
rows = [('Normalize a to the aligned peak', 'flat plane with three spikes'),
        ('Carrier e^{ikz} on the lab axis, as Eq. (2) prints', 'ridge along z_c'),
        ('Rotate in (u, v), as Eq. (2) prints', 'many spikes'),
        ('Both of the above', 'ridge along z_c'),
        ('Nothing changed, θ = 0', 'the paper’s dome')]
for i, (what, res) in enumerate(rows):
    t = 1.45 + i * 0.66
    last = i == len(rows) - 1
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.5, t, 9.0, 0.56, CARD)
    text(s, 0.7, t, 5.2, 0.56, what, 12.5, NAVY, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 6.0, t, 3.3, 0.56, res, 12.5, GREEN if last else RED, True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'Five changes to the model at theta = pi/2; none gives the paper’s dome.',
      'Before concluding the caption is wrong we tried to make theta = pi/2 fit. Normalizing to the aligned peak, putting the carrier '
      'on the lab axis or rotating in optical coordinates as the paper prints, or both, all fail. The same model at theta = 0, with '
      'nothing changed, gives the dome. The same model also reproduces the paper’s theta = pi/2 panels in Figs. 4 and 5, so the '
      'theta = pi/2 geometry itself is right.')

# ══ 14. the abstract's three results ═════════════════════════════════════
s = slide('The abstract’s three results hold', 'Each comparison the abstract draws between 2CE and 2PE comes out the same way here.')
card(s, 0.5, 1.45, 2.9, 3.55, 'θ = π/2, in-plane', PURPLE, [
    'Paper: 2CE degrades less than 2PE',
    '2CE ≥ 0.89 over |x_c| ≤ 1.33 λ_1, smooth',
    '2PE down to 0.70, and back to 0.94 at 1.0 λ'], 11.5)
card(s, 3.55, 1.45, 2.9, 3.55, 'θ = π', RED, [
    'Paper: the two degrade alike',
    '2CE: 0.82, 0.70, 0.22',
    '2PE: 0.84, 0.73, 0.27',
    'at x_c = 0.37, 0.5, 1.0 λ'], 11.5)
card(s, 6.6, 1.45, 2.9, 3.55, 'θ = π/2, axial', ORANGE, [
    'Paper: 2CE falls monotonically, 2PE fluctuates',
    '2CE: 0.91, 0.84, 0.68, falling at every step',
    '2PE: 0.85, 0.72, 0.51, with 14 rises and falls',
    'at z_c = 1.33, 1.8, 2.7 λ'], 11.5)
notes(s, 'Each comparison the abstract draws between 2CE and 2PE comes out the same way here.',
      'At theta = pi/2 with in-plane offsets, two-color stays above 89 percent and falls smoothly, while two-photon drops to 70 and '
      'recovers: it fluctuates. At theta = pi the two fall alike. Along the axis at theta = pi/2, two-color falls at every step while '
      'two-photon rises and falls fourteen times as fringes pass the peak.')

# ══ 15. conclusions ══════════════════════════════════════════════════════
s = slide('Conclusions', 'The physics of Lim & Saloma (2002) reproduces; read Figs. 5–6 and Eq. (2) with care.')
numbered(s, 1, PURPLE, 1.45, '2CE tolerates misalignment better than two-beam 2PE, most of all at θ = π/2: confirmed.')
numbered(s, 2, RED, 2.15, 'Figs. 5–6 plot Q where they say C; the text repeats the swap.')
numbered(s, 3, ORANGE, 2.85, 'Beam 2 is rotated in real space; Eq. (2) as printed does not generate the figures.')
numbered(s, 4, NAVY, 3.55, 'Figs. 6(c)–(d) are most likely θ = 0, not θ = π/2.')
text(s, 0.6, 4.5, 8.9, 0.4, 'Next: high-NA vector focus (Richards–Wolf); then pulses and a time delay, the temporal half of simultaneity.', 12, GREY)
notes(s, 'The physics of Lim & Saloma (2002) reproduces; read Figs. 5–6 and Eq. (2) with care.',
      'The paper’s conclusion stands: two-color excitation is more tolerant of misalignment, most of all with crossed beams. Three '
      'details need care: the C and Q labels, the rotation as printed, and the caption of Fig. 6(c)–(d). Next we move to the high-NA '
      'vector focus, and after that to pulsed beams with a delay between them.')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')
