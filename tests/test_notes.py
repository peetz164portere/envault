"""Tests for envault/notes.py"""

import pytest
from pathlib import Path
from envault.notes import (
    set_note,
    get_note,
    delete_note,
    list_notes,
    NoteError,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / "vault"


def test_set_and_get_note(tmp_vault_dir):
    set_note("myproject", "remember to rotate keys", tmp_vault_dir)
    result = get_note("myproject", tmp_vault_dir)
    assert result == "remember to rotate keys"


def test_get_note_not_set_returns_none(tmp_vault_dir):
    result = get_note("nonexistent", tmp_vault_dir)
    assert result is None


def test_set_note_overwrites_existing(tmp_vault_dir):
    set_note("proj", "first note", tmp_vault_dir)
    set_note("proj", "updated note", tmp_vault_dir)
    assert get_note("proj", tmp_vault_dir) == "updated note"


def test_set_note_strips_whitespace(tmp_vault_dir):
    set_note("proj", "  hello world  ", tmp_vault_dir)
    assert get_note("proj", tmp_vault_dir) == "hello world"


def test_set_note_empty_project_raises(tmp_vault_dir):
    with pytest.raises(NoteError, match="Project name"):
        set_note("", "some note", tmp_vault_dir)


def test_set_note_empty_note_raises(tmp_vault_dir):
    with pytest.raises(NoteError, match="Note text"):
        set_note("proj", "   ", tmp_vault_dir)


def test_delete_note_removes_entry(tmp_vault_dir):
    set_note("proj", "to be deleted", tmp_vault_dir)
    delete_note("proj", tmp_vault_dir)
    assert get_note("proj", tmp_vault_dir) is None


def test_delete_note_missing_raises(tmp_vault_dir):
    with pytest.raises(NoteError, match="No note found"):
        delete_note("ghost", tmp_vault_dir)


def test_list_notes_returns_all(tmp_vault_dir):
    set_note("alpha", "note alpha", tmp_vault_dir)
    set_note("beta", "note beta", tmp_vault_dir)
    notes = list_notes(tmp_vault_dir)
    assert notes == {"alpha": "note alpha", "beta": "note beta"}


def test_list_notes_empty_vault(tmp_vault_dir):
    notes = list_notes(tmp_vault_dir)
    assert notes == {}
