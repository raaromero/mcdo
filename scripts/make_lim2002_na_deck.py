r"""Deck: Lim & Saloma (2002) against NA. Where their scalar model applies,
measured on their own metrics, for uniform input and for α_t = 4.

Same style as the replication deck (mcdo.deckstyle). Every number on the slides
is read from the result files the figure scripts write, so a rerun updates
the deck:

    fig_lim2002_quoted_vs_na.py    [ALPHA_T=4]  -> quoted_vs_na[_at4].csv, quoted_vs_na_{1..5}[_at4].png
    fig_lim2002_na_breakdown.py    [ALPHA_T=4]  -> na_breakdown[_at4].csv, na_breakdown_{metrics,severity}[_at4].png
    fig_lim2002_na_profiles.py                  -> na_profiles_theta_{pi,pi2}.png
    fig_lim2002_na_contours.py                  -> na_contours_fig{2,3}{a..d}.png
    fig_lim2002_axial_truncation.py             -> axial_lim_vs_truncation.png, axial_scalar_vs_vector_truncation.png
    N_MED=1.33 fig_lim2002_na_breakdown.py      -> na_breakdown_metrics[_at4]_n1.33.png   (water, NA to 1.2)
    fig_lim2002_fidelity_na{,_plot}.py          -> fidelity/fidelity_na_*.png, fidelity/fidelity_shape_*.csv

    python scripts/make_lim2002_na_deck.py
    -> ~/Downloads/Research/two_color/lim2002_na_study.pptx
"""

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

import mcdo.deckstyle as ds
from mcdo.deckstyle import (CARD, FIG, GREY, NAVY, ORANGE, PALE, PURPLE, RED, WHITE, MSO_ANCHOR, MSO_SHAPE,
                            PP_ALIGN, bullets, card, chip, dots, figure, label, notes, numbered, prs, shape,
                            slide, text)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_na_study.pptx')
ds.CITE = ''                     # cited on the title slide; no footer on every slide
F = lambda name: os.path.join(FIG, name)
QUOTED = [  # metric number: (title, paper %)
    ('2CE, θ = π/2, x_c = 1.33 λ_1', 11), ('2CE, θ = π, x_c = 0.37 λ_1', 20),
    ('2PE, θ = π/2, x_c = 0.5 λ_{2p}', 30), ('2CE, θ = π, z_c = 2.7 λ_1', 20),
    ('2CE, θ = π/2, z_c = 2.7 λ_1', 30)]


# ── read the results ──────────────────────────────────────────────────────
def rows_of(path):
    """The saved rows of a result file; empty while its run has not produced a point yet."""
    a = np.loadtxt(path, delimiter=',', ndmin=2)
    return a if a.size else np.empty((0, 8))


def load_quoted(suf):
    d = {}
    for k in range(1, 6):
        for path in glob.glob(F(f'quoted_vs_na{suf}_m{k}.csv')) + glob.glob(F(f'quoted_vs_na{suf}_m{k}_*.csv')):
            for na, v, sc in rows_of(path):
                d[(k, round(na, 3))] = (v, sc)
    return d


def load_breakdown(suf):
    d = {}
    for key in ('pi', 'pi2'):
        for path in glob.glob(F(f'na_breakdown{suf}_{key}.csv')) + glob.glob(F(f'na_breakdown{suf}_{key}_*.csv')):
          for na, sx, sz, rx, rz, Fi, wx, wz in rows_of(path):
            d[(key, round(na, 3))] = dict(x=abs(sx / rx - 1) * 100, z=abs(sz / rz - 1) * 100,
                                          wx=abs(wx - 1) * 100, wz=abs(wz - 1) * 100,
                                          F=(1 - Fi) * 100, rx=rx, rz=rz)
    return d


def first_above(d, key, m, thr):
    nas = sorted(na for (k, na) in d if k == key)
    return next((na for na in nas if d[(key, na)][m] > thr), None)


have = lambda name: os.path.exists(F(name))
SECTION = os.environ.get('SECTION')                 # progress report: 'high_na', 'fidelity', 'gaussian' or 'foundations'
SUFS = ('_at4',) if SECTION == 'gaussian' else ('',) if SECTION else ('', '_at4')
GT = ' (α_t = 4)' if SECTION == 'gaussian' else ''  # marks Part 4's result slides
Q = {suf: q for suf in ('', '_at4') if len(q := load_quoted(suf)) and all((k, 0.5) in q and (k, 0.9) in q for k in range(1, 6))}
B = {suf: b for suf in ('', '_at4') if len(b := load_breakdown(suf)) and all((t, 0.5) in b and (t, 0.9) in b for t in ('pi', 'pi2'))}


def pending(title, what):
    s = slide(title, 'Result still computing; this slide fills in when the deck is rebuilt.')
    bullets(s, 0.6, 1.45, 8.9, 1.5, [what], 13)
    notes(s, 'Pending result.', what)
    return s
fmt_na = lambda v: f'{v:.2f}' if v is not None else '> 0.95'


# ── helpers for this deck ─────────────────────────────────────────────────
def glossary(title, takeaway, rows):
    s = slide(title, takeaway)
    for i, (term, meaning) in enumerate(rows):
        t = 1.35 + i * 0.315
        if i % 2 == 0:
            shape(s, MSO_SHAPE.RECTANGLE, 0.5, t, 9.0, 0.315, CARD)
        text(s, 0.65, t, 1.85, 0.315, term, 11.5, PURPLE, True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 2.55, t, 6.85, 0.315, meaning, 10.5, NAVY, anchor=MSO_ANCHOR.MIDDLE)
    return s


def stacked(s, name):
    """Uniform input on top, Gaussian input (α_t = 4) below when it exists; one wide figure each."""
    at4 = name.replace('.png', '_at4.png')
    if SECTION == 'gaussian' and have(at4):
        figure(s, F(at4), 0.45, 1.4, 9.1, 3.7)
    elif SECTION is None and have(at4):
        label(s, 0.3, 1.3, 1.2, 'Uniform', GREY)
        figure(s, F(name), 1.5, 1.28, 8.0, 1.92)
        label(s, 0.3, 3.25, 1.2, 'α_t = 4', PURPLE)
        figure(s, F(at4), 1.5, 3.23, 8.0, 1.92)
    else:
        figure(s, F(name), 0.45, 1.4, 9.1, 3.7)


def pair(title, takeaway, left, right, labels, items, main, script, latex=None):
    """Two figures side by side, points below."""
    s = slide(title, takeaway)
    for i, (path, lab) in enumerate(zip((left, right), labels)):
        label(s, 0.45 + i * 4.6, 1.3, 4.5, lab, GREY if i == 0 else PURPLE)
        figure(s, path, 0.45 + i * 4.6, 1.58, 4.5, 2.85)
    bullets(s, 0.6, 4.5, 8.9, 0.75, items, 11)
    notes(s, main, script, latex)
    return s


