"""Base users client."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from threads._base.client import BaseSubClient, BaseThreadsClient


class BaseUsersClient(BaseSubClient, ABC):
    """Abstract base class for user profile operations.

    Handles retrieving user profile information.
    """

    # Default fields to retrieve for user profiles
    DEFAULT_PROFILE_FIELDS: ClassVar[list[str]] = [
        "id",
        "username",
        "name",
        "threads_profile_picture_url",
        "threads_biography",
    ]

    # Extended fields that require additional permissions
    EXTENDED_PROFILE_FIELDS: ClassVar[list[str]] = [
        "id",
        "username",
        "name",
        "threads_profile_picture_url",
        "threads_biography",
        "is_eligible_for_geo_gating",
        "hide_status",
        "follower_count",
        "following_count",
    ]

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    @abstractmethod
    def get_me(
        self,
        fields: list[str] | None = None,
    ) -> Any:
        """Get the authenticated user's profile.

        Args:
            fields: Fields to retrieve. If None, uses DEFAULT_PROFILE_FIELDS.

        Returns:
            UserProfile with the requested fields.
        """
        ...

    @abstractmethod
    def get(
        self,
        user_id: str,
        fields: list[str] | None = None,
    ) -> Any:
        """Get a user's profile by ID.

        Args:
            user_id: The Threads user ID.
            fields: Fields to retrieve. If None, uses DEFAULT_PROFILE_FIELDS.

        Returns:
            UserProfile with the requested fields.
        """
        ...
