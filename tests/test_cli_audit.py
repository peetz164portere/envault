"""Tests for envault.cli_audit module."""

import argparse
import pytest

from envault.audit import record_event
from envault.cli_audit import cmd_audit_log, cmd_audit_clear, register_audit_commands


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _make_args(**kwargs):
    ns = argparse.Namespace()
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_audit_log_empty(tmp_vault_dir, capsys):
    args = _make_args(project=None)
    cmd_audit_log(args, vault_dir=tmp_vault_dir)
    out = capsys.readouterr().out
    assert "No audit events found" in out


def test_audit_log_shows_events(tmp_vault_dir, capsys):
    record_event("set", "myproj", vault_dir=tmp_vault_dir)
    record_event("get", "myproj", vault_dir=tmp_vault_dir)
    args = _make_args(project=None)
    cmd_audit_log(args, vault_dir=tmp_vault_dir)
    out = capsys.readouterr().out
    assert "set" in out
    assert "get" in out
    assert "myproj" in out


def test_audit_log_filtered_by_project(tmp_vault_dir, capsys):
    record_event("set", "alpha", vault_dir=tmp_vault_dir)
    record_event("set", "beta", vault_dir=tmp_vault_dir)
    args = _make_args(project="alpha")
    cmd_audit_log(args, vault_dir=tmp_vault_dir)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" not in out


def test_audit_clear_with_yes_flag(tmp_vault_dir, capsys):
    record_event("set", "proj", vault_dir=tmp_vault_dir)
    args = _make_args(yes=True)
    cmd_audit_clear(args, vault_dir=tmp_vault_dir)
    out = capsys.readouterr().out
    assert "cleared" in out.lower()
    from envault.audit import read_events
    assert read_events(vault_dir=tmp_vault_dir) == []


def test_audit_clear_aborted(tmp_vault_dir, capsys, monkeypatch):
    record_event("set", "proj", vault_dir=tmp_vault_dir)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    args = _make_args(yes=False)
    cmd_audit_clear(args, vault_dir=tmp_vault_dir)
    out = capsys.readouterr().out
    assert "Aborted" in out
    from envault.audit import read_events
    assert len(read_events(vault_dir=tmp_vault_dir)) == 1


def test_register_audit_commands_creates_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    register_audit_commands(subparsers)
    args = parser.parse_args(["audit", "log"])
    assert args.cmd == "audit"
