"""Tests for envault.env_lint."""

import pytest

from envault.vault import save_env
from envault.env_lint import lint_project, LintError, LintIssue


@pytest.fixture
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _save(project, env, password, vault_dir):
    save_env(project, env, password, vault_dir=str(vault_dir))


def test_lint_clean_project_has_no_issues(tmp_vault_dir):
    _save("myapp", {"DATABASE_URL": "postgres://localhost/db", "API_KEY": "supersecretvalue"}, "pw", tmp_vault_dir)
    result = lint_project("myapp", "pw", vault_dir=str(tmp_vault_dir))
    assert result.project == "myapp"
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_lint_empty_project_returns_info(tmp_vault_dir):
    _save("empty", {}, "pw", tmp_vault_dir)
    result = lint_project("empty", "pw", vault_dir=str(tmp_vault_dir))
    assert len(result.issues) == 1
    assert result.issues[0].severity == "info"
    assert result.issues[0].key == "*"


def test_lint_detects_non_upper_snake_case(tmp_vault_dir):
    _save("proj", {"myKey": "value"}, "pw", tmp_vault_dir)
    result = lint_project("proj", "pw", vault_dir=str(tmp_vault_dir))
    keys_with_issues = [i.key for i in result.issues]
    assert "myKey" in keys_with_issues
    severities = {i.key: i.severity for i in result.issues}
    assert severities["myKey"] == "warning"


def test_lint_detects_empty_value(tmp_vault_dir):
    _save("proj", {"EMPTY_VAR": ""}, "pw", tmp_vault_dir)
    result = lint_project("proj", "pw", vault_dir=str(tmp_vault_dir))
    issue = next(i for i in result.issues if i.key == "EMPTY_VAR")
    assert issue.severity == "warning"
    assert "empty" in issue.message.lower()


def test_lint_detects_placeholder_value(tmp_vault_dir):
    _save("proj", {"SECRET_KEY": "CHANGE_ME"}, "pw", tmp_vault_dir)
    result = lint_project("proj", "pw", vault_dir=str(tmp_vault_dir))
    issue = next(i for i in result.issues if i.key == "SECRET_KEY")
    assert issue.severity == "error"
    assert result.has_errors


def test_lint_detects_short_secret(tmp_vault_dir):
    _save("proj", {"API_TOKEN": "abc"}, "pw", tmp_vault_dir)
    result = lint_project("proj", "pw", vault_dir=str(tmp_vault_dir))
    issue = next(i for i in result.issues if i.key == "API_TOKEN")
    assert issue.severity == "warning"
    assert "short" in issue.message.lower()


def test_lint_wrong_password_raises(tmp_vault_dir):
    _save("proj", {"FOO": "bar"}, "correct", tmp_vault_dir)
    with pytest.raises(LintError):
        lint_project("proj", "wrong", vault_dir=str(tmp_vault_dir))


def test_lint_missing_project_raises(tmp_vault_dir):
    with pytest.raises(LintError):
        lint_project("nonexistent", "pw", vault_dir=str(tmp_vault_dir))


def test_lint_multiple_issues_collected(tmp_vault_dir):
    _save("proj", {
        "badKey": "",
        "ANOTHER_SECRET": "FIXME",
    }, "pw", tmp_vault_dir)
    result = lint_project("proj", "pw", vault_dir=str(tmp_vault_dir))
    assert len(result.issues) >= 2
