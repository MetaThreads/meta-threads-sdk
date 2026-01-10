"""Type definitions and protocols for the Threads SDK."""

from typing import Any, Protocol, runtime_checkable

# Type aliases
type JSON = dict[str, Any]
type Headers = dict[str, str]
type QueryParams = dict[str, str | int | bool | None]


@runtime_checkable
class SupportsClose(Protocol):
    """Protocol for objects that support closing."""

    def close(self) -> None: ...


@runtime_checkable
class SupportsAsyncClose(Protocol):
    """Protocol for objects that support async closing."""

    async def aclose(self) -> None: ...


@runtime_checkable
class HTTPClient(Protocol):
    """Protocol for synchronous HTTP clients."""

    def get(
        self,
        url: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    def post(
        self,
        url: str,
        *,
        data: JSON | None = None,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    def delete(
        self,
        url: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    def close(self) -> None: ...


@runtime_checkable
class AsyncHTTPClient(Protocol):
    """Protocol for asynchronous HTTP clients."""

    async def get(
        self,
        url: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    async def post(
        self,
        url: str,
        *,
        data: JSON | None = None,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    async def delete(
        self,
        url: str,
        *,
        params: QueryParams | None = None,
        headers: Headers | None = None,
    ) -> Any: ...

    async def aclose(self) -> None: ...
