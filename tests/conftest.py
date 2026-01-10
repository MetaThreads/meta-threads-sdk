"""Shared test fixtures."""

import pytest

from threads import AsyncThreadsClient, ThreadsClient


@pytest.fixture
def access_token() -> str:
    """Fixture providing a test access token."""
    return "test_access_token_123"


@pytest.fixture
def user_id() -> str:
    """Fixture providing a test user ID."""
    return "123456789"


@pytest.fixture
def client(access_token: str) -> ThreadsClient:
    """Fixture providing a sync ThreadsClient."""
    return ThreadsClient(access_token=access_token)


@pytest.fixture
async def async_client(access_token: str) -> AsyncThreadsClient:
    """Fixture providing an async ThreadsClient."""
    return AsyncThreadsClient(access_token=access_token)


@pytest.fixture
def mock_post_response() -> dict:
    """Fixture providing a mock post API response."""
    return {
        "id": "post_123",
        "media_product_type": "THREADS",
        "media_type": "TEXT",
        "text": "Hello, Threads!",
        "permalink": "https://threads.net/@user/post/123",
        "username": "testuser",
        "timestamp": "2024-01-01T12:00:00Z",
        "is_quote_post": False,
    }


@pytest.fixture
def mock_container_response() -> dict:
    """Fixture providing a mock container API response."""
    return {"id": "container_123"}


@pytest.fixture
def mock_insights_response() -> dict:
    """Fixture providing a mock insights API response."""
    return {
        "data": [
            {"name": "views", "period": "lifetime", "values": [{"value": 1000}]},
            {"name": "likes", "period": "lifetime", "values": [{"value": 50}]},
            {"name": "replies", "period": "lifetime", "values": [{"value": 10}]},
            {"name": "reposts", "period": "lifetime", "values": [{"value": 5}]},
            {"name": "quotes", "period": "lifetime", "values": [{"value": 2}]},
        ]
    }


@pytest.fixture
def mock_error_response() -> dict:
    """Fixture providing a mock error API response."""
    return {
        "error": {
            "message": "Invalid OAuth access token.",
            "type": "OAuthException",
            "code": 190,
            "fbtrace_id": "ABC123",
        }
    }
