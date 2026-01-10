"""Base authentication client."""

from abc import ABC, abstractmethod
from typing import Any

from threads._base.client import BaseSubClient, BaseThreadsClient
from threads.constants import OAUTH_BASE_URL, Scope


class BaseAuthClient(BaseSubClient, ABC):
    """Abstract base class for authentication operations.

    Handles OAuth 2.0 flow, token exchange, and token refresh.
    """

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)
        self._oauth_base_url = OAUTH_BASE_URL

    def get_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: list[Scope] | None = None,
        state: str | None = None,
    ) -> str:
        """Generate the OAuth authorization URL.

        Args:
            client_id: Your app's client ID.
            redirect_uri: URL to redirect after authorization.
            scopes: List of OAuth scopes to request.
            state: Optional state parameter for CSRF protection.

        Returns:
            The authorization URL to redirect the user to.
        """
        if scopes is None:
            scopes = [Scope.BASIC, Scope.CONTENT_PUBLISH]

        scope_str = ",".join(scopes)

        params = [
            f"client_id={client_id}",
            f"redirect_uri={redirect_uri}",
            f"scope={scope_str}",
            "response_type=code",
        ]

        if state:
            params.append(f"state={state}")

        return f"{self._oauth_base_url}/authorize?{'&'.join(params)}"

    @abstractmethod
    def exchange_code(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code: str,
    ) -> Any:
        """Exchange authorization code for short-lived access token.

        Args:
            client_id: Your app's client ID.
            client_secret: Your app's client secret.
            redirect_uri: The redirect URI used in authorization.
            code: The authorization code from the callback.

        Returns:
            ShortLivedToken with the access token and user ID.
        """
        ...

    @abstractmethod
    def get_long_lived_token(
        self,
        client_secret: str,
        short_lived_token: str,
    ) -> Any:
        """Exchange short-lived token for long-lived token.

        Args:
            client_secret: Your app's client secret.
            short_lived_token: The short-lived access token.

        Returns:
            LongLivedToken valid for 60 days.
        """
        ...

    @abstractmethod
    def refresh_token(self, access_token: str) -> Any:
        """Refresh a long-lived token.

        Args:
            access_token: The current long-lived access token.

        Returns:
            RefreshedToken with new expiration.
        """
        ...

    def _build_exchange_params(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code: str,
    ) -> dict[str, str]:
        """Build parameters for code exchange."""
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }

    def _build_long_lived_params(
        self,
        client_secret: str,
        short_lived_token: str,
    ) -> dict[str, str]:
        """Build parameters for long-lived token exchange."""
        return {
            "grant_type": "th_exchange_token",
            "client_secret": client_secret,
            "access_token": short_lived_token,
        }

    def _build_refresh_params(self, access_token: str) -> dict[str, str]:
        """Build parameters for token refresh."""
        return {
            "grant_type": "th_refresh_token",
            "access_token": access_token,
        }
