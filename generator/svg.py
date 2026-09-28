"""Shared SVG helpers: escaping, the document wrapper, fonts, text sizing and the contribution grid."""

from __future__ import annotations

import random
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from xml.sax.saxutils import escape

from .github_data import Day

WIDTH = 840
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO_CHAR = 0.6   # width of one monospace glyph, in em
SANS_CHAR = 0.56  # rough average width of a sans-serif glyph, in em


def esc(text: object) -> str:
    return escape(str(text), {'"': "&quot;"})


def document(
    width: float, height: float, body: str, *, title: str, style: str = "", defs: str = ""
) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" '
        f'viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        + (f"<defs>{defs}</defs>" if defs else "")
        + (f"<style>{style}</style>" if style else "")
        + body
        + "</svg>\n"
    )


def text_width(text: str, size: float, *, mono: bool = False) -> float:
    return len(text) * size * (MONO_CHAR if mono else SANS_CHAR)


def compact(n: int) -> str:
    """1234 -> '1.2k', 999 -> '999'."""
    for limit, suffix in ((1_000_000, "M"), (1_000, "k")):
        if n >= limit:
            return f"{n / limit:.1f}".rstrip("0").rstrip(".") + suffix
    return str(n)


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(text, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = truncate(lines[-1] + " …", width)
    return lines


@dataclass(frozen=True)
class Cell:
    col: int
    row: int
    level: int
    count: int


def grid(weeks: Sequence[Sequence[Day]]) -> list[Cell]:
    """One Cell per calendar day: col = week index, row = weekday (0 = Sunday)."""
    return [Cell(c, d.weekday, d.level, d.count) for c, week in enumerate(weeks) for d in week]


def rng(seed: str) -> random.Random:
    """Deterministic randomness so decorations don't change (and cause commits) every day."""
    return random.Random(seed)
