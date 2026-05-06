"""Tests for envault/pin.py"""

import pytest
from pathlib import Path
from envault.pin import set_hint, get_hint, remove_hint, list_hints, PinError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path


def test_set_and_get_hint(tmp_vault_dir):
    set_hint("myproject", "first pet name", tmp_vault_dir)
    result = get_hint("myproject", tmp_vault_dir)
    assert result == "first pet name"


def test_get_hint_not_set_returns_none(tmp_vault_dir):
    result = get_hint("nonexistent", tmp_vault_dir)
    assert result is None


def test_set_hint_empty_raises(tmp_vault_dir):
    with pytest.raises(PinError, match="Hint must not be empty"):
        set_hint("proj", "   ", tmp_vault_dir)


def test_set_hint_strips_whitespace(tmp_vault_dir):
    set_hint("proj", "  my hint  ", tmp_vault_dir)
    assert get_hint("proj", tmp_vault_dir) == "my hint"


def test_set_hint_overwrites_existing(tmp_vault_dir):
    set_hint("proj", "old hint", tmp_vault_dir)
    set_hint("proj", "new hint", tmp_vault_dir)
    assert get_hint("proj", tmp_vault_dir) == "new hint"


def test_remove_hint_deletes_entry(tmp_vault_dir):
    set_hint("proj", "some hint", tmp_vault_dir)
    remove_hint("proj", tmp_vault_dir)
    assert get_hint("proj", tmp_vault_dir) is None


def test_remove_hint_missing_raises(tmp_vault_dir):
    with pytest.raises(PinError, match="No hint found"):
        remove_hint("ghost", tmp_vault_dir)


def test_list_hints_returns_all(tmp_vault_dir):
    set_hint("alpha", "hint a", tmp_vault_dir)
    set_hint("beta", "hint b", tmp_vault_dir)
    result = list_hints(tmp_vault_dir)
    assert result == {"alpha": "hint a", "beta": "hint b"}


def test_list_hints_empty_vault(tmp_vault_dir):
    result = list_hints(tmp_vault_dir)
    assert result == {}


def test_hints_persist_across_calls(tmp_vault_dir):
    set_hint("proj", "persistent hint", tmp_vault_dir)
    # Simulate a fresh load by calling get_hint independently
    assert get_hint("proj", tmp_vault_dir) == "persistent hint"
    assert "proj" in list_hints(tmp_vault_dir)
