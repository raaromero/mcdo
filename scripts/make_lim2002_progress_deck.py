r"""Progress report: Lim & Saloma (2002), from replication to high NA, with the choices that remain.

The full report has six parts and ends with one glossary of every term:

  Part 1  replication, as built by make_lim2002_replication_deck.py
  Part 2  high NA, uniform input: make_lim2002_na_deck.py with SECTION=high_na
  Part 3  fidelity against NA: the Linfoot criteria, then SECTION=fidelity
  Part 4  Gaussian input, α_t = 4: SECTION=gaussian
  Part 5  polarization as a decision: unpolarized against s–s and p–p, from fig_lim2002_polarization.py
  Part 6  next time: pulses, what the model has to account for (theory only)

Each part is also built as a deck that stands on its own (PART=k): its own title
and summary, the geometry and field equations it relies on (SECTION=foundations),
its slides, and a glossary of the terms it uses. The existing decks run into the
same presentation (DECK_APPEND=1 stops them saving their own files). Every
number is read from the saved results, so a rerun updates every deck.

    python scripts/make_lim2002_progress_deck.py            # the report, then each part in its own process
    PART=3 python scripts/make_lim2002_progress_deck.py     # one part
    -> ~/Downloads/Research/two_color/lim2002_progress_report.pptx, lim2002_progress_report_part{1..6}_*.pptx
"""

import os
import runpy
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DECK_APPEND'] = '1'

import numpy as np

import mcdo.deckstyle as ds
from mcdo.deckstyle import (CARD, FIG, GREY, NAVY, ORANGE, PALE, PURPLE, RED, WHITE, MSO_ANCHOR, MSO_SHAPE, PP_ALIGN,
                            bullets, chip, dots, figure, notes, prs, shape, slide, text)

PART = int(os.environ['PART']) if os.environ.get('PART') else None    # None: the full report
NAMES = ['replication', 'high_na', 'fidelity', 'gaussian', 'polarization', 'pulses_next']
REPORT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_progress_report.pptx')
OUT = REPORT if PART is None else REPORT.replace('.pptx', f'_part{PART}_{NAMES[PART - 1]}.pptx')
WANT = lambda k: PART in (None, k)
HERE = os.path.dirname(__file__)
PUL = os.path.join(FIG, 'pulsed')
title_of = lambda sl: next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()), '')


def navy(title, lines, chips=()):
    """A navy slide: the report title or a section divider."""
    s = prs.slides.add_slide(ds.BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    dots(s, 0.6, 0.7, 0.2, 0.27)
    text(s, 0.6, 1.15, 8.8, 1.5, title, 30, WHITE, True, 'Cambria')
    for i, (line, size, col) in enumerate(lines):
        text(s, 0.6, 2.85 + i * 0.4, 8.8, 0.4, line, size, col)
    for i, (lab, col) in enumerate(chips):
        chip(s, 0.6 + i * 1.6, 4.45, 1.45, lab, col)
    return s


def part(no, title, what):
    """The divider of a part in the full report, or the title slide of a standalone part deck."""
    if PART is None:
        s = navy(f'Part {no}: {title}', [(what, 14, PALE)])
    else:
        s = navy(f'Part {no}: {title[0].upper() + title[1:]}', [
            ('Roland Albert A. Romero', 18, WHITE),
            ('Progress report on Lim & Saloma (2002): two-color excitation with misaligned foci', 13, PALE),
            ('M. Lim & C. Saloma, Opt. Commun. 207, 121–130 (2002)', 13, PALE)])
    notes(s, f'Part {no}: {title}.', what)


def summary(rows, title='Summary'):
    """Main point per part as a bullet, the supporting points as a sub-bullet."""
    s = slide(title, 'Main point; supporting points beneath.' if len(rows) > 1 else rows[0][2])
    items = []
    for head, _, main, support in rows:
        items += [f'{head.split(". ", 1)[-1]}: {main}' if len(rows) > 1 else main, '– ' + support.replace(' · ', '; ')]
    bullets(s, 0.6, 1.35, 8.9, 3.85, items, 12 if len(rows) > 1 else 13)
    notes(s, 'Main points.', ' '.join(f'{h}: {m} Supporting: {sup.replace(" · ", "; ")}.' for h, _, m, sup in rows))


def run_deck(script, section=None):
    """Append another deck's slides, marking its own title slide for removal."""
    at = len(prs.slides)
    if section:
        os.environ['SECTION'] = section
    try:
        runpy.run_path(os.path.join(HERE, script), run_name='__main__')
    except SystemExit:                                         # it stops before saving in append mode
        pass
    os.environ.pop('SECTION', None)
    ds.DROP = getattr(ds, 'DROP', [])
    ds.DROP.append(list(prs.slides._sldIdLst)[at])


def foundations():
    """The geometry and the two field models, for a part deck that must stand on its own."""
    run_deck('make_lim2002_na_deck.py', 'foundations')


def linfoot():
    s = slide('Linfoot’s criteria', 'How Lim & Saloma score a misaligned PSF against the aligned one.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        't: the aligned PSF; a: the PSF with O′ offset by (x_c, z_c); each scaled to its own peak; ⟨·⟩: mean over the window.',
        'Fidelity F = 1 − ⟨(t − a)^2⟩ / ⟨t^2⟩: 1 when a = t, falls as the shape departs.',
        'Structural content C = ⟨a^2⟩ / ⟨t^2⟩; correlation quality Q = ⟨t a⟩ / ⟨t^2⟩.',
        'The three are tied by F = 2Q − C; ε = 1 − F is the normalized mean-squared error.',
        'Lim & Saloma map F, C and Q over (x_c, z_c) in their Figs. 5–6; Part 3 follows how those maps change with NA.'], 13)
    notes(s, 'How Lim and Saloma score a misaligned PSF against the aligned one.',
          'Linfoot’s three criteria compare the misaligned point spread function a with the aligned one t, each normalized to '
          'its peak and averaged over the window. Fidelity is one minus the normalized mean-squared difference; structural '
          'content compares the energies; correlation quality is the normalized overlap. They obey F = 2Q − C.',
          r"""F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \quad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, \quad Q = \frac{\langle t\,a \rangle}{\langle t^2 \rangle}
F = 2Q - C, \qquad \epsilon = 1 - F""")