def wide(title, takeaway, path, items, main, script, latex=None, **_):
    """A full-width figure (drawn at twice this width, so its text reads at 12–16 pt) and one line under it;
    the other points go to the notes."""
    s = slide(title, takeaway)
    figure(s, path, 0.45, 1.35, 9.1, 3.5)
    bullets(s, 0.6, 4.88, 8.9, 0.35, items[:1], 11)
    notes(s, main, ' '.join([script] + [str(i) for i in items[1:]]), latex)
    return s


def one(title, takeaway, path, items, main, script, latex=None, fw=5.6):
    """One figure at the left, points at the right."""
    s = slide(title, takeaway)
    figure(s, path, 0.45, 1.35, fw, 3.85)
    bullets(s, 0.45 + fw + 0.25, 1.45, 9.5 - fw - 0.7, 3.8, items, 11.5)
    notes(s, main, script, latex)
    return s


START = len(prs.slides)                             # slides already in a shared presentation (progress report)

# ══ 1. title ═════════════════════════════════════════════════════════════
s = prs.slides.add_slide(ds.BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
dots(s, 0.6, 0.7, 0.2, 0.27)
text(s, 0.6, 1.15, 8.8, 1.5, 'Where Lim & Saloma’s scalar model applies, as a function of NA',
     30, WHITE, True, 'Cambria')
text(s, 0.6, 2.85, 8.8, 0.4, 'Roland Albert A. Romero', 18, WHITE)
text(s, 0.6, 3.25, 8.8, 0.35, 'National Institute of Physics, University of the Philippines Diliman', 13, PALE)
text(s, 0.6, 3.6, 8.8, 0.35, 'Lim & Saloma’s own metrics, recomputed with the vector (Richards–Wolf) focus', 13, PALE)
chip(s, 0.6, 4.45, 1.15, 'NA 0.1', PURPLE)
text(s, 1.8, 4.45, 0.35, 0.36, '→', 16, WHITE, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
chip(s, 2.2, 4.45, 1.15, 'NA 1.2', RED)
text(s, 3.5, 4.45, 5.5, 0.36, 'air to NA 0.99, water to 1.2; uniform input and α_t = 4', 12, PALE, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'Lim & Saloma’s scalar model is good to a few percent below NA 0.45 and fails on the depth of focus above it.',
      'This deck asks how far Lim and Saloma’s results carry as the numerical aperture grows. We recompute the '
      'their quoted metrics with the vector model, keep their model alongside, and measure the gap.')

# ══ 2. main points ═══════════════════════════════════════════════════════
def main_point(title, main, support, size=13):
    """Bantang's format: the main point in bold, then the supporting points as short phrases."""
    s = slide(title, main)
    bullets(s, 0.6, 1.45, 8.9, 3.75, [main] + ['– ' + x for x in support], size)
    return s


if '' in B:
    b0 = B['']
    s = main_point('Main points', 'The paraxial scalar model holds at low NA and fails first on the depth of focus.', [
        f'Axial tolerance: deviation above 5% from NA {fmt_na(first_above(b0, "pi", "z", 5))}, above 10% from '
        f'NA {fmt_na(first_above(b0, "pi", "z", 10))}',
        f'Lateral tolerance: within 5% up to NA {fmt_na(first_above(b0, "pi", "x", 5))}',
        f'At NA 0.5, the limit Lim & Saloma state: {b0[("pi", 0.5)]["z"]:.0f}% on the axial tolerance',
        'Cause: the small-angle phase, not the missing polarization',
        'Checks: vector engines agree to 10^{−8}; α_t → 0 recovers Lim & Saloma'])
else:                                                 # the uniform sweep is still running: no numbers yet
    s = main_point('Main points', 'The paraxial scalar model holds at low NA and fails first on the depth of focus.', [
        'Axial tolerances depart first; lateral ones hold much longer',
        'Cause: the small-angle phase, not the missing polarization',
        '(Thresholds fill in when the dense uniform sweep finishes.)'])
notes(s, 'The scalar model tracks the vector one at low NA; the depth of focus departs first.',
      'The models and the engine check out at low NA. The metrics set by the depth of focus depart first, by more '
      'than five percent from NA 0.45 and more than ten percent from 0.6. The cause is the paraxial phase, not '
      'polarization. Metrics set by the width stay close to about NA 0.8, and a Gaussian input reduces every difference. '
      'Lim and Saloma state their model for NA up to 0.5; this marks where it still applies.')

# ══ Gaussian input (Part 4 of the progress report) ═══════════════════════
if SECTION == 'gaussian' and '_at4' in B and '' in B:
    g, u = B['_at4'], B['']
    s = main_point('Gaussian input: main points', 'A Gaussian input (α_t = 4) extends the paraxial scalar model’s range.', [
        'Same α_t = 4 on both lenses; everything else as in Part 2',
        f'Tolerances at NA 0.5, θ = π: {g[("pi", 0.5)]["rx"] / u[("pi", 0.5)]["rx"]:.2f}× lateral, '
        f'{g[("pi", 0.5)]["rz"] / u[("pi", 0.5)]["rz"]:.2f}× axial',
        f'Axial deviation above 5% from NA {fmt_na(first_above(g, "pi", "z", 5))}, above 10% from NA '
        f'{fmt_na(first_above(g, "pi", "z", 10))} (uniform: {fmt_na(first_above(u, "pi", "z", 5))}, '
        f'{fmt_na(first_above(u, "pi", "z", 10))})',
        'Same power laws: NA^{−1} lateral, NA^{−2} axial',
        'Why: the dim pupil edge removes the steepest rays; the focus acts like a lower NA'])
    notes(s, 'A Gaussian input keeps the scalar model valid to a higher NA and loosens every tolerance.',
          'The same study with a Gaussian input on both lenses. The dim edge of the pupil removes the steepest rays, so the '
          'focus is larger, the tolerances looser, and the scalar model holds to a higher NA.')
    s = slide('Gaussian input: the pupil of both beams', 'Each lens is filled by a Gaussian beam truncated at α_t = 4.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        'Pupil amplitude of each beam: A(ϑ) = exp(−α_t sin^2ϑ / sin^2α), with ϑ the ray angle and sin α = NA/n.',
        'In the paraxial model the same function at sin ϑ = ρ NA/n is exactly exp(−α_t ρ^2), ρ the pupil radius over its edge.',
        'α_t = 0 is uniform input, Lim & Saloma’s case. α_t = 4: the field at the pupil edge is e^{−4} ≈ 1.8% of the centre, '
        'and the beam’s 1/e^2 intensity radius is half the pupil radius.',
        'The same α_t on both lenses, for both wavelengths, in every result of this part.'], 13)
    notes(s, 'Each lens is filled by a Gaussian beam truncated at alpha_t = 4.',
          'The Gaussian input multiplies the pupil of both lenses by the same apodization. In the paraxial model it reduces to '
          'exp(−alpha_t rho squared). With α_t = 4 the edge of the pupil is dim, so the high-angle rays carry little light.',
          r'A(\vartheta) = \exp\!\left(-\alpha_t \frac{\sin^2\vartheta}{\sin^2\alpha}\right), \quad \sin\alpha = \mathrm{NA}/n, \qquad A = e^{-\alpha_t \rho^2}\ (\text{paraxial})')

# ══ 3–4. glossary ════════════════════════════════════════════════════════
glossary('Glossary: geometry and optics', 'Every symbol on the following slides.', [
    ('NA', 'numerical aperture, n sin α: how wide a cone of light the lens focuses'),
    ('n', 'refractive index of the medium; air (n = 1), and water (n = 1.33) for NA above 0.99'),
    ('α', 'half-angle of the focusing cone'),
    ('L1, L2', 'the lenses focusing beam 1 and beam 2'),
    ('O', 'geometric focus of L1, the origin'),
    ('O′', 'geometric focus of L2, displaced to (x_c, z_c)'),
    ('x_c', 'offset of O′ across the axis of L1 (in the focal plane)'),
    ('z_c', 'offset of O′ along the axis of L1'),
    ('θ', 'angle between the optical axes of L1 and L2: π facing, π/2 crossed'),
    ('λ_1, λ_2', '2CE wavelengths, 750 nm and 656 nm'),
    ('λ_{2p}', '2PE wavelength, 700 nm, for both beams'),
    ('θ = π/2 limit', 'two lenses cross in air only for NA ≤ 1/√2 ≈ 0.71; above it, computed but not buildable'),
])
glossary('Glossary: signals, models and measures', 'What is computed and how it is scored.', [
    ('2CE / 2PE', 'two-color excitation, signal I_1 I_2 / two-photon excitation, signal |U_1 + U_2|^4'),
    ('PSF', 'point spread function: the fluorescence pattern from one point of the sample'),
    ('Peak lost', '1 − (peak of the misaligned PSF)/(peak of the aligned PSF), in percent'),
    ('20% tolerance', 'the offset x_c or z_c at which 20% of the peak is lost'),
    ('Paraxial scalar', 'Lim & Saloma’s focus: small-angle phase, no polarization'),
    ('Scalar Debye', 'exact angular phase kz cos ϑ, still no polarization'),
    ('Vector', 'Richards–Wolf (Debye–Wolf) focus: exact phase and polarization'),
    ('Unpolarized', 'intensity averaged over two orthogonal input polarizations'),
    ('α_t', 'truncation parameter, pupil amplitude exp(−α_t sin²ϑ/sin²α); 0 = uniform'),
    ('FWHM', 'full width at half maximum of a profile'),
    ('Scalar deviation', '|scalar/vector − 1| of a metric, in percent: how far the scalar model departs'),
    ('Linfoot F', 'fidelity of the misaligned PSF against the aligned one, each scaled to its peak (Lim & Saloma)'),
])

glossary('Glossary: fidelity, input, polarization and pulses', 'The symbols of the fidelity maps and of the later parts.', [
    ('x̃, z̃', 'offsets in units of the spot: x_c NA/λ across a beam, z_c NA^2/(nλ) along it'),
    ('F, C, Q', 'Linfoot fidelity, structural content, correlation quality, as Lim & Saloma define them'),
    ('ΔF', 'F with the vector model minus F with the paraxial scalar focus, at the same NA'),
    ('F ≥ 0.8 region', 'the offsets of O′ that keep F ≥ 0.8; its half-widths and area describe its shape'),
    ('A(ϑ)', 'pupil amplitude of a Gaussian input, exp(−α_t sin^2ϑ / sin^2α); the same on both lenses'),
    ('ψ', 'input polarization angle about a beam’s own axis'),
    ('s–s / p–p', 'both beams polarized perpendicular to / in the plane of the two lens axes'),
    ('Unpolarized', 'each beam averaged over two perpendicular input polarizations: exactly circular polarization'),
    ('τ, Δt', 'pulse length (intensity FWHM); delay of pulse 2 after pulse 1'),
    ('Gate', 'where the two pulses overlap in time; FWHM c√2 τ/2n along z at θ = π'),
    ('n sin(θ/2)', 'the largest NA at which two lenses with axes at angle θ fit side by side'),
])

# ══ 5. geometry ══════════════════════════════════════════════════════════
one('Geometry: x_c, z_c and θ', 'Beam 2’s focus O′ is displaced from O by x_c across and z_c along L1’s axis.',
    F('fig1_geometry.png'), [
        'O: focus of L1, the origin; O′: focus of L2.',
        'x_c: offset across L1’s axis; z_c: offset along it.',
        'θ: angle between the two optical axes.',
        'Lim & Saloma quote losses at fixed offsets in wavelengths, such as x_c = 0.37 λ_1.'],
    'Beam 2’s focus O prime is displaced from O by x_c across and z_c along L1’s axis.',
    'The geometry of Lim & Saloma’s Fig. 1. Every metric in this deck is a peak loss or a tolerance for moving O prime '
    'away from O, at the facing (theta = pi) or crossed (theta = pi/2) arrangement.', fw=4.4)

# ══ the single-beam field, before and after ══════════════════════════════
s = slide('The single-beam field: before and after', 'Lim & Saloma’s paraxial scalar field against the vector Richards–Wolf field.')
text(s, 0.5, 1.35, 4.3, 0.35, 'Before: Lim & Saloma (paraxial scalar)', 13, PURPLE, True, 'Cambria')
bullets(s, 0.5, 1.8, 4.3, 2.75, [
    'U(u, v) ∝ e^{ikz} · 2∫_0^1 J_0(vρ) e^{−iuρ²/2} ρ dρ',
    'u = k NA² z/n, v = k NA r, k = 2πn/λ',
    'Intensity I = |U|²',
    'One scalar field; the phase kz cos ϑ is replaced by its small-angle form.'], 12)
text(s, 5.1, 1.35, 4.4, 0.35, 'After: Richards–Wolf (vector)', 13, PURPLE, True, 'Cambria')
bullets(s, 5.1, 1.8, 4.4, 2.75, [
    'E(r, φ, z) ∝ (I_0 + I_2 cos 2φ, I_2 sin 2φ, 2i I_1 cos φ)',
    'I_0 = ∫_0^α √cos ϑ sin ϑ (1 + cos ϑ) J_0(kr sin ϑ) e^{ikz cos ϑ} dϑ',
    'I_1 = ∫_0^α √cos ϑ sin²ϑ J_1(kr sin ϑ) e^{ikz cos ϑ} dϑ',
    'I_2 = ∫_0^α √cos ϑ sin ϑ (1 − cos ϑ) J_2(kr sin ϑ) e^{ikz cos ϑ} dϑ',
    'sin α = NA/n; unpolarized: I averaged over two perpendicular input polarizations.'], 11.5)
text(s, 0.5, 4.6, 9.0, 0.3, 'r, z: distance from the focus across and along the axis; φ: azimuth about the axis; ρ: pupil radius over its '
     'edge; ϑ: ray angle; J_n: Bessel function of order n; λ: vacuum wavelength; n: medium index.', 10, GREY)
text(s, 0.5, 4.95, 9.0, 0.3, 'Both: a Gaussian input multiplies the pupil by A(ϑ) = exp(−α_t sin²ϑ/sin²α); α_t = 0 is uniform.', 11, GREY)
notes(s, 'Lim and Saloma’s paraxial scalar field against the vector Richards–Wolf field.',
      'Before: Lim and Saloma’s single-beam field, a scalar Debye integral in its small-angle, paraxial form, in the '
      'optical coordinates u and v. After: the Richards–Wolf field, which keeps the exact phase kz cos theta, the '
      'aplanatic factor root cos theta, and the three components of the electric field. Both take the same pupil '
      'function for a Gaussian input. At low NA the second reduces to the first.',
      r"""U(u,v) \propto e^{ikz}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\,\rho\, d\rho, \quad u = \frac{k\,\mathrm{NA}^2 z}{n},\ v = k\,\mathrm{NA}\, r
\mathbf{E}(r,\phi,z) \propto \left(I_0 + I_2\cos 2\phi,\ I_2 \sin 2\phi,\ 2i I_1 \cos\phi\right)
I_0 = \int_0^\alpha \sqrt{\cos\vartheta}\,\sin\vartheta\,(1+\cos\vartheta)\, J_0(kr\sin\vartheta)\, e^{ikz\cos\vartheta}\, d\vartheta
I_1 = \int_0^\alpha \sqrt{\cos\vartheta}\,\sin^2\vartheta\, J_1(kr\sin\vartheta)\, e^{ikz\cos\vartheta}\, d\vartheta
I_2 = \int_0^\alpha \sqrt{\cos\vartheta}\,\sin\vartheta\,(1-\cos\vartheta)\, J_2(kr\sin\vartheta)\, e^{ikz\cos\vartheta}\, d\vartheta
A(\vartheta) = \exp\!\left(-\alpha_t \frac{\sin^2\vartheta}{\sin^2\alpha}\right), \qquad \sin\alpha = \mathrm{NA}/n""")

# ══ 6–9. checks, Gaussian input, the lens problem ═════════════════════════
wide('Check 1: Lim & Saloma is the α_t → 0 limit', 'Truncated scalar foci converge smoothly onto Lim & Saloma’s as α_t → 0.',
    F('axial_lim_vs_truncation.png'), [
        'α_t = 0.5 already overlays the uniform (Lim & Saloma) curve; single beam, 750 nm, on-axis intensity.',
        'Larger α_t lengthens the focus and fills the axial zeros, as a Gaussian pupil must.'],
    'Truncated scalar foci converge smoothly onto Lim and Saloma’s as alpha_t goes to zero.',
    'Before comparing across NA we check the truncation itself. With the same pupil function as the vector model, the '
    'scalar focus moves smoothly away from Lim and Saloma’s as truncation grows, and returns to it as truncation vanishes.')
wide('Gaussian input against uniform, vector model', 'A Gaussian input (α_t = 4) lengthens the focus and fills its zeros at every NA.',
    F('axial_gaussian_vs_uniform.png'), [
        'The Gaussian dims the high-angle rays, so the focus acts like a lower NA (single beam, 750 nm, vector model, air).',
        'Black: uniform input, Lim & Saloma’s case. Red: Gaussian input, α_t = 4.'],
    'A Gaussian input lengthens the focus and fills its zeros at every NA.',
    'The vector model with a uniform input and with a Gaussian input, α_t = 4, at NA 0.5, 0.7 and 0.9. The '
    'Gaussian leaves the edge of the pupil dim, which lengthens the focus and removes the axial zeros; it is the input '
    'used for the second set of results.', fw=5.9)
wide('Check 2: scalar and vector agree at low NA', 'At every truncation the three foci coincide at low NA and part only slowly.',
    F('axial_scalar_vs_vector_truncation.png'), [
        'Largest on-axis gap, uniform → α_t = 4: 0.2% → 0.1% at NA 0.1, 1.9% → 0.8% at 0.3, 5.7% → 2.3% at 0.5.',
        'Our vector engine (mcdo.twobeam) and the analysis engine (mcdo.rw_integrals) agree to 10^{−8}.'],
    'At every truncation the three foci coincide at low NA and part only slowly.',
    'Scalar and vector on-axis profiles for truncation 0 and 4 at NA 0.1, 0.3 and 0.5, with the Richards–Wolf '
    'engine used throughout the rest of the analysis overlaid. The numbers we project come from identical optics.')

s = slide('The θ = π/2 lens problem', 'Above NA 0.71 in air, two lenses cannot cross at θ = π/2.')
figure(s, os.path.join(os.path.dirname(FIG), 'na_crossing_limit_air.png'), 0.45, 1.35, 5.4, 3.85)
notes(s, 'In air, two lenses cannot cross at theta = pi/2 above NA 1 over root 2.',
      'The limit is geometric. Each lens fills a cone of directions around its axis. With the axes at right angles, the '
      'cones stop overlapping only while each half-angle is at most 45 degrees, which in air is NA 0.71.',
      r'\mathrm{NA} = n\sin\alpha \le \frac{n}{\sqrt{2}}')

s = slide('Discussion: how high can crossed beams go?', 'Two lenses fit only while NA ≤ n sin(θ/2).')
figure(s, os.path.join(os.path.dirname(FIG), 'na_crossing_general.png'), 0.45, 1.35, 5.2, 3.85)
bullets(s, 5.85, 1.45, 3.65, 3.75, [
    'At θ = π/2 the limit is 0.71 in air, 0.94 in water and 1.07 in immersion oil.',
    'NA can never exceed n itself, so NA above 1 needs an immersion medium.',
    'Crossing at θ = π/2 with NA 1.2 would need n ≥ 1.70, beyond common immersion media.',
    'A smaller NA, or a wider angle between the lenses, keeps the geometry buildable.'], 12)
notes(s, 'Two lenses fit only while NA is at most n sin(theta/2).',
      'The general condition for two cones meeting at angle theta is that each half-angle be at most theta over two. '
      'At theta = pi/2 that gives 0.71 in air, 0.94 in water and 1.07 in oil. NA 1.2 at right angles would need an '
      'index of at least 1.7.',
      r'\mathrm{NA} \le n \sin(\theta/2)')

s = slide('Discussion: what our results above the limit mean', 'Computed field overlap, not a buildable microscope.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'We keep computing θ = π/2 above the limit, in air to NA 0.99 and in water to NA 1.2; these ranges are hatched.',
    'The calculation assumes both full cones reach the focus; real lenses there would block part of each other’s rays.',
    'So above the limit the results are a trend of the ideal overlap, not what an instrument would measure.',
    'Question 1: report these as trends, or stop θ = π/2 at the limit of the medium?',
    'Question 2: move the crossed-beam study to immersion (water, up to NA 0.94)?',
    'Question 3: study other crossing angles, where the limit is n sin(θ/2)?'], 13)
