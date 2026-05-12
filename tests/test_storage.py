"""Tests for envault.storage — vault file persistence."""

import pytest

from envault import storage
from envault.storage import (
    delete_vault,
    list_vaults,
    read_vault,
    vault_exists,
    write_vault,
)


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temp directory for each test."""
    monkeypatch.setattr(storage, "VAULT_DIR", tmp_path / "vaults")


def test_write_and_read_vault():
    write_vault("myproject", "encrypted_blob")
    result = read_vault("myproject")
    assert result == "encrypted_blob"


def test_vault_exists_after_write():
    assert not vault_exists("alpha")
    write_vault("alpha", "data")
    assert vault_exists("alpha")


def test_read_vault_missing_raises():
    with pytest.raises(FileNotFoundError, match="no vault found" ):
        read_vault("ghost")


def test_delete_vault_removes_file():
    write_vault("beta", "somedata")
    assert vault_exists("beta")
    delete_vault("beta")
    assert not vault_exists("beta")


def test_delete_vault_missing_raises():
    with pytest.raises(FileNotFoundError):
        delete_vault("nonexistent")


def test_list_vaults_empty():
    assert list_vaults() == []


def test_list_vaults_returns_project_names():
    write_vault("proj_a", "d1")
    write_vault("proj_b", "d2")
    names = list_vaults()
    assert sorted(names) == ["proj_a", "proj_b"]


def test_write_vault_overwrites_existing():
    write_vault("dup", "first")
    write_vault("dup", "second")
    assert read_vault("dup") == "second"


def test_list_vaults_does_not_include_deleted():
    """Ensure deleted vaults no longer appear in list_vaults output."""
    write_vault("keep", "data1")
    write_vault("remove", "data2")
    delete_vault("remove")
    names = list_vaults()
    assert "keep" in names
    assert "remove" not in names