# ══ glossary: every term, with the parts that use it ═════════════════════
ALL = {1, 2, 3, 4, 5, 6}
GLOSSARY = [
    ('NA', 'numerical aperture, n sin α: how wide a cone of light the lens focuses', ALL),
    ('n', 'refractive index of the medium: air n = 1, water n = 1.33', ALL),
    ('α', 'half-angle of the focusing cone, sin α = NA/n', {2, 4, 5, 6}),
    ('L1, L2', 'the lenses focusing beam 1 and beam 2', ALL),
    ('O, O′', 'geometric foci of L1 and L2; O is the origin', ALL),
    ('x_c, z_c', 'position of O′ across and along the axis of L1', ALL),
    ('d', 'focus separation, (x_c^2 + z_c^2)^{1/2}', {1}),
    ('θ', 'angle between the axes of L1 and L2: π facing, π/2 crossed', ALL),
    ('λ_1, λ_2', '2CE wavelengths, 750 nm and 656 nm', ALL),
    ('λ_{2p}', '2PE wavelength, 700 nm, both beams', ALL),
    ('λ_e', 'single-photon equivalent, 1/λ_e = 1/λ_1 + 1/λ_2 (350 nm)', {1}),
    ('u, v', 'optical coordinates along and across the axis, paraxial model', {1, 2, 4}),
    ('ϑ, ρ, φ', 'ray angle; pupil radius over its edge; azimuth about the axis', {2, 4, 5}),
    ('2CE', 'two-color excitation: signal F_{2c} ∝ I_1 I_2', ALL),
    ('2PE', 'two-photon excitation: signal F_{2p} ∝ |U_1 + U_2|^4', ALL),
    ('PSF', 'point spread function: the signal from one point, scaled to its peak', ALL),
    ('Paraxial scalar model', 'Lim & Saloma’s focus: small-angle phase, no polarization', ALL),
    ('Scalar Debye', 'exact phase kz cos ϑ, no polarization', {2}),
    ('Vector model', 'Richards–Wolf focus: exact phase and polarization', ALL),
    ('Depth of focus', 'axial FWHM of the PSF', {2, 4, 6}),
    ('Lateral width', 'FWHM of the PSF across the axis', {2, 4, 5}),
    ('Peak loss', '1 − (misaligned peak)/(aligned peak), in percent', {1, 2, 4, 5}),
    ('20% tolerance', 'the offset x_c or z_c at which 20% of the peak is lost', {2, 4, 5}),
    ('Scalar–vector deviation', '|scalar/vector − 1| of a metric, in percent', {2, 3, 4, 5}),
    ('F, C, Q', 'Linfoot fidelity, structural content, correlation quality', {1, 3, 5}),
    ('ε', 'normalized mean-squared error, 1 − F', {1, 3}),
    ('x̃, z̃', 'offsets in spot units: x_c NA/λ across a beam, z_c NA^2/(nλ) along it', {3}),
    ('ΔF', 'F with the vector model minus F with the paraxial scalar model, same NA', {3}),
    ('F ≥ 0.8 region', 'offsets of O′ that keep F ≥ 0.8; half-widths and area give its shape', {3, 5}),
    ('α_t', 'truncation parameter of the Gaussian input; 0 is uniform', {2, 4}),
    ('A(ϑ)', 'pupil amplitude of the Gaussian input, exp(−α_t sin^2ϑ / sin^2α), both lenses', {2, 4}),
    ('Unpolarized', 'each beam averaged over two perpendicular input polarizations; equals circular', {2, 3, 4, 5}),
    ('ψ', 'input polarization angle about a beam’s own axis', {5}),
    ('s–s / p–p', 'both beams polarized perpendicular to / in the plane of the two lens axes', {5}),
    ('n sin(θ/2)', 'the largest NA at which two lenses at angle θ fit side by side', {2, 4, 5}),
    ('τ, Δt', 'pulse duration (intensity FWHM); delay of pulse 2 after pulse 1', {6}),
    ('Gate', 'where the two pulses overlap in time; FWHM c√2 τ/2n along z at θ = π', {6}),
]


