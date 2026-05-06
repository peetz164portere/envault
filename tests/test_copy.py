"""Tests for envault.copy module."""

import pytest

from envault.vault import save_env, load_env
from envault.copy import copy_project, merge_projects, CopyError


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, data, password, vault_dir):
    save_env(project, data, password, vault_dir=vault_dir)


def test_copy_project_all_keys(tmp_vault_dir):
    _save("alpha", {"A": "1", "B": "2"}, "pw", tmp_vault_dir)
    copied = copy_project("alpha", "pw", "beta", "newpw", vault_dir=tmp_vault_dir)
    assert copied == {"A": "1", "B": "2"}
    result = load_env("beta", "newpw", vault_dir=tmp_vault_dir)
    assert result == {"A": "1", "B": "2"}


def test_copy_project_selected_keys(tmp_vault_dir):
    _save("alpha", {"A": "1", "B": "2", "C": "3"}, "pw", tmp_vault_dir)
    copied = copy_project(
        "alpha", "pw", "beta", "newpw", keys=["A", "C"], vault_dir=tmp_vault_dir
    )
    assert copied == {"A": "1", "C": "3"}
    result = load_env("beta", "newpw", vault_dir=tmp_vault_dir)
    assert "B" not in result
    assert result["A"] == "1"
    assert result["C"] == "3"


def test_copy_project_merges_into_existing_dst(tmp_vault_dir):
    _save("alpha", {"NEW": "val"}, "pw", tmp_vault_dir)
    _save("beta", {"EXISTING": "old"}, "bpw", tmp_vault_dir)
    copy_project("alpha", "pw", "beta", "bpw", vault_dir=tmp_vault_dir)
    result = load_env("beta", "bpw", vault_dir=tmp_vault_dir)
    assert result["EXISTING"] == "old"
    assert result["NEW"] == "val"


def test_copy_project_missing_source_raises(tmp_vault_dir):
    with pytest.raises(CopyError, match="does not exist"):
        copy_project("ghost", "pw", "beta", "newpw", vault_dir=tmp_vault_dir)


def test_copy_project_missing_key_raises(tmp_vault_dir):
    _save("alpha", {"A": "1"}, "pw", tmp_vault_dir)
    with pytest.raises(CopyError, match="MISSING"):
        copy_project(
            "alpha", "pw", "beta", "newpw", keys=["MISSING"], vault_dir=tmp_vault_dir
        )


def test_copy_project_wrong_src_password_raises(tmp_vault_dir):
    _save("alpha", {"A": "1"}, "correct", tmp_vault_dir)
    with pytest.raises(Exception):
        copy_project("alpha", "wrong", "beta", "newpw", vault_dir=tmp_vault_dir)


def test_merge_projects_copies_everything(tmp_vault_dir):
    _save("src", {"X": "10", "Y": "20"}, "pw", tmp_vault_dir)
    merge_projects("src", "pw", "dst", "dpw", vault_dir=tmp_vault_dir)
    result = load_env("dst", "dpw", vault_dir=tmp_vault_dir)
    assert result == {"X": "10", "Y": "20"}
