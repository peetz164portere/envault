import pytest
from types import SimpleNamespace
from envault.cli_groups import (
    cmd_group_create,
    cmd_group_get,
    cmd_group_delete,
    cmd_group_add_project,
    cmd_group_remove_project,
    cmd_group_list,
)
from envault.env_groups import create_group


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def _make_args(vault_dir, **kwargs):
    return SimpleNamespace(vault_dir=vault_dir, **kwargs)


def test_cmd_group_create_prints_confirmation(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir, group="prod", projects=["app", "db"])
    cmd_group_create(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "app" in out


def test_cmd_group_create_empty_name_exits(tmp_vault_dir):
    args = _make_args(tmp_vault_dir, group="  ", projects=["app"])
    with pytest.raises(SystemExit):
        cmd_group_create(args)


def test_cmd_group_get_shows_projects(tmp_vault_dir, capsys):
    create_group(tmp_vault_dir, "staging", ["svc1", "svc2"])
    args = _make_args(tmp_vault_dir, group="staging")
    cmd_group_get(args)
    out = capsys.readouterr().out
    assert "svc1" in out
    assert "svc2" in out


def test_cmd_group_get_missing_exits(tmp_vault_dir):
    args = _make_args(tmp_vault_dir, group="ghost")
    with pytest.raises(SystemExit):
        cmd_group_get(args)


def test_cmd_group_delete_removes_group(tmp_vault_dir, capsys):
    create_group(tmp_vault_dir, "dev", ["x"])
    args = _make_args(tmp_vault_dir, group="dev")
    cmd_group_delete(args)
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_group_delete_missing_exits(tmp_vault_dir):
    args = _make_args(tmp_vault_dir, group="nope")
    with pytest.raises(SystemExit):
        cmd_group_delete(args)


def test_cmd_group_add_project_prints_confirmation(tmp_vault_dir, capsys):
    create_group(tmp_vault_dir, "team", ["alpha"])
    args = _make_args(tmp_vault_dir, group="team", project="beta")
    cmd_group_add_project(args)
    out = capsys.readouterr().out
    assert "beta" in out
    assert "team" in out


def test_cmd_group_remove_project_prints_confirmation(tmp_vault_dir, capsys):
    create_group(tmp_vault_dir, "team", ["alpha", "beta"])
    args = _make_args(tmp_vault_dir, group="team", project="alpha")
    cmd_group_remove_project(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "removed" in out


def test_cmd_group_list_shows_all(tmp_vault_dir, capsys):
    create_group(tmp_vault_dir, "g1", ["p1"])
    create_group(tmp_vault_dir, "g2", ["p2"])
    args = _make_args(tmp_vault_dir)
    cmd_group_list(args)
    out = capsys.readouterr().out
    assert "g1" in out
    assert "g2" in out


def test_cmd_group_list_empty_vault(tmp_vault_dir, capsys):
    args = _make_args(tmp_vault_dir)
    cmd_group_list(args)
    out = capsys.readouterr().out
    assert "No groups" in out
