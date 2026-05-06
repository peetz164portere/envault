"""Tests for envault.tags module."""

import pytest
from pathlib import Path

from envault.tags import (
    add_tag,
    remove_tag,
    get_tags,
    projects_with_tag,
    all_tags,
    TagError,
)


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    vault_dir = tmp_path / ".envault"
    vault_dir.mkdir()
    import envault.tags as tags_mod
    import envault.storage as storage_mod
    monkeypatch.setattr(tags_mod, "_vault_path", lambda name: vault_dir / f"{name}.vault")
    monkeypatch.setattr(storage_mod, "_vault_path", lambda name: vault_dir / f"{name}.vault")
    return vault_dir


def test_add_tag_creates_entry(tmp_vault_dir):
    add_tag("myapp", "production", vault_dir=tmp_vault_dir)
    assert "production" in get_tags("myapp", vault_dir=tmp_vault_dir)


def test_add_tag_idempotent(tmp_vault_dir):
    add_tag("myapp", "staging", vault_dir=tmp_vault_dir)
    add_tag("myapp", "staging", vault_dir=tmp_vault_dir)
    assert get_tags("myapp", vault_dir=tmp_vault_dir).count("staging") == 1


def test_add_multiple_tags(tmp_vault_dir):
    add_tag("myapp", "production", vault_dir=tmp_vault_dir)
    add_tag("myapp", "web", vault_dir=tmp_vault_dir)
    tags = get_tags("myapp", vault_dir=tmp_vault_dir)
    assert "production" in tags
    assert "web" in tags


def test_remove_tag(tmp_vault_dir):
    add_tag("myapp", "staging", vault_dir=tmp_vault_dir)
    remove_tag("myapp", "staging", vault_dir=tmp_vault_dir)
    assert "staging" not in get_tags("myapp", vault_dir=tmp_vault_dir)


def test_remove_tag_missing_raises(tmp_vault_dir):
    with pytest.raises(TagError, match="not found"):
        remove_tag("myapp", "ghost", vault_dir=tmp_vault_dir)


def test_get_tags_unknown_project_returns_empty(tmp_vault_dir):
    assert get_tags("unknown", vault_dir=tmp_vault_dir) == []


def test_projects_with_tag(tmp_vault_dir):
    add_tag("app1", "production", vault_dir=tmp_vault_dir)
    add_tag("app2", "production", vault_dir=tmp_vault_dir)
    add_tag("app3", "staging", vault_dir=tmp_vault_dir)
    result = projects_with_tag("production", vault_dir=tmp_vault_dir)
    assert "app1" in result
    assert "app2" in result
    assert "app3" not in result


def test_projects_with_tag_none_returns_empty(tmp_vault_dir):
    assert projects_with_tag("nonexistent", vault_dir=tmp_vault_dir) == []


def test_all_tags_returns_full_mapping(tmp_vault_dir):
    add_tag("app1", "production", vault_dir=tmp_vault_dir)
    add_tag("app2", "staging", vault_dir=tmp_vault_dir)
    result = all_tags(vault_dir=tmp_vault_dir)
    assert result["app1"] == ["production"]
    assert result["app2"] == ["staging"]


def test_remove_last_tag_cleans_project_entry(tmp_vault_dir):
    add_tag("app1", "solo", vault_dir=tmp_vault_dir)
    remove_tag("app1", "solo", vault_dir=tmp_vault_dir)
    assert "app1" not in all_tags(vault_dir=tmp_vault_dir)
