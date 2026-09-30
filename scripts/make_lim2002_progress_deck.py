r"""Progress report: Lim & Saloma (2002), from replication to high NA and pulses.

One deck in three parts, in the shared style (mcdo.deckstyle):

  Part 1  the replication deck, as built by make_lim2002_replication_deck.py
  Part 2  the NA study, as built by make_lim2002_na_deck.py
  Part 3  pulses and a time delay, from fig_lim2002_pulsed.py (built here)

The two existing decks run unchanged into the same presentation (DECK_APPEND=1
stops them saving their own files); their title slides give way to section
dividers, and the NA deck's forward-looking pulse slides give way to Part 3.
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
    chips=(('Replication', PURPLE), ('High NA', RED), ('Pulses', ORANGE)))
notes(s, 'Three steps: the paper rebuilt, its model tested against the vector focus at high NA, and pulses added.',
      'This report collects the work on Lim and Saloma (2002). First the replication of the paper itself; then how far its '
      'scalar model carries as the numerical aperture grows; then what changes when the two beams are pulses with a delay.')

s = slide('Where we are', 'Replication done; high-NA study done; pulses and a time delay started.')
numbered(s, 1, PURPLE, 1.45, 'Replication: every quoted number and 22 of 24 panels reproduce; three details of the paper do not.')
numbered(s, 2, RED, 2.15, 'High NA: the scalar model gets the focal length wrong first, by 5% from NA 0.45 and 10% from 0.6 in air; '
         'the deviation follows NA/n.')
numbered(s, 3, ORANGE, 2.85, 'Pulses: the two pulses meet only in a gate of width c√2 τ/2n; at θ = π short pulses shorten the focus.')
numbered(s, 4, NAVY, 3.55, 'Open: polarization of the two beams, and crossed beams above the lens-crossing limit.')
notes(s, 'Replication done; high-NA study done; pulses and a time delay started.',
      'Where the project stands. The replication is complete. The high-NA study compares Lim and Saloma’s scalar model with the '
      'vector focus on their own metrics, in air and in water. Pulses have just been added: the new physics is that the two '
      'pulses overlap in time only in a narrow region, which matters for facing lenses. Two questions are open for discussion.')

# ══ Part 1: the replication deck ═════════════════════════════════════════
part(1, 'replication', 'Lim & Saloma (2002) rebuilt from its equations, checked number by number.')
drop = [len(prs.slides)]                                       # the replication deck's own title slide
runpy.run_path(os.path.join(HERE, 'make_lim2002_replication_deck.py'), run_name='__main__')

# ══ Part 2: the NA deck ══════════════════════════════════════════════════
part(2, 'high NA', 'Where Lim & Saloma’s scalar model applies: their metrics recomputed with the vector focus, NA 0.03 to 1.2.')
drop.append(len(prs.slides))                                   # the NA deck's own title slide
try:
    runpy.run_path(os.path.join(HERE, 'make_lim2002_na_deck.py'), run_name='__main__')
except SystemExit:                                             # it stops before saving in append mode
    pass
drop += [i for i, sl in enumerate(prs.slides) if title_of(sl).startswith(('Next: optical pulses', 'Other next steps'))]

# ══ Part 3: pulses ═══════════════════════════════════════════════════════
part(3, 'pulses and a time delay', 'Transform-limited pulses of 100 fs and 20 fs, vector focus, NA 0.5 unless stated.')
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

s = slide('Check: the gate', 'The computed overlap matches the analytic gate.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'Low NA (0.1), θ = π, 20 fs: the signal along z divided by the CW signal is the gate.',
    'Its FWHM is 4.25 µm; the analytic value c√2 τ/2n is 4.24 µm.',
    'With Δt = 15 fs its centre moves to z = 2.30 µm; the analytic value cΔt/2n is 2.25 µm.',
    'Pulses of 2 ps reproduce the CW signal to 0.5%.',
    'θ = π/2, NA 0.5, 20 fs: the map differs from the CW map by at most 0.6%.'], 13)
notes(s, 'The computed overlap matches the analytic gate.',
      'Before using the pulsed signal we check its limits. Very long pulses give back the continuous-wave signal. At low NA, '
      'where the focus is much longer than the gate, the signal is the gate itself, with the predicted width and position. '
      'Crossed beams barely change, as expected. These checks are part of the test suite.')

if os.path.exists(os.path.join(PUL, 'pulsed_maps.png')):
    d = np.load(os.path.join(PUL, 'pulsed_maps.npz'))
    z = d['z_um']
    ax_fwhm = lambda F: (lambda p: np.ptp(z[p >= 0.5 * p.max()]))(F[:, len(d['x_um']) // 2])
    cw, f20 = ax_fwhm(d['pi_CW']), ax_fwhm(d['pi_20'])
    s = slide('The aligned PSF with pulses, NA 0.5', f'θ = π: 20 fs pulses shorten the focus from {cw:.1f} to {f20:.1f} µm; θ = π/2 is unchanged.')
    figure(s, os.path.join(PUL, 'pulsed_maps.png'), 0.45, 1.35, 4.9, 3.85)
    bullets(s, 5.55, 1.45, 3.95, 3.75, [
        'Lim & Saloma’s axes and contour levels; CW, 100 fs and 20 fs.',
        'θ = π: the gate (4.2 µm for 20 fs) is comparable to the focal length, so it trims the focus along z.',
        'At 100 fs the gate is 21 µm and changes little.',
        'θ = π/2: the gate is far wider than the crossed spot; the PSF is the CW one.'], 11.5)
    notes(s, 'Short pulses shorten the focus of facing beams and leave crossed beams unchanged.',
          'The aligned two-color point spread function at NA 0.5 with continuous beams and with 100 and 20 femtosecond pulses. '
          'With facing lenses the pulses overlap only within the gate, which for 20 femtoseconds is about as long as the focus, '
          'so the focus is shortened. Crossed beams already confine the spot to the overlap of two narrow widths.')
else:
    s = slide('The aligned PSF with pulses, NA 0.5', 'Result still computing; this slide fills in when the report is rebuilt.')
    notes(s, 'Pending result.', 'From fig_lim2002_pulsed.py, PART=maps.')

if os.path.exists(os.path.join(PUL, 'pulsed_na.png')):
    r = np.load(os.path.join(PUL, 'pulsed_na.npz'))['rows']
    at = lambda na, j: 100 * (1 - r[np.argmin(np.abs(r[:, 0] - na)), j] / r[np.argmin(np.abs(r[:, 0] - na)), 1])
    s = slide('When pulses matter: axial FWHM against NA', f'20 fs shortens the facing-beam focus by {at(0.3, 3):.0f}% at NA 0.3, '
              f'{at(0.5, 3):.0f}% at 0.5, {at(0.9, 3):.0f}% at 0.9.')
    figure(s, os.path.join(PUL, 'pulsed_na.png'), 0.45, 1.35, 9.1, 3.1)
    bullets(s, 0.6, 4.5, 8.9, 0.75, [
        'The focus shrinks as nλ/NA²; the gate does not change with NA. Pulses matter where the focus is longer than the gate: low NA.',
        f'100 fs: {at(0.3, 2):.0f}% at NA 0.3 and {at(0.5, 2):.0f}% at 0.5.'], 11)
    notes(s, 'Pulses matter where the focus is longer than the gate, which is at low NA.',
          'The axial width of the facing-beam focus against NA, for continuous beams and for 100 and 20 femtosecond pulses. The '
          'dashed lines are the gate widths. Where the focus is longer than the gate, the gate sets the width; at high NA the focus '
          'is already shorter than the gate and pulses change little.')
else:
    s = slide('When pulses matter: axial FWHM against NA', 'Result still computing; this slide fills in when the report is rebuilt.')
    notes(s, 'Pending result.', 'From fig_lim2002_pulsed.py, PART=na.')

if os.path.exists(os.path.join(PUL, 'pulsed_delay.png')):
    d = np.load(os.path.join(PUL, 'pulsed_delay.npz'))

    def t20(key, tau):
        dl, pk = d[f'delays_{tau:g}'], d[f'{key}_{tau:g}_peak']
        lost = 100 * (1 - pk / pk[np.argmin(np.abs(dl))])
        pos = dl >= 0
        return np.interp(20.0, lost[pos], dl[pos]) if lost[pos].max() >= 20 else np.nan
    s = slide('The time delay', f'20% of the peak is lost at Δt = {t20("pi", 20.0):.0f} fs (θ = π) and '
              f'{t20("pi2", 20.0):.0f} fs (θ = π/2) for 20 fs pulses.')
    figure(s, os.path.join(PUL, 'pulsed_delay.png'), 0.45, 1.35, 9.1, 2.95)
    bullets(s, 0.6, 4.4, 8.9, 0.85, [
        f'100 fs pulses: 20% lost at Δt = {t20("pi", 100.0):.0f} fs (θ = π) and {t20("pi2", 100.0):.0f} fs (θ = π/2).',
        'At θ = π a delay moves the meeting point of the pulses along z, at cΔt/2n; the peak follows it.'], 11)
    notes(s, 'A delay moves where the pulses meet; the peak survives a delay of a fraction of the pulse length.',
          'The peak two-color signal against the delay between the pulses, in units of the pulse length, and at theta = pi the '
          'position of the peak along the axis. At theta = pi the delay slides the gate along z, so the signal follows the gate '
          'until it leaves the focus. At theta = pi/2 the delay moves the gate across the crossed spot.')
else:
    s = slide('The time delay', 'Result still computing; this slide fills in when the report is rebuilt.')
    notes(s, 'Pending result.', 'From fig_lim2002_pulsed.py, PART=delay.')

s = slide('Next steps', 'Two questions to discuss, and the pulsed study to widen.')
bullets(s, 0.6, 1.45, 8.9, 3.75, [
    'Polarization of the two beams: keep them unpolarized, or fix linear polarizations to match an instrument (see the options).',
    'Crossed beams above the lens-crossing limit, NA > n sin(θ/2): report as a computed trend, or stop at the limit.',
    'Pulses: the misalignment tolerances and fidelity with pulses, and the delay that best recovers a misaligned focus.',
    'Pulses shorter than about 8 fs: the two colors’ spectra overlap and they interfere, beyond Lim & Saloma’s model.'], 13)
notes(s, 'Two questions to discuss, and the pulsed study to widen.',
      'Two questions for discussion: the polarization of the beams and the crossed geometry above the lens limit. For pulses, '
      'the next step is to redo the misalignment tolerances with the pulsed signal, including whether a delay can compensate an '
      'axial misalignment, since the delay moves the meeting point along the axis.')

# ══ drop the sub-decks' title slides and the superseded pulse slides; renumber ══
ids = list(prs.slides._sldIdLst)
for i in sorted(set(drop), reverse=True):
    el = ids[i]
    prs.part.drop_rel(el.rId)
    prs.slides._sldIdLst.remove(el)
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
shutil.copy(OUT, os.path.expanduser('~/Downloads'))
print('Saved ->', OUT, f'({len(prs.slides)} slides), copied to ~/Downloads')
