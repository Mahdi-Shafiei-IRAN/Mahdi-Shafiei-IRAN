from datetime import date

import pytest

from conftest import make_payload
from generator.__main__ import main
from generator.build import BuildError, run
from generator.github_data import load_cache, parse_response
from generator.themes import ORDER, THEMES

DAY = date(2026, 9, 28)  # 270 days after the epoch -> 270 % 6 == 0 -> "terminal"


def test_offline_build_writes_readme_assets_and_previews(project_root):
    result = run(project_root, day=DAY, offline=True)
    assert (result.theme, result.failed, result.used_cache) == ("terminal", (), True)
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    assert 'src="assets/terminal/terminal.svg"' in readme
    assert readme.endswith("<!-- theme: terminal · generated 2026-09-28 -->\n")
    for name in ORDER:
        preview = (project_root / "previews" / f"{name}.md").read_text(encoding="utf-8")
        assert f'src="../assets/{name}/' in preview
        assert any((project_root / "assets" / name).glob("*.svg"))
    assert b"\r\n" not in (project_root / "README.md").read_bytes()


def test_theme_override_without_previews(project_root):
    result = run(project_root, day=DAY, theme="snake", offline=True, previews=False)
    assert result.theme == "snake"
    assert not (project_root / "previews").exists()
    assert not (project_root / "assets" / "terminal").exists()


def test_unknown_theme(project_root):
    with pytest.raises(BuildError, match="unknown theme"):
        run(project_root, day=DAY, theme="nope", offline=True)


def test_broken_theme_falls_back_to_the_next_one(project_root, monkeypatch):
    def broken(ctx):
        raise RuntimeError("boom")

    monkeypatch.setattr(THEMES["terminal"], "build", broken)
    result = run(project_root, day=DAY, offline=True)
    assert result.theme == "cinematic" and result.failed == ("terminal",)
    assert 'src="assets/cinematic/hero.svg"' in (project_root / "README.md").read_text(encoding="utf-8")


def test_all_themes_broken_leaves_everything_untouched(project_root, monkeypatch):
    (project_root / "README.md").write_text("old", encoding="utf-8")
    for module in THEMES.values():
        monkeypatch.setattr(module, "build", lambda ctx: 1 / 0)
    with pytest.raises(BuildError, match="every theme failed"):
        run(project_root, day=DAY, offline=True)
    assert (project_root / "README.md").read_text(encoding="utf-8") == "old"
    assert not (project_root / "assets").exists()


def test_stale_assets_are_removed(project_root):
    stale = project_root / "assets" / "terminal" / "project-9.svg"
    stale.parent.mkdir(parents=True)
    stale.write_text("<svg/>", encoding="utf-8")
    run(project_root, day=DAY, offline=True)
    assert not stale.exists()


def test_fresh_api_data_updates_the_cache(project_root):
    fresh = parse_response(make_payload(active=False))
    result = run(project_root, day=DAY, token="t", fetcher=lambda login, token: fresh)
    assert not result.used_cache
    assert load_cache(project_root / "data" / "github.json") == fresh


def test_cli_build_and_list(project_root, tmp_path, monkeypatch, capsys):
    output, summary = tmp_path / "github_output", tmp_path / "step_summary"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("PROFILE_TOKEN", raising=False)
    assert main(["build", "--offline", "--root", str(project_root), "--date", "2026-09-29"]) == 0
    assert output.read_text(encoding="utf-8") == "theme=cinematic\ndate=2026-09-29\n"
    report = summary.read_text(encoding="utf-8")
    assert "README theme: `cinematic` (2026-09-29)" in report and "cached stats" in report
    assert main(["list", "--date", "2026-09-28"]) == 0
    assert "-> terminal" in capsys.readouterr().out


def test_cli_returns_1_on_config_errors(tmp_path):
    assert main(["build", "--offline", "--root", str(tmp_path)]) == 1
