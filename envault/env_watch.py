"""Watch a project's env keys for changes over time (polling-based)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from envault.vault import load_env, project_exists


class WatchError(Exception):
    pass


@dataclass
class WatchEvent:
    project: str
    key: str
    kind: str  # 'added' | 'removed' | 'changed'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def _diff_envs(
    old: Dict[str, str], new: Dict[str, str], project: str
) -> list[WatchEvent]:
    events: list[WatchEvent] = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key in old and key not in new:
            events.append(WatchEvent(project, key, "removed", old_value=old[key]))
        elif key not in old and key in new:
            events.append(WatchEvent(project, key, "added", new_value=new[key]))
        elif old[key] != new[key]:
            events.append(
                WatchEvent(project, key, "changed", old_value=old[key], new_value=new[key])
            )
    return events


def watch_project(
    project: str,
    password: str,
    callback: Callable[[WatchEvent], None],
    interval: float = 2.0,
    max_polls: Optional[int] = None,
    vault_dir: Optional[str] = None,
) -> None:
    """Poll a project vault and invoke callback on each detected change."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    if not project_exists(project, **kwargs):
        raise WatchError(f"Project '{project}' does not exist.")

    current = load_env(project, password, **kwargs)
    polls = 0

    while max_polls is None or polls < max_polls:
        time.sleep(interval)
        polls += 1
        try:
            updated = load_env(project, password, **kwargs)
        except Exception:
            continue
        events = _diff_envs(current, updated, project)
        for event in events:
            callback(event)
        current = updated
