"""Tests for asynchronous users client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import AsyncThreadsClient
from threads.exceptions import AuthenticationError, NotFoundError


class TestAsyncUsersClient:
    """Tests for AsyncUsersClient."""

    @respx.mock
    async def test_get_me_success(self):
        """Test successful async get_me request."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/me").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "12345678",
                    "username": "testuser",
                    "name": "Test User",
                    "threads_profile_picture_url": "https://example.com/pic.jpg",
                    "threads_biography": "Hello, I'm a test user",
                },
            )
        )

        async with AsyncThreadsClient(access_token="test_token") as client:
            result = await client.users.get_me()

            assert result.id == "12345678"
            assert result.username == "testuser"
            assert result.name == "Test User"
            assert result.threads_profile_picture_url == "https://example.com/pic.jpg"
            assert result.threads_biography == "Hello, I'm a test user"

    @respx.mock
    async def test_get_me_with_custom_fields(self):
        """Test async get_me with custom fields."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/me").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "12345678",
                    "username": "testuser",
                    "follower_count": 1000,
                    "following_count": 500,
                },
            )
        )

        async with AsyncThreadsClient(access_token="test_token") as client:
            result = await client.users.get_me(
                fields=["id", "username", "follower_count", "following_count"]
            )

            assert result.id == "12345678"
            assert result.username == "testuser"
            assert result.follower_count == 1000
            assert result.following_count == 500

    @respx.mock
    async def test_get_me_authentication_error(self):
        """Test async get_me with authentication error."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/me").mock(
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

        async with AsyncThreadsClient(access_token="invalid_token") as client:
            with pytest.raises(AuthenticationError):
                await client.users.get_me()

    @respx.mock
    async def test_get_user_success(self):
        """Test successful async get user by ID."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/user_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "user_123",
                    "username": "otheruser",
                    "name": "Other User",
                    "threads_profile_picture_url": "https://example.com/other.jpg",
                    "threads_biography": "Another user profile",
                },
            )
        )

        async with AsyncThreadsClient(access_token="test_token") as client:
            result = await client.users.get("user_123")

            assert result.id == "user_123"
            assert result.username == "otheruser"
            assert result.name == "Other User"
            assert result.threads_biography == "Another user profile"

    @respx.mock
    async def test_get_user_with_custom_fields(self):
        """Test async get user by ID with custom fields."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/user_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "user_456",
                    "username": "customuser",
                    "is_eligible_for_geo_gating": True,
                    "hide_status": "visible",
                },
            )
        )

        async with AsyncThreadsClient(access_token="test_token") as client:
            result = await client.users.get(
                "user_456",
                fields=["id", "username", "is_eligible_for_geo_gating", "hide_status"],
            )

            assert result.id == "user_456"
            assert result.username == "customuser"
            assert result.is_eligible_for_geo_gating is True
            assert result.hide_status == "visible"

    @respx.mock
    async def test_get_user_not_found(self):
        """Test async get user with not found error."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/nonexistent").mock(
            return_value=httpx.Response(
                404,
                json={
                    "error": {
                        "message": "User not found",
                        "type": "OAuthException",
                        "code": 100,
                    }
                },
            )
        )

        async with AsyncThreadsClient(access_token="test_token") as client:
            with pytest.raises(NotFoundError):
                await client.users.get("nonexistent")

    async def test_default_profile_fields(self):
        """Test that default profile fields are set correctly."""
        async with AsyncThreadsClient(access_token="test_token") as client:
            expected_fields = [
                "id",
                "username",
                "name",
                "threads_profile_picture_url",
                "threads_biography",
            ]

            assert client.users.DEFAULT_PROFILE_FIELDS == expected_fields

    async def test_extended_profile_fields(self):
        """Test that extended profile fields are set correctly."""
        async with AsyncThreadsClient(access_token="test_token") as client:
            expected_fields = [
                "id",
                "username",
                "name",
                "threads_profile_picture_url",
                "threads_biography",
                "is_eligible_for_geo_gating",
                "hide_status",
                "follower_count",
                "following_count",
            ]

            assert client.users.EXTENDED_PROFILE_FIELDS == expected_fields
