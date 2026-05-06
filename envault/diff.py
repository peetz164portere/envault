"""Compare environment variables between two snapshots or a snapshot and current state."""

from dataclasses import dataclass
from typing import Optional
from envault.vault import load_env, project_exists
from envault.snapshot import restore_snapshot, list_snapshots, SnapshotError


class DiffError(Exception):
    pass


@dataclass
class DiffEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]

    @property
    def status(self) -> str:
        if self.old_value is None:
            return "added"
        if self.new_value is None:
            return "removed"
        return "changed"


def diff_snapshots(
    project: str,
    password: str,
    snapshot_a: str,
    snapshot_b: str,
    vault_dir: Optional[str] = None,
) -> list[DiffEntry]:
    """Compare two named snapshots for a project. Returns list of DiffEntry."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    try:
        env_a = restore_snapshot(project, password, snapshot_a, **kwargs)
        env_b = restore_snapshot(project, password, snapshot_b, **kwargs)
    except SnapshotError as e:
        raise DiffError(str(e)) from e
    return _compute_diff(env_a, env_b)


def diff_snapshot_vs_current(
    project: str,
    password: str,
    snapshot_name: str,
    vault_dir: Optional[str] = None,
) -> list[DiffEntry]:
    """Compare a snapshot against the current saved environment."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    if not project_exists(project, **kwargs):
        raise DiffError(f"Project '{project}' does not exist.")
    try:
        env_snap = restore_snapshot(project, password, snapshot_name, **kwargs)
    except SnapshotError as e:
        raise DiffError(str(e)) from e
    env_current = load_env(project, password, **kwargs)
    return _compute_diff(env_snap, env_current)


def _compute_diff(env_a: dict, env_b: dict) -> list[DiffEntry]:
    all_keys = set(env_a) | set(env_b)
    entries = []
    for key in sorted(all_keys):
        old_val = env_a.get(key)
        new_val = env_b.get(key)
        if old_val != new_val:
            entries.append(DiffEntry(key=key, old_value=old_val, new_value=new_val))
    return entries
