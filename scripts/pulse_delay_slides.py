r"""Slides of the delay between the two pulses, shared by make_pulse_delay_deck.py (the delay alone) and
make_2ce_decks.py (DECK=pulses, Part 2), so that the two decks carry the same titles, bullets and notes.

The results are written in the framework of Lim & Saloma (2002), who report the peak 2CE fluorescence against the
misalignment of the two foci at θ = 0, π/2 and π; here the misalignment is in time. Figures are those of
cambaliza2000_pulses_delay_plot.py; the numbers in the notes are read from the stored tables.

    from pulse_delay_slides import delay_slides, fitted
    delay_slides(slide, big, notes)        # slide(title, ''), big(title, items, fig, main, script), notes(s, main, script, latex)
"""
import os

import numpy as np
from PIL import ImageFont
from pptx.util import Inches, Pt

import cambaliza2000_pulses_delay as P
from mcdo.deckstyle import GREY, bullets, equation, text, where

F = P.ROOT
EQ_T = r'\frac{F(\Delta t)}{F(0)} = \exp\left(-2\ln 2\,\frac{\Delta t^2}{\tau^2}\right)'
EQ_M1 = r'\frac{F_{\mathrm{peak}}(\Delta t)}{F_{\mathrm{peak}}(0)} = \exp\left[-4\ln 2\,\frac{z_m^2}{D^2 + G^2}\right]'
EQ_M2 = r'z_m = \frac{c\,\Delta t}{2n}, \qquad G = \frac{c\,\tau}{\sqrt{2}\,n}'


def fitted(slide):
    """slide(title, takeaway) with the title set smaller when it is wider than its box at 24 pt, so that it stays on
    one line (the box is 8.6 in wide; Helvetica Neue Bold)."""
    def make(title, takeaway=''):
        s = slide(title, takeaway)
        try:
            w24 = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 100, index=1).getlength(title) * 24 / 7200
        except OSError:
            w24 = 0.157 * len(title)
        size = 24 if w24 <= 8.5 else max(18, int(24 * 8.5 / w24))
        if size != 24:
            for sh in s.shapes:
                if sh.has_text_frame and abs(sh.left - Inches(1.2)) < 2000 and abs(sh.top - Inches(0.28)) < 2000:
                    for par in sh.text_frame.paragraphs:
                        for r in par.runs:
                            r.font.size = Pt(size)
        return s
    return make


DASH = os.environ.get('DASHBOARD', 'http://localhost:4317/')     # the local dashboard (npm run dev in dashboard/cambaliza)
# slide title -> the highlight of the dashboard that shows the same result (dashboard/cambaliza/src/highlights.ts), or
# the address of the view when no highlight exists
LINKS = {
    'Two-color excitation with two confocal beams at an angle θ': '#mode=live',
    'Transverse 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π': '#mode=theta&wdir=x&pk=90',
    'Axial 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π': '#mode=theta&wdir=z&pk=90',
    'Central spot and depth of focus against NA: 2CE, θ = 0 and π': '#hl=cw-dof-collinear',
    'Axial 2CE PSF at NA 0.5 and NA 0.9: paraxial and vector focus': '#hl=cw-scalar-dof',
    'Paraxial over vector widths of 2CE against NA': '#hl=cw-scalar-5pct',
    'Central spot and depth of focus against NA: 2CE, θ = π/2': '#hl=cw-dof-crossed',
    'Central spot and depth of focus against NA: 2PE, θ = π/2': '#hl=cw-2pe-crossed',
    'Depth of focus, collinear and crossed lenses': '#hl=pulse-collinear',
    'Depth of focus, facing lenses': '#hl=pulse-facing-dof',
    'Overlap in time of the two facing pulses': '#hl=pulse-facing-dof',
    'Pulse width that matches continuous beams against NA, θ = π': '#hl=pulse-facing-na',
    'Pulse width that matches continuous beams, θ = 0 and π/2': '#hl=pulse-crossed',
    'Pulse width that matches continuous beams: pupils, θ = π': '#hl=pulse-facing-pupil',
    'Delay between the two pulses and their temporal overlap': '#hl=delay-collinear',
    'Peak 2CE fluorescence and its position against the delay, θ = π': '#hl=delay-facing-lowna',
    'Peak 2CE fluorescence at a delay of one pulse width against NA': '#hl=delay-pupils',
    'Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5': '#hl=delay-fringes',
    'Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5': '#hl=delay-fringes',
    'Peak 2CE fluorescence against the delay for two polarizations': '#hl=delay-polarization',
    '2CE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0 and π': '#hl=cw-scalar-dof',
    '2CE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2': '#hl=cw-dof-crossed',
    '2PE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2': '#hl=cw-2pe-crossed',
    '2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = π': '#hl=cw-2pe-facing',
    'Central spot and depth of focus against NA: 2PE, θ = π': '#hl=cw-2pe-facing',
    '2CE depth of focus against pulse width, facing lenses': '#hl=pulse-facing-na',
    '2CE depth of focus against NA, facing lenses': '#hl=pulse-facing-na',
    '2CE depth of focus against pulse width, collinear and crossed lenses': '#hl=pulse-crossed',
    '2CE along the axis with pulses at NA 0.5 and NA 0.9, facing lenses': '#hl=pulse-facing-dof',
}


