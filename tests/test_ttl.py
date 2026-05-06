"""Tests for envault.ttl — project TTL / expiry support."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from envault.ttl import (
    TTLError,
    set_ttl,
    get_ttl,
    is_expired,
    clear_ttl,
    list_ttls,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path / "vault")


def test_set_and_get_ttl(tmp_vault_dir):
    set_ttl("myproject", 3600, tmp_vault_dir)
    result = get_ttl("myproject", tmp_vault_dir)
    assert result is not None
    expiry = datetime.fromisoformat(result)
    now = datetime.now(tz=timezone.utc)
    assert expiry > now
    assert expiry < now + timedelta(seconds=3601)


def test_get_ttl_not_set_returns_none(tmp_vault_dir):
    assert get_ttl("ghost", tmp_vault_dir) is None


def test_set_ttl_invalid_seconds_raises(tmp_vault_dir):
    with pytest.raises(TTLError, match="positive"):
        set_ttl("proj", 0, tmp_vault_dir)
    with pytest.raises(TTLError, match="positive"):
        set_ttl("proj", -10, tmp_vault_dir)


def test_is_expired_false_for_future_ttl(tmp_vault_dir):
    set_ttl("alpha", 9999, tmp_vault_dir)
    assert is_expired("alpha", tmp_vault_dir) is False


def test_is_expired_true_for_past_ttl(tmp_vault_dir):
    # Set a TTL then mock time to be in the future
    set_ttl("beta", 1, tmp_vault_dir)
    future = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
    with patch("envault.ttl._now_utc", return_value=future):
        assert is_expired("beta", tmp_vault_dir) is True


def test_is_expired_no_ttl_returns_false(tmp_vault_dir):
    assert is_expired("no-ttl-project", tmp_vault_dir) is False


def test_clear_ttl_removes_entry(tmp_vault_dir):
    set_ttl("gamma", 500, tmp_vault_dir)
    clear_ttl("gamma", tmp_vault_dir)
    assert get_ttl("gamma", tmp_vault_dir) is None


def test_clear_ttl_missing_raises(tmp_vault_dir):
    with pytest.raises(TTLError, match="No TTL set"):
        clear_ttl("nonexistent", tmp_vault_dir)


def test_list_ttls_returns_all(tmp_vault_dir):
    set_ttl("p1", 100, tmp_vault_dir)
    set_ttl("p2", 200, tmp_vault_dir)
    result = list_ttls(tmp_vault_dir)
    assert set(result.keys()) == {"p1", "p2"}
    for v in result.values():
        assert isinstance(v, str)
        datetime.fromisoformat(v)  # must be valid ISO


def test_list_ttls_empty(tmp_vault_dir):
    assert list_ttls(tmp_vault_dir) == {}
