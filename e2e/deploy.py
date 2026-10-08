"""The deploy gate: what must be true before anything is deployed.

A skill can tell an agent to run preflight checks; nothing stops the agent from
skipping them. The gate makes the checks a precondition the engine enforces:
:func:`gate` runs them and records the outcome against the exact state of the
working tree, and :func:`e2e.tools.decide` refuses a deploy capability unless
that record exists, passed, and still describes the tree being deployed.

The gate composes checks that already exist (the secret scan, the story check,
and the deployment skills' own scripts) instead of re-implementing them.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import stories as story_registry
from .hooks import secret_scan
from .project import skills_paths

GATES = ("preview", "production")
RECORD = ".e2e/deploy-gate.json"

#: Kept out of the fingerprint: the gate writes its own record there.
_EXCLUDE = ":(exclude).e2e"


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def fingerprint(root: str | Path) -> dict[str, str | None]:
    """Identify the tree a gate result applies to: the commit plus any local changes.

    A gate that passed on one commit says nothing about the next, and nothing
    about uncommitted edits made after it ran.
    """
    root = Path(root).resolve()
    commit = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain", "--", ".", _EXCLUDE)
    if commit is None or status is None:
        return {"commit": None, "state": None}
    diff = _git(root, "diff", "HEAD", "--", ".", _EXCLUDE) or ""
    digest = hashlib.sha256(f"{commit}\n{status}\n{diff}".encode("utf-8", errors="replace")).hexdigest()[:16]
    return {"commit": commit.strip(), "state": digest}


def _skill_script(root: Path, skill: str, script: str) -> Path | None:
    for base in skills_paths(root):
        candidate = base / skill / "scripts" / script
        if candidate.is_file():
            return candidate
    return None


def _run_script(root: Path, check: str, skill: str, script: str, *args: str) -> dict[str, Any]:
    path = _skill_script(root, skill, script)
    if path is None:
        return {"check": check, "status": "unavailable", "detail": f"{skill}/scripts/{script} not found on the skill path"}
    try:
        proc = subprocess.run(
            [sys.executable, str(path), "--root", str(root), "--json", *args],
            cwd=root, text=True, capture_output=True, timeout=180,
        )
        data = json.loads(proc.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"check": check, "status": "fail", "detail": f"{script} did not return a result: {exc}"}
    return {
        "check": check,
        "status": "pass" if proc.returncode == 0 else "fail",
        "errors": data.get("errors", []),
        "warnings": data.get("warnings", []),
    }


def _stories(root: Path, env: str) -> dict[str, Any]:
    if not (root / story_registry.STORIES_DIR).is_dir():
        return {"check": "stories", "status": "skipped", "detail": "project has no stories/"}
    result = story_registry.check(root)
    errors = list(result["errors"])
    if env == "production":
        pending = [s["id"] for s in story_registry.load(root) if s["status"] != "done"]
        if pending:
            errors.append("not done: " + ", ".join(pending))
    return {"check": "stories", "status": "fail" if errors else "pass", "errors": errors, "warnings": result["warnings"]}


def _tests(root: Path, command: str | None) -> dict[str, Any]:
    if not command:
        return {"check": "tests", "status": "not-run", "detail": "no test command supplied; pass --test to make tests part of the gate"}
    try:
        proc = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=900)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"check": "tests", "status": "fail", "command": command, "detail": str(exc)}
    return {"check": "tests", "status": "pass" if proc.returncode == 0 else "fail", "command": command, "exit_code": proc.returncode}


def _is_mobile(root: Path) -> bool:
    return (
        (root / "eas.json").is_file()
        or (root / "app.json").is_file()
        or any(root.glob("app.config.*"))
        or (root / "fastlane" / "Fastfile").is_file()
    )


def _has_workflows(root: Path) -> bool:
    folder = root / ".github" / "workflows"
    return folder.is_dir() and any(p.suffix in {".yml", ".yaml"} for p in folder.iterdir())


def gate(root: str | Path = ".", env: str = "preview", test_command: str | None = None) -> dict[str, Any]:
    """Run every pre-deploy check for ``env`` and record the outcome.

    Production fails closed: a check that could not run counts as a failure.
    In preview an unavailable check is reported and does not block.
    """
    if env not in GATES:
        raise ValueError(f"unknown gate: {env}")
    root = Path(root).resolve()
    production = env == "production"

    scan = secret_scan(root)
    state = fingerprint(root)
    checks: list[dict[str, Any]] = [
        # Without a commit a deploy cannot be traced or shown to be unchanged.
        {"check": "version-control", "status": "pass", "commit": state["commit"]}
        if state["commit"]
        else {"check": "version-control", "status": "fail", "errors": ["no git commit; commit the project so the deploy is traceable"]},
        {"check": "secret-scan", "status": "pass" if scan["status"] == "pass" else "fail", "errors": scan["evidence"]},
        _stories(root, env),
    ]
    if (root / "CREDENTIALS.md").is_file():
        args = ("--code-scan", "--strict") if production else ("--code-scan",)
        checks.append(_run_script(root, "credential-register", "credential-inventory", "credentials_check.py", *args))
    else:
        # In production the deploy preflight reports the missing register as an error.
        checks.append({"check": "credential-register", "status": "skipped", "detail": "CREDENTIALS.md not found"})
    checks.append(_run_script(root, "deploy-preflight", "app-deployment", "deploy_preflight.py", "--env", env))
    if _is_mobile(root):
        checks.append(_run_script(root, "mobile-preflight", "mobile-release", "mobile_preflight.py", "--env", env))
    if _has_workflows(root):
        checks.append(_run_script(root, "workflow-lint", "ci-cd-pipeline", "workflow_lint.py"))
    checks.append(_tests(root, test_command))

    blocking = {"fail", "unavailable"} if production else {"fail"}
    failed = [c["check"] for c in checks if c["status"] in blocking]
    result = {
        "env": env,
        "status": "fail" if failed else "pass",
        "failed": failed,
        "checks": checks,
        "commit": state["commit"],
        "state": state["state"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "approval": "release owner approval is still required" if production else "none",
    }
    _record(root, result)
    return result


def _load_record(root: Path) -> dict[str, Any]:
    try:
        data = json.loads((root / RECORD).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _record(root: Path, result: dict[str, Any]) -> None:
    record = _load_record(root)
    # A failed run replaces an earlier pass, so a stale approval cannot linger.
    record[result["env"]] = {key: result[key] for key in ("status", "failed", "commit", "state", "checked_at")}
    path = root / RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def gate_satisfied(root: str | Path, name: str) -> bool:
    """Whether ``name`` passed for the tree as it is right now.

    The production gate is a superset of preview, so it satisfies both.
    """
    root = Path(root).resolve()
    record = _load_record(root)
    current = fingerprint(root)
    if current["state"] is None:
        return False
    accepted = (name, "production") if name == "preview" else (name,)
    return any(
        isinstance(record.get(env), dict)
        and record[env].get("status") == "pass"
        and record[env].get("commit") == current["commit"]
        and record[env].get("state") == current["state"]
        for env in accepted
    )


def status(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    record = _load_record(root)
    current = fingerprint(root)
    return {
        "commit": current["commit"],
        "gates": {
            env: {**record[env], "current": gate_satisfied(root, env)} if isinstance(record.get(env), dict) else {"status": "not-run", "current": False}
            for env in GATES
        },
    }
