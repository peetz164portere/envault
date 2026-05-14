"""Tests for envault/env_stats.py"""

from __future__ import annotations

import pytest

from envault.env_stats import StatsError, all_stats, project_stats, summary_stats
from envault.vault import save_env


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _save(project, env, password, vault_dir):
    save_env(project, env, password, vault_dir=vault_dir)


def test_project_stats_key_count(tmp_vault_dir):
    _save("alpha", {"A": "1", "B": "22", "C": "333"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.key_count == 3


def test_project_stats_total_value_bytes(tmp_vault_dir):
    _save("alpha", {"X": "hello", "Y": "world"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.total_value_bytes == len("hello") + len("world")


def test_project_stats_avg_value_bytes(tmp_vault_dir):
    _save("alpha", {"A": "ab", "B": "abcd"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.avg_value_bytes == 3.0


def test_project_stats_key_lengths(tmp_vault_dir):
    _save("alpha", {"AB": "v", "LONGKEY": "v"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.max_key_length == len("LONGKEY")
    assert stats.min_key_length == len("AB")


def test_project_stats_vault_file_bytes_nonzero(tmp_vault_dir):
    _save("alpha", {"K": "V"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.vault_file_bytes > 0


def test_project_stats_keys_sorted(tmp_vault_dir):
    _save("alpha", {"Z": "1", "A": "2", "M": "3"}, "pw", tmp_vault_dir)
    stats = project_stats("alpha", "pw", vault_dir=tmp_vault_dir)
    assert stats.keys == sorted(["Z", "A", "M"])


def test_project_stats_missing_project_raises(tmp_vault_dir):
    with pytest.raises(StatsError, match="does not exist"):
        project_stats("ghost", "pw", vault_dir=tmp_vault_dir)


def test_project_stats_empty_project(tmp_vault_dir):
    _save("empty", {}, "pw", tmp_vault_dir)
    stats = project_stats("empty", "pw", vault_dir=tmp_vault_dir)
    assert stats.key_count == 0
    assert stats.avg_value_bytes == 0.0
    assert stats.max_key_length == 0
    assert stats.min_key_length == 0


def test_all_stats_returns_all_projects(tmp_vault_dir):
    _save("proj1", {"A": "1"}, "pw", tmp_vault_dir)
    _save("proj2", {"B": "2", "C": "3"}, "pw", tmp_vault_dir)
    result = all_stats("pw", vault_dir=tmp_vault_dir)
    assert "proj1" in result
    assert "proj2" in result
    assert result["proj1"].key_count == 1
    assert result["proj2"].key_count == 2


def test_summary_stats_totals(tmp_vault_dir):
    _save("p1", {"A": "1", "B": "2"}, "pw", tmp_vault_dir)
    _save("p2", {"C": "3"}, "pw", tmp_vault_dir)
    summary = summary_stats("pw", vault_dir=tmp_vault_dir)
    assert summary["project_count"] == 2
    assert summary["total_keys"] == 3
    assert set(summary["projects"]) == {"p1", "p2"}


def test_summary_stats_no_projects(tmp_vault_dir):
    summary = summary_stats("pw", vault_dir=tmp_vault_dir)
    assert summary["project_count"] == 0
    assert summary["total_keys"] == 0
