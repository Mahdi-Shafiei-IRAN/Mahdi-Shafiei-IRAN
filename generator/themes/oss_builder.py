"""OSS Builder theme: neon-green glass cards — hero, live profile scan, projects list and language stack.

Viewers whose GitHub is in light mode get the cream-paper Cap Tip look instead (via <picture>)."""

from __future__ import annotations

from ..components import centered, image, label, page
from ..context import BuildContext
from ..github_data import Repo
from ..svg import MONO, SANS, WIDTH, compact, document, esc, grid, truncate, wrap
from . import cap_tip, snake_trail
from .base import ThemeOutput

NAME = "oss-builder"
TITLE = "OSS Builder"

INK, GLASS = "#050a07", "#04100a"
GREEN, NEON, MINT, SOFT = "#16a34a", "#22c55e", "#4ade80", "#bbf7d0"
MUTED, TRACK = "#6b8f78", "#14231a"

BASE_STYLE = (
    f"svg{{font-family:{MONO}}}"  # inherited, so a text's own font-family attribute still wins
    ".fade{opacity:0;animation:fade .8s ease-out forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".blink{animation:blink 1.1s steps(1) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    ".pulse{animation:pulse 4s ease-in-out infinite}"
    "@keyframes pulse{50%{stroke-opacity:.9}}"
)


def _delay(seconds: float) -> str:
    return f'style="animation-delay:{seconds:.2f}s"'


def _glass(height: float) -> tuple[str, str]:
    """(defs, body) for the glowing outer card every panel sits in."""
    defs = (
        f'<radialGradient id="g1" cx=".28" cy="0" r=".65"><stop offset="0" stop-color="{NEON}" stop-opacity=".7"/>'
        f'<stop offset="1" stop-color="{NEON}" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="g2" cx="1" cy="1" r=".55"><stop offset="0" stop-color="#4c1d95" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="#4c1d95" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="g3" cx=".62" cy="1.05" r=".45"><stop offset="0" stop-color="#bef264" stop-opacity=".5"/>'
        '<stop offset="1" stop-color="#bef264" stop-opacity="0"/></radialGradient>'
        '<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="4" '
        'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )
    body = (
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2:g}" rx="18" fill="{INK}"/>'
        + "".join(
            f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2:g}" rx="18" fill="url(#{g})"/>'
            for g in ("g1", "g2", "g3")
        )
        + f'<rect class="pulse" x="1" y="1" width="{WIDTH - 2}" height="{height - 2:g}" rx="18" fill="none" '
        f'stroke="{NEON}" stroke-opacity=".35" stroke-width="1.5"/>'
    )
    return defs, body


def _inner(x: float, y: float, w: float, h: float) -> str:
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="12" fill="{GLASS}" fill-opacity=".72" '
        f'stroke="{NEON}" stroke-opacity=".45"/>'
    )


