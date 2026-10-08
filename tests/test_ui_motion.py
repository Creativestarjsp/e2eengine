"""Interface motion must honour reduced motion and stay off layout properties; the checker enforces the common cases."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from e2e.skills import discover, match

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ui-motion"

spec = importlib.util.spec_from_file_location("motion_check", SKILL / "scripts" / "motion_check.py")
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)


def project(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


GOOD_CSS = ":root{--motion-base:200ms}@media (prefers-reduced-motion: reduce){:root{--motion-base:0ms}}\n.b{transition: transform var(--motion-base), opacity var(--motion-base);}\n"


def test_shipped_examples_pass_cleanly():
    result = mc.run(SKILL / "examples")
    assert result["ok"] and result["warnings"] == [], result
    assert result["reduced_motion"] == "global"
    assert len(result["animating_files"]) == 3


def test_project_that_animates_without_reduced_motion_fails(tmp_path: Path):
    root = project(tmp_path, {"a.css": ".b{transition: transform 200ms;}\n"})
    result = mc.run(root)
    assert not result["ok"] and "handles reduced motion nowhere" in result["errors"][0]


def test_global_handling_covers_every_file(tmp_path: Path):
    root = project(tmp_path, {
        "tokens.css": GOOD_CSS,
        "App.tsx": 'import { motion } from "motion/react";\nexport const A = () => <motion.div animate={{ opacity: 1 }} transition={{ duration: 0.2 }} />;\n',
    })
    result = mc.run(root)
    assert result["ok"] and result["warnings"] == [] and result["reduced_motion"] == "global"


def test_only_local_handling_warns_about_the_other_files(tmp_path: Path):
    root = project(tmp_path, {
        "Card.tsx": 'import { motion, useReducedMotion } from "motion/react";\nconst r = useReducedMotion();\n',
        "Other.tsx": 'import { motion } from "motion/react";\nexport const O = () => <motion.div animate={{ x: 10 }} />;\n',
    })
    result = mc.run(root)
    assert result["ok"] and result["reduced_motion"] == "local"
    assert result["warnings"] == ["Other.tsx: animates without a reduced-motion branch, and the project has no app-level handling"]


@pytest.mark.parametrize(
    "name, text, expected, is_error",
    [
        ("a.css", GOOD_CSS + ".x{transition: all 200ms;}\n", "`transition: all`", True),
        ("a.css", GOOD_CSS + ".x{transition: height 200ms, opacity 200ms;}\n", "animates a layout property", False),
        ("a.css", GOOD_CSS + "@keyframes grow { from { width: 0 } to { width: 100px } }\n", "animates a layout property", False),
        ("a.css", GOOD_CSS + ".x{transition: transform 1.2s;}\n", "1200 ms is long", False),
        ("a.css", GOOD_CSS + ".x{animation: spin 1s linear infinite;}\n", "infinite motion", False),
        ("A.tsx", 'import { motion } from "motion/react";\nconst r = useReducedMotion();\n<motion.div animate={{ height: 200 }} />\n', "animates a layout property", False),
        ("A.tsx", 'import { motion } from "motion/react";\nconst r = useReducedMotion();\n<motion.div transition={{ duration: 2 }} />\n', "duration 2s is long", False),
        ("A.tsx", 'import { motion } from "motion/react";\nconst r = useReducedMotion();\n<motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity }} />\n', "infinite motion", False),
        ("A.tsx", 'import { motion, useReducedMotion } from "framer-motion";\n', "imports `framer-motion`", False),
        ("N.tsx", 'import Animated, { withTiming, useReducedMotion } from "react-native-reanimated";\nh.value = withTiming(200, { duration: 900 });\nconst s = useAnimatedStyle(() => ({ height: h.value }));\n', "900 ms is long", False),
        ("N.tsx", 'import Animated, { withTiming, useReducedMotion } from "react-native-reanimated";\nconst s = useAnimatedStyle(() => ({ height: h.value }));\n', "animates a layout property", False),
        ("N.tsx", 'import Animated, { withRepeat, useReducedMotion } from "react-native-reanimated";\nr.value = withRepeat(withTiming(1), -1);\n', "infinite motion", False),
    ],
)
def test_findings(tmp_path: Path, name: str, text: str, expected: str, is_error: bool):
    result = mc.run(project(tmp_path, {name: text}))
    bucket = result["errors"] if is_error else result["warnings"]
    assert any(expected in item for item in bucket), result


def test_skips_dependencies_build_output_and_tests(tmp_path: Path):
    root = project(tmp_path, {
        "node_modules/lib/x.css": ".b{transition: all 1s;}\n",
        "dist/x.css": ".b{transition: all 1s;}\n",
        "src/a.test.tsx": 'import { motion } from "framer-motion";\n',
        "src/ok.css": GOOD_CSS,
    })
    result = mc.run(root)
    assert result["ok"] and result["warnings"] == [] and result["files"] == 1


def test_cli_exit_codes(tmp_path: Path, capsys):
    root = project(tmp_path, {"a.css": GOOD_CSS + ".x{transition: transform 1.2s;}\n"})
    assert mc.main(["--root", str(root)]) == 0
    assert mc.main(["--root", str(root), "--strict"]) == 1
    capsys.readouterr()
    assert mc.main(["--root", str(root), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] and report["reduced_motion"] == "global" and len(report["warnings"]) == 1
    assert mc.main([str(root / "absent.css")]) == 1


# --- skill, references, pointers -------------------------------------------


def test_skill_is_registered_and_cites_existing_files():
    skill = next(s for s in discover(ROOT) if s["name"] == "ui-motion")
    assert skill["has_frontmatter"]
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for rel in set(re.findall(r"`((?:references|examples)/[\w./-]+\.\w+)`", text)):
        assert (SKILL / rel).is_file(), rel
    for rel in set(re.findall(r"python (skills/[\w./-]+\.py)", text)):
        assert (ROOT / rel).is_file(), rel
    for name in ("choosing-the-tool.md", "motion-tokens.md", "web-motion.md", "native-motion.md"):
        assert (SKILL / "references" / name).is_file(), name


def test_examples_use_current_packages_and_honour_reduced_motion():
    web = (SKILL / "examples" / "web" / "ExpandableCard.tsx").read_text(encoding="utf-8")
    native = (SKILL / "examples" / "native" / "PressableScale.tsx").read_text(encoding="utf-8")
    assert 'from "motion/react"' in web and "useReducedMotion" in web and "framer-motion" not in web
    assert 'from "react-native-reanimated"' in native and "useReducedMotion" in native
    assert "prefers-reduced-motion" in (SKILL / "examples" / "web" / "transitions.css").read_text(encoding="utf-8")


def test_design_template_and_neighbours_point_here():
    assert "## Motion" in (ROOT / "templates" / "DESIGN.md").read_text(encoding="utf-8")
    assert "`ui-motion`" in (ROOT / "skills" / "lottie-animation" / "SKILL.md").read_text(encoding="utf-8")
    assert "`ui-motion`" in (ROOT / "skills" / "ui-ux-designer" / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("task", ["add a slide-up transition for the filters sheet", "the hover animation on the cards feels janky", "swipe to dismiss a notification with Reanimated", "page transitions between routes with Motion"])
def test_routes_on_motion_work(task: str):
    assert match(ROOT, task)[0]["name"] == "ui-motion", [s["name"] for s in match(ROOT, task)[:3]]


def test_stays_out_of_unrelated_work():
    for task in ("build a login API endpoint", "create an empty state illustration for the projects list", "deploy the app to production", "design the database schema for orders", "add a settings page", "optimize a slow SQL query"):
        assert "ui-motion" not in [s["name"] for s in match(ROOT, task)[:2]], task
    # Canned animation belongs to lottie-animation even though both skills speak of animation.
    for task in ("add a loading spinner animation", "animate the payment success state"):
        assert match(ROOT, task)[0]["name"] == "lottie-animation", task
