r"""Slide style shared by the Lim & Saloma (2002) decks: 16:9 at 10 × 5.625 in,
navy title slide, three colored dots, Cambria titles with a one-line takeaway,
grey cards, framed figures and a MAIN POINT speaker script in the notes, after
~/Downloads/lim02_2ce_presentation.pptx.

A deck script imports the primitives, may reset ``deckstyle.CITE`` (the
footer), builds its slides and saves ``deckstyle.prs``. Text supports x_c,
λ_1, x^2, _{..} and ^{..} as real sub/superscripts.
"""

import os
import re

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.join(os.path.dirname(__file__), '..')
FIG = os.path.join(ROOT, 'output', '08_two_color', 'lim2002')
ORIG = os.path.join(FIG, 'original')
PAN = os.path.join(FIG, 'panels')

NAVY, RED, ORANGE, PURPLE = (RGBColor.from_string(c) for c in ('14213D', 'B23A48', 'D9731F', '5B3FA8'))
GREY, CARD, FRAME, PALE = (RGBColor.from_string(c) for c in ('5C6370', 'F2F3F8', 'D5D8E0', 'C9CEDF'))
WHITE, GREEN = RGBColor(0xFF, 0xFF, 0xFF), RGBColor.from_string('1B7F3A')
W, H = 10.0, 5.625
CITE = 'Lim & Saloma, Opt. Commun. 207, 121–130 (2002)'   # footer; a deck script may reset it
TOK = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\}|_[A-Za-z0-9]|\^[A-Za-z0-9])')

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


# ── primitives ────────────────────────────────────────────────────────────

def runs(p, text, size, color=NAVY, bold=False, font='Calibri', italic=False):
    """Add text to paragraph p, rendering _x, _{..}, ^x, ^{..} as sub/superscripts."""
    for part in TOK.split(text):
        if not part:
            continue
        base = 0
        if part[0] in '_^' and len(part) > 1:
            base = -25000 if part[0] == '_' else 30000
            part = part[2:-1] if part[1] == '{' else part[1:]
        r = p.add_run(); r.text = part
        f = r.font
        f.size, f.bold, f.italic, f.name, f.color.rgb = Pt(size), bold, italic, font, color
        if base:
            f._element.set('baseline', str(base))


def text(s, l, t, w, h, txt, size, color=NAVY, bold=False, font='Calibri',
         anchor=MSO_ANCHOR.TOP, align=None, italic=False):
    tf = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate(txt.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align:
            p.alignment = align
        runs(p, line, size, color, bold, font, italic)
    return tf


def bullets(s, l, t, w, h, items, size=12.5, color=NAVY):
    """Bulleted list as in the style deck: • with hanging indent, 8 pt after."""
    tf = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', '228600'); pPr.set('indent', '-228600')
        spc = pPr.makeelement(qn('a:spcAft'), {}); pts = spc.makeelement(qn('a:spcPts'), {'val': '700'})
        spc.append(pts); pPr.append(spc)
        pPr.append(pPr.makeelement(qn('a:buSzPct'), {'val': '100000'}))
        pPr.append(pPr.makeelement(qn('a:buChar'), {'char': '•'}))
        runs(p, it, size, color)
    return tf


def shape(s, kind, l, t, w, h, fill, line=None, line_w=1.0):
    sh = s.shapes.add_shape(kind, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line or fill; sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.08
    return sh


def dots(s, x0, y, d, gap):
    for i, c in enumerate((RED, ORANGE, PURPLE)):
        shape(s, MSO_SHAPE.OVAL, x0 + i * gap, y, d, d, c)


def chip(s, l, t, w, label, fill, fg=WHITE):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, 0.36, fill)
    text(s, l, t, w, 0.36, label, 12, fg, True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)


def notes(s, main, script, latex=None):
    body = f'MAIN POINT: {main}\n\n{script}'
    if latex:
        body += '\n\nLaTeX:\n' + '\n'.join(l.strip() for l in latex.strip().splitlines())
    s.notes_slide.notes_text_frame.text = body


PAGE = [0]


def slide(title, takeaway):
    """White content slide: dots, Cambria title, purple takeaway, footer."""
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
    PAGE[0] += 1
    dots(s, 0.5, 0.42, 0.13, 0.2)
    text(s, 1.2, 0.28, 8.6, 0.45, title, 24, NAVY, True, 'Cambria', MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 0.78, 9.0, 0.5, takeaway, 13, PURPLE)
    text(s, 0.5, 5.28, 6.0, 0.22, CITE, 8.5, GREY)
    text(s, 9.0, 5.28, 0.5, 0.22, str(PAGE[0] + 1), 8.5, GREY)
    return s


def card(s, l, t, w, h, heading, hcolor, items, size=12, bulleted=True):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h, CARD)
    text(s, l + 0.2, t + 0.12, w - 0.4, 0.35, heading, 14, hcolor, True, 'Cambria')
    if bulleted:
        bullets(s, l + 0.2, t + 0.55, w - 0.4, h - 0.65, items, size)
    else:
        text(s, l + 0.2, t + 0.55, w - 0.4, h - 0.65, '\n'.join(items), size)


