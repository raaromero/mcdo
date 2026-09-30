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
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mcdo.deckstyle as ds
from mcdo.deckstyle import (BLANK, CARD, FIG, GREEN, GREY, H, NAVY, ORANGE, ORIG, PALE, PAN, PURPLE, RED, W,
                            WHITE, MSO_ANCHOR, MSO_SHAPE, PP_ALIGN, bullets, card, chip, compare, dots, figure,
                            label, notes, numbered, prs, shape, slide, stat, text, verdict)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_replication.pptx')
ds.CITE = 'Replication of Lim & Saloma, Opt. Commun. 207, 121–130 (2002)'

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

# ══ 15–17. high NA, first look ══════════════════════════════════════════
COLS = ('NA 0.5\npaper', 'NA 0.5\nRW', 'NA 0.7\nRW', 'NA 0.9\nRW, water')


def num_table(s, l, t, w, title, rows, highlight=(2, 3)):
    """A small grey card holding a numbers table: first column labels, then one column per model."""
    nc = len(rows[0]) - 1
    lw = 1.05; cw = (w - 0.4 - lw) / nc
    h = 0.62 + 0.3 + 0.32 * len(rows)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h, CARD)
    text(s, l + 0.2, t + 0.1, w - 0.4, 0.45, title, 11.5, PURPLE, True, 'Cambria')
    heads = COLS if nc == 4 else (COLS[0], COLS[2], COLS[3])
    for j, hd in enumerate(heads):
        text(s, l + 0.2 + lw + j * cw, t + 0.55, cw, 0.35, hd, 8.5, GREY, True, align=PP_ALIGN.CENTER)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            hi = j - 1 in highlight
            text(s, l + 0.2 + (0 if j == 0 else lw + (j - 1) * cw), t + 0.95 + i * 0.32,
                 lw if j == 0 else cw, 0.3, v, 10.5, RED if hi else NAVY, hi,
                 align=None if j == 0 else PP_ALIGN.CENTER)
    return t + h


s = slide('First look at high NA', 'The paper’s scalar model holds at NA 0.5; at higher NA the 2CE tolerances shrink with the spot.')
figure(s, os.path.join(FIG, 'highna_tolerance.png'), 0.45, 1.35, 4.9, 3.55)
b = num_table(s, 5.5, 1.35, 4.0, 'Offset that costs 20% of the peak (µm)', [
    ('θ = π/2, x_c', '> 1.0', '> 1.0', '0.62', '0.50'),
    ('θ = π/2, z_c', '1.54', '1.44', '0.68', '0.55'),
    ('θ = π, x_c', '0.30', '0.30', '0.22', '0.17'),
    ('θ = π, z_c', '2.06', '1.93', '0.91', '0.73')])
bullets(s, 5.55, b + 0.12, 3.95, 5.2 - b - 0.12, [
    'NA 0.5: the vector focus agrees with the paper within 7%.',
    'θ = π in-plane shrinks as λ/NA; the rest as about nλ/NA^2.',
    'Unpolarized beams; NA 0.9 needs water (n = 1.33) to cross at θ = π/2.'], 10)
text(s, 0.45, 4.98, 4.9, 0.22, 'Peak 2CE signal against x_c (z_c = 0) and z_c (x_c = 0); dotted line: 20% lost.', 8.5, GREY)
notes(s, 'The paper’s scalar model holds at NA 0.5; at higher NA the 2CE tolerances shrink with the spot.',
      'A first high-NA check with our Richards–Wolf vector focus. Both beams are unpolarized: each intensity is the average over two '
      'orthogonal input polarizations, which is what the scalar model implicitly describes. At NA 0.5 the vector curves sit on the '
      'paper’s scalar ones, within 7 percent, so the paper’s model is adequate at its own NA. At NA 0.7 in air, close to the largest '
      'NA at which two cones can cross at right angles, and at NA 0.9 in water, every tolerance shrinks. The in-plane tolerance at '
      'theta = pi is set by the spot width and shrinks as lambda over NA: 0.30, 0.22, 0.17 micrometres. The others are set by a spot '
      'length and shrink as n lambda over NA squared, for example 1.93, 0.91, 0.73 micrometres along z at theta = pi.',
      r"""
r_{\mathrm{width}} \propto \frac{\lambda}{\mathrm{NA}}, \qquad z_{\mathrm{length}} \propto \frac{n\lambda}{\mathrm{NA}^2}
\mathrm{NA} \le \frac{n}{\sqrt{2}} \ \text{for two cones crossing at } \theta = \pi/2
""")

WIDTHS = [('θ = π, x', '520', '385', '300'), ('θ = π, z', '3570', '1570', '1280'),
          ('θ = π/2, x', '765', '560', '435'), ('θ = π/2, z', '680', '500', '390')]
PEAKS = [('θ = π', '(0.23, 0.55)', '(0.23, 0.58)', '(0.23, 0.58)'),
         ('θ = π/2', '(0.01, 1.00)', '(0.03, 0.95)', '(0.03, 0.95)')]
HEADS3 = ('Paper, NA 0.5', 'RW, NA 0.7', 'RW, NA 0.9, water')


