"""Backup and restore entire vault archives."""

import json
import zipfile
import os
from pathlib import Path
from datetime import datetime, timezone

from envault.storage import _vault_path, ensure_vault_dir, list_vaults
from envault.vault import load_env, save_env


class BackupError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_backup(vault_dir: Path, output_path: Path | None = None) -> Path:
    """Create a zip archive of all raw vault files (still encrypted)."""
    ensure_vault_dir(vault_dir)
    if output_path is None:
        output_path = vault_dir / f"backup_{_now_iso()}.zip"

    vault_files = list(vault_dir.glob("*.vault"))
    if not vault_files:
        raise BackupError("No vault files found to back up.")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for vf in vault_files:
            zf.write(vf, arcname=vf.name)

    return output_path


def restore_backup(vault_dir: Path, backup_path: Path, overwrite: bool = False) -> list[str]:
    """Restore vault files from a zip archive. Returns list of restored project names."""
    if not backup_path.exists():
        raise BackupError(f"Backup file not found: {backup_path}")

    ensure_vault_dir(vault_dir)
    restored = []

    with zipfile.ZipFile(backup_path, "r") as zf:
        for name in zf.namelist():
            if not name.endswith(".vault"):
                continue
            dest = vault_dir / name
            if dest.exists() and not overwrite:
                raise BackupError(
                    f"Vault '{name}' already exists. Use overwrite=True to replace."
                )
            zf.extract(name, vault_dir)
            restored.append(name.removesuffix(".vault"))

    return restored


def list_backups(vault_dir: Path) -> list[str]:
    """Return sorted list of backup archive filenames in the vault directory."""
    return sorted(p.name for p in vault_dir.glob("backup_*.zip"))
