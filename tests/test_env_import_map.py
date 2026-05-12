"""Tests for envault/env_import_map.py"""

import pytest

from envault.vault import save_env, load_env
from envault.env_import_map import apply_map, parse_map_string, ImportMapError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _save(project, password, data, vault_dir):
    save_env(project, password, data, vault_dir=vault_dir)


def test_apply_map_renames_keys(tmp_vault_dir):
    _save("src", "pass", {"DB_HOST": "localhost", "DB_PORT": "5432"}, tmp_vault_dir)
    written = apply_map(
        "src", "dst", {"DB_HOST": "DATABASE_HOST"},
        "pass", "dstpass", vault_dir=tmp_vault_dir
    )
    assert written == {"DATABASE_HOST": "localhost"}
    dst = load_env("dst", "dstpass", vault_dir=tmp_vault_dir)
    assert dst["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in dst


def test_apply_map_merges_into_existing_dst(tmp_vault_dir):
    _save("src", "pass", {"X": "1"}, tmp_vault_dir)
    _save("dst", "dpass", {"EXISTING": "yes"}, tmp_vault_dir)
    apply_map("src", "dst", {"X": "NEW_X"}, "pass", "dpass", vault_dir=tmp_vault_dir)
    dst = load_env("dst", "dpass", vault_dir=tmp_vault_dir)
    assert dst["EXISTING"] == "yes"
    assert dst["NEW_X"] == "1"


def test_apply_map_missing_source_key_raises(tmp_vault_dir):
    _save("src", "pass", {"A": "1"}, tmp_vault_dir)
    with pytest.raises(ImportMapError, match="Keys not found in source"):
        apply_map("src", "dst", {"NOPE": "X"}, "pass", "dpass", vault_dir=tmp_vault_dir)


def test_apply_map_conflict_without_overwrite_raises(tmp_vault_dir):
    _save("src", "pass", {"A": "1"}, tmp_vault_dir)
    _save("dst", "dpass", {"B": "existing"}, tmp_vault_dir)
    with pytest.raises(ImportMapError, match="already exist"):
        apply_map("src", "dst", {"A": "B"}, "pass", "dpass", vault_dir=tmp_vault_dir)


def test_apply_map_conflict_with_overwrite_succeeds(tmp_vault_dir):
    _save("src", "pass", {"A": "new_val"}, tmp_vault_dir)
    _save("dst", "dpass", {"B": "old_val"}, tmp_vault_dir)
    apply_map(
        "src", "dst", {"A": "B"}, "pass", "dpass",
        vault_dir=tmp_vault_dir, overwrite=True
    )
    dst = load_env("dst", "dpass", vault_dir=tmp_vault_dir)
    assert dst["B"] == "new_val"


def test_apply_map_empty_key_map_raises(tmp_vault_dir):
    _save("src", "pass", {"A": "1"}, tmp_vault_dir)
    with pytest.raises(ImportMapError, match="must not be empty"):
        apply_map("src", "dst", {}, "pass", "dpass", vault_dir=tmp_vault_dir)


def test_parse_map_string_valid():
    result = parse_map_string("DB_HOST=DATABASE_HOST, DB_PORT=DATABASE_PORT")
    assert result == {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}


def test_parse_map_string_single():
    assert parse_map_string("OLD=NEW") == {"OLD": "NEW"}


def test_parse_map_string_invalid_format_raises():
    with pytest.raises(ImportMapError, match="Invalid mapping"):
        parse_map_string("NOEQUALSSIGN")


def test_parse_map_string_empty_raises():
    with pytest.raises(ImportMapError, match="No valid mappings"):
        parse_map_string("   ")


def test_parse_map_string_empty_key_raises():
    with pytest.raises(ImportMapError, match="Empty key"):
        parse_map_string("=NEW")
