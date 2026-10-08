"""Illustration assets are executable content and visual work: check both the safety rules and the review tooling."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from e2e import blueprints
from e2e.skills import discover, match

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "vector-illustration"


def load(skill: str, script: str):
    spec = importlib.util.spec_from_file_location(script, ROOT / "skills" / skill / "scripts" / f"{script}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


svg_check = load("vector-illustration", "svg_check")
preview = load("vector-illustration", "render_preview")
capture = load("ux-laws", "capture_screens")

GOOD = '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg" fill="none"><g id="a"><circle cx="400" cy="300" r="120" fill="#6366F1"/></g></svg>'


def svg(tmp_path: Path, text: str, name: str = "art.svg") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def body(inner: str, root_attrs: str = 'viewBox="0 0 800 600"') -> str:
    return f'<svg {root_attrs} xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">{inner}</svg>'


# --- svg_check --------------------------------------------------------------


def test_minimal_and_shipped_artwork_pass(tmp_path: Path):
    assert svg_check.check(svg(tmp_path, GOOD))[:2] == ([], [])
    errors, warnings, info = svg_check.check(SKILL / "examples" / "EmptyProjectsIllustration.svg")
    assert errors == [] and warnings == []
    assert info["nodes"] < 60 and info["colors"] <= 8


@pytest.mark.parametrize(
    "inner, expected",
    [
        ("<script>alert(1)</script>", "<script> is not allowed"),
        ('<circle r="5" onclick="x()"/>', "event-handler attribute `onclick`"),
        ('<foreignObject width="10" height="10"/>', "<foreignObject> is not allowed"),
        ('<image href="photo.png" width="10" height="10"/>', "embedded raster image"),
        ('<image href="data:image/png;base64,AAAA" width="10" height="10"/>', "embedded raster image"),
        ('<use href="https://cdn.example.com/sprite.svg#a"/>', "references an external resource"),
        ('<a xlink:href="javascript:alert(1)"><circle r="5"/></a>', "references an external resource"),
        ('<style>@import url("https://cdn.example.com/a.css");</style>', "<style> loads a remote resource"),
        ('<rect width="5" height="5" style="fill:url(https://cdn.example.com/p.svg#g)"/>', "loads a remote resource"),
    ],
)
def test_executable_and_remote_content_is_rejected(tmp_path: Path, inner: str, expected: str):
    errors, _, _ = svg_check.check(svg(tmp_path, body(inner)))
    assert any(expected in e for e in errors), errors


def test_internal_references_are_allowed(tmp_path: Path):
    inner = '<defs><linearGradient id="g"><stop offset="0" stop-color="#6366F1"/></linearGradient><circle id="dot" r="5"/></defs><rect width="10" height="10" fill="url(#g)"/><use href="#dot"/>'
    assert svg_check.check(svg(tmp_path, body(inner)))[:2] == ([], [])


def test_structure_problems(tmp_path: Path):
    assert "not well-formed XML" in svg_check.check(svg(tmp_path, "<svg><g></svg>"))[0][0]
    assert svg_check.check(svg(tmp_path, "<html></html>"))[0] == ["root element is <html>, not <svg>"]
    assert svg_check.check(svg(tmp_path, '<!DOCTYPE svg [<!ENTITY a "b">]><svg/>'))[0] == ["DOCTYPE or entity declarations are not allowed"]
    assert any("viewBox" in e for e in svg_check.check(svg(tmp_path, body("", 'width="10"')))[0])
    assert any("viewBox" in e for e in svg_check.check(svg(tmp_path, body("", 'viewBox="0 0 0 600"')))[0])
    assert any("missing xmlns" in e for e in svg_check.check(svg(tmp_path, '<svg viewBox="0 0 8 6"/>'))[0])
    assert svg_check.check(tmp_path / "absent.svg")[0][0].startswith("cannot read file")


def test_budgets(tmp_path: Path):
    many = body("".join('<circle r="1"/>' for _ in range(50)))
    assert any("exceeds the budget of 20" in e for e in svg_check.check(svg(tmp_path, many), max_nodes=20)[0])
    assert any("bytes exceeds the budget" in e for e in svg_check.check(svg(tmp_path, many), max_bytes=100)[0])
    assert svg_check.check(svg(tmp_path, many))[0] == []


def test_warnings_for_rules_that_need_judgement(tmp_path: Path):
    inner = (
        '<rect width="800" height="600" fill="#FFFFFF"/><text x="1" y="1">Hi</text>'
        '<defs><clipPath id="unused"><rect width="1" height="1"/></clipPath></defs>'
        '<circle r="5" display="none"/>'
        + "".join(f'<rect width="1" height="1" fill="#{i:02d}{i:02d}{i:02d}"/>' for i in range(10, 20))
    )
    errors, warnings, _ = svg_check.check(svg(tmp_path, body(inner, 'viewBox="0 0 800 600" width="800" height="600"')))
    joined = " | ".join(warnings)
    assert errors == []
    for expected in ("text inside the artwork", "fixed width", "opaque full-canvas background", "`unused` is never referenced", "hidden <circle>", "distinct colours"):
        assert expected in joined, expected


def test_cli_exit_codes_and_strict(tmp_path: Path, capsys):
    good = svg(tmp_path, GOOD, "good.svg")
    warned = svg(tmp_path, body('<text x="1" y="1">Hi</text>'), "warned.svg")
    bad = svg(tmp_path, body("<script/>"), "bad.svg")
    assert svg_check.main([str(good), str(warned)]) == 0
    assert svg_check.main([str(warned), "--strict"]) == 1
    assert svg_check.main([str(good), str(bad), "--json"]) == 1
    out = capsys.readouterr().out
    assert json.loads(out[out.rindex('{\n  "ok"'):])["files"][1]["ok"] is False


# --- render_preview ---------------------------------------------------------


def test_preview_page_shows_every_size_on_both_themes_without_scripts(tmp_path: Path):
    art = svg(tmp_path, GOOD)
    page = preview.write_html(art, tmp_path, [120, 480]).read_text(encoding="utf-8")
    assert page.count("<img ") == 4 and page.count('width="120"') == 2 and page.count('width="480"') == 2
    assert "light" in page and "dark" in page
    assert "<script" not in page.lower()
    assert preview.aspect_ratio(art) == 0.75


def test_preview_reports_honestly_when_nothing_can_render(tmp_path: Path, monkeypatch, capsys):
    art = svg(tmp_path, GOOD)
    monkeypatch.setattr(preview, "find_chrome", lambda: None)
    monkeypatch.setattr(preview, "rasterise", lambda *a, **k: None)
    assert preview.main([str(art), "--out", str(tmp_path / "p")]) == 2
    out = capsys.readouterr().out
    assert "NO RENDERER" in out and "has not been visually reviewed" in out
    assert (tmp_path / "p" / "preview.html").is_file()


def test_preview_uses_a_browser_when_one_exists(tmp_path: Path, monkeypatch, capsys):
    art = svg(tmp_path, GOOD)
    commands: list[list[str]] = []

    def fake_run(command, timeout=60):
        commands.append(command)
        Path(next(a for a in command if a.startswith("--screenshot=")).split("=", 1)[1]).write_bytes(b"png")
        return True

    monkeypatch.setattr(preview, "find_chrome", lambda: "/fake/chrome")
    monkeypatch.setattr(preview, "_run", fake_run)
    assert preview.main([str(art), "--out", str(tmp_path / "p"), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["renderer"] == "chrome" and result["reviewed"] is False
    assert commands[0][0] == "/fake/chrome" and "--headless" in commands[0]


def test_preview_rejects_bad_input(tmp_path: Path, capsys):
    assert preview.main([str(tmp_path / "absent.svg")]) == 1
    assert preview.main([str(svg(tmp_path, GOOD)), "--sizes", "0,abc"]) == 1
    capsys.readouterr()


# --- capture_screens --------------------------------------------------------


def test_capture_plan_covers_every_path_at_every_viewport(tmp_path: Path):
    shots = capture.plan("http://localhost:3000", ["/", "/projects/new"], capture.parse_viewports(capture.DEFAULT_VIEWPORTS), tmp_path)
    assert [(s["path"], s["viewport"], s["width"]) for s in shots] == [("/", "phone", 390), ("/", "desktop", 1440), ("/projects/new", "phone", 390), ("/projects/new", "desktop", 1440)]
    assert shots[0]["url"] == "http://localhost:3000/" and shots[2]["url"] == "http://localhost:3000/projects/new"
    assert Path(shots[0]["file"]).name == "home-phone.png" and Path(shots[3]["file"]).name == "projects-new-desktop.png"


def test_narrow_viewports_are_framed_at_their_exact_width(tmp_path: Path):
    phone, desktop = capture.plan("http://localhost:3000", ["/a"], capture.parse_viewports("phone=390x844,desktop=1440x900"), tmp_path)
    narrow = capture.command("/fake/chrome", phone)
    assert f"--window-size={capture.MIN_WINDOW_WIDTH},844" in narrow and narrow[-1].startswith("file://") and phone["framed"]
    frame = (tmp_path / "_frames" / "a-phone.html").read_text(encoding="utf-8")
    assert 'width="390"' in frame and 'height="844"' in frame and "http://localhost:3000/a" in frame and "<script" not in frame

    wide = capture.command("/fake/chrome", desktop)
    assert "--window-size=1440,900" in wide and wide[-1] == "http://localhost:3000/a" and not desktop["framed"]


def test_capture_rejects_bad_input_and_reports_a_missing_browser(tmp_path: Path, monkeypatch, capsys):
    assert capture.main(["--url", "file:///etc/passwd"]) == 1
    assert capture.main(["--url", "http://localhost:3000", "--viewports", "huge"]) == 1
    monkeypatch.setattr(capture, "find_chrome", lambda: None)
    assert capture.main(["--url", "http://localhost:3000", "--out", str(tmp_path)]) == 2
    assert "screens were not looked at" in capsys.readouterr().out


# --- skill, references, lifecycle -------------------------------------------


def test_skill_is_registered_and_its_files_exist():
    skill = next(s for s in discover(ROOT) if s["name"] == "vector-illustration")
    assert skill["has_frontmatter"]
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for rel in set(re.findall(r"`((?:references|examples)/[\w./-]+\.\w+)`", text)):
        assert (SKILL / rel).is_file(), rel
    for rel in set(re.findall(r"python (skills/[\w./-]+\.py)", text)):
        assert (ROOT / rel).is_file(), rel


def test_undraw_is_a_human_step_and_no_library_assets_are_bundled():
    fallback = (SKILL / "references" / "undraw-fallback.md").read_text(encoding="utf-8")
    for needle in ("A person chooses and downloads", "crawl, scrape, search, or fetch", "https://undraw.co/license", "train"):
        assert needle in fallback, needle
    assert "Do not crawl, search, scrape, hotlink, or bulk-download" in (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert [p.name for p in (SKILL / "examples").glob("*.svg")] == ["EmptyProjectsIllustration.svg"]


def test_react_example_is_themable_and_accessible():
    component = (SKILL / "examples" / "EmptyProjectsIllustration.tsx").read_text(encoding="utf-8")
    for needle in ("primaryColor", "secondaryColor", "className", "width", "height", 'role: "img"', '"aria-hidden": true', 'viewBox="0 0 800 600"'):
        assert needle in component, needle


@pytest.mark.parametrize(
    "task",
    [
        "create an empty state illustration for the projects list",
        "draw a hero illustration in SVG for the landing page",
        "should this spot use an icon or an illustration",
    ],
)
def test_routes_on_illustration_work(task: str):
    assert match(ROOT, task)[0]["name"] == "vector-illustration", [s["name"] for s in match(ROOT, task)[:3]]


def test_does_not_appear_in_unrelated_work():
    for task in ("build a login API endpoint", "design the database schema for orders", "deploy the app to production", "break the PRD into user stories"):
        assert "vector-illustration" not in [s["name"] for s in match(ROOT, task)[:3]], task


def test_designer_has_patterns_and_harden_phase_reviews_the_built_screens():
    patterns = (ROOT / "skills" / "ui-ux-designer" / "references" / "screen-patterns.md").read_text(encoding="utf-8")
    for heading in ("## Navigation shell", "## Sign in and sign up", "## List and detail", "## Forms (create and edit)", "## Checkout and payment", "## States every screen has"):
        assert heading in patterns, heading
    assert "references/screen-patterns.md" in (ROOT / "skills" / "ui-ux-designer" / "SKILL.md").read_text(encoding="utf-8")

    for name in ("full-stack-app", "web-app", "mobile-app"):
        harden = blueprints.select_workers(ROOT, name, "harden")
        assert "ux-laws" in [s["name"] for s in harden["skills"]] and len(harden["skills"]) <= 4
        assert "UX-REVIEW.md" in harden["phase"]["produces"]
    assert (ROOT / "templates" / "UX-REVIEW.md").is_file()
