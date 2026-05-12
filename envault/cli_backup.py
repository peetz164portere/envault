"""CLI commands for vault backup and restore."""

import sys
from pathlib import Path

from envault.storage import ensure_vault_dir
from envault.backup import BackupError, create_backup, restore_backup, list_backups


def _vault_dir(args) -> Path:
    return Path(args.vault_dir)


def cmd_backup_create(args) -> None:
    vault_dir = _vault_dir(args)
    output = Path(args.output) if getattr(args, "output", None) else None
    try:
        path = create_backup(vault_dir, output_path=output)
        print(f"Backup created: {path}")
    except BackupError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_backup_restore(args) -> None:
    vault_dir = _vault_dir(args)
    backup_path = Path(args.backup_file)
    overwrite = getattr(args, "overwrite", False)
    if not backup_path.exists():
        print(f"Error: backup file not found: {backup_path}", file=sys.stderr)
        sys.exit(1)
    if not backup_path.suffix == ".zip":
        print(f"Error: backup file must be a .zip archive: {backup_path}", file=sys.stderr)
        sys.exit(1)
    try:
        restored = restore_backup(vault_dir, backup_path, overwrite=overwrite)
        if restored:
            print("Restored projects:")
            for name in restored:
                print(f"  {name}")
        else:
            print("No projects restored.")
    except BackupError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_backup_list(args) -> None:
    vault_dir = _vault_dir(args)
    backups = list_backups(vault_dir)
    if not backups:
        print("No backups found.")
    else:
        for name in backups:
            print(f"  {name}")


def register_backup_commands(subparsers, vault_dir: str) -> None:
    p_create = subparsers.add_parser("backup-create", help="Create a backup archive")
    p_create.add_argument("--output", default=None, help="Output zip path")
    p_create.set_defaults(func=cmd_backup_create, vault_dir=vault_dir)

    p_restore = subparsers.add_parser("backup-restore", help="Restore from a backup archive")
    p_restore.add_argument("backup_file", help="Path to backup zip")
    p_restore.add_argument("--overwrite", action="store_true", help="Overwrite existing vaults")
    p_restore.set_defaults(func=cmd_backup_restore, vault_dir=vault_dir)

    p_list = subparsers.add_parser("backup-list", help="List available backups")
    p_list.set_defaults(func=cmd_backup_list, vault_dir=vault_dir)
