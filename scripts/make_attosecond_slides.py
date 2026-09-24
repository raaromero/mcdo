"""Slides: the 18 as soft X-ray paper against our 1 fs optical pulse.

    python scripts/make_attosecond_slides.py
    -> ~/Downloads/attosecond_comparison.pptx
"""

import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = os.path.join(os.path.dirname(__file__), '..')
FIG = os.path.join(ROOT, 'output', '05_pulsed_pupils')
OUT = os.path.expanduser('~/Downloads/attosecond_comparison.pptx')

NAVY = RGBColor(0x0B, 0x3C, 0x5D)
GREY = RGBColor(0x55, 0x55, 0x55)
CITE = RGBColor(0x1F, 0x6F, 0xB4)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def title(s, text, size=32):
    tb = s.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    r = tf.paragraphs[0].add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.color.rgb = Pt(size), True, NAVY


def bullets(s, items, left, top, width, height, size=20):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        lvl, text = item[0], item[1]
        cite = item[2] if len(item) > 2 else None
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl
        r = p.add_run()
        r.text = ('•  ' if lvl == 0 else '–  ') + text
        r.font.size = Pt(size if lvl == 0 else size - 2)
        r.font.color.rgb = RGBColor(0, 0, 0) if lvl == 0 else GREY
        if cite:
            c = p.add_run()
            c.text = f'  [{cite}]'
            c.font.size = Pt(size - 6)
            c.font.color.rgb = CITE
        p.space_after = Pt(8)


def figure(s, name, top, max_h):
    from PIL import Image
    path = os.path.join(FIG, name)
    w, h = Image.open(path).size
    width = min(12.1, max_h * w / h)
    height = width * h / w
    s.shapes.add_picture(path, Inches((13.333 - width) / 2), Inches(top),
                         Inches(width), Inches(height))


# 1 — title
s = prs.slides.add_slide(BLANK)
tb = s.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(11.7), Inches(2.5))
tf = tb.text_frame
tf.word_wrap = True
r = tf.paragraphs[0].add_run()
r.text = '18 as Soft X-Ray Pulses and Our 1 fs Optical Pulse'
r.font.size, r.font.bold, r.font.color.rgb = Pt(38), True, NAVY
p = tf.add_paragraph()
r = p.add_run()
r.text = ('Gao et al., Nature Communications 17, 8810 (2026), '
          'doi:10.1038/s41467-026-76827-3')
r.font.size, r.font.color.rgb = Pt(18), GREY

# 2 — summary
s = prs.slides.add_slide(BLANK)
title(s, 'Summary of the Paper')
bullets(s, [
    (0, 'Isolated soft X-ray pulses of 18 ± 2 as, the shortest measured to date '
        '(previous record 40–50 as)', 'Gao p. 1, abstract; p. 9, left col.'),
    (0, 'Source: Yb laser at 1030 nm, 170 fs, compressed to 3.7 fs',
        'Gao p. 2, left col.; p. 3, left col.'),
    (1, 'Drives high-harmonic generation in helium: 3.9–25 nm (50–320 eV)',
        'Gao p. 1, abstract'),
    (0, 'Duration measured by angle-resolved photoelectron streaking',
        'Gao p. 3, left col.'),
    (1, 'Pulse shape retrieved from data, not assumed; chirp compensated with carbon filters',
        'Gao p. 11, Eq. (5); p. 6–7'),
    (0, 'Relevant to us'),
    (1, 'Same Gaussian time–bandwidth relation: τ·δω = 1.8 fs·eV',
        'Gao p. 3, right col.'),
    (1, 'Ours: Δν·τ = 0.44, i.e. 1.825 fs·eV',
        'Romallosa p. 2, Sec. II.B'),
    (1, 'Weak focusing (f = 500 mm, ~100 µm spot): no high numerical aperture',
        'Gao p. 10, left col.'),
], 0.6, 1.4, 12.1, 5.9, size=19)