def hero_svg(ctx: BuildContext) -> str:
    p, d = ctx.profile, ctx.data
    h = 210
    defs, body = _glass(h)
    cx, cy, r = 96, 92, 46
    defs += (
        f'<clipPath id="face"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
        f'<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/>'
        f'<stop offset="1" stop-color="#86efac"/></linearGradient>'
    )
    if ctx.photo.available:
        face = (
            f'<image href="{ctx.photo.data_uri()}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" '
            'clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        face = (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}"/><text x="{cx}" y="{cy + 12}" '
            f'text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" fill="{INK}">'
            f"{esc(p.initials)}</text>"
        )
    size = min(40.0, 470 / max(1, len(p.name) * 0.6))
    chips, x = [], 40.0
    labels = list(p.skills[:6]) or [lang.name for lang in d.languages[:3]]
    for i, name in enumerate(labels):
        w = max(84.0, len(name) * 7.5 + 30)
        chips.append(
            f'<g class="fade" {_delay(0.9 + i * 0.12)}><rect x="{x:g}" y="160" width="{w:g}" height="26" rx="13" '
            f'fill="none" stroke="{NEON}" stroke-opacity=".6"/><text x="{x + w / 2:g}" y="177" text-anchor="middle" '
            f'font-size="11.5" fill="{MINT}">{esc(name)}</text></g>'
        )
        x += w + 10
    tagline = p.tagline or p.role
    body += (
        _inner(18, 18, WIDTH - 36, h - 36)
        + f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="#fff"/>{face}'
        + f'<text class="fade" x="164" y="66" font-size="12" font-weight="700" letter-spacing="3" fill="{MINT}">'
        f"@{esc(p.username.lower())}</text>"
        + f'<path class="fade" d="M290 58q120-14 180 4" fill="none" stroke="{NEON}" stroke-opacity=".5"/>'
        + f'<text class="fade" {_delay(0.2)} x="162" y="110" font-family="{SANS}" font-size="{size:.0f}" '
        f'font-weight="800" fill="url(#name)" filter="url(#glow)">{esc(p.name)}</text>'
        + f'<text class="fade" {_delay(0.5)} x="164" y="136" font-family="{SANS}" font-size="13.5" '
        f'fill="{SOFT}">{esc(truncate(tagline, 62))}</text>'
        + "".join(chips)
        + f'<text class="fade" {_delay(0.7)} x="712" y="104" text-anchor="middle" font-family="{SANS}" '
        f'font-size="40" font-weight="800" fill="{MINT}" filter="url(#glow)">{compact(d.stars)}</text>'
        + f'<text class="fade" {_delay(0.8)} x="712" y="126" text-anchor="middle" font-size="10" font-weight="700" '
        f'letter-spacing="3" fill="{MINT}">TOTAL STARS</text>'
    )
    return document(WIDTH, h, body, title=f"{p.name}: profile header", style=BASE_STYLE, defs=defs)


def _info_rows(ctx: BuildContext) -> list[tuple[str, str]]:
    p, d = ctx.profile, ctx.data
    contact = site_label(p.links["website"]) if p.links.get("website") else (
        p.links.get("linkedin", "").replace("https://", "").replace("www.", "").replace("linkedin.com/", "")
    )
    rows = [
        ("Subject", p.name),
        ("Handle", f"@{p.username}"),
        ("Role", p.role),
        ("Location", p.location),
        ("Learning", " | ".join(p.learning)),
        ("Languages", ", ".join(lang.name for lang in d.languages[:3])),
        ("Repositories", str(d.public_repos)),
        ("Contributions", f"{d.total_contributions:,}"),
        ("Stars", compact(d.stars)),
        ("Followers", compact(d.followers)),
        ("Contact", contact or f"github.com/{p.username}"),
    ]
    return [(k, v) for k, v in rows if v]


