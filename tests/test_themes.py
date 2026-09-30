import re
import xml.etree.ElementTree as ET

import pytest

from generator.themes import ORDER, THEMES

EXTERNAL = re.compile(r'\b(?:href|src)="(?!data:|#)')


@pytest.mark.parametrize("name", ORDER)
@pytest.mark.parametrize("which", ["ctx", "bare_ctx"])
def test_theme_builds_valid_self_contained_svgs(name, which, request):
    ctx = request.getfixturevalue(which)
    out = THEMES[name].build(ctx)
    assert out.assets
    for file, svg in out.assets.items():
        assert file.endswith(".svg")
        ET.fromstring(svg)  # well-formed XML
        assert "<script" not in svg
        assert not EXTERNAL.search(svg), f"{file} loads an external resource"
        assert len(svg.encode("utf-8")) < 1_000_000
    readme = out.readme("assets/x/")
    referenced = set(re.findall(r'src="assets/x/([^"]+)"', readme))
    assert referenced and referenced <= set(out.assets)
    assert f'href="https://github.com/{ctx.profile.username}"' in readme


@pytest.mark.parametrize("name", ORDER)
def test_theme_shows_the_profile(name, ctx):
    out = THEMES[name].build(ctx)
    readme = out.readme("")
    assert "Mahdi Shafiei" in "".join(out.assets.values()) + readme
    assert "https://linkedin.com/in/mahdi-shafiei-iran" in readme
    assert "Contribution" not in "".join(out.assets)  # no contribution-activity section


@pytest.mark.parametrize("name", ORDER)
def test_theme_output_is_deterministic(name, ctx):
    assert THEMES[name].build(ctx).assets == THEMES[name].build(ctx).assets


# --- rotation order (added together with the last theme) ---------------------


def test_rotation_order_matches_the_spec():
    assert ORDER == ("oss-builder",)


def test_light_mode_viewers_get_the_cap_tip_look(ctx):
    out = THEMES["oss-builder"].build(ctx)
    readme = out.readme("assets/x/")
    assert readme.count('<source media="(prefers-color-scheme: dark)"') == 4
    assert 'srcset="assets/x/hero.svg"' in readme and 'src="assets/x/light-portrait.svg"' in readme
    hero = out.assets["hero.svg"]
    assert all(skill in hero for skill in ctx.profile.skills[:6])


def test_website_gets_a_visit_card_and_a_clickable_header(ctx):
    from dataclasses import replace

    profile = replace(ctx.profile, links={"website": "https://example.dev", **ctx.profile.links})
    out = THEMES["oss-builder"].build(replace(ctx, profile=profile))
    readme = out.readme("assets/x/")
    assert "example.dev" in out.assets["visit.svg"] and "example.dev" in out.assets["light-visit.svg"]
    assert readme.count('<a href="https://example.dev"><picture>') == 2  # header + visit card
    assert "example.dev" in out.assets["scan.svg"]  # contact row
