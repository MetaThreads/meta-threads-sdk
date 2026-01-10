"""Asynchronous authentication client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.auth import BaseAuthClient
from threads._utils.logger import get_logger
from threads.constants import API_BASE_URL, API_VERSION
from threads.exceptions import raise_for_error
from threads.models.auth import LongLivedToken, RefreshedToken, ShortLivedToken

if TYPE_CHECKING:
    from threads._async.client import AsyncThreadsClient

logger = get_logger("auth")


class AsyncAuthClient(BaseAuthClient):
    """Asynchronous client for authentication operations."""

    def __init__(self, parent: AsyncThreadsClient) -> None:
        super().__init__(parent)
        self._parent: AsyncThreadsClient = parent

    async def exchange_code(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code: str,
    ) -> ShortLivedToken:
        """Exchange authorization code for short-lived access token.

        Args:
            client_id: Your app's client ID.
            client_secret: Your app's client secret.
            redirect_uri: The redirect URI used in authorization.
            code: The authorization code from the callback.

        Returns:
            ShortLivedToken with the access token and user ID.
        """
        logger.debug("Exchanging authorization code for short-lived token")
        params = self._build_exchange_params(
            client_id, client_secret, redirect_uri, code
        )

        response = await self._parent.http.post(
            f"{API_BASE_URL}/oauth/access_token",
            data=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to exchange code: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info("Successfully exchanged code for short-lived token")
        return ShortLivedToken(
            access_token=data["access_token"],
            user_id=str(data["user_id"]),
        )

    async def get_long_lived_token(
        self,
        client_secret: str,
        short_lived_token: str,
    ) -> LongLivedToken:
        """Exchange short-lived token for long-lived token.

        Args:
            client_secret: Your app's client secret.
            short_lived_token: The short-lived access token.

        Returns:
            LongLivedToken valid for 60 days.
        """
        logger.debug("Exchanging short-lived token for long-lived token")
        params = self._build_long_lived_params(client_secret, short_lived_token)

        response = await self._parent.http.get(
            f"{API_BASE_URL}/{API_VERSION}/access_token",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(
                f"Failed to get long-lived token: status={response.status_code}"
            )
            raise_for_error(data, response.status_code)

        logger.info(
            f"Successfully obtained long-lived token (expires_in={data['expires_in']}s)"
        )
        return LongLivedToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data["expires_in"],
        )

    async def refresh_token(self, access_token: str) -> RefreshedToken:
        """Refresh a long-lived token.

        Args:
            access_token: The current long-lived access token.

        Returns:
            RefreshedToken with new expiration.
        """
        logger.debug("Refreshing long-lived token")
        params = self._build_refresh_params(access_token)

        response = await self._parent.http.get(
            f"{API_BASE_URL}/{API_VERSION}/refresh_access_token",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(f"Failed to refresh token: status={response.status_code}")
            raise_for_error(data, response.status_code)

        logger.info(f"Successfully refreshed token (expires_in={data['expires_in']}s)")
        return RefreshedToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data["expires_in"],
        )
