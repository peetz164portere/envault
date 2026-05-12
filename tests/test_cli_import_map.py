"""Tests for envault/cli_import_map.py"""

import argparse
import pytest

from envault.vault import save_env, load_env
from envault.cli_import_map import cmd_import_map


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


class Args(argparse.Namespace):
    def __init__(self, **kwargs):
        defaults = dict(
            src="src",
            dst="dst",
            map="A=B",
            src_password="srcpass",
            dst_password="dstpass",
            overwrite=False,
            vault_dir=None,
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


def _make_args(vault_dir, **kwargs):
    return Args(vault_dir=vault_dir, **kwargs)


def _save(project, password, data, vault_dir):
    save_env(project, password, data, vault_dir=vault_dir)


def test_cmd_import_map_prints_confirmation(tmp_vault_dir, capsys):
    _save("src", "srcpass", {"A": "hello"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, src="src", dst="dst", map="A=B")
    cmd_import_map(args)
    out = capsys.readouterr().out
    assert "1 key(s)" in out
    assert "src" in out
    assert "dst" in out


def test_cmd_import_map_writes_correct_key(tmp_vault_dir):
    _save("src", "srcpass", {"OLD": "value123"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, src="src", dst="dst", map="OLD=NEW")
    cmd_import_map(args)
    dst = load_env("dst", "dstpass", vault_dir=tmp_vault_dir)
    assert dst["NEW"] == "value123"


def test_cmd_import_map_invalid_map_exits(tmp_vault_dir, capsys):
    _save("src", "srcpass", {"A": "1"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, map="BADFORMAT")
    with pytest.raises(SystemExit) as exc:
        cmd_import_map(args)
    assert exc.value.code == 1
    assert "Error" in capsys.readouterr().err


def test_cmd_import_map_missing_source_key_exits(tmp_vault_dir, capsys):
    _save("src", "srcpass", {"A": "1"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, map="NOPE=X")
    with pytest.raises(SystemExit) as exc:
        cmd_import_map(args)
    assert exc.value.code == 1


def test_cmd_import_map_conflict_without_overwrite_exits(tmp_vault_dir, capsys):
    _save("src", "srcpass", {"A": "1"}, tmp_vault_dir)
    _save("dst", "dstpass", {"B": "old"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, map="A=B", overwrite=False)
    with pytest.raises(SystemExit):
        cmd_import_map(args)


def test_cmd_import_map_overwrite_flag_succeeds(tmp_vault_dir):
    _save("src", "srcpass", {"A": "new"}, tmp_vault_dir)
    _save("dst", "dstpass", {"B": "old"}, tmp_vault_dir)
    args = _make_args(tmp_vault_dir, map="A=B", overwrite=True)
    cmd_import_map(args)
    dst = load_env("dst", "dstpass", vault_dir=tmp_vault_dir)
    assert dst["B"] == "new"
