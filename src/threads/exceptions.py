"""Exception hierarchy for the Threads API SDK."""

from typing import Any

from threads._utils.logger import get_logger

logger = get_logger("exceptions")


class ThreadsError(Exception):
    """Base exception for all Threads SDK errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        self.message = message
        self.details = kwargs
        super().__init__(message)


class ThreadsAPIError(ThreadsError):
    """Base exception for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: int | None = None,
        error_subcode: int | None = None,
        fbtrace_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.error_subcode = error_subcode
        self.fbtrace_id = fbtrace_id
        super().__init__(message, **kwargs)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"status_code={self.status_code}")
        if self.error_code:
            parts.append(f"error_code={self.error_code}")
        if self.fbtrace_id:
            parts.append(f"fbtrace_id={self.fbtrace_id}")
        return " | ".join(parts)


class AuthenticationError(ThreadsAPIError):
    """Raised when authentication fails or token is invalid."""


class AuthorizationError(ThreadsAPIError):
    """Raised when the user lacks permission for the requested action."""


class RateLimitError(ThreadsAPIError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class NotFoundError(ThreadsAPIError):
    """Raised when a requested resource is not found."""


class ValidationError(ThreadsError):
    """Raised when input validation fails."""


class MediaError(ThreadsAPIError):
    """Raised when media processing fails."""


class ContainerError(ThreadsAPIError):
    """Raised when media container creation or publishing fails."""


class WebhookError(ThreadsAPIError):
    """Raised when webhook operations fail."""


class NetworkError(ThreadsError):
    """Raised when network-related errors occur."""


class TimeoutError(NetworkError):
    """Raised when a request times out."""


def raise_for_error(response_data: dict[str, Any], status_code: int) -> None:
    """Parse API error response and raise appropriate exception.

    Args:
        response_data: The JSON response from the API.
        status_code: HTTP status code of the response.

    Raises:
        ThreadsAPIError: The appropriate exception based on the error.
    """
    error = response_data.get("error", {})
    message = error.get("message", "Unknown error")
    error_code = error.get("code")
    error_subcode = error.get("error_subcode")
    fbtrace_id = error.get("fbtrace_id")

    common_kwargs = {
        "status_code": status_code,
        "error_code": error_code,
        "error_subcode": error_subcode,
        "fbtrace_id": fbtrace_id,
    }

    logger.debug(
        f"API error: status={status_code}, code={error_code}, subcode={error_subcode}, message={message}"
    )

    if status_code == 401 or error_code in (190, 102):
        logger.warning(f"Authentication error: {message}")
        raise AuthenticationError(message, **common_kwargs)
    if status_code == 403 or error_code in (10, 200, 294):
        logger.warning(f"Authorization error: {message}")
        raise AuthorizationError(message, **common_kwargs)
    if status_code == 429 or error_code in (4, 17, 32, 613):
        logger.warning(f"Rate limit exceeded: {message}")
        raise RateLimitError(message, **common_kwargs)
    if status_code == 404:
        logger.warning(f"Resource not found: {message}")
        raise NotFoundError(message, **common_kwargs)

    logger.error(f"API error: {message}")
    raise ThreadsAPIError(message, **common_kwargs)
