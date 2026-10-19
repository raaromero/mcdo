r"""Progress report on two-color excitation (2CE), one deck per section.

  00 overview     overall summary, next steps
  01 replication  scalar 2CE rebuilt from the paper (make_lim2002_replication_deck.py)
  02 vector       vector 2CE, uniform input, against NA
  03 fidelity     Linfoot's criteria F, C, Q against NA
  04 gaussian     vector 2CE, Gaussian input (α_t = 4): the results of 02 and 03
  05 delay        time delay between continuous beams, and against a misalignment in space
  06 polarization s–s and p–p linear polarization against unpolarized beams

Each deck stands on its own: title, summary (main point and two supporting
sentences), the geometry and field equations it uses, its results, and a glossary.
Figures come from fig_lim2002_slides.py, fig_lim2002_phase_delay.py and the
replication scripts; equations are displayed on the slides with LaTeX in the notes.

    python scripts/make_lim2002_progress_deck.py              # every section, each in its own process
    SECTION=vector python scripts/make_lim2002_progress_deck.py
    -> ~/Downloads/Research/two_color/2ce_<NN>_<section>.pptx
"""

import io
import os
import runpy
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DECK_APPEND'] = '1'

from PIL import Image

import mcdo.deckstyle as ds
from mcdo.deckstyle import (CARD, FIG, GREY, MSO_SHAPE, NAVY, ORIG, PALE, PAN, PURPLE, RED, WHITE, bullets, card, dots, equation,
                            figure, label, notes, prs, shape, slide, text, where)

SECTIONS = ['overview', 'replication', 'vector', 'fidelity', 'gaussian', 'delay', 'polarization', 'pulses']
MEETING = 'meeting'                                            # SECTION=meeting: highlights for one meeting, not in the full build
CMEETING = 'cmeeting'                                          # SECTION=cmeeting: meeting on Cambaliza & Saloma (2000)
SECTION = os.environ.get('SECTION')
DIR = os.path.expanduser(os.environ.get('DECK_DIR', '~/Downloads/Research/two_color'))
HERE = os.path.dirname(__file__)
SL = lambda name: os.path.join(FIG, 'slides', name)
PD = lambda name: os.path.join(FIG, 'phase_delay', name)
ds.CITE = ''

if SECTION is None:                                            # build each section in a fresh process
    for sec in SECTIONS:
        r = subprocess.run([sys.executable, __file__], env={**os.environ, 'SECTION': sec}, capture_output=True, text=True)
        print(r.stdout.strip() if r.returncode == 0 else f'{sec} FAILED:\n{r.stderr[-3000:]}')
    sys.exit()


