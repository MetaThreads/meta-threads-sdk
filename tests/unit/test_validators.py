"""Tests for input validators."""

import pytest

from threads._utils.validators import (
    validate_carousel_items,
    validate_country_codes,
    validate_media_url,
    validate_reply_control,
    validate_text_length,
)
from threads.constants import MediaType
from threads.exceptions import ValidationError


class TestValidateTextLength:
    """Tests for text length validation."""

    def test_valid_text(self):
        validate_text_length("Hello, Threads!")

    def test_none_text(self):
        validate_text_length(None)

    def test_max_length_text(self):
        text = "a" * 500
        validate_text_length(text)

    def test_exceeds_max_length(self):
        text = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            validate_text_length(text)
        assert "exceeds maximum length" in str(exc_info.value)


class TestValidateMediaUrl:
    """Tests for media URL validation."""

    def test_valid_image_url(self):
        validate_media_url("https://example.com/image.jpg", MediaType.IMAGE)

    def test_valid_video_url(self):
        validate_media_url("https://example.com/video.mp4", MediaType.VIDEO)

    def test_none_for_text(self):
        validate_media_url(None, MediaType.TEXT)

    def test_none_required_for_image(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_media_url(None, MediaType.IMAGE)
        assert "required" in str(exc_info.value)

    def test_invalid_scheme(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_media_url("ftp://example.com/image.jpg", MediaType.IMAGE)
        assert "http or https" in str(exc_info.value)

    def test_invalid_image_format(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_media_url("https://example.com/image.bmp", MediaType.IMAGE)
        assert "Unsupported image format" in str(exc_info.value)


class TestValidateCarouselItems:
    """Tests for carousel item validation."""

    def test_valid_carousel(self):
        validate_carousel_items(["id1", "id2", "id3"])

    def test_minimum_items(self):
        validate_carousel_items(["id1", "id2"])

    def test_too_few_items(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_carousel_items(["id1"])
        assert "at least 2" in str(exc_info.value)

    def test_too_many_items(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_carousel_items([f"id{i}" for i in range(25)])
        assert "more than 20" in str(exc_info.value)


class TestValidateReplyControl:
    """Tests for reply control validation."""

    def test_valid_everyone(self):
        validate_reply_control("EVERYONE")

    def test_valid_accounts_you_follow(self):
        validate_reply_control("ACCOUNTS_YOU_FOLLOW")

    def test_valid_mentioned_only(self):
        validate_reply_control("MENTIONED_ONLY")

    def test_none_value(self):
        validate_reply_control(None)

    def test_invalid_value(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_reply_control("invalid")
        assert "Invalid reply_control" in str(exc_info.value)


class TestValidateCountryCodes:
    """Tests for country code validation."""

    def test_valid_codes(self):
        validate_country_codes(["US", "GB", "CA"])

    def test_none_codes(self):
        validate_country_codes(None)

    def test_invalid_lowercase(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_country_codes(["us", "gb"])
        assert "Invalid ISO country codes" in str(exc_info.value)

    def test_invalid_length(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_country_codes(["USA"])
        assert "2-letter uppercase" in str(exc_info.value)
