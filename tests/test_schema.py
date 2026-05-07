"""Tests for envault/schema.py"""

import pytest
from envault.schema import (
    SchemaError,
    set_schema,
    remove_schema,
    get_schema,
    validate,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_set_schema_creates_rule(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "DATABASE_URL", required=True)
    rules = get_schema(tmp_vault_dir, "myapp")
    assert "DATABASE_URL" in rules
    assert rules["DATABASE_URL"]["required"] is True


def test_set_schema_with_pattern(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "PORT", pattern=r"\d+")
    rules = get_schema(tmp_vault_dir, "myapp")
    assert rules["PORT"]["pattern"] == r"\d+"


def test_set_schema_invalid_pattern_raises(tmp_vault_dir):
    with pytest.raises(SchemaError, match="Invalid regex"):
        set_schema(tmp_vault_dir, "myapp", "KEY", pattern="[invalid")


def test_set_schema_empty_key_raises(tmp_vault_dir):
    with pytest.raises(SchemaError, match="empty"):
        set_schema(tmp_vault_dir, "myapp", "")


def test_get_schema_missing_project_returns_empty(tmp_vault_dir):
    assert get_schema(tmp_vault_dir, "ghost") == {}


def test_remove_schema_deletes_rule(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "SECRET_KEY", required=True)
    remove_schema(tmp_vault_dir, "myapp", "SECRET_KEY")
    assert "SECRET_KEY" not in get_schema(tmp_vault_dir, "myapp")


def test_remove_schema_missing_key_raises(tmp_vault_dir):
    with pytest.raises(SchemaError, match="No schema rule"):
        remove_schema(tmp_vault_dir, "myapp", "NONEXISTENT")


def test_validate_passes_when_all_required_present(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "DB", required=True)
    violations = validate(tmp_vault_dir, "myapp", {"DB": "postgres://localhost/db"})
    assert violations == []


def test_validate_reports_missing_required_key(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "DB", required=True)
    violations = validate(tmp_vault_dir, "myapp", {})
    assert any("DB" in v for v in violations)


def test_validate_reports_pattern_mismatch(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "PORT", pattern=r"\d+")
    violations = validate(tmp_vault_dir, "myapp", {"PORT": "not-a-number"})
    assert any("PORT" in v for v in violations)


def test_validate_passes_when_pattern_matches(tmp_vault_dir):
    set_schema(tmp_vault_dir, "myapp", "PORT", pattern=r"\d+")
    violations = validate(tmp_vault_dir, "myapp", {"PORT": "5432"})
    assert violations == []


def test_validate_no_schema_returns_empty(tmp_vault_dir):
    violations = validate(tmp_vault_dir, "noschema", {"ANY": "value"})
    assert violations == []
