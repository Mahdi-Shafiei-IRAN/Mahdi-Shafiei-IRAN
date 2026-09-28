"""Build today's README (plus a preview of every theme) in memory, then write it all at once."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import load_profile
from .context import BuildContext
from .github_data import GitHubData, cache_json, fetch, get_data
from .photo import download, load_photo
from .rotation import theme_for
from .themes import ORDER, THEMES
from .themes.base import ThemeOutput

log = logging.getLogger(__name__)

CACHE = "data/github.json"


class BuildError(Exception):
    """An unknown theme was requested, or no theme could be built."""


@dataclass(frozen=True)
class BuildResult:
    theme: str
    failed: tuple[str, ...]
    used_cache: bool


def _stamp(name: str, day: date) -> str:
    return f"<!-- theme: {name} · generated {day.isoformat()} -->\n"


def render(ctx: BuildContext, theme: str, *, previews: bool = True) -> tuple[str, dict[str, str], list[str]]:
    """Returns (theme used for README.md, {relative path: file text}, themes that failed)."""
    if theme not in THEMES:
        raise BuildError(f"unknown theme {theme!r}; choose one of: {', '.join(ORDER)}")
    outputs: dict[str, ThemeOutput] = {}
    failed: list[str] = []

    def attempt(name: str) -> bool:
        try:
            outputs[name] = THEMES[name].build(ctx)
            return True
        except Exception:  # one broken theme must never take the whole profile down
            log.exception("theme %s failed to build", name)
            failed.append(name)
            return False

    start = ORDER.index(theme)
    chosen = next((name for name in ORDER[start:] + ORDER[:start] if attempt(name)), None)
    if chosen is None:
        raise BuildError("every theme failed to build; README left unchanged")
    if previews:
        for name in ORDER:
            if name not in outputs and name not in failed:
                attempt(name)

    files: dict[str, str] = {}
    for name, out in outputs.items():
        for file, svg in out.assets.items():
            files[f"assets/{name}/{file}"] = svg
        if previews:
            files[f"previews/{name}.md"] = out.readme(f"../assets/{name}/") + "\n" + _stamp(name, ctx.day)
    files["README.md"] = outputs[chosen].readme(f"assets/{chosen}/") + "\n" + _stamp(chosen, ctx.day)
    return chosen, files, failed


def write_outputs(root: Path, files: dict[str, str]) -> None:
    """Write every file (LF line endings) and delete leftovers in regenerated asset folders."""
    for folder in {Path(rel).parent for rel in files if rel.startswith("assets/")}:
        keep = {Path(rel).name for rel in files if Path(rel).parent == folder}
        if (root / folder).is_dir():
            for old in (root / folder).iterdir():
                if old.is_file() and old.name not in keep:
                    old.unlink()
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(path)


def run(
    root: Path,
    *,
    day: date,
    theme: str | None = None,
    offline: bool = False,
    previews: bool = True,
    token: str = "",
    fetcher: Callable[[str, str], GitHubData] = fetch,
    downloader: Callable[[str], bytes] = download,
) -> BuildResult:
    profile = load_profile(root / "profile.yml")
    data, from_cache = get_data(profile.username, token, root / CACHE, offline=offline, fetcher=fetcher)
    photo = load_photo(profile, data, root, offline=offline, downloader=downloader)
    ctx = BuildContext(profile, data, photo, day)
    chosen, files, failed = render(ctx, theme or theme_for(day, ORDER), previews=previews)
    if not from_cache:
        files[CACHE] = cache_json(data)
    write_outputs(root, files)
    if failed:
        log.warning("themes that failed to build: %s", ", ".join(failed))
    return BuildResult(theme=chosen, failed=tuple(failed), used_cache=from_cache)
