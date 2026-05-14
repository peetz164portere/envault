"""Per-project environment statistics: key count, size, last modified, etc."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.storage import _vault_path, vault_exists
from envault.vault import load_env, list_projects


class StatsError(Exception):
    pass


@dataclass
class ProjectStats:
    project: str
    key_count: int
    total_value_bytes: int
    avg_value_bytes: float
    max_key_length: int
    min_key_length: int
    vault_file_bytes: int
    keys: List[str] = field(default_factory=list)


def project_stats(project: str, password: str, vault_dir: Optional[str] = None) -> ProjectStats:
    """Return statistics for a single project."""
    if not vault_exists(project, vault_dir=vault_dir):
        raise StatsError(f"Project '{project}' does not exist.")

    env = load_env(project, password, vault_dir=vault_dir)
    keys = list(env.keys())
    values = list(env.values())

    key_count = len(keys)
    total_value_bytes = sum(len(v.encode()) for v in values)
    avg_value_bytes = total_value_bytes / key_count if key_count else 0.0
    max_key_length = max((len(k) for k in keys), default=0)
    min_key_length = min((len(k) for k in keys), default=0)

    path = _vault_path(project, vault_dir=vault_dir)
    vault_file_bytes = os.path.getsize(path) if os.path.exists(path) else 0

    return ProjectStats(
        project=project,
        key_count=key_count,
        total_value_bytes=total_value_bytes,
        avg_value_bytes=round(avg_value_bytes, 2),
        max_key_length=max_key_length,
        min_key_length=min_key_length,
        vault_file_bytes=vault_file_bytes,
        keys=sorted(keys),
    )


def all_stats(password: str, vault_dir: Optional[str] = None) -> Dict[str, ProjectStats]:
    """Return stats for every project accessible with the given password."""
    results: Dict[str, ProjectStats] = {}
    for proj in list_projects(vault_dir=vault_dir):
        try:
            results[proj] = project_stats(proj, password, vault_dir=vault_dir)
        except Exception:
            pass
    return results


def summary_stats(password: str, vault_dir: Optional[str] = None) -> Dict[str, object]:
    """Return an aggregate summary across all projects."""
    stats_map = all_stats(password, vault_dir=vault_dir)
    total_keys = sum(s.key_count for s in stats_map.values())
    total_bytes = sum(s.total_value_bytes for s in stats_map.values())
    return {
        "project_count": len(stats_map),
        "total_keys": total_keys,
        "total_value_bytes": total_bytes,
        "projects": sorted(stats_map.keys()),
    }
