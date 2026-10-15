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
from mcdo.deckstyle import (CARD, MSO_SHAPE, ORANGE, PP_ALIGN, RED, card, chip, equation, shape, where, BLANK, FIG, GREY, NAVY, ORIG, PALE, PAN, PURPLE, WHITE, bullets, dots, figure, label,
                            notes, prs, slide, text)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_replication.pptx')
ds.CITE = ''                     # cited on the title slide only

P = lambda name: os.path.join(PAN, name)
LINFOOT_TEX = r'''
F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \quad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, \quad Q = \frac{\langle t\,a \rangle}{\langle t^2 \rangle}
F = 2Q - C
'''


def panel(title, orig, ours, line, main, script, latex=None, ours_label='Current work'):
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

BGD = os.path.join(os.path.dirname(FIG))                     # output/08_two_color: background figures


def eqslide(title, takeaway, eqs, main, script, latex, side=None, size=18):
    """Equation slide in the style deck's format: numbered equations, each with its 'where' line; an optional card."""
    s = slide(title, takeaway)
    w = 9.0 if side is None else 5.9
    t = 1.35
    for tex, wh in eqs:
        h = equation(s, 0.55, t, w, tex, size)
        t += h + 0.08
        if wh:
            t += where(s, 0.6, t, w - 0.6, wh)
        t += 0.12
    if side:
        head, lines = side
        card(s, 6.75, 1.35, 2.75, 3.75, head, RED, lines, 10.5, bulleted=False)
    notes(s, main, script, latex)
    return s


# ══ background: two colors, two photons ══════════════════════════════════
s = slide('Two-color and two-photon excitation', 'In 2CE, one photon at λ_1 and one at λ_2 jointly excite a transition at λ_e; '
          'excitation requires spatial and temporal overlap of both beams.')
h = equation(s, 0.55, 1.45, 5.3, r'\frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}', 22)
where(s, 0.6, 1.55 + h, 5.2, 'λ_e = one-photon excitation wavelength of the sample; λ_1, λ_2 = the two excitation wavelengths.')
bullets(s, 0.6, 2.75, 5.2, 2.3, [
    'Excitation requires spatial and temporal overlap of both beams.',
    'The 2CE PSF is less broadened by scattering than the one-photon or two-photon PSF [Cambaliza & Saloma 2000].'], 12)
for k, (head, col, chips, txt) in enumerate((
        ('2CE (λ_1 ≠ λ_2)', RED, (('750 nm', RED), ('656 nm', ORANGE)),
         'No interference: total intensity I = I_1 + I_2. Neither beam alone excites fluorescence.'),
        ('2PE (λ_1 = λ_2)', RED, (('700 nm', RED), ('700 nm', RED)),
         'Interference: I = |U_1 + U_2|^2 contains fringe terms. One beam alone excites fluorescence.'))):
    t = 1.35 + k * 1.9
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 6.1, t, 3.4, 1.75, CARD)
    text(s, 6.3, t + 0.1, 3.0, 0.3, head, 12.5, col, True, 'Helvetica Neue')
    chip(s, 6.3, t + 0.5, 0.95, chips[0][0], chips[0][1]); text(s, 7.27, t + 0.5, 0.25, 0.36, '+', 13, NAVY, True)
    chip(s, 7.5, t + 0.5, 0.95, chips[1][0], chips[1][1]); text(s, 8.47, t + 0.5, 0.25, 0.36, '→', 13, NAVY, True)
    chip(s, 8.7, t + 0.5, 0.72, '350 nm', PURPLE)
    text(s, 6.3, t + 1.0, 3.05, 0.7, txt, 10.5, NAVY)
notes(s, 'In 2CE one photon of each color excites the transition; in 2PE two photons of one color do.',
      '750 and 656 nanometre photons together reach the same transition as one 350 nanometre photon or two 700 nanometre '
      'photons. Two colors do not interfere; one color does.', r'\frac{1}{\lambda_e} = \frac{1}{\lambda_1} + \frac{1}{\lambda_2}')

