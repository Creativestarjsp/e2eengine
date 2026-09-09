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


def skills_source(root: str | Path = ".") -> str:
    """Where the skill paths came from: ``env:…``, ``config:…`` or ``default``."""
    return _configured_paths(Path(root).resolve())[1]


def init(
    root: str | Path = ".",
    skills: list[str] | None = None,
    force: bool = False,
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

    return {
        "status": "initialized",
        "root": str(root),
        "created": created,
        "existing": existing,
        "skills_paths": [p.as_posix() for p in skills_paths(root)],
        "skills_found": found,
        "missing_skills_paths": missing,
        "warnings": warnings,
    }
