"""Synchronous users client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.users import BaseUsersClient
from threads._utils.logger import get_logger
from threads.exceptions import raise_for_error
from threads.models.user import UserProfile

if TYPE_CHECKING:
    from threads._sync.client import ThreadsClient

logger = get_logger("users")


class UsersClient(BaseUsersClient):
    """Synchronous client for user profile operations."""

    def __init__(self, parent: ThreadsClient) -> None:
        super().__init__(parent)
        self._parent: ThreadsClient = parent

    def get_me(
        self,
        fields: list[str] | None = None,
    ) -> UserProfile:
        """Get the authenticated user's profile.

        Args:
            fields: Fields to retrieve. If None, uses DEFAULT_PROFILE_FIELDS.

        Returns:
            UserProfile with the requested fields.
        """
        if fields is None:
            fields = self.DEFAULT_PROFILE_FIELDS

        logger.debug(f"Getting authenticated user profile with fields: {fields}")

        params = self._get_params(fields=",".join(fields))

        response = self._parent.http.get(
            "/me",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to get user profile: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info(f"Successfully retrieved profile for user {data.get('id')}")
        return UserProfile.model_validate(data)

    def get(
        self,
        user_id: str,
        fields: list[str] | None = None,
    ) -> UserProfile:
        """Get a user's profile by ID.

        Args:
            user_id: The Threads user ID.
            fields: Fields to retrieve. If None, uses DEFAULT_PROFILE_FIELDS.

        Returns:
            UserProfile with the requested fields.
        """
        if fields is None:
            fields = self.DEFAULT_PROFILE_FIELDS

        logger.debug(f"Getting user profile {user_id} with fields: {fields}")

        params = self._get_params(fields=",".join(fields))

        response = self._parent.http.get(
            f"/{user_id}",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to get user profile: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info(f"Successfully retrieved profile for user {user_id}")
        return UserProfile.model_validate(data)
