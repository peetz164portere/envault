"""Tests for envault export/import functionality."""

import os
import pytest
from pathlib import Path

from envault import storage
from envault.export import export_env, import_env, parse_env_file
from envault.vault import load_env


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", str(tmp_path / ".envault"))
    return tmp_path


SAMPLE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
PASSWORD = "test-password"
PROJECT = "myapp"


def test_export_creates_file(tmp_vault_dir):
    from envault.vault import save_env
    save_env(PROJECT, SAMPLE_VARS, PASSWORD)
    out = str(tmp_vault_dir / "myapp.env")
    result = export_env(PROJECT, PASSWORD, output_path=out)
    assert result == out
    assert os.path.exists(out)


def test_export_file_contents(tmp_vault_dir):
    from envault.vault import save_env
    save_env(PROJECT, SAMPLE_VARS, PASSWORD)
    out = str(tmp_vault_dir / "myapp.env")
    export_env(PROJECT, PASSWORD, output_path=out)
    content = Path(out).read_text()
    for key, value in SAMPLE_VARS.items():
        assert f"{key}={value}" in content


def test_export_default_filename(tmp_vault_dir, monkeypatch):
    from envault.vault import save_env
    monkeypatch.chdir(tmp_vault_dir)
    save_env(PROJECT, SAMPLE_VARS, PASSWORD)
    result = export_env(PROJECT, PASSWORD)
    assert result == f"{PROJECT}.env"
    assert os.path.exists(result)


def test_import_round_trip(tmp_vault_dir):
    env_file = tmp_vault_dir / "input.env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    imported = import_env(PROJECT, PASSWORD, str(env_file))
    assert imported == {"FOO": "bar", "BAZ": "qux"}
    loaded = load_env(PROJECT, PASSWORD)
    assert loaded == {"FOO": "bar", "BAZ": "qux"}


def test_import_missing_file_raises(tmp_vault_dir):
    with pytest.raises(FileNotFoundError):
        import_env(PROJECT, PASSWORD, str(tmp_vault_dir / "nope.env"))


def test_import_empty_file_raises(tmp_vault_dir):
    env_file = tmp_vault_dir / "empty.env"
    env_file.write_text("# just a comment\n\n")
    with pytest.raises(ValueError, match="No valid"):
        import_env(PROJECT, PASSWORD, str(env_file))


def test_parse_env_file_strips_quotes(tmp_vault_dir):
    env_file = tmp_vault_dir / "quoted.env"
    env_file.write_text('KEY="hello world"\nOTHER=\'simple\'\n')
    result = parse_env_file(str(env_file))
    assert result["KEY"] == "hello world"
    assert result["OTHER"] == "simple"


def test_parse_env_file_skips_comments_and_blanks(tmp_vault_dir):
    env_file = tmp_vault_dir / "mixed.env"
    env_file.write_text("# comment\n\nVALID=yes\n")
    result = parse_env_file(str(env_file))
    assert result == {"VALID": "yes"}
