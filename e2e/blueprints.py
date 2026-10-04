"""Blueprints: the lifecycle a product moves through, phase by phase.

Keyword matching answers "which specialist fits this sentence". It cannot
answer "what comes after the API contract" or "is this app ready to deploy".
A blueprint states the phases of a product type, the skills each phase needs,
and the artifact that proves the phase is finished, so SD2 can sequence a
whole build and refuse to start a phase whose inputs do not exist yet.

Blueprints are JSON so the engine needs no YAML dependency.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import stories as story_registry
from .project import load_config
from .skills import discover

#: Searched in order when a project has no explicit configuration.
DEFAULT_BLUEPRINT_PATHS = ("workflows", ".e2e/workflows")

#: Colon-separated paths, highest precedence. Mirrors E2E_SKILLS_PATH.
BLUEPRINTS_PATH_ENV = "E2E_BLUEPRINTS_PATH"

VALID_APPROVALS = (None, "owner")


def blueprint_paths(root: str | Path = ".") -> list[Path]:
    root = Path(root).resolve()
    env = os.environ.get(BLUEPRINTS_PATH_ENV, "").strip()
    if env:
        raw = [p for p in env.split(os.pathsep) if p]
    else:
        configured = load_config(root).get("blueprints_paths")
        raw = [str(p) for p in configured] if isinstance(configured, list) and configured else list(DEFAULT_BLUEPRINT_PATHS)
    resolved: list[Path] = []
    for entry in raw:
        candidate = Path(entry)
        candidate = candidate if candidate.is_absolute() else root / candidate
        if candidate not in resolved:
            resolved.append(candidate)
    return resolved


def _skill_name(entry: Any) -> str:
    return entry["skill"] if isinstance(entry, dict) else str(entry)


def _skill_platforms(entry: Any) -> list[str]:
    return [p.lower() for p in entry.get("platforms", [])] if isinstance(entry, dict) else []


def list_blueprints(root: str | Path = ".") -> list[dict[str, Any]]:
    """Every readable blueprint, earlier paths winning on a name clash."""
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for base in blueprint_paths(root):
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                data = {"name": path.stem, "_error": f"unreadable: {exc}"}
            if not isinstance(data, dict):
                data = {"name": path.stem, "_error": "top level must be an object"}
            data.setdefault("name", path.stem)
            data["_path"] = path.as_posix()
            if data["name"] not in seen:
                seen.add(data["name"])
                found.append(data)
    return found


def load(root: str | Path, name: str) -> dict[str, Any]:
    for blueprint in list_blueprints(root):
        if blueprint["name"] == name:
            if blueprint.get("_error"):
                raise ValueError(f"blueprint {name}: {blueprint['_error']}")
            return blueprint
    available = ", ".join(b["name"] for b in list_blueprints(root)) or "none"
    raise ValueError(f"blueprint {name} not found (available: {available})")


def _ancestors(phase_id: str, phases: dict[str, dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    stack = list(phases[phase_id].get("depends_on", []))
    while stack:
        current = stack.pop()
        if current in seen or current not in phases:
            continue
        seen.add(current)
        stack.extend(phases[current].get("depends_on", []))
    return seen


def _contract_order(names: list[str], registry: dict[str, dict[str, Any]]) -> tuple[dict[str, list[str]], list[str]]:
    """Within one phase, who must wait for whom, from the skills' contracts.

    Returns ``(dependencies per skill, skills stuck in a cycle)``.
    """
    produced_by = {artifact: name for name in names for artifact in registry.get(name, {}).get("produces", [])}
    edges = {
        name: sorted({produced_by[a] for a in registry.get(name, {}).get("consumes", []) if a in produced_by and produced_by[a] != name})
        for name in names
    }
    pending = {name: set(deps) for name, deps in edges.items()}
    while pending:
        free = [name for name, deps in pending.items() if not deps]
        if not free:
            return edges, sorted(pending)
        for name in free:
            del pending[name]
        for deps in pending.values():
            deps.difference_update(free)
    return edges, []


def _validate(blueprint: dict[str, Any], registry: dict[str, dict[str, Any]]) -> list[str]:
    name = blueprint["name"]
    if blueprint.get("_error"):
        return [f"{name}: {blueprint['_error']}"]
    errors: list[str] = []
    phases = blueprint.get("phases")
    if not isinstance(phases, list) or not phases:
        return [f"{name}: `phases` must be a non-empty list"]
    inputs = set(blueprint.get("inputs", []))
    by_id: dict[str, dict[str, Any]] = {}
    for phase in phases:
        pid = phase.get("id") if isinstance(phase, dict) else None
        if not pid:
            errors.append(f"{name}: a phase has no `id`")
            continue
        label = f"{name}/{pid}"
        if pid in by_id:
            errors.append(f"{label}: duplicate phase id")
            continue
        # Dependencies must point backwards. That keeps the file readable top
        # to bottom and makes a cycle impossible to write.
        for dep in phase.get("depends_on", []):
            if dep not in by_id:
                errors.append(f"{label}: depends_on `{dep}` is not an earlier phase")
        by_id[pid] = phase

        names = [_skill_name(entry) for entry in phase.get("skills", [])]
        if not names:
            errors.append(f"{label}: no skills")
        for skill in names:
            if skill not in registry:
                errors.append(f"{label}: skill `{skill}` is not in the registry")
        if phase.get("approval") not in VALID_APPROVALS:
            errors.append(f"{label}: approval `{phase.get('approval')}` not in {[a for a in VALID_APPROVALS if a]}")
        produces = phase.get("produces", [])
        if not produces and not phase.get("requires_stories_done"):
            errors.append(f"{label}: no exit condition (`produces` or `requires_stories_done`)")

        offered = {artifact for skill in names for artifact in registry.get(skill, {}).get("produces", [])}
        for artifact in produces:
            if artifact not in offered:
                errors.append(f"{label}: no skill in this phase declares `produces: {artifact}`")

        available = set(inputs) | offered
        for ancestor in _ancestors(pid, by_id):
            available.update(by_id[ancestor].get("produces", []))
        for skill in names:
            for artifact in registry.get(skill, {}).get("consumes", []):
                if artifact not in available:
                    errors.append(f"{label}: `{skill}` consumes {artifact}, which no input or earlier phase provides")
        _, cycle = _contract_order(names, registry)
        if cycle:
            errors.append(f"{label}: contract cycle between {', '.join(cycle)}")
    return errors


def check(root: str | Path = ".") -> dict[str, Any]:
    """Validate every blueprint against the skill registry and its contracts."""
    root = Path(root).resolve()
    registry = {s["name"]: s for s in discover(root)}
    blueprints = list_blueprints(root)
    errors: list[str] = []
    if not blueprints:
        errors.append("no blueprints found. Searched: " + ", ".join(p.as_posix() for p in blueprint_paths(root)))
    for blueprint in blueprints:
        errors.extend(_validate(blueprint, registry))
    return {
        "status": "fail" if errors else "pass",
        "blueprints": [b["name"] for b in blueprints],
        "searched": [p.as_posix() for p in blueprint_paths(root)],
        "errors": errors,
    }


def _present(root: Path, artifact: str) -> bool:
    """Whether an artifact exists. Presence only: SD3 judges its quality."""
    target = root / artifact
    if artifact.endswith("/"):
        return target.is_dir() and any(p.is_file() for p in target.iterdir())
    return target.is_file() and target.stat().st_size > 0


def status(root: str | Path, name: str) -> dict[str, Any]:
    """Where a project stands in a blueprint, and what may start next."""
    root = Path(root).resolve()
    blueprint = load(root, name)
    missing_inputs = [a for a in blueprint.get("inputs", []) if not _present(root, a)]
    stories = story_registry.load(root)
    open_stories = [s["id"] for s in stories if s["status"] != "done"]

    phases: list[dict[str, Any]] = []
    complete: set[str] = set()
    for phase in blueprint["phases"]:
        missing = [a for a in phase.get("produces", []) if not _present(root, a)]
        stories_pending: list[str] = []
        if phase.get("requires_stories_done"):
            stories_pending = open_stories if stories else ["<no stories written>"]
        waiting_on = [d for d in phase.get("depends_on", []) if d not in complete]
        if not missing and not stories_pending:
            state = "complete"
            complete.add(phase["id"])
        elif missing_inputs or waiting_on:
            state = "blocked"
        else:
            state = "ready"
        phases.append({
            "id": phase["id"],
            "state": state,
            "objective": phase.get("objective", ""),
            "skills": [_skill_name(e) for e in phase.get("skills", [])],
            "missing_artifacts": missing,
            "stories_pending": stories_pending,
            "waiting_on": waiting_on,
            "approval": phase.get("approval"),
        })

    ready = [p["id"] for p in phases if p["state"] == "ready"]
    return {
        "blueprint": blueprint["name"],
        "description": blueprint.get("description", ""),
        "state": "complete" if len(complete) == len(phases) else ("blocked" if not ready else "in-progress"),
        "missing_inputs": missing_inputs,
        "current_phase": ready[0] if ready else None,
        "ready_phases": ready,
        "phases": phases,
    }


def select_workers(
    root: str | Path,
    name: str,
    phase_id: str,
    platforms: list[str] | None = None,
    limit: int = 4,
) -> dict[str, Any]:
    """The skills to run for one phase, ordered by their contracts.

    Skills tagged with platforms are dropped when the story being built does
    not target any of them, so a web-only story never launches a mobile worker.
    Anything over ``limit`` is reported as deferred rather than silently lost.
    """
    root = Path(root).resolve()
    blueprint = load(root, name)
    phase = next((p for p in blueprint["phases"] if p["id"] == phase_id), None)
    if phase is None:
        raise ValueError(f"blueprint {name} has no phase {phase_id}")
    wanted = {p.lower() for p in platforms or []}
    names: list[str] = []
    skipped: list[str] = []
    for entry in phase.get("skills", []):
        tags = _skill_platforms(entry)
        if wanted and tags and not wanted.intersection(tags):
            skipped.append(_skill_name(entry))
        elif _skill_name(entry) not in names:
            names.append(_skill_name(entry))
    registry = {s["name"]: s for s in discover(root)}
    selected, deferred = names[:limit], names[limit:]
    edges, _ = _contract_order(selected, registry)
    return {
        "phase": phase,
        "skills": [registry.get(n) or {"name": n, "path": f"skills/{n}/SKILL.md", "consumes": [], "produces": []} for n in selected],
        "depends_on": edges,
        "deferred": deferred,
        "skipped_for_platform": skipped,
    }
