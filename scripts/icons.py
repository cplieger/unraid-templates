#!/usr/bin/env python3
"""Render the repository icon, one icon per template, and the copied brand marks.

One design for the generated set. Every glyph sits in the same 40x32 box on the
same square tile, is drawn with one stroke width and one corner radius, uses
solid dots of one size for its marks, and takes its colour from one perceptual
lightness and chroma with the hue set by the app's ecosystem. Unraid draws the
PNG as-is at 32x32 with no rounding and no theme adaptation, so the filled tile
is what makes one file work on every theme. The canonical set is the accent tile
with an off-white glyph, square: SVG sources in icons/src/ and PNGs beside the
templates, which is what every <Icon> points at.

The other shape and polarity combinations render to icons/variants/<name>/ so a
future surface can be served without re-deriving them; nothing references them
and Unraid never downloads them. Run with `uv run --with cairosvg scripts/icons.py`.

Apps that already ship their own mark keep it: icons/brand/*.svg holds those
copied verbatim from the app's own favicon, and this script only rasterises and
reshapes them, so they are the one part of icons/ that is edited as art rather
than generated from the constants below.
"""

import math
import re
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent.parent
SIZE = 512
VIEW = 64
TILE = '#f7f5f4'
STROKE = 4.5
CORNER = 4
TILE_CORNER = 12
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
# What Unraid gets, and the alternates kept for a surface that masks differently.
CANONICAL = ('square', 'inverted')
ALTERNATES = (
    ('square', 'classic'),
    ('rounded', 'classic'),
    ('rounded', 'inverted'),
    ('circle', 'classic'),
    ('circle', 'inverted'),
    ('square', 'transparent'),
)
BRAND_ALTERNATES = ('rounded', 'circle')


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


def tile(shape, fill):
    """The background as one SVG element, or nothing when there is no tile."""
    if fill is None:
        return ''
    if shape == 'circle':
        half = VIEW / 2
        return f'<circle cx="{half:g}" cy="{half:g}" r="{half:g}" fill="{fill}"/>'
    radius = f' rx="{TILE_CORNER}"' if shape == 'rounded' else ''
    return f'<rect width="{VIEW}" height="{VIEW}"{radius} fill="{fill}"/>'


def svg(ecosystem, shapes, shape='square', ink='inverted'):
    accent = hue(ECOSYSTEM[ecosystem])
    background, glyph = {
        'classic': (TILE, accent),
        'inverted': (accent, TILE),
        'transparent': (None, accent),
    }[ink]
    style = {
        'line': (
            f'fill="none" stroke="{glyph}" stroke-width="{STROKE}" '
            'stroke-linecap="round" stroke-linejoin="round"'
        ),
        'fill': f'fill="{glyph}"',
    }
    body = ''.join(f'<path {style[kind]} d="{d}"/>' for kind, d in shapes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}">'
        f'{tile(shape, background)}{body}</svg>'
    )


BRAND = re.compile(
    r'(<svg\b[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*>)(.*)(</svg>)\s*\Z', re.DOTALL
)


def reshape_brand(source, shape):
    """Clip a copied brand mark to the tile shape; its own art is never redrawn."""
    if shape == 'square':
        return source
    match = BRAND.match(source.strip())
    if match is None:
        msg = 'brand mark has no square viewBox to clip against'
        raise ValueError(msg)
    head, width, height, body, tail = match.groups()
    width, height = float(width), float(height)
    if shape == 'circle':
        half = min(width, height) / 2
        clip = f'<circle cx="{width / 2:g}" cy="{height / 2:g}" r="{half:g}"/>'
    else:
        radius = min(width, height) * TILE_CORNER / VIEW
        clip = f'<rect width="{width:g}" height="{height:g}" rx="{radius:g}"/>'
    return (
        f'{head}<defs><clipPath id="tile">{clip}</clipPath></defs>'
        f'<g clip-path="url(#tile)">{body}</g>{tail}'
    )


def rasterise(source):
    return cairosvg.svg2png(bytestring=source.encode(), output_width=SIZE, output_height=SIZE)


def subjects():
    """Every generated icon as (destination stem, ecosystem, shapes)."""
    yield 'icon', *REPO_GLYPH
    for name, (ecosystem, shapes) in GLYPHS.items():
        yield name, ecosystem, shapes


def write(directory, stem, source):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f'{stem}.svg').write_text(source + '\n')
    (directory / f'{stem}.png').write_bytes(rasterise(source))


def main():
    icons = ROOT / 'icons'
    shape, ink = CANONICAL
    for stem, ecosystem, shapes in subjects():
        source = svg(ecosystem, shapes, shape, ink)
        (icons / 'src' / f'{stem}.svg').parent.mkdir(parents=True, exist_ok=True)
        (icons / 'src' / f'{stem}.svg').write_text(source + '\n')
        target = ROOT / 'icon.png' if stem == 'icon' else icons / f'{stem}.png'
        target.write_bytes(rasterise(source))
    for shape, ink in ALTERNATES:
        directory = icons / 'variants' / (ink if ink == 'transparent' else f'{shape}-{ink}')
        for stem, ecosystem, shapes in subjects():
            write(directory, stem, svg(ecosystem, shapes, shape, ink))
    brands = sorted((icons / 'brand').glob('*.svg'))
    for path in brands:
        source = path.read_text()
        if 'rx=' in source:
            msg = f'{path.name} carries a corner radius; the canonical tile is square'
            raise ValueError(msg)
        (icons / f'{path.stem}.png').write_bytes(rasterise(source))
        for shape in BRAND_ALTERNATES:
            write(icons / 'variants' / f'{shape}-brand', path.stem, reshape_brand(source, shape))
    generated = sum(1 for _ in subjects())
    variants = generated * len(ALTERNATES) + len(brands) * len(BRAND_ALTERNATES)
    print(f'wrote {generated} canonical icons, {len(brands)} brand icons and {variants} variants')


if __name__ == '__main__':
    main()
