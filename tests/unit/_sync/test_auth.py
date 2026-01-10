"""Tests for synchronous auth client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.exceptions import AuthenticationError


class TestAuthClient:
    """Tests for AuthClient."""

    @respx.mock
    def test_exchange_code_success(self):
        """Test successful code exchange."""
        respx.post("https://graph.threads.net/oauth/access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "short_lived_token_123",
                    "user_id": 12345678,
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        result = client.auth.exchange_code(
            client_id="app_123",
            client_secret="secret_456",
            redirect_uri="https://example.com/callback",
            code="auth_code_789",
        )

        assert result.access_token == "short_lived_token_123"
        assert result.user_id == "12345678"
        client.close()

    @respx.mock
    def test_exchange_code_error(self):
        """Test code exchange with error response."""
        respx.post("https://graph.threads.net/oauth/access_token").mock(
            return_value=httpx.Response(
                401,
                json={
                    "error": {
                        "message": "Invalid authorization code",
                        "type": "OAuthException",
                        "code": 190,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        with pytest.raises(AuthenticationError):
            client.auth.exchange_code(
                client_id="app_123",
                client_secret="secret_456",
                redirect_uri="https://example.com/callback",
                code="invalid_code",
            )
        client.close()

    @respx.mock
    def test_get_long_lived_token_success(self):
        """Test successful long-lived token exchange."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "long_lived_token_abc",
                    "token_type": "bearer",
                    "expires_in": 5184000,
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        result = client.auth.get_long_lived_token(
            client_secret="secret_456",
            short_lived_token="short_token",
        )

        assert result.access_token == "long_lived_token_abc"
        assert result.token_type == "bearer"
        assert result.expires_in == 5184000
        assert result.expires_in_days == 60
        client.close()

    @respx.mock
    def test_get_long_lived_token_error(self):
        """Test long-lived token exchange with error."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/access_token").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "Invalid short-lived token",
                        "type": "OAuthException",
                        "code": 190,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        with pytest.raises(AuthenticationError):
            client.auth.get_long_lived_token(
                client_secret="secret_456",
                short_lived_token="invalid_token",
            )
        client.close()

    @respx.mock
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/refresh_access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "refreshed_token_xyz",
                    "token_type": "bearer",
                    "expires_in": 5184000,
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        result = client.auth.refresh_token(access_token="old_token")

        assert result.access_token == "refreshed_token_xyz"
        assert result.token_type == "bearer"
        assert result.expires_in == 5184000
        client.close()

    @respx.mock
    def test_refresh_token_error(self):
        """Test token refresh with error."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/refresh_access_token").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "Token expired",
                        "type": "OAuthException",
                        "code": 190,
                    }
                },
            )
        )

        client = ThreadsClient(access_token="temp")
        with pytest.raises(AuthenticationError):
            client.auth.refresh_token(access_token="expired_token")
        client.close()
