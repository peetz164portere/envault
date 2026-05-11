import pytest
from pathlib import Path
from envault.session import (
    set_active_project,
    get_active_project,
    clear_active_project,
    session_info,
    SessionError,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_active_project(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "myapp")
    assert get_active_project(tmp_vault_dir) == "myapp"


def test_get_active_project_not_set_returns_none(tmp_vault_dir):
    assert get_active_project(tmp_vault_dir) is None


def test_set_active_project_overwrites_previous(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "first")
    set_active_project(tmp_vault_dir, "second")
    assert get_active_project(tmp_vault_dir) == "second"


def test_set_active_project_strips_whitespace(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "  spaced  ")
    assert get_active_project(tmp_vault_dir) == "spaced"


def test_set_active_project_empty_raises(tmp_vault_dir):
    with pytest.raises(SessionError):
        set_active_project(tmp_vault_dir, "")


def test_set_active_project_whitespace_only_raises(tmp_vault_dir):
    with pytest.raises(SessionError):
        set_active_project(tmp_vault_dir, "   ")


def test_clear_active_project_removes_entry(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "myapp")
    clear_active_project(tmp_vault_dir)
    assert get_active_project(tmp_vault_dir) is None


def test_clear_active_project_idempotent(tmp_vault_dir):
    clear_active_project(tmp_vault_dir)  # no error when nothing set
    assert get_active_project(tmp_vault_dir) is None


def test_session_info_returns_dict(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "proj")
    info = session_info(tmp_vault_dir)
    assert isinstance(info, dict)
    assert info["active_project"] == "proj"


def test_session_file_created_on_set(tmp_vault_dir):
    set_active_project(tmp_vault_dir, "proj")
    session_file = Path(tmp_vault_dir) / ".session.json"
    assert session_file.exists()


def test_session_info_empty_before_set(tmp_vault_dir):
    assert session_info(tmp_vault_dir) == {}
