"""Project-level expiry: set a date after which a project's secrets are considered stale."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from envault.storage import ensure_vault_dir


class ExpiryError(Exception):
    pass


def _expiry_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "expiry.json"


def _load_expiry(vault_dir: str) -> dict:
    p = _expiry_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(vault_dir: str, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    _expiry_path(vault_dir).write_text(json.dumps(data, indent=2))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def set_expiry(vault_dir: str, project: str, expires_at: str) -> None:
    """Set expiry for a project. expires_at must be ISO-8601 (e.g. '2025-12-31T00:00:00+00:00')."""
    try:
        dt = datetime.fromisoformat(expires_at)
    except ValueError:
        raise ExpiryError(f"Invalid ISO-8601 date: {expires_at!r}")
    if dt.tzinfo is None:
        raise ExpiryError("expires_at must include timezone info")
    data = _load_expiry(vault_dir)
    data[project] = dt.isoformat()
    _save_expiry(vault_dir, data)


def get_expiry(vault_dir: str, project: str) -> str | None:
    """Return the expiry ISO string for a project, or None if not set."""
    return _load_expiry(vault_dir).get(project)


def is_expired(vault_dir: str, project: str) -> bool:
    """Return True if the project has an expiry date that is in the past."""
    raw = get_expiry(vault_dir, project)
    if raw is None:
        return False
    return datetime.fromisoformat(raw) <= _now_utc()


def clear_expiry(vault_dir: str, project: str) -> None:
    """Remove expiry for a project."""
    data = _load_expiry(vault_dir)
    if project not in data:
        raise ExpiryError(f"No expiry set for project: {project!r}")
    del data[project]
    _save_expiry(vault_dir, data)


def list_expiries(vault_dir: str) -> dict[str, str]:
    """Return all project expiry entries as {project: iso_string}."""
    return dict(_load_expiry(vault_dir))
