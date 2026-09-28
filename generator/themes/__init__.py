"""Theme registry. ORDER is the daily rotation order."""

from . import cinematic, terminal

THEMES = {m.NAME: m for m in (terminal, cinematic)}
ORDER: tuple[str, ...] = tuple(THEMES)
