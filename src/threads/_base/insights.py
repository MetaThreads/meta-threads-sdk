"""Base insights client."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from threads._base.client import BaseSubClient, BaseThreadsClient
from threads.constants import MetricType


class BaseInsightsClient(BaseSubClient, ABC):
    """Abstract base class for insights operations.

    Handles retrieving analytics and metrics for posts and users.
    """

    # Available metrics for media insights
    MEDIA_METRICS: ClassVar[list[MetricType]] = [
        MetricType.VIEWS,
        MetricType.LIKES,
        MetricType.REPLIES,
        MetricType.REPOSTS,
        MetricType.QUOTES,
    ]

    # Available metrics for user insights (follower_demographics requires breakdown param)
    USER_METRICS: ClassVar[list[MetricType]] = [
        MetricType.VIEWS,
        MetricType.FOLLOWERS_COUNT,
    ]

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    @abstractmethod
    def get_media_insights(
        self,
        media_id: str,
        metrics: list[MetricType] | None = None,
    ) -> Any:
        """Get insights for a specific post.

        Args:
            media_id: The post/media ID.
            metrics: Specific metrics to retrieve. Defaults to all.

        Returns:
            InsightsResponse with the requested metrics.
        """
        ...

    @abstractmethod
    def get_user_insights(
        self,
        user_id: str,
        metrics: list[MetricType] | None = None,
        *,
        since: int | None = None,
        until: int | None = None,
    ) -> Any:
        """Get insights for a user account.

        Args:
            user_id: The Threads user ID.
            metrics: Specific metrics to retrieve.
            since: Unix timestamp for start of period.
            until: Unix timestamp for end of period.

        Returns:
            UserInsightsResponse with the requested metrics.
        """
        ...

    def _build_metrics_param(
        self,
        metrics: list[MetricType] | None,
        default_metrics: list[MetricType],
    ) -> str:
        """Build comma-separated metrics parameter.

        Args:
            metrics: User-specified metrics or None for defaults.
            default_metrics: Default metrics to use if none specified.

        Returns:
            Comma-separated metric names.
        """
        if metrics is None:
            metrics = default_metrics
        return ",".join(m.value for m in metrics)
