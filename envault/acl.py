"""Per-project access control lists — restrict which system users can read a project."""

import json
import os
from pathlib import Path
from typing import List, Optional

from envault.storage import ensure_vault_dir, _vault_path


class ACLError(Exception):
    pass


def _acl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "acl.json"


def _load_acl(vault_dir: str) -> dict:
    path = _acl_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_acl(vault_dir: str, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    path = _acl_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_user(vault_dir: str, project: str, username: str) -> None:
    """Grant a system user access to a project."""
    if not username or not username.strip():
        raise ACLError("Username must not be empty.")
    if not project or not project.strip():
        raise ACLError("Project name must not be empty.")
    data = _load_acl(vault_dir)
    users = set(data.get(project, []))
    users.add(username.strip())
    data[project] = sorted(users)
    _save_acl(vault_dir, data)


def remove_user(vault_dir: str, project: str, username: str) -> None:
    """Revoke a system user's access to a project."""
    data = _load_acl(vault_dir)
    users = set(data.get(project, []))
    users.discard(username.strip())
    if users:
        data[project] = sorted(users)
    else:
        data.pop(project, None)
    _save_acl(vault_dir, data)


def list_users(vault_dir: str, project: str) -> List[str]:
    """Return list of users allowed to access a project."""
    data = _load_acl(vault_dir)
    return data.get(project, [])


def is_allowed(vault_dir: str, project: str, username: str) -> bool:
    """Return True if username is in the ACL for project, or ACL is empty (open)."""
    users = list_users(vault_dir, project)
    if not users:
        return True  # no ACL set means unrestricted
    return username.strip() in users


def clear_acl(vault_dir: str, project: str) -> None:
    """Remove all ACL entries for a project (make it unrestricted)."""
    data = _load_acl(vault_dir)
    data.pop(project, None)
    _save_acl(vault_dir, data)
