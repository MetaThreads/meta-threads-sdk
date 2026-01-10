"""HTTP utilities for the Threads SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode, urljoin

from threads.constants import API_BASE_URL, API_VERSION
from threads.exceptions import raise_for_error

if TYPE_CHECKING:
    from threads.types import JSON, QueryParams


def build_url(
    endpoint: str,
    path_params: dict[str, str] | None = None,
    query_params: QueryParams | None = None,
    base_url: str = API_BASE_URL,
    version: str = API_VERSION,
) -> str:
    """Build a full API URL with path and query parameters.

    Args:
        endpoint: The API endpoint path (e.g., "{user_id}/threads").
        path_params: Parameters to substitute in the endpoint path.
        query_params: Query string parameters.
        base_url: Base URL for the API.
        version: API version string.

    Returns:
        The fully constructed URL.
    """
    if path_params:
        endpoint = endpoint.format(**path_params)

    url = urljoin(f"{base_url}/{version}/", endpoint.lstrip("/"))

    if query_params:
        filtered_params = {k: v for k, v in query_params.items() if v is not None}
        if filtered_params:
            query_string = urlencode(filtered_params, doseq=True)
            url = f"{url}?{query_string}"

    return url


def parse_error_response(response_data: JSON, status_code: int) -> None:
    """Parse API response and raise exception if error present.

    Args:
        response_data: The JSON response body.
        status_code: HTTP status code.

    Raises:
        ThreadsAPIError: If the response contains an error.
    """
    if "error" in response_data:
        raise_for_error(response_data, status_code)


def extract_id(response: JSON) -> str:
    """Extract the ID from an API response.

    Args:
        response: The JSON response containing an 'id' field.

    Returns:
        The extracted ID string.

    Raises:
        KeyError: If 'id' is not in the response.
    """
    return str(response["id"])


def prepare_request_params(
    access_token: str,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare common request parameters.

    Args:
        access_token: The OAuth access token.
        extra_params: Additional parameters to include.

    Returns:
        Dictionary of request parameters.
    """
    params: dict[str, Any] = {"access_token": access_token}
    if extra_params:
        params.update({k: v for k, v in extra_params.items() if v is not None})
    return params
