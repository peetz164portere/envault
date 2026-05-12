"""Tests for envault.cli_compress."""

import sys
import pytest
from unittest.mock import patch
from envault.vault import save_env
import envault.storage as storage
from envault.cli_compress import cmd_compress_show, cmd_compress_ratio


@pytest.fixture
def tmp_vault_dir(tmp_path):
    storage.VAULT_DIR = str(tmp_path)
    yield str(tmp_path)
    storage.VAULT_DIR = None


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _make_args(**kwargs):
    defaults = {"vault_dir": None}
    defaults.update(kwargs)
    return Args(**defaults)


def _save(project, password, data, tmp_vault_dir):
    storage.VAULT_DIR = tmp_vault_dir
    save_env(project, password, data)


def test_cmd_compress_show_prints_blob(tmp_vault_dir, capsys):
    _save("myapp", "pass", {"KEY": "value"}, tmp_vault_dir)
    args = _make_args(project="myapp", password="pass", vault_dir=tmp_vault_dir)
    cmd_compress_show(args)
    out = capsys.readouterr().out
    assert len(out.strip()) > 0


def test_cmd_compress_show_bad_password_exits(tmp_vault_dir):
    _save("myapp", "correct", {"KEY": "val"}, tmp_vault_dir)
    args = _make_args(project="myapp", password="wrong", vault_dir=tmp_vault_dir)
    with pytest.raises(SystemExit):
        cmd_compress_show(args)


def test_cmd_compress_show_missing_project_exits(tmp_vault_dir):
    args = _make_args(project="ghost", password="x", vault_dir=tmp_vault_dir)
    with pytest.raises(SystemExit):
        cmd_compress_show(args)


def test_cmd_compress_ratio_prints_ratio(tmp_vault_dir, capsys):
    _save("proj", "pw", {"FOO": "bar" * 30}, tmp_vault_dir)
    args = _make_args(project="proj", password="pw", vault_dir=tmp_vault_dir)
    cmd_compress_ratio(args)
    out = capsys.readouterr().out
    assert "compression ratio" in out
    assert "%" in out


def test_cmd_compress_ratio_empty_project_no_ratio(tmp_vault_dir, capsys):
    _save("empty", "pw", {}, tmp_vault_dir)
    args = _make_args(project="empty", password="pw", vault_dir=tmp_vault_dir)
    cmd_compress_ratio(args)
    out = capsys.readouterr().out
    assert "not applicable" in out


def test_cmd_compress_ratio_wrong_password_exits(tmp_vault_dir):
    _save("proj", "correct", {"A": "1"}, tmp_vault_dir)
    args = _make_args(project="proj", password="bad", vault_dir=tmp_vault_dir)
    with pytest.raises(SystemExit):
        cmd_compress_ratio(args)
