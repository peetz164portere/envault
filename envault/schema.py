"""Schema validation for .env projects — enforce required keys and value patterns."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional


class SchemaError(Exception):
    pass


def _schema_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "schemas.json"


def _load_schemas(vault_dir: str) -> dict:
    p = _schema_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schemas(vault_dir: str, data: dict) -> None:
    _schema_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_schema(vault_dir: str, project: str, key: str, required: bool = False, pattern: Optional[str] = None) -> None:
    """Define a schema rule for a key in a project."""
    if not key:
        raise SchemaError("Key must not be empty.")
    if pattern:
        try:
            re.compile(pattern)
        except re.error as e:
            raise SchemaError(f"Invalid regex pattern: {e}") from e
    data = _load_schemas(vault_dir)
    data.setdefault(project, {})
    data[project][key] = {"required": required, "pattern": pattern}
    _save_schemas(vault_dir, data)


def remove_schema(vault_dir: str, project: str, key: str) -> None:
    """Remove a schema rule for a key."""
    data = _load_schemas(vault_dir)
    if project not in data or key not in data[project]:
        raise SchemaError(f"No schema rule for '{key}' in project '{project}'.")
    del data[project][key]
    if not data[project]:
        del data[project]
    _save_schemas(vault_dir, data)


def get_schema(vault_dir: str, project: str) -> dict:
    """Return all schema rules for a project."""
    return _load_schemas(vault_dir).get(project, {})


def validate(vault_dir: str, project: str, env: dict) -> list[str]:
    """Validate env dict against project schema. Returns list of violation messages."""
    rules = get_schema(vault_dir, project)
    violations = []
    for key, rule in rules.items():
        if rule.get("required") and key not in env:
            violations.append(f"Required key '{key}' is missing.")
            continue
        pattern = rule.get("pattern")
        if pattern and key in env:
            if not re.fullmatch(pattern, env[key]):
                violations.append(f"Key '{key}' value does not match pattern '{pattern}'.")
    return violations
