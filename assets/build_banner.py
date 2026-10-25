# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools[woff]"]
# ///
"""Build the profile header in the NASApunk style, day and night.

Run with `uv run assets/build_banner.py`. Fonts are subset to the glyphs the
header uses and embedded, because GitHub shows SVGs as images, which cannot
load external fonts. The background is transparent so the header sits on the
page like the theme's site header.
"""

import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent

# Text ------------------------------------------------------------------------

NAME = "KKKZOZ"
LINE = ["LIU JINYI", "ML SYSTEMS"]
SITE = "BLOG.KKKZOZ.TOP"

# Palette (from tola-theme-nasapunk, assets/styles/site.css) -------------------

THEMES = {
    "light": dict(ink="#222a2d", orange="#cb4b22", muted="#65716f",
                  rule="#c5c9be", ring="#9aa3a0"),
    "dark": dict(ink="#dde2dc", orange="#ec6e42", muted="#919c99",
                 rule="#3b4447", ring="#7d8986"),
}

# Fonts -----------------------------------------------------------------------

FONTS = {
    "Rajdhani": "rajdhani-latin-700-normal.woff2",
    "Plex": "ibm-plex-mono-latin-500-normal.woff2",
}
TEXT = {
    "Rajdhani": NAME,
    "Plex": "".join(LINE) + "/" + SITE,
}


def font_face(family: str) -> str:
    font = TTFont(HERE / "fonts" / FONTS[family])
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=TEXT[family] + " ")
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f'@font-face {{ font-family: "{family}"; '
            f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}')


# Drawing ---------------------------------------------------------------------

W, H = 1280, 150
RULE_Y = 100


def mark(c: dict, x: float, y: float, s: float) -> str:
    """The theme's favicon: ring, core, orange trajectory, satellite."""
    return f"""<g transform="translate({x} {y}) scale({s})" fill="none">
  <circle cx="16" cy="16" r="13.5" stroke="{c["ring"]}" stroke-width="1.5"/>
  <circle cx="16" cy="16" r="6" stroke="{c["ink"]}" stroke-width="2.2"/>
  <line x1="3.5" y1="24.75" x2="28.5" y2="7.25" stroke="{c["orange"]}" stroke-width="3.2" stroke-linecap="round"/>
  <circle cx="26" cy="4.6" r="2.6" fill="{c["ink"]}"/>
</g>"""


def header(c: dict, faces: str) -> str:
    line = f' <tspan fill="{c["orange"]}">/</tspan> '.join(LINE)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{NAME}: {', '.join(LINE[1:]).lower()}">
<style>
{faces}
.name {{ font: 700 76px Rajdhani; fill: {c["ink"]}; }}
.meta {{ font: 500 15px Plex; letter-spacing: 2.6px; fill: {c["muted"]}; }}
</style>
{mark(c, 2, 18, 2.2)}
<text class="name" x="92" y="80">{NAME}</text>
<line x1="0" y1="{RULE_Y}" x2="{W}" y2="{RULE_Y}" stroke="{c["rule"]}" stroke-width="1.4"/>
<line x1="0" y1="{RULE_Y}" x2="300" y2="{RULE_Y}" stroke="{c["orange"]}" stroke-width="3"/>
<text class="meta" x="0" y="{RULE_Y + 36}">{line}</text>
<text class="meta" x="{W}" y="{RULE_Y + 36}" text-anchor="end">{SITE}</text>
</svg>
"""


def main() -> None:
    faces = "\n".join(font_face(f) for f in FONTS)
    for name, colours in THEMES.items():
        out = HERE / f"banner-{name}.svg"
        out.write_text(header(colours, faces))
        print(f"{out.relative_to(HERE.parent)}: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