s = slide('One photon against two photons', 'Two-photon excitation is confined to the focus; one-photon excitation is not.')
figure(s, os.path.join(BGD, 'bg_nonlinear.png'), 0.45, 1.3, 5.4, 3.85)
h = equation(s, 6.05, 1.45, 3.45, r'R_1 \propto I, \qquad R_2 \propto I^2', 18)
bullets(s, 6.1, 1.65 + h, 3.4, 3.2, [
    'One-photon absorption grows as I; each plane through the beam carries the same power, so it excites along the whole cone.',
    'Two-photon absorption grows as I^2; the signal per plane falls away from the focus, which confines excitation.',
    'Computed for NA 0.5 at 700 nm.'], 11.5)
notes(s, 'Two-photon excitation is confined to the focus.', 'The per-plane integral of I is constant; that of I squared peaks at '
      'the focus.', r'R_1 \propto I, \qquad R_2 \propto I^2')

s = slide('Two-color excitation', 'The photon energies add up to the transition, so fluorescence needs both beams.')
figure(s, os.path.join(BGD, 'bg_energy_levels.png'), 0.45, 1.3, 5.6, 3.85)
h = equation(s, 6.2, 1.45, 3.3, r'\hbar\omega_1 + \hbar\omega_2 = \hbar\omega_e', 18)
h += equation(s, 6.2, 1.6 + h, 3.3, r'F_{2c}(P) = \kappa_{2c}\, I_1(P)\, I_2(P)', 18)
bullets(s, 6.25, 1.85 + h, 3.25, 2.8, [
    '750 nm and 656 nm photons reach the same 3.54 eV state as one 350 nm photon or two 700 nm photons.',
    'The rate is proportional to I_1 I_2, so fluorescence comes only from where the two foci overlap.'], 11.5)
notes(s, 'Fluorescence needs a photon from each beam.', 'The two photon energies add to the transition energy.',
      r'\hbar\omega_1 + \hbar\omega_2 = \hbar\omega_e \qquad F_{2c}(P) = \kappa_{2c} I_1(P) I_2(P)')

s = slide('Interference: one color and two colors', 'Two colors beat at their difference frequency and average out.')
figure(s, os.path.join(BGD, 'bg_beating.png'), 0.45, 1.25, 9.1, 3.05)
h = equation(s, 0.55, 4.38, 9.0, r'|\mathbf{E}|^2 = |\mathbf{E}_1|^2 + |\mathbf{E}_2|^2 + 2\,\mathrm{Re}\left[\mathbf{E}_1\cdot'
             r'\mathbf{E}_2^{*}\, e^{-i(\omega_1-\omega_2)t}\right]', 17)
bullets(s, 0.6, 4.45 + h, 8.9, 0.4, [
    'One color: the cross term is steady, so the beams form fringes. Two colors: it oscillates every 17.5 fs and averages to '
    'I_1 + I_2.'], 11)
notes(s, 'One color interferes; two colors average out.', 'So 2PE with two beams follows |U1 + U2|^4 and has fringes, while '
      '2CE follows I1 I2 and has none.',
      r'|\mathbf{E}|^2 = |\mathbf{E}_1|^2 + |\mathbf{E}_2|^2 + 2\,\mathrm{Re}[\mathbf{E}_1\cdot\mathbf{E}_2^* e^{-i(\omega_1-\omega_2)t}]')

# ══ the problem ══════════════════════════════════════════════════════════
s = slide('Breakdown of the confocality condition', 'Refractive-index mismatch and finite working distance displace the two '
          'foci; the paper quantifies the PSF degradation for aberration-free focal displacement.')
card(s, 0.5, 1.4, 4.4, 3.7, 'Causes of focal misalignment', RED, [
    'Image formed by point-by-point scanning of the common focus',
    'Refractive-index mismatch between sample and surrounding medium',
    'Finite working distance of the focusing objectives',
    'Index mismatch also introduces spherical aberration (deferred to future work)'], 11.5)
card(s, 5.1, 1.4, 4.4, 3.7, 'Scope of the study', PURPLE, [
    'Aberration-free displacement d of focus O′ from O',
    'Beam angles: θ = 0, π/2, π',
    'Measures: peak fluorescence and Linfoot’s criteria F, C, Q',
    'Same analysis for two-beam 2PE'], 11.5)
notes(s, 'Why the two foci separate, and what the paper measures.',
      'In a real sample the index mismatch and the working distance move the two foci apart. The paper treats the '
      'displacement alone, without aberration, and measures the peak and Linfoot’s criteria.')

