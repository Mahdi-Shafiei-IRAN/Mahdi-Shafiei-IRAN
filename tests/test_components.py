import xml.etree.ElementTree as ET

from generator.components import (
    CARD_H,
    CARD_W,
    Palette,
    link_button,
    links_html,
    page,
    project_card,
    projects_html,
    slug,
)
from generator.config import parse_profile
from generator.github_data import Repo
from generator.svg import compact, document, esc, grid, truncate, wrap

P = Palette(bg="#000", border="#111", text="#fff", muted="#888", accent="#0f0")


def test_esc():
    assert esc('a & <b> "c"') == "a &amp; &lt;b&gt; &quot;c&quot;"


def test_document_is_valid_svg():
    root = ET.fromstring(document(100, 50, "<rect/>", title="T & co", style="rect{fill:red}"))
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.get("width") == "100" and root.get("viewBox") == "0 0 100 50"


def test_compact_truncate_wrap():
    assert [compact(n) for n in (7, 999, 1000, 1234, 15_500, 2_000_000)] == ["7", "999", "1k", "1.2k", "15.5k", "2M"]
    assert truncate("abcdef", 4) == "abc…" and truncate("abc", 4) == "abc"
    lines = wrap("one two three four five six seven", 10, 2)
    assert len(lines) == 2 and lines[-1].endswith("…")


def test_grid_positions(data):
    cells = grid(data.weeks)
    assert len(cells) == 366
    assert (cells[0].col, cells[0].row) == (0, 0)
    assert (cells[-1].col, cells[-1].row) == (52, 1)


def test_link_buttons_for_known_and_unknown_keys():
    for key in ("github", "linkedin", "my blog"):
        assert ET.fromstring(link_button(key, P)).get("height") == "38"
    assert slug("My Blog!") == "my-blog"


def test_project_card_escapes_text():
    repo = Repo("a&b", "Uses <tags> & more", "https://x", 1500, 1, "Python", "#3572A5")
    svg = project_card(repo, P, prefix="~/")
    root = ET.fromstring(svg)
    assert (root.get("width"), root.get("height")) == (str(CARD_W), str(CARD_H))
    assert "~/a&amp;b" in svg and "1.5k" in svg and "1 fork" in svg


def test_readme_html(profile_raw, data):
    profile = parse_profile(profile_raw)
    links = links_html(profile, "assets/t/")
    assert 'href="https://github.com/Mahdi-Shafiei-IRAN"' in links
    assert 'src="assets/t/link-linkedin.svg"' in links
    cards = projects_html(data.featured, "../assets/t/")
    assert cards.count("<a href=") == 2 and 'src="../assets/t/project-2.svg"' in cards
    assert projects_html((), "x/") == ""
    assert page("a", "", "b") == "a\n\nb\n"
