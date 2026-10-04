from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from . import blueprints as blueprint_registry
from . import stories as story_registry
from .brain import CodeBrain
from .context import build_context
from .intelligence import build_intelligence
from .regression import analyze_regression_risk
from .skills import discover, match

MAX_ACTIVE_WORKERS = 4


def _id(task: str, skill: str, index: int) -> str:
    raw = f"{task}:{skill}:{index}".encode()
    return "sd1-" + hashlib.sha1(raw).hexdigest()[:10]


def _phase(skill: str) -> str:
    name = skill.lower()
    if any(x in name for x in ("architect", "database", "api")):
        return "foundation"
    if any(x in name for x in ("frontend", "react", "native", "expo", "ui-ux")):
        return "implementation"
    if any(x in name for x in ("security", "qa", "code-review")):
        return "verification"
    if "devops" in name:
        return "delivery"
    if name in {"research-first-engineering", "agent-introspection-debugging"}:
        return "foundation"
    return "implementation"


def _needs_research(task: str) -> bool:
    terms = {"add", "build", "create", "implement", "integrate", "replace", "refactor", "design", "new"}
    return any(term in task.lower().split() for term in terms)


def _skill_by_name(skills: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((skill for skill in skills if skill.get("name") == name), None)


def _fallback_skill(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "path": f"skills/{name}/SKILL.md",
        "purpose": f"Provide {name} responsibilities required by the execution plan.",
        "triggers": "runtime-required specialist escalation",
    }


def _prioritize_regression_workers(matched: list[dict[str, Any]], regression: dict[str, Any], available: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if regression["level"] == "low":
        return matched
    result = list(matched)
    qa = _skill_by_name(available, "qa-engineer") or _fallback_skill("qa-engineer")
    security = None
    if regression["level"] == "high":
        security = _skill_by_name(available, "security-engineer") or _fallback_skill("security-engineer")
    for required in (qa, security):
        if required and required["name"] in {s["name"] for s in result}:
            continue
        if required:
            if len(result) >= MAX_ACTIVE_WORKERS:
                result[-1] = required
            else:
                result.append(required)
    deduped = []
    seen = set()
    for skill in result:
        if skill["name"] not in seen:
            seen.add(skill["name"])
            deduped.append(skill)
    return deduped


def _story_gate(root: Path, story_id: str) -> tuple[dict[str, Any], list[str]]:
    """Load a story and say why it cannot start, if it cannot."""
    story = story_registry.get(root, story_id)
    blockers = []
    if story["status"] == "done":
        blockers.append(f"{story['id']} is already done")
    if not story["criteria"]:
        blockers.append(f"{story['id']} has no acceptance criteria to build or verify against")
    blockers.extend(
        f"{story['id']} waits on {dep}" for dep in story_registry.unmet_dependencies(story, story_registry.load(root))
    )
    return story, blockers


def plan(
    root: str | Path,
    task: str,
    brain: CodeBrain | None = None,
    blueprint: str | None = None,
    story: str | None = None,
) -> dict[str, Any]:
    """Build the SD2 plan for a task.

    With no blueprint, skills are chosen by matching the task text. With one,
    the blueprint's next ready phase chooses them and the skills' artifact
    contracts order them, so the plan follows the product lifecycle instead of
    the wording of the request. A story narrows the plan to one feature and
    hands its acceptance criteria to SD3.
    """
    root = Path(root).resolve()
    brain = brain or CodeBrain(root)
    if not brain.store.exists():
        brain.build()
    context = build_context(root, task, brain)
    blockers: list[str] = []
    story_record: dict[str, Any] | None = None
    if story:
        story_record, blockers = _story_gate(root, story)

    progress: dict[str, Any] | None = None
    selection: dict[str, Any] | None = None
    if blueprint:
        progress = blueprint_registry.status(root, blueprint)
        blockers.extend(f"blueprint input {artifact} is missing" for artifact in progress["missing_inputs"])
        if progress["current_phase"]:
            selection = blueprint_registry.select_workers(
                root, blueprint, progress["current_phase"], story_record["platforms"] if story_record else None, MAX_ACTIVE_WORKERS
            )
            if story_record and not selection["phase"].get("requires_stories_done"):
                blockers.append(
                    f"{story_record['id']} cannot start: blueprint phase `{progress['current_phase']}` must finish first"
                )
        elif progress["state"] == "complete":
            blockers.append(f"blueprint {blueprint} is complete; nothing is left to run")
        elif not progress["missing_inputs"]:
            blockers.append(f"blueprint {blueprint} has no ready phase")
        matched = selection["skills"] if selection else []
    else:
        matched = match(root, task)
        if _needs_research(task):
            research = next((s for s in discover(root) if s["name"] == "research-first-engineering"), None)
            if research and research["name"] not in {s["name"] for s in matched}:
                matched.insert(0, research)
        if not matched:
            matched = [{"name": "software-architect", "path": "skills/software-architect/SKILL.md", "purpose": "Clarify architecture and implementation boundaries.", "triggers": "ambiguous engineering tasks"}]

    regression = analyze_regression_risk(root, task)
    if not blueprint:
        # A blueprint phase is an explicit decision about who works now; QA and
        # security have their own phases there, so nothing is swapped in.
        matched = _prioritize_regression_workers(matched, regression, discover(root))

    workers = []
    for index, skill in enumerate(matched[:MAX_ACTIVE_WORKERS], start=1):
        worker = {
            "id": _id(task, skill["name"], index),
            "role": "SD1",
            "skill": skill["name"],
            "phase": selection["phase"]["id"] if selection else _phase(skill["name"]),
            "objective": f"Execute the {skill['name']} work required by: {task}",
            "inputs": {"task": task, "context": context},
            "outputs": ["implementation", "verification-evidence", "risks", "handoff"],
            "status": "blocked" if blockers else "ready",
        }
        for key in ("consumes", "produces"):
            if skill.get(key):
                worker[key] = list(skill[key])
        if story_record:
            worker["inputs"]["story"] = story_record["id"]
            worker["outputs"].append("acceptance-evidence")
        workers.append(worker)

    if selection:
        by_skill = {w["skill"]: w["id"] for w in workers}
        for worker in workers:
            worker["depends_on"] = [by_skill[name] for name in selection["depends_on"].get(worker["skill"], []) if name in by_skill]
    else:
        foundation = [w["id"] for w in workers if w["phase"] == "foundation"]
        implementation = [w["id"] for w in workers if w["phase"] in {"foundation", "implementation", "delivery"}]
        for worker in workers:
            if worker["phase"] in {"implementation", "delivery"}:
                worker["depends_on"] = foundation.copy()
            elif worker["phase"] == "verification":
                worker["depends_on"] = [x for x in implementation if x != worker["id"]]
            else:
                worker["depends_on"] = []

    draft = {
        "plan_id": hashlib.sha1(f"{task}:{time.time_ns()}".encode()).hexdigest()[:12],
        "role": "SD2",
        "task": task,
        "max_active_workers": MAX_ACTIVE_WORKERS,
        "context": context,
        "workers": workers,
        "preflight": {"research_first": _needs_research(task), "rule": "research before custom implementation when existing solutions may exist"},
        "regression": regression,
        "supervisor_gate": {"role": "SD3", "required": True, "checks": ["requirements", "architecture", "integration", "tests", "security", "evidence", "agent-evaluation", "regression"], "decision": "pending-runtime-agent-review"},
        "policy": {
            "parallelize": True,
            "do_not_exceed_worker_limit": True,
            "no_blind_retries": True,
            "escalate_architectural_blockers": True,
            "evaluate_non_trivial_runs": True,
            "regression_aware": True,
        },
    }
    draft["blockers"] = blockers
    if progress:
        draft["blueprint"] = {
            "name": progress["blueprint"],
            "state": progress["state"],
            "current_phase": progress["current_phase"],
            "ready_phases": progress["ready_phases"],
            "exit_artifacts": selection["phase"].get("produces", []) if selection else [],
            "deferred_skills": selection["deferred"] if selection else [],
            "skipped_for_platform": selection["skipped_for_platform"] if selection else [],
        }
        if selection and selection["phase"].get("approval") == "owner":
            draft["supervisor_gate"]["owner_approval_required"] = True
    if story_record:
        draft["story"] = {
            "id": story_record["id"],
            "title": story_record["title"],
            "path": story_record["path"],
            "status": story_record["status"],
            "platforms": story_record["platforms"],
            "depends_on": story_record["depends_on"],
            "brief": story_registry.brief(story_record),
        }
        draft["supervisor_gate"]["checks"].append("acceptance-traceability")
        draft["supervisor_gate"]["acceptance_criteria"] = story_record["criteria"]
    draft["intelligence"] = build_intelligence(root, task, draft)
    return draft


def write_plan(root: str | Path, task: str, blueprint: str | None = None, story: str | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    result = plan(root, task, blueprint=blueprint, story=story)
    out = root / ".e2e" / "plans"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{result['plan_id']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    result["plan_path"] = path.relative_to(root).as_posix()
    return result