# 2b — why the output is soft X-ray
s = prs.slides.add_slide(BLANK)
title(s, 'How an Infrared Laser Makes Soft X-Rays')
bullets(s, [
    (0, 'Yb laser: infrared light from ytterbium ions, 1030 nm (1.20 eV photons); '
        'it never changes wavelength', 'Gao p. 2, left col.'),
    (0, 'It acts as a strong electric field: focused into helium at 1.4 × 10¹⁵ W/cm²',
        'Gao p. 5, Fig. 3'),
    (0, 'The field frees an electron and drives it back, giving it up to ~130 eV of energy '
        '(ponderomotive energy, ∝ intensity × wavelength²)',
        'Gao p. 2, left col.; 130 eV computed'),
    (0, 'On recombining with its ion, the electron emits one new photon: kinetic energy '
        '+ 24.6 eV binding energy', 'Gao p. 11; Corkum, Phys. Rev. Lett. 71, 1994 (1993)'),
    (1, 'Result: 3.9–25 nm (50–320 eV), soft X-ray light emitted by helium',
        'Gao p. 1, abstract'),
    (0, 'Emission lasts a fraction of one optical cycle, so each burst is attoseconds; '
        'spatial gating isolates one', 'Gao p. 4, right col.; p. 5, Fig. 3'),
], 0.6, 1.4, 12.1, 5.9, size=19)

# 3 — comparison table
s = prs.slides.add_slide(BLANK)
title(s, 'Their Pulse Against Ours')
R, G = 'Romallosa', 'Gao'
rows = [(('', ''), ('Ours', ''), ('Gao et al. (2026)', '')),
        (('Duration', ''), ('1 fs', f'{R} p. 1, abstract'),
         ('18 as', f'{G} p. 9, left col.')),
        (('Center', ''), ('750 nm (1.65 eV)', f'{R} p. 1, abstract'),
         ('Soft X-ray, 3.9–25 nm (50–320 eV); midpoint ~6.7 nm (~185 eV, our estimate)',
          f'{G} p. 1, abstract')),
        (('Spectrum', ''), ('Assumed Gaussian', f'{R} p. 2, Eqs. (8)–(9)'),
         ('Measured, not Gaussian', f'{G} p. 4, Fig. 2d')),
        (('Pulse shape', ''), ('Fixed by the Gaussian', f'{R} p. 2, Eq. (8)'),
         ('Retrieved from streaking data', f'{G} p. 11, Eq. (5)')),
        (('Chirp', ''), ('None (b = 0)', f'{R} p. 2, Sec. II.B'),
         ('Compensated; transform limit 11.4 as', f'{G} p. 3, right col.')),
        (('Duration definition', ''), ('Intensity FWHM', f'{R} p. 2, Eq. (9)'),
         ('Intensity FWHM', f'{G} p. 9, left col.')),
        (('Focusing', ''), ('Numerical aperture 0.1–1.2, vector',
                            f'{R} p. 2, Sec. II.A'),
         ('f = 500 mm, ~100 µm spot', f'{G} p. 10, left col.'))]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.6), Inches(1.4),
                         Inches(12.1), Inches(5.8)).table
for c, wdt in enumerate((2.6, 4.3, 5.2)):
    tbl.columns[c].width = Inches(wdt)
for i, row in enumerate(rows):
    for j, (txt, cite) in enumerate(row):
        para = tbl.cell(i, j).text_frame.paragraphs[0]
        r = para.add_run()
        r.text = txt
        r.font.size, r.font.bold = Pt(16), (i == 0 or j == 0)
        if cite:
            p2 = tbl.cell(i, j).text_frame.add_paragraph()
            c = p2.add_run()
            c.text = cite
            c.font.size, c.font.color.rgb = Pt(11), CITE

