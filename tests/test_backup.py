"""Tests for envault.backup module."""

import pytest
from pathlib import Path

from envault.vault import save_env, load_env
from envault.backup import (
    BackupError,
    create_backup,
    restore_backup,
    list_backups,
)


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _save(vault_dir, project, password, env):
    save_env(project, env, password, vault_dir=vault_dir)


def test_create_backup_produces_zip(tmp_vault_dir):
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    backup_path = create_backup(tmp_vault_dir)
    assert backup_path.exists()
    assert backup_path.suffix == ".zip"


def test_create_backup_contains_vault_files(tmp_vault_dir):
    import zipfile
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    _save(tmp_vault_dir, "beta", "pw2", {"X": "Y"})
    backup_path = create_backup(tmp_vault_dir)
    with zipfile.ZipFile(backup_path) as zf:
        names = zf.namelist()
    assert "alpha.vault" in names
    assert "beta.vault" in names


def test_create_backup_no_vaults_raises(tmp_vault_dir):
    with pytest.raises(BackupError, match="No vault files"):
        create_backup(tmp_vault_dir)


def test_create_backup_custom_output_path(tmp_vault_dir):
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    out = tmp_vault_dir / "my_backup.zip"
    result = create_backup(tmp_vault_dir, output_path=out)
    assert result == out
    assert out.exists()


def test_restore_backup_round_trip(tmp_vault_dir, tmp_path):
    _save(tmp_vault_dir, "alpha", "secret", {"FOO": "bar"})
    backup_path = create_backup(tmp_vault_dir)

    restore_dir = tmp_path / "restore"
    restore_dir.mkdir()
    restored = restore_backup(restore_dir, backup_path)

    assert "alpha" in restored
    env = load_env("alpha", "secret", vault_dir=restore_dir)
    assert env["FOO"] == "bar"


def test_restore_backup_no_overwrite_raises(tmp_vault_dir):
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    backup_path = create_backup(tmp_vault_dir)
    with pytest.raises(BackupError, match="already exists"):
        restore_backup(tmp_vault_dir, backup_path, overwrite=False)


def test_restore_backup_overwrite_succeeds(tmp_vault_dir):
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    backup_path = create_backup(tmp_vault_dir)
    restored = restore_backup(tmp_vault_dir, backup_path, overwrite=True)
    assert "alpha" in restored


def test_restore_backup_missing_file_raises(tmp_vault_dir):
    with pytest.raises(BackupError, match="not found"):
        restore_backup(tmp_vault_dir, tmp_vault_dir / "nonexistent.zip")


def test_list_backups_returns_sorted(tmp_vault_dir):
    _save(tmp_vault_dir, "alpha", "pw", {"K": "V"})
    create_backup(tmp_vault_dir, output_path=tmp_vault_dir / "backup_20240101T000000Z.zip")
    create_backup(tmp_vault_dir, output_path=tmp_vault_dir / "backup_20240202T000000Z.zip")
    backups = list_backups(tmp_vault_dir)
    assert backups == sorted(backups)
    assert len(backups) == 2


def test_list_backups_empty(tmp_vault_dir):
    assert list_backups(tmp_vault_dir) == []