def title_of(s):
    """Title of a white slide (the text box at 1.2 in, 0.28 in), or None for a title or divider slide."""
    for sh in s.shapes:
        if sh.has_text_frame and abs(sh.left - Inches(1.2)) < 2000 and abs(sh.top - Inches(0.28)) < 2000:
            return sh.text_frame.text
    return None


def finish(prs, keep=None):
    """Last pass over a deck: with `keep`, drop the white slides whose title is not in it and the divider slides;
    number the pages by their position in the deck; add the link to the dashboard under the slides that have one."""
    ids = prs.slides._sldIdLst
    if keep is not None:
        for i in reversed(range(len(prs.slides))):
            t = title_of(prs.slides[i])
            if (t is None and i > 0) or (t is not None and t not in keep):
                prs.part.drop_rel(ids[i].rId)
                ids.remove(ids[i])
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:                                  # the page number, written at (9.0 in, 5.28 in) by slide()
            if sh.has_text_frame and abs(sh.left - Inches(9.0)) < 2000 and abs(sh.top - Inches(5.28)) < 2000:
                sh.text_frame.paragraphs[0].runs[0].text = str(i)
        link = LINKS.get(title_of(s))
        if link:
            tf = text(s, 0.5, 5.45, 3.0, 0.16, 'Open in the dashboard', 8.5, GREY)   # under the figure frame
            tf.paragraphs[0].runs[0].hyperlink.address = DASH + link


def tolerance(q, level=0.8):
    """Delay, in units of τ, at which the peak of the 350-nm pairs has fallen to `level` of its value without delay."""
    q = q.sort_values('delay_tau')
    x, y = q.delay_tau.values, q.rel_cross.values
    below = np.nonzero(y < level)[0]
    if len(below) == 0:
        return np.nan
    i = below[0]
    return x[i - 1] + (y[i - 1] - level) / (y[i - 1] - y[i]) * (x[i] - x[i - 1])