def glossary(part_no=None):
    rows = [(t, m) for t, m, used in GLOSSARY if part_no is None or part_no in used]
    pages = [rows[i:i + 12] for i in range(0, len(rows), 12)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''),
                  'Every symbol and term in this deck.' if part_no else 'Every symbol and term in the report.')
        for i, (term, meaning) in enumerate(page):
            t = 1.35 + i * 0.315
            if i % 2 == 0:
                shape(s, MSO_SHAPE.RECTANGLE, 0.5, t, 9.0, 0.315, CARD)
            text(s, 0.65, t, 2.3, 0.315, term, 11.5, PURPLE, True, anchor=MSO_ANCHOR.MIDDLE)
            text(s, 3.0, t, 6.4, 0.315, meaning, 11, NAVY, anchor=MSO_ANCHOR.MIDDLE)
        notes(s, 'Glossary.', ' '.join(f'{t}: {m}.' for t, m in page))


# ══ title and summary ════════════════════════════════════════════════════
ds.CITE = ''                                                   # the paper is cited on the title slide only
SUMMARY = [   # (part, colour, main point, supporting points as short phrases)
    ('1. Replication', PURPLE, '2CE tolerates misalignment far better than 2PE, most of all with crossed beams (θ = π/2).',
     'lateral: 20% peak loss at x_c = 0.37 λ_1 (θ = π), only 11% at x_c = 1.33 λ_1 (θ = π/2); 2PE: 30% at 0.5 λ_{2p} · '
     'axial: 20% at z_c = 2.7 λ_1 (θ = π), 30% (θ = π/2) · all reproduced, 22 of 24 panels · '
     'paper errors: C and Q swapped, Eq. (2) rotation, Fig. 6(c)–(d) is θ = 0'),
    ('2. High NA', RED, 'The paraxial scalar model fails first on the depth of focus.',
     'deviation 5% at NA 0.45, 10% at 0.6 · lateral width holds to NA 0.8 · tolerances ∝ NA^{−0.97} lateral, NA^{−2.12} axial '
     '· follows NA/n (water)'),
    ('3. Fidelity', ORANGE, 'High NA reshapes the 2CE fidelity region; 2PE is set by its fringes.',
     '2CE F ≥ 0.8 area at NA 0.9: 17–26% below scalar · 2PE: 1–3%'),
    ('4. Gaussian input', NAVY, 'A Gaussian input (α_t = 4) extends the paraxial scalar model’s range.',
     'tolerances about 1.4× larger · deviation 5% at NA 0.525, 10% at 0.7 · same power laws'),
    ('5. Polarization', GREY, 'Polarization changes only lateral results and crossed-beam 2PE.',
     'unpolarized = circular · axial results unchanged · lateral spread up to ±20% at NA 0.9–1.2 · 2PE p–p: no interference'),
    ('Next', GREY, 'Pulses and a time delay.', 'signal = time overlap of the pulses · gated along z at θ = π'),
]
if PART is None:
    s = navy('Lim & Saloma (2002): replication, high NA and pulses', [
        ('Roland Albert A. Romero', 18, WHITE),
        ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
        ('Progress report on two-color excitation with misaligned foci', 13, PALE),
        ('M. Lim & C. Saloma, Opt. Commun. 207, 121–130 (2002)', 13, PALE)],
        chips=(('Replication', PURPLE), ('High NA', RED), ('Polarization', ORANGE)))
    notes(s, 'The paper rebuilt, its model tested against the vector model at high NA, and the choices that remain.',
          'This report collects the work on Lim and Saloma (2002). First the replication of the paper itself; then how far its '
          'scalar model carries as the numerical aperture grows; then the choices that remain.')
    summary(SUMMARY)

# ══ Part 1: replication ══════════════════════════════════════════════════
if WANT(1):
    part(1, 'replication', SUMMARY[0][2] + ' ' + SUMMARY[0][3].replace(' · ', '; ') + '.')
    run_deck('make_lim2002_replication_deck.py')