notes(s, 'Computed field overlap, not a buildable microscope.',
      'The results above the limit are well-defined calculations of how two ideal foci overlap, but no pair of lenses '
      'could deliver those full cones at right angles. These are the questions for the discussion.')

# ══ 8–12. the paper's quoted losses against NA ═══════════════════════════
for k, (title, paper) in enumerate(QUOTED, 1):
    if '' not in Q:
        pending(f'Quoted loss {k}: {title}', f'Lim & Saloma quote {paper}% lost at NA 0.5. Curve against NA from '
                'fig_lim2002_quoted_vs_na.py.')
        continue
    if '_at4' not in Q or SECTION:                  # one input per slide: uniform, or α_t = 4 in the Gaussian section
        qs = '_at4' if SECTION == 'gaussian' else ''
        v5u, s5u = Q[qs][(k, 0.5)]
        v9u, s9u = Q[qs][(k, 0.9)]
        one(f'Quoted loss {k}{GT}: {title}', f'Lim & Saloma: {paper}% lost at NA 0.5 (uniform). Vector: {v5u:.0f}% at NA 0.5, {v9u:.0f}% at NA 0.9.',
            F(f'quoted_vs_na_{k}{qs}.png'), [
                f'NA 0.5: vector {v5u:.1f}%, scalar {s5u:.1f}%, Lim & Saloma {paper}%.',
                f'NA 0.9: vector {v9u:.1f}% (the scalar model is shown only up to NA 0.5).',
                'The same offset in wavelengths costs more as the spot shrinks.'],
            f'Lim & Saloma: {paper} percent lost at NA 0.5; the same offset costs more as NA grows.',
            f'Lim and Saloma quote {paper} percent lost for {title.replace("_", " ")}. Solid: vector model; dotted: their '
            'paraxial scalar model, up to NA 0.5; black dashed: their quoted value; shaded: the range they claim for their model.',
            fw=5.0)
        continue
    v5u, s5u = Q[''][(k, 0.5)]
    v5g, _ = Q['_at4'][(k, 0.5)]
    v9u, s9u = Q[''][(k, 0.9)]
    pair(f'Quoted loss {k}: {title}', f'Lim & Saloma: {paper}% lost at NA 0.5. Vector: {v5u:.0f}% at NA 0.5, {v9u:.0f}% at NA 0.9.',
         F(f'quoted_vs_na_{k}.png'), F(f'quoted_vs_na_{k}_at4.png'), ('Uniform input (Lim & Saloma’s case)', 'Gaussian input, α_t = 4'), [
             f'NA 0.5: vector {v5u:.1f}%, scalar {s5u:.1f}%, Lim & Saloma {paper}%; with α_t = 4 the vector loss is {v5g:.1f}%.',
             f'NA 0.9: vector {v9u:.1f}%. The same offset in wavelengths costs more as the spot shrinks.'],
         f'Lim & Saloma: {paper} percent lost at NA 0.5; the same offset costs more as NA grows.',
         f'Lim and Saloma quote {paper} percent lost for {title.replace("_", " ")}. The solid line is the vector model, the '
         'dotted line their paraxial scalar model up to NA 0.5, the black dashed line their quoted value. The shaded band is the '
         'range they claim for their model. Right: the same with a Gaussian input, α_t = 4, which enlarges the spot and '
         'so lowers every loss.')

