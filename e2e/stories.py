"""User stories: the unit of feature work between a PRD and a verified change.

A story file states who wants what, the acceptance criteria that define done,
and the evidence that proves each criterion. SD2 orders stories by their
dependencies; SD3 approves a story only when every criterion has evidence.
The format is deliberately plain Markdown so a person can write one by hand.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

STORIES_DIR = "stories"
VALID_STATUS = ("todo", "in-progress", "done")

_TITLE = re.compile(r"^#\s+(STORY-\d+)\s*[:—-]\s*(.+?)\s*$")
_FIELD = re.compile(r"^(status|platforms|depends on)\s*:\s*(.*)$", re.IGNORECASE)
_CRITERION = re.compile(r"^\s*[-*]\s+(AC\d+)\s*:\s*(.*)$")
_STORY_REF = re.compile(r"STORY-\d+")
_NARRATIVE = re.compile(r"\bas an?\b.+\bi want\b", re.IGNORECASE | re.DOTALL)

#: Evidence cells that say "nothing here yet". A done story must not hide
#: behind one of these.
_PLACEHOLDERS = {"", "-", "tbd", "todo", "n/a", "na", "none", "pending"}


def _number(story_id: str) -> int:
    return int(story_id.split("-")[1])


def _has_evidence(text: str) -> bool:
    cleaned = text.strip().strip("()").strip().lower()
    return cleaned not in _PLACEHOLDERS


def parse(path: Path, root: Path | None = None) -> dict[str, Any]:
    """Parse one story file. Problems are recorded on the story, never raised."""
    text = path.read_text(encoding="utf-8", errors="replace")
    story: dict[str, Any] = {
        "id": "",
        "title": "",
        "path": path.relative_to(root).as_posix() if root else path.as_posix(),
        "status": "",
        "platforms": [],
        "depends_on": [],
        "criteria": [],
        "evidence": {},
        "has_narrative": bool(_NARRATIVE.search(text)),
        "problems": [],
    }
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not story["id"]:
            title = _TITLE.match(line)
            if title:
                story["id"], story["title"] = title.group(1), title.group(2)
                continue
        if not section:
            field = _FIELD.match(line.strip())
            if field:
                key, value = field.group(1).lower(), field.group(2).strip()
                if key == "status":
                    story["status"] = value.lower()
                elif key == "platforms":
                    story["platforms"] = [p.strip().lower() for p in value.split(",") if p.strip()]
                else:
                    story["depends_on"] = _STORY_REF.findall(value)
            continue
        criterion = _CRITERION.match(line)
        if not criterion:
            continue
        ac, body = criterion.group(1), criterion.group(2).strip()
        if section == "acceptance criteria":
            if any(c["id"] == ac for c in story["criteria"]):
                story["problems"].append(f"duplicate criterion {ac}")
            elif not body:
                story["problems"].append(f"{ac} has no text")
            else:
                story["criteria"].append({"id": ac, "text": body})
        elif section == "evidence" and _has_evidence(body):
            story["evidence"][ac] = body

    if not story["id"]:
        story["problems"].append("missing `# STORY-<n>: <title>` heading")
    return story


def load(root: str | Path = ".", directory: str = STORIES_DIR) -> list[dict[str, Any]]:
    """Every story under ``<root>/<directory>``, ordered by story number."""
    root = Path(root).resolve()
    base = root / directory
    if not base.is_dir():
        return []
    stories = [parse(path, root) for path in sorted(base.glob("*.md")) if path.name.upper().startswith("STORY-")]
    return sorted(stories, key=lambda s: (_number(s["id"]) if s["id"] else 10**9, s["path"]))


def get(root: str | Path, story_id: str, directory: str = STORIES_DIR) -> dict[str, Any]:
    wanted = story_id.strip().upper()
    for story in load(root, directory):
        if story["id"] == wanted:
            return story
    raise ValueError(f"story {wanted} not found in {directory}/")


def order(stories: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Dependency order as ``(ordered ids, ids stuck in a cycle)``."""
    known = {s["id"] for s in stories if s["id"]}
    pending = {s["id"]: {d for d in s["depends_on"] if d in known} for s in stories if s["id"]}
    ordered: list[str] = []
    while pending:
        free = sorted((sid for sid, deps in pending.items() if not deps), key=_number)
        if not free:
            return ordered, sorted(pending, key=_number)
        for sid in free:
            ordered.append(sid)
            del pending[sid]
        for deps in pending.values():
            deps.difference_update(free)
    return ordered, []


