"""TTL (time-to-live) support for vault projects — auto-expiry after a set duration."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envault.storage import ensure_vault_dir, _vault_path


class TTLError(Exception):
    pass


def _ttl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "ttl.json"


def _load_ttl(vault_dir: str) -> dict:
    p = _ttl_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_ttl(vault_dir: str, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    with open(_ttl_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def set_ttl(project: str, seconds: int, vault_dir: str) -> None:
    """Set an expiry TTL (in seconds from now) for a project."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    data = _load_ttl(vault_dir)
    expires_at = (_now_utc() + timedelta(seconds=seconds)).isoformat()
    data[project] = {"expires_at": expires_at}
    _save_ttl(vault_dir, data)


def get_ttl(project: str, vault_dir: str) -> Optional[str]:
    """Return the ISO expiry timestamp for a project, or None if not set."""
    data = _load_ttl(vault_dir)
    entry = data.get(project)
    return entry["expires_at"] if entry else None


def is_expired(project: str, vault_dir: str) -> bool:
    """Return True if the project TTL has passed."""
    expires_at = get_ttl(project, vault_dir)
    if expires_at is None:
        return False
    expiry = datetime.fromisoformat(expires_at)
    return _now_utc() >= expiry


def clear_ttl(project: str, vault_dir: str) -> None:
    """Remove the TTL entry for a project."""
    data = _load_ttl(vault_dir)
    if project not in data:
        raise TTLError(f"No TTL set for project '{project}'.")
    del data[project]
    _save_ttl(vault_dir, data)


def list_ttls(vault_dir: str) -> dict:
    """Return all project TTL entries as {project: expires_at}."""
    data = _load_ttl(vault_dir)
    return {k: v["expires_at"] for k, v in data.items()}
