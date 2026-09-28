"""Theme registry. ORDER is the daily rotation order."""

from . import cinematic, terminal, wow

THEMES = {m.NAME: m for m in (terminal, cinematic, wow)}
ORDER: tuple[str, ...] = tuple(THEMES)
