"""Tests for envault.acl access control list module."""

import pytest
from envault.acl import (
    add_user, remove_user, list_users, is_allowed, clear_acl, ACLError
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path / "vault")


def test_add_user_creates_entry(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    assert "alice" in list_users(tmp_vault_dir, "myproject")


def test_add_user_idempotent(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    add_user(tmp_vault_dir, "myproject", "alice")
    assert list_users(tmp_vault_dir, "myproject").count("alice") == 1


def test_add_multiple_users(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    add_user(tmp_vault_dir, "myproject", "bob")
    users = list_users(tmp_vault_dir, "myproject")
    assert "alice" in users
    assert "bob" in users


def test_remove_user(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    remove_user(tmp_vault_dir, "myproject", "alice")
    assert "alice" not in list_users(tmp_vault_dir, "myproject")


def test_remove_nonexistent_user_is_silent(tmp_vault_dir):
    # should not raise
    remove_user(tmp_vault_dir, "myproject", "ghost")


def test_list_users_empty_project_returns_empty(tmp_vault_dir):
    assert list_users(tmp_vault_dir, "noproject") == []


def test_is_allowed_when_acl_empty(tmp_vault_dir):
    # no ACL set — everyone is allowed
    assert is_allowed(tmp_vault_dir, "myproject", "anyone") is True


def test_is_allowed_when_user_in_acl(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    assert is_allowed(tmp_vault_dir, "myproject", "alice") is True


def test_is_not_allowed_when_user_not_in_acl(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    assert is_allowed(tmp_vault_dir, "myproject", "bob") is False


def test_clear_acl_makes_project_open(tmp_vault_dir):
    add_user(tmp_vault_dir, "myproject", "alice")
    clear_acl(tmp_vault_dir, "myproject")
    assert list_users(tmp_vault_dir, "myproject") == []
    assert is_allowed(tmp_vault_dir, "myproject", "anyone") is True


def test_add_user_empty_username_raises(tmp_vault_dir):
    with pytest.raises(ACLError, match="Username"):
        add_user(tmp_vault_dir, "myproject", "")


def test_add_user_empty_project_raises(tmp_vault_dir):
    with pytest.raises(ACLError, match="Project"):
        add_user(tmp_vault_dir, "", "alice")


def test_acl_isolated_per_project(tmp_vault_dir):
    add_user(tmp_vault_dir, "proj_a", "alice")
    assert list_users(tmp_vault_dir, "proj_b") == []
