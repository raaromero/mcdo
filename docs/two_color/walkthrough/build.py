"""Dashboard walkthrough: walkthrough.src.md + steps.json -> walkthrough.md -> HTML and PDF.

Each [[id]] line in the source becomes one step: a link that opens the dashboard with exactly the settings of steps.json
(every parameter left out is at its default), the settings in words, and a screenshot of what the view shows.
Screenshots: node shoot.mjs steps.json img (local `vite preview` on port 4173 and headless Chromium on port 9333).

Run: python build.py          (needs pandoc; Chromium for the PDF) -> the meeting deck walkthrough
     python build.py pulses   -> the walkthrough of pulse_results.pptx: walkthrough_pulses.src.md + steps_pulses.json,
                                 screenshots in img_pulses/ (node shoot.mjs steps_pulses.json img_pulses), links to the
                                 local dashboard (npm run dev, port 4317) until it is deployed again
     python build.py high_na_pulses  -> the guide of 2ce_high_na_pulses.pptx: walkthrough_high_na_pulses.src.md + steps_high_na_pulses.json,
                                 screenshots in img_high_na_pulses/ -> output/08_two_color/decks/high_na_pulses_guide.{html,pdf}
     python build.py delay    -> the guide of pulse_delay.pptx: walkthrough_delay.src.md + steps_delay.json,
                                 screenshots in img_delay/ -> output/08_two_color/cambaliza2000/deck/delay_guide.{html,pdf}
     (the last three link to the local dashboard, port 4317, and write the settings of each step as a sentence;
     screenshots: node shoot.mjs steps_<name>.json img_<name>)
"""
import os
import sys
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
MODE = sys.argv[1] if sys.argv[1:] else ""
PULSES = MODE in ("pulses", "high_na_pulses", "delay")           # local links, the settings of each step as a sentence
URL = os.environ.get("URL", "http://localhost:4317/#" if PULSES else "https://2color-excitation.vercel.app/#")
OUT = Path("/Users/raaromero/mcdo_dev/output/08_two_color/" + ("decks" if MODE in ("", "high_na_pulses") else "cambaliza2000/deck"))
TAG = f"_{MODE}" if MODE else ""
NAME = {"": "dashboard_walkthrough", "pulses": "pulse_walkthrough", "high_na_pulses": "high_na_pulses_guide", "delay": "delay_guide"}[MODE]
CSS = "walkthrough.css" if not MODE else "walkthrough_pulses.css"
CHROMIUM = next(Path.home().glob("Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"))

TAB = {"live": "Focal spot", "theta": "Lens angle θ", "dl": "Wavelength gap Δλ", "eps": "Annular pupil ε",
       "na": "Scalar vs vector at high NA", "pulses": "Femtosecond pulses", "scatter": "Scattering (Fig. 8)",
       "ptime": "Pulses in time", "psum": "Pulse results"}
PTH = {"0": "θ = 0", "90": "θ = π/2", "180": "θ = π"}
METRIC = {"width": "width", "cmp": "paper's comparisons", "gap": "scalar / vector", "nrmse": "NRMSE", "F": "Linfoot F",
          "C": "Linfoot C", "Q": "Linfoot Q", "lobe": "side-lobe distance", "lobeh": "side-lobe height"}
CMP = {"r1": "p. 28: 2PE spot, θ = π/2 over θ = 0", "r2": "p. 29: 2CE spot over 2PE spot, θ = π/2",
       "r3": "2CE DOF over 2PE DOF, θ = π/2", "a1": "p. 31: annular 2CE spot, θ = 0 over π/2",
       "a2": "p. 31: annular, 2PE spot narrower than 2CE", "a3": "p. 32: 2CE DOF shorter, annular than circular",
       "a4": "p. 32: annular 2CE DOF longer than circular 2PE"}
TH = {"0": "0", "pi2": "π/2", "pi": "π"}
WDIR = {"x": "across (FWHM)", "z": "along (DOF)", "xz": "both"}


def eps(v):
    return "circular" if float(v) == 0 else f"annular ε {v}"


