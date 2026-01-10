"""Tests for HTTP utilities."""

from __future__ import annotations

import pytest

from threads._utils.http import (
    build_url,
    extract_id,
    parse_error_response,
    prepare_request_params,
)
from threads.exceptions import ThreadsAPIError


class TestBuildUrl:
    """Tests for build_url function."""

    def test_simple_endpoint(self):
        """Test building URL with simple endpoint."""
        url = build_url("me/threads")

        assert url == "https://graph.threads.net/v1.0/me/threads"

    def test_endpoint_with_leading_slash(self):
        """Test building URL with leading slash."""
        url = build_url("/me/threads")

        assert url == "https://graph.threads.net/v1.0/me/threads"

    def test_endpoint_with_path_params(self):
        """Test building URL with path parameters."""
        url = build_url(
            "{user_id}/threads",
            path_params={"user_id": "123456"},
        )

        assert url == "https://graph.threads.net/v1.0/123456/threads"

    def test_endpoint_with_query_params(self):
        """Test building URL with query parameters."""
        url = build_url(
            "me/threads",
            query_params={"access_token": "token123", "fields": "id,text"},
        )

        assert "access_token=token123" in url
        assert "fields=id%2Ctext" in url or "fields=id,text" in url

    def test_query_params_none_filtered(self):
        """Test that None values are filtered from query params."""
        url = build_url(
            "me/threads",
            query_params={"access_token": "token123", "since": None, "until": None},
        )

        assert "access_token=token123" in url
        assert "since" not in url
        assert "until" not in url

    def test_custom_base_url(self):
        """Test building URL with custom base URL."""
        url = build_url(
            "me/threads",
            base_url="https://custom.api.com",
        )

        assert url == "https://custom.api.com/v1.0/me/threads"

    def test_custom_version(self):
        """Test building URL with custom API version."""
        url = build_url(
            "me/threads",
            version="v2.0",
        )

        assert url == "https://graph.threads.net/v2.0/me/threads"


class TestParseErrorResponse:
    """Tests for parse_error_response function."""

    def test_raises_on_error_response(self):
        """Test that error response raises exception."""
        response_data = {
            "error": {
                "message": "Invalid access token",
                "type": "OAuthException",
                "code": 190,
            }
        }

        with pytest.raises(ThreadsAPIError):
            parse_error_response(response_data, 401)

    def test_no_raise_on_success(self):
        """Test that success response doesn't raise."""
        response_data = {"id": "123", "text": "Hello"}

        # Should not raise
        parse_error_response(response_data, 200)


class TestExtractId:
    """Tests for extract_id function."""

    def test_extract_id_success(self):
        """Test extracting ID from response."""
        response = {"id": "post_123", "text": "Hello"}

        result = extract_id(response)

        assert result == "post_123"

    def test_extract_id_missing(self):
        """Test extracting ID when not present."""
        response = {"text": "Hello"}

        with pytest.raises(KeyError):
            extract_id(response)


class TestPrepareRequestParams:
    """Tests for prepare_request_params function."""

    def test_basic_params(self):
        """Test preparing basic params."""
        result = prepare_request_params("token123")

        assert result == {"access_token": "token123"}

    def test_with_extra_params(self):
        """Test preparing params with extras."""
        result = prepare_request_params(
            "token123",
            extra_params={"fields": "id,text", "limit": 10},
        )

        assert result == {
            "access_token": "token123",
            "fields": "id,text",
            "limit": 10,
        }

    def test_extra_params_none_filtered(self):
        """Test that None values in extra params are filtered."""
        result = prepare_request_params(
            "token123",
            extra_params={"fields": "id,text", "since": None, "until": None},
        )

        assert result == {
            "access_token": "token123",
            "fields": "id,text",
        }
        assert "since" not in result
        assert "until" not in result

    def test_empty_extra_params(self):
        """Test with empty extra params."""
        result = prepare_request_params("token123", extra_params={})

        assert result == {"access_token": "token123"}

    def test_none_extra_params(self):
        """Test with None extra params."""
        result = prepare_request_params("token123", extra_params=None)

        assert result == {"access_token": "token123"}
