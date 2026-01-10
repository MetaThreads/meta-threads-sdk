"""Tests for asynchronous client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import AsyncThreadsClient


class TestAsyncThreadsClient:
    """Tests for AsyncThreadsClient."""

    async def test_client_initialization(self):
        """Test client initializes correctly."""
        client = AsyncThreadsClient(access_token="test_token")

        assert client._access_token == "test_token"
        assert client.http is not None
        assert client.auth is not None
        assert client.posts is not None
        assert client.media is not None
        assert client.insights is not None
        assert client.replies is not None
        assert client.webhooks is not None
        await client.aclose()

    async def test_client_context_manager(self):
        """Test async context manager."""
        async with AsyncThreadsClient(access_token="test_token") as client:
            assert client.http is not None

    async def test_client_close(self):
        """Test client close."""
        client = AsyncThreadsClient(access_token="test_token")
        await client.aclose()

        with pytest.raises(RuntimeError, match="Client has been closed"):
            _ = client.http

    async def test_client_custom_config(self):
        """Test client with custom configuration."""
        client = AsyncThreadsClient(
            access_token="test_token",
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
        )

        assert client._base_url == "https://custom.api.com"
        assert client._timeout == 60.0
        assert client._max_retries == 5
        await client.aclose()


class TestAsyncAuthClient:
    """Tests for AsyncAuthClient."""

    @respx.mock
    async def test_exchange_code(self):
        """Test async code exchange."""
        respx.post("https://graph.threads.net/oauth/access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "short_lived_token",
                    "user_id": 12345,
                },
            )
        )

        async with AsyncThreadsClient(access_token="temp") as client:
            result = await client.auth.exchange_code(
                client_id="app_123",
                client_secret="secret_456",
                redirect_uri="https://example.com/callback",
                code="auth_code",
            )

            assert result.access_token == "short_lived_token"
            assert result.user_id == "12345"

    @respx.mock
    async def test_get_long_lived_token(self):
        """Test async long-lived token exchange."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "long_lived_token",
                    "token_type": "bearer",
                    "expires_in": 5184000,
                },
            )
        )

        async with AsyncThreadsClient(access_token="temp") as client:
            result = await client.auth.get_long_lived_token(
                client_secret="secret",
                short_lived_token="short_token",
            )

            assert result.access_token == "long_lived_token"
            assert result.expires_in == 5184000

    @respx.mock
    async def test_refresh_token(self):
        """Test async token refresh."""
        respx.get(
            url__startswith="https://graph.threads.net/v1.0/refresh_access_token"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "refreshed_token",
                    "token_type": "bearer",
                    "expires_in": 5184000,
                },
            )
        )

        async with AsyncThreadsClient(access_token="temp") as client:
            result = await client.auth.refresh_token(access_token="old_token")

            assert result.access_token == "refreshed_token"


class TestAsyncPostsClient:
    """Tests for AsyncPostsClient."""

    @respx.mock
    async def test_get_post(self):
        """Test async get post."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_123",
                    "text": "Test post",
                    "media_type": "TEXT",
                    "timestamp": "2024-01-15T10:30:00+0000",
                },
            )
        )

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.posts.get("post_123")

            assert result.id == "post_123"
            assert result.text == "Test post"

    @respx.mock
    async def test_get_user_posts(self):
        """Test async get user posts."""
        respx.get(
            url__startswith="https://graph.threads.net/v1.0/user_123/threads"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post_1",
                            "text": "Post 1",
                            "media_type": "TEXT",
                            "timestamp": "2024-01-15T10:30:00+0000",
                        },
                        {
                            "id": "post_2",
                            "text": "Post 2",
                            "media_type": "TEXT",
                            "timestamp": "2024-01-14T10:30:00+0000",
                        },
                    ]
                },
            )
        )

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.posts.get_user_posts("user_123")

            assert len(result) == 2


class TestAsyncMediaClient:
    """Tests for AsyncMediaClient."""

    @respx.mock
    async def test_create_container(self):
        """Test async create container."""
        respx.post(
            url__startswith="https://graph.threads.net/v1.0/user_123/threads"
        ).mock(return_value=httpx.Response(200, json={"id": "container_123"}))

        async with AsyncThreadsClient(access_token="token") as client:
            from threads.constants import MediaType

            result = await client.media.create_container(
                user_id="user_123",
                media_type=MediaType.TEXT,
                text="Hello",
            )

            assert result.id == "container_123"

    @respx.mock
    async def test_get_container_status(self):
        """Test async get container status."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/container_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "FINISHED",
                },
            )
        )

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.media.get_container_status("container_123")

            assert result.is_ready is True


class TestAsyncInsightsClient:
    """Tests for AsyncInsightsClient."""

    @respx.mock
    async def test_get_media_insights(self):
        """Test async get media insights."""
        respx.get(
            url__startswith="https://graph.threads.net/v1.0/post_123/insights"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"name": "views", "values": [{"value": 1000}]},
                        {"name": "likes", "values": [{"value": 50}]},
                    ]
                },
            )
        )

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.insights.get_media_insights("post_123")

            assert result.views == 1000
            assert result.likes == 50


class TestAsyncRepliesClient:
    """Tests for AsyncRepliesClient."""

    @respx.mock
    async def test_get_replies(self):
        """Test async get replies."""
        respx.get(
            url__startswith="https://graph.threads.net/v1.0/post_123/replies"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "reply_1",
                            "text": "Reply 1",
                            "timestamp": "2024-01-15T11:00:00+0000",
                        },
                    ]
                },
            )
        )

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.replies.get_replies("post_123")

            assert len(result) == 1
            assert result[0].text == "Reply 1"

    @respx.mock
    async def test_hide_reply(self):
        """Test async hide reply."""
        respx.post(
            url__startswith="https://graph.threads.net/v1.0/reply_123/manage_reply"
        ).mock(return_value=httpx.Response(200, json={"success": True}))

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.replies.hide("reply_123")

            assert result is True


class TestAsyncWebhooksClient:
    """Tests for AsyncWebhooksClient."""

    @respx.mock
    async def test_subscribe(self):
        """Test async webhook subscribe."""
        respx.post(
            url__startswith="https://graph.threads.net/v1.0/me/subscribed_apps"
        ).mock(return_value=httpx.Response(200, json={"success": True}))

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.webhooks.subscribe(
                callback_url="https://example.com/webhook",
                verify_token="verify_token",
            )

            assert result.active is True

    @respx.mock
    async def test_unsubscribe(self):
        """Test async webhook unsubscribe."""
        respx.delete(
            url__startswith="https://graph.threads.net/v1.0/me/subscribed_apps"
        ).mock(return_value=httpx.Response(200, json={"success": True}))

        async with AsyncThreadsClient(access_token="token") as client:
            result = await client.webhooks.unsubscribe()

            assert result is True
