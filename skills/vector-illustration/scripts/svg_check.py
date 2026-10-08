#!/usr/bin/env python3
"""Check that an SVG illustration is safe to ship and built to the skill's rules.

Errors (exit 1):
  - not well-formed XML, or the root is not <svg>
  - DOCTYPE or entity declarations
  - missing or malformed viewBox
  - executable or remote content: <script>, <foreignObject>, event-handler
    attributes, javascript: links, references to external URLs, @import
  - embedded raster images
  - over the element or size budget

Warnings:
  - text inside the artwork
  - fixed pixel width/height on the root
  - an opaque full-canvas background
  - definitions that nothing references, hidden elements, many filters
  - more distinct colours than a controlled palette needs

Usage:
  svg_check.py FILE.svg [FILE.svg ...] [--max-nodes 600] [--max-bytes 100000] [--strict] [--json]

Applies equally to generated artwork and to downloaded files.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
FORBIDDEN_ELEMENTS = {"script", "foreignObject", "iframe", "object", "embed", "audio", "video"}
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)|\bhsla?\([^)]*\)")
URL_REF = re.compile(r"url\(\s*['\"]?#([^)'\"\s]+)")
REMOTE = re.compile(r"^\s*(?:https?:)?//|^\s*(?:javascript|data|file|ftp):", re.IGNORECASE)
REMOTE_IN_CSS = re.compile(r"@import|url\(\s*['\"]?\s*(?:https?:)?//", re.IGNORECASE)
MAX_COLORS = 8


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _normalise(color: str) -> str:
    color = color.lower().replace(" ", "")
    if re.fullmatch(r"#[0-9a-f]{3}", color):
        color = "#" + "".join(ch * 2 for ch in color[1:])
    return color


def check(path: Path, max_nodes: int = 600, max_bytes: int = 100_000) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    info: dict = {"file": path.as_posix(), "nodes": 0, "bytes": 0, "colors": 0}
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [f"cannot read file: {exc}"], warnings, info
    info["bytes"] = len(raw)
    text = raw.decode("utf-8", errors="replace")

    # Checked before parsing: entity declarations are how XML parsers get attacked.
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
        return ["DOCTYPE or entity declarations are not allowed"], warnings, info
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"], warnings, info
    if local(root.tag) != "svg":
        return [f"root element is <{local(root.tag)}>, not <svg>"], warnings, info
    if not root.tag.startswith("{" + SVG_NS + "}"):
        errors.append("root <svg> is missing xmlns=\"http://www.w3.org/2000/svg\"")

    view_box = root.get("viewBox", "")
    parts = re.split(r"[\s,]+", view_box.strip()) if view_box.strip() else []
    canvas = None
    try:
        numbers = [float(p) for p in parts]
        if len(numbers) != 4 or numbers[2] <= 0 or numbers[3] <= 0:
            raise ValueError
        canvas = (numbers[2], numbers[3])
    except ValueError:
        errors.append("missing or malformed viewBox (expected four numbers with positive width and height)")
    for attr in ("width", "height"):
        value = root.get(attr, "")
        if value and not value.strip().endswith("%"):
            warnings.append(f"root has a fixed {attr}=\"{value}\"; remove it so the artwork scales with its container")

    elements = list(root.iter())
    info["nodes"] = len(elements)
    defined: dict[str, str] = {}
    referenced: set[str] = set()
    colors: set[str] = set()
    filters = 0
    for element in elements:
        tag = local(element.tag)
        if tag in FORBIDDEN_ELEMENTS:
            errors.append(f"<{tag}> is not allowed in an illustration")
        if tag == "image":
            errors.append("embedded raster image; illustrations are vector only")
        if tag in {"text", "tspan", "textPath"}:
            warnings.append("text inside the artwork; put copy in the interface so it can be translated and read aloud")
        if tag == "filter":
            filters += 1
        if tag == "style" and REMOTE_IN_CSS.search(element.text or ""):
            errors.append("<style> loads a remote resource")
        if element.get("id"):
            defined[element.get("id")] = tag
        for name, value in element.attrib.items():
            attr = local(name)
            if attr.lower().startswith("on"):
                errors.append(f"event-handler attribute `{attr}` on <{tag}>")
            if name in ("href", XLINK_HREF):
                if value.startswith("#"):
                    referenced.add(value[1:])
                elif REMOTE.search(value) or value.strip():
                    errors.append(f"<{tag}> references an external resource")
            elif attr == "style" and REMOTE_IN_CSS.search(value):
                errors.append(f"style on <{tag}> loads a remote resource")
            referenced.update(URL_REF.findall(value))
            if attr in {"fill", "stroke", "stop-color", "style", "flood-color"}:
                colors.update(_normalise(c) for c in COLOR.findall(value))
            if (attr == "display" and value == "none") or (attr == "visibility" and value == "hidden") or (attr == "opacity" and value.strip() in {"0", "0.0"}):
                warnings.append(f"hidden <{tag}>; remove elements that are never shown")
        if tag == "style":
            css = element.text or ""
            colors.update(_normalise(c) for c in COLOR.findall(css))
            referenced.update(URL_REF.findall(css))

    info["colors"] = len(colors)
    for definitions in (e for e in elements if local(e.tag) == "defs"):
        for child in definitions.iter():
            identifier = child.get("id")
            if identifier and child is not definitions and identifier not in referenced and local(child.tag) != "style":
                warnings.append(f"definition `{identifier}` is never referenced")
    if filters > 2:
        warnings.append(f"{filters} filters; filters are expensive to render")
    if len(colors) > MAX_COLORS:
        warnings.append(f"{len(colors)} distinct colours; a controlled palette uses one primary, one or two supporting colours, and neutrals")

    first = next((e for e in root if local(e.tag) not in {"style", "defs", "title", "desc"}), None)
    if canvas and first is not None and local(first.tag) == "rect":
        try:
            covers = float(first.get("width", "0").rstrip("%") or 0) >= canvas[0] and float(first.get("height", "0").rstrip("%") or 0) >= canvas[1]
        except ValueError:
            covers = first.get("width") == "100%" and first.get("height") == "100%"
        if covers and first.get("fill", "none") not in {"none", "transparent"}:
            warnings.append("opaque full-canvas background; keep the background transparent unless the layout requires one")

    if info["nodes"] > max_nodes:
        errors.append(f"{info['nodes']} elements exceeds the budget of {max_nodes}")
    if info["bytes"] > max_bytes:
        errors.append(f"{info['bytes']} bytes exceeds the budget of {max_bytes}")
    return sorted(set(errors)), sorted(set(warnings)), info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--max-nodes", type=int, default=600)
    parser.add_argument("--max-bytes", type=int, default=100_000)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results = []
    ok = True
    for name in args.files:
        errors, warnings, info = check(Path(name), args.max_nodes, args.max_bytes)
        if args.strict:
            errors, warnings = errors + warnings, []
        ok = ok and not errors
        results.append({**info, "ok": not errors, "errors": errors, "warnings": warnings})
    if args.json:
        print(json.dumps({"ok": ok, "files": results}, indent=2))
        return 0 if ok else 1
    for result in results:
        label = Path(result["file"]).name
        for error in result["errors"]:
            print(f"ERROR   {label}: {error}")
        for warning in result["warnings"]:
            print(f"WARN    {label}: {warning}")
        print(
            f"svg_check: {'OK' if result['ok'] else 'FAIL'} {label} "
            f"({result['nodes']} elements, {result['bytes']} bytes, {result['colors']} colours)"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
