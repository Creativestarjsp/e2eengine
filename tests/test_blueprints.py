"""Blueprints must stay in step with the skill contracts they sequence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from e2e import blueprints
from e2e.project import SKILLS_PATH_ENV
from e2e.skills import discover

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv(SKILLS_PATH_ENV, raising=False)
    monkeypatch.delenv(blueprints.BLUEPRINTS_PATH_ENV, raising=False)


def write_skill(root: Path, name: str, consumes: str = "", produces: str = "") -> None:
    folder = root / "skills" / name
    folder.mkdir(parents=True, exist_ok=True)
    front = f"---\nname: {name}\ndescription: \"{name} work\"\n"
    front += f"consumes: {consumes}\n" if consumes else ""
    front += f"produces: {produces}\n" if produces else ""
    (folder / "SKILL.md").write_text(front + f"---\n\n# {name}\n\n## Purpose\nDo {name} work.\n", encoding="utf-8")


def write_blueprint(root: Path, phases: list[dict], name: str = "app", inputs: list[str] | None = None) -> None:
    folder = root / "workflows"
    folder.mkdir(exist_ok=True)
    data = {"name": name, "inputs": ["PRD.md"] if inputs is None else inputs, "phases": phases}
    (folder / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")


def project(root: Path) -> None:
    write_skill(root, "planner", consumes="PRD.md", produces="stories/")
    write_skill(root, "architect", consumes="PRD.md", produces="ARCHITECTURE.md")
    write_skill(root, "modeller", consumes="ARCHITECTURE.md", produces="DATA-MODEL.md")
    write_skill(root, "api", consumes="ARCHITECTURE.md, DATA-MODEL.md", produces="API-CONTRACT.md")
    write_skill(root, "web", consumes="API-CONTRACT.md, stories/")
    write_skill(root, "mobile", consumes="API-CONTRACT.md, stories/")
    write_skill(root, "tester", consumes="stories/")
    write_blueprint(root, [
        {"id": "define", "skills": ["planner"], "produces": ["stories/"]},
        {"id": "architecture", "skills": ["architect"], "produces": ["ARCHITECTURE.md"]},
        {"id": "contracts", "depends_on": ["define", "architecture"], "skills": ["api", "modeller"], "produces": ["DATA-MODEL.md", "API-CONTRACT.md"]},
        {"id": "build", "depends_on": ["contracts"], "requires_stories_done": True,
         "skills": [{"skill": "web", "platforms": ["web"]}, {"skill": "mobile", "platforms": ["mobile"]}, "tester"]},
    ])


def story(root: Path, status: str) -> None:
    (root / "stories").mkdir(exist_ok=True)
    evidence = "t (pass)" if status == "done" else ""
    (root / "stories" / "STORY-001-x.md").write_text(
        f"# STORY-001: X\n\nStatus: {status}\nPlatforms: web\n\nAs a user, I want x.\n\n## Acceptance Criteria\n\n- AC1: x\n\n## Evidence\n\n- AC1: {evidence}\n",
        encoding="utf-8",
    )


def test_registry_exposes_contracts(tmp_path: Path):
    project(tmp_path)
    api = next(s for s in discover(tmp_path) if s["name"] == "api")
    assert api["consumes"] == ["ARCHITECTURE.md", "DATA-MODEL.md"]
    assert api["produces"] == ["API-CONTRACT.md"]
    assert next(s for s in discover(tmp_path) if s["name"] == "tester")["produces"] == []


def test_repository_blueprints_match_the_skill_contracts():
    result = blueprints.check(ROOT)
    assert result["status"] == "pass", result["errors"]
    assert {"full-stack-app", "web-app", "mobile-app"} <= set(result["blueprints"])


def test_valid_blueprint_passes(tmp_path: Path):
    project(tmp_path)
    assert blueprints.check(tmp_path) == {
        "status": "pass", "blueprints": ["app"], "errors": [],
        "searched": [p.as_posix() for p in blueprints.blueprint_paths(tmp_path)],
    }


@pytest.mark.parametrize(
    "phases, expected",
    [
        ([{"id": "a", "skills": ["ghost"], "produces": ["X.md"]}], "skill `ghost` is not in the registry"),
        ([{"id": "a", "skills": ["architect"], "produces": ["ARCHITECTURE.md"], "depends_on": ["later"]}], "depends_on `later` is not an earlier phase"),
        ([{"id": "a", "skills": ["architect"], "produces": ["OTHER.md"]}], "no skill in this phase declares `produces: OTHER.md`"),
        ([{"id": "a", "skills": ["api"], "produces": ["API-CONTRACT.md"]}], "`api` consumes ARCHITECTURE.md, which no input or earlier phase provides"),
        ([{"id": "a", "skills": ["tester"]}], "no exit condition"),
        ([{"id": "a", "skills": ["architect"], "produces": ["ARCHITECTURE.md"], "approval": "anyone"}], "approval `anyone`"),
        ([{"id": "a", "skills": [], "produces": ["X.md"]}], "no skills"),
        ([{"id": "a", "skills": ["architect"], "produces": ["ARCHITECTURE.md"]}, {"id": "a", "skills": ["architect"], "produces": ["ARCHITECTURE.md"]}], "duplicate phase id"),
    ],
)
def test_invalid_blueprints_are_rejected(tmp_path: Path, phases, expected):
    project(tmp_path)
    write_blueprint(tmp_path, phases)
    result = blueprints.check(tmp_path)
    assert result["status"] == "fail"
    assert any(expected in e for e in result["errors"]), result["errors"]


def test_contract_cycle_inside_a_phase_is_rejected(tmp_path: Path):
    write_skill(tmp_path, "left", consumes="R.md", produces="L.md")
    write_skill(tmp_path, "right", consumes="L.md", produces="R.md")
    write_blueprint(tmp_path, [{"id": "a", "skills": ["left", "right"], "produces": ["L.md", "R.md"]}], inputs=[])
    assert any("contract cycle between left, right" in e for e in blueprints.check(tmp_path)["errors"])


def test_unreadable_and_missing_blueprints_are_reported(tmp_path: Path):
    assert "no blueprints found" in blueprints.check(tmp_path)["errors"][0]
    (tmp_path / "workflows").mkdir()
    (tmp_path / "workflows" / "bad.json").write_text("{not json", encoding="utf-8")
    assert "bad: unreadable" in blueprints.check(tmp_path)["errors"][0]
    with pytest.raises(ValueError, match="not found"):
        blueprints.load(tmp_path, "missing")


def test_status_advances_only_when_exit_artifacts_exist(tmp_path: Path):
    project(tmp_path)
    first = blueprints.status(tmp_path, "app")
    assert first["state"] == "blocked" and first["missing_inputs"] == ["PRD.md"] and first["current_phase"] is None

    (tmp_path / "PRD.md").write_text("# PRD\n", encoding="utf-8")
    second = blueprints.status(tmp_path, "app")
    assert second["current_phase"] == "define" and second["ready_phases"] == ["define", "architecture"]
    assert next(p for p in second["phases"] if p["id"] == "contracts")["waiting_on"] == ["define", "architecture"]

    (tmp_path / "stories").mkdir()  # an empty directory is not an artifact
    assert blueprints.status(tmp_path, "app")["current_phase"] == "define"
    (tmp_path / "ARCHITECTURE.md").write_text("", encoding="utf-8")  # nor is an empty file
    assert "architecture" in blueprints.status(tmp_path, "app")["ready_phases"]

    story(tmp_path, "todo")
    (tmp_path / "ARCHITECTURE.md").write_text("# A\n", encoding="utf-8")
    assert blueprints.status(tmp_path, "app")["current_phase"] == "contracts"

    for name in ("DATA-MODEL.md", "API-CONTRACT.md"):
        (tmp_path / name).write_text("# x\n", encoding="utf-8")
    build = blueprints.status(tmp_path, "app")
    assert build["current_phase"] == "build"
    assert next(p for p in build["phases"] if p["id"] == "build")["stories_pending"] == ["STORY-001"]

    story(tmp_path, "done")
    done = blueprints.status(tmp_path, "app")
    assert done["state"] == "complete" and done["current_phase"] is None


def test_workers_are_ordered_by_contract_and_filtered_by_platform(tmp_path: Path):
    project(tmp_path)
    contracts = blueprints.select_workers(tmp_path, "app", "contracts")
    assert [s["name"] for s in contracts["skills"]] == ["api", "modeller"]
    assert contracts["depends_on"] == {"api": ["modeller"], "modeller": []}

    web_only = blueprints.select_workers(tmp_path, "app", "build", platforms=["web"])
    assert [s["name"] for s in web_only["skills"]] == ["web", "tester"]
    assert web_only["skipped_for_platform"] == ["mobile"]

    everything = blueprints.select_workers(tmp_path, "app", "build")
    assert [s["name"] for s in everything["skills"]] == ["web", "mobile", "tester"]

    capped = blueprints.select_workers(tmp_path, "app", "build", limit=2)
    assert [s["name"] for s in capped["skills"]] == ["web", "mobile"] and capped["deferred"] == ["tester"]

    with pytest.raises(ValueError, match="no phase nope"):
        blueprints.select_workers(tmp_path, "app", "nope")


def test_blueprint_path_can_be_overridden(tmp_path: Path, monkeypatch):
    project(tmp_path)
    other = tmp_path / "elsewhere"
    other.mkdir()
    (other / "solo.json").write_text(json.dumps({"inputs": [], "phases": [{"id": "a", "skills": ["architect"], "produces": ["ARCHITECTURE.md"]}]}), encoding="utf-8")
    monkeypatch.setenv(blueprints.BLUEPRINTS_PATH_ENV, str(other))
    assert [b["name"] for b in blueprints.list_blueprints(tmp_path)] == ["solo"]


def test_every_produced_artifact_has_a_template():
    """A contract that names a document nobody can start from is a broken promise."""
    templates = {p.name for p in (ROOT / "templates").glob("*.md")}
    templates |= {p.name for p in (ROOT / "skills").glob("*/templates/*.md")}
    produced = {a for s in discover(ROOT) for a in s["produces"]}
    assert produced, "expected lifecycle skills to declare contracts"
    for artifact in produced:
        if artifact.endswith("/"):
            assert artifact == "stories/" and "STORY.md" in templates
        else:
            assert artifact in templates, artifact


def test_story_writer_routes_on_story_work_only():
    from e2e.skills import match

    for task in ("break the PRD into user stories with acceptance criteria", "split this feature into stories"):
        assert match(ROOT, task)[0]["name"] == "story-writer", task
    for task in ("fix the flaky checkout test", "write unit tests for the cart", "build a login API endpoint"):
        assert "story-writer" not in [s["name"] for s in match(ROOT, task)], task
