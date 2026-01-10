"""Base client class for the Threads SDK."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from threads.constants import (
    API_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)

T = TypeVar("T")


class BaseThreadsClient[T](ABC):
    """Abstract base class for Threads API clients.

    This class defines the interface and shared configuration for both
    synchronous and asynchronous clients.

    Type Parameters:
        T: The HTTP client type (httpx.Client or httpx.AsyncClient).
    """

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the Threads client.

        Args:
            access_token: OAuth access token for authentication.
            base_url: Base URL for API requests.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        self._access_token = access_token
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._http_client: T | None = None

    @property
    def access_token(self) -> str:
        """Get the current access token."""
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        """Update the access token."""
        self._access_token = value

    @property
    @abstractmethod
    def auth(self) -> Any:
        """Get the authentication client."""
        ...

    @property
    @abstractmethod
    def media(self) -> Any:
        """Get the media client."""
        ...

    @property
    @abstractmethod
    def posts(self) -> Any:
        """Get the posts client."""
        ...

    @property
    @abstractmethod
    def insights(self) -> Any:
        """Get the insights client."""
        ...

    @property
    @abstractmethod
    def replies(self) -> Any:
        """Get the replies client."""
        ...

    @property
    @abstractmethod
    def webhooks(self) -> Any:
        """Get the webhooks client."""
        ...

    @abstractmethod
    def _get_default_params(self) -> dict[str, str]:
        """Get default request parameters including access token."""
        ...

    @abstractmethod
    def _build_url(self, endpoint: str, **path_params: str) -> str:
        """Build a full API URL."""
        ...


class BaseSubClient:
    """Base class for sub-clients (auth, media, posts, etc.).

    Sub-clients handle specific API domains while sharing the parent
    client's HTTP client and configuration.
    """

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        """Initialize the sub-client.

        Args:
            parent: The parent ThreadsClient instance.
        """
        self._parent = parent

    @property
    def _access_token(self) -> str:
        """Get access token from parent."""
        return self._parent.access_token

    def _get_params(self, **extra: Any) -> dict[str, Any]:
        """Build request parameters with access token.

        Args:
            **extra: Additional parameters to include.

        Returns:
            Dictionary with access_token and any extra parameters.
        """
        params: dict[str, Any] = {"access_token": self._access_token}
        params.update({k: v for k, v in extra.items() if v is not None})
        return params

    def _build_fields_param(self, fields: list[str] | None) -> str | None:
        """Build comma-separated fields parameter.

        Args:
            fields: List of field names to request.

        Returns:
            Comma-separated string or None.
        """
        return ",".join(fields) if fields else None
