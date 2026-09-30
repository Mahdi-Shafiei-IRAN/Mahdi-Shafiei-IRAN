"""Load and validate profile.yml into a Profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class ConfigError(Exception):
    """profile.yml is missing, unreadable, or has a missing/mistyped field."""


@dataclass(frozen=True)
class Education:
    degree: str = ""
    university: str = ""


@dataclass(frozen=True)
class Profile:
    name: str
    username: str
    role: str
    tagline: str = ""
    location: str = ""
    about: str = ""
    learning: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    education: Education = Education()
    links: dict[str, str] = field(default_factory=dict)
    photo: str = ""
    projects: tuple[str, ...] = ()  # repo names to feature, in order

    @property
    def initials(self) -> str:
        words = [w for w in self.name.split() if w]
        return "".join(w[0] for w in words[:2]).upper() or self.username[:2].upper()

    @property
    def first_name(self) -> str:
        return (self.name.split() or [self.username])[0]

    @property
    def all_links(self) -> dict[str, str]:
        """GitHub first, then the links from profile.yml in file order."""
        return {"github": f"https://github.com/{self.username}", **self.links}


def _text(raw: dict, key: str, *, label: str | None = None, required: bool = False) -> str:
    label = label or key
    value = raw.get(key)
    if value is None:
        if required:
            raise ConfigError(f"profile.yml: '{label}' is required")
        return ""
    if not isinstance(value, str):
        raise ConfigError(f"profile.yml: '{label}' must be text, got {type(value).__name__}")
    value = value.strip()
    if required and not value:
        raise ConfigError(f"profile.yml: '{label}' must not be empty")
    return value


def _list(raw: dict, key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"profile.yml: '{key}' must be a list of text")
    return tuple(v.strip() for v in value if v.strip())


def _links(raw: dict) -> dict[str, str]:
    value = raw.get("links") or {}
    if not isinstance(value, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    ):
        raise ConfigError("profile.yml: 'links' must map names to URLs")
    links: dict[str, str] = {}
    for key, url in value.items():
        key, url = key.strip().lower(), url.strip()
        if not url or key == "github":
            continue
        if key == "email" and not url.startswith("mailto:"):
            url = f"mailto:{url}"
        links[key] = url
    return links


def parse_profile(raw: object) -> Profile:
    if not isinstance(raw, dict):
        raise ConfigError("profile.yml must be a mapping of fields")
    education = raw.get("education") or {}
    if not isinstance(education, dict):
        raise ConfigError("profile.yml: 'education' must be a mapping")
    return Profile(
        name=_text(raw, "name", required=True),
        username=_text(raw, "username", required=True),
        role=_text(raw, "role", required=True),
        tagline=_text(raw, "tagline"),
        location=_text(raw, "location"),
        about=_text(raw, "about"),
        learning=_list(raw, "learning"),
        skills=_list(raw, "skills"),
        education=Education(
            degree=_text(education, "degree", label="education.degree"),
            university=_text(education, "university", label="education.university"),
        ),
        links=_links(raw),
        photo=_text(raw, "photo"),
        projects=_list(raw, "projects"),
    )


def load_profile(path: Path) -> Profile:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{path} not found") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc
    return parse_profile(raw)
