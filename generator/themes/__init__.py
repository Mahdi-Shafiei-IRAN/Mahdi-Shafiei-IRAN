"""Theme registry. ORDER is the daily rotation order."""

from . import terminal

THEMES = {m.NAME: m for m in (terminal,)}
ORDER: tuple[str, ...] = tuple(THEMES)
