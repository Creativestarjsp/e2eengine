#!/usr/bin/env python3
"""Check that a project is in a fit state to deploy, before any deploy command runs.

Reports which hosting targets are configured and fails on conditions that make
a deploy unsafe or unrepeatable:

  - env files, private keys, or service-account files tracked by git
  - a Dockerfile that copies an env file or bakes a secret-named value into the image
  - (production) missing CREDENTIALS.md, DEPLOYMENT.md, or RELEASE-CHECKLIST.md
  - (production) DEPLOYMENT.md without filled Targets, Smoke Test, Rollback, Evidence
  - (production) RELEASE-CHECKLIST.md without a named release owner and approval date

In preview the missing documents are warnings, because the deployment workflow
writes them.

Usage:
  deploy_preflight.py [--root DIR] [--env preview|production] [--json]

Reads file names and document structure only. Never prints file contents.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

#: Configuration file -> the target it indicates. Directories end with "/".
TARGET_MARKERS = {
    "vercel.json": "vercel",
    ".vercel/project.json": "vercel",
    "firebase.json": "firebase",
    "apphosting.yaml": "firebase",
    "supabase/config.toml": "supabase",
    "railway.json": "railway",
    "railway.toml": "railway",
    "amplify.yml": "aws",
    "cdk.json": "aws",
    "samconfig.toml": "aws",
    "buildspec.yml": "aws",
    "cloudbuild.yaml": "gcp",
    "app.yaml": "gcp",
    "staticwebapp.config.json": "azure",
    "azure.yaml": "azure",
    "Dockerfile": "container",
    "docker-compose.yml": "container",
    "docker-compose.yaml": "container",
    "compose.yaml": "container",
    "compose.yml": "container",
}

ENV_TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist"}
#: Tracked files that should never be in a repository, by glob on the file name.
FORBIDDEN_TRACKED = (
    "*.pem", "*.p12", "*.pfx", "id_rsa", "id_ed25519", "id_ecdsa",
    "*service-account*.json", "*serviceAccount*.json", "*-firebase-adminsdk-*.json",
)
SECRET_NAME = re.compile(r"(SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY)", re.IGNORECASE)
DOCKER_ASSIGN = re.compile(r"^\s*(?:ENV|ARG)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|\s)\s*(\S+)", re.IGNORECASE)
DOCKER_COPY_ENV = re.compile(r"^\s*(?:COPY|ADD)\s+.*(?:^|[\s/])\.env(?:\.[\w.-]+)?(?:\s|$)", re.IGNORECASE)

REQUIRED_SECTIONS = ("Targets", "Smoke Test", "Rollback")
PRODUCTION_SECTIONS = REQUIRED_SECTIONS + ("Evidence",)


def tracked_files(root: Path) -> list[str] | None:
    """Paths git tracks, or None when ``root`` is not a git repository."""
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.splitlines() if proc.returncode == 0 else None


def detect_targets(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for marker, target in TARGET_MARKERS.items():
        if (root / marker).is_file():
            found.setdefault(target, []).append(marker)
    return found


def sections(text: str) -> dict[str, str]:
    """``## Heading`` -> body text, for a Markdown document."""
    result: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            result[current] = []
        elif current is not None:
            result[current].append(line)
    return {name: "\n".join(body).strip() for name, body in result.items()}


def _template_sections() -> dict[str, str]:
    """Bodies of the shipped template, so an unfilled copy is not mistaken for a record."""
    template = Path(__file__).resolve().parents[3] / "templates" / "DEPLOYMENT.md"
    try:
        return sections(template.read_text(encoding="utf-8"))
    except OSError:
        return {}


def _table_rows(body: str) -> int:
    rows = [line for line in body.splitlines() if line.strip().startswith("|")]
    return max(0, len(rows) - 2)  # header and separator are not data


def unfilled_sections(text: str, required: tuple[str, ...]) -> list[str]:
    found = sections(text)
    template = _template_sections()
    missing = []
    for name in required:
        body = found.get(name, "")
        if not body or body == template.get(name, object()):
            missing.append(name)
        elif name == "Targets" and _table_rows(body) == 0:
            missing.append(name)
    return missing


