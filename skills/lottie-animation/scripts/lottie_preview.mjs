#!/usr/bin/env node
// Render pinned frames of a Lottie file with CanvasKit/Skottie so the animation can be looked at before it ships.
//
// Usage:
//   node lottie_preview.mjs FILE.json [--frames 0,30,59] [--out DIR] [--sheet]
//
// Writes frame-NNN.png (transparent) for each frame, plus preview.html showing every
// frame on a light and a dark background. With --sheet it also screenshots that page
// to preview.png using a headless Chrome or Chromium when one is installed.
//
// Default frames: first, quarter, middle, three-quarter, last. For a loop, compare the
// first and last frames; they should be identical.
//
// Requires the `canvaskit-wasm` package (its "full" build includes Skottie), resolved
// from the working directory: `npm install --no-save canvaskit-wasm`. Exit 2 when it is
// missing, 1 on bad input or a file Skottie cannot parse. No other dependencies.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith("--"));
const option = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
if (!file) { console.error("usage: lottie_preview.mjs FILE.json [--frames 0,30,59] [--out DIR] [--sheet]"); process.exit(1); }
if (!fs.existsSync(file)) { console.error(`lottie_preview: FAIL (${file} not found)`); process.exit(1); }

const require = createRequire(path.join(process.cwd(), "package.json"));
let fullBuild;
try {
  fullBuild = require.resolve("canvaskit-wasm/full");
} catch {
  console.error("lottie_preview: NO RENDERER. canvaskit-wasm is not installed here; run `npm install --no-save canvaskit-wasm` in this directory. The animation has not been visually reviewed.");
  process.exit(2);
}
const CanvasKit = await require(fullBuild)({ locateFile: (f) => path.join(path.dirname(fullBuild), f) });

const json = fs.readFileSync(file, "utf8");
let doc;
try { doc = JSON.parse(json); } catch (e) { console.error(`lottie_preview: FAIL (not valid JSON: ${e.message})`); process.exit(1); }
const anim = CanvasKit.MakeManagedAnimation(json, null);
if (!anim) { console.error("lottie_preview: FAIL (Skottie could not parse the animation)"); process.exit(1); }

const w = doc.w, h = doc.h, last = doc.op - 1;
const frames = option("--frames")
  ? option("--frames").split(",").map(Number)
  : [0, Math.round(last / 4), Math.round(last / 2), Math.round((3 * last) / 4), last];
if (frames.some((f) => !Number.isInteger(f) || f < 0 || f > last)) { console.error(`lottie_preview: FAIL (frames must be integers between 0 and ${last})`); process.exit(1); }

const out = option("--out") ?? path.join(path.dirname(file), "preview");
fs.mkdirSync(out, { recursive: true });
const surface = CanvasKit.MakeSurface(w, h);
const canvas = surface.getCanvas();
const written = [];
for (const frame of frames) {
  anim.seekFrame(frame);
  canvas.clear(CanvasKit.TRANSPARENT);
  anim.render(canvas, CanvasKit.LTRBRect(0, 0, w, h));
  surface.flush();
  const image = surface.makeImageSnapshot();
  const target = path.join(out, `frame-${String(frame).padStart(3, "0")}.png`);
  fs.writeFileSync(target, image.encodeToBytes());
  image.delete();
  written.push({ frame, file: target });
}

const escape = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const figures = written.map((f) => `<figure><img src="${escape(path.basename(f.file))}" width="${Math.min(w, 200)}" alt=""><figcaption>frame ${f.frame}</figcaption></figure>`).join("");
const section = (name, bg, fg) => `<section style="background:${bg};color:${fg}"><h2>${escape(doc.nm ?? path.basename(file))} · ${name}</h2><div class="row">${figures}</div></section>`;
const html = `<!doctype html><html><head><meta charset="utf-8"><title>${escape(doc.nm ?? "Lottie")} preview</title><style>body{margin:0;font:13px system-ui,sans-serif}section{padding:12px 16px}h2{font-size:13px;margin:0 0 6px}.row{display:flex;gap:10px;flex-wrap:wrap}figure{margin:0;text-align:center}img{display:block;height:auto}figcaption{margin-top:2px;opacity:.7}</style></head><body>${section("light", "#FFFFFF", "#1F2937")}${section("dark", "#111827", "#E5E7EB")}</body></html>`;
const page = path.join(out, "preview.html");
fs.writeFileSync(page, html);

let sheet = null;
if (args.includes("--sheet")) {
  const candidates = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"];
  const onPath = (c) => c.includes("/") ? fs.existsSync(c) : spawnSync("which", [c]).status === 0;
  const chrome = candidates.find(onPath);
  if (chrome) {
    const target = path.join(out, "preview.png");
    const width = Math.max(900, frames.length * (Math.min(w, 200) + 10) + 48);
    const height = 2 * (Math.round(Math.min(w, 200) * (h / w)) + 80);
    spawnSync(chrome, ["--headless", "--disable-gpu", "--hide-scrollbars", `--window-size=${width},${height}`, `--screenshot=${target}`, "file://" + path.resolve(page)], { stdio: "ignore" });
    if (fs.existsSync(target)) sheet = target;
  }
}

for (const f of written) console.log(`frame    ${f.file}`);
console.log(`html     ${page}`);
if (sheet) console.log(`sheet    ${sheet}`);
console.log(`lottie_preview: OK (${written.length} frames of ${doc.op - doc.ip} at ${doc.fr} fps, ${w}x${h}). Look at the frames before reporting the animation as reviewed.`);