def scan_svg(ctx: BuildContext) -> str:
    h = 370
    defs, body = _glass(h)
    user = ctx.profile.first_name.lower()
    lx, ly, lw, lh = 30, 60, 362, 286
    rx = lx + lw + 14
    rw = WIDTH - 30 - rx
    defs += (
        f'<clipPath id="map"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10"/></clipPath>'
        f'<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NEON}" '
        f'stop-opacity="0"/><stop offset=".5" stop-color="{NEON}" stop-opacity=".4"/>'
        f'<stop offset="1" stop-color="{NEON}" stop-opacity="0"/></linearGradient>'
    )
    if ctx.photo.available:
        cols, rows_n = 66, 34
        pitch = (lh - 40) / rows_n
        art = "".join(
            f'<text class="fade" {_delay(0.3 + i * 0.03)} x="{lx + 14}" y="{ly + 34 + i * pitch:.1f}" '
            f'textLength="{lw - 28}" lengthAdjust="spacing" xml:space="preserve">{esc(line)}</text>'
            for i, line in enumerate(ctx.photo.ascii(cols, rows_n))
        )
        art = f'<g font-size="7.2" fill="{MINT}" style="white-space:pre">{art}</g>'
    else:
        art = (
            f'<text x="{lx + lw / 2}" y="{ly + lh / 2 + 20}" text-anchor="middle" font-family="{SANS}" '
            f'font-size="72" font-weight="800" fill="{MINT}" fill-opacity=".8">{esc(ctx.profile.initials)}</text>'
        )
    info = []
    room = int((rw - 200) / 6.6)
    for i, (key, value) in enumerate(_info_rows(ctx)):
        y = ly + 36 + i * 23
        info.append(
            f'<g class="fade" {_delay(0.4 + i * 0.12)}>'
            f'<text x="{rx + 14}" y="{y}" font-size="11" font-weight="700" fill="{MINT}">{key}</text>'
            f'<path d="M{rx + 104} {y - 3}h{rw - 300}" stroke="{MUTED}" stroke-dasharray="1 4"/>'
            f'<text x="{rx + 214}" y="{y}" font-size="11" fill="{SOFT}">{esc(truncate(value, room))}</text></g>'
        )
    body += (
        _inner(14, 14, WIDTH - 28, h - 28)
        + "".join(
            f'<circle cx="{32 + i * 14}" cy="32" r="4" fill="{c}"/>'
            for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840"))
        )
        + f'<text x="{WIDTH / 2:g}" y="36" text-anchor="middle" font-size="11" fill="{SOFT}">'
        f"{esc(user)}@github ~ $ ./profile-scan --live</text>"
        + f'<text x="{WIDTH - 34}" y="36" text-anchor="end" font-size="10" font-weight="700" fill="{MINT}">'
        f'<tspan class="blink">●</tspan> LIVE</text>'
        + f'<path d="M14 46h{WIDTH - 28}" stroke="{NEON}" stroke-opacity=".3"/>'
        + _inner(lx, ly, lw, lh)
        + f'<text x="{lx + 12}" y="{ly + 16}" font-size="9" letter-spacing="2" fill="{MUTED}">VISUAL.MAP</text>'
        + art
        + f'<g clip-path="url(#map)"><rect class="scan" x="{lx}" y="{ly - 40}" width="{lw}" height="40" '
        'fill="url(#band)"/></g>'
        + _inner(rx, ly, rw, lh)
        + f'<text x="{rx + 12}" y="{ly + 16}" font-size="9" letter-spacing="2" fill="{MUTED}">SYSTEM.INFO</text>'
        + "".join(info)
    )
    style = BASE_STYLE + (
        f".scan{{animation:scan 3.2s linear infinite}}@keyframes scan{{to{{transform:translateY({lh + 40}px)}}}}"
    )
    return document(WIDTH, h, body, title="Live profile scan", style=style, defs=defs)


def _donut(cx: float, cy: float, share: float) -> str:
    r = 17
    circumference = 2 * 3.14159 * r
    arc = circumference * max(0.0, min(share, 1.0))
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="5"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#3b82f6" stroke-width="5" '
        f'stroke-dasharray="{arc:.1f} {circumference:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#a855f7" stroke-width="5" '
        f'stroke-dasharray="{min(arc, 6):.1f} {circumference:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy + 3.5}" text-anchor="middle" font-size="9" font-weight="700" fill="{SOFT}">'
        f"{round(share * 100)}%</text>"
    )


def chosen_projects(ctx: BuildContext) -> tuple[Repo, ...]:
    """profile.yml `projects` (in that order) when set, otherwise the pinned / top-starred repos."""
    by_name = {r.name.lower(): r for r in ctx.data.featured + ctx.data.repos}  # full repo list wins
    picked = tuple(by_name[n.lower()] for n in ctx.profile.projects if n.lower() in by_name)
    return (picked or ctx.data.featured)[:6]


def projects_head_svg(count: int) -> str:
    h = 76
    defs, body = _glass(h)
    body += (
        _inner(14, 14, WIDTH - 28, h - 28)
        + f'<text x="40" y="44" font-size="11" font-weight="700" letter-spacing="3" fill="{MINT}">PROJECTS.LIST</text>'
        + f'<text x="190" y="44" font-size="11" fill="{MUTED}">./projects.sh --featured</text>'
        + f'<text x="{WIDTH - 40}" y="44" text-anchor="end" font-size="10" fill="{MUTED}">'
        f'{count} featured · click a card <tspan class="blink" fill="{MINT}">↓</tspan></text>'
    )
    return document(WIDTH, h, body, title="Projects list", style=BASE_STYLE, defs=defs)


