"""Tests for envault.expiry."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone

from envault.expiry import (
    ExpiryError,
    set_expiry,
    get_expiry,
    is_expired,
    clear_expiry,
    list_expiries,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path / "vault")


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


def _past() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()


def test_set_and_get_expiry(tmp_vault_dir):
    ts = _future()
    set_expiry(tmp_vault_dir, "myproject", ts)
    assert get_expiry(tmp_vault_dir, "myproject") == ts


def test_get_expiry_not_set_returns_none(tmp_vault_dir):
    assert get_expiry(tmp_vault_dir, "ghost") is None


def test_set_expiry_invalid_date_raises(tmp_vault_dir):
    with pytest.raises(ExpiryError, match="Invalid ISO-8601"):
        set_expiry(tmp_vault_dir, "proj", "not-a-date")


def test_set_expiry_without_timezone_raises(tmp_vault_dir):
    with pytest.raises(ExpiryError, match="timezone"):
        set_expiry(tmp_vault_dir, "proj", "2025-12-31T00:00:00")


def test_is_expired_false_for_future(tmp_vault_dir):
    set_expiry(tmp_vault_dir, "proj", _future())
    assert is_expired(tmp_vault_dir, "proj") is False


def test_is_expired_true_for_past(tmp_vault_dir):
    set_expiry(tmp_vault_dir, "proj", _past())
    assert is_expired(tmp_vault_dir, "proj") is True


def test_is_expired_false_when_not_set(tmp_vault_dir):
    assert is_expired(tmp_vault_dir, "noexpiry") is False


def test_clear_expiry_removes_entry(tmp_vault_dir):
    set_expiry(tmp_vault_dir, "proj", _future())
    clear_expiry(tmp_vault_dir, "proj")
    assert get_expiry(tmp_vault_dir, "proj") is None


def test_clear_expiry_missing_raises(tmp_vault_dir):
    with pytest.raises(ExpiryError, match="No expiry set"):
        clear_expiry(tmp_vault_dir, "ghost")


def test_list_expiries_returns_all(tmp_vault_dir):
    ts1, ts2 = _future(), _future()
    set_expiry(tmp_vault_dir, "a", ts1)
    set_expiry(tmp_vault_dir, "b", ts2)
    result = list_expiries(tmp_vault_dir)
    assert result == {"a": ts1, "b": ts2}


def test_list_expiries_empty(tmp_vault_dir):
    assert list_expiries(tmp_vault_dir) == {}
