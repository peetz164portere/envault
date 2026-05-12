"""CLI commands for renaming keys and projects."""

from __future__ import annotations

import argparse
import sys

from envault.env_rename import RenameError, rename_key, rename_project


def cmd_rename_key(args: argparse.Namespace) -> None:
    try:
        rename_key(args.project, args.old_key, args.new_key, args.password)
        print(
            f"Key '{args.old_key}' renamed to '{args.new_key}' "
            f"in project '{args.project}'."
        )
    except RenameError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_rename_project(args: argparse.Namespace) -> None:
    new_pw = getattr(args, "new_password", None) or None
    try:
        rename_project(args.old_name, args.new_name, args.password, new_pw)
        print(f"Project '{args.old_name}' renamed to '{args.new_name}'.")
    except RenameError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_rename_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    # rename-key
    p_key = subparsers.add_parser(
        "rename-key", help="Rename an environment variable key inside a project."
    )
    p_key.add_argument("project", help="Project name.")
    p_key.add_argument("old_key", help="Existing key name.")
    p_key.add_argument("new_key", help="New key name.")
    p_key.add_argument("--password", required=True, help="Vault password.")
    p_key.set_defaults(func=cmd_rename_key)

    # rename-project
    p_proj = subparsers.add_parser(
        "rename-project", help="Rename an entire project."
    )
    p_proj.add_argument("old_name", help="Current project name.")
    p_proj.add_argument("new_name", help="New project name.")
    p_proj.add_argument("--password", required=True, help="Current vault password.")
    p_proj.add_argument(
        "--new-password",
        default=None,
        help="Optional new password for the renamed project.",
    )
    p_proj.set_defaults(func=cmd_rename_project)
