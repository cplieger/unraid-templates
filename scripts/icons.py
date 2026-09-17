#!/usr/bin/env python3
"""Render the repository icon, one icon per template, and the copied brand marks.

One design for the generated set. Every glyph sits in the same 40x32 box on the
same square off-white tile, is drawn with one stroke width and one corner
radius, uses solid dots of one size for its marks, and takes its colour from one
perceptual lightness and chroma with the hue set by the app's ecosystem. Unraid draws the
PNG as-is at 32x32 with no rounding and no theme adaptation, so the tile is
what keeps the glyph readable on every theme. The SVG sources land in
icons/src/ and the PNGs beside the templates; run with
`uv run --with cairosvg scripts/icons.py`.

Apps that already ship their own mark keep it: icons/brand/*.svg holds those
copied verbatim from the app's own favicon, and this script only rasterises
them, so they are the one part of icons/ that is edited as art rather than
generated from the constants below.
"""

import math
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent.parent
SIZE = 512
VIEW = 64
TILE = '#f7f5f4'
STROKE = 4.5
CORNER = 4
DOT = 2.8
# One perceptual lightness and chroma (OKLCH) for the whole family, the
# highest chroma every hue below reaches inside sRGB at this lightness; only the
# hue changes, and the hue says what the app talks to.
LIGHTNESS, CHROMA = 0.55, 0.136
ECOSYSTEM = {
    'subflux': 32,  # subflux's own red, also the repository mark
    'plex': 55,  # the nearest in-gamut hue to Plex's gold
    'arr': 255,  # Sonarr's blue
    'storage': 150,  # green for the tools that work on the filesystem
}


def hue(degrees):
    """OKLCH (LIGHTNESS, CHROMA, degrees) as an sRGB hex colour."""
    a = CHROMA * math.cos(math.radians(degrees))
    b = CHROMA * math.sin(math.radians(degrees))
    l_ = LIGHTNESS + 0.3963377774 * a + 0.2158037573 * b
    m_ = LIGHTNESS - 0.1055613458 * a - 0.0638541728 * b
    s_ = LIGHTNESS - 0.0894841775 * a - 1.2914855480 * b
    lin = (
        +4.0767416621 * l_**3 - 3.3077115913 * m_**3 + 0.2309699292 * s_**3,
        -1.2684380046 * l_**3 + 2.6097574011 * m_**3 - 0.3413193965 * s_**3,
        -0.0041960863 * l_**3 - 0.7034186147 * m_**3 + 1.7076147010 * s_**3,
    )
    channels = []
    for c in lin:
        if not 0 <= c <= 1:
            msg = f'hue {degrees} at L={LIGHTNESS} C={CHROMA} leaves sRGB'
            raise ValueError(msg)
        channels.append(12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)
    return '#' + ''.join(f'{round(c * 255):02x}' for c in channels)


def rect(x, y, w, h, r=CORNER):
    return (
        f'M{x + r} {y}h{w - 2 * r}a{r} {r} 0 0 1 {r} {r}v{h - 2 * r}a{r} {r} 0 0 1-{r} {r}'
        f'h-{w - 2 * r}a{r} {r} 0 0 1-{r}-{r}v-{h - 2 * r}a{r} {r} 0 0 1 {r}-{r}z'
    )


def dot(cx, cy, r=DOT):
    return f'M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0-{2 * r} 0z'


# The glyph box: x 12..52, y 16..48.
# The frame pinched at the waist: a cell about to divide.
CELL = (
    'M16 16c8 0 10 11 16 11s8-11 16-11a4 4 0 0 1 4 4v24a4 4 0 0 1-4 4'
    'c-8 0-10-11-16-11s-8 11-16 11a4 4 0 0 1-4-4V20a4 4 0 0 1 4-4z'
)
# name -> (ecosystem, [(kind, path)]) where kind is 'line' (stroked) or 'fill'
GLYPHS = {
    # a screen carrying two subtitle lines
    'subflux': (
        'subflux',
        [
            ('line', rect(12, 16, 40, 32)),
            ('line', 'M20 39h14'),
            ('line', 'M40 39h4'),
        ],
    ),
    # the frame as a sync loop (top bar right, bottom bar left) around a sound mark
    'plex-language-sync': (
        'plex',
        [
            ('line', 'M12 28v-8a4 4 0 0 1 4-4h30'),
            ('line', 'M41 11l5 5-5 5'),
            ('line', 'M52 36v8a4 4 0 0 1-4 4H18'),
            ('line', 'M23 43l-5 5 5 5'),
            ('line', 'M24 29v6M32 25v14M40 29v6'),
        ],
    ),
    # a player with an arrow leaving it
    'plex-exporter': (
        'plex',
        [
            ('line', 'M36 16H16a4 4 0 0 0-4 4v24a4 4 0 0 0 4 4h32a4 4 0 0 0 4-4V32'),
            ('line', 'M40 28L52 16'),
            ('line', 'M44 16h8v8'),
            ('fill', 'M20 27l14 8-14 8z'),
        ],
    ),
    # a map: a trail of marks leading to the X
    'seadex-scout': (
        'arr',
        [
            ('line', rect(12, 16, 40, 32)),
            ('fill', dot(21, 39)),
            ('fill', dot(28, 30)),
            ('fill', dot(35, 38)),
            ('line', 'M39 25l6 6M45 25l-6 6'),
        ],
    ),
    # the frame itself as a cell in mitosis: a pinched waist and a nucleus on each side
    'fclones-scheduler': (
        'storage',
        [
            ('line', CELL),
            ('fill', dot(22, 32)),
            ('fill', dot(42, 32)),
        ],
    ),
}
# the catalogue: four squares filling the glyph box
REPO_GLYPH = ('subflux', [('fill', rect(x, y, 14, 14)) for x in (16, 34) for y in (16, 34)])


def svg(ecosystem, shapes):
    accent = hue(ECOSYSTEM[ecosystem])
    style = {
        'line': (
            f'fill="none" stroke="{accent}" stroke-width="{STROKE}" '
            'stroke-linecap="round" stroke-linejoin="round"'
        ),
        'fill': f'fill="{accent}"',
    }
    body = ''.join(f'<path {style[kind]} d="{d}"/>' for kind, d in shapes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}">'
        f'<rect width="{VIEW}" height="{VIEW}" fill="{TILE}"/>{body}</svg>'
    )


def rasterise(source):
    return cairosvg.svg2png(bytestring=source.encode(), output_width=SIZE, output_height=SIZE)


def render(ecosystem, shapes):
    source = svg(ecosystem, shapes)
    return source, rasterise(source)


def main():
    src = ROOT / 'icons' / 'src'
    src.mkdir(parents=True, exist_ok=True)
    for name, (ecosystem, shapes) in GLYPHS.items():
        source, png = render(ecosystem, shapes)
        (src / f'{name}.svg').write_text(source + '\n')
        (ROOT / 'icons' / f'{name}.png').write_bytes(png)
    source, png = render(*REPO_GLYPH)
    (src / 'icon.svg').write_text(source + '\n')
    (ROOT / 'icon.png').write_bytes(png)
    brands = sorted((ROOT / 'icons' / 'brand').glob('*.svg'))
    for path in brands:
        source = path.read_text()
        if 'rx=' in source:
            msg = f'{path.name} carries a corner radius; Unraid needs the tile square'
            raise ValueError(msg)
        (ROOT / 'icons' / f'{path.stem}.png').write_bytes(rasterise(source))
    print(f'wrote {len(GLYPHS)} app icons, {len(brands)} brand icons and icon.png')


if __name__ == '__main__':
    main()
