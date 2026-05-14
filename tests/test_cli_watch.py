"""Tests for envault.cli_watch."""

import sys
import pytest
import unittest.mock as mock

from envault.vault import save_env
from envault.cli_watch import cmd_watch, _format_event, register_watch_commands
from envault.env_watch import WatchEvent


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _make_args(**kw):
    defaults = dict(project="proj", password="pass", interval=0.0, vault_dir=None)
    defaults.update(kw)
    return _Args(**defaults)


def _save(project, data, password, vault_dir):
    save_env(project, data, password, vault_dir=vault_dir)


# --- _format_event ---

def test_format_event_added():
    e = WatchEvent("p", "KEY", "added", new_value="val")
    assert "[+]" in _format_event(e)
    assert "KEY" in _format_event(e)


def test_format_event_removed():
    e = WatchEvent("p", "KEY", "removed", old_value="old")
    assert "[-]" in _format_event(e)


def test_format_event_changed():
    e = WatchEvent("p", "KEY", "changed", old_value="a", new_value="b")
    assert "[~]" in _format_event(e)
    assert "->" in _format_event(e)


# --- cmd_watch ---

def test_cmd_watch_missing_project_exits(tmp_vault_dir, capsys):
    args = _make_args(project="ghost", vault_dir=tmp_vault_dir)
    with pytest.raises(SystemExit) as exc:
        cmd_watch(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_watch_calls_watch_project(tmp_vault_dir, capsys):
    _save("proj", {"K": "v"}, "pass", tmp_vault_dir)
    args = _make_args(project="proj", password="pass", vault_dir=tmp_vault_dir)

    with mock.patch("envault.cli_watch.watch_project") as mocked:
        cmd_watch(args)
        mocked.assert_called_once()
        call_kwargs = mocked.call_args
        assert call_kwargs[0][0] == "proj"
        assert call_kwargs[0][1] == "pass"


def test_cmd_watch_keyboard_interrupt_exits_cleanly(tmp_vault_dir, capsys):
    _save("proj", {"K": "v"}, "pass", tmp_vault_dir)
    args = _make_args(project="proj", password="pass", vault_dir=tmp_vault_dir)

    with mock.patch("envault.cli_watch.watch_project", side_effect=KeyboardInterrupt):
        cmd_watch(args)  # should not raise
    out = capsys.readouterr().out
    assert "stopped" in out.lower()


def test_register_watch_commands_adds_subparser():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_watch_commands(sub)
    parsed = parser.parse_args(["watch", "myproj", "--password", "s3cr3t"])
    assert parsed.project == "myproj"
    assert parsed.password == "s3cr3t"
    assert parsed.interval == 2.0
