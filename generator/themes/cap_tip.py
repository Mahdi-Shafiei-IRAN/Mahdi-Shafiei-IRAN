"""Cap Tip look (light mode): a portrait in a golden frame whose graduation cap keeps tipping hello,
on cream paper cards. oss_builder shows these to viewers whose GitHub is in light mode."""

from __future__ import annotations

from ..context import BuildContext
from ..svg import SANS, WIDTH, compact, document, esc, rng, truncate, wrap

NIGHT, INDIGO = "#0f172a", "#1e1b4b"
TEXT, MUTED, SOFT = "#f8fafc", "#94a3b8", "#cbd5e1"
GOLD, TEAL, PINK, SKY = "#fbbf24", "#2dd4bf", "#f472b6", "#60a5fa"
PAPER, PAPER_EDGE, INK, INK_SOFT, MAROON = "#fdf6e3", "#d6c7a1", "#3b3222", "#7c6f57", "#9f1239"
SERIF = "Georgia, 'Times New Roman', serif"

HERO_H = 380
CX, CY, R = 215, 206, 118

FADE = (
    ".up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}"
    "@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
)


def _confetti() -> str:
    r = rng("cap-tip-confetti")
    pieces = []
    for _ in range(42):
        color = r.choice((GOLD, TEAL, PINK, SKY))
        x = r.uniform(0, WIDTH)
        dur = r.uniform(6, 12)
        anim = f'style="animation:fall {dur:.1f}s linear -{r.uniform(0, dur):.1f}s infinite"'
        if r.random() < 0.5:
            pieces.append(f'<rect class="bit" {anim} x="{x:.0f}" y="-16" width="4" height="9" rx="1" fill="{color}"/>')
        else:
            pieces.append(f'<circle class="bit" {anim} cx="{x:.0f}" cy="-12" r="2.5" fill="{color}"/>')
    return f'<g opacity=".55">{"".join(pieces)}</g>'


def _cap() -> str:
    tassel = (
        f'<g class="tassel"><path d="M72 0v38" stroke="{GOLD}" stroke-width="2.5"/>'
        f'<rect x="67" y="36" width="10" height="20" rx="3" fill="{GOLD}"/>'
        f'<path d="M69 56v6M72 56v7M75 56v6" stroke="{GOLD}" stroke-width="1.4"/></g>'
    )
    return (
        f'<g transform="translate({CX} {CY - R + 4}) rotate(-8)"><g class="cap">'
        '<path d="M-54 2L54 2 48 32Q0 44-48 32z" fill="#111827" stroke="#374151" stroke-width="1.5"/>'
        '<path d="M0-26L108-4 0 18-108-4z" fill="#1f2937" stroke="#4b5563" stroke-width="1.5"/>'
        '<path d="M0-26L108-4 0-14-108-4z" fill="#fff" fill-opacity=".06"/>'
        f'<path d="M0-4Q40-6 72 0" fill="none" stroke="{GOLD}" stroke-width="2.5"/>'
        f"{tassel}"
        f'<circle cx="0" cy="-4" r="5" fill="{GOLD}"/></g></g>'
    )


