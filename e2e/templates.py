"""Templates: the starting documents skills ask for, findable from any project.

Skills say "start from the STORY template". That only works if the template
can be found from wherever the engine is being used, so templates resolve like
skills do, and a skill's own ``templates/`` directory is searched too.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .project import skills_paths, template_paths


def list_templates(root: str | Path = ".") -> list[dict[str, Any]]:
    """Every template visible to the project. Earlier locations win on a name clash."""
    root = Path(root).resolve()
    sources: list[tuple[str, Path]] = [("templates", base) for base in template_paths(root)]
    for base in skills_paths(root):
        if base.is_dir():
            sources.extend((f"skill:{folder.parent.name}", folder) for folder in sorted(base.glob("*/templates")))
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source, base in sources:
        if not base.is_dir():
            continue
        for path in sorted(p for p in base.iterdir() if p.is_file() and not p.name.startswith(".")):
            if path.name.lower() in seen:
                continue
            seen.add(path.name.lower())
            found.append({"name": path.name, "source": source, "path": path.as_posix()})
    return sorted(found, key=lambda item: item["name"].lower())


def find(root: str | Path, name: str) -> dict[str, Any]:
    """Look a template up by file name or by its name without the extension."""
    wanted = name.strip().lower()
    templates = list_templates(root)
    matches = [t for t in templates if t["name"].lower() == wanted] or [t for t in templates if Path(t["name"]).stem.lower() == wanted]
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise ValueError(f"template {name} is ambiguous: {', '.join(m['name'] for m in matches)}")
    available = ", ".join(t["name"] for t in templates) or "none (set E2E_TEMPLATES_PATH or templates_paths in e2e.json)"
    raise ValueError(f"template {name} not found (available: {available})")


def copy(root: str | Path, name: str, destination: str | None = None) -> dict[str, Any]:
    """Copy a template into the project. Never overwrites, never writes outside the project."""
    root = Path(root).resolve()
    template = find(root, name)
    target = root / (destination or template["name"])
    if destination and (destination.endswith("/") or target.is_dir()):
        target = target / template["name"]
    target = target.resolve()
    if target != root and root not in target.parents:
        raise ValueError("destination is outside the project")
    if target.exists():
        raise ValueError(f"{target.relative_to(root).as_posix()} already exists; templates never overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(Path(template["path"]).read_text(encoding="utf-8"), encoding="utf-8")
    return {"template": template["name"], "source": template["source"], "written": target.relative_to(root).as_posix()}