def unmet_dependencies(story: dict[str, Any], stories: list[dict[str, Any]]) -> list[str]:
    """Dependencies of ``story`` that are missing or not yet done."""
    by_id = {s["id"]: s for s in stories}
    return [d for d in story["depends_on"] if by_id.get(d, {}).get("status") != "done"]


def ready(root: str | Path = ".", directory: str = STORIES_DIR) -> list[dict[str, Any]]:
    """Stories that can be worked on now: not done, with every dependency done."""
    stories = load(root, directory)
    sequence, _ = order(stories)
    by_id = {s["id"]: s for s in stories}
    return [
        by_id[sid]
        for sid in sequence
        if by_id[sid]["status"] != "done" and not unmet_dependencies(by_id[sid], stories)
    ]


def check(root: str | Path = ".", directory: str = STORIES_DIR) -> dict[str, Any]:
    """Validate the story set. ``fail`` means a story cannot be trusted as written."""
    root = Path(root).resolve()
    stories = load(root, directory)
    errors: list[str] = []
    warnings: list[str] = []
    if not (root / directory).is_dir():
        errors.append(f"{directory}/ not found; copy templates/STORY.md to {directory}/STORY-001-<slug>.md")
    elif not stories:
        errors.append(f"{directory}/ contains no STORY-*.md files")

    seen: dict[str, str] = {}
    by_id = {s["id"]: s for s in stories if s["id"]}
    for story in stories:
        label = story["id"] or story["path"]
        errors.extend(f"{label}: {problem}" for problem in story["problems"])
        if not story["id"]:
            continue
        if story["id"] in seen:
            errors.append(f"{label}: duplicate id, also in {seen[story['id']]}")
        seen.setdefault(story["id"], story["path"])
        if story["status"] not in VALID_STATUS:
            errors.append(f"{label}: Status `{story['status'] or '<missing>'}` not in {list(VALID_STATUS)}")
        if not story["criteria"]:
            errors.append(f"{label}: no acceptance criteria")
        criteria_ids = {c["id"] for c in story["criteria"]}
        for ac in sorted(set(story["evidence"]) - criteria_ids):
            errors.append(f"{label}: evidence for unknown criterion {ac}")
        for dep in story["depends_on"]:
            if dep == story["id"]:
                errors.append(f"{label}: depends on itself")
            elif dep not in by_id:
                errors.append(f"{label}: depends on unknown story {dep}")
        if story["status"] == "done":
            missing = [c["id"] for c in story["criteria"] if c["id"] not in story["evidence"]]
            if missing:
                errors.append(f"{label}: done without evidence for {', '.join(missing)}")
            open_deps = [d for d in story["depends_on"] if d in by_id and by_id[d]["status"] != "done"]
            if open_deps:
                errors.append(f"{label}: done but depends on unfinished {', '.join(open_deps)}")
        if not story["has_narrative"]:
            warnings.append(f"{label}: no `As a ..., I want ...` statement")
        if not story["platforms"]:
            warnings.append(f"{label}: no Platforms line")

    sequence, cycle = order(stories)
    if cycle:
        errors.append("dependency cycle: " + ", ".join(cycle))

    summary = {status: sum(1 for s in stories if s["status"] == status) for status in VALID_STATUS}
    return {
        "status": "fail" if errors else "pass",
        "directory": directory,
        "count": len(stories),
        "summary": summary,
        "order": sequence,
        "errors": errors,
        "warnings": warnings,
    }


def brief(story: dict[str, Any]) -> str:
    """The story as an agent reads it: what to build and what proves it."""
    lines = [f"STORY {story['id']}: {story['title']}"]
    if story["platforms"]:
        lines.append("PLATFORMS: " + ", ".join(story["platforms"]))
    lines.append("ACCEPTANCE CRITERIA (each needs evidence before the story is done):")
    lines.extend(f"- {c['id']}: {c['text']}" for c in story["criteria"])
    return "\n".join(lines)
