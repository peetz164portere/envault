"""Webhook notification support for envault events."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from envault.storage import ensure_vault_dir


class WebhookError(Exception):
    pass


def _webhook_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "webhooks.json"


def _load_webhooks(vault_dir: str) -> dict:
    path = _webhook_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_webhooks(vault_dir: str, data: dict) -> None:
    ensure_vault_dir(vault_dir)
    _webhook_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_webhook(vault_dir: str, project: str, url: str) -> None:
    """Register a webhook URL for a project."""
    if not url.startswith(("http://", "https://")):
        raise WebhookError(f"Invalid webhook URL: {url!r}")
    data = _load_webhooks(vault_dir)
    data[project] = url
    _save_webhooks(vault_dir, data)


def remove_webhook(vault_dir: str, project: str) -> None:
    """Remove the webhook for a project."""
    data = _load_webhooks(vault_dir)
    if project not in data:
        raise WebhookError(f"No webhook registered for project {project!r}")
    del data[project]
    _save_webhooks(vault_dir, data)


def get_webhook(vault_dir: str, project: str) -> Optional[str]:
    """Return the webhook URL for a project, or None."""
    return _load_webhooks(vault_dir).get(project)


def list_webhooks(vault_dir: str) -> dict[str, str]:
    """Return all registered webhooks as {project: url}."""
    return dict(_load_webhooks(vault_dir))


def fire_webhook(vault_dir: str, project: str, event: str, extra: Optional[dict] = None) -> None:
    """POST a JSON payload to the project's webhook URL if one is registered."""
    url = get_webhook(vault_dir, project)
    if url is None:
        return
    payload = {"project": project, "event": event}
    if extra:
        payload.update(extra)
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
    except urllib.error.URLError as exc:
        raise WebhookError(f"Webhook delivery failed for {project!r}: {exc}") from exc
