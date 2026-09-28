"""Everything a theme needs to render, bundled so themes never touch files or the network."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .config import Profile
from .github_data import GitHubData
from .photo import Photo


@dataclass(frozen=True)
class BuildContext:
    profile: Profile
    data: GitHubData
    photo: Photo
    day: date
