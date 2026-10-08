"""Project-level configuration for an E2E-managed repository.

`e2e init` writes the config this module reads. Everything that needs to know
where a project keeps its skills goes through :func:`skills_paths` so there is
one answer, and so a misconfigured project reports a diagnostic instead of
silently behaving as if it had no skills.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "e2e.json"
STATE_DIR = ".e2e"
SCHEMA_VERSION = 1

#: Searched in order when a project has no explicit configuration.
DEFAULT_SKILLS_PATHS = ("skills", ".e2e/skills")

#: Colon-separated paths, highest precedence. Mirrors PATH semantics.
SKILLS_PATH_ENV = "E2E_SKILLS_PATH"

#: Blueprints and templates ship beside the skills, and resolve the same way.
DEFAULT_BLUEPRINT_PATHS = ("workflows", ".e2e/workflows")
BLUEPRINTS_PATH_ENV = "E2E_BLUEPRINTS_PATH"
DEFAULT_TEMPLATE_PATHS = ("templates", ".e2e/templates")
TEMPLATES_PATH_ENV = "E2E_TEMPLATES_PATH"


def config_path(root: str | Path = ".") -> Path:
    return Path(root).resolve() / CONFIG_FILENAME


def load_config(root: str | Path = ".") -> dict[str, Any]:
    """Return the project config, or an empty mapping when absent/unreadable."""
    path = config_path(root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _configured_paths(root: Path) -> tuple[list[str], str]:
    """Resolve which skill directories to search, and say where that came from."""
    env = os.environ.get(SKILLS_PATH_ENV, "").strip()
    if env:
        return [p for p in env.split(os.pathsep) if p], f"env:{SKILLS_PATH_ENV}"

    configured = load_config(root).get("skills_paths")
    if isinstance(configured, list) and configured:
        return [str(p) for p in configured], f"config:{CONFIG_FILENAME}"

    return list(DEFAULT_SKILLS_PATHS), "default"


def skills_paths(root: str | Path = ".") -> list[Path]:
    """Absolute skill directories to search, in precedence order.

    Includes directories that do not exist; callers report them as diagnostics
    rather than silently treating a typo as "this project has no skills".
    """
    root = Path(root).resolve()
    raw, _ = _configured_paths(root)
    resolved: list[Path] = []
    for entry in raw:
        candidate = Path(entry)
        candidate = candidate if candidate.is_absolute() else root / candidate
        if candidate not in resolved:
            resolved.append(candidate)
    return resolved


def configured_paths(root: str | Path, config_key: str, env_name: str, defaults: tuple[str, ...]) -> list[Path]:
    """Resolve a list of search directories: environment, then config, then defaults."""
    root = Path(root).resolve()
    env = os.environ.get(env_name, "").strip()
    if env:
        raw = [p for p in env.split(os.pathsep) if p]
    else:
        configured = load_config(root).get(config_key)
        raw = [str(p) for p in configured] if isinstance(configured, list) and configured else list(defaults)
    resolved: list[Path] = []
    for entry in raw:
        candidate = Path(entry)
        candidate = candidate if candidate.is_absolute() else root / candidate
        if candidate not in resolved:
            resolved.append(candidate)
    return resolved


def blueprint_paths(root: str | Path = ".") -> list[Path]:
    return configured_paths(root, "blueprints_paths", BLUEPRINTS_PATH_ENV, DEFAULT_BLUEPRINT_PATHS)


def template_paths(root: str | Path = ".") -> list[Path]:
    return configured_paths(root, "templates_paths", TEMPLATES_PATH_ENV, DEFAULT_TEMPLATE_PATHS)


def _beside_skills(root: Path, skills: list[str], folder: str, defaults: tuple[str, ...]) -> list[str]:
    """Blueprints and templates normally live next to the skills directory.

    When a project points at skills elsewhere, look for the sibling folder so
    one flag is enough to adopt a shared skill library. The project's own
    folders stay first, so it can override a shared blueprint or template.
    """
    found: list[str] = []
    for entry in skills:
        sibling = Path(entry).parent / folder
        resolved = sibling if sibling.is_absolute() else root / sibling
        if resolved.is_dir() and sibling.as_posix() not in found and sibling.as_posix() not in defaults:
            found.append(sibling.as_posix())
    return list(defaults) + found


def skills_source(root: str | Path = ".") -> str:
    """Where the skill paths came from: ``env:…``, ``config:…`` or ``default``."""
    return _configured_paths(Path(root).resolve())[1]


def init(
    root: str | Path = ".",
    skills: list[str] | None = None,
    force: bool = False,
    blueprints: list[str] | None = None,
    templates: list[str] | None = None,
) -> dict[str, Any]:
    """Create the project scaffolding `e2e` expects, idempotently.

    Reports every path it created, left alone, or could not find, so a caller
    can tell the difference between "already set up" and "did nothing".
    """
    root = Path(root).resolve()
    created: list[str] = []
    existing: list[str] = []
    warnings: list[str] = []

    state = root / STATE_DIR
    (created if not state.exists() else existing).append(f"{STATE_DIR}/")
    state.mkdir(exist_ok=True)

    evals = state / "evals"
    (created if not evals.exists() else existing).append(f"{STATE_DIR}/evals/")
    evals.mkdir(exist_ok=True)

    requested = skills or list(DEFAULT_SKILLS_PATHS)
    config_file = config_path(root)
    if config_file.exists() and not force:
        existing.append(CONFIG_FILENAME)
    else:
        config = {
            "schema_version": SCHEMA_VERSION,
            "skills_paths": requested,
            "blueprints_paths": blueprints or _beside_skills(root, requested, "workflows", DEFAULT_BLUEPRINT_PATHS),
            "templates_paths": templates or _beside_skills(root, requested, "templates", DEFAULT_TEMPLATE_PATHS),
            "brain_store": f"{STATE_DIR}/brain.json",
        }
        config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        created.append(CONFIG_FILENAME)

    # Report skill coverage now, while the operator is looking at the output.
    found = 0
    missing: list[str] = []
    for path in skills_paths(root):
        if path.is_dir():
            found += len(list(path.glob("*/SKILL.md")))
        else:
            missing.append(path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path))
    if found == 0:
        warnings.append(
            "No SKILL.md files found. Searched: "
            + ", ".join(p.as_posix() for p in skills_paths(root))
            + f". Set {SKILLS_PATH_ENV} or edit skills_paths in {CONFIG_FILENAME}."
        )

    blueprints_found = sum(len(list(p.glob("*.json"))) for p in blueprint_paths(root) if p.is_dir())
    templates_found = sum(len(list(p.glob("*.md"))) for p in template_paths(root) if p.is_dir())
    notes: list[str] = []
    if blueprints_found == 0:
        notes.append(f"No blueprints found; `e2e blueprint list` will be empty. Use --blueprints-path or set {BLUEPRINTS_PATH_ENV}.")
    if templates_found == 0:
        notes.append(f"No templates found; `e2e template list` will be empty. Use --templates-path or set {TEMPLATES_PATH_ENV}.")

    return {
        "status": "initialized",
        "root": str(root),
        "created": created,
        "existing": existing,
        "skills_paths": [p.as_posix() for p in skills_paths(root)],
        "skills_found": found,
        "missing_skills_paths": missing,
        "blueprints_paths": [p.as_posix() for p in blueprint_paths(root)],
        "blueprints_found": blueprints_found,
        "templates_paths": [p.as_posix() for p in template_paths(root)],
        "templates_found": templates_found,
        "warnings": warnings,
        "notes": notes,
    }
