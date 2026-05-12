"""Tests for envault.env_validate."""
import pytest

from envault.env_validate import ValidationError, validate_project
from envault.schema import set_schema
from envault.vault import save_env


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return str(tmp_path)


def _save(project, env, password, vault_dir):
    save_env(project, env, password, vault_dir=vault_dir)


def test_validate_clean_project_has_no_issues(tmp_vault_dir):
    _save("web", {"PORT": "8080"}, "pass", tmp_vault_dir)
    set_schema("web", "PORT", pattern=r"\d+", vault_dir=tmp_vault_dir)
    result = validate_project("web", "pass", vault_dir=tmp_vault_dir)
    assert result.valid
    assert result.issues == []


def test_validate_pattern_mismatch_raises_error_issue(tmp_vault_dir):
    _save("web", {"PORT": "not-a-number"}, "pass", tmp_vault_dir)
    set_schema("web", "PORT", pattern=r"\d+", vault_dir=tmp_vault_dir)
    result = validate_project("web", "pass", vault_dir=tmp_vault_dir)
    assert not result.valid
    assert any(i.key == "PORT" and i.severity == "error" for i in result.issues)


def test_validate_required_key_present_and_non_empty_passes(tmp_vault_dir):
    _save("svc", {"API_KEY": "secret"}, "pass", tmp_vault_dir)
    set_schema("svc", "API_KEY", required=True, vault_dir=tmp_vault_dir)
    result = validate_project("svc", "pass", vault_dir=tmp_vault_dir)
    assert result.valid


def test_validate_required_key_empty_value_fails(tmp_vault_dir):
    _save("svc", {"API_KEY": ""}, "pass", tmp_vault_dir)
    set_schema("svc", "API_KEY", required=True, vault_dir=tmp_vault_dir)
    result = validate_project("svc", "pass", vault_dir=tmp_vault_dir)
    assert not result.valid
    assert any(i.key == "API_KEY" for i in result.issues)


def test_validate_required_key_missing_entirely_fails(tmp_vault_dir):
    _save("svc", {"OTHER": "val"}, "pass", tmp_vault_dir)
    set_schema("svc", "API_KEY", required=True, vault_dir=tmp_vault_dir)
    result = validate_project("svc", "pass", vault_dir=tmp_vault_dir)
    assert not result.valid
    assert any(i.key == "API_KEY" for i in result.issues)


def test_validate_allowed_values_mismatch_is_warning(tmp_vault_dir):
    _save("app", {"ENV": "staging"}, "pass", tmp_vault_dir)
    set_schema("app", "ENV", allowed_values=["production", "development"], vault_dir=tmp_vault_dir)
    result = validate_project("app", "pass", vault_dir=tmp_vault_dir)
    issues = [i for i in result.issues if i.key == "ENV"]
    assert issues
    assert issues[0].severity == "warning"
    # warnings do not make the result invalid
    assert result.valid


def test_validate_allowed_values_match_passes(tmp_vault_dir):
    _save("app", {"ENV": "production"}, "pass", tmp_vault_dir)
    set_schema("app", "ENV", allowed_values=["production", "development"], vault_dir=tmp_vault_dir)
    result = validate_project("app", "pass", vault_dir=tmp_vault_dir)
    assert result.valid


def test_validate_no_schema_defined_passes(tmp_vault_dir):
    """Projects with no schema rules should always validate successfully."""
    _save("bare", {"FOO": "bar", "BAZ": ""}, "pass", tmp_vault_dir)
    result = validate_project("bare", "pass", vault_dir=tmp_vault_dir)
    assert result.valid
    assert result.issues == []
