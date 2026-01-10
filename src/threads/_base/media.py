"""Base media client."""

from abc import ABC, abstractmethod
from typing import Any

from threads._base.client import BaseSubClient, BaseThreadsClient
from threads._utils.validators import (
    validate_carousel_items,
    validate_media_url,
    validate_reply_control,
    validate_text_length,
)
from threads.constants import MediaType, ReplyControl


class BaseMediaClient(BaseSubClient, ABC):
    """Abstract base class for media container operations.

    Handles creating media containers for images, videos, and carousels.
    """

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    def _validate_and_build_params(
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
    ) -> dict[str, Any]:
        """Validate inputs and build container creation parameters.

        Args:
            user_id: The Threads user ID.
            media_type: Type of media (TEXT, IMAGE, VIDEO, CAROUSEL).
            text: Text content for the post.
            image_url: Public URL of the image.
            video_url: Public URL of the video.
            is_carousel_item: Whether this is a carousel item.
            children: Container IDs for carousel items.
            reply_to_id: Post ID to reply to.
            reply_control: Who can reply to the post.

        Returns:
            Dictionary of validated parameters.
        """
        validate_text_length(text)

        if reply_control:
            validate_reply_control(reply_control.value)

        if media_type == MediaType.IMAGE:
            validate_media_url(image_url, MediaType.IMAGE)
        elif media_type == MediaType.VIDEO:
            validate_media_url(video_url, MediaType.VIDEO)
        elif media_type == MediaType.CAROUSEL and children:
            validate_carousel_items(children)

        params = self._get_params(
            media_type=media_type.value,
            text=text,
            image_url=image_url,
            video_url=video_url,
            is_carousel_item=is_carousel_item if is_carousel_item else None,
            reply_to_id=reply_to_id,
            reply_control=reply_control.value if reply_control else None,
        )

        if children:
            params["children"] = ",".join(children)

        return params

    @abstractmethod
    def create_container(
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
    ) -> Any:
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
        ...

    @abstractmethod
    def get_container_status(self, container_id: str) -> Any:
        """Get the status of a media container.

        Args:
            container_id: The container ID to check.

        Returns:
            MediaContainerStatus with current status.
        """
        ...
