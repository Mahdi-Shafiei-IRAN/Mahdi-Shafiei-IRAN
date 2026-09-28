"""Cinematic theme: letterbox bars open, the name glows in like a title card, cards follow."""

from __future__ import annotations

from ..components import Palette, image, link_assets, links_html, page, project_assets, projects_html
from ..context import BuildContext
from ..svg import SANS, WIDTH, compact, document, esc, rng, text_width, wrap
from .base import ThemeOutput

NAME = "cinematic"
TITLE = "Cinematic"

INK, PANEL, BORDER = "#07060d", "#130e24", "#3b2d63"
TEXT, MUTED = "#f5f3ff", "#a69cc9"
GOLD, ROSE, VIOLET, CYAN = "#f5c76b", "#ff5e8a", "#8b5cf6", "#5eead4"
PALETTE = Palette(bg=PANEL, border=BORDER, text=TEXT, muted=MUTED, accent=GOLD, radius=10)

BASE_STYLE = (
    f"text{{font-family:{SANS}}}"
    ".fade{opacity:0;animation:fade 1.2s ease-out forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".rise{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}"
    "@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}"
)

HERO_H = 380
BAR_H = 46


def _delay(seconds: float) -> str:
    return f'style="animation-delay:{seconds:.2f}s"'


def _bokeh() -> str:
    r = rng("cinematic-bokeh")
    dots = []
    for _ in range(22):
        size = r.uniform(4, 34)
        dots.append(
            f'<circle cx="{r.uniform(0, WIDTH):.0f}" cy="{r.uniform(BAR_H, HERO_H - BAR_H):.0f}" '
            f'r="{size:.0f}" fill="{r.choice((VIOLET, ROSE, GOLD, CYAN))}" opacity="{r.uniform(.07, .22):.2f}" '
            f'style="animation:drift{r.randint(1, 2)} {r.uniform(9, 18):.1f}s ease-in-out '
            f'-{r.uniform(0, 9):.1f}s infinite alternate"/>'
        )
    return "".join(dots)


def hero_svg(ctx: BuildContext) -> str:
    p = ctx.profile
    size = min(58.0, 720 / max(1, len(p.name) * 0.6))
    mid = HERO_H / 2
    title_attrs = (
        f'x="{WIDTH / 2:g}" y="196" text-anchor="middle" font-size="{size:.0f}" font-weight="800" '
        f'letter-spacing="2"'
    )
    defs = (
        '<linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0620"/>'
        '<stop offset=".55" stop-color="#1d0b3a"/><stop offset="1" stop-color="#3a0d2e"/></linearGradient>'
        f'<radialGradient id="spot" cx=".5" cy=".48" r=".55"><stop offset="0" stop-color="{VIOLET}" '
        'stop-opacity=".4"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c8923a"/>'
        '<stop offset=".5" stop-color="#fff1c1"/><stop offset="1" stop-color="#c8923a"/></linearGradient>'
        '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" '
        'stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<filter id="glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="7" '
        'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<clipPath id="title"><text {title_attrs}>{esc(p.name)}</text></clipPath>'
    )
    style = BASE_STYLE + (
        "@keyframes drift1{to{transform:translate(34px,-26px)}}"
        "@keyframes drift2{to{transform:translate(-30px,22px)}}"
        ".title{opacity:0;animation:title 2.4s cubic-bezier(.2,.7,.2,1) .6s forwards}"
        "@keyframes title{from{opacity:0;letter-spacing:24px}to{opacity:1;letter-spacing:2px}}"
        ".sweep{animation:sweep 5s ease-in-out 3.2s infinite}"
        f"@keyframes sweep{{from{{transform:translateX(0)}}60%,to{{transform:translateX({WIDTH + 260}px)}}}}"
    )
    bars = (
        f'<rect x="0" y="0" width="{WIDTH}" height="{mid:g}" fill="#000">'
        f'<animate attributeName="height" values="{mid:g};{BAR_H}" dur="1.4s" begin=".2s" fill="freeze" '
        'calcMode="spline" keySplines=".6 0 .2 1"/></rect>'
        f'<rect x="0" y="{mid:g}" width="{WIDTH}" height="{mid:g}" fill="#000">'
        f'<animate attributeName="y" values="{mid:g};{HERO_H - BAR_H}" dur="1.4s" begin=".2s" fill="freeze" '
        'calcMode="spline" keySplines=".6 0 .2 1"/>'
        f'<animate attributeName="height" values="{mid:g};{BAR_H}" dur="1.4s" begin=".2s" fill="freeze" '
        'calcMode="spline" keySplines=".6 0 .2 1"/></rect>'
    )
    tagline = (
        f'<text class="fade" {_delay(2.4)} x="{WIDTH / 2:g}" y="270" text-anchor="middle" font-size="14" '
        f'font-style="italic" fill="{MUTED}">“{esc(p.tagline)}”</text>'
        if p.tagline else ""
    )
    body = (
        f'<rect width="{WIDTH}" height="{HERO_H}" fill="url(#sky)"/>'
        f'<rect width="{WIDTH}" height="{HERO_H}" fill="url(#spot)"/>'
        f"{_bokeh()}"
        f'<g class="fade" {_delay(1.0)}>'
        f'<path d="M258 111h60M522 111h60" stroke="{GOLD}" stroke-opacity=".6"/>'
        f'<text x="{WIDTH / 2:g}" y="116" text-anchor="middle" font-size="12" font-weight="700" '
        f'letter-spacing="8" fill="{GOLD}">NOW SHOWING</text></g>'
        f'<text class="title" {title_attrs} fill="url(#gold)" filter="url(#glow)">{esc(p.name)}</text>'
        f'<g clip-path="url(#title)"><g transform="skewX(-20)"><rect class="sweep" x="-220" y="130" '
        'width="160" height="90" fill="url(#sweep)"/></g></g>'
        f'<text class="fade" {_delay(1.8)} x="{WIDTH / 2:g}" y="238" text-anchor="middle" font-size="19" '
        f'letter-spacing="1" fill="{TEXT}">{esc(p.role)}</text>'
        f"{tagline}{bars}"
        f'<path d="M0 {BAR_H + .5}h{WIDTH}M0 {HERO_H - BAR_H - .5}h{WIDTH}" stroke="{GOLD}" stroke-opacity=".35" '
        f'class="fade" {_delay(1.6)}/>'
        f'<text class="fade" {_delay(2.9)} x="{WIDTH / 2:g}" y="{HERO_H - 18}" text-anchor="middle" '
        f'font-size="11" letter-spacing="5" fill="{MUTED}">A {esc(ctx.data.login.upper())} PRODUCTION</text>'
    )
    return document(WIDTH, HERO_H, body, title=f"{p.name}: cinematic title card", style=style, defs=defs)


