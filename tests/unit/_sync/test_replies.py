"""Tests for synchronous replies client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.exceptions import ThreadsAPIError


class TestRepliesClient:
    """Tests for RepliesClient."""

    @respx.mock
    def test_get_replies(self):
        """Test getting replies to a post."""
        respx.get("https://graph.threads.net/v1.0/post_123/replies").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "reply_1",
                            "text": "First reply",
                            "timestamp": "2024-01-15T11:00:00+0000",
                        },
                        {
                            "id": "reply_2",
                            "text": "Second reply",
                            "timestamp": "2024-01-15T12:00:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.get_replies("post_123")

        assert len(result) == 2
        assert result[0].id == "reply_1"
        assert result[0].text == "First reply"
        assert result[1].id == "reply_2"
        client.close()

    @respx.mock
    def test_get_replies_with_reverse(self):
        """Test getting replies in reverse order."""
        respx.get("https://graph.threads.net/v1.0/post_123/replies").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "reply_1",
                            "text": "Oldest first",
                            "timestamp": "2024-01-15T10:00:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.get_replies("post_123", reverse=True)

        assert len(result) == 1
        client.close()

    @respx.mock
    def test_get_replies_error(self):
        """Test getting replies with error."""
        respx.get("https://graph.threads.net/v1.0/post_123/replies").mock(
            return_value=httpx.Response(
                404,
                json={
                    "error": {
                        "message": "Post not found",
                        "type": "ThreadsAPIException",
                        "code": 100,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        with pytest.raises(ThreadsAPIError):
            client.replies.get_replies("post_123")
        client.close()

    @respx.mock
    def test_get_conversation(self):
        """Test getting conversation thread."""
        respx.get("https://graph.threads.net/v1.0/reply_123/conversation").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post_1",
                            "text": "Original post",
                            "timestamp": "2024-01-15T10:00:00+0000",
                        },
                        {
                            "id": "reply_1",
                            "text": "Reply to post",
                            "timestamp": "2024-01-15T11:00:00+0000",
                        },
                        {
                            "id": "reply_123",
                            "text": "Reply to reply",
                            "timestamp": "2024-01-15T12:00:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.get_conversation("reply_123")

        assert len(result) == 3
        assert result[0].text == "Original post"
        assert result[2].id == "reply_123"
        client.close()

    @respx.mock
    def test_hide_reply(self):
        """Test hiding a reply."""
        respx.post("https://graph.threads.net/v1.0/reply_123/manage_reply").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.hide("reply_123")

        assert result is True
        client.close()

    @respx.mock
    def test_hide_reply_failure(self):
        """Test hiding a reply that fails."""
        respx.post("https://graph.threads.net/v1.0/reply_123/manage_reply").mock(
            return_value=httpx.Response(200, json={"success": False})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.hide("reply_123")

        assert result is False
        client.close()

    @respx.mock
    def test_unhide_reply(self):
        """Test unhiding a reply."""
        respx.post("https://graph.threads.net/v1.0/reply_123/manage_reply").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.unhide("reply_123")

        assert result is True
        client.close()

    @respx.mock
    def test_get_user_replies(self):
        """Test getting replies by a user."""
        respx.get("https://graph.threads.net/v1.0/user_123/replies").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "reply_1",
                            "text": "User's reply 1",
                            "timestamp": "2024-01-15T10:00:00+0000",
                        },
                        {
                            "id": "reply_2",
                            "text": "User's reply 2",
                            "timestamp": "2024-01-14T10:00:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.get_user_replies("user_123")

        assert len(result) == 2
        assert result[0].text == "User's reply 1"
        client.close()

    @respx.mock
    def test_get_user_replies_with_filters(self):
        """Test getting user replies with time filters."""
        respx.get("https://graph.threads.net/v1.0/user_123/replies").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "reply_1",
                            "text": "Filtered reply",
                            "timestamp": "2024-01-15T10:00:00+0000",
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.replies.get_user_replies(
            "user_123",
            since="1704067200",
            until="1706745600",
            limit=50,
        )

        assert len(result) == 1
        client.close()
