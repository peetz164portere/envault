"""Tag-based project grouping and filtering for envault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import ensure_vault_dir, _vault_path


class TagError(Exception):
    pass


def _tags_path(vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir or _vault_path("").parent
    return base / "tags.json"


def _load_tags(vault_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Return mapping of project -> list of tags."""
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise TagError(f"Failed to read tags file: {exc}") from exc


def _save_tags(data: Dict[str, List[str]], vault_dir: Optional[Path] = None) -> None:
    ensure_vault_dir(vault_dir)
    path = _tags_path(vault_dir)
    path.write_text(json.dumps(data, indent=2))


def add_tag(project: str, tag: str, vault_dir: Optional[Path] = None) -> None:
    """Add a tag to a project."""
    data = _load_tags(vault_dir)
    tags = data.setdefault(project, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags(data, vault_dir)


def remove_tag(project: str, tag: str, vault_dir: Optional[Path] = None) -> None:
    """Remove a tag from a project. Raises TagError if tag not present."""
    data = _load_tags(vault_dir)
    tags = data.get(project, [])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on project '{project}'")
    tags.remove(tag)
    if not tags:
        del data[project]
    else:
        data[project] = tags
    _save_tags(data, vault_dir)


def get_tags(project: str, vault_dir: Optional[Path] = None) -> List[str]:
    """Return all tags for a project."""
    return _load_tags(vault_dir).get(project, [])


def projects_with_tag(tag: str, vault_dir: Optional[Path] = None) -> List[str]:
    """Return all projects that have the given tag."""
    data = _load_tags(vault_dir)
    return sorted(proj for proj, tags in data.items() if tag in tags)


def all_tags(vault_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Return the full project -> tags mapping."""
    return dict(_load_tags(vault_dir))
