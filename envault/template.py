"""Template support: generate .env templates from projects and apply them."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_env, save_env, project_exists


class TemplateError(Exception):
    pass


def export_template(project: str, password: str, output_path: str, mask_values: bool = True) -> None:
    """Write a .env template from a project, optionally masking values."""
    env = load_env(project, password)
    lines = []
    for key, value in sorted(env.items()):
        if mask_values:
            lines.append(f"{key}=\n")
        else:
            lines.append(f"{key}={value}\n")
    with open(output_path, "w") as fh:
        fh.writelines(lines)


def apply_template(project: str, password: str, template_path: str, overwrite: bool = False) -> dict[str, str]:
    """Load a .env template file and apply keys to a project.

    Keys that already exist in the project are skipped unless *overwrite* is True.
    Returns a dict of keys that were actually written.
    """
    template_vars = _parse_template(template_path)

    existing: dict[str, str] = {}
    if project_exists(project):
        try:
            existing = load_env(project, password)
        except Exception as exc:
            raise TemplateError(f"Could not load existing project '{project}': {exc}") from exc

    merged = dict(existing)
    written: dict[str, str] = {}
    for key, value in template_vars.items():
        if key not in merged or overwrite:
            merged[key] = value
            written[key] = value

    save_env(project, merged, password)
    return written


def list_template_keys(template_path: str) -> list[str]:
    """Return the list of keys defined in a template file."""
    return sorted(_parse_template(template_path).keys())


def _parse_template(path: str) -> dict[str, str]:
    """Parse a .env-style template file into a dict."""
    result: dict[str, str] = {}
    try:
        with open(path) as fh:
            for lineno, raw in enumerate(fh, 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise TemplateError(f"Invalid template line {lineno}: {raw!r}")
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    except OSError as exc:
        raise TemplateError(f"Cannot read template file '{path}': {exc}") from exc
    return result
