from __future__ import annotations

from pathlib import Path

import pytest

from e2e.project import SKILLS_PATH_ENV
from e2e.skills import diagnose, discover, match


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv(SKILLS_PATH_ENV, raising=False)


def write_skill(root: Path, name: str, body: str, description: str | None = None) -> Path:
    path = root / "skills" / name
    path.mkdir(parents=True, exist_ok=True)
    front = f'---\nname: {name}\ndescription: "{description}"\n---\n\n' if description else ""
    (path / "SKILL.md").write_text(front + body, encoding="utf-8")
    return path


EXPO = """# Expo

## Purpose
Build React Native applications using Expo.

## Use When
Use for Expo applications, Expo Router and Expo SDK APIs.

## When Not to Use
Do not use as the primary skill for bare React Native CLI projects.
"""

RN_CLI = """# React Native CLI

## Purpose
Build React Native applications using the React Native CLI workflow.

## Use When
Use for React Native CLI applications and native Android/iOS integration.

## When Not to Use
Do not use as the primary skill for Expo-only workflows.
"""

FRONTEND = """# Frontend

## Purpose
Build accessible frontend experiences.

## Use When
Use for component work and accessibility. Do not use as the primary skill for backend APIs.
"""

DESIGNER = """# Designer

## Purpose
Design product experiences.

## Use When
Use for screen design and visual direction. Do not use as a substitute for frontend implementation.
"""


def test_frontmatter_is_parsed(tmp_path: Path):
    write_skill(tmp_path, "expo-developer", EXPO, description="Ship Expo apps.")
    skill = discover(tmp_path)[0]
    assert skill["name"] == "expo-developer"
    assert skill["description"] == "Ship Expo apps."
    assert skill["has_frontmatter"]
    # Frontmatter must not leak into the parsed body sections.
    assert "---" not in skill["purpose"]


def test_exclusions_are_parsed_separately_from_triggers(tmp_path: Path):
    write_skill(tmp_path, "frontend-developer", FRONTEND)
    skill = discover(tmp_path)[0]
    assert "backend" in skill["exclusions"].lower()
    # The negated sentence must not count as a trigger, or "backend" scores
    # positively for a frontend skill.
    assert "backend" not in skill["triggers"].lower()


def test_backend_task_does_not_route_to_frontend_skill(tmp_path: Path):
    write_skill(tmp_path, "frontend-developer", FRONTEND)
    assert [s["name"] for s in match(tmp_path, "implement the backend APIs")] == []


def test_expo_task_excludes_the_bare_cli_skill(tmp_path: Path):
    write_skill(tmp_path, "expo-developer", EXPO)
    write_skill(tmp_path, "react-native-cli-developer", RN_CLI)

    names = [s["name"] for s in match(tmp_path, "build Expo Router screens in React Native")]

    assert names[0] == "expo-developer"
    assert "react-native-cli-developer" not in names


def test_bare_cli_task_excludes_the_expo_skill(tmp_path: Path):
    write_skill(tmp_path, "expo-developer", EXPO)
    write_skill(tmp_path, "react-native-cli-developer", RN_CLI)

    names = [s["name"] for s in match(tmp_path, "wire a native module into the React Native CLI project")]

    assert names[0] == "react-native-cli-developer"
    assert "expo-developer" not in names


def test_complementary_boundary_does_not_disqualify(tmp_path: Path):
    """"Not a substitute for X" marks a shared boundary, not a contradiction."""
    write_skill(tmp_path, "ui-ux-designer", DESIGNER)
    write_skill(tmp_path, "frontend-developer", FRONTEND)

    names = [s["name"] for s in match(tmp_path, "design the screen and visual direction")]

    assert "ui-ux-designer" in names


def test_stopwords_do_not_create_matches(tmp_path: Path):
    write_skill(tmp_path, "expo-developer", EXPO)
    assert match(tmp_path, "and the with for this that") == []


def test_discover_reads_configured_path(tmp_path: Path, monkeypatch):
    other = tmp_path / "elsewhere"
    skill = other / "skills" / "expo-developer"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(EXPO, encoding="utf-8")
    monkeypatch.setenv(SKILLS_PATH_ENV, str(other / "skills"))

    assert [s["name"] for s in discover(tmp_path)] == ["expo-developer"]


def test_diagnose_explains_an_empty_registry(tmp_path: Path):
    report = diagnose(tmp_path)
    assert report["count"] == 0
    assert report["warnings"]
    assert report["searched"]


def test_diagnose_flags_missing_frontmatter(tmp_path: Path):
    write_skill(tmp_path, "expo-developer", EXPO)
    report = diagnose(tmp_path)
    assert report["count"] == 1
    assert any("frontmatter" in w for w in report["warnings"])


def test_weak_matches_are_dropped_below_the_relevance_floor(tmp_path: Path):
    """SD2 turns matches into workers, so a marginal match must not qualify."""
    write_skill(tmp_path, "expo-developer", EXPO)
    write_skill(tmp_path, "designer", DESIGNER)
    write_skill(tmp_path, "frontend-developer", FRONTEND)

    names = [s["name"] for s in match(tmp_path, "Expo Router screens and Expo SDK APIs")]

    assert names == ["expo-developer"]


def test_common_terms_do_not_decide_routing(tmp_path: Path):
    """A word every skill uses carries no signal and must not score."""
    for name in ("alpha-developer", "beta-developer", "gamma-developer"):
        write_skill(
            tmp_path,
            name,
            f"# {name}\n\n## Purpose\nBuild software applications.\n\n## Use When\nUse for build work.\n",
        )
    write_skill(tmp_path, "expo-developer", EXPO)

    names = [s["name"] for s in match(tmp_path, "build an Expo application")]

    assert names[0] == "expo-developer"