CARD_W, CARD_H = 410, 150


def project_card_svg(repo: Repo, total_stars: int) -> str:
    w, h = CARD_W, CARD_H
    desc = wrap(repo.description or "No description yet.", 44, 2)
    tag = repo.language or "code"
    tag_w = len(tag) * 7 + 22
    defs = (
        f'<radialGradient id="g1" cx=".2" cy="0" r=".8"><stop offset="0" stop-color="{NEON}" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="{NEON}" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="g2" cx="1" cy="1" r=".7"><stop offset="0" stop-color="#4c1d95" stop-opacity=".5"/>'
        '<stop offset="1" stop-color="#4c1d95" stop-opacity="0"/></radialGradient>'
    )
    body = (
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{INK}"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#g1)"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#g2)"/>'
        f'<rect class="pulse" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="none" stroke="{NEON}" '
        'stroke-opacity=".45" stroke-width="1.5"/>'
        f'<text x="16" y="24" font-size="9.5" fill="{MUTED}">▸ {esc(truncate(repo.name, 40))}</text>'
        f'<circle cx="{w - 18}" cy="20" r="3" fill="{NEON}"/>'
        f'<path d="M1 34h{w - 2}" stroke="{NEON}" stroke-opacity=".3"/>'
        f'<text x="18" y="60" font-size="15" font-weight="700" fill="{MINT}">'
        f'{esc(truncate(repo.name, 30))} <tspan class="blink">_</tspan></text>'
        + "".join(
            f'<text x="18" y="{82 + k * 15}" font-size="10.5" fill="{SOFT}">{esc(t)}</text>'
            for k, t in enumerate(desc)
        )
        + f'<rect x="18" y="{h - 42}" width="{tag_w}" height="17" rx="8.5" fill="none" stroke="{NEON}" '
        'stroke-opacity=".6"/>'
        + f'<text x="{18 + tag_w / 2}" y="{h - 30}" text-anchor="middle" font-size="9" fill="{MINT}">'
        f"{esc(tag.lower())}</text>"
        + f'<text x="{28 + tag_w}" y="{h - 30}" font-size="10" fill="{MUTED}">★ {compact(repo.stars)}</text>'
        + f'<text x="{w - 18}" y="{h - 14}" text-anchor="end" font-size="10" font-weight="700" fill="{MINT}">'
        'open repo →</text>'
        + _donut(w - 44, 82, repo.stars / max(1, total_stars))
    )
    return document(w, h, body, title=f"{repo.name} project", style=BASE_STYLE, defs=defs)


def stack_svg(ctx: BuildContext) -> str:
    langs = ctx.data.languages[:5]
    h = 124 + len(langs) * 30
    defs, body = _glass(h)
    defs += (
        f'<linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/>'
        f'<stop offset="1" stop-color="#86efac"/></linearGradient>'
    )
    rows = []
    bar_x, bar_w = 290, 500
    for i, lang in enumerate(langs):
        y = 116 + i * 30
        w = bar_w * lang.percent / 100
        rows.append(
            f'<circle cx="48" cy="{y - 4}" r="4.5" fill="{lang.color}"/>'
            f'<text x="62" y="{y}" font-size="12" font-weight="700" fill="{MINT}">{esc(lang.name)}</text>'
            f'<text x="266" y="{y}" text-anchor="end" font-size="12" font-weight="700" fill="{lang.color}">'
            f"{lang.percent:g}%</text>"
            f'<rect x="{bar_x}" y="{y - 8}" width="{bar_w}" height="7" rx="3.5" fill="{TRACK}"/>'
            f'<rect x="{bar_x}" y="{y - 8}" width="0" height="7" rx="3.5" fill="{lang.color}">'
            f'<animate attributeName="width" values="0;{w:.1f}" dur="1s" begin="{0.3 + i * 0.2:.1f}s" '
            'fill="freeze"/></rect>'
        )
    body += (
        _inner(18, 18, WIDTH - 36, h - 36)
        + f'<text x="40" y="60" font-family="{SANS}" font-size="24" font-weight="800" fill="url(#title)">'
        "Language Stack</text>"
        + f'<text x="40" y="80" font-family="{SANS}" font-size="11.5" font-weight="700" fill="#86efac">'
        "Repository-weighted technologies</text>"
        + f'<text x="{WIDTH - 50}" y="60" text-anchor="end" font-size="12" font-weight="700" fill="{MINT}">'
        f'&gt; stack.scan <tspan class="blink">_</tspan></text>'
        + "".join(rows)
    )
    return document(WIDTH, h, body, title="Language stack", style=BASE_STYLE, defs=defs)