# 3b — wavelengths
s = prs.slides.add_slide(BLANK)
title(s, 'Wavelengths')
bullets(s, [
    (0, 'Their driver: Yb laser at 1030 nm, compressed pulse centered near 1000 nm',
        'Gao p. 2, left col.; p. 4, left col.'),
    (0, 'Their attosecond output: 3.9–25 nm (50–320 eV); no single carrier stated',
        'Gao p. 1, abstract; nm conversion computed'),
    (0, 'Their spectrum is measured, not Gaussian; transform limit 11.4 as',
        'Gao p. 4, Fig. 2d, 2f'),
    (0, '7.2 nm is not from the paper: the lowest carrier for a Gaussian 18 as pulse '
        'that stays at positive frequency (4σ = 172 eV)', 'computed'),
    (0, 'Ours: 750 nm (1.65 eV), following Romallosa', 'Romallosa p. 1, abstract'),
    (0, 'Conversion: photon energy E [eV] = 1240 / λ [nm]'),
    (1, 'The extension contains no wavelength; absolute depths scale with wavelength'),
], 0.6, 1.4, 12.1, 5.9, size=20)

# 3c — rule of thumb
s = prs.slides.add_slide(BLANK)
title(s, 'The Time–Bandwidth Rule of Thumb')
bullets(s, [
    (0, 'Gao et al.: τ[fs] · δω[eV] = 1.8 fs·eV for a Gaussian envelope',
        'Gao p. 3, right col.'),
    (0, 'Origin: an unchirped Gaussian pulse has Δν · τ = 0.44', 'Romallosa p. 2, Sec. II.B'),
    (1, 'In photon energy, ΔE = h Δν with h = 4.136 eV·fs, so ΔE · τ = 1.825 fs·eV',
        'computed'),
    (0, 'It sets the shortest pulse a bandwidth allows: 18 as needs at least 101 eV of bandwidth',
        'computed'),
    (1, 'Chirp or a non-Gaussian spectrum makes the pulse longer, so for a measured '
        'spectrum it is an estimate'),
    (0, 'Their spectrum is measured with a grating spectrometer; only Fig. 2g is simulated',
        'Gao p. 4, Fig. 2 caption; p. 10, Methods'),
], 0.6, 1.4, 12.1, 5.9, size=20)

# 5 — wavelength with bands
s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Wavelength')
figure(s, 'spectrum_bands_1fs_18as.png', 1.35, 4.9)
bullets(s, [
    (0, '18 as needs a carrier of at most 7.2 nm (172 eV) to stay at positive frequency',
        'computed: 4σ of the Romallosa p. 2 spectrum'),
], 0.6, 6.5, 12.1, 0.8, size=18)

# 7 — linear wavelength, Gaussian model
s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Wavelength, Linear Axis')
figure(s, 'spectrum_bands_1fs_18as_linear_wavelength.png', 1.3, 4.5)
bullets(s, [
    (0, 'The skew comes from λ = c/f, not from the axis scale; relative to its carrier, '
        '1 fs is wider (1.10 against 0.59)', 'computed'),
    (0, 'Hatched: their measured band, 4.4–24.8 nm', 'Gao p. 3, right col.; p. 4, Fig. 2d'),
], 0.6, 6.0, 12.1, 1.4, size=17)

# 7b — band overlap is not spectral agreement
s = prs.slides.add_slide(BLANK)
title(s, 'Inside Their Band Is Not the Same Spectrum')
bullets(s, [
    (0, 'Accurate: our 18 as Gaussian lies inside their measured band',
        'Gao p. 3, right col.; p. 4, Fig. 2d'),
    (1, 'Half-maximum width of our model: 5.6–10.2 nm (122–223 eV), '
        'inside 4.4–24.8 nm (50–284 eV)', 'computed'),
    (0, 'Not established: that our spectrum matches theirs'),
    (1, 'The hatched region marks only where their spectrum is nonzero, '
        'not how bright each wavelength is'),
    (1, 'Their spectrum is measured and non-Gaussian, with a hard edge at 4.4 nm '
        '(carbon K edge)', 'Gao p. 3, right col.; p. 4, Fig. 2d'),
    (1, 'Our 7.2 nm center is our choice (lowest carrier keeping the Gaussian at '
        'positive frequency), not fitted to their data', 'computed'),
    (1, 'Their spectrum supports 11.4 as at the transform limit, shorter than '
        'the 18 as our Gaussian assumes', 'Gao p. 3, right col.; p. 4, Fig. 2f'),
    (0, 'A real comparison needs their spectral intensity, which is available '
        'in Code Ocean', 'Gao p. 12, Data availability'),
], 0.6, 1.4, 12.1, 5.9, size=19)

