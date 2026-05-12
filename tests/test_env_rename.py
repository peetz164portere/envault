"""Tests for envault.env_rename."""

from __future__ import annotations

import pytest

from envault.env_rename import RenameError, rename_key, rename_project
from envault.vault import load_env, save_env, project_exists


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _save(project, env, password="pass"):
    save_env(project, env, password)


# --- rename_key ---

def test_rename_key_updates_name(tmp_vault_dir):
    _save("proj", {"OLD_KEY": "val"})
    rename_key("proj", "OLD_KEY", "NEW_KEY", "pass")
    env = load_env("proj", "pass")
    assert "NEW_KEY" in env
    assert env["NEW_KEY"] == "val"
    assert "OLD_KEY" not in env


def test_rename_key_preserves_other_keys(tmp_vault_dir):
    _save("proj", {"A": "1", "B": "2"})
    rename_key("proj", "A", "A_RENAMED", "pass")
    env = load_env("proj", "pass")
    assert env["B"] == "2"
    assert env["A_RENAMED"] == "1"


def test_rename_key_missing_project_raises(tmp_vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_key("ghost", "K", "K2", "pass")


def test_rename_key_missing_old_key_raises(tmp_vault_dir):
    _save("proj", {"EXISTING": "v"})
    with pytest.raises(RenameError, match="not found"):
        rename_key("proj", "MISSING", "NEW", "pass")


def test_rename_key_conflict_raises(tmp_vault_dir):
    _save("proj", {"A": "1", "B": "2"})
    with pytest.raises(RenameError, match="already exists"):
        rename_key("proj", "A", "B", "pass")


def test_rename_key_identical_names_raises(tmp_vault_dir):
    _save("proj", {"A": "1"})
    with pytest.raises(RenameError, match="identical"):
        rename_key("proj", "A", "A", "pass")


def test_rename_key_wrong_password_raises(tmp_vault_dir):
    """Ensure a bad password surfaces an error rather than silently succeeding."""
    _save("proj", {"KEY": "value"})
    with pytest.raises(Exception):
        rename_key("proj", "KEY", "NEW_KEY", "wrongpass")


# --- rename_project ---

def test_rename_project_creates_new_and_removes_old(tmp_vault_dir):
    _save("alpha", {"X": "10"})
    rename_project("alpha", "beta", "pass")
    assert project_exists("beta")
    assert not project_exists("alpha")


def test_rename_project_data_intact(tmp_vault_dir):
    _save("alpha", {"X": "10", "Y": "20"})
    rename_project("alpha", "beta", "pass")
    env = load_env("beta", "pass")
    assert env == {"X": "10", "Y": "20"}


def test_rename_project_with_new_password(tmp_vault_dir):
    _save("alpha", {"K": "v"})
    rename_project("alpha", "beta", "pass", new_password="newpass")
    env = load_env("beta", "newpass")
    assert env["K"] == "v"


def test_rename_project_with_new_password_old_password_invalid(tmp_vault_dir):
    """After re-encrypting with a new password, the old password should no longer work."""
    _save("alpha", {"K": "v"})
    rename_project("alpha", "beta", "pass", new_password="newpass")
    with pytest.raises(Exception):
        load_env("beta", "pass")


def test_rename_project_missing_raises(tmp_vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_project("ghost", "new", "pass")


def test_rename_project_destination_exists_raises(tmp_vault_dir):
    _save("alpha", {"A": "1"})
    _save("beta", {"B": "2"})
    with pytest.raises(RenameError, match="already exists"):
        rename_project("alpha", "beta", "pass")