def portrait_svg(ctx: BuildContext) -> str:
    p = ctx.profile
    if ctx.photo.available:
        face = (
            f'<image href="{ctx.photo.data_uri()}" x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}" '
            'clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        face = (
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#mono)"/>'
            f'<text x="{CX}" y="{CY + 26}" text-anchor="middle" font-size="76" font-weight="800" '
            f'fill="{TEXT}">{esc(p.initials)}</text>'
        )
    size = min(40.0, 400 / max(1, len(p.name) * 0.56))
    lines: list[tuple[str, float, str]] = [(p.name, size, "name")]
    if p.education.degree:
        lines.append((p.education.degree, 18, "degree"))
    if p.education.university:
        lines.append((p.education.university, 15, "uni"))
    lines += [(line, 14, "role") for line in wrap(p.role, 44, 2)]
    if p.tagline:
        lines += [(line, 13, "tag") for line in wrap(p.tagline, 50, 2)]
    colors = {"name": TEXT, "degree": GOLD, "uni": SOFT, "role": MUTED, "tag": MUTED}
    y, parts = 118.0, [
        f'<text class="up" x="400" y="104" font-size="12" font-weight="700" letter-spacing="5" '
        f'fill="{GOLD}">ACADEMIC PROFILE</text>'
    ]
    for i, (text, fs, kind) in enumerate(lines):
        y += fs + (14 if kind in ("name", "degree") else 9)
        style = ' font-style="italic"' if kind == "tag" else ""
        weight = ' font-weight="800"' if kind == "name" else ' font-weight="600"' if kind == "degree" else ""
        parts.append(
            f'<text class="up" style="animation-delay:{0.25 + i * 0.15:.2f}s" x="400" y="{y:.0f}" '
            f'font-size="{fs:.0f}"{weight}{style} fill="{colors[kind]}">{esc(text)}</text>'
        )
        if kind == "name":
            parts.append(
                f'<rect class="up" style="animation-delay:.4s" x="400" y="{y + 12:.0f}" width="64" height="3" '
                f'rx="1.5" fill="{GOLD}"/>'
            )
            y += 10
    defs = (
        f'<linearGradient id="night" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NIGHT}"/>'
        f'<stop offset="1" stop-color="{INDIGO}"/></linearGradient>'
        f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fde68a"/>'
        f'<stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#b45309"/></linearGradient>'
        f'<linearGradient id="mono" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TEAL}"/>'
        f'<stop offset="1" stop-color="{SKY}"/></linearGradient>'
        f'<clipPath id="face"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>'
    )
    style = (
        f"text{{font-family:{SANS}}}{FADE}"
        ".bit{transform-box:fill-box;transform-origin:center}"
        f"@keyframes fall{{to{{transform:translateY({HERO_H + 40}px) rotate(540deg)}}}}"
        f".halo{{transform-origin:{CX}px {CY}px;animation:spin 24s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".cap{transform-box:fill-box;transform-origin:85% 100%;animation:tip 3.4s ease-in-out 1s infinite}"
        "@keyframes tip{0%,55%,100%{transform:none}66%,80%{transform:translate(-8px,-26px) rotate(-14deg)}"
        "92%{transform:translate(0,2px)}}"
        ".tassel{transform-box:fill-box;transform-origin:50% 0;animation:swing 1.7s ease-in-out infinite alternate}"
        "@keyframes swing{from{transform:rotate(-9deg)}to{transform:rotate(9deg)}}"
    )
    body = (
        f'<rect width="{WIDTH}" height="{HERO_H}" rx="18" fill="url(#night)"/>{_confetti()}'
        f'<circle class="halo" cx="{CX}" cy="{CY}" r="{R + 22}" fill="none" stroke="{GOLD}" stroke-opacity=".45" '
        'stroke-width="1.5" stroke-dasharray="3 9"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R + 8}" fill="none" stroke="url(#ring)" stroke-width="6"/>'
        f"{face}{_cap()}"
        + "".join(parts)
    )
    return document(WIDTH, HERO_H, body, title=f"{p.name}: graduation portrait", style=style, defs=defs)


def _check(x: float, y: float) -> str:
    return f'<path d="M{x} {y - 4}l3.5 3.5 7-7.5" fill="none" stroke="{MAROON}" stroke-width="2" stroke-linecap="round"/>'


