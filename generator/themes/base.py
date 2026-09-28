"""The contract every theme module fulfils: NAME, TITLE and build(ctx) -> ThemeOutput."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeOutput:
    # file name -> SVG text, written to assets/<theme>/<file name>
    assets: dict[str, str]
    # asset path prefix ("assets/terminal/" or "../assets/terminal/") -> README markdown
    readme: Callable[[str], str]
