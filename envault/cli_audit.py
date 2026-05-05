"""CLI commands for audit log inspection."""

import argparse
import sys
from typing import Optional

from envault.audit import read_events, clear_events


def cmd_audit_log(args: argparse.Namespace, vault_dir: Optional[str] = None) -> None:
    """Print audit log events, optionally filtered by project."""
    project = getattr(args, "project", None)
    events = read_events(project=project, vault_dir=vault_dir)

    if not events:
        msg = "No audit events found"
        if project:
            msg += f" for project '{project}'"
        print(msg + ".")
        return

    header = f"{'Timestamp':<30} {'Action':<10} {'Project':<20} {'OK':<6} {'Detail'}"
    print(header)
    print("-" * len(header))
    for e in events:
        ts = e.get("timestamp", "")[:26]
        action = e.get("action", "")
        proj = e.get("project", "")
        ok = "yes" if e.get("success") else "no"
        detail = e.get("detail", "")
        print(f"{ts:<30} {action:<10} {proj:<20} {ok:<6} {detail}")


def cmd_audit_clear(args: argparse.Namespace, vault_dir: Optional[str] = None) -> None:
    """Clear the audit log after confirmation."""
    if not getattr(args, "yes", False):
        confirm = input("Clear all audit logs? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return
    clear_events(vault_dir=vault_dir)
    print("Audit log cleared.")


def register_audit_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register 'audit' subcommands onto an existing subparsers object."""
    audit_parser = subparsers.add_parser("audit", help="Audit log commands")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    # audit log
    log_parser = audit_sub.add_parser("log", help="Show audit log")
    log_parser.add_argument(
        "--project", "-p", default=None, help="Filter by project name"
    )
    log_parser.set_defaults(func=cmd_audit_log)

    # audit clear
    clear_parser = audit_sub.add_parser("clear", help="Clear audit log")
    clear_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    clear_parser.set_defaults(func=cmd_audit_clear)
