"""With a blueprint the plan follows the lifecycle; with a story SD3 gets the acceptance criteria."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from e2e import blueprints
from e2e.cli import main
from e2e.executor import execute
from e2e.orchestrator import MAX_ACTIVE_WORKERS, plan
from e2e.project import SKILLS_PATH_ENV

from test_blueprints import project, story


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv(SKILLS_PATH_ENV, raising=False)
    monkeypatch.delenv(blueprints.BLUEPRINTS_PATH_ENV, raising=False)


def at_build_phase(root: Path, status: str = "todo") -> None:
    project(root)
    story(root, status)
    for name in ("PRD.md", "ARCHITECTURE.md", "DATA-MODEL.md", "API-CONTRACT.md"):
        (root / name).write_text("# x\n", encoding="utf-8")


def test_default_plan_is_unchanged_in_shape(tmp_path: Path):
    project(tmp_path)
    result = plan(tmp_path, "build api work")
    assert result["blockers"] == []
    assert "blueprint" not in result and "story" not in result
    assert "acceptance_criteria" not in result["supervisor_gate"]
    assert all(w["status"] == "ready" for w in result["workers"])


def test_blueprint_chooses_the_phase_and_contracts_order_the_workers(tmp_path: Path):
    project(tmp_path)
    story(tmp_path, "todo")
    for name in ("PRD.md", "ARCHITECTURE.md"):
        (tmp_path / name).write_text("# x\n", encoding="utf-8")
    result = plan(tmp_path, "anything at all", blueprint="app")
    assert result["blueprint"]["current_phase"] == "contracts"
    assert result["blueprint"]["exit_artifacts"] == ["DATA-MODEL.md", "API-CONTRACT.md"]
    workers = {w["skill"]: w for w in result["workers"]}
    assert set(workers) == {"api", "modeller"}
    assert all(w["phase"] == "contracts" for w in workers.values())
    assert workers["api"]["depends_on"] == [workers["modeller"]["id"]]
    assert workers["modeller"]["depends_on"] == []
    assert workers["api"]["produces"] == ["API-CONTRACT.md"]


def test_missing_input_blocks_the_plan(tmp_path: Path):
    project(tmp_path)
    result = plan(tmp_path, "start", blueprint="app")
    assert result["workers"] == []
    assert result["blockers"] == ["blueprint input PRD.md is missing"]


def test_story_reaches_workers_and_supervisor(tmp_path: Path):
    at_build_phase(tmp_path)
    result = plan(tmp_path, "build x", blueprint="app", story="STORY-001")
    assert result["blockers"] == []
    assert [w["skill"] for w in result["workers"]] == ["web", "tester"]  # story is web-only
    assert result["blueprint"]["skipped_for_platform"] == ["mobile"]
    assert all("acceptance-evidence" in w["outputs"] and w["inputs"]["story"] == "STORY-001" for w in result["workers"])
    gate = result["supervisor_gate"]
    assert "acceptance-traceability" in gate["checks"]
    assert gate["acceptance_criteria"] == [{"id": "AC1", "text": "x"}]
    assert "AC1: x" in result["story"]["brief"]
    assert len(result["workers"]) <= MAX_ACTIVE_WORKERS


def test_story_cannot_jump_ahead_of_the_blueprint(tmp_path: Path):
    project(tmp_path)
    story(tmp_path, "todo")
    (tmp_path / "PRD.md").write_text("# x\n", encoding="utf-8")
    result = plan(tmp_path, "build x", blueprint="app", story="STORY-001")
    assert result["blockers"] == ["STORY-001 cannot start: blueprint phase `architecture` must finish first"]
    assert all(w["status"] == "blocked" for w in result["workers"])


def test_done_and_unknown_stories(tmp_path: Path):
    at_build_phase(tmp_path, status="done")
    assert "STORY-001 is already done" in plan(tmp_path, "x", story="STORY-001")["blockers"]
    with pytest.raises(ValueError, match="STORY-404 not found"):
        plan(tmp_path, "x", story="STORY-404")
    with pytest.raises(ValueError, match="blueprint nope not found"):
        plan(tmp_path, "x", blueprint="nope")


def test_completed_blueprint_has_nothing_to_run(tmp_path: Path):
    at_build_phase(tmp_path, status="done")
    result = plan(tmp_path, "more", blueprint="app")
    assert result["workers"] == [] and "is complete" in result["blockers"][0]


def test_owner_approval_is_flagged_never_granted(tmp_path: Path):
    project(tmp_path)
    blueprints_dir = tmp_path / "workflows"
    (blueprints_dir / "ship.json").write_text(json.dumps({"inputs": [], "phases": [
        {"id": "release", "skills": ["architect"], "produces": ["ARCHITECTURE.md"], "approval": "owner"}]}), encoding="utf-8")
    (tmp_path / "PRD.md").write_text("# x\n", encoding="utf-8")
    gate = plan(tmp_path, "ship", blueprint="ship")["supervisor_gate"]
    assert gate["owner_approval_required"] is True and gate["decision"] == "pending-runtime-agent-review"


def test_execute_reports_blocked_and_launches_nothing(tmp_path: Path):
    project(tmp_path)
    result = execute(tmp_path, "start", runtime="claude-code", execute_agents=False, blueprint="app")
    assert result["status"] == "blocked"
    assert result["blockers"] == ["blueprint input PRD.md is missing"]
    assert result["workers"] == []


def test_execute_dry_run_plans_a_story(tmp_path: Path):
    at_build_phase(tmp_path)
    result = execute(tmp_path, "build x", runtime="claude-code", execute_agents=False, blueprint="app", story="STORY-001")
    assert result["status"] == "planned"
    assert [w["skill"] for w in result["workers"]] == ["web", "tester"]
    assert result["story"]["id"] == "STORY-001" and result["blueprint"]["current_phase"] == "build"


def test_cli_commands_and_exit_codes(tmp_path: Path, monkeypatch, capsys):
    at_build_phase(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["story", "check"]) == 0
    assert json.loads(capsys.readouterr().out)["count"] == 1
    assert main(["story", "next"]) == 0
    assert [s["id"] for s in json.loads(capsys.readouterr().out)] == ["STORY-001"]
    assert main(["blueprint", "check"]) == 0
    capsys.readouterr()
    assert main(["blueprint", "list"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["phases"] == ["define", "architecture", "contracts", "build"]
    assert main(["blueprint", "status", "app"]) == 0
    assert json.loads(capsys.readouterr().out)["current_phase"] == "build"

    assert main(["blueprint", "status", "nope"]) == 1
    capsys.readouterr()
    assert main(["orchestrate", "x", "--story", "STORY-404"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"
    assert main(["orchestrate", "build x", "--blueprint", "app", "--story", "STORY-001"]) == 0
    assert json.loads(capsys.readouterr().out)["story"]["id"] == "STORY-001"

    (tmp_path / "stories" / "STORY-001-x.md").write_text("# STORY-001: X\n\nStatus: done\n\n## Acceptance Criteria\n\n- AC1: x\n", encoding="utf-8")
    assert main(["story", "check"]) == 1