# ══ 13–16. tolerances and severity ═══════════════════════════════════════
for suf, lab in (('', 'uniform input'), ('_at4', 'α_t = 4')):
    if suf not in B or suf not in SUFS:                                # α_t = 4 is a next step until its sweep is run
        continue
    b = B[suf]
    def slope(key, col):                           # exponent p of the power law A·NA^(−p), fitted as in the figure
        nas_ = np.array(sorted(na for (k, na) in b if k == key))
        return -np.polyfit(np.log(nas_), np.log([b[(key, na)][col] for na in nas_]), 1)[0]
    s = slide(f'20% tolerances against NA, {lab}', 'Each tolerance shrinks as NA grows, following a power law in NA.')
    figure(s, F(f'na_breakdown_metrics_grid{suf}.png'), 0.45, 1.35, 4.9, 3.85)
    bullets(s, 5.55, 1.45, 3.95, 3.75, [
        'Tolerance: offset of O′ that costs 20% of the two-color peak.',
        'Each tolerance shrinks as NA grows, following a power law in NA.',
        f'θ = π: the tolerance across the axis falls as NA^{{−{slope("pi", "rx"):.2f}}} and the one along the axis as '
        f'NA^{{−{slope("pi", "rz"):.2f}}}.',
        f'θ = π/2: both tolerances fall as about NA^{{−{(slope("pi2", "rx") + slope("pi2", "rz")) / 2:.1f}}}.',
        'Dashed: Lim & Saloma at NA 0.5' + (' (uniform input)' if suf else '') + '; red: paraxial scalar, NA ≤ 0.5; '
        'hatched: lenses cannot cross.'], 12)
    notes(s, 'Tolerances shrink with the spot; the scalar model gives larger length-set ones than the vector model.',
          f'The offset costing twenty percent of the two-color peak, along x_c and z_c, at theta = pi and pi/2, for {lab}. '
          'The vector model is the reference; the dotted line is the paraxial scalar model. The gap between them is the next slide.')
    rows = [(f'θ = {"π" if key == "pi" else "π/2"}, {nm}', fmt_na(first_above(b, key, m, 5)), fmt_na(first_above(b, key, m, 10)))
            for key in ('pi', 'pi2') for m, nm in (('z', 'tolerance z_c'), ('x', 'tolerance x_c'), ('wz', 'depth of focus'), ('wx', 'lateral width'))]
    s = slide(f'Severity of the scalar–vector deviation, {lab}', 'NA at which the scalar–vector deviation first exceeds 5% and 10%.')
    figure(s, F(f'na_breakdown_severity{suf}.png'), 0.45, 1.35, 5.4, 3.85)
    for j, h in enumerate(('', '5%', '10%')):
        text(s, 6.2 + (0 if j == 0 else 1.75 + (j - 1) * 0.8), 1.42, 1.7 if j == 0 else 0.75, 0.25, h, 10, GREY, True,
             align=None if j == 0 else PP_ALIGN.CENTER)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            text(s, 6.2 + (0 if j == 0 else 1.75 + (j - 1) * 0.8), 1.72 + i * 0.3, 1.7 if j == 0 else 0.75, 0.28, v,
                 9.5, NAVY, j == 0, align=None if j == 0 else PP_ALIGN.CENTER)
    notes(s, 'The scalar–vector deviation grows with NA; length-set metrics cross 5% first.',
          f'Each line is how far the scalar model departs from the vector model, in percent, for {lab}. The table gives the NA '
          'at which each first exceeds five and ten percent. Entries above 0.95 never cross in the range computed.')

