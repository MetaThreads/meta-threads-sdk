"""Asynchronous Threads API client."""

from __future__ import annotations

from typing import Self

import httpx

from threads._async.auth import AsyncAuthClient
from threads._async.insights import AsyncInsightsClient
from threads._async.media import AsyncMediaClient
from threads._async.posts import AsyncPostsClient
from threads._async.replies import AsyncRepliesClient
from threads._async.users import AsyncUsersClient
from threads._async.webhooks import AsyncWebhooksClient
from threads._base.client import BaseThreadsClient
from threads._utils.http import build_url
from threads._utils.logger import get_logger
from threads.constants import (
    API_BASE_URL,
    API_VERSION,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)

logger = get_logger("async_client")


class AsyncThreadsClient(BaseThreadsClient[httpx.AsyncClient]):
    """Asynchronous client for the Threads API.

    Example:
        ```python
        from threads import AsyncThreadsClient

        async with AsyncThreadsClient(access_token="your_token") as client:
            post = await client.posts.create_and_publish(
                user_id="your_user_id",
                text="Hello from Threads SDK!",
            )
            print(f"Published: {post.permalink}")
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
        """Initialize the asynchronous Threads client.

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
            f"Initializing AsyncThreadsClient with base_url={base_url}, timeout={timeout}, max_retries={max_retries}"
        )

        transport = httpx.AsyncHTTPTransport(retries=max_retries)
        self._http_client = httpx.AsyncClient(
            base_url=f"{base_url}/{API_VERSION}",
            timeout=timeout,
            transport=transport,
        )

        self._auth = AsyncAuthClient(self)
        self._media = AsyncMediaClient(self)
        self._posts = AsyncPostsClient(self)
        self._insights = AsyncInsightsClient(self)
        self._replies = AsyncRepliesClient(self)
        self._users = AsyncUsersClient(self)
        self._webhooks = AsyncWebhooksClient(self)

        logger.info("AsyncThreadsClient initialized successfully")

    @property
    def http(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._http_client is None:
            raise RuntimeError("Client has been closed")
        return self._http_client

    @property
    def auth(self) -> AsyncAuthClient:
        """Get the authentication client."""
        return self._auth

    @property
    def media(self) -> AsyncMediaClient:
        """Get the media client."""
        return self._media

    @property
    def posts(self) -> AsyncPostsClient:
        """Get the posts client."""
        return self._posts

    @property
    def insights(self) -> AsyncInsightsClient:
        """Get the insights client."""
        return self._insights

    @property
    def replies(self) -> AsyncRepliesClient:
        """Get the replies client."""
        return self._replies

    @property
    def webhooks(self) -> AsyncWebhooksClient:
        """Get the webhooks client."""
        return self._webhooks

    @property
    def users(self) -> AsyncUsersClient:
        """Get the users client."""
        return self._users

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

    async def aclose(self) -> None:
        """Close the HTTP client and release resources."""
        if self._http_client is not None:
            logger.debug("Closing AsyncThreadsClient HTTP connection")
            await self._http_client.aclose()
            self._http_client = None
            logger.info("AsyncThreadsClient closed")

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.aclose()
