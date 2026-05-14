"""Tests for envault.env_watch."""

import os
import pytest

from envault.vault import save_env
from envault.env_watch import WatchError, WatchEvent, _diff_envs, watch_project


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, data, password, vault_dir):
    save_env(project, data, password, vault_dir=vault_dir)


# --- _diff_envs unit tests ---

def test_diff_envs_detects_added_key():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    events = _diff_envs(old, new, "proj")
    assert len(events) == 1
    assert events[0].kind == "added"
    assert events[0].key == "B"
    assert events[0].new_value == "2"


def test_diff_envs_detects_removed_key():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    events = _diff_envs(old, new, "proj")
    assert len(events) == 1
    assert events[0].kind == "removed"
    assert events[0].key == "B"
    assert events[0].old_value == "2"


def test_diff_envs_detects_changed_key():
    old = {"A": "1"}
    new = {"A": "99"}
    events = _diff_envs(old, new, "proj")
    assert len(events) == 1
    assert events[0].kind == "changed"
    assert events[0].old_value == "1"
    assert events[0].new_value == "99"


def test_diff_envs_no_changes_returns_empty():
    env = {"A": "1", "B": "2"}
    assert _diff_envs(env, env.copy(), "proj") == []


def test_diff_envs_sets_project_name():
    events = _diff_envs({}, {"X": "y"}, "myproject")
    assert events[0].project == "myproject"


# --- watch_project integration tests ---

def test_watch_project_missing_project_raises(tmp_vault_dir):
    with pytest.raises(WatchError, match="does not exist"):
        watch_project(
            "ghost", "pw", callback=lambda e: None,
            max_polls=1, interval=0, vault_dir=tmp_vault_dir
        )


def test_watch_project_detects_change(tmp_vault_dir):
    _save("proj", {"KEY": "v1"}, "pass", tmp_vault_dir)
    collected = []

    poll_count = 0

    def callback(event):
        collected.append(event)

    # Patch time.sleep to update vault on first poll
    original_sleep = __import__("time").sleep
    call_count = [0]

    import envault.env_watch as ew

    def fake_sleep(t):
        call_count[0] += 1
        if call_count[0] == 1:
            _save("proj", {"KEY": "v2"}, "pass", tmp_vault_dir)

    ew_sleep = ew.__dict__.get("time")
    import unittest.mock as mock
    with mock.patch("envault.env_watch.time.sleep", side_effect=fake_sleep):
        watch_project(
            "proj", "pass", callback=callback,
            interval=0, max_polls=1, vault_dir=tmp_vault_dir
        )

    assert len(collected) == 1
    assert collected[0].kind == "changed"
    assert collected[0].key == "KEY"
    assert collected[0].new_value == "v2"
