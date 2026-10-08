#!/usr/bin/env python3
"""Find the common motion mistakes in a project's source: static, pattern-based.

Errors (exit 1):
  - the project animates something but handles reduced motion nowhere
    (no `prefers-reduced-motion`, `useReducedMotion`, `MotionConfig reducedMotion`,
    `ReduceMotion`, or `isReduceMotionEnabled` anywhere)
  - `transition: all` in CSS

Warnings:
  - layout properties animated (width, height, top, left, right, bottom, margin, padding)
    in CSS transitions/keyframes, Motion `animate`/`whileHover`/`whileTap`, or Reanimated styles
  - durations longer than 500 ms in functional motion (CSS, Motion `duration` in seconds,
    Reanimated `withTiming` in milliseconds)
  - infinite motion (`repeat: Infinity`, `infinite`, `withRepeat(..., -1)`)
  - imports from `framer-motion` (the current package is `motion`)
  - a file that animates without a local reduced-motion branch, when the project has
    no app-level handling (`MotionConfig reducedMotion` or a global reduced-motion rule)

Usage:
  motion_check.py [--root DIR] [--strict] [--json] [FILE ...]

Scans .css, .scss, .js, .jsx, .ts, .tsx under --root (skipping node_modules, build output,
and tests). Line-based; it finds the usual mistakes, not every one.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUFFIXES = {".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".mjs"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".expo", "coverage", "android", "ios", "__pycache__", "vendor"}
TEST_MARKERS = (".test.", ".spec.", "__tests__")
LAYOUT_PROPS = r"(?:width|height|top|left|right|bottom|margin(?:-?(?:top|left|right|bottom))?|padding(?:-?(?:top|left|right|bottom))?)"

MOTION_SIGNS = re.compile(r"\btransition\s*:|@keyframes|\banimation\s*:|from\s+['\"](?:motion|framer-motion)|\bwithTiming\(|\bwithSpring\(|\bAnimated\.(?:View|Text|timing|spring)|\buseAnimatedStyle\(")
REDUCED_LOCAL = re.compile(r"prefers-reduced-motion|useReducedMotion|isReduceMotionEnabled|ReduceMotion\.|reducedMotion")
REDUCED_GLOBAL = re.compile(r"MotionConfig[^>]*reducedMotion|@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)")
TRANSITION_ALL = re.compile(r"\btransition(?:-property)?\s*:\s*all\b")
CSS_LAYOUT_TRANSITION = re.compile(r"\btransition(?:-property)?\s*:[^;]*\b" + LAYOUT_PROPS + r"\b")
CSS_LAYOUT_KEYFRAME = re.compile(r"(?:^|[{;\s])" + LAYOUT_PROPS + r"\s*:", re.IGNORECASE)
MOTION_LAYOUT_PROP = re.compile(r"(?:animate|whileHover|whileTap|whileFocus|whileInView|initial|exit)\s*=\s*\{\{[^}]*\b(?:width|height|top|left|right|bottom|margin\w*|padding\w*)\s*:")
REANIMATED_LAYOUT_PROP = re.compile(r"\b(?:width|height|top|left|right|bottom|margin\w*|padding\w*)\s*:\s*(?:withTiming|withSpring|\w+\.value)")
CSS_DURATION = re.compile(r"\b(?:transition|animation)(?:-duration)?\s*:[^;]*?(\d+(?:\.\d+)?)(ms|s)\b")
MOTION_DURATION = re.compile(r"\bduration\s*:\s*(\d+(?:\.\d+)?)\b")
REANIMATED_DURATION = re.compile(r"\bwith(?:Timing|Delay)\([^)]*?duration\s*:\s*(\d+)")
INFINITE = re.compile(r"repeat\s*:\s*Infinity|\banimation(?:-iteration-count)?\s*:[^;]*\binfinite\b|withRepeat\(.*?,\s*-1\s*[,)]")
FRAMER_IMPORT = re.compile(r"from\s+['\"]framer-motion['\"]")
MAX_MS = 500


def source_files(root: Path) -> list[Path]:
    found = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts) or any(marker in path.name or marker in path.parts for marker in TEST_MARKERS):
            continue
        found.append(path)
    return sorted(found)


def check_file(path: Path, root: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(root).as_posix() if root in path.parents or path == root else path.as_posix()
    errors: list[str] = []
    warnings: list[str] = []
    is_css = path.suffix in {".css", ".scss"}
    keyframe_depth = 0  # brace depth inside an @keyframes block; 0 means outside
    for number, line in enumerate(text.splitlines(), start=1):
        if TRANSITION_ALL.search(line):
            errors.append(f"{rel}:{number}: `transition: all`; name the properties (transform, opacity)")
        if is_css:
            in_keyframes = keyframe_depth > 0 or "@keyframes" in line
            if "@keyframes" in line:
                keyframe_depth = max(keyframe_depth, 0)
                keyframe_depth += line.count("{") - line.count("}")
                keyframe_depth = max(keyframe_depth, 0) if "{" in line else 1
            elif keyframe_depth > 0:
                keyframe_depth += line.count("{") - line.count("}")
            if CSS_LAYOUT_TRANSITION.search(line) or (in_keyframes and CSS_LAYOUT_KEYFRAME.search(line)):
                warnings.append(f"{rel}:{number}: animates a layout property; use transform/opacity or a layout animation")
            for value, unit in CSS_DURATION.findall(line):
                ms = float(value) * (1000 if unit == "s" else 1)
                if ms > MAX_MS:
                    warnings.append(f"{rel}:{number}: {int(ms)} ms is long for functional motion (keep under {MAX_MS} ms)")
        else:
            if MOTION_LAYOUT_PROP.search(line) or REANIMATED_LAYOUT_PROP.search(line):
                warnings.append(f"{rel}:{number}: animates a layout property; use transform/opacity or a layout animation")
            if re.search(r"from\s+['\"](?:motion|framer-motion)", text) or "transition={{" in line:
                for value in MOTION_DURATION.findall(line):
                    if float(value) * 1000 > MAX_MS and float(value) < 60:
                        warnings.append(f"{rel}:{number}: duration {value}s is long for functional motion (keep under {MAX_MS / 1000:g}s)")
            for value in REANIMATED_DURATION.findall(line):
                if int(value) > MAX_MS:
                    warnings.append(f"{rel}:{number}: {value} ms is long for functional motion (keep under {MAX_MS} ms)")
            if FRAMER_IMPORT.search(line):
                warnings.append(f"{rel}:{number}: imports `framer-motion`; the current package is `motion` (`motion/react`)")
        if INFINITE.search(line):
            warnings.append(f"{rel}:{number}: infinite motion; it needs a reason (a loader) and a way to stop")
    return {
        "file": rel,
        "animates": bool(MOTION_SIGNS.search(text)),
        "reduced_local": bool(REDUCED_LOCAL.search(text)),
        "reduced_global": bool(REDUCED_GLOBAL.search(text)),
        "errors": errors,
        "warnings": warnings,
    }


def run(root: Path, files: list[Path] | None = None) -> dict:
    paths = files or source_files(root)
    results = [check_file(p, root) for p in paths]
    errors = [e for r in results for e in r["errors"]]
    warnings = [w for r in results for w in r["warnings"]]
    animating = [r for r in results if r["animates"]]
    global_handling = any(r["reduced_global"] for r in results)
    any_handling = global_handling or any(r["reduced_local"] for r in results)
    if animating and not any_handling:
        errors.append("the project animates but handles reduced motion nowhere; add `MotionConfig reducedMotion=\"user\"` or a `prefers-reduced-motion` rule at the root, or `useReducedMotion` in native code")
    elif animating and not global_handling:
        for r in animating:
            if not r["reduced_local"]:
                warnings.append(f"{r['file']}: animates without a reduced-motion branch, and the project has no app-level handling")
    return {
        "root": root.as_posix(),
        "files": len(results),
        "animating_files": [r["file"] for r in animating],
        "reduced_motion": "global" if global_handling else ("local" if any_handling else "none"),
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="files to check (default: every source file under --root)")
    parser.add_argument("--root", default=".")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    files = [Path(f).resolve() for f in args.files] or None
    if files and any(not f.is_file() for f in files):
        print("motion_check: FAIL (file not found)")
        return 1
    result = run(root, files)
    if args.strict:
        result["errors"], result["warnings"] = result["errors"] + result["warnings"], []
        result["ok"] = not result["errors"]
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    for error in result["errors"]:
        print(f"ERROR   {error}")
    for warning in result["warnings"]:
        print(f"WARN    {warning}")
    print(f"motion_check: {'OK' if result['ok'] else 'FAIL'} ({result['files']} files, {len(result['animating_files'])} animate, reduced motion: {result['reduced_motion']}; {len(result['errors'])} errors, {len(result['warnings'])} warnings)")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
