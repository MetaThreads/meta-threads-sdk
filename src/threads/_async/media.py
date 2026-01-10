"""Asynchronous media client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.media import BaseMediaClient
from threads._utils.logger import get_logger
from threads.constants import MediaType, ReplyControl
from threads.exceptions import raise_for_error
from threads.models.media import MediaContainer, MediaContainerStatus

if TYPE_CHECKING:
    from threads._async.client import AsyncThreadsClient

logger = get_logger("media")


class AsyncMediaClient(BaseMediaClient):
    """Asynchronous client for media container operations."""

    def __init__(self, parent: AsyncThreadsClient) -> None:
        super().__init__(parent)
        self._parent: AsyncThreadsClient = parent

    async def create_container(
        self,
        user_id: str,
        media_type: MediaType,
        *,
        text: str | None = None,
        image_url: str | None = None,
        video_url: str | None = None,
        is_carousel_item: bool = False,
        children: list[str] | None = None,
        reply_to_id: str | None = None,
        reply_control: ReplyControl | None = None,
    ) -> MediaContainer:
        """Create a media container.

        Args:
            user_id: The Threads user ID.
            media_type: Type of media to create.
            text: Text content for the post.
            image_url: Public URL of the image.
            video_url: Public URL of the video.
            is_carousel_item: Whether this is a carousel item.
            children: Container IDs for carousel items.
            reply_to_id: Post ID to reply to.
            reply_control: Who can reply.

        Returns:
            MediaContainer with the container ID.
        """
        logger.debug(f"Creating {media_type} container for user {user_id}")
        params = self._validate_and_build_params(
            user_id,
            media_type,
            text=text,
            image_url=image_url,
            video_url=video_url,
            is_carousel_item=is_carousel_item,
            children=children,
            reply_to_id=reply_to_id,
            reply_control=reply_control,
        )

        response = await self._parent.http.post(
            f"/{user_id}/threads",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to create container: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info(f"Created container {data['id']}")
        return MediaContainer(id=data["id"])

    async def get_container_status(self, container_id: str) -> MediaContainerStatus:
        """Get the status of a media container.

        Args:
            container_id: The container ID to check.

        Returns:
            MediaContainerStatus with current status.
        """
        logger.debug(f"Getting status for container {container_id}")
        params = self._get_params(fields="id,status,error_message")

        response = await self._parent.http.get(
            f"/{container_id}",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(
                f"Failed to get container status: status={response.status_code}"
            )
            raise_for_error(data, response.status_code)

        status = MediaContainerStatus.model_validate(data)
        logger.debug(f"Container {container_id} status: {status.status}")
        return status

    async def create_image_container(
        self,
        user_id: str,
        image_url: str,
        *,
        text: str | None = None,
        is_carousel_item: bool = False,
    ) -> MediaContainer:
        """Convenience method to create an image container.

        Args:
            user_id: The Threads user ID.
            image_url: Public URL of the image.
            text: Optional text caption.
            is_carousel_item: Whether this is a carousel item.

        Returns:
            MediaContainer with the container ID.
        """
        return await self.create_container(
            user_id,
            MediaType.IMAGE,
            text=text,
            image_url=image_url,
            is_carousel_item=is_carousel_item,
        )

    async def create_video_container(
        self,
        user_id: str,
        video_url: str,
        *,
        text: str | None = None,
        is_carousel_item: bool = False,
    ) -> MediaContainer:
        """Convenience method to create a video container.

        Args:
            user_id: The Threads user ID.
            video_url: Public URL of the video.
            text: Optional text caption.
            is_carousel_item: Whether this is a carousel item.

        Returns:
            MediaContainer with the container ID.
        """
        return await self.create_container(
            user_id,
            MediaType.VIDEO,
            text=text,
            video_url=video_url,
            is_carousel_item=is_carousel_item,
        )

    async def create_carousel_container(
        self,
        user_id: str,
        children: list[str],
        *,
        text: str | None = None,
    ) -> MediaContainer:
        """Create a carousel container from existing media containers.

        Args:
            user_id: The Threads user ID.
            children: List of media container IDs.
            text: Optional text caption.

        Returns:
            MediaContainer for the carousel.
        """
        return await self.create_container(
            user_id,
            MediaType.CAROUSEL,
            text=text,
            children=children,
        )
