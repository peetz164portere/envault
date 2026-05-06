"""CLI commands for managing project tags in envault."""

from __future__ import annotations

import argparse
from typing import Optional
from pathlib import Path

from envault.tags import add_tag, remove_tag, get_tags, projects_with_tag, TagError


def cmd_tag_add(args: argparse.Namespace, vault_dir: Optional[Path] = None) -> None:
    """Add a tag to a project."""
    try:
        add_tag(args.project, args.tag, vault_dir=vault_dir)
        print(f"Tag '{args.tag}' added to project '{args.project}'.")
    except TagError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_tag_remove(args: argparse.Namespace, vault_dir: Optional[Path] = None) -> None:
    """Remove a tag from a project."""
    try:
        remove_tag(args.project, args.tag, vault_dir=vault_dir)
        print(f"Tag '{args.tag}' removed from project '{args.project}'.")
    except TagError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_tag_list(args: argparse.Namespace, vault_dir: Optional[Path] = None) -> None:
    """List tags for a project, or projects matching a tag."""
    try:
        if args.project:
            tags = get_tags(args.project, vault_dir=vault_dir)
            if not tags:
                print(f"No tags found for project '{args.project}'.")
            else:
                print(f"Tags for '{args.project}': {', '.join(sorted(tags))}")
        elif args.filter:
            projects = projects_with_tag(args.filter, vault_dir=vault_dir)
            if not projects:
                print(f"No projects tagged with '{args.filter}'.")
            else:
                print(f"Projects tagged '{args.filter}':")
                for proj in projects:
                    print(f"  {proj}")
        else:
            print("Specify --project or --filter.")
            raise SystemExit(1)
    except TagError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def register_tag_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register tag subcommands onto the given subparsers."""
    tag_parser = subparsers.add_parser("tag", help="Manage project tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    add_p = tag_sub.add_parser("add", help="Add a tag to a project")
    add_p.add_argument("project", help="Project name")
    add_p.add_argument("tag", help="Tag to add")
    add_p.set_defaults(func=cmd_tag_add)

    rm_p = tag_sub.add_parser("remove", help="Remove a tag from a project")
    rm_p.add_argument("project", help="Project name")
    rm_p.add_argument("tag", help="Tag to remove")
    rm_p.set_defaults(func=cmd_tag_remove)

    ls_p = tag_sub.add_parser("list", help="List tags or projects by tag")
    ls_p.add_argument("--project", default=None, help="Show tags for this project")
    ls_p.add_argument("--filter", default=None, help="Show projects with this tag")
    ls_p.set_defaults(func=cmd_tag_list)
