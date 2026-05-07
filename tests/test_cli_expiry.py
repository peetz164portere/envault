"""Tests for envault.cli_expiry."""

from __future__ import annotations

import sys
import pytest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from envault.cli_expiry import (
    cmd_expiry_set,
    cmd_expiry_get,
    cmd_expiry_clear,
    cmd_expiry_list,
)
from envault.expiry import set_expiry


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path / "vault")


def _make_args(vault_dir, **kwargs):
    return SimpleNamespace(vault_dir=vault_dir, **kwargs)


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()


def _past() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()


def test_cmd_expiry_set_prints_confirmation(tmp_vault_dir, capsys):
    ts = _future()
    args = _make_args(tmp_vault_dir, project="myapp", expires_at=ts)
    cmd_expiry_set(args)
    out = capsys.readouterr().out
    assert "myapp" in out
    assert ts in out


def test_cmd_expiry_set_invalid_date_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, project="myapp", expires_at="bad-date")
    with pytest.raises(SystemExit):
        cmd_expiry_set(args)
    assert "Error" in capsys.readouterr().err


def test_cmd_expiry_get_shows_date(tmp_vault_dir, capsys):
    ts = _future()
    set_expiry(tmp_vault_dir, "proj", ts)
    args = _make_args(tmp_vault_dir, project="proj")
    cmd_expiry_get(args)
    out = capsys.readouterr().out
    assert ts in out
    assert "EXPIRED" not in out


def test_cmd_expiry_get_shows_expired_flag(tmp_vault_dir, capsys):
    ts = _past()
    set_expiry(tmp_vault_dir, "proj", ts)
    args = _make_args(tmp_vault_dir, project="proj")
    cmd_expiry_get(args)
    out = capsys.readouterr().out
    assert "EXPIRED" in out


def test_cmd_expiry_get_not_set(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, project="ghost")
    cmd_expiry_get(args)
    out = capsys.readouterr().out
    assert "No expiry" in out


def test_cmd_expiry_clear_removes_entry(tmp_vault_dir, capsys):
    set_expiry(tmp_vault_dir, "proj", _future())
    args = _make_args(tmp_vault_dir, project="proj")
    cmd_expiry_clear(args)
    assert "cleared" in capsys.readouterr().out


def test_cmd_expiry_clear_missing_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, project="ghost")
    with pytest.raises(SystemExit):
        cmd_expiry_clear(args)


def test_cmd_expiry_list_shows_all(tmp_vault_dir, capsys):
    set_expiry(tmp_vault_dir, "alpha", _future())
    set_expiry(tmp_vault_dir, "beta", _past())
    args = _make_args(tmp_vault_dir)
    cmd_expiry_list(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
    assert "EXPIRED" in out


def test_cmd_expiry_list_empty(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir)
    cmd_expiry_list(args)
    assert "No expiry" in capsys.readouterr().out
