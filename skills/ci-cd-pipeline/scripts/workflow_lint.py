#!/usr/bin/env python3
"""Check GitHub Actions workflows for unsafe or fragile patterns.

Errors (exit 1):
  - an action pinned to a branch (`@main`, `@master`, …) or not pinned at all
  - an unresolved `<placeholder>` left from a template
  - a secret, or an untrusted event field, interpolated inside a `run:` script
  - a secret echoed to the log
  - `pull_request_target` combined with a checkout of the pull request's code
  - `continue-on-error: true` on a job or step

Warnings:
  - no `permissions:` block
  - a job without `timeout-minutes`
  - a production deploy without `environment:` or `concurrency:`

Usage:
  workflow_lint.py [--root DIR] [--strict] [--json] [FILE ...]

With no FILE, checks `.github/workflows/*.yml|yaml` under --root.
Line-based and dependency-free: it catches common patterns, not every one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)")
RUN = re.compile(r"^(\s*)-?\s*run:\s*(.*)$")
PLACEHOLDER = re.compile(r"<[a-z][a-z0-9-]*>")
BRANCH_REFS = {"main", "master", "develop", "dev", "trunk", "latest", "head"}
SECRET_EXPR = re.compile(r"\$\{\{\s*secrets\.[A-Za-z0-9_]+\s*\}\}")
#: Event fields an outsider controls; inside a script they are an injection.
UNTRUSTED_EXPR = re.compile(
    r"\$\{\{\s*github\.(?:head_ref|event\.(?:issue|pull_request|comment|review|discussion|head_commit|commits|pages)\b[^}]*"
    r"(?:title|body|message|name|email|label|ref|default_branch|page_name)[^}]*)\s*\}\}"
)
PR_HEAD_CHECKOUT = re.compile(r"github\.event\.pull_request\.head\.(?:sha|ref)|github\.head_ref")
JOB_KEY = re.compile(r"^  ([A-Za-z_][\w-]*):\s*$")
PRODUCTION = re.compile(r"--prod\b|environment[= ]+production|deploy[-_ ]?prod|production deploy", re.IGNORECASE)


def run_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Every line that belongs to a `run:` script, as ``(line number, text)``."""
    found: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = RUN.match(lines[index])
        if not match:
            index += 1
            continue
        indent, rest = len(match.group(1)), match.group(2).strip()
        if rest and rest[0] not in "|>":
            found.append((index + 1, rest))
            index += 1
            continue
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            found.append((index + 1, line))
            index += 1
    return found


def split_jobs(lines: list[str]) -> dict[str, list[str]]:
    jobs: dict[str, list[str]] = {}
    in_jobs = False
    current = None
    for line in lines:
        if re.match(r"^jobs:\s*$", line):
            in_jobs = True
            continue
        if in_jobs and line and not line[0].isspace() and not line.startswith("#"):
            in_jobs = False
        if not in_jobs:
            continue
        key = JOB_KEY.match(line)
        if key:
            current = key.group(1)
            jobs[current] = []
        elif current:
            jobs[current].append(line)
    return jobs


def lint(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    code = [line.split(" #", 1)[0] if not line.lstrip().startswith("#") else "" for line in lines]
    name = path.name

    for number, line in enumerate(code, start=1):
        if PLACEHOLDER.search(line):
            errors.append(f"{name}:{number}: unresolved template placeholder")
        uses = USES.match(line)
        if uses:
            target = uses.group(1)
            if target.startswith(("./", "docker://")):
                continue
            ref = target.rsplit("@", 1)[1] if "@" in target else ""
            if not ref:
                errors.append(f"{name}:{number}: action `{target}` is not pinned to a version")
            elif ref.lower() in BRANCH_REFS:
                errors.append(f"{name}:{number}: action `{target}` is pinned to a branch; use a release tag or commit SHA")
        if re.match(r"^\s*-?\s*continue-on-error:\s*true\b", line):
            errors.append(f"{name}:{number}: continue-on-error hides failures")

    for number, line in run_blocks(code):
        if SECRET_EXPR.search(line):
            if re.search(r"\b(echo|printf|print|cat)\b", line):
                errors.append(f"{name}:{number}: a secret is written to the log")
            else:
                errors.append(f"{name}:{number}: secret interpolated inside a run script; pass it through `env:`")
        if UNTRUSTED_EXPR.search(line):
            errors.append(f"{name}:{number}: untrusted event field interpolated inside a run script; pass it through `env:`")

    joined = "\n".join(code)
    if re.search(r"^\s*pull_request_target\s*:|\[\s*[^\]]*pull_request_target", joined, re.MULTILINE) and PR_HEAD_CHECKOUT.search(joined):
        errors.append(f"{name}: pull_request_target checks out pull-request code; untrusted code would run with secrets")

    if not re.search(r"^\s*permissions\s*:", joined, re.MULTILINE):
        warnings.append(f"{name}: no `permissions:` block; the token gets the repository default")
    for job, body in split_jobs(code).items():
        block = "\n".join(body)
        if re.search(r"^\s+uses:\s*\S+\.ya?ml", block, re.MULTILINE) and "steps:" not in block:
            continue  # a reusable-workflow call has no steps of its own to time out
        if "timeout-minutes" not in block:
            warnings.append(f"{name}: job `{job}` has no timeout-minutes")
        if PRODUCTION.search(job) or PRODUCTION.search(block):
            if not re.search(r"^\s+environment\s*:", block, re.MULTILINE):
                warnings.append(f"{name}: job `{job}` deploys to production without `environment:`; approval cannot be enforced")
            if not re.search(r"^\s+concurrency\s*:", block, re.MULTILINE) and not re.search(r"^concurrency\s*:", joined, re.MULTILINE):
                warnings.append(f"{name}: job `{job}` deploys to production without `concurrency:`; releases can overlap")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="workflow files (default: .github/workflows under --root)")
    parser.add_argument("--root", default=".")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [Path(f) for f in args.files] or sorted(
        p for p in (root / ".github" / "workflows").glob("*") if p.suffix in {".yml", ".yaml"}
    )
    errors: list[str] = []
    warnings: list[str] = []
    if not paths:
        errors.append("no workflow files found")
    for path in paths:
        if not path.is_file():
            errors.append(f"{path}: not found")
            continue
        file_errors, file_warnings = lint(path)
        errors.extend(file_errors)
        warnings.extend(file_warnings)
    if args.strict:
        errors, warnings = errors + warnings, []

    ok = not errors
    if args.json:
        print(json.dumps({"ok": ok, "files": [p.as_posix() for p in paths], "errors": errors, "warnings": warnings}, indent=2))
        return 0 if ok else 1
    for error in errors:
        print(f"ERROR   {error}")
    for warning in warnings:
        print(f"WARN    {warning}")
    print(f"workflow_lint: {'OK' if ok else 'FAIL'} ({len(paths)} files, {len(errors)} errors, {len(warnings)} warnings)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
