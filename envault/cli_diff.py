"""CLI commands for diffing snapshots and current env state."""

import argparse
from envault.diff import diff_snapshots, diff_snapshot_vs_current, DiffError


def _print_diff(entries):
    if not entries:
        print("No differences found.")
        return
    for entry in entries:
        if entry.status == "added":
            print(f"  + {entry.key} = {entry.new_value}")
        elif entry.status == "removed":
            print(f"  - {entry.key} = {entry.old_value}")
        else:
            print(f"  ~ {entry.key}: {entry.old_value!r} -> {entry.new_value!r}")


def cmd_diff(args):
    vault_dir = getattr(args, "vault_dir", None)
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    try:
        if args.snapshot_b:
            entries = diff_snapshots(
                args.project, args.password, args.snapshot_a, args.snapshot_b, **kwargs
            )
            print(f"Diff [{args.snapshot_a}] -> [{args.snapshot_b}] for project '{args.project}':")
        else:
            entries = diff_snapshot_vs_current(
                args.project, args.password, args.snapshot_a, **kwargs
            )
            print(f"Diff snapshot [{args.snapshot_a}] vs current for project '{args.project}':")
        _print_diff(entries)
    except DiffError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def register_diff_commands(subparsers):
    p = subparsers.add_parser("diff", help="Diff snapshots or snapshot vs current env")
    p.add_argument("project", help="Project name")
    p.add_argument("snapshot_a", help="First snapshot name (or baseline)")
    p.add_argument(
        "snapshot_b",
        nargs="?",
        default=None,
        help="Second snapshot name (omit to compare against current env)",
    )
    p.add_argument("--password", required=True, help="Vault password")
    p.set_defaults(func=cmd_diff)
    return p
