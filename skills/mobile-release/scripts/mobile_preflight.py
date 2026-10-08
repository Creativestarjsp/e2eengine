#!/usr/bin/env python3
"""Check a mobile project before building or submitting.

Fails (exit 1) when:
  - git tracks signing material or store credentials
  - an Expo project has no `eas.json`, or lacks the build profile for the environment
  - `app.json` has no version, iOS bundle identifier, or Android package
  - (production) `eas.json` has no production submit profile

Warns when configuration is dynamic (`app.config.js|ts`) and cannot be read,
when updates are configured without a runtime version, or when the project is
not a git repository.

Usage:
  mobile_preflight.py [--root DIR] [--env preview|production] [--json]

Reads names and structure only; never prints credential contents.
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

#: Signing and store-credential files that must not be tracked.
FORBIDDEN_TRACKED = (
    "*.p8", "*.p12", "*.pfx", "*.mobileprovision", "*.provisionprofile",
    "*.jks", "*.keystore", "*service-account*.json", "*serviceAccount*.json",
    "play-store-credentials*.json", "google-play*.json", "*-firebase-adminsdk-*.json",
    "credentials.json",
)
#: React Native templates ship a debug keystore on purpose; it signs nothing real.
ALLOWED = {"debug.keystore"}
PROFILE_FOR_ENV = {"preview": "preview", "production": "production"}


def tracked_files(root: Path) -> list[str] | None:
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.splitlines() if proc.returncode == 0 else None


def read_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"not valid JSON ({exc.msg} at line {exc.lineno})"
    return (data, None) if isinstance(data, dict) else (None, "top level is not an object")


def project_type(root: Path) -> str:
    if (root / "eas.json").is_file() or (root / "app.json").is_file() or any(root.glob("app.config.*")):
        return "expo"
    if (root / "fastlane" / "Fastfile").is_file():
        return "fastlane"
    if (root / "ios").is_dir() or (root / "android").is_dir():
        return "react-native"
    return "unknown"


def check_tracked(files: list[str]) -> list[str]:
    errors = []
    for path in files:
        name = path.rsplit("/", 1)[-1]
        if name in ALLOWED:
            continue
        if any(fnmatch.fnmatch(name, pattern) for pattern in FORBIDDEN_TRACKED):
            errors.append(f"{path}: signing or store credential is tracked by git; remove it and rotate the credential")
    return errors


def check_expo(root: Path, env: str) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    profiles: list[str] = []

    eas_path = root / "eas.json"
    if not eas_path.is_file():
        errors.append("eas.json missing; define build profiles before building")
    else:
        eas, problem = read_json(eas_path)
        if eas is None:
            errors.append(f"eas.json: {problem}")
        else:
            build = eas.get("build") if isinstance(eas.get("build"), dict) else {}
            profiles = sorted(build)
            wanted = PROFILE_FOR_ENV[env]
            if wanted not in build:
                errors.append(f"eas.json: no `{wanted}` build profile")
            if env == "production":
                submit = eas.get("submit") if isinstance(eas.get("submit"), dict) else {}
                if "production" not in submit:
                    errors.append("eas.json: no `production` submit profile")

    app_path = root / "app.json"
    if app_path.is_file():
        app, problem = read_json(app_path)
        if app is None:
            errors.append(f"app.json: {problem}")
        else:
            expo = app.get("expo") if isinstance(app.get("expo"), dict) else app
            if not expo.get("version"):
                errors.append("app.json: no `version`")
            if not (expo.get("ios") or {}).get("bundleIdentifier"):
                errors.append("app.json: no `ios.bundleIdentifier`")
            if not (expo.get("android") or {}).get("package"):
                errors.append("app.json: no `android.package`")
            if expo.get("updates") and not expo.get("runtimeVersion"):
                warnings.append("app.json: updates are configured without a `runtimeVersion`; OTA updates may reach incompatible builds")
    if any(root.glob("app.config.*")):
        warnings.append("app.config.js|ts is dynamic; check version, bundle identifier, package, and runtime version by hand")
    elif not app_path.is_file():
        errors.append("no app.json or app.config.* found")
    return errors, warnings, profiles


def run(root: Path, env: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    profiles: list[str] = []
    kind = project_type(root)

    files = tracked_files(root)
    if files is None:
        warnings.append("not a git repository; tracked-file checks skipped")
    else:
        errors.extend(check_tracked(files))

    if kind == "expo":
        expo_errors, expo_warnings, profiles = check_expo(root, env)
        errors.extend(expo_errors)
        warnings.extend(expo_warnings)
    elif kind == "fastlane":
        warnings.append("Fastlane project: lanes and signing are not inspected; verify them by hand")
    elif kind == "react-native":
        warnings.append("bare React Native project without fastlane/Fastfile; no release automation found")
    else:
        errors.append("no mobile project found (expected app.json, eas.json, fastlane/, ios/, or android/)")

    return {"env": env, "project": kind, "profiles": profiles, "errors": errors, "warnings": warnings, "ok": not errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="mobile project root (default: .)")
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
        f"mobile_preflight: {'OK' if result['ok'] else 'FAIL'} "
        f"(env={result['env']}, project={result['project']}, profiles={', '.join(result['profiles']) or 'none'}; "
        f"{len(result['errors'])} errors, {len(result['warnings'])} warnings)"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
