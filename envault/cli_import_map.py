"""CLI commands for key-remapping import."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from envault.env_import_map import apply_map, parse_map_string, ImportMapError


def _vault_dir(args: argparse.Namespace) -> Optional[str]:
    return getattr(args, "vault_dir", None)


def cmd_import_map(args: argparse.Namespace) -> None:
    """Remap keys from one project into another."""
    try:
        key_map = parse_map_string(args.map)
    except ImportMapError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        written = apply_map(
            src_project=args.src,
            dst_project=args.dst,
            key_map=key_map,
            src_password=args.src_password,
            dst_password=args.dst_password,
            vault_dir=_vault_dir(args),
            overwrite=args.overwrite,
        )
    except ImportMapError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Mapped {len(written)} key(s) from '{args.src}' → '{args.dst}':")
    for new_key in sorted(written):
        print(f"  {new_key}")


def register_import_map_commands(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    p = subparsers.add_parser(
        "import-map",
        help="Copy and rename keys from one project to another",
    )
    p.add_argument("src", help="Source project name")
    p.add_argument("dst", help="Destination project name")
    p.add_argument(
        "--map",
        required=True,
        metavar="OLD=NEW,...",
        help="Comma-separated key remappings, e.g. DB_HOST=DATABASE_HOST",
    )
    p.add_argument("--src-password", required=True, dest="src_password")
    p.add_argument("--dst-password", required=True, dest="dst_password")
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in destination",
    )
    p.set_defaults(func=cmd_import_map)
