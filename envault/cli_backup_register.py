"""Integration helper: register backup commands into the main CLI.

This thin module is imported by the main entry point so backup
subcommands appear alongside all other envault commands.

Usage in cli.py (or main entry point)::

    from envault.cli_backup_register import attach
    attach(subparsers, vault_dir)
"""

from __future__ import annotations

from envault.cli_backup import register_backup_commands


def attach(subparsers, vault_dir: str) -> None:
    """Register all backup-related subcommands onto *subparsers*.

    Args:
        subparsers: The argparse subparsers action object from the main parser.
        vault_dir:  Resolved path to the active vault directory, forwarded
                    to every backup command as ``args.vault_dir``.
    """
    register_backup_commands(subparsers, vault_dir)


# Convenience: expose the individual command handlers at package level
# so callers can import them without going through cli_backup directly.
from envault.cli_backup import (  # noqa: E402  (re-export)
    cmd_backup_create,
    cmd_backup_restore,
    cmd_backup_list,
)

__all__ = [
    "attach",
    "cmd_backup_create",
    "cmd_backup_restore",
    "cmd_backup_list",
]
