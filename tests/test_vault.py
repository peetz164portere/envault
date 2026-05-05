"""Tests for envault.vault — high-level env var save/load operations."""

import pytest

from envault import storage
from envault.vault import (
    list_projects,
    load_env,
    project_exists,
    remove_env,
    save_env,
)

PASSWORD = "supersecret"
SAMPLE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc123"}


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", tmp_path / "vaults")


def test_save_and_load_env():
    save_env("web", SAMPLE_ENV, PASSWORD)
    result = load_env("web", PASSWORD)
    assert result == SAMPLE_ENV


def test_project_exists_after_save():
    assert not project_exists("web")
    save_env("web", SAMPLE_ENV, PASSWORD)
    assert project_exists("web")


def test_load_env_wrong_password_raises():
    save_env("web", SAMPLE_ENV, PASSWORD)
    with pytest.raises(Exception):
        load_env("web", "wrongpassword")


def test_load_env_missing_project_raises():
    with pytest.raises(FileNotFoundError):
        load_env("ghost", PASSWORD)


def test_remove_env_deletes_project():
    save_env("web", SAMPLE_ENV, PASSWORD)
    remove_env("web")
    assert not project_exists("web")


def test_remove_env_missing_raises():
    with pytest.raises(FileNotFoundError):
        remove_env("nope")


def test_list_projects_returns_all_saved():
    save_env("proj1", {"X": "1"}, PASSWORD)
    save_env("proj2", {"Y": "2"}, PASSWORD)
    assert sorted(list_projects()) == ["proj1", "proj2"]


def test_save_env_overwrites_existing():
    save_env("web", {"OLD": "value"}, PASSWORD)
    save_env("web", {"NEW": "value"}, PASSWORD)
    result = load_env("web", PASSWORD)
    assert result == {"NEW": "value"}
    assert "OLD" not in result
