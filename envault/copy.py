"""Copy or clone environment variables between projects."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_env, save_env, project_exists


class CopyError(Exception):
    pass


def copy_project(
    src_project: str,
    src_password: str,
    dst_project: str,
    dst_password: str,
    keys: Optional[list[str]] = None,
    vault_dir: Optional[str] = None,
) -> dict[str, str]:
    """Copy env vars from src_project to dst_project.

    If *keys* is provided, only those keys are copied; otherwise all keys
    are copied.  The destination project is created or merged into.
    Returns the dict of copied key/value pairs.
    """
    if not project_exists(src_project, vault_dir=vault_dir):
        raise CopyError(f"Source project '{src_project}' does not exist.")

    src_env = load_env(src_project, src_password, vault_dir=vault_dir)

    if keys is not None:
        missing = [k for k in keys if k not in src_env]
        if missing:
            raise CopyError(
                f"Key(s) not found in '{src_project}': {', '.join(missing)}"
            )
        to_copy = {k: src_env[k] for k in keys}
    else:
        to_copy = dict(src_env)

    # Merge into destination if it already exists
    if project_exists(dst_project, vault_dir=vault_dir):
        dst_env = load_env(dst_project, dst_password, vault_dir=vault_dir)
        dst_env.update(to_copy)
        merged = dst_env
    else:
        merged = to_copy

    save_env(dst_project, merged, dst_password, vault_dir=vault_dir)
    return to_copy


def merge_projects(
    src_project: str,
    src_password: str,
    dst_project: str,
    dst_password: str,
    vault_dir: Optional[str] = None,
) -> dict[str, str]:
    """Alias for copy_project without key filtering — copies everything."""
    return copy_project(
        src_project,
        src_password,
        dst_project,
        dst_password,
        keys=None,
        vault_dir=vault_dir,
    )
