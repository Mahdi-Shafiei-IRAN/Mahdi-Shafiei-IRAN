import io

import pytest
from PIL import Image

from conftest import make_portrait
from generator.config import parse_profile
from generator.photo import RAMP, SIZE, Photo, load_photo, square


@pytest.fixture
def profile(profile_raw):
    return parse_profile(profile_raw)


def test_square_crops_and_resizes():
    img = square(Image.new("RGB", (400, 200), "red"))
    assert img.size == (SIZE, SIZE) and img.mode == "RGB"


def test_loads_photo_from_profile_path(tmp_path, profile_raw, data):
    make_portrait().save(tmp_path / "me.png")
    profile = parse_profile({**profile_raw, "photo": "me.png"})
    photo = load_photo(profile, data, tmp_path, downloader=lambda url: pytest.fail("must not download"))
    assert photo.available and photo.image.size == (SIZE, SIZE)


def test_downloads_avatar_when_no_photo_is_set(tmp_path, profile, data):
    buffer = io.BytesIO()
    make_portrait().save(buffer, format="PNG")
    seen = []
    photo = load_photo(profile, data, tmp_path, downloader=lambda url: seen.append(url) or buffer.getvalue())
    assert photo.available and seen == ["https://avatars.example.com/u/1.png"]


def test_offline_skips_the_avatar_download(tmp_path, profile, data):
    photo = load_photo(profile, data, tmp_path, offline=True, downloader=lambda url: pytest.fail("no network"))
    assert not photo.available and photo.initials == "MS"


def test_broken_or_missing_photo_falls_back_to_initials(tmp_path, profile_raw, data):
    (tmp_path / "broken.png").write_bytes(b"not an image")
    for name in ("broken.png", "missing.png"):
        profile = parse_profile({**profile_raw, "photo": name})
        assert not load_photo(profile, data, tmp_path).available


def test_ascii_dimensions_and_brightness():
    art = Photo(square(make_portrait()), "MS").ascii(40, 20)
    assert len(art) == 20 and all(len(line) == 40 for line in art)
    assert art[0][0] == " "                     # dark backdrop -> blank
    assert RAMP.index(art[8][20]) > len(RAMP) // 2  # bright face -> dense glyph


def test_data_uri_is_jpeg():
    assert Photo(square(make_portrait()), "MS").data_uri().startswith("data:image/jpeg;base64,")


def test_methods_need_an_image():
    with pytest.raises(ValueError):
        Photo(None, "MS").data_uri()
    with pytest.raises(ValueError):
        Photo(None, "MS").ascii(10, 10)