# ══ helpers ══════════════════════════════════════════════════════════════
def navy(title, lines):
    s = prs.slides.add_slide(ds.BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    dots(s, 0.6, 0.7, 0.2, 0.27)
    text(s, 0.6, 1.15, 8.8, 1.5, title, 30, WHITE, True, 'Helvetica Neue')
    for i, (line, size, col) in enumerate(lines):
        text(s, 0.6, 2.85 + i * 0.4, 8.8, 0.4, line, size, col)
    return s


def title(name, what):
    s = navy(name, [('Roland Albert A. Romero', 18, WHITE),
                    ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
                    (what, 13, PALE)])
    notes(s, name + '.', what)


def summary(main, *rest):
    """Main point in bold, its supporting points beneath; the last item is the speaker script."""
    *support, script = rest
    s = slide('Summary', '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, [main] + ['– ' + x for x in support], 14 if len(support) <= 2 else 13, bold=True)
    notes(s, main, script)


def words(name, items, main, script, latex=None, size=13):
    s = slide(name, '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, items, size)
    notes(s, main, script, latex)


def wide(name, path, items, main, script, latex=None):
    s = slide(name, '')
    if SECTION in ('cambaliza', CMEETING):                     # figure as tall as the bullets beneath allow
        h = 4.12 - 0.3 * (len(items) - 1)
        figure(s, path, 0.45, 0.92, 9.1, h)
        bullets(s, 0.6, 0.98 + h, 8.6, 0.3 * len(items) + 0.05, items, 13)
    else:
        figure(s, path, 0.45, 0.95, 9.1, 3.72)
        bullets(s, 0.6, 4.72, 8.9, 0.55, items, 11.5)
    notes(s, main, script, latex)


def side(name, path, items, main, script, latex=None, fw=5.3):
    s = slide(name, '')
    figure(s, path, 0.45, 0.95, fw, 4.25)
    bullets(s, 0.45 + fw + 0.25, 1.05, 9.5 - fw - 0.7, 4.15, items, 12)
    notes(s, main, script, latex)


CB = os.path.join(FIG, '..', 'cambaliza2000')                 # Cambaliza & Saloma (2000) figures


def trimmed(path, pad=6):
    """Copy of a scanned panel without its white margin (in the system temp folder), so it fills its slot."""
    import tempfile
    out = os.path.join(tempfile.gettempdir(), 'cpanel_trim', os.path.basename(path))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im = Image.open(path).convert('RGB')
    box = Image.eval(im.convert('L'), lambda v: 255 if v < 235 else 0).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(out)
    return out


def side(title, path, items, main, script, size=14):
    """Figure at the left, as large as the slide allows; bullets at the right."""
    s = slide(title, '')
    figure(s, path, 0.3, 0.95, 5.9, 4.45)
    bullets(s, 6.35, 1.1, 3.35, 4.2, items, size)
    notes(s, main, script)


def cpanel(title, key, ours, line, script=None):
    """Original panel of Cambaliza & Saloma (2000) beside current work, one line (or one per curve) beneath."""
    lines = [line] if isinstance(line, str) else list(line)
    hmax = 3.9 - 0.28 * (len(lines) - 1)
    s = slide(title, '')
    left, right = trimmed(os.path.join(CB, 'original', f'{key}.png')), os.path.join(CB, 'panels', ours)
    a1, a2 = (Image.open(p).size[0] / Image.open(p).size[1] for p in (left, right))
    h = min(hmax, (9.5 - 0.15 - 0.2) / (a1 + a2) + 0.1)        # same height for both, as large as the width allows
    w1, w2 = a1 * (h - 0.1) + 0.1, a2 * (h - 0.1) + 0.1
    x1 = (10 - (w1 + w2 + 0.15)) / 2
    label(s, x1, 0.9, w1, 'Cambaliza & Saloma (2000)')
    label(s, x1 + w1 + 0.15, 0.9, w2, 'Current work', PURPLE)
    figure(s, left, x1, 1.15, w1, h)
    figure(s, right, x1 + w1 + 0.15, 1.15, w2, h)
    bullets(s, 0.6, 1.2 + h, 8.6, 0.28 * len(lines) + 0.07, lines, 14 if len(lines) == 1 else 13)
    notes(s, title, script or ' '.join(lines))


def coverlay(keys, ttl, line):
    """Four panels of current work drawn over the original figures."""
    s = slide(ttl, '')
    for q, k in enumerate(keys):
        figure(s, os.path.join(CB, 'overlay', f'{k}.png'), 0.45 + (q % 2) * 4.6, 0.95 + (q // 2) * 2.0, 4.45, 1.95)
    bullets(s, 0.6, 4.98, 8.6, 0.4, [line], 14)
    notes(s, ttl, line)


def cmodel(fig=None):
    U1 = r'U(P;\theta) = -j\,\frac{\pi\,\mathrm{NA}^2 A\, e^{\,j (2f/D)^2 u}}{\lambda}\,\left[C(v_r, w_r, u_r) - jS(v_r, w_r, u_r)\right]'
    U2 = r'u_r = u\cos\theta - v\sin\theta, \quad v_r = v\cos\theta + u\sin\theta, \quad u = \frac{2\pi\mathrm{NA}^2}{\lambda}z, \quad v = \frac{2\pi\mathrm{NA}}{\lambda}x'
    U3 = r'F_{2c} = \kappa\,|U_1|^2|U_2|^2, \qquad F_{2p} = \kappa\,'"'"r'|U_1 + U_2|^4, \qquad U_a = U_R - U_{\varepsilon R}'
    eqslide('Paraxial scalar model: Eqs. 1–6', 'Beam 2 is rotated in real space; Eq. 1 writes the rotation in (u, v).', [
        (U1, 'Eq. 1: C, S = Lommel functions; f = focal length, D = pupil diameter; NA 0.5.'),
        (U2, 'rotated coordinates of beam 2 (Eq. 1); θ = angle between the lens axes.'),
        (U3, 'Eqs. 2–6: 2CE (750 + 656 nm), 2PE (700 nm); annular ε = 0.99.')],
        'Paraxial scalar model, Eqs. 1-6.', 'Equations 1 to 6.', '\n'.join((U1, U2, U3)), fig=fig, size=14)


def chigh_na(part='High NA', water_x=False, summary=None):
    """Part on high NA of the Cambaliza decks: scalar against vector widths, air and water, and the paper's comparisons."""
    hn = os.path.join(CB, 'high_na')
    navy(part, [])
    if summary:
        words(*summary, size=16)
    if SECTION == CMEETING:                                    # one configuration per slide: medium and θ
        WHY_0 = 'Why: the paraxial phase uses sin²α/2 for 1 − cos α, which lengthens the focus by tan²(α/2).'
        WHY_P2 = 'Why: each beam is cut by the other beam’s narrow spot, which the paraxial model reproduces.'
        WHY_PI = 'Why: the 2PE width along the axis is the interference fringe, set by the wavelength, not by the focus.'
        WHY_0 = 'Why: the paraxial phase uses sin²α/2 for 1 − cos α, which lengthens the focus by tan²(α/2).'
        for key, ttl, items in (
                ('2ce_0', '2CE, θ = 0 and π', [
                    'Across the axis scalar and vector agree within 5% up to NA 0.86 in air and 1.14 in water.',
                    'Along the axis the paraxial depth of focus is 5% longer at NA 0.43 in air, 0.57 in water.', WHY_0]),
                ('2ce_pi2', '2CE, θ = π/2', [
                    'Scalar and vector agree within 4% up to NA 0.7 in air and 0.9 in water, where crossed lenses fit.',
                    'Why: each width is set by the other beam’s narrow spot, which the paraxial model reproduces.']),
                ('2pe_0', '2PE, θ = 0', [
                    'The same as 2CE at θ = 0: along the axis the paraxial depth of focus is 5% longer at NA 0.43 in air.',
                    WHY_0]),
                ('2pe_pi2', '2PE, θ = π/2', [
                    'Scalar and vector agree within 0.4% in air and water.',
                    'Why: the width is the interference fringe of the two crossed beams, set by the wavelength.']),
                ('2pe_pi', '2PE, θ = π', [
                    'Across the axis: the same as θ = 0. Along the axis the fringe agrees within 5% up to NA 0.91 in air.',
                    'Why: along the axis the width is the fringe of the two facing beams, λ/4n, not the focus.'])):
            wide(f'Widths against NA: {ttl}', os.path.join(hn, f'cfg_{key}.png'), items,
                 f'Scalar against vector widths, {ttl}.',
                 'Solid: vector (Richards-Wolf), beams along y; dashed: paraxial scalar. Blue: air; green: water. '
                 'Linear axes. Gap numbers from high_na/split.txt.')
        wide('Scalar over vector width against NA: 2CE', os.path.join(hn, 'gap_2ce.png'), [
            'Along the axis the gap reaches 5% at NA 0.43 in air and 0.57 in water; across the axis at 0.86 and 1.14.',
            'At θ = π/2 the gap stays below 4%.'],
            'Where the paraxial 2CE widths depart from the vector ones.',
            'Gap = scalar / vector - 1. Diamonds: NA where the gap reaches 5% (interpolated).')
        wide('Scalar over vector width against NA: 2PE', os.path.join(hn, 'gap_2pe.png'), [
            'θ = 0: as 2CE. θ = π/2: below 0.4%. θ = π along the axis: −5% at NA 0.91 in air, 1.21 in water.'],
            'Where the paraxial 2PE widths depart from the vector ones.',
            'Gap = scalar / vector - 1. 2PE across the axis at theta = pi equals theta = 0 and is not drawn twice.')
    else:
        wide('Widths across the axis against NA, air', os.path.join(hn, 'widths_air_x.png'), [
            'Across the axis the paraxial widths agree with the vector ones within 6% up to NA 0.9.'],
            'The paraxial model holds across the axis.',
            'Solid vector, dashed paraxial scalar; both beams polarized along y. Scalar wider by up to 1.4% at NA 0.5, 3.4% at '
            '0.7, 5.9% at 0.9. theta = 0 and pi coincide; theta = pi/2 to NA 0.71 (lenses fit at 90 degrees).')
        wide('Depth of focus against NA, air', os.path.join(hn, 'widths_air_z.png'), [
            'The paraxial depth of focus is too long at high NA: by 36% at NA 0.9.'],
            'Along the axis the paraxial model gives too long a focus at high NA.',
            'Scalar DOF longer by 7% at NA 0.5, 16% at 0.7, 36% at 0.9: the factor tan^2(alpha/2) from the small-angle phase. '
            '2PE at theta = pi/2 and pi: the width of the central interference fringe, set by the wavelength.')
        if water_x:
            wide('Widths across the axis against NA, water', os.path.join(hn, 'widths_water_x.png'), [
                'In water the paraxial widths across the axis agree within 3% up to NA 0.9.'],
                'The paraxial model holds across the axis in water.',
                'Scalar wider by up to 0.7% at NA 0.5, 1.6% at 0.7, 3.1% at 0.9, 7.2% at 1.25. theta = pi/2 to NA 0.94.')
        wide('Depth of focus against NA, water', os.path.join(hn, 'widths_water_z.png'), [
            'In water the paraxial error at the same NA is about half that in air: 15% at NA 0.9.'],
            'In water the paraxial model holds to a higher NA.',
            'Scalar DOF longer by 4% at NA 0.5, 8% at 0.7, 15% at 0.9, 44% at 1.25 (tan^2(alpha/2) with sin(alpha) = NA/1.33). '
            'theta = pi/2 to NA 0.94 (lenses fit at 90 degrees).')
    if SECTION != CMEETING:
     wide('Scalar over vector width against NA, θ = 0 and π', os.path.join(hn, 'split_0pi.png'), [
        'Across the axis the scalar width is 5% larger at NA 0.86 in air and 1.14 in water.',
        'Along the axis the paraxial depth of focus is 5% longer at NA 0.43 in air and 0.57 in water.'],
        'The paraxial model departs first along the axis.',
        'Gap = scalar / vector - 1. Diamonds: NA where the gap reaches 5% (interpolated). theta = 0 and pi give the same '
        'widths except 2PE along the axis, where facing lenses give fringes; the 2PE fringe at pi reaches -5% at NA 0.91 '
        '(air) and 1.21 (water). 2PE and 2CE gaps coincide at theta = 0.')
    if SECTION != CMEETING:
     wide('Scalar over vector width against NA, θ = π/2', os.path.join(hn, 'split_pi2.png'), [
        'At θ = π/2 the two agree within 4% up to NA 0.7 in air and 0.9 in water, where the lenses fit.'],
        'At theta = pi/2 the two models do not split.',
        'Crossed lenses fit up to a half-angle of 45 degrees: NA 0.71 in air, 0.94 in water. Largest gap: 2CE across the '
        'axis, 3.4% (air, NA 0.7) and 3.1% (water, NA 0.9).')
    wide('Comparisons across the axis against NA, θ = π/2', os.path.join(hn, 'ratios_x.png'), [
        'Scalar and vector agree within 4%: the 2CE–2PE comparisons made at NA 0.5 hold at high NA.',
        'The 2CE spot shrinks with NA while the 2PE fringe keeps its width, so their ratio falls.'],
        'The 2CE-2PE comparisons hold at high NA; their size depends on NA.',
        'Within 4% to NA 0.7 (air) and 0.9 (water). 2CE over 2PE at theta = pi/2: 2.9x at NA 0.5, 2.0x at NA 0.7 in air. '
        '2PE crossed over facing: 0.50 at NA 0.5, 0.71 at NA 0.7 in air.')
    wide('Depth-of-focus comparison against NA, θ = π/2', os.path.join(hn, 'ratios_z.png'), [
        'The 2CE depth of focus shrinks with NA while the 2PE fringe keeps its width, so their ratio falls.'],
        'The DOF comparison holds at high NA.',
        'DOF of 2CE over 2PE at theta = pi/2: 2.6 at NA 0.5, 1.8 at NA 0.7 in air; 3.5 at 0.5, 1.9 at 0.9 in water. '
        'Scalar and vector within 4%. The 2PE width is that of the central fringe, which does not change with NA, '
        'so the ratio falls as the 2CE focus shortens.')


def green(marks):
    """Lines that show current work is correct, in green: {slide title: (phrases)}."""
    for sl in prs.slides:
        frames = [sh.text_frame for sh in sl.shapes if sh.has_text_frame]
        key = next((f.text for f in frames if f.text in marks), None)
        if key is None:
            continue
        for f in frames:
            for para in f.paragraphs:
                if any(k in para.text for k in marks[key]):
                    for r_ in para.runs:
                        r_.font.color.rgb = GREEN


GREEN = ds.RGBColor.from_string('1E8449')


def red(diff):
    """Slides where current work and the paper differ: the title and the difference in red."""
    for sl in prs.slides:
        frames = [sh.text_frame for sh in sl.shapes if sh.has_text_frame]
        if not any(f.text in diff for f in frames):
            continue
        key = next(f.text for f in frames if f.text in diff)
        for f in frames:
            for para in f.paragraphs:
                if para.text == key or any(k in para.text for k in diff[key]):
                    for r in para.runs:
                        r.font.color.rgb = RED


GLOSS = {   # term: (meaning, sections that use it)
    'NA': ('numerical aperture, n sin α; α is the half-angle of the focusing cone', 'all'),
    'n': ('refractive index of the medium, 1 for air and 1.33 for water', 'all'),
    'L1, L2; O, O′': ('the two lenses and their foci; O is the origin', 'all'),
    'x_c, z_c': ('misalignment of O′ across and along the axis of L1', 'all'),
    'θ': ('angle between the two lens axes (π facing, π/2 crossed)', 'all'),
    'λ_1, λ_2, λ_{2p}': ('2CE wavelengths 750 and 656 nm; 2PE wavelength 700 nm', 'all'),
    '2CE, 2PE': ('two-color excitation, signal ∝ I_1 I_2; two-photon excitation, signal ∝ |U_1 + U_2|^4', 'all'),
    'PSF': ('point spread function: the fluorescence from one point, scaled to its peak', 'all'),
    'Scalar 2CE': ('the paraxial scalar model (small-angle phase, no polarization)', 'all'),
    'Vector 2CE': ('the same signals with the Richards–Wolf focus (exact phase and polarization)', 'overview vector fidelity gaussian polarization pulses cmeeting'),
    'Scalar Debye': ('scalar focus with the exact phase, no polarization', 'vector'),
    'Peak lost': ('drop of the peak of the misaligned PSF, in percent of the aligned peak', 'overview replication vector gaussian delay polarization'),
    '20% tolerance': ('the misalignment x_c or z_c that reduces the 2CE peak by 20%', 'overview vector gaussian polarization'),
    '20% tolerance in time': ('the time delay Δt that reduces the 2CE peak by 20%', 'pulses'),
    'F, C, Q': ('Linfoot’s criteria: fidelity, structural content and correlation quality', 'overview replication fidelity gaussian delay pulses'),
    'α_t': ('truncation parameter of the Gaussian input; 0 is uniform input', 'overview gaussian'),
    'Unpolarized': ('averaged over two perpendicular input polarizations, equal to circular', 'overview vector fidelity gaussian polarization pulses'),
    's–s, p–p': ('both beams polarized perpendicular to (s) or in (p) the plane of the two lens axes', 'polarization'),
    'Δt, φ': ('time delay of beam 2; the phase it adds, φ = ωΔt', 'overview delay pulses'),
    'τ': ('pulse duration: full width at half maximum of the intensity', 'pulses cambaliza cmeeting'),
    'FWHM, DOF': ('full width at half maximum; depth of focus, the FWHM along the axis', 'cambaliza cmeeting'),
    'L1, L2': ('the two focusing lenses; L1 carries λ_1 along z, L2 carries λ_2 and is turned by θ', 'cmeeting'),
    'U_1, U_2; I_1, I_2': ('focused fields of lenses L1 and L2; their intensities |U|^2', 'cmeeting'),
    'Excitation (2PE)': ('|U_1 + U_2|^2, the focused intensity; the 2PE signal is its square (Eq. 6)', 'cmeeting'),
    'ε': ('obstruction ratio of the annular pupil: inner over outer radius, 0.99 here', 'cmeeting'),
    'Δλ': ('gap λ_1 − λ_2 between the 2CE wavelengths, with 1/λ_1 + 1/λ_2 = 1/350 nm fixed', 'cmeeting'),
    'Transform-limited pulse': ('the shortest pulse for its spectrum, with no chirp', 'cmeeting'),
    'h, d_s, g': ('slab half-thickness; mean free path between scattering events; anisotropy ⟨cos⟩ of one scattering', 'cambaliza cmeeting'),
    'ν_a, ν_b, ν_e': ('photon frequencies from the 750 and 656 nm lasers, and of the transition (ν = c/λ)', 'pulses'),
    'p_i(ν)': ('spectral probability density of a photon of laser i', 'pulses'),
    'P(ν_a), δ': ('joint probability of a resonant pair; detuning ν_e − (ν_1 + ν_2) of the transition', 'pulses'),
    'A(P)': ('two-photon amplitude: the sum of the resonant pairs; the 2CE signal is |A|²', 'pulses'),
    'O(P, Δt), t_1, t_2': ('overlap in time of the two pulses; times at which they pass P (t_2 includes Δt)', 'pulses'),
    'N': ('number of wavelengths sampled per pulse', 'pulses'),
    'K': ('fringe wavevector of the two 2PE beams, |K| = 2k sin(θ/2)', 'delay'),
}


GLOSS_TEX = [   # meeting deck on Cambaliza & Saloma (2000): (LaTeX symbol, meaning)
    (r'\mathrm{NA} = n\sin\alpha', 'numerical aperture; α is the half-angle of the focusing cone'),
    (r'n', 'refractive index of the medium: 1 for air, 1.33 for water'),
    (r'\theta', 'angle between the axes of the two lenses: 0 collinear, π/2 crossed, π facing'),
    (r'L_1,\ L_2', 'the two focusing lenses; L₂ is turned by θ about the common focus'),
    (r'\lambda_1,\ \lambda_2,\ \lambda_{2p}', '2CE wavelengths, 750 nm on L₁ and 656 nm on L₂; 2PE wavelength, 700 nm'),
    (r'\Delta\lambda = \lambda_1 - \lambda_2', 'gap between the 2CE wavelengths, with 1/λ₁ + 1/λ₂ = 1/λₑ fixed, λₑ = 350 nm'),
    (r'U_1,\ U_2;\quad I = |U|^2', 'focused fields of L₁ and L₂, and their intensities'),
    (r'F_{2c} = \kappa\, I_1 I_2', 'two-color excitation (2CE) fluorescence'),
    (r"F_{2p} = \kappa'\, |U_1 + U_2|^4", 'two-photon excitation (2PE) fluorescence; |U₁ + U₂|² is the excitation'),
    (r'\varepsilon', 'obstruction ratio of the annular pupil, inner over outer radius: 0.99'),
    (r'\mathrm{FWHM},\ \mathrm{DOF}', 'full width at half maximum of the central peak; depth of focus, the FWHM along the axis'),
    (r'\mathrm{scalar},\ \mathrm{vector}', 'paraxial scalar model (Eqs. 1–6); Richards–Wolf focus, with exact phase and polarization'),
    (r'\tau', 'pulse duration, FWHM of the intensity; transform-limited pulses are the shortest for their spectrum'),
    (r'h,\ d_s,\ g', 'slab half-thickness; mean free path between scattering events; anisotropy, the mean cosine of one scattering'),
]


def glossary_tex():
    """Glossary with each symbol set in LaTeX on the left and its meaning on the right; LaTeX source in the notes."""
    pages = [GLOSS_TEX[i:i + 7] for i in range(0, len(GLOSS_TEX), 7)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''), '')
        t = 1.05
        for tex, meaning in page:
            h = max(equation(s, 0.55, t, 3.0, tex, 17, number=False), 0.36)
            text(s, 3.45, t, 6.1, h, meaning, 14, NAVY, anchor=ds.MSO_ANCHOR.MIDDLE)
            t += h + 0.14
        notes(s, 'Glossary.', ' '.join(f'{tx}: {m}.' for tx, m in page), '\n'.join(tx for tx, _ in page))


def glossary():
    if SECTION == CMEETING:
        return glossary_tex()
    skip = {'Scalar Debye', 'p_i(ν)', 'A(P)', 'N', 's–s, p–p', 'K'}       # terms the meeting deck does not use
    if SECTION == CMEETING:                                    # no misalignment in the Cambaliza study
        skip = {'x_c, z_c', 'PSF', 'L1, L2; O, O′'}
    rows = [f'{t}: {m}.' for t, (m, use) in GLOSS.items()
            if (use == 'all' or (SECTION == MEETING and t not in skip) or SECTION in use.split())
            and not (SECTION == CMEETING and t in skip)]
    pages = [rows[i:i + 9] for i in range(0, len(rows), 9)]
    for k, page in enumerate(pages, 1):
        s = slide('Glossary' + (f' ({k}/{len(pages)})' if len(pages) > 1 else ''), '')
        bullets(s, 0.6, 1.1, 8.9, 4.1, page, 12.5)
        notes(s, 'Glossary.', ' '.join(page))


def checks_slide(part):
    """The physics checks of one part, from scripts/check_lim2002_physics.py."""
    import csv as _csv
    path = os.path.join(FIG, 'physics_checks.csv')
    parts = part if isinstance(part, tuple) else (part,)
    if not os.path.exists(path) or not part:
        return
    rows_ = [r for r in _csv.DictReader(open(path)) if r['part'] in parts]
    if not rows_:
        return
    s = slide('Physics checks', '')
    bullets(s, 0.6, 1.1, 8.9, 4.1, [f"{r['check']}: expected {r['expected']}, obtained {r['obtained']}"
                                    + ('' if r['passed'] == 'yes' else ' (fails)') for r in rows_], 12)
    notes(s, 'Each result is checked against an analytic limit, a symmetry or an independent calculation.',
          ' '.join(f"{r['check']}: {r['obtained']}." for r in rows_))


# ── shared setup slides ──
def geometry():
    side('Geometry: x_c, z_c and θ', os.path.join(FIG, 'fig1_geometry.png'), [
        'Lens L1 focuses beam 1 at O, the origin. Lens L2 focuses beam 2 at O′.',
        'x_c is the misalignment of O′ across the axis of L1, in its focal plane; z_c is the misalignment along that axis.',
        'θ is the angle between the two lens axes: θ = π for lenses facing each other, θ = π/2 for crossed lenses.',
        '2CE: λ_1 = 750 nm and λ_2 = 656 nm. 2PE: both beams at λ_{2p} = 700 nm.'],
        'O prime is misaligned from O by x_c across and z_c along the axis of L1.',
        'The geometry of scalar 2CE. Each result is a loss of peak fluorescence, or a change of shape, when O prime moves away '
        'from O, with facing or crossed lenses.', fw=4.4)


def eqslide(title, takeaway, eqs, main, script, latex, side=None, fig=None, size=17):
    """Equation slide: numbered LaTeX equations, each with its 'where' line; a card or a figure at the right."""
    s = slide(title, takeaway)
    w = 9.0 if side is None and fig is None else (5.9 if fig is None else 5.5)
    t = 1.4
    for tex, wh in eqs:
        h = equation(s, 0.55, t, w, tex, size)
        t += h + 0.06
        if wh:
            t += where(s, 0.6, t, w - 0.6, wh)
        t += 0.1
    if side:
        head, lines = side
        card(s, 6.75, 1.4, 2.75, 3.7, head, RED, lines, 10.5, bulleted=False)
    if fig:
        figure(s, fig, 6.15, 1.35, 3.4, 3.8)
    notes(s, main, script, latex)
    return s


ZB = r'z_b = (x - x_c)\sin\theta + (z - z_c)\cos\theta, \qquad x_b = (x - x_c)\cos\theta - (z - z_c)\sin\theta'
UPAR = r'U(u,v) \propto e^{i n k_0 z}\, 2\int_0^1 J_0(v\rho)\, e^{-iu\rho^2/2}\,\rho\, d\rho'


def scalar_fields():
    eqslide('Field equations: scalar 2CE', 'Each beam is the paraxial scalar Debye field; beam 2 is the same field rotated by θ '
            'and centred at O′.', [
        (UPAR, 'r, z = distance from the focus across and along the axis; ρ = radius in the pupil over its edge.'),
        (r'u = \frac{k_0\,\mathrm{NA}^2 z}{n}, \qquad v = k_0\,\mathrm{NA}\, r, \qquad k_0 = \frac{2\pi}{\lambda}',
         'u, v = axial and transverse optical coordinates; λ = vacuum wavelength; n = refractive index.'),
        (ZB, 'x_b, z_b = coordinates of beam 2, rotated by θ about O′ = (x_c, z_c).'),
        (r'F_{2c} = \kappa_{2c}\, I_1 I_2, \qquad F_{2p} = \kappa_{2p}\, |U_1 + U_2|^4', 'I = |U|^2; 2CE multiplies the two '
         'intensities, 2PE adds the two fields.')],
        'The scalar 2CE model: paraxial fields, beam 2 rotated and shifted, 2CE as a product and 2PE as a sum.',
        'The model of the paper, used for the time-delay study at NA 0.5.',
        '\n'.join((UPAR, r'u = k\,\mathrm{NA}^2 z/n, \quad v = k\,\mathrm{NA}\, r', ZB,
                   r'F_{2c} = \kappa_{2c} I_1 I_2, \qquad F_{2p} = \kappa_{2p} |U_1 + U_2|^4')), size=16)


IM = r'I_m = \int_0^\alpha A(\beta)\sqrt{\cos\beta}\,\sin\beta\; g_m(\beta)\, J_m(kr\sin\beta)\, e^{ikz\cos\beta}\, d\beta'
EVEC = r'\mathbf{E} \propto \left(I_0 + I_2\cos 2\phi,\;\; I_2\sin 2\phi,\;\; 2i I_1\cos\phi\right)'
GM = r'g_0 = 1 + \cos\beta, \qquad g_1 = \sin\beta, \qquad g_2 = 1 - \cos\beta, \qquad \sin\alpha = \mathrm{NA}/n'
UNPOL = r'I = \frac{1}{2}\left(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2\right), \qquad F_{2c} = \kappa_{2c}\, I_1 I_2'
F2PV = r'F_{2p} = \kappa_{2p}\, |\mathbf{E}_1 + \mathbf{E}_2|^4'


def vector_fields():
    side('Focusing by an aplanatic lens', os.path.join(os.path.dirname(FIG), 'bg_focusing_geometry.png'), [
        'Each ray leaves the lens toward the focus at an angle β to the axis, up to the cone half-angle α, sin α = NA/n.',
        'After the lens the polarization is transverse to each ray, so the focused field gains a component along z.',
        'Scalar 2CE replaces the phase kz cos β by its small-angle form and leaves out that component; the Richards–Wolf field '
        'keeps both.'],
        'The aplanatic lens bends each ray toward the focus and turns its polarization with it.',
        'This is what the vector model adds: the exact phase of steep rays and the field component along the axis.', fw=5.5)
    eqslide('Field equations: vector 2CE (Richards–Wolf)', 'The Richards–Wolf field keeps the exact phase of each ray and the '
            'three components of the electric field.', [
        (EVEC, 'E = focal field for input polarized along x; φ = angle about the axis.'),
        (IM, 'β = ray angle; r, z = distance from the focus; A(β) = pupil amplitude, 1 for uniform input; √cos β = aplanatic '
             'factor.'),
        (GM, 'α = half-angle of the focusing cone; m = 0, 1, 2.')],
        'The vector Richards–Wolf field.',
        'At low NA it reduces to the paraxial scalar field.', '\n'.join((EVEC, IM, GM)),
        side=('Against scalar 2CE', ['Exact phase kz cos β instead of its small-angle form.', '',
                                     'Three field components; the one along z grows with NA.', '',
                                     'At low NA it reduces to the paraxial scalar field.']), size=15)
    eqslide('Two beams: placement and signals', 'Beam 2 is the same field rotated by θ and centred at O′; 2CE multiplies '
            'unpolarized intensities, 2PE adds polarized fields.', [
        (ZB, 'x_b, z_b = coordinates of beam 2, rotated by θ about O′ = (x_c, z_c).'),
        (UNPOL, 'ψ = input polarization angle; the average over ψ = 0 and π/2 equals circular polarization.'),
        (F2PV, 'both 2PE beams at 700 nm, polarized perpendicular to the plane of the two lens axes, so their fields add.')],
        'Beam 2 is rotated and shifted; 2CE multiplies unpolarized intensities, 2PE adds polarized fields.',
        'In scalar 2CE, I = |U|^2 and F2p = kappa |U1 + U2|^4.', '\n'.join((ZB, UNPOL, F2PV)), size=16)


def lens_problem():
    s = slide('Largest NA of two crossed lenses', 'Two lenses with crossed axes fit side by side while each cone half-angle is at '
              'most 45°.')
    figure(s, os.path.join(os.path.dirname(FIG), 'na_crossing_limit.png'), 0.45, 1.3, 9.1, 3.2)
    h = equation(s, 0.55, 4.6, 5.2, r'\alpha \leq \theta/2 \;\Leftrightarrow\; \mathrm{NA} \leq n\sin(\theta/2)', 17)
    bullets(s, 5.9, 4.6, 3.6, 0.7, ['Any lens: NA = n sin α ≤ n, so NA < 1 in air. θ = π/2: NA 0.71 in air, 0.94 in water; above '
                                     'NA 0.71 our crossed lenses are in water.'], 11)
    notes(s, 'Crossed lenses fit up to NA n sin(theta/2).',
          'Each lens fills a cone of half-angle alpha, sin alpha = NA/n. Two cones meeting at a right angle overlap once their '
          'half-angles exceed 45 degrees: NA 0.71 in air, 0.94 in water. Above NA 0.71 the crossed lenses are computed in '
          'water (n = 1.33). A medium raises the NA but not the cone angle, so in water at NA 0.9 the crossed focus has the '
          'shape of the focus in air at NA 0.68 (0.9/1.33), 1.33 times smaller.', r'\mathrm{NA} \le n \sin(\theta/2)')


FCQ = (r'F = 1 - \frac{\langle (t-a)^2 \rangle}{\langle t^2 \rangle}, \qquad C = \frac{\langle a^2 \rangle}{\langle t^2 \rangle}, '
       r'\qquad Q = \frac{\langle t\, a \rangle}{\langle t^2 \rangle}')
SPOT = r'\tilde{x} = \frac{x_c\,\mathrm{NA}}{\lambda}, \qquad \tilde{z} = \frac{z_c\,\mathrm{NA}^2}{n\lambda}'


def linfoot():
    eqslide('Linfoot’s criteria', 'Fidelity, structural content and correlation quality compare the misaligned PSF with the '
            'aligned PSF over the window.', [
        (FCQ, 't = aligned PSF; a = misaligned PSF, each scaled to its own peak; ⟨ ⟩ = mean over the 100 × 100 x–z window.'),
        (r'2Q - C = F', 'each criterion is 1 when a = t.'),
        (r'\Delta F = F_{\mathrm{vector}} - F_{\mathrm{scalar}} \quad (\mathrm{same\ NA})',
         'the difference maps compare vector and scalar 2CE at the same NA, so they isolate the exact phase and polarization.')],
        'Linfoot’s three criteria compare the misaligned PSF with the aligned one.',
        'Shown as surfaces over the offset of O prime, as in Figs. 5–6 of the paper, then as differences from scalar 2CE.',
        '\n'.join((FCQ, r'2Q - C = F', r'\Delta F = F_{vector} - F_{scalar}')),
        side=('F, C and Q', ['F, fidelity: overall similarity; 1 − normalized mean-squared error.', '',
                             'C, structural content: relative energy; rises above 1 for a broader PSF.', '',
                             'Q, correlation quality: overlap of the two PSFs.']), size=16)


CASES = [('2ce_pi', '2CE, θ = π'), ('2ce_pi2', '2CE, θ = π/2'), ('2pe_pi', '2PE, θ = π'), ('2pe_pi2', '2PE, θ = π/2')]
LINF = {   # (case, criterion): what the map shows, with uniform input
    ('2ce_pi', 'F'): 'At high NA the region F ≥ 0.8 is shorter along the axis than the scalar 2CE region (red dotted) and '
                     'slightly wider across it: the vector focus is less elongated, so a misalignment along the axis changes '
                     'the shape sooner.',
    ('2ce_pi', 'C'): 'C rises as O′ moves away. At high NA the region C ≤ 1.2 is shorter along the axis than the scalar 2CE '
                     'region, as for F.',
    ('2ce_pi', 'Q'): 'Near the aligned point the region Q ≥ 0.8 changes little with NA. Farther out Q rises again, because the '
                     'misaligned PSF, scaled to its own peak, is broad and covers the aligned one.',
    ('2ce_pi2', 'F'): 'With crossed beams the region F ≥ 0.8 becomes narrower in x_c and longer in z_c at high NA: a '
                      'misalignment in x_c moves O′ along beam 2, whose focus is shorter in the vector model.',
    ('2ce_pi2', 'C'): 'With crossed beams C stays within 20% up to about one spot unit in x_c; at high NA this range narrows.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0; the band changes little with NA near the aligned point.',
    ('2pe_pi', 'F'): 'The 2PE region F ≥ 0.8 is set by the standing-wave fringes, whose spacing λ_{2p}/2n does not depend on '
                     'NA, and changes little with NA.',
    ('2pe_pi', 'C'): 'C stays within 20% for x_c up to about 0.35 spot units (x_c NA/λ) and changes little with NA.',
    ('2pe_pi', 'Q'): 'Q ≥ 0.8 near the aligned point and again near the next fringes; both change little with NA.',
    ('2pe_pi2', 'F'): 'With crossed beams the regions F ≥ 0.8 repeat with the fringes, one wavelength apart, and change little '
                      'with NA.',
    ('2pe_pi2', 'C'): 'The regions C ≤ 1.2 follow the tilted fringes; at high NA they close into loops around the aligned point.',
    ('2pe_pi2', 'Q'): 'Q ≥ 0.8 near the aligned point and near the next fringes, one wavelength away; at high NA the central '
                      'region tilts with the fringes.',
}
LINF_G = {   # the same maps with Gaussian input (α_t = 4)
    ('2ce_pi', 'F'): 'At high NA the region F ≥ 0.8 is slightly shorter along the axis than the scalar 2CE region, by less than '
                     'with uniform input: the Gaussian focus is closer to paraxial.',
    ('2ce_pi', 'C'): 'The region C ≤ 1.2 is an ellipse; at high NA it is shorter along the axis than the scalar 2CE region.',
    ('2ce_pi', 'Q'): 'Q stays above 0.8 between the two lines, over the whole computed range along the axis; the lines change '
                     'little with NA.',
    ('2ce_pi2', 'F'): 'With crossed beams the region F ≥ 0.8 changes less with NA than with uniform input.',
    ('2ce_pi2', 'C'): 'In scalar 2CE the region C ≤ 1.2 is bounded in x_c and open along z_c; at high NA the vector region closes '
                      'into an ellipse.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0, about ±0.3 spot units wide, which changes little with NA.',
    ('2pe_pi', 'F'): 'As with uniform input, the region F ≥ 0.8 is set by the standing-wave fringes and changes little with NA.',
    ('2pe_pi', 'C'): 'C stays within 20% for x_c up to about 0.4 spot units (x_c NA/λ) and changes little with NA.',
    ('2pe_pi', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0, about ±0.15 λ/n wide, which changes little with NA.',
    ('2pe_pi2', 'F'): 'With crossed beams the regions F ≥ 0.8 repeat with the fringes, one wavelength apart, and change little '
                      'with NA.',
    ('2pe_pi2', 'C'): 'The regions C ≤ 1.2 follow the tilted fringes as diagonal bands.',
    ('2pe_pi2', 'Q'): 'Q ≥ 0.8 near the aligned point and near the next fringes, one wavelength apart.',
}
LEV = {'F': 'F = 0.8', 'C': 'C = 1.2', 'Q': 'Q = 0.8'}
NAME = {'F': 'Fidelity', 'C': 'Structural content', 'Q': 'Correlation quality'}


SURF = {   # (case, criterion): what the surfaces show, scalar 2CE at NA 0.5 against vector 2CE at NA 0.7 and 0.9
    ('2ce_pi', 'F'): 'The peak of F around the aligned point narrows along z_c as NA grows, and F falls below −1 over most of the '
                     'misalignments: the spot is smaller, so the same misalignment changes its shape more.',
    ('2ce_pi', 'C'): 'C rises above 1 as O′ moves away; the region near 1 shrinks to a small well around the aligned point at '
                     'high NA.',
    ('2ce_pi', 'Q'): 'Q dips next to the aligned point and returns toward 1 farther out; the pattern becomes finer as NA '
                     'grows.',
    ('2ce_pi2', 'F'): 'With crossed beams F stays high along x_c in scalar 2CE; at NA 0.9 the high region closes in x_c as well.',
    ('2ce_pi2', 'C'): 'C stays near 1 in a band around z_c = 0; at high NA the band becomes uneven along x_c.',
    ('2ce_pi2', 'Q'): 'Q ≥ 0.8 in a band around z_c = 0 in scalar 2CE; at NA 0.9 the band becomes a closed region.',
    ('2pe_pi', 'F'): 'The 2PE F is set by the standing-wave fringes; at high NA the region near the aligned point narrows and the '
                     'side structure becomes finer.',
    ('2pe_pi', 'C'): 'C rises steeply as O′ moves across the axis; at high NA the well around the aligned point narrows.',
    ('2pe_pi', 'Q'): 'Q dips near the aligned point and returns toward 1 at the next fringes; the dip narrows as NA grows.',
    ('2pe_pi2', 'F'): 'With crossed beams F peaks at each bright fringe, about one wavelength apart in x_c; the peaks stay at the '
                      'same places as NA grows.',
    ('2pe_pi2', 'C'): 'C follows the tilted fringes and rises quickly away from them.',
    ('2pe_pi2', 'Q'): 'Q is high near the aligned point and near the next fringes, one wavelength apart.',
}


def linfoot_maps(suf, tag):
    """For each case and criterion: the 3D surfaces (scalar 2CE, NA 0.7, NA 0.9), then the difference from scalar 2CE."""
    for case, lab in CASES:
        for key in 'FCQ':
            t = f'{NAME[key]}{tag}: {lab}'
            if suf:
                wide(f'{key}: uniform against Gaussian input, {lab}', SL(f'linfoot3d_{key}_{case}_input.png'), [
                    'Scalar 2CE at NA 0.5 with uniform input (left) and Gaussian input, α_t = 4 (right): the effect of the '
                    'Gaussian input alone, before NA is raised.'],
                    f'{lab}: {NAME[key].lower()}, uniform against Gaussian input.',
                    'Same model, NA, window and offsets; only the pupil amplitude changes.')
            side3 = ('With the Gaussian input the surfaces are smoother and change less with NA than with uniform input, '
                     'because the dim pupil edge keeps the focus closer to paraxial.') if suf else SURF[(case, key)]
            wide(t, SL(f'linfoot3d_{key}_{case}{suf}.png'), [side3 + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'pi2' in case else '')],
                 f'{lab}: {NAME[key].lower()} against the misalignment, scalar 2CE and vector 2CE.',
                 'Surfaces over (x_c, z_c) on the axes of Figs. 5–6, in units of lambda_1 (2CE) or lambda_2p (2PE): scalar 2CE at '
                 'NA 0.5, then vector 2CE at NA 0.7 and 0.9. Crossed lenses at NA 0.9 are in water (n = 1.33).')
            wide(f'{key}{tag}, vector − scalar: {lab}', SL(f'linfoot_diff_{key}_{case}{suf}.png'), [
                f'Δ{key} = {key} of vector 2CE minus {key} of scalar 2CE at the same NA: red where the vector value is higher, blue '
                'where it is lower; black line: no difference. The difference grows from NA 0.7 to NA 0.9.'],
                f'{lab}: where vector and scalar {NAME[key].lower()} differ.',
                'Both computed at the same NA, so the difference is the effect of the exact phase and polarization alone. The '
                'colour scale covers 98 percent of the points; the arrows mark values beyond it.')


FIGTXT = {
    (2, 'a'): ('2CE, θ = π', 'From scalar 2CE at NA 0.5 to vector 2CE at NA 0.9 the aligned 2CE spot becomes a little over half '
               'as wide and about a third as long, so it is less elongated.'),
    (2, 'b'): ('2PE, θ = π', 'The 2PE standing wave keeps its fringe spacing, λ_{2p}/2, while the spot around it shrinks; at '
               'NA 0.9 it holds a few fringes.'),
    (2, 'c'): ('2CE, θ = π/2', 'With crossed beams the aligned 2CE spot is set by the widths of the two beams; it shrinks in both '
               'directions as NA grows.'),
    (2, 'd'): ('2PE, θ = π/2', 'The 2PE PSF keeps its tilted fringes and shrinks as NA grows; the weak 1% halo of scalar 2CE disappears.'),
    (3, 'a'): ('2CE, θ = π', 'With O′ at (0.4, 1.0) µm the 2CE spot still forms between O and O′; at high NA it is smaller and '
               'tilted toward O′.'),
    (3, 'b'): ('2PE, θ = π', 'At NA 0.9 the misaligned 2PE spot breaks into a few separate fringes between O and O′.'),
    (3, 'c'): ('2CE, θ = π/2', 'With crossed beams the misaligned 2CE peak follows beam 2 along z; at NA 0.9 it also moves toward O′ in x.'),
    (3, 'd'): ('2PE, θ = π/2', 'The misaligned 2PE PSF breaks into separate pieces along the fringes; at NA 0.9 a second maximum appears near O.'),
    (4, 'a'): ('2CE, θ = π', 'The misalignments that keep 80% of the 2CE peak reach about ±2.7 λ_1 along the axis in scalar 2CE and '
               'about ±0.7 λ_1 at NA 0.9.'),
    (4, 'b'): ('2PE, θ = π', 'The 2PE peak map shrinks in the same way; the standing-wave fringes make it vary slightly along z.'),
    (4, 'c'): ('2CE, θ = π/2', 'In scalar 2CE the peak barely depends on x_c; with vector 2CE at high NA the region that keeps the '
               'peak closes in x_c as well as in z_c.'),
    (4, 'd'): ('2PE, θ = π/2', 'The tilted bands of the 2PE peak map, from interference, narrow as NA grows.'),
}


def maps(suf, tag):
    for (no, t), (lab, line) in FIGTXT.items():
        where = {2: 'aligned foci', 3: 'O′ at (0.4, 1.0) µm', 4: 'peak against the misalignment (x_c, z_c)'}[no]
        if suf and no == 4:
            line = ('With the Gaussian input the region that keeps the peak is larger than with uniform input at the same NA, '
                    'and it shrinks in the same way as NA grows.')
        elif suf:
            line = ('With the Gaussian input the spot is wider and longer than with uniform input at the same NA, and it shrinks '
                    'in the same way as NA grows.')
        if suf:
            wide(f'Fig. {no}({t}), uniform against Gaussian input: {lab}', SL(f'map_fig{no}{t}_input.png'), [
                'Scalar 2CE at NA 0.5, the case of the paper, with uniform input (left) and Gaussian input, α_t = 4 (right): the '
                'effect of the Gaussian input alone, before NA is raised.'],
                f'Fig. {no}({t}): the effect of the Gaussian input at NA 0.5.',
                'Same model, NA and axes; only the pupil amplitude changes. Contours in percent of the peak; orange: 50 percent.')
        wide(f'Fig. {no}({t}) against NA{tag}: {lab}', SL(f'map_fig{no}{t}{suf}.png'), [line + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'π/2' in lab else '')],
             f'Fig. {no}({t}): scalar 2CE at NA 0.5 against vector 2CE at NA 0.7 and 0.9.',
             f'Fig. {no}({t}), {lab}, {where}: scalar 2CE at NA 0.5 (the replication), then vector 2CE at NA 0.7 and 0.9, on the '
             'axes of the paper. Contours in percent of the peak; orange: 50 percent.'
             + (' At theta = pi/2, NA 0.9 is in water (n = 1.33): the two lenses do not fit in air above NA 0.71.'
                if 'π/2' in lab else ''))
        wide(f'Fig. {no}({t}), scalar and vector at the same NA{tag}: {lab}', SL(f'map_fig{no}{t}_samena{suf}.png'), [
            'Scalar 2CE and vector 2CE at the same NA, 0.7 and 0.9: the difference between the two models alone, without the '
            'change of NA.' + (' At θ = π/2, NA 0.9 is in water (n = 1.33): two crossed lenses do not fit in air above NA 0.71.' if 'π/2' in lab else '')],
            f'Fig. {no}({t}): scalar against vector at equal NA.', 'Same NA, same axes; contours in percent of the peak.')


PEAK = [
    ('2CE, θ = π/2, x_c = 1.33 λ_1', 'We move O′ by 1.33 λ_1 across the axis of L1, which is along the axis of beam 2.',
     'At NA 0.5 the 2CE peak drops by about 12%; scalar 2CE gives 11%.',
     'The loss grows to about 45% at NA 0.7: the misalignment is along beam 2, so it follows the length of its focus, which '
     'shrinks as 1/NA^2.'),
    ('2CE, θ = π, x_c = 0.37 λ_1', 'We move O′ by 0.37 λ_1 across the axis, with the lenses facing each other.',
     'At NA 0.5 the 2CE peak drops by 17%; scalar 2CE gives 20%.',
     'At NA 0.9 the same misalignment reduces the peak by about 42%: the spot narrows as 1/NA, so the same shift is a larger '
     'part of it.'),
    ('2PE, θ = π/2, x_c = 0.5 λ_{2p}', 'We move O′ by half a wavelength across the axis of L1, with crossed beams at 700 nm.',
     'At NA 0.5 the 2PE peak drops by 26%; scalar 2CE gives 30%.',
     'The loss grows to about 44% at NA 0.7, as the spot shrinks while the fringes keep their spacing. Below NA 0.3 the grid '
     'of misalignments is coarser than the fringes, so those points are left out.'),
    ('2CE, θ = π, z_c = 2.7 λ_1', 'We move O′ by 2.7 λ_1 along the axis, with the lenses facing each other.',
     'At NA 0.5 the 2CE peak drops by 22%; scalar 2CE gives 20%.',
     'The loss rises to about 70% at NA 0.7 and 95% at NA 0.9: the length of the focus shrinks as 1/NA^2, faster than its '
     'width.'),
    ('2CE, θ = π/2, z_c = 2.7 λ_1', 'We move O′ by 2.7 λ_1 along the axis of L1, with crossed beams.',
     'At NA 0.5 the 2CE peak drops by 36%; scalar 2CE gives 30%.',
     'The loss rises to about 90% at NA 0.7: the misalignment slides beam 2 along the length of beam 1. Below NA 0.2 the grid '
     'of misalignments is too coarse for the long focus, so those points are left out.'),
]
PEAK_G = [(51, 'about 6%'), (24, 'about 8%'), (38, 'about 14%'), (72, 'about 11%'), (75, 'about 19%')]
LEGEND = ('Blue: vector 2CE; red: scalar 2CE; star: the loss reported at NA 0.5; grey: NA above 0.5, where the paraxial model '
          'is expected to break down.')


def peaks(suf):
    for k, (lab, how, low, high) in enumerate(PEAK, 1):
        if suf:
            v9, v5 = PEAK_G[k - 1]
            items = [how, f'With α_t = 4 the peak drops by {v5} at NA 0.5, about half the loss with uniform input, and by '
                          f'about {v9}% at NA 0.9.', 'The Gaussian focus is larger, so the same misalignment is a smaller part of it.']
            name = f'Peak lost, Gaussian input: {lab}'
        else:
            items, name = [how, low, high], f'Peak lost against NA: {lab}'
        if 'π/2' in lab:
            items.append('Above NA 0.71 the two lenses do not fit in air; open circles: the lenses in water (n = 1.33).')
        side(name, SL(f'peaklost_{k}{suf}.png'), items, f'{name}.', LEGEND)


DECIDE = ['Polarization of the two beams: keep unpolarized (circular) beams, or account for linear polarization.',
          'Optical pulses: weight the photon pairs by the dye’s absorption (which dye, which band).']

SUMMARIES = {   # section: (main point, supporting, supporting, speaker script); the overview shows them all
    'overview': (
        'At high NA the 2CE alignment tolerances shrink with the size of the focus: with facing lenses, as 1/NA across the axis '
        'and 1/NA^2 along it.',
        'Rebuilt from its equations, scalar 2CE reproduces the paper: the 2CE PSF is more robust against misalignment than the 2PE '
        'PSF, most of all with crossed beams.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.45, which validates it there; a Gaussian input makes the '
        'tolerances about 1.4 times larger.',
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments along the axis than scalar 2CE predicts.',
        'A time delay between continuous beams leaves the 2CE PSF unchanged but shifts the 2PE fringes, with the same effect as a '
        'misalignment of cΔt/n in space.',
        'With vector fields, the alignment tolerances follow the width and length of the focus as NA grows. The paper is '
        'reproduced, its scalar model agrees with the vector one where the paper uses it, a Gaussian input loosens the tolerances, '
        'and a time delay acts on 2PE through its fringes while 2CE does not change.'),
    'replication': (
        'Rebuilt from its equations, the scalar 2CE model reproduces the six figures and, within a few percent, the losses '
        'reported in the paper.',
        'What holds: the 2CE PSF is more robust against misalignment than the 2PE PSF, most of all when the two beams cross at '
        'θ = π/2.',
        'What differs: C and Q are swapped in Figs. 5–6, Eq. (2) has to be applied as a rotation in space, Figs. 6(c)–(d) are '
        'most likely θ = 0, and the reported losses differ from ours by up to 3 points (20% against 18%, 30% against 27%).',
        'The figures and losses are reproduced, and the conclusion holds. Four things differ: the C and Q labels, the rotation as '
        'printed, the caption of the bottom row of Fig. 6, and the reported losses by a few points.'),
    'vector': (
        'With vector 2CE the alignment tolerances shrink as NA grows, following the size of the focus.',
        'With facing lenses the 20% tolerances shrink as NA^{−0.97} across the axis and NA^{−2.12} along it; with crossed lenses '
        'both shrink as about NA^{−2.1}.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.45, which validates it there; above it, its small-angle phase '
        'overestimates the tolerance along the axis, and in water this starts at 1.33 times the NA in air.',
        'Recomputed with the vector focus, the tolerances follow the width and length of the focus. The paraxial model agrees to '
        'five percent up to NA 0.45; above that, its longer focus overestimates the tolerance along the axis.'),
    'fidelity': (
        'At high NA the 2CE PSF keeps its shape over a smaller range of misalignments than scalar 2CE predicts.',
        'With facing lenses the region of high fidelity narrows along z_c from scalar 2CE to vector NA 0.9; with crossed lenses '
        'it also closes in x_c.',
        'For 2PE, Linfoot’s criteria are set by the fringes, whose spacing does not depend on NA; the vector−scalar differences '
        'follow the fringes.',
        'Linfoot’s criteria of the paper, as surfaces against the misalignment for scalar 2CE and vector 2CE at NA 0.7 and 0.9, '
        'and as differences from scalar 2CE at the same NA.'),
    'gaussian': (
        'With a Gaussian input (α_t = 4) the alignment tolerances are about 1.4 times larger than with uniform input.',
        'The dim edge of the pupil removes the high-angle rays, so the focus is wider and longer; at NA 0.5 the same '
        'misalignments cost about half the peak they cost with uniform input.',
        'Scalar 2CE agrees with vector 2CE within 5% up to NA 0.525, against 0.45 with uniform input.',
        'With a Gaussian input the high-angle rays are dim, so the focus behaves like a lower NA: larger tolerances, and a '
        'paraxial model that holds to a higher NA.'),
    'delay': (
        'A time delay Δt between continuous beams is a phase ωΔt: it leaves the 2CE PSF unchanged and shifts the 2PE fringes, '
        'as a misalignment of cΔt/n does.',
        'The 2CE signal I_1 I_2 depends on intensities, which do not carry the phase; for 2PE at θ = π/2, half an optical period '
        '(1.17 fs) puts the centre on a dark fringe and loses 29% of the peak.',
        'The 2PE loss of a misalignment is mainly this fringe phase: the matching time delay brings the loss of a 0.5 λ_{2p} '
        'misalignment from 26% to about 1%. 2CE has no fringes, so a time delay cannot change its loss.',
        'Delaying a continuous beam multiplies its field by a phase. Two-color excitation multiplies intensities, so the phase '
        'drops out. Two-photon excitation adds fields, so the phase moves its fringes, by the same amount as a misalignment of '
        'c Delta t over n at theta = pi/2.'),
}
PART_TITLE = {'replication': 'Part 1: Replication of scalar 2CE', 'vector': 'Part 2: Vector 2CE, uniform input',
              'fidelity': 'Part 3: Linfoot’s criteria against NA', 'gaussian': 'Part 4: Vector 2CE, Gaussian input',
              'delay': 'Part 5: Time delay'}


# ══ sections ═════════════════════════════════════════════════════════════
if SECTION == 'overview':
    title('Progress Report', 'Two-color excitation: scalar 2CE, vector 2CE, time delay and optical pulses')
    words('Things done', [
        'Part 1: Replication of scalar 2CE.',
        '– Rebuilt from its equations, the model reproduces the figures and reported losses: 2CE is more robust against '
        'misalignment than 2PE, most of all with crossed beams.',
        'Part 2: Vector 2CE, uniform input, against NA.',
        '– The alignment tolerances shrink as NA grows, as 1/NA across the axis and 1/NA^2 along it; scalar 2CE agrees within 5% '
        'up to NA 0.45. Crossed lenses above NA 0.71 do not fit in air and are computed in water.',
        'Part 3: Linfoot’s criteria against NA.',
        '– At high NA the 2CE PSF keeps its shape over a smaller range of misalignments than scalar 2CE predicts.',
        'Part 4: Vector 2CE, Gaussian input.',
        '– The tolerances are about 1.4 times larger than with uniform input, and scalar 2CE holds to NA 0.525.',
        'Part 5: Time delay between continuous beams.',
        '– A time delay leaves the 2CE PSF unchanged and shifts the 2PE fringes, as a misalignment of cΔt/n does.',
        'Part 6: Polarization, s and p.',
        '– At high NA linear polarization changes the 2CE results across the axis with facing lenses, and decides whether '
        'crossed-beam 2PE interferes; results along the axis do not change.',
        'Part 7: Optical pulses and time delay.',
        '– A time delay lowers 2CE because the photon pairs that reach the transition add out of phase where the two pulses do '
        'not arrive together; with crossed lenses 20% of the peak is lost at a delay of 0.4 τ.'],
        'Seven parts, each with its main result.',
        ' '.join(SUMMARIES[k][3] for k in PART_TITLE), size=11.5)
    words('New since the last meeting', [
        'Photon pairs: the probability of each pair of wavelengths, one from each pulse, that reaches the 350 nm transition, '
        'derived in closed form. Shorter pulses bring in more pairs (Part 7).',
        'Pulsed 2CE counts those pairs: the PSF is the continuous-beam PSF times the probability that a pair reaches the '
        'transition, times the overlap in time of the two pulses. At equal pulse energy, shorter pulses give no more signal '
        '(Part 7).',
        'Time delay between pulses: with crossed lenses the PSF keeps its shape and loses 20% of its peak at a delay of 0.4 τ; '
        'with facing lenses and 10–20 fs pulses the PSF moves along the axis with the plane where the pulses meet (Part 7).',
        'Crossed lenses above NA 0.71 are computed in water, so the crossed-lens results continue to NA 0.9 (Parts 2–4).',
        'Air and water at the same NA: the same power laws; in water the focus is about 1.4 times longer, and the departure '
        'from the paraxial law starts at 1.33 times the NA (Part 2).',
        'Scalar 2CE and vector 2CE compared at the same NA, 0.7 and 0.9, which shows the difference between the two models '
        'alone (Parts 2–4 and 7).'],
        'Photon pairs, pulsed 2CE with a time delay, and crossed lenses in water.',
        'Since the last meeting: the photon-pair calculation, the pulsed PSF with a time delay, water for crossed lenses, '
        'air against water at the same NA, and scalar against vector at the same NA.', size=13)
    words('Next steps: points to settle', DECIDE, 'Two points to settle before the next results.',
          'The polarization of the beams, and the dye that weights the photon pairs.')
    words('To consider: polarization of the two beams', [
        'Polarization is the direction in which a beam’s electric field oscillates; it is always perpendicular to the direction '
        'the beam travels.',
        'The two lens axes lie in one plane (the x–z plane of the geometry). s polarization: the field is perpendicular to that '
        'plane (out of the page). p polarization: the field lies in that plane. s–s and p–p mean both beams are s, or both p.',
        'So far each 2CE beam is unpolarized (averaged over both directions, the same as circular polarization), which gives a '
        'round focal spot.',
        'At high NA a linearly polarized spot is wider along its field, so results across the axis depend on the direction of '
        'the misalignment. For 2PE with crossed beams, s–s fields are parallel and interfere; p–p fields are perpendicular and '
        'barely interfere.',
        'To decide: keep unpolarized beams, or account for linear (s or p) polarization.'],
        'Polarization is the direction of the field; s is perpendicular to the plane of the lens axes, p lies in it.',
        'The definitions of s and p, and why the choice matters at high NA.', size=12.5)
    wide('To consider: polarization, focal spot', SL('polarization_spot.png'), [
        'One beam at focus, across x. At high NA the focused spot is wider along the polarization than across it, so results '
        'across the axis depend on how the misalignment is oriented.'],
        'At high NA the spot depends on the polarization.',
        'Blue: field along y; red: field along x. At NA 0.5 the two nearly coincide; at NA 0.9 the spot is about 1.35 times '
        'wider along the polarization.')
    RATE = r'\text{rate} \propto \int g(\Omega)\, \bigl|\tilde{P}(\Omega)\bigr|^2 d\Omega, \qquad P(t) = E_1(t)\, E_2(t)'
    eqslide('To consider: weighting the pairs by the dye', 'The dye’s absorption g weights each pair by its total frequency; a '
            'flat g gives the time-overlap signal used so far.', [
        (RATE, 'Ω = ω_1 + ω_2 = total frequency of a pair; g(Ω) = absorption of the dye; P̃ = spectrum of the product field.'),
        (r'g = \text{const.}: \quad \int g\,|\tilde{P}|^2 d\Omega \;\propto\; \int I_1(t)\, I_2(t)\, dt',
         'Parseval: a flat absorption gives exactly the current signal (checked numerically: equal to 6 digits).'),
        (r'\text{equal Gaussian pulses: } |\tilde{P}(\Omega)|^2 \propto e^{-(\Omega-\Omega_0)^2 \tau^2/8\ln 2}\ \text{at every point}',
         'the pair spectrum has the same shape everywhere, so weighting scales the signal by one factor and leaves the PSF '
         'shapes and tolerances unchanged.')],
        'Weighting by the dye changes how much signal there is, not the shape of the PSF, for equal Gaussian pulses.',
        'The weighted rate integrates the dye absorption against the spectrum of the product field.', RATE, size=14)
    wide('To consider: signal kept by the dye weighting', SL('pulse_pairs_weight.png'), [
        'Signal kept when the dye absorbs in a Gaussian band around 350 nm, relative to a flat band. At 100 fs nearly all '
        'pairs fall within a 10 nm band; at 20 fs about 60% do, and at 10 fs about 35%. To decide: which dye, and so which g.'],
        'Short pulses waste pairs outside the dye band.', 'Gaussian absorption bands of FWHM 2, 5, 10 and 20 nm centred at 350 nm.')

elif SECTION == 'replication':
    at = len(prs.slides)
    try:
        runpy.run_path(os.path.join(HERE, 'make_lim2002_replication_deck.py'), run_name='__main__')
    except SystemExit:
        pass

elif SECTION == 'vector':
    title('Part 2: Vector 2CE, uniform input', 'The results of scalar 2CE with the Richards–Wolf focus, NA 0.03 to 1.2')
    summary(*SUMMARIES['vector'])
    geometry(); vector_fields()
    maps('', '')
    for key, lab, line in (
            ('pi', 'θ = π', 'Across the axis the tolerance falls as NA^{−0.97}, close to 1/NA, as the width of the spot does; '
             'along the axis it falls as NA^{−2.12}, close to 1/NA^2, as its length does.'),
            ('pi2', 'θ = π/2', 'With crossed beams both tolerances fall as about NA^{−2}: a misalignment in x_c is along the axis '
             'of beam 2 and one in z_c is along the axis of beam 1, so both follow the length of the focus. Above NA 0.71 the '
             'lenses are in water (open circles), where the focus is 1.33 times longer at the same NA.')):
        wide(f'20% tolerances against NA, {lab}', SL(f'tolerance_{key}.png'), [
            'The tolerance is the misalignment of O′ that reduces the 2CE peak by 20%. ' + line],
            f'At {lab} the 20% tolerances shrink as a power of NA.',
            'Blue: vector 2CE; red: scalar 2CE; star: the tolerance reported at NA 0.5; grey: NA above 0.5, where the paraxial model is '
            'expected to break down.')
    wide('Scalar 2CE against vector 2CE, 20% tolerances', SL('deviation.png'), [
        'The difference between the 20% tolerances of scalar and vector 2CE passes 5% at NA 0.45 and 10% at NA 0.6 along the '
        'axis, and with crossed beams in both directions. Across the axis at θ = π it stays within 5% up to NA 0.8. With '
        'crossed lenses in water (dashed), the difference at NA 0.9 is 14%, as in air at NA 0.68: it follows the cone angle.'],
        'Scalar 2CE is within 5% up to NA 0.45; along the axis it departs first.',
        'The paraxial focus is longer than the vector one, so it overestimates the tolerance along the axis. Across the axis the two '
        'differ through polarization, which is small up to NA 0.8. The vertical line is NA 0.5, the value used in scalar 2CE.')
    wide('20% tolerances in water, θ = π', SL('tolerance_pi_n1.33.png'), [
        'In water (n = 1.33) the tolerances follow the same power laws. Scalar 2CE departs by 5% at NA 0.6 and 10% '
        'at NA 0.8, 1.33 times the values in air: the difference is set by the angle of the cone, sin α = NA/n.'],
        'In water scalar 2CE holds to 1.33 times the NA it holds to in air.',
        'The same 20% tolerances in water, up to NA 1.2.')
    for key, lab, line in (
            ('pi', 'θ = π', 'Facing lenses, vector 2CE, uniform input. At the same NA the tolerance across the axis is the same '
             'in air and water, and along the axis it is about 1.4 times larger in water. Fitted over NA 0.5–0.7, where both '
             'media are computed, the power laws are the same: close to 1/NA across the axis and 1/NA^2 along it. Air is a '
             'little steeper along the axis, because its wider cone departs from the paraxial law sooner.'),
            ('pi2', 'θ = π/2', 'Crossed lenses, vector 2CE, uniform input; in air the lenses fit up to NA 0.71. At the same NA '
             'both tolerances are about 1.4 times larger in water, because both follow the length of the focus. Fitted over '
             'NA 0.5–0.7 both media follow about 1/NA^2; air is a little steeper.')):
        wide(f'20% tolerances in air and water, {lab}', SL(f'air_water_{key}.png'), [line],
             'Water keeps the power laws and moves the high-NA departure to 1.33 times the NA.',
             'Filled: air; open: water. Lines: power-law fits over NA 0.5 to 0.7, solid for air and dashed for water. At the '
             'same NA the cone in water is narrower, sin alpha = NA/n, so the focus is about as wide and 1.33 times longer.')
    lens_problem()
    peaks('')
    wide('Profiles at NA 0.8, θ = π', SL('profiles_pi_na0.8.png'), [
        'The aligned 2CE spot at NA 0.8 with three foci. Across the axis the three agree. Along the axis the paraxial spot is '
        'longer, while the scalar Debye focus, which keeps the exact phase but no polarization, matches the vector one: the '
        'small-angle phase causes the difference.'],
        'The small-angle phase, not polarization, lengthens the paraxial focus.',
        'Three foci of the same beams: paraxial scalar, scalar Debye with the exact phase kz cos beta, and vector.')
    wide('Check: scalar and vector focus at NA 0.5', SL('onaxis_scalar_vector_na0.5.png'), [
        'At NA 0.5, the value used in scalar 2CE, the scalar and vector foci of one beam nearly coincide along the axis, for uniform '
        'input and for a Gaussian input (α_t = 4).'],
        'At NA 0.5 the two foci nearly coincide.', 'A single beam at 750 nm, intensity along the axis.')

elif SECTION == 'fidelity':
    title('Part 3: Linfoot’s criteria against NA', 'Linfoot’s criteria (F, C and Q) of the misaligned PSF: scalar 2CE, and vector 2CE at NA 0.7 and 0.9')
    summary(*SUMMARIES['fidelity'])
    geometry(); vector_fields(); linfoot()
    linfoot_maps('', '')

elif SECTION == 'gaussian':
    title('Part 4: Vector 2CE, Gaussian input', 'Both lenses filled by a Gaussian beam, truncation parameter α_t = 4')
    summary(*SUMMARIES['gaussian'])
    geometry(); vector_fields()
    eqslide('Gaussian input: the pupil of both beams', 'Each lens is filled by a Gaussian beam with α_t = 4, which the aperture barely truncates; the '
            'same pupil amplitude on both lenses and for both wavelengths.', [
        (r'A(\beta) = \exp\left(-\alpha_t\, \frac{\sin^2\beta}{\sin^2\alpha}\right), \qquad \sin\alpha = \mathrm{NA}/n',
         'A(β) = pupil amplitude in the Richards–Wolf integrals; α_t = truncation parameter; 0 is uniform input.'),
        (r'A(\rho) = e^{-\alpha_t \rho^2}', 'the same amplitude in scalar 2CE, with ρ = radius in the pupil over its edge.'),
        (r'A(\rho = 1) = e^{-4} \approx 0.02 \quad (\alpha_t = 4)', 'the field at the edge of the pupil is about 2% of the '
                                                                     'centre and the aperture cuts off about 0.03% of the beam power: nearly untruncated.')],
        'Each lens is filled by a nearly untruncated Gaussian beam, alpha_t = 4.',
        'The apodization enters the Richards–Wolf integrals as A(beta).',
        r'A(\beta) = \exp\!\left(-\alpha_t \frac{\sin^2\beta}{\sin^2\alpha}\right), \quad \sin\alpha = \mathrm{NA}/n \qquad A(\rho) = e^{-\alpha_t \rho^2}',
        fig=SL('pupil_apodization.png'), size=17)
    wide('Check: uniform input is the limit α_t → 0', os.path.join(FIG, 'axial_lim_vs_truncation.png'), [
        'The scalar focus along the axis for several α_t. As α_t decreases the focus returns to the uniform focus; at α_t = 0.5 '
        'the two already overlap.'],
        'The Gaussian focus returns to the uniform one as alpha_t goes to zero.',
        'A single beam at 750 nm. Larger alpha_t lengthens the focus and fills its zeros.')
    wide('Gaussian input against uniform input', SL('onaxis_gaussian_uniform.png'), [
        'Along the axis the Gaussian focus (α_t = 4) is longer than the uniform one and has no zeros, at NA 0.5 and at NA 0.9.'],
        'A Gaussian input lengthens the focus.', 'A single beam at 750 nm, vector focus, intensity along the axis.')
    maps('_at4', ', Gaussian input')
    for key, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
        wide(f'20% tolerances, Gaussian input, {lab}', SL(f'tolerance_{key}_at4.png'), [
            'With α_t = 4 the tolerances follow the same power laws as with uniform input and are about 1.4 times larger. The '
            'star is the value reported for uniform input at NA 0.5.'],
            f'Gaussian input: the tolerances at {lab} are larger by about 1.4.',
            'Blue: vector 2CE; red: scalar 2CE up to NA 0.5.')
    wide('Scalar 2CE against vector 2CE, Gaussian input', SL('deviation_at4.png'), [
        'With α_t = 4 the scalar 2CE tolerances depart by 5% at NA 0.525 and 10% at NA 0.7, against 0.45 and 0.6 for uniform '
        'input: the dim pupil edge removes the rays for which the small-angle phase is worst.'],
        'With a Gaussian input the paraxial focus holds to a higher NA.',
        'The difference between scalar and vector 20% tolerances, Gaussian input.')
    wide('20% tolerances in water, Gaussian input, θ = π', SL('tolerance_pi_at4_n1.33.png'), [
        'In water with α_t = 4 the tolerances follow the same power laws. Scalar 2CE departs by 5% at NA 0.7 and 10% '
        'at NA 0.9.'],
        'In water with a Gaussian input scalar 2CE holds to NA 0.7.', 'The same tolerances in water, up to NA 1.2.')
    lens_problem()
    peaks('_at4')
    linfoot()
    linfoot_maps('_at4', ', Gaussian input')

elif SECTION == 'delay':
    title('Part 5: Time delay', 'A time delay Δt between two continuous beams, and its relation to a misalignment, scalar 2CE, NA 0.5')
    summary(*SUMMARIES['delay'])
    geometry(); scalar_fields()
    D1 = r'U_2(P, t - \Delta t) = U_2(P, t)\, e^{i\phi}, \qquad \phi = \omega\Delta t = \frac{2\pi c\,\Delta t}{\lambda}'
    D2 = r'F_{2c} = \kappa_{2c}\, I_1 \left|U_2 e^{i\phi}\right|^2 = \kappa_{2c}\, I_1 I_2'
    D3 = r'\left|U_1 + U_2 e^{i\phi}\right|^2 = I_1 + I_2 + 2|U_1 U_2| \cos(\mathbf{K}\cdot\mathbf{r} - \phi)'
    eqslide('Time delay between continuous beams', 'A time delay of a continuous beam is a phase: 2CE does not see it, the 2PE fringes '
            'move with it.', [
        (D1, 'Δt = time delay of beam 2; φ = phase it adds; c = speed of light; λ = vacuum wavelength.'),
        (D2, '2CE multiplies intensities, which do not carry the phase.'),
        (D3, '2PE adds the fields, F_{2p} = κ_{2p}|U_1 + U_2 e^{iφ}|^4; K = fringe wavevector, |K| = 2k sin(θ/2): the time delay moves '
             'the fringes.')],
        'A time delay is a phase: 2CE does not see it, 2PE fringes move with it.',
        'For continuous beams a time delay is a constant phase on beam 2. The two-color signal uses only intensities. The two-photon '
        'signal contains the interference term, whose fringes shift with the phase.', '\n'.join((D1, D2, D3)), size=17)
    words('Choice of time delays: φ = 0, π/2, π', [
        'The effect of a time delay repeats with each optical period: φ = 2π is Δt = λ/c, 2.33 fs at 700 nm.',
        'φ and 2π − φ give the same loss, so φ from 0 to π covers all time delays.',
        'φ = 0 is the aligned case. φ = π/2 (Δt = 0.58 fs) moves the fringes by a quarter of their period. φ = π (Δt = 1.17 fs) '
        'moves them by half a period, so bright and dark fringes swap: the largest effect.',
        'φ = π is the time delay that matches the 2PE misalignment of 0.5 λ_{2p} used in scalar 2CE.'],
        'One optical period covers every time delay; pi is the largest effect.',
        'The time delays are chosen as fractions of the optical period, the time version of misalignments in fractions of a '
        'wavelength.')
    wide('Peak lost and fidelity against time delay', PD('phase_delay.png'), [
        'The 2CE peak and shape do not change with the time delay at either angle. For 2PE at θ = π/2 the peak drops to 71% at φ = π, '
        'as the centre falls on a dark fringe; at θ = π a bright fringe stays near the centre, so the peak stays but F drops '
        'to −0.85 as the standing wave moves.'],
        'A time delay leaves 2CE unchanged and changes 2PE through its fringes.',
        'Left: peak lost against phi; right: fidelity F against the aligned PSF. phi = pi is a time delay of 1.17 fs. The peak '
        'is found on a fine grid near the focus, so the moving fringes are resolved.')

    K1 = r'\mathbf{K} = k\left(\hat{\mathbf{k}}_1 - \hat{\mathbf{k}}_2\right), \qquad |\mathbf{K}| = 2k\sin(\theta/2)'
    K2 = r'\Delta s = \frac{\phi}{|\mathbf{K}|} = \frac{c\,\Delta t}{2n\sin(\theta/2)}'
    K3 = r'\theta = \pi:\ \Delta z = \frac{c\,\Delta t}{2n}, \qquad \theta = \pi/2:\ x_c = z_c = \frac{c\,\Delta t}{n}'
    eqslide('Time delay as a shift of the fringes', 'A time delay moves the 2PE fringes along K; at θ = π/2 it matches a '
            'misalignment of cΔt/n.', [
        (K1, 'k̂_1, k̂_2 = directions of the two beams; k = 2πn/λ; the 2PE fringes vary as cos(K·r − φ).'),
        (K2, 'Δs = shift of the fringes along K for a time delay Δt.'),
        (K3, 'the misalignment that gives the fringes the same phase as the time delay.')],
        'A time delay moves the 2PE fringes by c Delta t over 2n sin(theta/2).',
        'The fringe pattern of two plane waves has wavevector K, the difference of the two wavevectors. A phase phi moves it by '
        'phi over the magnitude of K.', '\n'.join((K1, K2, K3)), size=17)
    P1 = r'\phi_{eq} = \mathbf{K}\cdot\mathbf{r}_c + k\,\hat{\mathbf{k}}_2\cdot\mathbf{d}'
    P2 = r'\omega\,\Delta t = \phi_{eq}'
    eqslide('Misalignment in space as a phase', 'A misalignment changes the phase of the fringe at the peak; a time delay of the '
            'same phase cancels it.', [
        (P1, 'd = misalignment of O′; r_c = centre of the overlap of the two beams; k k̂_2·d = phase beam 2 gains by moving along '
             'its own direction; K·r_c = fringe phase where the beams now overlap.'),
        (P2, 'a time delay with this phase puts a bright fringe back on the peak.')],
        'A misalignment changes the fringe phase at the peak by phi_eq; a time delay can cancel it.',
        'The phase has two parts: beam 2 moving along its own direction, and the overlap of the two beams moving to another '
        'fringe. At theta = pi the two cancel for a misalignment along z.', '\n'.join((P1, P2)),
        side=('Cases', ['θ = π/2: x_c = 0.5 λ_{2p} or z_c = 0.5 λ_{2p} gives φ_{eq} = π.', '',
                        'θ = π, misalignment along z: the two terms cancel, φ_{eq} = 0, so the fringe at the centre stays bright '
                        'and the peak barely drops.']), size=18)
    wide('Time delay and misalignment, 2PE, θ = π/2', PD('time_vs_space.png'), [
        'Blue: a time delay Δt with the foci aligned. Red, green: a misalignment of the same fringe phase with no delay. One axis serves '
        'both, since a time delay of one period T shifts the fringes as much as a misalignment of one wavelength. Up to half a period '
        'the losses agree; beyond it the misalignment also separates the two foci, so its loss stays above that of the time delay.'],
        'A time delay and the matching misalignment cost the 2PE peak about the same up to half a period.',
        'The time-delay curve is symmetric about half a period and returns to zero after one, because a full period restores the '
        'fringes. Its sharp top is where the brightest fringe hands over from one side of the focus to the other.')
    words('Cancelling a misalignment with a time delay', [
        'At θ = π/2 a misalignment x_c = 0.5 λ_{2p} reduces the 2PE peak by 26%; with a time delay of φ = 0.92π the loss is 1.3%.',
        'A misalignment z_c = 0.5 λ_{2p} gives the same: 26% without the time delay and 1.3% with it.',
        'At x_c = 0.25 λ_{2p} the loss falls from 7% to 0.3% with φ = 0.46π.',
        'The best time delays are slightly below the predicted π and π/2, most likely from the Gouy phase of the focused beams, which '
        'the plane-wave form leaves out.',
        'What remains, about 1%, is the loss of overlap of the two foci: the part 2CE also has.'],
        'The 2PE loss of a misalignment is mainly phase, and a time delay removes most of it.',
        'Scalar model, NA 0.5. The time delay that best restores the peak is close to phi_eq.', size=12.5)

elif SECTION == 'polarization':
    title('Part 6: Polarization, s and p', 'Linear polarization of the two beams against unpolarized (circular) beams, vector 2CE')
    summary('At high NA, linear polarization (s: field perpendicular to the plane of the lens axes; p: field in it) changes the '
            '2CE results across the axis with facing lenses, and decides whether crossed-beam 2PE interferes; results along the '
            'axis do not change.',
            'At NA 0.9, θ = π, a misalignment of 0.37 λ_1 across the axis reduces the 2CE peak by about 51% for s–s, 42% '
            'unpolarized and 32% for p–p: the spot is wider along the polarization.',
            'For 2PE with crossed beams, p–p fields are perpendicular and barely interfere: a misalignment of 0.5 λ_{2p} costs a '
            'few percent of the peak up to NA 0.7, against 26–44% for s–s.',
            'Unpolarized beams give a round spot. Linear polarization makes the spot wider along the field, so results across the '
            'axis depend on the orientation of the misalignment. For 2PE the relative orientation of the two fields decides the '
            'interference.')
    geometry()
    words('Polarization: s and p', [
        'Light is a transverse wave: its electric field oscillates in a direction perpendicular to the direction the beam travels. '
        'That direction of oscillation is the polarization.',
        'A laser beam is usually linearly polarized: the field oscillates along one fixed direction.',
        'Circular polarization: the field direction rotates once per optical period, so on average no direction is preferred.',
        'Unpolarized light, or the average over two perpendicular linear polarizations, gives the same time-averaged intensity '
        'as circular polarization.',
        'In the paraxial scalar model of the paper the field has no direction at all, so polarization cannot enter.'],
        'Polarization is the direction in which the electric field oscillates.',
        'The scalar model has no direction for the field; the vector model does, so polarization enters at high NA.', size=13)
    side('s and p polarization', SL('polarization_sp_diagram.png'), [
        'The two lens axes lie in one plane, the x–z plane of the geometry.',
        's (German senkrecht, perpendicular): the field is perpendicular to that plane, along y, out of the page.',
        'p (parallel): the field lies in that plane, perpendicular to each beam: along x for beam 1, along z for beam 2.',
        's–s: both beams s; their fields are parallel for any θ.',
        'p–p: both beams p; with crossed beams (θ = π/2) their fields are perpendicular.'],
        's is perpendicular to the plane of the two lens axes, p lies in it.',
        'Diagram: crossed beams, beam 1 (red) travelling along z, beam 2 (blue) along x.', fw=4.6)
    eqslide('Polarization in the field equations', 'The input polarization sets the direction of the focused field; the '
            'unpolarized case averages two perpendicular directions.', [
        (r'\mathbf{E}_\psi = \cos\psi\,\mathbf{E}_{x} + \sin\psi\,\mathbf{E}_{y}',
         'E_x, E_y = Richards–Wolf focal fields for input polarized along x and along y of the beam’s own frame; ψ = input '
         'polarization angle: ψ = π/2 is s, ψ = 0 is p.'),
        (r'I_{\mathrm{unpol}} = \frac{1}{2}\left(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2\right)',
         'unpolarized: the average of the two, equal to circular polarization; the focal spot is round.'),
        (r'F_{2c} = \kappa_{2c}\, |\mathbf{E}_1|^2\, |\mathbf{E}_2|^2', '2CE uses the two intensities, so it depends on '
         'polarization only through the shape of each spot.'),
        (r'F_{2p} = \kappa_{2p}\, |\mathbf{E}_1 + \mathbf{E}_2|^4 \;\ni\; 2\,\mathrm{Re}\,(\mathbf{E}_1\cdot\mathbf{E}_2^{*})',
         '2PE interferes through E_1·E_2*: full interference for parallel fields (s–s), almost none for perpendicular fields '
         '(p–p at θ = π/2).')],
        'The input polarization angle psi enters the vector field; 2PE interference depends on E1 dot E2.',
        'Same Richards-Wolf fields as Parts 2-4, with a fixed input polarization instead of the average.',
        r"""\mathbf{E}_\psi = \cos\psi\,\mathbf{E}_x + \sin\psi\,\mathbf{E}_y
I_{unpol} = \tfrac{1}{2}(|\mathbf{E}_{\psi=0}|^2 + |\mathbf{E}_{\psi=\pi/2}|^2)
F_{2p} \ni 2\,\mathrm{Re}(\mathbf{E}_1\cdot\mathbf{E}_2^*)""", size=15)
    wide('Focal spot and polarization', SL('polarization_spot.png'), [
        'One beam at focus, across x. At NA 0.5 the two polarizations nearly coincide; at NA 0.9 the spot is about 1.35 times '
        'wider along the field than across it, because the focused field gains a component along z, strongest along the '
        'polarization.'],
        'At high NA the focal spot is wider along the polarization.',
        'Blue: field along y (s), so x is across the polarization. Red: field along x (p).')
    wide('20% tolerances and polarization, θ = π', SL('polarization_tolerance_pi.png'), [
        'Along the axis the three give the same tolerance. Across the axis, at NA 0.9, the tolerance is about 160 nm for s–s, '
        '180 nm unpolarized and 210 nm for p–p: wider along the polarization, as the spot is.'],
        'With facing lenses polarization changes the tolerance across the axis only.',
        'The 20 percent tolerances against NA for unpolarized, s–s and p–p beams.')
    wide('20% tolerances and polarization, θ = π/2', SL('polarization_tolerance_pi2.png'), [
        'With crossed beams the three nearly coincide in both directions: a misalignment in x_c is along the axis of beam 2, so '
        'it follows the length of the focus, which polarization barely changes (335, 328 and 346 nm at NA 0.9).'],
        'With crossed beams polarization barely changes the tolerances.',
        'Hatched: crossed lenses above NA 0.71.')
    wide('Peak lost and polarization', SL('polarization_peaklost.png'), [
        'Left: at NA 0.9, θ = π, a misalignment of 0.37 λ_1 across the axis costs about 51% (s–s), 42% (unpolarized) and 32% '
        '(p–p) of the 2CE peak. Right: for crossed-beam 2PE, p–p fields barely interfere, so a misalignment of 0.5 λ_{2p} costs '
        'a few percent up to NA 0.7, against 26–44% for s–s.'],
        'Polarization changes the losses across the axis, and for crossed-beam 2PE decides whether the beams interfere.',
        'Above NA 0.7 the p–p loss rises because the focused fields gain components that are no longer perpendicular.')
    words('Parts 2–4 with s and p polarization', [
        'Part 2, facing lenses: tolerances and losses across the axis move by up to about ±20% at NA 0.9; along the axis they do '
        'not change.',
        'Part 2, crossed lenses: 2CE tolerances change by a few percent at most.',
        '2PE with crossed beams: with p–p the fringes vanish, so the 2PE loss of a misalignment, and its link to a time delay '
        '(Part 5), largely disappear; s–s is the case the paper describes.',
        'Part 4, Gaussian input: the same pattern, smaller, since the Gaussian focus is closer to paraxial.'],
        'Linear polarization moves the results across the axis and removes crossed-beam 2PE interference for p–p.',
        'A summary of what would change in each earlier part if the beams were linearly polarized.', size=13)
    MOL = (r'\langle |\mathbf{E}_1\cdot\hat{\mathbf{d}}|^2\, |\mathbf{E}_2\cdot\hat{\mathbf{d}}|^2 \rangle = \frac{|\mathbf{E}_1|^2'
           r'|\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2|^2 + |\mathbf{E}_1\cdot\mathbf{E}_2^{*}|^2}{15}')
    eqslide('Orientation of the dye molecules', 'With linear polarization the orientation of each molecule’s transition '
            'dipole also enters the 2CE signal.', [
        (MOL, 'd̂ = direction of the molecule’s transition dipole; ⟨ ⟩ = average over randomly oriented molecules.'),
        (r'\text{parallel fields: } \tfrac{3}{15}\,|\mathbf{E}_1|^2|\mathbf{E}_2|^2, \qquad \text{perpendicular fields: } '
         r'\tfrac{1}{15}\,|\mathbf{E}_1|^2|\mathbf{E}_2|^2',
         'the signal is three times larger for parallel fields; the unpolarized product I_1 I_2 assumes this does not matter.')],
        'With linear polarization the molecular orientation factor enters the signal.',
        'For randomly oriented molecules the average of the two dipole projections gives this factor.', MOL, size=16)

elif SECTION == 'pulses':
    PS = SL
    title('Part 7: Optical pulses and time delay', 'Photon pairs from two Gaussian pulses, derived step by step; scalar 2CE at '
          'NA 0.5, 0.7 and 0.9 and vector 2CE at NA 0.7 and 0.9; τ = 10, 20 and 100 fs')
    summary('A time delay lowers 2CE because the photon pairs that reach the transition add out of phase where the two pulses do '
            'not arrive together: the signal is the pair probability times the overlap in time of the two pulses.',
            'With crossed lenses the PSF keeps its shape and its peak falls with the delay, by 20% at Δt = 0.4 τ; with facing lenses the delay moves the plane where the pulses meet, and with 10–20 fs pulses the PSF moves with it along the axis.',
            'Counting the pairs that reach the transition gives the same PSF shapes as the overlap in time; it changes the signal '
            'level, which at equal pulse energy no longer grows for shorter pulses.',
            'At the same NA, scalar and vector 2CE lose the same peak to a time delay, except with 10 fs pulses and facing lenses, '
            'where the longer paraxial focus follows the plane where the pulses meet further.',
            'Each pulse is a band of wavelengths. Two-color excitation takes one photon from each pulse, and the two frequencies '
            'must add up to the transition. Where the two pulses pass together these pairs add in phase; a time delay makes them '
            'add out of phase, which is the overlap in time. With crossed lenses the delay lowers the whole PSF; with facing '
            'lenses it moves the place where the pulses meet.')
    geometry(); scalar_fields()
    eqslide('Step 1: a pulse in time', 'A pulse is a fast oscillation (the carrier) inside a slowly varying envelope.', [
        (r'E(t) = A(t)\,\cos(\omega_0 t)', 'ω_0 = carrier frequency (2πc/750 nm, one oscillation every 2.5 fs); A(t) = '
                                           'envelope, which sets how long the pulse lasts.'),
        (r'I(t) = A(t)^2', 'intensity: what the molecule responds to, averaged over each fast oscillation.')],
        'A pulse is a carrier wave inside an envelope.',
        'The envelope is the slow shape; the carrier is the fast oscillation. Only the envelope matters for when the pulse is '
        'present.', r'E(t) = A(t)\cos(\omega_0 t), \qquad I(t) = A(t)^2', fig=PS('pulse_in_time.png'), size=18)
    eqslide('Step 2: a Gaussian envelope', 'We take the envelope to be a Gaussian in t; its intensity is then a Gaussian of '
            'full width at half maximum τ.', [
        (r'A(t) = \exp\left(-\frac{2\ln 2\; t^2}{\tau^2}\right)', 'Gaussian envelope, largest at t = 0.'),
        (r'I(t) = A(t)^2 = \exp\left(-\frac{4\ln 2\; t^2}{\tau^2}\right)', 'squaring doubles the exponent.'),
        (r'I\!\left(\tfrac{\tau}{2}\right) = \exp\left(-\frac{4\ln 2}{\tau^2}\cdot\frac{\tau^2}{4}\right) = e^{-\ln 2} = '
         r'\frac{1}{2}', 'at t = ±τ/2 the intensity is half its peak: τ is the full width at half maximum, the pulse duration.')],
        'The Gaussian envelope gives an intensity of FWHM tau.',
        'The constant 4 ln 2 is chosen so that tau is the full width at half maximum of the intensity.',
        r'A(t) = e^{-2\ln 2\, t^2/\tau^2}, \quad I(t) = e^{-4\ln 2\, t^2/\tau^2}, \quad I(\tau/2) = 1/2', size=18)
    eqslide('Step 3: a pulse is a sum of frequencies', 'A short pulse needs a range of frequencies; a Gaussian spread of '
            'frequencies adds up to a Gaussian pulse.', [
        (r'E(t) = \int a(\omega)\, e^{-i\omega t}\, d\omega', 'each frequency ω is a continuous wave; a(ω) = its amplitude.'),
        (r'a(\omega) = \exp\left(-\frac{(\omega-\omega_0)^2\,\tau^2}{8\ln 2}\right)', 'Gaussian spectrum centred on ω_0; its '
         'width is set by 1/τ.'),
        (r'\Delta\nu \approx \frac{0.441}{\tau}', 'spectral width (FWHM): about 22 THz at 20 fs, so a 750 nm pulse spans about '
                                                 '730–770 nm.')],
        'Adding many frequencies with a Gaussian spread gives a Gaussian pulse.',
        'With few frequencies the waves never cancel; with many they cancel everywhere except near t = 0, which is the pulse.',
        r'E(t) = \int a(\omega) e^{-i\omega t}\, d\omega, \quad a(\omega) = e^{-(\omega-\omega_0)^2\tau^2/8\ln 2}', size=17)
    wide('Step 3: adding frequencies, seen', PS('pulse_sum_of_frequencies.png'), [
        'Three frequencies added give a wave that never dies out. Nine give a pulse that repeats. Many frequencies with a '
        'Gaussian spread give one Gaussian pulse of duration τ = 20 fs.'],
        'Many frequencies make one pulse.', 'Same carrier, Gaussian weights, 3, 9 and 201 frequencies.')
    eqslide('Step 4: the pulse travels through the focus', 'Each frequency is focused by the lens; added together, the focused '
            'pulse moves through the focus at c/n.', [
        (r't_i(P) = \frac{n\, z_{b,i}}{c}', 'the time pulse i passes point P; z_{b,i} = distance of P along beam i from its '
                                            'focus (pulse i is at its focus at t = 0).'),
        (r'I_i(P, t) = I_i^{\mathrm{CW}}(P)\; \exp\left(-\frac{4\ln 2\,\left(t - t_i(P)\right)^2}{\tau^2}\right)',
         'the focused pulse: the continuous-beam intensity I^CW (the focal spot of the paper), switched on only while the '
         'pulse passes.'),
        (r't_2(P) = \frac{n\, z_{b,2}}{c} + \Delta t', 'beam 2 is sent a time Δt later: the time delay.')],
        'At each point the focused pulse is the continuous-beam spot, switched on while the pulse passes.',
        'This separates space and time: I^CW carries the shape of the focus, the Gaussian carries when the pulse is there. It '
        'neglects the small change of spot size across the spectrum.',
        r't_i = n z_{b,i}/c, \quad I_i(P,t) = I_i^{CW}(P)\, e^{-4\ln 2 (t-t_i)^2/\tau^2}, \quad t_2 = n z_{b,2}/c + \Delta t',
        size=16)
    wide('Step 5: photon pairs at the two-photon resonance', SL('pairs_overlap.png'), [
        '(a) Spectral probability density of each pulse at 20 fs. (b) Joint probability of the photon pairs at the two-photon '
        'resonance ν_a + ν_b = ν_e (λ_e = 350 nm), against the 750 nm photon (red axis) and its partner from the 656 nm laser '
        '(blue axis). Shorter pulses bring in more pairs; continuous beams have the single pair 750 + 656 nm.'],
        'The resonant photon pairs form a Gaussian that narrows as the pulses get longer.',
        'One photon from each pulse; the pair excites the dye when the two frequencies add up to the transition. Independent '
        'lasers, so the joint probability is the product of the two spectral probabilities. Derivation on the next slides.')
    R1 = r'h\nu_a + h\nu_b = h\nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{\lambda_e}'
    R2 = r'p_i(\nu) \propto \exp\left(-\frac{4\ln 2\,(\nu - \nu_i)^2}{\Delta\nu^2}\right), \qquad \Delta\nu = \frac{0.441}{\tau}'
    R3 = r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)'
    eqslide('Step 6: resonance and joint probability', 'A pair excites the 350 nm transition when its photon energies add up to '
            'the transition energy; photons of the two lasers are independent.', [
        (R1, 'two-photon resonance (energy conservation); ν = c/λ is the photon frequency.'),
        (R2, 'spectral probability density of laser i (i = 1: 750 nm, i = 2: 656 nm) for a τ-long Gaussian pulse (Step 3).'),
        (R3, 'joint probability of the resonant pair whose 750 nm photon has frequency ν_a: independent lasers, so the '
             'probabilities multiply.')],
        'Resonant pairs: energies add up to the transition; independent photons, so probabilities multiply.',
        'Which photon pairs reach the transition.', '\n'.join((R1, R2, R3)), size=16)
    S1 = r'\delta = \nu_e - (\nu_1 + \nu_2)'
    S2 = (r'(\nu_a - \nu_1)^2 + (\nu_a - \nu_1 - \delta)^2 = 2\left(\nu_a - \nu_1 - \tfrac{\delta}{2}\right)^2 '
          r'+ \tfrac{\delta^2}{2}')
    S3 = (r'P(\nu_a) \propto \exp\left(-\frac{8\ln 2\,(\nu_a - \nu_1 - \delta/2)^2}{\Delta\nu^2}\right)\, '
          r'\exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right)')
    eqslide('Step 7: complete the square', 'The product of two Gaussians is a Gaussian; δ measures how far the target sits from '
            'the design pair.', [
        (S1, 'detuning of the target ν_e from the design pair 750 + 656 nm; δ = 0 for λ_e = 350 nm.'),
        (S2, 'the two exponents of P(ν_a), with ν_e − ν_a − ν_2 = ν_1 + δ − ν_a, expanded and regrouped.'),
        (S3, 'a Gaussian in ν_a centred at ν_1 + δ/2, times a factor that depends only on δ.')],
        'The resonant pairs form a Gaussian.', 'Complete the square in nu_a.', '\n'.join((S1, S2, S3)), size=16)
    T1 = r'\mathrm{FWHM}_{\nu_a} = \frac{\Delta\nu}{\sqrt{2}}'
    T2 = (r'\int P(\nu_a)\, d\nu_a \;\propto\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) = '
          r'\exp\left(-\frac{4\ln 2\,\delta^2}{(\sqrt{2}\,\Delta\nu)^2}\right)')
    T3 = (r'\Delta\lambda_a \approx \frac{\lambda_1^2}{c}\,\frac{\Delta\nu}{\sqrt{2}} \approx \frac{585\ \mathrm{nm\,fs}}{\tau}, '
          r'\quad \Delta\lambda_b \approx \frac{448\ \mathrm{nm\,fs}}{\tau}, \quad '
          r'\Delta\lambda_e \approx \frac{255\ \mathrm{nm\,fs}}{\tau}')
    eqslide('Step 8: width and probability of the resonant pairs', 'The resonant pairs are √2 narrower than either pulse; the probability of '
            'reaching ν_e is a Gaussian √2 wider.', [
        (T1, 'spread of the 750 nm photons in resonant pairs, and of their partners: the exponent 8 ln2/Δν² of Step 7.'),
        (T2, 'probability that a pair reaches ν_e, summed over all pairs: a Gaussian in δ of FWHM √2 Δν, the spread of pair '
             'frequencies.'),
        (T3, 'in wavelength (|dλ| = λ²dν/c): 29, 22 and 13 nm at 20 fs; 6, 4.5 and 2.5 nm at 100 fs. τ → ∞ gives the single '
             'pair 750 + 656 nm.')],
        'Which pairs, and how many, in closed form.', 'Width of the resonant pairs and of the pair frequencies.',
        '\n'.join((T1, T2, T3)), size=15)
    eqslide('Step 9: the two pulses must overlap in time', 'A pair needs one photon from each pulse at the molecule at the same '
            'time; the overlap in time of the two intensities measures how much the pulses coincide.', [
        (r'O(P, \Delta t) = \int_{-\infty}^{\infty} I_1(P, t)\, I_2(P, t)\, dt', 'overlap in time at point P; with continuous '
         'beams the integrand is constant in time and O is the I_1 I_2 of the paper.'),
        (r'= I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \int e^{-a (t-t_1)^2}\, e^{-a (t-t_2)^2}\, dt, \qquad '
         r'a = \frac{4\ln 2}{\tau^2}', 'substituting Step 4: the spatial part comes out of the integral.')],
        'The overlap in time of the two pulses at each point.',
        'Only the time integral of two Gaussians is left to do.',
        r'O = \int I_1 I_2\, dt = I_1^{CW} I_2^{CW} \int e^{-a(t-t_1)^2} e^{-a(t-t_2)^2} dt', size=17)
    eqslide('Step 10: the Gaussian integral, line by line', 'Complete the square in t; one Gaussian integral is left.', [
        (r'(t-t_1)^2 + (t-t_2)^2 = 2\left(t - \bar{t}\right)^2 + \frac{(t_1 - t_2)^2}{2}, \qquad \bar{t} = \frac{t_1+t_2}{2}',
         'expand both squares and regroup: the cross terms collect into the second term.'),
        (r'\int e^{-a(t-t_1)^2} e^{-a(t-t_2)^2} dt = e^{-a (t_1-t_2)^2/2} \int e^{-2a (t-\bar{t})^2} dt',
         'the second term does not depend on t, so it leaves the integral.'),
        (r'\int_{-\infty}^{\infty} e^{-2a u^2} du = \sqrt{\frac{\pi}{2a}}', 'standard Gaussian integral, u = t − t̄: a '
         'constant, the same at every point.'),
        (r'\Rightarrow\; O \;\propto\; I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)',
         'with a = 4 ln2/τ², a/2 = 2 ln2/τ².')],
        'The time integral of two Gaussians is a Gaussian in the difference of their arrival times.',
        'Completing the square separates a part that depends on t from one that depends only on t1 − t2.',
        r'(t-t_1)^2+(t-t_2)^2 = 2(t-\bar t)^2 + (t_1-t_2)^2/2; \int e^{-2au^2}du = \sqrt{\pi/2a}', size=15)
    PA = r'A(P) = \int \sqrt{P(\nu_a)}\; U_1(P, \nu_a)\, U_2(P, \nu_e - \nu_a)\, d\nu_a, \qquad F_{2c}(P) = \kappa_{2c}\, |A(P)|^2'
    PU = r'U_i(P, \nu) \approx U_i^{\mathrm{CW}}(P)\, e^{\,i 2\pi \nu\, t_i(P)}'
    PH = r'2\pi\nu_a t_1 + 2\pi(\nu_e - \nu_a)\, t_2 = 2\pi\nu_e t_2 + 2\pi\nu_1 (t_1 - t_2) + 2\pi(\nu_a - \nu_1)(t_1 - t_2)'
    eqslide('Step 11: phase of the resonant pairs', 'The two-photon amplitude adds all resonant pairs; '
            'each pair carries the phase of the times at which the two pulses pass the point.', [
        (PA, 'A = two-photon amplitude; √P = amplitude of the pair whose 750 nm photon has frequency ν_a (its square is the joint '
             'probability of Step 6); U_i(P, ν) = focal field of beam i at frequency ν. The signal is the square of the sum.'),
        (PU, 'each frequency passes P with its pulse, at t_i = n z_{b,i}/c (Step 4); t_2 includes the delay Δt.'),
        (PH, 'phase of a pair: the first two terms are the same for all pairs; the last differs between pairs unless t_1 = t_2.')],
        'The pairs add with the phase of the arrival times; they add fully where the pulses arrive together.',
        'Where the two pulses pass at the same time, all pairs have the same phase and add up. Where they pass at different times, '
        'the phase changes across the spread of pairs, and the pairs partly cancel.', '\n'.join((PA, PU, PH)), size=15)
    G1 = (r'\sqrt{P(\nu_a)} \propto \exp\left(-\frac{4\ln 2\,(\nu_a - \nu_1 - \delta/2)^2}{\Delta\nu^2}\right) '
          r'\exp\left(-\frac{\ln 2\,\delta^2}{\Delta\nu^2}\right)')
    G2 = (r'-a x^2 + i k x = -a\left(x - \frac{ik}{2a}\right)^2 - \frac{k^2}{4a} \;\Rightarrow\; '
          r'\int e^{-a x^2 + ikx}\, dx = \sqrt{\frac{\pi}{a}}\; e^{-k^2/4a}')
    G3 = (r'a = \frac{4\ln 2}{\Delta\nu^2},\ \ k = 2\pi (t_1 - t_2),\ \ \Delta\nu = \frac{2\ln 2}{\pi\tau}:\quad '
          r'\frac{k^2}{4a} = \frac{\ln 2\,(t_1 - t_2)^2}{\tau^2}')
    eqslide('Step 12: the sum over pairs, line by line', 'With Gaussian pulses the sum over pairs is a Gaussian integral with a '
            'phase; it gives a Gaussian in the difference of the arrival times.', [
        (G1, 'square root of the joint probability of Step 7; x = ν_a − ν_1 − δ/2 is the variable of the sum.'),
        (G2, 'complete the square in x; the shifted Gaussian integrates to √(π/a), as in Step 10.'),
        (G3, 'Δν = 0.441/τ = 2 ln2/(πτ) (Step 3). So |A| falls as exp(−ln2 (t_1 − t_2)²/τ²), and |A|² as '
             'exp(−2 ln2 (t_1 − t_2)²/τ²): the overlap in time of Step 10.')],
        'The sum over pairs gives the same Gaussian in the arrival times as the overlap in time.',
        'The Fourier transform of a Gaussian is a Gaussian. The square of the amplitude has the exponent of Step 10.',
        '\n'.join((G1, G2, G3)), size=15)
    CF = (r'F_{2c}(P, \Delta t) \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) '
          r'\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)')
    T12 = r't_1 - t_2 = \frac{n\,(z_{b,1} - z_{b,2})}{c} - \Delta t'
    eqslide('Step 13: closed form of the pulsed 2CE PSF', 'The pulsed PSF is the continuous-beam PSF of the paper, times the '
            'probability that a pair reaches the transition, times the overlap in time.', [
        (CF, 'I^CW_1 I^CW_2 = the 2CE PSF of the paper; first exponential = probability that a pair reaches ν_e (Step 8), the '
             'same at all points; second = overlap in time (Steps 10 and 12).'),
        (T12, 'difference of the arrival times at P (Step 4): it sets where the pulses meet.'),
        (r'\tau \to \infty:\quad F_{2c} \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}', 'long pulses recover the '
         'continuous-beam result of the paper.')],
        'Pulsed PSF = continuous-beam PSF times pair probability times overlap in time.', 'Steps 8, 10 and 12 combined.',
        '\n'.join((CF, T12)), size=15)
    eqslide('Step 14: meeting plane of the two pulses', 'The overlap depends on z_{b,1} − z_{b,2}, which differs for facing and crossed '
            'lenses.', [
        (r'\theta = \pi:\ z_{b,1} = z,\ z_{b,2} = -z \;\Rightarrow\; \text{overlap peaks at } z = \frac{c\,\Delta t}{2n},\ '
         r'\mathrm{FWHM} = \frac{c\sqrt{2}\,\tau}{2n}',
         'facing pulses meet on a thin slab that a time delay slides along the axis: 4.2 µm long at 20 fs, 2.1 µm at 10 fs. '
         'Near the focus the pulse moves faster than c/n, so the slab sits about 6% further at NA 0.5 and 30% at NA 0.9; '
         'the full calculation includes this.'),
        (r'\theta = \pi/2:\ z_{b,1} = z,\ z_{b,2} = x \;\Rightarrow\; \exp\left(-\frac{2\ln 2}{\tau^2}'
         r'\left(\frac{n(z - x)}{c} - \Delta t\right)^2\right)',
         'crossed pulses meet along a diagonal band, much wider than the crossed spot.'),
        (r'\text{at the focus: } \exp\left(-2\ln 2\,(\Delta t/\tau)^2\right) = 0.71,\ 0.25\ \text{at}\ \Delta t = \tau/2,\ \tau',
         'how much a time delay lowers the PSF where the band is wider than the spot.')],
        'Facing pulses meet on a thin moving slab; crossed pulses on a wide band.', 'The overlap for each geometry. The arrival '
        'times n z/c hold away from the focus. Near the focus the pulse is a sum of plane waves tilted up to the cone angle, '
        'and the point where each crosses the axis moves at c/(n cos beta), faster than c/n: the pulse arrives at 0.94 z n/c '
        'at NA 0.5, 0.87 at NA 0.7 and 0.76 at NA 0.9 (vector). The plane where facing pulses meet is then at about '
        'c Delta t/(2n) divided by these factors. The pair calculation includes this through the phase of each frequency.',
        r'\theta=\pi: z = c\Delta t/2n,\ \mathrm{FWHM} = c\sqrt{2}\tau/2n', size=14)
    wide('Step 14: facing pulses meet, seen', PS('pulse_facing_meet.png'), [
        'Pulse 1 (red) travels toward +z and pulse 2 (blue) toward −z. Both are present at the same place only near z = 0, '
        'around t = 0 (green): that is where 2CE happens.'],
        'Facing pulses overlap only where they meet.', 'τ = 20 fs, no time delay.')
    wide('Step 14: the overlap against the time delay', PS('pulse_overlap.png'), [
        'Left: crossed beams, the overlap at the focus falls as exp(−2 ln2 (Δt/τ)²). Right: facing beams, a time delay slides '
        'the meeting slab along the axis by cΔt/2n.'],
        'A time delay lowers the crossed overlap and moves the facing slab.', 'From Step 14.')
    wide('Wavelengths per pulse', PS('pairs_convergence.png'), [
        'Largest change of the 2CE PSF against the number of wavelengths per pulse N, compared with N = 257, over the window, '
        'with O′ at the extreme offsets and Δt up to ±2τ. From N = 17 the change is below 2×10⁻⁵ of the peak; the runs use '
        'N = 25, where it is below 10⁻⁶.'],
        'Twenty-five wavelengths per pulse: more wavelengths change the PSF by less than one part in a million.',
        'Each pair adds with the phase of its arrival time, so the wavelengths must be sampled finely enough to resolve the '
        'largest difference of arrival times on the grid: facing lenses, the far end of the window, O prime offset by 4.8 '
        'micrometres and a delay of two pulse durations. Checked for scalar 2CE at NA 0.5 for all pulse durations and both '
        'geometries, and for vector 2CE at NA 0.9 in the 10 fs facing case. Scalar 2CE at 10 fs with facing lenses needs the most '
        'wavelengths; the vector focus at NA 0.9 is dimmer far from the focus and needs fewer.')
    words('Check: closed form against the full calculation', [
        'The full calculation focuses 25 wavelengths of each pulse separately and adds all resonant pairs with their phases '
        '(Step 11), with no envelope approximation.',
        'Largest difference over the window, relative to the aligned peak, at Δt = 0, τ/2 and τ: crossed lenses 0.6% or less at 10, 20 and 100 fs; facing lenses 0.4% at 100 fs, 1.9% at 20 fs and 3.9% at 10 fs. The difference is the change of spot size across the spectrum, which the closed form leaves out.'],
        'The closed form matches the full sum over pairs.', 'Scalar 2CE, NA 0.5.', size=13)
    eqslide('2PE with pulses', '2PE adds the two fields, so with pulses it has two kinds of terms: each beam alone, and the '
            'interference of the two.', [
        (r'F_{2p}(P, \Delta t) = \kappa_{2p} \int \left|E_1(P,t) + E_2(P,t)\right|^4 dt', 'both beams at 700 nm; E_2 is '
                                                                                         'delayed by Δt.'),
        (r'\ni\ \int \left(I_1^2 + I_2^2\right) dt', 'each pulse alone excites 2PE, whether or not the pulses overlap.'),
        (r'\Delta t \gg \tau:\quad \frac{F_{2p}}{F_{2p}(\Delta t = 0)} \to \frac{1^2 + 1^2}{2^4} = \frac{1}{8}',
         'at the aligned peak the two fields add to twice one field, so 2PE never falls below 1/8 of its peak.')],
        '2PE keeps a floor of 1/8 because each beam alone excites it.',
        'The interference terms need the pulses to overlap; the single-beam terms do not. 2PE is computed with the overlap in '
        'time of the fields.', r'F_{2p} = \kappa_{2p}\int |E_1+E_2|^4 dt \ni \int (I_1^2 + I_2^2) dt', size=17)
    TXT = {('2ce', 'pi'): 'With facing lenses the 2CE PSF shrinks along z as the pulses get shorter: at 10 fs the slab where the pulses meet (2.1 µm) is shorter than the focus.',
           ('2ce', 'pi2'): 'With crossed lenses the 2CE PSF does not change with the pulse duration: the band where the pulses meet is wider than the spot.',
           ('2pe', 'pi'): 'With facing lenses the 2PE standing wave is confined to where the pulses meet.',
           ('2pe', 'pi2'): 'With crossed lenses the 2PE PSF keeps its fringes; pulses barely change it.'}
    for key, no, what in (('psf2', 2, 'aligned'), ('psf3', 3, 'O′ at (0.4, 1.0) µm')):
        for pair, lab2 in (('2ce', '2CE'), ('2pe', '2PE')):
            for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
                wide(f'Pulsed Fig. {no}: {lab2}, {lab}', PS(f'pulse_{key}_{pair}_{th}.png'), [TXT[(pair, th)]],
                     f'Pulsed Fig. {no}, {lab2}, {lab}.', f'Scalar model, NA 0.5, {what}, no time delay; continuous beams (CW) '
                     'and tau = 100, 20, 10 fs. Contours at 1, 10, 20, 40, 60 and 80 percent of the peak; orange: 50 percent. 2CE from the resonant '
                     'pairs, 2PE from the overlap in time.')
    for pair, lab2 in (('2ce', '2CE'), ('2pe', '2PE')):
        for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
            wide(f'Pulsed Fig. 4: {lab2}, {lab}', PS(f'pulse_peakmap_{pair}_{th}.png'), [
                'With no time delay the peak against the misalignment of O′ changes little with the pulse duration: each pulse '
                'is timed to reach its own focus, so the pulses meet midway between the two foci.'],
                f'Pulsed Fig. 4, {lab2}, {lab}.', 'Scalar model, NA 0.5, tau = 100, 20, 10 fs.')
    words('Misalignment in time and in space', [
        'In space (the paper): O′ moves away from O, so the two focal spots no longer coincide. The 2CE PSF is their product, so '
        'its peak drops and moves; the tolerance is set by the size of the focal spot.',
        'In time: pulse 2 arrives Δt late. The two focal spots still coincide, but at the focus the pulses pass at different '
        'times, so the resonant pairs add out of phase (Steps 11–12) and the signal there drops as exp(−2 ln2 Δt²/τ²). The '
        'tolerance is set by the pulse duration τ.',
        'The pairs still add in phase where the pulses meet: on the plane z = cΔt/2n for facing lenses, and along the line '
        'z − x = cΔt/n for crossed lenses (Step 14).',
        'Crossed lenses: the pulses meet along a band wider than the focal spot, so the PSF keeps its shape and its peak drops by the factor at the focus.',
        'Facing lenses: the plane where the pulses meet moves along the axis by cΔt/2n. With 100 fs pulses the slab (21 µm) is longer than the focus and the PSF behaves as with crossed lenses; with 10–20 fs pulses the slab (2–4 µm) is about as long as the focus, so the PSF moves along the axis toward it, much like an axial misalignment, and its peak drops less.'],
        'A time delay moves where the pulses meet; a misalignment in space moves where the spots meet.',
        'The paper misaligns the foci in space. Here the foci stay aligned and the pulses are misaligned in time. Each causes a '
        'loss of peak and a change of shape, for different reasons and with different scales.', size=12.5)
    PSFTXT = {10: 'With 10 fs pulses the slab where the pulses meet (2.1 µm) is shorter than the focus, so the PSF follows it (blue): at Δt = τ the peak moves 1.15 µm along the axis and keeps 68% of its value, much like an axial misalignment.', 20: 'With 20 fs pulses the slab (4.2 µm) is about as long as the focus: at Δt = τ/2 the PSF moves 0.6 µm toward the plane where the pulses meet (blue) and keeps 81% of its peak; at Δt = τ it moves 1.25 µm and keeps 43%.', 100: 'With 100 fs pulses the slab (21 µm) is much longer than the focus: the PSF stays nearly in place (0.4 µm at Δt = τ) and its peak falls as at the focus, to 71% at τ/2 and 26% at τ.'}
    for tau in (10, 20, 100):
        wide(f'PSF against the time delay: θ = π, τ = {tau} fs', PS(f'pairs_time_psf_pi_tau{tau}.png'), [PSFTXT[tau]],
             f'Facing lenses, {tau} fs.', 'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Contours at 1, 10, 20, 40, 60 and 80 percent of '
             'the peak at zero delay; orange: 50 percent; blue dashed: the plane where the pulses meet, z = c Delta t / 2n.')
    wide('PSF against the time delay: θ = π/2, τ = 10 fs', PS('pairs_time_psf_pi2_tau10.png'), ['With crossed lenses the pulses meet along a band wider than the spot, so even at 10 fs the PSF keeps its shape and its peak falls as at the focus: 72% at τ/2 and 27% at τ.'],
         'Crossed lenses, 10 fs.', 'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Contours at 1, 10, 20, 40, 60 and 80 percent of the '
         'peak at zero delay; orange: 50 percent.')
    wide('Peak against the time delay', PS('pairs_time_peak.png'), ['Crossed lenses: the peak follows the overlap at the focus, exp(−2 ln2 Δt²/τ²), at 10, 20 and 100 fs. Facing lenses: with 10 and 20 fs pulses the peak falls more slowly, because the PSF moves with the slab where the pulses meet.'],
         'The peak against the time delay, as Fig. 4 of the paper against the misalignment.',
         'Scalar 2CE, NA 0.5, resonant pairs, aligned foci. Orange: the overlap at the focus, exp(-2 ln2 Delta t^2 / tau^2).')
    LINTXT = {'pi': 'Facing lenses: as the PSF moves along the axis, F and Q fall, more for shorter pulses; at Δt = τ, F is 0.23 at 10 fs, 0.55 at 20 fs and 0.97 at 100 fs. C stays near 1 because the moved PSF keeps nearly the same size.', 'pi2': 'Crossed lenses: F, C and Q stay above 0.93 up to Δt = τ at 10, 20 and 100 fs: the delay lowers the PSF without changing its shape.'}
    for th, lab in (('pi', 'θ = π'), ('pi2', 'θ = π/2')):
        wide(f'Linfoot’s criteria against the time delay: {lab}', PS(f'pairs_time_linfoot_{th}.png'), [LINTXT[th]],
             f'Linfoot’s criteria against the time delay, {lab}.', 'Scalar 2CE, NA 0.5, resonant pairs. F, C and Q compare the '
             'delayed PSF with the aligned one, each scaled to its own peak, as in Figs. 5 and 6 of the paper.')
    wide('20% tolerance in time', PS('pairs_time_tolerance.png'), ['With crossed lenses a time delay of 0.40 τ reduces the 2CE peak by 20% at all NA, scalar and vector alike. With facing lenses and 10 fs pulses the tolerance is 0.76 τ at NA 0.5 and falls toward 0.40 τ as NA grows (0.43 τ at NA 0.9): a longer focus lets the PSF follow the plane where the pulses meet.'],
         'The time delay that costs 20% of the 2CE peak.', 'Scalar 2CE (dashed) and vector 2CE (solid); NA by colour. Orange '
         'dotted: 0.40 tau, the value at the focus.')
    wide('Scalar 2CE against vector 2CE at the same NA: θ = π', PS('pairs_time_samena.png'), ['At the same NA, scalar and vector 2CE lose the same peak with 100 fs pulses. With 10 fs pulses the scalar PSF keeps slightly more of its peak (42% against 38% at Δt = τ, NA 0.7) and changes shape more, because the paraxial focus is longer along the axis than the vector one and follows the plane where the pulses meet further.'],
         'Scalar and vector 2CE against the time delay at the same NA.', 'Facing lenses, NA 0.7 and 0.9, tau = 10, 20, 100 fs. '
         'Black: scalar 2CE, the paraxial model; red: vector 2CE, the Richards–Wolf focus, unpolarized. With crossed lenses the '
         'two agree (previous slide).')
    wide('Time delay and axial misalignment: θ = π', PS('pairs_time_z.png'), ['Peak against the axial misalignment z_c and the time delay, facing lenses. For each z_c the best time delay recovers less than 0.5% of the peak: each pulse is timed to its own focus, so the pulses meet between the two foci, and a delay moves them away from there.'],
         'A time delay and an axial misalignment together.', 'Scalar 2CE, NA 0.5, resonant pairs. Contours in percent of the '
         'aligned peak; orange: 50 percent.')
    wide('Peak against the time delay: 2PE', PS('pulse_delay_peak_2pe.png'), [
        'The 2PE peak falls with the time delay but levels off at 1/8 (dotted), where each pulse alone excites 2PE and the '
        'interference is lost.'],
        '2PE keeps a floor of 1/8 when the pulses no longer overlap.', 'Scalar model, NA 0.5, overlap in time of the fields.')
    wide('Resonant pairs against all pairs', PS('pairs_vs_every_pair.png'), ['Aligned 2CE peak at equal pulse energies. Counting all pairs (the overlap in time) the signal grows as 1/τ, 10 times larger at 10 fs than at 100 fs. Counting the pairs that reach ν_e it stays the same, because a shorter pulse spreads its pairs over more transition frequencies. The PSF shapes and time-delay curves of the two agree within 0.3%.'],
         'The resonant pairs change the signal level, not the PSF shape.',
         'Aligned peak at the focus against the pulse duration, at equal pulse energies, scalar 2CE at NA 0.5.')
    RATE = r'\text{rate} \propto \int g(\Omega)\, \bigl|\tilde{P}(\Omega)\bigr|^2 d\Omega, \qquad P(t) = E_1(t)\, E_2(t)'
    eqslide('Weighting the pairs by the dye', 'The dye’s absorption g weights each pair by its total frequency: a narrow band '
            'keeps the resonant pairs, a flat band counts all pairs.', [
        (RATE, 'Ω = ω_1 + ω_2 = total frequency of a pair; g(Ω) = absorption of the dye; P̃ = spectrum of the product field.'),
        (r'g = \text{const.}: \quad \int g\,|\tilde{P}|^2 d\Omega \;\propto\; \int I_1(t)\, I_2(t)\, dt',
         'Parseval: a flat absorption gives the overlap in time of Step 9 for all pairs (checked numerically).'),
        (r'g = \delta(\Omega - \Omega_e): \quad \text{rate} \propto |\tilde{P}(\Omega_e)|^2 = |A|^2',
         'a narrow band gives the resonant pairs of Steps 11–13; for equal Gaussian pulses both give the same PSF shapes.')],
        'Weighting by the dye changes how much signal there is, not the shape of the PSF.', 'The weighted rate.', RATE, size=14)
    wide('Signal kept by the dye weighting', SL('pulse_pairs_weight.png'), [
        'Shorter pulses spread the photon pairs over more wavelengths, so a dye that absorbs only near 350 nm uses fewer of '
        'them: with a 10 nm band, about 97% is kept at 100 fs, 60% at 20 fs and 35% at 10 fs.'],
        'Short pulses waste pairs outside the dye band.', 'Gaussian absorption bands of FWHM 2, 5, 10 and 20 nm at 350 nm.')
    words('Conclusions: optical pulses', ['With pulses, 2CE counts the photon pairs whose frequencies add up to the transition. For Gaussian pulses the PSF is the continuous-beam PSF times the probability that a pair reaches the transition, times the overlap in time of the two pulses.', 'A time delay makes the resonant pairs add out of phase where the two pulses do not arrive together. At the focus the signal falls as exp(−2 ln2 Δt²/τ²), so 20% is lost at Δt = 0.40 τ.', 'Crossed lenses: the PSF keeps its shape and its peak falls by that factor. Facing lenses: the delay moves the plane where the pulses meet; with 10–20 fs pulses the PSF moves with it along the axis, much like an axial misalignment, and loses less peak.', 'Counting the resonant pairs instead of all pairs leaves the PSF shapes and time-delay curves unchanged (within 0.3%) and changes the signal level: at equal pulse energy, shorter pulses give no more signal.', 'At the same NA, scalar and vector 2CE lose the same peak to a time delay with crossed lenses and with 100 fs pulses. With 10 fs pulses and facing lenses the scalar PSF keeps slightly more peak, because the paraxial focus is longer along the axis.', 'A time delay does not recover the loss from an axial misalignment. Open: the dye’s absorption band decides between the resonant pairs and all pairs.'],
          'Pulsed 2CE = continuous-beam PSF times pair probability times overlap in time.', 'Summary of the pulsed study.',
          size=12.5)

elif SECTION == MEETING:
    title('Two-color excitation: progress report', '')
    words('Summary', [
        'Extended the 2CE misalignment study to high NA (vector focus), water, Gaussian input and optical pulses.',
        '– Offset for 20% loss: ∝ 1/NA across the axis, 1/NA^2 along it (width and length of the focus). Paraxial model within '
        '5% up to NA 0.45; along the axis off by tan^2(α/2).',
        '– Air and water: same power laws; focus 1.4× longer in water at the same NA. Crossed lenses fit to NA 0.71 in air, '
        '0.94 in water.',
        '– Fidelity: at high NA, F high over a smaller range of misalignments; vector and scalar differ more at NA 0.9.',
        '– Gaussian input: wider, longer focus; offsets 1.4× larger, same power laws.',
        '– Continuous beams: a time delay is a phase; shifts the 2PE fringes, no change in 2CE.',
        '– Optical pulses: 2CE counts photon pairs with ν_a + ν_b = ν_e, one photon from each pulse; shorter pulses, more pairs.'],
        'Extended the misalignment study to high NA, water, Gaussian input and pulses.', 'One line per section.', size=15)
    geometry()
    def section(k, name, line):
        navy(f'{k}. {name}', [(line, 15, PALE)])

    section(1, 'Offset for 20% loss against NA', 'Extended to high NA, vector focus.')
    lens_problem()
    scalar_fields()
    eqslide('Field equations: vector 2CE (Richards–Wolf)', 'Exact phase of each ray and all three field components.', [
        (EVEC, 'E = focal field for input polarized along x; φ = angle about the axis; unpolarized = mean of x and y input.'),
        (IM, 'β = ray angle; r, z = distance from the focus; A(β) = pupil amplitude (1 uniform, Gaussian for α_t = 4); '
             '√cos β = aplanatic factor; k = 2πn/λ.'),
        (GM, 'α = half-angle of the focusing cone; m = 0, 1, 2.')],
        'The vector Richards–Wolf field.', 'At low NA it reduces to the paraxial scalar field.', '\n'.join((EVEC, IM, GM)), size=15)
    words('Scalar and vector focal fields at the same NA', [
        'Scalar (paraxial): small-angle phase k n z sin²θ/2; no polarization.',
        'Vector (Richards–Wolf): exact phase k n z cos θ; field components E_x, E_y, E_z; pupil weight √cos θ.',
        'Across the axis: same width, ≈ λ/NA; polarization widens the vector spot slightly along the field.',
        'Along the axis: paraxial focus longer by 2/(1 + cos α): 7% at NA 0.5, 39% at NA 0.9 (air).'],
        'Same NA: same width; the paraxial focus is longer along the axis.', 'Scalar against vector focal fields.', size=14)
    wide('Focal field along the axis at NA 0.8, θ = π', SL('profiles_pi_na0.8.png'), [
        'Aligned 2CE spot, three focal fields. Across: all agree. Along: paraxial longer.',
        'Scalar with the exact phase = vector: the small-angle phase causes the difference.'],
        'The small-angle phase, not polarization, lengthens the paraxial focus.',
        'Paraxial scalar, scalar Debye with the exact phase, and vector.')
    wide('Offset for 20% loss against NA, θ = π', SL('tolerance_media_pi.png'), [
        'T: offset of O′ for 20% loss of the 2CE peak. Lines: power law, fit NA 0.1–0.5.',
        'Insets: scalar = vector at low NA; scalar above vector at high NA, along z first.'],
        'The offsets follow power laws in NA set by the width and length of the focus.',
        'Blue: vector; red: paraxial scalar; filled: air; open: water. Star: value of the paper at NA 0.5. Air ends at NA 1.')
    wide('Offset for 20% loss against NA, θ = π/2', SL('tolerance_media_pi2.png'), [
        'Crossed lenses: both ∝ 1/NA^2, both misalignments along the length of a beam.', 'Air to NA 0.71 (lenses fit); water to 0.94.'],
        'Crossed lenses: both offsets follow the length of the focus.',
        'Blue: vector; red: paraxial scalar; filled: air, up to NA 0.71; open: water.')
    SA1 = r'\text{exact: } k n z\,(1 - \cos\theta), \quad \text{paraxial: } k n z\,\frac{\sin^2\theta}{2}'
    SA2 = r'\frac{\text{paraxial length}}{\text{exact length}} = \frac{2}{1 + \cos\alpha}'
    SA3 = r'\frac{|T_{\mathrm{scalar}} - T_{\mathrm{vector}}|}{T_{\mathrm{vector}}} \approx \tan^2\frac{\alpha}{2}, \quad \sin\alpha = \frac{\mathrm{NA}}{n}'
    s = slide('Scalar 2CE against vector 2CE', '')
    figure(s, SL('deviation_media.png'), 0.4, 0.95, 5.6, 4.3)
    t = 1.05
    for tex, wh in ((SA1, 'axial phase of a ray at angle θ'), (SA2, 'small-angle phase: focus too long'),
                    (SA3, 'black curves; α = half-angle of the cone')):
        t += equation(s, 6.15, t, 3.4, tex, 13) + 0.02
        t += where(s, 6.2, t, 3.3, wh) + 0.12
    bullets(s, 6.15, t + 0.05, 3.4, 1.2, ['T: offset for 20% loss. At NA 0.5: 7% in air, 4% in water along z.'], 11)
    notes(s, 'The along-axis difference is tan^2(alpha/2), from the small-angle phase.',
          'Same sinc^2 along the axis, stretched by 2/(1 + cos alpha); no free parameter.', '\n'.join((SA1, SA2, SA3)))

    section(2, 'Air and water at the same NA', 'Same power laws; longer focus in water at the same NA.')
    wide('Offset for 20% loss in air and water, θ = π', SL('air_water_pi.png'), [
        'Same NA: across, equal in air and water; along, 1.4× larger in water.', 'Same power laws (fit NA 0.1–0.7).'],
        'Water keeps the power laws and enlarges the offset along the axis.', 'Filled: air; open: water.')
    wide('Offset for 20% loss in air and water, θ = π/2', SL('air_water_pi2.png'), [
        'Crossed lenses: both 1.4× larger in water at the same NA.', 'Same power laws, ∝ 1/NA^2 (fit NA 0.1–0.7).'],
        'Crossed lenses: water keeps the power laws.', 'Filled: air, up to NA 0.71; open: water.')

    section(3, 'Fidelity against NA', 'Linfoot fidelity F of the misaligned 2CE PSF, vector and scalar.')
    wide('Fidelity: 2CE, θ = π', SL('linfoot3d_F_2ce_pi_grid.png'), [
        'F: similarity of misaligned and aligned PSF (1 = identical). Top: vector; bottom: scalar; NA 0.5, 0.7, 0.9.',
        'Vector: high-F region shrinks along z_c as NA grows.'],
        'At high NA the PSF keeps its shape over a smaller range of misalignments.', 'Axes in lambda_1.')
    wide('Fidelity, vector − scalar at the same NA: 2CE, θ = π', SL('linfoot_diff3_F_2ce_pi.png'), [
        'ΔF = F_{vector} − F_{scalar}, same NA: 0.5, 0.7, 0.9. Red: vector higher; blue: lower.', 'Grows with NA.'],
        'At the same NA the vector and scalar fidelity differ, more at NA 0.9.', 'Same NA, same axes.')

    section(4, 'Gaussian input', 'Gaussian input (α_t = 4) against uniform input.')
    wide('Offset for 20% loss, Gaussian input, θ = π', SL('tolerance_media_pi_at4.png'), [
        'Dim pupil edge → wider, longer focus; offsets 1.4× larger than with uniform input.', 'Same power laws in air and water.'],
        'A Gaussian input gives 1.4 times larger offsets.', 'Blue: vector; red: scalar; filled: air; open: water.')
    wide('Offset for 20% loss, Gaussian input, θ = π/2', SL('tolerance_media_pi2_at4.png'), [
        'Crossed lenses: both ∝ 1/NA^2, as with uniform input.', 'Air to NA 0.71 (lenses fit); water to 0.94.'],
        'Crossed lenses with a Gaussian input.', 'Blue: vector; red: scalar; filled: air; open: water.')
    wide('Scalar 2CE against vector 2CE, Gaussian input', SL('deviation_media_at4.png'), [
        'Difference in T = |T_{scalar} − T_{vector}| / T_{vector}, same NA; black: tan^2(α/2), uniform pupil (Gaussian input lies below).',
        'Passes 5% at NA 0.525 in air and 0.675 in water (uniform input: 0.45 and 0.575): dim pupil edge, fewer high-angle rays.'],
        'With a Gaussian input the paraxial model holds to a higher NA.', 'Same axes as for uniform input.')
    wide('Fidelity, Gaussian input: 2CE, θ = π', SL('linfoot3d_F_2ce_pi_grid_at4.png'), [
        'Top: vector; bottom: scalar; NA 0.5, 0.7, 0.9.', 'Smoother and changes less with NA than with uniform input.'],
        'Gaussian input: fidelity changes less with NA.', 'Axes in lambda_1.')
    wide('Fidelity, vector − scalar, Gaussian input: 2CE, θ = π', SL('linfoot_diff3_F_2ce_pi_at4.png'), [
        'ΔF = F_{vector} − F_{scalar}, same NA, Gaussian input.', 'Smaller than with uniform input at the same NA.'],
        'Gaussian input: vector and scalar fidelity closer.', 'Same NA, same axes.')
    wide('Fidelity, Gaussian vs uniform input: vector, θ = π', SL('linfoot3d_F_2ce_pi_gauss_uniform.png'), [
        'Top: uniform input; bottom: Gaussian input; vector, NA 0.5, 0.7, 0.9.', 'Gaussian: high-F region larger at each NA.'],
        'A Gaussian input keeps the PSF shape over a larger range.', 'Axes in lambda_1.')
    wide('Fidelity, Gaussian − uniform input: vector, θ = π', SL('linfoot_diff3_F_2ce_pi_gauss_uniform.png'), [
        'ΔF = F_{Gaussian} − F_{uniform}, vector, same NA.', 'Red: Gaussian input higher.'],
        'Fidelity difference from the input alone.', 'Same NA, same axes.')
    section(5, 'Time delay, continuous beams', 'A time delay is a phase on each field.')
    wide('Time delay with continuous beams', PD('phase_delay.png'), [
        'Delay Δt → phase φ = ωΔt on the field (φ = π: half an optical period, 1.17 fs at 700 nm).',
        '2PE ∝ |E₁ + E₂|⁴: interference term carries φ → fringes shift. 2CE ∝ |E₁|²|E₂|²: φ cancels → no change.'],
        'A time delay changes 2PE through its fringes; 2CE does not change.', 'Peak lost and fidelity against the phase.')

    section(6, 'Optical pulses', 'A pulse holds a range of wavelengths; 2CE needs one photon from each pulse.')
    wide('Photon pairs at the two-photon resonance', SL('pairs_overlap.png'), [
        'Joint probability: chance that the 750 nm pulse gives λ_a and the 656 nm pulse gives λ_b; independent lasers → p₁(λ_a)·p₂(λ_b).',
        '(b): pairs with 1/λ_a + 1/λ_b = 1/350 nm. Shorter pulses: more pairs.'],
        'The pairs that reach the transition, from the two pulse spectra.', 'Continuous beams: the single pair 750 + 656 nm.')
    wide('Pairs that reach 350 nm', SL('pair_line.png'), [
        'Shading: joint probability of any pair, 20 fs. Line: pairs with 1/λ_a + 1/λ_b = 1/λ_e.',
        'Pairs on the 350 nm line excite the transition.'],
        'The line of pairs with the same total photon energy.', 'Dashed: 345 and 355 nm.')
    n0 = len(prs.slides)
    PT = r'I_i(P, t) = I_i^{\mathrm{CW}}(P)\, \exp\left(-\frac{4\ln 2\,(t - t_i)^2}{\tau^2}\right), \qquad t_1 = \frac{n z_{b,1}}{c}, \quad t_2 = \frac{n z_{b,2}}{c} + \Delta t'
    eqslide('Working on: closed form, term 1: the continuous-beam PSF', 'Each pulse: continuous-beam focus, passing P at its own time.', [
        (r'F_{2c}^{\mathrm{CW}}(P) \propto I_1^{\mathrm{CW}}(P)\; I_2^{\mathrm{CW}}(P)', 'the 2CE PSF of the paper: the '
         'product of the two focused intensities.'),
        (PT, 'pulse i at P: the continuous-beam intensity times a Gaussian in time of FWHM τ, centred on the time t_i at which '
             'the pulse passes P; z_{b,i} = distance of P along beam i from its focus; Δt = time delay of pulse 2.')],
        'Term 1: the focused intensities of the paper, each pulse passing P at its own time.',
        'The spatial part is the continuous-beam focus; the pulse adds a Gaussian envelope in time.',
        r'F^{CW} \propto I_1^{CW} I_2^{CW}' + '\n' + PT, size=15)
    T2M = r'\int P(\nu_a)\, d\nu_a \;\propto\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right), \qquad \delta = \nu_e - (\nu_1 + \nu_2)'
    eqslide('Working on: closed form, term 2: the pair probability', 'Resonant pair: energies add to the transition; independent lasers.', [
        (R1M := r'h\nu_a + h\nu_b = h\nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{\lambda_e}',
         'two-photon resonance; ν = c/λ.'),
        (R2M := r'p_i(\nu) \propto \exp\left(-\frac{4\ln 2\,(\nu - \nu_i)^2}{\Delta\nu^2}\right), \qquad \Delta\nu = \frac{0.441}{\tau}',
         'spectral probability density of laser i (750 and 656 nm) for a τ-long Gaussian pulse.'),
        (R3M := r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)', 'joint probability of the pair whose 750 nm photon has '
         'frequency ν_a: independent lasers, so the probabilities multiply.'),
        (T2M, 'summed over all pairs (complete the square in ν_a): the probability that a pair reaches ν_e; δ = 0 for '
              '750 + 656 nm → 350 nm.')],
        'Term 2: the probability that a pair of photons reaches the transition.',
        'Resonance, the two spectra, their product, and the sum over pairs.', '\n'.join((R1M, R2M, R3M, T2M)), size=14)
    eqslide('Working on: closed form, term 3: the overlap in time', 'One photon from each pulse at P at the same time.', [
        (r'O(P, \Delta t) = \int I_1(P, t)\, I_2(P, t)\, dt = I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \int e^{-a (t-t_1)^2} '
         r'e^{-a (t-t_2)^2} dt, \quad a = \frac{4\ln 2}{\tau^2}', 'overlap in time at P, with term 1 substituted.'),
        (r'(t-t_1)^2 + (t-t_2)^2 = 2\left(t - \bar{t}\right)^2 + \frac{(t_1 - t_2)^2}{2}, \qquad \bar{t} = \frac{t_1+t_2}{2}',
         'complete the square in t; the second term does not depend on t.'),
        (r'O \;\propto\; I_1^{\mathrm{CW}} I_2^{\mathrm{CW}} \exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)',
         'the remaining Gaussian integral is a constant, √(π/2a); a/2 = 2 ln2/τ².')],
        'Term 3: the overlap in time is a Gaussian in the difference of the arrival times.',
        'Completing the square separates the part in t from the part in t1 − t2.',
        r'O \propto I_1^{CW} I_2^{CW} \exp(-2\ln 2 (t_1-t_2)^2/\tau^2)', size=15)
    CF = (r'F_{2c}(P, \Delta t) \propto \underbrace{I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}}_{\text{term 1}}\; '
          r'\underbrace{\exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right)}_{\text{term 2}}\; '
          r'\underbrace{\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)}_{\text{term 3}}')
    T12 = r't_1 - t_2 = \frac{n\,(z_{b,1} - z_{b,2})}{c} - \Delta t'
    eqslide('Working on: closed form, combined', 'Pulsed PSF = term 1 × term 2 × term 3, for Gaussian pulses.', [
        (CF, 'continuous-beam PSF × probability that a pair reaches ν_e (the same at all points) × overlap in time.'),
        (T12, 'difference of the arrival times at P: it sets where the pulses meet; Δt moves that place.'),
        (r'\tau \to \infty:\quad F_{2c} \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}', 'long pulses recover the '
         'continuous-beam result of the paper.')],
        'Pulsed PSF = term 1 × term 2 × term 3.', 'The three terms of the previous slides, multiplied.',
        '\n'.join((CF, T12)), size=15)
    for sl_ in list(prs.slides)[n0:]:
        sl_._element.set('show', '0')                  # hidden: closed form in progress

    navy('Next steps', [('Time delay between optical pulses.', 15, PALE)])
    words('Time delay between two pulses', [
        'Each laser emits a train of short pulses; the two trains are synchronized.',
        'Δt: arrival of pulse 2 at the focus after pulse 1, set by the path of beam 2 (1 µm longer → 3.34 fs).',
        'A pulse (no chirp) carries all its wavelengths throughout: the spectrum gives which wavelengths, the envelope '
        '(FWHM τ) gives when.',
        'Δt = 0: the pulses overlap at the focus. Δt ≫ τ: no pair forms there.'],
        'Delay = arrival of pulse 2 after pulse 1 at the focus.', 'What is delayed, and which wavelengths are present.', size=14)
    s = slide('Optical pulses with a time delay: steps', '')
    BOX = ['Pulse spectra: 750 and 656 nm, duration τ', 'Pairs λ_a + λ_b reaching 350 nm (joint probability)',
           'Focus each wavelength (vector field)', 'Delay pulse 2 by Δt: phase e^{iωΔt} per wavelength',
           'Add the pairs at each point → 2CE PSF(Δt)', 'Offset and delay for 20% loss; fidelity']
    for i, txt in enumerate(BOX):
        r, c = divmod(i, 3)
        c = c if r == 0 else 2 - c                      # snake: left to right, then right to left
        l, tp = 0.6 + c * 3.05, 1.3 + r * 1.9
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, tp, 2.6, 1.15, CARD, NAVY, 1.25)
        text(s, l + 0.1, tp + 0.08, 2.4, 1.0, f'{i + 1}. {txt}', 13, NAVY, anchor=ds.MSO_ANCHOR.MIDDLE)
        if i in (0, 1):
            shape(s, MSO_SHAPE.RIGHT_ARROW, l + 2.65, tp + 0.42, 0.35, 0.3, NAVY)
        elif i == 2:
            shape(s, MSO_SHAPE.DOWN_ARROW, l + 1.15, tp + 1.2, 0.3, 0.6, NAVY)
        elif i in (3, 4):
            shape(s, MSO_SHAPE.LEFT_ARROW, l - 0.4, tp + 0.42, 0.35, 0.3, NAVY)
    notes(s, 'Steps of the pulsed 2CE calculation with a time delay.', ' '.join(BOX))
    s._element.set('show', '0')                         # hidden: steps of the running calculation
    words('Next steps', ['Run the time delay between optical pulses (currently running).',
                         'Derive the closed form of the pulsed PSF for Gaussian pulses.',
                         'Draft the paper: main point, offsets follow the size of the focus; sub-points, larger focus (water, '
                         'Gaussian input) and optical pulses.'],
          'Run pulses with a delay, derive the closed form, draft the paper.', 'Next steps.', size=14)

