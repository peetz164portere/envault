"""Tests for envault.env_clone."""

import pytest

from envault.env_clone import CloneError, clone_project, clone_with_filter
from envault.vault import load_env, project_exists


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, env, password, vault_dir):
    from envault.vault import save_env
    save_env(project, env, password, vault_dir=vault_dir)


# ---------------------------------------------------------------------------
# clone_project
# ---------------------------------------------------------------------------

def test_clone_project_copies_all_keys(tmp_vault_dir):
    _save("alpha", {"A": "1", "B": "2"}, "pass", tmp_vault_dir)
    clone_project("alpha", "beta", "pass", vault_dir=tmp_vault_dir)
    assert load_env("beta", "pass", vault_dir=tmp_vault_dir) == {"A": "1", "B": "2"}


def test_clone_project_uses_new_password(tmp_vault_dir):
    _save("alpha", {"KEY": "val"}, "old", tmp_vault_dir)
    clone_project("alpha", "beta", "old", dst_password="new", vault_dir=tmp_vault_dir)
    assert load_env("beta", "new", vault_dir=tmp_vault_dir) == {"KEY": "val"}


def test_clone_project_old_password_invalid_for_dst(tmp_vault_dir):
    _save("alpha", {"KEY": "val"}, "old", tmp_vault_dir)
    clone_project("alpha", "beta", "old", dst_password="new", vault_dir=tmp_vault_dir)
    with pytest.raises(Exception):
        load_env("beta", "old", vault_dir=tmp_vault_dir)


def test_clone_project_missing_src_raises(tmp_vault_dir):
    with pytest.raises(CloneError, match="does not exist"):
        clone_project("ghost", "beta", "pass", vault_dir=tmp_vault_dir)


def test_clone_project_existing_dst_raises_without_overwrite(tmp_vault_dir):
    _save("alpha", {"K": "v"}, "pass", tmp_vault_dir)
    _save("beta", {"K": "v"}, "pass", tmp_vault_dir)
    with pytest.raises(CloneError, match="already exists"):
        clone_project("alpha", "beta", "pass", vault_dir=tmp_vault_dir)


def test_clone_project_overwrite_replaces_dst(tmp_vault_dir):
    _save("alpha", {"NEW": "data"}, "pass", tmp_vault_dir)
    _save("beta", {"OLD": "stuff"}, "pass", tmp_vault_dir)
    clone_project("alpha", "beta", "pass", overwrite=True, vault_dir=tmp_vault_dir)
    assert load_env("beta", "pass", vault_dir=tmp_vault_dir) == {"NEW": "data"}


# ---------------------------------------------------------------------------
# clone_with_filter
# ---------------------------------------------------------------------------

def test_clone_with_filter_copies_subset(tmp_vault_dir):
    _save("src", {"A": "1", "B": "2", "C": "3"}, "pass", tmp_vault_dir)
    result = clone_with_filter("src", "dst", "pass", ["A", "C"], vault_dir=tmp_vault_dir)
    assert result == {"A": "1", "C": "3"}
    assert load_env("dst", "pass", vault_dir=tmp_vault_dir) == {"A": "1", "C": "3"}


def test_clone_with_filter_missing_key_raises(tmp_vault_dir):
    _save("src", {"A": "1"}, "pass", tmp_vault_dir)
    with pytest.raises(CloneError, match="Keys not found"):
        clone_with_filter("src", "dst", "pass", ["A", "NOPE"], vault_dir=tmp_vault_dir)


def test_clone_with_filter_missing_src_raises(tmp_vault_dir):
    with pytest.raises(CloneError, match="does not exist"):
        clone_with_filter("ghost", "dst", "pass", ["K"], vault_dir=tmp_vault_dir)
