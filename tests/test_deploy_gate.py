"""Deploy capabilities must be refused until the gate has passed for the exact tree being deployed."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from e2e import deploy
from e2e.cli import main
from e2e.project import SKILLS_PATH_ENV
from e2e.tools import check_registry, decide, load_tools, policy_for_role

ROOT = Path(__file__).resolve().parents[1]
STORY = "# STORY-001: X\n\nStatus: {status}\nPlatforms: web\n\nAs a user, I want x.\n\n## Acceptance Criteria\n\n- AC1: x\n\n## Evidence\n\n- AC1: {evidence}\n"
REGISTER = (
    "# Credentials\n\n## Register\n\n"
    "| Variable | Service | Purpose | Environments | Source | Storage | Owner | Rotation | Status |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    "| DATABASE_URL | Postgres | db | all | team | GH secret | platform | 90d | active |\n"
)


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", *args], cwd=root, check=True, capture_output=True)


def commit(root: Path, message: str = "change") -> None:
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv(SKILLS_PATH_ENV, str(ROOT / "skills"))
    (tmp_path / "runtime").mkdir()
    shutil.copy(ROOT / "runtime" / "tools.json", tmp_path / "runtime" / "tools.json")
    (tmp_path / ".gitignore").write_text(".e2e/\n.env\n", encoding="utf-8")
    (tmp_path / "vercel.json").write_text("{}", encoding="utf-8")
    (tmp_path / "stories").mkdir()
    (tmp_path / "stories" / "STORY-001-x.md").write_text(STORY.format(status="todo", evidence=""), encoding="utf-8")
    git(tmp_path, "init", "-q")
    commit(tmp_path, "init")
    return tmp_path


def make_releasable(root: Path) -> None:
    (root / "stories" / "STORY-001-x.md").write_text(STORY.format(status="done", evidence="tests/x (pass)"), encoding="utf-8")
    shutil.copy(ROOT / "skills" / "app-deployment" / "examples" / "DEPLOYMENT.example.md", root / "DEPLOYMENT.md")
    checklist = (ROOT / "templates" / "RELEASE-CHECKLIST.md").read_text(encoding="utf-8")
    checklist = checklist.replace("- Release owner:", "- Release owner: A. Owner").replace("- Approved on:", "- Approved on: 2026-10-07")
    (root / "RELEASE-CHECKLIST.md").write_text(checklist, encoding="utf-8")
    (root / "CREDENTIALS.md").write_text(REGISTER, encoding="utf-8")
    (root / "app.js").write_text("const u = process.env.DATABASE_URL;\n", encoding="utf-8")
    commit(root, "release ready")


def statuses(result: dict) -> dict[str, str]:
    return {c["check"]: c["status"] for c in result["checks"]}


# --- registry ---------------------------------------------------------------


def test_deploy_tools_are_registered_with_the_right_controls():
    tools = {t.name: t for t in load_tools(ROOT)}
    assert (tools["deploy.preview"].approval, tools["deploy.preview"].gate) == ("none", "preview")
    assert (tools["mobile.build"].approval, tools["mobile.build"].gate) == ("none", "preview")
    assert (tools["deploy.production"].approval, tools["deploy.production"].gate) == ("explicit", "production")
    assert (tools["store.submit"].approval, tools["store.submit"].gate) == ("explicit", "production")
    # An incident must never wait on a failing check.
    assert (tools["deploy.rollback"].approval, tools["deploy.rollback"].gate) == ("explicit", "")
    assert tools["repo.read"].gate == ""
    assert all("sd3" not in t.roles and "sd2" not in t.roles for n, t in tools.items() if n.split(".")[0] in {"deploy", "mobile", "store"})


def test_policy_shows_the_gate_and_registry_rejects_unknown_gates(tmp_path: Path):
    policy = policy_for_role(ROOT, "sd1")
    assert {"name": "deploy.preview", "transport": "runtime", "risk": "write", "scopes": ["deploy.preview", "network.write"], "approval": "none", "gate": "preview"} in policy["allowed_tools"]
    assert next(t for t in policy["approval_required_tools"] if t["name"] == "deploy.production")["gate"] == "production"
    assert "gate" not in next(t for t in policy["allowed_tools"] if t["name"] == "repo.read")

    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "tools.json").write_text(json.dumps({"tools": [{"name": "x", "scopes": ["x"], "roles": ["sd1"], "gate": "whenever"}]}), encoding="utf-8")
    result = check_registry(tmp_path)
    assert result["status"] == "fail" and result["invalid_gates"] == ["x"]


# --- decisions --------------------------------------------------------------


def test_deploy_is_denied_until_the_gate_passes(project: Path):
    assert decide(project, "deploy.preview", "sd1").reason == "deploy-gate-required:preview"
    assert decide(project, "deploy.production", "sd1", approved=True).reason == "deploy-gate-required:production"
    assert decide(project, "deploy.rollback", "sd1").reason == "approval-required"
    assert decide(project, "deploy.rollback", "sd1", approved=True).allowed

    assert deploy.gate(project, "preview")["status"] == "pass"
    assert decide(project, "deploy.preview", "sd1").allowed
    assert decide(project, "mobile.build", "sd1").allowed
    # Passing preview says nothing about production.
    assert decide(project, "deploy.production", "sd1", approved=True).reason == "deploy-gate-required:production"
    assert decide(project, "deploy.preview", "sd3").reason == "role-not-authorized"


def test_production_needs_the_gate_and_then_approval(project: Path):
    make_releasable(project)
    result = deploy.gate(project, "production", "true")
    assert result["status"] == "pass", result["checks"]
    assert decide(project, "deploy.production", "sd1").reason == "approval-required"
    assert decide(project, "deploy.production", "sd1", approved=True).allowed
    assert decide(project, "store.submit", "sd1", approved=True).allowed
    assert decide(project, "deploy.preview", "sd1").allowed  # production is a superset of preview


def test_a_gate_result_does_not_outlive_the_tree_it_checked(project: Path):
    deploy.gate(project, "preview")
    assert deploy.gate_satisfied(project, "preview")

    (project / "vercel.json").write_text('{"changed": true}', encoding="utf-8")
    assert not deploy.gate_satisfied(project, "preview")
    assert decide(project, "deploy.preview", "sd1").reason == "deploy-gate-required:preview"

    deploy.gate(project, "preview")
    assert deploy.gate_satisfied(project, "preview")
    commit(project)
    assert not deploy.gate_satisfied(project, "preview")  # a new commit needs a new run


def test_a_failed_run_replaces_an_earlier_pass(project: Path):
    deploy.gate(project, "preview")
    assert deploy.gate(project, "preview", "false")["status"] == "fail"
    assert not deploy.gate_satisfied(project, "preview")
    assert deploy.status(project)["gates"]["preview"]["failed"] == ["tests"]


# --- checks -----------------------------------------------------------------


def test_preview_and_production_differ_on_unfinished_work(project: Path):
    preview = deploy.gate(project, "preview")
    assert preview["status"] == "pass"
    assert statuses(preview) == {"version-control": "pass", "secret-scan": "pass", "stories": "pass", "credential-register": "skipped", "deploy-preflight": "pass", "tests": "not-run"}

    production = deploy.gate(project, "production")
    assert production["status"] == "fail" and production["failed"] == ["stories", "deploy-preflight"]
    stories_check = next(c for c in production["checks"] if c["check"] == "stories")
    assert stories_check["errors"] == ["not done: STORY-001"]


def test_a_committed_secret_blocks_every_gate(project: Path):
    fake = "sk-" + "a" * 24
    (project / "config.js").write_text(f"const k = '{fake}';\n", encoding="utf-8")
    commit(project)
    result = deploy.gate(project, "preview")
    assert result["status"] == "fail" and "secret-scan" in result["failed"]
    assert fake not in json.dumps(result)


def test_credential_drift_blocks_production_only(project: Path):
    make_releasable(project)
    (project / "app.js").write_text("const a = process.env.DATABASE_URL, b = process.env.UNDOCUMENTED_KEY;\n", encoding="utf-8")
    commit(project)
    assert statuses(deploy.gate(project, "preview"))["credential-register"] == "pass"
    production = deploy.gate(project, "production")
    assert "credential-register" in production["failed"]


def test_production_fails_closed_when_a_check_cannot_run(project: Path, tmp_path_factory, monkeypatch):
    make_releasable(project)
    monkeypatch.setenv(SKILLS_PATH_ENV, str(tmp_path_factory.mktemp("no-skills")))
    preview = deploy.gate(project, "preview")
    assert statuses(preview)["deploy-preflight"] == "unavailable" and preview["status"] == "pass"
    production = deploy.gate(project, "production")
    assert production["status"] == "fail" and "deploy-preflight" in production["failed"]


def test_mobile_and_workflow_checks_run_only_when_relevant(project: Path):
    assert "mobile-preflight" not in statuses(deploy.gate(project, "preview"))
    (project / "eas.json").write_text(json.dumps({"build": {"preview": {}}}), encoding="utf-8")
    (project / "app.json").write_text(json.dumps({"expo": {"version": "1.0.0", "ios": {"bundleIdentifier": "com.x"}, "android": {"package": "com.x"}}}), encoding="utf-8")
    workflows = project / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("on: push\njobs:\n  t:\n    runs-on: x\n    steps:\n      - uses: actions/checkout@main\n", encoding="utf-8")
    commit(project)
    result = deploy.gate(project, "preview")
    assert statuses(result)["mobile-preflight"] == "pass"
    assert statuses(result)["workflow-lint"] == "fail" and result["status"] == "fail"


def test_an_uncommitted_project_cannot_pass(tmp_path: Path, monkeypatch):
    monkeypatch.setenv(SKILLS_PATH_ENV, str(ROOT / "skills"))
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    result = deploy.gate(tmp_path, "preview")
    assert result["status"] == "fail" and "version-control" in result["failed"]
    assert not deploy.gate_satisfied(tmp_path, "preview")


def test_unknown_gate_is_rejected(project: Path):
    with pytest.raises(ValueError, match="unknown gate"):
        deploy.gate(project, "staging")


# --- CLI --------------------------------------------------------------------


def test_cli_reports_the_gate_and_sets_the_exit_code(project: Path, monkeypatch, capsys):
    monkeypatch.chdir(project)
    assert main(["deploy", "status"]) == 0
    assert json.loads(capsys.readouterr().out)["gates"]["preview"] == {"status": "not-run", "current": False}
    assert main(["deploy", "check", "--env", "preview"]) == 0
    capsys.readouterr()
    assert main(["deploy", "check", "--env", "production"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "fail"
    assert main(["deploy", "status"]) == 0
    gates = json.loads(capsys.readouterr().out)["gates"]
    assert gates["preview"]["current"] is True and gates["production"]["current"] is False
