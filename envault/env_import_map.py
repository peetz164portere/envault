"""Key remapping/aliasing during import — lets you rename keys as they're loaded."""

from __future__ import annotations

from typing import Dict, Optional

from envault.vault import load_env, save_env


class ImportMapError(Exception):
    pass


def apply_map(
    src_project: str,
    dst_project: str,
    key_map: Dict[str, str],
    src_password: str,
    dst_password: str,
    *,
    vault_dir: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Copy keys from src_project to dst_project, renaming them via key_map.

    key_map: {old_key: new_key}
    Returns the dict of keys that were written.
    """
    if not key_map:
        raise ImportMapError("key_map must not be empty")

    src_env = load_env(src_project, src_password, vault_dir=vault_dir)

    missing = [k for k in key_map if k not in src_env]
    if missing:
        raise ImportMapError(f"Keys not found in source project: {missing}")

    try:
        dst_env = load_env(dst_project, dst_password, vault_dir=vault_dir)
    except Exception:
        dst_env = {}

    conflicts = [new for old, new in key_map.items() if new in dst_env and not overwrite]
    if conflicts:
        raise ImportMapError(
            f"Keys already exist in destination (use overwrite=True): {conflicts}"
        )

    written: Dict[str, str] = {}
    for old_key, new_key in key_map.items():
        dst_env[new_key] = src_env[old_key]
        written[new_key] = src_env[old_key]

    save_env(dst_project, dst_password, dst_env, vault_dir=vault_dir)
    return written


def parse_map_string(map_string: str) -> Dict[str, str]:
    """Parse a comma-separated 'OLD=NEW,...' string into a dict."""
    result: Dict[str, str] = {}
    for part in map_string.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ImportMapError(f"Invalid mapping (expected OLD=NEW): {part!r}")
        old, new = part.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ImportMapError(f"Empty key or value in mapping: {part!r}")
        result[old] = new
    if not result:
        raise ImportMapError("No valid mappings found in map string")
    return result
