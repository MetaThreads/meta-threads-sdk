"""Input validators for the Threads SDK."""

import re
from urllib.parse import urlparse

from threads.constants import MediaType
from threads.exceptions import ValidationError

# Threads text post limit
MAX_TEXT_LENGTH = 500

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {"jpg", "jpeg", "png", "gif", "webp"}

# Supported video formats
SUPPORTED_VIDEO_FORMATS = {"mp4", "mov"}


def validate_text_length(text: str | None, max_length: int = MAX_TEXT_LENGTH) -> None:
    """Validate that text doesn't exceed maximum length.

    Args:
        text: The text content to validate.
        max_length: Maximum allowed characters.

    Raises:
        ValidationError: If text exceeds maximum length.
    """
    if text is None:
        return

    if len(text) > max_length:
        raise ValidationError(
            f"Text exceeds maximum length of {max_length} characters "
            f"(got {len(text)} characters)"
        )


def validate_media_url(
    url: str | None,
    media_type: MediaType,
) -> None:
    """Validate a media URL.

    Args:
        url: The URL to validate.
        media_type: Expected media type.

    Raises:
        ValidationError: If URL is invalid or doesn't match expected type.
    """
    if url is None:
        if media_type in (MediaType.IMAGE, MediaType.VIDEO):
            raise ValidationError(f"URL is required for {media_type} posts")
        return

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"Invalid URL format: {url}")

    if parsed.scheme not in ("http", "https"):
        raise ValidationError(f"URL must use http or https scheme: {url}")

    extension = parsed.path.rsplit(".", 1)[-1].lower() if "." in parsed.path else ""

    if (
        media_type == MediaType.IMAGE
        and extension
        and extension not in SUPPORTED_IMAGE_FORMATS
    ):
        raise ValidationError(
            f"Unsupported image format: {extension}. "
            f"Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )
    elif (
        media_type == MediaType.VIDEO
        and extension
        and extension not in SUPPORTED_VIDEO_FORMATS
    ):
        raise ValidationError(
            f"Unsupported video format: {extension}. "
            f"Supported: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
        )


def validate_carousel_items(item_ids: list[str]) -> None:
    """Validate carousel item IDs.

    Args:
        item_ids: List of media container IDs.

    Raises:
        ValidationError: If carousel requirements aren't met.
    """
    if len(item_ids) < 2:
        raise ValidationError("Carousel requires at least 2 items")

    if len(item_ids) > 20:
        raise ValidationError("Carousel cannot have more than 20 items")


def validate_reply_control(reply_control: str | None) -> None:
    """Validate reply control value.

    Args:
        reply_control: The reply control setting.

    Raises:
        ValidationError: If reply control value is invalid.
    """
    valid_values = {"EVERYONE", "ACCOUNTS_YOU_FOLLOW", "MENTIONED_ONLY"}

    if reply_control is not None and reply_control not in valid_values:
        raise ValidationError(
            f"Invalid reply_control value: {reply_control}. "
            f"Must be one of: {', '.join(valid_values)}"
        )


def validate_country_codes(codes: list[str] | None) -> None:
    """Validate ISO country codes for geo-gating.

    Args:
        codes: List of ISO 3166-1 alpha-2 country codes.

    Raises:
        ValidationError: If any country code is invalid.
    """
    if codes is None:
        return

    iso_pattern = re.compile(r"^[A-Z]{2}$")

    invalid_codes = [code for code in codes if not iso_pattern.match(code)]

    if invalid_codes:
        raise ValidationError(
            f"Invalid ISO country codes: {', '.join(invalid_codes)}. "
            "Must be 2-letter uppercase codes (e.g., 'US', 'GB')"
        )