HEAT = ("#10231a", "#0e4429", "#006d32", "#26a641", "#39d353")
PITCH, CELL = 14, 11


def contrib_svg(ctx: BuildContext) -> str:
    """Contribution Activity: the year's heatmap in neon green, with a snake eating every active day."""
    gx, gy = (WIDTH - 53 * PITCH) // 2, 104
    h = gy + 7 * PITCH + 40
    defs, body = _glass(h)
    defs += (
        f'<linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/>'
        f'<stop offset="1" stop-color="#86efac"/></linearGradient>'
    )
    lx = WIDTH - 50 - 5 * PITCH - 34
    legend = (
        f'<text x="{lx - 8}" y="62" text-anchor="end" font-size="10.5" fill="{MUTED}">Less</text>'
        + "".join(
            f'<rect x="{lx + i * PITCH}" y="52" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
            for i, color in enumerate(HEAT)
        )
        + f'<text x="{lx + 5 * PITCH + 4}" y="62" font-size="10.5" fill="{MUTED}">More</text>'
    )
    body += (
        _inner(18, 18, WIDTH - 36, h - 36)
        + f'<text x="40" y="60" font-family="{SANS}" font-size="24" font-weight="800" fill="url(#title)">'
        "Contribution Activity</text>"
        + f'<text x="40" y="82" font-family="{SANS}" font-size="12" font-weight="700" fill="#86efac">'
        f"{ctx.data.total_contributions:,} contributions in the last year · "
        f'<tspan fill="{snake_trail.HEAD}">snake mode</tspan></text>'
        + legend
        + snake_trail.board(ctx, gx, gy, PITCH, CELL, HEAT)
    )
    return document(WIDTH, h, body, title="Contribution activity with a snake", style=BASE_STYLE, defs=defs)


def site_label(url: str) -> str:
    return url.split("://", 1)[-1].rstrip("/")


def visit_svg(ctx: BuildContext, url: str) -> str:
    """A big call-to-action card for the personal website."""
    h = 160
    defs, body = _glass(h)
    defs += (
        f'<linearGradient id="url" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/>'
        f'<stop offset="1" stop-color="#bef264"/></linearGradient>'
    )
    site = site_label(url)
    size = min(46.0, 520 / max(1, len(site) * 0.58))
    bx, by, bw, bh = 612, 54, 190, 52
    body += (
        _inner(18, 18, WIDTH - 36, h - 36)
        + f'<text x="44" y="54" font-size="12" fill="{MUTED}">&gt; portfolio --open '
        f'<tspan class="blink" fill="{MINT}">█</tspan></text>'
        + f'<text class="fade" {_delay(0.2)} x="42" y="{60 + size:.0f}" font-family="{SANS}" font-size="{size:.0f}" '
        f'font-weight="800" fill="url(#url)" filter="url(#glow)">{esc(site)}</text>'
        + f'<text class="fade" {_delay(0.5)} x="44" y="132" font-size="11.5" fill="{SOFT}">'
        "Drag a role · jump through a black hole · read the full story</text>"
        + f'<rect class="ring" x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="none" '
        f'stroke="{NEON}" stroke-width="2"/>'
        + f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{NEON}" filter="url(#glow)"/>'
        + f'<text x="{bx + 64}" y="{by + 33}" text-anchor="middle" font-family="{SANS}" font-size="19" '
        f'font-weight="800" fill="{INK}">VISIT</text>'
        + f'<g class="nudge"><path d="M{bx + 118} {by + 26}h34m-12-12l12 12-12 12" fill="none" stroke="{INK}" '
        'stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
    )
    style = BASE_STYLE + (
        ".nudge{animation:nudge 1.2s ease-in-out infinite}@keyframes nudge{50%{transform:translateX(7px)}}"
        ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2s ease-out infinite}"
        "@keyframes ring{from{opacity:.8;transform:scale(1)}to{opacity:0;transform:scale(1.18,1.5)}}"
    )
    return document(WIDTH, h, body, title=f"Visit {site}", style=style, defs=defs)


