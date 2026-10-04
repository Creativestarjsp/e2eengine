"""Blueprints and templates must be reachable from a project that only points at a shared skill library."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from e2e import stories, templates
from e2e.cli import main
from e2e.project import (
    BLUEPRINTS_PATH_ENV,
    SKILLS_PATH_ENV,
    TEMPLATES_PATH_ENV,
    blueprint_paths,
    init,
    load_config,
    template_paths,
)

ROOT = Path(__file__).resolve().parents[1]
STORY_TEMPLATE = (ROOT / "templates" / "STORY.md").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for name in (SKILLS_PATH_ENV, BLUEPRINTS_PATH_ENV, TEMPLATES_PATH_ENV):
        monkeypatch.delenv(name, raising=False)


def library(root: Path) -> Path:
    """A shared library laid out like this repository: skills/, workflows/, templates/ side by side."""
    lib = root / "library"
    (lib / "skills" / "writer" / "templates").mkdir(parents=True)
    (lib / "skills" / "writer" / "SKILL.md").write_text("---\nname: writer\ndescription: \"w\"\nproduces: DOC.md\n---\n\n# Writer\n", encoding="utf-8")
    (lib / "skills" / "writer" / "templates" / "REGISTER.md").write_text("# Register\n", encoding="utf-8")
    (lib / "workflows").mkdir()
    (lib / "workflows" / "app.json").write_text(json.dumps({"inputs": [], "phases": [{"id": "a", "skills": ["writer"], "produces": ["DOC.md"]}]}), encoding="utf-8")
    (lib / "templates").mkdir()
    (lib / "templates" / "STORY.md").write_text(STORY_TEMPLATE, encoding="utf-8")
    (lib / "templates" / "DOC.md").write_text("# Doc\n", encoding="utf-8")
    return lib


# --- init and path resolution -----------------------------------------------


def test_default_init_records_default_locations_and_notes_what_is_missing(tmp_path: Path):
    report = init(tmp_path)
    config = load_config(tmp_path)
    assert config["blueprints_paths"] == ["workflows", ".e2e/workflows"]
    assert config["templates_paths"] == ["templates", ".e2e/templates"]
    assert report["blueprints_found"] == 0 and report["templates_found"] == 0
    assert len(report["notes"]) == 2 and "--blueprints-path" in report["notes"][0]


def test_pointing_at_shared_skills_also_finds_what_sits_beside_them(tmp_path: Path):
    lib = library(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    report = init(project, skills=[str(lib / "skills")])
    assert (report["skills_found"], report["blueprints_found"], report["templates_found"]) == (1, 1, 2)
    assert report["notes"] == []
    # The project's own folders come first so it can override the shared library.
    assert blueprint_paths(project) == [project / "workflows", project / ".e2e" / "workflows", lib / "workflows"]
    assert template_paths(project) == [project / "templates", project / ".e2e" / "templates", lib / "templates"]


def test_explicit_paths_and_environment_take_precedence(tmp_path: Path, monkeypatch):
    lib = library(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    init(project, skills=[str(lib / "skills")], blueprints=["my-flows"], templates=["my-templates"])
    assert blueprint_paths(project) == [project / "my-flows"]
    assert template_paths(project) == [project / "my-templates"]
    monkeypatch.setenv(TEMPLATES_PATH_ENV, str(lib / "templates"))
    assert template_paths(project) == [lib / "templates"]


def test_existing_config_without_the_new_keys_falls_back_to_defaults(tmp_path: Path):
    (tmp_path / "e2e.json").write_text('{"skills_paths": ["skills"]}\n', encoding="utf-8")
    assert blueprint_paths(tmp_path) == [tmp_path / "workflows", tmp_path / ".e2e" / "workflows"]
    assert template_paths(tmp_path) == [tmp_path / "templates", tmp_path / ".e2e" / "templates"]


# --- templates --------------------------------------------------------------


@pytest.fixture
def project(tmp_path: Path) -> Path:
    lib = library(tmp_path)
    root = tmp_path / "project"
    root.mkdir()
    init(root, skills=[str(lib / "skills")])
    return root


def test_templates_come_from_template_paths_and_from_skills(project: Path):
    found = {t["name"]: t["source"] for t in templates.list_templates(project)}
    assert found == {"DOC.md": "templates", "STORY.md": "templates", "REGISTER.md": "skill:writer"}


def test_project_local_template_overrides_the_shared_one(project: Path):
    local = project / "templates"
    local.mkdir()
    (local / "DOC.md").write_text("# Ours\n", encoding="utf-8")
    assert Path(templates.find(project, "doc")["path"]) == local / "DOC.md"


def test_find_by_name_or_stem_and_explain_misses(project: Path):
    assert templates.find(project, "STORY.md")["name"] == "STORY.md"
    assert templates.find(project, "register")["source"] == "skill:writer"
    with pytest.raises(ValueError, match="not found \\(available: DOC.md, REGISTER.md, STORY.md\\)"):
        templates.find(project, "RUNBOOK")
    (project / ".e2e" / "templates").mkdir(parents=True)
    (project / ".e2e" / "templates" / "DOC.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="ambiguous"):
        templates.find(project, "doc")


def test_copy_never_overwrites_and_never_leaves_the_project(project: Path):
    assert templates.copy(project, "DOC") == {"template": "DOC.md", "source": "templates", "written": "DOC.md"}
    (project / "DOC.md").write_text("# edited by a person\n", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        templates.copy(project, "DOC")
    assert (project / "DOC.md").read_text(encoding="utf-8") == "# edited by a person\n"

    assert templates.copy(project, "DOC", "docs/")["written"] == "docs/DOC.md"
    assert templates.copy(project, "DOC", "docs/design/spec.md")["written"] == "docs/design/spec.md"
    with pytest.raises(ValueError, match="outside the project"):
        templates.copy(project, "DOC", "../elsewhere.md")
    assert not (project.parent / "elsewhere.md").exists()


# --- story creation ---------------------------------------------------------


def test_new_story_gets_the_next_number_and_passes_the_check(project: Path):
    first = stories.new(project, "Sign in with email")
    assert first == {"id": "STORY-001", "title": "Sign in with email", "path": "stories/STORY-001-sign-in-with-email.md"}
    second = stories.new(project, "  Reset a forgotten   password!  ")
    assert second["id"] == "STORY-002" and second["path"] == "stories/STORY-002-reset-a-forgotten-password.md"
    assert stories.get(project, "STORY-002")["title"] == "Reset a forgotten password!"
    result = stories.check(project)
    assert result["status"] == "pass" and result["order"] == ["STORY-001", "STORY-002"]


def test_story_numbers_are_never_reused(project: Path):
    for title in ("One", "Two", "Three"):
        stories.new(project, title)
    (project / "stories" / "STORY-002-two.md").unlink()
    assert stories.new(project, "Four")["id"] == "STORY-004"


def test_new_story_needs_a_title_and_a_template(project: Path, tmp_path: Path):
    with pytest.raises(ValueError, match="needs a title"):
        stories.new(project, "   ")
    bare = tmp_path / "bare"
    bare.mkdir()
    with pytest.raises(ValueError, match="template STORY not found"):
        stories.new(bare, "Anything")


# --- CLI --------------------------------------------------------------------


def test_cli_init_template_and_story_commands(tmp_path: Path, monkeypatch, capsys):
    lib = library(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    assert main(["init", "--skills-path", str(lib / "skills")]) == 0
    assert json.loads(capsys.readouterr().out)["blueprints_found"] == 1
    assert main(["blueprint", "check"]) == 0
    capsys.readouterr()
    assert main(["template", "list"]) == 0
    assert [t["name"] for t in json.loads(capsys.readouterr().out)] == ["DOC.md", "REGISTER.md", "STORY.md"]
    assert main(["template", "copy", "DOC"]) == 0
    capsys.readouterr()
    assert main(["template", "copy", "DOC"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"
    assert main(["story", "new", "First feature"]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == "STORY-001"
    assert main(["story", "check"]) == 0
    capsys.readouterr()

    assert main(["init", "--force", "--skills-path", str(lib / "skills"), "--templates-path", "nowhere"]) == 0
    assert json.loads(capsys.readouterr().out)["templates_found"] == 0
    assert main(["story", "new", "Second"]) == 1


# --- this repository --------------------------------------------------------


def test_every_template_a_skill_tells_the_agent_to_copy_exists():
    cited: set[str] = set()
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        cited |= set(re.findall(r"e2e template copy ([A-Za-z][\w.-]*)", skill.read_text(encoding="utf-8")))
    assert {"PRD", "DEPLOYMENT", "RUNBOOK", "CREDENTIALS", "API-CONTRACT"} <= cited
    for name in cited:
        assert templates.find(ROOT, name)["name"], name


def test_authoring_standard_documents_contracts_and_routing():
    standard = (ROOT / "standards" / "SKILL-AUTHORING-STANDARD.md").read_text(encoding="utf-8")
    for needle in ("consumes:", "produces:", "Routing vocabulary", "Not a substitute for", "e2e blueprint check"):
        assert needle in standard, needle
    writer = (ROOT / "skills" / "sr-skills-developer" / "SKILL.md").read_text(encoding="utf-8")
    assert "## Registry Integration" in writer and "consumes" in writer
