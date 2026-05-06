"""Tests for envault.snapshot."""

from __future__ import annotations

import pytest

from envault.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
)
from envault.vault import load_env, save_env


@pytest.fixture()
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432"}
PASSWORD = "hunter2"
PROJECT = "myapp"


def test_save_snapshot_creates_restorable_snapshot(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "v1", PASSWORD, vault_dir=tmp_vault_dir)

    # Overwrite current env
    save_env(PROJECT, {"DB_HOST": "remotehost"}, PASSWORD, vault_dir=tmp_vault_dir)

    restored = restore_snapshot(PROJECT, "v1", PASSWORD, vault_dir=tmp_vault_dir)
    assert restored == ENV


def test_restore_snapshot_updates_project(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "backup", PASSWORD, vault_dir=tmp_vault_dir)

    save_env(PROJECT, {"NEW_KEY": "new_val"}, PASSWORD, vault_dir=tmp_vault_dir)
    restore_snapshot(PROJECT, "backup", PASSWORD, vault_dir=tmp_vault_dir)

    current = load_env(PROJECT, PASSWORD, vault_dir=tmp_vault_dir)
    assert current == ENV


def test_restore_missing_snapshot_raises(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(PROJECT, "ghost", PASSWORD, vault_dir=tmp_vault_dir)


def test_list_snapshots_returns_names(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "v1", PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "v2", PASSWORD, vault_dir=tmp_vault_dir)

    names = list_snapshots(PROJECT, PASSWORD, vault_dir=tmp_vault_dir)
    assert "v1" in names
    assert "v2" in names


def test_list_snapshots_empty_when_none(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    assert list_snapshots(PROJECT, PASSWORD, vault_dir=tmp_vault_dir) == []


def test_list_snapshots_scoped_to_project(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    save_env("other", {"X": "1"}, PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "snap1", PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot("other", "snap2", PASSWORD, vault_dir=tmp_vault_dir)

    names = list_snapshots(PROJECT, PASSWORD, vault_dir=tmp_vault_dir)
    assert names == ["snap1"]


def test_delete_snapshot_removes_it(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    save_snapshot(PROJECT, "v1", PASSWORD, vault_dir=tmp_vault_dir)
    delete_snapshot(PROJECT, "v1", vault_dir=tmp_vault_dir)

    assert list_snapshots(PROJECT, PASSWORD, vault_dir=tmp_vault_dir) == []


def test_delete_missing_snapshot_raises(tmp_vault_dir):
    save_env(PROJECT, ENV, PASSWORD, vault_dir=tmp_vault_dir)
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(PROJECT, "nonexistent", vault_dir=tmp_vault_dir)
