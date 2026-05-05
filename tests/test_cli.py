"""Tests for the envault CLI."""

import os
import pytest

from unittest.mock import patch
from envault import cli
from envault.vault import save_env
import envault.storage as storage


ENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=hunter2\n"
PASSWORD = "testpassword"


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", str(tmp_path / ".envault"))
    return tmp_path


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT)
    return str(p)


def test_cmd_set_saves_project(env_file):
    with patch("getpass.getpass", side_effect=[PASSWORD, PASSWORD]):
        rc = cli.main(["set", "myapp", env_file])
    assert rc == 0
    from envault.vault import project_exists
    assert project_exists("myapp")


def test_cmd_set_password_mismatch(env_file, capsys):
    with patch("getpass.getpass", side_effect=["abc", "xyz"]):
        rc = cli.main(["set", "myapp", env_file])
    assert rc == 1
    captured = capsys.readouterr()
    assert "do not match" in captured.err


def test_cmd_set_missing_file(capsys):
    with patch("getpass.getpass", side_effect=[PASSWORD, PASSWORD]):
        rc = cli.main(["set", "myapp", "/nonexistent/.env"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_cmd_get_prints_env(capsys):
    save_env("myapp", ENV_CONTENT, PASSWORD)
    with patch("getpass.getpass", return_value=PASSWORD):
        rc = cli.main(["get", "myapp"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "DB_HOST=localhost" in captured.out


def test_cmd_get_wrong_password(capsys):
    save_env("myapp", ENV_CONTENT, PASSWORD)
    with patch("getpass.getpass", return_value="wrongpassword"):
        rc = cli.main(["get", "myapp"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "wrong password" in captured.err


def test_cmd_get_missing_project(capsys):
    with patch("getpass.getpass", return_value=PASSWORD):
        rc = cli.main(["get", "ghost"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "no vault found" in captured.err


def test_cmd_remove_project(capsys):
    save_env("myapp", ENV_CONTENT, PASSWORD)
    rc = cli.main(["remove", "myapp"])
    assert rc == 0
    from envault.vault import project_exists
    assert not project_exists("myapp")


def test_cmd_remove_missing_project(capsys):
    rc = cli.main(["remove", "ghost"])
    assert rc == 1


def test_cmd_list_empty(capsys):
    rc = cli.main(["list"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "No projects" in captured.out


def test_cmd_list_with_projects(capsys):
    save_env("alpha", ENV_CONTENT, PASSWORD)
    save_env("beta", ENV_CONTENT, PASSWORD)
    rc = cli.main(["list"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out
