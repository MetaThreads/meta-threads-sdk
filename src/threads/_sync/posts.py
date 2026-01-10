"""Synchronous posts client."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from threads._base.posts import BasePostsClient
from threads._utils.logger import get_logger
from threads.constants import ContainerStatus, ReplyControl
from threads.exceptions import ContainerError, raise_for_error
from threads.models.post import Post, PublishingLimit

if TYPE_CHECKING:
    from threads._sync.client import ThreadsClient
    from threads.models.media import MediaContainerStatus

logger = get_logger("posts")


class PostsClient(BasePostsClient):
    """Synchronous client for post operations."""

    def __init__(self, parent: ThreadsClient) -> None:
        super().__init__(parent)
        self._parent: ThreadsClient = parent

    def publish(
        self,
        user_id: str,
        container_id: str,
        *,
        fetch_post: bool = True,
    ) -> Post:
        """Publish a media container as a post.

        Args:
            user_id: The Threads user ID.
            container_id: The container ID to publish.
            fetch_post: Whether to fetch full post details after publishing.
                Set to False if you only need the post ID.

        Returns:
            Post with the published post data.
        """
        logger.debug(f"Publishing container {container_id} for user {user_id}")
        params = self._get_params(creation_id=container_id)

        response = self._parent.http.post(
            f"/{user_id}/threads_publish",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to publish container: status={response.status_code}")
            raise_for_error(data, response.status_code)

        post_id = data["id"]
        logger.info(f"Successfully published post {post_id}")

        if not fetch_post:
            # Return minimal Post object with just the ID
            return Post(id=post_id, media_type="TEXT_POST")

        try:
            return self.get(post_id)
        except Exception as e:
            logger.warning(f"Could not fetch post details: {e}")
            # Return minimal Post object if fetch fails
            return Post(id=post_id, media_type="TEXT_POST")

    def create_and_publish(
        self,
        user_id: str,
        *,
        text: str | None = None,
        image_url: str | None = None,
        video_url: str | None = None,
        reply_to_id: str | None = None,
        reply_control: ReplyControl | None = None,
        wait_for_ready: bool = True,
        poll_interval: float = 1.0,
        max_wait_time: float = 60.0,
    ) -> Post:
        """Create a container and publish it in one call.

        Args:
            user_id: The Threads user ID.
            text: Text content for the post.
            image_url: Public URL of an image.
            video_url: Public URL of a video.
            reply_to_id: Post ID to reply to.
            reply_control: Who can reply.
            wait_for_ready: Wait for video processing to complete.
            poll_interval: Seconds between status checks.
            max_wait_time: Maximum seconds to wait for processing.

        Returns:
            Post with the published post data.
        """
        logger.debug(f"Creating and publishing post for user {user_id}")
        self._validate_publish_params(text, image_url, video_url)
        media_type = self._determine_media_type(text, image_url, video_url)
        logger.debug(f"Determined media_type={media_type}")

        container = self._parent.media.create_container(
            user_id,
            media_type,
            text=text,
            image_url=image_url,
            video_url=video_url,
            reply_to_id=reply_to_id,
            reply_control=reply_control,
        )

        if wait_for_ready and video_url:
            logger.debug(f"Waiting for video container {container.id} to be ready")
            self._wait_for_container(
                container.id,
                poll_interval=poll_interval,
                max_wait_time=max_wait_time,
            )

        return self.publish(user_id, container.id)

    def _wait_for_container(
        self,
        container_id: str,
        poll_interval: float = 1.0,
        max_wait_time: float = 60.0,
    ) -> MediaContainerStatus:
        """Wait for a container to be ready for publishing.

        Args:
            container_id: The container ID to check.
            poll_interval: Seconds between status checks.
            max_wait_time: Maximum seconds to wait.

        Returns:
            MediaContainerStatus when ready.

        Raises:
            ContainerError: If container fails or times out.
        """
        start_time = time.time()
        logger.debug(f"Starting to poll container {container_id} status")

        while True:
            status = self._parent.media.get_container_status(container_id)
            logger.debug(f"Container {container_id} status: {status.status}")

            if status.is_ready:
                logger.info(f"Container {container_id} is ready for publishing")
                return status

            if status.has_error:
                logger.error(f"Container {container_id} failed: {status.error_message}")
                raise ContainerError(
                    f"Container processing failed: {status.error_message}",
                    error_code=None,
                )

            if status.status == ContainerStatus.EXPIRED:
                logger.error(f"Container {container_id} expired before publishing")
                raise ContainerError("Container expired before publishing")

            elapsed = time.time() - start_time
            if elapsed >= max_wait_time:
                logger.error(f"Container {container_id} timed out after {max_wait_time}s")
                raise ContainerError(
                    f"Container not ready after {max_wait_time}s "
                    f"(status: {status.status})"
                )

            time.sleep(poll_interval)

    def get(
        self,
        post_id: str,
        fields: list[str] | None = None,
    ) -> Post:
        """Get a post by ID.

        Args:
            post_id: The post ID.
            fields: Fields to retrieve.

        Returns:
            Post with requested fields.
        """
        if fields is None:
            fields = self.DEFAULT_POST_FIELDS

        params = self._get_params(fields=",".join(fields))

        response = self._parent.http.get(
            f"/{post_id}",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return Post.model_validate(data)

    def get_user_posts(
        self,
        user_id: str,
        *,
        fields: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
    ) -> list[Post]:
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
        if fields is None:
            fields = self.DEFAULT_POST_FIELDS

        params = self._get_params(
            fields=",".join(fields),
            since=since,
            until=until,
            limit=limit,
        )

        response = self._parent.http.get(
            f"/{user_id}/threads",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return [Post.model_validate(item) for item in data.get("data", [])]

    def delete(self, post_id: str) -> bool:
        """Delete a post.

        Args:
            post_id: The post ID to delete.

        Returns:
            True if successfully deleted.
        """
        logger.debug(f"Deleting post {post_id}")
        params = self._get_params()

        response = self._parent.http.delete(
            f"/{post_id}",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to delete post: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info(f"Successfully deleted post {post_id}")
        return data.get("success", True)

    def get_publishing_limit(self, user_id: str) -> PublishingLimit:
        """Get the user's publishing rate limit status.

        Args:
            user_id: The Threads user ID.

        Returns:
            PublishingLimit with quota information.
        """
        params = self._get_params(fields="quota_usage,config")

        response = self._parent.http.get(
            f"/{user_id}/threads_publishing_limit",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        limit_data = data.get("data", [{}])[0] if data.get("data") else {}
        config = limit_data.get("config", {})

        return PublishingLimit(
            quota_usage=limit_data.get("quota_usage", 0),
            quota_total=config.get("quota_total", 250),
            reply_quota_usage=limit_data.get("reply_quota_usage"),
            reply_quota_total=config.get("reply_quota_total"),
        )
