from pathlib import Path

from e2e.guardrails import check, write_policy


def test_guardrail_policy_is_materialized(tmp_path: Path):
    path = write_policy(tmp_path)
    assert path.exists()
    assert "pre-commit" in path.read_text(encoding="utf-8")


def test_protected_runtime_path_is_blocked(tmp_path: Path):
    result = check(tmp_path, "pre-commit", [".e2e/worktrees/worker/file.txt"])
    assert result["status"] == "block"
    assert "runtime-protected-paths" in result["blocked_rules"]


def test_secret_like_content_is_blocked(tmp_path: Path):
    key_name = "api" + "_key"
    value = "abcdefghijklmnopqrstuvwxyz"
    (tmp_path / "bad.py").write_text(f'{key_name} = "{value}"\n', encoding="utf-8")
    result = check(tmp_path, "pre-commit", ["bad.py"])
    assert result["status"] == "block"
    assert "secrets" in result["blocked_rules"]


def test_relative_to_root_normalises_absolute_paths(tmp_path):
    """Hooks pass absolute paths; guardrail rules match repo-relative ones."""
    from e2e.cli import _relative_to_root

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("", encoding="utf-8")

    assert _relative_to_root(tmp_path, str(tmp_path / ".git" / "config")) == ".git/config"
    assert _relative_to_root(tmp_path, ".git/config") == ".git/config"
    # A path outside the repo stays absolute so the rule still sees it.
    assert _relative_to_root(tmp_path, "/etc/passwd") == "/etc/passwd"


def test_check_accepts_explicit_files_instead_of_staged_diff(tmp_path):
    """pre-edit runs before the write, so there is no staged diff to read."""
    from e2e.guardrails import check

    result = check(tmp_path, "pre-edit", [".env"])

    assert result["status"] == "block"
    assert "protected-paths" in result["blocked_rules"]