SAY = {   # Pulses in time and Pulse results: each setting as part of a sentence
    "qsig": lambda v: f"set the signal to {v}", "qth": lambda v: f"set the angle θ to {v}°",
    "qtau": lambda v: f"set the pulse width τ to {v} fs", "qdel": lambda v: f"set the delay of pulse 2 to {v} λ",
    "qna": lambda v: f"set the NA to {v}", "qn": lambda v: "set the medium to " + ("water" if v == "1.33" else "air"),
    "qvid": lambda v: "press Load the video", "rsig": lambda v: f"set the signal to {v}",
    "rcut": lambda v: "set the direction to " + ("across" if v == "x" else "along the axis"),
    "rpth": lambda v: f"set the profile at the picked τ to {PTH[v]}",
    "rdth": lambda v: f"set the angle for the maps and delay to {PTH[v]}",
    "rdt": lambda v: f"set τ for the maps and delay to {v} fs",
    "rk": lambda v: f"click τ = {v} fs on a width chart", "rdn": lambda v: f"click N = {v} on a delay chart",
    # Pulse results, the plots against NA and the section "Delay between the pulses, against NA"
    "nth": lambda v: f"set the angle for the plots against NA to {PTH[v]}",
    "nm": lambda v: f"set the measure of the pulse width against NA to {NM[v]}",
    "nset": lambda v: f"set the model, medium and pupil of the plot of one measure against another to {setname(v)}",
    "nx": lambda v: f"set its x axis to {NX.get(v, NM.get(v, v))}", "ny": lambda v: f"set its y axis to {NM[v]}",
    "xth": lambda v: f"set the angle for the delay against NA to {PTH[v]}",
    "xtau": lambda v: f"set τ for the delay against NA to {v} fs",
    "xnas": lambda v: "draw " + " and ".join(", ".join(f"NA {int(k) / 100:g}" for k in v.split("."))
                                            .rsplit(", ", 1)) + " against the delay",
    "xna": lambda v: f"set the NA of the chart of all pairs to {v}",
    "xpol": lambda v: "set the polarization of the chart of all pairs to " + (
        "in the plane of the lens axes" if v == "p" else "perpendicular to the plane of the lens axes"),
    # Scalar vs vector at high NA, Lens angle θ, Focal spot
    "metric": lambda v: f"set the plot to {METRIC[v]}", "sig": lambda v: f"set the signal to {v}",
    "ths": lambda v: "set the angles to " + " and ".join(", ".join(TH[t] for t in v.split(".")).rsplit(", ", 1)),
    "axis": lambda v: "set the direction to " + ("across" if v == "x" else "along"),
    "model": lambda v: f"set the model to {v}", "pupil": lambda v: "set the pupil to " + ("annular" if v == "ann" else "circular"),
    "input": lambda v: "set the input to " + ("Gaussian" if v == "gau" else "uniform"), "med": lambda v: f"set the medium to {v}",
    "na": lambda v: f"click NA {v} on the left chart", "th": lambda v: f"set the angle θ to {v}°",
    "wdir": lambda v: f"set the width to {WDIR[v]}", "pk": lambda v: f"click θ = {v}° on the left chart",
}
NM = {"diff": "largest difference", "dof": "depth of focus", "wx": "width across", "side": "side lobe", "F": "Linfoot F",
      "S": "Linfoot S", "Q": "Linfoot Q"}
NX = {"tau": "pulse width τ", "na": "NA"}


def setname(v):
    """'rw_air_eps0.9' -> 'Richards–Wolf, air, ε = 0.9', as in the menu of Pulse results."""
    p = v.split("_")
    lab = ["Richards–Wolf" if p[0] == "rw" else "scalar", p[1]]
    for q in p[2:]:
        lab.append(f"ε = {q[3:]}" if q.startswith("eps") else "Gaussian input α = 4")
    return ", ".join(lab)


def sentence(h: str, card: str = "", into: bool = False) -> str:
    """The settings of a link as one sentence: which tab, what to set, what to click. A link with hl=<id> is a card of
    the tab Highlights, whose first words are given as card."""
    q = dict(p.split("=") for p in h.split("&"))
    tab = TAB[q.pop("mode")]
    hl = q.pop("hl", None)
    acts = [SAY[k](v) for k, v in q.items()]
    if hl:
        third = {"set": "sets", "click": "picks", "draw": "draws", "press": "presses"}
        acts = [third.get(a.split(" ", 1)[0], a.split(" ", 1)[0]) + " " + a.split(" ", 1)[1] for a in acts]
        body = acts[0] if len(acts) == 1 else ", ".join(acts[:-1]) + " and " + acts[-1]
        return (f"Open the tab “Highlights” and click the card that begins “{card}”. It opens the tab “{tab}”, "
                + (f"{body}, and brings the plot of the result into view." if into else f"{body}."))
    if not acts:
        return f"Open the tab “{tab}” with all controls at their defaults."
    body = acts[0] if len(acts) == 1 else ", ".join(acts[:-1]) + " and " + acts[-1]
    return f"Open the tab “{tab}”, {body}; the other controls stay at their defaults."


