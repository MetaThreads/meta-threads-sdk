"""Tests for type definitions and protocols."""

from __future__ import annotations

from typing import Any

import pytest

from threads.types import (
    JSON,
    AsyncHTTPClient,
    Headers,
    HTTPClient,
    QueryParams,
    SupportsAsyncClose,
    SupportsClose,
)


class TestTypeAliases:
    """Tests for type aliases."""

    def test_json_type(self):
        """Test JSON type alias accepts dict."""
        data: JSON = {"key": "value", "number": 123, "nested": {"inner": True}}
        assert isinstance(data, dict)
        assert data["key"] == "value"

    def test_headers_type(self):
        """Test Headers type alias accepts string dict."""
        headers: Headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        assert isinstance(headers, dict)
        assert headers["Content-Type"] == "application/json"

    def test_query_params_type(self):
        """Test QueryParams type alias accepts mixed value dict."""
        params: QueryParams = {
            "access_token": "token123",
            "limit": 10,
            "active": True,
            "optional": None,
        }
        assert isinstance(params, dict)
        assert params["limit"] == 10


class TestSupportsCloseProtocol:
    """Tests for SupportsClose protocol."""

    def test_object_with_close_matches_protocol(self):
        """Test that object with close method matches protocol."""

        class Closeable:
            def close(self) -> None:
                pass

        obj = Closeable()
        assert isinstance(obj, SupportsClose)

    def test_object_without_close_does_not_match(self):
        """Test that object without close method doesn't match."""

        class NotCloseable:
            def shutdown(self) -> None:
                pass

        obj = NotCloseable()
        assert not isinstance(obj, SupportsClose)


class TestSupportsAsyncCloseProtocol:
    """Tests for SupportsAsyncClose protocol."""

    def test_object_with_aclose_matches_protocol(self):
        """Test that object with aclose method matches protocol."""

        class AsyncCloseable:
            async def aclose(self) -> None:
                pass

        obj = AsyncCloseable()
        assert isinstance(obj, SupportsAsyncClose)

    def test_object_without_aclose_does_not_match(self):
        """Test that object without aclose method doesn't match."""

        class NotAsyncCloseable:
            def close(self) -> None:
                pass

        obj = NotAsyncCloseable()
        assert not isinstance(obj, SupportsAsyncClose)


class TestHTTPClientProtocol:
    """Tests for HTTPClient protocol."""

    def test_conforming_class_matches_protocol(self):
        """Test that a conforming class matches HTTPClient protocol."""

        class MockHTTPClient:
            def get(
                self,
                url: str,
                *,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"data": "response"}

            def post(
                self,
                url: str,
                *,
                data: JSON | None = None,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"id": "123"}

            def delete(
                self,
                url: str,
                *,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"success": True}

            def close(self) -> None:
                pass

        client = MockHTTPClient()
        assert isinstance(client, HTTPClient)

    def test_partial_implementation_does_not_match(self):
        """Test that partial implementation doesn't match."""

        class PartialClient:
            def get(self, url: str) -> Any:
                return {}

        client = PartialClient()
        assert not isinstance(client, HTTPClient)


class TestAsyncHTTPClientProtocol:
    """Tests for AsyncHTTPClient protocol."""

    def test_conforming_class_matches_protocol(self):
        """Test that a conforming class matches AsyncHTTPClient protocol."""

        class MockAsyncHTTPClient:
            async def get(
                self,
                url: str,
                *,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"data": "response"}

            async def post(
                self,
                url: str,
                *,
                data: JSON | None = None,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"id": "123"}

            async def delete(
                self,
                url: str,
                *,
                params: QueryParams | None = None,
                headers: Headers | None = None,
            ) -> Any:
                return {"success": True}

            async def aclose(self) -> None:
                pass

        client = MockAsyncHTTPClient()
        assert isinstance(client, AsyncHTTPClient)

    def test_sync_client_does_not_match_async_protocol(self):
        """Test that sync client doesn't match async protocol."""

        class SyncClient:
            def get(self, url: str) -> Any:
                return {}

            def close(self) -> None:
                pass

        client = SyncClient()
        assert not isinstance(client, AsyncHTTPClient)