def na_grid(s, panels):
    """Rows θ = π and π/2; columns: paper at NA 0.5, ours at NA 0.7 and 0.9."""
    for c, hd in enumerate(HEADS3):
        label(s, 0.75 + c * 1.9, 1.3, 1.8, hd, GREY if c == 0 else PURPLE)
    for r, rl in enumerate(('θ = π', 'θ = π/2')):
        text(s, 0.2, 1.58 + r * 1.78 + 0.7, 0.55, 0.3, rl, 10, NAVY, True)
        for c in range(3):
            figure(s, panels[r][c], 0.75 + c * 1.9, 1.58 + r * 1.78, 1.8, 1.72)


def small_table(s, l, t, w, title, heads, rows):
    lw = 0.8; cw = (w - 0.4 - lw) / len(heads)
    h = 0.95 + 0.32 * len(rows)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h, CARD)
    text(s, l + 0.2, t + 0.1, w - 0.4, 0.45, title, 11, PURPLE, True, 'Cambria')
    for j, hd in enumerate(heads):
        text(s, l + 0.2 + lw + j * cw, t + 0.6, cw, 0.3, hd, 9, GREY, True, align=PP_ALIGN.CENTER)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            text(s, l + 0.2 + (0 if j == 0 else lw + (j - 1) * cw), t + 0.92 + i * 0.32,
                 lw if j == 0 else cw, 0.3, v, 9.5 if j else 10, NAVY, j == 0,
                 align=None if j == 0 else PP_ALIGN.CENTER)
    return t + h


hp = lambda na, k: P(f'highna_psf_{na}_p{k}.png')
s = slide('2CE aligned PSFs: NA 0.5, 0.7, 0.9', 'Higher NA shrinks the 2CE spot; crossed beams (θ = π/2) still give the shortest spot along z.')
na_grid(s, [[os.path.join(ORIG, 'orig_fig2a.png'), hp('na0p7', 1), hp('na0p9_water', 1)],
            [os.path.join(ORIG, 'orig_fig2c.png'), hp('na0p7', 3), hp('na0p9_water', 3)]])
b = small_table(s, 6.55, 1.35, 2.95, 'Central spot FWHM (nm)', ('0.5', '0.7', '0.9'), WIDTHS)
bullets(s, 6.6, b + 0.12, 2.9, 5.2 - b - 0.12, [
    'Width shrinks as λ/NA, length as nλ/NA^2.',
    'NA 0.5 values are our reconstruction of the paper’s panels.'], 9.5)
text(s, 0.2, 5.1, 6.2, 0.2, 'Same axes (±1 × ±5 µm) and contours (1–80%) in every panel; RW = Richards–Wolf, unpolarized.', 8, GREY)
notes(s, 'Higher NA shrinks the 2CE spot; crossed beams still give the shortest spot along z.',
      'Left column: the paper’s own panels at NA 0.5. Middle and right: our Richards–Wolf vector focus at NA 0.7 in air and NA 0.9 '
      'in water, unpolarized, on the same axes and contour levels. The spot shrinks in every direction: across the axis as lambda over '
      'NA, 520, 385, 300 nanometres at theta = pi; along it as n lambda over NA squared, 3.6, 1.6, 1.3 micrometres. The comparison the '
      'paper draws between the angles does not change: at every NA, crossing the beams at pi/2 gives a spot three to five times shorter '
      'along z than facing them at pi.')

s = slide('2CE misaligned PSFs: NA 0.5, 0.7, 0.9', 'With O′ = (0.4, 1.0) µm the 2CE peak lands in the same place at every NA.')
na_grid(s, [[os.path.join(ORIG, 'orig_fig3a.png'), hp('na0p7', 2), hp('na0p9_water', 2)],
            [os.path.join(ORIG, 'orig_fig3c.png'), hp('na0p7', 4), hp('na0p9_water', 4)]])
b = small_table(s, 6.55, 1.35, 2.95, 'Peak position (µm)', ('0.5', '0.7', '0.9'), PEAKS)
bullets(s, 6.6, b + 0.12, 2.9, 5.2 - b - 0.12, [
    'θ = π: the peak sits between O and O′, as the paper states.',
    'θ = π/2: the peak follows beam 2 along z only.',
    'The spot around it shrinks with NA, as on the previous slide.'], 9.5)
text(s, 0.2, 5.1, 6.2, 0.2, 'Paper panels: its Fig. 3(a), 3(c). Ours: Richards–Wolf, unpolarized; NA 0.9 in water.', 8, GREY)
notes(s, 'With O prime at (0.4, 1.0) micrometres the 2CE peak lands in the same place at every NA.',
      'The misaligned case of the paper’s Fig. 3 at the three NAs. At theta = pi the peak sits between the two foci, at (0.23, 0.58) '
      'micrometres for NA 0.7 and 0.9, against (0.23, 0.55) at NA 0.5 and the paper’s midpoint (0.20, 0.50). At theta = pi/2 the peak '
      'follows beam 2 along z only, at z about 1. Where the peak goes is set by the geometry of the offset, not by NA; only the size of '
      'the spot around it changes.')

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

if not os.environ.get('DECK_APPEND'):                 # set by make_lim2002_progress_deck.py, which saves the whole report
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs.save(OUT)
    print('Saved ->', OUT, f'({len(prs.slides)} slides)')