s = slide('Two lenses at an angle', 'Lenses facing each other (θ = π) or crossed (θ = π/2) shorten the region where both '
          'beams overlap.')
for i, (k, lab) in enumerate(((1, 'θ = 0'), (2, 'θ = π/2'), (3, 'θ = π'))):
    figure(s, os.path.join(BGD, 'panels', f'setup_p{k}.png'), 0.45 + i * 3.07, 1.3, 2.95, 3.0)
h = equation(s, 0.55, 4.4, 4.5, r'\alpha \leq 45^\circ \;\Leftrightarrow\; \mathrm{NA} \leq n/\sqrt{2}', 17)
bullets(s, 5.1, 4.38, 4.4, 0.8, [
    'θ = π is the 4Pi arrangement; θ = π/2 is the idea of theta microscopy.',
    'Crossed lenses fit only while α ≤ 45°, NA 0.71 in air.'], 10.5)
notes(s, 'Two lenses at an angle.', 'Both arrangements need the two foci to coincide: the confocality condition.',
      r'\alpha \le 45^\circ \Leftrightarrow \mathrm{NA} \le n/\sqrt{2}')

# ══ geometry and model, in the paper's equations ═════════════════════════
s = slide('Geometry of misalignment', 'Beam 1 is focused at O; beam 2 is focused at O′, displaced by d, with its optical axis '
          'at angle θ to the z axis.')
figure(s, os.path.join(FIG, 'fig1_geometry.png'), 0.4, 1.3, 4.45, 3.9)
h = equation(s, 5.0, 1.5, 4.5, r'd = \left(x_c^2 + z_c^2\right)^{1/2}', 22)
where(s, 5.05, 1.6 + h, 4.4, 'd = focus separation in units of λ_1; x_c, z_c = offsets of O′ across and along the L1 axis. '
      'Confocal only if d = 0.')
for i, (lab, sub) in enumerate((('θ = 0', 'co-propagating'), ('θ = π', 'counter-propagating (4Pi)'),
                                ('θ = π/2', 'orthogonal (theta microscopy)'))):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 5.0 + i * 1.5, 2.95, 1.4, 1.1, CARD)
    text(s, 5.0 + i * 1.5, 3.02, 1.4, 0.4, lab, 15, PURPLE, True, align=PP_ALIGN.CENTER)
    text(s, 5.05 + i * 1.5, 3.45, 1.3, 0.55, sub, 9.5, GREY, align=PP_ALIGN.CENTER)
text(s, 5.0, 4.3, 4.5, 0.4, 'All fields computed in the x–z plane containing both axes (w_c = 0).', 10.5, GREY)
notes(s, 'O prime is displaced from O by d, with beam 2 at angle theta.', 'The geometry of Fig. 1 of the paper.',
      r'd = \left(x_c^2 + z_c^2\right)^{1/2}')

eqslide('Focal-field model', 'Each focal field is the scalar Debye field of an aberration-free lens (Born and Wolf); the field '
        'of L2 is obtained by rotating the optical coordinates by θ.', [
    (r'U(P;\theta) = -\frac{\pi i a^2 A}{\lambda f}\, e^{i(f/a)^2 u}\left[C(u_r,v_r) - iS(u_r,v_r)\right]',
     'U(P; θ) = field at P; a, f = aperture radius, focal length; A = pupil amplitude; C, S = real and imaginary parts of the '
     'pupil integral (Lommel functions).'),
    (r'v = \frac{2\pi a}{f\lambda}\, x, \qquad w = \frac{2\pi a}{f\lambda}\, y, \qquad u = \frac{2\pi a^2}{f^2\lambda}\, z',
     'v, w = transverse and u = axial optical coordinates; the axial scale carries an extra a/f.'),
    (r'u_r = u\cos\theta - v\sin\theta, \qquad v_r = v\cos\theta + u\sin\theta',
     'u_r, v_r = coordinates rotated by θ to build the tilted beam 2 (Eq. (2) of the paper).')],
    'The paraxial scalar Debye field, and its rotation for beam 2.',
    'The model of the paper, written as in the paper.',
    r"""U(P;\theta) = -\frac{\pi i a^2 A}{\lambda f} e^{i(f/a)^2 u}\left[C(u_r,v_r) - iS(u_r,v_r)\right]
v = \frac{2\pi a}{f\lambda} x, \quad w = \frac{2\pi a}{f\lambda} y, \quad u = \frac{2\pi a^2}{f^2\lambda} z
u_r = u\cos\theta - v\sin\theta, \quad v_r = v\cos\theta + u\sin\theta""",
    side=('Spot aspect ratio', ['At NA 0.5 and 750 nm: lateral first zero ≈ 0.9 µm, axial ≈ 6 µm (paraxial estimate, not from '
                                'the paper).', '', 'Sensitivity to displacement therefore depends on its direction relative to '
                                'each optical axis.', '', 'Scalar model, stated valid for NA ≤ 0.5.']), size=17)

