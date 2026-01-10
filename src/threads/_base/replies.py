"""Base replies client."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from threads._base.client import BaseSubClient, BaseThreadsClient


class BaseRepliesClient(BaseSubClient, ABC):
    """Abstract base class for reply management operations.

    Handles retrieving, hiding, and managing replies to posts.
    """

    # Default fields for reply retrieval
    DEFAULT_REPLY_FIELDS: ClassVar[list[str]] = [
        "id",
        "text",
        "username",
        "permalink",
        "timestamp",
        "media_type",
        "media_url",
        "hide_status",
        "has_replies",
    ]

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    @abstractmethod
    def get_replies(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        reverse: bool = False,
    ) -> Any:
        """Get replies to a post.

        Args:
            post_id: The post ID to get replies for.
            fields: Fields to retrieve for each reply.
            reverse: If True, return oldest first.

        Returns:
            List of Reply objects.
        """
        ...

    @abstractmethod
    def get_conversation(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        reverse: bool = False,
    ) -> Any:
        """Get the full conversation thread for a post.

        Args:
            post_id: The post ID (can be a reply).
            fields: Fields to retrieve.
            reverse: If True, return oldest first.

        Returns:
            List of Reply objects in the conversation.
        """
        ...

    @abstractmethod
    def hide(self, reply_id: str) -> Any:
        """Hide a reply.

        Args:
            reply_id: The reply ID to hide.

        Returns:
            True if successful.
        """
        ...

    @abstractmethod
    def unhide(self, reply_id: str) -> Any:
        """Unhide a previously hidden reply.

        Args:
            reply_id: The reply ID to unhide.

        Returns:
            True if successful.
        """
        ...

    @abstractmethod
    def get_user_replies(
        self,
        user_id: str,
        *,
        fields: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """Get replies made by a user.

        Args:
            user_id: The Threads user ID.
            fields: Fields to retrieve.
            since: Unix timestamp or strtotime for start.
            until: Unix timestamp or strtotime for end.
            limit: Maximum number of replies to return.

        Returns:
            List of Reply objects.
        """
        ...
