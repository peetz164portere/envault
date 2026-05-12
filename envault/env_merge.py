"""Merge multiple project environments into a single resolved dict."""

from typing import Dict, List, Optional
from envault.vault import load_env, project_exists


class MergeError(Exception):
    pass


MERGE_STRATEGIES = ("first", "last", "error")


def merge_projects(
    projects: List[str],
    password: str,
    strategy: str = "last",
    vault_dir: Optional[str] = None,
) -> Dict[str, str]:
    """Merge envs from multiple projects in order.

    strategy:
      - 'last'  : later projects overwrite earlier ones (default)
      - 'first' : earlier projects win, later values are ignored
      - 'error' : raise MergeError on any duplicate key
    """
    if strategy not in MERGE_STRATEGIES:
        raise MergeError(
            f"Unknown strategy '{strategy}'. Choose from: {MERGE_STRATEGIES}"
        )
    if not projects:
        raise MergeError("At least one project must be specified.")

    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    merged: Dict[str, str] = {}
    seen: Dict[str, str] = {}  # key -> first project that defined it

    for project in projects:
        if not project_exists(project, **kwargs):
            raise MergeError(f"Project '{project}' does not exist.")
        env = load_env(project, password, **kwargs)
        for key, value in env.items():
            if key in seen:
                if strategy == "error":
                    raise MergeError(
                        f"Duplicate key '{key}' found in '{project}' "
                        f"(already defined in '{seen[key]}')."
                    )
                elif strategy == "first":
                    continue  # keep original
            else:
                seen[key] = project
            merged[key] = value

    return merged


def diff_merge(
    projects: List[str],
    password: str,
    vault_dir: Optional[str] = None,
) -> Dict[str, List[Optional[str]]]:
    """Return per-key values across all projects for comparison.

    Returns {key: [value_in_proj1, value_in_proj2, ...]} with None if absent.
    """
    if not projects:
        raise MergeError("At least one project must be specified.")

    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    envs = []
    for project in projects:
        if not project_exists(project, **kwargs):
            raise MergeError(f"Project '{project}' does not exist.")
        envs.append(load_env(project, password, **kwargs))

    all_keys: List[str] = sorted({k for env in envs for k in env})
    return {key: [env.get(key) for env in envs] for key in all_keys}