eqslide('Rotation of beam 2', 'The rotation in space reproduces the numbers of the paper; Eq. (2) as printed does not.', [
    (r'z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta',
     'x_b, z_b = coordinates of beam 2 rotated in space; u and v of Eq. (2) scale differently with NA, so rotating them '
     'stretches beam 2.'),
    (r'F^p_{2c}(\pi/2):\quad -0.063\, x_c^2 + 1 \ \ \mathrm{(space)}, \qquad -0.21\, x_c^2 + 1 \ \ \mathrm{(Eq.\ 2\ as\ printed)}',
     'the paper reports −0.06 x_c^2 + 1; the two rotations agree at θ = π and differ at θ = π/2.')],
    'Only a rotation in real space reproduces the theta = pi/2 numbers of the paper.',
    'The paper writes the rotation on the optical coordinates u and v. But u carries NA squared and v carries NA, so rotating '
    '(u, v) stretches beam 2. The in-plane 2CE loss at theta = pi/2 decides.',
    r"""z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta
F^p_{2c}(\pi/2) = -0.06\, x_c^2 + 1""", size=16)

s = slide('2CE and 2PE fluorescence intensities', 'The 2CE intensity is the product of two incoherent intensities; the 2PE '
          'intensity is the fourth power of the coherent field sum and contains interference terms.')
for k, (head, tex, txt) in enumerate((
        ('2CE: product of intensities', r'F_{2c}(P;\theta;x_c,z_c) = \kappa_{2c}\, I_2(P;\theta;x_c,z_c)\, I_1(P)',
         'Zero wherever either beam is absent. No interference terms.'),
        ('2PE: fourth power of summed field', r'F_{2p}(P;\theta;x_c,z_c) = \kappa_{2p}\left|U_2(P;\theta;x_c,z_c) + U_1(P)\right|^4',
         'Fields are summed before the modulus is taken: cross terms produce interference fringes. One beam alone excites '
         'fluorescence.'))):
    l = 0.5 + k * 4.6
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, 1.45, 4.4, 2.6, CARD)
    text(s, l + 0.2, 1.55, 4.0, 0.35, head, 13, RED if k == 0 else NAVY, True)
    equation(s, l + 0.15, 2.05, 4.1, tex, 14)
    text(s, l + 0.2, 2.85, 4.0, 1.1, txt, 10.5, NAVY)
where(s, 0.6, 4.25, 8.9, 'I_1 = |U_1|^2, aligned beam 1 (focus O); I_2 = |U_2|^2, tilted and shifted beam 2 (focus O′); '
      'κ_{2c}, κ_{2p} = cross sections, which cancel on normalization. The PSF is the normalized F.')
notes(s, '2CE multiplies intensities; 2PE takes the fourth power of the summed field.', 'Eqs. (3)–(4) of the paper.',
      r"""F_{2c}(P;\theta;x_c,z_c) = \kappa_{2c} I_2(P;\theta;x_c,z_c) I_1(P)
F_{2p}(P;\theta;x_c,z_c) = \kappa_{2p} |U_2(P;\theta;x_c,z_c) + U_1(P)|^4""")

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
_t = 1.15
for tex in (r'F^p_{2c}(\pi/2) = -0.06\,x_c^2 + 1 \qquad\qquad F^p_{2c}(0) = -0.37\,x_c^4 + 0.01\,x_c^3 - 1.14\,x_c^2 + 0.98',
            r'F^p_{2c}(0) = -0.027\,z_c^2 + 0.996 \qquad\qquad F^p_{2c}(\pi/2) = -0.045\,z_c^2 + 0.986'):
    _t += equation(s, 0.55, _t, 9.0, tex, 15) + 0.12