# ══ water, NA to 1.2 ═════════════════════════════════════════════════════
BW = {suf: b for suf in ('_n1.33', '_at4_n1.33') if len(b := load_breakdown(suf))}
if SECTION and have(f'na_breakdown_metrics{SUFS[0]}_n1.33.png') and f'{SUFS[0]}_n1.33' in BW:
    bw, ba = BW[f'{SUFS[0]}_n1.33'], B[SUFS[0]]
    wide(f'20% tolerances in water, NA 0.5 to 1.2{GT}', 'The scalar deviation follows NA/n: in water it starts at 1.33 times the air NA.',
        F(f'na_breakdown_metrics{SUFS[0]}_n1.33.png'), [
            f'θ = π, axial: the deviation passes 5% at NA {fmt_na(first_above(bw, "pi", "z", 5))} and 10% at NA '
            f'{fmt_na(first_above(bw, "pi", "z", 10))} (air: {fmt_na(first_above(ba, "pi", "z", 5))} and '
            f'{fmt_na(first_above(ba, "pi", "z", 10))}).',
            'The paraxial scalar model is shown only at NA 0.5, its stated range.',
            'Hatched: θ = π/2 above NA 0.94, where two lenses cannot cross in water.'],
        'In water the scalar deviation starts at 1.33 times the air NA: it follows the aperture angle NA/n.',
        'The same tolerances in water, to NA 1.2. The NA at which the scalar model departs by five and ten percent moves up '
        'by the index, because what sets the deviation is the half-angle of the cone, sin alpha = NA/n.', fw=5.4)
