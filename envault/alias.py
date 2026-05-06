"""Project alias management — assign short names to projects."""

import json
from pathlib import Path
from envault.storage import ensure_vault_dir, _vault_path


class AliasError(Exception):
    pass


def _alias_path(vault_dir: str | None = None) -> Path:
    base = Path(vault_dir) if vault_dir else _vault_path("").parent
    return base / "aliases.json"


def _load_aliases(vault_dir: str | None = None) -> dict:
    path = _alias_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_aliases(aliases: dict, vault_dir: str | None = None) -> None:
    ensure_vault_dir(vault_dir)
    path = _alias_path(vault_dir)
    with path.open("w") as f:
        json.dump(aliases, f, indent=2)


def set_alias(alias: str, project: str, vault_dir: str | None = None) -> None:
    """Map an alias to a project name."""
    alias = alias.strip()
    if not alias:
        raise AliasError("Alias must not be empty.")
    if not project.strip():
        raise AliasError("Project name must not be empty.")
    aliases = _load_aliases(vault_dir)
    aliases[alias] = project.strip()
    _save_aliases(aliases, vault_dir)


def remove_alias(alias: str, vault_dir: str | None = None) -> None:
    """Remove an alias mapping."""
    aliases = _load_aliases(vault_dir)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(aliases, vault_dir)


def resolve_alias(alias: str, vault_dir: str | None = None) -> str:
    """Return the project name for an alias, or the alias itself if not mapped."""
    aliases = _load_aliases(vault_dir)
    return aliases.get(alias, alias)


def list_aliases(vault_dir: str | None = None) -> dict:
    """Return all alias -> project mappings."""
    return _load_aliases(vault_dir)
