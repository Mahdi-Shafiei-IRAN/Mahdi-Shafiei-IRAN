"""Theme registry. ORDER is the daily rotation order."""

from . import cap_tip, cinematic, snake, space_shooter, terminal, wow

THEMES = {m.NAME: m for m in (terminal, cinematic, wow, space_shooter, cap_tip, snake)}
ORDER: tuple[str, ...] = tuple(THEMES)
