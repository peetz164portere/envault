"""Tests for envault/template.py"""

import os
import pytest

from envault import storage
from envault.vault import save_env, load_env
from envault.template import (
    export_template,
    apply_template,
    list_template_keys,
    TemplateError,
)


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "VAULT_DIR", str(tmp_path / "vault"))
    return tmp_path


def _save(project, env, password="pw"):
    save_env(project, env, password)


def test_export_template_creates_file(tmp_path):
    _save("myapp", {"DB_HOST": "localhost", "DB_PORT": "5432"})
    out = str(tmp_path / "template.env")
    export_template("myapp", "pw", out)
    assert os.path.exists(out)


def test_export_template_masks_values(tmp_path):
    _save("myapp", {"SECRET": "supersecret", "HOST": "localhost"})
    out = str(tmp_path / "template.env")
    export_template("myapp", "pw", out, mask_values=True)
    content = open(out).read()
    assert "supersecret" not in content
    assert "SECRET=" in content


def test_export_template_unmasked_values(tmp_path):
    _save("myapp", {"HOST": "localhost"})
    out = str(tmp_path / "template.env")
    export_template("myapp", "pw", out, mask_values=False)
    content = open(out).read()
    assert "HOST=localhost" in content


def test_apply_template_adds_keys(tmp_path):
    template = tmp_path / "tmpl.env"
    template.write_text("API_KEY=abc123\nDEBUG=false\n")
    written = apply_template("newproj", "pw", str(template))
    assert written == {"API_KEY": "abc123", "DEBUG": "false"}
    env = load_env("newproj", "pw")
    assert env["API_KEY"] == "abc123"


def test_apply_template_skips_existing_keys_by_default(tmp_path):
    _save("proj", {"API_KEY": "original"})
    template = tmp_path / "tmpl.env"
    template.write_text("API_KEY=new_value\nEXTRA=hello\n")
    written = apply_template("proj", "pw", str(template), overwrite=False)
    assert "API_KEY" not in written
    assert written.get("EXTRA") == "hello"
    env = load_env("proj", "pw")
    assert env["API_KEY"] == "original"


def test_apply_template_overwrites_when_flag_set(tmp_path):
    _save("proj", {"API_KEY": "original"})
    template = tmp_path / "tmpl.env"
    template.write_text("API_KEY=replaced\n")
    apply_template("proj", "pw", str(template), overwrite=True)
    env = load_env("proj", "pw")
    assert env["API_KEY"] == "replaced"


def test_list_template_keys(tmp_path):
    template = tmp_path / "tmpl.env"
    template.write_text("FOO=1\nBAR=2\n# comment\n\nBAZ=3\n")
    keys = list_template_keys(str(template))
    assert keys == ["BAR", "BAZ", "FOO"]


def test_apply_template_missing_file_raises(tmp_path):
    with pytest.raises(TemplateError, match="Cannot read"):
        apply_template("proj", "pw", str(tmp_path / "nonexistent.env"))


def test_apply_template_invalid_line_raises(tmp_path):
    template = tmp_path / "bad.env"
    template.write_text("NODEQUALS\n")
    with pytest.raises(TemplateError, match="Invalid template line"):
        apply_template("proj", "pw", str(template))
