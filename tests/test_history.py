"""Tests for envault.history."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.history import (
    HistoryError,
    HISTORY_LIMIT,
    record_write,
    get_history,
    clear_history,
    list_projects_with_history,
)


@pytest.fixture()
def tmp_vault_dir(tmp_path: Path) -> Path:
    return tmp_path / ".envault"


def test_record_and_get_single_entry(tmp_vault_dir):
    record_write(tmp_vault_dir, "myapp", ["DB_URL", "SECRET"], "2024-01-01T00:00:00")
    history = get_history(tmp_vault_dir, "myapp")
    assert len(history) == 1
    assert history[0]["timestamp"] == "2024-01-01T00:00:00"
    assert history[0]["keys"] == ["DB_URL", "SECRET"]


def test_record_multiple_entries_ordered(tmp_vault_dir):
    record_write(tmp_vault_dir, "proj", ["A"], "2024-01-01T10:00:00")
    record_write(tmp_vault_dir, "proj", ["B"], "2024-01-02T10:00:00")
    history = get_history(tmp_vault_dir, "proj")
    assert len(history) == 2
    assert history[0]["timestamp"] == "2024-01-01T10:00:00"
    assert history[1]["timestamp"] == "2024-01-02T10:00:00"


def test_history_capped_at_limit(tmp_vault_dir):
    for i in range(HISTORY_LIMIT + 5):
        record_write(tmp_vault_dir, "proj", [f"KEY_{i}"], f"2024-01-{i+1:02d}T00:00:00")
    history = get_history(tmp_vault_dir, "proj")
    assert len(history) == HISTORY_LIMIT
    # oldest entries are dropped
    assert history[0]["keys"] == ["KEY_5"]


def test_get_history_missing_project_returns_empty(tmp_vault_dir):
    result = get_history(tmp_vault_dir, "nonexistent")
    assert result == []


def test_clear_history_removes_entries(tmp_vault_dir):
    record_write(tmp_vault_dir, "proj", ["X"], "2024-01-01T00:00:00")
    clear_history(tmp_vault_dir, "proj")
    assert get_history(tmp_vault_dir, "proj") == []


def test_clear_history_missing_project_is_noop(tmp_vault_dir):
    # should not raise
    clear_history(tmp_vault_dir, "ghost")


def test_list_projects_with_history(tmp_vault_dir):
    record_write(tmp_vault_dir, "alpha", ["K"], "2024-01-01T00:00:00")
    record_write(tmp_vault_dir, "beta", ["K"], "2024-01-01T00:00:00")
    projects = list_projects_with_history(tmp_vault_dir)
    assert projects == ["alpha", "beta"]


def test_record_empty_project_raises(tmp_vault_dir):
    with pytest.raises(HistoryError):
        record_write(tmp_vault_dir, "", ["KEY"], "2024-01-01T00:00:00")


def test_keys_stored_sorted(tmp_vault_dir):
    record_write(tmp_vault_dir, "proj", ["ZEBRA", "ALPHA", "MIDDLE"], "2024-01-01T00:00:00")
    history = get_history(tmp_vault_dir, "proj")
    assert history[0]["keys"] == ["ALPHA", "MIDDLE", "ZEBRA"]
