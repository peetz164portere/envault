"""Tests for envault.diff module."""

import pytest
from envault.vault import save_env
from envault.snapshot import save_snapshot
from envault.diff import diff_snapshots, diff_snapshot_vs_current, DiffError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _save(project, password, env, vault_dir):
    save_env(project, password, env, vault_dir=vault_dir)


def test_diff_snapshots_detects_changed_key(tmp_vault_dir):
    _save("proj", "pw", {"KEY": "v1", "OTHER": "same"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"KEY": "v2", "OTHER": "same"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap2", vault_dir=tmp_vault_dir)

    entries = diff_snapshots("proj", "pw", "snap1", "snap2", vault_dir=tmp_vault_dir)
    assert len(entries) == 1
    assert entries[0].key == "KEY"
    assert entries[0].old_value == "v1"
    assert entries[0].new_value == "v2"
    assert entries[0].status == "changed"


def test_diff_snapshots_detects_added_key(tmp_vault_dir):
    _save("proj", "pw", {"A": "1"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"A": "1", "B": "2"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap2", vault_dir=tmp_vault_dir)

    entries = diff_snapshots("proj", "pw", "snap1", "snap2", vault_dir=tmp_vault_dir)
    assert len(entries) == 1
    assert entries[0].key == "B"
    assert entries[0].status == "added"
    assert entries[0].old_value is None


def test_diff_snapshots_detects_removed_key(tmp_vault_dir):
    _save("proj", "pw", {"A": "1", "B": "gone"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"A": "1"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap2", vault_dir=tmp_vault_dir)

    entries = diff_snapshots("proj", "pw", "snap1", "snap2", vault_dir=tmp_vault_dir)
    assert len(entries) == 1
    assert entries[0].key == "B"
    assert entries[0].status == "removed"
    assert entries[0].new_value is None


def test_diff_snapshots_no_changes(tmp_vault_dir):
    _save("proj", "pw", {"X": "same"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)
    save_snapshot("proj", "pw", "snap2", vault_dir=tmp_vault_dir)

    entries = diff_snapshots("proj", "pw", "snap1", "snap2", vault_dir=tmp_vault_dir)
    assert entries == []


def test_diff_snapshot_vs_current(tmp_vault_dir):
    _save("proj", "pw", {"K": "old"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "baseline", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"K": "new", "EXTRA": "yes"}, tmp_vault_dir)

    entries = diff_snapshot_vs_current("proj", "pw", "baseline", vault_dir=tmp_vault_dir)
    keys = {e.key: e for e in entries}
    assert "K" in keys and keys["K"].new_value == "new"
    assert "EXTRA" in keys and keys["EXTRA"].status == "added"


def test_diff_missing_snapshot_raises(tmp_vault_dir):
    _save("proj", "pw", {"K": "v"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)

    with pytest.raises(DiffError):
        diff_snapshots("proj", "pw", "snap1", "nonexistent", vault_dir=tmp_vault_dir)


def test_diff_missing_both_snapshots_raises(tmp_vault_dir):
    _save("proj", "pw", {"K": "v"}, tmp_vault_dir)

    with pytest.raises(DiffError):
        diff_snapshots("proj", "pw", "ghost1", "ghost2", vault_dir=tmp_vault_dir)
