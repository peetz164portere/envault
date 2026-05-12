"""Lint .env files and vault projects for common issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_env


class LintError(Exception):
    pass


@dataclass
class LintIssue:
    key: str
    severity: str  # 'error' | 'warning' | 'info'
    message: str


@dataclass
class LintResult:
    project: str
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_PLACEHOLDER_RE = re.compile(r'^(CHANGE_ME|TODO|PLACEHOLDER|FIXME|XXX|<.*>)$', re.IGNORECASE)


def lint_project(project: str, password: str, vault_dir: Optional[str] = None) -> LintResult:
    """Load a vault project and run lint checks on its keys/values."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    try:
        env = load_env(project, password, **kwargs)
    except Exception as exc:
        raise LintError(f"Could not load project '{project}': {exc}") from exc

    result = LintResult(project=project)

    if not env:
        result.issues.append(LintIssue(key="*", severity="info", message="Project has no keys defined."))
        return result

    for key, value in env.items():
        # Key naming convention
        if not _VALID_KEY_RE.match(key):
            result.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention.",
            ))

        # Empty value
        if value == "":
            result.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=f"Key '{key}' has an empty value.",
            ))
            continue

        # Placeholder values
        if _PLACEHOLDER_RE.match(value):
            result.issues.append(LintIssue(
                key=key,
                severity="error",
                message=f"Key '{key}' appears to contain a placeholder value: '{value}'.",
            ))

        # Suspiciously short secrets
        secret_hints = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS", "PWD")
        if any(hint in key.upper() for hint in secret_hints) and len(value) < 8:
            result.issues.append(LintIssue(
                key=key,
                severity="warning",
                message=f"Key '{key}' looks like a secret but has a very short value (< 8 chars).",
            ))

    return result
