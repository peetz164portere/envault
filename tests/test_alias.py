"""Tests for envault/alias.py"""

import pytest
from envault.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    AliasError,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    import envault.storage as storage
    original = storage._VAULT_DIR
    storage._VAULT_DIR = str(tmp_path / "vault")
    yield str(tmp_path / "vault")
    storage._VAULT_DIR = original


def test_set_alias_creates_mapping(tmp_vault_dir):
    set_alias("myapp", "my-application", vault_dir=tmp_vault_dir)
    aliases = list_aliases(vault_dir=tmp_vault_dir)
    assert aliases["myapp"] == "my-application"


def test_set_alias_overwrites_existing(tmp_vault_dir):
    set_alias("app", "project-a", vault_dir=tmp_vault_dir)
    set_alias("app", "project-b", vault_dir=tmp_vault_dir)
    assert list_aliases(vault_dir=tmp_vault_dir)["app"] == "project-b"


def test_set_alias_empty_alias_raises(tmp_vault_dir):
    with pytest.raises(AliasError, match="empty"):
        set_alias("  ", "some-project", vault_dir=tmp_vault_dir)


def test_set_alias_empty_project_raises(tmp_vault_dir):
    with pytest.raises(AliasError, match="Project"):
        set_alias("alias", "", vault_dir=tmp_vault_dir)


def test_remove_alias_deletes_entry(tmp_vault_dir):
    set_alias("dev", "dev-project", vault_dir=tmp_vault_dir)
    remove_alias("dev", vault_dir=tmp_vault_dir)
    assert "dev" not in list_aliases(vault_dir=tmp_vault_dir)


def test_remove_alias_missing_raises(tmp_vault_dir):
    with pytest.raises(AliasError, match="not found"):
        remove_alias("ghost", vault_dir=tmp_vault_dir)


def test_resolve_alias_returns_project(tmp_vault_dir):
    set_alias("prod", "production-env", vault_dir=tmp_vault_dir)
    assert resolve_alias("prod", vault_dir=tmp_vault_dir) == "production-env"


def test_resolve_alias_unknown_returns_self(tmp_vault_dir):
    result = resolve_alias("unknown-alias", vault_dir=tmp_vault_dir)
    assert result == "unknown-alias"


def test_list_aliases_empty_when_none_set(tmp_vault_dir):
    assert list_aliases(vault_dir=tmp_vault_dir) == {}


def test_list_aliases_returns_all(tmp_vault_dir):
    set_alias("a", "alpha", vault_dir=tmp_vault_dir)
    set_alias("b", "beta", vault_dir=tmp_vault_dir)
    aliases = list_aliases(vault_dir=tmp_vault_dir)
    assert len(aliases) == 2
    assert aliases["a"] == "alpha"
    assert aliases["b"] == "beta"


def test_set_alias_whitespace_stripped(tmp_vault_dir):
    """Alias and project names with surrounding whitespace should be stored stripped."""
    set_alias("  myapp  ", "  my-application  ", vault_dir=tmp_vault_dir)
    aliases = list_aliases(vault_dir=tmp_vault_dir)
    assert "myapp" in aliases
    assert aliases["myapp"] == "my-application"