where(s, 0.6, _t, 8.9, 'F^p_{2c}(θ) = 2CE peak normalized to aligned; x_c, z_c in units of λ_1 = 750 nm. Top: shifts in the L1 '
      'focal plane; bottom: along the L1 axis. Fits from the paper.')
bullets(s, 0.6, _t + 0.5, 8.9, 2.4, [
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
s = slide('Linfoot’s criteria', 'Fidelity, structural content and correlation quality compare the misaligned PSF with the '
          'aligned PSF over the full x–z field.')
h = equation(s, 0.55, 1.4, 9.0, r'F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \qquad C = \frac{\langle a^2 \rangle}'
             r'{\langle t^2 \rangle}, \qquad Q = \frac{\langle |a|\,|t| \rangle}{\langle t^2 \rangle}', 19)
h2 = equation(s, 0.55, 1.55 + h, 9.0, r'2Q - C = F = 1 - \varepsilon', 19)
where(s, 0.6, 1.7 + h + h2, 8.9, 't = aligned reference PSF; a = misaligned PSF; ⟨ ⟩ = average over the 100 × 100 x–z window '
      'centred at O; ε = normalized mean-squared error.')
for i, (head, col, txt) in enumerate((
        ('F  fidelity', PURPLE, 'Overall similarity, 1 − NMSE. Negative when the NMSE exceeds 1.'),
        ('C  structural content', RED, 'Relative mean-squared value (sharpness). > 1 for broader peaks, < 1 for narrower peaks.'),
        ('Q  correlation quality', NAVY, 'Alignment of peaks and troughs. Deviates from 1 for displaced, missing or spurious '
                                         'peaks.'))):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.5 + i * 3.05, 3.35, 2.9, 1.75, CARD)
    text(s, 0.7 + i * 3.05, 3.45, 2.6, 0.3, head, 12.5, col, True)
    text(s, 0.7 + i * 3.05, 3.85, 2.55, 1.2, txt, 10.5, NAVY)
notes(s, 'Linfoot’s three criteria compare the misaligned PSF with the aligned one.', 'Eq. (5) of the paper.', LINFOOT_TEX)

# ══ Fig. 5 and the C/Q labels, one panel per slide ═════════════════════
for t, (lab, ours, line) in {
        'a': ('Linfoot’s criteria, 2CE, θ = π: F', 'Current work: F', 'Fidelity F for 2CE at θ = π agrees with the paper.'),
        'b': ('Linfoot’s criteria, 2CE, θ = π, labelled C', 'Current work: Q', 'The panel the paper labels C matches our correlation quality Q.'),
        'c': ('Linfoot’s criteria, 2CE, θ = π/2: F', 'Current work: F', 'Fidelity F for 2CE at θ = π/2 agrees with the paper.'),
        'd': ('Linfoot’s criteria, 2CE, θ = π/2, labelled C', 'Current work: Q', 'At θ = π/2 the panel labelled C also matches our Q.')}.items():
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
        ('a', 'Linfoot’s criteria, 2PE, θ = π: F', 'Current work: F', 'fig6_linfoot_p1.png', 'Fidelity F for 2PE at θ = π agrees with the paper.'),
        ('b', 'Linfoot’s criteria, 2PE, θ = π, labelled C', 'Current work: Q', 'fig6_linfoot_p2.png',
         'The panel the paper labels C matches our correlation quality Q.'),
        ('c', 'Linfoot’s criteria, captioned θ = π/2', 'Current work: F, θ = π/2', 'fig6_linfoot_p3.png',
         'Our F at θ = π/2 changes sharply with O′, from the fringes of the crossed beams; the surface in the paper is smooth.'),
        ('c', 'Linfoot’s criteria, against θ = 0', 'Current work: F, θ = 0', 'fig6_theta0_p1.png',
         'At θ = 0 the same model gives the smooth surface of the paper: the bottom row of Fig. 6 is most likely θ = 0.'),
        ('d', 'Linfoot’s criteria, against θ = 0', 'Current work: Q, θ = 0', 'fig6_theta0_p2.png',
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
