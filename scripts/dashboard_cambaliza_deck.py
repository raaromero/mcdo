r"""Slides of the meeting deck for the dashboard: the manifest written by make_lim2002_progress_deck.py (SECTION=cmeeting)
becomes dashboard/cambaliza/public/data/deck.json, and every figure it uses is copied, scaled to at most 1600 px wide,
into dashboard/cambaliza/public/img/deck/.

    SECTION=cmeeting python scripts/make_lim2002_progress_deck.py     # writes output/08_two_color/decks/2ce_meeting_manifest.json
    python scripts/dashboard_cambaliza_deck.py
"""
import hashlib
import json
import os

from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
MAN = os.path.join(ROOT, 'output', '08_two_color', 'decks', '2ce_meeting_manifest.json')
DATA = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'data')
IMG = os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'img', 'deck')
MAXW = 1600
Image.MAX_IMAGE_PIXELS = None

os.makedirs(IMG, exist_ok=True)
slides = json.load(open(MAN))
keep = set()
for s in slides:
    figs = []
    for path in s['figs']:
        stem = os.path.splitext(os.path.basename(path))[0]
        name = f'{stem}_{hashlib.md5(path.encode()).hexdigest()[:6]}.png'
        out = os.path.join(IMG, name)
        im = Image.open(path)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > MAXW:
            im = im.resize((MAXW, round(MAXW * im.height / im.width)), Image.LANCZOS)
        if im.mode == 'RGBA':                                   # flatten on white: figures are read on a white card
            bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3]); im = bg
        im.save(out, optimize=True)
        figs.append({'src': f'./img/deck/{name}', 'w': im.width, 'h': im.height})
        keep.add(name)
    s['figs'] = figs
for f in os.listdir(IMG):                                       # drop figures the deck no longer uses
    if f not in keep:
        os.remove(os.path.join(IMG, f))
json.dump(slides, open(os.path.join(DATA, 'deck.json'), 'w'), ensure_ascii=False)
size = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print(f'{len(slides)} slides, {len(keep)} figures ({size / 1e6:.1f} MB) -> {IMG}')
