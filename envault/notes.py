"""Per-project plaintext notes stored alongside the vault."""

import json
from pathlib import Path
from envault.storage import ensure_vault_dir, _vault_path


class NoteError(Exception):
    pass


def _notes_path(vault_dir: Path) -> Path:
    return vault_dir / "notes.json"


def _load_notes(vault_dir: Path) -> dict:
    path = _notes_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_notes(vault_dir: Path, data: dict) -> None:
    path = _notes_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_note(project: str, note: str, vault_dir: Path) -> None:
    """Set or replace the note for a project."""
    if not project or not project.strip():
        raise NoteError("Project name must not be empty.")
    note = note.strip()
    if not note:
        raise NoteError("Note text must not be empty.")
    ensure_vault_dir(vault_dir)
    data = _load_notes(vault_dir)
    data[project] = note
    _save_notes(vault_dir, data)


def get_note(project: str, vault_dir: Path) -> str | None:
    """Return the note for a project, or None if not set."""
    data = _load_notes(vault_dir)
    return data.get(project)


def delete_note(project: str, vault_dir: Path) -> None:
    """Delete the note for a project. Raises NoteError if not found."""
    data = _load_notes(vault_dir)
    if project not in data:
        raise NoteError(f"No note found for project '{project}'.")
    del data[project]
    _save_notes(vault_dir, data)


def list_notes(vault_dir: Path) -> dict:
    """Return all project notes as a dict."""
    return _load_notes(vault_dir)