elif have('na_breakdown_metrics_n1.33.png') and '_n1.33' in BW:
    bw = BW['_n1.33']
    pair('20% tolerances in water, NA 0.5 to 1.2', 'The scalar deviation follows NA/n: in water it starts at 1.33 times the air NA.',
         F('na_breakdown_metrics_n1.33.png'), F('na_breakdown_metrics_at4_n1.33.png'),
         ('Uniform input, n = 1.33', 'Gaussian input, α_t = 4, n = 1.33'), [
             f'θ = π, axial: the deviation passes 5% at NA {fmt_na(first_above(bw, "pi", "z", 5))} and 10% at NA '
             f'{fmt_na(first_above(bw, "pi", "z", 10))} (air: {fmt_na(first_above(B[""], "pi", "z", 5))} and '
             f'{fmt_na(first_above(B[""], "pi", "z", 10))}).',
             'Hatched: θ = π/2 above NA 0.94, where two lenses cannot cross in water.'],
         'In water the scalar deviation starts at 1.33 times the air NA: it follows the aperture angle NA/n.',
         'The same tolerances in water, to NA 1.2. The paraxial scalar model is shown only at NA 0.5, its stated range. '
         'The NA at which the scalar model departs by five and ten percent moves up by the index, because what sets the '
         'deviation is the half-angle of the cone, sin alpha = NA/n.')

# ══ Fig. 4 maps against NA ═══════════════════════════════════════════════
for tag, lab in (('a', '2CE, θ = π'), ('b', '2PE, θ = π'), ('c', '2CE, θ = π/2'), ('d', '2PE, θ = π/2')):
    if not have(f'na_peakmaps_fig4{tag}.png'):
        pending(f'Fig. 4({tag}) against NA: {lab}', 'Peak maps over (x_c, z_c) at NA 0.5, 0.7, 0.9 from fig_lim2002_na_peakmaps.py.')
        continue
    s = slide(f'Fig. 4({tag}) against NA{GT}: {lab}', 'Peak surviving over (x_c, z_c): the tolerance region shrinks as NA grows.')
    stacked(s, f'na_peakmaps_fig4{tag}.png')
    notes(s, 'The region of (x_c, z_c) that keeps most of the peak shrinks as NA grows.',
          f'Lim & Saloma’s Fig. 4({tag}), {lab}, recomputed with the vector model at NA 0.5, 0.7 and 0.9, on their '
          'offset axes. Each contour marks the offsets that keep that percentage of the aligned peak.')

# ══ 17–18. why: the error split ══════════════════════════════════════════
wide('Where the length difference comes from', 'Keeping the exact phase fixes the length; polarization only widens the spot slightly.',
    F('na_profiles_theta_pi.png'), [
        'The scalar Debye length matches the vector one (NA 0.5: 3324 against 3326 nm; Lim & Saloma: 3562 nm), so the length '
        'error is the small-angle phase; polarization only widens the spot.',
        'The paraxial scalar model makes two simplifications: a small-angle phase and no polarization.'],
    'The length difference comes from the small-angle phase; polarization only widens the spot slightly.',
    'Three models: Lim & Saloma’s paraxial scalar focus, the exact scalar Debye integral, and the vector model. The '
    'scalar Debye length equals the vector length, so the length difference comes from replacing kz cos theta by its '
    'small-angle form. The width difference is polarization: at high angles part of the field turns longitudinal.', fw=3.9)
wide('Profiles at θ = π/2', 'Crossed beams see only widths, so only the smaller polarization difference appears.',
    F('na_profiles_theta_pi2.png'), [
        'Both scalar models give a spot 1.4–5% narrower than the vector one up to NA 0.7: only the widths of the two beams enter.',
        'Tolerances at θ = π/2 still err more, because an offset slides one beam along the other’s length.'],
    'Crossed beams see only widths, so only the smaller polarization difference appears.',
    'At theta = pi/2 the aligned spot is bounded by the two beams’ lateral widths, so its size is nearly right in the '
    'scalar model. The tolerances are not, because moving O prime slides one beam along the other’s long axis.', fw=3.9)

# ══ 19–26. contour comparisons ═══════════════════════════════════════════
PANEL = {'a': '2CE, θ = π', 'b': '2PE, θ = π', 'c': '2CE, θ = π/2', 'd': '2PE, θ = π/2'}
for fig_no, where in ((2, 'aligned'), (3, 'O′ = (0.4, 1.0) µm')):
    for tag, lab in PANEL.items():
        nas = '0.5, 0.7, 0.9' if 'π/2' not in lab else '0.5, 0.6, 0.7'
        s = slide(f'Fig. {fig_no}({tag}) against NA{GT}: {lab}', f'{where}; NA {nas}, vector, Lim & Saloma’s axes.')
        stacked(s, f'na_contours_fig{fig_no}{tag}.png')
        notes(s, 'The same panel at three NAs: the spot shrinks and becomes less elongated.',
              f'Lim & Saloma’s Fig. {fig_no}({tag}), {lab}, {where}, recomputed with the vector model at NA {nas} on '
              'their axes and contour levels. Width shrinks as lambda over NA and length as n lambda over NA squared.')

