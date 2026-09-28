"""Clickable pieces every theme reuses (project cards, link buttons) and README HTML helpers.

GitHub can't follow links inside an <img>, so each clickable thing is its own SVG
wrapped in an <a> in the README.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .config import Profile
from .github_data import Repo
from .svg import SANS, compact, document, esc, text_width, truncate, wrap

CARD_W, CARD_H = 410, 128
BUTTON_H = 38

LABELS = {
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "website": "Website",
    "email": "Email",
    "x": "X",
    "telegram": "Telegram",
    "youtube": "YouTube",
}

GITHUB_MARK = (
    "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49"
    "-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58"
    " 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31"
    "-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09"
    " 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87"
    " 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0"
    " 0016 8c0-4.42-3.58-8-8-8z"
)


@dataclass(frozen=True)
class Palette:
    bg: str
    border: str
    text: str
    muted: str
    accent: str
    font: str = SANS
    radius: int = 12


def slug(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-") or "link"


def label(key: str) -> str:
    return LABELS.get(key, key.replace("-", " ").replace("_", " ").title())


def icon(key: str, color: str) -> str:
    """A 16x16 icon drawn with plain shapes at the origin."""
    line = f'fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    shapes = {
        "github": f'<path fill="{color}" d="{GITHUB_MARK}"/>',
        "linkedin": f'<rect x="1" y="1" width="14" height="14" rx="3" {line}/>'
        f'<path d="M5 7v4.5M5 4.6v.1M8 11.5V7m0 2c0-1.2.8-2 1.9-2s1.6.8 1.6 2v2.5" {line}/>',
        "website": f'<circle cx="8" cy="8" r="6.5" {line}/>'
        f'<ellipse cx="8" cy="8" rx="2.8" ry="6.5" {line}/><path d="M1.5 8h13" {line}/>',
        "email": f'<rect x="1" y="3" width="14" height="10" rx="2" {line}/>'
        f'<path d="M1.5 4l6.5 5 6.5-5" {line}/>',
        "x": f'<path d="M2.5 2.5l11 11M13.5 2.5l-11 11" {line}/>',
        "telegram": f'<path d="M14.5 2L1.5 7.2l4.6 1.6L12 4.5 7.5 9.8l.3 4.2 2.4-3 3.4 2.5z" {line}/>',
        "youtube": f'<rect x="1" y="3" width="14" height="10" rx="3" {line}/>'
        f'<path d="M6.5 5.8v4.4L10.3 8z" fill="{color}"/>',
    }
    return shapes.get(
        key,
        f'<path d="M6.5 9.5l3-3M7 4.5l1.2-1.2a2.8 2.8 0 014 4L11 8.5'
        f'M9 11.5l-1.2 1.2a2.8 2.8 0 01-4-4L5 7.5" {line}/>',
    )


def link_button(key: str, p: Palette) -> str:
    text = label(key)
    width = round(52 + text_width(text, 14))
    body = (
        f'<rect x="1" y="1" width="{width - 2}" height="{BUTTON_H - 2}" rx="{min(p.radius, 18)}" '
        f'fill="{p.bg}" stroke="{p.border}" stroke-width="1.5"/>'
        f'<g transform="translate(15 11)">{icon(key, p.accent)}</g>'
        f'<text x="40" y="24" font-family="{p.font}" font-size="14" font-weight="600" '
        f'fill="{p.text}">{esc(text)}</text>'
    )
    return document(width, BUTTON_H, body, title=text)


def project_card(repo: Repo, p: Palette, *, prefix: str = "", decor: str = "") -> str:
    desc = wrap(repo.description or "No description yet.", 48, 2)
    lines = "".join(
        f'<text x="22" y="{68 + i * 19}" font-size="13" fill="{p.muted}">{esc(t)}</text>'
        for i, t in enumerate(desc)
    )
    base = CARD_H - 20
    meta, x = "", 22.0
    if repo.language:
        meta += (
            f'<circle cx="{x + 5:g}" cy="{base - 4.5:g}" r="5" fill="{repo.language_color}"/>'
            f'<text x="{x + 15:g}" y="{base:g}" font-size="12" fill="{p.muted}">{esc(repo.language)}</text>'
        )
        x += 15 + text_width(repo.language, 12) + 18
    counts = f"★ {compact(repo.stars)}"
    if repo.forks:
        counts += f"  ·  {compact(repo.forks)} fork{'' if repo.forks == 1 else 's'}"
    meta += f'<text x="{x:g}" y="{base:g}" font-size="12" fill="{p.muted}">{counts}</text>'
    body = (
        f'<g font-family="{p.font}">'
        f'<rect x="1" y="1" width="{CARD_W - 2}" height="{CARD_H - 2}" rx="{p.radius}" '
        f'fill="{p.bg}" stroke="{p.border}" stroke-width="1.5"/>'
        f"{decor}"
        f'<text x="22" y="40" font-size="17" font-weight="700" fill="{p.accent}">'
        f"{esc(truncate(prefix + repo.name, 36))}</text>"
        f"{lines}{meta}</g>"
    )
    return document(CARD_W, CARD_H, body, title=f"{repo.name} project")


def link_assets(profile: Profile, p: Palette) -> dict[str, str]:
    return {f"link-{slug(k)}.svg": link_button(k, p) for k in profile.all_links}


def project_assets(repos: Sequence[Repo], p: Palette, **card_kwargs: str) -> dict[str, str]:
    return {f"project-{i}.svg": project_card(r, p, **card_kwargs) for i, r in enumerate(repos, 1)}


def centered(items: Sequence[str]) -> str:
    if not items:
        return ""
    return '<p align="center">\n  ' + "\n  ".join(items) + "\n</p>"


def image(prefix: str, file: str, alt: str, width: int = 840) -> str:
    return centered([f'<img src="{prefix}{file}" alt="{esc(alt)}" width="{width}">'])


def links_html(profile: Profile, prefix: str) -> str:
    return centered([
        f'<a href="{esc(url)}"><img src="{prefix}link-{slug(key)}.svg" alt="{esc(label(key))}" '
        f'height="{BUTTON_H}"></a>'
        for key, url in profile.all_links.items()
    ])


def projects_html(repos: Sequence[Repo], prefix: str) -> str:
    return centered([
        f'<a href="{esc(r.url)}"><img src="{prefix}project-{i}.svg" alt="{esc(r.name)}" '
        f'width="{CARD_W}"></a>'
        for i, r in enumerate(repos, 1)
    ])


def page(*blocks: str) -> str:
    return "\n\n".join(b for b in blocks if b) + "\n"
