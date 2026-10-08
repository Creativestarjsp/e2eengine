"""The credential-inventory checker must reject values and report drift honestly."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "credential-inventory"

spec = importlib.util.spec_from_file_location("credentials_check", SKILL / "scripts" / "credentials_check.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

HEADER = (
    "## Register\n\n"
    "| Variable | Service | Purpose | Environments | Source | Storage | Owner | Rotation | Status |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


def register(tmp_path: Path, *rows: str) -> Path:
    (tmp_path / "CREDENTIALS.md").write_text(HEADER + "".join(r + "\n" for r in rows), encoding="utf-8")
    return tmp_path


def test_template_and_example_pass_without_code_scan(tmp_path: Path):
    for src in (SKILL / "templates" / "CREDENTIALS.md", SKILL / "examples" / "CREDENTIALS.example.md"):
        (tmp_path / "CREDENTIALS.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)
        assert result["ok"], (src.name, result["errors"])


# Fixtures are assembled from pieces, and given plain ids, so neither this file
# nor pytest's node-id cache contains a literal the repository secret scan
# would (correctly) block.
FAKE_VALUES = {
    "generic-assignment": "api_key = " + "abc123def456ghij",
    "stripe-live-key": "sk_" + "live_abcdefghijklmnopqrstuvwx",
    "github-token": "ghp" + "_abcdefghijklmnopqrstuvwxyz0123456789",
    "aws-access-key-id": "AKIA" + "ABCDEFGHIJKLMNOP",
    "database-url-with-password": "postgres://admin:" + "hunter22@db.internal/app",
    "private-key-block": "-----BEGIN RSA " + "PRIVATE KEY-----",
}


@pytest.mark.parametrize("storage", list(FAKE_VALUES.values()), ids=list(FAKE_VALUES))
def test_secret_like_values_are_rejected(tmp_path: Path, storage: str):
    register(tmp_path, f"| A_KEY | X | p | all | s | {storage} | o | r | active |")
    result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)
    assert not result["ok"]
    assert any("secret-like" in e for e in result["errors"])
    # The finding names a line, never the value.
    assert storage not in " ".join(result["errors"])


def test_storage_locations_are_not_mistaken_for_values(tmp_path: Path):
    register(
        tmp_path,
        "| A_KEY | X | p | all | s | 1Password: Vault/Item | o | r | active |",
        "| B_KEY | X | p | all | s | GH secret B_KEY; AWS SM /prod/x | o | none: public identifier | active |",
    )
    result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)
    assert result["ok"], result["errors"]


def test_row_shape_is_validated(tmp_path: Path):
    register(
        tmp_path,
        "| bad-name | X | p | all | s | st | o | r | weird |",
        "| B_KEY | X |  | all | s | st | o | r | active |",
        "| B_KEY | X | p | all | s | st | o | r | active |",
    )
    errors = " ".join(cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)["errors"])
    assert "UPPER_SNAKE_CASE" in errors
    assert "Status `weird`" in errors
    assert "`Purpose` is empty" in errors
    assert "duplicate row" in errors


def test_missing_register_is_an_error(tmp_path: Path):
    result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)
    assert not result["ok"] and "not found" in result["errors"][0]


def test_code_scan_reports_drift_in_both_directions(tmp_path: Path):
    register(
        tmp_path,
        "| DOCUMENTED | X | p | all | s | st | o | r | active |",
        "| UNUSED_ONE | X | p | all | s | st | o | r | active |",
        "| OLD_ONE | X | p | none | s | st | o | r | retired |",
    )
    (tmp_path / "app.ts").write_text("process.env.DOCUMENTED; process.env['NEW_JS'];", encoding="utf-8")
    (tmp_path / "svc.py").write_text("os.environ['NEW_PY']; os.getenv('DOCUMENTED')", encoding="utf-8")
    (tmp_path / "ci.yml").write_text("k: ${{ secrets.NEW_CI }}\nh: ${HOME}\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("NEW_TEMPLATE=\n", encoding="utf-8")
    # Real env files are protected and must never be read.
    (tmp_path / ".env").write_text("LEAKED=postgres://u:p@h/db\n", encoding="utf-8")

    result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=True, strict=False)
    assert result["ok"]  # drift is a warning by default
    assert set(result["undocumented"]) == {"NEW_JS", "NEW_PY", "NEW_CI", "NEW_TEMPLATE"}
    assert result["unused"] == ["UNUSED_ONE"]  # retired rows are not "unused"
    assert "LEAKED" not in result["undocumented"]
    assert "HOME" not in result["undocumented"]

    strict = cc.run(tmp_path, "CREDENTIALS.md", code_scan=True, strict=True)
    assert not strict["ok"]


def test_unknown_cells_are_surfaced_not_hidden(tmp_path: Path):
    register(tmp_path, "| A_KEY | X | p | all | unknown | st | unknown | r | active |")
    result = cc.run(tmp_path, "CREDENTIALS.md", code_scan=False, strict=False)
    assert result["ok"]
    assert result["unknown_cells"] == {"A_KEY": ["Source", "Owner"]}


def test_skill_is_discovered_by_registry():
    from e2e.skills import discover, match

    names = {s["name"] for s in discover(ROOT)}
    assert "credential-inventory" in names
    top = [s["name"] for s in match(ROOT, "what env vars and API keys do I need to run this project")[:3]]
    assert "credential-inventory" in top
