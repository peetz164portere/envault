"""Track per-project write history (last N saves)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from envault.storage import ensure_vault_dir, _vault_path

HISTORY_LIMIT = 20


class HistoryError(Exception):
    pass


def _history_path(vault_dir: Path) -> Path:
    return vault_dir / "history.json"


def _load_history(vault_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    path = _history_path(vault_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise HistoryError(f"Failed to read history: {exc}") from exc


def _save_history(vault_dir: Path, data: Dict[str, List[Dict[str, Any]]]) -> None:
    ensure_vault_dir(vault_dir)
    _history_path(vault_dir).write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def record_write(
    vault_dir: Path,
    project: str,
    keys: List[str],
    timestamp: str,
) -> None:
    """Append a write event for *project* (capped at HISTORY_LIMIT entries)."""
    if not project:
        raise HistoryError("project name must not be empty")
    data = _load_history(vault_dir)
    entries = data.get(project, [])
    entries.append({"timestamp": timestamp, "keys": sorted(keys)})
    data[project] = entries[-HISTORY_LIMIT:]
    _save_history(vault_dir, data)


def get_history(
    vault_dir: Path,
    project: str,
) -> List[Dict[str, Any]]:
    """Return write history for *project*, oldest first."""
    if not project:
        raise HistoryError("project name must not be empty")
    data = _load_history(vault_dir)
    return list(data.get(project, []))


def clear_history(vault_dir: Path, project: str) -> None:
    """Remove all history entries for *project*."""
    if not project:
        raise HistoryError("project name must not be empty")
    data = _load_history(vault_dir)
    data.pop(project, None)
    _save_history(vault_dir, data)


def list_projects_with_history(vault_dir: Path) -> List[str]:
    """Return sorted list of projects that have at least one history entry."""
    return sorted(_load_history(vault_dir).keys())
