"""Tests for envault/search.py"""

import pytest
from envault import storage, vault
from envault.search import search_key, search_value, list_keys, SearchError


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", str(tmp_path / ".envault"))
    storage.ensure_vault_dir()
    yield tmp_path


def _save(project, password, env):
    vault.save_env(project, password, env)


def test_search_key_finds_matching_keys():
    _save("proj1", "pass", {"DATABASE_URL": "postgres://...", "SECRET_KEY": "abc"})
    _save("proj2", "pass", {"DATABASE_HOST": "localhost", "PORT": "5432"})

    results = search_key("pass", "database")
    keys_found = [(r["project"], r["key"]) for r in results]
    assert ("proj1", "DATABASE_URL") in keys_found
    assert ("proj2", "DATABASE_HOST") in keys_found
    assert all("database" in r["key"].lower() for r in results)


def test_search_key_scoped_to_project():
    _save("proj1", "pass", {"DATABASE_URL": "postgres://...", "API_KEY": "xyz"})
    _save("proj2", "pass", {"DATABASE_URL": "mysql://..."})

    results = search_key("pass", "database", project="proj1")
    assert len(results) == 1
    assert results[0]["project"] == "proj1"


def test_search_key_no_match_returns_empty():
    _save("proj1", "pass", {"FOO": "bar"})
    results = search_key("pass", "NONEXISTENT")
    assert results == []


def test_search_value_finds_matching_values():
    _save("proj1", "pass", {"DB_URL": "postgres://myhost/db", "REDIS_URL": "redis://otherhost"})

    results = search_value("pass", "myhost")
    assert len(results) == 1
    assert results[0]["key"] == "DB_URL"


def test_search_value_case_insensitive():
    _save("proj1", "pass", {"NOTE": "HelloWorld"})
    results = search_value("pass", "helloworld")
    assert len(results) == 1


def test_search_key_raises_when_no_projects():
    with pytest.raises(SearchError, match="No projects found"):
        search_key("pass", "anything")


def test_list_keys_returns_sorted_keys():
    _save("myproj", "pass", {"ZEBRA": "1", "ALPHA": "2", "MIDDLE": "3"})
    keys = list_keys("pass", "myproj")
    assert keys == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_list_keys_wrong_password_raises():
    _save("myproj", "correct", {"KEY": "val"})
    with pytest.raises(SearchError, match="Could not load project"):
        list_keys("wrong", "myproj")


def test_search_skips_projects_with_wrong_password():
    _save("proj1", "pass1", {"SHARED_KEY": "value1"})
    _save("proj2", "pass2", {"SHARED_KEY": "value2"})

    # Only proj1 accessible with pass1
    results = search_key("pass1", "shared_key")
    assert len(results) == 1
    assert results[0]["project"] == "proj1"
