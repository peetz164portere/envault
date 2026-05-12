"""Tests for envault.env_merge."""

import pytest
from envault.env_merge import MergeError, diff_merge, merge_projects
from envault.vault import save_env


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, data, password="pass", vault_dir=None):
    save_env(project, data, password, vault_dir=vault_dir)


def test_merge_last_strategy_overwrites(tmp_vault_dir):
    _save("a", {"KEY": "from_a", "SHARED": "a_val"}, vault_dir=tmp_vault_dir)
    _save("b", {"KEY2": "from_b", "SHARED": "b_val"}, vault_dir=tmp_vault_dir)
    result = merge_projects(["a", "b"], "pass", strategy="last", vault_dir=tmp_vault_dir)
    assert result["KEY"] == "from_a"
    assert result["KEY2"] == "from_b"
    assert result["SHARED"] == "b_val"  # last wins


def test_merge_first_strategy_keeps_original(tmp_vault_dir):
    _save("a", {"SHARED": "a_val"}, vault_dir=tmp_vault_dir)
    _save("b", {"SHARED": "b_val"}, vault_dir=tmp_vault_dir)
    result = merge_projects(["a", "b"], "pass", strategy="first", vault_dir=tmp_vault_dir)
    assert result["SHARED"] == "a_val"  # first wins


def test_merge_error_strategy_raises_on_duplicate(tmp_vault_dir):
    _save("a", {"SHARED": "a_val"}, vault_dir=tmp_vault_dir)
    _save("b", {"SHARED": "b_val"}, vault_dir=tmp_vault_dir)
    with pytest.raises(MergeError, match="Duplicate key 'SHARED'"):
        merge_projects(["a", "b"], "pass", strategy="error", vault_dir=tmp_vault_dir)


def test_merge_no_overlap_all_strategies(tmp_vault_dir):
    _save("x", {"A": "1"}, vault_dir=tmp_vault_dir)
    _save("y", {"B": "2"}, vault_dir=tmp_vault_dir)
    for strat in ("first", "last", "error"):
        result = merge_projects(["x", "y"], "pass", strategy=strat, vault_dir=tmp_vault_dir)
        assert result == {"A": "1", "B": "2"}


def test_merge_missing_project_raises(tmp_vault_dir):
    _save("real", {"K": "v"}, vault_dir=tmp_vault_dir)
    with pytest.raises(MergeError, match="does not exist"):
        merge_projects(["real", "ghost"], "pass", vault_dir=tmp_vault_dir)


def test_merge_empty_list_raises(tmp_vault_dir):
    with pytest.raises(MergeError, match="At least one"):
        merge_projects([], "pass", vault_dir=tmp_vault_dir)


def test_merge_unknown_strategy_raises(tmp_vault_dir):
    _save("p", {"K": "v"}, vault_dir=tmp_vault_dir)
    with pytest.raises(MergeError, match="Unknown strategy"):
        merge_projects(["p"], "pass", strategy="random", vault_dir=tmp_vault_dir)


def test_diff_merge_returns_per_key_values(tmp_vault_dir):
    _save("a", {"FOO": "1", "BAR": "hello"}, vault_dir=tmp_vault_dir)
    _save("b", {"FOO": "2", "BAZ": "world"}, vault_dir=tmp_vault_dir)
    result = diff_merge(["a", "b"], "pass", vault_dir=tmp_vault_dir)
    assert result["FOO"] == ["1", "2"]
    assert result["BAR"] == ["hello", None]
    assert result["BAZ"] == [None, "world"]


def test_diff_merge_empty_list_raises(tmp_vault_dir):
    with pytest.raises(MergeError, match="At least one"):
        diff_merge([], "pass", vault_dir=tmp_vault_dir)


def test_diff_merge_missing_project_raises(tmp_vault_dir):
    _save("real", {"K": "v"}, vault_dir=tmp_vault_dir)
    with pytest.raises(MergeError, match="does not exist"):
        diff_merge(["real", "nope"], "pass", vault_dir=tmp_vault_dir)
