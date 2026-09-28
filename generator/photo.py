"""Load the profile photo (profile.yml `photo` or the GitHub avatar) and turn it into SVG-ready forms."""

from __future__ import annotations

import base64
import io
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageOps

from .config import Profile
from .github_data import GitHubData

log = logging.getLogger(__name__)

SIZE = 256
# sparse -> dense; dense glyphs mark bright pixels because the portrait is light text on a dark canvas
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
DARK_CUTOFF = 60  # after auto-contrast, pixels darker than this become blank so a dark backdrop vanishes


@dataclass(frozen=True)
class Photo:
    image: Image.Image | None
    initials: str

    @property
    def available(self) -> bool:
        return self.image is not None

    def data_uri(self) -> str:
        if self.image is None:
            raise ValueError("no photo available")
        buffer = io.BytesIO()
        self.image.save(buffer, format="JPEG", quality=85)
        return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")

    def ascii(self, cols: int, rows: int) -> list[str]:
        if self.image is None:
            raise ValueError("no photo available")
        w, h = self.image.size
        framed = self.image.crop((int(w * 0.12), 0, int(w * 0.88), int(h * 0.76)))  # head and shoulders
        gray = ImageOps.autocontrast(framed.convert("L"), cutoff=1)
        gray = gray.point(lambda v: 0 if v < DARK_CUTOFF else v).resize((cols, rows))
        top = len(RAMP) - 1
        return [
            "".join(RAMP[gray.getpixel((x, y)) * top // 255] for x in range(cols))
            for y in range(rows)
        ]


def square(image: Image.Image) -> Image.Image:
    """Center-crop to a square and resize to SIZE x SIZE RGB."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    return ImageOps.fit(image, (SIZE, SIZE), method=Image.Resampling.LANCZOS)


def download(url: str) -> bytes:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


def load_photo(
    profile: Profile,
    data: GitHubData,
    root: Path,
    *,
    offline: bool = False,
    downloader: Callable[[str], bytes] = download,
) -> Photo:
    image = None
    try:
        if profile.photo:
            image = square(Image.open(root / profile.photo))
        elif data.avatar_url and not offline:
            image = square(Image.open(io.BytesIO(downloader(data.avatar_url))))
    except (OSError, requests.RequestException) as exc:
        log.warning("photo unavailable (%s); drawing initials instead", exc)
        image = None
    return Photo(image=image, initials=profile.initials)
