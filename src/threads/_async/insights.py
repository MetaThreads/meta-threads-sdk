"""Asynchronous insights client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.insights import BaseInsightsClient
from threads.constants import MetricType
from threads.exceptions import raise_for_error
from threads.models.insights import InsightsResponse, UserInsightsResponse

if TYPE_CHECKING:
    from threads._async.client import AsyncThreadsClient


class AsyncInsightsClient(BaseInsightsClient):
    """Asynchronous client for insights operations."""

    def __init__(self, parent: AsyncThreadsClient) -> None:
        super().__init__(parent)
        self._parent: AsyncThreadsClient = parent

    async def get_media_insights(
        self,
        media_id: str,
        metrics: list[MetricType] | None = None,
    ) -> InsightsResponse:
        """Get insights for a specific post.

        Args:
            media_id: The post/media ID.
            metrics: Specific metrics to retrieve. Defaults to all.

        Returns:
            InsightsResponse with the requested metrics.
        """
        metrics_str = self._build_metrics_param(metrics, self.MEDIA_METRICS)
        params = self._get_params(metric=metrics_str)

        response = await self._parent.http.get(
            f"/{media_id}/insights",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return InsightsResponse.model_validate(data)

    async def get_user_insights(
        self,
        user_id: str,
        metrics: list[MetricType] | None = None,
        *,
        since: int | None = None,
        until: int | None = None,
    ) -> UserInsightsResponse:
        """Get insights for a user account.

        Args:
            user_id: The Threads user ID.
            metrics: Specific metrics to retrieve.
            since: Unix timestamp for start of period.
            until: Unix timestamp for end of period.

        Returns:
            UserInsightsResponse with the requested metrics.
        """
        metrics_str = self._build_metrics_param(metrics, self.USER_METRICS)
        params = self._get_params(
            metric=metrics_str,
            since=since,
            until=until,
        )

        response = await self._parent.http.get(
            f"/{user_id}/threads_insights",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return UserInsightsResponse.model_validate(data)

    async def get_views(self, media_id: str) -> int:
        """Get view count for a post.

        Args:
            media_id: The post/media ID.

        Returns:
            Number of views.
        """
        insights = await self.get_media_insights(media_id, [MetricType.VIEWS])
        return insights.views

    async def get_engagement(self, media_id: str) -> dict[str, int]:
        """Get all engagement metrics for a post.

        Args:
            media_id: The post/media ID.

        Returns:
            Dictionary with likes, replies, reposts, quotes counts.
        """
        insights = await self.get_media_insights(
            media_id,
            [
                MetricType.LIKES,
                MetricType.REPLIES,
                MetricType.REPOSTS,
                MetricType.QUOTES,
            ],
        )

        return {
            "likes": insights.likes,
            "replies": insights.replies,
            "reposts": insights.reposts,
            "quotes": insights.quotes,
        }