FIGURES = []                                        # (path, width on the slide in inches) of every figure placed


def figure(s, path, l, t, w, h):
    """Image inside a thin grey frame, as in the style deck; returns the frame box."""
    iw, ih = Image.open(path).size
    k = min((w - 0.1) / iw, (h - 0.1) / ih)
    fw, fh = iw * k + 0.1, ih * k + 0.1
    fl = l + (w - fw) / 2
    shape(s, MSO_SHAPE.RECTANGLE, fl, t, fw, fh, WHITE, FRAME, 0.75)
    s.shapes.add_picture(path, Inches(fl + 0.05), Inches(t + 0.05), Inches(iw * k), Inches(ih * k))
    FIGURES.append((path, iw * k))                     # source and width on the slide (in), for the legibility audit
    return fl, t, fw, fh


def label(s, l, t, w, txt, color=GREY):
    text(s, l, t, w, 0.25, txt, 10, color, True, align=PP_ALIGN.CENTER)


def verdict(s, ok):
    lab, col = {'match': ('REPRODUCED', GREEN), 'partial': ('PARTLY REPRODUCED', ORANGE),
                'no': ('NOT REPRODUCED', RED)}[ok]
    text(s, 7.2, 0.3, 2.3, 0.3, lab, 10, col, True, align=PP_ALIGN.RIGHT)


def stat(s, l, t, value, vcolor, lines):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, l, t, 2.9, 1.35, CARD)
    text(s, l, t + 0.05, 1.45, 0.8, value, 34, vcolor, True, 'Cambria', MSO_ANCHOR.MIDDLE, PP_ALIGN.CENTER)
    text(s, l + 1.45, t + 0.15, 1.4, 1.1, lines, 10.5, NAVY, True)


def numbered(s, n, color, t, txt, size=13):
    shape(s, MSO_SHAPE.OVAL, 0.6, t, 0.45, 0.45, color)
    text(s, 0.6, t, 0.45, 0.45, str(n), 15, WHITE, True, 'Cambria', MSO_ANCHOR.MIDDLE, PP_ALIGN.CENTER)
    text(s, 1.3, t - 0.02, 8.2, 0.55, txt, size, NAVY, anchor=MSO_ANCHOR.MIDDLE)


def compare(title, takeaway, orig, ours, ok, items, caption, main, script, latex=None):
    """Original and reconstruction side by side, framed; points at the right."""
    s = slide(title, takeaway); verdict(s, ok)
    label(s, 0.45, 1.3, 3.2, 'Paper')
    label(s, 3.75, 1.3, 3.2, 'Reconstruction', PURPLE)
    figure(s, os.path.join(ORIG, orig), 0.45, 1.58, 3.2, 3.2)
    figure(s, ours, 3.75, 1.58, 3.2, 3.2)
    bullets(s, 7.15, 1.45, 2.4, 3.4, items, 11.5)
    text(s, 0.45, 4.85, 6.5, 0.4, caption, 9, GREY)
    notes(s, main, script, latex)
    return s
