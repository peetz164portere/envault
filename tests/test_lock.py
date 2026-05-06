"""Tests for envault.lock."""

import os
import pytest
from pathlib import Path
from envault.lock import acquire_lock, release_lock, is_locked, lock_owner, LockError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / "vault"


def test_acquire_creates_lock_file(tmp_vault_dir):
    acquire_lock("myproject", tmp_vault_dir)
    assert (tmp_vault_dir / "myproject.lock").exists()
    release_lock("myproject", tmp_vault_dir)


def test_is_locked_true_after_acquire(tmp_vault_dir):
    acquire_lock("myproject", tmp_vault_dir)
    assert is_locked("myproject", tmp_vault_dir) is True
    release_lock("myproject", tmp_vault_dir)


def test_is_locked_false_before_acquire(tmp_vault_dir):
    assert is_locked("myproject", tmp_vault_dir) is False


def test_release_removes_lock_file(tmp_vault_dir):
    acquire_lock("myproject", tmp_vault_dir)
    release_lock("myproject", tmp_vault_dir)
    assert not is_locked("myproject", tmp_vault_dir)


def test_release_nonexistent_lock_is_safe(tmp_vault_dir):
    # should not raise
    release_lock("ghost", tmp_vault_dir)


def test_lock_owner_returns_pid(tmp_vault_dir):
    acquire_lock("myproject", tmp_vault_dir, pid=12345)
    assert lock_owner("myproject", tmp_vault_dir) == 12345
    release_lock("myproject", tmp_vault_dir)


def test_lock_owner_returns_none_when_not_locked(tmp_vault_dir):
    assert lock_owner("myproject", tmp_vault_dir) is None


def test_double_acquire_raises_lock_error(tmp_vault_dir):
    acquire_lock("myproject", tmp_vault_dir)
    with pytest.raises(LockError, match="Could not acquire lock"):
        acquire_lock("myproject", tmp_vault_dir, timeout=0.1)
    release_lock("myproject", tmp_vault_dir)


def test_different_projects_can_be_locked_independently(tmp_vault_dir):
    acquire_lock("proj_a", tmp_vault_dir)
    acquire_lock("proj_b", tmp_vault_dir)
    assert is_locked("proj_a", tmp_vault_dir)
    assert is_locked("proj_b", tmp_vault_dir)
    release_lock("proj_a", tmp_vault_dir)
    release_lock("proj_b", tmp_vault_dir)
