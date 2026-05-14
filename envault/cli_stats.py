"""CLI commands for displaying environment statistics."""

from __future__ import annotations

import argparse
import sys

from envault.env_stats import StatsError, all_stats, project_stats, summary_stats


def cmd_stats_project(args: argparse.Namespace) -> None:
    """Print stats for a single project."""
    vault_dir = getattr(args, "vault_dir", None)
    try:
        stats = project_stats(args.project, args.password, vault_dir=vault_dir)
    except StatsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Project      : {stats.project}")
    print(f"Keys         : {stats.key_count}")
    print(f"Value bytes  : {stats.total_value_bytes}")
    print(f"Avg val bytes: {stats.avg_value_bytes}")
    print(f"Max key len  : {stats.max_key_length}")
    print(f"Min key len  : {stats.min_key_length}")
    print(f"Vault size   : {stats.vault_file_bytes} bytes")
    if getattr(args, "show_keys", False):
        print("Keys         : " + ", ".join(stats.keys))


def cmd_stats_all(args: argparse.Namespace) -> None:
    """Print a summary of stats across all projects."""
    vault_dir = getattr(args, "vault_dir", None)
    summary = summary_stats(args.password, vault_dir=vault_dir)

    print(f"Projects     : {summary['project_count']}")
    print(f"Total keys   : {summary['total_keys']}")
    print(f"Total bytes  : {summary['total_value_bytes']}")
    if summary["projects"]:
        print("Project list : " + ", ".join(summary["projects"]))
    else:
        print("No projects found.")


def cmd_stats_compare(args: argparse.Namespace) -> None:
    """Print side-by-side key counts for all projects."""
    vault_dir = getattr(args, "vault_dir", None)
    stats_map = all_stats(args.password, vault_dir=vault_dir)
    if not stats_map:
        print("No projects found.")
        return
    width = max(len(p) for p in stats_map)
    print(f"{'Project':<{width}}  Keys  Vault bytes")
    print("-" * (width + 20))
    for proj, s in sorted(stats_map.items()):
        print(f"{proj:<{width}}  {s.key_count:<5} {s.vault_file_bytes}")


def register_stats_commands(subparsers: argparse._SubParsersAction) -> None:
    p_proj = subparsers.add_parser("stats", help="Show stats for a project")
    p_proj.add_argument("project")
    p_proj.add_argument("password")
    p_proj.add_argument("--show-keys", action="store_true", dest="show_keys")
    p_proj.set_defaults(func=cmd_stats_project)

    p_all = subparsers.add_parser("stats-all", help="Show aggregate stats")
    p_all.add_argument("password")
    p_all.set_defaults(func=cmd_stats_all)

    p_cmp = subparsers.add_parser("stats-compare", help="Compare key counts across projects")
    p_cmp.add_argument("password")
    p_cmp.set_defaults(func=cmd_stats_compare)
