"""The UX laws skill must stay complete, route on UX review work, and be reachable from the skills that build UI."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from e2e.skills import discover, match

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ux-laws"
UI_SKILLS = ("ui-ux-designer", "frontend-developer", "react-js-developer", "expo-developer", "react-native-cli-developer")


def test_skill_is_registered():
    skill = next(s for s in discover(ROOT) if s["name"] == "ux-laws")
    assert skill["has_frontmatter"] and "Fitts" in skill["description"]


def test_all_twenty_two_laws_are_in_the_reference():
    text = (SKILL / "references" / "ux-laws.md").read_text(encoding="utf-8")
    numbers = sorted(int(n) for n in re.findall(r"^### (\d+)\. ", text, re.MULTILINE))
    assert numbers == list(range(1, 23))
    for law in ("Fitts", "Hick", "Jakob", "Miller", "Doherty", "Tesler", "Postel", "Zeigarnik", "Occam", "Pareto", "Parkinson"):
        assert law in text, law


def test_cited_files_exist():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    cited = set(re.findall(r"`((?:references|examples)/[\w./-]+\.md)`", text))
    assert cited == {"references/ux-laws.md", "references/platform-and-accessibility.md", "examples/review-example.md"}
    for rel in cited:
        assert (SKILL / rel).is_file(), rel


def test_example_follows_the_report_format_it_teaches():
    example = (SKILL / "examples" / "review-example.md").read_text(encoding="utf-8")
    for heading in ("### UX Score", "### Problems", "### Not Assessed"):
        assert heading in example
    for dimension in ("Usability", "Clarity", "Navigation", "Accessibility", "Responsiveness", "Visual hierarchy", "Performance perception"):
        assert f"- {dimension}:" in example
    # The skill forbids scoring what was not inspected; the example must obey.
    assert "Responsiveness: not assessed" in example
    assert example.count("- Principle:") == example.count("- Fix:")


def test_ui_building_skills_point_at_the_laws():
    for name in UI_SKILLS:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "skills/ux-laws/references/ux-laws.md" in text, name


@pytest.mark.parametrize(
    "task",
    [
        "review the UX of the checkout screen",
        "do a usability audit of the dashboard",
        "check this design against UX laws",
        "reduce cognitive load on the settings page",
    ],
)
def test_routes_on_ux_review_work(task: str):
    assert match(ROOT, task)[0]["name"] == "ux-laws", task


def test_does_not_take_over_other_review_or_design_work():
    assert "ux-laws" not in [s["name"] for s in match(ROOT, "review authentication code for XSS and injection")]
    assert "ux-laws" not in [s["name"] for s in match(ROOT, "review this pull request")]
    assert match(ROOT, "design the onboarding flow and visual system")[0]["name"] == "ui-ux-designer"
