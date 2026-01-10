"""Asynchronous webhooks client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from threads._base.webhooks import BaseWebhooksClient
from threads.exceptions import raise_for_error
from threads.models.webhook import WebhookSubscription

if TYPE_CHECKING:
    from threads._async.client import AsyncThreadsClient


class AsyncWebhooksClient(BaseWebhooksClient):
    """Asynchronous client for webhook operations."""

    def __init__(self, parent: AsyncThreadsClient) -> None:
        super().__init__(parent)
        self._parent: AsyncThreadsClient = parent

    async def subscribe(
        self,
        callback_url: str,
        verify_token: str,
        fields: list[str] | None = None,
    ) -> WebhookSubscription:
        """Subscribe to webhook events.

        Args:
            callback_url: URL to receive webhook events.
            verify_token: Token for verification challenge.
            fields: Event types to subscribe to.

        Returns:
            WebhookSubscription confirmation.
        """
        if fields is None:
            fields = ["messages", "messaging_postbacks"]

        params = self._get_params(
            object="page",
            callback_url=callback_url,
            verify_token=verify_token,
            fields=",".join(fields),
        )

        response = await self._parent.http.post(
            "/me/subscribed_apps",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return WebhookSubscription(
            callback_url=callback_url,
            verify_token=verify_token,
            fields=fields,
            active=data.get("success", False),
        )

    async def unsubscribe(self) -> bool:
        """Unsubscribe from webhook events.

        Returns:
            True if successful.
        """
        params = self._get_params()

        response = await self._parent.http.delete(
            "/me/subscribed_apps",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        return bool(data.get("success", False))

    async def get_subscriptions(self) -> list[WebhookSubscription]:
        """Get current webhook subscriptions.

        Returns:
            List of WebhookSubscription objects.
        """
        params = self._get_params()

        response = await self._parent.http.get(
            "/me/subscribed_apps",
            params=params,
        )

        data = response.json()

        if response.status_code != 200:
            raise_for_error(data, response.status_code)

        subscriptions = []
        for item in data.get("data", []):
            subscriptions.append(
                WebhookSubscription(
                    callback_url=item.get("callback_url", ""),
                    fields=item.get("fields", []),
                    active=item.get("active", True),
                )
            )

        return subscriptions
