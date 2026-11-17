r"""Backup deck of the delay between the two pulses, against NA, pulse width and pupil (Richards–Wolf, air), from
cambaliza2000_pulses_delay_plot.py; numbers in the speaker notes. pulse_results.pptx is left as it is.

    python scripts/make_pulse_delay_deck.py -> output/08_two_color/cambaliza2000/deck/pulse_delay.pptx
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mcdo.deckstyle as ds
from mcdo.deckstyle import prs, slide, text, bullets, figure, dots, NAVY, WHITE, PALE
from PIL import Image

import cambaliza2000_pulses_delay as P
from pulse_delay_slides import delay_slides, finish, fitted

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


slide = fitted(slide)
t = P.load('rw_air', 'coarse')
face = t.query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100 and delay_tau == 1").set_index('na')

s = navy('Delay between the two pulses', [('Roland Albert A. Romero', 18, WHITE),
         ('National Institute of Physics, University of the Philippines Diliman', 13, PALE),
         ('Extension of Cambaliza & Saloma (2000) and Lim & Saloma (2002, 2003) to optical pulses', 13, PALE)])
notes(s, 'Peak 2CE fluorescence against the delay between the 750-nm and 656-nm pulses.',
      'All results are for the vector (Richards–Wolf) model in air unless a slide says otherwise; the same quantities for '
      'the scalar model, water, oil, Gaussian input and annular pupils are in the data files of the delay results.')

s = slide('Summary: delay between the two pulses', '')
bullets(s, 0.5, 0.95, 9.0, 4.2, [
    'Delayed the 656-nm pulse relative to the 750-nm pulse by up to twice the pulse width, for collinear, crossed and '
    'facing lenses from NA 0.1 to 0.95.',
    'Found that with collinear and crossed lenses, and with facing lenses at high NA, the peak 2CE fluorescence '
    'decreases as the temporal overlap of the two pulses, to one quarter at a delay of one pulse width.',
    'Found that with facing lenses at low NA, the delayed pulses still meet inside the long depth of focus, so the peak '
    'moves along the axis and is largely retained.',
    'Derived the peak 2CE fluorescence with facing lenses from the position where the delayed pulses meet; the result '
    'agrees with the computed peaks to within 0.01.',
    'Found that below about 20 fs, with all photon pairs and phase-locked pulses, the peak oscillates with the delay; '
    'the 2CE of the 350-nm pairs alone decreases smoothly.',
    'Found that with crossed lenses and the polarization in the plane of the lens axes, the fringes against the delay '
    'are about a quarter as deep.'], 13)
notes(s, 'A delay reduces the peak 2CE fluorescence through the temporal overlap of the pulses, except where facing lenses '
      'have a long depth of focus.',
      f'With facing lenses and 100-fs pulses, the peak at a delay of one pulse width is {face.loc[0.1, "rel_cross"]:.2f} '
      f'of the peak without delay at NA 0.1, {face.loc[0.2, "rel_cross"]:.2f} at NA 0.2 and '
      f'{face.loc[0.9, "rel_cross"]:.2f} at NA 0.9.')

delay_slides(slide, big, notes)

finish(prs)
ds.keynote_fonts()
path = os.path.join(OUT, 'pulse_delay.pptx')
prs.save(path)
print('Saved ->', path, f'({len(prs.slides)} slides)')
