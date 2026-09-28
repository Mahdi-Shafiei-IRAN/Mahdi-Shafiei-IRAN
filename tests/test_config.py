import pytest
import yaml

from generator.config import ConfigError, load_profile, parse_profile


def test_parses_full_profile(profile_raw):
    p = parse_profile(profile_raw)
    assert p.name == "Mahdi Shafiei"
    assert p.skills[:2] == ("Python", "Django")
    assert p.education.degree == "B.Sc. Computer Engineering"
    assert p.initials == "MS"
    assert p.first_name == "Mahdi"


def test_links_put_github_first_and_turn_email_into_mailto(profile_raw):
    links = parse_profile(profile_raw).all_links
    assert list(links) == ["github", "linkedin", "email"]
    assert links["github"] == "https://github.com/Mahdi-Shafiei-IRAN"
    assert links["email"] == "mailto:me@example.com"


def test_optional_fields_default_to_empty():
    p = parse_profile({"name": "Ada", "username": "ada", "role": "Engineer"})
    assert (p.tagline, p.skills, p.links, p.photo, p.education.university) == ("", (), {}, "", "")
    assert p.initials == "A"


@pytest.mark.parametrize("field", ["name", "username", "role"])
def test_missing_required_field_is_named(profile_raw, field):
    del profile_raw[field]
    with pytest.raises(ConfigError, match=f"'{field}' is required"):
        parse_profile(profile_raw)


def test_blank_required_field_is_rejected(profile_raw):
    profile_raw["role"] = "   "
    with pytest.raises(ConfigError, match="'role' must not be empty"):
        parse_profile(profile_raw)


def test_wrong_types_are_rejected(profile_raw):
    with pytest.raises(ConfigError, match="'skills' must be a list"):
        parse_profile({**profile_raw, "skills": "Python"})
    with pytest.raises(ConfigError, match="'education.degree' must be text"):
        parse_profile({**profile_raw, "education": {"degree": 5}})
    with pytest.raises(ConfigError, match="'links' must map"):
        parse_profile({**profile_raw, "links": ["https://x.com"]})


def test_load_profile_reads_utf8_yaml(tmp_path, profile_raw):
    path = tmp_path / "profile.yml"
    path.write_text(yaml.safe_dump(profile_raw, allow_unicode=True), encoding="utf-8")
    assert load_profile(path).role.startswith("Computer Engineering Student ·")


def test_load_profile_errors(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_profile(tmp_path / "missing.yml")
    bad = tmp_path / "bad.yml"
    bad.write_text("name: [unclosed", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid YAML"):
        load_profile(bad)
    top = tmp_path / "list.yml"
    top.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="must be a mapping"):
        load_profile(top)
