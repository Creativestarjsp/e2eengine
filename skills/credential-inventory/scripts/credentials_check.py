#!/usr/bin/env python3
"""Validate a project's CREDENTIALS.md register and, optionally, its drift from code.

Checks (exit 1 on any failure):
  - CREDENTIALS.md exists and contains a `## Register` table with the fixed columns
  - no cell or line contains a secret-like value
  - every row has Variable, Service, Purpose, Storage filled
  - Variable names are UPPER_SNAKE_CASE
  - Status is one of active | pending | deprecated | retired

Drift (--code-scan; warnings unless --strict):
  - variables referenced in code or env templates but not registered
  - registered variables (not retired) that no code or template references

Usage:
  credentials_check.py [--root DIR] [--file CREDENTIALS.md] [--code-scan] [--strict] [--json]

Never prints file contents that matched a secret pattern; only the line number.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = [
    "Variable", "Service", "Purpose", "Environments", "Source",
    "Storage", "Owner", "Rotation", "Status",
]
REQUIRED_CELLS = ("Variable", "Service", "Purpose", "Storage")
VALID_STATUS = {"active", "pending", "deprecated", "retired"}
VARIABLE_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Value-shaped content that must never appear in the register. Superset of
# e2e/hooks.py SECRET_PATTERNS plus common vendor prefixes. The generic
# key=value form requires a digit and 12+ chars so prose such as
# "1Password: Vault/Item" in the conventions section does not trip it.
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"]?(?=[A-Za-z0-9_\-./+=]*\d)[A-Za-z0-9_\-./+=]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),                 # OpenAI-style
    re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"),  # Stripe
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                     # AWS access key id
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),           # GitHub tokens
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),           # Slack
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),               # Google API key
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT
    re.compile(r"(?i)\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp)://[^:\s/]+:[^@\s]+@"),  # URL with password
]

# Environment-variable access idioms, by language. Each pattern captures the name.
ENV_REFERENCE_PATTERNS = [
    re.compile(r"process\.env\.([A-Z][A-Z0-9_]*)"),                       # JS/TS
    re.compile(r"process\.env\[['\"]([A-Z][A-Z0-9_]*)['\"]\]"),           # JS/TS
    re.compile(r"import\.meta\.env\.([A-Z][A-Z0-9_]*)"),                  # Vite
    re.compile(r"Deno\.env\.get\(['\"]([A-Z][A-Z0-9_]*)['\"]\)"),         # Deno
    re.compile(r"os\.environ(?:\.get)?\s*[\[(]\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),  # Python
    re.compile(r"os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),            # Python
    re.compile(r"ENV(?:\.fetch)?\s*[\[(]\s*['\"]([A-Z][A-Z0-9_]*)['\"]"), # Ruby
    re.compile(r"os\.(?:Getenv|LookupEnv)\(\s*\"([A-Z][A-Z0-9_]*)\""),    # Go
    re.compile(r"System\.getenv\(\s*\"([A-Z][A-Z0-9_]*)\""),              # Java/Kotlin
    re.compile(r"env::var(?:_os)?\(\s*\"([A-Z][A-Z0-9_]*)\""),            # Rust
    re.compile(r"getenv\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),                # PHP/C
    re.compile(r"\$\{([A-Z][A-Z0-9_]*)(?::?[-=+?][^}]*)?\}"),             # shell/compose/CI
    re.compile(r"\$\{\{\s*secrets\.([A-Z][A-Z0-9_]*)\s*\}\}"),            # GitHub Actions
]
ENV_TEMPLATE_NAMES = {".env.example", ".env.sample", ".env.template", ".env.dist"}
ENV_TEMPLATE_LINE = re.compile(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=")
SCAN_SUFFIXES = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".java", ".kt",
    ".rs", ".php", ".c", ".cc", ".cpp", ".h", ".sh", ".bash", ".zsh", ".yml", ".yaml",
    ".toml", ".json", ".env", ".Dockerfile",
}
SCAN_NAMES = {"Dockerfile", "Makefile", "Procfile"}
SKIP_DIRS = {".git", "node_modules", ".e2e", "__pycache__", ".venv", "venv", "dist",
             "build", ".next", "target", "vendor", ".tox", ".mypy_cache", ".pytest_cache"}
# Shell/CI variables that are not project credentials.
IGNORED_VARIABLES = {
    "PATH", "HOME", "USER", "SHELL", "PWD", "TERM", "LANG", "LC_ALL", "TMPDIR", "TZ",
    "NODE_ENV", "PORT", "HOST", "HOSTNAME", "DEBUG", "CI", "GITHUB_TOKEN", "GITHUB_SHA",
    "GITHUB_REF", "GITHUB_WORKSPACE", "GITHUB_ACTIONS", "PYTHONPATH", "VIRTUAL_ENV",
    "LOG_LEVEL", "ENV", "ENVIRONMENT", "APP_ENV", "RAILS_ENV", "FLASK_ENV", "GOPATH",
}
MAX_FILE_BYTES = 1_000_000


def parse_register(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """Return (rows, errors) from the first pipe table under `## Register`."""
    errors: list[str] = []
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == "## register"), None)
    if start is None:
        return [], ["missing `## Register` heading"]
    table: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if line.strip().startswith("|"):
            table.append(line)
        elif table:
            break
    if len(table) < 2:
        return [], ["no table found under `## Register`"]

    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    header = cells(table[0])
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        errors.append("missing columns: " + ", ".join(missing))
        return [], errors
    rows: list[dict[str, str]] = []
    for n, line in enumerate(table[2:], start=3):
        values = cells(line)
        if len(values) != len(header):
            errors.append(f"table row {n}: expected {len(header)} cells, found {len(values)}")
            continue
        rows.append(dict(zip(header, values)))
    return rows, errors


def check_secrets(text: str) -> list[str]:
    hits: list[str] = []
    for n, line in enumerate(text.splitlines(), start=1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                hits.append(f"line {n}: secret-like value (pattern: {pattern.pattern[:30]}...)")
                break
    return hits


def check_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        name = row["Variable"].strip("`")
        label = name or "<empty>"
        for col in REQUIRED_CELLS:
            if not row[col]:
                errors.append(f"{label}: `{col}` is empty (write `unknown` if not known)")
        if name and not VARIABLE_NAME.match(name):
            errors.append(f"{label}: Variable is not UPPER_SNAKE_CASE")
        if name in seen:
            errors.append(f"{label}: duplicate row")
        seen.add(name)
        status = row["Status"].lower()
        if status not in VALID_STATUS:
            errors.append(f"{label}: Status `{row['Status']}` not in {sorted(VALID_STATUS)}")
    return errors


def scan_code(root: Path, register_file: Path) -> dict[str, set[str]]:
    """Map variable name -> set of relative file paths that reference it."""
    found: dict[str, set[str]] = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.resolve() == register_file.resolve():
            continue
        is_template = path.name in ENV_TEMPLATE_NAMES
        if not (is_template or path.suffix in SCAN_SUFFIXES or path.name in SCAN_NAMES):
            continue
        if path.suffix == ".env" and not is_template:
            continue  # real env files are protected; never read them
        if path.name.startswith(".env") and not is_template:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        if is_template:
            for line in text.splitlines():
                m = ENV_TEMPLATE_LINE.match(line)
                if m:
                    found.setdefault(m.group(1), set()).add(rel)
            continue
        for pattern in ENV_REFERENCE_PATTERNS:
            for m in pattern.finditer(text):
                found.setdefault(m.group(1), set()).add(rel)
    return {k: v for k, v in found.items() if k not in IGNORED_VARIABLES}


def run(root: Path, file_name: str, code_scan: bool, strict: bool) -> dict:
    register_file = root / file_name
    result: dict = {
        "file": register_file.as_posix(), "errors": [], "warnings": [],
        "registered": [], "undocumented": {}, "unused": [], "ok": False,
    }
    if not register_file.is_file():
        result["errors"].append(f"{file_name} not found; copy templates/CREDENTIALS.md to the project root")
        return result
    text = register_file.read_text(encoding="utf-8", errors="ignore")
    result["errors"].extend(check_secrets(text))
    rows, parse_errors = parse_register(text)
    result["errors"].extend(parse_errors)
    result["errors"].extend(check_rows(rows))
    result["registered"] = [r["Variable"].strip("`") for r in rows]
    result["unknown_cells"] = {
        r["Variable"].strip("`"): [c for c in REQUIRED_COLUMNS if r[c].lower() == "unknown"]
        for r in rows if any(r[c].lower() == "unknown" for c in REQUIRED_COLUMNS)
    }

    if code_scan:
        live = {r["Variable"].strip("`") for r in rows if r["Status"].lower() != "retired"}
        referenced = scan_code(root, register_file)
        undocumented = {k: sorted(v) for k, v in referenced.items() if k not in set(result["registered"])}
        unused = sorted(v for v in live if v not in referenced)
        result["undocumented"] = dict(sorted(undocumented.items()))
        result["unused"] = unused
        bucket = result["errors"] if strict else result["warnings"]
        for var, files in result["undocumented"].items():
            bucket.append(f"{var}: referenced in {', '.join(files[:3])} but not registered")
        for var in unused:
            bucket.append(f"{var}: registered (not retired) but not referenced in code or env templates")

    result["ok"] = not result["errors"]
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="project root (default: .)")
    ap.add_argument("--file", default="CREDENTIALS.md", help="register file name relative to root")
    ap.add_argument("--code-scan", action="store_true", help="compare the register with env references in code")
    ap.add_argument("--strict", action="store_true", help="treat drift as an error")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    result = run(Path(args.root).resolve(), args.file, args.code_scan, args.strict)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1

    for e in result["errors"]:
        print(f"ERROR   {e}")
    for w in result["warnings"]:
        print(f"WARN    {w}")
    for var, cols in result.get("unknown_cells", {}).items():
        print(f"TODO    {var}: {', '.join(cols)} = unknown")
    secretish = sum(1 for e in result["errors"] if "secret-like" in e)
    print(
        f"credentials_check: {'OK' if result['ok'] else 'FAIL'} "
        f"({len(result['registered'])} registered, {len(result['undocumented'])} undocumented, "
        f"{len(result['unused'])} unused, {secretish} secret-like values)"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