def stats_svg(ctx: BuildContext) -> str:
    d = ctx.data
    stats = (
        ("Followers", d.followers),
        ("Repositories", d.public_repos),
        ("Stars", d.stars),
        ("Contributions", d.total_contributions),
    )
    w, gap, h = 195, 20, 120
    cards = []
    for i, (label, value) in enumerate(stats):
        x = i * (w + gap)
        cards.append(
            f'<g transform="translate({x} 6)"><g class="rise" {_delay(i * 0.18)}>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 14}" rx="12" fill="{PANEL}" stroke="url(#edge)" '
            f'stroke-width="1.5"/>'
            f'<rect class="pulse" style="animation-delay:{i * 0.6:.1f}s" x="1" y="1" width="{w - 2}" '
            f'height="{h - 14}" rx="12" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
            f'<text x="{w / 2:g}" y="58" text-anchor="middle" font-size="32" font-weight="800" '
            f'fill="{TEXT}">{compact(value)}</text>'
            f'<text x="{w / 2:g}" y="86" text-anchor="middle" font-size="11" letter-spacing="3" '
            f'fill="{MUTED}">{label.upper()}</text></g></g>'
        )
    defs = (
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ROSE}"/>'
        f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
    )
    style = BASE_STYLE + (
        ".pulse{stroke-opacity:0;animation:pulse 4s ease-in-out infinite}"
        "@keyframes pulse{50%{stroke-opacity:.9}}"
    )
    return document(WIDTH, h, "".join(cards), title="Profile statistics", style=style, defs=defs)


def _chip_rows(skills: tuple[str, ...], max_width: float = 800) -> list[list[tuple[str, float]]]:
    rows: list[list[tuple[str, float]]] = [[]]
    used = 0.0
    for skill in skills:
        w = text_width(skill, 14) + 36
        if rows[-1] and used + w > max_width:
            rows.append([])
            used = 0.0
        rows[-1].append((skill, w))
        used += w + 10
    return [r for r in rows if r]


