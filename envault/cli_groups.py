"""CLI commands for managing environment groups."""

import argparse
from envault.env_groups import (
    GroupError,
    create_group,
    get_group,
    delete_group,
    add_project_to_group,
    remove_project_from_group,
    list_groups,
)
from envault.storage import ensure_vault_dir


def _vault_dir() -> str:
    from envault.storage import _vault_path
    import os
    return str(_vault_path("").parent)


def cmd_group_create(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    try:
        create_group(vault_dir, args.group, args.projects)
        print(f"Group '{args.group}' created with projects: {', '.join(args.projects)}")
    except GroupError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_group_get(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    try:
        projects = get_group(vault_dir, args.group)
        print(f"Group '{args.group}': {', '.join(projects)}")
    except GroupError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_group_delete(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    try:
        delete_group(vault_dir, args.group)
        print(f"Group '{args.group}' deleted.")
    except GroupError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_group_add_project(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    try:
        add_project_to_group(vault_dir, args.group, args.project)
        print(f"Project '{args.project}' added to group '{args.group}'.")
    except GroupError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_group_remove_project(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    try:
        remove_project_from_group(vault_dir, args.group, args.project)
        print(f"Project '{args.project}' removed from group '{args.group}'.")
    except GroupError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_group_list(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    groups = list_groups(vault_dir)
    if not groups:
        print("No groups defined.")
    else:
        for g in groups:
            print(g)


def register_group_commands(subparsers, vault_dir: str) -> None:
    def _add(name, func, help_text, extra=None):
        p = subparsers.add_parser(name, help=help_text)
        p.set_defaults(func=func, vault_dir=vault_dir)
        if extra:
            extra(p)
        return p

    _add("group-list", cmd_group_list, "List all groups")

    def _create_args(p):
        p.add_argument("group")
        p.add_argument("projects", nargs="+")
    _add("group-create", cmd_group_create, "Create a group", _create_args)

    def _group_only(p):
        p.add_argument("group")
    _add("group-get", cmd_group_get, "Show projects in a group", _group_only)
    _add("group-delete", cmd_group_delete, "Delete a group", _group_only)

    def _group_project(p):
        p.add_argument("group")
        p.add_argument("project")
    _add("group-add", cmd_group_add_project, "Add project to group", _group_project)
    _add("group-remove", cmd_group_remove_project, "Remove project from group", _group_project)
