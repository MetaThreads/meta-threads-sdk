"""Tests for synchronous ThreadsClient."""

import respx
from httpx import Response

from threads import MediaType, ThreadsClient


class TestThreadsClient:
    """Tests for ThreadsClient initialization and lifecycle."""

    def test_init(self, access_token: str):
        client = ThreadsClient(access_token=access_token)
        assert client.access_token == access_token
        client.close()

    def test_context_manager(self, access_token: str):
        with ThreadsClient(access_token=access_token) as client:
            assert client.access_token == access_token

    def test_update_access_token(self, access_token: str):
        client = ThreadsClient(access_token=access_token)
        client.access_token = "new_token"
        assert client.access_token == "new_token"
        client.close()

    def test_sub_clients_available(self, client: ThreadsClient):
        assert client.auth is not None
        assert client.media is not None
        assert client.posts is not None
        assert client.insights is not None
        assert client.replies is not None
        assert client.webhooks is not None
        client.close()


class TestPostsClient:
    """Tests for posts operations."""

    @respx.mock
    def test_get_post(
        self,
        client: ThreadsClient,
        mock_post_response: dict,
    ):
        respx.get("https://graph.threads.net/v1.0/post_123").mock(
            return_value=Response(200, json=mock_post_response)
        )

        post = client.posts.get("post_123")
        assert post.id == "post_123"
        assert post.text == "Hello, Threads!"
        client.close()

    @respx.mock
    def test_get_user_posts(
        self,
        client: ThreadsClient,
        user_id: str,
        mock_post_response: dict,
    ):
        respx.get(f"https://graph.threads.net/v1.0/{user_id}/threads").mock(
            return_value=Response(200, json={"data": [mock_post_response]})
        )

        posts = client.posts.get_user_posts(user_id)
        assert len(posts) == 1
        assert posts[0].id == "post_123"
        client.close()


class TestMediaClient:
    """Tests for media operations."""

    @respx.mock
    def test_create_container(
        self,
        client: ThreadsClient,
        user_id: str,
        mock_container_response: dict,
    ):
        respx.post(f"https://graph.threads.net/v1.0/{user_id}/threads").mock(
            return_value=Response(200, json=mock_container_response)
        )

        container = client.media.create_container(
            user_id,
            MediaType.TEXT,
            text="Hello!",
        )
        assert container.id == "container_123"
        client.close()


class TestInsightsClient:
    """Tests for insights operations."""

    @respx.mock
    def test_get_media_insights(
        self,
        client: ThreadsClient,
        mock_insights_response: dict,
    ):
        respx.get("https://graph.threads.net/v1.0/post_123/insights").mock(
            return_value=Response(200, json=mock_insights_response)
        )

        insights = client.insights.get_media_insights("post_123")
        assert insights.views == 1000
        assert insights.likes == 50
        client.close()