def transcript_svg(ctx: BuildContext) -> str:
    p = ctx.profile
    parts = [
        f'<text x="{WIDTH / 2:g}" y="46" text-anchor="middle" font-size="20" letter-spacing="4" fill="{INK}">'
        "COURSEWORK &amp; SKILLS</text>"
        f'<path d="M60 60h720M60 64h720" stroke="{PAPER_EDGE}"/>'
    ]
    y, order = 100.0, 0
    col_w = 720 / 3
    for i, skill in enumerate(p.skills):
        col, row = i % 3, i // 3
        x, yy = 70 + col * col_w, y + row * 30
        parts.append(
            f'<g class="up" style="animation-delay:{order * 0.06:.2f}s">{_check(x, yy)}'
            f'<text x="{x + 20:.0f}" y="{yy:.0f}" font-size="16" fill="{INK}">{esc(skill)}</text></g>'
        )
        order += 1
    if p.skills:
        y += ((len(p.skills) + 2) // 3) * 30 + 10
    if p.learning:
        parts.append(
            f'<text x="60" y="{y:.0f}" font-size="13" letter-spacing="3" fill="{INK_SOFT}">CURRENTLY STUDYING</text>'
        )
        y += 30
        x = 70.0
        for item in p.learning:
            w = len(item) * 8.6 + 118
            parts.append(
                f'<g class="up" style="animation-delay:{order * 0.06:.2f}s">'
                f'<text x="{x:.0f}" y="{y:.0f}" font-size="16" fill="{INK}">{esc(item)}</text>'
                f'<rect x="{x + len(item) * 8.6 + 10:.0f}" y="{y - 14:.0f}" width="92" height="19" rx="9.5" '
                f'fill="{MAROON}" fill-opacity=".1" stroke="{MAROON}" stroke-opacity=".5"/>'
                f'<text x="{x + len(item) * 8.6 + 56:.0f}" y="{y - 0.5:.0f}" text-anchor="middle" font-size="10" '
                f'letter-spacing="1.5" fill="{MAROON}">IN PROGRESS</text></g>'
            )
            x += w
            order += 1
        y += 20
    h = max(y + 40, 190)
    sx, sy = WIDTH - 96, h - 76
    ring_text = (f"{ctx.data.login.upper()} · GITHUB · " * 3)[:40]
    seal = (
        f'<g class="seal"><circle cx="{sx}" cy="{sy}" r="46" fill="{MAROON}" fill-opacity=".08" stroke="{MAROON}" '
        f'stroke-width="1.5"/><circle cx="{sx}" cy="{sy}" r="32" fill="none" stroke="{MAROON}" stroke-opacity=".5"/>'
        f'<path id="seal-ring" d="M{sx - 39} {sy}a39 39 0 1 1 78 0a39 39 0 1 1-78 0" fill="none"/>'
        f'<text font-size="8" letter-spacing="1.2" fill="{MAROON}"><textPath href="#seal-ring" textLength="236" lengthAdjust="spacing">{esc(ring_text)}'
        "</textPath></text></g>"
        f'<text x="{sx}" y="{sy + 8}" text-anchor="middle" font-size="22" font-weight="700" fill="{MAROON}">'
        f"{esc(p.initials)}</text>"
    )
    style = (
        f"text{{font-family:{SERIF}}}{FADE}"
        f".seal{{transform-origin:{sx}px {sy}px;animation:spin 30s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    body = (
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{h - 2:.0f}" rx="10" fill="{PAPER}" stroke="{PAPER_EDGE}" '
        'stroke-width="2"/>'
        f'<rect x="12" y="12" width="{WIDTH - 24}" height="{h - 24:.0f}" rx="6" fill="none" stroke="{PAPER_EDGE}"/>'
        + "".join(parts)
        + seal
    )
    return document(WIDTH, round(h), body, title="Coursework and skills", style=style)


def _paper(h: float) -> str:
    return (
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{h - 2:.0f}" rx="10" fill="{PAPER}" stroke="{PAPER_EDGE}" '
        'stroke-width="2"/>'
        f'<rect x="12" y="12" width="{WIDTH - 24}" height="{h - 24:.0f}" rx="6" fill="none" stroke="{PAPER_EDGE}"/>'
    )


def _heading(text: str) -> str:
    return (
        f'<text x="{WIDTH / 2:g}" y="46" text-anchor="middle" font-size="20" letter-spacing="4" fill="{INK}">'
        f"{esc(text)}</text><path d=\"M60 60h720M60 64h720\" stroke=\"{PAPER_EDGE}\"/>"
    )


def projects_svg(ctx: BuildContext) -> str:
    repos = ctx.data.featured[:4]
    card_w, card_h, gap = 374, 118, 16
    rows_n = (len(repos) + 1) // 2
    h = 88 + rows_n * card_h + (rows_n - 1) * gap + 30
    cards = []
    for i, repo in enumerate(repos):
        x = 36 + (i % 2) * (card_w + gap + 2)
        y = 84 + (i // 2) * (card_h + gap)
        desc = wrap(repo.description or "No description yet.", 46, 2)
        meta = f"★ {compact(repo.stars)}"
        cards.append(
            f'<g class="up" style="animation-delay:{i * 0.12:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="8" fill="#fffaf0" stroke="{PAPER_EDGE}"/>'
            f'<text x="{x + 18}" y="{y + 32}" font-size="17" font-weight="700" fill="{MAROON}">'
            f"{esc(truncate(repo.name, 34))}</text>"
            + "".join(
                f'<text x="{x + 18}" y="{y + 56 + k * 18}" font-size="13" fill="{INK_SOFT}">{esc(t)}</text>'
                for k, t in enumerate(desc)
            )
            + (f'<circle cx="{x + 23}" cy="{y + card_h - 19}" r="5" fill="{repo.language_color}"/>'
               f'<text x="{x + 34}" y="{y + card_h - 15}" font-size="12" fill="{INK_SOFT}">{esc(repo.language)}</text>'
               if repo.language else "")
            + f'<text x="{x + card_w - 18}" y="{y + card_h - 15}" text-anchor="end" font-size="12" '
            f'fill="{INK_SOFT}">{meta}</text></g>'
        )
    style = f"text{{font-family:{SERIF}}}{FADE}"
    body = _paper(h) + _heading("SELECTED WORK") + "".join(cards)
    return document(WIDTH, round(h), body, title="Selected work", style=style)


def languages_svg(ctx: BuildContext) -> str:
    langs = ctx.data.languages[:5]
    h = 104 + len(langs) * 32
    rows = []
    for i, lang in enumerate(langs):
        y = 104 + i * 32
        w = 440 * lang.percent / 100
        rows.append(
            f'<text x="90" y="{y}" font-size="16" fill="{INK}">{esc(lang.name)}</text>'
            f'<rect x="250" y="{y - 11}" width="440" height="8" rx="4" fill="#efe6cc"/>'
            f'<rect x="250" y="{y - 11}" width="0" height="8" rx="4" fill="{lang.color}">'
            f'<animate attributeName="width" values="0;{w:.1f}" dur="1s" begin="{0.3 + i * 0.2:.1f}s" '
            'fill="freeze"/></rect>'
            f'<text x="750" y="{y}" text-anchor="end" font-size="14" fill="{MAROON}">{lang.percent:g}%</text>'
        )
    style = f"text{{font-family:{SERIF}}}{FADE}"
    body = _paper(h) + _heading("LANGUAGES") + "".join(rows)
    return document(WIDTH, round(h), body, title="Languages", style=style)
