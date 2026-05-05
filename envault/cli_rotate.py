"""CLI commands for password rotation."""

import argparse
import getpass

from envault.rotate import rotate_project, rotate_all, RotationError


def cmd_rotate(args):
    old_password = getpass.getpass("Current password: ")
    new_password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm new password: ")

    if new_password != confirm:
        print("Error: new passwords do not match.")
        return 1

    vault_dir = getattr(args, "vault_dir", None)

    if args.all:
        results = rotate_all(old_password, new_password, vault_dir=vault_dir)
        ok = [p for p, r in results.items() if r == "ok"]
        failed = {p: r for p, r in results.items() if r != "ok"}
        if ok:
            print(f"Rotated: {', '.join(ok)}")
        for project, err in failed.items():
            print(f"Failed [{project}]: {err}")
        return 0 if not failed else 1
    else:
        if not args.project:
            print("Error: specify --project or use --all.")
            return 1
        try:
            rotate_project(args.project, old_password, new_password, vault_dir=vault_dir)
            print(f"Password rotated for '{args.project}'.")
            return 0
        except RotationError as e:
            print(f"Error: {e}")
            return 1


def register_rotate_commands(subparsers):
    p = subparsers.add_parser("rotate", help="Rotate encryption password for one or all projects")
    p.add_argument("--project", "-p", default=None, help="Project name to rotate")
    p.add_argument("--all", action="store_true", help="Rotate all projects")
    p.set_defaults(func=cmd_rotate)
