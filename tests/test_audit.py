"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import record_event, read_events, clear_events, _audit_log_path


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_record_creates_log_file(tmp_vault_dir):
    record_event("set", "myproject", vault_dir=tmp_vault_dir)
    log_path = _audit_log_path(tmp_vault_dir)
    assert log_path.exists()


def test_record_and_read_single_event(tmp_vault_dir):
    record_event("set", "alpha", success=True, vault_dir=tmp_vault_dir)
    events = read_events(vault_dir=tmp_vault_dir)
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["project"] == "alpha"
    assert events[0]["success"] is True


def test_record_multiple_events(tmp_vault_dir):
    record_event("set", "proj1", vault_dir=tmp_vault_dir)
    record_event("get", "proj1", vault_dir=tmp_vault_dir)
    record_event("remove", "proj2", vault_dir=tmp_vault_dir)
    events = read_events(vault_dir=tmp_vault_dir)
    assert len(events) == 3


def test_filter_by_project(tmp_vault_dir):
    record_event("set", "proj1", vault_dir=tmp_vault_dir)
    record_event("get", "proj2", vault_dir=tmp_vault_dir)
    record_event("get", "proj1", vault_dir=tmp_vault_dir)
    events = read_events(project="proj1", vault_dir=tmp_vault_dir)
    assert len(events) == 2
    assert all(e["project"] == "proj1" for e in events)


def test_event_has_timestamp(tmp_vault_dir):
    record_event("set", "ts_project", vault_dir=tmp_vault_dir)
    events = read_events(vault_dir=tmp_vault_dir)
    assert "timestamp" in events[0]
    assert "Z" in events[0]["timestamp"] or "+" in events[0]["timestamp"]


def test_event_with_detail(tmp_vault_dir):
    record_event("get", "proj", success=False, detail="wrong password", vault_dir=tmp_vault_dir)
    events = read_events(vault_dir=tmp_vault_dir)
    assert events[0]["detail"] == "wrong password"


def test_read_events_no_log_returns_empty(tmp_vault_dir):
    events = read_events(vault_dir=tmp_vault_dir)
    assert events == []


def test_clear_events_removes_log(tmp_vault_dir):
    record_event("set", "proj", vault_dir=tmp_vault_dir)
    clear_events(vault_dir=tmp_vault_dir)
    log_path = _audit_log_path(tmp_vault_dir)
    assert not log_path.exists()


def test_clear_events_no_file_does_not_raise(tmp_vault_dir):
    # Should not raise even if log doesn't exist
    clear_events(vault_dir=tmp_vault_dir)
