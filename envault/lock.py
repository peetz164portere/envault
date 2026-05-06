"""Project locking — prevent concurrent access to a vault project."""

import os
import time
from pathlib import Path
from envault.storage import ensure_vault_dir, _vault_path


class LockError(Exception):
    pass


def _lock_path(vault_dir: Path, project: str) -> Path:
    return vault_dir / f"{project}.lock"


def acquire_lock(project: str, vault_dir: Path, timeout: float = 5.0, pid: int | None = None) -> None:
    """Create a lock file for *project*. Raises LockError if already locked."""
    ensure_vault_dir(vault_dir)
    lock = _lock_path(vault_dir, project)
    deadline = time.monotonic() + timeout
    pid = pid or os.getpid()
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(str(pid))
            return
        except FileExistsError:
            time.sleep(0.05)
    raise LockError(f"Could not acquire lock for project '{project}' within {timeout}s")


def release_lock(project: str, vault_dir: Path) -> None:
    """Remove the lock file for *project* if it exists."""
    lock = _lock_path(vault_dir, project)
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


def is_locked(project: str, vault_dir: Path) -> bool:
    """Return True if *project* currently has a lock file."""
    return _lock_path(vault_dir, project).exists()


def lock_owner(project: str, vault_dir: Path) -> int | None:
    """Return the PID stored in the lock file, or None if not locked."""
    lock = _lock_path(vault_dir, project)
    try:
        return int(lock.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None
