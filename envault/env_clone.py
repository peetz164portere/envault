"""Clone a project vault to a new name, optionally re-encrypting with a new password."""

from __future__ import annotations

from envault.vault import load_env, save_env, project_exists


class CloneError(Exception):
    """Raised when a clone operation fails."""


def clone_project(
    src: str,
    dst: str,
    src_password: str,
    dst_password: str | None = None,
    vault_dir: str | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Clone *src* project into *dst*.

    Parameters
    ----------
    src:          name of the source project
    dst:          name of the destination project
    src_password: password used to decrypt *src*
    dst_password: password used to encrypt *dst*; defaults to *src_password*
    vault_dir:    override vault directory (used in tests)
    overwrite:    if False, raise CloneError when *dst* already exists

    Returns the env dict that was written to *dst*.
    """
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    if not project_exists(src, **kwargs):
        raise CloneError(f"Source project '{src}' does not exist.")

    if not overwrite and project_exists(dst, **kwargs):
        raise CloneError(
            f"Destination project '{dst}' already exists. "
            "Pass overwrite=True to replace it."
        )

    env = load_env(src, src_password, **kwargs)

    effective_password = dst_password if dst_password is not None else src_password
    save_env(dst, env, effective_password, **kwargs)

    return env


def clone_with_filter(
    src: str,
    dst: str,
    src_password: str,
    keys: list[str],
    dst_password: str | None = None,
    vault_dir: str | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Clone only *keys* from *src* into *dst*."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    if not project_exists(src, **kwargs):
        raise CloneError(f"Source project '{src}' does not exist.")

    if not overwrite and project_exists(dst, **kwargs):
        raise CloneError(
            f"Destination project '{dst}' already exists. "
            "Pass overwrite=True to replace it."
        )

    full_env = load_env(src, src_password, **kwargs)
    missing = [k for k in keys if k not in full_env]
    if missing:
        raise CloneError(f"Keys not found in '{src}': {', '.join(missing)}")

    subset = {k: full_env[k] for k in keys}
    effective_password = dst_password if dst_password is not None else src_password
    save_env(dst, subset, effective_password, **kwargs)

    return subset
