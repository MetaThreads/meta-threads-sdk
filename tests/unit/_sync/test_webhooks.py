"""Tests for synchronous webhooks client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.exceptions import ThreadsAPIError


class TestWebhooksClient:
    """Tests for WebhooksClient."""

    @respx.mock
    def test_subscribe(self):
        """Test subscribing to webhook events."""
        respx.post("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.subscribe(
            callback_url="https://example.com/webhook",
            verify_token="my_verify_token",
        )

        assert result.callback_url == "https://example.com/webhook"
        assert result.verify_token == "my_verify_token"
        assert result.active is True
        client.close()

    @respx.mock
    def test_subscribe_with_custom_fields(self):
        """Test subscribing with custom event fields."""
        respx.post("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.subscribe(
            callback_url="https://example.com/webhook",
            verify_token="my_verify_token",
            fields=["messages", "story_mentions"],
        )

        assert result.fields == ["messages", "story_mentions"]
        assert result.active is True
        client.close()

    @respx.mock
    def test_subscribe_failure(self):
        """Test subscribing when API returns failure."""
        respx.post("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"success": False})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.subscribe(
            callback_url="https://example.com/webhook",
            verify_token="my_verify_token",
        )

        assert result.active is False
        client.close()

    @respx.mock
    def test_subscribe_error(self):
        """Test subscribing with API error."""
        respx.post("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "Invalid callback URL",
                        "type": "ThreadsAPIException",
                        "code": 100,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.webhooks.subscribe(
                callback_url="invalid-url",
                verify_token="my_verify_token",
            )
        client.close()

    @respx.mock
    def test_unsubscribe(self):
        """Test unsubscribing from webhook events."""
        respx.delete("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.unsubscribe()

        assert result is True
        client.close()

    @respx.mock
    def test_unsubscribe_failure(self):
        """Test unsubscribing when it fails."""
        respx.delete("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"success": False})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.unsubscribe()

        assert result is False
        client.close()

    @respx.mock
    def test_unsubscribe_error(self):
        """Test unsubscribing with API error."""
        respx.delete("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(
                401,
                json={
                    "error": {
                        "message": "Invalid access token",
                        "type": "OAuthException",
                        "code": 190,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.webhooks.unsubscribe()
        client.close()

    @respx.mock
    def test_get_subscriptions(self):
        """Test getting current subscriptions."""
        respx.get("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "callback_url": "https://example.com/webhook1",
                            "fields": ["messages"],
                            "active": True,
                        },
                        {
                            "callback_url": "https://example.com/webhook2",
                            "fields": ["messaging_postbacks"],
                            "active": True,
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.get_subscriptions()

        assert len(result) == 2
        assert result[0].callback_url == "https://example.com/webhook1"
        assert result[0].fields == ["messages"]
        assert result[1].callback_url == "https://example.com/webhook2"
        client.close()

    @respx.mock
    def test_get_subscriptions_empty(self):
        """Test getting subscriptions when none exist."""
        respx.get("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(200, json={"data": []})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.webhooks.get_subscriptions()

        assert len(result) == 0
        client.close()

    @respx.mock
    def test_get_subscriptions_error(self):
        """Test getting subscriptions with error."""
        respx.get("https://graph.threads.net/v1.0/me/subscribed_apps").mock(
            return_value=httpx.Response(
                500,
                json={
                    "error": {
                        "message": "Internal server error",
                        "type": "ThreadsAPIException",
                        "code": 500,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.webhooks.get_subscriptions()
        client.close()
