"""CLI commands for project locking."""

import argparse
from pathlib import Path
from envault.lock import acquire_lock, release_lock, is_locked, lock_owner, LockError


def cmd_lock_acquire(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    try:
        acquire_lock(args.project, vault_dir, timeout=args.timeout)
        print(f"Lock acquired for project '{args.project}'.")
    except LockError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


def cmd_lock_release(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    release_lock(args.project, vault_dir)
    print(f"Lock released for project '{args.project}'.")


def cmd_lock_status(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    if is_locked(args.project, vault_dir):
        pid = lock_owner(args.project, vault_dir)
        print(f"Project '{args.project}' is LOCKED (pid={pid}).")
    else:
        print(f"Project '{args.project}' is not locked.")


def register_lock_commands(subparsers: argparse._SubParsersAction, vault_dir: str) -> None:
    # acquire
    p_acq = subparsers.add_parser("lock-acquire", help="Acquire a lock on a project")
    p_acq.add_argument("project")
    p_acq.add_argument("--timeout", type=float, default=5.0)
    p_acq.set_defaults(func=cmd_lock_acquire, vault_dir=vault_dir)

    # release
    p_rel = subparsers.add_parser("lock-release", help="Release a lock on a project")
    p_rel.add_argument("project")
    p_rel.set_defaults(func=cmd_lock_release, vault_dir=vault_dir)

    # status
    p_sta = subparsers.add_parser("lock-status", help="Check lock status of a project")
    p_sta.add_argument("project")
    p_sta.set_defaults(func=cmd_lock_status, vault_dir=vault_dir)
