"""Tests for envault.quota module."""

import pytest
from pathlib import Path
from envault.quota import (
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    list_quotas,
    QuotaError,
    DEFAULT_QUOTA,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / ".envault"


def test_set_and_get_quota(tmp_vault_dir):
    set_quota("myproject", 20, tmp_vault_dir)
    assert get_quota("myproject", tmp_vault_dir) == 20


def test_get_quota_returns_default_when_not_set(tmp_vault_dir):
    assert get_quota("unset_project", tmp_vault_dir) == DEFAULT_QUOTA


def test_set_quota_invalid_limit_raises(tmp_vault_dir):
    with pytest.raises(QuotaError, match="at least 1"):
        set_quota("proj", 0, tmp_vault_dir)


def test_set_quota_negative_raises(tmp_vault_dir):
    with pytest.raises(QuotaError):
        set_quota("proj", -5, tmp_vault_dir)


def test_remove_quota_reverts_to_default(tmp_vault_dir):
    set_quota("proj", 10, tmp_vault_dir)
    remove_quota("proj", tmp_vault_dir)
    assert get_quota("proj", tmp_vault_dir) == DEFAULT_QUOTA


def test_remove_quota_missing_raises(tmp_vault_dir):
    with pytest.raises(QuotaError, match="No custom quota"):
        remove_quota("ghost", tmp_vault_dir)


def test_check_quota_passes_under_limit(tmp_vault_dir):
    set_quota("proj", 5, tmp_vault_dir)
    check_quota("proj", 4, tmp_vault_dir)  # should not raise


def test_check_quota_raises_at_limit(tmp_vault_dir):
    set_quota("proj", 5, tmp_vault_dir)
    with pytest.raises(QuotaError, match="reached its key quota"):
        check_quota("proj", 5, tmp_vault_dir)


def test_check_quota_raises_over_limit(tmp_vault_dir):
    set_quota("proj", 3, tmp_vault_dir)
    with pytest.raises(QuotaError):
        check_quota("proj", 10, tmp_vault_dir)


def test_list_quotas_returns_all_set(tmp_vault_dir):
    set_quota("alpha", 10, tmp_vault_dir)
    set_quota("beta", 50, tmp_vault_dir)
    result = list_quotas(tmp_vault_dir)
    assert result == {"alpha": 10, "beta": 50}


def test_list_quotas_empty_when_none_set(tmp_vault_dir):
    assert list_quotas(tmp_vault_dir) == {}


def test_set_quota_overwrites_existing(tmp_vault_dir):
    set_quota("proj", 10, tmp_vault_dir)
    set_quota("proj", 25, tmp_vault_dir)
    assert get_quota("proj", tmp_vault_dir) == 25
