"""Tests for envault.webhook."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from envault.webhook import (
    set_webhook,
    remove_webhook,
    get_webhook,
    list_webhooks,
    fire_webhook,
    WebhookError,
)


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_webhook(tmp_vault_dir):
    set_webhook(tmp_vault_dir, "myapp", "https://example.com/hook")
    assert get_webhook(tmp_vault_dir, "myapp") == "https://example.com/hook"


def test_get_webhook_not_set_returns_none(tmp_vault_dir):
    assert get_webhook(tmp_vault_dir, "missing") is None


def test_set_webhook_invalid_url_raises(tmp_vault_dir):
    with pytest.raises(WebhookError, match="Invalid webhook URL"):
        set_webhook(tmp_vault_dir, "myapp", "ftp://bad.url")


def test_set_webhook_overwrites_existing(tmp_vault_dir):
    set_webhook(tmp_vault_dir, "myapp", "https://first.example.com/hook")
    set_webhook(tmp_vault_dir, "myapp", "https://second.example.com/hook")
    assert get_webhook(tmp_vault_dir, "myapp") == "https://second.example.com/hook"


def test_remove_webhook(tmp_vault_dir):
    set_webhook(tmp_vault_dir, "myapp", "https://example.com/hook")
    remove_webhook(tmp_vault_dir, "myapp")
    assert get_webhook(tmp_vault_dir, "myapp") is None


def test_remove_webhook_missing_raises(tmp_vault_dir):
    with pytest.raises(WebhookError, match="No webhook registered"):
        remove_webhook(tmp_vault_dir, "ghost")


def test_list_webhooks_returns_all(tmp_vault_dir):
    set_webhook(tmp_vault_dir, "app1", "https://a.example.com/hook")
    set_webhook(tmp_vault_dir, "app2", "https://b.example.com/hook")
    result = list_webhooks(tmp_vault_dir)
    assert result == {
        "app1": "https://a.example.com/hook",
        "app2": "https://b.example.com/hook",
    }


def test_list_webhooks_empty(tmp_vault_dir):
    assert list_webhooks(tmp_vault_dir) == {}


def test_fire_webhook_no_url_is_noop(tmp_vault_dir):
    # Should not raise even without a registered webhook
    fire_webhook(tmp_vault_dir, "unregistered", "env.set")


def test_fire_webhook_posts_payload(tmp_vault_dir):
    set_webhook(tmp_vault_dir, "myapp", "https://example.com/hook")
    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        fire_webhook(tmp_vault_dir, "myapp", "env.set", extra={"key": "DB_URL"})
        mock_open.assert_called_once()
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["project"] == "myapp"
        assert body["event"] == "env.set"
        assert body["key"] == "DB_URL"


def test_fire_webhook_url_error_raises(tmp_vault_dir):
    import urllib.error
    set_webhook(tmp_vault_dir, "myapp", "https://example.com/hook")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        with pytest.raises(WebhookError, match="Webhook delivery failed"):
            fire_webhook(tmp_vault_dir, "myapp", "env.set")