def words(h: str) -> str:
    """The settings of a link, as they read on the dashboard."""
    q = dict(p.split("=") for p in h.split("&"))
    mode = q.pop("mode")
    lab = {
        "lna": lambda v: f"NA {v}", "wna": lambda v: f"NA {v}", "na": lambda v: f"click NA {v}",
        "n": lambda v: "water" if v == "1.33" else "air", "wn": lambda v: "water" if v == "1.33" else "air",
        "med": lambda v: v, "th": lambda v: f"θ = {v}°", "pth": lambda v: f"θ = {v}°",
        "wth": lambda v: f"Angle θ = {({'0': '0', '90': 'π/2', '180': 'π'})[v]}",
        "dl": lambda v: f"Δλ = {v} nm", "wdl": lambda v: f"Δλ = {v} nm", "eps": eps, "weps": eps,
        "pupil": lambda v: "annular" if v == "ann" else "circular",
        "wdir": lambda v: f"Width: {WDIR[v]}", "axis": lambda v: "Direction: " + ("across" if v == "x" else "along"),
        "metric": lambda v: f"Plot: {METRIC[v]}", "cmp": lambda v: f"Comparison: {CMP[v]}",
        "sig": lambda v: f"Signal {v}", "ths": lambda v: "Angle " + ", ".join(TH[t] for t in v.split(".")),
        "how": lambda v: "How it is measured: show", "map": lambda v: "2D map: contours" if v == "contour" else "2D map: heat map",
        "msc": lambda v: "Map scale: per unit total energy" if v == "energy" else "Map scale: of its own peak",
        "rot": lambda v: "Rotation: (u, v) as printed" if v == "uv" else "Rotation: (x, z)",
        "pe": lambda v: "2PE plotted as |U₁ + U₂|²" if v == "1" else "2PE plotted as |U₁ + U₂|⁴",
        "tau": lambda v: f"Beams: {v} fs", "pplot": lambda v: "Left chart: pulsed / continuous" if v == "ratio" else "Left chart: widths",
        "one": lambda v: "Show: one run" if v == "1" else "Show: mean of 10 runs", "h": lambda v: f"click h = {v} µm",
        "cx": lambda v: f"cut along at x = {v} µm", "cz": lambda v: f"cut across at z = {v} µm",
        # Pulses in time and Pulse results
        "qsig": lambda v: f"Signal {v}", "qth": lambda v: f"Angle θ = {v}°", "qtau": lambda v: f"Pulse width τ = {v} fs",
        "qdel": lambda v: f"Delay of pulse 2 = {v} λ", "qna": lambda v: f"NA {v}", "qn": lambda v: "water" if v == "1.33" else "air",
        "qvid": lambda v: "Load the video", "rsig": lambda v: f"Signal {v}",
        "rcut": lambda v: "Direction: " + ("across" if v == "x" else "along the axis"),
        "rk": lambda v: f"click τ = {v} fs on a width chart", "rpth": lambda v: f"Profile at the picked τ: {PTH[v]}",
        "rdth": lambda v: f"Maps and delay: angle {PTH[v]}", "rdt": lambda v: f"Maps and delay: τ = {v} fs",
        "rdn": lambda v: f"click N = {v} on a delay chart",
    }
    pk = q.pop("pk", None)
    sets, clicks = [], []
    for k, v in q.items():
        t = lab[k](v)
        (clicks if t.startswith("click ") else sets).append(t[6:] if t.startswith("click ") else t)
    if pk is not None:
        unit = {"theta": "°", "dl": " nm", "pulses": " fs"}.get(mode, "")
        clicks.append(f"{('τ = ' if mode == 'pulses' else 'ε ' if mode == 'eps' else '')}{pk}{unit} on the left chart")
    # quick instructions: which tab, which controls (all others at default), what to click
    parts = [f"**Tab** {TAB[mode]}", "**Set** " + (" · ".join(sets) if sets else "defaults")]
    if clicks:
        parts.append("**Click** " + " · ".join(clicks))
    return "  →  ".join(parts)


def main():
    steps = {s["id"]: s for s in json.loads((HERE / f"steps{TAG}.json").read_text())}
    src = (HERE / f"walkthrough{TAG}.src.md").read_text()
    n = 0

    def step(m):
        nonlocal n
        n += 1
        s = steps[m.group(1)]
        sl = m.group(2) or ""
        sep = ", " if PULSES else " · "
        lab = (f"[Slide {sl[:-1]}{sep}beyond the slide]{{.slide}} " if sl.endswith("b") else f"[Slide {sl}]{{.slide}} ") if sl else ""
        img = f"img{TAG}/{s['id']}.jpg"
        shot = f"\n\n![]({img})" if (HERE / img).exists() else ""
        return (f'::: step\n{lab}[Step {n}]{{.num}} [Open ↗]({URL}{s["h"]}){{.open}} {sentence(s["h"], s.get("card", ""), bool(s.get("scroll"))) if PULSES else words(s["h"])}'
                + (f" · *scroll to the {s['where']}*" if s.get("where") else "") + f"{shot}\n:::")

    md = re.sub(r"^\[\[(\w+)(?:\|(\w+))?\]\]$", step, src, flags=re.M)
    (HERE / f"walkthrough{TAG}.md").write_text(md)
    html = OUT / f"{NAME}.html"
    subprocess.run(["pandoc", f"walkthrough{TAG}.md", "-s", "--embed-resources", "--css", CSS, "-o", str(html)],
                   cwd=HERE, check=True)
    subprocess.run(["perl", "-e", "alarm 120; exec @ARGV", str(CHROMIUM), "--headless=new", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT / (NAME + '.pdf')}", html.as_uri()], check=True, capture_output=True)
    print(n, "steps ->", OUT / f"{NAME}.pdf")


if __name__ == "__main__":
    main()