# ══ Part 2: high NA, uniform input ═══════════════════════════════════════
if WANT(2):
    part(2, 'high NA', SUMMARY[1][2] + ' Lim & Saloma’s metrics, vector model, NA 0.03 to 1.2, uniform input.')
    run_deck('make_lim2002_na_deck.py', 'high_na')

# ══ Part 3: fidelity against NA ══════════════════════════════════════════
if WANT(3):
    part(3, 'fidelity against NA', SUMMARY[2][2] + ' Linfoot F over the offset of O′, NA 0.1 to 1.2.')
    if PART:
        summary([SUMMARY[2]]); foundations()
    linfoot()
    run_deck('make_lim2002_na_deck.py', 'fidelity')

# ══ Part 4: Gaussian input ═══════════════════════════════════════════════
if WANT(4):
    part(4, 'Gaussian input, α_t = 4', SUMMARY[3][2] + ' The same study, Gaussian input on both lenses.')
    if PART:
        foundations()
    run_deck('make_lim2002_na_deck.py', 'gaussian')

# ══ Part 5: polarization, a decision ═════════════════════════════════════
LIM = FIG


def brow(suf, key, na):
    path = os.path.join(LIM, f'na_breakdown{suf}_{key}.csv')
    if not os.path.exists(path):
        return None
    a = np.loadtxt(path, delimiter=',', ndmin=2)
    r = a[np.isclose(a[:, 0], na)] if a.size else a
    return r[0] if len(r) else None


def qrow(suf, k, na):
    import glob
    rows_ = [np.loadtxt(f, delimiter=',', ndmin=2) for f in glob.glob(os.path.join(LIM, f'quoted_vs_na{suf}_m{k}*.csv'))]
    rows_ = [r for r in rows_ if r.size]
    if not rows_:
        return None
    a = np.concatenate(rows_)
    r = a[np.isclose(a[:, 0], na)]
    return r[0, 1] if len(r) else None




