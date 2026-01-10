"""Media models for the Threads API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from threads.constants import ContainerStatus, MediaType


class MediaContainer(BaseModel):
    """Media container for publishing posts."""

    id: str = Field(description="Container ID returned by the API")


class MediaContainerStatus(BaseModel):
    """Status of a media container."""

    id: str
    status: ContainerStatus
    error_message: str | None = Field(
        default=None,
        description="Error message if status is ERROR",
    )

    @property
    def is_ready(self) -> bool:
        """Check if container is ready for publishing."""
        return self.status == ContainerStatus.FINISHED

    @property
    def has_error(self) -> bool:
        """Check if container has an error."""
        return self.status == ContainerStatus.ERROR


class MediaUploadRequest(BaseModel):
    """Request parameters for creating a media container."""

    media_type: MediaType
    text: str | None = None
    image_url: str | None = None
    video_url: str | None = None
    is_carousel_item: bool = False
    children: list[str] | None = Field(
        default=None,
        description="Container IDs for carousel items",
    )
    reply_to_id: str | None = Field(
        default=None,
        description="Post ID to reply to",
    )
    reply_control: str | None = Field(
        default=None,
        description="Who can reply: everyone, accounts_you_follow, mentioned_only",
    )
    allowlisted_country_codes: list[str] | None = Field(
        default=None,
        description="ISO country codes for geo-gating",
    )
