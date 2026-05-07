"""Per-project key quota enforcement for envault."""

import json
from pathlib import Path
from envault.storage import ensure_vault_dir, _vault_path

DEFAULT_QUOTA = 100


class QuotaError(Exception):
    pass


def _quota_path(vault_dir: Path) -> Path:
    return vault_dir / "quotas.json"


def _load_quotas(vault_dir: Path) -> dict:
    p = _quota_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quotas(vault_dir: Path, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    _quota_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_quota(project: str, limit: int, vault_dir: Path) -> None:
    """Set the maximum number of keys allowed for a project."""
    if limit < 1:
        raise QuotaError("Quota limit must be at least 1")
    data = _load_quotas(vault_dir)
    data[project] = limit
    _save_quotas(vault_dir, data)


def get_quota(project: str, vault_dir: Path) -> int:
    """Return the quota limit for a project (default if not set)."""
    data = _load_quotas(vault_dir)
    return data.get(project, DEFAULT_QUOTA)


def remove_quota(project: str, vault_dir: Path) -> None:
    """Remove a custom quota for a project, reverting to default."""
    data = _load_quotas(vault_dir)
    if project not in data:
        raise QuotaError(f"No custom quota set for project '{project}'")
    del data[project]
    _save_quotas(vault_dir, data)


def check_quota(project: str, current_key_count: int, vault_dir: Path) -> None:
    """Raise QuotaError if adding one more key would exceed the quota."""
    limit = get_quota(project, vault_dir)
    if current_key_count >= limit:
        raise QuotaError(
            f"Project '{project}' has reached its key quota of {limit}"
        )


def list_quotas(vault_dir: Path) -> dict:
    """Return all explicitly set project quotas."""
    return dict(_load_quotas(vault_dir))
