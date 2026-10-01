r"""Progress report: Lim & Saloma (2002), from replication to high NA, with the choices that remain.

One deck in six parts, in the shared style (mcdo.deckstyle):

  Part 1  replication, as built by make_lim2002_replication_deck.py
  Part 2  high NA, uniform input: make_lim2002_na_deck.py with SECTION=uniform
  Part 3  fidelity against NA: the fidelity slides of that same run
  Part 4  Gaussian input, α_t = 4: make_lim2002_na_deck.py with SECTION=gaussian
  Part 5  polarization as a decision: unpolarized against s–s and p–p, from fig_lim2002_polarization.py
  Part 6  next time: pulses, what the model has to account for (theory only)

The existing decks run into the same presentation (DECK_APPEND=1 stops them
saving their own files); their title slides give way to section dividers.
Every number is read from the saved results, so a rerun updates the report.

    python scripts/make_lim2002_progress_deck.py
    -> ~/Downloads/Research/two_color/lim2002_progress_report.pptx (and a copy in ~/Downloads)
"""

import os
import runpy
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DECK_APPEND'] = '1'

import numpy as np

import mcdo.deckstyle as ds
from mcdo.deckstyle import (FIG, GREY, NAVY, ORANGE, PALE, PURPLE, RED, WHITE, MSO_ANCHOR, PP_ALIGN, bullets, chip,
                            dots, figure, notes, numbered, prs, slide, text)

OUT = os.path.expanduser('~/Downloads/Research/two_color/lim2002_progress_report.pptx')
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
    s = navy(f'Part {no}: {title}', [(what, 14, PALE)])
    notes(s, f'Part {no}: {title}.', what)


# ══ title and overview ═══════════════════════════════════════════════════
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002): progress report'
s = navy('Lim & Saloma (2002): replication, high NA and pulses', [
    ('Roland Albert A. Romero', 18, WHITE),
    ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
    ('Progress report on two-color excitation with misaligned foci', 13, PALE)],
    chips=(('Replication', PURPLE), ('High NA', RED), ('Polarization', ORANGE)))
notes(s, 'The paper rebuilt, its model tested against the vector model at high NA, and the choices that remain.',
      'This report collects the work on Lim and Saloma (2002). First the replication of the paper itself; then how far its '
      'scalar model carries as the numerical aperture grows; then what changes when the two beams are pulses with a delay.')

SUMMARY = [   # (part, colour, main point, supporting points as short phrases)
    ('1. Replication', PURPLE, 'Lim & Saloma (2002) reproduces.',
     'every number in Sec. 3.2 · 22 of 24 panels · C and Q swapped · Eq. (2) rotation wrong as printed · Fig. 6(c)–(d) is θ = 0'),
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
s = slide('Summary', 'One main point per part; supporting points beneath.')
for i, (head, col, main, support) in enumerate(SUMMARY):
    t = 1.3 + i * 0.64
    text(s, 0.5, t, 1.75, 0.3, head, 12, col, True)
    text(s, 2.3, t, 7.2, 0.3, main, 12.5, NAVY, True)
    text(s, 2.3, t + 0.29, 7.2, 0.3, support, 11, GREY)
notes(s, 'One main point per part.',
      ' '.join(f'{h}: {m} Supporting: {sup.replace(" · ", "; ")}.' for h, _, m, sup in SUMMARY))

# ══ Part 1: the replication deck ═════════════════════════════════════════
part(1, 'replication', SUMMARY[0][2] + ' ' + SUMMARY[0][3].replace(' · ', '; ') + '.')
at = len(prs.slides)
runpy.run_path(os.path.join(HERE, 'make_lim2002_replication_deck.py'), run_name='__main__')
ds.DROP = [list(prs.slides._sldIdLst)[at]]                      # its own title slide; removed at the end

# ══ Parts 2–3: the NA deck, uniform input (high NA, then fidelity) ═════════
part(2, 'high NA', SUMMARY[1][2] + ' Lim & Saloma’s metrics, vector model, NA 0.03 to 1.2, uniform input.')
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), at high NA'


