"""Stories are only useful if a `done` one can be trusted, so the checker is strict about evidence."""

from __future__ import annotations

from pathlib import Path

from e2e import stories

ROOT = Path(__file__).resolve().parents[1]


def write_story(root: Path, number: int, status: str = "todo", depends: str = "", criteria: int = 2,
                evidence: dict[int, str] | None = None, narrative: bool = True, platforms: str = "web") -> Path:
    folder = root / "stories"
    folder.mkdir(exist_ok=True)
    lines = [f"# STORY-{number:03d}: Feature {number}", "", f"Status: {status}", f"Platforms: {platforms}", f"Depends on: {depends}", ""]
    if narrative:
        lines += ["As a user, I want feature things, so that I benefit.", ""]
    lines += ["## Acceptance Criteria", ""] + [f"- AC{i}: outcome {i} is visible" for i in range(1, criteria + 1)]
    lines += ["", "## Evidence", ""] + [f"- AC{i}: {(evidence or {}).get(i, '')}".rstrip() for i in range(1, criteria + 1)]
    path = folder / f"STORY-{number:03d}-feature.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_shipped_examples_pass_and_only_the_unblocked_story_is_ready(tmp_path: Path):
    target = tmp_path / "stories"
    target.mkdir()
    for src in (ROOT / "skills" / "story-writer" / "examples").glob("STORY-*.md"):
        (target / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    result = stories.check(tmp_path)
    assert result["status"] == "pass", result["errors"]
    assert result["warnings"] == []
    assert result["order"] == ["STORY-001", "STORY-002", "STORY-003"]
    assert [s["id"] for s in stories.ready(tmp_path)] == ["STORY-002"]


def test_template_parses_as_a_valid_todo_story(tmp_path: Path):
    (tmp_path / "stories").mkdir()
    (tmp_path / "stories" / "STORY-001-new.md").write_text((ROOT / "templates" / "STORY.md").read_text(encoding="utf-8"), encoding="utf-8")
    result = stories.check(tmp_path)
    assert result["status"] == "pass", result["errors"]
    story = stories.get(tmp_path, "story-001")
    assert story["status"] == "todo" and story["platforms"] == ["web", "mobile"]
    assert [c["id"] for c in story["criteria"]] == ["AC1", "AC2"] and story["evidence"] == {}


def test_done_requires_evidence_for_every_criterion(tmp_path: Path):
    write_story(tmp_path, 1, status="done", evidence={1: "tests/a.py::test_one (pass)"})
    errors = stories.check(tmp_path)["errors"]
    assert errors == ["STORY-001: done without evidence for AC2"]


def test_placeholders_are_not_evidence(tmp_path: Path):
    write_story(tmp_path, 1, status="done", evidence={1: "TBD", 2: "(pending)"})
    assert "done without evidence for AC1, AC2" in stories.check(tmp_path)["errors"][0]


def test_done_story_cannot_rest_on_unfinished_dependency(tmp_path: Path):
    write_story(tmp_path, 1)
    write_story(tmp_path, 2, status="done", depends="STORY-001", evidence={1: "t (pass)", 2: "t (pass)"})
    assert "STORY-002: done but depends on unfinished STORY-001" in stories.check(tmp_path)["errors"]


def test_structural_problems_are_reported(tmp_path: Path):
    write_story(tmp_path, 1, status="shipped")
    write_story(tmp_path, 2, criteria=0)
    write_story(tmp_path, 3, depends="STORY-042")
    path = write_story(tmp_path, 4)
    path.write_text(path.read_text(encoding="utf-8") + "- AC9: tests (pass)\n", encoding="utf-8")
    (tmp_path / "stories" / "STORY-005-broken.md").write_text("no heading here\n", encoding="utf-8")
    errors = " | ".join(stories.check(tmp_path)["errors"])
    assert "STORY-001: Status `shipped`" in errors
    assert "STORY-002: no acceptance criteria" in errors
    assert "STORY-003: depends on unknown story STORY-042" in errors
    assert "STORY-004: evidence for unknown criterion AC9" in errors
    assert "missing `# STORY-<n>: <title>` heading" in errors


def test_duplicate_ids_and_cycles_fail(tmp_path: Path):
    write_story(tmp_path, 1, depends="STORY-002")
    write_story(tmp_path, 2, depends="STORY-001")
    copy = tmp_path / "stories" / "STORY-001-again.md"
    copy.write_text((tmp_path / "stories" / "STORY-001-feature.md").read_text(encoding="utf-8"), encoding="utf-8")
    result = stories.check(tmp_path)
    errors = " | ".join(result["errors"])
    assert "duplicate id" in errors
    assert "dependency cycle: STORY-001, STORY-002" in errors
    assert stories.ready(tmp_path) == []


def test_missing_directory_fails_and_weak_stories_warn(tmp_path: Path):
    assert stories.check(tmp_path)["status"] == "fail"
    write_story(tmp_path, 1, narrative=False, platforms="")
    result = stories.check(tmp_path)
    assert result["status"] == "pass"
    assert len(result["warnings"]) == 2


def test_brief_carries_the_acceptance_criteria(tmp_path: Path):
    write_story(tmp_path, 7, platforms="web, mobile")
    text = stories.brief(stories.get(tmp_path, "STORY-007"))
    assert "STORY-007" in text and "PLATFORMS: web, mobile" in text
    assert "- AC1: outcome 1 is visible" in text and "- AC2:" in text
