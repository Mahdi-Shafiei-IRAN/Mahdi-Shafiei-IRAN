import pytest


@pytest.fixture
def profile_raw() -> dict:
    return {
        "name": "Mahdi Shafiei",
        "username": "Mahdi-Shafiei-IRAN",
        "role": "Computer Engineering Student · Python & Django Developer",
        "tagline": "Coding since 14 — writing, making videos, always learning.",
        "location": "Iran",
        "about": "A computer engineering student who loves building things.",
        "learning": ["Django", "Python"],
        "skills": ["Python", "Django", "Django REST", "Docker", "Git", "Linux", "PostgreSQL", "C#"],
        "education": {"degree": "B.Sc. Computer Engineering", "university": "Example University"},
        "links": {
            "linkedin": "https://linkedin.com/in/mahdi-shafiei-iran",
            "email": "me@example.com",
        },
    }


# --- GitHub API sample data -------------------------------------------------

from datetime import date, timedelta  # noqa: E402

LEVEL_NAMES = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
PATTERN = (0, 0, 1, 3, 0, 6, 10, 0, 2)


def _level(count: int) -> int:
    return 0 if count == 0 else 1 if count < 3 else 2 if count < 6 else 3 if count < 10 else 4


def _repo(name, stars, forks, lang, color, desc, *, fork=False, langs=()):
    return {
        "name": name,
        "description": desc,
        "url": f"https://github.com/Mahdi-Shafiei-IRAN/{name}",
        "stargazerCount": stars,
        "forkCount": forks,
        "primaryLanguage": {"name": lang, "color": color} if lang else None,
        "isFork": fork,
        "languages": {"edges": [{"size": s, "node": {"name": n, "color": c}} for n, c, s in langs]},
    }


def make_payload(*, active: bool = True, pinned: bool = True, repos: bool = True) -> dict:
    """A GraphQL response shaped like GitHub's: 366 days from Sunday 2025-09-28 to Monday 2026-09-28."""
    start = date(2025, 9, 28)
    weeks: list[dict] = []
    total = 0
    for i in range(366):
        day = start + timedelta(days=i)
        count = PATTERN[i % len(PATTERN)] if active else 0
        total += count
        if i % 7 == 0:
            weeks.append({"contributionDays": []})
        weeks[-1]["contributionDays"].append({
            "date": day.isoformat(),
            "weekday": (day.weekday() + 1) % 7,
            "contributionCount": count,
            "contributionLevel": LEVEL_NAMES[_level(count)],
        })
    nodes = [
        _repo("django-shop", 12, 3, "Python", "#3572A5",
              "An online shop built with Django & DRF: carts, payments and an admin dashboard for sellers.",
              langs=[("Python", "#3572A5", 9000), ("HTML", "#e34c26", 3000)]),
        _repo("qt-notes", 5, 1, "C#", "#178600", "Desktop note-taking app.",
              langs=[("C#", "#178600", 4000)]),
        _repo("forked-lib", 99, 20, "Go", "#00ADD8", "A fork.", fork=True,
              langs=[("Go", "#00ADD8", 50000)]),
        _repo("dotfiles", 0, 0, None, None, ""),
    ] if repos else []
    pin = [{k: v for k, v in n.items() if k not in ("isFork", "languages")} for n in nodes[:2]]
    pinned_nodes = [pin[0], {}, pin[1]] if pinned and pin else []  # {} = a pinned gist, must be skipped
    return {"data": {"user": {
        "login": "Mahdi-Shafiei-IRAN",
        "name": "Mahdi Shafiei",
        "avatarUrl": "https://avatars.example.com/u/1.png",
        "followers": {"totalCount": 42},
        "repositories": {"totalCount": len(nodes), "nodes": nodes},
        "pinnedItems": {"nodes": pinned_nodes},
        "contributionsCollection": {"contributionCalendar": {"totalContributions": total, "weeks": weeks}},
    }}}


@pytest.fixture
def payload() -> dict:
    return make_payload()


@pytest.fixture
def data():
    from generator.github_data import parse_response

    return parse_response(make_payload())


# --- photo ------------------------------------------------------------------

from PIL import Image, ImageDraw  # noqa: E402


def make_portrait() -> Image.Image:
    """A bright face on a dark background, like a real portrait photo."""
    img = Image.new("RGB", (400, 400), (20, 20, 24))
    draw = ImageDraw.Draw(img)
    draw.ellipse((130, 70, 270, 240), fill=(226, 190, 160))
    draw.rectangle((90, 262, 310, 400), fill=(44, 44, 52))
    return img


@pytest.fixture
def photo_file(tmp_path):
    path = tmp_path / "me.png"
    make_portrait().save(path)
    return path


# --- theme contexts ---------------------------------------------------------


@pytest.fixture
def ctx(profile_raw, data):
    from generator.config import parse_profile
    from generator.context import BuildContext
    from generator.photo import Photo, square

    profile = parse_profile(profile_raw)
    return BuildContext(profile, data, Photo(square(make_portrait()), profile.initials), date(2026, 9, 28))


@pytest.fixture
def bare_ctx():
    """Minimum profile, no contributions, no repos, no photo."""
    from generator.config import parse_profile
    from generator.context import BuildContext
    from generator.github_data import parse_response
    from generator.photo import Photo

    profile = parse_profile({"name": "Ada", "username": "ada", "role": "Engineer"})
    data = parse_response(make_payload(active=False, pinned=False, repos=False))
    return BuildContext(profile, data, Photo(None, profile.initials), date(2026, 9, 28))
