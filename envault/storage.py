"""Handles reading and writing encrypted vault files on disk."""

import json
import os
from pathlib import Path

VAULT_DIR = Path.home() / ".envault" / "vaults"


def _vault_path(project_name: str) -> Path:
    return VAULT_DIR / f"{project_name}.vault"


def ensure_vault_dir() -> None:
    """Create the vault storage directory if it doesn't exist."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)


def vault_exists(project_name: str) -> bool:
    """Return True if a vault for the given project exists."""
    return _vault_path(project_name).exists()


def write_vault(project_name: str, encrypted_data: str) -> None:
    """Persist encrypted vault data to disk."""
    ensure_vault_dir()
    path = _vault_path(project_name)
    payload = {"project": project_name, "data": encrypted_data}
    path.write_text(json.dumps(payload), encoding="utf-8")


def read_vault(project_name: str) -> str:
    """Read and return the encrypted data string from a vault file."""
    path = _vault_path(project_name)
    if not path.exists():
        raise FileNotFoundError(f"No vault found for project '{project_name}'")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["data"]


def delete_vault(project_name: str) -> None:
    """Delete a vault file from disk."""
    path = _vault_path(project_name)
    if not path.exists():
        raise FileNotFoundError(f"No vault found for project '{project_name}'")
    path.unlink()


def list_vaults() -> list[str]:
    """Return a list of all stored project vault names."""
    if not VAULT_DIR.exists():
        return []
    return [p.stem for p in VAULT_DIR.glob("*.vault")]
