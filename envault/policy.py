"""Policy enforcement for envault projects.

Allows defining per-project rules such as required keys, forbidden keys,
and minimum password length requirements.
"""

import json
from pathlib import Path
from typing import Optional

POLICY_FILE = "policies.json"


class PolicyError(Exception):
    pass


def _policy_path(vault_dir: str) -> Path:
    return Path(vault_dir) / POLICY_FILE


def _load_policies(vault_dir: str) -> dict:
    p = _policy_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(vault_dir: str, data: dict) -> None:
    _policy_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_policy(
    vault_dir: str,
    project: str,
    required_keys: Optional[list] = None,
    forbidden_keys: Optional[list] = None,
    min_password_length: Optional[int] = None,
) -> None:
    """Set or update a policy for a project."""
    if not project:
        raise PolicyError("Project name must not be empty.")
    if min_password_length is not None and min_password_length < 1:
        raise PolicyError("min_password_length must be a positive integer.")
    data = _load_policies(vault_dir)
    entry = data.get(project, {})
    if required_keys is not None:
        entry["required_keys"] = sorted(set(required_keys))
    if forbidden_keys is not None:
        entry["forbidden_keys"] = sorted(set(forbidden_keys))
    if min_password_length is not None:
        entry["min_password_length"] = min_password_length
    data[project] = entry
    _save_policies(vault_dir, data)


def get_policy(vault_dir: str, project: str) -> dict:
    """Return the policy dict for a project, or empty dict if none set."""
    return _load_policies(vault_dir).get(project, {})


def delete_policy(vault_dir: str, project: str) -> None:
    """Remove the policy for a project."""
    data = _load_policies(vault_dir)
    if project not in data:
        raise PolicyError(f"No policy found for project '{project}'.")
    del data[project]
    _save_policies(vault_dir, data)


def enforce_policy(vault_dir: str, project: str, env: dict, password: str) -> None:
    """Raise PolicyError if the given env or password violates the project policy."""
    policy = get_policy(vault_dir, project)
    if not policy:
        return
    for key in policy.get("required_keys", []):
        if key not in env:
            raise PolicyError(f"Policy violation: required key '{key}' is missing.")
    for key in policy.get("forbidden_keys", []):
        if key in env:
            raise PolicyError(f"Policy violation: forbidden key '{key}' is present.")
    min_len = policy.get("min_password_length")
    if min_len and len(password) < min_len:
        raise PolicyError(
            f"Policy violation: password must be at least {min_len} characters."
        )
