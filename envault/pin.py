"""Per-project PIN/passphrase hint storage (stores hints, NOT secrets)."""

import json
from pathlib import Path
from envault.storage import ensure_vault_dir, _vault_path


class PinError(Exception):
    pass


def _pin_path(vault_dir: Path) -> Path:
    return vault_dir / "pins.json"


def _load_pins(vault_dir: Path) -> dict:
    p = _pin_path(vault_dir)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_pins(vault_dir: Path, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    with _pin_path(vault_dir).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_hint(project: str, hint: str, vault_dir: Path) -> None:
    """Store a password hint for a project."""
    if not hint or not hint.strip():
        raise PinError("Hint must not be empty.")
    pins = _load_pins(vault_dir)
    pins[project] = hint.strip()
    _save_pins(vault_dir, pins)


def get_hint(project: str, vault_dir: Path) -> str | None:
    """Return the hint for a project, or None if not set."""
    return _load_pins(vault_dir).get(project)


def remove_hint(project: str, vault_dir: Path) -> None:
    """Remove the hint for a project."""
    pins = _load_pins(vault_dir)
    if project not in pins:
        raise PinError(f"No hint found for project '{project}'.")
    del pins[project]
    _save_pins(vault_dir, pins)


def list_hints(vault_dir: Path) -> dict:
    """Return all project -> hint mappings."""
    return dict(_load_pins(vault_dir))
