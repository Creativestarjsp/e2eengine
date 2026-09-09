from pathlib import Path

from e2e.brain import CodeBrain


def test_brain_build_and_search(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path, provider="regex")
    data = brain.build()
    assert any(s["name"] == "login" for s in data["symbols"])
    assert brain.search("login")
    assert brain.callers("login")
    assert brain.check()["fresh"]
    assert data["provider"] == "regex"


def test_impact_reports_coverage(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()
    impact = brain.impact("login")
    assert impact["affected_files"] == ["app.py"]
    assert impact["coverage"] == "structural"


def test_auto_provider_keeps_fallback_portable(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n")
    brain = CodeBrain(tmp_path, provider="auto")
    data = brain.build()
    assert data["providers"]
    assert data["provider"] in {"tree-sitter", "regex", "regex-fallback"}
    assert any(s["name"] == "login" for s in data["symbols"])


def test_search_matches_multi_word_task_descriptions(tmp_path: Path):
    """`context(task)` passes whole task strings in, not single identifiers."""
    (tmp_path / "card.js").write_text("export function ActivityCard() {}\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()

    hits = brain.search("add the activity card to the discovery screen")

    assert [h["name"] for h in hits] == ["ActivityCard"]


def test_search_splits_camel_and_snake_case(tmp_path: Path):
    (tmp_path / "a.js").write_text("export function ActivityCard() {}\n")
    (tmp_path / "b.py").write_text("def use_lookin():\n    return 1\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()

    assert [h["name"] for h in brain.search("card")] == ["ActivityCard"]
    assert [h["name"] for h in brain.search("lookin")] == ["use_lookin"]


def test_search_ranks_stronger_matches_first(tmp_path: Path):
    (tmp_path / "app.js").write_text(
        "export function ActivityCard() {}\nexport function Unrelated() {}\n"
    )
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()

    hits = brain.search("activity card")

    assert hits[0]["name"] == "ActivityCard"
    assert hits[0]["score"] > 0


def test_search_ignores_stopword_only_queries(tmp_path: Path):
    (tmp_path / "app.js").write_text("export function ActivityCard() {}\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()

    assert brain.search("and the with") == []


def test_symbols_are_not_duplicated_by_overlapping_patterns(tmp_path: Path):
    """Several regexes match `export function x(` at different offsets."""
    (tmp_path / "app.js").write_text("export function handler() {}\n")
    brain = CodeBrain(tmp_path, provider="regex")
    data = brain.build()

    assert [s["name"] for s in data["symbols"]].count("handler") == 1


def test_context_surfaces_symbols_for_a_task(tmp_path: Path):
    (tmp_path / "card.js").write_text("export function ActivityCard() {}\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()

    context = brain.context("update the activity card")

    assert context["relevant_files"] == ["card.js"]
    assert [s["name"] for s in context["relevant_symbols"]] == ["ActivityCard"]
