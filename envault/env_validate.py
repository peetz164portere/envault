"""Validate project env vars against their schema rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envault.schema import _load_schemas, _schema_path
from envault.vault import load_env


class ValidationError(Exception):
    """Raised when validation cannot be performed."""


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class ValidationResult:
    project: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def validate_project(
    project: str,
    password: str,
    vault_dir: Optional[str] = None,
) -> ValidationResult:
    """Validate all env vars for *project* against stored schema rules.

    Returns a ValidationResult with any issues found.
    Raises ValidationError if the project cannot be loaded.
    """
    try:
        env = load_env(project, password, vault_dir=vault_dir)
    except Exception as exc:
        raise ValidationError(f"Could not load project '{project}': {exc}") from exc

    schemas = _load_schemas(vault_dir)
    project_schemas = schemas.get(project, {})

    result = ValidationResult(project=project)

    for key, value in env.items():
        rule = project_schemas.get(key)
        if rule is None:
            continue

        required = rule.get("required", False)
        pattern = rule.get("pattern")
        allowed = rule.get("allowed_values")

        if required and not value:
            result.issues.append(
                ValidationIssue(key=key, message=f"'{key}' is required but empty", severity="error")
            )

        if pattern and value:
            if not re.fullmatch(pattern, value):
                result.issues.append(
                    ValidationIssue(
                        key=key,
                        message=f"'{key}' value does not match pattern '{pattern}'",
                        severity="error",
                    )
                )

        if allowed and value not in allowed:
            result.issues.append(
                ValidationIssue(
                    key=key,
                    message=f"'{key}' value '{value}' not in allowed values {allowed}",
                    severity="warning",
                )
            )

    # Warn about required keys defined in schema but missing from env entirely
    for key, rule in project_schemas.items():
        if key not in env and rule.get("required", False):
            result.issues.append(
                ValidationIssue(key=key, message=f"Required key '{key}' is missing from env", severity="error")
            )

    return result