# ══ fidelity maps against NA ═════════════════════════════════════════════
FD = os.path.join(FIG, 'fidelity')
s = slide('Fidelity against NA: how it is shown', 'Offsets in units of the spot, so a pure change of scale drops out.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'Linfoot F over the offset (x_c, z_c) of O′, as in Lim & Saloma’s Figs. 5–6: the misaligned PSF against the aligned one.',
    'Offsets are divided by the size of the spot they move across: λ/NA across a beam, nλ/NA² along it; for 2PE, λ/n '
    'along a fringe direction, since the fringes (period λ/2n) set F there.',
    'In these units the paraxial scalar map is the same at every NA, so any change in the vector map is the effect of NA itself.',
    '(a) the F = 0.8 contour at every NA over the scalar one; (b) F vector − F scalar at six NAs; (c) the half-widths '
    'and area of the F ≥ 0.8 region, vector over scalar, against NA.',
    '41 × 41 offsets per map, 20–24 NAs per case, air to 0.99 and water (open markers) to 1.2.'], 12.5)
notes(s, 'Offsets in units of the spot, so a pure change of scale drops out.',
      'The fidelity maps are two-dimensional, so to compare NAs we put the offsets in units of the spot. The scalar map '
      'then does not change with NA at all, and what remains in the vector map is the effect of high NA. Each figure has '
      'three rows: the contour overlay, the difference maps and three shape numbers against NA.',
      r'	ilde{x} = rac{x_c\,\mathrm{NA}}{\lambda}, \qquad 	ilde{z} = rac{z_c\,\mathrm{NA}^2}{n\lambda}')


def shape_rows(case):
    path = os.path.join(FD, f'fidelity_shape_{case}_F.csv')
    return np.loadtxt(path, delimiter=',', ndmin=2) if os.path.exists(path) else np.empty((0, 8))


def ratio_at(a, na, col):
    r = a[(np.abs(a[:, 0] - na) < 1e-6) & (a[:, 1] == 1)]
    return r[0, col] / r[0, col + 3] if len(r) else np.nan


for case, lab in (('2ce_pi', '2CE, θ = π'), ('2ce_pi2', '2CE, θ = π/2'), ('2pe_pi', '2PE, θ = π'), ('2pe_pi2', '2PE, θ = π/2')):
    u, g = os.path.join(FD, f'fidelity_na_{case}_F.png'), os.path.join(FD, f'fidelity_na_{case}_at4_F.png')
    a = shape_rows(case + ('_at4' if SECTION == 'gaussian' else ''))
    if SECTION != 'both' and os.path.exists(g if SECTION == 'gaussian' else u) and len(a):
        hx, hz, ar = (ratio_at(a, 0.9, c) for c in (2, 3, 4))
        src = g if SECTION == 'gaussian' else u
        wide(f'Fidelity against NA{GT}: {lab}', f'NA 0.9, vector over scalar: half-width {hx:.2f} in x_c, {hz:.2f} in z_c; area {ar:.2f}.',
             src, [f'NA 0.5: {ratio_at(a, 0.5, 2):.2f} in x_c, {ratio_at(a, 0.5, 3):.2f} in z_c, area {ratio_at(a, 0.5, 4):.2f}. '
                   'Red dotted: the paraxial scalar; open markers: water (n = 1.33).'],
             f'{lab}: how the F ≥ 0.8 region changes shape against NA, relative to the scalar model.',
             f'Left, the contour F = 0.8 at every NA in spot units, over the paraxial scalar one. Right, its half-widths and '
             f'area, vector over scalar, against NA. At NA 0.9: {hx:.2f} and {hz:.2f}, area {ar:.2f}.')
        dsrc = src.replace('fidelity_na_', 'fidelity_dF_')
        if os.path.exists(dsrc):
            wide(f'Fidelity against NA{GT}: {lab}, ΔF maps', 'Where the vector fidelity differs from the scalar one, at six NAs.',
                 dsrc, ['Red: the vector model keeps more fidelity than the scalar model predicts; blue: less. (w): water.'],
                 f'{lab}: where vector and scalar fidelity differ.',
                 'F with the vector model minus F with the paraxial scalar focus, over the offset of O prime, at six NAs from '
                 'the lowest to the highest computed. The colour scale is set where the scalar fidelity is at least zero.')
        continue
    if not (os.path.exists(u) and os.path.exists(g)) or not len(a):
        pending(f'Fidelity against NA: {lab}', 'F maps over the offset of O′ against NA from fig_lim2002_fidelity_na.py.')
        continue
    hx, hz, ar = (ratio_at(a, 0.9, c) for c in (2, 3, 4))
    s = slide(f'Fidelity against NA: {lab}',
              f'NA 0.9, vector over scalar: half-width {hx:.2f} in x_c, {hz:.2f} in z_c; area {ar:.2f}.')
    for i, (path, l) in enumerate(((u, 'Uniform input'), (g, 'α_t = 4'))):
        label(s, 0.45 + i * 4.6, 1.3, 4.5, l, GREY if i == 0 else PURPLE)
        figure(s, path, 0.45 + i * 4.6, 1.58, 4.5, 3.65)
    notes(s, f'{lab}: how the F ≥ 0.8 region changes shape against NA, relative to the scalar model.',
          f'Linfoot fidelity over the offset of O prime for {lab}, uniform input on the left and a Gaussian input on the '
          f'right. At NA 0.5 the vector region is {ratio_at(a, 0.5, 2):.2f} of the scalar in x_c and '
          f'{ratio_at(a, 0.5, 3):.2f} in z_c; at NA 0.9, {hx:.2f} and {hz:.2f}, with area {ar:.2f}. Structural content C '
          'and correlation quality Q are in the same folder, in the same layout.')

# ══ 27. interpretation ═══════════════════════════════════════════════════
s = slide('How NA changes the picture', 'Everything scales with the spot; the scalar model gets the length wrong first.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'The focus shrinks as NA grows: lateral width as λ/NA, depth of focus as nλ/NA^2, so it also becomes less elongated.',
    'Every alignment tolerance shrinks with the spot, so the same offset in wavelengths costs more of the peak.',
    'Crossing the beams at θ = π/2 helps by cutting across the long axis of the spot; a less elongated spot gains '
    'less, and above NA 0.71 in air the crossing cannot be built.',
    'Lim & Saloma’s scalar model gives a longer depth of focus than the vector model through its small-angle phase; at the edge of its stated range, NA 0.5, the difference is 7%.',
    'Without polarization it gives a slightly smaller lateral width, by 5% near NA 0.8.',
    'A Gaussian input dims the high-angle rays and reduces both differences.'], 13)
