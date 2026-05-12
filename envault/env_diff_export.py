"""Export diffs between snapshots or snapshot vs current to various formats."""

from __future__ import annotations

import csv
import io
import json
from typing import List, Literal

from envault.diff import DiffEntry, diff_snapshot_vs_current, diff_snapshots

OutputFormat = Literal["json", "csv", "text"]


class DiffExportError(Exception):
    pass


def _entries_to_dicts(entries: List[DiffEntry]) -> List[dict]:
    return [
        {"key": e.key, "status": e.status, "old": e.old_value, "new": e.new_value}
        for e in entries
    ]


def export_diff_to_string(
    entries: List[DiffEntry],
    fmt: OutputFormat = "text",
) -> str:
    """Render a list of DiffEntry objects as a string in the requested format."""
    if fmt == "json":
        return json.dumps(_entries_to_dicts(entries), indent=2)

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["key", "status", "old", "new"])
        writer.writeheader()
        writer.writerows(_entries_to_dicts(entries))
        return buf.getvalue()

    if fmt == "text":
        if not entries:
            return "No differences found."
        lines = []
        for e in entries:
            if e.status == "added":
                lines.append(f"+ {e.key}={e.new_value}")
            elif e.status == "removed":
                lines.append(f"- {e.key}={e.old_value}")
            else:
                lines.append(f"~ {e.key}: {e.old_value!r} -> {e.new_value!r}")
        return "\n".join(lines)

    raise DiffExportError(f"Unknown format: {fmt!r}")


def export_snapshots_diff(
    project: str,
    password: str,
    snap_a: str,
    snap_b: str,
    fmt: OutputFormat = "text",
    vault_dir: str | None = None,
) -> str:
    """Return a formatted diff between two named snapshots."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    entries = diff_snapshots(project, password, snap_a, snap_b, **kwargs)
    return export_diff_to_string(entries, fmt)


def export_snapshot_vs_current(
    project: str,
    password: str,
    snapshot_name: str,
    fmt: OutputFormat = "text",
    vault_dir: str | None = None,
) -> str:
    """Return a formatted diff between a snapshot and the current project state."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    entries = diff_snapshot_vs_current(project, password, snapshot_name, **kwargs)
    return export_diff_to_string(entries, fmt)
