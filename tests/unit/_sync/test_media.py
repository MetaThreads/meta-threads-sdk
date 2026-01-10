"""Tests for synchronous media client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.constants import ContainerStatus, MediaType, ReplyControl
from threads.exceptions import ThreadsAPIError


class TestMediaClient:
    """Tests for MediaClient."""

    @respx.mock
    def test_create_text_container(self):
        """Test creating a text container."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_container(
            user_id="user_123",
            media_type=MediaType.TEXT,
            text="Hello World",
        )

        assert result.id == "container_123"
        client.close()

    @respx.mock
    def test_create_image_container(self):
        """Test creating an image container."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "container_456"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_image_container(
            user_id="user_123",
            image_url="https://example.com/image.jpg",
            text="Check out this image!",
        )

        assert result.id == "container_456"
        client.close()

    @respx.mock
    def test_create_video_container(self):
        """Test creating a video container."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "container_789"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_video_container(
            user_id="user_123",
            video_url="https://example.com/video.mp4",
            text="Check out this video!",
        )

        assert result.id == "container_789"
        client.close()

    @respx.mock
    def test_create_carousel_container(self):
        """Test creating a carousel container."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "carousel_123"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_carousel_container(
            user_id="user_123",
            children=["item_1", "item_2", "item_3"],
            text="My carousel post",
        )

        assert result.id == "carousel_123"
        client.close()

    @respx.mock
    def test_create_carousel_item(self):
        """Test creating a carousel item."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "item_123"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_image_container(
            user_id="user_123",
            image_url="https://example.com/image.jpg",
            is_carousel_item=True,
        )

        assert result.id == "item_123"
        client.close()

    @respx.mock
    def test_create_container_with_reply_control(self):
        """Test creating container with reply control."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "container_123"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_container(
            user_id="user_123",
            media_type=MediaType.TEXT,
            text="Mentioned only",
            reply_control=ReplyControl.MENTIONED_ONLY,
        )

        assert result.id == "container_123"
        client.close()

    @respx.mock
    def test_create_container_as_reply(self):
        """Test creating container as a reply."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(200, json={"id": "reply_container_123"})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.create_container(
            user_id="user_123",
            media_type=MediaType.TEXT,
            text="This is a reply",
            reply_to_id="post_456",
        )

        assert result.id == "reply_container_123"
        client.close()

    @respx.mock
    def test_create_container_error(self):
        """Test creating container with error."""
        respx.post("https://graph.threads.net/v1.0/user_123/threads").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "Invalid media URL",
                        "type": "ThreadsAPIException",
                        "code": 100,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.media.create_container(
                user_id="user_123",
                media_type=MediaType.IMAGE,
                image_url="https://invalid-url.com/image.jpg",
            )
        client.close()

    @respx.mock
    def test_get_container_status_finished(self):
        """Test getting container status when finished."""
        respx.get("https://graph.threads.net/v1.0/container_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "FINISHED",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.get_container_status("container_123")

        assert result.id == "container_123"
        assert result.status == ContainerStatus.FINISHED
        assert result.is_ready is True
        assert result.has_error is False
        client.close()

    @respx.mock
    def test_get_container_status_in_progress(self):
        """Test getting container status when in progress."""
        respx.get("https://graph.threads.net/v1.0/container_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "IN_PROGRESS",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.get_container_status("container_123")

        assert result.status == ContainerStatus.IN_PROGRESS
        assert result.is_ready is False
        client.close()

    @respx.mock
    def test_get_container_status_error(self):
        """Test getting container status with error."""
        respx.get("https://graph.threads.net/v1.0/container_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "container_123",
                    "status": "ERROR",
                    "error_message": "Video processing failed",
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.media.get_container_status("container_123")

        assert result.status == ContainerStatus.ERROR
        assert result.has_error is True
        assert result.error_message == "Video processing failed"
        client.close()
