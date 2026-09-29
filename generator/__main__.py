"""Command line: `python -m generator build` or `python -m generator list`."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path

from .build import BuildError, BuildResult, run
from .config import ConfigError
from .github_data import GitHubDataError
from .rotation import TEHRAN, theme_for, theme_for_hour, today_in_tehran
from .themes import ORDER


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m generator", description="Daily rotating profile README.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build README.md, assets/ and previews/")
    build.add_argument("--date", type=date.fromisoformat, help="pretend today is YYYY-MM-DD (Tehran time)")
    build.add_argument("--theme", choices=ORDER, help="ignore the rotation and use this theme")
    build.add_argument("--offline", action="store_true", help="use data/github.json; no network at all")
    build.add_argument("--no-previews", action="store_true", help="build only the README theme")
    build.add_argument("--root", type=Path, default=Path("."), help="repository root (default: current folder)")
    show = sub.add_parser("list", help="print the rotation order, marking today's theme")
    show.add_argument("--date", type=date.fromisoformat, help="pretend today is YYYY-MM-DD (Tehran time)")
    return parser


def _github_output(**values: str) -> None:
    """Expose values to later GitHub Actions steps as steps.<id>.outputs.<name>."""
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            for key, value in values.items():
                fh.write(f"{key}={value}\n")


def _step_summary(result: BuildResult, day: date) -> None:
    """Show the outcome on the GitHub Actions run page."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    lines = [f"### README theme: `{result.theme}` ({day.isoformat()})"]
    if result.failed:
        lines.append(f"- Failed to build: {', '.join(result.failed)}")
    if result.used_cache:
        lines.append("- GitHub API not used or unavailable: built from cached stats")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    day = args.date or today_in_tehran()
    if args.command == "list":
        today = theme_for(day, ORDER)
        for name in ORDER:
            print(f"{'->' if name == today else '  '} {name}")
        return 0
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    try:
        result = run(
            args.root,
            day=day,
            theme=args.theme or (None if args.date else theme_for_hour(datetime.now(TEHRAN), ORDER)),
            offline=args.offline,
            previews=not args.no_previews,
            token=token,
        )
    except (ConfigError, GitHubDataError, BuildError) as exc:
        logging.error("%s", exc)
        return 1
    print(f"README theme: {result.theme} ({day.isoformat()})")
    _github_output(theme=result.theme, date=day.isoformat())
    _step_summary(result, day)
    return 0


if __name__ == "__main__":
    sys.exit(main())
