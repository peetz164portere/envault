"""Group multiple projects under a named environment group."""

import json
from pathlib import Path
from typing import List, Optional


class GroupError(Exception):
    pass


def _groups_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "groups.json"


def _load_groups(vault_dir: str) -> dict:
    p = _groups_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_groups(vault_dir: str, data: dict) -> None:
    p = _groups_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def create_group(vault_dir: str, group: str, projects: List[str]) -> None:
    """Create or overwrite a named group with the given project list."""
    if not group.strip():
        raise GroupError("Group name must not be empty.")
    if not projects:
        raise GroupError("Group must contain at least one project.")
    data = _load_groups(vault_dir)
    data[group] = list(dict.fromkeys(projects))  # deduplicate, preserve order
    _save_groups(vault_dir, data)


def get_group(vault_dir: str, group: str) -> List[str]:
    """Return the list of projects in a group."""
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    return data[group]


def delete_group(vault_dir: str, group: str) -> None:
    """Remove a group by name."""
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    del data[group]
    _save_groups(vault_dir, data)


def add_project_to_group(vault_dir: str, group: str, project: str) -> None:
    """Add a project to an existing group."""
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if project not in data[group]:
        data[group].append(project)
    _save_groups(vault_dir, data)


def remove_project_from_group(vault_dir: str, group: str, project: str) -> None:
    """Remove a project from a group."""
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if project not in data[group]:
        raise GroupError(f"Project '{project}' is not in group '{group}'.")
    data[group].remove(project)
    _save_groups(vault_dir, data)


def list_groups(vault_dir: str) -> List[str]:
    """Return all group names."""
    return list(_load_groups(vault_dir).keys())