# 4 — frequency
s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Frequency, 750 nm Carrier')
figure(s, 'spectrum_1fs_vs_18as.png', 1.35, 4.9)
bullets(s, [
    (0, 'At 750 nm, 18 as spans 24,500 THz, 61× the carrier; only 3.1% lies in 0–800 THz',
        'computed from Romallosa p. 2, Eq. (9) power spectrum'),
], 0.6, 6.5, 12.1, 0.8, size=18)

# 6 — linear frequency, Gaussian model
s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Frequency, Linear Axis')
figure(s, 'spectrum_bands_1fs_18as_freq.png', 1.3, 4.5)
bullets(s, [
    (0, 'Both are Gaussian in frequency; 18 as spans 24,500 THz against 441 THz for 1 fs',
        'computed from Romallosa p. 2, Eq. (9)'),
    (0, 'Hatched: their measured band with the carbon filter, 4.4–24.8 nm (50–284 eV); our Gaussian '
        'model lies inside it', 'Gao p. 3, right col.; p. 4, Fig. 2d'),
], 0.6, 6.0, 12.1, 1.4, size=17)

# 8, 9 — photon energy
s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Photon Energy, Log Axis')
figure(s, 'spectrum_bands_1fs_18as_logenergy.png', 1.3, 4.7)
bullets(s, [
    (0, 'Photon energy E [eV] = 1240 / λ [nm]; a Gaussian in frequency is a Gaussian in energy'),
    (0, 'Hatched: their measured band, 50–284 eV (4.4–24.8 nm)', 'Gao p. 3, right col.; p. 4, Fig. 2d'),
], 0.6, 6.1, 12.1, 1.3, size=17)

s = prs.slides.add_slide(BLANK)
title(s, 'Spectral Power Against Photon Energy, Linear Axis')
figure(s, 'spectrum_bands_1fs_18as_linear_energy.png', 1.3, 4.5)
bullets(s, [
    (0, 'Same center, 172 eV: 18 as spans 101 eV at half maximum, 1 fs only 1.8 eV', 'computed'),
    (0, 'Hatched: their measured band, 50–284 eV (4.4–24.8 nm)', 'Gao p. 3, right col.; p. 4, Fig. 2d'),
], 0.6, 6.0, 12.1, 1.4, size=17)

# 10–12 — log-axis pairs
for fname, ttl, note in (
        ('spectrum_bands_1fs_18as_pair_log_wavelength.png',
         'Spectral Power Against Wavelength, Log-Axis Pair', 'Wavelength'),
        ('spectrum_bands_1fs_18as_pair_log_freq.png',
         'Spectral Power Against Frequency, Log-Axis Pair', 'Frequency'),
        ('spectrum_bands_1fs_18as_pair_log_energy.png',
         'Spectral Power Against Photon Energy, Log-Axis Pair', 'Photon energy')):
    s = prs.slides.add_slide(BLANK)
    title(s, ttl)
    figure(s, fname, 1.3, 4.9)
    bullets(s, [
        (0, 'Hatched: their measured band, 4.4–24.8 nm (50–284 eV)',
            'Gao p. 3, right col.; p. 4, Fig. 2d'),
    ], 0.6, 6.4, 12.1, 0.9, size=17)

prs.save(OUT)
print('Saved ->', OUT, f'({len(prs.slides)} slides)')
