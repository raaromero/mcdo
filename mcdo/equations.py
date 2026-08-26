"""Render the deck's LaTeX equations to transparent PNGs.

python-pptx cannot typeset mathematics, so each equation in
:data:`mcdo.deck.LX` is rendered once with matplotlib's mathtext and placed on
the slide as an image. The LaTeX source stays in the slide notes as well, so it
can still be copied into LaTeXiT or MathType.

    python -m mcdo.equations        # -> output/deck/equations/<key>.png
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EQ_DIR = os.path.join(ROOT, "output", "deck", "equations")


def _wrap(text: str, width: int = 92) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def render(latex: str, path: str, fontsize: int = 22, color: str = "#1A1A1A") -> str:
    """Render one equation block to `path` as the formula alone.

    What the equation is and what its symbols mean belongs in the slide bullets
    (`deck.LX_CAPTION`), not burnt into the image: the image is meant to be
    copied straight into a slide, and text baked into it cannot be edited,
    reflowed or read by anything but an eye.
    """
    lines = [ln.strip() for ln in latex.split("\n") if ln.strip()]
    body = "\n".join(f"${ln}$" for ln in lines)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0.0, 0.0, body, fontsize=fontsize, color=color,
             ha="left", va="bottom", linespacing=2.0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.06, transparent=True)
    plt.close(fig)
    return path


def render_all(out_dir: str = EQ_DIR) -> dict[str, str]:
    """Render every equation declared in the deck. Returns {key: path}."""
    from mcdo.deck import LX

    return {key: render(src, os.path.join(out_dir, f"{key}.png"))
            for key, src in LX.items()}


if __name__ == "__main__":
    paths = render_all()
    for key, path in sorted(paths.items()):
        print(f"  {key:12s} -> {os.path.relpath(path, ROOT)}")
    print(f"{len(paths)} equations rendered")
