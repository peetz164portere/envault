"""Search and grep across vault projects."""

from typing import Optional
from envault.vault import load_env, list_projects


class SearchError(Exception):
    pass


def search_key(password: str, key_pattern: str, project: Optional[str] = None) -> list[dict]:
    """Search for env keys matching a pattern across one or all projects.

    Returns a list of dicts: [{project, key, value}, ...]
    Raises SearchError if no projects are accessible.
    """
    projects = [project] if project else list_projects()
    if not projects:
        raise SearchError("No projects found in vault.")

    results = []
    pattern = key_pattern.lower()

    for proj in projects:
        try:
            env = load_env(proj, password)
        except Exception:
            continue
        for k, v in env.items():
            if pattern in k.lower():
                results.append({"project": proj, "key": k, "value": v})

    return results


def search_value(password: str, value_pattern: str, project: Optional[str] = None) -> list[dict]:
    """Search for env values containing a pattern across one or all projects.

    Returns a list of dicts: [{project, key, value}, ...]
    """
    projects = [project] if project else list_projects()
    if not projects:
        raise SearchError("No projects found in vault.")

    results = []
    pattern = value_pattern.lower()

    for proj in projects:
        try:
            env = load_env(proj, password)
        except Exception:
            continue
        for k, v in env.items():
            if pattern in v.lower():
                results.append({"project": proj, "key": k, "value": v})

    return results


def list_keys(password: str, project: str) -> list[str]:
    """Return all keys stored for a given project."""
    try:
        env = load_env(project, password)
    except Exception as e:
        raise SearchError(f"Could not load project '{project}': {e}") from e
    return sorted(env.keys())
