import sys

from e2e.eval_harness import (
    PYTHON_PLACEHOLDER,
    command_runner,
    compare_baseline,
    resolve_command,
    run_suite,
    summarize_attempts,
)


def test_pass_at_k_uses_independent_attempts():
    result = summarize_attempts([
        {"passed": True, "latency_seconds": 1},
        {"passed": False, "latency_seconds": 2},
        {"passed": False, "latency_seconds": 3},
        {"passed": True, "latency_seconds": 4},
    ], ks=(1, 2, 4))
    assert result["pass_rate"] == 0.5
    assert result["pass_at_k"]["1"] == 0.5
    assert result["pass_at_k"]["2"] == 0.8333
    assert result["pass_power_k"]["2"] == 0.25


def test_baseline_detects_quality_regression():
    result = compare_baseline(
        {"run_id": "current", "summary": {"pass_rate": 0.75, "mean_latency_seconds": 2.0}},
        {"run_id": "baseline", "summary": {"pass_rate": 1.0, "mean_latency_seconds": 1.0}},
    )
    assert result["status"] == "regression"
    assert "pass-rate-regression" in result["regressions"]
    assert "latency-regression" in result["regressions"]


def test_missing_binary_is_a_failed_case_not_a_crash(tmp_path):
    """The harness gathers evidence, so an environment problem is a result."""
    suite = {
        "id": "missing-binary",
        "cases": [{
            "id": "absent",
            "command": ["e2e-definitely-not-installed"],
            "graders": [{"type": "exit-code", "expected": 0}],
        }],
    }

    report = run_suite(tmp_path, suite, command_runner)

    attempt = report["attempts"][0]
    assert attempt["passed"] is False
    assert "returncode=127" in attempt["graders"][0]["evidence"]


def test_python_placeholder_resolves_to_the_running_interpreter():
    resolved = resolve_command([PYTHON_PLACEHOLDER, "-c", "pass"])
    assert resolved == [sys.executable, "-c", "pass"]


def test_bare_python_resolves_only_when_absent_from_path(monkeypatch):
    """Suites written before the placeholder still run where `python` is missing."""
    monkeypatch.setattr("e2e.eval_harness.shutil.which", lambda name: None)
    assert resolve_command(["python", "-m", "e2e"]) == [sys.executable, "-m", "e2e"]

    monkeypatch.setattr("e2e.eval_harness.shutil.which", lambda name: "/usr/bin/python")
    assert resolve_command(["python", "-m", "e2e"]) == ["python", "-m", "e2e"]


def test_non_python_commands_are_untouched():
    assert resolve_command(["git", "status"]) == ["git", "status"]
