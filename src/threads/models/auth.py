"""Authentication models for the Threads API."""

from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class ShortLivedToken(BaseModel):
    """Short-lived access token (valid for ~1 hour)."""

    access_token: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def is_expired(self) -> bool:
        """Check if token is likely expired (1 hour lifetime)."""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed >= 3600


class LongLivedToken(BaseModel):
    """Long-lived access token (valid for 60 days)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until expiration")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def expires_at(self) -> datetime:
        """Calculate the expiration datetime."""
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now() >= self.expires_at

    @property
    def expires_in_days(self) -> int:
        """Get expiration time in days."""
        return self.expires_in // 86400


class RefreshedToken(BaseModel):
    """Refreshed long-lived access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until expiration")
