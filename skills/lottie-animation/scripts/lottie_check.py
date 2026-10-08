#!/usr/bin/env python3
"""Check a Lottie file before it ships.

Errors (exit 1):
  - not valid JSON, or missing v, fr, ip, op, w, h, layers
  - op not after ip; non-positive size or frame rate
  - a slot referenced by `sid` that is not defined in `slots`
  - keyframes not in ascending time order
  - image assets that are remote (http/https) or embedded (data: URI), or whose file is missing beside the JSON
  - text layers without a declared font, or a declared font whose file is missing beside the JSON
  - over the size budget

Warnings:
  - frame rate outside 24..60, or duration over 10 seconds
  - expressions (renderer-specific)
  - slots defined but never referenced
  - no top-level name; more than 200 layers

Usage:
  lottie_check.py FILE.json [FILE.json ...] [--max-bytes 150000] [--strict] [--json]

No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("v", "fr", "ip", "op", "w", "h", "layers")
FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}
TEXT_LAYER = 5


def walk(node, path="$"):
    """Yield (path, dict) for every object in the document."""
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def check(path: Path, max_bytes: int = 150_000) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    info: dict = {"file": path.as_posix(), "bytes": 0, "layers": 0, "frames": 0, "fps": None, "slots": 0}
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [f"cannot read file: {exc}"], warnings, info
    info["bytes"] = len(raw)
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"not valid JSON: {exc}"], warnings, info
    if not isinstance(doc, dict):
        return ["top level must be an object"], warnings, info

    missing = [key for key in REQUIRED if key not in doc]
    if missing:
        errors.append("missing top-level keys: " + ", ".join(missing))
    fr, ip, op = doc.get("fr"), doc.get("ip"), doc.get("op")
    if all(isinstance(v, (int, float)) for v in (fr, ip, op)):
        info["fps"] = fr
        if fr <= 0:
            errors.append("frame rate must be positive")
        elif not 24 <= fr <= 60:
            warnings.append(f"frame rate {fr}; UI animations usually use 24..60")
        if op <= ip:
            errors.append("op must be greater than ip (op is exclusive)")
        else:
            info["frames"] = op - ip
            if fr > 0 and (op - ip) / fr > 10:
                warnings.append(f"duration {(op - ip) / fr:.1f}s; UI animations are usually a few seconds at most")
    for key in ("w", "h"):
        if isinstance(doc.get(key), (int, float)) and doc[key] <= 0:
            errors.append(f"{key} must be positive")
    if not doc.get("nm"):
        warnings.append("no top-level `nm`; name the animation")

    layers = doc.get("layers") if isinstance(doc.get("layers"), list) else []
    info["layers"] = len(layers)
    if len(layers) > 200:
        warnings.append(f"{len(layers)} layers; simplify for UI use")

    slots = doc.get("slots") if isinstance(doc.get("slots"), dict) else {}
    info["slots"] = len(slots)
    referenced: set[str] = set()
    has_text_layer = False
    for where, obj in walk(doc):
        if "sid" in obj and isinstance(obj["sid"], str) and not where.startswith("$.slots"):
            referenced.add(obj["sid"])
            if obj["sid"] not in slots:
                errors.append(f"{where}: references slot `{obj['sid']}` which is not defined in `slots`")
        if obj.get("a") == 1 and isinstance(obj.get("k"), list):
            times = [k.get("t") for k in obj["k"] if isinstance(k, dict) and isinstance(k.get("t"), (int, float))]
            if times != sorted(times):
                errors.append(f"{where}: keyframes are not in ascending time order")
        if isinstance(obj.get("x"), str) and obj["x"].strip():
            warnings.append(f"{where}: expression; renderers differ in support")
        if obj.get("ty") == TEXT_LAYER and "t" in obj:
            has_text_layer = True
    for sid in slots:
        if sid not in referenced:
            warnings.append(f"slot `{sid}` is defined but never referenced")

    folder = path.parent
    for index, asset in enumerate(doc.get("assets") or []):
        if not isinstance(asset, dict) or "p" not in asset:
            continue
        location = f"{asset.get('u', '')}{asset.get('p', '')}"
        if location.startswith(("http://", "https://", "//")):
            errors.append(f"assets[{index}]: remote asset `{location[:60]}`; keep assets local to the project")
        elif location.startswith("data:") or asset.get("e") == 1:
            errors.append(f"assets[{index}]: embedded data-URI image; UI animations are vector")
        elif not (folder / location).is_file():
            errors.append(f"assets[{index}]: `{location}` not found beside the JSON")

    fonts = (doc.get("fonts") or {}).get("list") if isinstance(doc.get("fonts"), dict) else None
    font_files = {p.name for p in folder.iterdir() if p.suffix.lower() in FONT_SUFFIXES} if folder.is_dir() else set()
    if has_text_layer and not fonts:
        errors.append("text layer without a declared font (fonts.list); it will render blank")
    for font in fonts or []:
        if isinstance(font, dict) and not font_files:
            errors.append(f"font `{font.get('fFamily') or font.get('fName')}` declared but no .ttf/.otf/.ttc file sits beside the JSON")
            break

    if info["bytes"] > max_bytes:
        errors.append(f"{info['bytes']} bytes exceeds the budget of {max_bytes}")
    return sorted(set(errors)), sorted(set(warnings)), info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--max-bytes", type=int, default=150_000)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results, ok = [], True
    for name in args.files:
        errors, warnings, info = check(Path(name), args.max_bytes)
        if args.strict:
            errors, warnings = errors + warnings, []
        ok = ok and not errors
        results.append({**info, "ok": not errors, "errors": errors, "warnings": warnings})
    if args.json:
        print(json.dumps({"ok": ok, "files": results}, indent=2))
        return 0 if ok else 1
    for result in results:
        label = Path(result["file"]).parent.name + "/" + Path(result["file"]).name
        for error in result["errors"]:
            print(f"ERROR   {label}: {error}")
        for warning in result["warnings"]:
            print(f"WARN    {label}: {warning}")
        print(f"lottie_check: {'OK' if result['ok'] else 'FAIL'} {label} ({result['frames']} frames at {result['fps']} fps, {result['layers']} layers, {result['slots']} slots, {result['bytes']} bytes)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
