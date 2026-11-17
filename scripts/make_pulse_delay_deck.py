r"""Backup deck of the delay between the two pulses, against NA, pulse width and pupil (Richards–Wolf, air), from
cambaliza2000_pulses_delay_plot.py; numbers in the speaker notes. pulse_results.pptx is left as it is.

    python scripts/make_pulse_delay_deck.py -> output/08_two_color/cambaliza2000/deck/pulse_delay.pptx
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mcdo.deckstyle as ds
from mcdo.deckstyle import prs, slide, text, bullets, figure, dots, equation, where, NAVY, WHITE, PALE
from PIL import Image

import cambaliza2000_pulses_delay as P

ds.CITE = ''
ROOT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
F = os.path.join(ROOT, 'pulses', 'delay_sweep')
OUT = os.path.join(ROOT, 'deck')
os.makedirs(OUT, exist_ok=True)


def notes(s, main, script, latex=None):
    body = f'{main}\n\n{script}'
    if latex:
        body += '\n\nThe equation in LaTeX is\n' + '\n'.join(l.strip() for l in latex.strip().splitlines())
    s.notes_slide.notes_text_frame.text = body


def navy(title, lines):
    s = prs.slides.add_slide(ds.BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    dots(s, 0.6, 0.7, 0.2, 0.27)
    text(s, 0.6, 1.15, 8.8, 1.5, title, 30, WHITE, True, 'Helvetica Neue')
    for i, (line, size, col) in enumerate(lines):
        text(s, 0.6, 2.85 + i * 0.4, 8.8, 0.4, line, size, col)
    return s


def big(title, items, fig, main, script):
    """One or two one-line bullets and the figure across the full width of the slide."""
    s = slide(title, '')
    hb = sum(0.27 * -(-len(it) // 100) + 0.1 for it in items)          # about 100 characters per line at 13 pt
    bullets(s, 0.5, 0.86, 9.0, hb, items, 13)
    top = 0.9 + hb
    iw, ih = Image.open(fig).size
    h = 5.45 - top - 0.1                                            # down to the lower edge when the figure ends left
    if iw / ih * h + 0.1 > 7.9:                                     # of the page number, else above it
        h = min(5.22 - top - 0.1, 9.6 * ih / iw)
    figure(s, fig, 0.15, top, 9.7, h + 0.1)
    notes(s, main, script)
    return s


t = P.load('rw_air', 'coarse')
face = t.query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100 and delay_tau == 1").set_index('na')
tf = P.load('rw_air', 'fine')
gap = tf.assign(gap=(tf.rel_total - tf.rel_cross).abs()).groupby(['theta', 'cut', 'tau', 'na']).gap.max()

s = navy('Delay between the two pulses', [('Roland Albert A. Romero', 18, WHITE),
         ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
         ('Extension of Cambaliza & Saloma (2000) to optical pulses', 13, PALE)])
notes(s, 'Backup on the delay between the 750-nm and 656-nm pulses.',
      'All results are for the Richards–Wolf model in air unless a slide says otherwise; the same quantities for the '
      'scalar model, water, oil, Gaussian input and annular pupils are in the data files of the delay results.')

s = slide('Summary: delay between the pulses', '')
bullets(s, 0.5, 0.95, 9.0, 4.2, [
    'Delayed the 656-nm pulse against the 750-nm pulse by up to twice the pulse width, for collinear, crossed and '
    'facing lenses from NA 0.1 to 0.95.',
    'Found that with facing lenses at low NA the delayed pulses still meet inside the long depth of focus, so the 2CE '
    'peak moves along the axis and most of it is kept.',
    'Found that at high NA, and with collinear and crossed lenses, the 2CE peak falls with the temporal overlap of the '
    'two pulses, to a quarter at a delay of one pulse width.',
    'Found that below about 20 fs, phase-locked pulses with all photon pairs give fringes in the peak against the delay, '
    'one optical period apart; the 350-nm pairs alone fall smoothly.',
    'Derived the 2CE peak with facing lenses from the point where the delayed pulses meet, which agrees with the '
    'computed peaks to within 0.01.',
    'Found that with crossed lenses and the polarization in the plane of the lens axes, the fringes against the delay '
    'are about a quarter as deep, because the two fields are perpendicular at the focus.'], 14)
notes(s, 'A delay weakens 2CE through the temporal overlap, except where facing lenses have a long depth of focus.',
      f'With facing lenses and 100-fs pulses, the peak at a delay of one pulse width is {face.loc[0.1, "rel_cross"]:.2f} '
      f'of the peak without delay at NA 0.1, {face.loc[0.2, "rel_cross"]:.2f} at NA 0.2 and '
      f'{face.loc[0.9, "rel_cross"]:.2f} at NA 0.9.')

s = slide('Delay and temporal overlap', '')
bullets(s, 0.5, 0.95, 9.0, 1.3, [
    'Lim & Saloma (2003) note that 2CE needs the two pulses at the same place and time.',
    'At a fixed point, the 350-nm pairs fall with the overlap of two Gaussian pulses of width τ.'], 14)
h = equation(s, 1.5, 2.5, 7.0, r'\frac{F(\Delta t)}{F(0)} = \exp\left(-2\ln 2\,\frac{\Delta t^2}{\tau^2}\right)', 22)
where(s, 1.5, 2.7 + h, 7.0, 'F is the 2CE peak, Δt the delay of the 656-nm pulse and τ the FWHM of the pulse intensity. '
      'The peak halves at Δt = 0.71 τ and falls to a quarter at Δt = τ.', 12)
notes(s, 'The temporal overlap sets how fast 2CE falls with the delay at a fixed point.',
      'Lim & Saloma (2003), Appl. Opt. 42(17), 3398–3406: "Achieving optimal temporal overlap of the 2CE pulses is crucial because '
      'spatio-temporal simultaneity of the two confocal beams is a necessary condition for 2CE." The fluorescence probes '
      'are chosen to minimize two-photon excitation by λ₁ or λ₂ alone, so the 350-nm pairs carry the 2CE signal.',
      r'\frac{F(\Delta t)}{F(0)} = \exp\left(-2\ln 2\,\frac{\Delta t^2}{\tau^2}\right)')


FM1 = r'\frac{F_{\mathrm{peak}}(\Delta t)}{F_{\mathrm{peak}}(0)} = \exp\left[-4\ln 2\,\frac{z_m^2}{D^2 + G^2}\right]'
FM2 = r'z_m = \frac{c\,\Delta t}{2n}, \qquad G = \frac{c\,\tau}{\sqrt{2}\,n}'
s = slide('Facing lenses: where the pulses meet', '')
bullets(s, 0.5, 0.95, 9.0, 0.5, [
    'The delayed pulses meet at z_m, and the 2CE forms over a stretch of length G about it.'], 14)
h = equation(s, 1.5, 1.75, 7.0, FM1, 22)
h += equation(s, 1.5, 1.95 + h, 7.0, FM2, 22)
where(s, 1.5, 2.2 + h, 7.0, 'F_{peak} is the 2CE peak, Δt the delay of the 656-nm pulse, τ the FWHM of the pulse intensity, '
      'n the refractive index, c the speed of light and D the continuous-beam depth of focus of 2CE.', 12)
notes(s, 'With facing lenses the delay moves the place where the pulses meet, and the peak follows the formula.',
      'Comparison with the stored peaks at Δt = τ for 100-fs pulses in air (pulse_derivations.pdf, Section 7, Step 9), '
      'with G = 21.2 µm and z_m = 15.0 µm. The formula gives 0.928 at NA 0.1 against 0.930 stored, 0.518 at NA 0.2 '
      'against 0.513, 0.320 at NA 0.3 against 0.316, and 0.260 at NA 0.5 against 0.258. The table takes D from the '
      'scalar model (3.56 µm at NA 0.5, growing as 1/NA²), and the stored peaks are those of the vector model. When D '
      'is much longer than G (low NA), the peak moves to z_m and is kept; when D is much shorter (high NA), the formula '
      'becomes the temporal overlap exp(−2 ln2 Δt²/τ²).',
      FM1 + '\n' + FM2)

big('2CE peak and position against the delay, θ = π, 100 fs', [
    'At low NA the pulses still meet inside the long focus, so the peak moves along the axis.',
    'At NA 0.5 and above, the peak stays at the focus and falls with the temporal overlap.'],
    os.path.join(F, 'delay_facing_vs_na.png'), 'With facing lenses, a delay moves the 2CE along the axis at low NA and weakens it at high NA.',
    'Facing lenses, along the axis, 350-nm pairs. At low NA the depth of focus is longer than the distance cΔt/2, so the '
    'pulses meet inside the focus. Two counter-propagating pulses meet at z = cΔt/2 (dashed line, right). The 2CE profile along the axis is as long as the focus (FWHM 15 µm at NA 0.2, 3.3 µm at NA 0.5) or the stretch where the pulses meet (21 µm at 100 fs), whichever is shorter. '
    f'At a delay of one pulse width the peak is {face.loc[0.1, "rel_cross"]:.2f} of its value without delay at NA 0.1, '
    f'{face.loc[0.3, "rel_cross"]:.2f} at NA 0.3 and {face.loc[0.9, "rel_cross"]:.2f} at NA 0.9; the peak has moved by '
    f'{face.loc[0.1, "pos_cross"]:.1f}, {face.loc[0.3, "pos_cross"]:.1f} and {face.loc[0.9, "pos_cross"]:.2f} µm.')

big('2CE peak at a delay of τ against NA, θ = π', [
    'Shorter pulses keep more of the peak, since they travel a shorter distance during the delay.',
    'Pupils with a longer depth of focus keep more of the peak at the same NA.'],
    os.path.join(F, 'delay_retained_vs_na.png'), 'The kept peak depends on the depth of focus compared with the distance cτ/2.',
    'Facing lenses, along the axis, 350-nm pairs, delay Δt = τ. The dashed line is the temporal overlap, 0.25. Left: '
    'circular pupil and uniform input at 30, 50 and 100 fs. Right: pupils and inputs at 100 fs.')

for tau in (5, 10, 20):
    if os.path.exists(os.path.join(F, f'delay_fringes_{tau}fs.png')):
        first = ('At 20 fs the fringes are shallow, and all pairs follow the 350-nm pairs.' if tau == 20 else
                 'Phase-locked pulses with all pairs give fringes one optical period (2.2 to 2.5 fs) apart.')
        big(f'2CE peak against the delay, {tau} fs, NA 0.5', [
            first, 'The 350-nm pairs alone fall smoothly; with facing lenses the two curves nearly coincide.'],
            os.path.join(F, f'delay_fringes_{tau}fs.png'), 'Short phase-locked pulses give fringes against the delay.',
            'Fine grid of 0.1 fs. The delay changes the phase between the 350-nm pairs and the 375- and 328-nm pairs. The fringes are 2.19 fs apart against the 375-nm pairs (the period of 656 nm), 2.50 fs against the 328-nm pairs (the period of 750 nm), and 1.17 fs between the 375- and 328-nm pairs (the period of 350 nm). The 375-nm pairs (750 + 750 nm) and 328-nm pairs (656 + 656 nm) reach the 350-nm level '
            'through the edges of their spectra below about 20 fs. With two lasers that are not phase-locked the fringes '
            f'average out. Largest gap between the two curves at NA 0.5: θ = 0 {gap.loc[("0", "z", tau, 0.5)]:.2f}, '
            f'θ = π/2 {gap.loc[("pi2", "x", tau, 0.5)]:.2f}, θ = π {gap.loc[("pi", "z", tau, 0.5)]:.2f}.')

big('Fringe depth against NA, 5 to 20 fs', [
    'With crossed and facing lenses the fringes deepen with NA, as they cross a smaller spot.',
    'With collinear lenses the fringes stay fixed in space, so their depth is the same at any NA.'],
    os.path.join(F, 'delay_fringe_depth_vs_na.png'), 'Fringes against the delay deepen with NA for crossed and facing lenses.',
    'Fringe depth is the largest gap between the peak with all pairs and the peak with the 350-nm pairs alone, each over '
    'its value without delay. The delay moves the interference fringes in space with crossed and facing lenses; a high-NA '
    'spot is about one fringe wide, so the peak follows the fringes. With collinear lenses the depth is 0.92 at 5 fs and '
    '0.71 at 10 fs at all NAs. At 20 fs it is at most 0.04. With crossed lenses the peak is taken along the x axis through the focus; '
    'over the whole x–z plane the depth is about two thirds of this (0.28 against 0.42 at NA 0.5 and 5 fs).')


big('2CE peak against the delay, two polarizations, θ = π/2', [
    'Polarized in the plane of the lens axes, the beams have perpendicular fields at the focus.',
    'The fringes are then about a quarter as deep, and the 350-nm pairs fall in the same way.'],
    os.path.join(F, 'delay_polarization_pi2.png'),
    'With crossed lenses, the polarization in the plane of the lens axes makes the fringes against the delay shallow.',
    'Crossed lenses, cut along x through the focus, NA 0.5, 5-fs pulses, fine grid of 0.1 fs. Each panel is divided by '
    'its own total at no delay. Left: both beams polarized perpendicular to the plane of the lens axes; right: both '
    'polarized in that plane. The amplitude of the oscillating part (half its swing, after a 5-fs smooth is subtracted) is '
    'about 0.05 against 0.21 at NA 0.5 and 5 fs, and the 2CE spot is 0.83 µm '
    'against 0.75 µm. The fringes are not absent, because the longitudinal field away from the focus mixes the '
    'components. For real molecules the absorption of two photons with perpendicular polarizations differs from that of '
    'parallel ones by a factor that depends on the molecule, which the model does not include.')

ds.keynote_fonts()
path = os.path.join(OUT, 'pulse_delay.pptx')
prs.save(path)
print('Saved ->', path, f'({len(prs.slides)} slides)')