def skills_svg(ctx: BuildContext) -> str:
    parts: list[str] = []
    y = 30.0
    order = 0
    if ctx.profile.about:
        parts.append(
            f'<text x="{WIDTH / 2:g}" y="{y:g}" text-anchor="middle" font-size="12" font-weight="700" '
            f'letter-spacing="6" fill="{GOLD}">— SYNOPSIS —</text>'
        )
        y += 28
        for i, line in enumerate(wrap(ctx.profile.about, 88, 4)):
            parts.append(
                f'<text class="rise" {_delay(i * 0.12)} x="{WIDTH / 2:g}" y="{y:g}" text-anchor="middle" '
                f'font-size="14" font-style="italic" fill="{MUTED}">{esc(line)}</text>'
            )
            y += 22
        y += 22
    if ctx.profile.skills:
        parts.append(
            f'<text x="{WIDTH / 2:g}" y="{y:g}" text-anchor="middle" font-size="12" font-weight="700" '
            f'letter-spacing="6" fill="{GOLD}">— STARRING —</text>'
        )
        y += 22
        for row in _chip_rows(ctx.profile.skills):
            x = (WIDTH - (sum(w for _, w in row) + 10 * (len(row) - 1))) / 2
            for skill, w in row:
                parts.append(
                    f'<g class="rise" {_delay(order * 0.08)}>'
                    f'<rect class="chip" style="animation-delay:{order * 0.35:.2f}s" x="{x:.1f}" y="{y:g}" '
                    f'width="{w:.1f}" height="34" rx="17" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
                    f'<text x="{x + w / 2:.1f}" y="{y + 22:g}" text-anchor="middle" font-size="14" '
                    f'fill="{TEXT}">{esc(skill)}</text></g>'
                )
                x += w + 10
                order += 1
            y += 44
        y += 16
    if ctx.data.languages:
        parts.append(
            f'<text x="{WIDTH / 2:g}" y="{y + 8:g}" text-anchor="middle" font-size="12" font-weight="700" '
            f'letter-spacing="6" fill="{GOLD}">— GENRES —</text>'
        )
        y += 26
        bar_x, bar_w = 70.0, 700.0
        x = bar_x
        slot = bar_w / len(ctx.data.languages)
        for i, lang in enumerate(ctx.data.languages):
            seg = bar_w * lang.percent / 100
            parts.append(
                f'<rect x="{x:.1f}" y="{y:g}" width="0" height="10" fill="{lang.color}">'
                f'<animate attributeName="width" values="0;{seg:.1f}" dur=".8s" begin="{0.4 + i * 0.25:.2f}s" '
                'fill="freeze"/></rect>'
                f'<circle cx="{bar_x + slot * i + 8:.1f}" cy="{y + 32:g}" r="5" fill="{lang.color}"/>'
                f'<text x="{bar_x + slot * i + 18:.1f}" y="{y + 36.5:g}" font-size="13" fill="{TEXT}">'
                f'{esc(lang.name)} <tspan fill="{MUTED}">{lang.percent:g}%</tspan></text>'
            )
            x += seg
        y += 50
    style = BASE_STYLE + (
        ".chip{animation:shine 6s ease-in-out infinite}"
        f"@keyframes shine{{0%,80%,100%{{stroke:{BORDER}}}90%{{stroke:{GOLD}}}}}"
    )
    return document(WIDTH, round(y), "".join(parts), title="Synopsis, skills and languages", style=style)


def _sprockets() -> str:
    holes = "".join(
        f'<rect x="{x}" y="{y}" width="10" height="6" rx="1.5" fill="{INK}"/>'
        for x in range(16, 400, 22)
        for y in (6, 116)
    )
    return holes


def build(ctx: BuildContext) -> ThemeOutput:
    featured = ctx.data.featured
    show_skills = bool(ctx.profile.about or ctx.profile.skills or ctx.data.languages)
    assets = {
        "hero.svg": hero_svg(ctx),
        "stats.svg": stats_svg(ctx),
        **({"skills.svg": skills_svg(ctx)} if show_skills else {}),
        **project_assets(featured, PALETTE, decor=_sprockets()),
        **link_assets(ctx.profile, PALETTE),
    }

    def readme(prefix: str) -> str:
        return page(
            image(prefix, "hero.svg", f"{ctx.profile.name}: cinematic title card"),
            image(prefix, "stats.svg", "Profile statistics"),
            image(prefix, "skills.svg", "Synopsis, skills and languages") if show_skills else "",
            projects_html(featured, prefix),
            links_html(ctx.profile, prefix),
        )

    return ThemeOutput(assets, readme)
