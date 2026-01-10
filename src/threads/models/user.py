"""User models for the Threads API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class User(BaseModel):
    """Basic user information."""

    id: str
    username: str | None = None
    name: str | None = None
    threads_profile_picture_url: str | None = None
    threads_biography: str | None = None


class UserProfile(BaseModel):
    """Extended user profile information."""

    id: str
    username: str | None = None
    name: str | None = None
    threads_profile_picture_url: str | None = None
    threads_biography: str | None = None
    is_eligible_for_geo_gating: bool | None = Field(
        default=None,
        description="Whether user can use geo-gating features",
    )
    hide_status: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