if WANT(5):
    part(5, 'a decision: polarization', SUMMARY[4][2] + ' To decide: unpolarized (circular) or fixed linear.')
    if PART:
        summary([SUMMARY[4]]); foundations()
    s = slide('Two options for the polarization of the beams', 'At low NA it does not matter; at high NA it changes the spot and the interference.')
    text(s, 0.5, 1.35, 4.35, 0.35, 'A: unpolarized (used so far for 2CE)', 13, PURPLE, True, 'Cambria')
    bullets(s, 0.5, 1.8, 4.35, 3.35, [
        'Each beam’s focus averaged over two perpendicular input polarizations.',
        'Exactly the intensity of circularly polarized input (checked to 10^{−16}): a quarter-wave plate in each beam.',
        'A round spot: results do not depend on the direction of the offset.',
        'The natural vector counterpart of Lim & Saloma’s scalar 2CE.'], 11.5)
    text(s, 5.1, 1.35, 4.4, 0.35, 'B: fixed linear polarization', 13, PURPLE, True, 'Cambria')
    bullets(s, 5.1, 1.8, 4.4, 3.35, [
        's–s: both along y, perpendicular to the plane of the two axes; the two fields stay parallel at any θ '
        '(used so far for 2PE).',
        'p–p: both in that plane; at θ = π/2 the two fields are perpendicular and do not interfere; at θ = π they are '
        'antiparallel, which only moves the fringes by half a period.',
        'The spot is wider along the polarization, so tolerances depend on the offset direction.',
        'Matches an instrument; doubles the results.'], 11.5)
    notes(s, 'At low NA it does not matter; at high NA it changes the spot and the interference.',
          'Option A averages over the input polarization; for the intensity of each beam this is exactly circular polarization, '
          'so it is a real experiment, and the natural vector counterpart of the scalar 2CE model. Option B fixes a linear '
          'polarization, as a laser does, with two natural choices: perpendicular to the plane of the two lens axes, s, or in it, p. '
          'We ran both B cases next to A on Lim and Saloma’s metrics.')

    pl = os.path.join(LIM, 'polarization_spot.png')
    if os.path.exists(pl):
        from mcdo.twobeam import beam_field, intensity
        xx = np.linspace(-1.2, 1.2, 481)
        fw = lambda na, psi: (lambda v: np.ptp(xx[v >= 0.5 * v.max()]))(intensity(beam_field(xx, 0 * xx, 0.750, na, model='rw', psi=psi)))
        r5, r9 = fw(0.5, 0.0) / fw(0.5, np.pi / 2), fw(0.9, 0.0) / fw(0.9, np.pi / 2)
        s = slide('Why polarization matters at high NA', f'The spot is wider along the polarization: {r5:.2f}× at NA 0.5, {r9:.2f}× at NA 0.9.')
        figure(s, pl, 0.45, 1.35, 9.1, 3.5)
        bullets(s, 0.6, 4.88, 8.9, 0.35, [
            'At high NA the focused field gains a component along the axis, strongest along the polarization, which widens the spot there.'], 11)
        notes(s, 'The focal spot is wider along the polarization at high NA.',
              'One beam at focus, profile across x. With the field along y, s, the profile across x is the narrow direction; with '
              'the field along x, p, it is the wide one. The unpolarized average sits between. This is why the tolerance along x_c '
              'depends on the polarization.')
    else:
        s = slide('Why polarization matters at high NA', 'Result still computing; this slide fills in when the report is rebuilt.')
        notes(s, 'Pending result.', 'From fig_lim2002_polarization.py.')

    pl = os.path.join(LIM, 'polarization_tolerances.png')
    rA, rS, rP = brow('', 'pi', 0.9), brow('_pols', 'pi', 0.9), brow('_polp', 'pi', 0.9)
    if os.path.exists(pl) and rS is not None and rP is not None:
        s = slide('2CE tolerances by polarization', f'θ = π, NA 0.9, along x_c: A {1000 * rA[3]:.0f} nm, s–s {1000 * rS[3]:.0f} nm, '
                  f'p–p {1000 * rP[3]:.0f} nm.')
        figure(s, pl, 0.45, 1.35, 9.1, 3.5)
        qA, qS, qP = brow('', 'pi2', 0.9), brow('_pols', 'pi2', 0.9), brow('_polp', 'pi2', 0.9)
        bullets(s, 0.6, 4.88, 8.9, 0.35, [
            f'Along z_c the three coincide; along x_c (θ = π) p–p is {rP[3] / rS[3]:.2f}× s–s at NA 0.9, unpolarized between.'], 11)
        notes(s, 'The polarization moves the tolerances across the axis, not along it.',
              'The twenty percent tolerances against NA for the three choices. Along the axis they coincide; across it the linear '
              'polarizations bracket the unpolarized result, with the tolerance wider along the polarization, since the spot is. '
              + (f'At theta = pi/2, NA 0.9, along x_c: unpolarized {1000 * qA[3]:.0f}, s–s {1000 * qS[3]:.0f}, p–p {1000 * qP[3]:.0f} nm.'
                 if qP is not None else ''))
    else:
        s = slide('2CE tolerances by polarization', 'Result still computing; this slide fills in when the report is rebuilt.')
        notes(s, 'Pending result.', 'From fig_lim2002_na_breakdown.py with POL = s and p.')

    pl = os.path.join(LIM, 'polarization_quoted.png')
    q3s, q3p = qrow('', 3, 0.5), qrow('_polp', 3, 0.5)
    if os.path.exists(pl) and q3p is not None:
        s = slide('Lim & Saloma’s quoted losses by polarization', f'2PE crossed beams at NA 0.5: {q3s:.0f}% lost for s–s, {q3p:.0f}% for p–p '
                  '(Lim & Saloma: 30%).')
        figure(s, pl, 0.45, 1.35, 9.1, 3.5)
        bullets(s, 0.6, 4.88, 8.9, 0.35, [
            f'2CE across the axis at NA 0.9: {qrow("_pols", 2, 0.9):.0f}% (s–s), {qrow("", 2, 0.9):.0f}% (unpolarized), '
            f'{qrow("_polp", 2, 0.9):.0f}% (p–p); along the axis identical. 2PE with p–p: no fringes to lose.'], 11)
        notes(s, 'The 2PE crossed-beam result depends entirely on the polarization.',
              'Quoted losses 1 and 5, both crossed beams, move by under 0.1% at NA 0.5 and are not shown. '
              'Lim and Saloma’s 2PE result therefore assumes, implicitly, fields that stay parallel: s–s. '
              'Three of Lim and Saloma’s quoted losses against NA for the three choices. For two-color excitation the choice moves the '
              'losses across the axis, by up to about twenty points at NA 0.9, and leaves the losses along the axis unchanged. For two-photon excitation with crossed beams it decides whether the beams interfere at '
              'all: with both polarizations in the plane the fields are perpendicular and the fringes vanish.')
    else:
        s = slide('Lim & Saloma’s quoted losses by polarization', 'Result still computing; this slide fills in when the report is rebuilt.')
        notes(s, 'Pending result.', 'From fig_lim2002_quoted_vs_na.py with POL = s and p.')

    # ── what polarization changes in Parts 2–4, one row per earlier result ──
    def fid_area(case, na, pol):
        """Area with F ≥ 0.8, vector over scalar, from a saved fidelity map (as in fig_lim2002_fidelity_na_plot.py)."""
        from scipy.interpolate import RectBivariateSpline
        from scipy.ndimage import label as lab_
        path = os.path.join(FIG, 'fidelity', f'{case}{pol}_na{na:.3f}_n1.npz')
        if not os.path.exists(path):
            return None
        d = np.load(path)
        xt, zt = d['xt'], d['zt']

        def area(M):
            f = RectBivariateSpline(zt, xt, M)(np.linspace(zt[0], zt[-1], 20 * len(zt)), np.linspace(xt[0], xt[-1], 20 * len(xt)))
            L, _ = lab_(f >= 0.8)
            c = L[L.shape[0] // 2, L.shape[1] // 2]
            return np.count_nonzero(L == c) if c else 0
        return area(d['F_vec']) / area(d['F_sca'])


    def pct(v, ref):
        return '—' if v is None or ref is None else f'{v:.3g} ({100 * (v / ref - 1):+.0f}%)'


    def tol(suf, key, na, col):
        r = brow(suf, key, na)
        return None if r is None else 1000 * r[col]


    TROWS = [
        ('2: tolerance θ = π, x_c, NA 0.9 (nm)', [tol(p_, 'pi', 0.9, 3) for p_ in ('', '_pols', '_polp')]),
        ('2: tolerance θ = π, z_c, NA 0.9 (nm)', [tol(p_, 'pi', 0.9, 4) for p_ in ('', '_pols', '_polp')]),
        ('2: tolerance θ = π/2, x_c, NA 0.9 (nm)', [tol(p_, 'pi2', 0.9, 3) for p_ in ('', '_pols', '_polp')]),
        ('2: quoted loss 2, NA 0.9 (%)', [qrow(p_, 2, 0.9) for p_ in ('', '_pols', '_polp')]),
        ('2: quoted loss 3 (2PE), NA 0.9 (%)', [None, qrow('', 3, 0.9), qrow('_polp', 3, 0.9)]),
        ('2: water, tolerance θ = π, x_c, NA 1.2 (nm)', [tol(p_, 'pi', 1.2, 3) for p_ in ('_n1.33', '_n1.33_pols', '_n1.33_polp')]),
        ('3: fidelity area / scalar, 2CE θ = π, NA 0.9', [fid_area('2ce_pi', 0.9, p_) for p_ in ('', '_pols', '_polp')]),
        ('3: fidelity area / scalar, 2CE θ = π/2, NA 0.9', [fid_area('2ce_pi2', 0.9, p_) for p_ in ('', '_pols', '_polp')]),
        ('3: fidelity area / scalar, 2PE θ = π/2, NA 0.9', [None, fid_area('2pe_pi2', 0.9, ''), fid_area('2pe_pi2', 0.9, '_polp')]),
        ('4: α_t = 4, tolerance θ = π, x_c, NA 0.9 (nm)', [tol(p_, 'pi', 0.9, 3) for p_ in ('_at4', '_at4_pols', '_at4_polp')]),
    ]
    s = slide('What polarization changes in Parts 2–4', 'Change against the unpolarized (circular) result; 2PE compares p–p with s–s.')
    for j, h in enumerate(('Result', 'A: unpolarized', 's–s', 'p–p')):
        text(s, (0.5, 4.6, 6.2, 7.8)[j], 1.3, (4.0, 1.5, 1.5, 1.7)[j], 0.28, h, 10.5, GREY, True)
    for i, (name, (va, vs, vp)) in enumerate(TROWS):
        ref = va if va is not None else vs                          # 2PE: s–s is the reference
        t = 1.62 + i * 0.335
        text(s, 0.5, t, 4.0, 0.3, name, 10, NAVY, True)
        text(s, 4.6, t, 1.5, 0.3, '—' if va is None else f'{va:.3g}', 10, NAVY)
        text(s, 6.2, t, 1.5, 0.3, pct(vs, ref) if va is not None else ('—' if vs is None else f'{vs:.3g}'), 10, NAVY)
        text(s, 7.8, t, 1.7, 0.3, pct(vp, ref), 10, NAVY)
    notes(s, 'Which earlier results move with the polarization, and by how much.',
          'One row per earlier result, at the highest NA of each part, where polarization matters most. Each linear choice is '
          'compared with the unpolarized result used so far, which is circular polarization. For two-photon excitation the '
          'comparison is p–p against s–s, the polarization used so far. A dash means the case does not exist or has not been run.')

    s = slide('The decision', 'Proposed: 2CE with circular (A) and 2PE with s–s as the main result; linear 2CE as bounds.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        '2CE: A is circular polarization, a real experiment with a round spot; the natural vector form of Lim & Saloma’s 2CE.',
        '2PE: s–s keeps the two fields parallel at any θ, which is what Lim & Saloma’s 2PE result implicitly assumes.',
        'That is the set used so far. Linear s–s and p–p for 2CE bracket it; p–p shows crossed-beam 2PE losing its fringes.',
        'Open physics: with fixed linear polarizations the dye’s transition dipole matters; for randomly oriented molecules the '
        'signal goes as (|E_1|^2|E_2|^2 + |E_1·E_2|^2 + |E_1·E_2^*|^2)/15, 3× larger for parallel fields than perpendicular.',
        'Question: keep A / s–s as the main result, or move to linear polarization and add the molecular factor?'], 12.5)
    notes(s, 'Proposed: 2CE with circular polarization and 2PE with s–s as the main result; linear 2CE as bounds.',
          'The decision to make. The unpolarized average we used for 2CE is exactly the intensity of circularly polarized beams, so '
          'it is physical, round, and the natural vector version of the paper’s scalar model. For 2PE the fields must be parallel to '
          'interfere, which is the s–s case. Linear polarizations for 2CE bracket the circular result. If linear polarization '
          'becomes the main case, the orientation of the dye’s transition dipole should enter the signal as well; the isotropic '
          'product I_1 I_2 assumes it does not matter.',
          r'\langle |\mathbf{E}_1\cdot\hat{d}|^2 |\mathbf{E}_2\cdot\hat{d}|^2 \rangle = \frac{|\mathbf{E}_1|^2|\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2^*|^2}{15}')


