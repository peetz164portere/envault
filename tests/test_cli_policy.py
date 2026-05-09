"""Tests for envault/cli_policy.py"""

import sys
import pytest
from types import SimpleNamespace
from envault.cli_policy import cmd_policy_set, cmd_policy_get, cmd_policy_delete
from envault.policy import set_policy, get_policy


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _make_args(vault_dir, **kwargs):
    defaults = {
        "project": "myapp",
        "required": None,
        "forbidden": None,
        "min_password_length": None,
        "vault_dir": vault_dir,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_policy_set_prints_confirmation(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, required="DB_URL,SECRET")
    cmd_policy_set(args)
    out = capsys.readouterr().out
    assert "Policy updated" in out
    assert "myapp" in out


def test_cmd_policy_set_stores_required_keys(tmp_vault_dir):
    args = _make_args(tmp_vault_dir, required="DB_URL,SECRET")
    cmd_policy_set(args)
    policy = get_policy(tmp_vault_dir, "myapp")
    assert "DB_URL" in policy["required_keys"]
    assert "SECRET" in policy["required_keys"]


def test_cmd_policy_set_stores_forbidden_keys(tmp_vault_dir):
    args = _make_args(tmp_vault_dir, forbidden="DEBUG,TEST_MODE")
    cmd_policy_set(args)
    policy = get_policy(tmp_vault_dir, "myapp")
    assert "DEBUG" in policy["forbidden_keys"]


def test_cmd_policy_set_invalid_min_length_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, min_password_length=0)
    with pytest.raises(SystemExit):
        cmd_policy_set(args)
    err = capsys.readouterr().err
    assert "Error" in err


def test_cmd_policy_get_shows_policy(tmp_vault_dir, capsys):
    set_policy(tmp_vault_dir, "myapp", required_keys=["DB_URL"], min_password_length=10)
    args = _make_args(tmp_vault_dir)
    cmd_policy_get(args)
    out = capsys.readouterr().out
    assert "DB_URL" in out
    assert "10" in out


def test_cmd_policy_get_no_policy_message(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, project="ghost")
    cmd_policy_get(args)
    out = capsys.readouterr().out
    assert "No policy" in out


def test_cmd_policy_delete_removes_policy(tmp_vault_dir, capsys):
    set_policy(tmp_vault_dir, "myapp", required_keys=["X"])
    args = _make_args(tmp_vault_dir)
    cmd_policy_delete(args)
    out = capsys.readouterr().out
    assert "deleted" in out
    assert get_policy(tmp_vault_dir, "myapp") == {}


def test_cmd_policy_delete_missing_exits(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, project="ghost")
    with pytest.raises(SystemExit):
        cmd_policy_delete(args)
    err = capsys.readouterr().err
    assert "Error" in err