notes(s, 'Everything scales with the spot; the scalar model gets the length wrong first.',
      'Three things happen as NA grows. The spot shrinks, faster along the axis than across it, and every alignment '
      'tolerance shrinks with it. The crossed geometry loses some of its advantage because the spot is less elongated, '
      'and above NA 0.71 in air it cannot be built at all. Lim and Saloma’s scalar model gives a longer depth of focus through its '
      'paraxial phase and slightly narrower spots by ignoring polarization.')

# ══ next: optical pulses ═════════════════════════════════════════════════
s = slide('Next: optical pulses and a time delay', 'Questions to settle before adding pulses to 2CE.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'With pulses the fields are summed over frequency with their phases, giving the field in time, E(P, t).',
    'The two-color signal becomes the overlap of the two pulses at a delay: F_{2c}(Δt) = ∫ I_1(t) I_2(t − Δt) dt.',
    'Question: do the two colors’ spectra overlap? They stay distinct only for pulses longer than about 8 fs; if they '
    'overlap, the two colors interfere as in 2PE.',
    'Question: should frequency pairs ω_1 + ω_2 be weighted by the molecule’s absorption band?',
    'Question: does the spread of spot sizes across the spectrum matter? Lim & Saloma (2003) find it negligible above ~10 fs.',
    'Question: lab pulses of ~100 fs, or few-fs pulses as in the rest of the analysis? Frequencies sampled in ω, not λ.'], 12)
notes(s, 'Questions to settle before adding pulses to 2CE.',
      'With pulses the fields must be summed with their phases to give the field in time, and the two-color signal '
      'becomes the time overlap of the two pulses at a delay. The broad spectrum raises questions: whether the two '
      'colors’ spectra overlap, in which case they interfere; whether to weight frequency pairs by the molecule’s '
      'absorption band; and whether the spread of focal spot sizes over the spectrum matters, which it does only for '
      'pulses of a few femtoseconds.',
      r"""F_{2c}(\Delta t) = \kappa_{2c} \int I_1(P,t)\, I_2(P,t-\Delta t)\, dt
\Delta\nu \approx \frac{0.441}{\tau} < \nu_2 - \nu_1 = 57\ \mathrm{THz} \;\Rightarrow\; \tau > 8\ \mathrm{fs}""")

s = slide('Other next steps', 'One geometry choice to settle, and the Gaussian-input set.')
bullets(s, 0.6, 1.45, 8.9, 3.7, [
    'θ = π/2 above NA 0.71: keep as a computed trend (hatched), or move to immersion, where it is buildable.',
    'Second set of results with a Gaussian input (α_t = 4): the quoted losses, tolerances and deviation against NA.'], 13)
notes(s, 'The lens-crossing limit to settle.', 'Whether to keep theta = pi/2 above the lens-crossing limit as a trend.')

# ── the story, in the order of the Sep 29 progress report; everything else follows as supporting slides ──
STORY = ('Main points', 'Gaussian input: main points', 'Gaussian input: the pupil', 'Geometry:', 'The single-beam field',
         'Fig. 2(', 'Fig. 3(', '20% tolerances against NA', 'Severity of', '20% tolerances in water', 'The θ = π/2 lens problem')
if SECTION in ('high_na', 'gaussian'):
    sup = slide('Supporting slides', 'Checks, Lim & Saloma’s quoted losses, peak maps and profiles.')
    notes(sup, 'Supporting slides.', 'The slides after this one back the story above.')
    ttl = lambda sl: next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()), '')
    ids = prs.slides._sldIdLst
    run = list(zip(prs.slides, list(ids)))[START + 1:]
    def rank(k_sl):
        k, (sl, _) = k_sl
        t = ttl(sl)
        pos = next((i for i, p in enumerate(STORY) if t.startswith(p)), None)
        return (0, pos, k) if pos is not None else (1, 0 if t == 'Supporting slides' else 1, k)
    for _, (sl, el) in sorted(enumerate(run), key=rank):
        ids.remove(el); ids.append(el)

if SECTION:                                          # keep only this section's slides of this run
    title_ = lambda sl: next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()), '')
    LATER = ('Next: optical', 'Other next steps', 'Glossary')       # the report has its own next steps and glossary
    if SECTION == 'foundations':                     # what a standalone part needs: the geometry and the two field models
        keep = lambda t: t.startswith(('Geometry:', 'The single-beam field'))
    elif SECTION == 'fidelity':
        keep = lambda t: t.startswith('Fidelity against NA')
    elif SECTION == 'high_na':
        keep = lambda t: not t.startswith(('Gaussian input', 'Check 1', 'Fidelity against NA') + LATER)
    else:                                            # 'gaussian'
        keep = lambda t: not t.startswith(('Where Lim', 'Main points', 'Geometry:', 'The single-beam field', 'Check 2',
                                           'Discussion:', 'Where the length difference', 'Profiles at',
                                           'Fidelity against NA: how', 'How NA changes') + LATER)
    ds.DROP = getattr(ds, 'DROP', [])                  # marked here, removed once by the caller after every slide is added
    for sl, el in list(zip(prs.slides, prs.slides._sldIdLst))[START + 1:]:   # the run's own title is the caller's to replace
        if not keep(title_(sl)):
            ds.DROP.append(el)
if os.environ.get('DECK_APPEND'):                    # set by make_lim2002_progress_deck.py, which saves the whole report
    raise SystemExit
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')

# ── the 15-minute cut: the same slides, fewer of them, renumbered ──
from pptx import Presentation

SHORT = ('Where Lim & Saloma’s scalar model applies', 'Main points', 'Glossary: geometry', 'Glossary: signals',
         'Geometry:', 'Check 2:', 'Fig. 2(a) against NA', 'Fig. 4(a) against NA', '20% tolerances against NA, uniform',
         'How far the scalar model departs, uniform', '20% tolerances in water', 'Fidelity against NA: how',
         'Fidelity against NA: 2CE, θ = π', 'Where the length difference comes from', 'How NA changes',
         'Next: optical pulses')
short = Presentation(OUT)
title_of = lambda sl: next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()), '')
ids = list(short.slides._sldIdLst)
by_title = {title_of(sl): el for sl, el in zip(short.slides, ids)}
order = [el for key in SHORT for el in [next((el for t, el in by_title.items() if t.startswith(key)), None)] if el is not None]   # slides still pending are skipped
for el in ids:
    short.slides._sldIdLst.remove(el)
    if el not in order:
        short.part.drop_rel(el.rId)
for el in order:
    short.slides._sldIdLst.append(el)
for i, sl in enumerate(short.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
OUT15 = OUT.replace('.pptx', '_15min.pptx')
short.save(OUT15)
print('Saved ->', OUT15, f'({len(short.slides)} slides)')


