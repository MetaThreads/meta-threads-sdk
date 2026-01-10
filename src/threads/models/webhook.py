"""Webhook models for the Threads API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WebhookSubscription(BaseModel):
    """Webhook subscription configuration."""

    object: str = "page"
    callback_url: str
    fields: list[str] = Field(default_factory=list)
    verify_token: str | None = None
    active: bool = True


class WebhookEntry(BaseModel):
    """A single webhook entry."""

    id: str
    time: int = Field(description="Unix timestamp")
    changes: list[dict[str, str | dict[str, str]]] = Field(default_factory=list)

    @property
    def timestamp(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.time)


class WebhookPayload(BaseModel):
    """Webhook payload received from Threads."""

    object: str
    entry: list[WebhookEntry] = Field(default_factory=list)


class WebhookEvent(BaseModel):
    """Parsed webhook event."""

    event_type: str
    object_id: str
    timestamp: datetime
    data: dict[str, str | int | bool | None] = Field(default_factory=dict)


class WebhookVerification(BaseModel):
    """Webhook verification challenge."""

    model_config = ConfigDict(populate_by_name=True)

    hub_mode: str = Field(alias="hub.mode")
    hub_challenge: str = Field(alias="hub.challenge")
    hub_verify_token: str = Field(alias="hub.verify_token")
