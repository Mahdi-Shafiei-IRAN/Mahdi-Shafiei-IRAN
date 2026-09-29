"""Theme registry. ORDER is the rotation order (a single theme for now)."""

from . import oss_builder

THEMES = {m.NAME: m for m in (oss_builder,)}
ORDER: tuple[str, ...] = tuple(THEMES)