elif SECTION == 'cambaliza':
    title('Replication: Cambaliza & Saloma (2000)', 'Opt. Commun. 184 (2000) 25–35: 2CE and 2PE with two confocal beams, circular and annular pupils')
    words('Summary', [
        'Replicated Figs. 2–7 exactly from Eqs. 1–6, and Fig. 8 with assumed slab settings.',
        'The text differs from the figures in places: three quoted values, the Fig. 5 caption, 2PE in Figs. 6a and 7a.'],
        'Replicated the figures; the text differs in places.', 'Rebuilt from Eqs. 1-6 (paraxial scalar, NA 0.5): on every curve of Figs. 2, 3, 6, 7 and the lines of Fig. 5. 2CE exact everywhere. 2PE: Figs. 2a, 3a are |U1+U2|^4 (Eq. 6); Figs. 6a, 7a are |U1+U2|^2. Beam 2 rotated in real space; the (u, v) rotation of Eq. 1 gives other curves. Fig. 5 caption fit differs from the plotted lines. Three quoted values differ from the figures: 0.67, 1.58x wider, 20% longer. Fig. 8: shapes reproduced with h = 100 um; 2CE background higher.', size=18)
    cmodel()

    for key, title_, line in (
            ('fig2a', 'Fig. 2(a): 2PE, transverse, circular', 'θ = π/2: narrow spot with side lobes.'),
            ('fig2b', 'Fig. 2(b): 2CE, transverse, circular', 'θ = π/2 wider; θ = 0 and π coincide.'),
            ('fig3a', 'Fig. 3(a): 2PE, axial, circular', 'θ = π: standing-wave fringes.'),
            ('fig3b', 'Fig. 3(b): 2CE, axial, circular', 'θ = π/2 short along z.'),
            ('fig4a', 'Fig. 4(a): 2CE, θ = π/2, transverse, against Δλ', 'Spot widens slightly with Δλ.'),
            ('fig4b', 'Fig. 4(b): 2CE, θ = π/2, axial, against Δλ', 'DOF shortens slightly with Δλ.'),
            ('fig5', 'Fig. 5: FWHM and DOF against Δλ', 'Plotted lines match; caption numbers differ.'),
            ('fig6a', 'Fig. 6(a): 2PE, transverse, annular', 'With Eq. 6 (|U₁ + U₂|⁴): side lobes lower than printed.'),
            ('fig6b', 'Fig. 6(b): 2CE, transverse, annular', 'θ = π/2 wider, with side lobes.'),
            ('fig7a', 'Fig. 7(a): 2PE, axial, annular', 'With Eq. 6: θ = π/2 background 1/16; printed ≈ 0.25.'),
            ('fig7b', 'Fig. 7(b): 2CE, axial, annular', 'θ = π/2: 1 µm spot; θ = 0 and π flat.')):
        cpanel(title_, key, f'{key}.png', line)
    for key, title_, line in (
            ('fig6a', 'Fig. 6(a) with the excitation |U₁ + U₂|²', 'With |U₁ + U₂|²: minimum 0.086, as printed (0.08).'),
            ('fig7a', 'Fig. 7(a) with the excitation |U₁ + U₂|²', 'With |U₁ + U₂|²: background 0.25, as printed.')):
        cpanel(title_, key, f'{key}_excitation.png', line)
    coverlay(('fig2a', 'fig2b', 'fig3a', 'fig3b'), 'Current work over the paper: Figs. 2–3, circular',
             'Current work (red, blue) lies on the printed curves.')
    coverlay(('fig6a', 'fig6b', 'fig7a', 'fig7b'), 'Current work over the paper: Figs. 6–7, annular',
             'Orange (|U₁ + U₂|²) and blue lie on the printed curves.')
    words('Quoted values against the paper’s own figures', [
        'Most quoted values match; 0.67, "1.58× wider" and "20% longer" do not.',
        'Fig. 5 caption fit and Fig. 4 sign of Δλ differ from the plots.'],
        'Three quoted values do not match the figures.', 'Match: 30% (29.7%), 35% (34.0% with |U1+U2|^2), 32% (29.1%), 1 um (1.01 zero to zero). Width measure not stated: 0.75 and 0.82 give 0.68-0.87; 40% gives 30-37%; DOF 2x gives 2.2-2.6. Not in the figures: 0.67 -> 0.43-0.50; 1.58x -> 2.5-3.0; 20% longer -> 38-85%. Fig. 5 caption: 2.4e-4 dl + 0.0356 against plotted 5.2e-4 dl + 0.713; DOF slope printed with +. Fig. 4 caption dl = l2 - l1; text dl = l1 - l2.', size=18)
    for key, title_, line in (
            ('fig8a', 'Fig. 8(a): 2PE through a scattering slab, θ = π',
             'Ballistic peak at focus; 2PE background 0.09 (paper: 0.1–0.2).'),
            ('fig8b', 'Fig. 8(b): 2CE through a scattering slab, θ = π',
             '2CE background 0.07 (paper: near 0).')):
        cpanel(title_, key, f'{key}.png', line)
    words('Fig. 8: Monte Carlo settings', [
        'Not in the paper: slab half-thickness h and λ dependence of d_s; used h = 100 µm, d_s ∝ λ².',
        'h sets the background: broad at 20 µm, none at 1 mm.'],
        'Fig. 8 depends on two settings the paper does not give.', "Method of Blanca & Saloma (1998): Gaussian-beam photons, Henyey-Greenstein g = 0.9, up to 40 events; I(z) = photons inside w(z) per area; 10 trials x 1e6 photons per beam. Not stated: h and the lambda dependence of d_s. Used d_s ~ lambda^2, h/d_s = 8 at 700 nm. h = 20 um: broad pedestal; 1 mm: no background; 100 um: paper's narrow peak. In current work scattered light passes the focus, so the 2CE background (0.07) stays near 2PE (0.09).", size=18)
    chigh_na(water_x=True)
    navy('Optical pulses', [('Transform-limited pulses, zero delay, NA 0.5.', 15, PALE)])
    wide('Axial response with pulses, θ = π', os.path.join(CB, 'pulses', 'axial_pi.png'), [
        'Short pulses shorten the 2CE DOF: 3.6 µm → 1.9 µm at 10 fs.', 'θ = 0 and π/2: no change (2% or less).'],
        'Short pulses shorten the 2CE response along the axis at theta = pi.',
        'Head-on pulses overlap within sqrt(2) c tau / 2 of the focus (2.1 um at 10 fs). 2CE DOF 3.56 um continuous, 3.52 at 100 fs, 2.81 at 20 fs, 1.92 at 10 fs. 2PE fringes kept only where the pulses overlap.')
    words('Next steps', ['Decide the slab half-thickness h for Fig. 8.', 'Run pulses with a time delay and at high NA.'],
          'Fig. 8 setting, time delay.', 'Next steps.', size=18)
    DIFF = {                                                   # slides where current work and the paper differ: text in red
        'Summary': ('The text differs',),
        'Paraxial scalar model: Eqs. 1–6': ('Eq. 1 writes',),
        'Fig. 5: FWHM and DOF against Δλ': ('caption numbers differ',),
        'Fig. 6(a): 2PE, transverse, annular': ('lower than printed',),
        'Fig. 7(a): 2PE, axial, annular': ('printed ≈ 0.25',),
        'Quoted values against the paper’s own figures': ('do not', 'differ'),
        'Fig. 8(b): 2CE through a scattering slab, θ = π': ('paper: near 0',)}
    red(DIFF)