# ══ Part 6: next time, pulses ════════════════════════════════════════════
if WANT(6):
    part(6, 'next time: pulses and a time delay', 'What the pulsed model has to account for.')
    if PART:
        summary([SUMMARY[5]]); foundations()
    s = slide('The two-color signal with pulses', 'The signal is the time overlap of the two pulses, not a product of averages.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        'With pulses, the 2CE signal is the overlap in time of the two intensities at a delay Δt: F_{2c}(P, Δt) = ∫ I_1(P, t) I_2(P, t − Δt) dt.',
        'This is not the product of the two time-averaged intensities: each pulse is built in time from its spectrum, with phases, '
        'and travels through the focus at c/n.',
        'θ = π: the pulses meet head on, only within a gate of FWHM c√2 τ/2n along z, centred at z = cΔt/2n (4.2 µm for 20 fs).',
        'θ = π/2: the gate lies across the diagonal x − z and is c τ/n wide (6 µm for 20 fs), far wider than the crossed spot.',
        'Assumed: transform-limited Gaussian pulses, no lens dispersion, and the two colors kept separate as in Lim & Saloma '
        '(their spectra do not overlap for τ above about 8 fs).'], 12.5)
    notes(s, 'The signal is the time overlap of the two pulses, not a product of averages.',
          'With continuous beams the two-color signal is the product of the two intensities. With pulses it is their overlap in '
          'time, at a delay between them. Each pulse is built from its spectrum with the phases kept, so it travels through the '
          'focus at the speed of light in the medium. Facing pulses meet only within a short region along the axis, the gate; '
          'crossed pulses meet along a diagonal band much wider than the spot.',
          r"""F_{2c}(P,\Delta t) = \kappa \int I_1(P,t)\, I_2(P,t-\Delta t)\, dt
    \mathbf{E}(P,t) = \int a(\omega)\,\frac{\omega}{\omega_0}\,\mathbf{E}_\omega(P)\, e^{-i(\omega-\omega_0)t}\, d\omega, \quad a(\omega) = \exp\!\left[-\frac{(\omega-\omega_0)^2\tau^2}{8\ln 2}\right]
    \text{gate FWHM } (\theta=\pi) = \frac{c\sqrt{\tau_1^2+\tau_2^2}}{2n}, \quad z_{\text{centre}} = \frac{c\,\Delta t}{2n}""")

    s = slide('What the pulsed model has to account for', 'Each item changes the signal; together they set what to compute.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        'Where the pulses meet: the signal is a time overlap, so at θ = π it is gated along z (c√2 τ/2n), and a delay Δt moves the gate by cΔt/2n.',
        'The spectrum with its phases: each frequency focused on its own and summed coherently, sampled in ω, not λ, with the ω/ω_0 factor of the focal field.',
        'Separate colors: the 2CE term I_1 I_2 holds while the spectra do not overlap, τ above about 8 fs; shorter pulses make the colors interfere.',
        'The spread of spot sizes over the bandwidth: a few percent at 20 fs, negligible at 100 fs.',
        'Dispersion in the objective (chirp, and a delay between the pupil centre and edge): ignored so far, transform-limited pulses assumed.',
        'The dye: a flat absorption band and the I_1 I_2 term only, as in Lim & Saloma.'], 12)
    notes(s, 'Each item changes the signal; together they set what to compute.',
          'The points to settle before presenting pulsed results. The first is the new physics: the pulses overlap only in a gate. '
          'The others are what a correct calculation has to include or state as assumptions: coherent spectral summation, the '
          'separation of the two colors, the chromatic spread of the focus, dispersion in real objectives, and the dye’s absorption.')


