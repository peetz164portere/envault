"""Tests for envault/cli_template.py"""

import argparse
import pytest

from envault import storage
from envault.vault import save_env, load_env
from envault.cli_template import cmd_template_export, cmd_template_apply, cmd_template_keys


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", str(tmp_path / "vault"))
    return tmp_path


def _make_args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_template_export_creates_file(tmp_path):
    save_env("proj", {"KEY": "val"}, "pw")
    out = str(tmp_path / "out.env")
    args = _make_args(project="proj", password="pw", output=out, no_mask=False)
    cmd_template_export(args)
    content = open(out).read()
    assert "KEY=" in content
    assert "val" not in content  # masked


def test_cmd_template_export_no_mask(tmp_path):
    save_env("proj", {"KEY": "val"}, "pw")
    out = str(tmp_path / "out.env")
    args = _make_args(project="proj", password="pw", output=out, no_mask=True)
    cmd_template_export(args)
    assert "KEY=val" in open(out).read()


def test_cmd_template_apply_adds_keys(tmp_path, capsys):
    template = tmp_path / "tmpl.env"
    template.write_text("FOO=bar\nBAZ=qux\n")
    args = _make_args(
        project="newproj",
        password="pw",
        confirm_password="pw",
        template=str(template),
        overwrite=False,
    )
    cmd_template_apply(args)
    captured = capsys.readouterr()
    assert "2 key(s)" in captured.out
    env = load_env("newproj", "pw")
    assert env["FOO"] == "bar"


def test_cmd_template_apply_password_mismatch(capsys):
    with pytest.raises(SystemExit):
        args = _make_args(
            project="proj",
            password="pw",
            confirm_password="wrong",
            template="any.env",
            overwrite=False,
        )
        cmd_template_apply(args)
    captured = capsys.readouterr()
    assert "passwords do not match" in captured.err


def test_cmd_template_apply_no_new_keys_message(tmp_path, capsys):
    save_env("proj", {"FOO": "existing"}, "pw")
    template = tmp_path / "tmpl.env"
    template.write_text("FOO=new\n")
    args = _make_args(
        project="proj",
        password="pw",
        confirm_password="pw",
        template=str(template),
        overwrite=False,
    )
    cmd_template_apply(args)
    captured = capsys.readouterr()
    assert "No new keys" in captured.out


def test_cmd_template_keys_lists_keys(tmp_path, capsys):
    template = tmp_path / "tmpl.env"
    template.write_text("ALPHA=1\nBETA=2\n")
    args = _make_args(template=str(template))
    cmd_template_keys(args)
    captured = capsys.readouterr()
    assert "ALPHA" in captured.out
    assert "BETA" in captured.out


def test_cmd_template_keys_missing_file_exits(tmp_path, capsys):
    args = _make_args(template=str(tmp_path / "nope.env"))
    with pytest.raises(SystemExit):
        cmd_template_keys(args)
    assert "Cannot read" in capsys.readouterr().err
