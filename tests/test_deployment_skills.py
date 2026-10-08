"""The deployment skills' scripts decide whether a deploy may proceed, so they are tested like engine code."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from e2e import blueprints
from e2e.skills import discover, match

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NEW_SKILLS = ("app-deployment", "mobile-release", "ci-cd-pipeline", "observability")
TARGETS = ("vercel", "firebase", "supabase", "railway", "aws", "gcp", "azure", "vps")


def load(skill: str, script: str):
    spec = importlib.util.spec_from_file_location(script, SKILLS / skill / "scripts" / f"{script}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = load("app-deployment", "deploy_preflight")
smoke = load("app-deployment", "smoke_test")
mobile = load("mobile-release", "mobile_preflight")
lint = load("ci-cd-pipeline", "workflow_lint")


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


# --- deploy preflight -------------------------------------------------------


def test_preflight_detects_targets_and_only_warns_in_preview(repo: Path):
    (repo / "vercel.json").write_text("{}", encoding="utf-8")
    (repo / "supabase").mkdir()
    (repo / "supabase" / "config.toml").write_text("", encoding="utf-8")
    result = preflight.run(repo, "preview")
    assert result["ok"] and set(result["targets"]) == {"vercel", "supabase"}
    assert any("DEPLOYMENT.md missing" in w for w in result["warnings"])


def test_preflight_blocks_tracked_env_and_key_files(repo: Path):
    for name in (".env.production", ".env.example", "prod-firebase-adminsdk-x.json", "deploy.pem", "README.md"):
        (repo / name).write_text("x", encoding="utf-8")
    git(repo, "add", "-A")
    errors = preflight.run(repo, "preview")["errors"]
    flagged = {e.split(":")[0] for e in errors}
    assert flagged == {".env.production", "prod-firebase-adminsdk-x.json", "deploy.pem"}


def test_preflight_untracked_env_file_is_fine(repo: Path):
    (repo / ".env").write_text("x", encoding="utf-8")
    assert preflight.run(repo, "preview")["errors"] == []


def test_preflight_dockerfile_must_not_bake_secrets(repo: Path):
    (repo / "Dockerfile").write_text(
        "FROM node:22\nARG BUILD_TOKEN\nENV NODE_ENV=production\nENV API_KEY=abc\nENV JWT_SECRET=$JWT_SECRET\nCOPY .env .env\n",
        encoding="utf-8",
    )
    result = preflight.run(repo, "preview")
    assert result["errors"] == [
        "Dockerfile:4: sets a value for API_KEY; inject it at runtime instead",
        "Dockerfile:6: copies an env file into the image",
    ]
    assert "abc" not in json.dumps(result)
    assert any("runs as root" in w for w in result["warnings"])


def test_preflight_production_needs_real_records_and_approval(repo: Path):
    assert len(preflight.run(repo, "production")["errors"]) == 3

    (repo / "CREDENTIALS.md").write_text("# c\n", encoding="utf-8")
    (repo / "DEPLOYMENT.md").write_text((ROOT / "templates" / "DEPLOYMENT.md").read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "RELEASE-CHECKLIST.md").write_text((ROOT / "templates" / "RELEASE-CHECKLIST.md").read_text(encoding="utf-8"), encoding="utf-8")
    errors = " | ".join(preflight.run(repo, "production")["errors"])
    for section in ("Targets", "Smoke Test", "Rollback", "Evidence"):
        assert f"`## {section}` is empty or still the template text" in errors
    assert "`Release owner:` is not filled in" in errors and "`Approved on:` is not filled in" in errors

    example = (SKILLS / "app-deployment" / "examples" / "DEPLOYMENT.example.md").read_text(encoding="utf-8")
    (repo / "DEPLOYMENT.md").write_text(example, encoding="utf-8")
    checklist = (repo / "RELEASE-CHECKLIST.md").read_text(encoding="utf-8")
    checklist = checklist.replace("- Release owner:", "- Release owner: A. Owner").replace("- Approved on:", "- Approved on: 2026-10-06")
    (repo / "RELEASE-CHECKLIST.md").write_text(checklist, encoding="utf-8")
    assert preflight.run(repo, "production")["errors"] == []


def test_preflight_outside_git_says_so(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    assert any("not a git repository" in w for w in preflight.run(tmp_path, "preview")["warnings"])


# --- smoke test -------------------------------------------------------------


class _Handler(BaseHTTPRequestHandler):
    flaky_calls = 0
    seen_headers: list[str] = []

    def do_GET(self):  # noqa: N802 - http.server API
        type(self).seen_headers.append(self.headers.get("X-Bypass", ""))
        if self.path == "/health":
            self._send(200, "status ok")
        elif self.path == "/admin":
            self._send(401, "denied")
        elif self.path == "/flaky":
            type(self).flaky_calls += 1
            self._send(200 if type(self).flaky_calls >= 3 else 503, "warming")
        else:
            self._send(500, "boom")

    def _send(self, status: int, body: str) -> None:
        self.send_response(status)
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):  # keep test output quiet
        pass


@pytest.fixture
def server():
    _Handler.flaky_calls = 0
    _Handler.seen_headers = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_smoke_passes_on_expected_status_and_content(server: str, capsys):
    assert smoke.main(["--url", server, "--path", "/health", "--path", "/admin=401", "--contains", "ok", "--delay", "0"]) == 0
    out = capsys.readouterr().out
    assert "smoke_test: OK (2/2 checks)" in out and "PASS    /admin 401" in out


def test_smoke_fails_on_wrong_status_or_missing_text(server: str, capsys):
    assert smoke.main(["--url", server, "--path", "/boom", "--retries", "1"]) == 1
    assert "expected 200, got 500" in capsys.readouterr().out
    assert smoke.main(["--url", server, "--path", "/health", "--contains", "absent", "--retries", "1"]) == 1
    assert "does not contain the expected text" in capsys.readouterr().out


def test_smoke_retries_while_a_deploy_warms_up(server: str, capsys):
    assert smoke.main(["--url", server, "--path", "/flaky", "--retries", "3", "--delay", "0"]) == 0
    capsys.readouterr()
    _Handler.flaky_calls = 0
    assert smoke.main(["--url", server, "--path", "/flaky", "--retries", "2", "--delay", "0"]) == 1


def test_smoke_checks_file_and_headers_are_sent_but_never_printed(server: str, tmp_path: Path, capsys):
    checks = tmp_path / "smoke.json"
    checks.write_text(json.dumps([{"path": "/health", "contains": "ok"}, {"path": "/admin", "status": 401}]), encoding="utf-8")
    assert smoke.main(["--url", server, "--checks", str(checks), "--header", "X-Bypass: hush-value", "--json"]) == 0
    out = capsys.readouterr().out
    assert json.loads(out)["passed"] == 2
    assert "hush-value" in _Handler.seen_headers and "hush-value" not in out


def test_smoke_rejects_bad_input_and_unreachable_hosts(capsys):
    assert smoke.main(["--url", "file:///etc/passwd"]) == 1
    assert smoke.main(["--url", "http://127.0.0.1:9", "--path", "/health=abc"]) == 1
    assert smoke.main(["--url", "http://127.0.0.1:9", "--retries", "1", "--timeout", "1"]) == 1
    assert "no response" in capsys.readouterr().out


# --- mobile preflight -------------------------------------------------------


def expo_project(root: Path, profiles=("development", "preview", "production"), submit=True, **expo) -> None:
    eas = {"build": {name: {} for name in profiles}}
    if submit:
        eas["submit"] = {"production": {}}
    (root / "eas.json").write_text(json.dumps(eas), encoding="utf-8")
    app = {"version": "1.0.0", "ios": {"bundleIdentifier": "com.example.app"}, "android": {"package": "com.example.app"}}
    app.update(expo)
    (root / "app.json").write_text(json.dumps({"expo": app}), encoding="utf-8")


def test_mobile_preflight_accepts_a_complete_expo_project(repo: Path):
    expo_project(repo)
    for env in ("preview", "production"):
        result = mobile.run(repo, env)
        assert result["ok"] and result["project"] == "expo", result["errors"]
    assert mobile.run(repo, "preview")["profiles"] == ["development", "preview", "production"]


def test_mobile_preflight_reports_missing_configuration(repo: Path):
    expo_project(repo, profiles=("development",), submit=False, ios={}, version="")
    errors = " | ".join(mobile.run(repo, "production")["errors"])
    assert "no `production` build profile" in errors and "no `production` submit profile" in errors
    assert "no `version`" in errors and "no `ios.bundleIdentifier`" in errors
    assert "no `preview` build profile" in " | ".join(mobile.run(repo, "preview")["errors"])


def test_mobile_preflight_blocks_tracked_signing_material(repo: Path):
    expo_project(repo)
    (repo / "android").mkdir()
    for name in ("android/upload.keystore", "android/debug.keystore", "AuthKey_ABC123.p8", "play-store-credentials.json", "google-services.json"):
        (repo / name).write_text("x", encoding="utf-8")
    git(repo, "add", "-A")
    flagged = {e.split(":")[0] for e in mobile.run(repo, "preview")["errors"]}
    assert flagged == {"android/upload.keystore", "AuthKey_ABC123.p8", "play-store-credentials.json"}


def test_mobile_preflight_warnings_and_unknown_projects(repo: Path):
    expo_project(repo, updates={"url": "https://u.example.com"})
    assert any("runtimeVersion" in w for w in mobile.run(repo, "preview")["warnings"])
    (repo / "app.config.ts").write_text("export default {}", encoding="utf-8")
    assert any("dynamic" in w for w in mobile.run(repo, "preview")["warnings"])
    (repo / "eas.json").write_text("{not json", encoding="utf-8")
    assert any("eas.json: not valid JSON" in e for e in mobile.run(repo, "preview")["errors"])


def test_mobile_preflight_needs_a_mobile_project(repo: Path):
    assert "no mobile project found" in mobile.run(repo, "preview")["errors"][0]
    (repo / "fastlane").mkdir()
    (repo / "fastlane" / "Fastfile").write_text("lane :beta do\nend\n", encoding="utf-8")
    result = mobile.run(repo, "preview")
    assert result["ok"] and result["project"] == "fastlane"


# --- workflow lint ----------------------------------------------------------

GOOD_WORKFLOW = """name: CI
on:
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v9
      - uses: ./.github/actions/local
      - run: npm test
  deploy-production:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment: production
    concurrency: deploy-production
    steps:
      - uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3
      - name: Deploy
        run: ./deploy.sh --prod
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
"""


def workflow(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "wf.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_lint_accepts_a_careful_workflow(tmp_path: Path):
    assert lint.lint(workflow(tmp_path, GOOD_WORKFLOW)) == ([], [])


@pytest.mark.parametrize(
    "old, new, expected",
    [
        ("actions/checkout@v9", "actions/checkout@main", "pinned to a branch"),
        ("actions/checkout@v9", "actions/checkout", "not pinned to a version"),
        ("run: npm test", "run: echo ${{ secrets.DEPLOY_TOKEN }}", "a secret is written to the log"),
        ("run: npm test", "run: curl -H \"A: ${{ secrets.DEPLOY_TOKEN }}\" https://x.example", "secret interpolated inside a run script"),
        ("run: npm test", "run: |\n          echo start\n          git checkout ${{ github.head_ref }}", "untrusted event field"),
        ("run: npm test", "run: echo \"${{ github.event.pull_request.title }}\"", "untrusted event field"),
        ("      - run: npm test", "      - run: npm test\n        continue-on-error: true", "continue-on-error hides failures"),
        ("runs-on: ubuntu-latest\n    timeout-minutes: 10\n    steps:\n      - uses: actions/checkout@v9", "runs-on: <runner>\n    timeout-minutes: 10\n    steps:\n      - uses: actions/checkout@v9", "unresolved template placeholder"),
    ],
)
def test_lint_errors(tmp_path: Path, old: str, new: str, expected: str):
    assert old in GOOD_WORKFLOW
    errors, _ = lint.lint(workflow(tmp_path, GOOD_WORKFLOW.replace(old, new, 1)))
    assert any(expected in e for e in errors), errors


def test_lint_flags_pull_request_target_running_pr_code(tmp_path: Path):
    text = GOOD_WORKFLOW.replace("  pull_request:", "  pull_request_target:").replace(
        "      - uses: actions/checkout@v9", "      - uses: actions/checkout@v9\n        with:\n          ref: ${{ github.event.pull_request.head.sha }}"
    )
    errors, _ = lint.lint(workflow(tmp_path, text))
    assert any("pull_request_target checks out pull-request code" in e for e in errors)


def test_lint_warnings_and_strict_mode(tmp_path: Path, capsys):
    text = (
        GOOD_WORKFLOW.replace("permissions:\n  contents: read\n", "")
        .replace("    timeout-minutes: 10\n    steps:\n      - uses: actions/checkout@v9", "    steps:\n      - uses: actions/checkout@v9")
        .replace("    environment: production\n    concurrency: deploy-production\n", "")
    )
    path = workflow(tmp_path, text)
    errors, warnings = lint.lint(path)
    joined = " | ".join(warnings)
    assert errors == []
    assert "no `permissions:` block" in joined and "job `test` has no timeout-minutes" in joined
    assert "without `environment:`" in joined and "without `concurrency:`" in joined
    assert lint.main([str(path)]) == 0
    assert lint.main([str(path), "--strict"]) == 1
    capsys.readouterr()


def test_lint_template_fails_until_placeholders_are_replaced(capsys):
    assert lint.main([str(SKILLS / "ci-cd-pipeline" / "templates" / "ci.yml")]) == 1
    out = capsys.readouterr().out
    assert "unresolved template placeholder" in out and "pinned to a branch" not in out


def test_lint_reports_when_there_is_nothing_to_check(tmp_path: Path, capsys):
    assert lint.main(["--root", str(tmp_path)]) == 1
    assert "no workflow files found" in capsys.readouterr().out


# --- skills, references, blueprints -----------------------------------------


def test_skills_are_registered_with_contracts():
    registry = {s["name"]: s for s in discover(ROOT)}
    for name in NEW_SKILLS:
        assert registry[name]["has_frontmatter"], name
    assert registry["app-deployment"]["produces"] == ["DEPLOYMENT.md", "RELEASE-CHECKLIST.md"]
    assert registry["observability"]["produces"] == ["RUNBOOK.md"]
    assert registry["devops-engineer"]["produces"] == []


def test_every_target_has_a_reference_with_the_same_sections():
    for target in TARGETS:
        text = (SKILLS / "app-deployment" / "references" / f"{target}.md").read_text(encoding="utf-8")
        for heading in ("## Fits", "## Authentication", "## Preview deploy", "## Production deploy", "## Rollback", "## Gotchas"):
            assert heading in text, (target, heading)


def test_paths_cited_in_skill_documents_exist():
    for name in NEW_SKILLS:
        text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        for rel in set(re.findall(r"`((?:references|examples|templates|scripts)/[\w./-]+\.\w+)`", text)):
            assert (SKILLS / name / rel).is_file() or (ROOT / rel).is_file(), (name, rel)
        for rel in set(re.findall(r"python (skills/[\w./-]+\.py)", text)):
            assert (ROOT / rel).is_file(), (name, rel)


@pytest.mark.parametrize(
    "task, expected",
    [
        ("deploy the web app to Vercel", "app-deployment"),
        ("deploy the API to Railway and roll back if it fails", "app-deployment"),
        ("host the backend on a VPS", "app-deployment"),
        ("submit the iOS build to TestFlight", "mobile-release"),
        ("publish an OTA update for the Android app", "mobile-release"),
        ("add a GitHub Actions workflow to run tests on every pull request", "ci-cd-pipeline"),
        ("add error tracking and uptime alerts and write the runbook", "observability"),
    ],
)
def test_routing(task: str, expected: str):
    assert match(ROOT, task)[0]["name"] == expected, [s["name"] for s in match(ROOT, task)[:4]]


def test_unrelated_tasks_do_not_reach_deployment_skills():
    for task in ("build a login API endpoint", "design the database schema for orders", "review authentication code for XSS and injection"):
        assert not set(NEW_SKILLS) & {s["name"] for s in match(ROOT, task)[:3]}, task


def test_blueprint_deployment_phases_use_the_specialists_in_contract_order():
    preview = blueprints.select_workers(ROOT, "full-stack-app", "preview")
    assert [s["name"] for s in preview["skills"]] == ["app-deployment", "ci-cd-pipeline", "mobile-release"]
    assert preview["depends_on"] == {"app-deployment": [], "ci-cd-pipeline": ["app-deployment"], "mobile-release": ["app-deployment"]}

    release = blueprints.select_workers(ROOT, "full-stack-app", "release")
    assert [s["name"] for s in release["skills"]] == ["app-deployment", "mobile-release", "observability"]
    assert release["phase"]["approval"] == "owner"
    assert release["depends_on"]["observability"] == ["app-deployment"]

    assert "mobile-release" not in [s["name"] for s in blueprints.select_workers(ROOT, "web-app", "preview")["skills"]]
