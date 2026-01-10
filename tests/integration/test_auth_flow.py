"""Integration tests for OAuth flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads.constants import Scope


if TYPE_CHECKING:
    from threads import ThreadsClient


class TestAuthorizationUrl:
    """Tests for authorization URL generation."""

    def test_generate_auth_url(self, client: ThreadsClient):
        url = client.auth.get_authorization_url(
            client_id="app_123",
            redirect_uri="https://example.com/callback",
        )

        assert "https://threads.net/oauth/authorize" in url
        assert "client_id=app_123" in url
        assert "redirect_uri=https://example.com/callback" in url
        assert "response_type=code" in url
        client.close()

    def test_auth_url_with_scopes(self, client: ThreadsClient):
        url = client.auth.get_authorization_url(
            client_id="app_123",
            redirect_uri="https://example.com/callback",
            scopes=[Scope.BASIC, Scope.CONTENT_PUBLISH, Scope.MANAGE_INSIGHTS],
        )

        assert "threads_basic" in url
        assert "threads_content_publish" in url
        assert "threads_manage_insights" in url
        client.close()

    def test_auth_url_with_state(self, client: ThreadsClient):
        url = client.auth.get_authorization_url(
            client_id="app_123",
            redirect_uri="https://example.com/callback",
            state="random_state_123",
        )

        assert "state=random_state_123" in url
        client.close()