def na_deck(section):
    """Append the NA deck's slides for one section and mark its own title slide for removal."""
    at = len(prs.slides)
    os.environ['SECTION'] = section
    try:
        runpy.run_path(os.path.join(HERE, 'make_lim2002_na_deck.py'), run_name='__main__')
    except SystemExit:                                         # it stops before saving in append mode
        pass
    ds.DROP.append(list(prs.slides._sldIdLst)[at])


na_deck('uniform')
first_fid = next(i for i, sl in enumerate(prs.slides) if title_of(sl).startswith('Fidelity against NA'))
part(3, 'fidelity against NA', SUMMARY[2][2] + ' Linfoot F over the offset of O′, NA 0.1 to 1.2.')
ids = prs.slides._sldIdLst
el = list(ids)[-1]                                             # move the divider in front of the fidelity slides
ids.remove(el)
ids.insert(first_fid, el)

# ══ Part 4: Gaussian input ═══════════════════════════════════════════════
part(4, 'Gaussian input, α_t = 4', SUMMARY[3][2] + ' The same study, Gaussian input on both lenses.')
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), at high NA, Gaussian input'
na_deck('gaussian')
del os.environ['SECTION']

# ══ decision: polarization ═══════════════════════════════════════════════
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), at high NA: polarization'
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


part(5, 'a decision: polarization', SUMMARY[4][2] + ' To decide: unpolarized (circular) or fixed linear.')
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

# ══ next time: pulses, what the model must account for ═══════════════════
part(6, 'next time: pulses and a time delay', 'What the pulsed model has to account for.')
ds.CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002), with pulses'

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

s = slide('Next steps', 'Two questions to discuss, then pulses.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'Polarization of the two beams: which option to present as the main result (Part 4).',
    'Crossed beams above the lens-crossing limit, NA > n sin(θ/2): report as a computed trend, or stop at the limit.',
    'Pulses: settle the list above, then the misalignment tolerances and fidelity with pulses and a delay.'], 13)
notes(s, 'Two questions to discuss, and the pulsed study to widen.',
      'Two questions for discussion: the polarization of the beams and the crossed geometry above the lens limit. Then pulses, '
      'starting from the list of what the model has to account for.')

# ══ remove the marked slides (sub-deck titles, other sections' slides), only now; renumber ══
for el in ds.DROP:
    prs.part.drop_rel(el.rId)
    prs.slides._sldIdLst.remove(el)
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
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
        part = sh.part.related_part(sh._element.blipFill.blip.rEmbed)
        if id(part) in done:
            continue
        im = Image.open(io.BytesIO(part.blob))
        w = int(round(600 * sh.width / 914400))
        if im.size[0] > 1.05 * w:
            im = im.convert('RGB').resize((w, int(round(w * im.size[1] / im.size[0]))), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', dpi=(600, 600), optimize=True)
            part._blob = buf.getvalue()
        done[id(part)] = True
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
shutil.copy(OUT, os.path.expanduser('~/Downloads'))

# ── one deck per part, cut from the full report: each starts at its divider and is renumbered ──
from pptx import Presentation as _Pres


def renumber(pres):
    for i, sl in enumerate(pres.slides, 1):
        for sh in sl.shapes:
            if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                    and sh.text_frame.text.strip().isdigit():
                sh.text_frame.paragraphs[0].runs[0].text = str(i)


full = _Pres(OUT)
titles = [title_of(sl) for sl in full.slides]
starts = [i for i, t in enumerate(titles) if t.startswith('Part ')]
NAMES = ['replication', 'high_na', 'fidelity', 'gaussian', 'polarization', 'pulses_next']
for k, (a_, b_) in enumerate(zip(starts, starts[1:] + [len(titles)])):
    part_ = _Pres(OUT)
    ids = list(part_.slides._sldIdLst)
    for i in reversed(range(len(ids))):
        if not a_ <= i < b_:
            part_.part.drop_rel(ids[i].rId)
            part_.slides._sldIdLst.remove(ids[i])
    renumber(part_)
    path = OUT.replace('.pptx', f'_part{k + 1}_{NAMES[k]}.pptx')
    part_.save(path)
    print(f'Saved -> {os.path.basename(path)} ({len(part_.slides)} slides)')
print('Saved ->', OUT, f'({len(prs.slides)} slides), copied to ~/Downloads')
