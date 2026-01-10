"""Base webhooks client."""

from abc import ABC, abstractmethod
from typing import Any

from threads._base.client import BaseSubClient, BaseThreadsClient
from threads.models.webhook import WebhookPayload, WebhookVerification


class BaseWebhooksClient(BaseSubClient, ABC):
    """Abstract base class for webhook operations.

    Handles webhook subscription and event parsing.
    """

    def __init__(self, parent: BaseThreadsClient[Any]) -> None:
        super().__init__(parent)

    @abstractmethod
    def subscribe(
        self,
        callback_url: str,
        verify_token: str,
        fields: list[str] | None = None,
    ) -> Any:
        """Subscribe to webhook events.

        Args:
            callback_url: URL to receive webhook events.
            verify_token: Token for verification challenge.
            fields: Event types to subscribe to.

        Returns:
            WebhookSubscription confirmation.
        """
        ...

    @abstractmethod
    def unsubscribe(self) -> Any:
        """Unsubscribe from webhook events.

        Returns:
            True if successful.
        """
        ...

    @abstractmethod
    def get_subscriptions(self) -> Any:
        """Get current webhook subscriptions.

        Returns:
            List of WebhookSubscription objects.
        """
        ...

    def verify_challenge(
        self,
        params: dict[str, str],
        expected_verify_token: str,
    ) -> str | None:
        """Verify a webhook challenge request.

        Args:
            params: Query parameters from the challenge request.
            expected_verify_token: Your verify token to check against.

        Returns:
            The hub.challenge value if verified, None otherwise.
        """
        try:
            verification = WebhookVerification(
                **{
                    "hub.mode": params.get("hub.mode", ""),
                    "hub.challenge": params.get("hub.challenge", ""),
                    "hub.verify_token": params.get("hub.verify_token", ""),
                }
            )

            if verification.hub_mode != "subscribe":
                return None

            if verification.hub_verify_token != expected_verify_token:
                return None

            return verification.hub_challenge
        except Exception:
            return None

    def parse_payload(self, data: dict[str, Any]) -> WebhookPayload:
        """Parse a webhook payload.

        Args:
            data: The raw webhook payload data.

        Returns:
            Parsed WebhookPayload object.
        """
        return WebhookPayload.model_validate(data)
