"""Insights models for the Threads API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from threads.constants import MetricType


class Insight(BaseModel):
    """A single insight metric."""

    name: MetricType
    period: str = "lifetime"
    values: list[dict[str, int | str]]
    title: str | None = None
    description: str | None = None
    id: str | None = None

    @property
    def value(self) -> int:
        """Get the primary value for this metric."""
        if self.values and len(self.values) > 0:
            return int(self.values[0].get("value", 0))
        return 0


class InsightsResponse(BaseModel):
    """Response containing media insights."""

    data: list[Insight]

    def get_metric(self, metric: MetricType) -> int:
        """Get a specific metric value."""
        for insight in self.data:
            if insight.name == metric:
                return insight.value
        return 0

    @property
    def views(self) -> int:
        """Get views count."""
        return self.get_metric(MetricType.VIEWS)

    @property
    def likes(self) -> int:
        """Get likes count."""
        return self.get_metric(MetricType.LIKES)

    @property
    def replies(self) -> int:
        """Get replies count."""
        return self.get_metric(MetricType.REPLIES)

    @property
    def reposts(self) -> int:
        """Get reposts count."""
        return self.get_metric(MetricType.REPOSTS)

    @property
    def quotes(self) -> int:
        """Get quotes count."""
        return self.get_metric(MetricType.QUOTES)


class UserInsight(BaseModel):
    """A single user-level insight metric."""

    name: str
    period: str | None = None
    values: list[dict[str, int | str | dict[str, int]]] | None = None
    title: str | None = None
    description: str | None = None
    total_value: dict[str, int] | None = None
    id: str | None = None


class UserInsightsResponse(BaseModel):
    """Response containing user-level insights."""

    data: list[UserInsight]

    def get_metric(self, metric_name: str) -> int | None:
        """Get a specific metric value."""
        for insight in self.data:
            if insight.name == metric_name:
                if insight.total_value is not None:
                    return insight.total_value.get("value")
                if insight.values:
                    val = insight.values[0].get("value", 0)
                    if isinstance(val, int):
                        return val
                    if isinstance(val, str):
                        return int(val)
                    return 0
        return None


class DemographicBreakdown(BaseModel):
    """Demographic breakdown for user insights."""

    dimension: str = Field(description="e.g., 'city', 'country', 'age', 'gender'")
    results: list[dict[str, str | int]]
    timestamp: datetime | None = None
