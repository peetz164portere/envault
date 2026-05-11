"""Session management: remember the last-used project per vault directory."""

import json
from pathlib import Path


class SessionError(Exception):
    pass


def _session_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".session.json"


def _load_session(vault_dir: str) -> dict:
    p = _session_path(vault_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_session(vault_dir: str, data: dict) -> None:
    p = _session_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_active_project(vault_dir: str, project: str) -> None:
    """Record *project* as the currently active project."""
    if not project or not project.strip():
        raise SessionError("project name must not be empty")
    data = _load_session(vault_dir)
    data["active_project"] = project.strip()
    _save_session(vault_dir, data)


def get_active_project(vault_dir: str) -> str | None:
    """Return the currently active project, or None if none has been set."""
    return _load_session(vault_dir).get("active_project")


def clear_active_project(vault_dir: str) -> None:
    """Remove the active-project entry from the session."""
    data = _load_session(vault_dir)
    data.pop("active_project", None)
    _save_session(vault_dir, data)


def session_info(vault_dir: str) -> dict:
    """Return the full session dict (read-only view)."""
    return dict(_load_session(vault_dir))
