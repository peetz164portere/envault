"""Rename keys or projects within the vault."""

from __future__ import annotations

from envault.vault import load_env, save_env, project_exists, list_projects


class RenameError(Exception):
    pass


def rename_key(
    project: str,
    old_key: str,
    new_key: str,
    password: str,
) -> None:
    """Rename a single key inside a project, preserving all other keys."""
    if not project_exists(project):
        raise RenameError(f"Project '{project}' does not exist.")
    if not old_key or not new_key:
        raise RenameError("Key names must not be empty.")
    if old_key == new_key:
        raise RenameError("Old and new key names are identical.")

    env = load_env(project, password)

    if old_key not in env:
        raise RenameError(f"Key '{old_key}' not found in project '{project}'.")
    if new_key in env:
        raise RenameError(
            f"Key '{new_key}' already exists in project '{project}'. "
            "Remove it first or choose a different name."
        )

    env[new_key] = env.pop(old_key)
    save_env(project, env, password)


def rename_project(
    old_name: str,
    new_name: str,
    password: str,
    new_password: str | None = None,
) -> None:
    """Copy a project under a new name then remove the old one.

    If *new_password* is provided the new project is encrypted with it;
    otherwise the same password is reused.
    """
    if not old_name or not new_name:
        raise RenameError("Project names must not be empty.")
    if old_name == new_name:
        raise RenameError("Old and new project names are identical.")
    if not project_exists(old_name):
        raise RenameError(f"Project '{old_name}' does not exist.")
    if project_exists(new_name):
        raise RenameError(
            f"Project '{new_name}' already exists. Remove it first."
        )

    env = load_env(old_name, password)
    dest_password = new_password if new_password is not None else password
    save_env(new_name, env, dest_password)

    # Remove the old vault file
    from envault.storage import delete_vault
    delete_vault(old_name)
