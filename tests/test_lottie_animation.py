"""The Lottie skill wraps a vendored upstream skill; our checker and renderer are what make its output trustworthy."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from e2e.skills import discover, match

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "lottie-animation"
VENDOR = SKILL / "vendor" / "text-to-lottie"
EXAMPLES = sorted((SKILL / "examples").glob("*/lottie.json"))

spec = importlib.util.spec_from_file_location("lottie_check", SKILL / "scripts" / "lottie_check.py")
lottie_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lottie_check)

BASE = {"v": "5.12.2", "fr": 60, "ip": 0, "op": 30, "w": 100, "h": 100, "nm": "t", "assets": [], "layers": []}


def write(tmp_path: Path, doc: dict, name: str = "lottie.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


# --- checker ----------------------------------------------------------------


def test_shipped_examples_pass_cleanly():
    assert len(EXAMPLES) == 2
    for example in EXAMPLES:
        errors, warnings, info = lottie_check.check(example)
        assert errors == [] and warnings == [], (example, errors, warnings)
        assert info["slots"] >= 1 and info["bytes"] < 20_000


@pytest.mark.parametrize(
    "doc, expected",
    [
        ({**BASE, "layers": [{"ty": 4, "shapes": [{"ty": "fl", "c": {"a": 0, "k": [1, 0, 0, 1], "sid": "ghost"}}]}]}, "references slot `ghost` which is not defined"),
        ({**BASE, "layers": [{"ty": 4, "ks": {"o": {"a": 1, "k": [{"t": 10, "s": [0]}, {"t": 5, "s": [100]}]}}}]}, "keyframes are not in ascending time order"),
        ({**BASE, "assets": [{"id": "i", "u": "https://cdn.example.com/", "p": "a.png"}]}, "remote asset"),
        ({**BASE, "assets": [{"id": "i", "p": "data:image/png;base64,AAAA", "e": 1}]}, "embedded data-URI image"),
        ({**BASE, "assets": [{"id": "i", "p": "logo.png"}]}, "`logo.png` not found beside the JSON"),
        ({**BASE, "layers": [{"ty": 5, "t": {"d": {"k": []}}}]}, "text layer without a declared font"),
        ({**BASE, "fonts": {"list": [{"fName": "Inter", "fFamily": "Inter"}]}}, "no .ttf/.otf/.ttc file sits beside the JSON"),
        ({**BASE, "op": 0}, "op must be greater than ip"),
        ({k: v for k, v in BASE.items() if k != "layers"}, "missing top-level keys: layers"),
    ],
)
def test_errors(tmp_path: Path, doc: dict, expected: str):
    errors, _, _ = lottie_check.check(write(tmp_path, doc))
    assert any(expected in e for e in errors), errors


def test_local_assets_and_fonts_are_accepted(tmp_path: Path):
    (tmp_path / "logo.png").write_bytes(b"png")
    (tmp_path / "Inter.ttf").write_bytes(b"font")
    doc = {**BASE, "assets": [{"id": "i", "p": "logo.png"}], "fonts": {"list": [{"fName": "Inter", "fFamily": "Inter"}]}, "layers": [{"ty": 5, "t": {"d": {"k": []}}}]}
    assert lottie_check.check(write(tmp_path, doc))[0] == []


def test_warnings_and_budget(tmp_path: Path):
    doc = {**BASE, "fr": 12, "op": 200, "nm": "", "slots": {"unused": {"p": {"a": 0, "k": 1}}}, "layers": [{"ty": 4, "ks": {"o": {"a": 0, "k": 100, "x": "var $bm_rt = 50;"}}}]}
    errors, warnings, _ = lottie_check.check(write(tmp_path, doc))
    joined = " | ".join(warnings)
    assert errors == []
    for expected in ("frame rate 12", "duration 16.7s", "no top-level `nm`", "slot `unused` is defined but never referenced", "expression"):
        assert expected in joined, expected
    assert any("exceeds the budget of 50" in e for e in lottie_check.check(write(tmp_path, BASE), max_bytes=50)[0])


def test_cli_exit_codes(tmp_path: Path, capsys):
    good = write(tmp_path, BASE, "good.json")
    bad = write(tmp_path, {**BASE, "op": 0}, "bad.json")
    (tmp_path / "broken.json").write_text("{nope", encoding="utf-8")
    assert lottie_check.main([str(good)]) == 0
    assert lottie_check.main([str(good), str(bad), "--json"]) == 1
    out = capsys.readouterr().out
    assert json.loads(out[out.rindex('{\n  "ok"'):])["files"][1]["ok"] is False
    assert lottie_check.main([str(tmp_path / "broken.json")]) == 1
    warned = write(tmp_path, {**BASE, "nm": ""}, "warned.json")
    assert lottie_check.main([str(warned)]) == 0 and lottie_check.main([str(warned), "--strict"]) == 1


# --- renderer ---------------------------------------------------------------


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_preview_reports_honestly_without_canvaskit(tmp_path: Path):
    proc = subprocess.run(["node", str(SKILL / "scripts" / "lottie_preview.mjs"), str(EXAMPLES[0])], cwd=tmp_path, text=True, capture_output=True, timeout=60)
    assert proc.returncode == 2
    assert "NO RENDERER" in proc.stderr and "not been visually reviewed" in proc.stderr
    assert subprocess.run(["node", str(SKILL / "scripts" / "lottie_preview.mjs")], cwd=tmp_path, capture_output=True, timeout=60).returncode == 1


@pytest.mark.skipif(not os.environ.get("E2E_CANVASKIT_PROJECT"), reason="set E2E_CANVASKIT_PROJECT to a directory where canvaskit-wasm is installed")
def test_preview_renders_frames_with_canvaskit(tmp_path: Path):
    project = os.environ["E2E_CANVASKIT_PROJECT"]
    for example in EXAMPLES:
        proc = subprocess.run(["node", str(SKILL / "scripts" / "lottie_preview.mjs"), str(example), "--out", str(tmp_path / example.parent.name)], cwd=project, text=True, capture_output=True, timeout=120)
        assert proc.returncode == 0, proc.stderr
        frames = sorted((tmp_path / example.parent.name).glob("frame-*.png"))
        assert len(frames) == 5 and all(f.stat().st_size > 100 for f in frames)
        assert (tmp_path / example.parent.name / "preview.html").is_file()
    proc = subprocess.run(["node", str(SKILL / "scripts" / "lottie_preview.mjs"), str(EXAMPLES[0]), "--frames", "0,999", "--out", str(tmp_path / "bad")], cwd=project, text=True, capture_output=True, timeout=120)
    assert proc.returncode == 1 and "frames must be integers" in proc.stderr


# --- vendoring, registry, references ---------------------------------------


def test_upstream_is_vendored_unchanged_with_license_and_provenance():
    assert (VENDOR / "SKILL.md").is_file() and (VENDOR / "LICENSE").is_file()
    assert "MIT" in (VENDOR / "LICENSE").read_text(encoding="utf-8")
    assert (VENDOR / "references" / "player-contract.md").is_file() and (VENDOR / "references" / "recipe-loaders-icons.md").is_file()
    provenance = (SKILL / "vendor" / "VENDOR.md").read_text(encoding="utf-8")
    assert "github.com/diffusionstudio/lottie" in provenance and re.search(r"Commit: [0-9a-f]{40}", provenance)
    names = {s["name"] for s in discover(ROOT)}
    assert "lottie-animation" in names and "text-to-lottie" not in names


def test_cited_files_exist():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for rel in set(re.findall(r"`((?:references|examples|vendor)/[\w./-]+\.\w+)`", text)):
        assert (SKILL / rel).is_file(), rel
    for rel in set(re.findall(r"(?:python|node) (skills/[\w./-]+\.(?:py|mjs))", text)):
        assert (ROOT / rel).is_file(), rel


@pytest.mark.parametrize("task", ["add a loading spinner animation", "animate the payment success state", "check this Lottie file before it ships", "animated icon for the like button"])
def test_routes_on_animation_work(task: str):
    assert match(ROOT, task)[0]["name"] == "lottie-animation", [s["name"] for s in match(ROOT, task)[:3]]


def test_stays_out_of_unrelated_work():
    for task in ("debug the JSON parser", "edit the data chart on the dashboard", "build a login API endpoint", "create an empty state illustration for the projects list"):
        assert "lottie-animation" not in [s["name"] for s in match(ROOT, task)[:3]], task
