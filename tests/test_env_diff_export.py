"""Tests for envault.env_diff_export."""

from __future__ import annotations

import json
import os
import pytest

from envault.vault import save_env
from envault.snapshot import save_snapshot
from envault.env_diff_export import (
    DiffExportError,
    export_diff_to_string,
    export_snapshots_diff,
    export_snapshot_vs_current,
)
from envault.diff import DiffEntry


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, password, data, vault_dir):
    save_env(project, password, data, vault_dir=vault_dir)


# --- export_diff_to_string ---

def test_export_diff_text_added():
    entries = [DiffEntry(key="FOO", status="added", old_value=None, new_value="bar")]
    out = export_diff_to_string(entries, fmt="text")
    assert "+ FOO=bar" in out


def test_export_diff_text_removed():
    entries = [DiffEntry(key="X", status="removed", old_value="old", new_value=None)]
    out = export_diff_to_string(entries, fmt="text")
    assert "- X=old" in out


def test_export_diff_text_changed():
    entries = [DiffEntry(key="K", status="changed", old_value="a", new_value="b")]
    out = export_diff_to_string(entries, fmt="text")
    assert "~ K" in out
    assert "'a'" in out
    assert "'b'" in out


def test_export_diff_text_empty():
    out = export_diff_to_string([], fmt="text")
    assert "No differences" in out


def test_export_diff_json():
    entries = [DiffEntry(key="A", status="added", old_value=None, new_value="1")]
    out = export_diff_to_string(entries, fmt="json")
    parsed = json.loads(out)
    assert len(parsed) == 1
    assert parsed[0]["key"] == "A"
    assert parsed[0]["status"] == "added"


def test_export_diff_csv():
    entries = [DiffEntry(key="B", status="removed", old_value="v", new_value=None)]
    out = export_diff_to_string(entries, fmt="csv")
    assert "key,status,old,new" in out
    assert "B" in out
    assert "removed" in out


def test_export_diff_unknown_format_raises():
    with pytest.raises(DiffExportError, match="Unknown format"):
        export_diff_to_string([], fmt="xml")  # type: ignore


# --- export_snapshots_diff ---

def test_export_snapshots_diff_text(tmp_vault_dir):
    _save("proj", "pw", {"A": "1"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap1", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"A": "2", "B": "new"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "snap2", vault_dir=tmp_vault_dir)
    out = export_snapshots_diff("proj", "pw", "snap1", "snap2", fmt="text", vault_dir=tmp_vault_dir)
    assert "A" in out
    assert "B" in out


def test_export_snapshots_diff_json(tmp_vault_dir):
    _save("proj", "pw", {"X": "10"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "s1", vault_dir=tmp_vault_dir)
    _save("proj", "pw", {"X": "20"}, tmp_vault_dir)
    save_snapshot("proj", "pw", "s2", vault_dir=tmp_vault_dir)
    out = export_snapshots_diff("proj", "pw", "s1", "s2", fmt="json", vault_dir=tmp_vault_dir)
    data = json.loads(out)
    assert any(d["key"] == "X" for d in data)


# --- export_snapshot_vs_current ---

def test_export_snapshot_vs_current_detects_new_key(tmp_vault_dir):
    _save("p", "pw", {"K": "v"}, tmp_vault_dir)
    save_snapshot("p", "pw", "base", vault_dir=tmp_vault_dir)
    _save("p", "pw", {"K": "v", "NEW": "val"}, tmp_vault_dir)
    out = export_snapshot_vs_current("p", "pw", "base", fmt="text", vault_dir=tmp_vault_dir)
    assert "NEW" in out
