r"""Short local deck of the pulse results (2color excitation with femtosecond pulses), presented next to the dashboard.

Figures from cambaliza2000_pulse_time_frequency.py, fig_2ce_setup.py (setup_cambaliza.png),
cambaliza2000_pulses_na_plot.py, cambaliza2000_pulses_profile_10fs.py, cambaliza2000_pulses_sweep_plot.py and
cambaliza2000_pulses_delay_norm_plot.py (backup); numbers in the speaker notes.

Videos from cambaliza2000_pulse_video.py, embedded with a poster frame (deck/poster/, extracted with ffmpeg).

    python scripts/make_pulse_results_deck.py -> output/08_two_color/cambaliza2000/deck/pulse_results.pptx
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mcdo.deckstyle as ds
from mcdo.deckstyle import prs, slide, text, bullets, figure, dots, equation, where, NAVY, WHITE, PALE
from pptx.util import Inches

ds.CITE = ''
ROOT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
P = os.path.join(ROOT, 'pulses')
OUT = os.path.join(ROOT, 'deck')
os.makedirs(OUT, exist_ok=True)


def notes(s, main, script, latex=None):
    """Speaker notes in full sentences: the main point, the details, then the equation in LaTeX on its own lines."""
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


def result(title, items, fig, main, script, latex=None):
    """Title, one or two one-line bullets, the figure filling the rest of the slide."""
    s = slide(title, '')
    hb = sum(0.27 * -(-len(it) // 100) + 0.1 for it in items)          # about 100 characters per line at 13 pt
    bullets(s, 0.5, 0.86, 9.0, hb, items, 13)
    figure(s, fig, 0.5, 0.86 + hb + 0.08, 9.0, 5.2 - (0.86 + hb + 0.08))
    notes(s, main, script, latex)
    return s


def big(title, item, fig, main, script):
    """One one-line bullet and the figure across the full width of the slide."""
    s = slide(title, '')
    hb = 0.27 * -(-len(item) // 100) + 0.1                            # about 100 characters per line at 13 pt
    bullets(s, 0.5, 0.86, 9.0, hb, [item], 13)
    figure(s, fig, 0.15, 0.9 + hb, 9.7, 5.45 - (0.9 + hb))
    notes(s, main, script)
    return s


def video(title, item, mp4, main, script):
    """One bullet and an embedded video (poster frame: the middle, where the pulses meet), as large as the slide allows."""
    poster = os.path.join(OUT, 'poster', os.path.basename(mp4).replace('.mp4', '_mid.png'))
    os.makedirs(os.path.dirname(poster), exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4],
                               capture_output=True, text=True, check=True).stdout)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{dur / 2:.2f}', '-i', mp4, '-frames:v', '1', poster], check=True)
    # re-encoded for PowerPoint: H.264 Main profile, even size, index at the start of the file; this copy is the one
    # embedded and the one in videos/slideNN_<title>.mp4
    slug = re.sub(r'[^A-Za-z0-9]+', '_', title.replace('θ = π', 'facing lenses').replace('-fs', 'fs')).strip('_')
    ppt = os.path.join(VIDS, f'slide{len(prs.slides) + 1:02d}_{slug}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0',
                    '-pix_fmt', 'yuv420p', '-vf', 'scale=1280:-2', '-r', '20', '-movflags', '+faststart', '-an', ppt], check=True)
    s = slide(title, '')
    bullets(s, 0.5, 0.86, 9.0, 0.4, [item], 13)
    from PIL import Image
    iw, ih = Image.open(poster).size
    h = 5.45 - 1.3; w = h * iw / ih
    s.shapes.add_movie(ppt, Inches((10 - w) / 2), Inches(1.3), Inches(w), Inches(h), poster_frame_image=poster,
                       mime_type='video/mp4')
    notes(s, main, script)
    return s


def hide(s):
    s._element.set('show', '0')


VID = os.path.join(P, 'video')
VIDS = os.path.join(OUT, 'videos')                                  # the videos of the deck, one file per slide
shutil.rmtree(VIDS, ignore_errors=True); os.makedirs(VIDS)

s = navy('Two-color excitation with femtosecond pulses', [('Roland Albert A. Romero', 18, WHITE),
         ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
         ('Extension of Cambaliza & Saloma (2000) to optical pulses', 13, PALE)])
notes(s, 'Two-color excitation with femtosecond pulses.', 'Results shown here and in the dashboard tabs Pulses in time and Pulse results.')

s = slide('Continuous beams and femtosecond pulses', '')
bullets(s, 0.5, 0.95, 9.0, 3.0, [
    'Extended the 2CE and 2PE excitation profiles of Cambaliza & Saloma (2000) from continuous beams to femtosecond '
    'pulses of 5 to 100 fs.',
    'Computed the depth of focus against the pulse width for collinear, crossed and facing lenses from NA 0.2 to 0.9.',
    'Found the pulse width at which the pulsed profiles match the continuous-beam ones, using the depth of focus, the '
    'FWHM, the side lobes and the Linfoot criteria.',
    'With facing lenses, shorter pulses shorten the 2CE depth of focus more than the 2PE one, and more at lower NA. '
    'Collinear and crossed lenses keep their depth of focus.',
    'Below about 15 fs, the 375-nm pairs (750 + 750 nm) and 328-nm pairs (656 + 656 nm) also excite the 350-nm level '
    'through the edges of their spectra and add fringes to the 2CE.'], 15)
notes(s, 'This slide states what pulses change in the continuous-beam results.',
      'Collinear lenses θ = 0, crossed θ = π/2, facing θ = π. 2CE uses 750 nm in L1 and 656 nm in L2; 2PE uses 700 nm in both.')

s = slide('Results of Cambaliza & Saloma (2000)', '')
bullets(s, 0.5, 0.95, 9.0, 3.6, [
    'With circular pupils, the sharpest 2PE and 2CE profiles are obtained with crossed lenses (θ = π/2); 2PE has the '
    'narrower depth of focus and FWHM, but stronger side lobes.',
    'With annular pupils, the 2CE profile along the axis at θ = π/2 has a higher contrast and weaker side lobes than the 2PE one.',
    'The main advantage of 2CE is in observing objects through highly scattering media. 2CE needs both beams to overlap '
    'in space and time, so it produces no strong fluorescence background far from the focus.'], 15)
notes(s, 'With continuous beams 2CE has no clear advantage in resolution; its advantage is a weak background in scattering media.',
      'Cambaliza & Saloma (2000) write in Sec. 5 that "the main advantage of 2CE microscopy is not found in improved imaging '
      'resolution and optical sectioning capability, but in the observation of objects through highly scattering media." '
      'The pulse results below are compared with these three points.')
hide(s)                                                             # earlier results; shown only if asked

result('An optical pulse in time', [
    'The optical spectrum of a short pulse is a Gaussian in frequency about the carrier frequency (a), and each frequency is a continuous wave (b).',
    'At t = 0 all the frequencies are in phase and add up; away from t = 0 they drift out of phase, so their sum falls '
    'off as a Gaussian of width τ, the pulse (c).'],
    os.path.join(P, 'pulse_waves.png'), 'A pulse is a sum of continuous waves that are in phase only near t = 0.',
    '(a) The Gaussian spectrum of a 10-fs pulse at 750 nm, nine frequencies marked. (b) The waves at those frequencies; '
    'at 15 fs they are out of phase. With nine frequencies the waves come back into phase at intervals of 75 fs; the whole '
    'continuous spectrum never does. (c) The sum over the whole spectrum, E(t) = ∫ a(ω) e^{−iωt} dω.',
    r'E(t) = \int a(\omega)\, e^{-i\omega t}\, d\omega, \quad a(\omega) = \exp\left[-\frac{(\omega-\omega_0)^2\tau^2}{8\ln 2}\right]')

result('Pulse width and spectral bandwidth', [
    'A transform-limited Gaussian pulse is Gaussian in time and in frequency, with spectral bandwidth Δν = 0.441/τ, shown '
    'against frequency (b) and wavelength (c); both colors lie at the red edge of the visible range.',
    'Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.'],
    os.path.join(P, 'pulse_gaussian.png'), 'Shorter pulses have wider spectra.',
    'Intensity in time exp(−4 ln 2 t²/τ²), FWHM τ (the pulse width). Spectral bandwidth (FWHM) 88 THz at 5 fs, 44 THz '
    'at 10 fs, 22 THz at 20 fs, 4.4 THz at 100 fs. Against wavelength the spectrum is drawn per unit wavelength, '
    'S(λ) = S(ν) c/λ², so it leans towards longer wavelengths. The shaded band is the visible range, 380–750 nm; at 5 fs '
    'the 750-nm spectrum reaches well into the near infrared. '
    'At 10 fs each spectrum has 31% of its peak at 700 nm (428 THz); at 20 fs and longer it has almost none.')

result('Collinear, crossed and facing lenses', [
    'Lens L2 is lens L1 rotated by θ about the common focus O; L1 focuses 750 nm and L2 656 nm (700 nm in both for 2PE).',
    'Both beams are linearly polarized along y, perpendicular to the plane of the two lens axes, so their polarizations '
    'are parallel at every θ.'],
    os.path.join(ROOT, '..', 'setup_cambaliza.png'), 'Both beams are polarized along y at every θ.',
    'Vector (high-NA) results: psi = π/2 for both beams; the rotation about y leaves that direction unchanged, so the two '
    '700-nm fields of 2PE interfere fully, as in the scalar |U₁ + U₂|⁴. 2CE (I₁·I₂) does not depend on the angle between '
    'the polarizations; at high NA each spot is longer along its polarization (y) than across it, and the cuts across '
    'the axis are along x. The backup of the high-NA study has both beams polarized in the x–z plane, and unpolarized 2CE beams '
    '(high_na/pupils/polarization_2ce_circular.png).')

s = slide('Two pulses through the common focus', '')
bullets(s, 0.5, 0.9, 9.0, 1.0, [
    'Each lens focuses a Gaussian pulse of length τ; both pulse centres reach the focus at t = 0.',
    'The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level, then squares the total.'], 13)
h = equation(s, 1.5, 2.15, 7.0, r'A(P) = \int E(P,t)^2\, e^{i\omega_e t}\, dt, \qquad E = E_1 + E_2', 20)
h += equation(s, 1.5, 2.35 + h, 7.0, r'F(P) = |A(P)|^2', 20)
where(s, 1.5, 2.6 + h, 7.0, 'E_1 and E_2 are the fields of the two pulses at P, ω_e is the frequency of the 350-nm level, and F is '
      'the total excitation accumulated as the pulses pass the focus. 2CE uses 750 and 656 nm, 2PE uses 700 nm in both lenses. Paraxial model, NA 0.3 to 0.5, air.')
notes(s, 'The excitation counts all photon pairs that add up to 350 nm.',
      'Pairs across the two pulses (750 + 656 nm) are the 2CE pairs of the continuous-beam case. Pairs within one pulse '
      '(750 + 750 nm, 656 + 656 nm) add up to 375 and 328 nm and reach 350 nm only through the edges of the spectrum. '
      'Phase-locked pulses, a narrow 350-nm level, no chirp.',
      r'A(P) = \int E(P,t)^2 e^{i\omega_e t} dt = A_{11} + 2A_{12} + A_{22}, \quad F = |A|^2')
hide(s)

s = slide('Assumptions of the model', '')
bullets(s, 0.5, 0.95, 9.0, 4.2, [
    'Both pulses are transform-limited Gaussian pulses of the same length τ, without chirp.',
    'Each frequency is focused as in the paraxial scalar model, with circular, uniformly filled pupils and no chromatic aberration, at NA ≤ 0.5.',
    'The medium is air without dispersion, so the pulses keep their shape as they pass through the focus.',
    'The two pulses come from one phase-locked source, and their centres reach the focus at the same time.',
    'The 350-nm level is narrower than the pulse spectra, and the excitation is weak, without saturation.',
    'The fluorescence is collected over the whole passage of the pulses, so the excitation profile is the total accumulated as the pulses pass the focus.'], 14)
notes(s, 'The model idealizes the source, the medium and the absorber.',
      'The frequencies are sampled uniformly in ω over ±3.5 standard deviations, spaced so that the period of the sum is '
      'longer than the time window. A delay, where used, is given as a path difference cΔt = N × 700 nm.')
hide(s)

result('2CE with 100-fs pulses and with continuous beams', [
    'At 100 fs, pulsed 2CE is the same as with continuous beams at all three lens angles, so the continuous-beam results '
    'of Cambaliza & Saloma (2000) hold for pulses of that length.'],
    os.path.join(P, 'sweep', 'profiles_100fs_2ce.png'), 'At 100 fs the pulses give the continuous-beam 2CE.',
    'Total 2CE accumulated as the pulses pass the focus, NA 0.5, air. The widths agree to within 1%: 3.56 µm along the '
    'axis with collinear lenses, 0.76 µm across with crossed lenses, and 3.52 against 3.56 µm with facing lenses, where '
    'the pulses overlap over 21 µm, six times the focus.')

result('Depth of focus, facing lenses', [
    'With facing lenses, pulsed 2CE forms only where the two pulses meet, so its depth of focus is shorter than with continuous beams.',
    'The shortening is larger at lower NA, because the continuous-beam focus grows while the stretch where the pulses meet stays the same.',
    '2PE shortens less, because pairs of photons from one pulse need no overlap.'],
    os.path.join(P, 'sweep', 'dof_na_pi.png'), 'Pulses shorten the 2CE depth of focus with facing lenses, more at lower NA.',
    'Depth of focus = FWHM along the axis of the total, through the fringe crests. The pulses meet over a stretch of '
    'about √2·cτ/2 (4.2 µm at 20 fs), while the continuous-beam depth of focus is 3.6, 5.6 and 9.9 µm at NA 0.5, 0.4 '
    'and 0.3. At 20 fs the 2CE depth of focus is 0.79, 0.63 and 0.40 of the continuous-beam value, and the 2PE one 0.88, 0.76 and 0.56. Below 10 fs the three NAs give 1.5 to '
    '2.5 µm. At 100 fs both are within 1% (NA 0.5) to 9% (NA 0.3) of continuous beams.')

result('Why the facing pulses shorten the 2CE', [
    'Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time only over a '
    'stretch of cτ/√2 about the focus, 4.2 µm at 20 fs.',
    'The pulsed 2CE is the continuous-beam profile times this overlap: at 20 fs the product gives 2.74 µm and the full '
    'calculation 2.78 µm.'],
    os.path.join(P, 'sweep', 'gate_pi.png'), 'The overlap of the pulses in time cuts the 2CE focus.',
    'G(z) = ∫ I₁(t − z/c) I₂(t + z/c) dt ∝ exp(−8 ln 2 z²/(cτ)²), FWHM cτ/√2 (2.1 µm at 10 fs, 21 µm at 100 fs). With '
    'crossed lenses the overlap along z is √2·cτ wide (8.5 µm at 20 fs), much longer than the 0.67-µm focus; with '
    'collinear lenses the pulses travel together and overlap everywhere. At 10 fs the computed 2CE (2.14 µm) is longer '
    'than the product (1.83 µm), because the 375- and 328-nm pairs need no overlap.',
    r'G(z) = \int I_1(t - z/c)\, I_2(t + z/c)\, dt \propto \exp\left[-\frac{8\ln 2\, z^2}{(c\tau)^2}\right]')
video('100-fs and 10-fs pulses compared, θ = π, in time',
    'At 100 fs the pulses overlap over the whole focus and the 2CE follows the continuous beams; at 10 fs they overlap only near the focus.',
    os.path.join(VID, 'compare_2ce_pi_tau100_vs_10.mp4'), 'The overlap of the pulses sets the 2CE along the axis.',
    'Both runs are shown at the same t/τ. The small ripples of the 100-fs curve while it builds up come from the 375- and '
    '328-nm terms, which oscillate in the running sum and average out by the end at 100 fs.')

result('Depth of focus, collinear and crossed lenses', [
    'With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few '
    'percent, because the pulses overlap over the whole focus.',
    'Crossed lenses therefore keep the sharpest profiles, as with continuous beams.'],
    os.path.join(P, 'sweep', 'dof_na_0_pi2.png'), 'Collinear and crossed lenses keep their depth of focus.',
    'With crossed lenses the 2CE depth of focus grows by up to 6% below 10 fs, because the 375-nm pairs from L1 alone extend along its axis (z); '
    '2PE shortens by up to 7% at NA 0.3 and 5 fs. The width across the axis with crossed lenses narrows by about 2% at '
    '10 fs (0.76 to 0.75 µm at NA 0.5).')

big('2CE with 10-fs pulses, θ = π',
    'The total 2CE carries fringes 350 nm apart, because the beams travel in opposite directions, so the 375- and '
    '328-nm pairs fall in and out of phase with the 350-nm pairs along the axis.',
    os.path.join(P, 'sweep', 'profiles_pi_10_2ce.png'), 'At 10 fs, 2CE is confined to where the pulses meet.',
    'The left half shows the total accumulated as the pulses pass the focus, and the right half I₁·I₂ at t = 0, which has no fringes. The fringes come '
    'from the 375- and 328-nm pairs, which reach 350 nm at 10 fs. Depth of focus 2.14 µm against 3.56 µm.')
video('2CE with 10-fs pulses, θ = π, in time',
    'The two pulses pass through the focus; the 2CE builds up only where they overlap.',
    os.path.join(VID, 'pulse_2ce_pi_tau10.mp4'), 'The 2CE builds up where the pulses meet.',
    'The top row shows I₁, I₂, I₁·I₂ now and the 2CE accumulated up to t, the middle row the same along the axis, and the bottom row the spectrum '
    'arriving at the focus now. Click to play; it loops in the dashboard (Pulses in time).')
big('2PE with 10-fs pulses, θ = π',
    'The 2PE keeps its fringes 350 nm apart but is shorter than with continuous beams.',
    os.path.join(P, 'sweep', 'profiles_pi_10_2pe.png'), 'At 10 fs, 2PE extends further along the axis than 2CE.',
    'The left half shows the total accumulated as the pulses pass the focus, and the right half |E₁ + E₂|⁴ at t = 0. The depth of focus is 2.47 µm against '
    '3.55 µm; the L1 + L1 and L2 + L2 pairs need no overlap.')
video('2PE with 10-fs pulses, θ = π, in time',
    'Each pulse excites alone as it passes; the fringes form where the two pulses overlap.',
    os.path.join(VID, 'pulse_2pe_pi_tau10.mp4'), 'The 2PE builds up along each pulse, with fringes where they meet.',
    'The top row shows I₁, I₂, |E₁ + E₂|⁴ now and the 2PE accumulated up to t, the middle row the same along the axis, and the bottom row the spectrum '
    'arriving at the focus now.')

result('Signal added by the 375- and 328-nm pairs', [
    'Below about 15 fs the spectra reach 700 nm, so two photons of one pulse also excite the 350-nm level, through the '
    '375- and 328-nm pairs.',
    'Their amplitude interferes with that of the 350-nm pairs, which gives the fringes, and one beam alone now excites, '
    'so 2CE starts to lose the weak background of continuous beams.'],
    os.path.join(P, 'sweep', 'strength_vs_tau.png'), 'Pairs within one pulse matter below 15 fs.',
    'The peak of the total over that of the 350-nm pairs alone is 1.02 (20 fs), 1.15 (15 fs), 1.73 (10 fs), 3.1 (5 fs). Fringe depth '
    '0.02, 0.15, 0.57, 0.96.')

# Pulse width that gives the continuous-beam profiles, against NA (cambaliza2000_pulses_na_sweep.py). The figures go in
# once the scalar sweep in air covers at least three NAs; until then the slide gives the numbers of the first scalar run.
NS = os.path.join(P, 'na_sweep')
TW = {}
if os.path.exists(os.path.join(NS, 'tau_cw.txt')):
    for line in open(os.path.join(NS, 'tau_cw.txt')):
        k, v = line.split(': within tolerance from ')
        sig, tk, name, _, na = k.split()
        TW[(sig, tk, name, na)] = float(v.split('diff ')[1].split(' fs')[0])
nas_air = {k[3] for k in TW if k[2] == 'paraxial_air'}
if len(nas_air) >= 3:
    tw = lambda sig, tk, name, na: TW.get((sig, tk, name, f'{na:g}'), float('nan'))
    fs = lambda t: f'{t:.0f} fs' if t == t else 'more than 500 fs'
    big('Pulse width that matches continuous beams',
        f'With facing lenses, the pulsed 2CE matches the continuous-beam 2CE once the pulses are longer than about '
        f'{fs(tw("2ce", "pi", "paraxial_air", 0.9))} at NA 0.9, {fs(tw("2ce", "pi", "paraxial_air", 0.5))} at NA 0.5 '
        f'and {fs(tw("2ce", "pi", "paraxial_air", 0.3))} at NA 0.3, because a lower NA gives a longer focus for the '
        'pulses to overlap over.',
        os.path.join(NS, 'tau_cw_vs_na.png'), 'Facing lenses need the longest pulses to behave like continuous beams.',
        'With collinear lenses 5-fs pulses already give the continuous-beam profiles, and with crossed lenses 2CE does '
        'from about 20 to 30 fs. The results are for the scalar model in air. The difference is the largest gap between the pulsed and the '
        'continuous-beam profile, each scaled to its own peak, along the axis and across it; the pulse width is read '
        'where it falls below 1% of the peak. The grey band lies below the shortest pulse I ran (5 fs), and the open '
        'triangles mark NAs that still differ by more than 1% at 500 fs.')
    KD = json.load(open(os.path.join(NS, 'key_dof.json')))
    kd = lambda sig, tk, na, t: KD.get(f'{sig}|{tk}|{na:g}|{t:g}', float('nan'))
    big('2CE depth of focus against pulse width',
        'As the pulses get shorter, the 2CE depth of focus with facing lenses falls below that with continuous beams '
        '(ratio below 1), by '
        f'more at lower NA ({kd("2ce", "pi", 0.9, 20):.2f} at NA 0.9 and {kd("2ce", "pi", 0.3, 20):.2f} at NA 0.3, at 20 fs). '
        'Crossed lenses keep the sharpest profile, as with continuous beams.',
        os.path.join(NS, 'key_dof_vs_tau_2ce.png'), 'Shorter pulses and lower NA shorten the 2CE focus with facing lenses.',
        'The depth of focus is the FWHM along the axis through the fringe crests, divided by its continuous-beam value, '
        'for the scalar model in air with one line per NA. With collinear lenses it stays at the continuous-beam value, '
        'and with crossed lenses it changes by a few percent below 15 fs, so the crossed-lens focus stays the shortest.')
    big('2CE depth of focus against NA',
        'As NA increases, the ratio of the 2CE depth of focus with pulses to that with continuous beams returns to 1 '
        'with facing lenses at each pulse width, because the focus becomes shorter than the stretch where the pulses overlap.',
        os.path.join(NS, 'key_dof_vs_na_2ce.png'), 'Higher NA brings the pulsed 2CE focus back to the continuous-beam one.',
        f'At 100 fs the ratio is {kd("2ce", "pi", 0.3, 100):.2f} at NA 0.3, {kd("2ce", "pi", 0.5, 100):.2f} at NA 0.5 '
        f'and {kd("2ce", "pi", 0.9, 100):.2f} at NA 0.9. At low NA the pulsed 2CE with facing lenses therefore gives a '
        'shorter focus than continuous beams, which improves the optical sectioning. The same figures for 2PE are in the backup.')
else:
    s_ = slide('Pulse width that matches continuous beams', '')
    bullets(s_, 0.5, 0.95, 9.0, 4.2, [
        'I compared the pulsed 2CE and 2PE with continuous beams from NA 0.1 to 0.9 (scalar model, air), and read the '
        'pulse width at which the two profiles differ by less than 1% of the peak.',
        'With collinear lenses 5-fs pulses already give the continuous-beam profiles, and with crossed lenses 2CE does '
        'from about 20 to 30 fs.',
        'With facing lenses the pulses must be longer at lower NA, because the focus grows as about 1/NA² while the '
        'pulses overlap over about cτ. 2CE matches from about 30 fs at NA 0.9, 90 fs at NA 0.5 and 270 fs at NA 0.3.',
        'At NA 0.2 and below, 2CE with facing lenses still differs by more than 1% at 500 fs.'], 15)
    notes(s_, 'Facing lenses need the longest pulses to behave like continuous beams, more so at lower NA.',
          '2CE with facing lenses comes within 1% from 27 fs (NA 0.9), 33 fs (0.8), 45 fs (0.7), 63 fs (0.6), 93 fs '
          '(0.5), 149 fs (0.4) and 269 fs (0.3). 2PE with facing lenses comes within 1% from 16, 23, 31, 45, 66, 106 '
          'and 193 fs at the same NAs. With crossed lenses 2CE comes within 1% from 21 to 28 fs between NA 0.7 and 0.2, '
          'and 2PE from 5 to 17 fs.')

s = slide('Summary', '')
bullets(s, 0.5, 0.95, 9.0, 4.2, [
    'At 100 fs, pulsed 2CE is the same as with continuous beams.',
    'With facing lenses, pulsed 2CE forms only where the pulses meet, so its depth of focus is shorter than with '
    'continuous beams, more so at lower NA; 2PE shortens less.',
    'With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent.',
    'Below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to lose its weak background.',
    'With facing lenses, a delay between the pulses moves the 2CE along the axis and weakens it.',
    'Pulses give the continuous-beam profiles once they overlap over the whole focus; with facing lenses this takes '
    'about 90 fs at NA 0.5 and longer pulses at lower NA.',
    'The results assume phase-locked, transform-limited pulses and a narrow 350-nm level.'], 14)
notes(s, 'Pulses of about 20 fs give 2CE an axial advantage at θ = π, larger at lower NA.',
      'In practice 20 fs at the sample needs dispersion control, and both colors from one phase-locked source (an OPA). '
      'Below 15 fs the excitation by one beam alone works against the weak background that continuous beams give in '
      'scattering media.')

result('Next steps', [
    'Extend the comparison to the Richards–Wolf model, from NA 0.1 to 0.9 in air and from 0.5 to 1.2 in water, with '
    'the depth of focus, the width across the axis, the side lobes and the Linfoot criteria.',
    'The scalar model in water follows, then annular pupils (ε = 0.99) and the delay between the two pulses, previewed below.'],
    os.path.join(P, 'delay_norm', 'delay_pi.png'), 'High NA with the vector model is running; annular pupils and the delay come next.',
    'The figure previews the peak and the centre of the 2CE against the path difference N (λ₀ = 700 nm), θ = π, 10, 20 '
    'and 100 fs. At 20 fs the peak halves at N of about ±8 (19 fs). With continuous beams the timing does not matter; '
    'with facing lenses a delay moves the 2CE along the axis, within the focus, and weakens it. The backup has the '
    'profiles along the axis and the three angles.')

navy('Backup', [('Delay between the pulses', 16, PALE)])
DN = os.path.join(P, 'delay_norm')
result('2CE along the axis against the delay, θ = π, 20 fs', [
    'As the delay grows the 2CE moves towards L2 and weakens, as the meeting point leaves the focus.'],
    os.path.join(DN, 'delay_profiles_pi.png'), 'Delay shifts and weakens the 2CE.',
    'At N = 0, 4, 8 and 12 the centre is at 0, 0.5, 1.1 and 1.6 µm, while the pulses meet at 0, 1.4, 2.8 and 4.2 µm.')
result('2CE peak against the delay at three angles, 20 fs', [
    'With collinear and crossed lenses a delay only weakens the 2CE, without moving it, and it falls faster than with facing lenses.'],
    os.path.join(DN, 'delay_angles.png'), 'Facing lenses tolerate more delay.',
    'The curves for θ = 0 and π/2 coincide, because on the axis the crossed beam is thin along z, so the meeting point cannot move with the delay.')

if len(nas_air) >= 3:
    navy('Backup', [('Pulses against continuous beams over NA, all measures', 16, PALE)])
    big('Largest difference against pulse width',
        'The difference falls as the pulses get longer; with facing lenses it falls more slowly at lower NA.',
        os.path.join(NS, 'diff_vs_tau_paraxial_air.png'), 'Facing lenses converge most slowly.',
        'The difference is the largest gap between the pulsed and the continuous-beam profile, each scaled to its own '
        'peak, along the axis and across it, for the scalar model in air with one line per NA; the dotted line is at 1% '
        'of the peak. Below about 15 fs the '
        '375- and 328-nm pairs add fringes, so the difference stays near 100% with crossed and facing lenses.')
    for sig in ('2ce', '2pe'):
        big(f'Pulse width by each measure, {sig.upper()}',
            'The depth of focus needs the longest pulses with facing lenses; the width across the axis, the side lobes '
            'and the Linfoot fidelity reach the continuous-beam values with shorter pulses.',
            os.path.join(NS, f'tau_cw_vs_na_{sig}.png'), 'The depth of focus is the measure that needs the longest pulses.',
            'The measures are those of Cambaliza & Saloma (FWHM along and across the axis, side lobes) and of Romallosa et '
            'al. (Linfoot fidelity F), with the continuous-beam profile as the reference, for the scalar model in air. The tolerance is 1% for '
            'the difference and the FWHM, 1 point for the side lobe and 0.01 for F.')
        big(f'{sig.upper()} measures against pulse width',
            'Depth of focus, width across the axis, side lobe and the Linfoot fidelity and structural content approach '
            'their continuous-beam values as the pulses get longer.',
            os.path.join(NS, f'metrics_vs_tau_paraxial_air_{sig}.png'), 'All measures converge to continuous beams with longer pulses.',
            'The results are for the scalar model in air, with one line per NA, and the dotted lines mark the '
            'continuous-beam values. A structural content S below 1 means a narrower profile than with continuous beams.')
    for kind, ttl in (('tau', 'pulse width, at each NA'), ('na', 'NA, at each pulse width')):
        big(f'2PE depth of focus against {ttl.split(",")[0]}',
            'With facing lenses the 2PE depth of focus shortens less than the 2CE one, because pairs of photons from one '
            'pulse need no overlap.',
            os.path.join(NS, f'key_dof_vs_{kind}_2pe.png'), '2PE shortens less than 2CE.',
            'The depth of focus is the FWHM along the axis through the fringe crests, divided by its continuous-beam '
            'value, for the scalar model in air.')

ds.keynote_fonts()
path = os.path.join(OUT, 'pulse_results.pptx')
prs.save(path)
print('Saved ->', path, f'({len(prs.slides)} slides)')
