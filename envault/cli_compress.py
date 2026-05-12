"""CLI commands for compress/decompress of vault project data."""

import sys
from envault.env_compress import compress_env, decompress_env, compression_ratio, CompressError
from envault.vault import load_env, save_env


def _vault_dir(args):
    import os
    return getattr(args, "vault_dir", None) or os.path.expanduser("~/.envault")


def cmd_compress_show(args):
    """Print compressed blob for a project (for inspection or piping)."""
    import envault.storage as storage
    storage.VAULT_DIR = _vault_dir(args)
    try:
        data = load_env(args.project, args.password)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        blob = compress_env(data)
        ratio = compression_ratio(data) if data else None
    except CompressError as exc:
        print(f"compress error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(blob)
    if ratio is not None:
        print(f"# ratio: {ratio:.2%}", file=sys.stderr)


def cmd_compress_ratio(args):
    """Print the compression ratio for a project's env data."""
    import envault.storage as storage
    storage.VAULT_DIR = _vault_dir(args)
    try:
        data = load_env(args.project, args.password)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not data:
        print("project has no keys; ratio not applicable")
        return
    try:
        ratio = compression_ratio(data)
    except CompressError as exc:
        print(f"compress error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"compression ratio for '{args.project}': {ratio:.2%}")


def register_compress_commands(subparsers):
    p_show = subparsers.add_parser(
        "compress-show", help="print compressed blob for a project"
    )
    p_show.add_argument("project")
    p_show.add_argument("--password", required=True)
    p_show.set_defaults(func=cmd_compress_show)

    p_ratio = subparsers.add_parser(
        "compress-ratio", help="show compression ratio for a project"
    )
    p_ratio.add_argument("project")
    p_ratio.add_argument("--password", required=True)
    p_ratio.set_defaults(func=cmd_compress_ratio)
