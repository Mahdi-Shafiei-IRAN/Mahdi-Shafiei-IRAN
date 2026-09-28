"""Wow theme: an extruded 3D wordmark with a light sweep, next to an ASCII portrait that prints itself."""

from __future__ import annotations

import pyfiglet

from ..components import Palette, image, link_assets, links_html, page, project_assets, projects_html
from ..context import BuildContext
from ..svg import MONO, SANS, WIDTH, compact, document, esc, truncate, wrap
from .base import ThemeOutput

NAME = "wow"
TITLE = "Wow profile"

INK, PANEL, BORDER = "#06060b", "#0c0b16", "#2a2440"
TEXT, MUTED = "#eeeaff", "#9d97c0"
PINK, VIOLET, SKY = "#f0abfc", "#a78bfa", "#67e8f9"
PALETTE = Palette(bg=PANEL, border=BORDER, text=TEXT, muted=MUTED, accent=PINK, radius=14)

HERO_H = 420
DEPTH = 14
ASCII_COLS, ASCII_ROWS = 76, 44
PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 452, 34, 356, 352

STYLE = (
    f"text{{font-family:{SANS}}}"
    ".pop{opacity:0;transform-box:fill-box;transform-origin:center;"
    "animation:pop 1.1s cubic-bezier(.2,.8,.2,1.2) .2s forwards}"
    "@keyframes pop{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:none}}"
    ".float{animation:float 6s ease-in-out 1.4s infinite}"
    "@keyframes float{50%{transform:translateY(-5px)}}"
    ".fade{opacity:0;animation:fade .9s ease-out forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".ln{opacity:0;animation:fade .2s linear forwards}"
    ".shine{animation:shine 4.5s ease-in-out 1.6s infinite}"
    "@keyframes shine{from{transform:translateX(0)}55%,to{transform:translateX(560px)}}"
    ".scan{animation:scan 3.6s linear infinite}"
    f"@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({PANEL_H}px)}}}}"
)


def _mix(a: str, b: str, t: float) -> str:
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def _name_lines(name: str) -> list[str]:
    words = name.split() or [name]
    if len(name) <= 10 or len(words) == 1:
        return [name]
    return words[:3]


def _wordmark(ctx: BuildContext) -> tuple[str, str, float]:
    """Returns (wordmark markup, clip-path markup for the top face, bottom y)."""
    lines = _name_lines(ctx.profile.name)
    size = min(78.0, 380 / (max(map(len, lines)) * 0.62))
    x0, y0 = 40.0, 96 + size * 0.8
    layers, faces = [], []
    for k in range(DEPTH, 0, -1):
        color = _mix("#12081f", "#6d28d9", 1 - k / DEPTH)
        for i, line in enumerate(lines):
            layers.append(
                f'<text x="{x0 + k * 0.9:.1f}" y="{y0 + i * size + k * 0.9:.1f}" font-size="{size:.0f}" '
                f'font-weight="900" fill="{color}">{esc(line)}</text>'
            )
    for i, line in enumerate(lines):
        faces.append(
            f'<text x="{x0}" y="{y0 + i * size:.1f}" font-size="{size:.0f}" font-weight="900">{esc(line)}</text>'
        )
    face = "".join(faces).replace("<text ", '<text fill="url(#face)" stroke="#fff" stroke-opacity=".25" ', )
    markup = "".join(layers) + face
    bottom = y0 + (len(lines) - 1) * size + DEPTH
    return markup, "".join(faces), bottom


def _portrait(ctx: BuildContext) -> str:
    left = PANEL_X + 18
    if ctx.photo.available:
        lines = ctx.photo.ascii(ASCII_COLS, ASCII_ROWS)
        pitch = (PANEL_H - 30) / ASCII_ROWS
        return "".join(
            f'<text class="ln" style="animation-delay:{0.6 + i * 0.03:.2f}s" x="{left}" '
            f'y="{PANEL_Y + 22 + i * pitch:.1f}" textLength="{PANEL_W - 36}" lengthAdjust="spacing" '
            f'xml:space="preserve">{esc(line)}</text>'
            for i, line in enumerate(lines)
        )
    art = [ln.rstrip() for ln in pyfiglet.figlet_format(ctx.profile.initials, font="ansi_shadow").splitlines()]
    art = [ln for ln in art if ln.strip()]
    top = PANEL_Y + PANEL_H / 2 - len(art) * 10
    return "".join(
        f'<text class="ln" style="animation-delay:{0.6 + i * 0.08:.2f}s" x="{PANEL_X + PANEL_W / 2:g}" '
        f'y="{top + i * 20:.1f}" text-anchor="middle" font-size="18" xml:space="preserve">{esc(line)}</text>'
        for i, line in enumerate(art)
    )