def check_tracked(files: list[str]) -> list[str]:
    errors = []
    for path in files:
        name = path.rsplit("/", 1)[-1]
        if (name == ".env" or name.startswith(".env.")) and name not in ENV_TEMPLATES:
            errors.append(f"{path}: env file is tracked by git; remove it from the index and rotate what it held")
        elif any(fnmatch.fnmatch(name, pattern) for pattern in FORBIDDEN_TRACKED):
            errors.append(f"{path}: key or service-account file is tracked by git; remove it and rotate the credential")
    return errors


def check_dockerfile(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    dockerfile = root / "Dockerfile"
    if not dockerfile.is_file():
        return errors, warnings
    lines = dockerfile.read_text(encoding="utf-8", errors="ignore").splitlines()
    for number, line in enumerate(lines, start=1):
        if DOCKER_COPY_ENV.search(line):
            errors.append(f"Dockerfile:{number}: copies an env file into the image")
        assign = DOCKER_ASSIGN.match(line)
        # `ARG NAME` alone declares a build argument; only a value is a problem.
        if assign and SECRET_NAME.search(assign.group(1)) and not assign.group(2).startswith("$"):
            errors.append(f"Dockerfile:{number}: sets a value for {assign.group(1)}; inject it at runtime instead")
    if not any(re.match(r"^\s*USER\s+\S+", line, re.IGNORECASE) for line in lines):
        warnings.append("Dockerfile: no USER instruction; the container runs as root")
    ignore = root / ".dockerignore"
    if not ignore.is_file():
        warnings.append(".dockerignore missing; the build context may include env files and .git")
    elif not any(line.strip().startswith(".env") for line in ignore.read_text(encoding="utf-8", errors="ignore").splitlines()):
        warnings.append(".dockerignore does not exclude .env files")
    return errors, warnings


def check_documents(root: Path, env: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    production = env == "production"
    bucket = errors if production else warnings

    if not (root / "CREDENTIALS.md").is_file():
        bucket.append("CREDENTIALS.md missing; the deploy has no record of which variables each environment needs")

    deployment = root / "DEPLOYMENT.md"
    if not deployment.is_file():
        bucket.append("DEPLOYMENT.md missing; copy templates/DEPLOYMENT.md and record targets, smoke test, and rollback")
    else:
        required = PRODUCTION_SECTIONS if production else REQUIRED_SECTIONS
        for name in unfilled_sections(deployment.read_text(encoding="utf-8", errors="ignore"), required):
            bucket.append(f"DEPLOYMENT.md: `## {name}` is empty or still the template text")

    if production:
        checklist = root / "RELEASE-CHECKLIST.md"
        if not checklist.is_file():
            errors.append("RELEASE-CHECKLIST.md missing; production needs recorded owner approval")
        else:
            text = checklist.read_text(encoding="utf-8", errors="ignore")
            for label in ("Release owner", "Approved on"):
                match = re.search(rf"^[-* \t]*{label}[ \t]*:[ \t]*(.*)$", text, re.MULTILINE | re.IGNORECASE)
                if not match or not match.group(1).strip():
                    errors.append(f"RELEASE-CHECKLIST.md: `{label}:` is not filled in; production needs explicit owner approval")
    return errors, warnings


def run(root: Path, env: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    targets = detect_targets(root)
    if not targets:
        warnings.append("no target configuration found; choose one with references/choosing-a-target.md")
    files = tracked_files(root)
    if files is None:
        warnings.append("not a git repository; tracked-file checks skipped")
    else:
        errors.extend(check_tracked(files))
    for found_errors, found_warnings in (check_dockerfile(root), check_documents(root, env)):
        errors.extend(found_errors)
        warnings.extend(found_warnings)
    return {"env": env, "targets": targets, "errors": errors, "warnings": warnings, "ok": not errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument("--env", choices=("preview", "production"), default="preview")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    result = run(Path(args.root).resolve(), args.env)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    for error in result["errors"]:
        print(f"ERROR   {error}")
    for warning in result["warnings"]:
        print(f"WARN    {warning}")
    print(
        f"deploy_preflight: {'OK' if result['ok'] else 'FAIL'} "
        f"(env={result['env']}, targets={', '.join(sorted(result['targets'])) or 'none'}; "
        f"{len(result['errors'])} errors, {len(result['warnings'])} warnings)"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
