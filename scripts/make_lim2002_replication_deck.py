r"""Replication of Lim & Saloma (2002), in the style of
~/Downloads/lim02_2ce_presentation.pptx: 16:9 at 10 × 5.625 in, navy title
slide, three colored dots, Helvetica Neue titles, framed figures, and a speaker script
in the notes.

Each slide is one textbox of plain sentences (plus its figures); equations are
displayed on their own lines, with their LaTeX in the notes. Text supports x_c,
λ_1, x^2, _{..} and ^{..} as real sub/superscripts.

    python scripts/make_lim2002_replication_deck.py
    -> ~/Downloads/Research/two_color/lim2002_replication.pptx
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mcdo.deckstyle as ds
from mcdo.deckstyle import (BLANK, FIG, GREY, NAVY, ORIG, PALE, PAN, PURPLE, WHITE, bullets, dots, figure, label,
                            notes, prs, slide, text)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_replication.pptx')
ds.CITE = ''                     # cited on the title slide only

P = lambda name: os.path.join(PAN, name)
LINFOOT_TEX = r'''
F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \quad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, \quad Q = \frac{\langle t\,a \rangle}{\langle t^2 \rangle}
F = 2Q - C
'''


def panel(title, orig, ours, line, main, script, latex=None, ours_label='Ours'):
    """One panel of the paper and the same panel of ours, side by side at full height; one sentence beneath."""
    s = slide(title, '')
    label(s, 0.45, 0.95, 4.45, 'Lim & Saloma (2002)')
    label(s, 5.1, 0.95, 4.45, ours_label, PURPLE)
    figure(s, os.path.join(ORIG, orig), 0.45, 1.2, 4.45, 3.8)
    figure(s, ours, 5.1, 1.2, 4.45, 3.8)
    bullets(s, 0.6, 5.04, 8.3, 0.3, [line], 11)
    notes(s, main, script, latex)
    return s


# ══ title ════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
dots(s, 0.6, 0.7, 0.2, 0.27)
text(s, 0.6, 1.15, 8.8, 1.5, 'Part 1: Replication of Lim & Saloma (2002)', 30, WHITE, True, 'Helvetica Neue')
text(s, 0.6, 2.85, 8.8, 0.4, 'Roland Albert A. Romero', 18, WHITE)
text(s, 0.6, 3.25, 8.8, 0.35, 'National Institute of Physics, University of the Philippines Diliman', 13, PALE)
text(s, 0.6, 3.6, 8.8, 0.35, 'M. Lim & C. Saloma, Opt. Commun. 207, 121–130 (2002)', 13, PALE)
notes(s, 'The replication of Lim and Saloma (2002).',
      'We rebuilt the model from the equations in the paper, recomputed its six figures and the losses it reports, and compared '
      'them one by one.')

# ══ summary: main point, two supporting sentences ═══════════════════════
s = slide('Summary', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'Rebuilt from its equations, the model of Lim & Saloma (2002) reproduces the six figures and, within a few percent, the '
    'losses reported in the paper.',
    '– What holds: the 2CE PSF is more robust against misalignment than the 2PE PSF, most of all when the two beams cross at '
    'θ = π/2.',
    '– What differs: C and Q are swapped in Figs. 5–6, Eq. (2) has to be applied as a rotation in space, Figs. 6(c)–(d) are '
    'most likely θ = 0, and the reported losses differ from ours by up to 3 points (20% against 18%, 30% against 27%).'],
    14, bold=True)
notes(s, 'Rebuilt from its equations, the scalar 2CE model reproduces the paper.',
      'The paper asks how much fluorescence a two-color excitation microscope loses when its two foci are misaligned, against '
      'two-photon excitation. Rebuilt from its equations, the model gives the same figures and losses, and the same conclusion. '
      'Three details need correcting: the C and Q labels, the rotation as printed, and the caption of the bottom row of Fig. 6.')

# ══ model ════════════════════════════════════════════════════════════════
s = slide('Model', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'Each beam is focused by a lens of NA 0.5 in air; its field is the scalar paraxial Debye field.',
    'Beam 1 (λ_1 = 750 nm) is focused at O. Beam 2 (λ_2 = 656 nm) is focused at O′ = (x_c, z_c), and its axis makes an angle θ '
    'with the axis of beam 1. For 2PE both beams are at 700 nm.',
    'The 2CE fluorescence is the product of the two intensities; the 2PE fluorescence is the square of the total intensity, so '
    'the two beams interfere.',
    '$$ F_{2c} = κ_{2c} I_1 I_2,     F_{2p} = κ_{2p} |U_1 + U_2|^4',
    'As in the paper, the point spread function is computed over x within ±1 µm and z within ±5 µm.'], 13)
notes(s, 'The model of the paper, rebuilt from its equations.',
      'The field of each beam is the scalar paraxial Debye field at NA 0.5 in air. Beam 2 is rotated by theta and its focus moved '
      'to O prime. Two-color fluorescence is the product of the two intensities; two-photon fluorescence is the fourth power of '
      'the summed field, so it carries interference fringes.',
      r'''
U(u,v) \propto e^{ikz}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\rho\, d\rho, \quad u = k\,\mathrm{NA}^2 z/n, \quad v = k\,\mathrm{NA}\, r
F_{2c} = \kappa_{2c} I_1 I_2, \qquad F_{2p} = \kappa_{2p} |U_1 + U_2|^4
''')

# ══ rotation ═════════════════════════════════════════════════════════════
s = slide('Rotation of beam 2', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'Eq. (2) of the paper rotates beam 2 in the optical coordinates u and v:',
    '$$ u_r = u cos θ − v sin θ,     v_r = v cos θ + u sin θ',
    'u and v scale differently with NA, so this rotation also stretches beam 2. Rotating beam 2 in space instead:',
    '$$ z_b = (x − x_c) sin θ + (z − z_c) cos θ,     x_b = (x − x_c) cos θ − (z − z_c) sin θ',
    'The rotation in space reproduces the numbers of the paper: for 2CE at θ = π/2 the peak falls as −0.063 x_c^2, against '
    '−0.06 x_c^2 in the paper; the rotation as printed gives −0.21 x_c^2.',
    'The two rotations agree at θ = π; they differ at θ = π/2.'], 13)
notes(s, 'A rotation in real space reproduces the theta = pi/2 numbers of the paper.',
      'The paper writes the rotation on the optical coordinates u and v. But u carries NA squared and v carries NA, so rotating '
      '(u, v) stretches beam 2. The in-plane 2CE loss at theta = pi/2 decides: the paper reports −0.06 x_c squared; the rotation in '
      'space gives −0.063 and the rotation as printed gives −0.21.',
      r'''
u_r = u\cos\theta - v\sin\theta, \qquad v_r = v\cos\theta + u\sin\theta
z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta
F^p_{2c}(\pi/2) = -0.06\, x_c^2 + 1
''')

# ══ Figs. 2–4, one panel per slide ══════════════════════════════════════
FIG24 = {(2, 'a'): ('2CE, θ = π', 'The aligned 2CE PSF is a single smooth spot, elongated along z, as in the paper.'), (2, 'b'): ('2PE, θ = π', 'The aligned 2PE PSF is a standing wave along z, with fringes λ_{2p}/2 apart, as in the paper.'), (2, 'c'): ('2CE, θ = π/2', 'With crossed beams the aligned 2CE spot is short along z and long along x, as in the paper.'), (2, 'd'): ('2PE, θ = π/2', 'With crossed beams the aligned 2PE PSF has tilted fringes, as in the paper.'), (3, 'a'): ('2CE, θ = π', 'With O′ at (0.4, 1.0) µm the 2CE peak moves to (0.23, 0.55) µm, close to the midpoint of O and O′ that the paper states.'), (3, 'b'): ('2PE, θ = π', 'With O′ at (0.4, 1.0) µm the 2PE fringes shift and distort, as in the paper.'), (3, 'c'): ('2CE, θ = π/2', 'With crossed beams the misaligned 2CE peak moves along z with beam 2, as the paper states.'), (3, 'd'): ('2PE, θ = π/2', 'With crossed beams the misaligned 2PE fringes shift and break up, as in the paper.'), (4, 'a'): ('2CE, θ = π', 'With facing lenses the 2CE peak falls fastest when O′ moves across the axis, as in the paper.'), (4, 'b'): ('2PE, θ = π', 'The 2PE peak map at θ = π agrees with the paper; the standing-wave fringes add weak ripples along z.'), (4, 'c'): ('2CE, θ = π/2', 'With crossed beams the 2CE peak barely depends on x_c, as in the paper.'), (4, 'd'): ('2PE, θ = π/2', 'With crossed beams the 2PE peak varies in tilted bands from interference, as in the paper.')}
WHAT = {2: ('aligned PSF', 'contours'), 3: ('misaligned PSF, O′ at (0.4, 1.0) µm', 'contours'), 4: ('peak against O′', 'peak')}
for (n, t), (lab, line) in FIG24.items():
    what, key = WHAT[n]
    panel(f'Fig. {n}({t}): {lab}', f'orig_fig{n}{t}.png', P(f'fig{n}_{key}_p{"abcd".index(t) + 1}.png'), line,
          f'Fig. {n}({t}), {what}, {lab}: agrees with the paper.',
          f'Fig. {n}({t}) of the paper, {what}, {lab}, next to the same panel computed from the equations of the paper.')

# ══ peak lost: the values in the text ════════════════════════════════════
s = slide('Peak lost: values in Section 3.2', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'At θ = π/2, a misalignment of x_c = 1.33 λ_1 reduces the 2CE peak by 11%, as the paper reports.',
    'At θ = π, a misalignment of x_c = 0.37 λ_1 reduces the 2CE peak by 18%; the paper reports 20%.',
    'For 2PE at θ = π/2, a misalignment of x_c = 0.5 λ_{2p} reduces the peak by 27%; the paper reports 30%.',
    'Along the axis at θ = π, a misalignment of z_c = 2.7 λ_1 reduces the 2CE peak by 19%; the paper reports 20%.'], 13)
notes(s, 'Each peak loss reported in Section 3.2 comes back within a few percent.',
      'The two-color loss at theta = pi/2 is 11 percent at 1.33 lambda_1 in both. At theta = pi, 18 against the paper’s 20 '
      'percent at 0.37 lambda_1. The two-photon loss at theta = pi/2 is 27 against 30 percent. Along the axis, 19 against 20.',
      r'''
F^p_{2c}(\pi/2) = -0.06\,x_c^2 + 1
F^p_{2c}(0) = -0.027\,z_c^2 + 0.996
''')

# ══ Linfoot's criteria ═══════════════════════════════════════════════════
s = slide('Linfoot’s criteria', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'Lim & Saloma compare the misaligned PSF a with the aligned PSF t, each scaled to its own peak; ⟨·⟩ is the mean over the '
    'window.',
    'Fidelity F compares the two shapes; it is 1 when they are equal and falls as they differ:',
    '$$ F = 1 − ⟨(t − a)^2⟩ / ⟨t^2⟩',
    'Structural content C compares their energy, and correlation quality Q their overlap; both are 1 when a = t:',
    '$$ C = ⟨a^2⟩ / ⟨t^2⟩,     Q = ⟨t a⟩ / ⟨t^2⟩',
    'The three are related by',
    '$$ F = 2Q − C',
    'Figs. 5–6 map F and the second criterion over the misalignment (x_c, z_c) of O′.'], 13)
notes(s, 'Linfoot’s three criteria compare the misaligned PSF with the aligned one.',
      'F is one minus the normalized mean squared difference, C the ratio of energies, Q the normalized overlap. The relation '
      'F = 2Q − C is used two slides later to show that the panels labelled C are Q.', LINFOOT_TEX)

# ══ Fig. 5 and the C/Q labels, one panel per slide ═════════════════════
for t, (lab, ours, line) in {
        'a': ('Linfoot’s criteria, 2CE, θ = π: F', 'Ours: F', 'Fidelity F for 2CE at θ = π agrees with the paper.'),
        'b': ('Linfoot’s criteria, 2CE, θ = π, labelled C', 'Ours: Q', 'The panel the paper labels C matches our correlation quality Q.'),
        'c': ('Linfoot’s criteria, 2CE, θ = π/2: F', 'Ours: F', 'Fidelity F for 2CE at θ = π/2 agrees with the paper.'),
        'd': ('Linfoot’s criteria, 2CE, θ = π/2, labelled C', 'Ours: Q', 'At θ = π/2 the panel labelled C also matches our Q.')}.items():
    panel(f'Fig. 5({t}): {lab}', f'orig_fig5{t}.png', P(f'fig5_linfoot_p{"abcd".index(t) + 1}.png'), line,
          f'Fig. 5({t}): {line}', 'Linfoot criteria of the misaligned 2CE PSF over (x_c, z_c), paper against ours.', LINFOOT_TEX,
          ours_label=ours)

s = slide('C and Q are swapped', '')
figure(s, os.path.join(FIG, 'labeling_FCQ.png'), 0.45, 1.0, 6.4, 4.2)
bullets(s, 7.05, 1.1, 2.45, 4.1, [
    'The paper defines F = 2Q − C. Q cannot be negative, so F cannot be lower than −C.',
    'At |z_c| = 1.33 λ_1 it reports F ≈ −0.8 with C ≈ 0, which breaks that rule.',
    'Our calculation gives C = 1.00 and Q = 0.04 there: the panel labelled C is Q.'], 11.5)
notes(s, 'The paper’s own identity rules out its C near zero; the panel is Q.',
      'The paper defines F = 2Q − C. Q cannot be negative, so F is at least −C. The paper reports F about −0.8 together with C '
      'about zero at the same point. Our calculation gives C = 1 there, because a shifted spot keeps its sharpness, and Q = 0.04, '
      'the paper’s number.', LINFOOT_TEX)

# ══ Fig. 6, one panel per slide; its bottom row against θ = π/2 and θ = 0 ═
for t, lab, ours, path, line in (
        ('a', 'Linfoot’s criteria, 2PE, θ = π: F', 'Ours: F', 'fig6_linfoot_p1.png', 'Fidelity F for 2PE at θ = π agrees with the paper.'),
        ('b', 'Linfoot’s criteria, 2PE, θ = π, labelled C', 'Ours: Q', 'fig6_linfoot_p2.png',
         'The panel the paper labels C matches our correlation quality Q.'),
        ('c', 'Linfoot’s criteria, captioned θ = π/2', 'Ours: F, θ = π/2', 'fig6_linfoot_p3.png',
         'Our F at θ = π/2 changes sharply with O′, from the fringes of the crossed beams; the surface in the paper is smooth.'),
        ('c', 'Linfoot’s criteria, against θ = 0', 'Ours: F, θ = 0', 'fig6_theta0_p1.png',
         'At θ = 0 the same model gives the smooth surface of the paper: the bottom row of Fig. 6 is most likely θ = 0.'),
        ('d', 'Linfoot’s criteria, against θ = 0', 'Ours: Q, θ = 0', 'fig6_theta0_p2.png',
         'The panel labelled C in Fig. 6(d) matches our Q at θ = 0.')):
    panel(f'Fig. 6({t}): {lab}', f'orig_fig6{t}.png', P(path), line, f'Fig. 6({t}): {line}',
          'Same model, window and normalization as the other panels; only theta changes between the theta = pi/2 and theta = 0 '
          'comparisons.', LINFOOT_TEX, ours_label=ours)

# ══ the abstract ═════════════════════════════════════════════════════════
s = slide('Results in the abstract', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'The abstract compares how much 2CE and 2PE fluorescence remains when the second focus is moved away from the first.',
    'Beams crossed at θ = π/2, focus moved in the focal plane: the 2CE peak stays above 89% and decreases smoothly, while the 2PE '
    'peak drops to 70% and partly recovers as its fringes pass through the focus.',
    'Beams facing each other at θ = π: the 2CE and 2PE peaks decrease at about the same rate.',
    'Beams crossed, focus moved along the axis: the 2CE peak decreases steadily, while the 2PE peak rises and falls as the '
    'fringes pass.',
    'All three comparisons agree with the paper.'], 13)
notes(s, 'Each comparison the abstract draws between 2CE and 2PE comes out the same way here.',
      'At theta = pi/2 with in-plane offsets, two-color stays above 89 percent and falls smoothly, while two-photon drops to 70 and '
      'recovers. At theta = pi the two fall alike. Along the axis at theta = pi/2, two-color falls steadily while two-photon rises '
      'and falls as fringes pass the peak.')

# ══ conclusions ══════════════════════════════════════════════════════════
s = slide('Conclusions', '')
bullets(s, 0.6, 1.1, 8.9, 4.1, [
    'The 2CE point spread function is more robust against misalignment than the 2PE one, most of all with the beams crossed at '
    'θ = π/2, as Lim & Saloma conclude.',
    'In Figs. 5–6 and in the text, the panels labelled C show Q.',
    'Beam 2 has to be rotated in space; Eq. (2) as printed does not produce the figures.',
    'Figs. 6(c)–(d) are most likely θ = 0, not θ = π/2.'], 13)
notes(s, 'The conclusion of the paper holds; read Figs. 5–6 and Eq. (2) with care.',
      'Two-color excitation is more robust against misalignment, most of all with crossed beams. Three details need care: the C '
      'and Q labels, the rotation as printed, and the caption of Fig. 6(c)–(d).')

if not os.environ.get('DECK_APPEND'):                 # set by make_lim2002_progress_deck.py, which saves the whole report
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs.save(OUT)
    print('Saved ->', OUT, f'({len(prs.slides)} slides)')
