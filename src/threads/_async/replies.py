"""Asynchronous replies client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.replies import BaseRepliesClient
from threads.exceptions import raise_for_error
from threads.models.post import Reply

if TYPE_CHECKING:
    from threads._async.client import AsyncThreadsClient


class AsyncRepliesClient(BaseRepliesClient):
    """Asynchronous client for reply management operations."""

    def __init__(self, parent: AsyncThreadsClient) -> None:
        super().__init__(parent)
        self._parent: AsyncThreadsClient = parent

    async def get_replies(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        reverse: bool = False,
    ) -> list[Reply]:
        """Get replies to a post.

        Args:
            post_id: The post ID to get replies for.
            fields: Fields to retrieve for each reply.
            reverse: If True, return oldest first.

        Returns:
            List of Reply objects.
        """
        if fields is None:
            fields = self.DEFAULT_REPLY_FIELDS

        params = self._get_params(
            fields=",".join(fields),
            reverse=reverse if reverse else None,
        )

        response = await self._parent.http.get(
            f"/{post_id}/replies",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return [Reply.model_validate(item) for item in data.get("data", [])]

    async def get_conversation(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        reverse: bool = False,
    ) -> list[Reply]:
        """Get the full conversation thread for a post.

        Args:
            post_id: The post ID (can be a reply).
            fields: Fields to retrieve.
            reverse: If True, return oldest first.

        Returns:
            List of Reply objects in the conversation.
        """
        if fields is None:
            fields = self.DEFAULT_REPLY_FIELDS

        params = self._get_params(
            fields=",".join(fields),
            reverse=reverse if reverse else None,
        )

        response = await self._parent.http.get(
            f"/{post_id}/conversation",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return [Reply.model_validate(item) for item in data.get("data", [])]

    async def hide(self, reply_id: str) -> bool:
        """Hide a reply.

        Args:
            reply_id: The reply ID to hide.

        Returns:
            True if successful.
        """
        params = self._get_params(hide=True)

        response = await self._parent.http.post(
            f"/{reply_id}/manage_reply",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return bool(data.get("success", False))

    async def unhide(self, reply_id: str) -> bool:
        """Unhide a previously hidden reply.

        Args:
            reply_id: The reply ID to unhide.

        Returns:
            True if successful.
        """
        params = self._get_params(hide=False)

        response = await self._parent.http.post(
            f"/{reply_id}/manage_reply",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return bool(data.get("success", False))

    async def get_user_replies(
        self,
        user_id: str,
        *,
        fields: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
    ) -> list[Reply]:
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
        if fields is None:
            fields = self.DEFAULT_REPLY_FIELDS

        params = self._get_params(
            fields=",".join(fields),
            since=since,
            until=until,
            limit=limit,
        )

        response = await self._parent.http.get(
            f"/{user_id}/replies",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return [Reply.model_validate(item) for item in data.get("data", [])]
