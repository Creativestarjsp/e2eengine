"""Skill registry: discovery, parsing and task matching.

A skill document states both what it is for and what it is *not* for. Matching
reads both, so two specialists that explicitly exclude each other never end up
in the same plan.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .project import skills_paths, skills_source

#: Headings whose body is an exclusion rather than a trigger.
_EXCLUSION_HEADINGS = ("when not to use", "do not use", "when not to use it", "not for")

#: Sentence openers that flip an otherwise-positive sentence into an exclusion.
#: Without this, "Do not use ... for backend APIs" scores *positively* for the
#: word "backend" on a frontend skill.
_NEGATION = re.compile(
    r"^\s*(?:do not use|don't use|do not apply|never use|avoid using|not for|not a substitute)\b",
    re.IGNORECASE,
)

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_TERM = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")

#: Weight of a task term that only matches a skill's soft boundary text.
EXCLUSION_PENALTY = 2

#: Skill documents draw two different kinds of line, and they mean different
#: things for routing:
#:
#:   "Do not use as the primary skill for Expo-only workflows"  -> disqualifying
#:   "Do not use as a substitute for frontend implementation"   -> boundary
#:
#: The first says this skill is the wrong tool for that technology. The second
#: says two complementary skills own different parts of the same job, which is
#: not a reason to drop either of them.
_BOUNDARY = re.compile(r"\b(?:substitute|replacement|stand-in)\s+for\b|\breplace\b", re.IGNORECASE)


def _strip_frontmatter(text: str) -> tuple[str, dict[str, str]]:
    """Split YAML frontmatter from the body, without a YAML dependency."""
    match = _FRONTMATTER.match(text)
    if not match:
        return text, {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return text[match.end():], meta


def _section(text: str, headings: tuple[str, ...]) -> str:
    lines = text.splitlines()
    wanted = {h.lower() for h in headings}
    for i, line in enumerate(lines):
        if line.strip().lower().lstrip("# ") in wanted:
            out = []
            for x in lines[i + 1:]:
                if x.startswith("#"):
                    break
                out.append(x)
            return "\n".join(out).strip()
    return ""


def _split_directives(text: str) -> tuple[str, str]:
    """Partition prose into (what this is for, what this is not for).

    Sentences are cheap to split on and skill documents are written in them, so
    a single "Do not use ..." sentence inside a Use-When section is separated
    out rather than counted as a trigger.
    """
    positive: list[str] = []
    negative: list[str] = []
    for chunk in re.split(r"(?<=[.!?])\s+|\n", text):
        piece = chunk.strip(" -*\t")
        if not piece:
            continue
        (negative if _NEGATION.match(piece) else positive).append(piece)
    return " ".join(positive), " ".join(negative)


def _classify_exclusions(text: str) -> tuple[str, str]:
    """Split exclusion prose into (disqualifying, complementary-boundary)."""
    disqualifying: list[str] = []
    boundary: list[str] = []
    for chunk in re.split(r"(?<=[.!?])\s+|\n", text):
        piece = chunk.strip(" -*\t")
        if not piece:
            continue
        (boundary if _BOUNDARY.search(piece) else disqualifying).append(piece)
    return " ".join(disqualifying), " ".join(boundary)


def _parse(path: Path, root: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    body, meta = _strip_frontmatter(raw)

    purpose_pos, purpose_neg = _split_directives(_section(body, ("Purpose",)))
    trigger_pos, trigger_neg = _split_directives(_section(body, ("Use When", "When to Use", "Triggers")))
    described_pos, described_neg = _split_directives(meta.get("description", ""))
    excluded = _section(body, _EXCLUSION_HEADINGS)
    exclusion_text = " ".join(x for x in (excluded, purpose_neg, trigger_neg, described_neg) if x)
    disqualifying, boundary = _classify_exclusions(exclusion_text)

    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.as_posix()

    return {
        "name": meta.get("name") or path.parent.name,
        "path": rel,
        "description": meta.get("description", ""),
        "purpose": purpose_pos[:800],
        "triggers": trigger_pos[:1200],
        "exclusions": exclusion_text[:1200],
        "disqualifying": disqualifying[:1200],
        "has_frontmatter": bool(meta),
        "size": len(raw),
        # Kept separate so scoring never treats an exclusion as a trigger.
        "_positive": " ".join((path.parent.name.replace("-", " "), described_pos, purpose_pos, trigger_pos)).lower(),
    }


def discover(root: str | Path = ".") -> list[dict[str, Any]]:
    """All skills visible to this project, deduplicated by name.

    Searches every directory from :func:`e2e.project.skills_paths`, earlier
    paths winning, so a project can override a vendored skill without editing it.
    """
    root = Path(root).resolve()
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for base in skills_paths(root):
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*/SKILL.md")):
            skill = _parse(path, root)
            if skill["name"] in seen:
                continue
            seen.add(skill["name"])
            result.append(skill)
    return sorted(result, key=lambda s: s["name"])


def diagnose(root: str | Path = ".") -> dict[str, Any]:
    """Explain what the registry found, and why it found nothing when it does.

    An empty registry is almost always a misconfigured path, so it must never
    look the same as a project that legitimately has no skills.
    """
    root = Path(root).resolve()
    searched = skills_paths(root)
    skills = discover(root)
    missing = [p.as_posix() for p in searched if not p.is_dir()]
    warnings: list[str] = []
    if not skills:
        warnings.append(
            "No skills found. Searched: "
            + ", ".join(p.as_posix() for p in searched)
            + ". Run `e2e init --skills-path <dir>` or set E2E_SKILLS_PATH."
        )
    without_frontmatter = [s["name"] for s in skills if not s["has_frontmatter"]]
    if without_frontmatter:
        warnings.append(
            f"{len(without_frontmatter)} skill(s) lack YAML frontmatter and will not load "
            f"in runtimes that require it: {', '.join(without_frontmatter[:5])}"
        )
    return {
        "count": len(skills),
        "source": skills_source(root),
        "searched": [p.as_posix() for p in searched],
        "missing_paths": missing,
        "skills": [s["name"] for s in skills],
        "warnings": warnings,
    }


#: Words that appear in nearly every skill document, so matching on them
#: measures nothing but sentence length. Without this, "add the new feature"
#: scores against all thirty skills roughly equally.
_STOPWORDS = frozenset("""
and are but for from has have how into its not the that this those was were with
you your use used uses using add adds new all any can its our out per via when
where which while who why work works task tasks make makes made need needs
""".split())


def _terms(task: str) -> set[str]:
    return {w.lower() for w in _TERM.findall(task)} - _STOPWORDS


def match(root: str | Path, task: str, limit: int = 8) -> list[dict[str, Any]]:
    """Rank skills for a task, respecting each skill's stated exclusions.

    Scoring:

    * ``+1`` per task term found in the skill's name, description, purpose or
      triggers, and ``+5`` when the task names the skill outright.
    * ``-2`` per task term that only appears in the skill's soft boundary text.
    * A skill is dropped when a task term appears in its *disqualifying* prose
      and nowhere in its positive text. A document that says "not for Expo-only
      workflows" is stating it is the wrong tool for an Expo task, and no amount
      of shared "react"/"native" vocabulary should override that.

    Exclusions demote rather than eliminate. Skill documents say things like
    "not a substitute for frontend implementation", which marks a boundary
    between complementary skills rather than a contradiction, so a hard filter
    would drop skills that genuinely belong in the plan.
    """
    skills = discover(root)
    terms = _terms(task)
    lowered = task.lower()

    scored: list[tuple[int, dict[str, Any]]] = []
    for skill in skills:
        positive = skill["_positive"]
        disqualifying = skill["disqualifying"].lower()
        boundary = skill["exclusions"].lower()

        hits = {t for t in terms if t in positive}
        if any(t in disqualifying and t not in positive for t in terms):
            continue
        excluded_only = {t for t in terms if t in boundary and t not in positive}

        score = len(hits) - (EXCLUSION_PENALTY * len(excluded_only))
        if skill["name"].replace("-", " ") in lowered:
            score += 5
        if score > 0:
            scored.append((score, skill))

    ranked = [s for _, s in sorted(scored, key=lambda x: (-x[0], x[1]["name"]))][:limit]
    return [{k: v for k, v in s.items() if not k.startswith("_")} for s in ranked]
