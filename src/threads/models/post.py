"""Post models for the Threads API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from threads.constants import MediaType, ReplyControl


class Post(BaseModel):
    """A Threads post."""

    id: str
    media_product_type: str = "THREADS"
    media_type: MediaType
    media_url: str | None = None
    permalink: str | None = None
    owner: dict[str, str] | None = None
    username: str | None = None
    text: str | None = None
    timestamp: datetime | None = None
    shortcode: str | None = None
    thumbnail_url: str | None = None
    children: list[dict[str, str]] | None = Field(
        default=None,
        description="Child posts for carousels",
    )

    is_quote_post: bool = False
    has_replies: bool | None = None
    root_post: dict[str, str] | None = None
    replied_to: dict[str, str] | None = None
    is_reply: bool | None = None
    is_reply_owned_by_me: bool | None = None
    reply_audience: ReplyControl | None = None
    hide_status: str | None = None

    @field_validator("children", mode="before")
    @classmethod
    def extract_children_data(cls, v: Any) -> list[dict[str, str]] | None:
        """Extract children list from API response format."""
        if v is None:
            return None
        if isinstance(v, dict) and "data" in v:
            return v["data"]
        return v


class Reply(BaseModel):
    """A reply to a Threads post."""

    id: str
    text: str | None = None
    username: str | None = None
    permalink: str | None = None
    timestamp: datetime | None = None
    media_type: MediaType | None = None
    media_url: str | None = None
    hide_status: str | None = None
    has_replies: bool | None = None


class PublishingLimit(BaseModel):
    """User's publishing rate limit status."""

    quota_usage: int = Field(description="Posts made in the current period")
    quota_total: int = Field(
        default=250,
        description="Maximum posts allowed per 24 hours",
    )
    reply_quota_usage: int | None = Field(
        default=None,
        description="Replies made in the current period",
    )
    reply_quota_total: int | None = Field(
        default=1000,
        description="Maximum replies allowed per 24 hours",
    )

    @property
    def remaining_posts(self) -> int:
        """Calculate remaining posts allowed."""
        return max(0, self.quota_total - self.quota_usage)

    @property
    def remaining_replies(self) -> int | None:
        """Calculate remaining replies allowed."""
        if self.reply_quota_usage is None or self.reply_quota_total is None:
            return None
        return max(0, self.reply_quota_total - self.reply_quota_usage)
