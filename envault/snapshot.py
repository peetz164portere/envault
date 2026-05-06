"""Snapshot support: save and restore named snapshots of a project's env vars."""

from __future__ import annotations

import json
from typing import Optional

from envault.storage import _vault_path, ensure_vault_dir, read_vault, write_vault
from envault.vault import load_env, save_env


class SnapshotError(Exception):
    pass


def _snapshot_key(snapshot_name: str) -> str:
    """Return a namespaced project name for storing a snapshot."""
    return f"__snapshot__{snapshot_name}"


def save_snapshot(
    project: str,
    snapshot_name: str,
    password: str,
    vault_dir: Optional[str] = None,
) -> None:
    """Save the current env of *project* as a named snapshot."""
    env = load_env(project, password, vault_dir=vault_dir)
    snapshot_project = _snapshot_key(f"{project}__{snapshot_name}")
    save_env(snapshot_project, env, password, vault_dir=vault_dir)


def restore_snapshot(
    project: str,
    snapshot_name: str,
    password: str,
    vault_dir: Optional[str] = None,
) -> dict[str, str]:
    """Restore a snapshot into *project*, returning the restored env."""
    snapshot_project = _snapshot_key(f"{project}__{snapshot_name}")
    try:
        env = load_env(snapshot_project, password, vault_dir=vault_dir)
    except FileNotFoundError:
        raise SnapshotError(
            f"Snapshot '{snapshot_name}' not found for project '{project}'."
        )
    save_env(project, env, password, vault_dir=vault_dir)
    return env


def list_snapshots(
    project: str,
    password: str,
    vault_dir: Optional[str] = None,
) -> list[str]:
    """Return snapshot names available for *project*."""
    from envault.vault import list_projects

    prefix = _snapshot_key(f"{project}__")
    all_projects = list_projects(vault_dir=vault_dir)
    names = []
    for p in all_projects:
        if p.startswith(prefix):
            names.append(p[len(prefix):])
    return sorted(names)


def delete_snapshot(
    project: str,
    snapshot_name: str,
    vault_dir: Optional[str] = None,
) -> None:
    """Delete a named snapshot."""
    from envault.vault import remove_env

    snapshot_project = _snapshot_key(f"{project}__{snapshot_name}")
    try:
        remove_env(snapshot_project, vault_dir=vault_dir)
    except FileNotFoundError:
        raise SnapshotError(
            f"Snapshot '{snapshot_name}' not found for project '{project}'."
        )
