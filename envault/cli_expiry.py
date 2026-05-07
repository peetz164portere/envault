"""CLI commands for managing project expiry dates."""

from __future__ import annotations

import sys

from envault.expiry import (
    ExpiryError,
    set_expiry,
    get_expiry,
    is_expired,
    clear_expiry,
    list_expiries,
)
from envault.storage import DEFAULT_VAULT_DIR


def cmd_expiry_set(args) -> None:
    """Set an expiry date for a project."""
    vault_dir = getattr(args, "vault_dir", DEFAULT_VAULT_DIR)
    try:
        set_expiry(vault_dir, args.project, args.expires_at)
        print(f"Expiry set for '{args.project}': {args.expires_at}")
    except ExpiryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_expiry_get(args) -> None:
    """Show the expiry date for a project."""
    vault_dir = getattr(args, "vault_dir", DEFAULT_VAULT_DIR)
    value = get_expiry(vault_dir, args.project)
    if value is None:
        print(f"No expiry set for '{args.project}'.")
    else:
        expired = is_expired(vault_dir, args.project)
        status = " [EXPIRED]" if expired else ""
        print(f"{args.project}: {value}{status}")


def cmd_expiry_clear(args) -> None:
    """Remove the expiry date for a project."""
    vault_dir = getattr(args, "vault_dir", DEFAULT_VAULT_DIR)
    try:
        clear_expiry(vault_dir, args.project)
        print(f"Expiry cleared for '{args.project}'.")
    except ExpiryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_expiry_list(args) -> None:
    """List all projects with expiry dates."""
    vault_dir = getattr(args, "vault_dir", DEFAULT_VAULT_DIR)
    entries = list_expiries(vault_dir)
    if not entries:
        print("No expiry dates set.")
        return
    for project, ts in sorted(entries.items()):
        expired = is_expired(vault_dir, project)
        flag = " [EXPIRED]" if expired else ""
        print(f"  {project}: {ts}{flag}")


def register_expiry_commands(subparsers) -> None:
    """Attach expiry sub-commands to an argparse subparsers object."""
    p_set = subparsers.add_parser("expiry-set", help="Set project expiry date")
    p_set.add_argument("project")
    p_set.add_argument("expires_at", help="ISO-8601 datetime with timezone")
    p_set.set_defaults(func=cmd_expiry_set)

    p_get = subparsers.add_parser("expiry-get", help="Get project expiry date")
    p_get.add_argument("project")
    p_get.set_defaults(func=cmd_expiry_get)

    p_clear = subparsers.add_parser("expiry-clear", help="Clear project expiry date")
    p_clear.add_argument("project")
    p_clear.set_defaults(func=cmd_expiry_clear)

    p_list = subparsers.add_parser("expiry-list", help="List all expiry dates")
    p_list.set_defaults(func=cmd_expiry_list)
