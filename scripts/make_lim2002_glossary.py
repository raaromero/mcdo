r"""Main glossary for the 2CE progress report: every variable and term, symbols typeset in LaTeX.

    python scripts/make_lim2002_glossary.py
    -> ~/Downloads/Research/two_color/2ce_glossary.pptx (and pdfs/2ce_glossary.pdf)
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mcdo.deckstyle as ds
from mcdo.deckstyle import CARD, MSO_ANCHOR, MSO_SHAPE, NAVY, eq_image, notes, prs, shape, slide, text
from pptx.util import Inches

ds.CITE = ''
DIR = os.path.expanduser('~/Downloads/Research/two_color')
OUT = os.path.join(DIR, '2ce_glossary.pptx')

GROUPS = [
    ('Glossary: geometry', [
        (r'L_1,\ L_2', 'the two lenses, focusing beam 1 and beam 2'),
        (r'O,\ O^{\prime}', 'geometric foci of L1 and L2; O is the origin'),
        (r'x_c,\ z_c', 'misalignment of O′ across and along the axis of L1'),
        (r'd = \left(x_c^2 + z_c^2\right)^{1/2}', 'distance between the two foci'),
        (r'\theta', 'angle between the two lens axes: π facing (4Pi), π/2 crossed (theta microscopy)'),
        (r'x,\ z', 'position across and along the axis of L1, in the plane of the two lens axes'),
        (r'r', 'distance from a beam’s own axis'),
        (r'x_b,\ z_b', 'coordinates of beam 2, rotated by θ about O′'),
        (r'\mathrm{NA} = n \sin\alpha', 'numerical aperture; α is the half-angle of the focusing cone'),
        (r'n', 'refractive index of the medium: 1 for air, 1.33 for water'),
        (r'\mathrm{NA} \le n \sin(\theta/2)', 'condition for two lenses at angle θ to fit side by side: 0.71 in air at θ = π/2'),
    ]),
    ('Glossary: wavelengths and optics', [
        (r'\lambda_1,\ \lambda_2', '2CE excitation wavelengths, 750 nm and 656 nm'),
        (r'\lambda_{2p}', '2PE excitation wavelength, 700 nm for both beams'),
        (r'\dfrac{1}{\lambda_e} = \dfrac{1}{\lambda_1} + \dfrac{1}{\lambda_2}', 'one-photon wavelength of the same transition, 350 nm'),
        (r'k = \dfrac{2\pi n}{\lambda}', 'wavenumber in the medium'),
        (r'u = \dfrac{k\,\mathrm{NA}^2 z}{n},\quad v = k\,\mathrm{NA}\, r', 'axial and transverse optical coordinates'),
        (r'a,\ f', 'aperture radius and focal length of a lens (a/f = NA in the paper)'),
        (r'\rho', 'radius in the pupil over its edge, 0 to 1'),
        (r'\beta', 'angle of a ray to the lens axis, 0 to α'),
        (r'\phi', 'angle about the beam axis (azimuth)'),
        (r'\omega,\ \omega_0', 'angular frequency; carrier frequency of a pulse'),
    ]),
    ('Glossary: fields and signals', [
        (r'U', 'scalar focal field (paraxial scalar Debye field)'),
        (r'\mathbf{E}', 'vector focal field (Richards–Wolf)'),
        (r'I = |U|^2 \ \text{or}\ |\mathbf{E}|^2', 'intensity'),
        (r'I_0,\ I_1,\ I_2', 'Richards–Wolf integrals; g_m are their angular weights'),
        (r'F_{2c} = \kappa_{2c}\, I_1 I_2', 'two-color excitation (2CE) fluorescence: product of the two intensities'),
        (r'F_{2p} = \kappa_{2p}\, |U_1 + U_2|^4', 'two-photon excitation (2PE) fluorescence: fields add and interfere'),
        (r'\kappa_{2c},\ \kappa_{2p}', '2CE and 2PE cross sections; they cancel on normalization'),
        (r'\mathrm{PSF}', 'point spread function: fluorescence from one point, scaled to its peak'),
        (r'F^{p}', 'peak fluorescence relative to the aligned peak'),
        (r'\text{peak lost} = 1 - F^{p}', 'in percent of the aligned peak'),
        (r'\text{20\% tolerance}', 'the misalignment x_c or z_c that reduces the 2CE peak by 20%'),
    ]),
    ('Glossary: models and input', [
        (r'\text{scalar 2CE}', 'the paraxial scalar model of the paper: small-angle phase, no polarization'),
        (r'\text{scalar Debye}', 'scalar focus with the exact phase kz cos β, no polarization'),
        (r'\text{vector 2CE}', 'the same signals with the Richards–Wolf focus: exact phase and polarization'),
        (r'A(\beta) = \exp\!\left(-\alpha_t \dfrac{\sin^2\beta}{\sin^2\alpha}\right)', 'pupil amplitude of the Gaussian input'),
        (r'\alpha_t', 'truncation parameter of the Gaussian input; 0 is uniform input'),
        (r'\psi', 'input polarization angle about a beam’s own axis'),
        (r'I_{\mathrm{unpol}} = \tfrac{1}{2}\left(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2\right)',
         'unpolarized: equal to circular polarization; round spot'),
        (r'\text{s--s},\ \text{p--p}', 'both beams polarized perpendicular to (s) or in (p) the plane of the two lens axes'),
    ]),
    ('Glossary: Linfoot’s criteria', [
        (r't,\ a', 'aligned and misaligned PSF, each scaled to its own peak'),
        (r'\langle\cdot\rangle', 'mean over the 100 × 100 x–z window'),
        (r'F = 1 - \dfrac{\langle (t-a)^2\rangle}{\langle t^2\rangle}', 'fidelity: overall similarity of the two PSFs'),
        (r'C = \dfrac{\langle a^2\rangle}{\langle t^2\rangle}', 'structural content: relative energy; above 1 for a broader PSF'),
        (r'Q = \dfrac{\langle t\,a\rangle}{\langle t^2\rangle}', 'correlation quality: overlap of the two PSFs'),
        (r'2Q - C = F = 1 - \varepsilon', 'identity; ε is the normalized mean-squared error'),
        (r'\Delta F = F_{\mathrm{vector}} - F_{\mathrm{scalar}}', 'difference at the same NA (likewise ΔC, ΔQ)'),
        (r'\tilde{x} = \dfrac{x_c\,\mathrm{NA}}{\lambda},\quad \tilde{z} = \dfrac{z_c\,\mathrm{NA}^2}{n\lambda}', 'misalignment in units of the spot'),
    ]),
    ('Glossary: time delay and pulses', [
        (r'\Delta t', 'time delay of beam 2 after beam 1'),
        (r'\phi = \omega\,\Delta t', 'phase a time delay adds to a continuous beam'),
        (r'T = \lambda / c', 'optical period: 2.33 fs at 700 nm'),
        (r'\mathbf{K} = k\left(\hat{\mathbf{k}}_1 - \hat{\mathbf{k}}_2\right)', 'fringe wavevector; k̂ are the beam directions, |K| = 2k sin(θ/2)'),
        (r'\Delta s = \dfrac{c\,\Delta t}{2n\sin(\theta/2)}', 'shift of the 2PE fringes for a time delay Δt'),
        (r'\phi_{eq} = \mathbf{K}\cdot\mathbf{r}_c + k\,\hat{\mathbf{k}}_2\cdot\mathbf{d}', 'fringe phase of a misalignment d; r_c is the centre of the overlap'),
        (r'\tau', 'pulse duration (intensity FWHM)'),
        (r'F_{2c} \propto \int I_1(t)\, I_2(t - \Delta t)\, dt', '2CE signal with pulses: overlap in time of the two pulses'),
    ]),
]

for title, rows in GROUPS:
    s = slide(title, '')
    t = 1.05
    h_row = min(0.39, 4.15 / len(rows))
    for i, (tex, meaning) in enumerate(rows):
        if i % 2 == 0:
            shape(s, MSO_SHAPE.RECTANGLE, 0.45, t, 9.1, h_row, CARD)
        path, iw, ih = eq_image(tex, 13)
        k = min(1.0, 3.3 / iw, (h_row - 0.04) / ih)
        s.shapes.add_picture(path, Inches(0.6), Inches(t + (h_row - ih * k) / 2), Inches(iw * k), Inches(ih * k))
        text(s, 4.05, t, 5.4, h_row, meaning, 11.5, NAVY, anchor=MSO_ANCHOR.MIDDLE)
        t += h_row
    notes(s, title + '.', ' '.join(m for _, m in rows), '\n'.join(x for x, _ in rows))

ds.keynote_fonts()
os.makedirs(os.path.join(DIR, 'pdfs'), exist_ok=True)
prs.save(OUT)
subprocess.run(['open', '-a', 'Microsoft PowerPoint', OUT])
time.sleep(8)
subprocess.run(['osascript', '-e', f'''tell application "Microsoft PowerPoint"
save active presentation
save active presentation in POSIX file "{os.path.join(DIR, 'pdfs', '2ce_glossary.pdf')}" as save as PDF
close active presentation saving no
end tell'''], capture_output=True)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')