def delay_slides(slide, big, notes):
    t = P.load('rw_air', 'coarse')
    f100 = t.query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100")
    face = f100[f100.delay_tau == 1].set_index('na')
    tol = {na: tolerance(f100[f100.na == na]) for na in (0.1, 0.2, 0.3, 0.5, 0.9)}
    tf = P.load('rw_air', 'fine')
    tf = tf[tf.sig == '2ce']
    gap = tf.assign(gap=(tf.rel_total - tf.rel_cross).abs()).groupby(['theta', 'cut', 'tau', 'na']).gap.max()
    lost = lambda na: 100 * (1 - face.loc[na, 'rel_cross'])

    s = slide('Delay between the two pulses and their temporal overlap', '')
    bullets(s, 0.5, 0.95, 9.0, 1.45, [
        '2CE needs the two pulses at the same place and at the same time: Lim & Saloma (2003) note that achieving '
        'optimal temporal overlap of the 2CE pulses is crucial.',
        'At a fixed point, the 2CE of the 350-nm pairs decreases with the delay Δt as the overlap in time of two '
        'Gaussian pulses of width τ.'], 13)
    h = equation(s, 1.5, 2.6, 7.0, EQ_T, 22)
    where(s, 1.5, 2.8 + h, 7.0, 'F is the peak 2CE fluorescence, Δt the delay of the 656-nm pulse relative to the 750-nm '
          'pulse and τ the pulse width. A delay of 0.40 τ reduces the peak by 20%, a delay of 0.71 τ by one half and a '
          'delay of τ by 75%.', 12)
    notes(s, 'A delay is a misalignment of the two pulses in time, and the temporal overlap sets how fast the peak 2CE '
          'fluorescence decreases with it at a fixed point.',
          'Lim & Saloma (2002) report the peak 2CE fluorescence against the misalignment of the two foci in space; here '
          'the misalignment is in time. Lim & Saloma (2003), Appl. Opt. 42(17), 3398–3406: "Achieving optimal temporal '
          'overlap of the 2CE pulses is crucial because spatio-temporal simultaneity of the two confocal beams is a '
          'necessary condition for 2CE." The fluorescence probes are chosen to minimize two-photon excitation by λ₁ or λ₂ '
          'alone, so the 350-nm pairs carry the 2CE signal. With collinear lenses the stored peaks follow this function '
          'to 1e-5 at 100 fs, at all NAs. The derivation is in docs/two_color/pulse_derivations.pdf, Section 6.', EQ_T)

    s = slide('Facing lenses: position where the delayed pulses meet', '')
    bullets(s, 0.5, 0.95, 9.0, 1.45, [
        'With facing lenses, the delayed pulses meet at z_m = cΔt/2n, and 2CE forms over a stretch of length '
        'G = cτ/(√2 n) about that position.',
        'With D the continuous-beam depth of focus of 2CE, the peak 2CE fluorescence at a delay Δt follows from the '
        'product of the focus and this stretch.'], 13)
    h = equation(s, 1.5, 2.45, 7.0, EQ_M1, 22)
    h += equation(s, 1.5, 2.65 + h, 7.0, EQ_M2, 22)
    where(s, 1.5, 2.9 + h, 7.0, 'z_m is the position where the delayed pulses meet and G the length of the stretch over '
          'which they overlap. A long focus (D much larger than G) retains the peak, which moves with z_m; a short focus '
          'holds the peak at the focus, where it decreases as the temporal overlap.', 12)
    notes(s, 'With facing lenses the delay moves the position where the pulses meet, and the peak follows from that '
          'position and the length of the focus.',
          'Comparison with the stored peaks at Δt = τ for 100-fs pulses in air (pulse_derivations.pdf, Section 7, Step 9), '
          'with G = 21.2 µm and z_m = 15.0 µm. The formula gives 0.928 at NA 0.1 compared to 0.930 stored, 0.518 at NA 0.2 '
          'compared to 0.513, 0.320 at NA 0.3 compared to 0.316, and 0.260 at NA 0.5 compared to 0.258. The formula takes D '
          'from the scalar model (3.56 µm at NA 0.5, growing as 1/NA²) and approximates the focus by a Gaussian; the stored '
          'peaks are those of the vector model.', EQ_M1 + '\n' + EQ_M2)

    big('Peak 2CE fluorescence and its position against the delay, θ = π', [
        'With facing lenses at low NA, the delayed pulses still meet inside the long depth of focus, so the peak 2CE '
        f'fluorescence moves along the axis and is largely retained: at NA 0.1 and 100 fs, a delay of one pulse width '
        f'reduces the peak by {lost(0.1):.0f}%.',
        'At NA 0.5 and above, the peak stays at the focus and decreases as the temporal overlap of the two pulses '
        f'(dotted line), by {lost(0.5):.0f}% at a delay of one pulse width.'],
        os.path.join(F, 'delay_facing_vs_na.png'),
        'With facing lenses, a delay moves the 2CE along the axis at low NA and reduces its peak at high NA.',
        'Facing lenses, along the axis, 350-nm pairs, 100-fs pulses. Two pulses that travel in opposite directions meet '
        'at z = cΔt/2 (dashed line, right). At a delay of one pulse width the peak is '
        f'{face.loc[0.1, "rel_cross"]:.2f} of its value without delay at NA 0.1, {face.loc[0.3, "rel_cross"]:.2f} at NA '
        f'0.3 and {face.loc[0.9, "rel_cross"]:.2f} at NA 0.9, and it has moved by {face.loc[0.1, "pos_cross"]:.1f}, '
        f'{face.loc[0.3, "pos_cross"]:.1f} and {face.loc[0.9, "pos_cross"]:.2f} µm. The delay that reduces the peak by 20% '
        f'is {tol[0.5]:.2f} τ at NA 0.5 and {tol[0.9]:.2f} τ at NA 0.9, the value of the temporal overlap, and it grows '
        f'to {tol[0.3]:.2f} τ at NA 0.3, {tol[0.2]:.2f} τ at NA 0.2 and {tol[0.1]:.2f} τ at NA 0.1. The 2CE profile along '
        'the axis is as long as the focus (FWHM 15 µm at NA 0.2, 3.3 µm at NA 0.5) or the stretch where the pulses meet '
        '(21 µm at 100 fs), whichever is shorter.')

    big('Peak 2CE fluorescence at a delay of one pulse width against NA', [
        'As NA increases, the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, '
        'the temporal overlap of the two pulses; shorter pulses retain more, because the position where they meet '
        'moves by a shorter distance (left).',
        'A Gaussian input and annular pupils, which give a longer depth of focus, retain more of the peak at the same '
        'NA (right).'],
        os.path.join(F, 'delay_retained_vs_na.png'),
        'The peak that remains depends on the depth of focus compared with the distance cτ/2.',
        'Facing lenses, along the axis, 350-nm pairs, delay Δt = τ. The dashed line is the temporal overlap, 0.25. Left: '
        'circular pupil and uniform input at 30, 50 and 100 fs. Right: pupils and inputs at 100 fs; at NA 0.3 the peak '
        'that remains is 0.32 for the circular pupil, 0.38 for the Gaussian input (α = 4) and 0.80 for the annular pupil '
        'with ε = 0.9. Cambaliza & Saloma (2000) propose annular lenses, with their long depth of field, to keep the two '
        'beams aligned in space; the same holds here for their alignment in time.')

    for tau in (5, 10, 20):
        first = ('At 20 fs, the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the '
                 'total 2CE follows the 2CE of the 350-nm pairs.' if tau == 20 else
                 'With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with '
                 'periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to '
                 'the 375- and 328-nm pairs.')
        second = ('The peak decreases smoothly with the delay, as the temporal overlap of the two pulses.' if tau == 20
                  else 'The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of '
                  'the two pulses.')
        big(f'Peak 2CE fluorescence against the delay, τ = {tau} fs, NA 0.5', [first, second],
            os.path.join(F, f'delay_fringes_{tau}fs.png'),
            'With short phase-locked pulses the peak oscillates with the delay.',
            'Delay in steps of 0.1 fs; collinear lenses (left) and crossed lenses (right). The fringes are 2.19 fs apart '
            'for the 350-nm pairs with the 375-nm pairs (the period of 656 nm), 2.50 fs for the 350-nm pairs with the '
            '328-nm pairs (the period of 750 nm), and 1.17 fs for the 375-nm pairs with the 328-nm pairs (the period of '
            '350 nm). The 375-nm pairs (750 + 750 nm) and the 328-nm pairs (656 + 656 nm) reach the 350-nm level through '
            'the edges of the pulse spectra below about 20 fs. With two lasers that are not phase-locked the fringes '
            f'average out. Largest difference between the two curves at NA 0.5: θ = 0, {gap.loc[("0", "z", tau, 0.5)]:.2f}; '
            f'θ = π/2, {gap.loc[("pi2", "x", tau, 0.5)]:.2f}; θ = π, {gap.loc[("pi", "z", tau, 0.5)]:.2f}.')

    big('Fringe depth of the 2CE peak against NA, τ = 5, 10 and 20 fs', [
        'With crossed and facing lenses, the fringes of the peak against the delay deepen as NA increases, because the '
        'delay moves the interference fringes in space across a smaller focal spot.',
        'With collinear lenses, the three kinds of photon pairs have no fringes in space, so the fringe depth is the '
        'same at all NAs: 0.92 at 5 fs and 0.71 at 10 fs.'],
        os.path.join(F, 'delay_fringe_depth_vs_na.png'),
        'The fringes against the delay deepen with NA for crossed and facing lenses.',
        'The fringe depth is the largest difference between the peak with all pairs and the peak with the 350-nm pairs '
        'alone, each relative to its value without delay. With crossed and facing lenses the delay moves the '
        'interference fringes in space; a focal spot at high NA is about one fringe wide, so the peak follows the '
        'fringes. At 20 fs the depth is at most 0.04. With crossed lenses the peak is taken along the x axis through '
        'the focus; over the whole x–z plane the depth is about two thirds of this (0.28 compared to 0.42 at NA 0.5 and '
        '5 fs).')

    big('Peak 2CE fluorescence against the delay for two polarizations', [
        'With the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the '
        'focus, so the three kinds of photon pairs fall in different field components and interfere less.',
        'The fringes against the delay are then about a quarter as deep, while the 2CE of the 350-nm pairs decreases '
        'with the delay in the same way for both polarizations.'],
        os.path.join(F, 'delay_polarization_pi2.png'),
        'With crossed lenses, the polarization in the plane of the lens axes makes the fringes against the delay shallow.',
        'Crossed lenses (θ = π/2), along x through the focus, NA 0.5, 5-fs pulses, delay in steps of 0.1 fs. Each panel '
        'is relative to its own total at no delay. Left: both beams polarized perpendicular to the plane of the lens '
        'axes; right: both polarized in that plane. The amplitude of the oscillating part (half its swing, after a 5-fs '
        'smooth is subtracted) is about 0.05 compared to 0.21, and the 2CE spot is 0.83 µm compared to 0.75 µm. The '
        'fringes are not absent, because the longitudinal field away from the focus mixes the components. For real '
        'molecules the absorption of two photons with perpendicular polarizations differs from that of parallel ones '
        'by a factor that depends on the molecule, which the model does not include.')
