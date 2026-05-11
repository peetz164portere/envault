"""CLI commands for session management (active project tracking)."""

import sys
from envault.session import (
    set_active_project,
    get_active_project,
    clear_active_project,
    session_info,
    SessionError,
)


def _vault_dir(args) -> str:
    import os
    return getattr(args, "vault_dir", None) or os.path.expanduser("~/.envault")


def cmd_session_use(args) -> None:
    """Set the active project for the current vault."""
    try:
        set_active_project(_vault_dir(args), args.project)
        print(f"Active project set to '{args.project.strip()}'.")
    except SessionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_session_current(args) -> None:
    """Print the currently active project."""
    project = get_active_project(_vault_dir(args))
    if project is None:
        print("No active project set.")
    else:
        print(f"Active project: {project}")


def cmd_session_clear(args) -> None:
    """Clear the active project from the session."""
    clear_active_project(_vault_dir(args))
    print("Active project cleared.")


def cmd_session_info(args) -> None:
    """Print full session info."""
    info = session_info(_vault_dir(args))
    if not info:
        print("Session is empty.")
        return
    for key, value in info.items():
        print(f"  {key}: {value}")


def register_session_commands(subparsers, vault_dir_flag) -> None:
    """Attach session sub-commands to an existing argparse subparsers group."""
    p_use = subparsers.add_parser("session-use", help="set active project")
    vault_dir_flag(p_use)
    p_use.add_argument("project", help="project name to activate")
    p_use.set_defaults(func=cmd_session_use)

    p_cur = subparsers.add_parser("session-current", help="show active project")
    vault_dir_flag(p_cur)
    p_cur.set_defaults(func=cmd_session_current)

    p_clr = subparsers.add_parser("session-clear", help="clear active project")
    vault_dir_flag(p_clr)
    p_clr.set_defaults(func=cmd_session_clear)

    p_inf = subparsers.add_parser("session-info", help="show full session info")
    vault_dir_flag(p_inf)
    p_inf.set_defaults(func=cmd_session_info)
