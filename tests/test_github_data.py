import pytest
import requests

from conftest import make_payload
from generator.github_data import (
    GitHubDataError,
    cache_json,
    fetch,
    get_data,
    load_cache,
    parse_response,
)


def test_parse_totals(data):
    assert data.login == "Mahdi-Shafiei-IRAN"
    assert data.followers == 42
    assert data.public_repos == 4
    assert data.stars == 17  # 12 + 5 + 0; the forked repo's 99 stars don't count


def test_languages_are_ranked_by_size_without_forks(data):
    assert [lang.name for lang in data.languages] == ["Python", "C#", "HTML"]
    assert data.languages[0].percent == 56.2
    assert round(sum(lang.percent for lang in data.languages)) == 100


def test_featured_uses_pinned_repos_and_skips_non_repos(data):
    assert [r.name for r in data.featured] == ["django-shop", "qt-notes"]
    assert data.featured[0].language_color == "#3572A5"


def test_featured_falls_back_to_top_starred_non_forks():
    d = parse_response(make_payload(pinned=False))
    assert [r.name for r in d.featured] == ["django-shop", "qt-notes", "dotfiles"]
    assert d.featured[2].language == "" and d.featured[2].language_color == "#8b949e"


def test_calendar(data):
    assert len(data.weeks) == 53
    assert data.weeks[0][0].weekday == 0 and data.weeks[0][0].date == "2025-09-28"
    assert len(data.weeks[-1]) == 2
    assert {d.level for week in data.weeks for d in week} == {0, 1, 2, 3, 4}
    assert data.total_contributions == sum(d.count for week in data.weeks for d in week)
    assert data.active_days == sum(1 for week in data.weeks for d in week if d.count)


def test_api_errors_raise():
    with pytest.raises(GitHubDataError, match="Bad credentials"):
        parse_response({"errors": [{"message": "Bad credentials"}]})
    with pytest.raises(GitHubDataError, match="no user"):
        parse_response({"data": {"user": None}})


def test_cache_round_trip(tmp_path, data):
    path = tmp_path / "github.json"
    path.write_text(cache_json(data), encoding="utf-8")
    assert load_cache(path) == data


def test_load_cache_errors(tmp_path):
    with pytest.raises(GitHubDataError, match="no cached data"):
        load_cache(tmp_path / "nope.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{}", encoding="utf-8")
    with pytest.raises(GitHubDataError, match="unreadable"):
        load_cache(broken)


class FakeResponse:
    def __init__(self, status, body):
        self.status_code, self._body = status, body

    def json(self):
        return self._body


class FakeSession:
    def __init__(self, response):
        self.response, self.calls = response, []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_fetch_sends_token_and_login():
    session = FakeSession(FakeResponse(200, make_payload()))
    data = fetch("Mahdi-Shafiei-IRAN", "t0k3n", session=session)
    url, kwargs = session.calls[0]
    assert url == "https://api.github.com/graphql"
    assert kwargs["headers"]["Authorization"] == "bearer t0k3n"
    assert kwargs["json"]["variables"] == {"login": "Mahdi-Shafiei-IRAN"}
    assert data.followers == 42


def test_fetch_http_error():
    with pytest.raises(GitHubDataError, match="HTTP 502"):
        fetch("x", "t", session=FakeSession(FakeResponse(502, {})))


@pytest.fixture
def cache_file(tmp_path, data):
    path = tmp_path / "github.json"
    path.write_text(cache_json(data), encoding="utf-8")
    return path


def test_get_data_prefers_the_api(cache_file):
    fresh = parse_response(make_payload(active=False))
    assert get_data("x", "token", cache_file, fetcher=lambda login, token: fresh) == (fresh, False)


def test_get_data_falls_back_to_cache_on_network_error(cache_file, data):
    def boom(login, token):
        raise requests.ConnectionError("offline")

    assert get_data("x", "token", cache_file, fetcher=boom) == (data, True)


def test_get_data_offline_or_tokenless_never_calls_the_api(cache_file, data):
    def never(login, token):
        raise AssertionError("the API must not be called")

    assert get_data("x", "token", cache_file, offline=True, fetcher=never) == (data, True)
    assert get_data("x", "", cache_file, fetcher=never) == (data, True)


def test_get_data_without_cache_raises(tmp_path):
    def boom(login, token):
        raise GitHubDataError("down")

    with pytest.raises(GitHubDataError, match="no cached data"):
        get_data("x", "token", tmp_path / "none.json", fetcher=boom)
