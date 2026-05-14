"""CLI commands for env watch (live change detection)."""

from __future__ import annotations

import sys
from typing import Optional

from envault.env_watch import WatchError, WatchEvent, watch_project


def _format_event(event: WatchEvent) -> str:
    if event.kind == "added":
        return f"[+] {event.key} = {event.new_value!r}"
    elif event.kind == "removed":
        return f"[-] {event.key} (was {event.old_value!r})"
    else:
        return f"[~] {event.key}: {event.old_value!r} -> {event.new_value!r}"


def cmd_watch(args) -> None:
    """Watch a project for env key changes."""
    vault_dir: Optional[str] = getattr(args, "vault_dir", None)
    project: str = args.project
    password: str = args.password
    interval: float = getattr(args, "interval", 2.0)

    print(f"Watching '{project}' every {interval}s — press Ctrl+C to stop.")

    def on_event(event: WatchEvent) -> None:
        print(_format_event(event), flush=True)

    try:
        watch_project(
            project,
            password,
            callback=on_event,
            interval=interval,
            vault_dir=vault_dir,
        )
    except WatchError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nWatch stopped.")


def register_watch_commands(subparsers) -> None:
    p = subparsers.add_parser("watch", help="Watch a project for env changes")
    p.add_argument("project", help="Project name to watch")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Poll interval in seconds (default: 2.0)",
    )
    p.set_defaults(func=cmd_watch)
