"""High-level vault operations: save, load, and delete env vars for a project."""

import json

from envault.crypto import decrypt, encrypt
from envault.storage import (
    delete_vault,
    list_vaults,
    read_vault,
    vault_exists,
    write_vault,
)


def save_env(project_name: str, env_vars: dict[str, str], password: str) -> None:
    """
    Encrypt and persist a dict of env vars for the given project.
    Overwrites any existing vault for that project.
    """
    plaintext = json.dumps(env_vars)
    encrypted = encrypt(plaintext, password)
    write_vault(project_name, encrypted)


def load_env(project_name: str, password: str) -> dict[str, str]:
    """
    Load and decrypt env vars for the given project.
    Raises FileNotFoundError if the vault doesn't exist.
    Raises ValueError if the password is wrong or data is corrupted.
    """
    encrypted = read_vault(project_name)
    plaintext = decrypt(encrypted, password)
    return json.loads(plaintext)


def remove_env(project_name: str) -> None:
    """Delete the vault for the given project."""
    delete_vault(project_name)


def project_exists(project_name: str) -> bool:
    """Return True if a vault exists for the given project."""
    return vault_exists(project_name)


def list_projects() -> list[str]:
    """Return all project names that have a stored vault."""
    return list_vaults()
