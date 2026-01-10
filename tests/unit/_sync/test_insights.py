"""Tests for synchronous insights client."""

from __future__ import annotations

import httpx
import pytest
import respx

from threads import ThreadsClient
from threads.constants import MetricType
from threads.exceptions import ThreadsAPIError


class TestInsightsClient:
    """Tests for InsightsClient."""

    @respx.mock
    def test_get_media_insights(self):
        """Test getting media insights."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123/insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"name": "views", "values": [{"value": 1500}]},
                        {"name": "likes", "values": [{"value": 100}]},
                        {"name": "replies", "values": [{"value": 25}]},
                        {"name": "reposts", "values": [{"value": 10}]},
                        {"name": "quotes", "values": [{"value": 5}]},
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_media_insights("post_123")

        assert result.views == 1500
        assert result.likes == 100
        assert result.replies == 25
        assert result.reposts == 10
        assert result.quotes == 5
        client.close()

    @respx.mock
    def test_get_media_insights_with_specific_metrics(self):
        """Test getting specific media insights."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123/insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"name": "views", "values": [{"value": 1500}]},
                        {"name": "likes", "values": [{"value": 100}]},
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_media_insights(
            "post_123",
            metrics=[MetricType.VIEWS, MetricType.LIKES],
        )

        assert result.views == 1500
        assert result.likes == 100
        client.close()

    @respx.mock
    def test_get_media_insights_error(self):
        """Test getting media insights with error."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123/insights").mock(
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
            client.insights.get_media_insights("post_123")
        client.close()

    @respx.mock
    def test_get_user_insights(self):
        """Test getting user insights."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/user_123/threads_insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "name": "views",
                            "period": "lifetime",
                            "values": [{"value": 50000}],
                            "total_value": {"value": 50000},
                        },
                        {
                            "name": "followers_count",
                            "period": "lifetime",
                            "values": [{"value": 1000}],
                            "total_value": {"value": 1000},
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_user_insights("user_123")

        assert result.get_metric("views") == 50000
        assert result.get_metric("followers_count") == 1000
        client.close()

    @respx.mock
    def test_get_user_insights_with_time_range(self):
        """Test getting user insights with time range."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/user_123/threads_insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "name": "views",
                            "period": "day",
                            "values": [{"value": 10000}],
                            "total_value": {"value": 10000},
                        },
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_user_insights(
            "user_123",
            since=1704067200,
            until=1706745600,
        )

        assert result.get_metric("views") == 10000
        client.close()

    @respx.mock
    def test_get_views(self):
        """Test getting view count convenience method."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123/insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"name": "views", "values": [{"value": 2500}]},
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_views("post_123")

        assert result == 2500
        client.close()

    @respx.mock
    def test_get_engagement(self):
        """Test getting engagement metrics."""
        respx.get(url__startswith="https://graph.threads.net/v1.0/post_123/insights").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"name": "likes", "values": [{"value": 150}]},
                        {"name": "replies", "values": [{"value": 30}]},
                        {"name": "reposts", "values": [{"value": 15}]},
                        {"name": "quotes", "values": [{"value": 8}]},
                    ]
                },
            )
        )

        client = ThreadsClient(access_token="token_123")
        result = client.insights.get_engagement("post_123")

        assert result == {
            "likes": 150,
            "replies": 30,
            "reposts": 15,
            "quotes": 8,
        }
        client.close()