elif SECTION == CMEETING:
    title('Replication of Cambaliza & Saloma (2000) and its extension to high NA and optical pulses', 'Opt. Commun. 184 (2000) 25–35')
    words('Summary', [
        'Replication of Cambaliza & Saloma (2000), NA 0.5, paraxial scalar model',
        '– Identical: the 2PE and 2CE profiles of Figs. 2–4, 6 and 7 (2PE in 6a and 7a as the excitation |U₁ + U₂|²).',
        '– Not matching: the Fig. 5 slopes (5–9% apart), the width ratios given on pp. 28, 29 and 32, and the Fig. 5 caption equations.',
        'Extension to high NA: paraxial scalar model against the vector (Richards–Wolf) focus',
        '– The paraxial depth of focus departs by 5% at NA 0.43 in air and 0.57 in water.',
        '– The 2CE–2PE comparisons at θ = π/2 agree within 4% between the two models.',
        'Extension to optical pulses: transform-limited, zero delay',
        '– At θ = π, 10-fs pulses shorten the 2CE depth of focus from 3.3 to 1.9 µm at NA 0.5.',
        '– At high NA the focus is shorter than the pulse overlap, and the change is 4% or less.'],
        'Replication, high NA, optical pulses.',
        'Part 1: rebuilt from Eqs. 1-6 (paraxial scalar, NA 0.5). Figs. 6a and 7a plot the 2PE excitation |U1+U2|^2, not Eq. 6. '
        'Quoted ratios not in the figures: 0.67, 1.58x wider, 20% longer. Fig. 8 (Monte Carlo, scattering) is left out for now. '
        'Part 2: paraxial DOF error grows as tan^2(alpha/2). Part 3: head-on pulses overlap within sqrt(2) c tau / 2 of the focus.', size=14)
    navy('1. Replication of Cambaliza & Saloma (2000): 2PE and 2CE point spread functions, paraxial scalar model, NA 0.5', [])
    words('Summary: replication', [
        'Identical to the published curves (paraxial scalar model, NA 0.5)',
        '– 2PE and 2CE profiles for circular pupils (Figs. 2–3) and for the wavelength gap (Fig. 4).',
        '– 2CE profiles for annular pupils (Figs. 6b, 7b); 2PE (Figs. 6a, 7a) as the excitation |U₁ + U₂|².',
        'Not matching the published figures',
        '– Fig. 5: the same linear trends, with slopes 5–9% apart.',
        '– Width ratios given in the text: the curves give 0.49, 2.98 and 85% where pp. 28, 29 and 32 give 0.67, 1.58 and 20%.',
        '– Fig. 5 caption: its fit equations do not describe the plotted lines.'],
        'Replication: main points.', 'Eqs. 1-6 computed at NA 0.5 (paraxial scalar); every panel of Figs. 2-7 compared with '
        'the published one. Ranges for the quoted ratios depend on the width measure, which the text does not state. '
        'Fig. 5 caption: FWHM = 2.4e-4 dl + 0.0356, DOF = +4.81e-4 dl + 0.7112; plotted: 5.2e-4 dl + 0.713, -4.6e-4 dl + 0.713.', size=13)
    cmodel(os.path.join(FIG, '..', 'setup_model.png'))
    eqslide('Rotation of beam 2: (x, z) against (u, v)',
            'u and v scale z and x by different factors, so a rotation in (u, v) is not a rotation of the lens.', [
        (r'u = \frac{2\pi\,\mathrm{NA}^2}{\lambda}\,z, \qquad v = \frac{2\pi\,\mathrm{NA}}{\lambda}\,x',
         'optical coordinates: z is scaled by NA², x by NA.'),
        (r'\mathrm{Eq.\ 1:}\quad u_r = u\cos\theta - v\sin\theta = \frac{2\pi\,\mathrm{NA}}{\lambda}\left(\mathrm{NA}\,z\cos\theta - x\sin\theta\right)',
         'the rotation written in (u, v) weights z by an extra factor NA.'),
        (r'\mathrm{lens\ turned\ by\ }\theta:\quad u_r = \frac{2\pi\,\mathrm{NA}^2}{\lambda}\left(z\cos\theta - x\sin\theta\right)',
         'rotating (x, z) first and then scaling; both agree at θ = 0 and π.')],
        'Beam 2 should be rotated in real space.',
        'At theta = pi/2 the (u, v) rotation gives v_r = u: the transverse coordinate of beam 2 along z is scaled by NA^2 '
        'instead of NA, which stretches beam 2 along z by 1/NA (2x at NA 0.5).',
        '\n'.join((r'u = 2\pi\mathrm{NA}^2 z/\lambda, \quad v = 2\pi\mathrm{NA}\, x/\lambda',
                   r'u_r = u\cos\theta - v\sin\theta', r'z_r = z\cos\theta - x\sin\theta, \quad x_r = x\cos\theta + z\sin\theta')), size=15)
    cpanel('Rotation in (x, z) against (u, v), 2CE along the axis (Fig. 3b)', 'fig3b', '../evidence/rotation.png', (
        'At θ = 0 and π both rotations give the same curve, as published.',
        'At θ = π/2 the published width, 0.67 µm, is that of the (x, z) rotation; the (u, v) rotation gives 1.31 µm.',
        'Current work rotates beam 2 in (x, z).'),
        '2CE, theta = pi/2, NA 0.5. Across the axis (Fig. 2b) the two rotations nearly coincide.')
    for key, ttl, lines in (
            ('fig2a', '2PE across the axis, circular pupils (Fig. 2a)', (
                'At θ = 0 and π the profiles are identical (p. 28).',
                'At θ = π/2 the central spot is the sharpest, with stronger side lobes from the interference of the two beams (p. 28).')),
            ('fig2b', '2CE across the axis, circular pupils (Fig. 2b)', (
                'At θ = 0 and π the profiles are identical, and equal to the 2PE profile at θ = 0 (p. 28).',
                'At θ = π/2 the central spot is wider, with no interference side lobes (p. 29).')),
            ('fig3a', '2PE along the axis, circular pupils (Fig. 3a)', (
                'At θ = π/2 the central peak is of the order of λ₂ₚ, with strong side lobes from interference (p. 29).',
                'At θ = π the interference of the two beams modulates the profile; its envelope is the 2CE profile at θ = 0 (p. 29).')),
            ('fig3b', '2CE along the axis, circular pupils (Fig. 3b)', (
                'At θ = 0 and π the profiles are identical, and equal to the 2PE profile at θ = 0 (p. 29).',
                'At θ = π/2 the side lobes are weaker than for 2PE, with a longer depth of focus (p. 30).'))):
        cpanel(ttl, key, f'{key}.png', lines, f'{ttl}. Current work matches the published curves. Bullets: the statements of the paper, with page. ' + ' '.join(lines))
    words('Section 3.1: gap between the two wavelengths', [
        'The two 2CE wavelengths move apart, Δλ = 10 to 94 nm, with the sum of their photon energies fixed.',
        'Circular pupils, NA 0.5, lens angle θ = π/2.',
        'A wider gap widens the spot by less than 6% and shortens the depth of focus (p. 30).'],
        'Section 3.1: the wavelength gap, Figs. 4-5.',
        'p. 30: 1/lambda_e = 1/lambda_1 + 1/lambda_2 with lambda_e = 0.35 um; Delta lambda = 10 nm (705, 695), 39 nm '
        '(720, 681), 94 nm (750, 656). The shorter wavelength is on lens L2. Fig. 4: profiles for three gaps; Fig. 5: '
        'FWHM and DOF against the gap, with a linear fit.', size=18)
    for key, ttl, lines in (
            ('fig4a', '2CE across the axis for three wavelength gaps (Fig. 4a)', (
                'The central spot widens as Δλ grows from 10 to 94 nm (p. 30: by less than 6%).',
                'Why: across the axis the spot follows beam 1, which scales with λ₁: +6.4%; FWHM +6.1%.')),
            ('fig4b', '2CE along the axis for three wavelength gaps (Fig. 4b)', (
                'The depth of focus becomes sharper as Δλ grows (p. 30).',
                'Why: along the axis it follows beam 2, which scales with λ₂: −5.6%; depth of focus −5.5%.'))):
        cpanel(ttl, key, f'{key}.png', lines, f'{ttl}. Current work matches the published curves; theta = pi/2. ' + ' '.join(lines))
    cpanel('Spot width and depth of focus against the wavelength gap (Fig. 5)', 'fig5', 'fig5.png', (
        'The FWHM increases and the depth of focus decreases linearly with Δλ, as in the published plot.',
        'FWHM slope 5.2 ×10⁻⁴ µm/nm against 4.9 ×10⁻⁴ from the published points; values within 0.004 µm.'),
        'Caption: FWHM = 2.4e-4 dl + 0.0356, DOF = +4.81e-4 dl + 0.7112; plotted lines: 5.2e-4 dl + 0.713 and -4.6e-4 dl '
        '+ 0.713. The published points scatter by a few nm about the line; current work places the half maximum by '
        'interpolation on a 0.5-nm grid (scatter 0.3 nm). Reading the width at the nearest sample of a 5-nm grid gives '
        'a scatter of 4 nm, as in the published plot.')
    side('Source of the difference in Fig. 5', os.path.join(CB, 'evidence', 'fig5_overlay.png'), [
        'Blue, green: current work. Orange dashed: the DOF fit of the caption.',
        'Current work lies within 0.004 µm of the published points.',
        'The published points scatter by 0.002 µm rms, so their slope is uncertain by ±0.2 ×10⁻⁴ µm/nm: half the gap.',
        'Current work follows Eqs. 1–6; its slopes match the λ₁ and λ₂ scaling, about ±5 ×10⁻⁴ µm/nm.',
        'The caption fits match neither plotted line; the FWHM fit lies off the plot.'],
        'Fig. 5: same trends; slopes differ; caption fits inconsistent with the plot.',
        'Published points digitized from the scan: FWHM slope 4.86e-4, intercept 0.712, rms scatter 0.0016 um. Checked: the wavelength pairs (705, 695), (720, 681), (750, 656) nm satisfy 1/l1 + 1/l2 = 1/350 nm. Reading the '
        'width at the nearest sample of a 5-nm grid scatters the points as in the published plot but raises the FWHM '
        'slope to 5.7e-4, so it does not explain the lower published slope. Published lines: about +4.8e-4 dl + 0.711 '
        '(FWHM) and -4.8e-4 dl + 0.711 (DOF); the caption DOF line is +4.81e-4 dl + 0.7112. Current work: +5.24e-4 dl + '
        '0.7131 and -4.57e-4 dl + 0.7131.')
    words('Section 3.2: annular pupils', [
        'Each lens has a thin ring pupil, ε = 0.99, with the same outer diameter as the circular pupil.',
        'A thin ring gives a long focus along the axis.',
        'At θ = π/2 2CE has zeros and weaker side lobes than 2PE, a better axial response (p. 32).'],
        'Section 3.2: annular pupils, Figs. 6-7.',
        'pp. 30-32: epsilon = inner over outer radius of the ring. At theta = 0 and pi the annular 2CE response is flat '
        'along the axis (no sectioning); at theta = pi/2 its central peak is about 1 um. 2PE at theta = pi/2 has a 35% '
        'narrower spot but no zeros. Fig. 6: across the axis; Fig. 7: along it.', size=18)
    for key, ttl, ours, lines in (
            ('fig6a', '2PE across the axis, annular pupils (Fig. 6a)', 'fig6a_excitation.png', (
                'At θ = 0 and π the profiles are identical (p. 30).',
                'At θ = π/2 the central spot is 0.71 times as wide (0.36 against 0.50 µm), with no zeros (p. 31).',
                'The published minimum, 0.08, is that of |U₁ + U₂|² (0.086), not Eq. 6 (0.007).')),
            ('fig6b', '2CE across the axis, annular pupils (Fig. 6b)', 'fig6b.png', (
                'At θ = 0 and π the profiles are identical, with zero points (p. 31).',
                'At θ = π/2 the central spot is wider, with stronger side lobes, and also has zero points (p. 31).')),
            ('fig7a', '2PE along the axis, annular pupils (Fig. 7a)', 'fig7a_excitation.png', (
                'At θ = 0 the profile is constant along z: no optical sectioning (p. 32).',
                'At θ = π/2 the central spot is near λ₂ₚ, without zeros; its 0.25 background is that of |U₁ + U₂|², not Eq. 6.',
                'At θ = π the two counter-propagating waves give a uniform sinusoidal modulation (p. 32).')),
            ('fig7b', '2CE along the axis, annular pupils (Fig. 7b)', 'fig7b.png', (
                'At θ = 0 and π the profile is 1.0 along z: no optical sectioning (p. 32).',
                'At θ = π/2 the central spot is about 1 µm (1.43 λ₂ₚ), with zero points across the range (p. 32).'))):
        cpanel(ttl, key, ours, lines, f'{ttl}. ' + ' '.join(lines))
    wide('Source of the difference in Figs. 6a and 7a', os.path.join(CB, 'evidence', 'eq6_excitation.png'), [
        'Eq. 6 defines 2PE as |U₁ + U₂|⁴ (red); Figs. 6a and 7a plot |U₁ + U₂|² (orange), the excitation, not Eq. 6.',
        'Fig. 6a minimum 0.08: |U₁ + U₂|² gives 0.086, Eq. 6 0.007. Fig. 7a background 0.25: Eq. 6 gives 0.06.',
        'Figs. 2a and 3a follow Eq. 6, as current work does.'],
        'Figs. 6a and 7a plot the excitation, not the 2PE signal of Eq. 6.',
        'The side peaks of the published Fig. 7a curve at theta = pi/2 match |U1+U2|^2 within 0.02 um (correlation 0.98). '
        'Evidence: minimum of Fig. 6a at theta = pi/2, published 0.08: |U1+U2|^2 gives 0.086, Eq. 6 0.007. Background of '
        'Fig. 7a, published 0.25: |U1+U2|^2 gives 0.25, Eq. 6 1/16. The circular 2PE panels (Figs. 2a, 3a) follow Eq. 6.')
    words('Values stated in the text compared to the published figures', [
        'Consistent with the figures: 30%, 35%, 32% and 1 µm (pp. 31–32).',
        'Consistent for some width measure, which the text does not state: 0.75, 0.82, 40% and "twice".',
        'Not consistent with the figures:',
        '– p. 28, 2PE spot at θ = π/2 over θ = 0: "0.67"; the curves and current work give 0.49.',
        '– p. 29, 2CE over 2PE spot at θ = π/2: "1.58 times wider"; the curves and current work give 2.98.',
        '– p. 32, annular 2CE over circular 2PE depth of focus at θ = π/2: "20% longer"; the curves and current work give 85%.'],
        'Values stated in the text against the published figures.', 'Match: 30% (29.7%), 35% (34.0% with |U1+U2|^2), 32% (29.1%), 1 um (1.01 zero to zero). Width measure not stated: 0.75 and 0.82 give 0.68-0.87; 40% gives 30-37%; DOF 2x gives 2.2-2.6. Fig. 4 caption dl = l2 - l1; text dl = l1 - l2.', size=16)
    wide('Spot ratio stated on p. 28 (Fig. 2a)', os.path.join(CB, 'evidence', 'ratio_fig2a.png'), [
        'Stated: the 2PE spot at θ = π/2 is about 0.67 times the spot at θ = 0.',
        'Current work, which matches Fig. 2a, gives FWHM 0.256 and 0.517 µm: a ratio of 0.49.'],
        'Fig. 2a gives 0.49, not 0.67.',
        'Current work matches the published curves (previous slides). '
        'With the 1/e^2 or zero-to-zero width the ratio is 0.43-0.50.')
    wide('2CE over 2PE spot stated on p. 29 (Figs. 2a, 2b)', os.path.join(CB, 'evidence', 'ratio_158.png'), [
        'Stated: the 2CE spot at θ = π/2 is 1.58 times wider than the 2PE spot.',
        'Current work, which matches Figs. 2a and 2b, gives FWHM 0.763 and 0.256 µm: a ratio of 2.98.'],
        'Figs. 2a and 2b give 2.98, not 1.58.',
        'Other width measures give 2.5-3.0. 1.58 is also not the 2CE spot at pi/2 over the 2PE spot at 0 (1.48).')
    wide('Depth-of-focus ratio stated on p. 32 (Figs. 3a, 7b)', os.path.join(CB, 'evidence', 'ratio_20pct.png'), [
        'Stated: the annular 2CE depth of focus at θ = π/2 is 20% longer than the circular 2PE one.',
        'Current work, which matches Figs. 3a and 7b, gives FWHM 0.473 and 0.256 µm: 85% longer.'],
        'Figs. 3a and 7b give 85%, not 20%.', 'Other width measures give 38-85%.')
    chigh_na('2. Extension to high NA: paraxial scalar model against the vector (Richards–Wolf) focus, air and water', summary=('Summary: high NA', [
        'Paraxial scalar model against the vector (Richards–Wolf) focus, θ = 0 and π',
        '– Along the axis the paraxial depth of focus is 5% longer at NA 0.43 in air and 0.57 in water.',
        '– Across the axis the paraxial width is 5% larger at NA 0.86 in air and 1.14 in water.',
        'θ = π/2 and the 2CE–2PE comparisons',
        '– Scalar and vector agree within 4% up to NA 0.7 in air and 0.9 in water, where the lenses fit.',
        '– The 2CE spot is 2.9 times the 2PE spot at NA 0.5 and 2.0 times at NA 0.7 in air.'],
        'High NA: main points.', 'Vector = Richards-Wolf, both beams polarized along y. Paraxial DOF error grows as '
        'tan^2(alpha/2); in water it is about half that in air at the same NA. Annular pupils: paraxial DOF 2.2x too long '
        'at NA 0.9 in air.'))
    PU = os.path.join(CB, 'high_na', 'pupils')
    wide('Annular pupils: depth of focus against NA, air', os.path.join(PU, 'annular_widths_air_z.png'), [
        'With annular pupils the paraxial depth of focus is 2.2 times too long at NA 0.9 in air.',
        'Why: a thin ring uses only the pupil edge, where the paraxial phase error is largest.'],
        'Along the axis the paraxial model departs sooner with annular pupils.',
        'Vector (Richards-Wolf) with the annulus sin(theta) >= eps sin(alpha) (sine condition), beams polarized along y. '
        'Annular DOF (2CE, theta = 0), vector / scalar: 155 / 179 um at NA 0.5 (scalar 15% longer), 65 / 91 um at 0.7 '
        '(39%), 25 / 55 um at 0.9 (125%). Water: 221 / 238 at 0.5, 54 / 73 at 0.9, 18 / 41 at 1.2. Annular over circular '
        'DOF: 47x at NA 0.5, 42x at 0.7, 31x at 0.9 (paraxial: 1/(1 - eps^2) = 50). Spot across the axis: 0.70x the '
        'circular one at all NA. theta = pi/2: set by the narrow transverse spot of the other beam, so scalar and vector '
        'agree within 2%.')
    wide('Annular comparisons across the axis against NA', os.path.join(PU, 'annular_quoted_x.png'), [
        'Star: the value written on p. 31. Cross: the same ratio measured on the published figures; the paraxial curve passes through it.',
        'Fig. 6b: 0.82 stated, 0.67 on the curves. 2PE narrower: 35% stated, 34% on the curves.'],
        'Annular comparisons across the axis.',
        'Stars: values quoted at NA 0.5. Solid: vector; dashed: paraxial scalar; filled: air; open: water. The replication '
        'gives 0.67 at NA 0.5 for the Fig. 6b ratio.')
    wide('Annular comparisons along the axis against NA', os.path.join(PU, 'annular_quoted_z.png'), [
        'Star: the value written on p. 32. Cross: the same ratio measured on the published figures; the paraxial curve passes through it.',
        'Shorter than circular: 40% stated, 30% on the curves. Longer than 2PE: 20% stated, 85%.'],
        'Annular comparisons along the axis.',
        'Stars: values quoted at NA 0.5. Solid: vector; dashed: paraxial scalar; filled: air; open: water.')
    wide('Wavelength gap Δλ against NA (Figs. 4–5)', os.path.join(PU, 'dlambda_vs_na.png'), [
        'The Δλ dependence of Figs. 4–5 holds from NA 0.3 to 0.9, in air and water.',
        'Why: at θ = π/2 the spot follows λ₁ and the depth of focus λ₂ at every NA.'],
        'The wavelength gap changes the 2CE response by the same fraction at all NA.',
        '2CE, theta = pi/2, circular pupils; 1/lambda1 + 1/lambda2 = 1/350 nm. From 10 to 94 nm the FWHM grows by 6.3% at '
        'NA 0.3, 6.1% at 0.5, 5.7% at 0.7 (air), 5.8% at 0.9 (water); the DOF shrinks by 5.5% to 5.2%. Vector (y), '
        'unpolarized and scalar within 0.3% of each other in this relative change.')
    navy('3. Extension to optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses', [])
    words('Summary: optical pulses', [
        'Transform-limited pulses, zero delay between them',
        '– θ = π: 10-fs pulses shorten the 2CE depth of focus from 3.3 to 1.9 µm at NA 0.5 in air, 4.6 to 1.6 µm in water.',
        '– θ = π, 2PE: the fringes remain only where the two pulses overlap.',
        '– θ = 0 and π/2: the widths change by 2% or less.',
        'Pulses at high NA',
        '– At NA 0.9 in air and 1.2 in water the focus is shorter than the pulse overlap; the 2CE depth of focus changes by 4%.'],
        'Optical pulses: main points.', 'Vector focus, beams along y. Head-on pulses overlap within sqrt(2) c tau / 2 of '
        'the focus (2.1 um at 10 fs in air). The NA 0.5 slide uses the paraxial model: 3.6 to 1.9 um.', size=14)
    PE1 = r'E(t) = A(t)\cos(2\pi\nu_0 t), \qquad A(t) = e^{-2\ln 2\, t^2/\tau^2}, \qquad \Delta\nu = \frac{0.441}{\tau}'
    PE2 = r't_i(P) = \frac{n\, z_{b,i}(P)}{c}'
    eqslide('What an optical pulse adds', 'A pulse lasts τ, carries a spread of frequencies Δν, and passes each point at its own time.', [
        (PE1, 'transform-limited Gaussian pulse: τ = FWHM of the intensity; Δν = FWHM of the spectrum (no chirp).'),
        (PE2, 'time at which pulse i passes the point P; z_{b,i} = distance along the axis of beam i.')],
        'A pulse has a duration, a spectrum and an arrival time.',
        'Continuous beams have one frequency and are present at all times; a pulse has a band of frequencies and is present '
        'at each point only for about tau. 10 fs: delta nu = 44 THz, about 40 nm at 750 nm.', '\n'.join((PE1, PE2)), size=17)
    PP1 = r'\nu_a + \nu_b = \nu_e \;\Leftrightarrow\; \frac{1}{\lambda_a} + \frac{1}{\lambda_b} = \frac{1}{350\ \mathrm{nm}}'
    PP2 = r'P(\nu_a) = p_1(\nu_a)\; p_2(\nu_e - \nu_a)'
    PP3 = r'A(P) = \int \sqrt{P(\nu_a)}\; U_1(P, \nu_a)\, U_2(P, \nu_e - \nu_a)\, d\nu_a, \qquad F_{2c} = \kappa_{2c}\, |A|^2'
    eqslide('Photon pairs: which pairs excite the transition', '2CE needs one photon from each laser whose frequencies add up to the '
            'transition; every such pair contributes.', [
        (PP1, 'resonance: a photon of laser 1 (750 nm band) and one of laser 2 (656 nm band) add up to the 350 nm transition.'),
        (PP2, 'joint probability of a resonant pair: the two lasers are independent, so the spectral probabilities p_i multiply.'),
        (PP3, 'two-photon amplitude: the sum over resonant pairs, each with its focused fields U_1, U_2; the signal is its square.')],
        'Pairwise probabilities: resonant pairs, weighted by their joint probability, summed in amplitude.',
        'The pairs add with the phase of the times at which the two pulses pass P. Where the pulses arrive together all pairs '
        'add in phase; where they arrive apart, the pairs partly cancel.', '\n'.join((PP1, PP2, PP3)), size=16)
    PC1 = (r'F_{2c}(P) \propto I_1^{\mathrm{CW}} I_2^{\mathrm{CW}}\; \exp\left(-\frac{2\ln 2\,\delta^2}{\Delta\nu^2}\right) '
           r'\exp\left(-\frac{2\ln 2\,(t_1 - t_2)^2}{\tau^2}\right)')
    PC2 = r'\theta = \pi:\quad t_1 - t_2 = \frac{2nz}{c} \;\Rightarrow\; \mathrm{FWHM}_z = \frac{\sqrt{2}\, c\,\tau}{2n}'
    eqslide('Pulsed 2CE PSF: the pulses must meet', 'Summing the pairs gives the continuous PSF times the overlap of the two pulses '
            'in time; at θ = π they meet only near the focus.', [
        (PC1, 'I^CW_1 I^CW_2 = continuous 2CE PSF (Eq. 2); δ = detuning of the transition, 0 here; t_1 − t_2 = difference of '
              'arrival times.'),
        (PC2, 'facing pulses meet on a slab 2.1 µm long in air at 10 fs (1.6 µm in water); at θ = 0 they travel together, '
              'so there is no gating.')],
        'The photon-pair sum and the overlap in time give the same pulsed PSF at zero delay.',
        'The Gaussian sum over pairs gives exp(-2 ln2 (t1-t2)^2/tau^2), the same as the integral of I1(t) I2(t) over t. '
        'tau -> infinity recovers the continuous PSF.', '\n'.join((PC1, PC2)), size=16)
    wide('Axial response with pulses, NA 0.5, θ = π', os.path.join(CB, 'pulses', 'axial_pi.png'), [
        'Short pulses shorten the 2CE depth of focus: from 3.6 µm to 1.9 µm at 10 fs.',
        'Why: facing pulses meet only within the 2.1-µm overlap around the focus.'],
        'Short pulses shorten the 2CE response along the axis at theta = pi.',
        'Paraxial scalar. 2CE DOF 3.56 um continuous, 3.52 at 100 fs, 2.81 at 20 fs, 1.92 at 10 fs. theta = 0 and pi/2: '
        'change of 2% or less. 2PE fringes kept only where the pulses overlap.')
    PH = os.path.join(CB, 'pulses', 'high_na')
    if os.path.exists(os.path.join(PH, 'dof_pi.png')):
        wide('Depth of focus with pulses against NA, θ = π', os.path.join(PH, 'dof_pi.png'), [
            '2CE: at high NA the focus is shorter than the pulse overlap, so the pulse no longer shortens it.',
            '2PE: the depth of focus is the central fringe, far shorter than the overlap, so pulses leave it unchanged.'],
            'The effect of the pulse length fades as NA grows.',
            'Vector (Richards-Wolf), both beams polarized along y, zero delay. DOF = central-peak FWHM along z; '
            'pulsed over continuous. Widths (um), CW | 20 fs | 10 fs: '
            + '; '.join(l for l in open(os.path.join(PH, 'widths.txt')).read().splitlines()[1:] if ' z π |' in l))
    PULSE = {
        ('air', 0.5): ('2CE: 10-fs pulses shorten the depth of focus from 3.3 to 1.9 µm.',
                       '2PE: the fringes remain only where the two pulses overlap, within about 1 µm of the focus.',
                       'Why: facing pulses meet only near the focus; the overlap is 2.1 µm long at 10 fs.'),
        ('air', 0.7): ('2CE: 10-fs pulses shorten the depth of focus from 1.6 to 1.3 µm.',
                       '2PE: the outer fringes drop; the central fringe is unchanged.'),
        ('air', 0.9): ('2CE: the depth of focus changes by 4%, from 0.81 to 0.77 µm.',
                       'Why: the focus is already shorter than the 2.1-µm overlap.'),
        ('water', 0.5): ('2CE: 10-fs pulses shorten the depth of focus from 4.6 to 1.6 µm.',
                         '2PE: the fringes remain only where the two pulses overlap (1.6 µm in water at 10 fs).'),
        ('water', 0.9): ('2CE: 10-fs pulses shorten the depth of focus from 1.3 to 1.0 µm.',
                         '2PE: the outer fringes drop; the central fringe is unchanged.'),
        ('water', 1.2): ('2CE: the depth of focus changes by 4%, from 0.60 to 0.58 µm.',
                         'Why: the focus is already shorter than the 1.6-µm overlap.')}
    for (med, na), items in PULSE.items():
        path = os.path.join(PH, f'axial_pi_{med}_na{na:g}.png')
        if os.path.exists(path):
            wide(f'Along the axis with pulses, {med}, NA {na:g}, θ = π', path, list(items),
                 f'Pulses at NA {na:g}, {med}.',
                 'Vector (Richards-Wolf), beams along y (unpolarized 2CE: the same on the axis). 2PE: continuous and 10 fs; '
                 '2CE: continuous and tau = 100, 20, 10 fs; zero delay; each curve normalized to its own peak.')
    words('Next steps', [
        'Fig. 8, two-beam excitation through a scattering medium',
        '– Monte Carlo simulation of the excitation beams (method of Blanca & Saloma, 1998).',
        '– Set the slab half-thickness h, which the paper does not give, and compare the 2PE and 2CE backgrounds.',
        'Optical pulses',
        '– Add a time delay between the two pulses and follow the 2CE response as the delay grows.'],
        'Next steps.', 'Monte Carlo for Fig. 8; time delay between the pulses.', size=16)
    navy('Preview: Fig. 8, 2PE and 2CE through a scattering medium, Monte Carlo simulation', [])
    cpanel('2PE along the axis through a scattering slab, θ = π (Fig. 8a)', 'fig8a', 'fig8a.png', (
        'At the focus the unscattered (ballistic) photons give the peak.',
        'Away from the focus the 2PE background is 0.09 (published: 0.1–0.2).'))
    cpanel('2CE along the axis through a scattering slab, θ = π (Fig. 8b)', 'fig8b', 'fig8b.png', (
        'At the focus the unscattered photons of both beams give the peak.',
        'Away from the focus the 2CE background is 0.07 (published: near 0).'),
        'Current work is smoother: the mean of 10 runs of 1e6 photons, and I(z) counts each photon at every plane it crosses '
        'inside the beam radius w(z) (Blanca & Saloma 1998), so neighbouring points share photons. The paper uses 1e7 photons '
        'but does not state its binning; a single run or finer bins would give its noise.')
    wide('Fig. 8 background against the slab half-thickness h', os.path.join(CB, 'panels', 'fig8_h_scan.png'), [
        'The paper does not give h: a thin slab gives a broad pedestal, a thick slab no background.',
        'No h gives both the published 2PE background (0.1–0.2) and no 2CE background; h = 100 µm is used.'],
        'Fig. 8 depends on h, which the paper does not give.',
        "Method of Blanca & Saloma (1998): Gaussian-beam photons, Henyey-Greenstein g = 0.9, up to 40 events; I(z) = photons "
        "inside w(z) per area; 10 trials x 1e6 photons per beam. Not stated: h and the lambda dependence of d_s; used "
        "d_s ~ lambda^2, h/d_s = 8 at 700 nm for every h. Background for |z| > 10 um, 2PE / 2CE: h = 20 um broad pedestal; "
        "50 um 0.26 / 0.14; 100 um 0.09 / 0.07; 300 um 0.004 / 0.005; 1 mm none.")
    green({
        'Rotation in (x, z) against (u, v), 2CE along the axis (Fig. 3b)': ('Current work rotates',),
        'Source of the difference in Fig. 5': ('Current work follows Eqs. 1–6',),
        'Source of the difference in Figs. 6a and 7a': ('as current work does',),
        'Spot ratio stated on p. 28 (Fig. 2a)': ('Current work, which matches',),
        '2CE over 2PE spot stated on p. 29 (Figs. 2a, 2b)': ('Current work, which matches',),
        'Depth-of-focus ratio stated on p. 32 (Figs. 3a, 7b)': ('Current work, which matches',)})
    red({                                                     # differences from the published text, on their own slides only
        'Paraxial scalar model: Eqs. 1–6': ('Eq. 1 writes',),
        '2PE across the axis, annular pupils (Fig. 6a)': ('not Eq. 6',),
        '2PE along the axis, annular pupils (Fig. 7a)': ('not Eq. 6',),
        'Values stated in the text compared to the published figures': ('Not consistent', '"0.67"', '"1.58', '"20%'),
        'Spot ratio stated on p. 28 (Fig. 2a)': ('Stated:',),
        '2CE over 2PE spot stated on p. 29 (Figs. 2a, 2b)': ('Stated:',),
        'Depth-of-focus ratio stated on p. 32 (Figs. 3a, 7b)': ('Stated:',),
        'Source of the difference in Fig. 5': ('match neither',),
        'Source of the difference in Figs. 6a and 7a': ('not Eq. 6',),
        'Spot width and depth of focus against the wavelength gap (Fig. 5)': ('FWHM slope',)})

