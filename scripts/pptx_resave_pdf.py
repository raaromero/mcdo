r"""Re-save a deck written by python-pptx through PowerPoint and export it to PDF, as make_lim2002_progress_deck.py does.

Keynote can reject a file as python-pptx writes it; a re-save in place through PowerPoint makes it load. PowerPoint is
opened through Finder (open -a), which lets the sandboxed application reach a new file. PowerPoint marks what it saves
as quarantined, which Keynote refuses, so both files are written again as fresh copies. The PDF is saved beside the deck.

    python scripts/pptx_resave_pdf.py output/08_two_color/decks/2ce_high_na_pulses.pptx [more.pptx …]
"""
import os
import subprocess
import sys
import time

for deck in sys.argv[1:]:
    deck = os.path.realpath(deck)
    pdf = deck[:-5] + '.pdf'
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run(['open', '-a', 'Microsoft PowerPoint', deck])
    time.sleep(5)
    name = os.path.basename(deck)
    for _ in range(60):                                   # a large deck takes a while to open
        q = subprocess.run(['osascript', '-e', 'with timeout of 60 seconds\ntell application "Microsoft PowerPoint" to '
                            'return name of active presentation\nend timeout'], capture_output=True, text=True)
        if q.stdout.strip() == name:
            break
        time.sleep(2)
    r = subprocess.run(['osascript', '-e', f'''with timeout of 900 seconds
tell application "Microsoft PowerPoint"
save active presentation
save active presentation in POSIX file "{pdf}" as save as PDF
close active presentation saving no
end tell
end timeout'''], capture_output=True, text=True)
    for _ in range(30):                                   # the PDF export finishes after the call returns
        if os.path.exists(pdf) and os.path.getsize(pdf) > 0:
            break
        time.sleep(1)
    for f in (deck, pdf):
        if os.path.exists(f):
            data = open(f, 'rb').read()
            os.remove(f)
            open(f, 'wb').write(data)
    print(('Saved -> ' + pdf) if os.path.exists(pdf) else f'NO PDF for {deck}: {r.stderr.strip()}')
