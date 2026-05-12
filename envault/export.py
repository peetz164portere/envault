"""Export and import utilities for envault projects."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.vault import save_env, load_env


def export_env(project: str, password: str, output_path: Optional[str] = None) -> str:
    """Export a project's env vars to a plaintext .env file.

    Returns the path of the exported file.
    """
    env_vars = load_env(project, password)

    if output_path is None:
        output_path = f"{project}.env"

    lines = []
    for key, value in sorted(env_vars.items()):
        # Wrap values containing spaces or special chars in quotes
        if any(c in value for c in (' ', '"', "'", '\n', '\\')):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def import_env(project: str, password: str, input_path: str) -> dict:
    """Import env vars from a .env file into a project vault.

    Returns the parsed key-value dict that was saved.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    env_vars = parse_env_file(input_path)
    if not env_vars:
        raise ValueError(f"No valid KEY=VALUE pairs found in {input_path}")

    save_env(project, env_vars, password)
    return env_vars


def parse_env_file(path: str) -> dict:
    """Parse a .env file into a dict, skipping comments and blank lines.

    Handles quoted values (single or double quotes) and strips inline comments
    for unquoted values.
    """
    result = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            else:
                # Strip inline comments for unquoted values (e.g. FOO=bar # comment)
                if " #" in value:
                    value = value[:value.index(" #")].strip()
            if key:
                result[key] = value
    return result
