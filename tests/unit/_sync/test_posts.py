"""Tests for synchronous posts client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.constants import ContainerStatus, ReplyControl
from threads.exceptions import ContainerError, ThreadsAPIError, ValidationError


class TestPostsClient:
    """Tests for PostsClient."""

    @respx.mock
    def test_publish_success(self):
        """Test successful post publish."""
        respx.post(path__regex=r".*/user_123/threads_publish.*").mock(
            return_value=httpx.Response(200, json={"id": "post_456"})
        )
        respx.get(path__regex=r".*/post_456.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_456",
                    "text": "Hello World",
                    "media_type": "TEXT",
                    "timestamp": "2024-01-15T10:30:00+0000",
                    "permalink": "https://threads.net/@user/post/abc123",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.publish(user_id="user_123", container_id="container_789")

        assert result.id == "post_456"
        assert result.text == "Hello World"
        client.close()

    @respx.mock
    def test_publish_error(self):
        """Test publish with error."""
        respx.post(path__regex=r".*/user_123/threads_publish.*").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "Container not ready",
                        "type": "ThreadsAPIException",
                        "code": 100,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.posts.publish(user_id="user_123", container_id="container_789")
        client.close()

    @respx.mock
    def test_get_post(self):
        """Test getting a post by ID."""
        respx.get(path__regex=r".*/post_123.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_123",
                    "text": "Test post",
                    "media_type": "TEXT",
                    "timestamp": "2024-01-15T10:30:00+0000",
                    "permalink": "https://threads.net/@user/post/123",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get("post_123")

        assert result.id == "post_123"
        assert result.text == "Test post"
        assert result.media_type == "TEXT"
        client.close()

    @respx.mock
    def test_get_post_with_custom_fields(self):
        """Test getting a post with custom fields."""
        respx.get(path__regex=r".*/post_123.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_123",
                    "text": "Custom fields test",
                    "media_type": "TEXT",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get("post_123", fields=["id", "text"])

        assert result.id == "post_123"
        assert result.text == "Custom fields test"
        client.close()

    @respx.mock
    def test_get_user_posts(self):
        """Test getting user posts."""
        respx.get(path__regex=r".*/user_123/threads$").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post_1",
                            "text": "First post",
                            "media_type": "TEXT",
                            "timestamp": "2024-01-15T10:30:00+0000",
                        },
                        {
                            "id": "post_2",
                            "text": "Second post",
                            "media_type": "TEXT",
                            "timestamp": "2024-01-14T10:30:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get_user_posts("user_123")

        assert len(result) == 2
        assert result[0].id == "post_1"
        assert result[1].id == "post_2"
        client.close()

    @respx.mock
    def test_get_user_posts_with_filters(self):
        """Test getting user posts with time filters."""
        respx.get(path__regex=r".*/user_123/threads$").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post_1",
                            "text": "Filtered post",
                            "media_type": "TEXT",
                            "timestamp": "2024-01-15T10:30:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get_user_posts(
            "user_123",
            since="2024-01-01",
            until="2024-01-31",
            limit=10,
        )

        assert len(result) == 1
        client.close()

    @respx.mock
    def test_get_publishing_limit(self):
        """Test getting publishing limit."""
        respx.get(path__regex=r".*/user_123/threads_publishing_limit.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "quota_usage": 50,
                            "config": {
                                "quota_total": 250,
                                "reply_quota_total": 1000,
                            },
                            "reply_quota_usage": 100,
                        }
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get_publishing_limit("user_123")

        assert result.quota_usage == 50
        assert result.quota_total == 250
        assert result.reply_quota_usage == 100
        assert result.reply_quota_total == 1000
        client.close()

    @respx.mock
    def test_get_publishing_limit_empty_data(self):
        """Test getting publishing limit with empty data."""
        respx.get(path__regex=r".*/user_123/threads_publishing_limit.*").mock(
            return_value=httpx.Response(
                200,
                json={"data": []},
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.get_publishing_limit("user_123")

        assert result.quota_usage == 0
        assert result.quota_total == 250
        client.close()

    @respx.mock
    def test_create_and_publish_text(self):
        """Test create and publish text post."""
        # Mock create container - use more specific pattern to not match threads_publish
        respx.post(path__regex=r"/v1\.0/user_123/threads$").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )
        # Mock publish
        respx.post(path__regex=r"/v1\.0/user_123/threads_publish$").mock(
            return_value=httpx.Response(200, json={"id": "post_456"})
        )
        # Mock get post
        respx.get(path__regex=r"/v1\.0/post_456.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_456",
                    "text": "Hello from SDK",
                    "media_type": "TEXT",
                    "timestamp": "2024-01-15T10:30:00+0000",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.create_and_publish(
            user_id="user_123",
            text="Hello from SDK",
        )

        assert result.id == "post_456"
        assert result.text == "Hello from SDK"
        client.close()

    @respx.mock
    def test_create_and_publish_with_reply_control(self):
        """Test create and publish with reply control."""
        respx.post(path__regex=r"/v1\.0/user_123/threads$").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )
        respx.post(path__regex=r"/v1\.0/user_123/threads_publish$").mock(
            return_value=httpx.Response(200, json={"id": "post_456"})
        )
        respx.get(path__regex=r"/v1\.0/post_456.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_456",
                    "text": "Followers only",
                    "media_type": "TEXT",
                    "timestamp": "2024-01-15T10:30:00+0000",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.create_and_publish(
            user_id="user_123",
            text="Followers only",
            reply_control=ReplyControl.ACCOUNTS_YOU_FOLLOW,
        )

        assert result.id == "post_456"
        client.close()

    def test_create_and_publish_no_content_raises_error(self):
        """Test create and publish with no content raises error."""
        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ValidationError):
            client.posts.create_and_publish(user_id="user_123")
        client.close()


class TestWaitForContainer:
    """Tests for container waiting logic."""

    @respx.mock
    def test_wait_for_container_ready(self):
        """Test waiting for container that's immediately ready."""
        respx.post(path__regex=r"/v1\.0/user_123/threads$").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )
        respx.get(path__regex=r"/v1\.0/container_123.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "FINISHED",
                },
            )
        )
        respx.post(path__regex=r"/v1\.0/user_123/threads_publish$").mock(
            return_value=httpx.Response(200, json={"id": "post_456"})
        )
        respx.get(path__regex=r"/v1\.0/post_456.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "post_456",
                    "text": "Video post",
                    "media_type": "VIDEO",
                    "timestamp": "2024-01-15T10:30:00+0000",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.posts.create_and_publish(
            user_id="user_123",
            video_url="https://example.com/video.mp4",
            wait_for_ready=True,
        )

        assert result.id == "post_456"
        client.close()

    @respx.mock
    def test_wait_for_container_error(self):
        """Test waiting for container that has error."""
        respx.post(path__regex=r"/v1\.0/user_123/threads$").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )
        respx.get(path__regex=r"/v1\.0/container_123.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "ERROR",
                    "error_message": "Invalid video format",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ContainerError, match="Container processing failed"):
            client.posts.create_and_publish(
                user_id="user_123",
                video_url="https://example.com/bad_video.mp4",
                wait_for_ready=True,
            )
        client.close()

    @respx.mock
    def test_wait_for_container_expired(self):
        """Test waiting for container that expired."""
        respx.post(path__regex=r"/v1\.0/user_123/threads$").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )
        respx.get(path__regex=r"/v1\.0/container_123.*").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "EXPIRED",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ContainerError, match="Container expired"):
            client.posts.create_and_publish(
                user_id="user_123",
                video_url="https://example.com/video.mp4",
                wait_for_ready=True,
            )
        client.close()
