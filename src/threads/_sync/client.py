"""Synchronous Threads API client."""

from __future__ import annotations

from typing import Self

import httpx

from threads._base.client import BaseThreadsClient
from threads._sync.auth import AuthClient
from threads._sync.insights import InsightsClient
from threads._sync.media import MediaClient
from threads._sync.posts import PostsClient
from threads._sync.replies import RepliesClient
from threads._sync.webhooks import WebhooksClient
from threads._utils.http import build_url
from threads._utils.logger import get_logger
from threads.constants import (
    API_BASE_URL,
    API_VERSION,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)

logger = get_logger("client")


class ThreadsClient(BaseThreadsClient[httpx.Client]):
    """Synchronous client for the Threads API.

    Example:
        ```python
        from threads import ThreadsClient

        client = ThreadsClient(access_token="your_token")
        post = client.posts.create_and_publish(
            user_id="your_user_id",
            text="Hello from Threads SDK!",
        )
        print(f"Published: {post.permalink}")
        client.close()
        ```

    Or using context manager:
        ```python
        with ThreadsClient(access_token="your_token") as client:
            post = client.posts.create_and_publish(
                user_id="your_user_id",
                text="Hello from Threads SDK!",
            )
        ```
    """

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the synchronous Threads client.

        Args:
            access_token: OAuth access token for authentication.
            base_url: Base URL for API requests.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for failed requests.
        """
        super().__init__(
            access_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        logger.debug(
            f"Initializing ThreadsClient with base_url={base_url}, timeout={timeout}, max_retries={max_retries}"
        )

        transport = httpx.HTTPTransport(retries=max_retries)
        self._http_client = httpx.Client(
            base_url=f"{base_url}/{API_VERSION}",
            timeout=timeout,
            transport=transport,
        )

        self._auth = AuthClient(self)
        self._media = MediaClient(self)
        self._posts = PostsClient(self)
        self._insights = InsightsClient(self)
        self._replies = RepliesClient(self)
        self._webhooks = WebhooksClient(self)

        logger.info("ThreadsClient initialized successfully")

    @property
    def http(self) -> httpx.Client:
        """Get the HTTP client."""
        if self._http_client is None:
            raise RuntimeError("Client has been closed")
        return self._http_client

    @property
    def auth(self) -> AuthClient:
        """Get the authentication client."""
        return self._auth

    @property
    def media(self) -> MediaClient:
        """Get the media client."""
        return self._media

    @property
    def posts(self) -> PostsClient:
        """Get the posts client."""
        return self._posts

    @property
    def insights(self) -> InsightsClient:
        """Get the insights client."""
        return self._insights

    @property
    def replies(self) -> RepliesClient:
        """Get the replies client."""
        return self._replies

    @property
    def webhooks(self) -> WebhooksClient:
        """Get the webhooks client."""
        return self._webhooks

    def _get_default_params(self) -> dict[str, str]:
        """Get default request parameters."""
        return {"access_token": self._access_token}

    def _build_url(self, endpoint: str, **path_params: str) -> str:
        """Build a full API URL."""
        return build_url(
            endpoint,
            path_params=path_params if path_params else None,
            base_url=self._base_url,
        )

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._http_client is not None:
            logger.debug("Closing ThreadsClient HTTP connection")
            self._http_client.close()
            self._http_client = None
            logger.info("ThreadsClient closed")

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()