if PART in (None, 5, 6):
    s = slide('Next steps', 'Two questions to discuss, then pulses.')
    bullets(s, 0.6, 1.45, 8.9, 3.75, [
        'Polarization of the two beams: which option to present as the main result (Part 5).',
        'Crossed beams above the lens-crossing limit, NA > n sin(θ/2): report as a computed trend, or stop at the limit.',
        'Pulses: settle the list above, then the misalignment tolerances and fidelity with pulses and a delay.'], 13)
    notes(s, 'Two questions to discuss, and the pulsed study to widen.',
          'Two questions for discussion: the polarization of the beams and the crossed geometry above the lens limit. Then pulses, '
          'starting from the list of what the model has to account for.')


glossary(PART)

if PART:                                                          # a part deck opens with its main points, then the background
    ids = prs.slides._sldIdLst
    for sl, el in list(zip(prs.slides, list(ids))):
        if el not in getattr(ds, 'DROP', []) and title_of(sl) in ('Summary', 'Main points', 'Gaussian input: main points'):
            ids.remove(el); ids.insert(1, el)
            break

# ══ remove the marked slides (sub-deck titles, other sections' slides), only now; renumber ══
for el in getattr(ds, 'DROP', []):
    prs.part.drop_rel(el.rId)
    prs.slides._sldIdLst.remove(el)
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
if PART is None:                                               # the full report audits every figure once
    # ── legibility audit: how large a figure's smallest (24-pt) text appears on the slide ──
    FLOOR = 11.0                                                   # pt on this 10-in slide; see LEGIBILITY below
    LEGIBILITY = '''Floor for the smallest figure text as seen on the slide: a character height of 16 arcmin (ISO 9241-3's
    minimum; 20–22 arcmin preferred) for a viewer 4 slide heights away. Cap height ≈ 0.7 em, slide height 5.625 in:
    p ≥ 0.7⁻¹ · 72 · 4 · 5.625 · tan(16′) ≈ 11 pt. Figure text keeps Bantang's 24 : 28 : 32 ratio above it.'''
    import csv
    from PIL import Image as _Im
    _Im.MAX_IMAGE_PIXELS = None
    audit = []
    for path, shown in ds.FIGURES:
        im = _Im.open(path)
        figw = im.size[0] / (im.info.get('dpi') or (600, 600))[0]
        audit.append((os.path.relpath(path, FIG), round(figw, 2), round(shown, 2), round(24 * shown / figw, 1)))
    with open(os.path.join(FIG, 'progress_report_legibility.csv'), 'w', newline='') as fh:
        w_ = csv.writer(fh)
        w_.writerow(['figure', 'figure_width_in', 'width_on_slide_in', 'smallest_text_on_slide_pt'])
        w_.writerows(sorted(set(audit), key=lambda r: r[3]))
    # Part 1 keeps the replication figures as first shown (paper-matched layouts, side by side with the paper's panels)
    EXEMPT = ('fig1_', 'fig2_', 'fig3_', 'fig4_', 'fig5_', 'fig6_', 'panels/', 'highna_', 'labeling_')
    checked = {r for r in audit if not os.path.basename(r[0]).startswith(EXEMPT) and not r[0].startswith(EXEMPT)}
    below = sorted({r for r in checked if r[3] < FLOOR}, key=lambda r: r[3])
    print(f'legibility: {len(below)} of {len(checked)} figure placements in Parts 2–5 below {FLOOR:g} pt on the slide'
          f' ({len(set(audit)) - len(checked)} replication placements exempt)')
    for r in below:
        print('   ', r)

# ── embed each figure at 600 dpi of its size on the slide (the figure files keep their own resolution) ──
import io
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
done = {}
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.shape_type != 13:                                 # pictures only
            continue
        ipart = sh.part.related_part(sh._element.blipFill.blip.rEmbed)
        if id(ipart) in done:
            continue
        im = Image.open(io.BytesIO(ipart.blob))
        w = int(round(600 * sh.width / 914400))
        if im.size[0] > 1.05 * w:
            im = im.convert('RGB').resize((w, int(round(w * im.size[1] / im.size[0]))), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', dpi=(600, 600), optimize=True)
            ipart._blob = buf.getvalue()
        done[id(ipart)] = True
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)

print('Saved ->', OUT, f'({len(prs.slides)} slides)')

if PART is None:                                                  # each part as a deck of its own, in a fresh process
    for k in range(1, 7):
        r = subprocess.run([sys.executable, __file__], env={**os.environ, 'PART': str(k)}, capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 else f'part {k} FAILED:\n{r.stderr[-2000:]}')
