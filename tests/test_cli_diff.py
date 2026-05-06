"""Tests for CLI diff commands."""

import pytest
from types import SimpleNamespace
from envault.vault import save_env
from envault.snapshot import save_snapshot
from envault.cli_diff import cmd_diff


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _make_args(project, snapshot_a, snapshot_b=None, password="pw", vault_dir=None):
    return SimpleNamespace(
        project=project,
        snapshot_a=snapshot_a,
        snapshot_b=snapshot_b,
        password=password,
        vault_dir=vault_dir,
    )


def test_cmd_diff_two_snapshots_prints_changes(tmp_vault_dir, capsys):
    save_env("p", "pw", {"K": "1"}, vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "s1", vault_dir=tmp_vault_dir)
    save_env("p", "pw", {"K": "2"}, vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "s2", vault_dir=tmp_vault_dir)

    cmd_diff(_make_args("p", "s1", "s2", vault_dir=tmp_vault_dir))
    out = capsys.readouterr().out
    assert "K" in out
    assert "->" in out


def test_cmd_diff_vs_current_prints_changes(tmp_vault_dir, capsys):
    save_env("p", "pw", {"A": "old"}, vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "baseline", vault_dir=tmp_vault_dir)
    save_env("p", "pw", {"A": "new"}, vault_dir=tmp_vault_dir)

    cmd_diff(_make_args("p", "baseline", vault_dir=tmp_vault_dir))
    out = capsys.readouterr().out
    assert "A" in out
    assert "current" in out


def test_cmd_diff_no_changes_message(tmp_vault_dir, capsys):
    save_env("p", "pw", {"X": "same"}, vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "s1", vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "s2", vault_dir=tmp_vault_dir)

    cmd_diff(_make_args("p", "s1", "s2", vault_dir=tmp_vault_dir))
    out = capsys.readouterr().out
    assert "No differences" in out


def test_cmd_diff_missing_snapshot_exits(tmp_vault_dir):
    save_env("p", "pw", {"X": "v"}, vault_dir=tmp_vault_dir)
    save_snapshot("p", "pw", "s1", vault_dir=tmp_vault_dir)

    with pytest.raises(SystemExit):
        cmd_diff(_make_args("p", "s1", "ghost", vault_dir=tmp_vault_dir))


def test_cmd_diff_missing_project_exits(tmp_vault_dir):
    with pytest.raises(SystemExit):
        cmd_diff(_make_args("ghost", "snap", vault_dir=tmp_vault_dir))