def _slot(prefix: str, dark: str, light: str | None, alt: str, link: str = "") -> str:
    """One README image: `dark` for dark-mode viewers, `light` (when given) for light mode."""
    if light:
        img = (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="{prefix}{dark}">'
            f'<img src="{prefix}{light}" alt="{esc(alt)}" width="840"></picture>'
        )
    else:
        img = f'<img src="{prefix}{dark}" alt="{esc(alt)}" width="840">'
    return centered([f'<a href="{link}">{img}</a>' if link else img])


def _card(prefix: str, i: int, repo: Repo) -> str:
    return (
        f'<a href="{esc(repo.url)}"><picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{prefix}project-{i}.svg"><img src="{prefix}light-project-{i}.svg" alt="{esc(repo.name)}" '
        f'width="{CARD_W}"></picture></a>'
    )


def build(ctx: BuildContext) -> ThemeOutput:
    p = ctx.profile
    projects = chosen_projects(ctx)
    has_projects = bool(projects)
    has_stack = bool(ctx.data.languages)
    has_transcript = bool(p.skills or p.learning)
    site = p.links.get("website", "")
    has_contrib = ctx.data.total_contributions > 0  # 0 = no data (e.g. private profile without PROFILE_TOKEN)
    assets = {
        "hero.svg": hero_svg(ctx),
        "scan.svg": scan_svg(ctx),
        "light-portrait.svg": cap_tip.portrait_svg(ctx),
        **({"visit.svg": visit_svg(ctx, site), "light-visit.svg": cap_tip.visit_svg(ctx, site)} if site else {}),
        **({"light-transcript.svg": cap_tip.transcript_svg(ctx)} if has_transcript else {}),
        **({"projects-head.svg": projects_head_svg(len(projects)),
            "light-projects-head.svg": cap_tip.projects_head_svg()} if has_projects else {}),
        **{f"project-{i}.svg": project_card_svg(r, ctx.data.stars) for i, r in enumerate(projects, 1)},
        **{f"light-project-{i}.svg": cap_tip.project_card_svg(r) for i, r in enumerate(projects, 1)},
        **({"stack.svg": stack_svg(ctx), "light-languages.svg": cap_tip.languages_svg(ctx)} if has_stack else {}),
        **({"contrib.svg": contrib_svg(ctx), "light-contrib.svg": cap_tip.contrib_svg(ctx)} if has_contrib else {}),
    }
    def readme(prefix: str) -> str:
        return page(
            _slot(prefix, "hero.svg", "light-portrait.svg", f"{p.name}: profile header", site),
            _slot(prefix, "visit.svg", "light-visit.svg", f"Visit {site_label(site)}", site) if site else "",
            _slot(prefix, "scan.svg", "light-transcript.svg" if has_transcript else None, "Live profile scan"),
            _slot(prefix, "projects-head.svg", "light-projects-head.svg", "Projects list") if has_projects else "",
            centered([_card(prefix, i, r) for i, r in enumerate(projects, 1)]) if has_projects else "",
            _slot(prefix, "stack.svg", "light-languages.svg", "Language stack") if has_stack else "",
            _slot(prefix, "contrib.svg", "light-contrib.svg", "Contribution activity") if has_contrib else "",
            centered([" · ".join(
                [f'<a href="{esc(u)}">{esc(label(k))}</a>' for k, u in p.links.items()]
                + [f'<a href="https://github.com/{p.username}">GitHub</a>']
            )]),
        )

    return ThemeOutput(assets, readme)