pass                                                         # physics checks: see scripts/check_lim2002_physics.py
glossary()

# ── renumber, check legibility, embed at 600 dpi, save ──
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.has_text_frame and abs(sh.left / 914400 - 9.0) < 0.01 and abs(sh.top / 914400 - 5.28) < 0.01 \
                and sh.text_frame.text.strip().isdigit():
            sh.text_frame.paragraphs[0].runs[0].text = str(i)
FLOOR = 11.0          # pt; 16 arcmin (ISO 9241-3) at four slide heights on a 5.625-in slide
Image.MAX_IMAGE_PIXELS = None
low = set()
for path, shown in ds.FIGURES:
    if path.endswith('.png'):                                    # 24-pt smallest text at 600 dpi; the pair figures use 28 pt
        im = Image.open(path)
        small = 28 if os.path.basename(path).startswith('pairs_') else 24
        if os.path.basename(os.path.dirname(path)) == 'evidence' and os.path.basename(path) in ('fig5_caption.png', 'rotation.png'):
            small = 31
        if os.path.basename(path) == 'fig5_overlay.png':
            continue                                             # the published scan; its text is the paper's own                                           # panel-slot figures of evidence_cambaliza2000.py: 31-pt legend
        pt = small * shown / (im.size[0] / (im.info.get('dpi') or (600, 600))[0])
        if pt < FLOOR:
            low.add((os.path.basename(path), round(pt, 1)))
