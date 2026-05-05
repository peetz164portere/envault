"""Audit log for envault — tracks vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = "audit.log"


def _audit_log_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    return base / AUDIT_LOG_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_event(
    action: str,
    project: str,
    success: bool = True,
    detail: Optional[str] = None,
    vault_dir: Optional[str] = None,
) -> None:
    """Append a single audit event to the log file."""
    log_path = _audit_log_path(vault_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": _now_iso(),
        "action": action,
        "project": project,
        "success": success,
    }
    if detail:
        entry["detail"] = detail

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(
    project: Optional[str] = None,
    vault_dir: Optional[str] = None,
) -> list[dict]:
    """Return all audit events, optionally filtered by project."""
    log_path = _audit_log_path(vault_dir)
    if not log_path.exists():
        return []

    events = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if project is None or entry.get("project") == project:
                events.append(entry)
    return events


def clear_events(vault_dir: Optional[str] = None) -> None:
    """Delete the audit log file entirely."""
    log_path = _audit_log_path(vault_dir)
    if log_path.exists():
        log_path.unlink()
