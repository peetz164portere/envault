"""Tests for envault/policy.py"""

import pytest
from envault.policy import (
    PolicyError,
    set_policy,
    get_policy,
    delete_policy,
    enforce_policy,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_policy(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", required_keys=["DB_URL", "SECRET"])
    policy = get_policy(tmp_vault_dir, "myapp")
    assert policy["required_keys"] == ["DB_URL", "SECRET"]


def test_get_policy_not_set_returns_empty(tmp_vault_dir):
    policy = get_policy(tmp_vault_dir, "ghost")
    assert policy == {}


def test_set_policy_empty_project_raises(tmp_vault_dir):
    with pytest.raises(PolicyError, match="Project name"):
        set_policy(tmp_vault_dir, "", required_keys=["KEY"])


def test_set_policy_invalid_min_password_length_raises(tmp_vault_dir):
    with pytest.raises(PolicyError, match="min_password_length"):
        set_policy(tmp_vault_dir, "myapp", min_password_length=0)


def test_set_policy_deduplicates_keys(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", required_keys=["A", "A", "B"])
    policy = get_policy(tmp_vault_dir, "myapp")
    assert policy["required_keys"] == ["A", "B"]


def test_set_policy_forbidden_keys(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", forbidden_keys=["DEBUG"])
    policy = get_policy(tmp_vault_dir, "myapp")
    assert "DEBUG" in policy["forbidden_keys"]


def test_delete_policy(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", required_keys=["X"])
    delete_policy(tmp_vault_dir, "myapp")
    assert get_policy(tmp_vault_dir, "myapp") == {}


def test_delete_policy_missing_raises(tmp_vault_dir):
    with pytest.raises(PolicyError, match="No policy found"):
        delete_policy(tmp_vault_dir, "ghost")


def test_enforce_policy_passes_with_no_policy(tmp_vault_dir):
    enforce_policy(tmp_vault_dir, "myapp", {"A": "1"}, "pass")


def test_enforce_policy_missing_required_key_raises(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", required_keys=["DB_URL"])
    with pytest.raises(PolicyError, match="required key 'DB_URL'"):
        enforce_policy(tmp_vault_dir, "myapp", {"OTHER": "val"}, "password")


def test_enforce_policy_forbidden_key_raises(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", forbidden_keys=["DEBUG"])
    with pytest.raises(PolicyError, match="forbidden key 'DEBUG'"):
        enforce_policy(tmp_vault_dir, "myapp", {"DEBUG": "true"}, "password")


def test_enforce_policy_password_too_short_raises(tmp_vault_dir):
    set_policy(tmp_vault_dir, "myapp", min_password_length=12)
    with pytest.raises(PolicyError, match="at least 12 characters"):
        enforce_policy(tmp_vault_dir, "myapp", {}, "short")


def test_enforce_policy_all_pass(tmp_vault_dir):
    set_policy(
        tmp_vault_dir,
        "myapp",
        required_keys=["DB_URL"],
        forbidden_keys=["DEBUG"],
        min_password_length=8,
    )
    enforce_policy(tmp_vault_dir, "myapp", {"DB_URL": "postgres://"}, "strongpass")
