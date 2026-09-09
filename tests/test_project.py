import json
import os
from pathlib import Path

import pytest

from e2e.project import CONFIG_FILENAME, SKILLS_PATH_ENV, init, load_config, skills_paths, skills_source


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv(SKILLS_PATH_ENV, raising=False)


def test_init_creates_config_and_state(tmp_path: Path):
    report = init(tmp_path)
    assert (tmp_path / CONFIG_FILENAME).exists()
    assert (tmp_path / ".e2e" / "evals").is_dir()
    assert CONFIG_FILENAME in report["created"]
    assert load_config(tmp_path)["skills_paths"] == ["skills", ".e2e/skills"]


def test_init_is_idempotent_and_reports_what_already_existed(tmp_path: Path):
    init(tmp_path)
    (tmp_path / CONFIG_FILENAME).write_text('{"skills_paths": ["custom"]}\n', encoding="utf-8")

    report = init(tmp_path)

    assert CONFIG_FILENAME in report["existing"]
    assert CONFIG_FILENAME not in report["created"]
    # A second init must not discard a hand-edited config.
    assert load_config(tmp_path)["skills_paths"] == ["custom"]


def test_init_force_rewrites_config(tmp_path: Path):
    init(tmp_path)
    (tmp_path / CONFIG_FILENAME).write_text('{"skills_paths": ["custom"]}\n', encoding="utf-8")

    init(tmp_path, skills=["shared/skills"], force=True)

    assert load_config(tmp_path)["skills_paths"] == ["shared/skills"]


def test_init_warns_when_no_skills_are_reachable(tmp_path: Path):
    report = init(tmp_path)
    assert report["skills_found"] == 0
    assert report["warnings"], "an empty registry must not look like success"


def test_init_reports_skills_it_can_see(tmp_path: Path):
    skill = tmp_path / "skills" / "backend-developer"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Backend\n", encoding="utf-8")

    report = init(tmp_path)

    assert report["skills_found"] == 1
    assert report["warnings"] == []


def test_env_var_overrides_config(tmp_path: Path, monkeypatch):
    init(tmp_path, skills=["from-config"])
    monkeypatch.setenv(SKILLS_PATH_ENV, str(tmp_path / "from-env"))

    assert skills_paths(tmp_path) == [tmp_path / "from-env"]
    assert skills_source(tmp_path) == f"env:{SKILLS_PATH_ENV}"


def test_config_overrides_defaults(tmp_path: Path):
    init(tmp_path, skills=["shared/skills"])

    assert skills_paths(tmp_path) == [tmp_path / "shared" / "skills"]
    assert skills_source(tmp_path) == f"config:{CONFIG_FILENAME}"


def test_unreadable_config_falls_back_to_defaults(tmp_path: Path):
    (tmp_path / CONFIG_FILENAME).write_text("{not json", encoding="utf-8")

    assert load_config(tmp_path) == {}
    assert skills_paths(tmp_path) == [tmp_path / "skills", tmp_path / ".e2e" / "skills"]