done = set()
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.shape_type != 13:
            continue
        ipart = sh.part.related_part(sh._element.blipFill.blip.rEmbed)
        if id(ipart) in done:
            continue
        im = Image.open(io.BytesIO(ipart.blob))
        w = int(round(600 * sh.width / 914400))
        if im.size[0] > 1.05 * w:
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB').resize((w, int(round(w * im.size[1] / im.size[0]))), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', dpi=(600, 600), optimize=True)
            ipart._blob = buf.getvalue()
        done.add(id(ipart))
OUT = os.path.join(DIR, {MEETING: '2ce_meeting_2026-10-15.pptx', 'cambaliza': '2ce_cambaliza_replication.pptx',
                         CMEETING: '2ce_meeting_cambaliza.pptx'}.get(
    SECTION) or f'2ce_{SECTIONS.index(SECTION):02d}_{SECTION}.pptx')
os.makedirs(os.path.join(DIR, 'pdfs'), exist_ok=True)
ds.keynote_fonts()
prs.save(OUT)
# Keynote rejects the file as written by python-pptx; a re-save in place through PowerPoint makes it load. Opening through
# Finder (open -a) lets the sandboxed PowerPoint access a new file. Then export the PDF.
subprocess.run(['open', '-a', 'Microsoft PowerPoint', OUT])
import time as _time
_time.sleep(8)
subprocess.run(['osascript', '-e', f'''tell application "Microsoft PowerPoint"
save active presentation
save active presentation in POSIX file "{os.path.join(DIR, 'pdfs', os.path.basename(OUT)[:-5])}.pdf" as save as PDF
close active presentation saving no
end tell'''], capture_output=True)
for f in (OUT, os.path.join(DIR, 'pdfs', os.path.basename(OUT)[:-5] + '.pdf')):   # PowerPoint marks its saves as
    if os.path.exists(f):                                                            # quarantined, which Keynote refuses;
        data = open(f, 'rb').read()                                                  # a fresh copy drops the mark
        os.remove(f)
        open(f, 'wb').write(data)
print(f'Saved -> {OUT} ({len(prs.slides)} slides)' + (f'; below {FLOOR:g} pt: {sorted(low)}' if low else ''))
