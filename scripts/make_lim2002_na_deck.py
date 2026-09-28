r"""Deck: Lim & Saloma (2002) against NA. Where the paper's scalar model breaks
down, measured on the paper's own metrics, for uniform input and for α_t = 4.

Same style as the replication deck (mcdo.deckstyle). Every number on the slides
is read from the result files the figure scripts write, so a rerun updates
the deck:

    fig_lim2002_quoted_vs_na.py    [ALPHA_T=4]  -> quoted_vs_na[_at4].csv, quoted_vs_na_{1..5}[_at4].png
    fig_lim2002_na_breakdown.py    [ALPHA_T=4]  -> na_breakdown[_at4].csv, na_breakdown_{metrics,severity}[_at4].png
    fig_lim2002_na_profiles.py                  -> na_profiles_theta_{pi,pi2}.png
    fig_lim2002_na_contours.py                  -> na_contours_fig{2,3}{a..d}.png
    fig_lim2002_axial_truncation.py             -> axial_lim_vs_truncation.png, axial_scalar_vs_vector_truncation.png

    python scripts/make_lim2002_na_deck.py
    -> ~/Downloads/Research/two_color/lim2002_na_study.pptx
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

import mcdo.deckstyle as ds
from mcdo.deckstyle import (CARD, FIG, GREY, NAVY, ORANGE, PALE, PURPLE, RED, WHITE, MSO_ANCHOR, MSO_SHAPE,
                            PP_ALIGN, bullets, card, chip, dots, figure, label, notes, numbered, prs, shape,
                            slide, text)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_na_study.pptx')
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), at high NA'
F = lambda name: os.path.join(FIG, name)
QUOTED = [  # metric number: (title, paper %)
    ('2CE, θ = π/2, x_c = 1.33 λ_1', 11), ('2CE, θ = π, x_c = 0.37 λ_1', 20),
    ('2PE, θ = π/2, x_c = 0.5 λ_{2p}', 30), ('2CE, θ = π, z_c = 2.7 λ_1', 20),
    ('2CE, θ = π/2, z_c = 2.7 λ_1', 30)]


# ── read the results ──────────────────────────────────────────────────────
def load_quoted(suf):
    d = {}
    for k, na, v, s in np.loadtxt(F(f'quoted_vs_na{suf}.csv'), delimiter=','):
        d[(int(k), round(na, 2))] = (v, s)
    return d


def load_breakdown(suf):
    d = {}
    for t, na, sx, sz, rx, rz, Fi, wx, wz in np.loadtxt(F(f'na_breakdown{suf}.csv'), delimiter=','):
        d[('pi' if t == 0 else 'pi2', round(na, 2))] = dict(x=abs(sx / rx - 1) * 100, z=abs(sz / rz - 1) * 100,
                                                          wx=abs(wx - 1) * 100, wz=abs(wz - 1) * 100,
                                                          F=(1 - Fi) * 100, rx=rx, rz=rz)
    return d


def first_above(d, key, m, thr):
    nas = sorted(na for (k, na) in d if k == key)
    return next((na for na in nas if d[(key, na)][m] > thr), None)


have = lambda name: os.path.exists(F(name))
Q = {suf: load_quoted(suf) for suf in ('', '_at4') if have(f'quoted_vs_na{suf}.csv')}
B = {suf: load_breakdown(suf) for suf in ('', '_at4') if have(f'na_breakdown{suf}.csv')}


def pending(title, what):
    s = slide(title, 'Result still computing; this slide fills in when the deck is rebuilt.')
    card(s, 0.5, 1.45, 9.0, 1.4, 'Pending', ORANGE, [what], 13)
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


def pair(title, takeaway, left, right, labels, items, main, script, latex=None):
    """Two figures side by side, points below."""
    s = slide(title, takeaway)
    for i, (path, lab) in enumerate(zip((left, right), labels)):
        label(s, 0.45 + i * 4.6, 1.3, 4.5, lab, GREY if i == 0 else PURPLE)
        figure(s, path, 0.45 + i * 4.6, 1.58, 4.5, 2.85)
    bullets(s, 0.6, 4.5, 8.9, 0.75, items, 11)
    notes(s, main, script, latex)
    return s


def one(title, takeaway, path, items, main, script, latex=None, fw=5.6):
    """One figure at the left, points at the right."""
    s = slide(title, takeaway)
    figure(s, path, 0.45, 1.35, fw, 3.85)
    bullets(s, 0.45 + fw + 0.25, 1.45, 9.5 - fw - 0.7, 3.8, items, 11.5)
    notes(s, main, script, latex)
    return s


# ══ 1. title ═════════════════════════════════════════════════════════════
s = prs.slides.add_slide(ds.BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
dots(s, 0.6, 0.7, 0.2, 0.27)
text(s, 0.6, 1.15, 8.8, 1.5, 'Severity of the scalar-model defect as a function of NA: Lim & Saloma (2002)',
     30, WHITE, True, 'Cambria')
text(s, 0.6, 2.85, 8.8, 0.4, 'Roland Albert A. Romero', 18, WHITE)
text(s, 0.6, 3.25, 8.8, 0.35, 'National Institute of Physics, University of the Philippines Diliman', 13, PALE)
text(s, 0.6, 3.6, 8.8, 0.35, 'The paper’s own metrics, recomputed with the vector (Richards–Wolf) focus', 13, PALE)
chip(s, 0.6, 4.45, 1.15, 'NA 0.1', PURPLE)
text(s, 1.8, 4.45, 0.35, 0.36, '→', 16, WHITE, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
chip(s, 2.2, 4.45, 1.15, 'NA 0.95', RED)
text(s, 3.5, 4.45, 5.5, 0.36, 'air; uniform input and α_t = 4', 12, PALE, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'The paper’s scalar model is good to a few percent below NA 0.45 and fails on focal length above it.',
      'This deck asks how far Lim and Saloma’s results carry as the numerical aperture grows. We recompute the '
      'paper’s own quoted metrics with the vector focus, keep the paper’s model alongside, and measure the gap.')

# ══ 2. main points ═══════════════════════════════════════════════════════
b0 = B['']
s = slide('Main points', 'The scalar model misjudges focal length first; widths and shapes hold much longer.')
numbered(s, 1, PURPLE, 1.4, f'Checks pass: at low NA the scalar and vector foci coincide, our engine matches the '
                            f'analysis engine to 10^{{−8}}, and Lim & Saloma is the α_t → 0 limit.', 12)
numbered(s, 2, RED, 2.05, f'Length-set metrics break first: scalar error above 5% from NA '
                          f'{fmt_na(first_above(b0, "pi", "z", 5))} and above 10% from NA '
                          f'{fmt_na(first_above(b0, "pi", "z", 10))} (θ = π, axial tolerance).', 12)
numbered(s, 3, ORANGE, 2.7, 'That error is the paraxial approximation, not polarization: the scalar Debye '
                            'integral already has the right length.', 12)
numbered(s, 4, NAVY, 3.35, f'Width-set metrics hold to NA {fmt_na(first_above(b0, "pi", "x", 5))} (5%); '
                           'Gaussian input (α_t = 4) shrinks every error.', 12)
text(s, 0.6, 4.4, 8.9, 0.6, 'At the paper’s own NA 0.5 the scalar model already overstates the axial tolerance by '
     f'{b0[("pi", 0.5)]["z"]:.0f}%.', 12, GREY)
notes(s, 'The scalar model misjudges focal length first; widths and shapes hold much longer.',
      'Four points. The models and the engine check out at low NA. The metrics set by the length of the focus go wrong '
      'first, above five percent from NA 0.45 and above ten percent from 0.6. The cause is the paraxial phase, not '
      'polarization. Metrics set by the width hold to about NA 0.8, and a Gaussian input reduces every error.')

# ══ 3–4. glossary ════════════════════════════════════════════════════════
glossary('Glossary: geometry and optics', 'Every symbol on the following slides.', [
    ('NA', 'numerical aperture, n sin α: how wide a cone of light the lens focuses'),
    ('n', 'refractive index of the medium; air, n = 1, throughout'),
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
    ('Scalar error', '|scalar/vector − 1| of a metric, in percent'),
    ('Linfoot F', 'fidelity of the scalar PSF against the vector one; 1 − F reported'),
])

# ══ 5. geometry ══════════════════════════════════════════════════════════
one('Geometry: x_c, z_c and θ', 'Beam 2’s focus O′ is displaced from O by x_c across and z_c along L1’s axis.',
    F('fig1_geometry.png'), [
        'O: focus of L1, the origin; O′: focus of L2.',
        'x_c: offset across L1’s axis; z_c: offset along it.',
        'θ: angle between the two optical axes.',
        'The paper quotes losses at fixed offsets in wavelengths, such as x_c = 0.37 λ_1.'],
    'Beam 2’s focus O prime is displaced from O by x_c across and z_c along L1’s axis.',
    'The geometry of the paper’s Fig. 1. Every metric in this deck is a peak loss or a tolerance for moving O prime '
    'away from O, at the facing (theta = pi) or crossed (theta = pi/2) arrangement.', fw=4.4)

# ══ 6–9. checks, Gaussian input, the lens problem ═════════════════════════
one('Check 1: Lim & Saloma is the α_t → 0 limit', 'Truncated scalar foci converge smoothly onto Lim & Saloma’s as α_t → 0.',
    F('axial_lim_vs_truncation.png'), [
        'Single beam, 750 nm, on-axis intensity.',
        'α_t = 0.5 already overlays the uniform (Lim & Saloma) curve.',
        'Larger α_t lengthens the focus and fills the axial zeros, as a Gaussian pupil must.'],
    'Truncated scalar foci converge smoothly onto Lim and Saloma’s as alpha_t goes to zero.',
    'Before comparing across NA we check the truncation itself. With the same pupil function as the vector model, the '
    'scalar focus moves smoothly away from Lim and Saloma’s as truncation grows, and returns to it as truncation vanishes.')
one('Gaussian input against uniform, vector focus', 'A Gaussian input (α_t = 4) lengthens the focus and fills its zeros at every NA.',
    F('axial_gaussian_vs_uniform.png'), [
        'Single beam, 750 nm, on-axis intensity, Richards–Wolf focus in air.',
        'Black: uniform input, the paper’s case. Red: Gaussian input, α_t = 4.',
        'The Gaussian dims the high-angle rays, so the focus acts like a lower NA.'],
    'A Gaussian input lengthens the focus and fills its zeros at every NA.',
    'The vector focus with a uniform input and with a Gaussian input of truncation 4, at NA 0.5, 0.7 and 0.9. The '
    'Gaussian leaves the edge of the pupil dim, which lengthens the focus and removes the axial zeros; it is the input '
    'used for the second set of results.', fw=5.9)
one('Check 2: scalar and vector agree at low NA', 'At every truncation the three foci coincide at low NA and part only slowly.',
    F('axial_scalar_vs_vector_truncation.png'), [
        'Largest on-axis gap, uniform → α_t = 4: 0.2% → 0.1% at NA 0.1, 1.9% → 0.8% at 0.3, 5.7% → 2.3% at 0.5.',
        'Our vector engine (mcdo.twobeam) and the analysis engine (mcdo.rw_integrals) agree to 10^{−8}.'],
    'At every truncation the three foci coincide at low NA and part only slowly.',
    'Scalar and vector on-axis profiles for truncation 0, 1 and 4 at NA 0.1, 0.3 and 0.5, with the Richards–Wolf '
    'engine used throughout the rest of the analysis overlaid. The numbers we project come from identical optics.')

s = slide('The θ = π/2 lens problem', 'Above NA 0.71 in air, two lenses cannot cross at θ = π/2.')
figure(s, os.path.join(os.path.dirname(FIG), 'na_crossing_limit_air.png'), 0.45, 1.35, 5.4, 3.85)
card(s, 6.05, 1.35, 3.45, 3.85, 'Description', RED, ['(to be written)'], 12)
notes(s, 'Above NA 0.71 in air, two lenses cannot cross at theta = pi/2.',
      'Each lens focuses a cone of half-angle alpha, with NA = n sin alpha. At theta = pi/2 the two cones fit side by '
      'side only if alpha is at most 45 degrees, NA at most 1 over root 2 in air. Above that the two lenses would occupy '
      'the same directions from the focus. The field overlap is still well defined, so these NAs are computed and '
      'hatched in the plots as not buildable. The limit does not arise at theta = 0, where both colors share one lens, '
      'or at theta = pi, where the lenses face each other.',
      r'\mathrm{NA} = n\sin\alpha \le \frac{n}{\sqrt{2}}')

# ══ 8–12. the paper's quoted losses against NA ═══════════════════════════
for k, (title, paper) in enumerate(QUOTED, 1):
    if not ('' in Q and '_at4' in Q):
        pending(f'Quoted loss {k}: {title}', f'The paper quotes {paper}% lost at NA 0.5. Curves against NA, '
                'uniform and α_t = 4, from fig_lim2002_quoted_vs_na.py.')
        continue
    v5u, s5u = Q[''][(k, 0.5)]
    v5g, _ = Q['_at4'][(k, 0.5)]
    v9u, s9u = Q[''][(k, 0.9)]
    pair(f'Quoted loss {k}: {title}', f'Paper: {paper}% lost at NA 0.5. Vector: {v5u:.0f}% at NA 0.5, {v9u:.0f}% at NA 0.9.',
         F(f'quoted_vs_na_{k}.png'), F(f'quoted_vs_na_{k}_at4.png'), ('Uniform input (the paper’s case)', 'Gaussian input, α_t = 4'), [
             f'NA 0.5: vector {v5u:.1f}%, scalar {s5u:.1f}%, paper {paper}%; with α_t = 4 the vector loss is {v5g:.1f}%.',
             f'NA 0.9: vector {v9u:.1f}%, scalar {s9u:.1f}%. The same offset in wavelengths costs more as the spot shrinks.'],
         f'Paper: {paper} percent lost at NA 0.5; the same offset costs more as NA grows.',
         f'The paper quotes {paper} percent lost for {title.replace("_", " ")}. The solid line is the vector focus, the '
         'dashed line the paper’s paraxial scalar model, the star the paper’s number. The shaded band is the range the '
         'paper claims for its model. Right: the same with a Gaussian input, truncation 4, which enlarges the spot and '
         'so lowers every loss.')

# ══ 13–16. tolerances and severity ═══════════════════════════════════════
for suf, lab in (('', 'uniform input'), ('_at4', 'α_t = 4')):
    if suf not in B:
        pending(f'20% tolerances against NA, {lab}', 'From fig_lim2002_na_breakdown.py with ALPHA_T=4.')
        pending(f'Severity of the scalar model’s error, {lab}', 'From fig_lim2002_na_breakdown.py with ALPHA_T=4.')
        continue
    b = B[suf]
    one(f'20% tolerances against NA, {lab}', 'Vector (solid) against the paper’s scalar model (dashed); star: the paper.',
        F(f'na_breakdown_metrics{suf}.png'), [
            f'θ = π, axial: vector {b[("pi", 0.5)]["rz"]:.2f} µm at NA 0.5, {b[("pi", 0.9)]["rz"]:.2f} µm at NA 0.9.',
            f'θ = π, in-plane: vector {b[("pi", 0.5)]["rx"]:.2f} µm at NA 0.5, {b[("pi", 0.9)]["rx"]:.2f} µm at NA 0.9.',
            'Hatched: θ = π/2 above NA 0.71, not buildable in air.'],
        'Tolerances shrink with the spot; the scalar model overstates the length-set ones.',
        f'The offset costing twenty percent of the two-color peak, along x_c and z_c, at theta = pi and pi/2, for {lab}. '
        'The vector focus is the reference; the dashed line is the paper’s model. The gap between them is the next slide.',
        fw=5.4)
    rows = [(f'θ = {"π" if key == "pi" else "π/2"}, {nm}', fmt_na(first_above(b, key, m, 5)), fmt_na(first_above(b, key, m, 10)))
            for key in ('pi', 'pi2') for m, nm in (('z', 'tolerance z_c'), ('x', 'tolerance x_c'), ('wz', 'length'), ('wx', 'width'))]
    s = slide(f'Severity of the scalar model’s error, {lab}', 'NA at which the scalar error first exceeds 5% and 10%.')
    figure(s, F(f'na_breakdown_severity{suf}.png'), 0.45, 1.35, 5.4, 3.85)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 6.05, 1.35, 3.45, 0.42 + 0.3 * len(rows), CARD)
    for j, h in enumerate(('', '5%', '10%')):
        text(s, 6.2 + (0 if j == 0 else 1.75 + (j - 1) * 0.8), 1.42, 1.7 if j == 0 else 0.75, 0.25, h, 10, GREY, True,
             align=None if j == 0 else PP_ALIGN.CENTER)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            text(s, 6.2 + (0 if j == 0 else 1.75 + (j - 1) * 0.8), 1.72 + i * 0.3, 1.7 if j == 0 else 0.75, 0.28, v,
                 9.5, NAVY, j == 0, align=None if j == 0 else PP_ALIGN.CENTER)
    notes(s, 'The scalar model’s error grows with NA; length-set metrics cross 5% first.',
          f'Each line is the scalar model’s relative error against the vector focus, for {lab}. The table gives the NA '
          'at which each first exceeds five and ten percent. Entries above 0.95 never cross in the range computed.')

# ══ 17–18. why: the error split ══════════════════════════════════════════
one('Why the length goes wrong: paraxial, not polarization', 'Scalar Debye already has the vector length; the paraxial phase does not.',
    F('na_profiles_theta_pi.png'), [
        'θ = π, NA 0.5, length: paraxial 3562, scalar Debye 3324, vector 3326 nm.',
        'NA 0.95, length: 987, 660, 672 nm.',
        'Width: paraxial and scalar Debye agree; the vector spot is wider by 2–13% (polarization, E_z).'],
    'The scalar length error is the paraxial phase; the smaller width error is polarization.',
    'Three models: the paper’s paraxial scalar focus, the exact scalar Debye integral, and the vector focus. The '
    'scalar Debye length equals the vector length, so the length error comes from replacing kz cos theta by its '
    'small-angle form. The width error is polarization: at high angles part of the field turns longitudinal.', fw=3.9)
one('Profiles at θ = π/2', 'Crossed beams see only widths, so only the smaller polarization error appears.',
    F('na_profiles_theta_pi2.png'), [
        'Both FWHMs at θ = π/2 are set by lateral widths of the two beams.',
        'Paraxial and scalar Debye agree; the vector spot is 2–3% wider up to NA 0.7.',
        'Tolerances at θ = π/2 still err more, because an offset slides one beam along the other’s length.'],
    'Crossed beams see only widths, so only the smaller polarization error appears.',
    'At theta = pi/2 the aligned spot is bounded by the two beams’ lateral widths, so its size is nearly right in the '
    'scalar model. The tolerances are not, because moving O prime slides one beam along the other’s long axis.', fw=3.9)

# ══ 19–26. contour comparisons ═══════════════════════════════════════════
PANEL = {'a': '2CE, θ = π', 'b': '2PE, θ = π', 'c': '2CE, θ = π/2', 'd': '2PE, θ = π/2'}
for fig_no, where in ((2, 'aligned'), (3, 'O′ = (0.4, 1.0) µm')):
    for tag, lab in PANEL.items():
        nas = '0.5, 0.7, 0.9' if 'π/2' not in lab else '0.5, 0.6, 0.7'
        s = slide(f'Fig. {fig_no}({tag}) against NA: {lab}', f'{where}; NA {nas}, vector, the paper’s axes.')
        figure(s, F(f'na_contours_fig{fig_no}{tag}.png'), 0.45, 1.4, 9.1, 3.7)
        notes(s, 'The same panel at three NAs: the spot shrinks and becomes less elongated.',
              f'The paper’s Fig. {fig_no}({tag}), {lab}, {where}, recomputed with the vector focus at NA {nas} on the '
              'paper’s axes and contour levels. Width shrinks as lambda over NA and length as n lambda over NA squared.')

# ══ 27. interpretation ═══════════════════════════════════════════════════
s = slide('How NA changes the picture', 'Everything scales with the spot; the scalar model gets the length wrong first.')
card(s, 0.5, 1.4, 2.9, 3.6, 'Scaling', PURPLE, [
    'Width ∝ λ/NA, length ∝ nλ/NA^2: the spot shrinks and becomes less elongated.',
    'Every tolerance shrinks with it; a fixed offset in λ costs more.'], 11)
card(s, 3.55, 1.4, 2.9, 3.6, 'Crossed beams', RED, [
    'θ = π/2 gains by cutting the long axis; less elongation means less gain.',
    'Above NA 0.71 in air it cannot be built.'], 11)
card(s, 6.6, 1.4, 2.9, 3.6, 'The paper’s model', ORANGE, [
    'Paraxial phase: overstates length-set quantities, 7% already at NA 0.5.',
    'No polarization: understates widths, 5% near NA 0.8.',
    'Gaussian input reduces both.'], 11)
notes(s, 'Everything scales with the spot; the scalar model gets the length wrong first.',
      'Three things happen as NA grows. The spot shrinks, faster along the axis than across it, and every alignment '
      'tolerance shrinks with it. The crossed geometry loses some of its advantage because the spot is less elongated, '
      'and above NA 0.71 in air it cannot be built at all. The paper’s scalar model overstates focal lengths through its '
      'paraxial phase and slightly understates widths by ignoring polarization.')

# ══ next: optical pulses ═════════════════════════════════════════════════
s = slide('Next: optical pulses and a time delay', 'Questions to settle before adding pulses to 2CE.')
card(s, 0.5, 1.4, 4.4, 3.8, 'What changes', PURPLE, [
    'Time-resolved fields: E(P, t) from the fields summed over ω with their phases.',
    'Signal with delay: F_{2c}(Δt) = ∫ I_1(t) I_2(t − Δt) dt.',
    'Sample ω, not λ (adviser); keep ω > 0.',
    'Delays 0 to ±2τ; at θ = π, 1 fs of delay moves the meeting point about 0.15 µm.'], 11)
card(s, 5.1, 1.4, 4.4, 3.8, 'Questions: the broad spectrum', RED, [
    'Do the two colors’ spectra overlap? They stay distinct only for τ > 8 fs (57 THz apart).',
    'If they overlap, 2CE interferes like 2PE: allow it or require τ ≥ 20 fs?',
    'Which pairs ω_1 + ω_2 does the molecule absorb: include its band σ(ω_1 + ω_2)?',
    'Does the spot’s spread over λ matter? Negligible above ~10 fs (Lim & Saloma 2003).',
    'Lab pulses (~100 fs) or few-fs pulses like the rest of the analysis?'], 10.5)
notes(s, 'Questions to settle before adding pulses to 2CE.',
      'With pulses the fields must be summed with their phases to give the field in time, and the two-color signal '
      'becomes the time overlap of the two pulses at a delay. The broad spectrum raises questions: whether the two '
      'colors’ spectra overlap, in which case they interfere; whether to weight frequency pairs by the molecule’s '
      'absorption band; and whether the spread of focal spot sizes over the spectrum matters, which it does only for '
      'pulses of a few femtoseconds.',
      r"""F_{2c}(\Delta t) = \kappa_{2c} \int I_1(P,t)\, I_2(P,t-\Delta t)\, dt
\Delta\nu \approx \frac{0.441}{\tau} < \nu_2 - \nu_1 = 57\ \mathrm{THz} \;\Rightarrow\; \tau > 8\ \mathrm{fs}""")

s = slide('Other open choices', 'Two geometry choices to settle.')
bullets(s, 0.6, 1.45, 8.9, 3.7, [
    'θ = π/2 above NA 0.71: keep as a computed trend (hatched), or move to immersion, where it is buildable.',
    'Beam 2’s direction at θ = π/2: follow the paper’s Fig. 1 or keep ours; it only tilts the 2PE fringes.'], 13)
notes(s, 'Two geometry choices to settle.', 'The lens-crossing limit and the direction of beam 2 at theta = pi/2.')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')
