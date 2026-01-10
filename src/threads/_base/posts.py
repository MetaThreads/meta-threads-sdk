"""Base posts client."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from threads._base.client import BaseSubClient, BaseThreadsClient
from threads._utils.validators import validate_text_length
from threads.constants import MediaType, ReplyControl


class BasePostsClient(BaseSubClient, ABC):
    """Abstract base class for post operations.

    Handles publishing posts and retrieving post data.
    """

    # Default fields to retrieve for posts
    DEFAULT_POST_FIELDS: ClassVar[list[str]] = [
        "id",
        "media_product_type",
        "media_type",
        "media_url",
        "permalink",
        "owner",
        "username",
        "text",
        "timestamp",
        "shortcode",
        "thumbnail_url",
        "children",
        "is_quote_post",
        "has_replies",
        "reply_audience",
    ]

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    @abstractmethod
    def publish(
        self,
        user_id: str,
        container_id: str,
    ) -> Any:
        """Publish a media container as a post.

        Args:
            user_id: The Threads user ID.
            container_id: The container ID to publish.

        Returns:
            Post with the published post data.
        """
        ...

    @abstractmethod
    def create_and_publish(
        self,
        user_id: str,
        *,
        text: str | None = None,
        image_url: str | None = None,
        video_url: str | None = None,
        reply_to_id: str | None = None,
        reply_control: ReplyControl | None = None,
    ) -> Any:
        """Create a container and publish it in one call.

        This is a convenience method that handles the two-step
        publish process automatically.

        Args:
            user_id: The Threads user ID.
            text: Text content for the post.
            image_url: Public URL of an image.
            video_url: Public URL of a video.
            reply_to_id: Post ID to reply to.
            reply_control: Who can reply.

        Returns:
            Post with the published post data.
        """
        ...

    @abstractmethod
    def get(
        self,
        post_id: str,
        fields: list[str] | None = None,
    ) -> Any:
        """Get a post by ID.

        Args:
            post_id: The post ID.
            fields: Fields to retrieve.

        Returns:
            Post with requested fields.
        """
        ...

    @abstractmethod
    def get_user_posts(
        self,
        user_id: str,
        *,
        fields: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """Get posts for a user.

        Args:
            user_id: The Threads user ID.
            fields: Fields to retrieve.
            since: Unix timestamp or strtotime for start.
            until: Unix timestamp or strtotime for end.
            limit: Maximum number of posts to return.

        Returns:
            List of Post objects.
        """
        ...

    @abstractmethod
    def get_publishing_limit(self, user_id: str) -> Any:
        """Get the user's publishing rate limit status.

        Args:
            user_id: The Threads user ID.

        Returns:
            PublishingLimit with quota information.
        """
        ...

    def _determine_media_type(
        self,
        text: str | None,
        image_url: str | None,
        video_url: str | None,
    ) -> MediaType:
        """Determine the media type based on provided content.

        Args:
            text: Text content.
            image_url: Image URL.
            video_url: Video URL.

        Returns:
            The appropriate MediaType.
        """
        if video_url:
            return MediaType.VIDEO
        if image_url:
            return MediaType.IMAGE
        return MediaType.TEXT

    def _validate_publish_params(
        self,
        text: str | None,
        image_url: str | None,
        video_url: str | None,
    ) -> None:
        """Validate publish parameters."""
        validate_text_length(text)

        if not any([text, image_url, video_url]):
            from threads.exceptions import ValidationError

            raise ValidationError(
                "At least one of text, image_url, or video_url is required"
            )
