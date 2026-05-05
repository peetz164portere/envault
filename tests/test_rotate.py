"""Tests for password rotation."""

import pytest
from envault.vault import save_env, load_env
from envault.rotate import rotate_project, rotate_all, RotationError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_rotate_project_allows_load_with_new_password(tmp_vault_dir):
    save_env("myapp", {"KEY": "value"}, "old-pass", vault_dir=tmp_vault_dir)
    rotate_project("myapp", "old-pass", "new-pass", vault_dir=tmp_vault_dir)
    result = load_env("myapp", "new-pass", vault_dir=tmp_vault_dir)
    assert result == {"KEY": "value"}


def test_rotate_project_old_password_no_longer_works(tmp_vault_dir):
    save_env("myapp", {"KEY": "value"}, "old-pass", vault_dir=tmp_vault_dir)
    rotate_project("myapp", "old-pass", "new-pass", vault_dir=tmp_vault_dir)
    with pytest.raises(Exception):
        load_env("myapp", "old-pass", vault_dir=tmp_vault_dir)


def test_rotate_project_wrong_old_password_raises(tmp_vault_dir):
    save_env("myapp", {"KEY": "value"}, "correct", vault_dir=tmp_vault_dir)
    with pytest.raises(RotationError, match="old password"):
        rotate_project("myapp", "wrong", "new-pass", vault_dir=tmp_vault_dir)


def test_rotate_project_missing_project_raises(tmp_vault_dir):
    with pytest.raises(RotationError):
        rotate_project("ghost", "old", "new", vault_dir=tmp_vault_dir)


def test_rotate_all_rotates_multiple_projects(tmp_vault_dir):
    save_env("app1", {"A": "1"}, "shared", vault_dir=tmp_vault_dir)
    save_env("app2", {"B": "2"}, "shared", vault_dir=tmp_vault_dir)
    results = rotate_all("shared", "newshared", vault_dir=tmp_vault_dir)
    assert results["app1"] == "ok"
    assert results["app2"] == "ok"
    assert load_env("app1", "newshared", vault_dir=tmp_vault_dir) == {"A": "1"}
    assert load_env("app2", "newshared", vault_dir=tmp_vault_dir) == {"B": "2"}


def test_rotate_all_partial_failure_continues(tmp_vault_dir):
    save_env("good", {"X": "1"}, "pass", vault_dir=tmp_vault_dir)
    save_env("bad", {"Y": "2"}, "different", vault_dir=tmp_vault_dir)
    results = rotate_all("pass", "newpass", vault_dir=tmp_vault_dir)
    assert results["good"] == "ok"
    assert results["bad"] != "ok"