def hero_svg(ctx: BuildContext) -> str:
    p, d = ctx.profile, ctx.data
    wordmark, face_clip, bottom = _wordmark(ctx)
    defs = (
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#fff" fill-opacity=".08"/></pattern>'
        f'<radialGradient id="blob" cx=".3" cy=".42" r=".45"><stop offset="0" stop-color="{VIOLET}" '
        'stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PINK}"/>'
        f'<stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>'
        '<linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" '
        'stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="faceclip">{face_clip}</clipPath>'
        f'<linearGradient id="ascii" gradientUnits="userSpaceOnUse" x1="{PANEL_X}" y1="{PANEL_Y}" '
        f'x2="{PANEL_X + PANEL_W}" y2="{PANEL_Y + PANEL_H}"><stop offset="0" stop-color="{PINK}"/>'
        f'<stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>'
        f'<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PINK}" '
        f'stop-opacity=".7"/><stop offset="1" stop-color="{SKY}" stop-opacity=".5"/></linearGradient>'
        '<linearGradient id="scanline" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" '
        'stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".16"/></linearGradient>'
        f'<clipPath id="panel"><rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" '
        'rx="16"/></clipPath>'
    )
    y = bottom + 34
    info = []
    for i, line in enumerate(wrap(p.role, 40, 2)):
        info.append(
            f'<text class="fade" style="animation-delay:1s" x="40" y="{y + i * 23:.0f}" font-size="17" '
            f'font-weight="600" fill="{TEXT}">{esc(line)}</text>'
        )
    y += 23 * (len(wrap(p.role, 40, 2)) - 1)
    if p.tagline:
        y += 26
        info.append(
            f'<text class="fade" style="animation-delay:1.2s" x="40" y="{y:.0f}" font-size="13" '
            f'fill="{MUTED}">{esc(truncate(p.tagline, 60))}</text>'
        )
    y += 34
    chips = [(PINK, f"★ {compact(d.stars)} stars"), (VIOLET, f"{compact(d.followers)} followers"),
             (SKY, f"{compact(d.public_repos)} repos")]
    x = 40.0
    for i, (color, label) in enumerate(chips):
        w = len(label) * 7.4 + 26
        info.append(
            f'<g class="fade" style="animation-delay:{1.4 + i * 0.15:.2f}s">'
            f'<rect x="{x:.1f}" y="{y - 17:.0f}" width="{w:.1f}" height="26" rx="13" fill="{color}" '
            f'fill-opacity=".12" stroke="{color}" stroke-opacity=".5"/>'
            f'<text x="{x + w / 2:.1f}" y="{y:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" '
            f'fill="{color}">{esc(label)}</text></g>'
        )
        x += w + 10
    body = (
        f'<rect width="{WIDTH}" height="{HERO_H}" rx="18" fill="{INK}"/>'
        f'<rect width="{WIDTH}" height="{HERO_H}" rx="18" fill="url(#dots)"/>'
        f'<rect width="{WIDTH}" height="{HERO_H}" rx="18" fill="url(#blob)"/>'
        f'<g class="pop"><g class="float">{wordmark}'
        f'<g clip-path="url(#faceclip)"><g transform="skewX(-18)"><rect class="shine" x="-180" y="0" '
        f'width="120" height="{HERO_H}" fill="url(#band)"/></g></g></g></g>'
        + "".join(info)
        + f'<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="16" fill="{PANEL}" '
        f'stroke="url(#rim)" stroke-width="1.5"/>'
        f'<g font-family="{MONO}" font-size="7.4" fill="url(#ascii)">{_portrait(ctx)}</g>'
        f'<g clip-path="url(#panel)"><rect class="scan" x="{PANEL_X}" y="{PANEL_Y - 28}" width="{PANEL_W}" '
        'height="28" fill="url(#scanline)"/></g>'
        f'<text x="{PANEL_X + PANEL_W - 14}" y="{PANEL_Y + PANEL_H + 20}" text-anchor="end" '
        f'font-family="{MONO}" font-size="11" fill="{MUTED}">~/portrait.txt</text>'
    )
    return document(WIDTH, HERO_H, body, title=f"{p.name}: 3D wordmark and ASCII portrait", style=STYLE, defs=defs)


def stats_svg(ctx: BuildContext) -> str:
    d = ctx.data
    stats = (
        ("Contributions", d.total_contributions, PINK),
        ("Stars", d.stars, VIOLET),
        ("Followers", d.followers, SKY),
        ("Repositories", d.public_repos, PINK),
    )
    w, gap, h = 195, 20, 104
    tiles = []
    for i, (label, value, color) in enumerate(stats):
        x = i * (w + gap)
        tiles.append(
            f'<g class="fade" style="animation-delay:{i * 0.15:.2f}s">'
            f'<rect x="{x + 1}" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<rect x="{x + 18}" y="1" width="{w - 36}" height="3" rx="1.5" fill="{color}"/>'
            f'<text x="{x + w / 2:g}" y="56" text-anchor="middle" font-size="30" font-weight="900" '
            f'fill="{color}">{compact(value)}</text>'
            f'<text x="{x + w / 2:g}" y="82" text-anchor="middle" font-size="12" letter-spacing="2" '
            f'fill="{MUTED}">{label.upper()}</text></g>'
        )
    return document(WIDTH, h, "".join(tiles), title="Profile statistics", style=STYLE)


STRIP = (
    f'<defs><linearGradient id="strip" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PINK}"/>'
    f'<stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{SKY}"/></linearGradient></defs>'
    '<rect x="20" y="1" width="370" height="3" rx="1.5" fill="url(#strip)"/>'
)


def build(ctx: BuildContext) -> ThemeOutput:
    featured = ctx.data.featured
    assets = {
        "hero.svg": hero_svg(ctx),
        "stats.svg": stats_svg(ctx),
        **project_assets(featured, PALETTE, decor=STRIP),
        **link_assets(ctx.profile, PALETTE),
    }

    def readme(prefix: str) -> str:
        return page(
            image(prefix, "hero.svg", f"{ctx.profile.name}: 3D wordmark and ASCII portrait"),
            image(prefix, "stats.svg", "Profile statistics"),
            projects_html(featured, prefix),
            links_html(ctx.profile, prefix),
        )

    return ThemeOutput(assets, readme)
