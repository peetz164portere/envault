"""Tests for envault.cli_backup module."""

import sys
import zipfile
import pytest
from pathlib import Path
from types import SimpleNamespace

from envault.vault import save_env
from envault.backup import create_backup
from envault.cli_backup import cmd_backup_create, cmd_backup_restore, cmd_backup_list


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_args(vault_dir, **kwargs):
    return SimpleNamespace(vault_dir=str(vault_dir), **kwargs)


def _save(vault_dir, project, password, env):
    save_env(project, env, password, vault_dir=vault_dir)


def test_cmd_backup_create_prints_path(tmp_vault_dir, capsys):
    _save(tmp_vault_dir, "proj", "pw", {"A": "1"})
    args = _make_args(tmp_vault_dir, output=None)
    cmd_backup_create(args)
    out = capsys.readouterr().out
    assert "Backup created" in out


def test_cmd_backup_create_no_vaults_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, output=None)
    with pytest.raises(SystemExit) as exc:
        cmd_backup_create(args)
    assert exc.value.code == 1
    assert "Error" in capsys.readouterr().err


def test_cmd_backup_restore_prints_projects(tmp_vault_dir, tmp_path, capsys):
    _save(tmp_vault_dir, "proj", "pw", {"A": "1"})
    backup = create_backup(tmp_vault_dir)
    restore_dir = tmp_path / "r"
    restore_dir.mkdir()
    args = _make_args(restore_dir, backup_file=str(backup), overwrite=False)
    cmd_backup_restore(args)
    out = capsys.readouterr().out
    assert "proj" in out


def test_cmd_backup_restore_conflict_exits(tmp_vault_dir, capsys):
    _save(tmp_vault_dir, "proj", "pw", {"A": "1"})
    backup = create_backup(tmp_vault_dir)
    args = _make_args(tmp_vault_dir, backup_file=str(backup), overwrite=False)
    with pytest.raises(SystemExit) as exc:
        cmd_backup_restore(args)
    assert exc.value.code == 1


def test_cmd_backup_restore_missing_file_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, backup_file="/no/such/file.zip", overwrite=False)
    with pytest.raises(SystemExit) as exc:
        cmd_backup_restore(args)
    assert exc.value.code == 1


def test_cmd_backup_list_shows_backups(tmp_vault_dir, capsys):
    _save(tmp_vault_dir, "proj", "pw", {"A": "1"})
    create_backup(tmp_vault_dir, output_path=tmp_vault_dir / "backup_20240101T000000Z.zip")
    args = _make_args(tmp_vault_dir)
    cmd_backup_list(args)
    out = capsys.readouterr().out
    assert "backup_20240101T000000Z.zip" in out


def test_cmd_backup_list_empty(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir)
    cmd_backup_list(args)
    out = capsys.readouterr().out
    assert "No backups" in out
