"""Tests for rotate CLI commands."""

import pytest
from unittest.mock import patch
from envault.vault import save_env, load_env
from envault.cli_rotate import cmd_rotate


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _make_args(project=None, all_flag=False, vault_dir=None):
    class Args:
        pass
    a = Args()
    a.project = project
    a.all = all_flag
    a.vault_dir = vault_dir
    return a


def test_cmd_rotate_single_project(tmp_vault_dir):
    save_env("proj", {"K": "v"}, "oldpass", vault_dir=tmp_vault_dir)
    args = _make_args(project="proj", vault_dir=tmp_vault_dir)
    with patch("getpass.getpass", side_effect=["oldpass", "newpass", "newpass"]):
        rc = cmd_rotate(args)
    assert rc == 0
    assert load_env("proj", "newpass", vault_dir=tmp_vault_dir) == {"K": "v"}


def test_cmd_rotate_password_mismatch(tmp_vault_dir):
    save_env("proj", {"K": "v"}, "oldpass", vault_dir=tmp_vault_dir)
    args = _make_args(project="proj", vault_dir=tmp_vault_dir)
    with patch("getpass.getpass", side_effect=["oldpass", "newpass", "wrong"]):
        rc = cmd_rotate(args)
    assert rc == 1


def test_cmd_rotate_wrong_old_password(tmp_vault_dir):
    save_env("proj", {"K": "v"}, "correct", vault_dir=tmp_vault_dir)
    args = _make_args(project="proj", vault_dir=tmp_vault_dir)
    with patch("getpass.getpass", side_effect=["wrong", "newpass", "newpass"]):
        rc = cmd_rotate(args)
    assert rc == 1


def test_cmd_rotate_all(tmp_vault_dir):
    save_env("a", {"X": "1"}, "pass", vault_dir=tmp_vault_dir)
    save_env("b", {"Y": "2"}, "pass", vault_dir=tmp_vault_dir)
    args = _make_args(all_flag=True, vault_dir=tmp_vault_dir)
    with patch("getpass.getpass", side_effect=["pass", "newpass", "newpass"]):
        rc = cmd_rotate(args)
    assert rc == 0


def test_cmd_rotate_no_project_no_all(tmp_vault_dir):
    args = _make_args(vault_dir=tmp_vault_dir)
    with patch("getpass.getpass", side_effect=["old", "new", "new"]):
        rc = cmd_rotate(args)
    assert rc == 1
