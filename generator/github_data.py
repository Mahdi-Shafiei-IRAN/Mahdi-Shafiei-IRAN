"""Fetch profile statistics from the GitHub GraphQL API, with a JSON cache fallback."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

log = logging.getLogger(__name__)

API_URL = "https://api.github.com/graphql"
DEFAULT_COLOR = "#8b949e"
LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    avatarUrl(size: 256)
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        ...RepoFields
        isFork
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes { ... on Repository { ...RepoFields } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}
fragment RepoFields on Repository {
  name description url stargazerCount forkCount primaryLanguage { name color }
}
"""


class GitHubDataError(Exception):
    """The API answered with an error, or no usable data/cache exists."""


@dataclass(frozen=True)
class Repo:
    name: str
    description: str
    url: str
    stars: int
    forks: int
    language: str
    language_color: str


@dataclass(frozen=True)
class Language:
    name: str
    color: str
    percent: float


@dataclass(frozen=True)
class Day:
    date: str
    count: int
    level: int
    weekday: int


@dataclass(frozen=True)
class GitHubData:
    login: str
    name: str
    avatar_url: str
    followers: int
    public_repos: int
    stars: int
    total_contributions: int
    languages: tuple[Language, ...]
    featured: tuple[Repo, ...]
    weeks: tuple[tuple[Day, ...], ...]
    repos: tuple[Repo, ...] = ()  # every public non-fork repo, most stars first

    @property
    def active_days(self) -> int:
        return sum(1 for week in self.weeks for day in week if day.count > 0)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, raw: dict) -> GitHubData:
        return cls(
            login=raw["login"],
            name=raw["name"],
            avatar_url=raw["avatar_url"],
            followers=raw["followers"],
            public_repos=raw["public_repos"],
            stars=raw["stars"],
            total_contributions=raw["total_contributions"],
            languages=tuple(Language(**x) for x in raw["languages"]),
            featured=tuple(Repo(**x) for x in raw["featured"]),
            weeks=tuple(tuple(Day(**d) for d in week) for week in raw["weeks"]),
            repos=tuple(Repo(**x) for x in raw.get("repos", [])),
        )


def _repo(node: dict) -> Repo:
    lang = node.get("primaryLanguage") or {}
    return Repo(
        name=node["name"],
        description=(node.get("description") or "").strip(),
        url=node["url"],
        stars=node.get("stargazerCount") or 0,
        forks=node.get("forkCount") or 0,
        language=lang.get("name") or "",
        language_color=lang.get("color") or DEFAULT_COLOR,
    )


def _languages(repos: list[dict]) -> tuple[Language, ...]:
    sizes: dict[str, int] = {}
    colors: dict[str, str] = {}
    for repo in repos:
        for edge in (repo.get("languages") or {}).get("edges", []):
            name = edge["node"]["name"]
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colors[name] = edge["node"].get("color") or DEFAULT_COLOR
    total = sum(sizes.values())
    if not total:
        return ()
    ranked = sorted(sizes.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    return tuple(Language(name, colors[name], round(100 * size / total, 1)) for name, size in ranked)


def parse_response(payload: dict) -> GitHubData:
    if payload.get("errors"):
        messages = "; ".join(e.get("message", "unknown error") for e in payload["errors"])
        raise GitHubDataError(f"GitHub API error: {messages}")
    user = (payload.get("data") or {}).get("user")
    if not user:
        raise GitHubDataError("GitHub API returned no user")

    repos = user["repositories"]
    own = [n for n in repos["nodes"] if n and not n.get("isFork")]
    pinned = [_repo(n) for n in user["pinnedItems"]["nodes"] if n and n.get("name")]
    featured = pinned or [_repo(n) for n in own[:4]]
    calendar = user["contributionsCollection"]["contributionCalendar"]

    return GitHubData(
        login=user["login"],
        name=user.get("name") or user["login"],
        avatar_url=user.get("avatarUrl") or "",
        followers=user["followers"]["totalCount"],
        public_repos=repos["totalCount"],
        stars=sum(n.get("stargazerCount") or 0 for n in own),
        total_contributions=calendar["totalContributions"],
        languages=_languages(own),
        featured=tuple(featured[:6]),
        weeks=tuple(
            tuple(
                Day(
                    date=d["date"],
                    count=d["contributionCount"],
                    level=LEVELS.get(d["contributionLevel"], 0),
                    weekday=d["weekday"],
                )
                for d in week["contributionDays"]
            )
            for week in calendar["weeks"]
        ),
        repos=tuple(_repo(n) for n in own),
    )


def fetch(login: str, token: str, session: requests.Session | None = None) -> GitHubData:
    http = session or requests.Session()
    response = http.post(
        API_URL,
        json={"query": QUERY, "variables": {"login": login}},
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme-generator"},
        timeout=30,
    )
    if response.status_code != 200:
        raise GitHubDataError(f"GitHub API returned HTTP {response.status_code}")
    return parse_response(response.json())


def cache_json(data: GitHubData) -> str:
    return json.dumps(data.to_json(), indent=2, ensure_ascii=False) + "\n"


def load_cache(path: Path) -> GitHubData:
    try:
        return GitHubData.from_json(json.loads(path.read_text(encoding="utf-8")))
    except FileNotFoundError as exc:
        raise GitHubDataError(f"no cached data at {path}") from exc
    except (ValueError, KeyError, TypeError) as exc:
        raise GitHubDataError(f"cached data at {path} is unreadable: {exc}") from exc


def get_data(
    login: str,
    token: str,
    cache_path: Path,
    *,
    offline: bool = False,
    fetcher: Callable[[str, str], GitHubData] = fetch,
) -> tuple[GitHubData, bool]:
    """Return (data, came_from_cache). Falls back to the cache when the API is unusable."""
    if offline:
        return load_cache(cache_path), True
    if not token:
        log.warning("no GITHUB_TOKEN/PROFILE_TOKEN set; using cached data")
        return load_cache(cache_path), True
    try:
        return fetcher(login, token), False
    except (requests.RequestException, GitHubDataError, ValueError, KeyError) as exc:
        log.warning("GitHub API failed (%s); using cached data", exc)
        return load_cache(cache_path), True
