#!/usr/bin/env python3
"""Render an SVG illustration so it can be looked at before it ships.

Always writes `preview.html`: the artwork at a small and a large size on a light
and a dark background. Then tries to turn that into images, using whatever is
installed:

  1. a headless Chrome or Chromium screenshot of preview.html (shows both themes)
  2. otherwise a direct rasteriser at each size: rsvg-convert, Inkscape,
     ImageMagick, CairoSVG, or macOS Quick Look

Usage:
  render_preview.py FILE.svg [--out DIR] [--sizes 120,480] [--json]

Exit 0 when at least one image was produced. Exit 2 when only preview.html
could be written: open it in a browser, and do not report the artwork as
visually reviewed until someone has looked at it.

The SVG is shown through <img>, so scripts inside it cannot run.
No third-party dependencies are required.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)
THEMES = (("light", "#FFFFFF", "#1F2937"), ("dark", "#111827", "#F3F4F6"))


def find_chrome() -> str | None:
    for candidate in CHROME_CANDIDATES:
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    return None


def write_html(svg: Path, out: Path, sizes: list[int]) -> Path:
    """A static page: every size on every theme. No scripts."""
    source = html.escape(svg.resolve().as_uri(), quote=True)
    cells = []
    for theme, background, foreground in THEMES:
        images = "".join(
            f'<figure><img src="{source}" width="{size}" alt=""><figcaption>{size}px</figcaption></figure>' for size in sizes
        )
        cells.append(f'<section style="background:{background};color:{foreground}"><h2>{theme}</h2><div class="row">{images}</div></section>')
    page = (
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>" + html.escape(svg.name) + " preview</title><style>"
        "body{margin:0;font:14px system-ui,sans-serif}section{padding:24px}h2{margin:0 0 16px;font-size:14px;font-weight:600}"
        ".row{display:flex;gap:32px;align-items:flex-end;flex-wrap:wrap}figure{margin:0}figcaption{margin-top:8px;opacity:.7}"
        "img{display:block;height:auto}</style></head><body>" + "".join(cells) + "</body></html>"
    )
    target = out / "preview.html"
    target.write_text(page, encoding="utf-8")
    return target


def _run(command: list[str], timeout: int = 60) -> bool:
    try:
        return subprocess.run(command, capture_output=True, timeout=timeout).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def aspect_ratio(svg: Path) -> float:
    """Height over width from the viewBox; 1.0 when it cannot be read."""
    match = re.search(r'viewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', svg.read_text(encoding="utf-8", errors="replace"))
    try:
        return float(match.group(2)) / float(match.group(1)) if match else 1.0
    except (ValueError, ZeroDivisionError):
        return 1.0


def screenshot_html(svg: Path, page: Path, out: Path, sizes: list[int]) -> Path | None:
    chrome = find_chrome()
    if chrome is None:
        return None
    target = out / "preview.png"
    width = max(900, sum(sizes) + 32 * len(sizes) + 96)
    height = 2 * (int(max(sizes) * aspect_ratio(svg)) + 120)
    ok = _run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},{height}", f"--screenshot={target}", page.resolve().as_uri()])
    return target if ok and target.is_file() and target.stat().st_size > 0 else None


def rasterise(svg: Path, out: Path, size: int) -> tuple[Path, str] | None:
    """One transparent PNG at ``size`` wide, from the first rasteriser that works."""
    target = out / f"{svg.stem}-{size}.png"
    attempts: list[tuple[str, list[str]]] = []
    if shutil.which("rsvg-convert"):
        attempts.append(("rsvg-convert", ["rsvg-convert", "-w", str(size), "-o", str(target), str(svg)]))
    if shutil.which("inkscape"):
        attempts.append(("inkscape", ["inkscape", str(svg), "--export-type=png", f"--export-width={size}", f"--export-filename={target}"]))
    if shutil.which("magick"):
        attempts.append(("imagemagick", ["magick", "-background", "none", "-density", "300", str(svg), "-resize", f"{size}x", str(target)]))
    for name, command in attempts:
        if _run(command) and target.is_file():
            return target, name
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(url=str(svg), write_to=str(target), output_width=size)
        if target.is_file():
            return target, "cairosvg"
    except Exception:  # noqa: BLE001 - optional dependency; any failure means "try the next renderer"
        pass
    if shutil.which("qlmanage"):
        produced = out / f"{svg.name}.png"
        if _run(["qlmanage", "-t", "-s", str(size), "-o", str(out), str(svg)]) and produced.is_file():
            produced.replace(target)
            return target, "quicklook"
    return None


def render(svg: Path, out: Path, sizes: list[int]) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    page = write_html(svg, out, sizes)
    images: list[str] = []
    renderer = None
    shot = screenshot_html(svg, page, out, sizes)
    if shot is not None:
        images.append(shot.as_posix())
        renderer = "chrome"
    else:
        for size in sizes:
            result = rasterise(svg, out, size)
            if result:
                images.append(result[0].as_posix())
                renderer = result[1]
    return {
        "svg": svg.as_posix(),
        "html": page.as_posix(),
        "images": images,
        "renderer": renderer,
        "reviewed": False,
        "note": "Look at the images before reporting the artwork as reviewed." if images else "No renderer found. Open preview.html in a browser; the artwork has not been visually reviewed.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg")
    parser.add_argument("--out", help="output directory (default: <svg folder>/preview)")
    parser.add_argument("--sizes", default="120,480", help="comma-separated widths in pixels")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    svg = Path(args.svg)
    if not svg.is_file():
        print(f"render_preview: FAIL ({svg} not found)")
        return 1
    try:
        sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
        if not sizes or any(s <= 0 or s > 4000 for s in sizes):
            raise ValueError
    except ValueError:
        print("render_preview: FAIL (--sizes must be positive widths such as 120,480)")
        return 1

    result = render(svg, Path(args.out) if args.out else svg.parent / "preview", sizes)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"html     {result['html']}")
        for image in result["images"]:
            print(f"image    {image}")
        print(f"render_preview: {'OK' if result['images'] else 'NO RENDERER'} ({result['renderer'] or 'html only'}) {result['note']}")
    return 0 if result["images"] else 2


if __name__ == "__main__":
    sys.exit(main())
