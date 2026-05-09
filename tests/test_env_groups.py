import pytest
from envault.env_groups import (
    GroupError,
    create_group,
    get_group,
    delete_group,
    add_project_to_group,
    remove_project_from_group,
    list_groups,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_create_and_get_group(tmp_vault_dir):
    create_group(tmp_vault_dir, "staging", ["app", "db"])
    assert get_group(tmp_vault_dir, "staging") == ["app", "db"]


def test_create_group_deduplicates_projects(tmp_vault_dir):
    create_group(tmp_vault_dir, "prod", ["app", "app", "db"])
    assert get_group(tmp_vault_dir, "prod") == ["app", "db"]


def test_create_group_empty_name_raises(tmp_vault_dir):
    with pytest.raises(GroupError, match="empty"):
        create_group(tmp_vault_dir, "  ", ["app"])


def test_create_group_empty_projects_raises(tmp_vault_dir):
    with pytest.raises(GroupError, match="at least one"):
        create_group(tmp_vault_dir, "g", [])


def test_get_missing_group_raises(tmp_vault_dir):
    with pytest.raises(GroupError, match="does not exist"):
        get_group(tmp_vault_dir, "nope")


def test_delete_group_removes_it(tmp_vault_dir):
    create_group(tmp_vault_dir, "dev", ["svc"])
    delete_group(tmp_vault_dir, "dev")
    assert "dev" not in list_groups(tmp_vault_dir)


def test_delete_missing_group_raises(tmp_vault_dir):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group(tmp_vault_dir, "ghost")


def test_add_project_to_group(tmp_vault_dir):
    create_group(tmp_vault_dir, "team", ["alpha"])
    add_project_to_group(tmp_vault_dir, "team", "beta")
    assert "beta" in get_group(tmp_vault_dir, "team")


def test_add_project_to_group_idempotent(tmp_vault_dir):
    create_group(tmp_vault_dir, "team", ["alpha"])
    add_project_to_group(tmp_vault_dir, "team", "alpha")
    assert get_group(tmp_vault_dir, "team").count("alpha") == 1


def test_add_project_to_missing_group_raises(tmp_vault_dir):
    with pytest.raises(GroupError, match="does not exist"):
        add_project_to_group(tmp_vault_dir, "no-group", "proj")


def test_remove_project_from_group(tmp_vault_dir):
    create_group(tmp_vault_dir, "grp", ["a", "b"])
    remove_project_from_group(tmp_vault_dir, "grp", "a")
    assert get_group(tmp_vault_dir, "grp") == ["b"]


def test_remove_project_not_in_group_raises(tmp_vault_dir):
    create_group(tmp_vault_dir, "grp", ["a"])
    with pytest.raises(GroupError, match="not in group"):
        remove_project_from_group(tmp_vault_dir, "grp", "z")


def test_list_groups_returns_all_names(tmp_vault_dir):
    create_group(tmp_vault_dir, "x", ["p1"])
    create_group(tmp_vault_dir, "y", ["p2"])
    groups = list_groups(tmp_vault_dir)
    assert set(groups) == {"x", "y"}


def test_list_groups_empty_vault(tmp_vault_dir):
    assert list_groups(tmp_vault_dir) == []
