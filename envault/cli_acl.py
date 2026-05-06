"""CLI commands for managing project ACLs."""

import os
from envault.acl import add_user, remove_user, list_users, clear_acl, is_allowed, ACLError


def cmd_acl_add(args) -> None:
    """Grant a user access to a project."""
    try:
        add_user(args.vault_dir, args.project, args.username)
        print(f"User '{args.username}' added to ACL for project '{args.project}'.")
    except ACLError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_acl_remove(args) -> None:
    """Revoke a user's access to a project."""
    try:
        remove_user(args.vault_dir, args.project, args.username)
        print(f"User '{args.username}' removed from ACL for project '{args.project}'.")
    except ACLError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_acl_list(args) -> None:
    """List users allowed to access a project."""
    users = list_users(args.vault_dir, args.project)
    if not users:
        print(f"No ACL set for '{args.project}' — access is unrestricted.")
    else:
        print(f"ACL for '{args.project}':")
        for u in users:
            print(f"  {u}")


def cmd_acl_check(args) -> None:
    """Check if a user is allowed to access a project."""
    allowed = is_allowed(args.vault_dir, args.project, args.username)
    status = "ALLOWED" if allowed else "DENIED"
    print(f"User '{args.username}' is {status} for project '{args.project}'.")
    if not allowed:
        raise SystemExit(1)


def cmd_acl_clear(args) -> None:
    """Clear all ACL entries for a project (make it unrestricted)."""
    clear_acl(args.vault_dir, args.project)
    print(f"ACL cleared for project '{args.project}'. Access is now unrestricted.")


def register_acl_commands(subparsers, vault_dir: str) -> None:
    """Register ACL subcommands onto an argparse subparsers object."""
    def _add(name, fn, help_text, need_user=True):
        p = subparsers.add_parser(name, help=help_text)
        p.set_defaults(func=fn, vault_dir=vault_dir)
        p.add_argument("project", help="Project name")
        if need_user:
            p.add_argument("username", help="System username")

    _add("acl-add", cmd_acl_add, "Grant a user access to a project")
    _add("acl-remove", cmd_acl_remove, "Revoke a user's access to a project")
    _add("acl-check", cmd_acl_check, "Check if a user can access a project")
    _add("acl-list", cmd_acl_list, "List users in a project's ACL", need_user=False)
    _add("acl-clear", cmd_acl_clear, "Clear all ACL entries for a project", need_user=False)
